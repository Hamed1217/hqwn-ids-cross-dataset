"""
Figures of the paper, all drawn from our own code and our own result files (no borrowed images).
Vector PDF + 600-dpi PNG, colour-blind-safe palette (Okabe-Ito), English labels (the paper is in English).

  fig1_architecture      the V3 detector: tree T, flow network D, spiking temporal path P, gate, alignment,
                         quantum-kernel novelty channel Q, late fusion, local threshold B, stage-2 naming   (schematic)
  fig2_temporal_path     (a) the temporal path step by step (schematic); (b) REAL mean 16-minute service-load
                         sequences of benign and attack types from the target cache
  fig3_protocol          datasets and roles (2017 train -> 2018 development -> UNSW confirmatory once), the benign thirds,
                         the four-level evaluation ladder                                                    (schematic)
  fig4_shift_2d          REAL flows in 2-D (PCA fitted on 2017 benign): benign of the three networks; UNSW benign vs attacks
  fig5_results           (a) ladder with 95% bootstrap intervals (ci_models.csv of bootstrap_ci.py); (b) per-seed paired
                         recall, hard level (threshold cliff); (c) per-type recall, UNSW; (d) latency and energy
  fig6_quantum           quantum (IQP) vs classical (RBF) kernel: same novelty channel, every seed x type, all levels

Every figure is skipped with a message if its input files are missing, so it can be run step by step.
  python make_figures.py --out_dir "D:/revised model/figures"
  (all paths have defaults under D:/revised model; see --help)
  python make_figures.py --selftest      (draws the schematics and every data figure from synthetic files)
"""
import argparse, json, os
import numpy as np
import pandas as pd

OI = dict(black="#000000", orange="#E69F00", sky="#56B4E9", green="#009E73", yellow="#F0E442", blue="#0072B2",
          vermillion="#D55E00", purple="#CC79A7", grey="#999999")
MODEL_COL = {"TREE": OI["grey"], "V3-SUP": OI["blue"], "V3-MAX": OI["vermillion"], "V3-MAX-RBF": OI["orange"],
             "V3-SUP-DENSE": OI["sky"], "V3-SUP-NOA": OI["green"]}
LEVELS = [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard"), ("hardest", "Hardest"),
          ("unsw_known", "UNSW\nall"), ("unsw_loo", "UNSW\nheld-out")]


def setup():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8,
                         "legend.fontsize": 7, "xtick.labelsize": 7, "ytick.labelsize": 7, "pdf.fonttype": 42,
                         "axes.spines.top": False, "axes.spines.right": False})
    return plt


def save(fig, out_dir, name):
    os.makedirs(out_dir, exist_ok=True)
    for ext, kw in (("pdf", {}), ("png", {"dpi": 600})):
        p = os.path.join(out_dir, f"{name}.{ext}")
        fig.savefig(p, bbox_inches="tight", **kw)
    print(f"  saved {os.path.join(out_dir, name)}.pdf / .png")


def box(ax, x, y, w, h, text, fc="#ffffff", ec="#333333", fs=7, bold=False, ls="-"):
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.015", fc=fc, ec=ec, lw=0.8,
                                ls=ls))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, weight="bold" if bold else "normal",
            wrap=True)


def arrow(ax, x0, y0, x1, y1, style="-|>", color="#333333", ls="-"):
    from matplotlib.patches import FancyArrowPatch
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=7, lw=0.8, color=color, ls=ls))


# ----------------------------------------------------------------------------------------------- schematics
def fig1(plt, out):
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.set_xlim(-0.01, 1.01); ax.set_ylim(0, 1); ax.axis("off")
    lt, fs = "#eef5fb", 6
    box(ax, 0.00, 0.64, 0.12, 0.14, "Flow features\n69 per flow\n(no IP address)", fc="#f4f4f4", fs=fs)
    box(ax, 0.00, 0.33, 0.12, 0.16, "Service-load\nsequence\n16 min x 3\nchannels", fc="#f4f4f4", fs=fs)
    box(ax, 0.16, 0.84, 0.20, 0.10, "T: gradient-boosted\ntree (logit)", fc=lt, fs=fs)
    box(ax, 0.16, 0.68, 0.20, 0.10, "D: flow network\n(MLP)", fc=lt, fs=fs)
    box(ax, 0.16, 0.31, 0.20, 0.31, "P: spiking temporal path\n\ncausal db2 wavelet\n|\nLIF spiking neurons\n|\n"
                                   "spiking self-attention\n|\nspike-rate read-out", fc=lt, fs=fs)
    box(ax, 0.41, 0.55, 0.10, 0.17, "Gate\nsoftmax\nweights\nper flow", fc=lt, fs=fs)
    box(ax, 0.41, 0.28, 0.10, 0.17, "MMD\nalignment\n(training\nonly)", ls="--", fs=fs)
    box(ax, 0.55, 0.58, 0.11, 0.11, "Supervised\nscore\nV3-SUP", fc="#dbe9f6", bold=True, fs=fs)
    box(ax, 0.16, 0.03, 0.35, 0.15, "Q: novelty channel\n8-qubit IQP kernel (simulated)\n+ one-class SVM on LOCAL benign flows", fc="#fdeee4", fs=fs)
    box(ax, 0.70, 0.34, 0.11, 0.15, "Late fusion\nmax of\npercentiles\n= V3-MAX", fc="#fbe0d0", bold=True, fs=fs)
    box(ax, 0.85, 0.34, 0.15, 0.15, "Threshold B\n99th percentile of\nlocal calibration\nbenign -> alarm",
        fc="#f4f4f4", fs=fs)
    box(ax, 0.85, 0.06, 0.15, 0.15, "Stage 2\nattack family\nor 'unknown'\n(open set)", ls="--", fs=fs)
    arrow(ax, 0.12, 0.74, 0.16, 0.89)
    arrow(ax, 0.12, 0.71, 0.16, 0.73)
    arrow(ax, 0.12, 0.41, 0.16, 0.46)
    arrow(ax, 0.06, 0.64, 0.06, 0.49, style="-")                     # flow features feed Q as well
    arrow(ax, 0.06, 0.33, 0.06, 0.10, style="-")
    arrow(ax, 0.06, 0.10, 0.16, 0.10)
    ax.text(0.065, 0.115, "flow features", fontsize=fs - 1, color="#555555", va="bottom")
    for y in (0.89, 0.73, 0.50):
        arrow(ax, 0.36, y, 0.41, 0.635)
    arrow(ax, 0.36, 0.40, 0.41, 0.365, ls="--")
    arrow(ax, 0.51, 0.635, 0.55, 0.635)
    arrow(ax, 0.605, 0.58, 0.72, 0.49)
    arrow(ax, 0.51, 0.105, 0.72, 0.34)
    arrow(ax, 0.81, 0.415, 0.85, 0.415)
    arrow(ax, 0.925, 0.34, 0.925, 0.21, ls="--")
    ax.text(0.60, 0.80, "trained with CIC-IDS2017 labels", fontsize=fs, color="#555555", ha="center")
    ax.text(0.68, 0.06, "no attack labels of the\nnew network are used", fontsize=fs, color="#555555", ha="center")
    save(fig, out, "fig1_architecture")
    plt.close(fig)


def fig3(plt, out):
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw=dict(width_ratios=[1.35, 1]))
    for ax in (a, b):
        ax.set_xlim(-0.02, 1.02); ax.set_ylim(0, 1); ax.axis("off")
    fs = 6
    box(a, 0.00, 0.60, 0.28, 0.26, "CIC-IDS2017\ntraining (labels)\nmodel design", fc="#dbe9f6", bold=True, fs=fs)
    box(a, 0.36, 0.60, 0.28, 0.26, "CSE-CIC-IDS2018\ndevelopment\n(4 revisions,\nall reported)", fc="#eef5fb", fs=fs)
    box(a, 0.72, 0.60, 0.28, 0.26, "CIC-UNSW-NB15\nconfirmatory\n(run once,\npre-registered)", fc="#fbe0d0",
        bold=True, fs=fs)
    arrow(a, 0.28, 0.73, 0.36, 0.73); arrow(a, 0.64, 0.73, 0.72, 0.73)
    a.text(0.5, 0.47, "benign flows of the new network (no attack labels), random thirds:", ha="center", fontsize=fs)
    for i, t in enumerate(("fit:\nnovelty model\n+ alignment", "calibration:\nthreshold B\n(99th percentile)",
                           "test:\nreal false-\nalarm rate")):
        box(a, 0.02 + i * 0.34, 0.10, 0.28, 0.28, t, fc="#f4f4f4", fs=fs)
    a.set_title("(a) datasets, roles and the local benign thirds", loc="left")
    b.set_title("(b) four-level evaluation ladder", loc="left")
    cells = [((0.22, 0.50), "EASY\nsame network\nseen attacks", "#e5f4e4"),
             ((0.61, 0.50), "MEDIUM\nsame network\nunseen attacks", "#f9eeda"),
             ((0.22, 0.08), "HARD\nnew network\nseen attacks", "#f9ece7"),
             ((0.61, 0.08), "HARDEST\nnew network\nunseen attacks", "#fbebeb")]
    for (x, y), t, c in cells:
        box(b, x, y, 0.36, 0.36, t, fc=c, fs=fs)
    b.text(0.60, 0.95, "attack type in training", ha="center", fontsize=fs)
    b.text(0.40, 0.89, "seen", ha="center", fontsize=fs, color="#555555")
    b.text(0.79, 0.89, "unseen", ha="center", fontsize=fs, color="#555555")
    b.text(0.04, 0.47, "network", rotation=90, va="center", fontsize=fs)
    b.text(0.13, 0.68, "same", rotation=90, va="center", fontsize=fs, color="#555555")
    b.text(0.13, 0.26, "new", rotation=90, va="center", fontsize=fs, color="#555555")
    save(fig, out, "fig3_protocol")
    plt.close(fig)


# ----------------------------------------------------------------------------------------------- data figures
def fig2(plt, out, cache):
    if not os.path.exists(cache):
        print(f"  fig2 (b) skipped: no target cache {cache}"); seq = None
    else:
        z = np.load(cache, allow_pickle=True)
        seq, lab = np.asarray(z["seq"], "float32"), z["lab"].astype(str)
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.6), gridspec_kw=dict(width_ratios=[1, 1.15]))
    a.set_xlim(0, 1); a.set_ylim(0, 1); a.axis("off")
    steps = [("16-minute service-load\nsequence (t-15 ... t)", "#f4f4f4"), ("causal db2 wavelet\n(3 levels, learnable,"
             " init. db2)", "#eef5fb"), ("LIF spiking neurons\n(binary spikes)", "#eef5fb"),
             ("spiking self-attention\nover the 16 minutes", "#eef5fb"), ("spike-rate read-out\n-> 32-d embedding",
                                                                       "#dbe9f6")]
    for i, (t, c) in enumerate(steps):
        y = 0.82 - i * 0.19
        box(a, 0.10, y, 0.80, 0.14, t, fc=c, fs=6)
        if i:
            arrow(a, 0.5, y + 0.19, 0.5, y + 0.14)
    a.set_title("(a) temporal path P", loc="left")
    if seq is not None:
        minutes = np.arange(-seq.shape[1] + 1, 1)
        ben = lab == "Benign"
        types_ = pd.Series(lab[~ben]).value_counts().index[:4]
        b.plot(minutes, seq[ben, :, 0].mean(0), color=OI["black"], lw=1.4, label="Benign")
        for t, c in zip(types_, (OI["vermillion"], OI["blue"], OI["green"], OI["purple"])):
            b.plot(minutes, seq[lab == t, :, 0].mean(0), color=c, lw=1.1, label=t)
        b.set_xlabel("minute relative to the flow (0 = the flow's minute)")
        b.set_ylabel("load of the flow's service\nrelative to its own normal (log)")
        b.legend(frameon=False, ncol=1)
        name = os.path.basename(cache).lower()
        net = "CIC-UNSW-NB15" if "unsw" in name else ("CSE-CIC-IDS2018" if "2018" in name else os.path.basename(cache))
        b.set_title(f"(b) mean sequences of real flows, {net}", loc="left")
    else:
        b.axis("off")
    save(fig, out, "fig2_temporal_path")
    plt.close(fig)


def load_networks(s17_dir, c18, cunsw, n_each, seed):
    import joblib
    feats = json.load(open(os.path.join(s17_dir, "feature_names.json")))
    flow = [f for f in feats if not f.startswith(("win_", "pw_", "gl_"))]
    fidx = np.array([feats.index(c) for c in flow])
    qt = joblib.load(os.path.join(s17_dir, "quantile_transformer.joblib"))
    z = np.load(os.path.join(s17_dir, "splits.npz"), allow_pickle=True)
    g = np.random.default_rng(seed)
    out = {}
    b17 = np.where(z["yte"] == 0)[0]
    out["2017"] = (z["Xte"][g.choice(b17, min(n_each, len(b17)), replace=False)][:, fidx], None)
    for name, path in (("2018", c18), ("UNSW", cunsw)):
        if not os.path.exists(path):
            continue
        zc = np.load(path, allow_pickle=True)
        raw = pd.DataFrame(zc["X"], columns=list(zc["cols"]))
        lab = zc["lab"].astype(str)
        pick = np.r_[g.choice(np.where(lab == "Benign")[0], min(n_each, int((lab == "Benign").sum())), replace=False),
                     g.choice(np.where(lab != "Benign")[0], min(n_each, int((lab != "Benign").sum())), replace=False)]
        full = pd.DataFrame(0.0, index=range(len(pick)), columns=feats)
        for c in feats:
            if c in raw.columns:
                full[c] = raw[c].values[pick]
        out[name] = (qt.transform(full)[:, fidx], lab[pick])
    return out


def fig4(plt, out, s17_dir, c18, cunsw, n_each=3000, seed=0):
    if not os.path.exists(os.path.join(s17_dir, "splits.npz")):
        print("  fig4 skipped: no 2017 stage-1 output"); return
    from sklearn.decomposition import PCA
    nets = load_networks(s17_dir, c18, cunsw, n_each, seed)
    pca = PCA(2, random_state=0).fit(nets["2017"][0])
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0), sharex=True, sharey=True)
    cols = {"2017": OI["blue"], "2018": OI["orange"], "UNSW": OI["green"]}
    for name, (X, lab) in nets.items():
        Xb = X if lab is None else X[lab == "Benign"]
        P = pca.transform(Xb)
        axs[0].scatter(P[:, 0], P[:, 1], s=1.5, alpha=0.35, color=cols[name], lw=0, label=f"{name} benign",
                       rasterized=True)
    axs[0].legend(frameon=False, markerscale=6)
    axs[0].set_title("(a) benign traffic of three networks", loc="left")
    if "UNSW" in nets:
        X, lab = nets["UNSW"]
        P = pca.transform(X)
        axs[1].scatter(*P[lab == "Benign"].T, s=1.5, alpha=0.35, color=OI["green"], lw=0, label="UNSW benign",
                       rasterized=True)
        for t, c in zip(pd.Series(lab[lab != "Benign"]).value_counts().index[:5],
                        (OI["vermillion"], OI["blue"], OI["purple"], OI["orange"], OI["black"])):
            axs[1].scatter(*P[lab == t].T, s=1.5, alpha=0.5, color=c, lw=0, label=t, rasterized=True)
        axs[1].legend(frameon=False, markerscale=6, fontsize=6)
        axs[1].set_title("(b) UNSW benign and attack types", loc="left")
    ev = pca.explained_variance_ratio_
    for ax in axs:
        ax.set_xlabel(f"PC 1 ({ev[0]:.0%} of 2017 benign variance)")
    axs[0].set_ylabel(f"PC 2 ({ev[1]:.0%})")
    save(fig, out, "fig4_shift_2d")
    plt.close(fig)


def fig5(plt, out, ci_csv, hard_csv, unsw_csv, lat_csv, en_csv, fast):
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.6))
    (a, b), (c, d) = axs
    drawn = 0
    if os.path.exists(ci_csv):
        ci = pd.read_csv(ci_csv)
        ci = ci[ci.metric == "recall1"]
        models = [m for m in ("TREE", "V3-SUP", "V3-MAX") if m in set(ci.model)]
        lv = [(k, t) for k, t in LEVELS if k in set(ci.level)]
        w = 0.8 / max(len(models), 1)
        for j, m in enumerate(models):
            for i, (k, _) in enumerate(lv):
                r = ci[(ci.level == k) & (ci.model == m)]
                if r.empty:
                    continue
                r = r.iloc[0]
                a.bar(i + (j - (len(models) - 1) / 2) * w, r["mean"], w * 0.9, color=MODEL_COL[m],
                      label=m if k == next(kk for kk, _ in lv if not ci[(ci.level == kk) & (ci.model == m)].empty) else None)
                a.errorbar(i + (j - (len(models) - 1) / 2) * w, r["mean"], yerr=[[r["mean"] - r.lo], [r.hi - r["mean"]]],
                           color="black", lw=0.7, capsize=1.5)
        a.set_xticks(range(len(lv)))
        a.set_xticklabels([t for _, t in lv], fontsize=6.5)
        a.set_ylabel("recall at 1% false alarms\n(mean over attack types)")
        a.set_ylim(0, 1.12)
        a.set_yticks(np.arange(0, 1.01, 0.2))
        a.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.02))
        drawn += 1
    else:
        print(f"  fig5 (a) skipped: no {ci_csv} (run bootstrap_ci.py)")
    a.set_title("(a) evaluation ladder, 95% bootstrap intervals", loc="left")
    if os.path.exists(hard_csv):
        h = pd.read_csv(hard_csv)
        h = h[h.scenario == "known"].groupby(["model", "seed"]).recall1.mean().unstack(0)
        if {"TREE", "V3-SUP"} <= set(h.columns):
            for s, r in h.iterrows():
                b.plot([0, 1], [r["TREE"], r["V3-SUP"]], color=OI["grey"], lw=0.7)
            b.scatter(np.zeros(len(h)), h["TREE"], color=MODEL_COL["TREE"], s=12, zorder=3)
            b.scatter(np.ones(len(h)), h["V3-SUP"], color=MODEL_COL["V3-SUP"], s=12, zorder=3)
            b.set_xticks([0, 1]); b.set_xticklabels(["TREE", "V3-SUP"]); b.set_xlim(-0.4, 1.4)
            b.set_ylabel("recall at 1% (one point per seed)")
            drawn += 1
    else:
        print(f"  fig5 (b) skipped: no {hard_csv}")
    b.set_title("(b) hard level: recall per seed (paired)", loc="left")
    if os.path.exists(unsw_csv):
        u = pd.read_csv(unsw_csv)
        u = u[u.scenario == "known"]
        piv = u.groupby(["type", "model"]).recall1.mean().unstack()
        piv = piv[[m for m in ("TREE", "V3-SUP", "V3-MAX-RBF", "V3-MAX") if m in piv.columns]]
        piv = piv.sort_values(piv.columns[-1], ascending=False)
        im = c.imshow(piv.values, aspect="auto", cmap="Blues", vmin=0, vmax=max(0.8, np.nanmax(piv.values)))
        c.set_xticks(range(len(piv.columns))); c.set_xticklabels(piv.columns, fontsize=6.5)
        c.set_yticks(range(len(piv.index))); c.set_yticklabels(piv.index, fontsize=6.5)
        for i in range(piv.shape[0]):
            for j in range(piv.shape[1]):
                v = piv.values[i, j]
                c.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6, color="white" if v > 0.45 else "black")
        fig.colorbar(im, ax=c, fraction=0.04, pad=0.02)
        drawn += 1
    else:
        print(f"  fig5 (c) skipped: no {unsw_csv}")
    c.set_title("(c) UNSW (confirmatory): recall at 1% per type", loc="left")
    if os.path.exists(lat_csv):
        L = pd.read_csv(lat_csv).set_index("config").end_to_end_p95_ms
        names = list(L.index)
        vals = list(L.values)
        cols = [OI["grey"] if n == "TREE" else (OI["vermillion"] if "MAX" in n else OI["blue"]) for n in names]
        y = np.arange(len(names))
        mx = np.array(["MAX" in n for n in names])
        if fast and mx.any():
            fv = [v if "MAX" not in n else L["V3-SUP"] + (fast[0] if "RBF" not in n else fast[1]) for n, v in zip(names, vals)]
            d.barh(y[mx], np.array(vals)[mx], color=np.array(cols)[mx], alpha=0.30, height=0.75)
            d.barh(y, fv, color=cols, height=0.45)
            for yy, v0, v1 in zip(y[mx], np.array(vals)[mx], np.array(fv)[mx]):
                d.text(v1 + 1, yy, "optimised", va="center", fontsize=5.5)
                d.text(v0 - 1, yy + 0.27, "first implementation (same outputs)", va="center", ha="right", fontsize=5.5,
                       color="#555555", zorder=4, bbox=dict(fc="#f2cfb2", ec="none", pad=0.4))
        else:
            d.barh(y, vals, color=cols, height=0.6)
        d.axvline(40, color="black", ls="--", lw=0.8, zorder=3)
        d.text(41, int(np.argmax(~mx)) + 0.0 if (~mx).any() else 0, "40 ms claim", fontsize=6, va="center")
        d.set_yticks(y); d.set_yticklabels(names, fontsize=6.5)
        d.set_xlim(0, max(90, max(vals) * 1.08))
        d.set_xlabel("end-to-end latency per flow, p95 (ms, 1 CPU thread)")
        if os.path.exists(en_csv):
            e = pd.read_csv(en_csv)
            r = []
            for mem in sorted(e.mem_pJ_per_read.unique()):
                q = e[e.mem_pJ_per_read == mem].set_index("model")
                if {"V3-SUP", "V3-SUP-DENSE"} <= set(q.index):
                    r.append(f"+{mem:g} pJ/read: {q.loc['V3-SUP', 'total_energy_nJ'] / q.loc['V3-SUP-DENSE', 'total_energy_nJ']:.2f}")
            if r:
                d.text(0.98, 0.04, "estimated energy,\nspiking / dense\n(whole model)\n" + "\n".join(r),
                       transform=d.transAxes, ha="right", va="bottom", fontsize=6)
        drawn += 1
    else:
        print(f"  fig5 (d) skipped: no {lat_csv} (measure_v3.py output)")
        d.axis("off")
    d.set_title("(d) efficiency", loc="left")
    fig.tight_layout()
    if drawn:
        save(fig, out, "fig5_results")
        # the journal guide discourages several graphs in one file -> each panel also as its own file
        from matplotlib.transforms import Bbox
        r = fig.canvas.get_renderer()
        extra = [x for x in fig.axes if x not in list(axs.flat)]           # colour bar of panel (c)
        for tag, grp in (("a", [a]), ("b", [b]), ("c", [c] + extra), ("d", [d])):
            if not grp[0].axison:
                continue
            bb = Bbox.union([g.get_tightbbox(r) for g in grp]).transformed(fig.dpi_scale_trans.inverted()).padded(0.04)
            for ext, kw in (("pdf", {}), ("png", {"dpi": 600})):
                fig.savefig(os.path.join(out, f"fig5{tag}.{ext}"), bbox_inches=bb, **kw)
        print(f"  saved the panels separately: fig5a ... fig5d")
    plt.close(fig)


def fig6(plt, out, runs):
    pts = []
    for label, path, scen in runs:
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        df = df[df.scenario == scen]
        if not {"V3-MAX", "V3-MAX-RBF"} <= set(df.model):
            continue
        p = df[df.model.isin(["V3-MAX", "V3-MAX-RBF"])].pivot_table(index=["seed", "held", "type"], columns="model",
                                                                    values="recall1")
        p["level"] = label
        pts.append(p.reset_index())
    if not pts:
        print("  fig6 skipped: no results with both V3-MAX and V3-MAX-RBF"); return
    P = pd.concat(pts)
    fig, ax = plt.subplots(figsize=(3.4, 3.2))
    for (lvl, g), c in zip(P.groupby("level", sort=False), (OI["blue"], OI["orange"], OI["green"], OI["vermillion"],
                                                            OI["purple"], OI["sky"])):
        ax.scatter(g["V3-MAX-RBF"], g["V3-MAX"], s=6, alpha=0.6, color=c, lw=0, label=f"{lvl} (n={len(g)})")
    ax.plot([0, 1], [0, 1], color="black", lw=0.7, ls="--")
    d = (P["V3-MAX"] - P["V3-MAX-RBF"])
    ax.text(0.03, 0.93, f"mean difference IQP - RBF {d.mean():+.3f}", transform=ax.transAxes, fontsize=6.5)
    ax.set_xlabel("recall at 1%, classical RBF kernel"); ax.set_ylabel("recall at 1%, quantum IQP kernel (simulated)")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.legend(frameon=False, fontsize=6, loc="lower right")
    # title goes in the caption (journal guide: caption title is not displayed on the figure)
    save(fig, out, "fig6_quantum")
    plt.close(fig)


def selftest(out):
    """synthetic inputs in a temporary folder; checks that every figure file is written"""
    import tempfile
    tmp = tempfile.mkdtemp()
    g = np.random.default_rng(0)
    ci = []
    for k, _ in LEVELS:
        for m in ("TREE", "V3-SUP", "V3-MAX"):
            v = g.uniform(0.02, 0.9)
            ci.append(dict(level=k, metric="recall1", model=m, mean=v, lo=max(v - 0.05, 0), hi=min(v + 0.05, 1)))
    pd.DataFrame(ci).to_csv(os.path.join(tmp, "ci.csv"), index=False)
    rows = []
    for s in range(10):
        for t in ("Exploits", "Fuzzers", "Recon", "DoS"):
            for m in ("TREE", "V3-SUP", "V3-MAX", "V3-MAX-RBF"):
                rows.append(dict(scenario="known", held="-", seed=s, model=m, type=t, recall1=g.uniform(0, 0.7)))
    pd.DataFrame(rows).to_csv(os.path.join(tmp, "res.csv"), index=False)
    pd.DataFrame(dict(config=["TREE", "V3-SUP", "V3-SUP-DENSE", "V3-MAX (IQP)", "V3-MAX-RBF"],
                      end_to_end_p95_ms=[3.4, 20.3, 16.4, 71.6, 83.4])).to_csv(os.path.join(tmp, "lat.csv"), index=False)
    pd.DataFrame([dict(model=m, mem_pJ_per_read=e, total_energy_nJ=v) for e in (0, 5, 50)
                  for m, v in (("V3-SUP", 97 + e), ("V3-SUP-DENSE", 463 + 2 * e))]).to_csv(os.path.join(tmp, "en.csv"),
                                                                                         index=False)
    n = 4000
    lab = np.where(g.random(n) < 0.6, "Benign", g.choice(["Exploits", "Fuzzers", "Recon"], n))
    seq = g.normal(size=(n, 16, 3)).astype("float16")
    seq[lab != "Benign", -3:, 0] += 1.5
    np.savez(os.path.join(tmp, "cache.npz"), seq=seq, lab=lab)
    plt = setup()
    fig1(plt, out); fig3(plt, out); fig2(plt, out, os.path.join(tmp, "cache.npz"))
    fig5(plt, out, os.path.join(tmp, "ci.csv"), os.path.join(tmp, "res.csv"), os.path.join(tmp, "res.csv"),
         os.path.join(tmp, "lat.csv"), os.path.join(tmp, "en.csv"), (3.19, 2.58))
    fig6(plt, out, [("UNSW", os.path.join(tmp, "res.csv"), "known")])
    want = ["fig1_architecture", "fig2_temporal_path", "fig3_protocol", "fig5_results", "fig6_quantum"]
    ok = all(os.path.exists(os.path.join(out, f + ".pdf")) and os.path.exists(os.path.join(out, f + ".png")) for f in want)
    print(("ALL PASS" if ok else "SOME FIGURES MISSING") + f" (fig4 needs the real 2017 stage-1 output) -> {out}")


def main():
    R = "D:/revised model"
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_dir", default=f"{R}/figures")
    ap.add_argument("--s17_dir", default=f"{R}/stage1_pw")
    ap.add_argument("--cache18", default=f"{R}/cross_out4/ids2018_sample_v4.npz")
    ap.add_argument("--cache_unsw", default=f"{R}/unsw/unsw_sample_v1h.npz")
    ap.add_argument("--ci", default=f"{R}/ci/ci_models.csv", help="from bootstrap_ci.py")
    ap.add_argument("--hard", default=f"{R}/v33_cross10/v3_results.csv")
    ap.add_argument("--medium", default=f"{R}/v33_within10/v3_results.csv")
    ap.add_argument("--unsw", default=f"{R}/unsw_primary/v3_results.csv")
    ap.add_argument("--latency", default=f"{R}/efficiency_v3/latency_end_to_end.csv")
    ap.add_argument("--energy", default=f"{R}/efficiency_v3/energy_memory_sensitivity.csv")
    ap.add_argument("--fast_ms", default="3.19,2.58", help="p95 of the optimised novelty channel IQP,RBF (fast_novelty.py)")
    ap.add_argument("--only", default="", help="e.g. 1,3,5")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest(a.out_dir if a.out_dir != f"{R}/figures" else "figures_selftest")
    plt = setup()
    only = {x.strip() for x in a.only.split(",") if x.strip()}
    want = lambda k: not only or k in only
    fast = tuple(float(x) for x in a.fast_ms.split(",")) if a.fast_ms else None
    if want("1"): fig1(plt, a.out_dir)
    if want("2"): fig2(plt, a.out_dir, a.cache_unsw)
    if want("3"): fig3(plt, a.out_dir)
    if want("4"): fig4(plt, a.out_dir, a.s17_dir, a.cache18, a.cache_unsw)
    if want("5"): fig5(plt, a.out_dir, a.ci, a.hard, a.unsw, a.latency, a.energy, fast)
    if want("6"): fig6(plt, a.out_dir, [("medium", a.medium, "loo"), ("hard", a.hard, "known"),
                                        ("hardest", a.hard, "loo"), ("UNSW all", a.unsw, "known"),
                                        ("UNSW held-out", a.unsw, "loo")])


if __name__ == "__main__":
    main()
