"""
portscan_audit.py - what are the CIC-IDS2017 flows that the stage-1 cleaning removed as CONFLICTING, and why?
Reads files only: nothing is trained, nothing is changed.

count_manifest.py showed HOW MANY were removed (PortScan 158,930 -> 1,850; 76,265 conflicting, 80,689 duplicates;
90,130 would stay if Destination_Port were part of the duplicate check). This script shows WHAT they are:
  1  every label: rows, DISTINCT flow vectors (the model features, Destination_Port excluded as in the final run),
     vectors that also occur with another label (conflicts), vectors kept. kept must equal the clean count.
  2  conflicts: for the rows of each label, which OTHER labels carry the identical vector.
  per audited label (default PortScan, DoS Hulk, Bot = the three labels with BENIGN conflicts):
  3  status of its rows (NaN/inf, conflict, duplicate, kept), feature profile per status, distinct destination ports
     per status, the most frequent vectors with their label mix.
  4  the BENIGN rows that carry a vector of that label ("partners"): capture file, source host (are they the hosts
     that send the label's own rows? 172.16.0.1 is the attacker of 12 of the 14 attack types), time (inside the
     labelled attack window or not), destination ports.
     -> other hosts: flows that also occur in normal traffic (cannot be told apart without context);
        the label's hosts inside the window: attack flows labelled BENIGN in the attack window;
        the label's hosts outside the window: traffic of those hosts that is not labelled at all (unlabelled attack?).
  5  where the kept rows of that label are in splits.npz (train / val / test).
The cleaning is the code of stage1_cicids2017_pipeline.py (load_raw + the steps of clean()), as in count_manifest.py.

Run it in the folder that holds stage1_cicids2017_pipeline.py (D:/revised model):
  python portscan_audit.py
  python portscan_audit.py --labels "SSH-Patator"           (other labels, comma separated)
Everything printed is also written to --out_dir/audit_log.txt, the tables to CSV files there.
"""
import argparse, json, os, re, sys, time
import numpy as np
import pandas as pd

ATTACKER = "172.16.0.1"
PROFILE = ["Total_Fwd_Packets", "Total_Backward_Packets", "Total_Length_of_Fwd_Packets",
           "Total_Length_of_Bwd_Packets", "Flow_Duration", "Flow_IAT_Mean", "Init_Win_bytes_forward",
           "Init_Win_bytes_backward", "SYN_Flag_Count", "RST_Flag_Count", "ACK_Flag_Count", "PSH_Flag_Count",
           "FIN_Flag_Count"]
SHOW = ("Total_Fwd_Packets", "Total_Backward_Packets", "Total_Length_of_Fwd_Packets", "Total_Length_of_Bwd_Packets",
        "Flow_Duration")
LOG = []


def say(*x):
    s = " ".join(str(v) for v in x)
    print(s, flush=True)
    LOG.append(s)


def tag_of(label):
    return re.sub(r"[^A-Za-z0-9]+", "_", label).strip("_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_glob", default="D:/revised model/GeneratedLabelledFlows(1)/**/*.csv")
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--labels", default="PortScan,DoS Hulk,Bot", help="labels to audit, comma separated")
    ap.add_argument("--top", type=int, default=10, help="most frequent vectors to show per label")
    ap.add_argument("--code_dir", default=".")
    ap.add_argument("--out_dir", default="D:/revised model/manifest/audit")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    labels = [x.strip() for x in a.labels.split(",") if x.strip()]
    say(f"portscan_audit.py  {time.strftime('%Y-%m-%d %H:%M')}  labels audited: {labels}")
    try:
        run(a, labels)
    finally:
        with open(os.path.join(a.out_dir, "audit_log.txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(LOG) + "\n")
        print(f"\nwritten to {a.out_dir}: audit_log.txt and the CSV tables")


def run(a, labels):
    sys.path.insert(0, os.path.abspath(a.code_dir))
    try:
        import stage1_cicids2017_pipeline as s1
    except ImportError as e:
        raise SystemExit(f"stage1_cicids2017_pipeline.py not found in {os.path.abspath(a.code_dir)} ({e})")
    port_kept = False
    fn = os.path.join(a.s17_dir, "feature_names.json")
    if os.path.exists(fn):
        with open(fn) as fh:
            port_kept = "Destination_Port" in json.load(fh)
    say(f"duplicate check on the flow features {'WITH' if port_kept else 'WITHOUT'} Destination_Port "
        f"(as in {a.s17_dir})")

    t0 = time.time()
    df = s1.load_raw(a.data_glob)
    say(f"loaded {len(df):,} rows [{time.time() - t0:.0f}s]")
    # ---- the steps of s1.clean()
    lab_c = next((c for c in df.columns if c.lower() == "label"), None)
    df = df.rename(columns={lab_c: "label"})
    df = df.drop(columns=[c for c in df.columns if re.search(r"\.\d+$", c) and re.sub(r"\.\d+$", "", c) in df.columns])
    df = df[df["label"].notna()].reset_index(drop=True)
    attack = df["label"].astype(str).str.strip().str.replace(r"[^\x20-\x7E]+", "-", regex=True)
    y = (~attack.str.upper().isin(["BENIGN", "0"])).astype(np.int8).values
    lab = np.where(y == 0, "BENIGN", attack.values).astype(object)
    missing = [L for L in labels if L not in set(lab)]
    if missing:
        raise SystemExit(f"labels {missing} not in the data; labels: {sorted(set(lab))}")
    feats = [c for c in df.columns if c not in s1.ID_COLS and c != "label"]
    if not port_kept and "Destination_Port" in feats:
        feats.remove("Destination_Port")
    X = df[feats].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    port = pd.to_numeric(df["Destination_Port"], errors="coerce").values if "Destination_Port" in df else None
    src = df["Source_IP"].astype(str).values if "Source_IP" in df else np.full(len(df), "")
    ts = (pd.to_datetime(df["ts"]).values if "ts" in df else np.full(len(df), np.datetime64("NaT"), "datetime64[ns]"))
    fil = df["source_file"].astype(str).values
    del df
    ok = X.notna().all(axis=1).values
    flow_cols = [c for c in X.columns if not c.startswith(("win_", "pw_", "gl_"))]
    prof = [c for c in PROFILE if c in X.columns]
    benign = lab == "BENIGN"
    hh = np.zeros(len(lab), dtype="uint64")
    hh[ok] = pd.util.hash_pandas_object(X.loc[ok, flow_cols], index=False).values
    say(f"{len(flow_cols)} columns in the duplicate check (constant columns included; they do not change equality)")
    t = pd.DataFrame({"h": hh[ok], "lab": lab[ok]})
    nlab = t.groupby("h")["lab"].transform("nunique").values
    conflict = np.zeros(len(lab), bool); conflict[ok] = nlab > 1
    dupl = np.zeros(len(lab), bool); dupl[ok] = t.duplicated(["h", "lab"]).values
    keep = ok & ~conflict & ~dupl
    status = np.where(~ok, "nan_inf", np.where(conflict, "conflict", np.where(dupl, "duplicate", "kept")))
    target = {L: lab == L for L in labels}
    part = {L: ok & benign & conflict & np.isin(hh, np.unique(hh[ok & target[L] & conflict])) for L in labels}
    use = ok & np.logical_or.reduce([target[L] | part[L] for L in labels])
    idx = np.flatnonzero(use)
    P = pd.DataFrame(X.loc[use, prof].values, columns=prof, index=idx)   # profiles: audited labels + partners only
    del X
    P["status"], P["lab"] = status[idx], lab[idx]
    pk = [c for c in ("Total_Fwd_Packets", "Total_Backward_Packets") if c in prof]
    if len(pk) == 2:
        P["packets"] = P[pk[0]] + P[pk[1]]

    # ---- 1. distinct vectors per label
    say("\n[1] rows and DISTINCT flow vectors per label")
    rows = []
    for L, g in t.assign(shared=nlab > 1).groupby("lab"):
        d = g.h.nunique()
        s = g.loc[g.shared, "h"].nunique()
        rows.append(dict(label=L, rows=int((lab == L).sum()), rows_valid=len(g), distinct_vectors=d,
                         vectors_shared_with_other_label=s, kept=d - s, kept_check=int((keep & (lab == L)).sum())))
    T1 = pd.DataFrame(rows).set_index("label").sort_values("rows", ascending=False)
    T1["rows_per_vector"] = (T1.rows_valid / T1.distinct_vectors).round(1)
    say(T1.to_string())
    say("check kept == kept_check (stage-1 rule): " + ("yes for every label" if (T1.kept == T1.kept_check).all()
                                                       else "NO -> " + str(T1.index[T1.kept != T1.kept_check].tolist())))
    T1.to_csv(os.path.join(a.out_dir, "audit_labels.csv"))

    # ---- 2. which labels share vectors (conflicts)
    say("\n[2] conflicts: rows of a label (row) whose vector also occurs with another label (column)")
    comp = t[nlab > 1].groupby(["h", "lab"]).size().unstack(fill_value=0)
    present = comp > 0
    M = pd.DataFrame(0, index=comp.columns, columns=comp.columns, dtype="int64")
    for L in comp.columns:
        has = present[L]
        M.loc[L] = present[has].astype("int64").mul(comp.loc[has, L], axis=0).sum()
        M.loc[L, L] = 0
    M = M.loc[M.sum(axis=1) > 0, M.sum(axis=0) > 0]
    say(M.to_string())
    M.to_csv(os.path.join(a.out_dir, "audit_conflict_pairs.csv"))
    tt = t.assign(row=np.flatnonzero(ok))

    for L in labels:
        audit_label(a, L, target[L], part[L], ok, conflict, keep, status, hh, tt, P, prof, port, src, ts, fil)


def audit_label(a, L, target, part, ok, conflict, keep, status, hh, tt, P, prof, port, src, ts, fil):
    tag = tag_of(L)
    say(f"\n{'=' * 100}\n[3] {L}: status of its {int(target.sum()):,} rows")
    say(pd.Series(status[target]).value_counts().to_string())
    if port is not None:
        h2 = (hh * np.uint64(0x9E3779B97F4A7C15)) ^ pd.util.hash_array(np.where(np.isnan(port), -1.0, port))
        t2 = pd.DataFrame({"h": h2[ok], "lab": tt.lab.values})
        k2 = np.zeros(len(hh), bool)
        k2[ok] = ~((t2.groupby("h")["lab"].transform("nunique") > 1).values | t2.duplicated(["h", "lab"]).values)
        say(f"  kept if Destination_Port were in the check: {int((k2 & target).sum()):,}")
        n_ports = pd.DataFrame({"st": status[target], "p": port[target]}).groupby("st")["p"].nunique()
        say("  distinct destination ports per status: " + ", ".join(f"{k} {v:,}" for k, v in n_ports.items())
            + f";  all rows: {pd.Series(port[target]).nunique():,}")
    pt = P[P.lab == L]
    cols = prof + (["packets"] if "packets" in P else [])
    agg = pt.groupby("status")[cols].median().T.astype("float64").round(2)
    if "packets" in P:
        agg.loc["share_le2"] = pt.groupby("status")["packets"].apply(lambda s: (s <= 2).mean()).round(3)
    agg.loc["rows"] = pt.groupby("status").size()
    say(f"\n  feature profile of {L} per status (median; share_le2 = share of flows with <= 2 packets):")
    say(agg.to_string())
    agg.to_csv(os.path.join(a.out_dir, f"audit_{tag}_profile.csv"))

    say(f"\n  the {a.top} most frequent {L} vectors (rows with this exact vector, per label):")
    top = tt[tt.lab == L].h.value_counts().head(a.top)
    out = []
    for i, (h, n) in enumerate(top.items(), 1):
        g = tt[tt.h == h]
        mix = g.lab.value_counts()
        r0 = g.loc[g.lab == L, "row"].values[0]
        r = dict(rank=i, **{L: int(n)}, BENIGN=int(mix.get("BENIGN", 0)),
                 other=int(mix.drop([L, "BENIGN"], errors="ignore").sum()),
                 dst_ports=int(pd.Series(port[g.row.values]).nunique()) if port is not None else None,
                 status="conflict" if len(mix) > 1 else "duplicate/kept")
        r.update({c: P.at[r0, c] for c in SHOW if c in prof})
        out.append(r)
    T3 = pd.DataFrame(out).set_index("rank")
    say(T3.to_string())
    nv = int((target & ok).sum())
    say(f"  these {len(top)} vectors hold {int(top.sum()):,} of the {nv:,} valid {L} rows ({top.sum() / max(nv, 1):.1%})")
    T3.to_csv(os.path.join(a.out_dir, f"audit_{tag}_top_vectors.csv"))

    # ---- 4. the BENIGN partners
    say(f"\n[4] BENIGN rows with exactly the same vector as some {L} row: {int(part.sum()):,} "
        f"(they make {int((target & conflict).sum()):,} {L} rows 'conflicting')")
    if part.any():
        tw = pd.DataFrame({"f": fil[target], "ts": ts[target]}).dropna().groupby("f")["ts"].agg(["min", "max"])
        say(f"  labelled time window of {L} per file:\n" + tw.to_string())
        B = pd.DataFrame({"file": fil[part], "src": src[part], "ts": ts[part],
                          "port": port[part] if port is not None else np.nan})
        own = pd.Series(src[target]).value_counts(normalize=True)
        hosts = own[own >= 0.01]                                 # the label's own source hosts (>= 1% of its rows)
        say("  source hosts of the " + L + " rows themselves (>= 1%): "
            + ", ".join(f"{k} {v:.0%}" for k, v in hosts.items()))
        B["attacker_src"] = B.src.isin(hosts.index)
        B["in_window"] = False
        for f, w in tw.iterrows():
            B.loc[(B.file == f) & (B.ts >= w["min"]) & (B.ts <= w["max"]), "in_window"] = True
        T4 = B.groupby("file").agg(rows=("src", "size"), from_attack_hosts=("attacker_src", "sum"),
                                   in_attack_window=("in_window", "sum"), first=("ts", "min"), last=("ts", "max"),
                                   minutes=("ts", "nunique"), dst_ports=("port", "nunique"))
        say(T4.to_string())
        A, W = B.attacker_src.mean(), B.in_window.mean()
        say(f"  share from the {L} source hosts: {A:.1%} (from {ATTACKER}: {(B.src == ATTACKER).mean():.1%});  "
            f"inside the labelled {L} window: {W:.1%};  "
            f"distinct source hosts: {B.src.nunique():,};  distinct destination ports: {B.port.nunique():,}")
        say("  top source hosts: " + ", ".join(f"{k} {v:,}" for k, v in B.src.value_counts().head(5).items()))
        say("  busiest minutes: " + ", ".join(f"{pd.Timestamp(k):%a %d %H:%M} {v:,}"
                                              for k, v in B.ts.value_counts().head(8).items()))
        say("  top destination ports: " + ", ".join(f"{int(k)} {v:,}" for k, v in B.port.value_counts().head(8).items()))
        pb = P[(P.lab == "BENIGN") & P.index.isin(np.flatnonzero(part))]
        if len(pb):
            say("  their feature profile (median): " + ", ".join(f"{c} {pb[c].median():g}" for c in SHOW if c in pb)
                + (f", share_le2 {(pb['packets'] <= 2).mean():.3f}" if "packets" in pb else ""))
        if A < 0.2:
            say("  READING: partners come from other hosts -> the removed flows also occur in normal traffic; "
                "without context they cannot be told apart.")
        elif A >= 0.8 and W >= 0.8:
            say("  READING: partners come from the label's own source hosts inside the labelled window -> attack "
                "flows labelled BENIGN (label noise inside the attack window).")
        elif A >= 0.8:
            say("  READING: partners come from the label's own source hosts but OUTSIDE the labelled window -> "
                "traffic of those hosts that was never labelled (possibly an unlabelled attack); see minutes and ports.")
        else:
            say("  READING: mixed sources -> both generic flows and attacker traffic; see the table.")
        B.to_csv(os.path.join(a.out_dir, f"audit_{tag}_benign_partners.csv"), index=False)

    # ---- 5. kept rows in the splits
    spl = os.path.join(a.s17_dir, "splits.npz")
    if os.path.exists(spl):
        z = np.load(spl, allow_pickle=True)
        n = {s: int((z[f"a{s}"].astype(str) == L).sum()) for s in ("tr", "va", "te")}
        say(f"\n[5] {L} in {spl}: train {n['tr']:,}  val {n['va']:,}  test {n['te']:,}  "
            f"(total {sum(n.values()):,}; kept above {int((keep & target).sum()):,})")


if __name__ == "__main__":
    main()
