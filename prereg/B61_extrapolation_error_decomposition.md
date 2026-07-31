# Pre-registration — B61: per-compound decomposition of novel-chemistry extrapolation error (FINALIZED 2026-07-31, PRE-RESULT)

## Origin (hypothesis-space construction, not a lone guess)
B60 opened P8 (the extrapolation gap: ligand-based models interpolate ~0.8 but extrapolate to novel chemistry ~0.3, NOT
governed by landscape roughness). A full mechanism-space enumeration + elimination using our own evidence (B60 ruled out
global roughness for extrapolation; B59 ruled out assay type; B32–B48 ruled out representation/model class) leaves the
live candidates all **per-compound** and untested at compound level. B61 tests them simultaneously at high power.

## Scientific question
For a ligand-based potency model predicting a compound **dissimilar to its training set** (novel chemistry), what
governs the per-compound extrapolation error — and is that error predictable at all?

## Data (OPEN; MoleculeACE 30 ChEMBL targets, cached; continuous potency)
Pool every **novel-chemistry test compound** (Bemis–Murcko scaffold-split test AND NN-Tanimoto to train < 0.40) across
all usable targets → thousands of compounds. Per target, HGB regressor (Morgan-1024) trained on the scaffold-train;
per-compound **absolute error** = |predicted − true pKi/pIC50|. (Targets with <15 novel test compounds skipped.)

## Candidate per-compound predictors (the competing mechanisms)
- **D1 AD-distance:** 1 − max Tanimoto to any training compound (covariate/feature shift; the canonical OOD driver).
- **C2 local-cliff:** potency std among the k=5 nearest *training* neighbours (local SAR ruggedness at the extrapolation point).
- **C3 scaffold-novelty:** 1 − max Tanimoto of the compound's Murcko scaffold to any training scaffold (continuous).
- **C4 potency-shift:** |true potency − training median| / training potency-std (label shift).
All predictors use TRAINING data + the compound's structure only (no leakage of the compound's own label).

## Analysis (Phase 9)
1. **Univariate:** Spearman(error, predictor) pooled across compounds AND within-target then averaged; rank by |Spearman|.
2. **Multivariate / predictability ceiling:** gradient boosting predicting per-compound error from ALL predictors,
   leave-one-target-out; report OOF Spearman(predicted-error, true-error) = how predictable the error is at all.

## Hypotheses (pre-registered)
- **H1 (AD-distance dominates):** D1 is the strongest single correlate AND positive (farther ⇒ larger error).
- **H2 (error meaningfully predictable):** multivariate OOF Spearman ≥ 0.3 → a usable "trust rule" exists.
- **H0 / null (irreducible):** no predictor reaches |Spearman| ≥ 0.2 AND multivariate OOF Spearman < 0.2 →
  novel-chemistry extrapolation error is largely irreducible / label-noise-bounded (a profound, honest ceiling). First-class.
- **Reported regardless:** all univariate correlations, multivariate predictability, importances, per-target counts.

## Honesty / scope
Retrospective, in-silico. Pooling risks target-confounding → within-target reported alongside. AD-distance and
scaffold-novelty are related (collinearity noted). Local-cliff uses k=5 (one operationalization). Absolute error depends
on each assay's dynamic range (partly normalized by potency-std). B30b already found AD→error is weak in aggregate, so a
strong H1 is not assumed. Not wet-lab. A null (irreducible error) is expected-allowed and valuable.

## Reproducibility
Deterministic (split seeds [1,2,3], model seed=42, k=5 fixed). Reproduce ×2 byte-identical (payload sha256 over
summary+per-target counts). Output: `experiments/B61_extrapolation_error_decomposition/results/B61_metrics.json`.
Env: intercepta-build; INTERCEPTA_DATA owned.
