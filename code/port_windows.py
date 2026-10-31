"""
IP-free temporal context: load of each destination SERVICE (Dst Port) over the last minutes.  Shared by
stage1_cicids2017_pipeline.py (--port_windows) and cross_dataset.py, so 2017 and 2018 get IDENTICAL features.

For a flow to port p at minute t (minutes counted from the start of its capture file; causal: only minutes <= t):
  pw_cnt_w1   flows to p in minute t                      (a decision is available at the end of the minute)
  pw_cnt_w5   flows to p in minutes t-4..t
  pw_hist60   mean flows/minute to p over the PREVIOUS 60 minutes (t-60..t-1), the service's own baseline
  pw_burst1   log(1+cnt_w1) - log(1+hist60)               jump of the service load relative to its own history
  pw_burst5   log(1+cnt_w5/5) - log(1+hist60)
  pw_zbwd_w1  share of the flows to p in minute t that have NO backward packet (unanswered: scans, floods)
  gl_burst1   the same jump for ALL traffic of the capture (whole-network load)
No IP address, host identity or port VALUE enters the features (the port only groups flows).
"""
import numpy as np
import pandas as pd

PW_COLS = ["pw_cnt_w1", "pw_cnt_w5", "pw_hist60", "pw_burst1", "pw_burst5", "pw_zbwd_w1", "gl_burst1"]
PW_REL = ["pw_burst1", "pw_burst5", "pw_zbwd_w1", "gl_burst1"]          # scale-free subset


def _lookup(ev_k, ev_v, rows_key):
    o = np.argsort(ev_k, kind="stable")
    ev_k, cum = ev_k[o], np.cumsum(ev_v[o])
    idx = np.searchsorted(ev_k, rows_key, side="right") - 1
    return np.where(idx >= 0, cum[np.maximum(idx, 0)], 0)


def _trail(K, m, w, T, mask):
    """number of masked events with the same key K in minutes m-w+1 .. m, looked up for every row"""
    key = K * T + m
    src = key[mask]
    if len(src) == 0:
        return np.zeros(len(key))
    uk, c = np.unique(src, return_counts=True)
    return _lookup(np.r_[uk, uk + w], np.r_[c, -c], key).astype("float64")


def port_window_features(port, minute, zero_bwd, valid=None):
    port = pd.to_numeric(pd.Series(np.asarray(port)), errors="coerce").fillna(-1).astype("int64").values
    m = np.asarray(minute, dtype="float64")
    valid = np.ones(len(m), bool) if valid is None else np.asarray(valid, bool)
    valid = valid & np.isfinite(m)
    m = np.where(valid, m, 0).astype("int64")
    if valid.any():
        m = np.where(valid, m - m[valid].min(), 0)
    m = np.maximum(m, 0)
    zb = np.asarray(zero_bwd, bool) & valid
    K = pd.factorize(port)[0].astype("int64")
    T = int(m.max()) + 70
    c1, c5, c61 = (_trail(K, m, w, T, valid) for w in (1, 5, 61))
    elapsed = m.astype("float64")
    hist = (c61 - c1) / np.clip(np.minimum(elapsed, 60), 1, None)
    n5 = np.clip(np.minimum(elapsed + 1, 5), 1, None)
    z1 = _trail(K, m, 1, T, zb)
    G = np.zeros_like(K)
    g1, g61 = _trail(G, m, 1, T, valid), _trail(G, m, 61, T, valid)
    ghist = (g61 - g1) / np.clip(np.minimum(elapsed, 60), 1, None)
    out = {"pw_cnt_w1": c1, "pw_cnt_w5": c5, "pw_hist60": hist,
           "pw_burst1": np.log1p(c1) - np.log1p(hist), "pw_burst5": np.log1p(c5 / n5) - np.log1p(hist),
           "pw_zbwd_w1": z1 / np.clip(c1, 1, None), "gl_burst1": np.log1p(g1) - np.log1p(ghist)}
    return pd.DataFrame({k: np.where(valid, v, 0).astype("float32") for k, v in out.items()})


# ----------------------------------------------------------------------------------------------- time sequences
SEQ_T = 16                                              # minutes t-15 .. t
SEQ_CH = ["port_rel", "port_zbwd", "glob_rel"]          # per minute: log-load of the service relative to its own
                                                        # 60-min baseline, unanswered share, same for all traffic


class PortTable:
    """Per-capture-file table of flow counts per (destination port, minute); answers the 7 pw_* features and the
    16-minute sequences for ANY subset of rows (so 2018 needs the table of the whole file but sequences only for
    the sampled rows). Same preprocessing as port_window_features (verified equal)."""

    def __init__(self, port, minute, zero_bwd, valid=None):
        port = pd.to_numeric(pd.Series(np.asarray(port)), errors="coerce").fillna(-1).astype("int64").values
        m = np.asarray(minute, dtype="float64")
        valid = np.ones(len(m), bool) if valid is None else np.asarray(valid, bool)
        valid = valid & np.isfinite(m)
        m = np.where(valid, m, 0).astype("int64")
        if valid.any():
            m = np.where(valid, m - m[valid].min(), 0)
        self.m = np.maximum(m, 0)
        self.valid = valid
        zb = np.asarray(zero_bwd, bool) & valid
        self.K = pd.factorize(port)[0].astype("int64")
        self.Tm = int(self.m.max()) + 70
        key = self.K * self.Tm + self.m
        self.uk, self.cnt = np.unique(key[valid], return_counts=True)
        self.zcnt = np.zeros(len(self.uk), "int64")
        uz, cz = np.unique(key[zb], return_counts=True)
        if len(uz):
            self.zcnt[np.searchsorted(self.uk, uz)] = cz
        self.gcnt = np.bincount(self.m[valid], minlength=self.Tm).astype("float64")
        c61 = _trail(self.K, self.m, 61, self.Tm, valid)
        c1, _ = self._at(key)
        el = np.clip(np.minimum(self.m, 60), 1, None).astype("float64")
        self.hist = (c61 - c1) / el
        g61 = _trail(np.zeros_like(self.K), self.m, 61, self.Tm, valid)
        self.ghist = (g61 - self.gcnt[self.m]) / el

    def _at(self, keys):
        idx = np.clip(np.searchsorted(self.uk, keys), 0, max(len(self.uk) - 1, 0))
        ok = (len(self.uk) > 0) & (self.uk[idx] == keys) if len(self.uk) else np.zeros(len(keys), bool)
        return np.where(ok, self.cnt[idx], 0).astype("float64"), np.where(ok, self.zcnt[idx], 0).astype("float64")

    def pw_features(self, rows):
        rows = np.asarray(rows)
        K, m, v = self.K[rows], self.m[rows], self.valid[rows]
        c1, z1 = self._at(K * self.Tm + m)
        c5 = np.zeros(len(rows))
        for j in range(5):
            mm = m - j
            c, _ = self._at(K * self.Tm + np.maximum(mm, 0))
            c5 += np.where(mm >= 0, c, 0)
        hist, ghist, g1 = self.hist[rows], self.ghist[rows], self.gcnt[m]
        n5 = np.clip(np.minimum(m + 1, 5), 1, None)
        out = {"pw_cnt_w1": c1, "pw_cnt_w5": c5, "pw_hist60": hist,
               "pw_burst1": np.log1p(c1) - np.log1p(hist), "pw_burst5": np.log1p(c5 / n5) - np.log1p(hist),
               "pw_zbwd_w1": z1 / np.clip(c1, 1, None), "gl_burst1": np.log1p(g1) - np.log1p(ghist)}
        return pd.DataFrame({k: np.where(v, x, 0).astype("float32") for k, x in out.items()})

    def sequences(self, rows, T=SEQ_T):
        rows = np.asarray(rows)
        K, m, v = self.K[rows], self.m[rows], self.valid[rows]
        lh, lg = np.log1p(self.hist[rows]), np.log1p(self.ghist[rows])
        out = np.zeros((len(rows), T, len(SEQ_CH)), "float32")
        for j in range(T):                                           # position j = minute t-(T-1-j); last = t
            mm = m - (T - 1 - j)
            okm = mm >= 0
            c, z = self._at(K * self.Tm + np.maximum(mm, 0))
            c, z = np.where(okm, c, 0), np.where(okm, z, 0)
            g = np.where(okm, self.gcnt[np.maximum(mm, 0)], 0)
            out[:, j, 0] = np.log1p(c) - lh
            out[:, j, 1] = z / np.clip(c, 1, None)
            out[:, j, 2] = np.log1p(g) - lg
        out[~v] = 0
        return np.clip(out, -8, 8)
