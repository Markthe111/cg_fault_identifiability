# Validation log

Date: 2026-07-07

## Checks performed

- `python -m compileall -q src scripts`: passed.
- `python scripts/reproduce_fig_b5_corrected.py`: passed and regenerated:
  - `figures/Fig_B5_real_case_on_synthetic_DSI_curve_CORRECTED_reproduced.png`
  - `figures/Fig_B5_real_case_on_synthetic_DSI_curve_CORRECTED_reproduced.pdf`

## Checks not completed

- `python -m pytest -q`: not run in the current base environment because
  `pytest` is not installed (`No module named pytest`).

To run tests in the release environment:

```bash
conda env create -f environment.yml
conda activate cg_fault_identifiability
pytest
```
