"""
Do the 2017, 2018 and UNSW features MEAN the same thing? check_saturation.py on the UNSW cache showed two groups that
look like differences of the CICFlowMeter VERSION (not of the network):
  - Subflow_* : ~96% zero in UNSW (2017: Subflow_Fwd_Packets never below its minimum)
  - *_Flag_Count : most UNSW values ABOVE the 2017 maximum (ACK 85%, SYN 65%, PSH 54%, FIN 13%)
This script checks the suspected meaning in every dataset, using labels nowhere:
  1. Is Subflow_X a copy of the matching total (Total_Fwd_Packets, ...)? 2017: from the quantiles stored in the 2017
     transformer (identical quantile curves); 2018 / UNSW: share of flows where the two values are equal.
  2. Are the flag counts 0/1 indicators in 2017 / 2018 (maximum 1) but real counts in UNSW?
  3. For reference: share of zeros in the minimum-packet-length and Active / Idle features.

  python check_extractor.py --s17_dir "D:/revised model/stage1_pw" --c18 "D:/revised model/cross_out4/ids2018_sample_v4.npz" --unsw "D:/revised model/unsw/unsw_sample_v1.npz"
"""
import argparse, json, os
import numpy as np
import pandas as pd

PAIRS = [("Subflow_Fwd_Packets", "Total_Fwd_Packets"), ("Subflow_Bwd_Packets", "Total_Backward_Packets"),
         ("Subflow_Fwd_Bytes", "Total_Length_of_Fwd_Packets"), ("Subflow_Bwd_Bytes", "Total_Length_of_Bwd_Packets")]
FLAGS = ["FIN_Flag_Count", "SYN_Flag_Count", "RST_Flag_Count", "PSH_Flag_Count", "ACK_Flag_Count", "URG_Flag_Count",
         "CWE_Flag_Count", "ECE_Flag_Count", "Fwd_PSH_Flags", "Fwd_URG_Flags"]
ZEROS = ["Fwd_Packet_Length_Min", "Bwd_Packet_Length_Min", "Min_Packet_Length", "Active_Mean", "Idle_Mean"]


def frame(path):
    z = np.load(path, allow_pickle=True)
    return pd.DataFrame(z["X"], columns=list(z["cols"])), z["lab"].astype(str)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--c18", default="D:/revised model/cross_out4/ids2018_sample_v4.npz")
    ap.add_argument("--unsw", default="D:/revised model/unsw/unsw_sample_v1.npz")
    a = ap.parse_args()
    import joblib
    feats = json.load(open(os.path.join(a.s17_dir, "feature_names.json")))
    qt = joblib.load(os.path.join(a.s17_dir, "quantile_transformer.joblib"))
    Q = pd.DataFrame(qt.quantiles_, columns=feats)                   # 2017 quantile curves (training data)
    D18, _ = frame(a.c18)
    DU, _ = frame(a.unsw)
    print("1. SUBFLOW = TOTAL ?   (2017: max |difference| of the two quantile curves; 2018 / UNSW: share equal)")
    for s, t in PAIRS:
        q = float(np.abs(Q[s] - Q[t]).max()) if s in Q and t in Q else np.nan
        e18 = float((D18[s] == D18[t]).mean()) if s in D18 and t in D18 else np.nan
        eu = float((DU[s] == DU[t]).mean()) if s in DU and t in DU else np.nan
        z18 = float((D18[s] == 0).mean()) if s in D18 else np.nan
        print(f"  {s:22s} vs {t:28s} 2017 quantile diff {q:10.4g} | 2018 equal {e18:6.1%} | UNSW equal {eu:6.1%} "
              f"(2018 zero {z18:5.1%}, UNSW zero {float((DU[s] == 0).mean()):5.1%})")
    print("\n2. FLAG COUNTS: maximum and share of values > 1")
    for f in FLAGS:
        if f not in Q:
            continue
        mx17 = float(Q[f].iloc[-1])
        print(f"  {f:16s} 2017 max {mx17:6.3g} (distinct quantile values {Q[f].nunique():3d}) | "
              f"2018 max {D18[f].max():6.3g}, >1 {float((D18[f] > 1).mean()):6.1%} | "
              f"UNSW max {DU[f].max():8.4g}, >1 {float((DU[f] > 1).mean()):6.1%}, >0 {float((DU[f] > 0).mean()):6.1%} "
              f"(2018 >0 {float((D18[f] > 0).mean()):6.1%})")
    print("\n3. share of ZEROS (reference)")
    for f in ZEROS:
        if f not in Q:
            continue
        z17 = float((Q[f] == 0).mean())                              # share of 2017 quantile levels at 0 ~ share of zeros
        print(f"  {f:22s} 2017 ~{z17:5.1%} | 2018 {float((D18[f] == 0).mean()):5.1%} | UNSW {float((DU[f] == 0).mean()):5.1%}")


if __name__ == "__main__":
    main()
