"""
Cross-dataset test: train on CIC-IDS2017 (stage-1 output), test on CSE-CIC-IDS2018 processed CSVs.  CPU only.

v3: adds the IP-free service-load features of port_windows.py (same code for both years) and compares feature sets
    flow        69 per-flow features (the baseline of the earlier runs)
    flow+pw     + 7 service-load features (counts, own-history bursts, unanswered share, whole-network burst)
    flow+pwrel  + only the 4 scale-free ones (bursts and shares)
Needs the stage-1 output made with --port_windows (feature_names.json then lists pw_* / gl_* columns) and
port_windows.py in the same folder as this script.

Scenarios: known (all 2017 attacks in training) | loo (the 2017 counterpart family removed from training).
Thresholds: A = from 2017 benign validation; B = from 2018 benign calibration flows (no attack label used).
Models: HistGB, XGBoost (if installed), IF-local2018 (IsolationForest fit on 2018 benign only).
Pre-registered rule: the temporal features help if, in the loo scenario, the mean recall@1%FPR (threshold B) of a
model with flow+pw (or flow+pwrel) is >= 0.36 AND >= its own flow-only value + 0.10.

Usage:
  python cross_dataset.py --s17_dir "D:/revised model/stage1_pw" --s17_npz splits.npz --data18 "D:/revised model/ids2018/*.csv" --out_dir "D:/revised model/cross_out3" --mode both --seeds 3
"""
import argparse, glob, json, os, re, time, warnings
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from port_windows import port_window_features, PW_COLS, PW_REL


def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def build_map():
    """normalised 2018 column name -> normalised 2017 column name (CICFlowMeter naming differences)"""
    m = {"dstport": "destinationport", "protocol": "protocol", "flowduration": "flowduration",
         "totfwdpkts": "totalfwdpackets", "totbwdpkts": "totalbackwardpackets",
         "totlenfwdpkts": "totallengthoffwdpackets", "totlenbwdpkts": "totallengthofbwdpackets",
         "flowbytss": "flowbytess", "flowpktss": "flowpacketss", "fwdiattot": "fwdiattotal", "bwdiattot": "bwdiattotal",
         "fwdpshflags": "fwdpshflags", "bwdpshflags": "bwdpshflags", "fwdurgflags": "fwdurgflags",
         "bwdurgflags": "bwdurgflags", "fwdheaderlen": "fwdheaderlength", "bwdheaderlen": "bwdheaderlength",
         "fwdpktss": "fwdpacketss", "bwdpktss": "bwdpacketss", "pktlenmin": "minpacketlength",
         "pktlenmax": "maxpacketlength", "pktlenmean": "packetlengthmean", "pktlenstd": "packetlengthstd",
         "pktlenvar": "packetlengthvariance", "cweflagcount": "cweflagcount", "downupratio": "downupratio",
         "pktsizeavg": "averagepacketsize", "fwdsegsizeavg": "avgfwdsegmentsize", "bwdsegsizeavg": "avgbwdsegmentsize",
         "fwdbytsbavg": "fwdavgbytesbulk", "fwdpktsbavg": "fwdavgpacketsbulk", "fwdblkrateavg": "fwdavgbulkrate",
         "bwdbytsbavg": "bwdavgbytesbulk", "bwdpktsbavg": "bwdavgpacketsbulk", "bwdblkrateavg": "bwdavgbulkrate",
         "subflowfwdpkts": "subflowfwdpackets", "subflowfwdbyts": "subflowfwdbytes",
         "subflowbwdpkts": "subflowbwdpackets", "subflowbwdbyts": "subflowbwdbytes",
         "initfwdwinbyts": "initwinbytesforward", "initbwdwinbyts": "initwinbytesbackward",
         "fwdactdatapkts": "actdatapktfwd", "fwdsegsizemin": "minsegsizeforward"}
    for f in ("fin", "syn", "rst", "psh", "ack", "urg", "ece"):
        m[f"{f}flagcnt"] = f"{f}flagcount"
    for s in ("max", "min", "mean", "std"):
        m[f"fwdpktlen{s}"], m[f"bwdpktlen{s}"] = f"fwdpacketlength{s}", f"bwdpacketlength{s}"
        for p in ("flowiat", "fwdiat", "bwdiat", "active", "idle"):
            m[f"{p}{s}"] = f"{p}{s}"
    return m


COUNTERPART = {"FTP-BruteForce": "FTP-Patator", "SSH-Bruteforce": "SSH-Patator",
               "DoS attacks-GoldenEye": "DoS GoldenEye", "DoS attacks-Slowloris": "DoS slowloris",
               "DoS attacks-Hulk": "DoS Hulk", "DoS attacks-SlowHTTPTest": "DoS Slowhttptest",
               "DDoS attacks-LOIC-HTTP": "DDoS", "DDOS attack-HOIC": None, "DDOS attack-LOIC-UDP": None,
               "Brute Force -Web": "Web Attack - Brute Force", "Brute Force -XSS": "Web Attack - XSS",
               "SQL Injection": "Web Attack - Sql Injection", "Infilteration": "Infiltration", "Bot": "Bot"}
NEW = "none (new in 2018)"


def sub_idx(y, n, seed):
    if n is None or n <= 0 or n >= len(y):
        return np.arange(len(y))
    try:
        idx, _ = train_test_split(np.arange(len(y)), train_size=n, stratify=y, random_state=seed)
    except ValueError:
        idx = np.random.default_rng(seed).choice(len(y), n, replace=False)
    return np.sort(idx)


def parse_ts(s):
    ts = pd.to_datetime(s, format="%d/%m/%Y %H:%M:%S", errors="coerce")
    if ts.isna().mean() > 0.01:
        ts = pd.to_datetime(s, errors="coerce", dayfirst=True, format="mixed")
    return ts


def load_2018(pattern, feats17, want_pw, want_seq, ben_n, cap, seed, chunk):
    """Sample 2018 flows (all attack types capped, benign subsampled) and attach the service-load features / sequences,
    which are computed from the WHOLE capture file (PortTable), not from the sample."""
    from port_windows import PortTable
    files = sorted(glob.glob(pattern, recursive=True))
    if not files:
        raise SystemExit(f"no CSV matched: {pattern}")
    m = build_map()
    want17 = {norm(f): f for f in feats17}
    cnt = {}                                                     # pass 1: label counts only (cheap)
    for f in files:
        for ch in pd.read_csv(f, usecols=lambda c: norm(c) == "label", chunksize=chunk, low_memory=False):
            lab = ch.iloc[:, 0].astype(str).str.strip()
            for k, v in lab[lab.str.lower() != "label"].value_counts().items():
                cnt[k] = cnt.get(k, 0) + int(v)
    n_ben = cnt.get("Benign", 0)
    rate = {k: (min(1.0, ben_n / max(n_ben, 1)) if k == "Benign" else min(1.0, cap / v)) for k, v in cnt.items()}
    print("  2018 labels:", ", ".join(f"{k} {v}" for k, v in sorted(cnt.items(), key=lambda t: -t[1])))
    need_ctx = want_pw or want_seq
    rng = np.random.default_rng(seed)
    parts, seqs, missing = [], [], None
    for f in files:                                              # pass 2: sample + whole-file context table
        cols = list(pd.read_csv(f, nrows=0).columns)
        by = {norm(c): c for c in cols}
        col_for = {}
        for c in cols:
            k17 = m.get(norm(c))
            if k17 in want17:
                col_for[want17[k17]] = c
        miss = [x for x in feats17 if x not in col_for]
        if missing is None or len(miss) < len(missing):
            missing = miss
        lab_c = by["label"]
        ctx_c = [by["dstport"], by["timestamp"], by["totbwdpkts"]] if need_ctx else []
        use = set(col_for.values()) | {lab_c} | set(ctx_c)
        ports, tss, bwds, hdrs, kept_pos, Xs = [], [], [], [], [], []
        off = 0
        for ch in pd.read_csv(f, usecols=lambda c: c in use, chunksize=chunk, low_memory=False):
            pos = np.arange(off, off + len(ch)); off += len(ch)
            lab_s = ch[lab_c].astype(str).str.strip()
            ok = (lab_s.str.lower() != "label").values
            if need_ctx:
                ports.append(ch[ctx_c[0]].values); tss.append(ch[ctx_c[1]].astype(str).values)
                bwds.append(ch[ctx_c[2]].values); hdrs.append(~ok)
            keep = ok & (rng.random(len(ch)) < lab_s.map(rate).fillna(0).values)
            sub = ch[keep]
            X = pd.DataFrame({f17: pd.to_numeric(sub[c], errors="coerce").values for f17, c in col_for.items()})
            X["__label"] = lab_s.values[keep]
            Xs.append(X); kept_pos.append(pos[keep])
        X = pd.concat(Xs, ignore_index=True); kp = np.concatenate(kept_pos)
        if need_ctx:
            hdr = np.concatenate(hdrs)
            ts = parse_ts(pd.Series(np.concatenate(tss)))
            minute = ((ts - ts[~hdr].min()) // pd.Timedelta(minutes=1)).values.astype("float64")
            zb = pd.to_numeric(pd.Series(np.concatenate(bwds)), errors="coerce").fillna(1).values == 0
            tab = PortTable(np.concatenate(ports), minute, zb, valid=(~hdr) & ts.notna().values)
            if want_pw:
                X[PW_COLS] = tab.pw_features(kp)[PW_COLS].values
            if want_seq:
                seqs.append(tab.sequences(kp).astype("float16"))
            del tab, ts, minute, zb
        parts.append(X)
        print(f"  {os.path.basename(f)}: {off} rows, kept {len(X)} (sampled)"
              + (" + service-load context" if need_ctx else ""), flush=True)
    D = pd.concat(parts, ignore_index=True)
    SEQ = np.concatenate(seqs) if want_seq else None
    if missing:
        print(f"  WARNING: {len(missing)} 2017 features have no 2018 column, filled with 0: {missing}")
        for x in missing:
            D[x] = 0.0
    cols_all = feats17 + (PW_COLS if want_pw else [])
    X = D[cols_all].replace([np.inf, -np.inf], np.nan)
    ok = X.notna().all(axis=1).values
    h = pd.util.hash_pandas_object(X[feats17], index=False).values       # duplicates judged on the flow itself
    t = pd.DataFrame({"h": h, "a": D["__label"].values})
    conflict = (t.groupby("h")["a"].transform("nunique") > 1).values
    dup = t.duplicated(["h", "a"]).values
    keep = ok & ~(conflict | dup)
    print(f"  2018 sample: {len(ok)} rows, dropped NaN/inf {int((~ok).sum())}, conflicting {int((conflict & ok).sum())}, "
          f"duplicates {int((dup & ~conflict & ok).sum())} -> {int(keep.sum())}")
    return (X[keep].reset_index(drop=True), D["__label"].values[keep], missing,
            SEQ[keep] if SEQ is not None else None)


def models(seed):
    ms = {"HistGB": HistGradientBoostingClassifier(max_iter=200, random_state=seed)}
    try:
        from xgboost import XGBClassifier
        ms["XGBoost"] = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.1, subsample=0.8,
                                      colsample_bytree=0.8, n_jobs=-1, tree_method="hist", random_state=seed,
                                      eval_metric="logloss")
    except ImportError:
        pass
    return ms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--s17_npz", default="splits.npz")
    ap.add_argument("--data18", default="D:/revised model/ids2018/*.csv")
    ap.add_argument("--out_dir", default="cross_out3")
    ap.add_argument("--mode", choices=["known", "loo", "both"], default="both")
    ap.add_argument("--sets", default="flow,flow+pw,flow+pwrel")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--max_train", type=int, default=100000)
    ap.add_argument("--val_max", type=int, default=50000)
    ap.add_argument("--ben18", type=int, default=300000)
    ap.add_argument("--cap18", type=int, default=20000)
    ap.add_argument("--chunk", type=int, default=500000)
    ap.add_argument("--reuse", action="store_true", help="reuse the 2018 sample saved by an earlier run")
    ap.add_argument("--seq", action="store_true", help="also build the 16-minute sequences (needed by hybrid_v2.py)")
    ap.add_argument("--prep_only", action="store_true", help="only build/cache the 2018 sample, train nothing")
    ap.add_argument("--fusion", action="store_true",
                    help="also score a late fusion (max of benign-percentiles) of the trained (model, feature set) views")
    a = ap.parse_args()
    warnings.filterwarnings("ignore")
    os.makedirs(a.out_dir, exist_ok=True)
    t0 = time.time()

    feats = json.load(open(os.path.join(a.s17_dir, "feature_names.json")))
    qt = joblib.load(os.path.join(a.s17_dir, "quantile_transformer.joblib"))
    flow_feats = [f for f in feats if not f.startswith(("win_", "pw_", "gl_"))]
    sets_req = [s.strip() for s in a.sets.split(",") if s.strip()]
    want_pw = any("pw" in s for s in sets_req)
    pw_feats = [c for c in PW_COLS if c in feats]
    if want_pw and len(pw_feats) != len(PW_COLS):
        raise SystemExit("feature_names.json has no (or not all) pw_* columns -> run stage 1 with --port_windows "
                         f"(found: {pw_feats})")
    model_cols = flow_feats + (PW_COLS if want_pw else [])
    model_idx = np.array([feats.index(c) for c in model_cols])
    nf = len(flow_feats)
    set_cols = {"flow": np.arange(nf)}
    if want_pw:
        set_cols["flow+pw"] = np.arange(len(model_cols))
        set_cols["flow+pwrel"] = np.r_[np.arange(nf), [nf + PW_COLS.index(c) for c in PW_REL]]
    bad = [s for s in sets_req if s not in set_cols]
    if bad:
        raise SystemExit(f"unknown --sets {bad}; available {list(set_cols)}")
    z = np.load(os.path.join(a.s17_dir, a.s17_npz), allow_pickle=True)
    Xtr, Xva = z["Xtr"][:, model_idx], z["Xva"][:, model_idx]
    ytr, yva = z["ytr"].astype(int), z["yva"].astype(int)
    atr, ava = z["atr"].astype(str), z["ava"].astype(str)
    print(f"2017: train {len(ytr)} val {len(yva)}, {nf} flow features"
          + (f" + {len(PW_COLS)} service-load" if want_pw else ""))

    cache = os.path.join(a.out_dir, "ids2018_sample_v4.npz")
    old = os.path.join(a.out_dir, "ids2018_sample_v3.npz")
    src = cache if os.path.exists(cache) else (old if os.path.exists(old) and not a.seq else None)
    if a.reuse and src:
        zc = np.load(src, allow_pickle=True)
        X18raw = pd.DataFrame(zc["X"], columns=list(zc["cols"])); lab18 = zc["lab"].astype(str)
        missing = list(zc["missing"])
        if a.seq and "seq" not in zc.files:
            raise SystemExit("cached sample has no sequences -> run once without --reuse")
        print(f"2018 sample reused from {src}: {len(lab18)} rows")
    else:
        print("loading 2018 ...")
        X18raw, lab18, missing, SEQ18 = load_2018(a.data18, flow_feats, want_pw or a.seq, a.seq, a.ben18, a.cap18,
                                                   0, a.chunk)
        extra = {"seq": SEQ18} if SEQ18 is not None else {}
        np.savez(cache, X=X18raw.values.astype("float64"), cols=np.array(list(X18raw.columns)), lab=lab18,
                 missing=np.array(missing or [], dtype=str), **extra)
        print(f"2018 sample saved -> {cache}" + (f"  (sequences {SEQ18.shape})" if SEQ18 is not None else ""))
    if a.prep_only:
        print("--prep_only: done"); return
    full = pd.DataFrame(0.0, index=X18raw.index, columns=feats)
    for c in model_cols:
        full[c] = X18raw[c].values
    X18 = qt.transform(full)[:, model_idx].astype("float32")              # 2017 transformer, never refit
    ben = np.where(lab18 == "Benign")[0]
    rng = np.random.default_rng(0); rng.shuffle(ben)
    k3 = len(ben) // 3
    cal_fit, cal, bte = ben[:k3], ben[k3:2 * k3], ben[2 * k3:]
    types = list(pd.Series(lab18[lab18 != "Benign"]).value_counts().index)
    print(f"2018: benign fit {len(cal_fit)} / calibration {len(cal)} / test {len(bte)}, attack types {len(types)} "
          f"[{time.time() - t0:.0f}s]")

    def evaluate(scen, held, mname, sname, seed, f, cols, sv_ben):
        s_cal, s_bte = f(X18[cal][:, cols]), f(X18[bte][:, cols])
        tA1 = np.quantile(sv_ben, 0.99) if sv_ben is not None else np.inf
        tB1, tB01 = np.quantile(s_cal, 0.99), np.quantile(s_cal, 0.999)
        out = []
        for t in types:
            cp = COUNTERPART.get(t) or NEW
            if scen == "loo" and (cp == NEW or (held is not None and cp != held)):
                continue
            sp = f(X18[lab18 == t][:, cols])
            auc = roc_auc_score(np.r_[np.ones(len(sp)), np.zeros(len(s_bte))], np.r_[sp, s_bte])
            out.append(dict(scenario=scen, fset=sname, type18=t, counterpart17=cp, n=len(sp), model=mname, seed=seed,
                            auc=auc, recB_1=float((sp >= tB1).mean()), recB_01=float((sp >= tB01).mean()),
                            fprB_1=float((s_bte >= tB1).mean()),
                            recA_1=float((sp >= tA1).mean()) if sv_ben is not None else np.nan,
                            fprA_1=float((s_bte >= tA1).mean()) if sv_ben is not None else np.nan))
        return out

    rows = []
    scen_list = (["known"] if a.mode in ("known", "both") else []) + (["loo"] if a.mode in ("loo", "both") else [])
    for scen in scen_list:
        helds = [None] if scen == "known" else sorted({c for t, c in COUNTERPART.items() if c and t in types})
        for held in helds:
            if held and not (atr == held).any():
                print(f"  {held}: not in 2017 train split, skipped"); continue
            mt = (atr != held) if held else np.ones(len(atr), bool)
            mv = (ava != held) if held else np.ones(len(ava), bool)
            for seed in range(a.seeds):
                i, j = sub_idx(ytr[mt], a.max_train, seed), sub_idx(yva[mv], a.val_max, seed)
                Xi, yi, Xj, yj = Xtr[mt][i], ytr[mt][i], Xva[mv][j], yva[mv][j]
                comps = []
                for sname in sets_req:
                    cols = set_cols[sname]
                    for mname, mdl in models(seed).items():
                        mdl.fit(Xi[:, cols], yi)
                        f = lambda X, mdl=mdl: mdl.predict_proba(X)[:, 1]
                        rows += evaluate(scen, held, mname, sname, seed, f, cols, f(Xj[yj == 0][:, cols]))
                        if a.fusion:
                            ref = np.sort(f(X18[cal_fit][:, cols]))   # 2018 benign (fit third) -> percentile map
                            comps.append((mname, cols, f, ref))
                if a.fusion and len(comps) > 1:
                    # late fusion: each view's score -> its percentile among 2018 benign flows, take the maximum;
                    # the fused threshold is then set on the separate calibration third (threshold B), as for all
                    allc = np.arange(len(model_cols))
                    groups = {"FUSE-all": comps}
                    for mname in {c[0] for c in comps}:
                        groups[f"FUSE-{mname}"] = [c for c in comps if c[0] == mname]
                    for gname, cs in groups.items():
                        if len(cs) < 2:
                            continue
                        def fz(X, cs=cs):
                            return np.max([np.searchsorted(r, ff(X[:, cc]), side="right") / len(r)
                                           for _, cc, ff, r in cs], axis=0)
                        rows += evaluate(scen, held, gname, "fused", seed, fz, allc, None)
            print(f"  {scen} {held or 'all 2017 attacks in training'} done [{time.time() - t0:.0f}s]", flush=True)
    for seed in range(a.seeds):                                           # benign-only, 2018 benign, no attack label
        for sname in sets_req:
            cols = set_cols[sname]
            iso = IsolationForest(n_estimators=200, random_state=seed, n_jobs=-1).fit(X18[cal_fit][:, cols])
            f = lambda X, iso=iso: -iso.score_samples(X)
            for scen in scen_list:
                rows += evaluate(scen, None, "IF-local2018", sname, seed, f, cols, None)

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(a.out_dir, "cross_dataset_results.csv"), index=False)
    L = []
    say = lambda s="": (print(s), L.append(s))
    say(f"\n2017 features without a 2018 column (filled 0): {missing or 'none'}")
    say("\n==== SUMMARY: mean recall @ 1% FPR (threshold B) over 2018 attack types, mean (sd) over seeds")
    g = df.groupby(["scenario", "model", "fset", "seed"])["recB_1"].mean().groupby(["scenario", "model", "fset"])
    sm = pd.DataFrame({"mean": g.mean(), "sd": g.std()})
    say(sm.round(3).to_string())
    say("(loo: the 12 types with a 2017 counterpart; known: all 14)")
    if "loo" in scen_list and "flow" in sets_req:
        say("\n==== DECISION RULE (loo): a temporal set helps if mean >= 0.36 and >= own flow-only mean + 0.10")
        for (mname, sname), v in sm.loc["loo"]["mean"].items():
            if sname in ("flow", "fused") or mname == "IF-local2018":
                continue
            base = sm.loc[("loo", mname, "flow"), "mean"]
            ok = v >= 0.36 and v >= base + 0.10
            say(f"  {mname:8s} {sname:10s} {v:.3f} vs flow {base:.3f}  ->  "
                + ("HELPS (rule met)" if ok else "rule not met"))
    if "loo" in scen_list and (df.fset == "fused").any():
        single = sm.loc["loo"].drop(index="IF-local2018", level=0, errors="ignore")
        single = single[single.index.get_level_values(1) != "fused"]
        best_name, best = single["mean"].idxmax(), single["mean"].max()
        say(f"\n==== FUSION (loo) vs best single view {best_name} = {best:.3f}  (rule: fusion counts if >= best + 0.05)")
        for (mname, sname), v in sm.loc["loo"]["mean"].items():
            if sname == "fused":
                say(f"  {mname:13s} {v:.3f}  ->  " + ("fusion HELPS" if v >= best + 0.05 else "no clear gain"))
    for scen in scen_list:
        d = df[df.scenario == scen]
        say(f"\n==== scenario: {scen}")
        for col, txt in (("recB_1", "recall @ 1% FPR, threshold B (2018 benign calibration)"),
                         ("recB_01", "recall @ 0.1% FPR, threshold B"), ("auc", "AUC vs 2018 benign")):
            pv = d.pivot_table(index="type18", columns=["model", "fset"], values=col, aggfunc="mean")
            pv.insert(0, "2017 counterpart", [COUNTERPART.get(t) or NEW for t in pv.index])
            say(f"\n-- {txt}")
            say(pv.round(3).to_string())
        fa = d.dropna(subset=["fprA_1"]).groupby(["model", "fset"])["fprA_1"].mean()
        say("\n-- actual 2018 false-alarm rate at threshold A (2017 benign, nominal 1%)")
        say(fa.round(3).to_string())
    open(os.path.join(a.out_dir, "report.txt"), "w", encoding="utf-8").write("\n".join(L))
    print(f"\nsaved -> {a.out_dir}  [{time.time() - t0:.0f}s]")


if __name__ == "__main__":
    main()
