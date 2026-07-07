"""Synthetic perturbation utilities."""
import numpy as np

def sample_fault_parameters(base_faults, n_models, seed, config):
    """Sample perturbed synthetic fault parameters from Gaussian controls."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_models):
        model = {}
        for name, fault in base_faults.items():
            model[name] = {
                "x": fault.get("x", 0.0) + rng.normal(0, config.get("trace_shift_sd", 20.0)),
                "dip": fault.get("dip", 65.0) + rng.normal(0, config.get("dip_sd", 4.0)),
                "azimuth": fault.get("azimuth", 0.0) + rng.normal(0, config.get("azimuth_sd", 8.0)),
            }
        out.append(model)
    return out

def run_monte_carlo_attribution(points, base_faults, config):
    """Run a simple one-dimensional synthetic Monte Carlo nearest-fault attribution."""
    rng = np.random.default_rng(config.get("seed", 1))
    n = config.get("n_models", 200)
    expected = points["expected_fault"].to_numpy()
    x = points["x"].to_numpy()
    reversals = np.zeros(len(points), dtype=float)
    for _ in range(n):
        shifts = {k: v.get("x", 0.0) + rng.normal(0, config.get("trace_shift_sd", 20.0)) for k, v in base_faults.items()}
        names = list(shifts)
        d = np.vstack([np.abs(x - shifts[name]) for name in names]).T
        assigned = np.array(names)[d.argmin(axis=1)]
        reversals += assigned != expected
    out = points.copy()
    out["reattribution_probability"] = reversals / n
    return out
