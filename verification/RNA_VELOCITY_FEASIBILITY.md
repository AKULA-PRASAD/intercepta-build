# RNA-Velocity "Time Machine" — feasibility (Constitution outcome 3: untestable on current data)
Date 2026-07-29. The vision's most novel idea: velocity detects a pre-resistant subpopulation on Day 1 that
predicts relapse/drug response. Assessed against available data.

## What exists
- Per-cell latent_time (velocity_star_latent_time.csv, 46,236 prostate cells) + per-cluster velocity magnitudes.
- scRNA: prostate (GSE137829/141445; velocity+clusters, NO outcome), AML vangalen2019 (CellType + Mut/Wt
  genotyping, NO per-cell drug response, NO paired pre/post-treatment).

## Why the predictive claim is NOT falsifiable now
Validating "velocity-predicted pre-resistance → actual resistance/drug response" requires a per-cell (or
per-population) GROUND TRUTH of resistance/outcome. None of the available scRNA has it. latent_time is an
unsupervised pseudotime; velocity is assumption-laden. Any "test" on current data would be a consistency
check (does high-velocity cluster look LSC/NE-like?), NOT a validation of the predictive claim — reporting it
as validation would be fabrication.

## Precise missing data that would make it testable
PAIRED LONGITUDINAL scRNA of the SAME patients at baseline AND relapse/post-treatment, with matched
drug-response/resistance outcome (ideally lineage-traced), so a baseline velocity-predicted pre-resistant
population can be checked against which cells actually survived/expanded. Such datasets are rare and mostly
controlled-access. Until obtained: RNA-velocity time machine = ARCHITECTURALLY NOVEL, EMPIRICALLY UNTESTED,
not falsifiable on current data. Do NOT claim it works.
