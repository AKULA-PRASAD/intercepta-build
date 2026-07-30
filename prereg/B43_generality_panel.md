# Pre-registration — B43: generality of retrospective enrichment across a diverse target panel (FINALIZED 2026-07-30, PRE-RESULT)

## Why (turn "1 target" into "many"; raise the generality link)
B42 validated the activity-scoring against real actives on ONE target (HIV: AUROC 0.806, EF@1% 7.4×). The vision is
"for many diseases," so the honest question is whether that enrichment **generalizes across diverse target classes**
— antiviral, GPCR, ion channel, kinase, enzyme — or was HIV-specific. B43 runs B42's validated retrospective
virtual-screening protocol across a panel and reports per-target + aggregate generality.

## Panel (OPEN, TDC HTS single-target bioactivity; real actives vs decoys)
Six diverse targets (chosen a priori to span classes; actives-count in parens):
`hiv` (antiviral phenotypic, 1443), `m1_muscarinic_receptor_antagonists_butkiewicz` (GPCR, 362),
`orexin1_receptor_butkiewicz` (GPCR, 233), `potassium_ion_channel_kir2.1_butkiewicz` (ion channel, 172),
`serine_threonine_kinase_33_butkiewicz` (kinase, 172), `sarscov2_3clpro_diamond` (viral protease, 78).
Actives span 78–1443 (deliberately includes hard, low-active screens — honest generality, not cherry-picked).

## Method (identical to B42 Arm 2, per target)
Per target: all actives + a seeded inactive subsample (≤6,000; keeps runtime bounded and improves balance);
featurize (Morgan2048+physchem); **Bemis–Murcko scaffold split ×3**; train the QSAR (`admet._TaskModel`, roc-auc) on
train scaffolds; score held-out test (real actives + decoys); rank; compute **AUROC, BEDROC(α=80.5), EF@1%, EF@5%**
(rdkit.ML.Scoring). Deterministic; reproduce ×2.

## Metrics & aggregate
Per-target: AUROC, BEDROC, EF@1%, EF@5% (mean over 3 scaffold seeds). Panel: mean AUROC/BEDROC/EF; **number of
targets with meaningful early enrichment (AUROC>0.70 AND EF@1%>3)**; and the honest per-target spread.

## Hypotheses (assumed FALSE)
- **H1 (generality):** the scoring enriches real actives (AUROC>0.70 AND EF@1%>3) in a MAJORITY (≥4/6) of the diverse
  targets — i.e. the capability is not HIV-specific.
- **H2 (early recognition):** panel-mean BEDROC(80.5) > 0.3 (actives recognized early, on average).
- **H0:** enrichment holds only for HIV / a minority → the approach does NOT generalize across target classes
  (first-class negative; honestly bounds the capability).

## Honesty / scope
Retrospective, in-silico, real-actives-vs-decoys enrichment — NOT prospective, NOT wet-lab. Low-active targets (78,
172) are hard and may fail; that is reported truthfully, not hidden. HTS actives carry assay noise; scaffold split
is the generalization probe within each target. Enrichment ≠ proven activity. This tests the SCORING's generality;
it does not claim novel-drug discovery.

## Reproducibility
Deterministic (seed=42; scaffold seeds fixed; inactive subsample seeded). Reproduce ×2 byte-identical (payload
sha256). Output: `experiments/B43_generality_panel/results/B43_metrics.json`.
