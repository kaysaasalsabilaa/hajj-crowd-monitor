import math
from collections import deque

MAX_DT_FOR_SPEED  = 1.0
MAX_ABSENT_FRAMES = 10
H_HISTORY_LEN     = 5


class MetricsCalculator:
    def __init__(
        self,
        tau           = 0.05,
        max_dt        = MAX_DT_FOR_SPEED,
        max_absent    = MAX_ABSENT_FRAMES,
        h_history_len = H_HISTORY_LEN
    ):
        self.tau           = tau
        self.max_dt        = max_dt
        self.max_absent    = max_absent
        self.h_history_len = h_history_len

        self.track_history = {}

    @staticmethod
    def _median(values):
        s   = sorted(values)
        n   = len(s)
        mid = n // 2
        return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0

    def update(self, confirmed_tracks, timestamp):

        count         = len(confirmed_tracks)
        n_terdefinisi = 0
        n_lambat      = 0
        slow_ids      = set()
        track_speeds  = []           

        active_ids = {t["id"] for t in confirmed_tracks}

        for t in confirmed_tracks:
            tid       = t["id"]
            cx, cy, h = t["cx"], t["cy"], t["h"]

            if tid in self.track_history:
                prev = self.track_history[tid]
                dt   = timestamp - prev["ts"]

                if 0 < dt <= self.max_dt:
                    h_robust = self._median(list(prev["h_hist"]))

                    if h_robust > 0:
                        d     = math.sqrt(
                            (cx - prev["cx"]) ** 2 + (cy - prev["cy"]) ** 2
                        )
                        vpx   = d / dt
                        vnorm = vpx / h_robust

                        n_terdefinisi += 1
                        is_lambat = int(vnorm < self.tau)

                        if is_lambat:
                            n_lambat += 1
                            slow_ids.add(tid)

                        track_speeds.append({
                            "track_id": tid,
                            "cx":       round(cx, 2),
                            "cy":       round(cy, 2),
                            "bbox_h":   round(h_robust, 2),
                            "v_norm":   round(vnorm, 6),
                            "is_lambat": is_lambat,
                        })

                prev["h_hist"].append(h)
                prev["cx"]     = cx
                prev["cy"]     = cy
                prev["ts"]     = timestamp
                prev["absent"] = 0

            else:
                self.track_history[tid] = {
                    "cx":     cx,
                    "cy":     cy,
                    "h_hist": deque([h], maxlen=self.h_history_len),
                    "ts":     timestamp,
                    "absent": 0,
                }

        # Hapus track yang sudah lama tidak muncul
        to_delete = []
        for tid, data in self.track_history.items():
            if tid not in active_ids:
                data["absent"] += 1
                if data["absent"] > self.max_absent:
                    to_delete.append(tid)
        for tid in to_delete:
            del self.track_history[tid]

        sf = n_lambat / n_terdefinisi if n_terdefinisi > 0 else 0.0

        return count, n_terdefinisi, n_lambat, sf, slow_ids, track_speeds