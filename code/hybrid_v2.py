"""
Hybrid IDS v2 (PyTorch): flow branches + TIME branches over the 16-minute service-load sequence, learned gate.
Evaluated with exactly the cross-dataset protocol of cross_dataset.py (train CIC-IDS2017 -> test CSE-CIC-IDS2018).

Inputs per flow
  xf  69 per-flow features (2017 quantile scaling, as for the trees)
  xs  16 x 3 sequence: for minutes t-15..t, load of the flow's destination SERVICE relative to its own 60-min baseline,
      share of unanswered flows to it, whole-network load relative to its baseline (port_windows.PortTable; no IPs)
Branches
  D  dense MLP on xf                                   (classical flow path)
  Q  quantum branch on xf: "inspired" two-path interference | "dense4" parameter-matched control | "vqc" PennyLane
  W  learnable Mallat wavelet filter bank along TIME (per channel, db2 start, QMF high-pass, orthonormality penalty)
  S  LIF spiking neurons driven by the sequence: one input current per minute (real temporal dynamics), learnable
     leak, positive learnable threshold, surrogate gradient; output = firing rates (all steps + last 4 steps)
  A  temporal self-attention over the 16 minute tokens (+ learned positions, CLS token)
  G  GRU over the sequence (CONTROL for W/S/A: a standard sequence model)
Fusion: softmax gate over the branch embeddings computed per sample (or "concat" control) -> MLP head -> one logit.

Configs (--configs)
  FLOW-MLP    D                      flow-only neural baseline (compare with the trees' "flow")
  SEQ-GRU     D + G                  standard sequence baseline
  FULL        D + Q(inspired) + W + S + A, gate
  FULL-SHUF   FULL, minutes randomly reordered inside every sequence (CONTROL: does the time ORDER matter?)
  FULL-PAST   FULL with the current minute hidden: strictly causal per flow (CONTROL: same-minute information)
  FULL-QD     FULL with Q = dense4 (CONTROL for the quantum branch)      FULL-VQC  Q = vqc (slow; few seeds)
  FULL-CONCAT FULL without the gate (CONTROL for the gate)                -W  -S  -A  -Q   ablations
Pre-registered: best tree baseline in loo = 0.299 (late fusion of trees) -> FULL succeeds if its loo mean
recall@1%FPR (threshold B) >= 0.399; it must also beat FULL-SHUF and SEQ-GRU (else the specific branches add nothing).

Run (CPU is fine; first --selftest, then --smoke):
  pip install torch            (pennylane only for FULL-VQC)
  python hybrid_v2.py --selftest
  python hybrid_v2.py --smoke
  python hybrid_v2.py --s17_dir "D:/revised model/stage1_pw" --cache18 "D:/revised model/cross_out4/ids2018_sample_v4.npz" --out_dir "D:/revised model/hybrid_out" --mode both --configs FLOW-MLP,SEQ-GRU,FULL,FULL-SHUF --seeds 3
"""
import argparse, json, os, time, warnings
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

COUNTERPART = {"FTP-BruteForce": "FTP-Patator", "SSH-Bruteforce": "SSH-Patator",
               "DoS attacks-GoldenEye": "DoS GoldenEye", "DoS attacks-Slowloris": "DoS slowloris",
               "DoS attacks-Hulk": "DoS Hulk", "DoS attacks-SlowHTTPTest": "DoS Slowhttptest",
               "DDoS attacks-LOIC-HTTP": "DDoS", "DDOS attack-HOIC": None, "DDOS attack-LOIC-UDP": None,
               "Brute Force -Web": "Web Attack - Brute Force", "Brute Force -XSS": "Web Attack - XSS",
               "SQL Injection": "Web Attack - Sql Injection", "Infilteration": "Infiltration", "Bot": "Bot"}
NEW = "none (new in 2018)"
BASELINE_LOO = 0.299                       # best tree baseline (late fusion), cross_out3 run 4


# ============================================================================ building blocks
class SpikeFn(torch.autograd.Function):
    """Heaviside forward, fast-sigmoid surrogate gradient backward."""
    @staticmethod
    def forward(ctx, v, slope):
        ctx.save_for_backward(v)
        ctx.slope = float(slope)
        return (v > 0).to(v.dtype)

    @staticmethod
    def backward(ctx, g):
        (v,) = ctx.saved_tensors
        return g / (1.0 + ctx.slope * v.abs()) ** 2, None


class FlowMLP(nn.Module):
    def __init__(self, d, hid):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, 64), nn.GELU(), nn.LayerNorm(64), nn.Linear(64, hid), nn.GELU(),
                                 nn.LayerNorm(hid))

    def forward(self, xf, xs):
        return self.net(xf)


class QuantumBranch(nn.Module):
    def __init__(self, d, hid, mode="inspired", nq=6, layers=2):
        super().__init__()
        self.mode, self.nq = mode, nq
        if mode == "inspired":                       # |a1 e^{i p1} + a2 e^{i p2}|^2 = a1^2 + a2^2 + 2 a1 a2 cos(p1 - p2)
            self.a1, self.a2, self.p1, self.p2 = (nn.Linear(d, nq) for _ in range(4))
        elif mode == "dense4":                       # parameter-matched classical control (~ same size as inspired)
            self.fc = nn.Sequential(nn.Linear(d, 4 * nq), nn.Tanh(), nn.Linear(4 * nq, nq), nn.Tanh())
        elif mode == "vqc":
            import pennylane as qml
            self.enc = nn.Linear(d, nq)
            self.w = nn.Parameter(0.1 * torch.randn(layers, nq, 3))
            dev = qml.device("default.qubit", wires=nq)

            @qml.qnode(dev, interface="torch", diff_method="backprop")
            def circ(inputs, weights):
                qml.AngleEmbedding(inputs, wires=range(nq), rotation="Y")
                qml.StronglyEntanglingLayers(weights, wires=range(nq))
                return [qml.expval(qml.PauliZ(i)) for i in range(nq)]
            self.circ = circ
        else:
            raise ValueError(mode)
        self.out = nn.Sequential(nn.Linear(nq, hid), nn.GELU(), nn.LayerNorm(hid))

    def forward(self, xf, xs):
        if self.mode == "inspired":
            a1, a2 = F.softplus(self.a1(xf)), F.softplus(self.a2(xf))
            ph = np.pi * (torch.tanh(self.p1(xf)) - torch.tanh(self.p2(xf)))
            q = torch.log1p(a1 * a1 + a2 * a2 + 2 * a1 * a2 * torch.cos(ph))
        elif self.mode == "dense4":
            q = self.fc(xf)
        else:
            z = np.pi * torch.tanh(self.enc(xf))
            r = self.circ(z.cpu(), self.w.cpu())
            r = torch.stack(list(r), dim=-1) if isinstance(r, (list, tuple)) else r
            if r.shape[0] != xf.shape[0]:
                r = r.T
            q = r.to(device=xf.device, dtype=xf.dtype)
        return self.out(q)


class WaveletTime(nn.Module):
    """Learnable Mallat filter bank along the time axis, shared over channels: T -> T/2 + T/4 + ... + approximation."""
    def __init__(self, T, C, hid, levels=3, k=4):
        super().__init__()
        assert T % (2 ** levels) == 0, "T must be divisible by 2**levels"
        self.levels, self.k = levels, k
        self.h = nn.Parameter(torch.tensor([0.48296291, 0.83651630, 0.22414387, -0.12940952]))   # Daubechies-2
        self.register_buffer("sign", torch.tensor([(-1.0) ** n for n in range(k)]))
        self.proj = nn.Sequential(nn.LayerNorm(C * T), nn.Linear(C * T, hid), nn.GELU(), nn.LayerNorm(hid))

    def coeffs(self, xs):                                   # xs (B,T,C) -> (B, C*T) [details fine->coarse, approx]
        B, T, C = xs.shape
        a = xs.permute(0, 2, 1).reshape(B * C, 1, T)
        h = self.h.view(1, 1, -1)
        g = (self.h.flip(0) * self.sign).view(1, 1, -1)    # quadrature-mirror high-pass
        out = []
        for _ in range(self.levels):
            ap = F.pad(a, (1, 1), mode="circular")         # periodic extension -> orthonormal transform
            out.append(F.conv1d(ap, g, stride=2)[..., : a.shape[-1] // 2])
            a = F.conv1d(ap, h, stride=2)[..., : a.shape[-1] // 2]
        out.append(a)
        return torch.cat(out, dim=-1).reshape(B, C * T)

    def forward(self, xf, xs):
        return self.proj(self.coeffs(xs))

    def regularizer(self):
        h = self.h
        r = (h.pow(2).sum() - 1.0) ** 2 + (h.sum() - float(np.sqrt(2.0))) ** 2
        for m in range(2, self.k, 2):
            r = r + (h[:-m] * h[m:]).sum() ** 2
        return r


class LIFTime(nn.Module):
    """Leaky integrate-and-fire neurons driven by one input current per minute of the sequence."""
    def __init__(self, C, hid, beta=0.9, slope=5.0):
        super().__init__()
        self.fc = nn.Linear(C, hid)
        self.beta_raw = nn.Parameter(torch.full((hid,), float(np.log(beta / (1 - beta)))))
        self.thr_raw = nn.Parameter(torch.full((hid,), float(np.log(np.e - 1))))          # softplus -> 1.0
        self.slope = slope
        self.proj = nn.Sequential(nn.Linear(2 * hid, hid), nn.GELU(), nn.LayerNorm(hid))
        self.last_rate = None

    def threshold(self):
        return F.softplus(self.thr_raw) + 0.05                                             # always positive

    def forward(self, xf, xs):
        B, T, C = xs.shape
        cur = self.fc(xs)                                                                  # (B,T,hid)
        beta, thr = torch.sigmoid(self.beta_raw), self.threshold()
        v = torch.zeros(B, cur.shape[-1], device=xs.device, dtype=xs.dtype)
        tot, recent = torch.zeros_like(v), torch.zeros_like(v)
        for t in range(T):
            v = beta * v + cur[:, t]
            s = SpikeFn.apply(v - thr, self.slope)
            v = v - s * thr                                                                # soft reset
            tot = tot + s
            if t >= T - 4:
                recent = recent + s
        rate = tot / T
        self.last_rate = rate.detach().mean()
        return self.proj(torch.cat([rate, recent / 4], dim=-1))


class TemporalAttention(nn.Module):
    def __init__(self, T, C, hid, d=32, heads=2):
        super().__init__()
        self.inp = nn.Linear(C, d)
        self.pos = nn.Parameter(0.02 * torch.randn(1, T, d))
        self.cls = nn.Parameter(0.02 * torch.randn(1, 1, d))
        self.att = nn.MultiheadAttention(d, heads, batch_first=True)
        self.ln1, self.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.ff = nn.Sequential(nn.Linear(d, 2 * d), nn.GELU(), nn.Linear(2 * d, d))
        self.out = nn.Sequential(nn.Linear(d, hid), nn.GELU(), nn.LayerNorm(hid))
        self.last_attn = None

    def forward(self, xf, xs):
        z = self.inp(xs) + self.pos
        z = torch.cat([self.cls.expand(xs.shape[0], -1, -1), z], dim=1)                   # (B, 1+T, d)
        a, w = self.att(z, z, z, need_weights=True, average_attn_weights=True)
        z = self.ln1(z + a)
        z = self.ln2(z + self.ff(z))
        wm = w[:, 0, 1:]                                                                   # CLS -> the 16 minutes
        self.last_attn = (wm / wm.sum(-1, keepdim=True).clamp_min(1e-9)).detach().mean(0)
        return self.out(z[:, 0])


class GRUSeq(nn.Module):
    def __init__(self, C, hid):
        super().__init__()
        self.gru = nn.GRU(C, hid, batch_first=True)
        self.ln = nn.LayerNorm(hid)

    def forward(self, xf, xs):
        _, h = self.gru(xs)
        return self.ln(h[-1])


class TreeBranch(nn.Module):
    """v2.1 flow expert: embeds the logit of a gradient-boosted tree (HistGB) trained on a DISJOINT 2017 subset.
    Trees transfer across networks far better than an MLP on the same 69 features (run 14: .26 vs .004)."""
    def __init__(self, hid):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(1, hid), nn.GELU(), nn.Linear(hid, hid), nn.GELU(), nn.LayerNorm(hid))

    def forward(self, xt, xs):
        return self.net(xt)


class HybridV2(nn.Module):
    def __init__(self, d, T, C, branches, q_mode="inspired", fuse="gate", shuffle=False, mask_last=False, hid=32,
                 dropout=0.1, balance=False, bdrop=0.0):
        super().__init__()
        mk = {"D": lambda: FlowMLP(d, hid), "Q": lambda: QuantumBranch(d, hid, q_mode),
              "W": lambda: WaveletTime(T, C, hid), "S": lambda: LIFTime(C, hid),
              "A": lambda: TemporalAttention(T, C, hid), "G": lambda: GRUSeq(C, hid), "T": lambda: TreeBranch(hid)}
        self.d, self.balance, self.bdrop, self._g = d, balance, bdrop, None
        self.names = list(branches)
        self.br = nn.ModuleList([mk[b]() for b in self.names])
        self.fuse, self.shuffle, self.mask_last = fuse, shuffle, mask_last
        nb = len(self.br)
        self.gate = nn.Linear(nb * hid, nb) if fuse == "gate" and nb > 1 else None
        self.head = nn.Sequential(nn.Linear(hid if fuse == "gate" or nb == 1 else nb * hid, hid), nn.GELU(),
                                  nn.Dropout(dropout), nn.Linear(hid, 1))
        self.last_gate = None

    def forward(self, xf, xs):
        if self.mask_last:                                     # strictly past: the current minute t is hidden
            xs = torch.cat([xs[:, :-1], torch.zeros_like(xs[:, -1:])], dim=1)
        if self.shuffle:                                       # random order of the minutes, per sample
            idx = torch.argsort(torch.rand(xs.shape[0], xs.shape[1], device=xs.device), dim=1)
            xs = torch.gather(xs, 1, idx.unsqueeze(-1).expand_as(xs))
        xflow = xf[:, : self.d]                                # column d (if present) = tree-expert logit
        xt = xf[:, self.d: self.d + 1] if xf.shape[1] > self.d else torch.zeros_like(xf[:, :1])
        H = torch.stack([b(xt, xs) if isinstance(b, TreeBranch) else b(xflow, xs) for b in self.br], dim=1)
        if len(self.br) == 1:
            z = H[:, 0]
        elif self.gate is not None:
            logits = self.gate(H.flatten(1))
            if self.training and self.bdrop > 0:               # branch dropout: every branch must be useful alone
                keep = torch.rand_like(logits) > self.bdrop
                none = ~keep.any(dim=1)
                if none.any():
                    rows = none.nonzero(as_tuple=True)[0]
                    keep[rows, torch.randint(0, keep.shape[1], (len(rows),), device=keep.device)] = True
                logits = logits.masked_fill(~keep, -1e9)
            g = torch.softmax(logits, dim=-1)
            self._g = g
            self.last_gate = g.detach().mean(0)
            z = (g.unsqueeze(-1) * H).sum(1)
        else:
            z = H.flatten(1)
        return self.head(z).squeeze(-1)

    def regularizer(self):
        return sum((b.regularizer() for b in self.br if isinstance(b, WaveletTime)), torch.zeros(()))

    def balance_loss(self):
        """KL(mean gate over the batch || uniform): >= 0, = 0 when every branch is used equally often on average
        (per-sample choices stay free) -> prevents the collapse onto one branch seen in run 14."""
        if not self.balance or self._g is None:
            return torch.zeros(())
        gm = self._g.mean(0)
        return (gm * torch.log(gm * gm.numel() + 1e-9)).sum()


CONFIGS = {
    "FLOW-MLP": dict(branches="D"),
    "SEQ-GRU": dict(branches="DG"),
    "FULL": dict(branches="DQWSA"),
    "FULL-SHUF": dict(branches="DQWSA", shuffle=True),
    "FULL-PAST": dict(branches="DQWSA", mask_last=True),   # CONTROL: only minutes t-15..t-1 (no same-minute info)
    "FULL-QD": dict(branches="DQWSA", q_mode="dense4"),
    "FULL-VQC": dict(branches="DQWSA", q_mode="vqc"),
    "FULL-CONCAT": dict(branches="DQWSA", fuse="concat"),
    "-W": dict(branches="DQSA"), "-S": dict(branches="DQWA"), "-A": dict(branches="DQWS"), "-Q": dict(branches="DWSA"),
    # ---- v2.1 (pre-registered revision after run 14): tree expert + balanced gate + branch dropout
    "TREE": dict(branches="T"),                                                   # tree expert alone (control)
    "H21-FLOW": dict(branches="TDQ", balance=True, bdrop=0.2),                    # no temporal branches (control)
    "H21-FULL": dict(branches="TDQWSA", balance=True, bdrop=0.2),                 # the v2.1 model
    "H21-SHUF": dict(branches="TDQWSA", balance=True, bdrop=0.2, shuffle=True),   # time order destroyed
    "H21-GRU": dict(branches="TDG", balance=True, bdrop=0.2),                     # standard sequence model
    "H21-NOBAL": dict(branches="TDQWSA"),                                         # gate without balance/dropout
    "H21-QD": dict(branches="TDQWSA", balance=True, bdrop=0.2, q_mode="dense4"),  # quantum control
    "H21-PAST": dict(branches="TDQWSA", balance=True, bdrop=0.2, mask_last=True), # strictly causal per flow
    # leave-one-component-out ablations of v2.1 (importance of each thesis component)
    "H21-noQ": dict(branches="TDWSA", balance=True, bdrop=0.2),
    "H21-noW": dict(branches="TDQSA", balance=True, bdrop=0.2),
    "H21-noS": dict(branches="TDQWA", balance=True, bdrop=0.2),
    "H21-noA": dict(branches="TDQWS", balance=True, bdrop=0.2),
}
TREE_CFG = {c for c, v in CONFIGS.items() if "T" in v["branches"]}


# ============================================================================ data
def sub_idx(y, n, seed):
    if n is None or n <= 0 or n >= len(y):
        return np.arange(len(y))
    try:
        idx, _ = train_test_split(np.arange(len(y)), train_size=n, stratify=y, random_state=seed)
    except ValueError:
        idx = np.random.default_rng(seed).choice(len(y), n, replace=False)
    return np.sort(idx)


def prep_seq(S):
    return np.clip(np.asarray(S, dtype="float32"), -8, 8) / 4.0


def load_real(a):
    import joblib
    feats = json.load(open(os.path.join(a.s17_dir, "feature_names.json")))
    flow = [f for f in feats if not f.startswith(("win_", "pw_", "gl_"))]
    fidx = np.array([feats.index(c) for c in flow])
    z = np.load(os.path.join(a.s17_dir, "splits.npz"), allow_pickle=True)
    q = np.load(os.path.join(a.s17_dir, "seq17.npz"))
    D = dict(Xtr=z["Xtr"][:, fidx], Xva=z["Xva"][:, fidx], ytr=z["ytr"].astype(int), yva=z["yva"].astype(int),
             atr=z["atr"].astype(str), ava=z["ava"].astype(str), Str=prep_seq(q["Str"]), Sva=prep_seq(q["Sva"]))
    if len(D["Str"]) != len(D["ytr"]):
        raise SystemExit("seq17.npz does not match splits.npz -> run stage 1 with --seq into the same folder")
    qt = joblib.load(os.path.join(a.s17_dir, "quantile_transformer.joblib"))
    zc = np.load(a.cache18, allow_pickle=True)
    if "seq" not in zc.files:
        raise SystemExit("the 2018 cache has no sequences -> cross_dataset.py --seq --prep_only")
    X18raw = pd.DataFrame(zc["X"], columns=list(zc["cols"]))
    full = pd.DataFrame(0.0, index=X18raw.index, columns=feats)
    for c in feats:
        if c in X18raw.columns:
            full[c] = X18raw[c].values
    D["X18"] = qt.transform(full)[:, fidx].astype("float32")              # 2017 transformer, never refit
    D["S18"] = prep_seq(zc["seq"])
    D["lab18"] = zc["lab"].astype(str)
    return D


def make_smoke(seed=0):
    """small synthetic stand-in with the same structure (attacks raise the service-load sequence)"""
    rng = np.random.default_rng(seed)
    fams17 = ["DDoS", "DoS Hulk", "FTP-Patator", "Bot"]
    def block(n, fams, p_att, shift):
        y = (rng.random(n) < p_att).astype(int)
        a = np.where(y == 1, rng.choice(fams, n), "BENIGN")
        X = rng.random((n, 69)).astype("float32"); X[y == 1, :5] += 0.3
        S = rng.normal(0, 0.3, (n, 16, 3)).astype("float32")
        S[y == 1, -4:, 0] += 1.5 + shift
        return X, y, a, S
    Xtr, ytr, atr, Str = block(6000, fams17, 0.2, 0.0)
    Xva, yva, ava, Sva = block(2000, fams17, 0.2, 0.0)
    n18 = 6000
    lab18 = np.where(rng.random(n18) < 0.6, "Benign",
                     rng.choice(["DDoS attacks-LOIC-HTTP", "DoS attacks-Hulk", "FTP-BruteForce", "DDOS attack-HOIC"], n18))
    X18 = rng.random((n18, 69)).astype("float32"); S18 = rng.normal(0, 0.3, (n18, 16, 3)).astype("float32")
    att = lab18 != "Benign"; X18[att, :5] += 0.1; S18[att, -4:, 0] += 1.2
    return dict(Xtr=Xtr, Xva=Xva, ytr=ytr, yva=yva, atr=atr, ava=ava, Str=Str / 4, Sva=Sva / 4,
                X18=X18, S18=S18 / 4, lab18=lab18)


# ============================================================================ training / scoring
def fit(cfg, Xf, Xs, y, Xvf, Xvs, yv, seed, a, dev, d=None):
    torch.manual_seed(seed); np.random.seed(seed)
    c = dict(CONFIGS[cfg])
    model = HybridV2(d or Xf.shape[1], Xs.shape[1], Xs.shape[2], c.pop("branches"), **c).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    pos = max(int(y.sum()), 1)
    lossf = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(min((len(y) - pos) / pos, 20.0), device=dev))
    tf, ts, ty = (torch.tensor(v) for v in (Xf, Xs, y.astype("float32")))
    vf, vs, vy = (torch.tensor(v, device=dev) for v in (Xvf, Xvs, yv.astype("float32")))
    best, best_state, bad = np.inf, None, 0
    g = torch.Generator().manual_seed(seed)
    for ep in range(a.epochs):
        model.train()
        perm = torch.randperm(len(ty), generator=g)
        for k in range(0, len(perm), a.bs):
            b = perm[k:k + a.bs]
            out = model(tf[b].to(dev), ts[b].to(dev))
            loss = (lossf(out, ty[b].to(dev)) + 0.1 * model.regularizer().to(dev)
                    + a.lb * model.balance_loss().to(dev))
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
        model.eval()
        with torch.no_grad(), torch.random.fork_rng(devices=[]):
            torch.manual_seed(12345)                           # same validation shuffles every epoch (FULL-SHUF)
            vl = float(np.mean([lossf(model(vf[k:k + 4096], vs[k:k + 4096]), vy[k:k + 4096]).item()
                                for k in range(0, len(vy), 4096)]))
        if vl < best - 1e-4:
            best, bad = vl, 0
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= a.patience:
                break
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    return model


@torch.no_grad()
def score(model, Xf, Xs, dev, bs=8192, track=False):
    """scores; with track=True also the sample-weighted mean gate weights and temporal-attention weights"""
    torch.manual_seed(0)                                     # fixed shuffling for FULL-SHUF at test time
    att = next((b for b in model.br if isinstance(b, TemporalAttention)), None)
    out, gs, ats, n = [], 0.0, 0.0, 0
    for k in range(0, len(Xf), bs):
        o = model(torch.tensor(Xf[k:k + bs], device=dev), torch.tensor(Xs[k:k + bs], device=dev))
        out.append(torch.sigmoid(o).cpu())
        nb = len(o)
        if track and model.last_gate is not None:
            gs = gs + model.last_gate.cpu().numpy() * nb
        if track and att is not None:
            ats = ats + att.last_attn.cpu().numpy() * nb
        n += nb
    s = torch.cat(out).numpy() if out else np.zeros(0, "float32")
    if not track:
        return s
    g = (gs / max(n, 1)).round(4).tolist() if model.last_gate is not None and n else None
    a = (ats / max(n, 1)).round(4).tolist() if att is not None and n else None
    return s, g, a


def run(D, a, dev, out_dir):
    lab18 = D["lab18"]
    ben = np.where(lab18 == "Benign")[0]
    rng = np.random.default_rng(0); rng.shuffle(ben)
    k3 = len(ben) // 3
    cal, bte = ben[k3:2 * k3], ben[2 * k3:]                  # identical split to cross_dataset.py
    types = list(pd.Series(lab18[lab18 != "Benign"]).value_counts().index)
    cfgs = [c.strip() for c in a.configs.split(",") if c.strip()]
    bad = [c for c in cfgs if c not in CONFIGS]
    if bad:
        raise SystemExit(f"unknown configs {bad}; available {list(CONFIGS)}")
    scen_list = (["known"] if a.mode in ("known", "both") else []) + (["loo"] if a.mode in ("loo", "both") else [])
    rows, diag, per_type, saved, t0 = [], [], [], {}, time.time()
    csv = os.path.join(out_dir, "hybrid_v2_results.csv")
    for scen in scen_list:
        helds = [None] if scen == "known" else sorted({c for t, c in COUNTERPART.items() if c and t in types})
        for held in helds:
            if held and not (D["atr"] == held).any():
                print(f"  {held}: not in 2017 train split, skipped"); continue
            mt = (D["atr"] != held) if held else np.ones(len(D["atr"]), bool)
            mv = (D["ava"] != held) if held else np.ones(len(D["ava"]), bool)
            for seed in range(a.seeds):
                i = sub_idx(D["ytr"][mt], a.max_train, seed); j = sub_idx(D["yva"][mv], a.val_max, seed)
                Xf, Xs, y = D["Xtr"][mt][i], D["Str"][mt][i], D["ytr"][mt][i]
                Vf, Vs, vy = D["Xva"][mv][j], D["Sva"][mv][j], D["yva"][mv][j]
                X18 = D["X18"]
                if any(c in TREE_CFG for c in cfgs):            # tree expert on a DISJOINT 2017 subset (no leakage)
                    from sklearn.ensemble import HistGradientBoostingClassifier
                    pool = np.where(mt)[0]
                    rest = np.setdiff1d(np.arange(len(pool)), i)
                    k = pool[rest[sub_idx(D["ytr"][pool[rest]], a.tree_train, seed + 100)]]
                    tree = HistGradientBoostingClassifier(max_iter=200, random_state=seed).fit(D["Xtr"][k], D["ytr"][k])
                    def tlogit(M):
                        p = np.clip(tree.predict_proba(M)[:, 1], 1e-6, 1 - 1e-6)
                        return (np.clip(np.log(p / (1 - p)), -10, 10) / 5).astype("float32")[:, None]
                    Xf, Vf = np.hstack([Xf, tlogit(Xf)]), np.hstack([Vf, tlogit(Vf)])
                    X18 = np.hstack([D["X18"], tlogit(D["X18"])])
                for cfg in cfgs:
                    t1 = time.time()
                    m = fit(cfg, Xf, Xs, y, Vf, Vs, vy, seed, a, dev, d=D["X18"].shape[1])
                    sv = score(m, Vf[vy == 0], Vs[vy == 0], dev)
                    s_cal, s_bte = score(m, X18[cal], D["S18"][cal], dev), score(m, X18[bte], D["S18"][bte], dev)
                    tA1, tB1, tB01 = np.quantile(sv, 0.99), np.quantile(s_cal, 0.99), np.quantile(s_cal, 0.999)
                    for t in types:
                        cp = COUNTERPART.get(t) or NEW
                        if scen == "loo" and (cp == NEW or cp != held):
                            continue
                        sel = lab18 == t
                        sp, g_t, a_t = score(m, X18[sel], D["S18"][sel], dev, track=True)
                        per_type.append(dict(scenario=scen, held=held, seed=seed, model=cfg, type18=t,
                                             branches="".join(m.names), gate=json.dumps(g_t), attn=json.dumps(a_t)))
                        if seed == 0:
                            saved[f"{scen}|{held}|{cfg}|{t}"] = sp.astype("float16")
                        auc = roc_auc_score(np.r_[np.ones(len(sp)), np.zeros(len(s_bte))], np.r_[sp, s_bte])
                        rows.append(dict(scenario=scen, model=cfg, fset="nn", type18=t, counterpart17=cp, n=len(sp),
                                         seed=seed, auc=auc, recB_1=float((sp >= tB1).mean()),
                                         recB_01=float((sp >= tB01).mean()), fprB_1=float((s_bte >= tB1).mean()),
                                         recA_1=float((sp >= tA1).mean()), fprA_1=float((s_bte >= tA1).mean())))
                    _, g_b, a_b = score(m, X18[bte], D["S18"][bte], dev, track=True)
                    per_type.append(dict(scenario=scen, held=held, seed=seed, model=cfg, type18="Benign (test)",
                                         branches="".join(m.names), gate=json.dumps(g_b), attn=json.dumps(a_b)))
                    if seed == 0:
                        saved[f"{scen}|{held}|{cfg}|Benign"] = s_bte.astype("float16")
                    gate = [round(float(x), 3) for x in g_b] if g_b is not None else None
                    diag.append(dict(scenario=scen, held=held, seed=seed, model=cfg, branches="".join(m.names),
                                     gate=gate, secs=round(time.time() - t1, 1)))
                    print(f"  {scen:5s} {str(held or 'all'):26s} seed={seed} {cfg:11s} gate={gate} "
                          f"[{time.time() - t1:.0f}s, total {time.time() - t0:.0f}s]", flush=True)
                pd.DataFrame(rows).to_csv(csv, index=False)          # saved as it goes (safe to interrupt)
    pd.DataFrame(diag).to_csv(os.path.join(out_dir, "hybrid_v2_runs.csv"), index=False)
    pd.DataFrame(per_type).to_csv(os.path.join(out_dir, "hybrid_v2_gates.csv"), index=False)   # per attack type
    np.savez_compressed(os.path.join(out_dir, "hybrid_v2_scores_seed0.npz"), **saved)          # for ROC/PR figures
    return pd.DataFrame(rows)


def report(df, out_dir):
    L = []
    say = lambda s="": (print(s), L.append(s))
    say("\n==== SUMMARY: mean recall @ 1% FPR (threshold B) over 2018 attack types, mean (sd) over seeds")
    g = df.groupby(["scenario", "model", "seed"])["recB_1"].mean().groupby(["scenario", "model"])
    sm = pd.DataFrame({"mean": g.mean(), "sd": g.std()})
    say(sm.round(3).to_string())
    if "loo" in sm.index.get_level_values(0):
        lo = sm.loc["loo"]["mean"]
        say(f"\n==== PRE-REGISTERED (loo): FULL must reach >= {BASELINE_LOO + 0.10:.3f} "
            f"(tree baseline {BASELINE_LOO:.3f} + 0.10) and beat FULL-SHUF and SEQ-GRU")
        if "FULL" in lo:
            v = lo["FULL"]
            per = df[df.scenario == "loo"].groupby(["model", "seed"])["recB_1"].mean().unstack(0)
            beats = all(lo.get(c, -1) < v for c in ("FULL-SHUF", "SEQ-GRU") if c in lo)
            say(f"  FULL {v:.3f}  -> target {'MET' if v >= BASELINE_LOO + 0.10 else 'not met'}; beats FULL-SHUF "
                f"and SEQ-GRU: {'yes' if beats else 'NO'}  => overall: "
                + ("SUCCESS" if v >= BASELINE_LOO + 0.10 and beats else "not a success under the pre-registered rule"))
            for ctrl in ("FULL-SHUF", "SEQ-GRU", "FLOW-MLP", "FULL-QD", "FULL-CONCAT", "-W", "-S", "-A", "-Q"):
                if ctrl in per:
                    d = (per["FULL"] - per[ctrl]).dropna()
                    say(f"  FULL - {ctrl:11s} {d.mean():+.3f}  (seeds where FULL is better: {int((d > 0).sum())}/{len(d)})")
    if "loo" in sm.index.get_level_values(0) and "H21-FULL" in sm.loc["loo"].index:
        lo = sm.loc["loo"]["mean"]; v = lo["H21-FULL"]
        say(f"\n==== PRE-REGISTERED v2.1 (loo, DEVELOPMENT on 2018; confirmation on the 3rd dataset):")
        say(f"  primary: H21-FULL >= {BASELINE_LOO + 0.10:.3f} AND > H21-FLOW (the temporal branches add to the tree expert)")
        base = lo.get("H21-FLOW", np.nan)
        ok = v >= BASELINE_LOO + 0.10 and v > base
        say(f"  H21-FULL {v:.3f} | H21-FLOW {base:.3f} | TREE {lo.get('TREE', np.nan):.3f}  => primary: "
            + ("MET" if ok else "not met"))
        per = df[df.scenario == "loo"].groupby(["model", "seed"])["recB_1"].mean().unstack(0)
        for ctrl in ("H21-FLOW", "TREE", "H21-SHUF", "H21-GRU", "H21-NOBAL", "H21-QD", "H21-PAST",
                     "H21-noQ", "H21-noW", "H21-noS", "H21-noA"):
            if ctrl in per:
                dd = (per["H21-FULL"] - per[ctrl]).dropna()
                say(f"  H21-FULL - {ctrl:10s} {dd.mean():+.3f}  (seeds where H21-FULL is better: {int((dd > 0).sum())}/{len(dd)})")
    for scen in df.scenario.unique():
        d = df[df.scenario == scen]
        for col, txt in (("recB_1", "recall @ 1% FPR, threshold B"), ("auc", "AUC vs 2018 benign")):
            pv = d.pivot_table(index="type18", columns="model", values=col, aggfunc="mean")
            pv.insert(0, "2017 counterpart", [COUNTERPART.get(t) or NEW for t in pv.index])
            say(f"\n-- [{scen}] {txt}")
            say(pv.round(3).to_string())
        say(f"\n-- [{scen}] real false-alarm rate on the separate 2018 benign TEST third: threshold B (nominal 1%) "
            f"and threshold A (2017 benign, nominal 1%)")
        say(d.groupby("model")[["fprB_1", "fprA_1"]].mean().round(3).to_string())
        if scen == "known":
            newt = d[d.counterpart17 == NEW]
            if len(newt):
                say("\n-- [known] attack types with NO 2017 counterpart (genuinely new in 2018), mean recall@1%FPR (B)")
                say(newt.groupby(["model", "seed"])["recB_1"].mean().groupby("model").agg(["mean", "std"]).round(3).to_string())
    open(os.path.join(out_dir, "report.txt"), "w", encoding="utf-8").write("\n".join(L))


# ============================================================================ self test
def selftest():
    torch.manual_seed(0)
    ok_all = True
    def check(name, ok, info=""):
        nonlocal ok_all
        ok_all &= bool(ok)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} {info}")
    B, T, C, d = 8, 16, 3, 69
    xf, xs = torch.randn(B, d), torch.randn(B, T, C)
    w = WaveletTime(T, C, 32)
    co = w.coeffs(xs)
    e0, e1 = float((xs ** 2).sum()), float((co ** 2).sum())
    check("wavelet over time: shape", co.shape == (B, C * T), str(tuple(co.shape)))
    check("wavelet over time: energy preserved at init (orthonormal, periodic)", abs(e0 - e1) < 1e-3 * e0,
          f"({e0:.4f} vs {e1:.4f})")
    check("wavelet: orthonormality penalty ~ 0 at init", float(w.regularizer()) < 1e-6)
    const = torch.ones(1, T, C)
    cd = w.coeffs(const)[0].view(C, T)[:, : T - 2]
    check("wavelet: a constant sequence has zero detail coefficients", float(cd.abs().max()) < 1e-4)
    lif = LIFTime(C, 32)
    xs_req = xs.clone().requires_grad_(True)
    out = lif(xf, xs_req)
    out.sum().backward()
    check("LIF: firing rate in [0,1]", 0 <= float(lif.last_rate) <= 1, f"(mean rate {float(lif.last_rate):.3f})")
    check("LIF: gradient reaches the input of every minute",
          bool((xs_req.grad.abs().sum(dim=(0, 2)) > 0).all()))
    check("LIF: threshold positive", bool((lif.threshold() > 0).all()))
    z = torch.zeros(1, T, C); z1 = z.clone(); z1[0, 3, 0] = 5.0; z2 = z.clone(); z2[0, 12, 0] = 5.0
    check("LIF: output depends on WHEN the input arrives", float((lif(None, z1) - lif(None, z2)).abs().sum()) > 0)
    att = TemporalAttention(T, C, 32)
    att(xf, xs)
    check("attention: weights over the 16 minutes sum to 1", abs(float(att.last_attn.sum()) - 1) < 1e-4)
    for cfg in ("FLOW-MLP", "SEQ-GRU", "FULL", "FULL-QD", "FULL-CONCAT", "-W"):
        c = dict(CONFIGS[cfg]); m = HybridV2(d, T, C, c.pop("branches"), **c)
        y = m(xf, xs)
        check(f"model {cfg}: output shape", y.shape == (B,))
        if m.last_gate is not None:
            check(f"model {cfg}: gate sums to 1", abs(float(m.last_gate.sum()) - 1) < 1e-4)
    c = dict(CONFIGS["FULL-SHUF"]); ms = HybridV2(d, T, C, c.pop("branches"), **c); ms.eval()
    torch.manual_seed(1); y1 = ms(xf, xs); torch.manual_seed(2); y2 = ms(xf, xs)
    check("FULL-SHUF: the minute order is really shuffled", float((y1 - y2).abs().max()) > 0)
    c = dict(CONFIGS["H21-FULL"]); mh = HybridV2(d, T, C, c.pop("branches"), **c); mh.train()
    xfa = torch.cat([xf, torch.randn(B, 1)], dim=1)                  # + tree-expert logit column
    yh = mh(xfa, xs)
    check("v2.1: output shape with tree column", yh.shape == (B,))
    check("v2.1: branch dropout keeps a valid gate (rows sum to 1, no NaN)",
          bool(torch.isfinite(mh._g).all()) and float((mh._g.sum(1) - 1).abs().max()) < 1e-4)
    bl = float(mh.balance_loss())
    check("v2.1: balance loss >= 0", bl >= -1e-6, f"({bl:.4f})")
    mh._g = torch.full((B, 6), 1 / 6)
    check("v2.1: balance loss = 0 for uniform use", abs(float(mh.balance_loss())) < 1e-5)
    mh.eval(); t1 = mh(xfa, xs); xfb = xfa.clone(); xfb[:, -1] += 3.0
    check("v2.1: output depends on the tree-expert column", float((mh(xfb, xs) - t1).abs().max()) > 0)
    mp = HybridV2(d, T, C, "DQWSA", mask_last=True); mp.eval(); xs2 = xs.clone(); xs2[:, -1] += 5.0
    check("FULL-PAST: the current minute is really hidden", float((mp(xf, xs2) - mp(xf, xs)).abs().max()) < 1e-6)
    qi, qd = QuantumBranch(d, 32, "inspired"), QuantumBranch(d, 32, "dense4")
    n_i = sum(p.numel() for p in qi.parameters()); n_d = sum(p.numel() for p in qd.parameters())
    check("quantum control: dense4 parameter-matched to inspired (within 15%)", abs(n_i - n_d) / n_i < 0.15,
          f"({n_i} vs {n_d})")
    try:
        import pennylane  # noqa: F401
        qv = QuantumBranch(d, 32, "vqc")
        check("VQC: output shape", qv(xf, xs).shape == (B, 32))
    except ImportError:
        print("  [SKIP] VQC (pennylane not installed; only needed for FULL-VQC)")
    print("SELFTEST " + ("OK" if ok_all else "FAILED"))
    return ok_all


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--cache18", default="D:/revised model/cross_out4/ids2018_sample_v4.npz")
    ap.add_argument("--out_dir", default="hybrid_out")
    ap.add_argument("--mode", choices=["known", "loo", "both"], default="both")
    ap.add_argument("--configs", default="FLOW-MLP,SEQ-GRU,FULL,FULL-SHUF")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--max_train", type=int, default=30000)
    ap.add_argument("--val_max", type=int, default=10000)
    ap.add_argument("--epochs", type=int, default=6)
    ap.add_argument("--patience", type=int, default=2)
    ap.add_argument("--bs", type=int, default=512)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--tree_train", type=int, default=100000, help="v2.1 tree expert: 2017 rows (disjoint from NN rows)")
    ap.add_argument("--lb", type=float, default=0.1, help="v2.1 weight of the gate load-balancing loss")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="tiny synthetic run of the whole pipeline (1-3 minutes)")
    a = ap.parse_args()
    warnings.filterwarnings("ignore")
    if a.selftest:
        raise SystemExit(0 if selftest() else 1)
    dev = torch.device("cuda" if a.device == "auto" and torch.cuda.is_available() else
                       ("cpu" if a.device == "auto" else a.device))
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    os.makedirs(a.out_dir, exist_ok=True)
    if a.smoke:
        a.seeds, a.max_train, a.epochs = 1, 3000, 2
        a.configs = "FLOW-MLP,FULL,FULL-PAST,TREE,H21-FLOW,H21-FULL,H21-SHUF"
        D = make_smoke()
    else:
        D = load_real(a)
    print(f"device {dev} | 2017 train {len(D['ytr'])} | 2018 sample {len(D['lab18'])} | sequences {D['Str'].shape[1:]}")
    df = run(D, a, dev, a.out_dir)
    report(df, a.out_dir)
    print(f"\nsaved -> {a.out_dir}")


if __name__ == "__main__":
    main()
