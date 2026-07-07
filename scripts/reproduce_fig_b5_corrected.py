"""Reproduce corrected Fig. B5 from public derived CSV files.

This script uses Eq. 5 real-case DSI values and the synthetic operating-region
table included in the repository. It does not use restricted raw coordinates.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "figures"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pd.read_csv(DATA / "synthetic_benchmark" / "DSI_OPERATING_REGIONS.csv")
    real = pd.read_csv(
        DATA
        / "real_case_public_derived"
        / "REAL_CASE_DSI_POSITION_IN_SYNTHETIC_BENCHMARK_CORRECTED.csv"
    )

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    xmax = max(20, real["median_dsi"].max() * 1.2)
    spans = [
        (0.4, 1.25, "ATTRIBUTION_UNRESOLVED"),
        (1.25, 2.0, "BOUNDARY_SENSITIVE"),
        (2.0, 4.0, "MODERATE_MARGIN_CONDITIONAL"),
        (4.0, xmax, "HIGH_MARGIN_STABLE"),
    ]
    for left, right, label in spans:
        ax.axvspan(left, right, alpha=0.14, label=label)
    colors = {"MZ-I": "#4878a8", "MZ-II": "#c0392b"}
    for _, row in real.iterrows():
        ax.scatter(row["median_dsi"], 0.02, s=90, color=colors.get(row["zone"], "black"), zorder=5)
        ax.text(row["median_dsi"], 0.07, f"{row['zone']} DSI={row['median_dsi']}", ha="center")
    ax.set_xscale("log")
    ax.set_xlabel("Domain-Separation Index (Eq. 5)")
    ax.set_yticks([])
    ax.set_title("Real-case DSI on synthetic operating regions")
    ax.grid(axis="x", color="#e8e8e8")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), fontsize=7, frameon=False, loc="upper left", ncol=1)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.88, bottom=0.18)
    fig.savefig(OUT / "Fig_B5_real_case_on_synthetic_DSI_curve_CORRECTED_reproduced.png", dpi=300)
    fig.savefig(OUT / "Fig_B5_real_case_on_synthetic_DSI_curve_CORRECTED_reproduced.pdf")


if __name__ == "__main__":
    main()
