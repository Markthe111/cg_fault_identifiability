# Minimal reproduction tutorial

This tutorial starts from a clean clone and runs only public workflows. It does
not require restricted mine data. Commands are shown for a shell opened at the
parent directory where the repository should be cloned.

## 1. Clone the public repository

```bash
git clone https://github.com/Markthe111/cg_fault_identifiability.git
cd cg_fault_identifiability
git checkout v0.2.0
```

Checking out v0.2.0 reproduces the formally archived scientific version.
Documentation-only clarifications may also exist on `main`, but they do not
change the v0.2.0 archive.

## 2. Install the package

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

Conda users may instead run:

```bash
conda env create -f environment.yml
conda activate cg_fault_identifiability
```

## 3. Run the test suite

```bash
pytest -q
```

The tests check public schemas, the canonical 48 MZ-I / 72 MZ-II set, Eq. 5,
OOD no-retuning, privacy-safe LOSO inputs, and frozen expected numbers.

## 4. Reproduce the public synthetic examples

```bash
python scripts/reproduce_all_synthetic.py
```

This runs the synthetic demonstration and quick DSI benchmark using their
repository-defined fixed seeds. In a clean checkout, regenerated tracked
reference products should not introduce an unexplained diff:

```bash
git diff -- outputs_expected/synthetic_demo outputs_expected/dsi_benchmark
```

## 5. Run grouped diagnostic validation

Use one output root for the dependent major-revision phases:

```bash
python scripts/major_revision/run_diagnostic_validation.py \
  --seed 20260806 \
  --output-root outputs/tutorial_major_revision
```

This reconstructs ID metrics from the frozen 18,000-scenario benchmark and
runs grouped held-out validation.

## 6. Run independent OOD validation

```bash
python scripts/major_revision/run_ood_validation.py \
  --seed 20260806 \
  --output-root outputs/tutorial_major_revision
```

The command consumes the ID products from the preceding step and evaluates the
frozen 3,000-scenario OOD set without OOD refitting, recalibration, or retuning.

## 7. Run the LOSO geometry comparison

```bash
python scripts/major_revision/run_loso_geometry_comparison.py \
  --seed 20260806 \
  --output-root outputs/tutorial_major_revision
```

The LOSO workflow uses only the public translated local-coordinate point and
trace tables. It compares the declared candidate families and applies the
predictive best-plus-1-SE admissibility rule.

## 8. Run the master reproduction command

The master entry point runs the same three phases in order and writes the
top-level comparison products. It is safe to rerun into the same generated
output directory:

```bash
python scripts/major_revision/reproduce_major_revision.py \
  --seed 20260806 \
  --output-root outputs/tutorial_major_revision
```

A successful run prints `MAJOR_REVISION_REPRODUCTION_PASS`.

## 9. Compare with `outputs_expected`

Inspect representative frozen tables directly:

```bash
git diff --no-index -- \
  outputs_expected/major_revision/phase2/heldout_pooled_metrics.csv \
  outputs/tutorial_major_revision/phase2/heldout_pooled_metrics.csv

git diff --no-index -- \
  outputs_expected/major_revision/phase3/OOD_diagnostic_performance.csv \
  outputs/tutorial_major_revision/phase3/OOD_diagnostic_performance.csv

git diff --no-index -- \
  outputs_expected/major_revision/phase5/model_family_summary.csv \
  outputs/tutorial_major_revision/phase5/model_family_summary.csv
```

No diff output and exit status 0 indicate byte-identical files. Some
manuscript-facing checks are intentionally schema-aware or tolerance-based;
run the test suite again for the authoritative numerical comparison:

```bash
pytest -q
```

Keep generated work under `outputs/`. Do not overwrite or update
`outputs_expected/`, change seeds, tune on OOD outcomes, or reinterpret the
public translated coordinates as mine survey positions.

## Citation

The archived v0.2.0 release is available at
<https://doi.org/10.5281/zenodo.21898348> under the MIT License.
