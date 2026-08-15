# Input schema

This page describes the public input contracts used by the example and
major-revision workflows. Column names are case-sensitive. Unless a table says
otherwise, distances and coordinates are expressed in metres.

## Synthetic point inputs

`example_data/synthetic_demo/synthetic_ore_points.csv` contains one row per
synthetic point:

| Column | Meaning |
|---|---|
| `point_id` | Synthetic, unique point identifier. |
| `zone` | Synthetic domain or mineralized-zone label. |
| `expected_fault` | Fault expected by the scenario design. |
| `x`, `y`, `z` | Synthetic Cartesian coordinates. |

`synthetic_sections.csv` supplies section labels, and
`synthetic_config.json` records `fault_separation`, `n_per_zone`, and `seed`.
These files are entirely synthetic and do not encode a mine location.

## Fault inputs

The minimal demonstration supports two public fault representations:

- `synthetic_faults.csv`: `fault, x`, for simple parallel synthetic faults.
- `synthetic_fault_points.csv`: `fault, section, x, y, z`, for sampled fault
  geometry grouped by section.

The attribution functions expect stable fault labels that can be matched to
`expected_fault`. A sampled surface must contain enough non-degenerate points
for the selected fitting or distance operation. Coordinate units must be
consistent across points and faults.

## Diagnostic inputs

The 18,000-record in-distribution benchmark is frozen at
`data/major_revision/diagnostic/DSI_BENCHMARK_RAW_RESULTS.csv`. Its columns fall
into these groups:

- scenario design: `fault_separation`, `domain_distance`,
  `perturbation_level`, `n_competing_faults`, and `domain_noise`;
- replication: `replicate`, `seed`, and `n_mc`;
- DSI summaries: `median_dsi`, `p10_dsi`, `p25_dsi`, and the
  `percent_dsi_le_*` fields;
- attribution and robustness outcomes: `attribution_accuracy_baseline`,
  `monte_carlo_reversal_probability`,
  `point_level_reattribution_probability`, `random_fault_p_value`, and
  `real_competing_fault_rank`;
- accounting: `runtime_s`.

The coordinate-free canonical diagnostic table is
`data/major_revision/diagnostic/canonical_distance_metrics_pointwise.csv`. It
uses a long format with:

`point_id, section_id, zone, point_class, is_primary, is_nearby, metric,
distance_type, associated_fault, competing_fault, value, units`.

Each `metric` row is interpreted only with its declared candidate set and
`distance_type`. The plan-view Eq. 5 DSI and supplementary 3-D quantities are
not interchangeable.

## OOD inputs

`data/major_revision/ood/OOD_dataset_summary.csv` is the frozen independent
3,000-scenario synthetic OOD set. It contains:

- identity and replication: `scenario_id`, `seed`, `n_points`, `n_mc`, and
  `generator`;
- geometry controls: `n_competing_faults`, `minimum_base_spacing`,
  `curvature_rms`, `amplitude_median`, `dip_base_control`,
  `dip_y_variation_control`, `dip_depth_variation_control`,
  `ore_scatter_scale`, and `perturbation_scale`;
- diagnostics: `DSI_2D`, `DSI_3D`, `distance_diff_2D`,
  `distance_diff_3D`, `normalized_margin_2D`, and `normalized_margin_3D`;
- outcomes: `baseline_accuracy`, `reversal_probability`,
  `binary_reversal_label`, and `point_level_reattribution_probability`.

Calibration is trained on the ID benchmark and applied to these rows without
OOD refitting, recalibration, or threshold retuning.

## LOSO translated local-coordinate inputs

Phase 5 reads two public-derived tables under
`data/major_revision/loso_coordinate_shifted/`:

- `all_section_constraints_fault_points_public_derived.csv`:
  `X, Y, Z, section_name, source_layer, feature_type, confidence, use_as_hard,
  note, dist_F2_m, dist_F7_m, nearest`;
- `fault_trace_profiles_public_derived.csv`: `fault, Y, X, Z`.

`X` and `Y` are arbitrary translated local coordinates shared consistently by
the point and trace tables. `Z`, relative geometry, distances, section labels,
and fault labels are retained for the public predictive comparison. The mine
survey origin, source-coordinate mapping, private GIS, and raw exploration
coordinates are not public inputs.

The LOSO script expects 132 points assigned to F2 across 8 sections and 63
points assigned to F7 across 3 sections. Those Phase 5 counts are separate from
the canonical Eq. 5 primary point set.

## Canonical 48/72 set

`data/real_case_public_derived/REAL_CASE_DSI_PRIMARY_PUBLIC.csv` is the frozen
canonical primary set:

- 48 MZ-I points;
- 72 MZ-II points.

Its public fields are:

`public_point_id, section_public_id, zone, expected_associated_fault,
nearest_competing_fault, d_plan_associated_m, d_plan_competing_m, dsi,
dsi_lt_1, dsi_gt_2, local_competitor_flag`.

For each row, Eq. 5 is exactly
`d_plan_competing_m / d_plan_associated_m`, where the numerator is the distance
to the nearest competing named fault and the denominator is the distance to the
expected associated fault.

## Confidentiality boundary

Public identifiers are anonymized or synthetic. The repository does not supply
restricted logs, proprietary layers, original mine survey coordinates, or a
mapping from local translated coordinates to a mine location. Do not attempt to
combine the public derived tables with private or external location data to
recover restricted information.

## Interpretation boundary

Schema validity does not establish geological truth. The input tables support
the documented attribution, diagnostic, OOD, and LOSO questions within their
declared fault and model candidate sets. Eq. 5 DSI is screening-only; LOSO
admission is predictive within the tested surface families; OOD performance
does not justify unrestricted transferability.
