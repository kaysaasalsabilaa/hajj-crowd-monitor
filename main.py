import csv
import json
import time
from datetime import datetime

import cv2

from classifier     import klasifikasi_keramaian, klasifikasi_pergerakan
from detector       import Detektor
from metrics        import KalkulatorMetrik
from rolling_window import RollingCrowdWindow
from tracker        import Tracker
from video_writer   import AnnotatedVideoWriter

VIDEO_PATH  = "videos/video1.mp4"
MODEL_PATH  = "best.pt"
VIDEO_NAME  = "video1"
LOCATION    = {
    "nama": "Titik A - Pelataran Masjid",
    "lat":  21.4225,
    "lon":  39.8262,
}

CONF_THRESH    = 0.40
IOU_THRESH     = 0.50
IMGSZ          = 1280
TAU            = 0.225
X_COUNT        = 60
Y_COUNT        = 90
SH             = 0.300
WINDOW_S       = 10.0
INTERVAL_S     = 1.0
WARMUP_FRAMES  = 10
CROWD_TOP_Y    = 200

# Kolom output CSV
FRAME_FIELDS = ["timestamp", "count", "n_terdefinisi", "n_lambat", "sf"]

FRAME_TRACK_FIELDS = [
    "timestamp",
    "frame_idx",
    "track_id",
    "cx",        # centroid x bounding box (piksel)
    "cy",        # centroid y bounding box (piksel)
    "bbox_h",    # tinggi bounding box ternormalisasi
    "v_norm",    # kecepatan relatif ternormalisasi = (d/dt) / bbox_h
    "is_lambat", # 1 jika v_norm < TAU, 0 jika tidak
]

WINDOW_FIELDS = [
    "window_k", "window_start", "window_end",
    "count_avg", "n_terdefinisi_total", "n_lambat_total",
    "slow_ratio", "label_crowd", "label_movement",
    "lat", "lon", "lokasi",
]


def get_timestamp(cap, indeks_frame, fps, is_live, waktu_awal):
    if is_live:
        return time.time() - waktu_awal
    ms = cap.get(cv2.CAP_PROP_POS_MSEC)
    return float(ms) / 1000.0 if ms > 0 else indeks_frame / fps


def save_metadata(path, video_name, fps, location, thresholds):
    meta = {
        "video_name":    video_name,
        "run_timestamp": datetime.now().isoformat(),
        "fps_source":    fps,
        "location":      location,
        "thresholds":    thresholds,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"Metadata : {path}")


def _hitung_track_mentah(tracker_obj) -> int:
    # Hitung jumlah track terkonfirmasi langsung dari objek DeepSort
    try:
        tracks = tracker_obj.tracker.tracks
        return sum(1 for t in tracks if t.is_confirmed())
    except Exception:
        return 0


def jalankan_pipeline(
    video_path,
    model_path,
    video_name,
    location,
    output_dir     = "outputs",
    conf_thresh    = CONF_THRESH,
    iou_thresh     = IOU_THRESH,
    imgsz          = IMGSZ,
    tau            = TAU,
    x_count        = X_COUNT,
    y_count        = Y_COUNT,
    sh             = SH,
    window_s       = WINDOW_S,
    interval_s     = INTERVAL_S,
    warmup_frames  = WARMUP_FRAMES,
    crowd_top_y    = CROWD_TOP_Y,
    save_video     = True,
    video_out_path = None,
    on_log         = None,
    on_progress    = None,
    on_window      = None,
    stop_flag      = None,
):
    import os
    os.makedirs(output_dir, exist_ok=True)

    def _log(msg):
        print(msg)
        if on_log:
            on_log(msg)

    is_live = isinstance(video_path, int)

    _log(f"▶ Membuka video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Tidak bisa membuka video: {video_path}")

    fps          = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_est = total_frames / fps if fps > 0 else 0
    vid_w        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h        = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    _log(
        f"   FPS: {fps:.1f} │ Frame: {total_frames} │ "
        f"Durasi: {duration_est:.1f}s │ Resolusi: {vid_w}x{vid_h}"
    )
    _log(
        f"   Conf: {conf_thresh} │ IoU: {iou_thresh} │ "
        f"imgsz: {imgsz} │ Warmup: {warmup_frames} │ "
        f"crowd_top_y: {crowd_top_y}px │ TAU: {tau}"
    )

    detektor   = Detektor(
        model_path,
        conf         = conf_thresh,
        iou          = iou_thresh,
        imgsz        = imgsz,
        zona_latar_y = crowd_top_y,
    )
    tracker    = Tracker(
        crowd_top_y  = crowd_top_y,
        frame_width  = vid_w,
        frame_height = vid_h,
    )
    calculator = KalkulatorMetrik(tau=tau)
    win        = RollingCrowdWindow(
        window_s=window_s,
        output_interval_s=interval_s,
    )

    vwriter   = None
    out_video = None
    if save_video:
        if video_out_path is None:
            out_video = os.path.join(output_dir, f"annotated_{video_name}.mp4")
        else:
            out_video = video_out_path
        vwriter = AnnotatedVideoWriter(
            out_video, fps, vid_w, vid_h,
            crowd_top_y=crowd_top_y,
        )
        if vwriter.is_open:
            out_video = vwriter.out_path
            _log(f"Video output: {out_video}")
        else:
            _log("VideoWriter gagal dibuka - video output dinonaktifkan.")
            vwriter   = None
            out_video = None

    _log("✓ Model YOLOv8 + DeepSORT siap")
    if warmup_frames > 0:
        _log(f"⏳ Warmup {warmup_frames} frame pertama...")
    _log("Pipeline dimulai...")

    waktu_awal          = time.time()
    indeks_frame        = 0
    jumlah_diproses     = 0
    baris_frame         = []
    frame_track_rows    = []
    baris_window        = []
    dihentikan_pengguna = False

    while cap.isOpened():
        if stop_flag and stop_flag():
            _log("⛔ Pipeline dihentikan oleh pengguna.")
            dihentikan_pengguna = True
            break

        ret, frame = cap.read()
        if not ret:
            break

        ts = get_timestamp(cap, indeks_frame, fps, is_live, waktu_awal)

        # Fase warmup: deteksi dan update tracker tapi tidak dicatat
        if indeks_frame < warmup_frames:
            hasil_deteksi = detektor.deteksi(frame)
            tracker.perbarui(hasil_deteksi, frame)
            indeks_frame += 1
            if on_progress and total_frames > 0:
                on_progress(min(int(indeks_frame / total_frames * 100), 5))
            continue

        hasil_deteksi = detektor.deteksi(frame)

        raw_confirmed_before  = _hitung_track_mentah(tracker)
        jalur_terkonfirmasi   = tracker.perbarui(hasil_deteksi, frame)
        n_ghost = max(0, raw_confirmed_before - len(jalur_terkonfirmasi))

        count, n_def, n_slow, sf, ids_lambat, kecepatan_track = calculator.perbarui(
            jalur_terkonfirmasi, ts
        )

        if jumlah_diproses % 30 == 0:
            _log(
                f"[Frame {indeks_frame}] raw_det={len(hasil_deteksi)} │ "
                f"confirmed={count} │ slow={n_slow} │ "
                f"ghost_suppressed={n_ghost} │ ts={ts:.1f}s"
            )

        baris_frame.append({
            "timestamp":     round(ts, 4),
            "count":         count,
            "n_terdefinisi": n_def,
            "n_lambat":      n_slow,
            "sf":            round(sf, 4),
        })

        for spd in kecepatan_track:
            frame_track_rows.append({
                "timestamp": round(ts, 4),
                "frame_idx": indeks_frame,
                "track_id":  spd["track_id"],
                "cx":        spd["cx"],
                "cy":        spd["cy"],
                "bbox_h":    spd["bbox_h"],
                "v_norm":    spd["v_norm"],
                "is_lambat": spd["is_lambat"],
            })

        # data ke rolling window dan ambil output jika waktunya
        win.push(ts, count, n_def, n_slow)

        while win.should_output(ts):
            feats = win.get_features(ts)
            if feats is None:
                break

            label_crowd    = klasifikasi_keramaian(
                feats["count_avg"], feats["slow_ratio"],
                X=x_count, Y=y_count, SH=sh,
            )
            label_movement = klasifikasi_pergerakan(
                feats["slow_ratio"], feats["count_avg"], x_count, SH=sh
            )

            row = {
                "window_k":            feats["window_k"],
                "window_start":        feats["window_start"],
                "window_end":          feats["window_end"],
                "count_avg":           feats["count_avg"],
                "n_terdefinisi_total": feats["n_terdefinisi_total"],
                "n_lambat_total":      feats["n_lambat_total"],
                "slow_ratio":          feats["slow_ratio"],
                "label_crowd":         label_crowd,
                "label_movement":      label_movement,
                "lat":                 location["lat"],
                "lon":                 location["lon"],
                "lokasi":              location["nama"],
            }
            baris_window.append(row)
            if on_window:
                on_window(row)

            _log(
                f"[W{feats['window_k']:03d}] "
                f"{feats['window_start']:.1f}-{feats['window_end']:.1f}s │ "
                f"count={feats['count_avg']:.1f} │ "
                f"slow={feats['slow_ratio']:.3f} │ "
                f"{label_crowd} / {label_movement}"
            )

        if vwriter is not None:
            vwriter.write_frame(
                frame, jalur_terkonfirmasi, indeks_frame, ts,
                ids_lambat=ids_lambat,
                n_ghost=n_ghost,
            )

        indeks_frame    += 1
        jumlah_diproses += 1
        if on_progress and total_frames > 0:
            on_progress(min(int(indeks_frame / total_frames * 100), 99))

    cap.release()
    if vwriter is not None:
        vwriter.release()
        _log(f"✅ Video tersimpan: {out_video}")

    _log(
        f"\n✓ Selesai — {jumlah_diproses} frame diproses "
        f"(+{warmup_frames} warmup, total {indeks_frame})"
    )

    # Simpan CSV & metadata
    out_frame       = os.path.join(output_dir, f"frame_{video_name}.csv")
    out_frame_track = os.path.join(output_dir, f"frame_track_{video_name}.csv")
    out_window      = os.path.join(output_dir, f"window_{video_name}.csv")
    out_meta        = os.path.join(output_dir, f"meta_{video_name}.json")

    if baris_frame:
        with open(out_frame, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FRAME_FIELDS)
            writer.writeheader()
            writer.writerows(baris_frame)
        _log(f"💾 Frame CSV          → {out_frame}")

    if frame_track_rows:
        with open(out_frame_track, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FRAME_TRACK_FIELDS)
            writer.writeheader()
            writer.writerows(frame_track_rows)
        _log(
            f"💾 Frame Track CSV    → {out_frame_track}  "
            f"({len(frame_track_rows):,} baris)"
        )
    else:
        _log("⚠  frame_track CSV kosong — tidak ada track dengan v_norm terdefinisi.")

    if baris_window:
        with open(out_window, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=WINDOW_FIELDS)
            writer.writeheader()
            writer.writerows(baris_window)
        _log(f"💾 Window CSV         → {out_window}")

    thresholds = {
        "CONF_THRESH":   conf_thresh,
        "IOU_THRESH":    iou_thresh,
        "IMGSZ":         imgsz,
        "TAU":           tau,
        "X_COUNT":       x_count,
        "Y_COUNT":       y_count,
        "SH":            sh,
        "WINDOW_S":      window_s,
        "INTERVAL_S":    interval_s,
        "WARMUP_FRAMES": warmup_frames,
        "CROWD_TOP_Y":   crowd_top_y,
    }
    save_metadata(
        path       = out_meta,
        video_name = video_name,
        fps        = fps,
        location   = location,
        thresholds = thresholds,
    )

    if on_progress:
        on_progress(100)

    return {
        "out_frame":           out_frame,
        "out_frame_track":     out_frame_track,
        "out_window":          out_window,
        "out_meta":            out_meta,
        "out_video":           out_video,
        "window_rows":         baris_window,
        "frame_count":         jumlah_diproses,
        "dihentikan_pengguna": dihentikan_pengguna,
    }


def main():
    """Entry point CLI."""
    jalankan_pipeline(
        video_path    = VIDEO_PATH,
        model_path    = MODEL_PATH,
        video_name    = VIDEO_NAME,
        location      = LOCATION,
        output_dir    = "outputs",
        conf_thresh   = CONF_THRESH,
        iou_thresh    = IOU_THRESH,
        imgsz         = IMGSZ,
        tau           = TAU,
        x_count       = X_COUNT,
        y_count       = Y_COUNT,
        sh            = SH,
        window_s      = WINDOW_S,
        interval_s    = INTERVAL_S,
        warmup_frames = WARMUP_FRAMES,
        crowd_top_y   = CROWD_TOP_Y,
        save_video    = True,
    )


if __name__ == "__main__":
    main()