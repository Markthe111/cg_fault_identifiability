"""Nearest-fault attribution utilities."""
import numpy as np
import pandas as pd
from .geometry import distance_points_to_surface

def assign_nearest_fault(points, fault_surfaces):
    """Assign each point to the nearest fault surface."""
    result = points.copy()
    distances = {}
    for name, surf in fault_surfaces.items():
        distances[name] = distance_points_to_surface(points[["x", "y", "z"]], surf[["x", "y", "z"]])
        result[f"d_{name}"] = distances[name]
    names = list(fault_surfaces)
    mat = np.vstack([distances[n] for n in names]).T
    result["assigned_fault"] = [names[i] for i in mat.argmin(axis=1)]
    result["nearest_distance"] = mat.min(axis=1)
    return result

def summarize_zone_attribution(assignments, zone_col):
    """Summarize assigned-fault proportions by zone."""
    return assignments.groupby([zone_col, "assigned_fault"]).size().reset_index(name="n")

def attribution_reversal_rate(mc_assignments, expected_fault_by_zone):
    """Compute the fraction of assignments not matching expected zone-fault mapping."""
    bad = 0
    total = 0
    for _, row in mc_assignments.iterrows():
        total += 1
        if row.get("assigned_fault") != expected_fault_by_zone.get(row.get("zone")):
            bad += 1
    return bad / total if total else float("nan")
