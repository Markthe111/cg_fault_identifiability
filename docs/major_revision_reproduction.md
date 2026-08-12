# Major-revision reproduction

Run from the repository root with seed `20260806`:

```bash
python scripts/major_revision/run_diagnostic_validation.py --seed 20260806 --output-root outputs/major_revision
python scripts/major_revision/run_ood_validation.py --seed 20260806 --output-root outputs/major_revision
python scripts/major_revision/run_loso_geometry_comparison.py --seed 20260806 --output-root outputs/major_revision
```

Or run all three via `python scripts/major_revision/reproduce_major_revision.py --seed 20260806 --output-root outputs/major_revision`.

Phase 1/2 reads the 18,000-scenario public synthetic benchmark and coordinate-free real-case distance metrics. Phase 3 reads the frozen independent 3,000-scenario OOD table, fits calibration only on ID data, and applies it without OOD refitting, recalibration, or retuning. Phase 5 reads only the translated public local-coordinate point and trace tables; neither translation origin nor private GIS is distributed. Its manuscript-facing depthwise output is an eight-row coordinate-free summary of median and maximum lateral divergence by fault and depth.
