"""
EXPLORATORY (not part of the pre-registered confirmatory test; the confirmatory test was run once on 2026-10-25).

Builds a copy of the CIC-UNSW-NB15 target cache whose 16-minute service-load sequences ('seq') are computed from
ATTACK-FREE traffic only: the per-(port, minute) counts, the 60-minute baselines and the whole-network load are
taken from flows labelled Benign; attack flows do not enter any count. Every sampled flow (benign or attack) gets
its sequence from this benign-only table, so no sequence carries attack-induced load. Everything else in the cache
(features, labels, rows, timestamps) is copied unchanged. hybrid_v3.py and port_windows.py are NOT edited.

Note on interpretation: attack flows also lose their own contribution to the load, so the supervised models lose a
signal they could use. The question asked is only whether the novelty gain of V3-MAX survives without
attack-induced context.

  python ctx_clean_cache.py --csv "D:/revised model/CIC-UNSW-NB15/CICFlowMeter_out.csv" ^
      --cache "D:/revised model/unsw/unsw_sample_v1h.npz" --out "D:/revised model/unsw/unsw_sample_v1h_ctxclean.npz"
  python ctx_clean_cache.py --selftest
"""
import argparse, hashlib, os, time
import numpy as np
import pandas as pd
from port_windows import PortTable, SEQ_T, SEQ_CH, _trail


class PortTableCtx(PortTable):
    """PortTable whose counts come from `count_mask` rows only, while every finite-minute row can ask for a sequence.
    Minutes are offset by the minimum over ALL finite rows (as in prep_unsw), so the time axis is identical."""

    def __init__(self, port, minute, zero_bwd, count_mask):
        port = pd.to_numeric(pd.Series(np.asarray(port)), errors="coerce").fillna(-1).astype("int64").values
        m = np.asarray(minute, dtype="float64")
        fin = np.isfinite(m)
        cm = np.asarray(count_mask, bool) & fin
        m = np.where(fin, m, 0).astype("int64")
        if fin.any():
            m = np.where(fin, m - m[fin].min(), 0)
        self.m = np.maximum(m, 0)
        self.valid = fin
        zb = np.asarray(zero_bwd, bool) & cm
        self.K = pd.factorize(port)[0].astype("int64")
        self.Tm = int(self.m.max()) + 70
        key = self.K * self.Tm + self.m
        self.uk, self.cnt = np.unique(key[cm], return_counts=True)
        self.zcnt = np.zeros(len(self.uk), "int64")
        uz, cz = np.unique(key[zb], return_counts=True)
        if len(uz):
            self.zcnt[np.searchsorted(self.uk, uz)] = cz
        self.gcnt = np.bincount(self.m[cm], minlength=self.Tm).astype("float64")
        c61 = _trail(self.K, self.m, 61, self.Tm, cm)
        c1, _ = self._at(key)
        el = np.clip(np.minimum(self.m, 60), 1, None).astype("float64")
        self.hist = (c61 - c1) / el
        g61 = _trail(np.zeros_like(self.K), self.m, 61, self.Tm, cm)
        self.ghist = (g61 - self.gcnt[self.m]) / el


def selftest():
    g = np.random.default_rng(1)
    n = 6000
    port = g.choice([80, 443, 53, 22], n)
    minute = g.integers(0, 200, n).astype(float)
    zb = g.random(n) < 0.1
    att = g.random(n) < 0.2
    # 1) all benign: identical to the original PortTable
    a = PortTable(port, minute, zb, valid=np.isfinite(minute))
    b = PortTableCtx(port, minute, zb, np.ones(n, bool))
    rows = np.arange(0, n, 7)
    ok1 = np.allclose(a.sequences(rows), b.sequences(rows))
    print("PASS" if ok1 else "FAIL", "benign-only mask reproduces PortTable exactly")
    # 2) attacks change nothing when removed from the data: table on benign rows == ctx table with mask
    ben = ~att
    c = PortTable(port[ben], minute[ben], zb[ben], valid=np.isfinite(minute[ben]))
    d = PortTableCtx(port, minute, zb, ben)
    # minute offset: original uses min over its own rows; make both start at the same minute for the comparison
    off_ok = minute[ben].min() == minute.min()
    rb = np.where(ben)[0][::11]
    ok2 = (not off_ok) or np.allclose(c.sequences(np.searchsorted(np.where(ben)[0], rb)), d.sequences(rb))
    print("PASS" if ok2 else "FAIL", "counts ignore attack rows (benign rows get the sequences of a benign-only table)")
    # 3) attack rows are not zeroed
    ra = np.where(att)[0][:200]
    ok3 = np.abs(d.sequences(ra)).sum() > 0
    print("PASS" if ok3 else "FAIL", "attack rows still receive a (benign-load) sequence")
    # 4) sequences really differ from the contaminated ones for rows near attacks
    ok4 = np.abs(b.sequences(rows) - d.sequences(rows)).max() > 0
    print("PASS" if ok4 else "FAIL", "removing attacks changes the sequences")
    print("ALL PASS" if all([ok1, ok2, ok3, ok4]) else "SOME CHECKS FAILED")


def parse_ts(s):
    return pd.to_datetime(s, format="%d/%m/%Y %I:%M:%S %p", errors="coerce")


def find(cols, *names):
    n = {c: "".join(ch for ch in str(c).lower() if ch.isalnum()) for c in cols}
    for nm in names:
        for c, v in n.items():
            if v == nm:
                return c
    raise SystemExit(f"column not found: {names}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv")
    ap.add_argument("--cache")
    ap.add_argument("--out")
    ap.add_argument("--chunk", type=int, default=500000)
    ap.add_argument("--gap_hours", type=float, default=6.0)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    t0 = time.time()
    z = np.load(a.cache, allow_pickle=True)
    d = {k: z[k] for k in z.files}
    for k in ("row", "lab", "seq"):
        if k not in d:
            raise SystemExit(f"cache has no '{k}'")
    cols = list(pd.read_csv(a.csv, nrows=0).columns)
    c_lab, c_ts = find(cols, "label"), find(cols, "timestamp")
    c_dp, c_bw = find(cols, "dstport", "destinationport"), find(cols, "totalbwdpackets", "totbwdpkts", "totalbackwardpackets")
    labs, tss, dps, zbs = [], [], [], []
    for ch in pd.read_csv(a.csv, usecols=[c_lab, c_ts, c_dp, c_bw], chunksize=a.chunk, low_memory=False):
        labs.append(ch[c_lab].astype(str).str.strip().values)
        tss.append(parse_ts(ch[c_ts].astype(str)).values)
        dps.append(ch[c_dp].values)
        zbs.append(pd.to_numeric(ch[c_bw], errors="coerce").fillna(1).values == 0)
    lab_all, ts_all = np.concatenate(labs), pd.to_datetime(np.concatenate(tss))
    dp_all, zb_all = np.concatenate(dps), np.concatenate(zbs)
    N = len(lab_all)
    okt = ts_all.notna()
    sec = np.where(okt, ts_all.values.astype("datetime64[s]").astype("int64"), np.nan)
    order = np.argsort(np.where(np.isfinite(sec), sec, np.inf), kind="stable")
    ss = sec[order]
    brk = np.r_[False, np.diff(ss) > a.gap_hours * 3600]
    session = np.full(N, -1, "int64")
    session[order] = np.where(np.isfinite(ss), np.cumsum(brk), -1)
    rows = np.asarray(d["row"]).astype("int64")
    # ALIGNMENT CHECKS: the cache rows must be the same CSV rows (same label, same session, same timestamp)
    if not (lab_all[rows] == d["lab"].astype(str)).all():
        raise SystemExit("labels of the cache rows do not match the CSV: wrong CSV or cache")
    if "session" in d and not (session[rows] == np.asarray(d["session"])).all():
        raise SystemExit("sessions do not match the cache")
    if "ts" in d and not np.allclose(sec[rows], np.asarray(d["ts"], float), equal_nan=True):
        raise SystemExit("timestamps do not match the cache")
    print(f"alignment OK: {len(rows):,} cache rows match the CSV ({N:,} rows) [{time.time() - t0:.0f}s]")
    is_ben = lab_all == "Benign"
    new = np.zeros_like(d["seq"])
    for s in np.unique(session[session >= 0]):
        idx = np.where(session == s)[0]
        minute = (sec[idx] - np.nanmin(sec[idx])) // 60
        tab = PortTableCtx(dp_all[idx], minute, zb_all[idx], is_ben[idx])
        pos = np.searchsorted(idx, rows)
        inside = (pos < len(idx)) & (idx[np.minimum(pos, len(idx) - 1)] == rows)
        new[inside] = tab.sequences(pos[inside]).astype(new.dtype)
        print(f"  session {s}: benign-only table ({int((is_ben[idx]).sum()):,} of {len(idx):,} flows counted); "
              f"sequences for {int(inside.sum()):,} cache rows [{time.time() - t0:.0f}s]", flush=True)
    lab = d["lab"].astype(str)
    old = d["seq"].astype("float32")
    nw = new.astype("float32")
    print("\nmean |new - old| per channel, by label group (how much attack-induced load the old context had):")
    for nm, m in (("benign", lab == "Benign"), ("attack", lab != "Benign")):
        print(f"  {nm:7s}", {SEQ_CH[j]: round(float(np.abs(nw[m][:, :, j] - old[m][:, :, j]).mean()), 4) for j in range(len(SEQ_CH))})
    d["seq"] = new
    d["seq_note"] = np.array("seq rebuilt from benign-only service-load table; exploratory (ctx_clean_cache.py)")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    np.savez(a.out, **d)
    sha = hashlib.sha256(open(a.out, "rb").read()).hexdigest()[:16]
    print(f"\nsaved -> {a.out}  sha256 {sha}  [{time.time() - t0:.0f}s]")


if __name__ == "__main__":
    main()
