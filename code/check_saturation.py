"""
Reviewer point 1: does the 2017-fitted QuantileTransformer SATURATE on the target network (values pushed to the edge of
the 2017 range)? For every flow feature: share of target flows at the lower / upper edge of the 2017 training range,
compared with the 2017 test split (same transformer, same network) as the reference. CPU, ~1 minute.

  python check_saturation.py --s17_dir "D:/revised model/stage1_pw" --target_cache "D:/revised model/cross_out4/ids2018_sample_v4.npz"
"""
import argparse, json, os
import numpy as np
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--target_cache", default="D:/revised model/cross_out4/ids2018_sample_v4.npz")
    ap.add_argument("--out", default="saturation.csv")
    a = ap.parse_args()
    import joblib
    feats = json.load(open(os.path.join(a.s17_dir, "feature_names.json")))
    flow = [f for f in feats if not f.startswith(("win_", "pw_", "gl_"))]
    fidx = np.array([feats.index(c) for c in flow])
    z = np.load(os.path.join(a.s17_dir, "splits.npz"), allow_pickle=True)
    Xtr, Xte = z["Xtr"][:, fidx], z["Xte"][:, fidx]
    qt = joblib.load(os.path.join(a.s17_dir, "quantile_transformer.joblib"))
    zc = np.load(a.target_cache, allow_pickle=True)
    raw = pd.DataFrame(zc["X"], columns=list(zc["cols"]))
    full = pd.DataFrame(0.0, index=raw.index, columns=feats)
    for c in feats:
        if c in raw.columns:
            full[c] = raw[c].values
    XT = qt.transform(full)[:, fidx]
    R = full.values[:, fidx]
    q0, q1 = qt.quantiles_[0, fidx], qt.quantiles_[-1, fidx]
    below, above = (R < q0).mean(0), (R > q1).mean(0)            # TRUE out-of-range (clipped) values
    lo, hi = Xtr.min(0), Xtr.max(0)
    eps = 1e-6 * (hi - lo + 1e-12)
    def share(X):
        return (X <= lo + eps).mean(0), (X >= hi - eps).mean(0)
    tl, th = share(Xte)
    gl, gh = share(XT)
    ben = pd.Series(zc["lab"].astype(str)).str.lower().eq("benign").values
    bl, bh = share(XT[ben])
    df = pd.DataFrame(dict(feature=flow, ref2017_low=tl, ref2017_high=th, target_low=gl, target_high=gh,
                           target_benign_low=bl, target_benign_high=bh, clipped_below=below, clipped_above=above))
    df["excess_saturation"] = (df.target_low + df.target_high) - (df.ref2017_low + df.ref2017_high)
    df = df.sort_values("excess_saturation", ascending=False)
    df.to_csv(a.out, index=False)
    print(f"output distribution of the transformer: {qt.output_distribution} | {len(flow)} flow features")
    print(f"mean share of values at the edge of the 2017 range: 2017 test {np.mean(tl + th):.3f} | "
          f"target {np.mean(gl + gh):.3f} | target benign {np.mean(bl + bh):.3f}")
    print(f"features with > 5 points MORE saturation in the target than in 2017: {(df.excess_saturation > 0.05).sum()}")
    print(f"TRUE out-of-range (raw value outside the 2017 range, clipped by the transformer): mean below "
          f"{below.mean():.4f}, mean above {above.mean():.4f}; features with > 1% clipped: {((below + above) > 0.01).sum()}")
    cl = df.assign(clipped=df.clipped_below + df.clipped_above).sort_values("clipped", ascending=False)
    print(cl[["feature", "clipped_below", "clipped_above"]].head(10).round(4).to_string(index=False))
    print("\n(edge share = value equal to the 2017 minimum/maximum, mostly a point mass at 0, i.e. a real shift)")
    print("\ntop 15 (shares 0..1):")
    print(df.head(15).round(3).to_string(index=False))
    print(f"\nsaved -> {a.out}")


if __name__ == "__main__":
    main()
