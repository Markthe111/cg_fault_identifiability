# Data included in this repository

This directory contains only open, derived, or synthetic data needed for
reproducible code review.

## Included

- `synthetic_benchmark/`: fixed-seed synthetic DSI benchmark outputs.
- `real_case_public_derived/`: manuscript-facing derived real-case summaries,
  including corrected Eq. 5 DSI values and figure-support fault/assignment
  tables.

## Excluded

Restricted raw drillhole logs, trench logs, original section digitization files,
mine-license GIS layers, and proprietary exploration data are not included.
Access to these restricted source data is subject to permission from the data owner.

## Provenance note

The real-case DSI overlay in this release uses Eq. 5 plan-distance DSI values:
MZ-I = 6.7 and MZ-II = 15.3. The older 23.4 / 48.0 values are retained only in
`REAL_CASE_PAIRWISE_3D_SEPARATION_RATIO_SUPPLEMENT.csv` and must not be cited as
DSI.

## Coordinate desensitization

Coordinates in `real_case_public_derived/` are local metric coordinates. A single translation offset was applied to all x/y coordinates to protect the mine-site location. Relative geometry, Euclidean distances, plan distances, and all distance-ratio metrics such as DSI are preserved. Z/elevation values are retained.
