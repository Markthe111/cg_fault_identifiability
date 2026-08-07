from __future__ import annotations

import argparse
import hashlib
import json
import platform
from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "outputs" / "major_revision"
DEFAULT_SEED = 20260806
FAULTS = ["F2", "F7"]
MODELS = ["single_plane", "segmented_plane", "quadratic_surface", "trace_constrained_ruled"]
DEPTHS = [100.0, 200.0, 300.0, 400.0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run major-revision Phase 5 geometry comparison.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Recorded master seed; Phase 5 is deterministic.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Root directory receiving phase5/ outputs.",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def trace_arrays(fault: str, profiles: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    q = profiles[profiles["fault"].eq(fault)].sort_values("Y")
    if q.empty:
        raise RuntimeError(f"No public-derived trace profile for {fault}")
    return q["Y"].to_numpy(float), q["X"].to_numpy(float), q["Z"].to_numpy(float)


@dataclass
class SurfaceModel:
    family: str
    coef: np.ndarray
    y0: float
    ys: float
    z0: float
    zs: float
    knot: float = 0.0
    trace_y: np.ndarray | None = None
    trace_x: np.ndarray | None = None
    trace_z: np.ndarray | None = None

    def predict(self, y: np.ndarray, z: np.ndarray) -> np.ndarray:
        y = np.asarray(y, float); z = np.asarray(z, float)
        if self.family == "trace_constrained_ruled":
            tx = np.interp(y, self.trace_y, self.trace_x)
            tz = np.interp(y, self.trace_y, self.trace_z)
            return tx + self.coef[0] * (tz - z)
        yy = (y - self.y0) / self.ys
        zz = (z - self.z0) / self.zs
        if self.family == "single_plane":
            a = np.column_stack([np.ones(len(y)), yy, zz])
        elif self.family == "segmented_plane":
            a = np.column_stack([np.ones(len(y)), yy, zz, np.maximum(yy - self.knot, 0.0)])
        elif self.family == "quadratic_surface":
            a = np.column_stack([np.ones(len(y)), yy, zz, yy**2, yy * zz, zz**2])
        else:
            raise ValueError(self.family)
        return a @ self.coef


def fit_model(family: str, train: pd.DataFrame, trace: tuple[np.ndarray, np.ndarray, np.ndarray]) -> SurfaceModel:
    y = train["Y"].to_numpy(float); z = train["Z"].to_numpy(float); x = train["X"].to_numpy(float)
    ty, tx, tz = trace
    if family == "trace_constrained_ruled":
        trace_x = np.interp(y, ty, tx); trace_z = np.interp(y, ty, tz)
        depth = trace_z - z
        denom = float(depth @ depth)
        beta = 0.0 if denom == 0 else float(depth @ (x - trace_x) / denom)
        return SurfaceModel(family, np.asarray([beta]), 0, 1, 0, 1, trace_y=ty, trace_x=tx, trace_z=tz)
    y0, z0 = float(y.mean()), float(z.mean())
    ys, zs = max(float(y.std(ddof=0)), 1.0), max(float(z.std(ddof=0)), 1.0)
    yy, zz = (y - y0) / ys, (z - z0) / zs
    if family == "single_plane":
        a = np.column_stack([np.ones(len(y)), yy, zz]); penalty = np.zeros(3)
        knot = 0.0
    elif family == "segmented_plane":
        knot = float(np.median(yy))
        a = np.column_stack([np.ones(len(y)), yy, zz, np.maximum(yy - knot, 0.0)]); penalty = np.zeros(4)
    elif family == "quadratic_surface":
        knot = 0.0
        a = np.column_stack([np.ones(len(y)), yy, zz, yy**2, yy * zz, zz**2])
        # Fixed weak-curvature penalty, declared a priori; linear terms remain unpenalized.
        penalty = np.asarray([0.0, 0.0, 0.0, 1.0, 1.0, 1.0])
    else:
        raise ValueError(family)
    coef = np.linalg.solve(a.T @ a + np.diag(penalty), a.T @ x)
    return SurfaceModel(family, coef, y0, ys, z0, zs, knot=knot)


def error_metrics(obs: np.ndarray, pred: np.ndarray) -> tuple[float, float, float]:
    residual = np.asarray(pred) - np.asarray(obs)
    absr = np.abs(residual)
    return float(np.sqrt(np.mean(residual**2))), float(np.mean(absr)), float(np.median(absr))


def markdown_table(df: pd.DataFrame) -> list[str]:
    return ["```text", df.to_string(index=False), "```"]


def main(seed: int, output_root: Path) -> None:
    output_root = output_root.resolve()
    out = output_root / "phase5"
    input_path = REPO_ROOT / "data" / "major_revision" / "all_section_constraints_fault_points_public_derived.csv"
    trace_path = REPO_ROOT / "data" / "major_revision" / "fault_trace_profiles_public_derived.csv"
    out.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(input_path)
    trace_profiles = pd.read_csv(trace_path)
    required = {"X", "Y", "Z", "section_name", "nearest"}
    if not required.issubset(data.columns):
        raise RuntimeError(f"Missing columns: {sorted(required - set(data.columns))}")
    counts = data.groupby("nearest").size().to_dict()
    sections = data.groupby("nearest")["section_name"].nunique().to_dict()
    if counts != {"F2": 132, "F7": 63} or sections != {"F2": 8, "F7": 3}:
        raise RuntimeError(f"Unexpected input structure: counts={counts}, sections={sections}")

    fold_rows: list[dict] = []
    full_models: dict[tuple[str, str], SurfaceModel] = {}
    trace_meta: dict[str, dict] = {}
    with nullcontext(trace_profiles) as profiles:
        traces: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
        for fault in FAULTS:
            ty, tx, tz = trace_arrays(fault, profiles)
            traces[fault] = (ty, tx, tz)
            trace_meta[fault] = {
                "coordinate_frame": "PUBLIC_LOCAL_TRANSLATED_METRES",
                "n_unique_y": int(len(ty)),
                "y_min": float(ty.min()),
                "y_max": float(ty.max()),
            }

        for fault in FAULTS:
            subset = data[data["nearest"] == fault].copy()
            for family in MODELS:
                for heldout in sorted(subset["section_name"].unique()):
                    train = subset[subset["section_name"] != heldout]
                    test = subset[subset["section_name"] == heldout]
                    model = fit_model(family, train, traces[fault])
                    pred = model.predict(test["Y"].to_numpy(), test["Z"].to_numpy())
                    rmse, mae, mad = error_metrics(test["X"].to_numpy(), pred)
                    fold_rows.append(
                        {"fault": fault, "model_family": family, "heldout_section": heldout,
                         "n_train": len(train), "n_test": len(test), "predictive_RMSE_m": rmse,
                         "predictive_MAE_m": mae, "predictive_median_absolute_deviation_m": mad}
                    )
                full_models[(fault, family)] = fit_model(family, subset, traces[fault])

        loso = pd.DataFrame(fold_rows)
        summary_rows: list[dict] = []
        admissible_rows: list[dict] = []
        for fault in FAULTS:
            sub = data[data["nearest"] == fault]
            aggregates = []
            for family in MODELS:
                q = loso[(loso["fault"] == fault) & (loso["model_family"] == family)]
                model = full_models[(fault, family)]
                pred = model.predict(sub["Y"].to_numpy(), sub["Z"].to_numpy())
                train_rmse, train_mae, train_mad = error_metrics(sub["X"].to_numpy(), pred)
                aggregates.append(
                    {"fault": fault, "model_family": family, "n_points": len(sub), "n_sections": sub["section_name"].nunique(),
                     "mean_LOSO_RMSE_m": q["predictive_RMSE_m"].mean(),
                     "SE_LOSO_RMSE_m": q["predictive_RMSE_m"].std(ddof=1) / np.sqrt(len(q)),
                     "mean_LOSO_MAE_m": q["predictive_MAE_m"].mean(),
                     "mean_LOSO_median_abs_dev_m": q["predictive_median_absolute_deviation_m"].mean(),
                     "full_fit_RMSE_m": train_rmse, "full_fit_MAE_m": train_mae, "full_fit_median_abs_dev_m": train_mad,
                     "parameter_count": len(model.coef), "continuous_surface": True}
                )
            agg = pd.DataFrame(aggregates)
            best = agg.sort_values("mean_LOSO_RMSE_m").iloc[0]
            threshold = float(best["mean_LOSO_RMSE_m"] + best["SE_LOSO_RMSE_m"])
            agg["best_plus_1SE_threshold_m"] = threshold
            agg["admissible"] = (agg["mean_LOSO_RMSE_m"] <= threshold) & agg["continuous_surface"]
            agg["selection_rule"] = "mean_LOSO_RMSE <= best mean + SE(best); continuous surface"
            summary_rows.extend(agg.to_dict("records"))
            for row in agg.itertuples():
                admissible_rows.append(
                    {"fault": fault, "model_family": row.model_family, "admissible": bool(row.admissible),
                     "mean_LOSO_RMSE_m": row.mean_LOSO_RMSE_m, "threshold_m": threshold,
                     "delta_from_best_m": row.mean_LOSO_RMSE_m - float(best["mean_LOSO_RMSE_m"]),
                     "continuous_surface": True,
                     "F7_inference_limit": "3 sections; limited discrimination" if fault == "F7" else "not_applicable"}
                )

        family_summary = pd.DataFrame(summary_rows)
        admissible = pd.DataFrame(admissible_rows)

        spread_rows: list[dict] = []
        for fault in FAULTS:
            sub = data[data["nearest"] == fault]
            active = admissible[(admissible["fault"] == fault) & admissible["admissible"]]["model_family"].tolist()
            if not active:
                raise RuntimeError(f"No admissible model for {fault}")
            ygrid = np.linspace(sub["Y"].min(), sub["Y"].max(), 121)
            ty, tx, tz = traces[fault]
            top_z = np.interp(ygrid, ty, tz)
            for depth in DEPTHS:
                zgrid = top_z - depth
                predictions = {family: full_models[(fault, family)].predict(ygrid, zgrid) for family in active}
                stack = np.vstack(list(predictions.values()))
                for i, y in enumerate(ygrid):
                    row = {"fault": fault, "depth_below_trace_m": depth, "Y_m": y, "top_elevation_m": top_z[i],
                           "admissible_model_count": len(active), "admissible_models": ";".join(active),
                           "x_min_m": float(stack[:, i].min()), "x_median_m": float(np.median(stack[:, i])),
                           "x_max_m": float(stack[:, i].max()), "x_spread_m": float(np.ptp(stack[:, i]))}
                    for family in MODELS:
                        row[f"x_{family}_m"] = float(predictions[family][i]) if family in predictions else np.nan
                    spread_rows.append(row)

    loso.to_csv(out / "LOSO_predictive_errors.csv", index=False, encoding="utf-8-sig")
    family_summary.to_csv(out / "model_family_summary.csv", index=False, encoding="utf-8-sig")
    admissible.to_csv(out / "admissible_model_set.csv", index=False, encoding="utf-8-sig")
    spread = pd.DataFrame(spread_rows)
    spread.to_csv(out / "depthwise_geometry_spread.csv", index=False, encoding="utf-8-sig")

    plt.rcParams.update({"font.family": "Arial", "font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
    colors = {"single_plane": "#2E5A87", "segmented_plane": "#2E8B72", "quadratic_surface": "#6E5A86", "trace_constrained_ruled": "#B15A3C"}
    fig, axes = plt.subplots(1, 2, figsize=(7, 3.2), sharey=False)
    for ax, fault in zip(axes, FAULTS):
        q = family_summary[family_summary["fault"] == fault]
        x = np.arange(len(q))
        ax.errorbar(x, q["mean_LOSO_RMSE_m"], yerr=q["SE_LOSO_RMSE_m"], fmt="none", ecolor="#555555", capsize=3)
        for i, row in enumerate(q.itertuples()):
            ax.scatter(i, row.mean_LOSO_RMSE_m, color=colors[row.model_family], marker="o" if row.admissible else "x", s=35)
        ax.axhline(q["best_plus_1SE_threshold_m"].iloc[0], color="#9A9A9A", ls="--", lw=1)
        ax.set_xticks(x); ax.set_xticklabels([m.replace("_", "\n") for m in q["model_family"]], rotation=0)
        ax.set_title(f"{fault} ({int(q.n_sections.iloc[0])} sections)"); ax.set_ylabel("Mean LOSO RMSE (m)")
    fig.tight_layout(); fig.savefig(out / "FIG_model_family_comparison.png", dpi=300); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(7, 3.2), sharey=False)
    for ax, fault in zip(axes, FAULTS):
        q = loso[loso["fault"] == fault]
        for i, family in enumerate(MODELS):
            vals = q[q["model_family"] == family]["predictive_RMSE_m"].to_numpy()
            ax.scatter(np.full(len(vals), i), vals, color=colors[family], s=20, alpha=.75)
            ax.plot([i-.18, i+.18], [np.mean(vals)]*2, color="black", lw=1)
        ax.set_xticks(range(len(MODELS))); ax.set_xticklabels([m.replace("_", "\n") for m in MODELS])
        ax.set_title(f"{fault} held-out sections"); ax.set_ylabel("Held-out RMSE (m)")
    fig.tight_layout(); fig.savefig(out / "FIG_LOSO_error_comparison.png", dpi=300); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(7, 3.2), sharey=False)
    for ax, fault in zip(axes, FAULTS):
        q = spread[spread["fault"] == fault]
        stats = q.groupby("depth_below_trace_m")["x_spread_m"].agg(["median", "max"]).reset_index()
        ax.plot(stats["depth_below_trace_m"], stats["median"], "o-", color="#2E5A87", label="median along-strike spread")
        ax.plot(stats["depth_below_trace_m"], stats["max"], "s--", color="#B15A3C", label="maximum spread")
        ax.set(title=f"{fault} admissible envelope", xlabel="Depth below mapped trace (m)", ylabel="Across-model X spread (m)")
        ax.legend(frameon=False, fontsize=7)
    fig.tight_layout(); fig.savefig(out / "FIG_depthwise_spread_envelope.png", dpi=300); plt.close(fig)

    depth_summary = spread.groupby(["fault", "depth_below_trace_m"]).agg(
        admissible_model_count=("admissible_model_count", "first"), median_x_spread_m=("x_spread_m", "median"),
        maximum_x_spread_m=("x_spread_m", "max")).reset_index()
    f2_adm = admissible[(admissible.fault == "F2") & admissible.admissible]["model_family"].tolist()
    f7_adm = admissible[(admissible.fault == "F7") & admissible.admissible]["model_family"].tolist()
    report = [
        "# Admissible geometry ensemble",
        "",
        "## Data and method",
        "",
        f"Input `{input_path}` (SHA-256 `{sha256(input_path)}`): F2 n=132 across 8 sections; F7 n=63 across 3 sections. X/Y coordinates use a public local translated frame in metres; the same translation was applied to points and trace profiles.",
        "Four continuous surface families were compared by leave-one-section-out prediction: single plane, continuous segmented plane, weakly curved ridge-regularized quadratic surface, and trace-constrained ruled surface. The admissible threshold is the best mean LOSO RMSE plus the standard error of that best model across held-out sections. Training residuals do not determine admission.",
        "Depthwise envelopes are model extrapolations at 100/200/300/400 m below the DEM-sampled mapped trace; they describe between-model spread, not a geological confidence interval.",
        "",
        "## Predictive comparison",
        "",
        *markdown_table(family_summary[["fault", "model_family", "mean_LOSO_RMSE_m", "SE_LOSO_RMSE_m", "best_plus_1SE_threshold_m", "admissible"]]),
        "",
        f"F2 admissible models: {', '.join(f2_adm)}.",
        f"F7 admissible models: {', '.join(f7_adm)}. With only three sections, this comparison has limited power to discriminate geometry families.",
        "",
        "## Depthwise spread",
        "",
        *markdown_table(depth_summary),
        "",
        "## Claim boundary",
        "",
        "For F2, 'multiple near-equal predictive models' is supported only if more than one family passes the declared 1-SE rule; otherwise the data do not support that phrase under this rule. 'Bounded' refers only to the envelope of admitted tested families and depths, not all possible geological surfaces.",
        "For F7, the defensible statement is that three sections are insufficient to discriminate robustly among alternative deep geometries. A formal non-uniqueness magnitude should not be generalized beyond the tested families.",
    ]
    (out / "REPORT_ADMISSIBLE_GEOMETRY.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    provenance = {
        "status": "PHASE5_PASS", "input": str(input_path), "input_sha256": sha256(input_path),
        "trace_input": str(trace_path), "trace_input_sha256": sha256(trace_path),
        "input_counts": counts, "section_counts": sections, "coordinate_frame": "PUBLIC_LOCAL_TRANSLATED_METRES", "trace_metadata": trace_meta,
        "model_families": MODELS, "admissibility_rule": "mean_LOSO_RMSE <= best mean + SE(best), continuous surface",
        "depths_m": DEPTHS, "seed": seed, "python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
    }
    (out / "PHASE5_PROVENANCE.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print("PHASE5_PASS")
    print(family_summary[["fault", "model_family", "mean_LOSO_RMSE_m", "SE_LOSO_RMSE_m", "admissible"]].to_string(index=False))
    print("DEPTHWISE_SPREAD")
    print(depth_summary.to_string(index=False))


if __name__ == "__main__":
    args = parse_args()
    main(args.seed, args.output_root)
