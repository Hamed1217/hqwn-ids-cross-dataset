"""
Stage 1 - CIC-IDS2017 (MachineLearningCVE-style CSVs) data pipeline + baselines.

What it does
  1. Loads all CSVs, normalises column names, drops the duplicated Fwd_Header_Length.1 column.
  2. Converts string labels (BENIGN / attack names) to binary y and keeps the attack type.
  3. Removes inf/NaN rows, exact duplicates and rows whose identical features carry conflicting labels.
  4. Drops constant columns and warns if the data looks pre-normalised (min-max scaled).
  5. Stratified 60/20/20 train/val/test split BEFORE any fitting (no leakage).
  6. Fits a QuantileTransformer on TRAIN only.
  7. Baselines (LogReg, HistGradientBoosting, XGBoost if installed); threshold is chosen on VAL only.
  8. Reports acc / precision / recall / F1 / FPR / ROC-AUC / PR-AUC + per-attack-type detection rate.
  9. Optional: leave-one-attack-out (unseen attack family) evaluation.
 10. CIC-IDS-2017 V2 (Abluva/Zenodo) contains a GAN-synthesised class "Comb". --comb_mode controls it:
       novel   (default) : removed from train/val/test; reported separately as a "novel synthetic attack" test
       exclude           : removed completely (benchmark on the real CIC-IDS2017 classes only)
       include           : treated as an ordinary attack class (NOT recommended for the main benchmark)

Usage
  python stage1_cicids2017_pipeline.py --data_glob "data/*.csv" --out_dir stage1_out
  (add --max_train 300000 for a fast first run, --leave_one_out for the unseen-attack test)
  GeneratedLabelledFlows (has Timestamp): --split blocked  = whole 1-minute time blocks per split
  (timestamps are 12-hour without am/pm; hours 1-7 are shifted +12 h, see fix_timestamp)
"""
import argparse, glob, json, os, re, warnings
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, confusion_matrix,
                             precision_recall_curve, precision_recall_fscore_support,
                             roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import QuantileTransformer

ID_COLS = {"Flow_ID", "Source_IP", "Source_Port", "Destination_IP", "Timestamp", "ts", "source_file", "__rid"}
_SEQ = {"parts": [], "all": None}        # 16-minute service-load sequences (--seq), aligned to raw rows by __rid


# ----------------------------------------------------------------------------- loading
def fix_timestamp(raw):
    """TrafficLabelling timestamps are day/month/year on a 12-hour clock WITHOUT am/pm.
    The capture ran during working hours (~08:00-17:30), so hours 1..7 are afternoon -> +12 h."""
    ts = pd.to_datetime(raw, errors="coerce", dayfirst=True, format="mixed")
    return ts + pd.to_timedelta(np.where(ts.dt.hour.between(1, 7), 12, 0), unit="h")


# ----------------------------------------------------------------------------- causal window features (counts only)
# Timestamps of GeneratedLabelledFlows have 1-MINUTE resolution, so a window is a number of minutes. The window of a
# flow at minute t covers minutes t-w+1 .. t of the SAME capture file (day) and uses only counts / distinct counts of
# the same Source_IP, Destination_IP or pair - never the IP identities. Order inside a minute is unknown, so a
# detection is available at the end of the minute (latency <= 1 min); nothing from later minutes is used.
def _composite(*codes):
    k = codes[0].astype("int64")
    for c in codes[1:]:
        card = int(c.max()) + 1
        k = pd.factorize(k * card + c.astype("int64"))[0].astype("int64")
    return k


def _lookup(ev_k, ev_v, rows_key):
    """running sum of the events (+v at start, -v at end) up to and including each row's key"""
    o = np.argsort(ev_k, kind="stable")
    ev_k, cum = ev_k[o], np.cumsum(ev_v[o])
    idx = np.searchsorted(ev_k, rows_key, side="right") - 1
    return np.where(idx >= 0, cum[np.maximum(idx, 0)], 0)


def _trail_count(K, m, w, T):
    key = K * T + m
    uk, c = np.unique(key, return_counts=True)
    return _lookup(np.r_[uk, uk + w], np.r_[c, -c], key)


def _trail_distinct(K, V, m, w, T):
    pair = _composite(K, V)
    u3 = np.unique(pair * T + m)
    p, mm = u3 // T, u3 % T
    first = np.unique(pair, return_index=True)[1]                    # pair ids are 0..n-1
    Kp = K[first][p]
    nxt = np.r_[mm[1:], 0]
    same = np.r_[p[1:] == p[:-1], False]
    end = np.where(same, np.minimum(mm + w - 1, nxt - 1), mm + w - 1)  # each (K,V) counted once per minute
    one = np.ones(len(mm), dtype="int64")
    return _lookup(np.r_[Kp * T + mm, Kp * T + end + 1], np.r_[one, -one], K * T + m)


def window_features_causal(src, dst, dport, minute, windows=(1, 5)):
    s = pd.factorize(src)[0].astype("int64")
    t = pd.factorize(dst)[0].astype("int64")
    p = pd.to_numeric(pd.Series(dport), errors="coerce").fillna(-1).astype("int64").values + 1
    m = np.asarray(minute).astype("int64")
    T = int(m.max()) + max(windows) + 2
    k_sd, k_sdp = _composite(s, t), _composite(s, t, p)
    out = {}
    for w in windows:
        out[f"win_src_flows_w{w}"] = _trail_count(s, m, w, T)
        out[f"win_src_dports_w{w}"] = _trail_distinct(s, p, m, w, T)
        out[f"win_src_dips_w{w}"] = _trail_distinct(s, t, m, w, T)
        out[f"win_dst_flows_w{w}"] = _trail_count(t, m, w, T)
        out[f"win_dst_srcs_w{w}"] = _trail_distinct(t, s, m, w, T)
        out[f"win_pair_flows_w{w}"] = _trail_count(k_sd, m, w, T)
        out[f"win_pair_dports_w{w}"] = _trail_distinct(k_sd, p, m, w, T)
        out[f"win_pairport_flows_w{w}"] = _trail_count(k_sdp, m, w, T)
    return pd.DataFrame({k: v.astype("float32") for k, v in out.items()})


def load_raw(pattern, win=None, pw=False, seq=False):
    files = sorted(glob.glob(pattern, recursive=True))
    if not files:
        raise FileNotFoundError(f"no CSV matched: {pattern}")
    parts = []
    for f in files:
        d = pd.read_csv(f, low_memory=False, encoding_errors="replace")
        d.columns = [re.sub(r"\s+", "_", str(c).strip()) for c in d.columns]
        lab = next((c for c in d.columns if c.lower() == "label"), None)
        if lab is not None:                      # blank rows (e.g. ~288k in the WebAttacks file) -> drop now, saves RAM
            d = d[d[lab].notna()]
        if "Timestamp" in d.columns:
            d["ts"] = fix_timestamp(d["Timestamp"])
        if win:                                  # window features need the IPs -> compute BEFORE they are dropped
            need = {"Source_IP", "Destination_IP", "Destination_Port", "ts"}
            if not need <= set(d.columns):
                raise KeyError(f"--window_feats needs columns {sorted(need)} (GeneratedLabelledFlows CSVs)")
            ts = d["ts"].fillna(d["ts"].min())
            minute = ((ts - ts.min()) // pd.Timedelta(minutes=1)).values
            W = window_features_causal(d["Source_IP"].values, d["Destination_IP"].values,
                                       d["Destination_Port"].values, minute, win)
            for c in W.columns:
                d[c] = W[c].values
        if pw:                                   # IP-free service-load windows (port_windows.py, shared with 2018)
            from port_windows import port_window_features
            need = {"Destination_Port", "ts", "Total_Backward_Packets"}
            if not need <= set(d.columns):
                raise KeyError(f"--port_windows needs columns {sorted(need)}")
            tsv = d["ts"]
            minute = ((tsv - tsv.min()) // pd.Timedelta(minutes=1)).values.astype("float64")
            zb = pd.to_numeric(d["Total_Backward_Packets"], errors="coerce").fillna(1).values == 0
            P = port_window_features(d["Destination_Port"].values, minute, zb, valid=tsv.notna().values)
            for c in P.columns:
                d[c] = P[c].values
        if seq:                                  # per-minute sequences for the hybrid model (same code as for 2018)
            from port_windows import PortTable
            tsv = d["ts"]
            minute = ((tsv - tsv.min()) // pd.Timedelta(minutes=1)).values.astype("float64")
            zb = pd.to_numeric(d["Total_Backward_Packets"], errors="coerce").fillna(1).values == 0
            tab = PortTable(d["Destination_Port"].values, minute, zb, valid=tsv.notna().values)
            off = sum(len(p) for p in _SEQ["parts"])
            _SEQ["parts"].append(tab.sequences(np.arange(len(d))).astype("float16"))
            d["__rid"] = np.arange(off, off + len(d))
        # keep only what later steps need (string columns are heavy)
        d = d.drop(columns=[c for c in ("Flow_ID", "Destination_IP", "Timestamp") if c in d.columns])
        if "Source_IP" in d.columns:
            d["Source_IP"] = d["Source_IP"].astype("category")
        d["source_file"] = os.path.basename(f)
        print(f"  loaded {os.path.basename(f)}: {d.shape}")
        parts.append(d)
    if seq:
        _SEQ["all"] = np.concatenate(_SEQ["parts"]); _SEQ["parts"] = []
    return pd.concat(parts, ignore_index=True)


# ----------------------------------------------------------------------------- cleaning
def clean(df, drop_dst_port=False):
    log = {"rows_raw": int(len(df))}
    lab = next((c for c in df.columns if c.lower() == "label"), None)
    if lab is None:
        raise KeyError("no label column found")
    df = df.rename(columns={lab: "label"})

    # pandas renames repeated headers to name.1 -> drop the copy (Fwd_Header_Length.1)
    dup_cols = [c for c in df.columns
                if re.search(r"\.\d+$", c) and re.sub(r"\.\d+$", "", c) in df.columns]
    df = df.drop(columns=dup_cols)
    log["dropped_duplicate_columns"] = dup_cols

    log["rows_dropped_missing_label"] = int(df["label"].isna().sum())   # blank lines / NaN labels
    df = df[df["label"].notna()].reset_index(drop=True)
    attack = (df["label"].astype(str).str.strip()
              .str.replace(r"[^\x20-\x7E]+", "-", regex=True))        # fix garbled 'Web Attack - ...'
    y = (~attack.str.upper().isin(["BENIGN", "0"])).astype(np.int8).values

    feats = [c for c in df.columns if c not in ID_COLS and c != "label"]
    if drop_dst_port and "Destination_Port" in feats:
        feats.remove("Destination_Port")
    X = df[feats].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    meta = pd.DataFrame({"ts": df["ts"] if "ts" in df.columns else pd.NaT,
                         "src": df["Source_IP"].astype(str) if "Source_IP" in df.columns else "",
                         "file": df["source_file"].values,
                         "rid": df["__rid"].values if "__rid" in df.columns else -1})

    ok = X.notna().all(axis=1).values
    log["rows_dropped_nan_inf"] = int((~ok).sum())
    X, y, attack, meta = X[ok].reset_index(drop=True), y[ok], attack[ok].reset_index(drop=True), meta[ok].reset_index(drop=True)

    # exact duplicates and conflicting duplicates (same features, different label)
    flow_cols = [c for c in X.columns if not c.startswith(("win_", "pw_", "gl_"))]      # duplicates are judged on the flow itself,
    h = pd.util.hash_pandas_object(X[flow_cols], index=False).values    # so the row set does not depend on --window_feats
    tmp = pd.DataFrame({"h": h, "a": attack.values})
    conflict = (tmp.groupby("h")["a"].transform("nunique") > 1).values
    dup = tmp.duplicated(["h", "a"]).values
    keep = ~(conflict | dup)
    log["rows_dropped_conflicting"] = int(conflict.sum())
    log["rows_dropped_duplicates"] = int((dup & ~conflict).sum())
    X, y, attack, meta = X[keep].reset_index(drop=True), y[keep], attack[keep].reset_index(drop=True), meta[keep].reset_index(drop=True)

    const = [c for c in X.columns if X[c].nunique() <= 1]
    X = X.drop(columns=const)
    log["dropped_constant_columns"] = const

    mn, mx = X.min(), X.max()
    log["looks_prenormalised"] = bool(((mn >= 0) & (mx <= 1.0)).mean() > 0.95)
    if log["looks_prenormalised"]:
        print("  WARNING: >95% of columns lie in [0,1] -> data looks globally min-max scaled "
              "(scaling stats leaked from test). Prefer the raw CSVs.")
    log["rows_clean"] = int(len(X))
    log["n_features"] = int(X.shape[1])
    log["attack_counts"] = attack.value_counts().to_dict()
    return X.astype("float32"), y, attack.values, meta, log


# ----------------------------------------------------------------------------- splitting
def strat_key(y, attack, min_n=10):
    vc = pd.Series(attack).value_counts()
    big = pd.Series(attack).map(vc).values >= min_n
    return np.where(big, attack, np.where(y == 1, "RARE_ATTACK", "BENIGN"))


def make_splits(y, attack, seed):
    key = strat_key(y, attack)
    idx = np.arange(len(y))
    tr, te = train_test_split(idx, test_size=0.20, stratify=key, random_state=seed)
    tr, va = train_test_split(tr, test_size=0.25, stratify=key[tr], random_state=seed)
    return tr, va, te, key


def make_blocked_splits(meta, y, attack, seed, block_min=1, min_blocks=3):
    """Time-block split: flows are grouped into `block_min`-minute blocks (per file/day) and whole
    blocks go to train/val/test (60/20/20). Neighbouring flows of one attack burst therefore cannot
    sit on both sides of the split. Each block is keyed by the rarest attack family it contains.
    Families present in fewer than `min_blocks` blocks go to TRAIN only (not evaluable)."""
    if meta["ts"].isna().all():
        raise ValueError("--split blocked needs Timestamp (use the GeneratedLabelledFlows CSVs)")
    ts = meta["ts"].fillna(meta["ts"].min())
    mins = ((ts - ts.min()).dt.total_seconds() // (block_min * 60)).astype("int64")   # resolution-independent
    bid = (meta["file"].astype(str) + "|" + mins.astype(str)).values
    cnt = pd.Series(attack).value_counts()
    rank = pd.Series(attack).map(cnt).values                       # small = rare
    d = pd.DataFrame({"bid": bid, "atk": np.where(y == 1, attack, "BENIGN"), "rank": np.where(y == 1, rank, 10**12)})
    bkey = d.sort_values("rank").groupby("bid")["atk"].first()     # rarest attack in block, else BENIGN
    rng = np.random.default_rng(seed)
    assign, train_only = {}, []
    for k, blocks in bkey.groupby(bkey).groups.items():
        blocks = np.array(list(blocks)); rng.shuffle(blocks)
        if len(blocks) < min_blocks:
            train_only.append((k, len(blocks))); parts = [blocks, [], []]
        else:
            n = len(blocks); n_te = max(1, round(.2 * n)); n_va = max(1, round(.2 * n))
            parts = [blocks[n_te + n_va:], blocks[n_te:n_te + n_va], blocks[:n_te]]
        for name, bl in zip(("tr", "va", "te"), parts):
            for b in bl:
                assign[b] = name
    sp = pd.Series(bid).map(assign).values
    key = strat_key(y, attack)
    if train_only:
        print("  families with <%d blocks -> train only (not evaluable):" % min_blocks, train_only)
    return (np.where(sp == "tr")[0], np.where(sp == "va")[0], np.where(sp == "te")[0], key)


# ----------------------------------------------------------------------------- metrics
def best_threshold(y, s):
    p, r, t = precision_recall_curve(y, s)
    f1 = 2 * p * r / np.clip(p + r, 1e-12, None)
    return float(t[int(np.nanargmax(f1[:-1]))])


def metrics(y, s, thr):
    pred = (s >= thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    pr, rc, f1, _ = precision_recall_fscore_support(y, pred, average="binary", zero_division=0)
    return dict(threshold=thr, accuracy=float((tp + tn) / len(y)), precision=float(pr),
                recall=float(rc), f1=float(f1), fpr=float(fp / max(fp + tn, 1)),
                roc_auc=float(roc_auc_score(y, s)), pr_auc=float(average_precision_score(y, s)),
                tp=int(tp), fp=int(fp), tn=int(tn), fn=int(fn))


def per_class(attack, s, thr):
    d = pd.DataFrame({"type": attack, "flagged": (s >= thr).astype(int)})
    out = d.groupby("type")["flagged"].agg(["size", "mean"]).rename(
        columns={"size": "n", "mean": "flagged_rate"})   # BENIGN row = FPR, attacks = recall
    return out.sort_values("n", ascending=False)


# ----------------------------------------------------------------------------- models
def get_models(seed):
    models = {
        "LogReg": LogisticRegression(max_iter=300, class_weight="balanced"),
        "HistGB": HistGradientBoostingClassifier(max_iter=200, random_state=seed),
    }
    try:
        from xgboost import XGBClassifier
        models["XGBoost"] = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.1,
                                          subsample=0.8, colsample_bytree=0.8, n_jobs=-1,
                                          tree_method="hist", random_state=seed, eval_metric="logloss")
    except ImportError:
        print("  xgboost not installed -> skipped")
    return models


def leave_one_attack_out(Xtr, ytr, atr, Xva, yva, ava, Xte, ate, X_raw, a_all, qt, seed, min_n=10):
    """Hold one attack family out of train/val (the model never sees it). Evaluate on ALL flows of
    that family (any split - safe, it was never trained on) vs. the benign TEST flows.
    recall_unseen uses the validation-chosen threshold; roc_auc_unseen is threshold-free."""
    rows = []
    neg = Xte[ate == "BENIGN"]
    for fam in sorted(f for f in set(a_all) if f != "BENIGN" and (a_all == f).sum() >= min_n):
        k, kv = atr != fam, ava != fam
        if ytr[k].sum() == 0 or yva[kv].sum() == 0:
            continue
        m = HistGradientBoostingClassifier(max_iter=100, random_state=seed).fit(Xtr[k], ytr[k])
        thr = best_threshold(yva[kv], m.predict_proba(Xva[kv])[:, 1])
        Xf = qt.transform(X_raw[a_all == fam]).astype("float32")
        sf, sn = m.predict_proba(Xf)[:, 1], m.predict_proba(neg)[:, 1]
        auc = roc_auc_score(np.r_[np.ones(len(sf)), np.zeros(len(sn))], np.r_[sf, sn])
        ben_val = m.predict_proba(Xva[kv][yva[kv] == 0])[:, 1]      # threshold at a FIXED false-alarm rate
        t1, t01 = np.quantile(ben_val, 0.99), np.quantile(ben_val, 0.999)
        rows.append(dict(held_out=fam, n_family=len(sf), recall_unseen=float((sf >= thr).mean()),
                         roc_auc_unseen=float(auc), **{"recall@1%FPR": float((sf >= t1).mean()),
                                                      "recall@0.1%FPR": float((sf >= t01).mean())},
                         fpr=float((sn >= thr).mean())))
    return pd.DataFrame(rows)


def _fixed_fpr_eval(s_ben_val, s_ben_test, s_pos):
    """Threshold-free AUC + recall at thresholds set on BENIGN validation scores (1% / 0.1% false alarms)."""
    t1, t01 = np.quantile(s_ben_val, 0.99), np.quantile(s_ben_val, 0.999)
    auc = roc_auc_score(np.r_[np.ones(len(s_pos)), np.zeros(len(s_ben_test))], np.r_[s_pos, s_ben_test])
    return {"n": len(s_pos), "roc_auc": float(auc),
            "recall@1%FPR": float((s_pos >= t1).mean()), "recall@0.1%FPR": float((s_pos >= t01).mean())}


def unsupervised_baselines(Xtr, ytr, Xva, yva, Xte, yte, ate, X_raw, a_all, qt, seed, max_fit=150_000):
    """Anomaly detectors trained on BENIGN train flows only (no attack labels at all). Every attack
    family is therefore 'unseen'. Scores: higher = more anomalous."""
    from sklearn.ensemble import IsolationForest
    from sklearn.neural_network import MLPRegressor
    rng = np.random.default_rng(seed)
    Xb = Xtr[ytr == 0]
    if len(Xb) > max_fit:
        Xb = Xb[rng.choice(len(Xb), max_fit, replace=False)]
    iso = IsolationForest(n_estimators=200, random_state=seed, n_jobs=-1).fit(Xb)
    ae = MLPRegressor(hidden_layer_sizes=(64, 32, 8, 32, 64), max_iter=40, batch_size=512,
                      random_state=seed).fit(Xb, Xb)
    scorers = {"IsolationForest": lambda Z: -iso.score_samples(Z),
               "Autoencoder": lambda Z: ((ae.predict(Z) - Z) ** 2).mean(axis=1)}
    ben_val, ben_te = Xva[yva == 0], Xte[ate == "BENIGN"]
    groups = {"ALL_ATTACKS(test)": Xte[yte == 1]}
    for fam in sorted(f for f in set(a_all) if f != "BENIGN" and (a_all == f).sum() >= 10):
        groups[fam] = qt.transform(X_raw[a_all == fam]).astype("float32")
    rows = []
    for name, f in scorers.items():
        sv, sn = f(ben_val), f(ben_te)
        for g, Z in groups.items():
            rows.append(dict(model=name, family=g, **_fixed_fpr_eval(sv, sn, f(Z))))
    return pd.DataFrame(rows)


def low_data_curve(Xtr, ytr, Xva, yva, Xte, yte, seed, sizes=(500, 1000, 2000, 5000, 20000), reps=3):
    """Train baselines on n labelled flows (val subset of the same size for the threshold), test on full test."""
    rows = []
    for n in sizes:
        if n >= len(ytr) or n >= len(yva):
            continue
        for r in range(reps):
            s = seed + r
            i, _ = train_test_split(np.arange(len(ytr)), train_size=n, stratify=ytr, random_state=s)
            j, _ = train_test_split(np.arange(len(yva)), train_size=n, stratify=yva, random_state=s)
            for name, m in get_models(s).items():
                m.fit(Xtr[i], ytr[i])
                sv, st = m.predict_proba(Xva[j])[:, 1], m.predict_proba(Xte)[:, 1]
                mt = metrics(yte, st, best_threshold(yva[j], sv))
                rows.append(dict(n_train=n, rep=r, model=name, f1=mt["f1"], pr_auc=mt["pr_auc"],
                                 recall=mt["recall"], fpr=mt["fpr"]))
    df = pd.DataFrame(rows)
    return df, df.groupby(["model", "n_train"])[["f1", "pr_auc", "recall", "fpr"]].agg(["mean", "std"])


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_glob", default="D:/revised model/GeneratedLabelledFlows(1)/**/*.csv")
    ap.add_argument("--out_dir", default="stage1_out")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max_train", type=int, default=0, help="subsample train rows (0 = all)")
    ap.add_argument("--drop_dst_port", action="store_true", help="remove Destination_Port (shortcut risk)")
    ap.add_argument("--leave_one_out", action="store_true")
    ap.add_argument("--comb_mode", choices=["novel", "exclude", "include"], default="novel")
    ap.add_argument("--unsup", action="store_true", help="IsolationForest + autoencoder trained on benign only")
    ap.add_argument("--low_data", action="store_true", help="baselines trained on 500..20000 labelled flows")
    ap.add_argument("--split", choices=["random", "blocked"], default="random",
                    help="random: stratified rows; blocked: whole time blocks (needs Timestamp)")
    ap.add_argument("--block_min", type=int, default=1, help="block length in minutes for --split blocked")
    ap.add_argument("--window_feats", action="store_true",
                    help="add causal window features (counts per Source_IP / Destination_IP / pair over the last "
                         "--window_min minutes of the same file)")
    ap.add_argument("--window_min", default="1,5", help="window lengths in minutes, comma separated")
    ap.add_argument("--seq", action="store_true",
                    help="also save 16-minute service-load sequences (seq17.npz) for hybrid_v2.py")
    ap.add_argument("--port_windows", action="store_true",
                    help="add IP-free service-load features per destination port (port_windows.py, same as for 2018)")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    np.random.seed(a.seed)
    warnings.filterwarnings("default")

    win = tuple(int(x) for x in a.window_min.split(",") if x.strip()) if a.window_feats else None
    print("[1] loading" + (f" (+ causal window features, windows {win} min)" if win else "")); raw = load_raw(a.data_glob, win, a.port_windows, a.seq)
    print("[2] cleaning"); X, y, attack, meta, log = clean(raw, a.drop_dst_port); del raw
    print(json.dumps({k: v for k, v in log.items() if k != "attack_counts"}, indent=2))
    print("attack counts:", log["attack_counts"])
    if meta["ts"].notna().any():   # sanity check of the AM/PM fix against the CIC attack schedule
        w = (pd.DataFrame({"label": attack, "ts": meta["ts"], "file": meta["file"]})
             .groupby(["file", "label"])["ts"].agg(["size", "min", "max"]))
        w.to_csv(f"{a.out_dir}/label_time_windows.csv")
        print("corrected time window per file/label (compare with the attack times on the UNB page):")
        print(w.to_string())

    Xcomb_df = None
    is_comb = pd.Series(attack).astype(str).str.strip().str.lower().eq("comb").values
    if a.comb_mode != "include" and is_comb.any():
        print(f"  'Comb' rows found: {int(is_comb.sum())} -> mode={a.comb_mode}")
        if a.comb_mode == "novel":
            Xcomb_df = X[is_comb]
        X, y, attack, meta = (X[~is_comb].reset_index(drop=True), y[~is_comb], attack[~is_comb],
                              meta[~is_comb].reset_index(drop=True))

    print(f"[3] split ({a.split})")
    if a.split == "blocked":
        tr, va, te, key = make_blocked_splits(meta, y, attack, a.seed, a.block_min)
    else:
        tr, va, te, key = make_splits(y, attack, a.seed)
    lab_split = np.empty(len(y), dtype=object); lab_split[tr], lab_split[va], lab_split[te] = "train", "val", "test"
    print("rows per class and split (before --max_train):")
    print(pd.crosstab(attack, lab_split).reindex(columns=["train", "val", "test"], fill_value=0).to_string())
    if y[va].mean() < 0.5 * y[tr].mean() or y[va].mean() > 2 * y[tr].mean():
        print("  WARNING: attack share in val differs a lot from train -> thresholds chosen on val are unreliable; "
              "use a smaller --block_min")
    if a.max_train and len(tr) > a.max_train:
        tr, _ = train_test_split(tr, train_size=a.max_train, stratify=key[tr], random_state=a.seed)
    print(f"  train {len(tr)}  val {len(va)}  test {len(te)}  | attack share "
          f"{y[tr].mean():.3f}/{y[va].mean():.3f}/{y[te].mean():.3f}")

    print("[4] preprocessing (fit on train only)")
    qt = QuantileTransformer(n_quantiles=1000, output_distribution="uniform",
                             subsample=200_000, random_state=a.seed).fit(X.iloc[tr])
    Xtr, Xva, Xte = (qt.transform(X.iloc[i]).astype("float32") for i in (tr, va, te))
    ytr, yva, yte = y[tr], y[va], y[te]
    atr, ava, ate = attack[tr], attack[va], attack[te]
    Xcomb = qt.transform(Xcomb_df).astype("float32") if Xcomb_df is not None else None
    joblib.dump(qt, f"{a.out_dir}/quantile_transformer.joblib")
    with open(f"{a.out_dir}/feature_names.json", "w") as fh:
        json.dump(list(X.columns), fh)
    np.savez(f"{a.out_dir}/splits.npz", Xtr=Xtr, Xva=Xva, Xte=Xte, ytr=ytr, yva=yva, yte=yte,
             atr=atr, ava=ava, ate=ate)
    if a.seq:
        rid = meta["rid"].values
        np.savez(f"{a.out_dir}/seq17.npz", Str=_SEQ["all"][rid[tr]], Sva=_SEQ["all"][rid[va]], Ste=_SEQ["all"][rid[te]])
        print(f"  sequences saved -> {a.out_dir}/seq17.npz  {(len(tr), len(va), len(te))} x {_SEQ['all'].shape[1:]}")

    print("[5] baselines")
    results, per_cls = {}, {}
    for name, m in get_models(a.seed).items():
        m.fit(Xtr, ytr)
        sv, st = m.predict_proba(Xva)[:, 1], m.predict_proba(Xte)[:, 1]
        thr = best_threshold(yva, sv)                      # chosen on validation only
        results[name] = {"val": metrics(yva, sv, thr), "test": metrics(yte, st, thr)}
        per_cls[name] = per_class(ate, st, thr)
        if Xcomb is not None:   # unseen synthetic class: fraction flagged as attack at the val-chosen threshold
            results[name]["comb_novel_recall"] = float((m.predict_proba(Xcomb)[:, 1] >= thr).mean())
        t = results[name]["test"]
        print(f"  {name:8s} test: acc={t['accuracy']:.4f} f1={t['f1']:.4f} fpr={t['fpr']:.4f} "
              f"roc={t['roc_auc']:.4f} pr={t['pr_auc']:.4f}"
              + (f" | Comb(novel) recall={results[name]['comb_novel_recall']:.4f}" if Xcomb is not None else ""))
    with open(f"{a.out_dir}/baseline_results.json", "w") as fh:
        json.dump({"clean_log": log, "results": results}, fh, indent=2, default=str)
    pd.concat(per_cls, axis=1).to_csv(f"{a.out_dir}/per_attack_detection.csv")

    if a.leave_one_out:
        print("[6] leave-one-attack-out")
        loo = leave_one_attack_out(Xtr, ytr, atr, Xva, yva, ava, Xte, ate, X, attack, qt, a.seed)
        loo.to_csv(f"{a.out_dir}/leave_one_attack_out.csv", index=False); print(loo.to_string(index=False))
    if a.unsup:
        print("[7] unsupervised baselines (trained on benign flows only)")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            un = unsupervised_baselines(Xtr, ytr, Xva, yva, Xte, yte, ate, X, attack, qt, a.seed)
        un.to_csv(f"{a.out_dir}/unsupervised_baselines.csv", index=False)
        for col in ("roc_auc", "recall@1%FPR", "recall@0.1%FPR"):
            print(f"-- {col}"); print(un.pivot(index="family", columns="model", values=col).round(3).to_string())
    if a.low_data:
        print("[8] low-data curve (3 repetitions)")
        raw_ld, summ = low_data_curve(Xtr, ytr, Xva, yva, Xte, yte, a.seed)
        raw_ld.to_csv(f"{a.out_dir}/low_data_curve_raw.csv", index=False)
        summ.to_csv(f"{a.out_dir}/low_data_curve.csv"); print(summ.round(4).to_string())
    print("done ->", a.out_dir)


if __name__ == "__main__":
    main()
