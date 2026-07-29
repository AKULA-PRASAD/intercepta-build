# Pre-registration — B22: is the drug-response ceiling a limit of the RNA MODALITY, or of baseline molecular profiling in general? (FINALIZED 2026-07-29, PRE-RESULT)

## The question (on the true-vision critical path)
Our validated intellectual core: baseline transcriptomics carries proliferation + lineage, not drug-specific
vulnerability, and cross-dataset transfer has a hard ceiling (ρ≈+0.212, B1/B2). The unresolved, decisive question:
**is that ceiling specific to the RNA modality, or does it bind any baseline molecular profile?** If a functional-
signaling modality — mass-spec **proteomics** — carries drug-specific signal RNA lacks, that is a genuine new
direction for the platform. If proteomics hits the SAME ceiling, the limit is modality-general (baseline omics
cannot resolve within-lineage drug specificity), a profound reframing that decisively motivates functional/
perturbation data (Track-1) over any baseline-omics modeling.

## Data (public, matched, cell-line level — where transfer is real)
- Proteomics: CCLE quantitative proteomics (Nusinow et al., Cell 2020; gygi.hms.harvard.edu, openly downloadable),
  gene-level, 375 lines; 7,947 proteins quantified in ≥70% of the matched set.
- Transcriptomics: DepMap RNA-seq (same lines).
- Labels: GDSC2 LN_IC50. Cell lines keyed to DepMap_ID via CCLE metadata (CCLE_Name / COSMIC_ID → DepMap_ID).
- **Matched set: 291 cell lines with proteomics ∩ RNA ∩ GDSC; 271 drugs with ≥120 matched lines.**

## Design (fair head-to-head — identical protocol, only the feature matrix changes)
For each drug (≥120 matched lines), 5-fold CV over cell lines (disjoint train/test, KFold shuffle seed=42),
per-drug RidgeCV (α∈{10,100,1000}), out-of-fold predictions, per-drug Spearman ρ(pred, LN_IC50). Three feature
sets, identical folds/lines/drugs: **R** = top-2000-variance RNA genes; **P** = top-2000-variance proteins; **RP**
= concatenation. Features standardized on each training fold (mean/SD), applied to test; residual protein missingness
imputed to the training mean (0 post-standardization). Top-variance selection is unsupervised (label-free).

## Hypotheses (assumed FALSE)
- **H1 (proteomics is a comparable modality):** mean per-drug ρ_P is within ±0.02 of ρ_R (paired across drugs).
- **H2 (proteomics adds beyond RNA — ceiling is RNA-specific):** ρ_P > ρ_R AND ρ_RP > ρ_R, paired Wilcoxon
  p<0.05 with a materially larger effect (Δρ ≥ +0.02 mean). This is the "new direction" hypothesis.
- H0: ρ_P ≤ ρ_R and ρ_RP ≈ ρ_R (Δρ < +0.02, or not significant) → the ceiling is modality-general.

## Decision rule & interpretation (fixed)
Primary comparisons: paired Wilcoxon on per-drug ρ, (P vs R) and (RP vs R); report mean/median ρ per modality and
the paired Δ. 
- **H2 PASS** (ρ_P and ρ_RP both beat ρ_R, p<0.05, mean Δρ≥+0.02) → proteomics resolves drug-specificity RNA
  misses; the ceiling is **RNA-specific** → a real, novel direction: shift the baseline-omics layer to proteomics
  (and pursue matched patient proteomics, e.g. BeatAML proteogenomics, as the translational follow-up).
- **H2 FAIL** → the ceiling is **modality-general**: baseline proteomics does not beat baseline RNA for drug-
  specific response → strong, publishable evidence that no baseline molecular profile resolves within-lineage
  drug specificity, and that functional/perturbation readouts (Track-1) are required. First-class either way.

## Honesty / scope
Cell-line internal CV (not the B1 cross-dataset transfer number; absolute ρ not directly comparable to +0.212 —
the comparison here is protein vs RNA under an identical protocol). Proteomics has ~27% missingness and fewer
features; top-2000-variance selection controls dimensionality fairly. A null (modality-general ceiling) is fully
expected and first-class. No clinical claim.

## Reproducibility
Deterministic (seed=42); reproduce ×2. Data sha256/MD5 in results. Output:
experiments/B22_modality_ceiling/results/B22_metrics.json.
