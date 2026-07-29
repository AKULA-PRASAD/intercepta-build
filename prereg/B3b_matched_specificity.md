# Pre-registration — B3b (L1b): recover drug-specificity in patient transfer (FINALIZED 2026-07-29, pre-run)

## Motivation
B3/L1 found real but NON-specific, proliferation-driven transfer (diag ρ=+0.054 p=0.0005; diag≈off-diag
p=0.12; not beyond R_prolif). Two candidate causes, both testable on held data: (i) cross-platform batch
(GDSC microarray → BeatAML RNA-seq); (ii) a dominant proliferation axis masking any drug-specific signal.
B3b attacks both.

## Question
After (i) training on a **matched RNA-seq platform** (DepMap/CCLE RNA-seq, labels = GDSC LN_IC50 via
COSMIC↔DepMap) and (ii) **residualizing out proliferation** (R_prolif) from both prediction and patient AUC,
is there any **drug-specific** cell-line→patient signal (diagonal > off-diagonal on residuals), or is the
patient-reaching signal entirely generic proliferation?

## Hypothesis (assumed FALSE)
- H1_matched: matched-platform diagonal mean per-drug ρ > 0, permutation p<0.05 (and ideally > B3's +0.054).
- H1_specific_resid: on proliferation-residualized vectors, mean diagonal ρ_resid > mean off-diagonal
  ρ_resid AND > 0, permutation p<0.05 → genuine drug-specific patient signal beyond proliferation.
- H0: matched platform does not help and/or no drug-specific signal survives proliferation removal → the
  patient-reaching signal is confirmed generic (bounds L1 definitively).

## Data (held; sha256 in MANIFEST)
Train expr: DepMap/CCLE RNA-seq `depmap_expression.csv` (cells×genes symbol). Labels: GDSC `LN_IC50`, joined to
DepMap cells via COSMIC↔DepMap (`depmap_meta.csv`). Test: BeatAML patient RNA `beataml_..._norm_exp` + ex-vivo
AUC (join dbgap_rnaseq_sample). Genes = DepMap ∩ BeatAML symbols, top-2000 variance on DepMap. Same 44-drug
overlap set. Leakage: BeatAML patients are disjoint from all DepMap cells — structurally clean.

## Design (locked)
Per-drug RidgeCV (alphas {10,100,1000}) on DepMap RNA-seq z-expression → GDSC LN_IC50; predict on BeatAML
z-expression. Per drug (≥30 train cells, ≥15 patients): diagonal ρ = Spearman(pred_dk, AUC_dk). Off-diagonal
ρ = mean over dj≠dk of Spearman(pred_dj, AUC_dk). RESIDUALIZED variant: regress out R_prolif (patient) from
both pred and AUC via OLS over the drug's patient set, recompute diagonal/off-diagonal on residuals.

## Baselines / bar
Frozen R_prolif transfer (as B3); B3's array-trained diagonal +0.054 (does matched platform beat it?);
off-diagonal (specificity control); zero (residual transfer).

## Primary metric + decision rule (fixed)
1. MATCHED-PLATFORM TRANSFER PASS: diag mean ρ>0, perm p<0.05 (k=2000, seed=42).
2. DRUG-SPECIFIC-BEYOND-PROLIF PASS: mean diag ρ_resid > mean off-diag ρ_resid AND >0, perm p<0.05.
The strong L1 claim ("drug-level patient prediction") requires (2). (1) alone only re-confirms generic transfer
on a cleaner platform.

## Falsification battery
Permutation nulls (patient-label for transfer; sign-flip for specificity). Proliferation residualization IS
the confound control. Leakage structurally absent.

## Honest prior
Given B2 (mutations add nothing), the falsified selective-axis history, and L1's non-specificity, P(drug-
specific signal survives proliferation removal) ~15–25%. A null here would DEFINITIVELY bound L1: "public
cell-line models transfer to patients only as a generic proliferation/chemosensitivity axis" — a clean,
important, vision-sizing result that redirects effort to L2 (controlled trials) and matched prospective data.

## Reproducibility
Closed-form Ridge; deterministic gene selection; seed=42, k=2000. Reproduce ×2 = identical metrics JSON.
Output: `experiments/B3b_patient_specificity/results/B3b_metrics.json`.
