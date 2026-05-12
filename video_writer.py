import cv2

_C_BOX_NORMAL   = (80,  200,  72)
_C_BOX_SLOW     = (0,   100, 255)
_C_WHITE        = (255, 255, 255)
_C_ID_BG_NORM   = (0,   100,  40)
_C_ID_BG_SLOW   = (0,    50, 160)
_C_PANEL        = (15,   15,  15)
_C_ZONE_LINE    = (0,    80, 200)


def _put_text_bg(img, text, org, font_scale=0.42, thickness=1,
                 text_color=_C_WHITE, bg_color=_C_ID_BG_NORM, pad=2):
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    x, y = org
    cv2.rectangle(img,
                  (x - pad,      y - th - pad),
                  (x + tw + pad, y + baseline + pad),
                  bg_color, -1)
    cv2.putText(img, text, (x, y), font, font_scale,
                text_color, thickness, cv2.LINE_AA)


def _draw_background_zone_line(frame, crowd_top_y: int):
    # Gambar garis putus putus batas zona crowd
    h, w = frame.shape[:2]
    dash_len = 20
    gap_len  = 10
    x = 0
    while x < w:
        x_end = min(x + dash_len, w)
        cv2.line(frame, (x, crowd_top_y), (x_end, crowd_top_y), _C_ZONE_LINE, 1)
        x += dash_len + gap_len
    _put_text_bg(
        frame,
        text       = f"CROWD ZONE > y={crowd_top_y}",
        org        = (4, crowd_top_y - 4),
        font_scale = 0.32,
        bg_color   = _C_ZONE_LINE,
    )


def _draw_tracks(frame, jalur_terkonfirmasi, ids_lambat=None, crowd_top_y=270):
    # Gambar bounding box dan label ID untuk setiap track yang terkonfirmasi
    ids_lambat = ids_lambat or set()
    n_border = 0
    h, w = frame.shape[:2]
    border_margin = 15

    for t in jalur_terkonfirmasi:
        cx, cy = t["cx"], t["cy"]
        th, tw = t["h"],  t["w"]
        x1 = int(cx - tw / 2)
        y1 = int(cy - th / 2)
        x2 = int(cx + tw / 2)
        y2 = int(cy + th / 2)

        is_slow   = t["id"] in ids_lambat
        box_color = _C_BOX_SLOW   if is_slow else _C_BOX_NORMAL
        id_bg     = _C_ID_BG_SLOW if is_slow else _C_ID_BG_NORM

        # Track di tepi frame digambar lebih tipis
        di_tepi = (x2 >= w - border_margin or y2 >= h - border_margin
                   or x1 <= border_margin)
        if di_tepi:
            n_border += 1
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 1)
        else:
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)

        label = f"ID:{t['id']}{'S' if is_slow else ''}"
        _put_text_bg(
            frame,
            text       = label,
            org        = (max(x1, 0), max(y1 - 2, 12)),
            font_scale = 0.38,
            bg_color   = id_bg,
        )

    return n_border


def _draw_info_panel(frame, frame_idx: int, timestamp: float,
                     count: int, n_slow: int = 0,
                     n_ghost: int = 0, n_border: int = 0,
                     crowd_top_y: int = 270):
    # Tampilkan panel info overlay di sudut kiri atas frame
    font   = cv2.FONT_HERSHEY_SIMPLEX
    fscale = 0.42
    thick  = 1
    pad_x  = 8
    pad_y  = 8
    line_h = 17

    lines = [
        (f"Frame  : {frame_idx}",              _C_WHITE),
        (f"Time   : {timestamp:7.2f} s",        _C_WHITE),
        (f"Count  : {count}",                   _C_WHITE),
        (f"Slow   : {n_slow}",             (0, 100, 255) if n_slow  > 0 else _C_WHITE),
        (f"Ghost  : {n_ghost}",            (0,  60, 220) if n_ghost > 0 else _C_WHITE),
        (f"Border : {n_border}",           (180, 180, 0) if n_border > 0 else _C_WHITE),
    ]

    max_tw = max(cv2.getTextSize(l, font, fscale, thick)[0][0]
                 for l, _ in lines)
    pw = max_tw + pad_x * 2
    ph = len(lines) * line_h + pad_y * 2

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (pw, ph), _C_PANEL, -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    for i, (line, color) in enumerate(lines):
        y = pad_y + (i + 1) * line_h - 3
        cv2.putText(frame, line, (pad_x, y), font, fscale,
                    color, thick, cv2.LINE_AA)


class AnnotatedVideoWriter:

    def __init__(self, out_path: str, fps: float, width: int, height: int,
                 crowd_top_y: int = 270,
                 show_zone_line: bool = False):
        self.out_path       = out_path
        self._fps           = max(fps, 1.0)
        self._w             = int(width)
        self._h             = int(height)
        self.crowd_top_y    = crowd_top_y
        self.show_zone_line = show_zone_line

        cc = cv2.VideoWriter_fourcc(*"mp4v")
        self._writer = cv2.VideoWriter(
            out_path, cc, self._fps, (self._w, self._h))
        if not self._writer.isOpened():
            import os
            base, _ = os.path.splitext(out_path)
            self.out_path = base + ".avi"
            cc2 = cv2.VideoWriter_fourcc(*"XVID")
            self._writer  = cv2.VideoWriter(
                self.out_path, cc2, self._fps, (self._w, self._h))
        self._ok = self._writer.isOpened()

    @property
    def is_open(self) -> bool:
        return self._ok

    def write_frame(self, frame, jalur_terkonfirmasi, frame_idx: int,
                    timestamp: float, ids_lambat=None, n_ghost: int = 0):
        if not self._ok:
            return

        annotated = frame.copy()
        count  = len(jalur_terkonfirmasi)
        n_slow = len(ids_lambat) if ids_lambat else 0

        if self.show_zone_line:
            _draw_background_zone_line(annotated, self.crowd_top_y)

        n_border = _draw_tracks(
            annotated, jalur_terkonfirmasi, ids_lambat, self.crowd_top_y)

        _draw_info_panel(
            annotated, frame_idx, timestamp,
            count, n_slow, n_ghost, n_border, self.crowd_top_y)

        self._writer.write(annotated)

    def release(self):
        if self._ok:
            self._writer.release()
            self._ok = False