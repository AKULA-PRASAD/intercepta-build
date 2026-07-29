# Pre-registration — B6: is the engine's confidence signal actually calibrated? (FINALIZED 2026-07-29, pre-run)

## Question
The engine now emits two candidate confidence signals: per-drug **CV reliability** (cell-line 5-fold Spearman)
and per-sample **OOD distance** (distance to the training cell distribution). Do EITHER actually predict real
patient-transfer accuracy on BeatAML? A confidence signal is only shippable if it tracks accuracy.

## Hypotheses (assumed FALSE)
- **H1 (per-drug reliability):** across drugs, cell-line CV reliability positively correlates with patient
  transfer accuracy (Spearman of drug transfer_pred vs BeatAML AUC). [Note: B3e H2 found this NULL on 4 verified
  pairs; B6 re-tests with power across ALL fitted drugs.]
- **H2 (per-sample OOD):** samples closer to the training distribution (low OOD) have higher transfer accuracy
  than far (high OOD) samples.
- H0: neither signal tracks accuracy → the engine cannot yet calibrate confidence; it stays conservatively LOW.

## Design / metric / rule (fixed)
- Fit engine on all drugs (≥30 patients w/ AUC). Per drug: `patient_rho` = Spearman(transfer_z, AUC) [higher = 
  better ranking]; `cv_rho` = engine drug reliability.
- **H1:** Spearman(cv_rho, patient_rho) across drugs; permutation p (shuffle, k=2000, seed=42). PASS iff ρ>0 & p<0.05.
- **H2:** split samples at median OOD; per drug compute patient_rho in low-OOD vs high-OOD halves; paired
  difference across drugs; sign-flip permutation p. PASS iff low-OOD mean > high-OOD mean & p<0.05.

## Consequence (fixed in advance)
- If H1 passes → drug reliability becomes a shippable confidence axis (MED/HIGH tiers by cv_rho).
- If H2 passes → OOD distance gates confidence (flag high-OOD samples).
- If BOTH null → HONEST outcome: engine confidence stays LOW for all; calibration deferred to a 2nd cohort.
  The metrics remain in the output as descriptive, explicitly NOT validated.

## Honesty
Prior on H1 is LOW (B3e). A null is fully expected and is a first-class result — it prevents shipping a fake
confidence signal. BeatAML is one cohort.

## Reproducibility
Deterministic (seed=42, k=2000); reproduce ×2. Output: `experiments/B6_calibration/results/B6_metrics.json`.
