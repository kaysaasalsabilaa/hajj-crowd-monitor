# Hajj Crowd Monitor

Sistem pemantauan keramaian pedestrian jamaah haji berbasis video CCTV menggunakan YOLOv8 dan DeepSORT, dilengkapi visualisasi peta interaktif untuk pemantauan real time

Dikembangkan sebagai bagian dari skripsi S1 Fisika, Universitas Airlangga (2026).

---

## Fitur

- Deteksi dan pelacakan orang secara realtime dari video CCTV menggunakan YOLOv8 + DeepSORT
- Perhitungan jumlah orang dan proporsi pejalan kaki berkecepatan rendah (*slow ratio*)
- Klasifikasi tingkat keramaian (Rendah / Sedang / Tinggi) berbasis rolling window 10 detik
- Klasifikasi kondisi pergerakan (Lancar / Tersendat)
- Visualisasi peta interaktif multi titik menggunakan Leaflet.js
- Dashboard analitik dengan grafik tren real-time

---

## Persyaratan Sistem

- Python 3.10 atau versi diatasnya
- Windows / macOS / Linux
- RAM minimal 8 GB (disarankan 16 GB)
- GPU opsional (CPU cukup untuk video pendek)

---

## Instalasi

### 1. Clone repositori

```bash
git clone https://github.com/[username]/hajj-crowd-monitor.git
cd hajj-crowd-monitor
```

### 2. Install dependencies

```bash
pip install -r requirements_app.txt
```

### 3. Download file model

Download file `best.pt` dari link berikut dan letakkan di dalam folder `project/`:

> 🔗 **Link model:** https://drive.google.com/drive/folders/1BKVhFzHY4sjDBI1NR560xRMFFZe7sub_?usp=sharing

Struktur folder setelah download:
```
project/
├── best.pt        letak best.pt di sini
├── main.py
├── run_app.py
└── ...
```

### 4. Siapkan video

Download video contoh dari link berikut dan letakkan di dalam folder `project/videos/`:

> 🔗 **Link video contoh:** https://drive.google.com/drive/folders/1BKVhFzHY4sjDBI1NR560xRMFFZe7sub_?usp=sharing

---

## Cara Menjalankan

```bash
cd project
python run_app.py
```

Aplikasi desktop akan terbuka. Langkah penggunaan:

1. **Pilih video** - klik Browse dan pilih file video CCTV
2. **Isi lokasi** - masukkan nama lokasi dan pilih koordinat dari peta
3. **Klik Mulai Analisis** - sistem akan memproses video 
4. **Lihat hasil** - pantau peta dan dashboard analitik yang diperbarui setiap detik

---

## Struktur Proyek

```
project/
├── app/                        # Komponen utama (PyQt6)
│   ├── main_window.py
│   ├── styles.py
│   ├── worker.py
│   └── widgets/
│       ├── chart_widget.py
│       ├── input_panel.py
│       ├── map_picker.py
│       ├── results_panel.py
│       └── status_bar.py
├── classifier.py               # Logika klasifikasi keramaian & pergerakan
├── detector.py                 # Deteksi YOLOv8
├── evaluator.py                # Fungsi evaluasi metrik
├── main.py                     # Pipeline utama untuk deteksi, tracking, dan output
├── metrics.py                  # Perhitungan v_norm dan slow ratio
├── rolling_window.py           # Agregasi temporal rolling window
├── tracker.py                  # Deteksi DeepSORT
├── video_writer.py             # Output video beranotasi
├── hitung_tau.py               # Script perhitungan nilai ambang TAU
├── run_app.py                  # Entry point aplikasi desktop
├── requirements_app.txt        # Daftar dependencies
├── videos/                     # Folder video input (tidak disertakan di repo)
└── outputs/                    # Folder hasil analisis (di generate otomatis)
```

---

## Parameter Utama

| Parameter | Default | Keterangan |
|-----------|---------|------------|
| `CONF_THRESH` | 0.40 | Confidence threshold deteksi YOLOv8 |
| `IOU_THRESH` | 0.50 | IoU threshold NMS |
| `IMGSZ` | 1280 | Resolusi inferensi (piksel) |
| `TAU` | 0.241 | Ambang kecepatan ternormalisasi (dari Q1 distribusi v_norm) |
| `X_COUNT` | 60 | Batas bawah jumlah orang → keramaian sedang |
| `Y_COUNT` | 90 | Batas bawah jumlah orang → keramaian tinggi |
| `SH` | 0.30 | Ambang slow ratio untuk kondisi pergerakan |
| `WINDOW_S` | 10.0 | Durasi rolling window (detik) |

Parameter dapat diubah melalui menu **Pengaturan Lanjutan** di dalam aplikasi.

---

## Output yang Dihasilkan

Setiap kali analisis dijalankan, sistem menyimpan file berikut di folder `outputs/`:

| File | Isi |
|------|-----|
| `window_[nama].csv` | Data agregat per window (jumlah orang, slow ratio, label) |
| `frame_[nama].csv` | Data per frame (count, n_lambat, sf) |
| `frame_track_[nama].csv` | Data v_norm per track per frame |
| `meta_[nama].json` | Metadata run (parameter, lokasi, FPS) |
| `annotated_[nama].mp4` | Video beranotasi dengan bounding box |

---

## Informasi

**Penulis:** Kaysa Salsabila Khairunnisa (182221047)  
**Program Studi:** S1 Fisika, Departemen Fisika  
**Fakultas:** Sains dan Teknologi, Universitas Airlangga  
**Tahun:** 2026
