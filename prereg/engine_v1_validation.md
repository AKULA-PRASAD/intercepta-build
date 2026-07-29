# Pre-registration — engine v1 validation (FINALIZED 2026-07-29, pre-run)

## Question
Does the shipped `InterceptaEngine` (which combines the verified transfer signal + verified mutation markers)
produce a combined per-drug sensitivity score that predicts BeatAML ex-vivo response BETTER than its transfer
component alone — i.e., does the engine actually embody the V10 "engine > parts" result through its real API?

## Hypothesis (assumed FALSE)
- H1: on the verified drug–marker pairs, |Spearman(engine combined_score, ex-vivo AUC)| > |Spearman(transfer
  component, AUC)| in a MAJORITY of pairs (combined predicts sensitivity better than transfer alone).
- H0: adding the markers via the engine does not improve over transfer alone.

## Data (held; controlled — env INTERCEPTA_BEATAML)
Engine fit on DepMap RNA-seq + GDSC2 LN_IC50. Test = BeatAML patient expression + ex-vivo AUC + mutation matrix
(NRAS/DNMT3A from WES, NPM1/FLT3-ITD from clinical). Verified pairs: trametinib/selumetinib~NRAS,
dasatinib~DNMT3A, sorafenib~FLT3-ITD (cabozantinib~NPM1 not testable — no GDSC2 cabo training drug).

## Metric + decision rule (fixed)
Per pair: rho_combined = Spearman(combined_score, AUC) [expect NEGATIVE — higher score = more sensitive = lower
AUC]; rho_transfer = Spearman(-transfer_z, AUC). ENGINE VALID iff combined is more negative (better) than
transfer-alone in ≥ half of testable pairs, consistent with LEDGER V10. (This re-demonstrates the ALREADY-
validated V10 through the engine's shipped code path — not a new claim.)

## Honesty
Effects are weak (per LEDGER); this validates that the engine faithfully embodies V10, NOT that it is a clinical
tool. One cohort. Confidence tag on every prediction is LOW by design.

## Reproducibility
Ridge closed-form; deterministic gene selection; reproduce ×2 = identical metrics JSON.
Output: `experiments/engine_v1_validation/results/engine_v1_metrics.json`.
