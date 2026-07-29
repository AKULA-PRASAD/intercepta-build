# Pre-registration — B3c (L1b external replication): does the drug-specific patient signal replicate with INDEPENDENT labels? (FINALIZED 2026-07-29, pre-run)

## Motivation
B3b/L1b found a weak but drug-specific, proliferation-independent cell-line→patient signal (residualized
diag−off = +0.040, perm p=0.010) using GDSC2 LN_IC50 labels. Per the Constitution, a positive is guilty until
it survives external replication. B3c repeats the EXACT B3b pipeline but swaps the drug-response label source
to **GDSC1** — an independent screen (different experiments, different drug panel) — keeping DepMap RNA-seq
training expression and BeatAML patient test identical.

## Question
With GDSC1 (independent) labels, does the proliferation-residualized drug-specific patient signal replicate
(residualized diag > off, perm p<0.05, same sign), or was B3b a single-screen artifact?

## Hypothesis (assumed FALSE)
- H1_rep: residualized diagonal mean ρ > off-diagonal AND > 0, permutation p<0.05, on the GDSC1-labeled run.
- H0: no drug-specific residual signal with independent labels → B3b does not replicate; downgrade L1b to
  PROVISIONAL / single-screen.

## Data
Identical to B3b except labels: GDSC1 `GDSC1_fitted_dose_response.xlsx` (COSMIC_ID, DRUG_NAME, LN_IC50), joined
to DepMap RNA-seq via COSMIC↔DepMap. Test = BeatAML patient RNA + ex-vivo AUC. sha256 in MANIFEST.

## Design / metric / rule
Identical to B3b (per-drug Ridge, top-2000 DepMap-variance shared genes, ≥30 train / ≥15 patients,
proliferation-residualized diagonal vs off-diagonal, permutation k=2000 seed=42). REPLICATION PASS iff
residualized (diag−off) > 0 AND perm p<0.05 (same direction as B3b).

## Interpretation grid (fixed in advance)
- PASS → L1b upgraded: drug-specific patient signal replicates across two independent screens → the strongest
  evidence yet that cell-line models carry genuine drug-level information to patients (still weak, ρ~0.07;
  still needs a second patient cohort for full external validity).
- FAIL → L1b downgraded to PROVISIONAL: report B3b honestly as not-replicated with independent labels;
  conclude the patient-reaching signal is (at current power) not robustly drug-specific.

## Reproducibility
Deterministic; seed=42, k=2000; reproduce ×2. Output: `experiments/B3c_external_replication/results/B3c_metrics.json`.
