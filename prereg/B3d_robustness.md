# Pre-registration — B3d (L1b robustness): is the weak drug-specific patient signal robust? (FINALIZED 2026-07-29, pre-run)

## Motivation
B3b/B3c found a weak (ρ≈0.07–0.08), replicated, drug-specific, proliferation-independent cell-line→patient
signal. Before it advances the vision further it must survive robustness attacks: is it driven by a few
drugs, or a single patient subset? B3d tries to break it on held data. No new claim if it survives — only
increased/decreased confidence in V9.

## Setup (identical training to B3b)
Train per-drug RidgeCV on DepMap RNA-seq z-expression + GDSC2 LN_IC50 labels; predict on BeatAML patients.
Primary quantity = proliferation-residualized specificity: mean_drug(diag_r) − mean_drug(off_r), where diag_r
= Spearman of prolif-residualized (prediction, AUC) for the matched drug, off_r = mean over mismatched drugs.
Training never uses patients → splitting patients for evaluation introduces no leakage.

## Tests + decision rules (fixed in advance)
- **R1 — drug jackknife (leave-one-drug-out).** Recompute mean(diag_r−off_r) dropping each drug in turn.
  ROBUST iff the value stays > 0 for ALL leave-one-out subsets (no single drug flips the sign).
- **R2 — bootstrap over drugs (B=2000, seed=42).** Resample drugs with replacement; 95% percentile CI of
  mean(diag_r−off_r). ROBUST iff CI lower bound > 0.
- **R3 — internal patient split-half.** Assign each BeatAML patient to half 0/1 by md5(sample) parity
  (deterministic, disjoint patients). Recompute residualized diag_r/off_r within each half (per-drug ≥8
  patients in that half). ROBUST iff BOTH halves have mean(diag_r−off_r) > 0 with the same sign
  (permutation p reported; given halved power we require direction agreement, not necessarily p<0.05 in both).

## Overall verdict
- If R1 AND R2 AND R3 all pass → V9 confidence upgraded to "robust to drug- and patient-subsetting" (still
  bounded to one cohort/cancer; still needs a 2nd patient cohort).
- If any fail → V9 downgraded with the exact fragility named (e.g., "driven by drug X" / "only in patient
  half A"); reported honestly, no spin.

## Exploratory (labeled, no pass/fail)
Per-drug residualized diagonal ρ ranking — which drugs transfer best beyond proliferation — surfaced for
mechanistic interpretation only. NOT a hypothesis test (drug-class curation would be researcher DOF).

## Reproducibility
Deterministic; seeds fixed (bootstrap/permutation seed=42). Reproduce ×2 = identical metrics JSON.
Output: `experiments/B3d_robustness/results/B3d_metrics.json`.
