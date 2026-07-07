"""Geometry helpers for synthetic fault-domain identifiability workflows."""
from __future__ import annotations
import numpy as np
import pandas as pd

def make_fault_surface_from_trace(trace_points, dip_deg, dip_direction_deg, depth_extent, depth_step):
    """Extrude trace points down dip to create a simple planar fault surface point cloud."""
    pts = np.asarray(trace_points, dtype=float)
    dip = np.deg2rad(dip_deg)
    az = np.deg2rad(dip_direction_deg)
    depths = np.arange(0, depth_extent + depth_step, depth_step)
    out = []
    for x, y, z in pts:
        for d in depths:
            horiz = d / max(np.tan(dip), 1e-6)
            out.append([x + horiz * np.sin(az), y + horiz * np.cos(az), z - d])
    return pd.DataFrame(out, columns=["x", "y", "z"])

def fit_plane_zxy(points):
    """Fit z = a*x + b*y + c by ordinary least squares."""
    p = np.asarray(points[["x", "y", "z"]] if hasattr(points, "__getitem__") else points, dtype=float)
    A = np.c_[p[:, 0], p[:, 1], np.ones(len(p))]
    a, b, c = np.linalg.lstsq(A, p[:, 2], rcond=None)[0]
    return {"a": float(a), "b": float(b), "c": float(c)}

def predict_plane_zxy(points_xy, plane_params):
    """Predict z for xy coordinates from plane coefficients."""
    xy = np.asarray(points_xy, dtype=float)
    return plane_params["a"] * xy[:, 0] + plane_params["b"] * xy[:, 1] + plane_params["c"]

def distance_points_to_surface(points, surface_points):
    """Approximate point-to-surface distance by nearest surface point Euclidean distance."""
    p = np.asarray(points[["x", "y", "z"]] if hasattr(points, "__getitem__") else points, dtype=float)
    s = np.asarray(surface_points[["x", "y", "z"]] if hasattr(surface_points, "__getitem__") else surface_points, dtype=float)
    d2 = ((p[:, None, :] - s[None, :, :]) ** 2).sum(axis=2)
    return np.sqrt(d2.min(axis=1))
