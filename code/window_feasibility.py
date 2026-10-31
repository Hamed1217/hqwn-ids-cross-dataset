"""
Step-1 data check for the window (multi-flow, behavioural) approach.  Run it on the RAW GeneratedLabelledFlows CSVs.

Only COUNTS and distinct-counts are used as window features, never IP identities, so there is no identity shortcut
(the attacker / victim addresses of CIC-IDS2017 are fixed and must not become features).

For every CSV (= one capture day) it
  1. reports the timestamp resolution (this limits how fine a window can be) ;
  2. builds behavioural window features inside fixed time bins (--bin_s, default 60 s):
       f_src_flows       flows from the same Source_IP in the bin
       f_src_dports      distinct Destination_Port values from that Source_IP in the bin       (port scan)
       f_src_dips        distinct Destination_IP values from that Source_IP in the bin          (sweep)
       f_pair_flows      flows of the same (Source_IP, Destination_IP) in the bin
       f_pair_dports     distinct Destination_Port values of that pair in the bin               (port scan)
       f_pairport_flows  flows of the same (Source_IP, Destination_IP, Destination_Port) in the bin   (brute force)
       f_dst_flows       flows to the same Destination_IP in the bin                            (DDoS)
       f_dst_srcs        distinct Source_IP values reaching that Destination_IP in the bin      (DDoS)
       f_grp_day         flows of the (src, dst, dst-port) group in the whole file               (beaconing)
       f_grp_bins        number of distinct bins in which that group is active
       f_grp_duty        f_grp_bins / (last active bin - first active bin + 1)                   (steady = bot-like)
  3. for each attack family: single-feature ROC-AUC (attack flows vs the BENIGN flows of the same day) of every window
     feature and of every single-flow feature (Destination_Port excluded, like the no-port experiments);
  4. window-size statistics for the attack flows;
  5. cluster analysis of selected families in per-flow feature space (default DDoS, FTP-Patator, PortScan):
     cluster sizes, medians, and the share of flows that sit as close to benign traffic as benign flows sit to each other.

Single-feature AUC understates what a model can do with several features, and the bins are NOT causal (they include
flows later in the same bin). It is a feasibility check, not a result: the real test is step 2 (XGBoost with causal window
features in the leave-one-attack-out experiment).

Usage (Windows, same folder as the other scripts):
  python window_feasibility.py --data_glob "D:/revised model/GeneratedLabelledFlows(1)/**/*.csv" --out_dir window_check
  (add --files Friday to run only the files whose name contains "Friday"; first run on one file to test)
Output: window_check/report.txt and window_check/auc_summary.csv  -> send report.txt
"""
import argparse, glob, os, re, time, warnings
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import QuantileTransformer

NON_FLOW = {"Flow_ID", "Source_IP", "Source_Port", "Destination_IP", "Destination_Port", "Timestamp", "ts", "label",
            "source_file"}
KEY_COLS = ["Flow_Duration", "Total_Fwd_Packets", "Total_Backward_Packets", "Total_Length_of_Fwd_Packets",
            "Total_Length_of_Bwd_Packets", "Flow_Bytes/s", "Flow_Packets/s", "Fwd_Packet_Length_Mean",
            "Init_Win_bytes_forward", "Init_Win_bytes_backward"]
REPORT = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    REPORT.append(s)


# ----------------------------------------------------------------------------- loading
def fix_timestamp(raw):
    """Same rule as stage 1: day/month/year on a 12-hour clock WITHOUT am/pm; hours 1..7 are afternoon -> +12 h."""
    ts = pd.to_datetime(raw, errors="coerce", dayfirst=True, format="mixed")
    return ts + pd.to_timedelta(np.where(ts.dt.hour.between(1, 7), 12, 0), unit="h")


def read_day(path):
    d = pd.read_csv(path, low_memory=False, encoding_errors="replace")
    d.columns = [re.sub(r"\s+", "_", str(c).strip()) for c in d.columns]
    lab = next((c for c in d.columns if c.lower() == "label"), None)
    if lab is None:
        raise KeyError(f"no Label column in {path}")
    d = d.rename(columns={lab: "label"})
    d = d[d["label"].notna()].copy()
    d["label"] = (d["label"].astype(str).str.replace(r"[^\x20-\x7E]+", "-", regex=True).str.strip())
    for c in ("Source_IP", "Destination_IP", "Destination_Port", "Timestamp"):
        if c not in d.columns:
            raise KeyError(f"column {c} missing in {path}; columns: {list(d.columns)[:12]} ...")
    d["ts"] = fix_timestamp(d["Timestamp"])
    d = d[d["ts"].notna()].reset_index(drop=True)
    return d


# ----------------------------------------------------------------------------- window features (counts only)
def composite(*codes):
    k = codes[0].astype("int64")
    for c in codes[1:]:
        card = int(c.max()) + 1
        k = pd.factorize(k * card + c.astype("int64"))[0].astype("int64")
    return k


def count_in(k):
    _, inv, c = np.unique(k, return_inverse=True, return_counts=True)
    return c[np.ravel(inv)].astype("float32")


def distinct_in(k, v):
    v = v.astype("int64")
    card = int(v.max()) + 1
    ukv = np.unique(k * card + v)
    uk, ck = np.unique(ukv // card, return_counts=True)
    return ck[np.searchsorted(uk, k)].astype("float32")


def window_features(d, bin_s):
    sec = ((d["ts"] - d["ts"].min()) // pd.Timedelta(seconds=1)).astype("int64").values
    b = (sec // bin_s).astype("int64")
    src = pd.factorize(d["Source_IP"])[0].astype("int64")
    dst = pd.factorize(d["Destination_IP"])[0].astype("int64")
    dpt = pd.to_numeric(d["Destination_Port"], errors="coerce").fillna(-1).astype("int64").values + 1
    k_sb, k_db = composite(src, b), composite(dst, b)
    k_pb, k_ppb = composite(src, dst, b), composite(src, dst, dpt, b)
    g = composite(src, dst, dpt)
    F = pd.DataFrame({
        "f_src_flows": count_in(k_sb), "f_src_dports": distinct_in(k_sb, dpt), "f_src_dips": distinct_in(k_sb, dst),
        "f_pair_flows": count_in(k_pb), "f_pair_dports": distinct_in(k_pb, dpt),
        "f_pairport_flows": count_in(k_ppb),
        "f_dst_flows": count_in(k_db), "f_dst_srcs": distinct_in(k_db, src),
        "f_grp_day": count_in(g), "f_grp_bins": distinct_in(g, b)})
    tmp = pd.DataFrame({"g": g, "b": b}).groupby("g")["b"].agg(["min", "max"])
    span = (tmp["max"] - tmp["min"] + 1).reindex(g).values.astype("float32")
    F["f_grp_duty"] = (F["f_grp_bins"].values / span).astype("float32")
    return F


def flow_matrix(d):
    cols = [c for c in d.columns if c not in NON_FLOW]
    S = d[cols].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    S = S.loc[:, S.notna().any()]
    return S.fillna(S.median()).astype("float32")


# ----------------------------------------------------------------------------- AUC
def auc_of(F, y, idx):
    out = {}
    for c in F.columns:
        x = F[c].values[idx]
        if np.nanmin(x) == np.nanmax(x):
            continue
        try:
            out[c] = float(roc_auc_score(y, x))
        except ValueError:
            pass
    return out


def top(aucs, n):
    items = sorted(aucs.items(), key=lambda kv: -abs(kv[1] - 0.5))[:n]
    return [(k, v, "higher=attack" if v >= 0.5 else "lower=attack") for k, v in items]


def window_stats(W, mask_att, mask_ben):
    rows = []
    for c in ("f_src_flows", "f_dst_flows", "f_pair_flows", "f_pairport_flows", "f_src_dports", "f_dst_srcs"):
        a, bn = W[c].values[mask_att], W[c].values[mask_ben]
        rows.append(dict(feature=c, att_median=np.median(a), att_p10=np.percentile(a, 10),
                         att_share_ge5=(a >= 5).mean(), att_share_ge20=(a >= 20).mean(), benign_median=np.median(bn)))
    return pd.DataFrame(rows).set_index("feature").round(3)


# ----------------------------------------------------------------------------- cluster analysis
def cluster_report(S, att_mask, ben_mask, fam, k, seed):
    rng = np.random.default_rng(seed)
    fi, bi = np.where(att_mask)[0], np.where(ben_mask)[0]
    fi = rng.choice(fi, min(len(fi), 15000), replace=False)
    bi = rng.choice(bi, min(len(bi), 53000), replace=False)
    Sx = S.drop(columns=[c for c in S.columns if S[c].iloc[np.r_[fi, bi]].nunique() <= 1])
    n_ref, n_qry = min(20000, int(0.4 * len(bi))), min(3000, int(0.06 * len(bi)))
    ref_i, qry_i, fit_i = bi[:n_ref], bi[n_ref:n_ref + n_qry], bi[n_ref + n_qry:]
    qt = QuantileTransformer(n_quantiles=min(1000, len(fit_i)), output_distribution="normal", subsample=200000,
                             random_state=seed).fit(Sx.iloc[fit_i].values)
    T = lambda ix: qt.transform(Sx.iloc[ix].values)
    Tf, Tr, Tq = T(fi), T(ref_i), T(qry_i)
    nn = NearestNeighbors(n_neighbors=1).fit(Tr)
    dq = nn.kneighbors(Tq)[0][:, 0]
    df_ = nn.kneighbors(Tf)[0][:, 0]
    thr50, thr90 = np.median(dq), np.percentile(dq, 90)
    lab = KMeans(n_clusters=k, n_init=5, random_state=seed).fit_predict(Tf)
    P(f"  --- {fam}: {len(fi)} flows sampled, {k} clusters; benign-to-benign nearest-neighbour distance: "
      f"median {thr50:.2f}, p90 {thr90:.2f}")
    rows = []
    for c in range(k):
        m = lab == c
        rows.append(dict(cluster=c, share=m.mean(), n=int(m.sum()),
                         near_benign_median=(df_[m] <= thr50).mean(), near_benign_p90=(df_[m] <= thr90).mean(),
                         nn_dist_median=np.median(df_[m])))
    P(pd.DataFrame(rows).set_index("cluster").round(3).to_string())
    keys = [c for c in KEY_COLS if c in S.columns]
    med = pd.DataFrame([S.iloc[fi[lab == c]][keys].median() for c in range(k)] + [S.iloc[ref_i][keys].median()],
                       index=[f"cluster{c}" for c in range(k)] + ["benign"])
    P("  medians of raw flow features:")
    P(med.round(2).T.to_string())
    P(f"  overall share of {fam} flows as close to benign as benign is to benign (<= median): "
      f"{(df_ <= thr50).mean():.3f}; (<= p90): {(df_ <= thr90).mean():.3f}")


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_glob", default="D:/revised model/GeneratedLabelledFlows(1)/**/*.csv")
    ap.add_argument("--out_dir", default="window_check")
    ap.add_argument("--bin_s", type=int, default=60, help="window length in seconds (>= timestamp resolution)")
    ap.add_argument("--files", default="", help="only files whose name contains this text")
    ap.add_argument("--cluster_fams", default="DDoS,FTP-Patator,PortScan")
    ap.add_argument("--k", type=int, default=2)
    ap.add_argument("--max_ben", type=int, default=200000, help="benign flows used per AUC computation")
    ap.add_argument("--min_fam", type=int, default=30, help="skip families with fewer flows")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    warnings.filterwarnings("ignore")
    os.makedirs(a.out_dir, exist_ok=True)
    files = [f for f in sorted(glob.glob(a.data_glob, recursive=True)) if a.files in os.path.basename(f)]
    if not files:
        raise FileNotFoundError(f"no CSV matched {a.data_glob} with --files '{a.files}'")
    cl_fams = {s.strip() for s in a.cluster_fams.split(",") if s.strip()}
    rng = np.random.default_rng(a.seed)
    summary = []
    t0 = time.time()
    P(f"window check | bin_s={a.bin_s} | files={len(files)}")
    for f in files:
        P("\n" + "=" * 100 + f"\nFILE {os.path.basename(f)}")
        d = read_day(f)
        nz = (d["ts"].dt.second != 0).mean()
        P(f"rows {len(d)} | timestamp range {d['ts'].min()} .. {d['ts'].max()} | rows with non-zero seconds: {nz:.1%} "
          f"| distinct timestamps: {d['ts'].nunique()}")
        if nz < 0.05 and a.bin_s < 60:
            P("  WARNING: timestamps have 1-minute resolution -> bins shorter than 60 s are meaningless")
        P("labels:", d["label"].value_counts().to_dict())
        W = window_features(d, a.bin_s)
        S = flow_matrix(d)
        lab = d["label"].values
        ben_all = np.where(lab == "BENIGN")[0]
        if len(ben_all) == 0:
            P("  no benign flows in this file -> AUC skipped")
        for fam in sorted(set(lab) - {"BENIGN"}):
            fi = np.where(lab == fam)[0]
            P(f"\n  FAMILY {fam}: {len(fi)} attack flows, {len(ben_all)} benign flows in this file")
            if len(fi) < a.min_fam or len(ben_all) == 0:
                P("    too few flows -> skipped")
                continue
            bi = rng.choice(ben_all, min(len(ben_all), a.max_ben), replace=False)
            idx = np.r_[fi, bi]
            y = np.r_[np.ones(len(fi)), np.zeros(len(bi))]
            aw, asf = auc_of(W, y, idx), auc_of(S, y, idx)
            P("    window features, single-feature AUC (|AUC-0.5| ranking):")
            for k_, v, dr in top(aw, 5):
                P(f"      {k_:18s} AUC={v:.3f}  ({dr})")
            P("    best single-flow features (Destination_Port excluded):")
            for k_, v, dr in top(asf, 3):
                P(f"      {k_:30s} AUC={v:.3f}  ({dr})")
            mask_a, mask_b = np.zeros(len(d), bool), np.zeros(len(d), bool)
            mask_a[fi], mask_b[ben_all] = True, True
            P("    window sizes (attack flows; benign median for reference):")
            P("      " + window_stats(W, mask_a, mask_b).to_string().replace("\n", "\n      "))
            bw, bf = top(aw, 1)[0], top(asf, 1)[0]
            summary.append(dict(file=os.path.basename(f), family=fam, n_attack=len(fi), n_benign=len(ben_all),
                                best_window_feature=bw[0], best_window_auc=max(bw[1], 1 - bw[1]),
                                best_flow_feature=bf[0], best_flow_auc=max(bf[1], 1 - bf[1])))
            if fam in cl_fams and len(fi) >= 200:
                try:
                    cluster_report(S, mask_a, mask_b, fam, a.k, a.seed)
                except Exception as e:                       # the cluster part must never kill the whole run
                    P(f"    cluster analysis failed: {type(e).__name__}: {e}")
        P(f"[elapsed {time.time() - t0:.0f}s]")

    P("\n" + "=" * 100 + "\nSUMMARY (direction-free AUC = max(AUC, 1-AUC); window = single best window feature, flow = single best flow feature)")
    if summary:
        T = pd.DataFrame(summary)
        T.to_csv(os.path.join(a.out_dir, "auc_summary.csv"), index=False)
        P(T.round(3).to_string(index=False))
    with open(os.path.join(a.out_dir, "report.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(REPORT))
    print(f"\nsaved -> {os.path.join(a.out_dir, 'report.txt')}")


if __name__ == "__main__":
    main()
