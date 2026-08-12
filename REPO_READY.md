# Repository readiness report

## Local repository path

Local working directory used for preparation: `cg_fault_identifiability`.

## What was organized

The repository was assembled from the existing B1 reproducibility package in
the author's local project workspace.

Additional manuscript-facing corrected DSI data were copied from the author's
local DSI-definition unification output.

## Structure

```text
cg_fault_identifiability/
  README.md
  LICENSE
  CITATION.cff
  environment.yml
  requirements.txt
  pyproject.toml
  SCRIPT_INVENTORY.csv
  docs/
  src/cg_fault_identifiability/
  scripts/
  data/
  demo/
  figures/
  reports/
  tests/
```

## Formula-to-code map

- Eq. 1 fault-surface extrusion: `src/cg_fault_identifiability/fault_surface.py`, `geometry.py`
- Eq. 2 nearest-fault/Voronoi attribution: `src/cg_fault_identifiability/attribution.py`
- 500-model perturbation logic: `src/cg_fault_identifiability/monte_carlo.py`, `perturbation.py`
- Eq. 3 null models: `src/cg_fault_identifiability/null_models.py`
- Eq. 4 REML variance components: `src/cg_fault_identifiability/variance.py`, `reml.py`
- Eq. 5 DSI: `src/cg_fault_identifiability/dsi.py`
- 18,000-record synthetic benchmark: `src/cg_fault_identifiability/benchmark.py`, `scripts/run_dsi_benchmark.py`
- Grouped diagnostic validation: `scripts/major_revision/run_diagnostic_validation.py`
- Independent OOD validation without OOD retuning: `scripts/major_revision/run_ood_validation.py`
- LOSO alternative-geometry comparison: `scripts/major_revision/run_loso_geometry_comparison.py`
- Major-revision master entry point: `scripts/major_revision/reproduce_major_revision.py`

## Public data included

- Synthetic benchmark raw and summary tables under `data/synthetic_benchmark/`
- Corrected Eq. 5 real-case DSI overlay under `data/real_case_public_derived/`
- Supplementary pairwise 3-D separation ratio table, explicitly not used as DSI
- Figure-support fault parameters and derived domain-assignment point table
- Frozen 3,000-scenario synthetic OOD table
- Translated local-coordinate LOSO inputs with no distributed translation origin
- Frozen major-revision expected outputs and numerical tests

Restricted original drillhole/trench logs, proprietary GIS layers, and raw mine
data are excluded.

## GitHub upload steps

1. Create an empty GitHub repository named `cg_fault_identifiability`.
2. Confirm that `CITATION.cff` and `README.md` use:
   `https://github.com/Markthe111/cg_fault_identifiability`.
3. Commit the repository:
   ```bash
   git add .
   git commit -m "Prepare cg_fault_identifiability reproducibility package"
   ```
4. Add the remote and push:
   ```bash
   git branch -M main
   git remote add origin https://github.com/Markthe111/cg_fault_identifiability.git
   git push -u origin main
   ```

## Zenodo DOI steps

1. Log in to Zenodo with the GitHub-linked account.
2. Open Zenodo > GitHub integration.
3. Enable archiving for `cg_fault_identifiability`.
4. Create the reviewed GitHub release for version `v0.2.0`.
5. Zenodo will archive that release and mint a DOI.
6. Add the DOI badge to `README.md` and update `CITATION.cff` with the DOI.
7. For manuscript submission, cite the Zenodo DOI, not only the GitHub URL.

## Missing or limited items

- A public standalone real-data 500-model Monte Carlo script independent of
  restricted project paths was not found. Public fixed-seed logic is included in
  `monte_carlo.py`.
- A public script reproducing every manuscript figure from only unrestricted
  data was not found. Corrected Fig. B5 and synthetic benchmark reproduction are
  included.
- Raw exploration data are intentionally excluded and should remain out of the
  public repository.

## Current readiness status

`PUBLIC_RELEASE_V2_INTEGRATED_LOCAL_ONLY`

Manual steps remaining:

- Review the local `submission-release-v2` commit and release-candidate tag.
- Push to GitHub only after author approval.
- Create the GitHub release and publish a new Zenodo version.

