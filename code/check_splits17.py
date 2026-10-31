"""
Reports how the CIC-IDS2017 train / validation / test splits used by hybrid_v3 (stage-1 output splits.npz) were made,
for Table 1 of the paper. Reads files only; nothing is trained or changed.

stage1_cicids2017_pipeline.py has two split modes:
  random   stratified ROWS: test 20%, then validation 25% of the rest  -> 60 / 20 / 20, same share per class
  blocked  whole 1-minute TIME BLOCKS (per capture file) assigned at random to 60 / 20 / 20
Neither is "train = past, test = future". This script tells which one splits.npz came from:
with the random mode every attack class is split val : test = 1 : 1 almost exactly; with the blocked mode the
ratio varies by class (whole blocks move together).

  python check_splits17.py --s17_dir "D:/revised model/stage1_pw"
Copy the whole printed output back.
"""
import argparse, os
import numpy as np
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    a = ap.parse_args()
    print("files in", a.s17_dir)
    for f in sorted(os.listdir(a.s17_dir)):
        p = os.path.join(a.s17_dir, f)
        print(f"  {f:40s} {os.path.getsize(p) / 1e6:9.1f} MB")
    z = np.load(os.path.join(a.s17_dir, "splits.npz"), allow_pickle=True)
    n = {s: len(z[f"y{s}"]) for s in ("tr", "va", "te")}
    tot = sum(n.values())
    print("\nrows: " + ", ".join(f"{s} {n[s]:,} ({n[s] / tot:.1%})" for s in n) + f", total {tot:,}")
    print("attack share: " + ", ".join(f"{s} {float(np.mean(z[f'y{s}'])):.3f}" for s in n))
    lab = {s: np.where(z[f"y{s}"] == 0, "BENIGN", z[f"a{s}"].astype(str)) for s in n}
    t = pd.DataFrame({s: pd.Series(lab[s]).value_counts() for s in n}).fillna(0).astype(int)
    t.columns = ["train", "val", "test"]
    t["val/test"] = (t["val"] / t["test"].replace(0, np.nan)).round(3)
    print("\nrows per class and split:")
    print(t.sort_values("test", ascending=False).to_string())
    big = t[(t["val"] >= 50) & (t["test"] >= 50)]
    dev = float((big["val/test"] - 1).abs().max()) if len(big) else float("nan")
    print(f"\nlargest |val/test - 1| over classes with >= 50 rows: {dev:.3f}")
    if dev < 0.02:
        print("VERDICT: random stratified split (--split random): rows of the same minute can be in train, val and test.")
    else:
        print("VERDICT: not row-stratified -> most likely --split blocked (1-minute time blocks).")
    for f in ("label_time_windows.csv",):
        p = os.path.join(a.s17_dir, f)
        if os.path.exists(p):
            print(f"\n{f} exists (timestamps were available at stage 1); first lines:")
            print(pd.read_csv(p).head(8).to_string())


if __name__ == "__main__":
    main()
