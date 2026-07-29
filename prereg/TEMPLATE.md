# Pre-registration — <ID> <title>

Written and committed BEFORE the experiment runs. Editing this after seeing results is a Constitution
violation; amendments are appended below with a timestamp and reason, never silent overwrites.

## Question
The single falsifiable question, phrased so that a specific outcome would kill the hypothesis.

## Hypothesis (assumed FALSE until it survives)
H1: ...   H0 (what we expect if there is nothing): ...

## Data
Inputs + sha256 (data/MANIFEST.md). Public only. No controlled-access data without a logged human gate.

## Design
Model, features, split (must be leakage-free — state how), covariates.

## Baselines / the bar (mandatory)
predict-the-mean; single-gene surrogate; parameter-free axis; and the current best (B1 ceiling ρ=+0.212).

## Primary metric + decision rule
The metric, and the exact numeric threshold + statistical test that decides PASS vs FAIL, fixed in advance.

## Falsification battery (rule 3)
Permutation null (k, seed); leakage audit; multiple-testing (BH-FDR); confound adjustment; external
replication dataset. Which apply, and the pass threshold for each.

## Reproducibility
Seed; determinism argument; reproduce ×2 requirement; metrics JSON path.

## Amendments
(append-only)
