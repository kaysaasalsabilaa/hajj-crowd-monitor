from ultralytics import YOLO
import numpy as np

BACKGROUND_ZONE_Y    = 270
_DEFAULT_MAX_SPLITS  = 4
_MIN_SAMPLES_FOR_SPLIT = 15  


class Detector:
    def __init__(
        self,
        model_path,
        conf              = 0.25,    
        iou               = 0.65,    
        imgsz             = 960,
        background_zone_y = BACKGROUND_ZONE_Y,
        max_splits        = _DEFAULT_MAX_SPLITS,
        min_samples_split = _MIN_SAMPLES_FOR_SPLIT,  
    ):

        self.model              = YOLO(model_path)
        self.conf               = conf
        self.iou                = iou
        self.imgsz_base         = imgsz   
        self.background_zone_y  = background_zone_y
        self.max_splits         = max_splits
        self.min_samples_split  = min_samples_split

        self._zone_width_estimates: dict[int, float] = {}
        self._normal_width_estimate: float | None = None

        self._single_box_samples = 0   
        self._split_ready        = False 

 
    def _get_rect_imgsz(self, frame_h: int, frame_w: int) -> tuple:
        target_w = self.imgsz_base
        target_h = round(self.imgsz_base * frame_h / frame_w / 32) * 32
        target_h = max(target_h, 32)   
        return [target_h, target_w]    

    @staticmethod
    def _estimate_normal_width(raw_boxes: list) -> float | None:
        
        widths = []
        for x1, y1, x2, y2 in raw_boxes:
            w = x2 - x1
            h = y2 - y1
            if h > 0 and (h / w) > 1.5 and w > 10:
                widths.append(w)
        if len(widths) < 2:
            return None
        return float(np.median(widths))

    def _try_multi_split_box(
        self, x1, y1, x2, y2, conf, normal_w: float
    ) -> list | None:
       
        w = x2 - x1
        h = y2 - y1
        if h <= 0:
            return None

        aspect = h / max(w, 1.0)

        if aspect >= 0.85:
            return None
        if w < normal_w * 1.5:
            return None

        n_splits = max(2, round(w / normal_w))
        n_splits = min(n_splits, self.max_splits)

        sub_w   = w / n_splits
        overlap = sub_w * 0.05

        result = []
        for i in range(n_splits):
            sx1 = x1 + i * sub_w - (overlap if i > 0 else 0)
            sx2 = x1 + (i + 1) * sub_w + (overlap if i < n_splits - 1 else 0)
            sw  = sx2 - sx1
            result.append(([float(sx1), float(y1), float(sw), float(h)], conf))

        return result if result else None

    def detect(self, frame) -> list:

        frame_h, frame_w = frame.shape[:2]
        frame_area = frame_h * frame_w

        rect_imgsz = self._get_rect_imgsz(frame_h, frame_w)

        results = self.model(
            frame,
            conf         = self.conf,
            classes      = [0],
            iou          = self.iou,
            imgsz        = rect_imgsz,   
            agnostic_nms = True,
            verbose      = False,
        )[0]

        raw_valid = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            w    = float(x2 - x1)
            h    = float(y2 - y1)

            if h < 1e-3:
                continue

            aspect     = h / max(w, 1.0)
            area_ratio = (w * h) / frame_area

            if not (0.3 < aspect < 5.0):
                continue

            if area_ratio < 0.0001:
                continue
            if area_ratio > 0.15:
                continue

            cy = (float(y1) + float(y2)) / 2.0
            if cy < self.background_zone_y:
                continue

            raw_valid.append((float(x1), float(y1), float(x2), float(y2), conf))

        zone_raw: dict[int, list] = {0: [], 1: [], 2: []}
        for x1, y1, x2, y2, _ in raw_valid:
            cy   = (y1 + y2) / 2.0
            zone = min(int(cy / frame_h * 3), 2)
            zone_raw[zone].append((x1, y1, x2, y2))

        for z, boxes in zone_raw.items():
            w_est = self._estimate_normal_width(boxes)
            if w_est is not None:
                if z not in self._zone_width_estimates:
                    self._zone_width_estimates[z] = w_est
                else:
                    self._zone_width_estimates[z] = (
                        0.80 * self._zone_width_estimates[z] + 0.20 * w_est
                    )

        global_nw = self._estimate_normal_width(
            [(x1, y1, x2, y2) for x1, y1, x2, y2, _ in raw_valid]
        )
        if global_nw is not None:
            if self._normal_width_estimate is None:
                self._normal_width_estimate = global_nw
            else:
                self._normal_width_estimate = (
                    0.85 * self._normal_width_estimate + 0.15 * global_nw
                )

        single_count = sum(
            1 for x1, y1, x2, y2, _ in raw_valid
            if (y2 - y1) / max(x2 - x1, 1.0) > 1.3
        )
        self._single_box_samples += single_count

        if not self._split_ready and self._single_box_samples >= self.min_samples_split:
            self._split_ready = True

        detections = []
        for x1, y1, x2, y2, conf in raw_valid:
            w = x2 - x1
            h = y2 - y1
            aspect = h / max(w, 1.0)

            cy   = (y1 + y2) / 2.0
            zone = min(int(cy / frame_h * 3), 2)

            effective_nw = (
                self._zone_width_estimates.get(zone)
                or self._normal_width_estimate
                or (frame_w * 0.05)
            )

            if aspect < 0.85 and self._split_ready:
                split = self._try_multi_split_box(x1, y1, x2, y2, conf, effective_nw)
                if split is not None:
                    for sub_bbox, sub_conf in split:
                        sx1, sy1, sw, sh = sub_bbox
                        if sw <= 0 or sh <= 0:
                            continue
                        sub_cy     = sy1 + sh / 2.0
                        sub_aspect = sh / max(sw, 1.0)
                        sub_area   = (sw * sh) / frame_area

                        if not (0.3 < sub_aspect < 5.0):
                            continue
                        if sub_area < 0.0001 or sub_area > 0.15:
                            continue
                        if sub_cy < self.background_zone_y:
                            continue

                        detections.append((sub_bbox, sub_conf, "person"))
                    continue

            detections.append(([float(x1), float(y1), w, h], conf, "person"))

        return detections