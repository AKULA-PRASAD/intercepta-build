# Pre-registration — B14: does the expression→inferred-dependency layer improve PATIENT (BeatAML ex-vivo) drug prediction? (FINALIZED 2026-07-29, PRE-RESULT)

## Rationale (the decisive test of the functional-inference thesis)
B12/B13 (cell lines): functional dependency predicts drug response and beats baseline expression; dependency is
learnable from expression (patient-translatable in principle). B14 tests it where it matters: **real patient
tumor samples (BeatAML ex-vivo)**, for target-anchored drugs, vs the weak direct transcriptomic transfer (V9,
ρ≈0.07). FLT3 is the key case — FLT3-ITD AML should show high inferred-FLT3-dependency → FLT3-inhibitor sensitivity.

## Data (public + controlled BeatAML)
Train expr→dependency (per target gene) on DepMap (expression + CRISPR). Apply to BeatAML patient RNA-seq →
inferred dependency per patient. Test vs BeatAML ex-vivo AUC. Direct-transfer comparator = engine.predict_transfer.

## Pre-declared drug → target pairs (drug in BeatAML + target dependency learnable in B13)
trametinib→MAP2K1, selumetinib→MAP2K1; sorafenib→FLT3, quizartinib→FLT3, gilteritinib→FLT3, crenolanib→FLT3;
venetoclax→BCL2; erlotinib→EGFR, gefitinib→EGFR, afatinib→EGFR.

## Hypotheses (assumed FALSE)
- **H1 (functional layer predicts patient response):** pooled ρ(inferred-dependency of target, BeatAML ex-vivo
  AUC), proliferation-residualized, > 0, permutation p<0.05. Direction: more inferred-dependent (more negative
  dep̂) → more sensitive (lower AUC) → positive ρ(dep̂, AUC).
- **H2 (beats / complements direct transfer):** median per-drug |ρ(inferred-dep)| > |ρ(direct engine transfer)|
  (the V9 baseline), paired across drugs, permutation p<0.05.
- H0: inferred dependency carries no patient ex-vivo signal, or no better than direct transfer.

## Decision rule (fixed)
Per drug (≥15 patients): Spearman(inferred-dep_target, AUC), prolif-residualized; and Spearman(direct transfer,
AUC). Pooled H1: mean ρ_inferred + permutation (patient-label, k=2000, seed=42). H2: paired |ρ_inferred| vs
|ρ_direct|, sign-flip permutation. BH per drug.

## Interpretation (fixed)
- H1+H2 pass → the functional-inference layer materially improves patient-level (ex-vivo) drug prediction over
  the direct transfer, using only expression → a genuine, novel, translatable advance (to be confirmed in Track-1).
- H1 pass, H2 fail → predicts but not better than direct → real but not an improvement.
- Null → functional layer does not translate to patients here (honest bound; contradicts the cell-line optimism).

## Honesty / scope
BeatAML ex-vivo (AML), still not clinical outcome. Target-anchored drugs. dep̂ trained on pan-cancer DepMap.
Effect sizes reported honestly; a null is first-class and would bound the functional-inference thesis.

## Reproducibility
Deterministic (seed=42, k=2000); reproduce ×2. Output: experiments/B14_functional_layer_patients/results/B14_metrics.json.
