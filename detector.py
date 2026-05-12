from ultralytics import YOLO
import numpy as np

BACKGROUND_ZONE_Y    = 270
_DEFAULT_MAX_SPLITS  = 4
_MIN_SAMPLES_FOR_SPLIT = 15


class Detektor:
    def __init__(
        self,
        model_path,
        conf              = 0.25,
        iou               = 0.65,
        imgsz             = 960,
        zona_latar_y      = BACKGROUND_ZONE_Y,
        max_splits        = _DEFAULT_MAX_SPLITS,
        min_samples_split = _MIN_SAMPLES_FOR_SPLIT,
    ):

        self.model              = YOLO(model_path)
        self.conf               = conf
        self.iou                = iou
        self.imgsz_base         = imgsz
        self.zona_latar_y       = zona_latar_y
        self.max_splits         = max_splits
        self.min_samples_split  = min_samples_split

        self._estimasi_lebar_zona: dict[int, float] = {}
        self._estimasi_lebar: float | None = None

        self._single_box_samples = 0
        self._split_ready        = False

    def _get_rect_imgsz(self, frame_h: int, frame_w: int) -> tuple:
        target_w = self.imgsz_base
        target_h = round(self.imgsz_base * frame_h / frame_w / 32) * 32
        target_h = max(target_h, 32)
        return [target_h, target_w]

    @staticmethod
    def _estimasi_lebar_normal(raw_boxes: list) -> float | None:

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

    def deteksi(self, frame) -> list:

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

        deteksi_valid = []
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
            if cy < self.zona_latar_y:
                continue

            deteksi_valid.append((float(x1), float(y1), float(x2), float(y2), conf))

        zone_raw: dict[int, list] = {0: [], 1: [], 2: []}
        for x1, y1, x2, y2, _ in deteksi_valid:
            cy   = (y1 + y2) / 2.0
            zone = min(int(cy / frame_h * 3), 2)
            zone_raw[zone].append((x1, y1, x2, y2))

        for z, boxes in zone_raw.items():
            w_est = self._estimasi_lebar_normal(boxes)
            if w_est is not None:
                if z not in self._estimasi_lebar_zona:
                    self._estimasi_lebar_zona[z] = w_est
                else:
                    self._estimasi_lebar_zona[z] = (
                        0.80 * self._estimasi_lebar_zona[z] + 0.20 * w_est
                    )

        global_nw = self._estimasi_lebar_normal(
            [(x1, y1, x2, y2) for x1, y1, x2, y2, _ in deteksi_valid]
        )
        if global_nw is not None:
            if self._estimasi_lebar is None:
                self._estimasi_lebar = global_nw
            else:
                self._estimasi_lebar = (
                    0.85 * self._estimasi_lebar + 0.15 * global_nw
                )

        single_count = sum(
            1 for x1, y1, x2, y2, _ in deteksi_valid
            if (y2 - y1) / max(x2 - x1, 1.0) > 1.3
        )
        self._single_box_samples += single_count

        if not self._split_ready and self._single_box_samples >= self.min_samples_split:
            self._split_ready = True

        hasil_deteksi = []
        for x1, y1, x2, y2, conf in deteksi_valid:
            w = x2 - x1
            h = y2 - y1
            aspect = h / max(w, 1.0)

            cy   = (y1 + y2) / 2.0
            zone = min(int(cy / frame_h * 3), 2)

            effective_nw = (
                self._estimasi_lebar_zona.get(zone)
                or self._estimasi_lebar
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
                        if sub_cy < self.zona_latar_y:
                            continue

                        hasil_deteksi.append((sub_bbox, sub_conf, "person"))
                    continue

            hasil_deteksi.append(([float(x1), float(y1), w, h], conf, "person"))

        return hasil_deteksi