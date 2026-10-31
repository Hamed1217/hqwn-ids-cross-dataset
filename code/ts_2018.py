"""
Recovers the TIMESTAMP of every flow in the CSE-CIC-IDS2018 sample cache (ids2018_sample_v4.npz), which was saved
without times. Needed by event_metrics.py (event-level metric) and benign_sensitivity.py (time-ordered split) for
the 2018 levels. The cache itself is NOT changed.

How: the sample was drawn by cross_dataset.load_2018 with a seeded random generator (seed 0), file by file and chunk
by chunk; which rows are drawn depends only on the label counts and the chunk size, not on the features. This script
replays exactly the same draw (same files in the same order, same --chunk, --ben18, --cap18), keeps the timestamp of
every drawn row, applies the same NaN / conflict / duplicate filter, and then CHECKS that the recovered rows equal the
cache row by row (all 69 flow features and the label). Only if they are identical is the output written.

  python ts_2018.py --data18 "D:/revised model/ids2018/*.csv" --cache "D:/revised model/cross_out4/ids2018_sample_v4.npz" --s17_dir "D:/revised model/stage1_pw"
Output: ids2018_times_v4.npz next to the cache: ts (seconds since 1970, float, NaN if unparsable), session (index of
the capture file = one day), files (names), verified = True. About 15-30 min (reads all 2018 CSV files once more).
"""
import argparse, glob, json, os, time
import numpy as np
import pandas as pd

from cross_dataset import build_map, norm, parse_ts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data18", default="D:/revised model/ids2018/*.csv")
    ap.add_argument("--cache", default="D:/revised model/cross_out4/ids2018_sample_v4.npz")
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--ben18", type=int, default=300000)
    ap.add_argument("--cap18", type=int, default=20000)
    ap.add_argument("--chunk", type=int, default=500000)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    t0 = time.time()
    feats = json.load(open(os.path.join(a.s17_dir, "feature_names.json")))
    feats17 = [f for f in feats if not f.startswith(("win_", "pw_", "gl_"))]
    zc = np.load(a.cache, allow_pickle=True)
    ccols = list(zc["cols"])
    cX = pd.DataFrame(zc["X"], columns=ccols)
    clab = zc["lab"].astype(str)
    files = sorted(glob.glob(a.data18, recursive=True))
    if not files:
        raise SystemExit(f"no CSV matched: {a.data18}")
    m = build_map()
    want17 = {norm(f): f for f in feats17}
    cnt = {}                                                       # pass 1 (as load_2018): label counts
    for f in files:
        for ch in pd.read_csv(f, usecols=lambda c: norm(c) == "label", chunksize=a.chunk, low_memory=False):
            lab = ch.iloc[:, 0].astype(str).str.strip()
            for k, v in lab[lab.str.lower() != "label"].value_counts().items():
                cnt[k] = cnt.get(k, 0) + int(v)
    n_ben = cnt.get("Benign", 0)
    rate = {k: (min(1.0, a.ben18 / max(n_ben, 1)) if k == "Benign" else min(1.0, a.cap18 / v)) for k, v in cnt.items()}
    print(f"pass 1 done: {sum(cnt.values()):,} labelled rows in {len(files)} files [{time.time() - t0:.0f}s]")
    rng = np.random.default_rng(a.seed)
    Xs, labs, tss, sess = [], [], [], []
    for fi, f in enumerate(files):                                  # pass 2: the same draw, plus the timestamp
        cols = list(pd.read_csv(f, nrows=0).columns)
        by = {norm(c): c for c in cols}
        col_for = {}
        for c in cols:
            k17 = m.get(norm(c))
            if k17 in want17:
                col_for[want17[k17]] = c
        lab_c, ts_c = by["label"], by["timestamp"]
        use = set(col_for.values()) | {lab_c, ts_c}
        n = 0
        for ch in pd.read_csv(f, usecols=lambda c: c in use, chunksize=a.chunk, low_memory=False):
            lab_s = ch[lab_c].astype(str).str.strip()
            ok = (lab_s.str.lower() != "label").values
            keep = ok & (rng.random(len(ch)) < lab_s.map(rate).fillna(0).values)
            sub = ch[keep]
            X = pd.DataFrame({f17: pd.to_numeric(sub[c], errors="coerce").values for f17, c in col_for.items()})
            Xs.append(X)
            labs.append(lab_s.values[keep])
            tss.append(sub[ts_c].astype(str).values)
            sess.append(np.full(int(keep.sum()), fi))
            n += int(keep.sum())
        print(f"  {os.path.basename(f)}: kept {n} [{time.time() - t0:.0f}s]", flush=True)
    D = pd.concat(Xs, ignore_index=True)
    for x in feats17:
        if x not in D.columns:
            D[x] = 0.0
    lab = np.concatenate(labs)
    ts_str = np.concatenate(tss)
    session = np.concatenate(sess)
    X = D[feats17].replace([np.inf, -np.inf], np.nan)
    okr = X.notna().all(axis=1).values
    h = pd.util.hash_pandas_object(X, index=False).values
    t = pd.DataFrame({"h": h, "a": lab})
    conflict = (t.groupby("h")["a"].transform("nunique") > 1).values
    dup = t.duplicated(["h", "a"]).values
    keep = okr & ~(conflict | dup)
    Xk, labk = X[keep].reset_index(drop=True), lab[keep]
    print(f"replayed sample: {len(keep)} drawn -> {int(keep.sum())} after filter; cache has {len(clab)}")
    # ---------------- verification (row by row)
    if int(keep.sum()) != len(clab):
        raise SystemExit("row count differs from the cache -> NOT the same draw (check --chunk / --ben18 / --cap18 / "
                         "the CSV folder, or the cache was built with other rows dropped). Nothing written.")
    same_lab = bool((labk == clab).all())
    diff = float(np.nanmax(np.abs(Xk.values - cX[feats17].values)))
    print(f"verify: labels identical {same_lab}, max feature difference {diff:.3g}")
    if not same_lab or diff > 1e-9:
        raise SystemExit("recovered rows differ from the cache -> nothing written")
    ts = parse_ts(pd.Series(ts_str[keep]))
    sec = np.where(ts.notna().values, ts.values.astype("datetime64[s]").astype("int64").astype("float64"), np.nan)
    out = os.path.join(os.path.dirname(os.path.abspath(a.cache)), "ids2018_times_v4.npz")
    np.savez(out, ts=sec, session=session[keep], files=np.array([os.path.basename(f) for f in files]), verified=True)
    print(f"timestamps parsed {np.isfinite(sec).mean():.2%}; per day: "
          + ", ".join(f"{os.path.basename(files[s])[:10]} {int((session[keep] == s).sum())}" for s in np.unique(session[keep])))
    print(f"saved -> {out} [{time.time() - t0:.0f}s]")


if __name__ == "__main__":
    main()
