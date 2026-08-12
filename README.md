# cg_fault_identifiability

Open and reproducible Python implementation for claim-specific identifiability auditing in sparse 3-D structural models.

## Workflow

1. **Fault-domain attribution audit** — finite fault surfaces, nearest-surface attribution, Monte Carlo robustness, random-fault null, mapped-fault ranking, and plan-view DSI screening.
2. **Diagnostic validation** — an 18,000-scenario synthetic benchmark, grouped held-out validation, distance-difference margins, logistic calibration, and 3,000 independent OOD scenarios with no OOD refitting, recalibration, or retuning.
3. **Deep-geometry identifiability** — REML residual diagnosis, LOSO comparison of alternative geometries, a 1-SE predictive admissible set, depthwise divergence, and coordinate-shifted public derived tables.

The manuscript Eq. 5 plan-view DSI is

`distance to nearest competing named fault / distance to expected associated fault`.

It is not a generic nearest-neighbor ratio. The frozen real-case primary point set contains 48 MZ-I points and 72 MZ-II points.

## Reproduce manuscript-facing open results

Install Python 3.10 or newer and the package dependencies:

```bash
python -m pip install -e ".[test]"
python scripts/reproduce_all_synthetic.py
python scripts/major_revision/reproduce_major_revision.py --seed 20260806 --output-root outputs/major_revision
```

The major-revision phases may also be run separately:

```bash
python scripts/major_revision/run_diagnostic_validation.py --seed 20260806 --output-root outputs/major_revision
python scripts/major_revision/run_ood_validation.py --seed 20260806 --output-root outputs/major_revision
python scripts/major_revision/run_loso_geometry_comparison.py --seed 20260806 --output-root outputs/major_revision
```

Expected manuscript-facing outputs are under `outputs_expected/major_revision/` and are checked by the test suite.

## Data scope and confidentiality

Synthetic benchmark and OOD data are public. The real-case DSI table contains anonymized identifiers and derived plan distances only. Raw mine coordinates are not included. LOSO tables use translated arbitrary local coordinates; the translation origin and its crosswalk are intentionally not distributed. Relative geometry required by the analysis is preserved.

## Interpretation boundary

The workflow audits whether evidence supports a stated fault-domain or deep-geometry claim within declared candidate sets. A locally closer plan-view competitor is not, by itself, a 3-D association or ore-control claim. F2 deep geometry is non-unique within the tested model families; F7 has only three sections and does not support strong model discrimination.

## License and citation

Code is released under the MIT License. See `CITATION.cff` for citation metadata.
