# Major-revision public inputs

This directory contains repository-local inputs needed by the major-revision
reproduction scripts.

## Public-derived geometry inputs

- `all_section_constraints_fault_points_public_derived.csv` contains the 195
  section-constraint points used by Phase 5.
- `fault_trace_profiles_public_derived.csv` contains the F2 and F7 trace-top
  profiles used by the trace-constrained model and depthwise envelopes.

The same fixed XY translation was applied to every point and trace vertex.
Elevation (`Z`), section membership, fault labels, and all non-coordinate
attributes were retained. The published X/Y values are therefore local
translated metre coordinates, not valid EPSG:4536 positions. The translation
offset is intentionally not distributed because it would reconstruct the
survey coordinates.

This translation preserves relative distances, fitted residuals, per-section
LOSO errors, model admission, and across-model lateral spread, up to floating-
point roundoff. The source shapefiles, DEM, and original EPSG:4536 point table
are not required by the public Phase 5 script.

## Diagnostic input

`canonical_distance_metrics_pointwise.csv` is the coordinate-free frozen
distance-metric input used by `run_phase1_phase2.py` for the real-case metric
comparison. It contains no X/Y coordinate columns.
