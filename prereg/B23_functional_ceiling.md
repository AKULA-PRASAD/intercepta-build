# Pre-registration — B23: does MEASURED functional dependency break the +0.212 baseline ceiling — beyond the trivial target? (FINALIZED 2026-07-29, PRE-RESULT)

## The question (on the true-vision critical path; fully local data)
Established: baseline molecular profiles cap drug-response prediction — RNA at ρ≈+0.212 (B1/B2/V7), and proteomics
does not beat RNA (B22/V21). The functional-inference layer (dependency *inferred* from expression) beat a
biomarker within one cohort but failed external replication (B20/B21). The decisive unresolved question: does
**MEASURED** functional dependency (DepMap CRISPR gene-effect — the real thing, not inferred) carry drug-specific
signal that baseline profiles lack — and does it do so **beyond the trivial case of a drug's own target** (whose
dependency predicts its own drug by construction)? If yes, measured functional profiling breaks the baseline
ceiling — a real, important result and strong evidence for the functional-measurement thesis. If no, the ceiling
holds even for measured genome-wide function once the direct target is removed — a deeper, first-class negative.

## Data (public, LOCAL, matched at cell-line level — no external dependency)
DepMap RNA-seq expression, DepMap CRISPR (Chronos) gene-effect, GDSC2 LN_IC50; cell lines keyed to DepMap_ID via
CCLE metadata (COSMIC_ID→DepMap_ID). **Matched: 498 cell lines (expr ∩ CRISPR ∩ GDSC); 272 drugs with ≥120 lines.**

## Design (fair head-to-head — identical CV/lines/drugs, only the feature matrix changes)
Per drug (≥120 matched lines), 5-fold CV over cell lines (disjoint, KFold seed=42), per-drug RidgeCV
(α∈{10,100,1000}), out-of-fold predictions, per-drug Spearman ρ(pred, LN_IC50). Three feature sets, unsupervised
top-2000-variance each (label-free): **R** = RNA genes; **D** = CRISPR dependency (gene-effect); **RD** =
concatenation. Standardized on each training fold; residual missingness imputed to training mean.

## Target-leakage control (critical — pre-specified)
Because a drug's own target-gene dependency can predict its response tautologically, for a curated set of
well-known single-target drugs (target gene in DepMap), rebuild the dependency feature set with **that drug's
target gene(s) EXCLUDED**, reselect top-2000-variance, and re-test D vs R on the same lines. If D's advantage
persists with the target removed, it is not target-leakage.

## Hypotheses (assumed FALSE)
- **H1 (measured function is at least comparable/better):** mean per-drug ρ_D ≥ ρ_R (paired Wilcoxon).
- **H2 (measured function ADDS — ceiling broken):** ρ_RD > ρ_R, paired Wilcoxon p<0.05, mean Δρ ≥ +0.02.
- **H3 (not target-leakage):** on the curated targeted-drug subset, ρ_D(target-excluded) > ρ_R, p<0.05.
- H0: ρ_D ≤ ρ_R and ρ_RD ≈ ρ_R (Δ<+0.02 or n.s.), and/or the D advantage vanishes once targets are excluded (H3
  fails) → the ceiling is not broken by measured function beyond the direct target.

## Decision rule & interpretation (fixed)
Primary: paired Wilcoxon on per-drug ρ, (D vs R) and (RD vs R); report mean/median ρ and paired Δ.
- **H2 PASS + H3 PASS** → **measured functional dependency breaks the baseline ceiling**, and not via target
  tautology → genuine advance; functional measurement is the informative modality (consistent with the whole
  program's thesis, now with measured cell-line evidence). Important, possibly breakthrough-relevant.
- **H2 PASS but H3 FAIL** → the advantage is target-tautological (dependency re-encodes the drug's target); honest
  bound — no generalizable functional-state signal beyond the known target.
- **H2 FAIL** → the ceiling is modality-general even for measured genome-wide function; deepens B22/V21.
Every outcome is first-class.

## Honesty / scope
Cell-line internal CV (not the B1 cross-dataset number; the comparison is D vs R under an identical protocol).
CRISPR has missingness and its own noise; top-2000-variance controls dimensionality fairly. Target-exclusion uses a
curated (necessarily incomplete) drug→target map — a representative leakage probe, not exhaustive. A null is fully
expected and first-class. No clinical claim.

## Reproducibility
Deterministic (seed=42); reproduce ×2. Data sha256 in results. Output:
experiments/B23_functional_ceiling/results/B23_metrics.json.
