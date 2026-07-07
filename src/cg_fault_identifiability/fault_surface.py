"""Fault-surface construction for Eq. 1.

This module keeps the manuscript-facing name used in the paper. The
implementation delegates to :mod:`cg_fault_identifiability.geometry`, which is
the original B1 reproducibility implementation.
"""

from __future__ import annotations

from .geometry import fit_plane_zxy, make_fault_surface_from_trace, predict_plane_zxy

__all__ = [
    "make_fault_surface_from_trace",
    "fit_plane_zxy",
    "predict_plane_zxy",
]
