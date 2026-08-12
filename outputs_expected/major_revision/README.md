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
- `phase5/`: frozen LOSO errors, family summary, and admissible model set.
- `depthwise_geometry_spread_expected.csv`: coordinate-free eight-row summary
  of median and maximum across-model lateral divergence by fault and depth.

No expected-output table contains along-strike sample positions or individual
model X coordinates. Those fields are unnecessary for reproducing the reported
depthwise divergence and are deliberately excluded from the public freeze.

## Commands from the repository root

```powershell
python scripts/major_revision/run_diagnostic_validation.py --seed 20260806 --output-root outputs/major_revision
python scripts/major_revision/run_ood_validation.py --seed 20260806 --output-root outputs/major_revision
python scripts/major_revision/run_loso_geometry_comparison.py --seed 20260806 --output-root outputs/major_revision
```

Alternatively, run all three in order with
`python scripts/major_revision/reproduce_major_revision.py --seed 20260806 --output-root outputs/major_revision`.

Phase 5 is deterministic; its seed is accepted and recorded for a uniform CLI.
It reads only the two public-derived geometry CSV files and has no GeoPandas,
Rasterio, shapefile, or DEM dependency.
