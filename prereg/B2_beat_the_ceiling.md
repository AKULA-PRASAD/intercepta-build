# Pre-registration — B2: can anything beat the +0.212 ceiling? (DRAFT — not yet run)

## Question
Does adding **verified biology** — (a) the frozen proliferation axis as a feature, and/or (b) somatic
mutation features (the AML mutation→drug signal generalized) — raise STRICT cross-dataset per-drug ρ above the
B1 transcriptome-only ceiling (+0.212), or is +0.212 a real ceiling for this data?

## Hypothesis (assumed FALSE)
- H1: an expression + {R_prolif, mutation-context} model beats +0.212 by a pre-set margin (Δρ ≥ +0.02, paired
  Wilcoxon p<0.05 across drugs).
- H0: no combination beats transcriptome-only; +0.212 is the ceiling of public cell-line generalization.

## Design (to finalize before running)
Same STRICT disjoint-cell-line, per-drug protocol as B1. Arms: (0) B1 transcriptome-only [control];
(1) + frozen R_prolif; (2) + mutation indicators for the drug's known target pathway (DepMap mutations);
(3) elastic-net vs ridge. All arms share identical splits and drug set.

## Bar
B1 STRICT ceiling +0.212 (the number to beat). Predict-the-mean and single-gene surrogate also reported.

## Falsification battery (all required for a POSITIVE)
Permutation null (k=2000) on the Δρ; BH-FDR across drugs; leakage audit (mutation features must not encode
cell-line identity); **external replication** on a third dataset (e.g., CTRPv2 or GDSC1) — the gain must hold,
not just appear once. A gain that does not replicate externally is logged as PROVISIONAL/failed, not a result.

## Honest prior
Given V1 (learned map already ≈ pathway-informed) and the falsification of a novel selective axis, prior that
B2 beats the ceiling is modest (~20–35%). A well-powered null here is a first-class result: it would establish
+0.212 as the genuine public-data ceiling and point to the missing data (patient transfer / controlled trials)
rather than more model tuning.
