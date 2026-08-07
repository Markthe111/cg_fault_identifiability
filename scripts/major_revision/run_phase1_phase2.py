from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.calibration import calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "outputs" / "major_revision"
DEFAULT_SEED = 20260806
N_BOOTSTRAP = 500


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run major-revision Phase 1 and Phase 2 analyses.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Master random seed.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Root directory for phase1/ and phase2/ outputs.",
    )
    return parser.parse_args()


def md_table(frame: pd.DataFrame, digits: int = 5) -> str:
    clean = frame.copy()
    for c in clean.select_dtypes(include=["float"]).columns:
        clean[c] = clean[c].map(lambda x: "" if pd.isna(x) else f"{x:.{digits}f}")
    clean = clean.where(pd.notna(clean), "")
    headers = list(map(str, clean.columns))
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in clean.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(x).replace("|", "\\|") for x in row) + " |")
    return "\n".join(lines)


def reconstruct_synthetic_metrics(raw: pd.DataFrame) -> pd.DataFrame:
    level_sd = {"low": 10.0, "medium": 25.0, "high": 60.0, "extreme": 120.0}
    noise_sd = {"low": 10.0, "medium": 30.0, "high": 70.0}
    rows = []
    for row in raw.itertuples(index=False):
        rr = np.random.default_rng(int(row.seed))
        x = rr.normal(float(row.domain_distance), noise_sd[row.domain_noise], 80)
        x = np.clip(x, 1, float(row.fault_separation) - 1)
        control = np.abs(x)
        competitor = np.abs(float(row.fault_separation) - x)
        if int(row.n_competing_faults) > 2:
            extra = rr.uniform(float(row.fault_separation) * 0.15, float(row.fault_separation) * 1.2, int(row.n_competing_faults) - 2)
            competitor = np.minimum(competitor, np.min(np.abs(x[:, None] - extra[None, :]), axis=1))
        dsi = competitor / np.clip(control, 1e-9, None)
        diff = competitor - control
        norm = diff / np.clip(competitor + control, 1e-9, None)
        rows.append(
            {
                "DSI_2D": float(np.median(dsi)),
                "DSI_3D": float(np.median(dsi)),
                "distance_diff_2D": float(np.median(diff)),
                "distance_diff_3D": float(np.median(diff)),
                "normalized_margin_2D": float(np.median(norm)),
                "normalized_margin_3D": float(np.median(norm)),
                "associated_distance_median": float(np.median(control)),
                "competing_distance_median": float(np.median(competitor)),
                "geometry_relation": "IDENTICAL_BY_1D_PARALLEL_VERTICAL_CONSTRUCTION",
                "sigma_shift": level_sd[row.perturbation_level],
            }
        )
    metrics = pd.DataFrame(rows)
    out = pd.concat([raw.reset_index(drop=True), metrics], axis=1)
    out["binary_reversal_label"] = (out["monte_carlo_reversal_probability"] > 0).astype(int)
    out["scenario_id"] = [f"ID_{i:05d}" for i in range(len(out))]
    return out


def correlation_row(dataset: str, point_set: str, zone: str, x: pd.Series, y: pd.Series) -> dict[str, object]:
    mask = np.isfinite(x) & np.isfinite(y)
    xv, yv = x[mask], y[mask]
    sp = spearmanr(xv, yv)
    pe = pearsonr(xv, yv)
    return {
        "dataset": dataset,
        "point_set": point_set,
        "zone": zone,
        "n": len(xv),
        "x_metric": "DSI_2D",
        "y_metric": "DSI_3D",
        "spearman_rho": float(sp.statistic),
        "spearman_p": float(sp.pvalue),
        "pearson_r": float(pe.statistic),
        "pearson_p": float(pe.pvalue),
    }


def safe_auc(y: np.ndarray, score: np.ndarray) -> float:
    return float(roc_auc_score(y, score)) if np.unique(y).size == 2 else np.nan


def evaluate_predictions(y: np.ndarray, prob: np.ndarray) -> dict[str, float]:
    return {
        "roc_auc": safe_auc(y, prob),
        "pr_auc": float(average_precision_score(y, prob)),
        "brier_score": float(brier_score_loss(y, prob)),
    }


def main(seed: int, output_root: Path) -> None:
    output_root = output_root.resolve()
    p1 = output_root / "phase1"
    p2 = output_root / "phase2"
    syn_path = REPO_ROOT / "data" / "synthetic_benchmark" / "DSI_BENCHMARK_RAW_RESULTS.csv"
    canonical_metrics_path = REPO_ROOT / "data" / "major_revision" / "canonical_distance_metrics_pointwise.csv"
    p1.mkdir(parents=True, exist_ok=True)
    p2.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(syn_path)
    if len(raw) != 18000:
        raise RuntimeError(f"Expected 18,000 synthetic records, got {len(raw)}")
    syn = reconstruct_synthetic_metrics(raw)
    max_dsi_reconstruction_error = float((syn["DSI_2D"] - syn["median_dsi"]).abs().max())
    if max_dsi_reconstruction_error > 1e-10:
        raise RuntimeError(f"Synthetic metric reconstruction mismatch: {max_dsi_reconstruction_error}")
    syn.to_csv(p1 / "synthetic_metric_comparison.csv", index=False, encoding="utf-8-sig")

    long = pd.read_csv(canonical_metrics_path)
    real = long.pivot_table(
        index=["point_id", "section_id", "zone", "point_class", "is_primary", "is_nearby"],
        columns="metric",
        values="value",
    ).reset_index()
    real = real.rename(columns={"3D_pairwise_F2F7_separation_ratio": "DSI_3D", "DSI_2D_Eq5": "DSI_2D"})
    real["distance_diff_2D"] = real["plan_trace_nearest_competing_distance"] - real["plan_trace_associated_distance"]
    real["distance_diff_3D"] = real["3D_surface_competing_F2F7_distance"] - real["3D_surface_associated_distance"]
    real["normalized_margin_2D"] = real["distance_diff_2D"] / (real["plan_trace_nearest_competing_distance"] + real["plan_trace_associated_distance"])
    real["normalized_margin_3D"] = real["distance_diff_3D"] / (real["3D_surface_competing_F2F7_distance"] + real["3D_surface_associated_distance"])
    real["reversal_probability"] = np.where(real["is_primary"], 0.0, np.nan)
    real["candidate_set_2D"] = "F1-F10 named plan traces"
    real["candidate_set_3D"] = "F2/F7 preserved finite surfaces only"
    real.to_csv(p1 / "real_case_DSI_comparison.csv", index=False, encoding="utf-8-sig")

    corr_rows = [correlation_row("synthetic_ID", "ALL", "ALL", syn["DSI_2D"], syn["DSI_3D"])]
    for point_set, subset in [("PRIMARY", real[real["is_primary"]]), ("ALL_CANONICAL", real)]:
        for zone, group in subset.groupby("zone"):
            corr_rows.append(correlation_row("Sitaihaiquan", point_set, zone, group["DSI_2D"], group["DSI_3D"]))
    corr = pd.DataFrame(corr_rows)
    corr.to_csv(p1 / "metric_correlation_summary.csv", index=False, encoding="utf-8-sig")

    # Phase 1 figures.
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    sample = syn.sample(2500, random_state=seed)
    axes[0].scatter(sample["DSI_2D"], sample["DSI_3D"], s=6, alpha=0.25, color="#6E5A86")
    axes[0].set_xscale("log"); axes[0].set_yscale("log")
    axes[0].set_xlabel("Synthetic DSI 2D"); axes[0].set_ylabel("Synthetic DSI 3D")
    axes[0].set_title("Construction identity")
    for zone, color in [("MZ-I", "#2E5A87"), ("MZ-II", "#B15A3C")]:
        g = real[real["is_primary"] & real["zone"].eq(zone)]
        axes[1].scatter(g["DSI_2D"], g["DSI_3D"], s=18, alpha=0.7, label=zone, color=color)
    axes[1].set_xscale("log"); axes[1].set_yscale("log")
    axes[1].set_xlabel("Real Eq.5 plan DSI"); axes[1].set_ylabel("Real F2/F7 3D ratio")
    axes[1].legend(frameon=False); axes[1].set_title("Canonical primary points")
    for ax in axes: ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(p1 / "FIG_DSI2D_vs_DSI3D.png", dpi=300); plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
    for ax, metric, label in zip(axes, ["DSI_2D", "distance_diff_2D", "normalized_margin_2D"], ["DSI", "Distance difference", "Normalized margin"]):
        ax.scatter(syn[metric], syn["monte_carlo_reversal_probability"], s=3, alpha=0.08, color="#2E5A87")
        ax.set_xlabel(label); ax.set_ylabel("Reversal probability"); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(p1 / "FIG_metric_vs_reversal.png", dpi=300); plt.close(fig)

    report1 = f"""# Phase 1 — DSI 2D versus DSI 3D

## Inputs

- Canonical real-point distance metrics: `{canonical_metrics_path}`.
- Existing synthetic benchmark: `{syn_path}`, n={len(syn)}.
- Maximum independently reconstructed synthetic median-DSI difference: {max_dsi_reconstruction_error:.3g}.

## Result

{md_table(corr)}

The canonical primary real points show positive monotonic association between Eq.5 plan DSI and the legacy F2/F7 3D ratio: MZ-I rho={corr[(corr.dataset=='Sitaihaiquan') & (corr.point_set=='PRIMARY') & (corr.zone=='MZ-I')].spearman_rho.iloc[0]:.3f}; MZ-II rho={corr[(corr.dataset=='Sitaihaiquan') & (corr.point_set=='PRIMARY') & (corr.zone=='MZ-II')].spearman_rho.iloc[0]:.3f}. The relationship weakens sharply in the all-point sensitivity set.

The 18,000-record synthetic benchmark cannot independently validate 2D against 3D: it uses one-dimensional x coordinates and parallel vertical faults, making the two distances identical by construction. Also, real 2D DSI compares F1-F10, whereas stored 3D distances include only F2 and F7. Therefore Eq.5 plan DSI is supported as a low-cost pre-model screening descriptor, not as a validated numerical surrogate for full-network 3D stability.
"""
    (p1 / "REPORT_DSI2D_vs_DSI3D.md").write_text(report1, encoding="utf-8")

    # Phase 2 diagnostic validation.
    metrics = ["DSI_2D", "DSI_3D", "distance_diff_2D", "distance_diff_3D", "normalized_margin_2D", "normalized_margin_3D"]
    y = syn["binary_reversal_label"].to_numpy(dtype=int)
    diag_rows = []
    for metric in metrics:
        risk = -syn[metric].to_numpy(dtype=float)
        diag_rows.append({
            "metric": metric,
            "n": len(y),
            "positive_fraction": float(y.mean()),
            "roc_auc_rank_only": safe_auc(y, risk),
            "pr_auc_rank_only": float(average_precision_score(y, risk)),
            "note": "2D/3D pair is construction-identical in ID benchmark",
        })
    pd.DataFrame(diag_rows).to_csv(p2 / "diagnostic_metrics_summary.csv", index=False, encoding="utf-8-sig")

    schemes = {
        "fault_spacing_family": "fault_separation",
        "perturbation_family": "perturbation_level",
        "competing_fault_count_family": "n_competing_faults",
        "domain_scatter_family": "domain_noise",
    }
    held_rows = []
    prediction_frames = []
    for scheme, group_col in schemes.items():
        for metric in metrics:
            oof = np.full(len(syn), np.nan)
            for held_value in sorted(syn[group_col].unique(), key=str):
                test = syn[group_col].eq(held_value).to_numpy()
                train = ~test
                xtrain = syn.loc[train, metric].to_numpy(dtype=float)
                xtest = syn.loc[test, metric].to_numpy(dtype=float)
                mean, sd = float(xtrain.mean()), float(xtrain.std(ddof=0))
                if sd <= 0: sd = 1.0
                model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=seed)
                model.fit(((xtrain - mean) / sd).reshape(-1, 1), y[train])
                prob = model.predict_proba(((xtest - mean) / sd).reshape(-1, 1))[:, 1]
                oof[test] = prob
                result = evaluate_predictions(y[test], prob)
                held_rows.append({"scheme": scheme, "heldout_value": held_value, "metric": metric, "n_test": int(test.sum()), **result})
            prediction_frames.append(pd.DataFrame({"scenario_id": syn["scenario_id"], "scheme": scheme, "metric": metric, "label": y, "probability": oof}))
    held = pd.DataFrame(held_rows)
    held.to_csv(p2 / "heldout_performance_summary.csv", index=False, encoding="utf-8-sig")
    preds = pd.concat(prediction_frames, ignore_index=True)

    # Pooled held-out metrics and percentile bootstrap CIs.
    rng = np.random.default_rng(seed)
    boot_rows = []
    pooled_rows = []
    for (scheme, metric), group in preds.groupby(["scheme", "metric"]):
        yy = group["label"].to_numpy(dtype=int); pp = group["probability"].to_numpy(dtype=float)
        point = evaluate_predictions(yy, pp)
        pooled_rows.append({"scheme": scheme, "metric": metric, "n": len(group), **point})
        draws = {k: [] for k in point}
        accepted = 0
        while accepted < N_BOOTSTRAP:
            idx = rng.integers(0, len(group), len(group))
            if np.unique(yy[idx]).size < 2: continue
            vals = evaluate_predictions(yy[idx], pp[idx])
            for key, value in vals.items(): draws[key].append(value)
            accepted += 1
        for key in point:
            boot_rows.append({
                "scheme": scheme, "metric": metric, "statistic": key, "point_estimate": point[key],
                "ci95_low": float(np.quantile(draws[key], 0.025)), "ci95_high": float(np.quantile(draws[key], 0.975)),
                "n_bootstrap": N_BOOTSTRAP, "seed": seed,
            })
    pooled = pd.DataFrame(pooled_rows)
    pooled.to_csv(p2 / "heldout_pooled_metrics.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(boot_rows).to_csv(p2 / "bootstrap_CI_summary.csv", index=False, encoding="utf-8-sig")

    cal_rows = []
    for (scheme, metric), group in preds.groupby(["scheme", "metric"]):
        bins = pd.cut(group["probability"], bins=np.linspace(0, 1, 11), include_lowest=True)
        for interval, b in group.groupby(bins, observed=True):
            cal_rows.append({
                "scheme": scheme, "metric": metric, "probability_bin": str(interval), "n": len(b),
                "mean_predicted_probability": float(b["probability"].mean()), "observed_reversal_fraction": float(b["label"].mean()),
            })
    cal = pd.DataFrame(cal_rows)
    cal.to_csv(p2 / "calibration_bins.csv", index=False, encoding="utf-8-sig")

    threshold_rows = []
    dsi = syn["DSI_2D"].to_numpy(dtype=float)
    for threshold in [1.25, 2.0, 4.0]:
        pred = (dsi < threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
        threshold_rows.append({
            "metric": "DSI_2D", "threshold": threshold, "rule": "predict reversal if DSI < threshold",
            "tn": tn, "fp": fp, "fn": fn, "tp": tp,
            "sensitivity": tp / (tp + fn), "specificity": tn / (tn + fp),
            "precision": tp / (tp + fp) if tp + fp else np.nan,
            "balanced_accuracy": balanced_accuracy_score(y, pred),
        })
    thresholds = pd.DataFrame(threshold_rows)
    thresholds.to_csv(p2 / "threshold_confusion_summary.csv", index=False, encoding="utf-8-sig")

    # Diagnostic figures use perturbation-family held-out probabilities; 3D duplicates omitted visually.
    plot_preds = preds[preds["scheme"].eq("perturbation_family")]
    colors = {"DSI_2D": "#6E5A86", "distance_diff_2D": "#2E5A87", "normalized_margin_2D": "#2E8B72"}
    fig, ax = plt.subplots(figsize=(5, 4.2))
    for metric, color in colors.items():
        g = plot_preds[plot_preds["metric"].eq(metric)]
        fpr, tpr, _ = roc_curve(g["label"], g["probability"])
        ax.plot(fpr, tpr, label=f"{metric} ({roc_auc_score(g['label'], g['probability']):.3f})", color=color)
    ax.plot([0, 1], [0, 1], "--", color="#9A9A9A"); ax.set(xlabel="False-positive rate", ylabel="True-positive rate")
    ax.legend(frameon=False, fontsize=8); ax.spines[["top", "right"]].set_visible(False); fig.tight_layout(); fig.savefig(p2 / "FIG_ROC_comparison.png", dpi=300); plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 4.2))
    for metric, color in colors.items():
        g = plot_preds[plot_preds["metric"].eq(metric)]
        precision, recall, _ = precision_recall_curve(g["label"], g["probability"])
        ax.plot(recall, precision, label=f"{metric} ({average_precision_score(g['label'], g['probability']):.3f})", color=color)
    ax.set(xlabel="Recall", ylabel="Precision"); ax.legend(frameon=False, fontsize=8); ax.spines[["top", "right"]].set_visible(False); fig.tight_layout(); fig.savefig(p2 / "FIG_PR_comparison.png", dpi=300); plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 4.2))
    for metric, color in colors.items():
        g = plot_preds[plot_preds["metric"].eq(metric)]
        frac, mean = calibration_curve(g["label"], g["probability"], n_bins=10, strategy="uniform")
        ax.plot(mean, frac, marker="o", ms=3, label=metric, color=color)
    ax.plot([0, 1], [0, 1], "--", color="#9A9A9A"); ax.set(xlabel="Predicted probability", ylabel="Observed fraction")
    ax.legend(frameon=False, fontsize=8); ax.spines[["top", "right"]].set_visible(False); fig.tight_layout(); fig.savefig(p2 / "FIG_calibration.png", dpi=300); plt.close(fig)

    best = pooled.sort_values(["scheme", "roc_auc"], ascending=[True, False]).groupby("scheme").head(1)
    report2 = f"""# Phase 2 — DSI diagnostic validation

## Label and validation

Binary reversal is `monte_carlo_reversal_probability > 0`; prevalence={y.mean():.4f} across n={len(y)} existing records. Univariate logistic calibration is fitted only on training scenario families and evaluated on held-out fault spacing, perturbation intensity, competing-fault count, or domain-scatter families. Bootstrap CIs use {N_BOOTSTRAP} percentile resamples with seed {seed}.

## Best pooled held-out metric by scheme

{md_table(best)}

## DSI thresholds

{md_table(thresholds)}

DSI, raw distance difference, and normalized margin all carry diagnostic signal. DSI does not demonstrate an independent gain over the simpler margins in every held-out family. DSI_2D and DSI_3D are exactly duplicated in this benchmark, as are their distance-difference and normalized-margin counterparts, so apparent 3D agreement is constructional. Threshold 1.25 has low sensitivity; threshold 4 captures more reversals at the cost of specificity. The 1.25–4 middle regime is conditional rather than a reliable hard decision region.

Conservative manuscript wording: DSI is a benchmark-supported pre-screening diagnostic whose extreme regimes are more interpretable than the intermediate regime; the present ID benchmark does not establish universal transferability or a full 3D surrogate.
"""
    (p2 / "REPORT_DSI_DIAGNOSTIC.md").write_text(report2, encoding="utf-8")
    print("PHASE1_PASS", len(real), len(syn), max_dsi_reconstruction_error)
    print("PHASE2_PASS", "label_prevalence", y.mean())
    print("POOLED_BEST", best[["scheme", "metric", "roc_auc", "pr_auc", "brier_score"]].to_dict(orient="records"))


if __name__ == "__main__":
    args = parse_args()
    main(args.seed, args.output_root)
