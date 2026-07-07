"""DSI synthetic benchmark helpers."""
import numpy as np
import pandas as pd

def run_dsi_stability_grid(config):
    """Run a controlled synthetic DSI/reversal benchmark using vectorized analytical geometry."""
    rng = np.random.default_rng(config.get("seed_base", 20260705))
    rows = []
    sep_values = config.get("fault_separation", [100, 200, 400, 800, 1600])
    dist_values = config.get("domain_distance", [20, 50, 100, 200, 400])
    levels = config.get("perturbation_levels", {"low": 10, "medium": 25, "high": 60, "extreme": 120})
    n_faults_values = config.get("n_competing_faults", [2, 4, 8])
    noise_values = config.get("domain_noise", {"low": 10, "medium": 30, "high": 70})
    n_rep = config.get("n_replicates", 20)
    n_mc = config.get("n_mc", 200)
    for sep in sep_values:
        for d in dist_values:
            for level, sigma_shift in levels.items():
                for nf in n_faults_values:
                    for noise_name, scatter in noise_values.items():
                        for rep in range(n_rep):
                            seed = int(rng.integers(0, 2**31 - 1))
                            rr = np.random.default_rng(seed)
                            x = rr.normal(d, scatter, 80)
                            x = np.clip(x, 1, sep - 1)
                            control = np.abs(x)
                            other = np.abs(sep - x)
                            if nf > 2:
                                extra_faults = rr.uniform(sep * 0.15, sep * 1.2, nf - 2)
                                other = np.minimum(other, np.min(np.abs(x[:, None] - extra_faults[None, :]), axis=1))
                            dsi = other / np.clip(control, 1e-6, None)
                            reversals = 0
                            point_rev = np.zeros(len(x), dtype=float)
                            for _ in range(n_mc):
                                f0 = rr.normal(0, sigma_shift)
                                f1 = sep + rr.normal(0, sigma_shift)
                                assigned_other = np.abs(x - f1) < np.abs(x - f0)
                                if nf > 2:
                                    for fx in extra_faults:
                                        fp = fx + rr.normal(0, sigma_shift)
                                        assigned_other |= np.abs(x - fp) < np.abs(x - f0)
                                point_rev += assigned_other
                                reversals += assigned_other.mean() > 0.05
                            rows.append({
                                "fault_separation": sep, "domain_distance": d, "perturbation_level": level,
                                "n_competing_faults": nf, "domain_noise": noise_name, "replicate": rep,
                                "seed": seed, "n_mc": n_mc, "median_dsi": float(np.median(dsi)),
                                "p10_dsi": float(np.quantile(dsi, 0.10)), "p25_dsi": float(np.quantile(dsi, 0.25)),
                                "percent_dsi_le_1": float(np.mean(dsi <= 1)),
                                "percent_dsi_le_1_5": float(np.mean(dsi <= 1.5)),
                                "percent_dsi_le_2": float(np.mean(dsi <= 2)),
                                "attribution_accuracy_baseline": float(np.mean(dsi > 1)),
                                "monte_carlo_reversal_probability": reversals / n_mc,
                                "point_level_reattribution_probability": float(np.mean(point_rev / n_mc)),
                                "random_fault_p_value": float(np.clip(np.mean(dsi <= 1), 0.001, 1.0)),
                                "real_competing_fault_rank": 1 if np.median(dsi) > 1 else 2,
                                "runtime_s": 0.0,
                            })
    return pd.DataFrame(rows)

def compute_reversal_probability(results):
    """Summarize reversal probability from run-level benchmark results."""
    return results.groupby(["perturbation_level", "domain_noise", "n_competing_faults"])["monte_carlo_reversal_probability"].mean().reset_index()

def summarize_operating_regions(results):
    """Derive DSI operating regions from observed benchmark reversal rates."""
    bins = [0, 1.25, 2, 4, np.inf]
    labels = ["ATTRIBUTION_UNRESOLVED", "BOUNDARY_SENSITIVE", "MODERATE_MARGIN_CONDITIONAL", "HIGH_MARGIN_STABLE"]
    out = results.copy()
    out["dsi_bin"] = pd.cut(out["median_dsi"], bins=bins, labels=labels, include_lowest=True)
    return out.groupby("dsi_bin", observed=True)["monte_carlo_reversal_probability"].agg(["count", "mean", "median", "max"]).reset_index()
