"""Matplotlib plotting helpers for synthetic benchmark outputs."""
import matplotlib.pyplot as plt

def plot_dsi_vs_reversal_probability(df):
    """Create a DSI-vs-reversal scatter plot."""
    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    ax.scatter(df["median_dsi"], df["monte_carlo_reversal_probability"], s=8, alpha=0.25, color="#4878a8")
    ax.set_xscale("log")
    ax.set_xlabel("Median DSI")
    ax.set_ylabel("Reversal probability")
    ax.grid(True, color="#e8e8e8")
    return fig

def plot_benchmark_heatmap(summary):
    """Create a compact operating-region heatmap."""
    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    piv = summary.pivot_table(index="domain_distance", columns="fault_separation", values="monte_carlo_reversal_probability", aggfunc="mean")
    im = ax.imshow(piv.values, origin="lower", aspect="auto", cmap="viridis_r", vmin=0, vmax=1)
    ax.set_xticks(range(len(piv.columns)), piv.columns)
    ax.set_yticks(range(len(piv.index)), piv.index)
    ax.set_xlabel("Fault separation (m)")
    ax.set_ylabel("Ore distance to associated fault (m)")
    fig.colorbar(im, ax=ax, label="Reversal probability")
    return fig

def plot_workflow_ablation_schema(ablation):
    """Create a module-by-claim ablation matrix."""
    import numpy as np
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    cols = [c for c in ablation.columns if c.startswith("can_")]
    mat = ablation[cols].astype(int).to_numpy()
    ax.imshow(mat, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(cols)), [c.replace("can_", "").replace("_", "\n") for c in cols], fontsize=7)
    ax.set_yticks(range(len(ablation)), ablation["variant"], fontsize=7)
    return fig

def plot_synthetic_case_geometry(points, faults):
    """Plot arbitrary-coordinate synthetic points and vertical fault traces."""
    fig, ax = plt.subplots(figsize=(5, 4))
    for zone, g in points.groupby("zone"):
        ax.scatter(g["x"], g["y"], s=12, alpha=0.6, label=zone)
    for _, f in faults.iterrows():
        ax.axvline(f["x"], color="0.25", lw=1)
        ax.text(f["x"], points["y"].max(), f["fault"], rotation=90, va="top", fontsize=8)
    ax.set_xlabel("Arbitrary x (m)")
    ax.set_ylabel("Arbitrary y (m)")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, color="#e8e8e8")
    return fig

def plot_case_result_summary(summary):
    """Plot a synthetic case summary bar chart."""
    fig, ax = plt.subplots(figsize=(4.8, 3.4))
    ax.bar(summary["metric"], summary["value"], color="#4878a8")
    ax.set_ylabel("Value")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(True, axis="y", color="#e8e8e8")
    return fig
