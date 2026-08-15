# User guide

## Purpose

`cg_fault_identifiability` provides public, reproducible tools for auditing
claim-specific fault-domain and geometry identifiability. It covers synthetic
fault attribution, grouped diagnostic validation, independent synthetic OOD
evaluation, and leave-one-section-out comparison of declared surface families.
The software supports screening and predictive diagnostics; it does not replace
geological interpretation.

## Installation

Python 3.10 or newer is required. From the repository root, create an isolated
environment and install the package with its test dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

Alternatively, use the pinned Conda environment:

```bash
conda env create -f environment.yml
conda activate cg_fault_identifiability
```

Confirm the installation without generating manuscript-facing results:

```bash
pytest -q
```

## Repository structure

| Path | Role |
|---|---|
| `src/cg_fault_identifiability/` | Package implementation. |
| `scripts/` | Synthetic examples and benchmark entry points. |
| `scripts/major_revision/` | Grouped, OOD, LOSO, and master reproduction commands. |
| `example_data/` | Fully synthetic demonstration inputs. |
| `data/` | Public synthetic or privacy-safe derived inputs. |
| `outputs_expected/` | Frozen v0.2.0 reference products; treat as read-only. |
| `tests/` | Schema, method, privacy-boundary, and frozen-result checks. |
| `docs/` | User, method, schema, and reproduction documentation. |

## Attribution workflow

Run the synthetic demonstration and quick DSI benchmark together:

```bash
python scripts/reproduce_all_synthetic.py
```

The underlying entry points can also be run separately:

```bash
python scripts/run_synthetic_demo.py
python scripts/run_dsi_benchmark.py --quick
```

The demonstration constructs synthetic points and faults, assigns points to
candidate fault domains, and reports DSI screening quantities. Eq. 5 uses the
nearest competing named fault over the expected associated fault; it is not a
generic neighbour-order ratio.

## Grouped diagnostic validation

Run Phase 1 and Phase 2 into a generated-output directory:

```bash
python scripts/major_revision/run_diagnostic_validation.py \
  --seed 20260806 \
  --output-root outputs/major_revision
```

This reads the frozen 18,000-record ID benchmark and coordinate-free canonical
distance metrics. Grouped held-out folds isolate fault-spacing, perturbation,
competing-fault-count, and domain-scatter families. Outputs are written under
`outputs/major_revision/phase1/` and `phase2/`.

## OOD validation

Run the grouped diagnostic phase first because OOD evaluation uses its ID
products, then run:

```bash
python scripts/major_revision/run_ood_validation.py \
  --seed 20260806 \
  --output-root outputs/major_revision
```

The frozen 3,000-scenario OOD set is evaluated with ID-trained calibration.
There is no OOD refitting, recalibration, threshold selection, or retuning.
Products are written under `outputs/major_revision/phase3/`.

## LOSO workflow

Run the public-derived geometry comparison with:

```bash
python scripts/major_revision/run_loso_geometry_comparison.py \
  --seed 20260806 \
  --output-root outputs/major_revision
```

The workflow holds out each section, compares the declared continuous surface
families, applies the best-plus-1-SE predictive admissibility rule, and
summarizes depthwise divergence among admitted models. It reads only the public
translated local-coordinate point and trace tables.

## Complete major-revision reproduction

Run the three phases in their required order and create the documented
top-level comparison files:

```bash
python scripts/major_revision/reproduce_major_revision.py \
  --seed 20260806 \
  --output-root outputs/major_revision
```

This command reproduces the public major-revision workflow; it does not recover
or require restricted mine data.

## Expected outputs

Generated results belong under `outputs/`, not `outputs_expected/`. The main
frozen comparisons include:

- grouped metrics and bootstrap/calibration products in `phase2/`;
- OOD metrics, predictions, and ID-versus-OOD comparisons in `phase3/`;
- LOSO errors, family summaries, and admissible sets in `phase5/`;
- coordinate-free top-level diagnostic, OOD, LOSO, and depthwise summaries.

Use the test suite for schema-aware and numerical comparison with v0.2.0:

```bash
pytest -q
```

For byte-level inspection of a selected table, use `git diff --no-index` on the
matching path under `outputs_expected/major_revision/` and the generated
`outputs/major_revision/` tree. See [TUTORIAL.md](TUTORIAL.md) for examples.

## Confidentiality

Synthetic data are public. Real-case public tables contain anonymized derived
distances or privacy-safe geometry in an arbitrary translated local coordinate
frame. Restricted exploration logs, proprietary GIS, original mine survey
coordinates, and the information needed to locate that local frame are not
distributed. Do not attempt privacy-sensitive recovery or join the derived
tables to restricted location data.

## Interpretation boundaries

- Identifiability is claim- and candidate-set-specific.
- Eq. 5 DSI is plan-view screening only, not a full 3-D association rule.
- A negative distance-difference margin identifies a locally closer competitor;
  it does not establish ore control or causality.
- Grouped ID and independent OOD validation answer different questions.
- The LOSO admissible set is predictive within tested surface families and is
  not a posterior or confidence interval over all possible geology.
- F7 has three sections, which limits deep-geometry discrimination.

## Citation

The formal archived release is v0.2.0 under the MIT License. Cite:

> Xie, F., Chen, Y., Yang, Y., and Luo, J. *cg_fault_identifiability:
> claim-specific fault-domain identifiability diagnostics*, v0.2.0. Zenodo.
> <https://doi.org/10.5281/zenodo.21898348>

Machine-readable citation metadata are in `CITATION.cff`.
