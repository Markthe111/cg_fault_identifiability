"""Validation utilities."""
import numpy as np
import pandas as pd
from .geometry import fit_plane_zxy, predict_plane_zxy

def leave_one_section_out_plane_validation(fault_points, section_col):
    """Leave each section out, fit a plane, and report held-out absolute z errors."""
    rows = []
    for sec in sorted(fault_points[section_col].unique()):
        train = fault_points[fault_points[section_col] != sec]
        test = fault_points[fault_points[section_col] == sec]
        if len(train) < 3 or len(test) == 0:
            continue
        params = fit_plane_zxy(train[["x", "y", "z"]])
        pred = predict_plane_zxy(test[["x", "y"]].to_numpy(), params)
        for err in np.abs(test["z"].to_numpy() - pred):
            rows.append({"section": sec, "abs_error": float(err)})
    return pd.DataFrame(rows)

def summarize_loso_errors(loso_results):
    """Summarize LOSO absolute errors."""
    s = loso_results["abs_error"]
    return {"median_abs_error": float(s.median()), "p90_abs_error": float(s.quantile(0.9)), "n": int(len(s))}
