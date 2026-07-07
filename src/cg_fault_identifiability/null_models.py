"""Null-model utilities for synthetic fault specificity tests."""
import numpy as np
import pandas as pd

def generate_random_faults_like_real_fault(real_fault, bbox, n, seed):
    """Generate random vertical fault traces with similar scale inside a bounding box."""
    rng = np.random.default_rng(seed)
    xmin, xmax = bbox
    return pd.DataFrame({"fault_id": [f"R{i:03d}" for i in range(n)], "x": rng.uniform(xmin, xmax, n)})

def random_fault_specificity_test(zone_points, real_fault, random_faults):
    """Compare mean distance to the real fault against random fault traces."""
    real = np.abs(zone_points["x"] - real_fault["x"]).mean()
    rand = [np.abs(zone_points["x"] - r.x).mean() for r in random_faults.itertuples()]
    return {"real_mean_distance": real, "p_value": float((np.sum(np.array(rand) <= real) + 1) / (len(rand) + 1))}

def real_fault_rank_specificity(zone_points, real_faults):
    """Rank named faults by mean distance to a zone point set."""
    rows = []
    for name, x in real_faults.items():
        rows.append({"fault": name, "mean_distance": float(np.abs(zone_points["x"] - x).mean())})
    return pd.DataFrame(rows).sort_values("mean_distance").reset_index(drop=True)
