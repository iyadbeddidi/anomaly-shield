import pandas as pd
import glob
import os


path = "C:/Users/iyadb/Bureau/stagepfa/anomaly-shield/archive/*.csv"

files = glob.glob(path)

dfs = []
for f in files:
    df = pd.read_csv(f, encoding='utf-8', low_memory=False)
    print(f"✅ {os.path.basename(f)} — {df.shape}")
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)
df_all.to_csv("dataset.csv", index=False)
print("✅ Sauvegardé — cicids2017_full.csv")