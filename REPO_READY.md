# Public release status

## Archived release

`cg_fault_identifiability` is publicly available on GitHub. The formal
manuscript reproducibility archive is **v0.2.0**:

- GitHub repository: <https://github.com/Markthe111/cg_fault_identifiability>
- GitHub release: <https://github.com/Markthe111/cg_fault_identifiability/releases/tag/v0.2.0>
- Zenodo DOI: <https://doi.org/10.5281/zenodo.21898348>
- License: MIT

The v0.2.0 scientific results, canonical inputs, expected outputs, definitions,
seeds, and validation design are frozen. Documentation-only commits made to
`main` after that release improve navigation and third-party instructions; they
do not alter the archived v0.2.0 scientific record.

## Repository structure

```text
cg_fault_identifiability/
  README.md
  LICENSE
  CITATION.cff
  environment.yml
  requirements.txt
  pyproject.toml
  docs/
  src/cg_fault_identifiability/
  scripts/
  data/
  example_data/
  outputs_expected/
  tests/
```

## Formula-to-code map

- Eq. 1 fault-surface extrusion: `src/cg_fault_identifiability/fault_surface.py`
  and `geometry.py`
- Eq. 2 nearest-fault/Voronoi attribution:
  `src/cg_fault_identifiability/attribution.py`
- 500-model perturbation logic: `src/cg_fault_identifiability/monte_carlo.py`
  and `perturbation.py`
- Eq. 3 null models: `src/cg_fault_identifiability/null_models.py`
- Eq. 4 REML variance components: `src/cg_fault_identifiability/variance.py`
  and `reml.py`
- Eq. 5 plan-view DSI: `src/cg_fault_identifiability/dsi.py`
- 18,000-record synthetic benchmark: `src/cg_fault_identifiability/benchmark.py`
  and `scripts/run_dsi_benchmark.py`
- Grouped diagnostic validation:
  `scripts/major_revision/run_diagnostic_validation.py`
- Independent OOD validation without OOD retuning:
  `scripts/major_revision/run_ood_validation.py`
- LOSO alternative-geometry comparison:
  `scripts/major_revision/run_loso_geometry_comparison.py`
- Major-revision master entry point:
  `scripts/major_revision/reproduce_major_revision.py`

## Public data boundary

The public repository includes synthetic inputs and outputs, coordinate-free
diagnostic metrics, anonymized real-case derived distance summaries, and
privacy-safe LOSO geometry inputs in an arbitrary translated local coordinate
frame. The canonical real-case primary set is fixed at 48 MZ-I points and 72
MZ-II points.

The public material is sufficient to run the documented synthetic, grouped
diagnostic, OOD, and LOSO workflows and to compare their products with the
frozen expected outputs.

## Restricted data boundary

Restricted drillhole and trench logs, original section digitization, mine-site
survey coordinates, proprietary GIS layers, and the information needed to map
the public local coordinate frame back to a mine location are not distributed.
No privacy-sensitive recovery is required or supported by the public workflow.

## Interpretation boundary

The repository supports claim-specific identifiability auditing within the
declared candidate sets. Eq. 5 DSI is a plan-view screening diagnostic, not a
full 3-D association rule or a universal geological law. Grouped held-out,
independent OOD, and LOSO results answer different validation questions and
must not be conflated. Deep-geometry conclusions are limited to the tested
candidate families and available sections.

## Release maintenance policy

- v0.2.0 remains the formal archived scientific release.
- The v0.2.0 tag and GitHub Release are not moved or rebuilt.
- Zenodo DOI `10.5281/zenodo.21898348` remains the archive citation.
- No later documentation-only `main` commit is part of v0.2.0 unless a reader
  explicitly checks out that later commit instead of the archived tag.
- A documentation clarification does not create a new scientific release or a
  new Zenodo archive.
