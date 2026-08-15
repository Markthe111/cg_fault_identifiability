# Reproducibility notes

## Fixed seeds

The archived v0.2.0 workflows use recorded, fixed seeds. The major-revision
diagnostic, OOD, and master commands use `20260806`; the public synthetic demo
and benchmark scripts use their repository-defined fixed seed. Pass the
documented seed explicitly when a command exposes `--seed`. Phase 5 is
deterministic but accepts and records the same major-revision seed for a uniform
command-line interface.

Changing a seed creates a sensitivity run, not a reproduction of the frozen
manuscript-facing result.

## Frozen expected outputs

`outputs_expected/` contains the v0.2.0 reference products used by the tests and
third-party comparisons. Treat this directory as read-only. Write new runs to
`outputs/` or another path supplied with `--output-root`, then compare against
the expected files. Documentation-only commits on `main` do not update these
references and do not alter the archived v0.2.0 results.

## OOD: no retuning

The 3,000-scenario OOD table is independent and frozen. Calibration is trained
on the 18,000-scenario ID benchmark and then applied to OOD data without
refitting, recalibration, threshold selection, or hyperparameter retuning on
OOD outcomes. Any OOD-informed adjustment would be a new experiment and must
not be described as the archived validation.

## Privacy boundary

The public repository contains synthetic data, coordinate-free metrics,
anonymized derived summaries, and LOSO geometry in an arbitrary translated
local coordinate frame. Restricted raw exploration records, proprietary GIS,
original mine survey coordinates, and information that would locate the public
frame in the mine survey system are excluded. Reproduction requires only the
public inputs and must not involve privacy-sensitive data recovery.

## Public reproduction boundary

Public reproduction covers the repository's synthetic attribution workflow,
18,000-scenario diagnostic benchmark, grouped held-out validation, frozen
3,000-scenario OOD evaluation, and LOSO comparison on public-derived local
geometry. It supports the claim and candidate-set boundaries stated in the
documentation. It does not reproduce analyses that require restricted raw
mine data, and it does not establish unrestricted geological or geographic
generalization.

The citable scientific archive is v0.2.0 at
<https://doi.org/10.5281/zenodo.21898348>. Later documentation-only `main`
commits can clarify usage but are not changes to that archived scientific
record.
