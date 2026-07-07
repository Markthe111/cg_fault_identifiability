"""Domain-Separation Index calculations."""
import numpy as np
import pandas as pd

def compute_dsi(points, associated_fault, other_faults):
    """Compute DSI as nearest non-associated distance divided by associated-fault distance."""
    out = points.copy()
    control = out[f"d_{associated_fault}"].astype(float).clip(lower=1e-9)
    other = out[[f"d_{f}" for f in other_faults]].astype(float).min(axis=1)
    out["dsi"] = other / control
    return out

def summarize_dsi_by_zone(points_with_dsi):
    """Return robust DSI summaries by zone."""
    return points_with_dsi.groupby("zone")["dsi"].agg(["count", "median", lambda s: s.quantile(0.1), lambda s: s.quantile(0.25)]).reset_index()

def classify_dsi_regime(dsi, thresholds=None):
    """Classify DSI into benchmark-calibrated operating regions."""
    thresholds = thresholds or {"high": 4.0, "moderate": 2.0, "boundary": 1.25}
    x = np.asarray(dsi, dtype=float)
    labels = np.full(x.shape, "ATTRIBUTION_UNRESOLVED", dtype=object)
    labels[x >= thresholds["high"]] = "HIGH_MARGIN_STABLE"
    labels[(x >= thresholds["moderate"]) & (x < thresholds["high"])] = "MODERATE_MARGIN_CONDITIONAL"
    labels[(x >= thresholds["boundary"]) & (x < thresholds["moderate"])] = "BOUNDARY_SENSITIVE"
    return labels
