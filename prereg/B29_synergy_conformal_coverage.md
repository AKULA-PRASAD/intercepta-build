# Pre-registration — B29: are the synergy tool's conformal prediction intervals CALIBRATED? (FINALIZED 2026-07-29, PRE-RESULT)

## The question (validate the uncertainty, don't just add it)
We added conformal prediction intervals to SynergyRanker (interval = prediction ± q, q from leave-combination-out
residuals). Uncertainty is only honest if its COVERAGE is validated: does the nominal (1−α) interval actually
cover ≈(1−α) of held-out synergy values for NEW drug combinations?

## Design (split-conformal, disjoint by combination — textbook, honest)
On O'Neil synergy (and DrugComb as a second corpus), over 5 seeds: split unique drug PAIRS disjointly into
proper-train (60%) / calibration (20%) / test (20%). Fit the SynergyRanker pipeline on train-pair rows; set
q(α)=quantile(|pred−y|, 1−α) on the calibration rows; measure empirical coverage = mean(|pred−y| ≤ q) on the
test rows. Because train/cal/test are disjoint by combination, this is valid coverage for UNSEEN combinations.
Report for nominal 80% (α=0.2) and 90% (α=0.1), averaged over seeds, plus mean interval half-width.

## Hypotheses (assumed FALSE)
- **H1 (calibrated):** empirical coverage ≈ nominal within ±0.05 (e.g., 90% interval covers 85–95%), for both
  nominal levels, in O'Neil.
- H0: empirical coverage deviates > 0.05 from nominal → intervals are miscalibrated (report honestly; do not ship
  as calibrated).

## Decision rule & interpretation (fixed)
- **H1 PASS** → the intervals are calibrated (or conservative if coverage > nominal); ship the uncertainty as
  validated, reporting the typical interval width so users see the (large) uncertainty honestly.
- **H1 FAIL (under-coverage)** → intervals too narrow → miscalibrated; report and either widen or label as
  approximate. **Over-coverage** → conservative but valid (acceptable, noted).
- Expect wide intervals: synergy is noisy and leave-combination-out residuals are large — an honest interval will
  be WIDE, which is itself the honest message (point predictions carry substantial uncertainty).

## Honesty / scope
Cell-line Loewe synergy. Split-conformal gives MARGINAL (average) coverage, not per-instance/conditional coverage;
OOD-flagged pairs may have worse local coverage (stated). A miscalibration finding is first-class. Deterministic
(seeds fixed); reproduce ×2. Output: experiments/B29_synergy_conformal_coverage/results/B29_metrics.json.
