# Major-revision frozen expected outputs

These files are frozen reference outputs for reviewer-side comparison. New
runs should be written under `outputs/major_revision/` or another directory
passed through `--output-root`; they should not overwrite this directory.

## Table naming

`tables/Table_4_diagnostic_performance.csv` is a byte-for-byte copy of
`outputs/Table_Y_diagnostic_performance.csv`. `Table_Y` was the internal
working name; `Table_4` is the manuscript name. Their content and values are
identical.

## Subdirectories

- `phase1/`: frozen reconstructed synthetic metric table required by Phase 3.
- `phase2/`: grouped held-out metrics, bootstrap intervals, calibration bins,
  and threshold diagnostics.
- `phase3/`: frozen OOD scenarios, predictions, diagnostic performance,
  calibration, thresholds, and ID-versus-OOD comparison.
- `phase5/`: frozen LOSO errors, family summary, admissible model set,
  and depthwise geometry spread.

The Phase 5 `depthwise_geometry_spread.csv` is a public-derived frozen table:
the absolute `Y_m` and model `x_*_m` columns received the same fixed XY
translation as the public inputs. Depth, elevation, `x_spread_m`, admissible
models, and all comparison statistics are unchanged.

## Commands from the repository root

```powershell
python scripts/major_revision/run_phase1_phase2.py --seed 20260806 --output-root outputs/major_revision
python scripts/major_revision/run_phase3_ood.py --seed 20260806 --output-root outputs/major_revision
python scripts/major_revision/run_phase5_geometry.py --seed 20260806 --output-root outputs/major_revision
```

Phase 5 is deterministic; its seed is accepted and recorded for a uniform CLI.
It reads only the two public-derived geometry CSV files and has no GeoPandas,
Rasterio, shapefile, or DEM dependency.
