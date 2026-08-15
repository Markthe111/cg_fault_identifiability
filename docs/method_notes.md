# Method notes

## Claim-specific identifiability

Identifiability is evaluated relative to a stated claim and a declared
candidate set. A workflow may support discrimination among named plan-view
fault domains while leaving deep geometry non-unique, or it may identify a
predictively admissible subset of tested surfaces without proving that the
geological truth lies in that subset. Results must therefore name the claim,
candidate faults or model families, data support, and validation regime.

## Eq. 5 DSI definition

For point `i`, the manuscript Eq. 5 plan-view Domain-Separation Index is

```text
DSI_i = d_plan(i, nearest competing named fault)
        / d_plan(i, expected associated fault)
```

The numerator searches the competing named-fault set; the denominator uses the
expected associated fault. This is not a generic nearest/next-nearest neighbour
ratio. A separately reported pairwise 3-D separation ratio is supplementary
and is not manuscript Eq. 5.

DSI is a low-cost screening diagnostic. It does not by itself establish 3-D
association, fault causality, ore control, or a universal stability guarantee.

## Distance-difference margins

The validation workflow also evaluates signed distance evidence:

```text
distance difference = d_competing - d_associated
normalized margin   = (d_competing - d_associated)
                      / (d_competing + d_associated)
```

Positive values favour the expected associated fault within the declared
candidate set; negative values identify a locally closer competitor. These
margins retain scale information that a ratio alone can obscure, but they are
still geometric diagnostics rather than geological proof.

## Grouped and OOD validation

Grouped held-out validation partitions the 18,000-scenario ID benchmark by
fault spacing, perturbation intensity, competing-fault count, or domain
scatter. Calibration is fitted on the remaining scenario families and tested
on the held-out family.

OOD validation instead uses the independent frozen 3,000-scenario generator
with curved traces, depth-variable geometry, correlated perturbations, and
irregular layouts. ID-fitted calibration is applied without OOD refitting,
recalibration, or threshold retuning. Grouped validation measures structured
interpolation within the benchmark design; OOD validation probes transfer to a
different synthetic geometry family. They are not interchangeable claims.

## LOSO predictive admissible set

For each fault and candidate surface family, leave-one-section-out prediction
holds out each section in turn and evaluates predictive error. The declared
admissibility rule is:

```text
mean LOSO RMSE <= best mean LOSO RMSE + SE(best),
and the candidate is a continuous surface.
```

Training residuals do not determine admission. The resulting set is a
predictive admissible set under this rule, not a posterior distribution or a
geological confidence interval. Depthwise envelopes summarize divergence among
admitted tested models at the evaluated depths.

## Candidate-family limitation

The LOSO comparison is limited to the implemented continuous surface families:
single plane, continuous segmented plane, weakly curved ridge-regularized
quadratic surface, and trace-constrained ruled surface. Conclusions do not
cover arbitrary geological surfaces. F7 has only three sections, so the public
analysis supports limited discrimination among the tested families rather than
a strong deep-geometry conclusion.
