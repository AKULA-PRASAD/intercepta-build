# Pre-registration — B62: is the novel-chemistry extrapolation gap correctable shrinkage or fundamental signal-loss? (FINALIZED 2026-07-31, PRE-RESULT)

## Phase-0 provenance (why THIS experiment, and why not the obvious one)
An ultra-deep literature sweep showed the "obvious" next experiment — comparing conformal/ensemble uncertainty vs
AD-distance for ranking novel-chemistry error — would **reproduce established results**: AD-distance is a known-unreliable
error predictor (Sheridan; Rethinking-AD 2024), ensembles are known to beat single-model UQ OOD (polymer/NN-potential
benchmarks), conformal coverage under covariate shift is a solved-in-principle subfield (CoDrug, KMM-CP), and
regression-to-the-mean shrinkage is textbook. **Low information gain → rejected.** The genuinely un-done, discriminating
question our own program opened: *is the novel-chemistry extrapolation gap a correctable estimator bias (shrinkage) or
fundamental signal-loss — and does that split explain the target-dependent binding residual (B58) that chemical-property
correlates (B57–B60) failed to explain?*

## Mechanism discrimination (every outcome changes the theory)
The extrapolation gap can arise from (a) **shrinkage** — predictions compressed toward the training mean but rank
preserved (correctable by monotone recalibration), or (b) **signal-loss** — no transferable rank signal (Spearman→0,
uncorrectable), or (c) irreducible assay noise. (a) is optimistic/actionable; (b)/(c) are a hard ceiling.

## Data (OPEN; MoleculeACE, cached; continuous potency)
Per target: HGB regressor (Morgan-1024), Bemis–Murcko scaffold split ×3, **novel-chemistry test** (NN-Tanimoto<0.40).
Targets with <15 novel test compounds skipped. (Same pipeline as B60/B61.)

## Metrics (per target, on the novel test set; mean over seeds)
- **rank_signal** = Spearman(pred, true)  — invariant to monotone recalibration ⇒ measures *surviving signal*.
- **shrinkage_ratio** = std(pred)/std(true) — <1 indicates compression toward the mean.
- **rmse_raw** and **rmse_recalibrated** — RMSE before, and after the *oracle optimal linear recalibration* (regress
  true on pred using the novel labels; an upper bound on what any monotone debiasing could recover).
- **correctable_fraction** = 1 − (rmse_recalibrated² / rmse_raw²) — the share of squared error removable by linear
  recalibration (the "shrinkage" component); the remainder is the signal-loss/irreducible component.
- Also read each target's committed **B58 A1B1 residual** (the doubly-debiased binding residual) for the linkage test.

## Hypotheses (pre-registered)
- **H1 (gap is substantially correctable — optimistic):** panel-median **correctable_fraction ≥ 0.5** → the
  extrapolation gap is >half a fixable recalibration/shrinkage problem, not fundamental. Would reframe P8.
- **H2 (rank signal survives):** panel-median **rank_signal > 0.2** AND shrinkage_ratio < 1 on the majority → the model
  retains ordering but compresses scale (shrinkage confirmed as a real component).
- **H3 (resolves the target-dependent residual):** across targets, **Spearman(rank_signal, B58 A1B1 residual) ≥ 0.5** →
  the residual mystery (unexplained by roughness/diversity/assay/AD in B57–B60) is a **signal-loss** phenomenon: targets
  whose novel-chemistry rank signal is higher are exactly those with a higher irreducible binding residual.
- **H0 (fundamental):** correctable_fraction < 0.3 AND rank_signal ≈ 0 for most targets → the gap is genuine
  signal-loss / irreducible; extrapolation is fundamentally hard here (confirms the ceiling). First-class.
- **Reported regardless:** per-target rank_signal, shrinkage_ratio, correctable_fraction, and the H3 linkage.

## Honesty / scope
Retrospective, in-silico, MoleculeACE (ChEMBL medchem). The optimal linear recalibration uses the *novel labels* → it
is an **oracle upper bound** on correctability, not an achievable method (stated). Cannot fully separate irreducible
signal-loss from assay label noise (caveat). Shrinkage/regression-dilution is textbook in general; the novelty is the
per-target decomposition of the *novel-chemistry* gap and its linkage to our binding residual. n≈24 targets for H3
(modest; effect size reported). Correlation ≠ causation. Not wet-lab.

## Reproducibility
Deterministic (split seeds [1,2,3], model seed=42). Reproduce ×2 byte-identical (payload sha256 over summary+per
target). Output: `experiments/B62_shrinkage_vs_signalloss/results/B62_metrics.json`. Env: intercepta-build; INTERCEPTA_DATA owned.

---

## AMENDMENT (2026-07-31, pre-run — H3 infeasible as written)
H3 proposed correlating each MoleculeACE target's novel-chemistry rank_signal with its **B58 A1B1 residual**. This is
**infeasible**: B58's residuals are for LIT-PCBA/TDC-HTS targets, a *different* target set than MoleculeACE's ChEMBL
targets — there is no target correspondence. This was a pre-registration error (caught before running). H3 is therefore
**withdrawn**; in its place a within-B62 descriptive link is reported (Spearman of rank_signal vs correctable_fraction)
with no confirmatory threshold. H1/H2/H0 (the shrinkage-vs-signal-loss decomposition) are unaffected and remain the
pre-registered core. Documented; original H3 left above as the record.
