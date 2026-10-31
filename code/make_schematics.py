"""Schematic figures 1 (architecture) and 2 (evaluation levels) for the manuscript."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "pdf.fonttype": 42, "ps.fonttype": 42})
GREY, LGREY, BLUE, LBLUE, DARK = "#a8a89f", "#ececE6", "#2a6fd6", "#dbe7fa", "#333333"

def box(ax, x, y, w, h, text, fc=LGREY, ec=GREY, bold=False, fs=7.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.015", fc=fc, ec=ec, lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=DARK, weight="bold" if bold else "normal", wrap=True)

def arrow(ax, x1, y1, x2, y2, color=DARK):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=8, lw=0.9, color=color))

def fig1(out):
    fig, ax = plt.subplots(figsize=(10, 5.6)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    # inputs
    box(ax, 0.01, 0.80, 0.17, 0.10, "69 flow features\n(quantile-scaled)")
    box(ax, 0.01, 0.47, 0.17, 0.12, "16-minute service-load\nsequence (3 channels)")
    box(ax, 0.01, 0.12, 0.17, 0.12, "Benign-labeled target\nreference flows")
    # branches
    box(ax, 0.24, 0.86, 0.20, 0.08, "Branch T: gradient-boosted\ntree → embedding")
    box(ax, 0.24, 0.74, 0.20, 0.08, "Branch D: dense network\n69→64→32")
    # temporal path
    ax.add_patch(FancyBboxPatch((0.225, 0.38), 0.47, 0.29, boxstyle="round,pad=0.01", fc="white", ec=BLUE, lw=1, ls="--"))
    ax.text(0.235, 0.645, "Branch P: spiking temporal path", fontsize=8, color=BLUE, weight="bold")
    box(ax, 0.235, 0.42, 0.10, 0.17, "Causal\nwavelet\nfilter bank\n(Db2 init.)", fc=LBLUE, ec=BLUE, fs=7)
    box(ax, 0.350, 0.42, 0.10, 0.17, "LIF spiking\nneurons\n(12→32)", fc=LBLUE, ec=BLUE, fs=7)
    box(ax, 0.465, 0.42, 0.10, 0.17, "Spiking\nself-attention\n(causal)", fc=LBLUE, ec=BLUE, fs=7)
    box(ax, 0.580, 0.42, 0.10, 0.17, "Spike-rate\nreadout\n(64→32)", fc=LBLUE, ec=BLUE, fs=7)
    for x in (0.335, 0.450, 0.565): arrow(ax, x, 0.505, x + 0.015, 0.505, BLUE)
    # gate & head
    box(ax, 0.72, 0.66, 0.12, 0.14, "Softmax gate\n+ head\n(MMD alignment\nin training)")
    box(ax, 0.87, 0.68, 0.12, 0.10, "V3-SUP score\n→ percentile", bold=True)
    # novelty
    box(ax, 0.24, 0.10, 0.44, 0.16, "Novelty channel: 75 inputs → quantile, PCA (8), scaling →\none-class SVM with IQP quantum fidelity kernel (8 qubits,\nexact simulation) or RBF control → percentile vs reference", fc=LBLUE, ec=BLUE, fs=7)
    box(ax, 0.72, 0.13, 0.12, 0.10, "Novelty score\n→ percentile")
    box(ax, 0.87, 0.36, 0.12, 0.14, "V3-MAX =\nmax of the two\npercentiles;\nthreshold B", fc=BLUE, ec=BLUE, bold=True, fs=7.5)
    for t in ax.texts[-1:]: t.set_color("white")
    # arrows
    arrow(ax, 0.18, 0.85, 0.24, 0.90); arrow(ax, 0.18, 0.85, 0.24, 0.78)
    arrow(ax, 0.18, 0.53, 0.235, 0.505)
    arrow(ax, 0.18, 0.18, 0.24, 0.18)
    arrow(ax, 0.18, 0.53, 0.24, 0.22)
    arrow(ax, 0.18, 0.85, 0.24, 0.24)
    arrow(ax, 0.44, 0.90, 0.72, 0.77); arrow(ax, 0.44, 0.78, 0.72, 0.74); arrow(ax, 0.68, 0.505, 0.72, 0.68)
    arrow(ax, 0.84, 0.73, 0.87, 0.73)
    arrow(ax, 0.68, 0.18, 0.72, 0.18)
    arrow(ax, 0.93, 0.68, 0.93, 0.50); arrow(ax, 0.84, 0.18, 0.92, 0.36)
    ax.text(0.01, 0.02, "Blue: components compared with matched classical twins (dense network; RBF kernel). Target attack labels are never used.", fontsize=6.8, color="#555")
    save(fig, out, "Fig1_architecture")

def fig2(out):
    fig, ax = plt.subplots(figsize=(9, 4.4)); ax.set_xlim(0, 1); ax.set_ylim(-0.08, 1); ax.axis("off")
    ax.text(0.40, 0.95, "Attack type has a counterpart in training", ha="center", fontsize=8, weight="bold")
    ax.text(0.795, 0.95, "Counterpart held out", ha="center", fontsize=8, weight="bold")
    ax.text(0.08, 0.66, "Same dataset\n(CIC-IDS2017,\nblock split)", ha="center", va="center", fontsize=8, weight="bold")
    ax.text(0.08, 0.27, "Target dataset\n(CSE-CIC-IDS2018:\ndevelopment;\nCIC-UNSW-NB15:\nconfirmatory)", ha="center", va="center", fontsize=8, weight="bold")
    box(ax, 0.20, 0.50, 0.40, 0.34, "L1\nall 14 types in training\n(within-dataset upper bound)")
    box(ax, 0.63, 0.50, 0.33, 0.34, "L2\none of ten types held out\nfrom training per run")
    box(ax, 0.20, 0.08, 0.40, 0.36, "L3\nmodel trained on all 2017 attacks,\ntested on all target types;\nbenign target traffic for alignment,\nnovelty reference and threshold B", fc=LBLUE, ec=BLUE)
    box(ax, 0.63, 0.08, 0.33, 0.36, "L4\n2017 counterpart family held out;\ntarget types with that\ncounterpart tested", fc=LBLUE, ec=BLUE)
    arrow(ax, 0.40, 0.03, 0.80, 0.03, GREY); ax.text(0.60, -0.01, "less overlap with training attacks →", ha="center", va="top", fontsize=7, color="#555")
    save(fig, out, "Fig2_levels")

def save(fig, out, name):
    import os
    for ext in ("pdf", "eps", "png"):
        fig.savefig(os.path.join(out, f"{name}.{ext}"), dpi=600 if ext == "png" else None, bbox_inches="tight")
    plt.close(fig)

if __name__ == "__main__":
    fig1("out"); fig2("out")
