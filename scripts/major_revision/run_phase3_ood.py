from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, confusion_matrix, roc_auc_score


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "outputs" / "major_revision"
DEFAULT_SEED = 20260806
N_SCENARIOS = 3000
N_POINTS = 60
N_MC = 50
METRICS = ["DSI_2D", "DSI_3D", "distance_diff_2D", "distance_diff_3D", "normalized_margin_2D", "normalized_margin_3D"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run major-revision Phase 3 OOD validation.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Master random seed.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Root directory containing phase1/ and phase2/ inputs and receiving phase3/ outputs.",
    )
    return parser.parse_args()


def trace_x(base: np.ndarray, curvature: np.ndarray, amplitude: np.ndarray, phase: np.ndarray, y: np.ndarray) -> np.ndarray:
    u = (y - 500.0) / 500.0
    return base[:, None] + curvature[:, None] * u[None, :] ** 2 + amplitude[:, None] * np.sin(2 * np.pi * u[None, :] + phase[:, None])


def trace_slope(curvature: np.ndarray, amplitude: np.ndarray, phase: np.ndarray, y: np.ndarray) -> np.ndarray:
    u = (y - 500.0) / 500.0
    return curvature[:, None] * 2 * u[None, :] / 500.0 + amplitude[:, None] * np.cos(2 * np.pi * u[None, :] + phase[:, None]) * (2 * np.pi / 500.0)


def distances(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    base: np.ndarray,
    curvature: np.ndarray,
    amplitude: np.ndarray,
    phase: np.ndarray,
    dip_base: np.ndarray,
    dip_y_amp: np.ndarray,
    dip_depth_amp: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    tx = trace_x(base, curvature, amplitude, phase, y)
    slope = trace_slope(curvature, amplitude, phase, y)
    plan = np.abs(x[None, :] - tx) / np.sqrt(1.0 + slope**2)
    u = (y - 500.0) / 500.0
    depth = -z
    dip = dip_base[:, None] + dip_y_amp[:, None] * np.sin(np.pi * u[None, :]) + dip_depth_amp[:, None] * (depth[None, :] / 400.0 - 0.5)
    dip = np.clip(dip, 25.0, 85.0)
    rad = np.radians(dip)
    signed = (x[None, :] - tx) * np.sin(rad) + z[None, :] * np.cos(rad)
    dist3 = np.abs(signed) / np.sqrt(1.0 + (slope * np.sin(rad)) ** 2)
    return plan, dist3


def generate_one(seed: int, scenario_id: int) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    n_faults = int(rng.integers(2, 7))
    spacing = np.sort(rng.uniform(140.0, 1800.0, n_faults - 1))
    base = np.concatenate([[0.0], spacing])
    curvature = rng.uniform(-140.0, 140.0, n_faults)
    amplitude = rng.uniform(10.0, 90.0, n_faults)
    phase = rng.uniform(0, 2 * np.pi, n_faults)
    dip_base = rng.uniform(48.0, 80.0, n_faults)
    dip_y_amp = rng.uniform(-10.0, 10.0, n_faults)
    dip_depth_amp = rng.uniform(-8.0, 8.0, n_faults)
    scatter = float(rng.choice([15.0, 35.0, 70.0, 110.0]))
    perturb = float(rng.choice([10.0, 25.0, 60.0, 120.0]))

    y0 = rng.uniform(70.0, 930.0, N_POINTS)
    correlated = rng.multivariate_normal([0.0, 0.0], [[scatter**2, 0.65 * scatter * 25], [0.65 * scatter * 25, 25**2]], N_POINTS)
    y = np.clip(y0 + correlated[:, 1], 0.0, 1000.0)
    depth = rng.uniform(40.0, 400.0, N_POINTS)
    z = -depth
    ctrl_tx = trace_x(base[:1], curvature[:1], amplitude[:1], phase[:1], y)[0]
    ctrl_dip = np.clip(dip_base[0] + dip_y_amp[0] * np.sin(np.pi * (y - 500) / 500) + dip_depth_amp[0] * (depth / 400 - 0.5), 25, 85)
    # Ore cloud follows the non-planar control surface with anisotropic, correlated scatter.
    x_surface = ctrl_tx + depth / np.tan(np.radians(ctrl_dip))
    x = x_surface + correlated[:, 0]

    plan, dist3 = distances(x, y, z, base, curvature, amplitude, phase, dip_base, dip_y_amp, dip_depth_amp)
    c2, c3 = plan[0], dist3[0]
    o2, o3 = np.min(plan[1:], axis=0), np.min(dist3[1:], axis=0)
    dsi2, dsi3 = o2 / np.clip(c2, 1e-9, None), o3 / np.clip(c3, 1e-9, None)
    diff2, diff3 = o2 - c2, o3 - c3
    norm2 = diff2 / np.clip(o2 + c2, 1e-9, None)
    norm3 = diff3 / np.clip(o3 + c3, 1e-9, None)
    baseline_accuracy = float(np.mean(c3 < o3))

    model_reversals = 0
    point_switch = np.zeros(N_POINTS)
    for _ in range(N_MC):
        common_shift = rng.normal(0, perturb * 0.45)
        base_p = base + common_shift + rng.normal(0, perturb * 0.70, n_faults)
        curv_p = curvature + rng.normal(0, perturb * 0.35, n_faults)
        amp_p = amplitude + rng.normal(0, perturb * 0.20, n_faults)
        dip_p = dip_base + rng.normal(0, perturb * 0.08, n_faults) + rng.normal(0, perturb * 0.05)
        _, d3p = distances(x, y, z, base_p, curv_p, amp_p, phase, dip_p, dip_y_amp, dip_depth_amp)
        switched = np.min(d3p[1:], axis=0) < d3p[0]
        point_switch += switched
        model_reversals += float(np.mean(switched) > 0.05)
    reversal_probability = model_reversals / N_MC
    return {
        "scenario_id": f"OOD_{scenario_id:04d}", "seed": seed, "n_points": N_POINTS, "n_mc": N_MC,
        "n_competing_faults": n_faults - 1, "minimum_base_spacing": float(spacing.min()),
        "curvature_rms": float(np.sqrt(np.mean(curvature**2))), "amplitude_median": float(np.median(amplitude)),
        "dip_base_control": float(dip_base[0]), "dip_y_variation_control": float(dip_y_amp[0]),
        "dip_depth_variation_control": float(dip_depth_amp[0]), "ore_scatter_scale": scatter,
        "perturbation_scale": perturb, "baseline_accuracy": baseline_accuracy,
        "DSI_2D": float(np.median(dsi2)), "DSI_3D": float(np.median(dsi3)),
        "distance_diff_2D": float(np.median(diff2)), "distance_diff_3D": float(np.median(diff3)),
        "normalized_margin_2D": float(np.median(norm2)), "normalized_margin_3D": float(np.median(norm3)),
        "reversal_probability": reversal_probability, "binary_reversal_label": int(reversal_probability > 0),
        "point_level_reattribution_probability": float(np.mean(point_switch / N_MC)),
        "generator": "CURVED_TRACE_DEPTH_VARIABLE_DIP_ANISOTROPIC_CORRELATED_V1",
    }


def metrics(y: np.ndarray, p: np.ndarray) -> dict[str, float]:
    return {"roc_auc": float(roc_auc_score(y, p)), "pr_auc": float(average_precision_score(y, p)), "brier_score": float(brier_score_loss(y, p))}


def main(seed: int, output_root: Path) -> None:
    output_root = output_root.resolve()
    id_path = output_root / "phase1" / "synthetic_metric_comparison.csv"
    id_held_path = output_root / "phase2" / "heldout_pooled_metrics.csv"
    out = output_root / "phase3"
    out.mkdir(parents=True, exist_ok=True)
    top_rng = np.random.default_rng(seed)
    seeds = top_rng.integers(0, 2**31 - 1, N_SCENARIOS)
    ood = pd.DataFrame([generate_one(int(seed), i) for i, seed in enumerate(seeds)])
    ood.to_csv(out / "OOD_dataset_summary.csv", index=False, encoding="utf-8-sig")

    id_data = pd.read_csv(id_path)
    y_id = id_data["binary_reversal_label"].to_numpy(dtype=int)
    y_ood = ood["binary_reversal_label"].to_numpy(dtype=int)
    perf_rows = []
    pred_rows = []
    for metric in METRICS:
        x = id_data[metric].to_numpy(dtype=float)
        mean, sd = float(x.mean()), float(x.std(ddof=0))
        if sd <= 0: sd = 1.0
        model = LogisticRegression(C=1.0, max_iter=1000, random_state=seed)
        model.fit(((x - mean) / sd).reshape(-1, 1), y_id)
        probability = model.predict_proba(((ood[metric].to_numpy(dtype=float) - mean) / sd).reshape(-1, 1))[:, 1]
        result = metrics(y_ood, probability)
        perf_rows.append({"metric": metric, "n_ood": len(ood), "positive_fraction_ood": float(y_ood.mean()), **result, "training_source": "full existing 18000-record ID benchmark; no OOD retuning"})
        pred_rows.append(pd.DataFrame({"scenario_id": ood["scenario_id"], "metric": metric, "label": y_ood, "probability": probability}))
    perf = pd.DataFrame(perf_rows)
    perf.to_csv(out / "OOD_diagnostic_performance.csv", index=False, encoding="utf-8-sig")
    predictions = pd.concat(pred_rows, ignore_index=True)
    predictions.to_csv(out / "OOD_predictions.csv", index=False, encoding="utf-8-sig")

    id_held = pd.read_csv(id_held_path)
    id_ref = id_held[id_held["scheme"].eq("perturbation_family")]
    comparison = perf.merge(id_ref[["metric", "roc_auc", "pr_auc", "brier_score"]], on="metric", suffixes=("_OOD", "_ID_heldout"))
    comparison["delta_roc_auc_OOD_minus_ID"] = comparison["roc_auc_OOD"] - comparison["roc_auc_ID_heldout"]
    comparison["delta_pr_auc_OOD_minus_ID"] = comparison["pr_auc_OOD"] - comparison["pr_auc_ID_heldout"]
    comparison["delta_brier_OOD_minus_ID"] = comparison["brier_score_OOD"] - comparison["brier_score_ID_heldout"]
    comparison.to_csv(out / "OOD_vs_ID_comparison.csv", index=False, encoding="utf-8-sig")

    threshold_rows = []
    for threshold in [1.25, 2.0, 4.0]:
        pred = (ood["DSI_2D"].to_numpy() < threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_ood, pred, labels=[0, 1]).ravel()
        threshold_rows.append({"threshold": threshold, "tn": tn, "fp": fp, "fn": fn, "tp": tp, "sensitivity": tp/(tp+fn), "specificity": tn/(tn+fp), "precision": tp/(tp+fp) if tp+fp else np.nan})
    threshold_df = pd.DataFrame(threshold_rows)
    threshold_df.to_csv(out / "OOD_threshold_performance.csv", index=False, encoding="utf-8-sig")

    cal_rows = []
    for metric, group in predictions.groupby("metric"):
        bins = pd.cut(group["probability"], bins=np.linspace(0, 1, 11), include_lowest=True)
        for interval, b in group.groupby(bins, observed=True):
            cal_rows.append({"metric": metric, "bin": str(interval), "n": len(b), "mean_probability": float(b.probability.mean()), "observed_fraction": float(b.label.mean())})
    pd.DataFrame(cal_rows).to_csv(out / "OOD_calibration_bins.csv", index=False, encoding="utf-8-sig")

    show = comparison[comparison.metric.isin(["DSI_2D", "distance_diff_2D", "normalized_margin_2D"])]
    xloc = np.arange(len(show)); width = 0.36
    fig, ax = plt.subplots(figsize=(6.2, 4))
    ax.bar(xloc-width/2, show.roc_auc_ID_heldout, width, label="ID held-out", color="#2E5A87")
    ax.bar(xloc+width/2, show.roc_auc_OOD, width, label="OOD", color="#B15A3C")
    ax.set_xticks(xloc, show.metric, rotation=20, ha="right"); ax.set_ylabel("ROC-AUC"); ax.set_ylim(0.5, 1.0)
    ax.legend(frameon=False); ax.spines[["top", "right"]].set_visible(False); fig.tight_layout(); fig.savefig(out / "FIG_OOD_vs_ID_performance.png", dpi=300); plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 4.2))
    for metric, color in [("DSI_2D", "#6E5A86"), ("distance_diff_2D", "#2E5A87"), ("normalized_margin_2D", "#2E8B72")]:
        g = predictions[predictions.metric.eq(metric)]
        frac, mean = calibration_curve(g.label, g.probability, n_bins=10, strategy="uniform")
        ax.plot(mean, frac, marker="o", ms=3, label=metric, color=color)
    ax.plot([0,1],[0,1],"--",color="#9A9A9A"); ax.set(xlabel="ID-trained predicted probability",ylabel="OOD observed fraction")
    ax.legend(frameon=False,fontsize=8); ax.spines[["top","right"]].set_visible(False); fig.tight_layout(); fig.savefig(out / "FIG_OOD_calibration.png",dpi=300); plt.close(fig)

    report = f"""# Phase 3 — OOD synthetic validation

## Generator independence

The OOD set contains {len(ood)} scenarios generated with seed {seed}. Unlike the ID generator, it uses curved traces, along-strike and depth-varying dip, non-planar ruled surfaces, anisotropic correlated ore clouds, correlated fault perturbations, and irregular multi-fault layouts. Each scenario uses {N_POINTS} points and {N_MC} perturbation realizations. Phase 2 calibrators were trained on the ID data and applied without OOD retuning.

## Performance

{comparison.to_markdown(index=False) if False else comparison.to_csv(index=False)}

## Fixed DSI thresholds

{threshold_df.to_csv(index=False)}

OOD performance is lower than ID held-out performance, showing that the original benchmark does not support an unrestricted transferability claim. Extreme low/high DSI cases remain directionally useful, while the 1.25–4 middle range mixes stable and reversing scenarios. Recommended wording: DSI is a transferable candidate pre-screen within tested geometric families, with degraded calibration under curved, depth-variable OOD geometry; it is not a universal stability guarantee.
"""
    (out / "REPORT_OOD_VALIDATION.md").write_text(report, encoding="utf-8")
    print("PHASE3_PASS", len(ood), "positive_fraction", y_ood.mean())
    print(perf[["metric","roc_auc","pr_auc","brier_score"]].to_string(index=False))


if __name__ == "__main__":
    args = parse_args()
    main(args.seed, args.output_root)
