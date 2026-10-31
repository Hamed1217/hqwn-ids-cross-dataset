"""Vector figures 4-6 for the Results section, read from results_tables.md (R1, R5, R7).
Usage: python make_paper_figures.py --md "D:/revised model/results_tables/results_tables.md" --out_dir figs"""
import argparse, os, re
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def table(md, prefix):
    for sec in re.split(r"\n## ", md):
        if sec.startswith(prefix):
            ls = [l for l in sec.split("\n") if l.startswith("|") and not l.startswith("|---")]
            hdr = [c.strip() for c in ls[0].strip("|").split("|")]
            rows = [[c.strip() for c in l.strip("|").split("|")] for l in ls[1:]]
            df = pd.DataFrame(rows, columns=hdr)
            for c in df.columns:
                v = pd.to_numeric(df[c], errors="coerce")
                if v.notna().all(): df[c] = v
            return df
    raise KeyError(prefix)

GREY_L, GREY, BLUE = "#d9d9d4", "#a8a89f", "#2a6fd6"
COL = {"TREE": GREY_L, "V3-SUP": GREY, "V3-MAX": BLUE}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "pdf.fonttype": 42, "ps.fonttype": 42,
                     "axes.spines.top": False, "axes.spines.right": False})

def fig4(md, out):
    r1 = table(md, "R1.")
    levels = [("easy (L1)", "L1\nwithin 2017"), ("medium (L2)", "L2\n2017, held-out"), ("hard (L3)", "L3\n2018, all types"),
              ("hardest (L4)", "L4\n2018, held-out"), ("UNSW known (L3)", "L3\nUNSW, all types"), ("UNSW held-out (L4)", "L4\nUNSW, held-out")]
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    w = 0.26
    for gi, (lv, lab) in enumerate(levels):
        sub = r1[(r1["level"] == lv) & r1["model"].isin(COL)]
        ms = [m for m in COL if m in set(sub["model"])]
        for j, m in enumerate(ms):
            v = float(sub.loc[sub["model"] == m, "recall1"].iloc[0])
            x = gi + (j - (len(ms) - 1) / 2) * (w + 0.02)
            ax.bar(x, v, w, color=COL[m], label=m if gi == 2 else None, edgecolor="none")
            ax.text(x, v + 0.015, f"{v + 1e-9:.2f}", ha="center", va="bottom", fontsize=7)
    ax.axvline(3.5, color="#888", ls="--", lw=0.8)
    ax.text(3.45, 0.97, "CIC-IDS2017 / CSE-CIC-IDS2018", ha="right", fontsize=7, color="#555")
    ax.text(3.55, 0.97, "CIC-UNSW-NB15 (confirmatory)", ha="left", fontsize=7, color="#555")
    ax.set_xticks(range(len(levels))); ax.set_xticklabels([l for _, l in levels], fontsize=7.5)
    ax.set_ylim(0, 1.0); ax.set_ylabel("Calibrated recall at nominal FPR 1%")
    ax.legend(frameon=False, ncol=3, loc="upper left", bbox_to_anchor=(0, 1.13), fontsize=8)
    fig.tight_layout(); save(fig, out, "Fig4_recall_ladder")

def fig5(md, out):
    r5 = table(md, "R5.")
    r5 = r5[r5["group"].isin(["counterpart", "new"])].sort_values("V3-MAX")
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    for i, (_, r) in enumerate(r5.iterrows()):
        ax.plot([r["V3-SUP"], r["V3-MAX"]], [i, i], color=GREY, lw=1.5, zorder=1)
        ax.scatter(r["V3-SUP"], i, s=28, color=GREY, zorder=2, label="V3-SUP" if i == 0 else None)
        ax.scatter(r["V3-MAX"], i, s=36, color=BLUE, zorder=3, label="V3-MAX" if i == 0 else None)
        ax.text(r["V3-MAX"] + 0.015, i, f"{r['V3-MAX']:.4f}" if r["V3-MAX"] < 0.01 else f"{r['V3-MAX']:.3f}", va="center", fontsize=7)
    ax.set_yticks(range(len(r5)))
    ax.set_yticklabels([t + (" \u2020" if g == "counterpart" else "") for t, g in zip(r5["type"], r5["group"])])
    ax.set_xlim(0, 0.8); ax.set_xlabel("Calibrated recall at nominal FPR 1%")
    ax.grid(axis="x", color="#eee"); ax.legend(frameon=False, loc="lower right", fontsize=8)
    fig.tight_layout(); save(fig, out, "Fig5_unsw_per_type")

def fig6(md, out):
    r7 = table(md, "R7_unsw_primary")
    d = r7[(r7["scenario"] == "known") & (r7["fpr"] == 0.01) & r7["model"].isin(COL)]
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    for m in COL:
        a = d[(d["model"] == m) & (d["k"] == 1)].iloc[0]; b = d[(d["model"] == m) & (d["k"] == 3)].iloc[0]
        ax.plot([a["fa_minutes_per_hour"], b["fa_minutes_per_hour"]], [a["episode_recall"], b["episode_recall"]],
                ls="--", lw=0.8, color=COL[m] if m != "TREE" else GREY)
        for r, mk in ((a, "o"), (b, "s")):
            ax.scatter(r["fa_minutes_per_hour"], r["episode_recall"], s=40, marker=mk, color=COL[m],
                       edgecolor=GREY if m == "TREE" else "none", zorder=3)
        if m == "V3-MAX":
            ax.annotate(f"{a['episode_recall']:.3f}", (a["fa_minutes_per_hour"], a["episode_recall"]), xytext=(-6, 8), textcoords="offset points", ha="right", fontsize=7)
            ax.annotate(f"{b['episode_recall']:.3f}", (b["fa_minutes_per_hour"], b["episode_recall"]), xytext=(6, -12), textcoords="offset points", fontsize=7)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker="o", ls="", color=COL[m], markeredgecolor=GREY if m == "TREE" else COL[m], label=m) for m in COL]
    h += [Line2D([], [], marker="o", ls="", color="#666", label="k = 1"), Line2D([], [], marker="s", ls="", color="#666", label="k = 3")]
    ax.legend(handles=h, frameon=False, fontsize=7.5, loc="upper left", ncol=2)
    ax.set_xlim(0, 18); ax.set_ylim(0, 0.8)
    ax.set_xlabel("False-alarm minutes per hour of benign traffic"); ax.set_ylabel("Episode recall")
    ax.grid(color="#eee"); fig.tight_layout(); save(fig, out, "Fig6_event_tradeoff")

def save(fig, out, name):
    for ext in ("pdf", "eps", "png"):
        fig.savefig(os.path.join(out, f"{name}.{ext}"), dpi=600 if ext == "png" else None, bbox_inches="tight")
    plt.close(fig); print("saved", name)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--md", required=True); ap.add_argument("--out_dir", default="figs")
    a = ap.parse_args(); os.makedirs(a.out_dir, exist_ok=True)
    md = open(a.md, encoding="utf-8").read()
    fig4(md, a.out_dir); fig5(md, a.out_dir); fig6(md, a.out_dir)
