import pandas as pd, numpy as np, os

# Kumpulkan semua nilai v_norm dari seluruh video
semua_vnorm = []
for nama_video in ["video1", "video2", "video3"]:
    path = f"outputs/frame_track_{nama_video}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        if "v_norm" in df.columns:
            vals = df["v_norm"].dropna()
            vals = vals[vals > 0]   # hanya track yang bergerak
            semua_vnorm.extend(vals.tolist())

arr = np.array(semua_vnorm)
print(f"Total sampel v_norm : {len(arr)}")
print(f"Mean                : {arr.mean():.4f}")
print(f"Median              : {np.median(arr):.4f}")
print(f"Q1 (persentil 25)   : {np.percentile(arr, 25):.4f}")
print(f"Q3 (persentil 75)   : {np.percentile(arr, 75):.4f}")
print(f"\nRekomendasi TAU = Q1 = {np.percentile(arr, 25):.4f}")