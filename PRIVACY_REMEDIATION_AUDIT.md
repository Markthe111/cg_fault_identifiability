# Public release v0.2.0 privacy-remediation audit

## Scope

The audit covered every CSV, JSON, Markdown, Python, YAML, TOML, and CFF file
under `data/major_revision/`, `outputs_expected/major_revision/`, and
`scripts/major_revision/`. It checked coordinate-like columns, numeric ranges,
local absolute paths, GIS/CRS origin metadata, credential patterns, the two
known confidential offset literals supplied in the remediation brief, and
pairwise combinations of public coordinate tables that could disclose a
constant translation.

## Finding

The earlier release candidate contained two depthwise tables with identical
rows: one in the public translated local frame and one at confidential survey
coordinate magnitude. Their row-wise differences disclosed a constant XY
translation. That candidate was never pushed.

The public LOSO input tables contain `X` and `Y` in an arbitrary translated
local metre frame. They are duplicated at two repository paths for backward
compatibility, but the copies are byte-identical. Their zero difference adds no
location information. No public table provides a second coordinate frame or a
crosswalk back to survey coordinates.

## Remediation

- Replaced `outputs_expected/major_revision/depthwise_geometry_spread_expected.csv`
  with an eight-row coordinate-free summary.
- Removed the frozen pointwise Phase 5 depthwise table from expected outputs.
- Retained only fault, depth, admitted-model count, median lateral divergence,
  and maximum lateral divergence in the manuscript-facing expected table.
- Changed the master reproduction entry point to publish the same
  coordinate-free summary at its top level.
- Added tests for local-coordinate range and the exact coordinate-free expected
  schema.
- Rebuilt the sole local release commit by amendment so the superseded candidate
  is not an ancestor of the final release branch.

## Reproduction impact

The diagnostic, OOD, LOSO, admissible-model, and depthwise-divergence formulas
are unchanged. Clean-room comparison now includes the median and maximum
divergence at four depths for both faults. It compares derived quantities only;
no along-strike location or individual predicted X coordinate is compared.

## Result

`PRIVACY_PASS`

`NO_RECOVERABLE_COORDINATE_ORIGIN`

