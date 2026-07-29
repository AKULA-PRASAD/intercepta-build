# Pre-registration — B1: re-establish the honest cross-dataset ceiling

## Question
Does a learned per-drug expression→response map trained on GDSC transcriptomics generalize to a *different*
dataset (CCLE/PRISM) with **disjoint cell lines**, better than the parameter-free proliferation axis?

## Hypothesis (assumed FALSE until it survives)
- H1: STRICT (disjoint-cell-line) mean per-drug Spearman ρ > R_prolif bar, paired Wilcoxon p<0.05.
- H0: learned map does not beat the parameter-free axis once cell-line-identity leakage is removed.

## Data
GDSC2 response + expression; DepMap/CCLE 22Q2 expression; PRISM secondary screen; DepMap COSMIC↔DepMap map.
All public; sha256 in `data/MANIFEST.md`, verified at load.

## Design
Per-drug RidgeCV (alphas {10,100,1000}) on GDSC z-scored top-2000-variance shared-gene expression → LN_IC50;
predict on CCLE z-expression; score per-drug Spearman vs PRISM AUC. ≥30 GDSC train rows and ≥20 shared test
cells per drug. **STRICT** design removes every test cell line's COSMIC from training (disjoint train/test).
The LEAKY design (test lines left in training) is reported only to quantify the leakage inflation.

## Baselines / the bar
Frozen parameter-free `R_prolif` (mandatory). LEAKY design as the upper (invalid) reference.

## Primary metric + decision rule
Primary = STRICT mean per-drug ρ. PASS iff STRICT mean ρ > R_prolif mean ρ AND paired Wilcoxon p<0.05.
Reproduction target (carried from ~/kaalcura V1B): STRICT mean ρ ≈ **+0.212**, 94/100 drugs>0.

## Falsification battery
Leakage audit is built in (STRICT vs LEAKY gap). Paired Wilcoxon vs the parameter-free bar is the null test.
(Permutation and external-dataset replication of the *learned gain* are deferred to B2/B3, pre-registered
separately, so B1 stays a clean reproduction of the established ceiling.)

## Reproducibility
Ridge is closed-form; no seeded stochastic step → deterministic. Reproduce ×2 = identical metrics JSON
(timestamp aside). Output: `experiments/B1_baseline_ceiling/results/B1_metrics.json`.
