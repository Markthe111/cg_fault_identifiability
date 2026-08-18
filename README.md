# cg_fault_identifiability

Open and reproducible Python implementation for claim-specific identifiability auditing in sparse 3-D structural models.

## Associated manuscript

**Auditing claim-specific identifiability in sparse 3-D structural models: robust fault-domain attribution despite non-unique deep geometry**

Authors: Fuyuan Xie, Yuhua Chen, Yongguo Yang, and Jinhui Luo.

Corresponding author: Yuhua Chen  
School of Resources and Geosciences, China University of Mining and Technology,  
Xuzhou 221116, China  
E-mail: chenyuhua@cumt.edu.cn

## Archived manuscript release

The formal manuscript reproducibility release is **v0.2.0**.

- GitHub release: https://github.com/Markthe111/cg_fault_identifiability/releases/tag/v0.2.0
- Zenodo DOI: https://doi.org/10.5281/zenodo.21898348
- Python: >= 3.10
- License: MIT

The scientific code, canonical inputs, expected outputs, seeds, and validation design in `v0.2.0` are frozen. Later commits on `main` contain documentation clarifications only and do not alter the archived scientific results.

## Quick verification

Clone the repository and check out the archived manuscript release:

```bash
git clone https://github.com/Markthe111/cg_fault_identifiability.git
cd cg_fault_identifiability
git checkout v0.2.0
```

Install the package and test dependencies:

```bash
python -m pip install -e ".[test]"
```

Run the public test suite:

```bash
pytest -q
```

Run the complete manuscript-facing public reproduction:

```bash
python scripts/major_revision/reproduce_major_revision.py --seed 20260806 --output-root outputs/major_revision
```

A successful major-revision reproduction prints:

`MAJOR_REVISION_REPRODUCTION_PASS`

The frozen scientific release is `v0.2.0`. Expanded user and reproduction documentation is maintained on `main`.

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
```

Run the public test suite:

```bash
pytest -q
```

Run the synthetic demonstration and benchmark:

```bash
python scripts/reproduce_all_synthetic.py
```

Run the manuscript-facing grouped validation, OOD validation, and LOSO geometry comparison:

```bash
python scripts/major_revision/reproduce_major_revision.py --seed 20260806 --output-root outputs/major_revision
```

The major-revision phases may also be run separately:

```bash
python scripts/major_revision/run_diagnostic_validation.py --seed 20260806 --output-root outputs/major_revision
python scripts/major_revision/run_ood_validation.py --seed 20260806 --output-root outputs/major_revision
python scripts/major_revision/run_loso_geometry_comparison.py --seed 20260806 --output-root outputs/major_revision
```

Expected manuscript-facing outputs are under `outputs_expected/major_revision/` and are checked by the test suite.

## Documentation

- [User guide](docs/USER_GUIDE.md)
- [Minimal reproduction tutorial](docs/TUTORIAL.md)
- [Input schema](docs/input_schema.md)
- [Major-revision reproduction](docs/major_revision_reproduction.md)
- [Method notes](docs/method_notes.md)
- [Reproducibility notes](docs/reproducibility_notes.md)

## Data scope and confidentiality

Synthetic benchmark and OOD data are public. Real-case public tables contain anonymized derived distances or privacy-safe geometry in an arbitrary translated local coordinate frame. Raw mine coordinates, original section interpretations, proprietary GIS layers, and other restricted exploration source data are not distributed. Access to restricted source data is subject to permission from the data owner.

The translation origin and its crosswalk are intentionally not distributed. Relative geometry required by the public analyses is preserved.

## Interpretation boundary

The workflow audits whether evidence supports a stated fault-domain or deep-geometry claim within declared candidate sets.

Eq. 5 DSI is a plan-view screening diagnostic and is not a full 3-D association rule or a universal geological threshold. A locally closer plan-view competitor is not, by itself, evidence of 3-D association, ore control, or causality.

F2 deep geometry is non-unique within the tested candidate model families. F7 has only three sections and therefore does not support strong deep-geometry model discrimination.

Grouped held-out validation, independent OOD validation, and LOSO comparison address different validation questions and should not be conflated.

## License and citation

Code is released under the MIT License.

Formal archived release:

**Xie, F., Chen, Y., Yang, Y., and Luo, J. `cg_fault_identifiability: claim-specific fault-domain identifiability diagnostics`, v0.2.0. Zenodo.**

DOI: https://doi.org/10.5281/zenodo.21898348

Machine-readable citation metadata are provided in `CITATION.cff`.
