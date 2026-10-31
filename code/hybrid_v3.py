"""
Hybrid IDS v3 (PyTorch) - redesigned after the diagnosis (diagnose_shift.py): the loss across networks comes from the
NETWORK CHANGE (benign 2017 vs 2018 separable with AUC .999), not from model capacity (inside 2018 trees reach .93-.97).
v3 keeps the thesis title and its four components but puts each one where it can matter:

  T  tree expert (HistGB logit, disjoint 2017 subset)                      - the proposal's XGBoost ensemble
  D  flow MLP                                                               - classical flow path
  P  TEMPORAL PATH, fully neuromorphic (spiking) over the 16-minute service-load sequence:
       causal stationary WAVELET filter bank (learnable db2, a-trous)  ->  LIF spiking neurons (input currents per
       minute)  ->  spiking self-ATTENTION over the minutes (binary Q/K/V, causal, no softmax, Spikformer-style)  ->
       spike rates.  Every layer after the wavelet receives spikes -> accumulate-only on neuromorphic hardware.
       CONTROL "dense twin": identical structure with real-valued leaky units instead of spikes (energy + accuracy).
  Q  QUANTUM one-class model of the LOCAL network's normal traffic (qkernel.py: IQP / ZZ-feature-map fidelity kernel,
     8 qubits, one-class SVM fitted on a few thousand local benign flows; never sees an attack). It enters the gate as
     the novelty PERCENTILE among held-out local benign flows (same scale in every network).
     CONTROLS: same pipeline with an RBF kernel, a random-feature kernel of the same dimension, Isolation Forest.
  Gate: softmax gate per flow with load balancing + branch dropout (as v2.1).
  ALIGN: the embedding of SOURCE benign flows is pulled towards the embedding of TARGET benign flows (multi-kernel MMD,
     target benign = the 'fit' third of the target's benign flows, the same assumption as the local threshold B).

Protocols
  cross   train CIC-IDS2017 -> test a target cache (CSE-CIC-IDS2018 = development; CIC-UNSW-NB15 = confirmatory,
          settings frozen before it is run). Scenarios: known / loo (target types' 2017 counterpart held out).
  within  CIC-IDS2017 only, time-ordered split (train past, test future), each attack type held out in turn.
Threshold: 99th / 99.9th percentile of the target's calibration benign third; real FPR on the separate test third.
Types with < 50 flows in the target sample are flagged 'tiny' and every mean is also reported without them.

Configs
  TREE        T                                   baseline
  V3-SUP      T D P(spiking) + align              supervised part only (no quantum)
  V3-FULL     T D P(spiking) Q(iqp) + align       THE v3 MODEL
  V3-NOALIGN  V3-FULL without alignment            V3-DENSE   P = dense twin (neuromorphic control)
  V3-QRBF / V3-QRFF / V3-QIF   Q from RBF kernel / random-feature kernel / Isolation Forest (quantum controls)
  V3-NOW / V3-NOA / V3-SHUF    no wavelet / no attention / minutes shuffled (time-order control)
  Q-IQP / Q-RBF / Q-RFF / Q-IF novelty score alone                   V3-MAX  max(percentile V3-SUP, percentile Q-IQP)
PRE-REGISTERED (every run writes prereg_v3.txt with this text and the SHA-256 of hybrid_v3.py + qkernel.py):
  primary   cross loo: V3-FULL mean recall@1%FPR > TREE (paired one-sided Wilcoxon over seed x type, p < 0.05),
            reported against 0.399 and on the non-tiny types
  quantum   V3-FULL > V3-QRBF, V3-QRFF, V3-QIF and Q-IQP > Q-RBF, Q-RFF, Q-IF (same test)
  others    V3-FULL > V3-NOALIGN (alignment), > V3-NOW (wavelet), > V3-NOA (attention), > V3-SHUF (time order)
  neuro     energy estimate of P: V3-FULL <= 0.5 x V3-DENSE and recall drop <= 0.02
Development on 2017/2018 may still change settings; CIC-UNSW-NB15 is run ONCE with the frozen file.
v3.1 revision (after 2018 run 1, before any v3.1 run): run 1 gave V3-FULL > TREE in 'known' (+0.049, p = .0016) but
not in 'loo'; Q inside the gate cost -0.03 (V3-FULL vs V3-SUP) and the IQP kernel equalled the RBF kernel. Final
candidate = V3-SUP (supervised hybrid) + the quantum one-class model by LATE FUSION (V3-MAX). Confirmatory tests on
UNSW: V3-MAX > TREE and V3-SUP > TREE (known, loo); V3-SUP vs V3-SUP-NOALIGN / -NOW / -NOA / -SHUF (components);
V3-SUP-DENSE twin for the neuromorphic claim; V3-MAX vs V3-MAX-RBF for the quantum claim.
v3.2 revision (after the v3.1 runs, before any v3.2 run): V3-MAX shared the 1% false alarms equally and cost -0.05
in 'known'; IQP = RBF in all four tests. Two pre-registered quantum roles:
  (a) complementary channel V3-MAX2: 0.8% of the false alarms to V3-SUP, 0.2% to the quantum one-class model.
      Success: V3-MAX2 > V3-SUP in loo (one-sided Wilcoxon) and V3-MAX2 >= V3-SUP - 0.02 in known; vs V3-MAX2-RBF
      reported (no quantum-specific advantage is expected or claimed).
  (b) quantum-inspired efficiency V3-SUP-TT: tensor-train (MPO) layers for the flow MLP and the attention projections.
      Success: recall >= V3-SUP - 0.02 (non-inferiority) with fewer parameters, and V3-SUP-TT > V3-SUP-LR
      (parameter-matched low-rank classical control).
v3.3 (after the 10-seed run, before any v3.3 run): results vary strongly with the 2017 subsample (sd ~.12 over seeds,
shared by all models). V3-SUP-ENS5 = mean score of 5 V3-SUP models trained on different 2017 subsamples; control
TREE-ENS5. Success: V3-SUP-ENS5 > V3-SUP and > TREE-ENS5 (paired, seed x type AND per-seed), smaller sd over seeds.
Every paired test is also reported per seed (one value per seed), the conservative version.

  python qkernel.py --selftest
  python hybrid_v3.py --selftest
  python hybrid_v3.py --smoke
  python hybrid_v3.py --protocol cross --target ids2018 --target_cache "D:/revised model/cross_out4/ids2018_sample_v4.npz" --out_dir "D:/revised model/v3_out" --configs TREE,V3-SUP,V3-FULL --seeds 3
"""
import argparse, json, os, time, warnings
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score
import hybrid_v2 as H
from qkernel import LocalNovelty, novelty_features

E_MAC_PJ, E_AC_PJ = 4.6, 0.9                     # 45 nm, Horowitz ISSCC 2014 (32-bit float MAC / add)
TINY = 50
CP = {"ids2018": {k: ((v,) if v else None) for k, v in H.COUNTERPART.items()},
      "unsw": {"Reconnaissance": ("PortScan",),
               "DoS": ("DoS Hulk", "DoS GoldenEye", "DoS slowloris", "DoS Slowhttptest", "DDoS"),
               "Exploits": None, "Fuzzers": None, "Generic": None, "Shellcode": None, "Backdoor": None,
               "Analysis": None, "Worms": None}}
WITHIN_FAMS = ["DDoS", "PortScan", "DoS Hulk", "DoS GoldenEye", "DoS slowloris", "DoS Slowhttptest", "FTP-Patator",
               "SSH-Patator", "Bot", "Web Attack - Brute Force"]

CONFIGS = {
    "TREE":       dict(branches="T", qkind=None, align=0.0),
    "V3-SUP":     dict(branches="TDP", qkind=None, align=1.0),
    "V3-FULL":    dict(branches="TDPQ", qkind="iqp", align=1.0),
    "V3-NOALIGN": dict(branches="TDPQ", qkind="iqp", align=0.0),
    "V3-DENSE":   dict(branches="TDPQ", qkind="iqp", align=1.0, spiking=False),
    "V3-QRBF":    dict(branches="TDPQ", qkind="rbf", align=1.0),
    "V3-QRFF":    dict(branches="TDPQ", qkind="rff", align=1.0),
    "V3-QIF":     dict(branches="TDPQ", qkind="iforest", align=1.0),
    "V3-NOW":     dict(branches="TDPQ", qkind="iqp", align=1.0, wavelet=False),
    "V3-NOA":     dict(branches="TDPQ", qkind="iqp", align=1.0, attn=False),
    "V3-SHUF":    dict(branches="TDPQ", qkind="iqp", align=1.0, shuffle=True),
    "Q-IQP": dict(novelty_only="iqp"), "Q-RBF": dict(novelty_only="rbf"), "Q-RFF": dict(novelty_only="rff"),
    "Q-IF": dict(novelty_only="iforest"),
    "V3-MAX": dict(max_of=("V3-SUP", "iqp")),
    # ---- v3.1 development revision (after 2018 run 1; registered before any v3.1 run): ablations on V3-SUP, the
    #      quantum one-class model used by late fusion (V3-MAX) instead of the gate (in the gate it cost -0.03)
    "V3-SUP-NOALIGN": dict(branches="TDP", qkind=None, align=0.0),
    "V3-SUP-DENSE":   dict(branches="TDP", qkind=None, align=1.0, spiking=False),
    "V3-SUP-NOW":     dict(branches="TDP", qkind=None, align=1.0, wavelet=False),
    "V3-SUP-NOA":     dict(branches="TDP", qkind=None, align=1.0, attn=False),
    "V3-SUP-SHUF":    dict(branches="TDP", qkind=None, align=1.0, shuffle=True),
    "V3-MAX-RBF":     dict(max_of=("V3-SUP", "rbf")),
    # ---- v3.2 (registered before any v3.2 run): quantum channel with a SMALL false-alarm share (0.2% of the 1%),
    #      and quantum-inspired tensor-train layers (efficiency) with a parameter-matched low-rank classical control
    "V3-MAX2":     dict(max_of=("V3-SUP", "iqp"), budget=(0.008, 0.002)),
    "V3-MAX2-RBF": dict(max_of=("V3-SUP", "rbf"), budget=(0.008, 0.002)),
    "V3-SUP-TT":   dict(branches="TDP", qkind=None, align=1.0, compact="tt", rank=4),
    "V3-SUP-LR":   dict(branches="TDP", qkind=None, align=1.0, compact="lr", rank=4),
    # ---- v3.3 (after the 10-seed run, before any v3.3 run): the result depends strongly on WHICH 2017 flows are
    #      sampled (sd ~0.12 over seeds, shared by all models) -> subsample ensembles, k members on different subsamples
    "V3-SUP-ENS5": dict(ens_of="V3-SUP", ens=5),
    "TREE-ENS5":   dict(ens_of="TREE", ens=5),
}


# ============================================================================ temporal path
class LIF(nn.Module):
    """leaky integrate-and-fire over the time axis; spiking=False -> 'dense twin' (same leak, real-valued output)"""
    def __init__(self, d, spiking=True, beta=0.9, slope=5.0):
        super().__init__()
        self.spiking, self.slope = spiking, slope
        self.beta_raw = nn.Parameter(torch.full((d,), float(np.log(beta / (1 - beta)))))
        # threshold 0.5 at start (softplus + 0.05): with 1.0 the smoke run fired only ~1.4% -> an almost silent path
        self.thr_raw = nn.Parameter(torch.full((d,), float(np.log(np.exp(0.45) - 1))))

    def forward(self, cur):                                         # (B,T,d) -> (B,T,d)
        beta, thr = torch.sigmoid(self.beta_raw), F.softplus(self.thr_raw) + 0.05
        v = torch.zeros_like(cur[:, 0])
        out = []
        for t in range(cur.shape[1]):
            v = beta * v + cur[:, t]
            s = H.SpikeFn.apply(v - thr, self.slope) if self.spiking else F.relu(v - thr)
            v = v - s * thr if self.spiking else v - s
            out.append(s)
        return torch.stack(out, dim=1)


class CausalWavelet(nn.Module):
    """stationary (a-trous) wavelet filter bank along time, CAUSAL (output at minute t uses minutes <= t only),
    learnable db2 low-pass, quadrature-mirror high-pass: (B,T,C) -> (B,T,C*(levels+1)) multi-scale currents"""
    def __init__(self, levels=3, k=4):
        super().__init__()
        self.levels, self.k = levels, k
        self.h = nn.Parameter(torch.tensor([0.48296291, 0.83651630, 0.22414387, -0.12940952]))
        self.register_buffer("sign", torch.tensor([(-1.0) ** n for n in range(k)]))

    def forward(self, xs):
        B, T, C = xs.shape
        a = xs.permute(0, 2, 1).reshape(B * C, 1, T)
        h = self.h.view(1, 1, -1)
        g = (self.h.flip(0) * self.sign).view(1, 1, -1)
        out = []
        for j in range(self.levels):
            dil = 2 ** j
            ap = F.pad(a, ((self.k - 1) * dil, 0))
            out.append(F.conv1d(ap, g, dilation=dil) / np.sqrt(2.0))
            a = F.conv1d(ap, h, dilation=dil) / np.sqrt(2.0)
        out.append(a)
        y = torch.cat(out, dim=1)                                   # (B*C, levels+1, T)
        return y.reshape(B, C * (self.levels + 1), T).permute(0, 2, 1)

    def regularizer(self):
        h = self.h
        r = (h.pow(2).sum() - 1.0) ** 2 + (h.sum() - float(np.sqrt(2.0))) ** 2
        for m in range(2, self.k, 2):
            r = r + (h[:-m] * h[m:]).sum() ** 2
        return r


def _three_factors(n):
    f = int(np.ceil(n ** (1 / 3)))
    return (f, f, int(np.ceil(n / (f * f))))


class TTLinear(nn.Module):
    """QUANTUM-INSPIRED tensor-train (matrix-product-operator) linear layer: the weight matrix is stored as a chain of
    three small cores, the representation used for many-body quantum states (MPS/MPO). Parameters ~ r^2 instead of
    in x out; computed by contracting the cores (no full matrix is built)."""
    def __init__(self, n_in, n_out, rank=4, bias=True):
        super().__init__()
        self.n_in, self.n_out, self.r = n_in, n_out, rank
        self.m, self.n = _three_factors(n_in), _three_factors(n_out)
        m, n, r = self.m, self.n, rank
        std = (1.0 / (n_in * r * r)) ** (1 / 6)
        self.G1 = nn.Parameter(torch.randn(m[0], n[0], r) * std)
        self.G2 = nn.Parameter(torch.randn(r, m[1], n[1], r) * std)
        self.G3 = nn.Parameter(torch.randn(r, m[2], n[2]) * std)
        self.bias = nn.Parameter(torch.zeros(n_out)) if bias else None
        self.macs = (m[0] * m[1] * m[2] * n[0] * r + m[1] * m[2] * n[0] * r * n[1] * r + m[2] * n[0] * n[1] * r * n[2])

    def forward(self, x):
        sh = x.shape[:-1]
        x = x.reshape(-1, self.n_in)
        pad = self.m[0] * self.m[1] * self.m[2] - self.n_in
        if pad:
            x = F.pad(x, (0, pad))
        x = x.reshape(-1, *self.m)
        t = torch.einsum("bijk,iax->bjkax", x, self.G1)
        t = torch.einsum("bjkax,xjcy->bkacy", t, self.G2)
        y = torch.einsum("bkacy,ykd->bacd", t, self.G3).reshape(x.shape[0], -1)[:, : self.n_out]
        if self.bias is not None:
            y = y + self.bias
        return y.reshape(*sh, self.n_out)


class LowRankLinear(nn.Module):
    """CLASSICAL control for TTLinear: W = U V with the rank chosen so that the parameter count matches"""
    def __init__(self, n_in, n_out, n_params, bias=True):
        super().__init__()
        k = max(1, int(round(n_params / (n_in + n_out))))
        self.u, self.v = nn.Linear(n_in, k, bias=False), nn.Linear(k, n_out, bias=bias)
        self.macs = n_in * k + k * n_out

    def forward(self, x):
        return self.v(self.u(x))


def make_linear(n_in, n_out, compact=None, rank=4, bias=True):
    if compact == "tt":
        return TTLinear(n_in, n_out, rank, bias)
    if compact == "lr":
        tt = TTLinear(n_in, n_out, rank, bias)
        return LowRankLinear(n_in, n_out, sum(p.numel() for p in tt.parameters()) - (n_out if bias else 0), bias)
    return nn.Linear(n_in, n_out, bias=bias)


class CompactFlowMLP(nn.Module):
    def __init__(self, d, hid, compact=None, rank=4):
        super().__init__()
        self.net = nn.Sequential(make_linear(d, 64, compact, rank), nn.GELU(), nn.LayerNorm(64),
                                 make_linear(64, hid, compact, rank), nn.GELU(), nn.LayerNorm(hid))

    def forward(self, xf, xs):
        return self.net(xf)


class TemporalPath(nn.Module):
    def __init__(self, T, C, hid, d=32, spiking=True, wavelet=True, attn=True, levels=3, compact=None, rank=4):
        super().__init__()
        self.T, self.d, self.spiking, self.attn, self.levels = T, d, spiking, attn, levels
        self.wav = CausalWavelet(levels) if wavelet else None
        cin = C * (levels + 1) if wavelet else C
        self.cin = cin
        self.norm = nn.LayerNorm(cin)
        self.inp = nn.Linear(cin, d)
        self.lif1 = LIF(d, spiking)
        if attn:
            self.q, self.k, self.v = (make_linear(d, d, compact, rank, bias=False) for _ in range(3))
            self.lq, self.lk, self.lv, self.ly, self.lo = (LIF(d, spiking) for _ in range(5))
            self.o = make_linear(d, d, compact, rank)
            self.register_buffer("mask", torch.tril(torch.ones(T, T)))
        self.read = nn.Sequential(nn.Linear(2 * d, hid), nn.GELU(), nn.LayerNorm(hid))
        self.count, self.ops, self.last_rate = False, None, None

    def forward(self, xf, xs):
        x = self.wav(xs) if self.wav is not None else xs
        s = self.lif1(self.inp(self.norm(x)))
        B, T, d = s.shape
        if self.attn:
            q, k, v = self.lq(self.q(s)), self.lk(self.k(s)), self.lv(self.v(s))
            att = (q @ k.transpose(1, 2)) * self.mask * 0.125
            ys = self.ly(att @ v)
            f = self.lo(self.o(ys))
        else:
            f = s
        if self.count:                                               # operation counts per flow (energy estimate)
            nz = lambda t: float((t != 0).float().sum()) / B
            mac = (self.wav is not None) * float(x.shape[2] // (self.levels + 1) * T * self.levels * 2 * 4)
            mac += T * self.cin * d                                    # input currents (real-valued input)
            ac = T * d                                                 # membrane updates lif1
            if self.attn:
                if self.spiking:
                    ac += 3 * nz(s) * d + nz(q) * T + nz(v) * T + nz(ys) * d
                else:
                    mac += 3 * T * d * d + 2 * T * T * d + T * d * d
                ac += 5 * T * d                                        # membrane updates of the 5 other LIF layers
            mac += 2 * d * self.read[0].out_features
            self.ops = dict(mac=mac, ac=ac, rate=float((f != 0).float().mean()) if self.spiking else float("nan"))
        self.last_rate = f.detach().mean()
        return self.read(torch.cat([f.mean(1), f[:, -4:].mean(1)], dim=-1))

    def regularizer(self):
        return self.wav.regularizer() if self.wav is not None else torch.zeros(())


class HybridV3(nn.Module):
    """xf = [d flow features | tree logit | novelty feature], xs = (B,T,C) sequence"""
    def __init__(self, d, T, C, branches="TDPQ", spiking=True, wavelet=True, attn=True, shuffle=False, hid=32,
                 bdrop=0.2, dropout=0.1, compact=None, rank=4):
        super().__init__()
        mk = {"T": lambda: H.TreeBranch(hid), "Q": lambda: H.TreeBranch(hid),
              "D": lambda: CompactFlowMLP(d, hid, compact, rank),
              "P": lambda: TemporalPath(T, C, hid, spiking=spiking, wavelet=wavelet, attn=attn, compact=compact, rank=rank)}
        self.d, self.names, self.shuffle, self.bdrop = d, list(branches), shuffle, bdrop
        self.br = nn.ModuleList([mk[b]() for b in self.names])
        nb = len(self.br)
        self.gate = nn.Linear(nb * hid, nb) if nb > 1 else None
        self.head = nn.Sequential(nn.Linear(hid, hid), nn.GELU(), nn.Dropout(dropout), nn.Linear(hid, 1))
        self._g, self.last_gate = None, None

    def forward(self, xf, xs, return_z=False):
        if self.shuffle:
            idx = torch.argsort(torch.rand(xs.shape[0], xs.shape[1], device=xs.device), dim=1)
            xs = torch.gather(xs, 1, idx.unsqueeze(-1).expand_as(xs))
        xflow, xt, xq = xf[:, : self.d], xf[:, self.d: self.d + 1], xf[:, self.d + 1: self.d + 2]
        inp = {"T": xt, "Q": xq, "D": xflow, "P": xflow}
        Hs = torch.stack([b(inp[n], xs) for n, b in zip(self.names, self.br)], dim=1)
        if self.gate is None:
            z = Hs[:, 0]
        else:
            logits = self.gate(Hs.flatten(1))
            if self.training and self.bdrop > 0:
                keep = torch.rand_like(logits) > self.bdrop
                none = ~keep.any(dim=1)
                if none.any():
                    rows = none.nonzero(as_tuple=True)[0]
                    keep[rows, torch.randint(0, keep.shape[1], (len(rows),), device=keep.device)] = True
                logits = logits.masked_fill(~keep, -1e9)
            g = torch.softmax(logits, dim=-1)
            self._g, self.last_gate = g, g.detach().mean(0)
            z = (g.unsqueeze(-1) * Hs).sum(1)
        out = self.head(z).squeeze(-1)
        return (out, z) if return_z else out

    def balance_loss(self):
        if self._g is None:
            return torch.zeros(())
        gm = self._g.mean(0)
        return (gm * torch.log(gm * gm.numel() + 1e-9)).sum()

    def regularizer(self):
        return sum((b.regularizer() for b in self.br if isinstance(b, TemporalPath)), torch.zeros(()))

    def temporal(self):
        return next((b for b in self.br if isinstance(b, TemporalPath)), None)


def mmd(x, y):
    """multi-kernel RBF MMD^2 (biased), bandwidths around the median distance"""
    xy = torch.cat([x, y], dim=0)
    d2 = torch.cdist(xy, xy).pow(2)
    med = d2.detach().median().clamp_min(1e-6)
    K = sum(torch.exp(-d2 / (med * s)) for s in (0.5, 1.0, 2.0))
    n = len(x)
    return K[:n, :n].mean() + K[n:, n:].mean() - 2 * K[:n, n:].mean()


# ============================================================================ training / scoring
def fit(cfg, Xf, Xs, y, Vf, Vs, vy, Af, As, seed, a, dev, d):
    torch.manual_seed(seed); np.random.seed(seed)
    c = CONFIGS[cfg]
    model = HybridV3(d, Xs.shape[1], Xs.shape[2], branches=c["branches"], spiking=c.get("spiking", True),
                     wavelet=c.get("wavelet", True), attn=c.get("attn", True), shuffle=c.get("shuffle", False),
                     compact=c.get("compact"), rank=c.get("rank", 4)).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    pos = max(int(y.sum()), 1)
    lossf = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(min((len(y) - pos) / pos, 20.0), device=dev))
    tf, ts, ty = (torch.tensor(v) for v in (Xf, Xs, y.astype("float32")))
    vf, vs, vt = (torch.tensor(v, device=dev) for v in (Vf, Vs, vy.astype("float32")))
    use_align = c["align"] > 0 and Af is not None and len(c["branches"]) > 1
    if use_align:
        af, as_ = torch.tensor(Af), torch.tensor(As)
    g = torch.Generator().manual_seed(seed)
    best, best_state, bad = np.inf, None, 0
    for ep in range(a.epochs):
        model.train()
        perm = torch.randperm(len(ty), generator=g)
        for k in range(0, len(perm), a.bs):
            b = perm[k:k + a.bs]
            out, z = model(tf[b].to(dev), ts[b].to(dev), return_z=True)
            yb = ty[b].to(dev)
            loss = lossf(out, yb) + 0.1 * model.regularizer().to(dev) + a.lb * model.balance_loss().to(dev)
            if use_align:
                zb = z[yb == 0][:256]
                if len(zb) >= 16:
                    tb = torch.randint(0, len(af), (len(zb),), generator=g)
                    _, zt = model(af[tb].to(dev), as_[tb].to(dev), return_z=True)
                    loss = loss + c["align"] * mmd(zb, zt)
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
        model.eval()
        with torch.no_grad(), torch.random.fork_rng(devices=[]):
            torch.manual_seed(12345)
            vl = float(np.mean([lossf(model(vf[k:k + 4096], vs[k:k + 4096]), vt[k:k + 4096]).item()
                                for k in range(0, len(vt), 4096)]))
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
def score(model, Xf, Xs, dev, bs=8192):
    torch.manual_seed(0)
    out, gs, n = [], 0.0, 0
    for k in range(0, len(Xf), bs):
        o = model(torch.tensor(Xf[k:k + bs], device=dev), torch.tensor(Xs[k:k + bs], device=dev))
        out.append(torch.sigmoid(o).cpu())
        if model.last_gate is not None:
            gs = gs + model.last_gate.cpu().numpy() * len(o)
        n += len(o)
    s = torch.cat(out).numpy() if out else np.zeros(0, "float32")
    return s, ((gs / max(n, 1)).round(3).tolist() if model.last_gate is not None and n else None)


@torch.no_grad()
def energy(model, Xf, Xs, dev):
    """estimated compute energy per flow (pJ): temporal path counted in detail, other layers as dense MACs"""
    tp = model.temporal()
    dense_mac = 0
    for n, b in zip(model.names, model.br):
        if n != "P":
            dense_mac += sum(m.in_features * m.out_features for m in b.modules() if isinstance(m, nn.Linear))
            dense_mac += sum(m.macs for m in b.modules() if isinstance(m, TTLinear))    # (low-rank: its two Linears)
    dense_mac += sum(m.in_features * m.out_features for m in model.head.modules() if isinstance(m, nn.Linear))
    if model.gate is not None:
        dense_mac += model.gate.in_features * model.gate.out_features
    row = dict(params=sum(p.numel() for p in model.parameters()),
               D_params=sum(p.numel() for n, b in zip(model.names, model.br) if n == "D" for p in b.parameters()),
               P_params=sum(p.numel() for n, b in zip(model.names, model.br) if n == "P" for p in b.parameters()),
               other_mac=dense_mac, P_mac=0.0, P_ac=0.0, P_rate=float("nan"))
    if tp is not None:
        tp.count = True
        model(torch.tensor(Xf, device=dev), torch.tensor(Xs, device=dev))
        tp.count = False
        row.update(P_mac=tp.ops["mac"], P_ac=tp.ops["ac"], P_rate=tp.ops["rate"])
    row["P_energy_nJ"] = (row["P_mac"] * E_MAC_PJ + row["P_ac"] * E_AC_PJ) / 1e3
    row["total_energy_nJ"] = row["P_energy_nJ"] + dense_mac * E_MAC_PJ / 1e3
    return row


# ============================================================================ data
def is_benign(lab):
    return pd.Series(np.asarray(lab).astype(str)).str.strip().str.lower().isin(["benign"]).values


def load_data(a):
    import joblib
    feats = json.load(open(os.path.join(a.s17_dir, "feature_names.json")))
    flow = [f for f in feats if not f.startswith(("win_", "pw_", "gl_"))]
    fidx = np.array([feats.index(c) for c in flow])
    z = np.load(os.path.join(a.s17_dir, "splits.npz"), allow_pickle=True)
    q = np.load(os.path.join(a.s17_dir, "seq17.npz"))
    D = {f"X{s}": z[f"X{s}"][:, fidx].astype("float32") for s in ("tr", "va", "te")}
    D.update({f"y{s}": z[f"y{s}"].astype(int) for s in ("tr", "va", "te")})
    D.update({f"a{s}": z[f"a{s}"].astype(str) for s in ("tr", "va", "te")})
    for s in ("tr", "va", "te"):
        key = f"S{s}"
        D[key] = H.prep_seq(q[key]) if key in q.files else None
        if D[key] is not None and len(D[key]) != len(D[f"y{s}"]):
            raise SystemExit(f"seq17.npz {key} does not match splits.npz")
    if a.protocol == "cross":
        qt = joblib.load(os.path.join(a.s17_dir, "quantile_transformer.joblib"))
        zc = np.load(a.target_cache, allow_pickle=True)
        Xraw = pd.DataFrame(zc["X"], columns=list(zc["cols"]))
        full = pd.DataFrame(0.0, index=Xraw.index, columns=feats)
        miss = [c for c in feats if c not in Xraw.columns]
        for c in feats:
            if c in Xraw.columns:
                full[c] = Xraw[c].values
        if miss:
            print(f"  target cache lacks {len(miss)} columns (set to 0): {miss[:8]}{' ...' if len(miss) > 8 else ''}")
        D["XT"] = qt.transform(full)[:, fidx].astype("float32")
        D["ST"] = H.prep_seq(zc["seq"])
        D["labT"] = zc["lab"].astype(str)
    return D


def make_smoke(protocol):
    S = H.make_smoke()
    D = dict(Xtr=S["Xtr"], Xva=S["Xva"], ytr=S["ytr"], yva=S["yva"], atr=S["atr"], ava=S["ava"], Str=S["Str"],
             Sva=S["Sva"], Xte=S["Xva"].copy(), yte=S["yva"].copy(), ate=S["ava"].copy(), Ste=S["Sva"].copy(),
             XT=S["X18"], ST=S["S18"], labT=S["lab18"])
    return D


# ============================================================================ experiment
def recall_at(s_cal, s_bte, s_pos):
    r = {}
    for fpr, tag in ((0.01, "1"), (0.001, "01")):
        thr = np.quantile(s_cal, 1 - fpr)
        r[f"recall{tag}"] = float((s_pos > thr).mean()) if len(s_pos) else np.nan
        r[f"fpr_test{tag}"] = float((s_bte > thr).mean())
    y = np.r_[np.zeros(len(s_bte)), np.ones(len(s_pos))]
    r["auc"] = float(roc_auc_score(y, np.r_[s_bte, s_pos])) if len(s_pos) else np.nan
    # partial AUC up to 1% FPR (McClish-standardised, 0.5 = chance): averages over all thresholds in [0, 1%] and is
    # much less sensitive than recall at ONE threshold, where flows of one attack tool cross it all-or-nothing
    r["pauc1"] = float(roc_auc_score(y, np.r_[s_bte, s_pos], max_fpr=0.01)) if len(s_pos) else np.nan
    return r


def pct_vs(ref, s):
    ref = np.sort(ref)
    return np.searchsorted(ref, s, side="right") / len(ref)


def qfeat(pct):
    return (-np.log1p(-np.clip(pct, 0, 0.999)) / 3).astype("float32")[:, None]


def build_target(D, a):
    """index sets of the target: evaluation rows, calibration benign, test benign, novelty fit / reference benign,
    alignment benign (cross only)"""
    rng = np.random.default_rng(0)
    if a.protocol == "cross":
        X, S, lab = D["XT"], D["ST"], D["labT"]
        ben = np.where(is_benign(lab))[0]
        rng.shuffle(ben)
        k3 = len(ben) // 3
        fitb, cal, bte = ben[:k3], ben[k3:2 * k3], ben[2 * k3:]       # identical thirds to hybrid_v2 / cross_dataset
        nfit, nref = fitb[: len(fitb) // 2], fitb[len(fitb) // 2:]
        cp = CP[a.target]
        return dict(X=X, S=S, lab=lab, calX=X[cal], calS=S[cal], bteX=X[bte], bteS=S[bte],
                    nfitX=X[nfit], nfitS=S[nfit], nrefX=X[nref], nrefS=S[nref], alX=X[fitb], alS=S[fitb], cp=cp,
                    cal_i=cal, bte_i=bte, al_i=fitb)
    if D.get("Ste") is None:
        raise SystemExit("within protocol needs Ste in seq17.npz (stage 1 with --seq)")
    vb = np.where(D["yva"] == 0)[0]
    rng.shuffle(vb)
    h = len(vb) // 2
    nfit, cal = vb[: h // 2], vb[h:]
    nref = vb[h // 2: h]
    tb = np.where(D["yte"] == 0)[0]
    return dict(X=D["Xte"], S=D["Ste"], lab=np.where(D["yte"] == 0, "Benign", D["ate"]), calX=D["Xva"][cal],
                calS=D["Sva"][cal], bteX=D["Xte"][tb], bteS=D["Ste"][tb], nfitX=D["Xva"][nfit], nfitS=D["Sva"][nfit],
                nrefX=D["Xva"][nref], nrefS=D["Sva"][nref], alX=None, alS=None, cp=None,
                cal_i=None, bte_i=tb, al_i=None)


def tasks(D, tg, a):
    lab = tg["lab"]
    types = [t for t in pd.Series(lab[~is_benign(lab)]).value_counts().index]
    out = []
    if a.mode in ("known", "both"):
        out.append(("known", None, types))
    if a.mode in ("loo", "both"):
        if a.protocol == "cross":
            helds = sorted({v for t, v in tg["cp"].items() if v and t in types}, key=str)
            for hset in helds:
                ev = [t for t in types if tg["cp"].get(t) == hset]
                if np.isin(D["atr"], hset).any():
                    out.append(("loo", hset, ev))
        else:
            for f in [x.strip() for x in a.within_fams.split(",") if x.strip()]:
                if f in types and np.isin(D["atr"], [f]).any():
                    out.append(("loo", (f,), [f]))
    return types, out


def run(D, a, dev, out_dir):
    tg = build_target(D, a)
    types, task_list = tasks(D, tg, a)
    cfgs = [c.strip() for c in a.configs.split(",") if c.strip()]
    bad = [c for c in cfgs if c not in CONFIGS]
    if bad:
        raise SystemExit(f"unknown configs {bad}; available {list(CONFIGS)}")
    mx = [c for c in cfgs if "max_of" in CONFIGS[c]]                 # late-fusion configs need their base first
    need = [CONFIGS[c]["max_of"][0] for c in mx]
    cfgs = [c for c in cfgs if c not in mx] + [b for b in dict.fromkeys(need) if b not in cfgs] + mx
    kinds = sorted({CONFIGS[c].get("qkind") or CONFIGS[c].get("novelty_only") for c in cfgs} - {None}
                   | {CONFIGS[c]["max_of"][1] for c in mx})
    lab = tg["lab"]
    n_type = pd.Series(lab).value_counts().to_dict()
    d = D["Xtr"].shape[1]
    rows, energy_rows, gates, t0 = [], [], [], time.time()
    csv = os.path.join(out_dir, "v3_results.csv")
    for seed in range(a.seeds):
        # ---- local novelty models (benign only; independent of the held-out family) ------------------------
        nov = {}
        for kind in kinds:
            tm = LocalNovelty(kind, n_qubits=a.qubits, m=a.q_m, nu=a.q_nu, seed=seed)
            tm.fit(novelty_features(tg["nfitX"], tg["nfitS"])).set_reference(novelty_features(tg["nrefX"], tg["nrefS"]))
            if a.protocol == "cross":                                 # source model: unused 2017 benign flows
                PX, PS, py = ((D["Xte"], D["Ste"], D["yte"]) if D.get("Ste") is not None
                              else (D["Xva"], D["Sva"], D["yva"]))
                pb = np.where(py == 0)[0]
                pick = np.random.default_rng(seed + 7).choice(pb, min(len(pb), 2 * a.q_m + 10000), replace=False)
                sm = LocalNovelty(kind, n_qubits=a.qubits, m=a.q_m, nu=a.q_nu, seed=seed)
                sm.fit(novelty_features(PX[pick[: 2 * a.q_m]], PS[pick[: 2 * a.q_m]]))
                sm.set_reference(novelty_features(PX[pick[2 * a.q_m:]], PS[pick[2 * a.q_m:]]))
            else:
                sm = tm
            allp = tm.percentile(novelty_features(tg["X"], tg["S"]))   # cal / test / align rows are subsets of X
            part = lambda key, xk, sk: (allp[tg[key]] if tg[key] is not None else
                                        (tm.percentile(novelty_features(tg[xk], tg[sk])) if tg[xk] is not None else None))
            nov[kind] = dict(src=sm, all=allp, cal=part("cal_i", "calX", "calS"), bte=part("bte_i", "bteX", "bteS"),
                             al=part("al_i", "alX", "alS"))
            print(f"  seed {seed}: novelty model '{kind}' ready (scale {getattr(tm, 'scale', float('nan')):.3g}) "
                  f"[{time.time() - t0:.0f}s]", flush=True)
        for ti, (scen, held, ev_types) in enumerate(task_list):
            mt = ~np.isin(D["atr"], held) if held else np.ones(len(D["atr"]), bool)
            mv = ~np.isin(D["ava"], held) if held else np.ones(len(D["ava"]), bool)
            pool_t, pool_v = np.where(mt)[0], np.where(mv)[0]
            i = pool_t[H.sub_idx(D["ytr"][pool_t], a.max_train, seed)]
            j = pool_v[H.sub_idx(D["yva"][pool_v], a.val_max, seed)]
            rest = np.setdiff1d(pool_t, i)
            k = rest[H.sub_idx(D["ytr"][rest], a.tree_train, seed + 100)]
            from sklearn.ensemble import HistGradientBoostingClassifier
            tree = HistGradientBoostingClassifier(max_iter=200, random_state=seed).fit(D["Xtr"][k], D["ytr"][k])
            def tlogit(M):
                p = np.clip(tree.predict_proba(M)[:, 1], 1e-6, 1 - 1e-6)
                return (np.clip(np.log(p / (1 - p)), -10, 10) / 5).astype("float32")[:, None]
            base = dict(tr=tlogit(D["Xtr"][i]), va=tlogit(D["Xva"][j]), all=tlogit(tg["X"]), cal=tlogit(tg["calX"]),
                        bte=tlogit(tg["bteX"]), al=tlogit(tg["alX"]) if tg["alX"] is not None else None)
            ev_idx = {t: np.where(lab == t)[0] for t in ev_types}
            cache = {}
            for cfg in cfgs:
                c = CONFIGS[cfg]
                if "novelty_only" in c:
                    nv = nov[c["novelty_only"]]
                    s_cal, s_bte, s_all = nv["cal"], nv["bte"], nv["all"]
                    g = None
                elif "max_of" in c:
                    sup = cache[c["max_of"][0]]
                    nv = nov[c["max_of"][1]]
                    if "budget" in c:                                 # each channel's own share of the false alarms
                        bs, bq = c["budget"]
                        f = lambda ps, pq: np.maximum((ps - (1 - bs)) / bs, (pq - (1 - bq)) / bq)
                        cq = nv["cal"]
                        s_cal = f(pct_vs(sup["cal"], sup["cal"]), pct_vs(cq, cq))
                        s_bte = f(pct_vs(sup["cal"], sup["bte"]), pct_vs(cq, nv["bte"]))
                        s_all = f(pct_vs(sup["cal"], sup["all"]), pct_vs(cq, nv["all"]))
                    else:
                        s_cal = np.maximum(pct_vs(sup["cal"], sup["cal"]), nv["cal"])
                        s_bte = np.maximum(pct_vs(sup["cal"], sup["bte"]), nv["bte"])
                        s_all = np.maximum(pct_vs(sup["cal"], sup["all"]), nv["all"])
                    g = None
                elif "ens" in c:
                    from sklearn.ensemble import HistGradientBoostingClassifier as HGB
                    acc = dict(cal=0.0, bte=0.0, all=0.0)
                    pool_e = np.setdiff1d(pool_t, k)                  # never the tree expert's own training rows
                    for e in range(c["ens"]):
                        se = seed * 1000 + e + 1
                        if c["ens_of"] == "TREE":
                            ke = rest[H.sub_idx(D["ytr"][rest], a.tree_train, se)]
                            te = HGB(max_iter=200, random_state=se).fit(D["Xtr"][ke], D["ytr"][ke])
                            pa, pb = te.predict_proba(tg["X"])[:, 1], te.predict_proba(tg["bteX"])[:, 1]
                            pc = pa[tg["cal_i"]] if tg["cal_i"] is not None else te.predict_proba(tg["calX"])[:, 1]
                        else:
                            ie = pool_e[H.sub_idx(D["ytr"][pool_e], a.max_train, se)]
                            z0 = lambda n: np.zeros((n, 1), "float32")
                            cat0 = lambda X, t: np.hstack([X, t, z0(len(X))]).astype("float32")
                            Ae = cat0(tg["alX"], base["al"]) if tg["alX"] is not None else None
                            me = fit(c["ens_of"], cat0(D["Xtr"][ie], tlogit(D["Xtr"][ie])), D["Str"][ie], D["ytr"][ie],
                                     cat0(D["Xva"][j], base["va"]), D["Sva"][j], D["yva"][j], Ae, tg["alS"], se, a, dev, d)
                            pa, _ = score(me, cat0(tg["X"], base["all"]), tg["S"], dev)
                            pb, _ = score(me, cat0(tg["bteX"], base["bte"]), tg["bteS"], dev)
                            pc = (pa[tg["cal_i"]] if tg["cal_i"] is not None
                                  else score(me, cat0(tg["calX"], base["cal"]), tg["calS"], dev)[0])
                        acc = dict(cal=acc["cal"] + pc, bte=acc["bte"] + pb, all=acc["all"] + pa)
                    s_cal, s_bte, s_all = (acc[x] / c["ens"] for x in ("cal", "bte", "all"))
                    g = None
                else:
                    qk = c.get("qkind")
                    zq = lambda n: np.zeros((n, 1), "float32")
                    if qk:
                        sm = nov[qk]["src"]
                        q_tr = qfeat(sm.percentile(novelty_features(D["Xtr"][i], D["Str"][i])))
                        q_va = qfeat(sm.percentile(novelty_features(D["Xva"][j], D["Sva"][j])))
                        q_all, q_cal, q_bte = (qfeat(nov[qk][s]) for s in ("all", "cal", "bte"))
                        q_al = qfeat(nov[qk]["al"]) if nov[qk]["al"] is not None else None
                    else:
                        q_tr, q_va = zq(len(i)), zq(len(j))
                        q_all, q_cal, q_bte = zq(len(tg["X"])), zq(len(tg["calX"])), zq(len(tg["bteX"]))
                        q_al = zq(len(tg["alX"])) if tg["alX"] is not None else None
                    cat = lambda X, t, q: np.hstack([X, t, q]).astype("float32")
                    Af = cat(tg["alX"], base["al"], q_al) if tg["alX"] is not None else None
                    m = fit(cfg, cat(D["Xtr"][i], base["tr"], q_tr), D["Str"][i], D["ytr"][i],
                            cat(D["Xva"][j], base["va"], q_va), D["Sva"][j], D["yva"][j],
                            Af, tg["alS"], seed, a, dev, d)
                    s_all, _ = score(m, cat(tg["X"], base["all"], q_all), tg["S"], dev)
                    s_bte, g = score(m, cat(tg["bteX"], base["bte"], q_bte), tg["bteS"], dev)
                    s_cal = (s_all[tg["cal_i"]] if tg["cal_i"] is not None
                             else score(m, cat(tg["calX"], base["cal"], q_cal), tg["calS"], dev)[0])
                    if ti == 0 and seed == 0 and m.temporal() is not None:
                        sub = np.arange(min(4096, len(tg["bteX"])))
                        e = energy(m, cat(tg["bteX"][sub], base["bte"][sub], q_bte[sub]), tg["bteS"][sub], dev)
                        energy_rows.append(dict(model=cfg, **e))
                    if g is not None:
                        gates.append(dict(scenario=scen, held=str(held), seed=seed, model=cfg,
                                          **{f"gate_{n}": v for n, v in zip(m.names, g)}))
                cache[cfg] = dict(cal=s_cal, bte=s_bte, all=s_all)
                for t in ev_types:
                    r = recall_at(s_cal, s_bte, s_all[ev_idx[t]])
                    rows.append(dict(protocol=a.protocol, scenario=scen, held="+".join(held) if held else "-",
                                     seed=seed, model=cfg, type=t, n=int(n_type.get(t, 0)),
                                     tiny=n_type.get(t, 0) < TINY, **r))
                print(f"  {scen:5s} {('+'.join(held) if held else 'all')[:30]:30s} seed={seed} {cfg:10s} "
                      f"mean recall@1% {np.nanmean([x['recall1'] for x in rows if x['model'] == cfg and x['seed'] == seed and x['scenario'] == scen and x['held'] == ('+'.join(held) if held else '-')]):.3f} "
                      f"[{time.time() - t0:.0f}s]", flush=True)
            pd.DataFrame(rows).to_csv(csv, index=False)
    df = pd.DataFrame(rows)
    pd.DataFrame(energy_rows).to_csv(os.path.join(out_dir, "v3_energy.csv"), index=False)
    pd.DataFrame(gates).to_csv(os.path.join(out_dir, "v3_gates.csv"), index=False)
    report(df, pd.DataFrame(energy_rows), out_dir)


def report(df, en, out_dir):
    from scipy.stats import wilcoxon
    L = []
    say = lambda s: (print(s), L.append(s))
    for scen in df.scenario.unique():
        s = df[df.scenario == scen]
        for subset, mask in (("all types", np.ones(len(s), bool)), ("non-tiny types", ~s.tiny.values)):
            per_seed = s[mask].groupby(["model", "seed"]).recall1.mean().reset_index()
            t = per_seed.groupby("model").recall1.agg(["mean", "std"]).round(3).sort_values("mean", ascending=False)
            say(f"\n==== [{scen}] mean recall@1%FPR (threshold B) over target types, {subset}; mean (sd) over seeds")
            say(t.to_string())
            fpr = s.groupby("model").fpr_test1.mean().round(4)
            if subset == "all types":
                say("real false-alarm rate on the test benign third (nominal 1%): " + ", ".join(f"{k} {v}" for k, v in fpr.items()))
                pa = s.groupby(["model", "seed"]).pauc1.mean().groupby("model").agg(["mean", "std"]).round(3)
                say("partial AUC up to 1% FPR (standardised, 0.5 = chance), mean (sd) over seeds:\n"
                    + pa.sort_values("mean", ascending=False).to_string())
        piv = s.groupby(["type", "model"]).recall1.mean().unstack().round(3)
        say(f"\n-- [{scen}] per type, recall@1%FPR")
        say(piv.to_string())
        pairs = [("V3-FULL", "TREE"), ("V3-FULL", "V3-QRBF"), ("V3-FULL", "V3-QRFF"), ("V3-FULL", "V3-QIF"),
                 ("Q-IQP", "Q-RBF"), ("Q-IQP", "Q-RFF"), ("Q-IQP", "Q-IF"), ("V3-FULL", "V3-NOALIGN"),
                 ("V3-FULL", "V3-NOW"), ("V3-FULL", "V3-NOA"), ("V3-FULL", "V3-SHUF"), ("V3-FULL", "V3-SUP"),
                 ("V3-FULL", "V3-DENSE"), ("V3-MAX", "TREE"),
                 ("V3-SUP", "TREE"), ("V3-SUP", "V3-SUP-NOALIGN"), ("V3-SUP", "V3-SUP-NOW"), ("V3-SUP", "V3-SUP-NOA"),
                 ("V3-SUP", "V3-SUP-SHUF"), ("V3-SUP", "V3-SUP-DENSE"), ("V3-MAX", "V3-SUP"),
                 ("V3-MAX", "V3-MAX-RBF"), ("V3-MAX2", "V3-SUP"), ("V3-MAX2", "TREE"), ("V3-MAX2", "V3-MAX2-RBF"),
                 ("V3-SUP-TT", "V3-SUP-LR"), ("V3-SUP-TT", "TREE"),
                 ("V3-SUP-ENS5", "V3-SUP"), ("V3-SUP-ENS5", "TREE-ENS5"), ("V3-SUP-ENS5", "TREE"), ("TREE-ENS5", "TREE")]
        if {"V3-SUP-TT", "V3-SUP"} <= set(s.model):
            dt = s[s.model == "V3-SUP-TT"].recall1.mean() - s[s.model == "V3-SUP"].recall1.mean()
            say(f"\n-- [{scen}] tensor-train non-inferiority: V3-SUP-TT - V3-SUP = {dt:+.3f} "
                f"(pre-registered: >= -0.02) -> {'MET' if dt >= -0.02 else 'not met'}")
        say(f"\n-- [{scen}] PRE-REGISTERED paired tests (one-sided Wilcoxon over seed x type)")
        for a_, b_ in pairs:
            if a_ in s.model.values and b_ in s.model.values:
                A = s[s.model == a_].set_index(["seed", "held", "type"]).recall1
                B = s[s.model == b_].set_index(["seed", "held", "type"]).recall1
                dlt = (A - B.reindex(A.index)).dropna()
                p = wilcoxon(dlt, alternative="greater").pvalue if (dlt != 0).sum() >= 3 else np.nan
                ds = dlt.groupby(level="seed").mean()              # conservative: one value per seed
                ps = wilcoxon(ds, alternative="greater").pvalue if (ds != 0).sum() >= 3 else np.nan
                say(f"  {a_:10s} vs {b_:10s} mean diff {dlt.mean():+.3f}  p = {p:.4f}  "
                    + ("SUPPORTED" if p < 0.05 and dlt.mean() > 0 else "not supported")
                    + f"   | per-seed: wins {int((ds > 0).sum())}/{len(ds)}, p = {ps:.4f}")
    if len(en):
        say("\n==== energy estimate per flow (45 nm: 4.6 pJ/MAC, 0.9 pJ/add; temporal path P in detail)")
        say(en.round(3).to_string(index=False))
        r = en.set_index("model")
        for sp, dn in (("V3-FULL", "V3-DENSE"), ("V3-SUP", "V3-SUP-DENSE")):
            if sp in r.index and dn in r.index:
                ratio = r.loc[sp, "P_energy_nJ"] / max(r.loc[dn, "P_energy_nJ"], 1e-12)
                tot = r.loc[sp, "total_energy_nJ"] / max(r.loc[dn, "total_energy_nJ"], 1e-12)
                say(f"neuromorphic claim {sp}: temporal-path energy spiking/dense = {ratio:.3f}, whole model "
                    f"{tot:.3f} (pre-registered <= 0.5, with recall drop <= 0.02 -> see the paired test vs {dn})")
    open(os.path.join(out_dir, "v3_report.txt"), "w", encoding="utf-8").write("\n".join(L))


# ============================================================================ checks
def selftest():
    ok = True
    def check(name, cond, info=""):
        nonlocal ok
        ok &= bool(cond)
        print(("PASS " if cond else "FAIL ") + name, info)
    torch.manual_seed(0)
    T, C, B = 16, 3, 8
    w = CausalWavelet()
    x = torch.randn(B, T, C)
    y1 = w(x)
    x2 = x.clone(); x2[:, 10:] += 5.0
    y2 = w(x2)
    check("wavelet: output shape (B,T,C*4)", tuple(y1.shape) == (B, T, C * 4))
    check("wavelet: CAUSAL (future change leaves minutes < 10 unchanged)", torch.allclose(y1[:, :10], y2[:, :10]))
    check("wavelet: regulariser ~ 0 at db2 init", float(w.regularizer()) < 1e-6)
    tp = TemporalPath(T, C, 32, spiking=True)
    tp.count = True
    out = tp(None, x)
    check("spiking path: embedding shape", tuple(out.shape) == (B, 32))
    s = tp.lif1(tp.inp(tp.norm(tp.wav(x))))
    check("LIF: outputs are binary spikes", bool(((s == 0) | (s == 1)).all()))
    e_s = tp.ops
    td = TemporalPath(T, C, 32, spiking=False)
    td.count = True
    td(None, x)
    e_d = td.ops
    check("ops counted", e_s["mac"] > 0 and e_s["ac"] > 0 and e_d["mac"] > e_s["mac"], f"(spiking mac {e_s['mac']:.0f} ac {e_s['ac']:.0f} | dense mac {e_d['mac']:.0f})")
    x3 = x.clone(); x3[:, -1] += 3.0
    a1, a2 = tp.lif1(tp.inp(tp.norm(tp.wav(x)))), tp.lif1(tp.inp(tp.norm(tp.wav(x3))))
    check("LIF: causal in time", torch.equal(a1[:, :-1], a2[:, :-1]))
    # gradient path wavelet -> LIF -> read-out (the attention block is tested separately: in a tiny random test it can
    # be silent at initialisation, which cuts its path; in the real runs it fires ~11% and its ablation changes results)
    tpa = TemporalPath(T, C, 32, spiking=True, attn=False)
    tpa(None, x).sum().backward()
    check("surrogate gradient reaches the wavelet filter", tpa.wav.h.grad is not None and float(tpa.wav.h.grad.abs().sum()) > 0)
    torch.manual_seed(1)
    tpb = TemporalPath(T, C, 32, spiking=True)
    xb = 3.0 * torch.randn(B, T, C)
    tpb(None, xb).sum().backward()
    qrate = float(tpb.lq(tpb.q(tpb.lif1(tpb.inp(tpb.norm(tpb.wav(xb)))))).mean())
    check("attention projections receive gradient when the block fires", float(tpb.q.weight.grad.abs().sum()) > 0 or qrate == 0,
          f"(query spike rate {qrate:.3f})")
    tt = TTLinear(69, 64, rank=4)
    W = torch.einsum("iax,xjcy,ykd->ijkacd", tt.G1, tt.G2, tt.G3).reshape(75, 64)[:69]
    xx = torch.randn(5, 69)
    check("tensor-train layer = contraction of its cores", torch.allclose(tt(xx), xx @ W + tt.bias, atol=1e-5))
    n_tt = sum(p.numel() for p in tt.parameters())
    lr = make_linear(69, 64, "lr", 4)
    n_lr = sum(p.numel() for p in lr.parameters())
    check("tensor-train has far fewer parameters; low-rank control matched",
          n_tt < 0.2 * (69 * 64 + 64) and abs(n_lr - n_tt) < 0.25 * n_tt, f"(dense {69 * 64 + 64}, TT {n_tt}, low-rank {n_lr})")
    mtt = HybridV3(10, T, C, branches="TDP", compact="tt")
    o2 = mtt(torch.randn(B, 12), x)
    check("hybrid with tensor-train layers runs", tuple(o2.shape) == (B,))
    zx, zy = torch.randn(64, 8), torch.randn(64, 8)
    check("MMD ~ 0 for same distribution, > for shifted", float(mmd(zx, zy)) < float(mmd(zx, zy + 2.0)),
          f"({float(mmd(zx, zy)):.4f} vs {float(mmd(zx, zy + 2.0)):.4f})")
    m = HybridV3(10, T, C, branches="TDPQ")
    xf = torch.randn(B, 12)
    o, z = m(xf, x, return_z=True)
    check("hybrid: logits and embedding", tuple(o.shape) == (B,) and tuple(z.shape) == (B, 32))
    check("hybrid: gate sums to 1", abs(float(m.last_gate.sum()) - 1) < 1e-5)
    # tiny learning test: attack = rising load in the last minutes
    g = torch.Generator().manual_seed(0)
    n = 512
    X = torch.randn(n, 12, generator=g); S = 0.3 * torch.randn(n, T, C, generator=g)
    yy = (torch.rand(n, generator=g) < 0.3).float()
    S[yy == 1, -4:, 0] += 1.5
    m = HybridV3(10, T, C, branches="DP")
    opt = torch.optim.Adam(m.parameters(), 3e-3)
    l0 = None
    for it in range(150):
        loss = F.binary_cross_entropy_with_logits(m(X, S), yy)
        l0 = float(loss) if l0 is None else l0
        opt.zero_grad(); loss.backward(); opt.step()
    check("hybrid learns a temporal pattern (loss falls)", float(loss) < 0.75 * l0, f"({l0:.3f} -> {float(loss):.3f})")
    print("ALL PASS" if ok else "SOME CHECKS FAILED")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", choices=["cross", "within"], default="cross")
    ap.add_argument("--target", choices=list(CP), default="ids2018")
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--target_cache", default="D:/revised model/cross_out4/ids2018_sample_v4.npz")
    ap.add_argument("--out_dir", default="v3_out")
    ap.add_argument("--mode", choices=["known", "loo", "both"], default="both")
    ap.add_argument("--configs", default="TREE,V3-SUP,V3-FULL,Q-IQP,Q-RBF")
    ap.add_argument("--within_fams", default=",".join(WITHIN_FAMS))
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--max_train", type=int, default=30000)
    ap.add_argument("--val_max", type=int, default=10000)
    ap.add_argument("--tree_train", type=int, default=100000)
    ap.add_argument("--epochs", type=int, default=6)
    ap.add_argument("--patience", type=int, default=2)
    ap.add_argument("--bs", type=int, default=512)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--lb", type=float, default=0.1)
    ap.add_argument("--qubits", type=int, default=8)
    ap.add_argument("--q_m", type=int, default=2000, help="local benign flows the one-class model is fitted on")
    ap.add_argument("--q_nu", type=float, default=0.1)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    warnings.filterwarnings("ignore")
    if a.selftest:
        raise SystemExit(0 if selftest() else 1)
    dev = torch.device("cuda" if a.device == "auto" and torch.cuda.is_available() else
                       ("cpu" if a.device == "auto" else a.device))
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    os.makedirs(a.out_dir, exist_ok=True)
    if a.smoke:
        a.seeds, a.epochs, a.max_train, a.val_max, a.tree_train, a.q_m, a.qubits = 1, 2, 3000, 1500, 3000, 300, 6
        a.target = "ids2018"
        if a.configs == ap.get_default("configs"):
            a.configs = "TREE,V3-SUP,V3-FULL,V3-DENSE,V3-QRBF,Q-IQP,Q-RBF,V3-MAX"
        D = make_smoke(a.protocol)
    else:
        D = load_data(a)
    json.dump(vars(a), open(os.path.join(a.out_dir, "v3_settings.json"), "w"), indent=1)
    import hashlib
    here = os.path.dirname(os.path.abspath(__file__))
    sha = {f: hashlib.sha256(open(os.path.join(here, f), "rb").read()).hexdigest() for f in ("hybrid_v3.py", "qkernel.py")}
    pre = __doc__[__doc__.index("PRE-REGISTERED"):__doc__.index("Development on")]
    open(os.path.join(a.out_dir, "prereg_v3.txt"), "w", encoding="utf-8").write(
        pre + "\n" + "\n".join(f"sha256 {k} {v}" for k, v in sha.items()) + "\nsettings " + json.dumps(vars(a)))
    print("code fingerprint:", {k: v[:12] for k, v in sha.items()})
    print(f"device {dev} | protocol {a.protocol} | 2017 train {len(D['ytr'])} | target "
          f"{len(D['XT']) if a.protocol == 'cross' else len(D['yte'])} | configs {a.configs}")
    run(D, a, dev, a.out_dir)


if __name__ == "__main__":
    main()
