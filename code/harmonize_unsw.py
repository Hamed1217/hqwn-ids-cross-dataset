"""
Harmonises the UNSW cache with the 2017 FEATURE DEFINITIONS (decided from check_extractor.py, which reads no labels;
no model was run on UNSW). The newer CICFlowMeter used for CIC-UNSW-NB15 defines two groups differently:

  Subflow_*      2017 / 2018: an exact copy of the matching total (2018: equal in 100% of flows; 2017: identical
                 quantile curves). UNSW: averaged per sub-flow, ~96% zero.            -> RECOMPUTED as in 2017
                 (Subflow_Fwd_Packets := Total_Fwd_Packets, ... ; exact, the 2017 definition is known)
  *_Flag_Count   2017 / 2018: 0/1 values with the old extractor's own (undocumented, partly faulty) rule, e.g. SYN
                 present in only 4.6% of 2018 flows. UNSW: real counts (ACK up to 23,030). The old rule cannot be
                 rebuilt from the UNSW columns (binarising gives FIN 85% vs 0.3%).    -> treated as UNAVAILABLE = 0,
                 the same rule the pipeline uses for every feature a target dataset does not provide.
Everything else is unchanged. Pre-registered: the harmonised cache is the PRIMARY UNSW test, the raw cache a
sensitivity analysis.

  python harmonize_unsw.py --inp "D:/revised model/unsw/unsw_sample_v1.npz" --out "D:/revised model/unsw/unsw_sample_v1h.npz"
"""
import argparse, hashlib, os
import numpy as np

SUBFLOW = {"Subflow_Fwd_Packets": "Total_Fwd_Packets", "Subflow_Bwd_Packets": "Total_Backward_Packets",
           "Subflow_Fwd_Bytes": "Total_Length_of_Fwd_Packets", "Subflow_Bwd_Bytes": "Total_Length_of_Bwd_Packets"}
FLAG_COUNTS = ["FIN_Flag_Count", "SYN_Flag_Count", "RST_Flag_Count", "PSH_Flag_Count", "ACK_Flag_Count",
               "URG_Flag_Count", "CWE_Flag_Count", "ECE_Flag_Count"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", default="D:/revised model/unsw/unsw_sample_v1.npz")
    ap.add_argument("--out", default="D:/revised model/unsw/unsw_sample_v1h.npz")
    a = ap.parse_args()
    z = np.load(a.inp, allow_pickle=True)
    d = {k: z[k] for k in z.files}
    cols = list(d["cols"])
    X = d["X"].copy()
    log = []
    for s, t in SUBFLOW.items():
        if s in cols and t in cols:
            before = float((X[:, cols.index(s)] == X[:, cols.index(t)]).mean())
            X[:, cols.index(s)] = X[:, cols.index(t)]
            log.append(f"{s} := {t}   (equal before: {before:.1%})")
        else:
            log.append(f"{s}: column missing, unchanged")
    for f in FLAG_COUNTS:
        if f in cols:
            nz = float((X[:, cols.index(f)] != 0).mean())
            X[:, cols.index(f)] = 0.0
            log.append(f"{f} := 0 (unavailable)   (non-zero before: {nz:.1%})")
    d["X"] = X
    d["harmonised"] = np.array(log)
    np.savez(a.out, **d)
    print("\n".join(log))
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    print(f"\nsaved -> {a.out}\nsha256 harmonised cache {sha(a.out)[:16]} | harmonize_unsw.py "
          f"{sha(os.path.abspath(__file__))[:16]} | raw cache {sha(a.inp)[:16]}")


if __name__ == "__main__":
    main()
