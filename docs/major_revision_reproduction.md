# Major-revision reproduction

Run all commands from the repository root with Python 3.10 or newer. Install
the declared dependencies first, for example with
`python -m pip install -r requirements.txt`.

## Commands

The master seed for every phase is `20260806`.

```powershell
python scripts/major_revision/run_phase1_phase2.py --seed 20260806 --output-root outputs/major_revision
python scripts/major_revision/run_phase3_ood.py --seed 20260806 --output-root outputs/major_revision
python scripts/major_revision/run_phase5_geometry.py --seed 20260806 --output-root outputs/major_revision
```

The commands must be run in this order because Phase 3 reads the Phase 1 and
Phase 2 files produced under the same `--output-root`.

## Inputs and expected outputs

| Phase | Repository inputs | Generated directory | Frozen comparison directory |
|---|---|---|---|
| 1/2 | `data/synthetic_benchmark/DSI_BENCHMARK_RAW_RESULTS.csv`; `data/major_revision/canonical_distance_metrics_pointwise.csv` | `outputs/major_revision/phase1/`; `outputs/major_revision/phase2/` | `outputs_expected/major_revision/phase1/`; `outputs_expected/major_revision/phase2/` |
| 3 | Generated `phase1/synthetic_metric_comparison.csv`; generated `phase2/heldout_pooled_metrics.csv` | `outputs/major_revision/phase3/` | `outputs_expected/major_revision/phase3/` |
| 5 | `data/major_revision/all_section_constraints_fault_points_public_derived.csv`; `data/major_revision/fault_trace_profiles_public_derived.csv` | `outputs/major_revision/phase5/` | `outputs_expected/major_revision/phase5/` |

The manuscript diagnostic table is frozen at
`outputs_expected/major_revision/tables/Table_4_diagnostic_performance.csv`.
It is content-identical to the internal working table named `Table_Y`; the
ignored internal file is not required for reproduction.

## Phase 5 coordinate handling

The two Phase 5 inputs are public-derived tables. The same fixed XY
translation was applied to the 195 section-constraint points and the F2/F7
trace profiles. Elevation, membership, labels, relative geometry, LOSO
residuals, per-section RMSE, admissible-model decisions, and across-model
lateral spreads are preserved up to floating-point roundoff. Their X/Y values
are local translated metre coordinates and are not valid EPSG:4536 survey
positions.

The public Phase 5 script reads only these CSV inputs. It does not require the
private source point table, DEM, shapefiles, GeoPandas, or Rasterio.

In the frozen Phase 5 `depthwise_geometry_spread.csv`, absolute `Y_m` and
model `x_*_m` columns use the same public translation. Depth, elevation,
`x_spread_m`, model admission, and comparison statistics are unchanged.
