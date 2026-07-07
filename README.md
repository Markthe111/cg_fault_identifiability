# cg_fault_identifiability

Reproducible Python code for the Computers & Geosciences manuscript on
claim-specific fault-domain identifiability.

The package implements the deterministic analysis components described in the
paper:

- Eq. 1: planar fault-surface extrusion from a mapped trace and attitude
- Eq. 2: nearest-fault / Voronoi-style ore-domain attribution
- 500 fixed-seed Monte Carlo perturbation logic for assignment stability
- Eq. 3: random-fault and real-fault-rank null models
- Eq. 4: leave-one-section-out residual summaries and REML variance components
- Eq. 5: Domain-Separation Index (DSI)
- Synthetic DSI benchmark tables and operating-region calibration

The repository is prepared for public release. It does not include restricted
raw drillhole, trench, mine-license, or proprietary GIS data. Public example and
derived tables are sufficient to rerun the open synthetic benchmark and inspect
the real-case DSI overlay used in the manuscript.

## Installation

```bash
conda env create -f environment.yml
conda activate cg_fault_identifiability
```

or:

```bash
python -m pip install -e ".[test]"
```

## Fixed random seeds

The reproducibility scripts use fixed seeds. The main synthetic benchmark uses
`seed_base = 20260705` unless overridden in a local configuration.

## Repository layout

```text
cg_fault_identifiability/
  README.md
  LICENSE
  CITATION.cff
  environment.yml
  requirements.txt
  pyproject.toml
  src/cg_fault_identifiability/
    fault_surface.py      # Eq. 1 public-facing wrapper
    geometry.py           # original geometry implementation
    attribution.py        # Eq. 2 nearest-fault attribution
    monte_carlo.py        # public-facing Monte Carlo wrapper
    perturbation.py       # original perturbation implementation
    null_models.py        # Eq. 3 null models
    variance.py           # Eq. 4 public-facing wrapper
    reml.py               # original REML implementation
    dsi.py                # Eq. 5 DSI
    benchmark.py          # synthetic DSI benchmark
    synthetic.py          # demo-data generation
    validation.py         # LOSO-style validation helpers
    plotting.py           # plotting helpers
  scripts/
    run_synthetic_demo.py
    run_dsi_benchmark.py
    reproduce_all_synthetic.py
  data/
    synthetic_benchmark/
    real_case_public_derived/
  demo/
  tests/
  reports/
```

## Reproduce the open synthetic results

Quick smoke run:

```bash
python scripts/run_synthetic_demo.py
python scripts/run_dsi_benchmark.py --quick
```

Full synthetic package:

```bash
python scripts/reproduce_all_synthetic.py
```

Expected outputs are written under `outputs_expected/` or script-local output
folders. The 18,000-record synthetic benchmark table is included in
`data/synthetic_benchmark/DSI_BENCHMARK_RAW_RESULTS.csv`.

## Reproduce manuscript-facing tables/figures from open data

The public repository includes:

- `data/synthetic_benchmark/DSI_BENCHMARK_RAW_RESULTS.csv`
- `data/synthetic_benchmark/DSI_BENCHMARK_SUMMARY_BY_BIN.csv`
- `data/synthetic_benchmark/DSI_OPERATING_REGIONS.csv`
- `data/real_case_public_derived/REAL_CASE_DSI_POSITION_IN_SYNTHETIC_BENCHMARK_CORRECTED.csv`
- `data/real_case_public_derived/REAL_CASE_PAIRWISE_3D_SEPARATION_RATIO_SUPPLEMENT.csv`
- `figures/Fig_B5_real_case_on_synthetic_DSI_curve_CORRECTED.*`

The corrected real-case DSI values follow Eq. 5: plan-distance ratio to the
nearest competing named fault divided by the associated-fault distance. The
pairwise 3-D F2-F7 distance ratio is retained only as a supplementary metric and
is not used as the manuscript DSI.

## Restricted source data

The real Sitaihaiquan drillhole/trench logs, raw ore-point coordinates, and
original mine GIS inputs are not included because of mineral-rights and project
data restrictions. Derived, manuscript-facing summary tables are included where
they can be released. Raw data are available on reasonable request subject to
permission from the data owners.

## Tests

```bash
pytest
```

The tests cover geometry extrusion, nearest-fault attribution, DSI
classification, and null-model helpers.

## Citation

See `CITATION.cff`. The repository URL is:
`https://github.com/Markthe111/cg_fault_identifiability`.

