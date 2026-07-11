"""Fig. B5 — Real-case DSI values on the synthetic DSI-reversal benchmark.

Reproducible from public data:
  data/synthetic_benchmark/DSI_BENCHMARK_RAW_RESULTS.csv
  data/real_case_public_derived/REAL_CASE_DSI_POSITION_IN_SYNTHETIC_BENCHMARK_CORRECTED.csv

Binning of the median curve is defined explicitly here (geometric bins on the
log axis), so the figure is reproducible end to end.

Operating-region edges [1.25, 2, 4] follow benchmark.py.
"""

from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

# ---------------------------------------------------------------- config
N_BINS = 15                      # median-curve bins (geometric on log axis)
REGION_EDGES = [1.25, 2.0, 4.0]  # from benchmark.py: bins=[0,1.25,2,4,inf]
XMIN, XMAX = 0.7, 70.0           # log-axis display window

REGIONS = [
    (XMIN, 1.25, "Unresolved",         "#f5d6d6"),
    (1.25, 2.0,  "Boundary-sensitive", "#f7e7c4"),
    (2.0,  4.0,  "Conditional",        "#d6e2f0"),
    (4.0,  XMAX, "High-margin stable", "#d9e8d5"),
]

C_SCATTER = "#7fa8cc"
C_CURVE   = "#1f6fa8"
C_MZ1     = "#e08214"
C_MZ2     = "#2f7a34"

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif"]


def load(root: Path):
    syn = pd.read_csv(root / "data" / "synthetic_benchmark" / "DSI_BENCHMARK_RAW_RESULTS.csv")
    syn.columns = [c.strip().replace("\ufeff", "") for c in syn.columns]
    real = pd.read_csv(root / "data" / "real_case_public_derived" / "REAL_CASE_DSI_POSITION_IN_SYNTHETIC_BENCHMARK_CORRECTED.csv")
    real.columns = [c.strip().replace("\ufeff", "") for c in real.columns]
    return syn, real


def binned_median(x, y, n_bins=N_BINS, lo=XMIN, hi=XMAX):
    """Geometric bins on the log axis; median of y within each populated bin."""
    edges = np.geomspace(lo, hi, n_bins + 1)
    idx = np.digitize(x, edges) - 1
    cx, cy = [], []
    for b in range(n_bins):
        m = idx == b
        if m.sum() >= 5:                       # skip near-empty bins
            cx.append(np.sqrt(edges[b] * edges[b + 1]))   # geometric centre
            cy.append(np.median(y[m]))
    return np.array(cx), np.array(cy)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    syn, real = load(root)

    x = syn["median_dsi"].to_numpy()
    y = syn["monte_carlo_reversal_probability"].to_numpy()

    # log axis cannot show DSI <= 0; keep the displayed window
    m = (x > 0) & (x >= XMIN) & (x <= XMAX)
    xs, ys = x[m], y[m]

    fig, ax = plt.subplots(figsize=(9.4, 5.4))

    # operating regions
    for left, right, label, colour in REGIONS:
        ax.axvspan(left, right, color=colour, alpha=0.55, zorder=0, lw=0)
    for e in REGION_EDGES:
        ax.axvline(e, color="#9aa4ad", lw=0.9, zorder=1)

    # synthetic cases
    ax.scatter(xs, ys, s=6, color=C_SCATTER, alpha=0.22,
               edgecolors="none", zorder=2)

    # binned median curve
    cx, cy = binned_median(xs, ys)
    ax.plot(cx, cy, "-o", color=C_CURVE, lw=2.0, ms=5.5,
            markeredgecolor="white", markeredgewidth=0.7, zorder=4)

    # real cases
    for _, r in real.iterrows():
        dsi = float(r["median_dsi"])
        colour = C_MZ1 if r["zone"] == "MZ-I" else C_MZ2
        marker = "D" if r["zone"] == "MZ-I" else "*"
        size = 130 if r["zone"] == "MZ-I" else 320
        ax.scatter(dsi, 0.0, marker=marker, s=size, color=colour,
                   edgecolors="black", linewidths=0.9, zorder=6, clip_on=False)
        ax.annotate(f"{r['zone']}\nDSI = {dsi}", xy=(dsi, 0.0),
                    xytext=(dsi, 0.135), ha="center", fontsize=10.5,
                    zorder=7,
                    arrowprops=dict(arrowstyle="-", lw=0.9, color="#444",
                                    shrinkA=2, shrinkB=6))

    ax.set_xscale("log")
    ax.set_xlim(XMIN, XMAX)
    ax.set_ylim(-0.035, 1.10)
    ax.set_xlabel("Median Domain-Separation Index  (Eq. 5, plan-distance ratio)",
                  fontsize=12.5, labelpad=8)
    ax.set_ylabel("Monte Carlo attribution\nreversal probability",
                  fontsize=12.5, labelpad=8)
    ax.tick_params(labelsize=11)
    ax.grid(axis="y", color="#e6e6e6", lw=0.8, zorder=1)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    # region names above the axes; the narrow band is raised to a second tier
    Y_LOW, Y_HIGH = 1.105, 1.215
    for left, right, label, _ in REGIONS:
        centre = np.sqrt(max(left, XMIN) * min(right, XMAX))
        if label == "Boundary-sensitive":
            ax.annotate(label, xy=(centre, 1.045), xytext=(centre, Y_HIGH),
                        ha="center", va="bottom", fontsize=10.5, color="#444",
                        zorder=5, annotation_clip=False,
                        arrowprops=dict(arrowstyle="-", lw=0.8, color="#9aa4ad",
                                        shrinkA=1, shrinkB=2))
        else:
            ax.text(centre, Y_LOW, label, ha="center", va="bottom",
                    fontsize=10.5, color="#444", zorder=5, clip_on=False)

    # legend below the axes, outside the data area
    handles = [
        Line2D([], [], marker="o", ls="none", ms=6, color=C_SCATTER,
               alpha=0.7, label="Synthetic cases"),
        Line2D([], [], marker="o", ls="-", ms=6, lw=2.0, color=C_CURVE,
               markeredgecolor="white", label="Binned median"),
        Line2D([], [], marker="D", ls="none", ms=9, color=C_MZ1,
               markeredgecolor="black", markeredgewidth=0.8, label="MZ-I real case"),
        Line2D([], [], marker="*", ls="none", ms=15, color=C_MZ2,
               markeredgecolor="black", markeredgewidth=0.8, label="MZ-II real case"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.155),
              ncol=4, fontsize=11.5, frameon=False,
              columnspacing=2.0, handletextpad=0.6)

    fig.subplots_adjust(top=0.84)
    fig.savefig(str(root / "figures" / "Fig_B5_real_case_on_synthetic_DSI_curve.png"), dpi=600, bbox_inches="tight",
                facecolor="white", pad_inches=0.22)
    fig.savefig(str(root / "figures" / "Fig_B5_real_case_on_synthetic_DSI_curve.pdf"), bbox_inches="tight",
                facecolor="white", pad_inches=0.22)

    print(f"synthetic points plotted: {m.sum()} of {len(x)} "
          f"({(x<=0).sum()} had DSI<=0, cannot appear on a log axis)")
    print(f"median-curve vertices: {len(cx)}")
    for _, r in real.iterrows():
        print(f"  {r['zone']}: DSI={r['median_dsi']}  ({r['classification']})")


if __name__ == "__main__":
    main()
