import math
from collections import deque

MAKS_DT_KECEPATAN  = 1.0   # batas selisih waktu antar frame (detik)
MAKS_FRAME_ABSEN   = 10    # toleransi frame tanpa deteksi sebelum track dihapus
PANJANG_RIWAYAT_H  = 5     # jumlah sampel tinggi bbox yang disimpan per track


class KalkulatorMetrik:
    def __init__(
        self,
        tau           = 0.05,
        maks_dt       = MAKS_DT_KECEPATAN,
        maks_absen    = MAKS_FRAME_ABSEN,
        panjang_hist  = PANJANG_RIWAYAT_H,
    ):
        self.tau          = tau
        self.maks_dt      = maks_dt
        self.maks_absen   = maks_absen
        self.panjang_hist = panjang_hist

        self.riwayat_track = {}

    @staticmethod
    def _median(nilai_list):
        terurut = sorted(nilai_list)
        n       = len(terurut)
        tengah  = n // 2
        return terurut[tengah] if n % 2 else (terurut[tengah - 1] + terurut[tengah]) / 2.0

    def perbarui(self, jalur_terkonfirmasi, timestamp):
        """
        Hitung metrik per frame dari daftar track yang terkonfirmasi.

        Parameter:
            jalur_terkonfirmasi : list dict track aktif dari Tracker
            timestamp           : waktu frame saat ini (detik)

        Kembalikan:
            jumlah, n_terdefinisi, n_lambat, sf, id_lambat, kecepatan_track
        """
        jumlah        = len(jalur_terkonfirmasi)
        n_terdefinisi = 0
        n_lambat      = 0
        id_lambat     = set()
        kecepatan_track = []

        id_aktif = {t["id"] for t in jalur_terkonfirmasi}

        for t in jalur_terkonfirmasi:
            tid       = t["id"]
            cx, cy, h = t["cx"], t["cy"], t["h"]

            if tid in self.riwayat_track:
                sebelumnya = self.riwayat_track[tid]
                dt         = timestamp - sebelumnya["ts"]

                if 0 < dt <= self.maks_dt:
                    h_robust = self._median(list(sebelumnya["riwayat_h"]))

                    if h_robust > 0:
                        jarak  = math.sqrt(
                            (cx - sebelumnya["cx"]) ** 2 + (cy - sebelumnya["cy"]) ** 2
                        )
                        v_piksel = jarak / dt
                        v_norm   = v_piksel / h_robust

                        n_terdefinisi += 1
                        lambat = int(v_norm < self.tau)

                        if lambat:
                            n_lambat += 1
                            id_lambat.add(tid)

                        kecepatan_track.append({
                            "track_id":  tid,
                            "cx":        round(cx, 2),
                            "cy":        round(cy, 2),
                            "bbox_h":    round(h_robust, 2),
                            "v_norm":    round(v_norm, 6),
                            "is_lambat": lambat,
                        })

                sebelumnya["riwayat_h"].append(h)
                sebelumnya["cx"]     = cx
                sebelumnya["cy"]     = cy
                sebelumnya["ts"]     = timestamp
                sebelumnya["absen"]  = 0

            else:
                self.riwayat_track[tid] = {
                    "cx":       cx,
                    "cy":       cy,
                    "riwayat_h": deque([h], maxlen=self.panjang_hist),
                    "ts":       timestamp,
                    "absen":    0,
                }

        # Hapus track yang lama tidak muncul
        akan_dihapus = []
        for tid, data in self.riwayat_track.items():
            if tid not in id_aktif:
                data["absen"] += 1
                if data["absen"] > self.maks_absen:
                    akan_dihapus.append(tid)
        for tid in akan_dihapus:
            del self.riwayat_track[tid]

        sf = n_lambat / n_terdefinisi if n_terdefinisi > 0 else 0.0

        return jumlah, n_terdefinisi, n_lambat, sf, id_lambat, kecepatan_track