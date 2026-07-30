# Pre-registration — B30b: validate the ADMET applicability-domain flag + calibrated conformal uncertainty (FINALIZED 2026-07-29, PRE-RESULT)

## Why (closes a self-identified gap in B30)
B30 shipped an ADMET screening filter with a Tanimoto **applicability-domain (AD)** flag and NO per-prediction
uncertainty. Two things were asserted but not proven: (i) that the AD flag actually predicts higher error (an AD
that doesn't track error is decorative — violates "bar before boast"); (ii) any calibrated confidence per molecule.
B30b tests (i) and adds (ii), extending the conformal approach validated for the synergy tool (B29) to ADMET.

## Data & setup
TDC ADMET Benchmark Group (22 tasks, OPEN, scaffold splits), official 5-seed protocol, same features/model as B30
(Morgan/ECFP4 2048-bit + 17 RDKit physchem; HistGradientBoosting, seed=42). Per seed: `get_train_valid_split` →
train on **train**, use **valid** as the conformal CALIBRATION set, evaluate on the fixed scaffold **test**.
AD distance = 1 − max Tanimoto similarity of a molecule to the training set (as in `admet.py`). Deterministic;
reproduce ×2.

## Aim 1 — Is the applicability domain VALID? (does error rise with AD distance?)
Per task, on the scaffold test set, per-molecule error: regression = |y − ŷ|; classification = |y − p̂| (bounded L1).
- **H1a:** Spearman ρ(per-molecule error, AD distance) > 0 (error increases with distance from training chemistry).
- **H1b:** molecules flagged OOD (AD distance beyond the B30 95th-percentile training threshold) have higher mean
  error than in-domain molecules.
- **H0:** ρ ≈ 0 / OOD error ≈ in-domain → the AD flag is not informative (report as such; it would be demoted to
  descriptive-only, exactly as engine reliability was in B6/V13).
**Decision rule:** AD **VALIDATED** iff a clear majority of the 22 tasks show ρ>0 with BH-FDR q<0.05 (across tasks)
AND pooled mean OOD error > pooled mean in-domain error. Effect size (ρ and error ratio) reported, not just p.

## Aim 2 — Calibrated conformal intervals (regression) coverage
Inductive split-conformal: nonconformity s_i=|y_i−ŷ_i| on the calibration (valid) set; q̂=the ⌈(n+1)(1−α)⌉/n
empirical quantile; test interval = ŷ ± q̂. Measure empirical coverage = mean(|y_test−ŷ_test| ≤ q̂) and mean width
2·q̂, per regression task (9), at nominal 90% and 80%, averaged over 5 seeds (mean±sd).
- **H2:** empirical coverage ≈ nominal within ±0.05 (averaged over regression tasks) at both levels.
- **Pre-declared honesty:** the scaffold test is intentionally OUT-of-distribution vs the (in-distribution) valid
  calibration set, so conformal exchangeability is violated and coverage MAY UNDER-cover. We report the true
  coverage either way; under-coverage is an honest, informative result (a known limit of conformal under covariate
  shift), not a hidden failure.

## Aim 3 — Calibrated conformal prediction-SETS (classification) coverage
Least-ambiguous-set (LAC) inductive conformal: nonconformity s_i = 1 − p̂(y_i|x_i) on calibration; q̂ as above;
test prediction set = {k : 1 − p̂(k|x) ≤ q̂}. Coverage = mean(y_test ∈ set); report mean set size, per classification
task (13), at 90%/80%, over 5 seeds.
- **H3:** empirical set coverage ≈ nominal within ±0.05 (averaged), same honest covariate-shift caveat as H2.

## Aim 4 (conditional — only if H2/H3 materially under-cover) — AD-conditioned (Mondrian) conformal
If plain conformal under-covers on the scaffold test, partition the calibration set into AD-distance quantile bins
(e.g. tertiles) and compute a per-bin q̂ (Mondrian conformal); a test molecule uses the q̂ of its AD bin — so OOD
molecules get WIDER intervals. **H4:** AD-conditioned conformal restores coverage closer to nominal (|cov−nominal|
smaller than plain) AND yields wider intervals for high-AD molecules — directly connecting Aim 1 to Aims 2/3. If
H2/H3 already hold, Aim 4 is skipped and noted.

## Ship
If the AD is validated and conformal coverage is acceptable (or fixed by Aim 4), add per-prediction uncertainty to
`ADMETPredictor` (regression pi_low/pi_high; classification prediction-set/confidence), calibrated via an internal
train/calibration split, OPTIONAL (default off → B30 behavior unchanged). Honest scope unchanged: an in-silico
screening filter, scaffold-split only, NOT a safety guarantee.

## Reproducibility
Deterministic (seed=42; TDC seeds fixed [1..5]; fingerprints cached). Reproduce ×2 byte-identical (payload sha256).
Provenance JSON: git_sha, python, libs, seeds, timestamp. Output:
`experiments/B30b_admet_uncertainty/results/B30b_metrics.json`.
