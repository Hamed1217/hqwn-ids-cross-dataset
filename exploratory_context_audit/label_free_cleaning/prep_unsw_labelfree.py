"""
Builds the CIC-UNSW-NB15 target cache for the CONFIRMATORY run of hybrid_v3 (same format as the 2018 cache
ids2018_sample_v4.npz, read unchanged by hybrid_v3.load_data), plus what the later analyses need.
CPU, reads the 3.5 M-row CICFlowMeter_out.csv in chunks (about 10-20 min, ~3 GB RAM).

Steps (the same rules as cross_dataset.load_2018 for 2018, so both targets are prepared alike):
  1. COLUMN MAP: newer CICFlowMeter names ("Total Fwd Packet", "Fwd Segment Size Avg", "FWD Init Win Bytes", ...) ->
     the 2017 feature names; every 2017 feature without a UNSW column is listed and set to 0 (as for 2018).
     Run --check first: it prints the full map on the first rows and changes nothing.
  2. TIMESTAMPS "22/01/2015 07:50:15 AM" (%d/%m/%Y %I:%M:%S %p). The file holds TWO capture sessions (22 Jan and
     17-18 Feb 2015); a gap of more than 6 h starts a new session. The service-load table (PortTable) and the
     16-minute sequences are built per session from ALL its flows (as per capture file in 2017 / 2018).
  3. SAMPLE: benign flows subsampled to --ben (300,000, as 2018), every attack class capped at --cap (20,000), seed 0;
     NaN / inf rows, label conflicts and exact duplicates removed (as 2018).
  4. SAVED per flow for later (never used as model features): timestamp, session, source / destination IP and port,
     protocol, row number in the CSV -> event-level metric, attack-family stage, identity-shortcut check.
  5. IDENTITY-SHORTCUT CHECK (reported, not used): how well "alarm if source IP is 175.45.176.x" alone would do.

  python prep_unsw.py --csv "D:/revised model/CIC-UNSW-NB15/CICFlowMeter_out.csv" --check
  python prep_unsw.py --csv "D:/revised model/CIC-UNSW-NB15/CICFlowMeter_out.csv" --out "D:/revised model/unsw/unsw_sample_v1.npz"
"""
import argparse, hashlib, json, os, re, time
import numpy as np
import pandas as pd

ATTACKER_NET = "175.45.176."


def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def build_map():
    """normalised source column name -> normalised 2017 name; 2018 names (cross_dataset) + newer CICFlowMeter names"""
    m = {"dstport": "destinationport", "destinationport": "destinationport",
         # 2018 naming (identical to cross_dataset.build_map)
         "totfwdpkts": "totalfwdpackets", "totbwdpkts": "totalbackwardpackets",
         "totlenfwdpkts": "totallengthoffwdpackets", "totlenbwdpkts": "totallengthofbwdpackets",
         "flowbytss": "flowbytess", "flowpktss": "flowpacketss", "fwdiattot": "fwdiattotal", "bwdiattot": "bwdiattotal",
         "fwdheaderlen": "fwdheaderlength", "bwdheaderlen": "bwdheaderlength", "fwdpktss": "fwdpacketss",
         "bwdpktss": "bwdpacketss", "pktlenmin": "minpacketlength", "pktlenmax": "maxpacketlength",
         "pktlenmean": "packetlengthmean", "pktlenstd": "packetlengthstd", "pktlenvar": "packetlengthvariance",
         "pktsizeavg": "averagepacketsize", "fwdsegsizeavg": "avgfwdsegmentsize", "bwdsegsizeavg": "avgbwdsegmentsize",
         "fwdbytsbavg": "fwdavgbytesbulk", "fwdpktsbavg": "fwdavgpacketsbulk", "fwdblkrateavg": "fwdavgbulkrate",
         "bwdbytsbavg": "bwdavgbytesbulk", "bwdpktsbavg": "bwdavgpacketsbulk", "bwdblkrateavg": "bwdavgbulkrate",
         "subflowfwdpkts": "subflowfwdpackets", "subflowfwdbyts": "subflowfwdbytes", "subflowbwdpkts": "subflowbwdpackets",
         "subflowbwdbyts": "subflowbwdbytes", "initfwdwinbyts": "initwinbytesforward",
         "initbwdwinbyts": "initwinbytesbackward", "fwdactdatapkts": "actdatapktfwd", "fwdsegsizemin": "minsegsizeforward",
         # newer CICFlowMeter naming (CIC-UNSW-NB15)
         "totalfwdpacket": "totalfwdpackets", "totalbwdpackets": "totalbackwardpackets",
         "totallengthoffwdpacket": "totallengthoffwdpackets", "totallengthofbwdpacket": "totallengthofbwdpackets",
         "packetlengthmin": "minpacketlength", "packetlengthmax": "maxpacketlength",
         "fwdsegmentsizeavg": "avgfwdsegmentsize", "bwdsegmentsizeavg": "avgbwdsegmentsize",
         "fwdbytesbulkavg": "fwdavgbytesbulk", "fwdpacketbulkavg": "fwdavgpacketsbulk", "fwdbulkrateavg": "fwdavgbulkrate",
         "bwdbytesbulkavg": "bwdavgbytesbulk", "bwdpacketbulkavg": "bwdavgpacketsbulk", "bwdbulkrateavg": "bwdavgbulkrate",
         "fwdinitwinbytes": "initwinbytesforward", "bwdinitwinbytes": "initwinbytesbackward",
         "cwrflagcount": "cweflagcount"}                      # 2017 calls the CWR flag count "CWE Flag Count"
    for f in ("fin", "syn", "rst", "psh", "ack", "urg", "ece", "cwe"):
        m[f"{f}flagcnt"] = f"{f}flagcount"
    for s in ("max", "min", "mean", "std"):
        m[f"fwdpktlen{s}"], m[f"bwdpktlen{s}"] = f"fwdpacketlength{s}", f"bwdpacketlength{s}"
    return m


def map_columns(cols, feats17):
    """2017 feature -> source column (exact normalised name first, then the alias table)"""
    m = build_map()
    want = {norm(f): f for f in feats17}
    out, how = {}, {}
    for c in cols:
        n = norm(c)
        if n in want and want[n] not in out:
            out[want[n]], how[want[n]] = c, "same name"
    for c in cols:
        k = m.get(norm(c))
        if k in want and want[k] not in out:
            out[want[k]], how[want[k]] = c, "alias"
    missing = [f for f in feats17 if f not in out]
    return out, how, missing


def find(cols, *cands):
    by = {norm(c): c for c in cols}
    for k in cands:
        if k in by:
            return by[k]
    raise SystemExit(f"column not found, tried {cands}")


def parse_ts(s):
    t = pd.to_datetime(s, format="%d/%m/%Y %I:%M:%S %p", errors="coerce")
    if t.isna().mean() > 0.01:
        t2 = pd.to_datetime(s, errors="coerce", dayfirst=True, format="mixed")
        t = t.fillna(t2)
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--out", default="D:/revised model/unsw/unsw_sample_v1_labelfree.npz")
    ap.add_argument("--ben", type=int, default=300000)
    ap.add_argument("--cap", type=int, default=20000)
    ap.add_argument("--chunk", type=int, default=500000)
    ap.add_argument("--gap_hours", type=float, default=6.0)
    ap.add_argument("--check", action="store_true", help="print the column map on the first rows and stop")
    ap.add_argument("--feats_json", default="", help="(testing) feature_names.json path instead of s17_dir")
    a = ap.parse_args()
    from port_windows import PortTable, SEQ_T, SEQ_CH
    t0 = time.time()
    feats = json.load(open(a.feats_json or os.path.join(a.s17_dir, "feature_names.json")))
    flow = [f for f in feats if not f.startswith(("win_", "pw_", "gl_"))]
    cols = list(pd.read_csv(a.csv, nrows=0).columns)
    col_for, how, missing = map_columns(cols, flow)
    c_lab = find(cols, "label")
    c_ts = find(cols, "timestamp")
    c_dp = find(cols, "dstport", "destinationport")
    c_sp = find(cols, "srcport", "sourceport")
    c_si = find(cols, "srcip", "sourceip")
    c_di = find(cols, "dstip", "destinationip")
    c_pr = find(cols, "protocol")
    c_bw = find(cols, "totalbwdpackets", "totbwdpkts", "totalbackwardpackets")
    print(f"{len(cols)} columns; {len(flow)} 2017 flow features: {len(col_for)} mapped "
          f"({sum(v == 'alias' for v in how.values())} by alias), {len(missing)} missing")
    print("\n2017 feature  <-  UNSW column  [how]")
    for f in flow:
        print(f"  {f:32s} <- {col_for.get(f, '--- MISSING (set to 0) ---'):30s} {how.get(f, '')}")
    unused = [c for c in cols if c not in col_for.values() and c not in (c_lab, c_ts, c_sp, c_si, c_di, c_pr, c_dp)]
    print(f"\nUNSW columns not used: {unused}")
    if a.check:
        h = pd.read_csv(a.csv, nrows=50000, low_memory=False)
        t = parse_ts(h[c_ts].astype(str))
        print(f"\nfirst 50,000 rows: timestamp parsed {t.notna().mean():.1%}, range {t.min()} -> {t.max()}")
        print("labels:", h[c_lab].astype(str).str.strip().value_counts().to_dict())
        print("example values (first mapped features):")
        print(h[[col_for[f] for f in flow if f in col_for][:8]].head(3).to_string())
        print("\n--check: nothing written. Send this output for review before building the cache.")
        return

    # ---------------- pass 1: context columns of ALL rows + label counts
    use1 = [c_lab, c_ts, c_dp, c_bw]
    labs, tss, dps, zbs = [], [], [], []
    for ch in pd.read_csv(a.csv, usecols=use1, chunksize=a.chunk, low_memory=False):
        labs.append(ch[c_lab].astype(str).str.strip().values)
        tss.append(parse_ts(ch[c_ts].astype(str)).values)
        dps.append(ch[c_dp].values)
        zbs.append(pd.to_numeric(ch[c_bw], errors="coerce").fillna(1).values == 0)
    lab_all, ts_all = np.concatenate(labs), pd.to_datetime(np.concatenate(tss))
    dp_all, zb_all = np.concatenate(dps), np.concatenate(zbs)
    N = len(lab_all)
    okt = ts_all.notna()
    print(f"\npass 1: {N:,} rows, timestamp parsed {okt.mean():.2%} [{time.time() - t0:.0f}s]")
    cnt = pd.Series(lab_all).value_counts()
    print("labels:", cnt.to_dict())
    # sessions: sort by time, a gap > gap_hours starts a new one
    sec = np.where(okt, ts_all.values.astype("datetime64[s]").astype("int64"), np.nan)
    order = np.argsort(np.where(np.isfinite(sec), sec, np.inf), kind="stable")
    ss = sec[order]
    brk = np.r_[False, np.diff(ss) > a.gap_hours * 3600]
    sess_sorted = np.cumsum(brk)
    session = np.full(N, -1, "int64")
    session[order] = np.where(np.isfinite(ss), sess_sorted, -1)
    for s in np.unique(session[session >= 0]):
        r = session == s
        print(f"  session {s}: {r.sum():,} flows, {pd.Timestamp(np.nanmin(sec[r]), unit='s')} -> "
              f"{pd.Timestamp(np.nanmax(sec[r]), unit='s')}")
    # ---------------- sample (seed 0) as for 2018
    rng = np.random.default_rng(0)
    n_ben = int(cnt.get("Benign", 0))
    rate = {k: (min(1.0, a.ben / max(n_ben, 1)) if k == "Benign" else min(1.0, a.cap / v)) for k, v in cnt.items()}
    keep = rng.random(N) < pd.Series(lab_all).map(rate).fillna(0).values
    keep &= session >= 0
    rows = np.where(keep)[0]
    print(f"sampled {len(rows):,} rows (benign rate {rate.get('Benign', 0):.4f}, cap {a.cap} per attack class)")
    # ---------------- service-load sequences per session (table from ALL flows of the session)
    seq = np.zeros((len(rows), SEQ_T, len(SEQ_CH)), "float16")
    for s in np.unique(session[session >= 0]):
        idx = np.where(session == s)[0]
        minute = (sec[idx] - np.nanmin(sec[idx])) // 60
        tab = PortTable(dp_all[idx], minute, zb_all[idx], valid=np.isfinite(minute))
        pos = np.searchsorted(idx, rows)
        inside = (pos < len(idx)) & (idx[np.minimum(pos, len(idx) - 1)] == rows)
        seq[inside] = tab.sequences(pos[inside]).astype("float16")
        del tab
        print(f"  session {s}: sequences for {int(inside.sum()):,} sampled flows [{time.time() - t0:.0f}s]", flush=True)
    # ---------------- pass 2: features + identifiers of the sampled rows
    use2 = set(col_for.values()) | {c_si, c_di, c_sp, c_pr}
    want = np.zeros(N, bool); want[rows] = True
    parts, off = [], 0
    for ch in pd.read_csv(a.csv, usecols=lambda c: c in use2, chunksize=a.chunk, low_memory=False):
        w = want[off:off + len(ch)]; off += len(ch)
        sub = ch[w]
        X = pd.DataFrame({f: pd.to_numeric(sub[c], errors="coerce").values for f, c in col_for.items()})
        X["__src_ip"], X["__dst_ip"] = sub[c_si].astype(str).values, sub[c_di].astype(str).values
        X["__sport"] = pd.to_numeric(sub[c_sp], errors="coerce").values
        X["__proto"] = pd.to_numeric(sub[c_pr], errors="coerce").values
        parts.append(X)
    D = pd.concat(parts, ignore_index=True)
    for f in missing:
        D[f] = 0.0
    lab = lab_all[rows]
    Xf = D[flow].replace([np.inf, -np.inf], np.nan)
    ok = Xf.notna().all(axis=1).values
    h = pd.util.hash_pandas_object(Xf, index=False).values
    t = pd.DataFrame({"h": h, "a": lab})
    # LABEL-FREE CLEANING (reviewer-requested sensitivity run): the label is never used to decide
    # which rows to drop. Every feature vector is kept once (first copy in file order); the copy
    # that is kept carries its own label. Nothing is removed because of a label conflict.
    conflict = (t.groupby("h")["a"].transform("nunique") > 1).values   # counted for the report only
    dup = t.duplicated(["h"]).values                                  # same vector, any label
    k = ok & ~dup
    print("LABEL-FREE: vectors with >1 label kept once:", int((conflict & ok & ~dup).sum()),
          "| attack rows lost vs. original rule are reported below")
    print(f"sample: {len(ok):,} rows, dropped NaN/inf {int((~ok).sum())}, conflicting {int((conflict & ok).sum())}, "
          f"duplicates {int((dup & ~conflict & ok).sum())} -> {int(k.sum()):,}")
    lab = lab[k]
    print("final sample labels:", pd.Series(lab).value_counts().to_dict())
    # ---------------- identity-shortcut check (reported only)
    src = D["__src_ip"].values[k]
    att = lab != "Benign"
    from_net = pd.Series(src).str.startswith(ATTACKER_NET).values
    print(f"\nIDENTITY SHORTCUT: rule 'alarm if source IP starts with {ATTACKER_NET}' -> recall "
          f"{from_net[att].mean():.3f} at false-alarm rate {from_net[~att].mean():.4f} "
          "(IPs are NEVER model features; this only shows how easy the labels are by identity)")
    print(pd.crosstab(pd.Series(lab, name="label"), pd.Series(from_net, name="src in 175.45.176.x")).to_string())
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    np.savez(a.out, X=Xf.values[k].astype("float64"), cols=np.array(flow), lab=lab,
             missing=np.array(missing, dtype=str), seq=seq[k],
             ts=sec[rows][k], session=session[rows][k], row=rows[k],
             src_ip=src.astype(str), dst_ip=D["__dst_ip"].values[k].astype(str),
             sport=D["__sport"].values[k], dport=pd.to_numeric(pd.Series(dp_all[rows][k]), errors="coerce").values,
             proto=D["__proto"].values[k])
    sha = hashlib.sha256(open(a.out, "rb").read()).hexdigest()
    me = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()
    print(f"\nsaved -> {a.out}  ({int(k.sum()):,} flows, sequences {seq[k].shape}) [{time.time() - t0:.0f}s]")
    print(f"sha256 cache {sha[:16]} | prep_unsw.py {me[:16]}  (record both in the UNSW pre-registration)")


if __name__ == "__main__":
    main()
