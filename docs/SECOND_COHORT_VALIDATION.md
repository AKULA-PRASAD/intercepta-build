# Second-cohort external validation — pre-registered protocol + data-access application

The single decisive next step for INTERCEPTA: replicate the internally-validated findings (V9, V10, engine v1,
the B5 markers) in an **independent patient drug-response cohort**. This protocol is **frozen now** so it can be
executed without post-hoc flexibility the moment data is available. Requires a data-access gate (below).

## Pre-registered hypotheses (frozen 2026-07-29 — to be run UNCHANGED on the new cohort)
Given a 2nd cohort with tumor RNA-seq + a per-sample drug-response readout (ex-vivo AUC/IC50 or response) and,
ideally, somatic mutations:
- **R1 (V9 replication):** proliferation-residualized drug-specific transfer (DepMap RNA-seq→cohort) has
  diagonal ρ > off-diagonal ρ, permutation p<0.05, same direction as BeatAML.
- **R2 (V10 replication):** for shared verified-marker drugs, marker+transfer beats transfer-alone (CV) in a
  majority of pairs.
- **R3 (engine v1):** `InterceptaEngine.rank()` combined_score predicts response better than transfer-alone.
- **R4 (B5 markers):** the genome-wide-robust markers — especially **FLT3-ITD→FLT3 inhibitors** and
  **RAS→MEK** — replicate direction + significance (if the cohort has the mutations + drugs).
- **R5 (B6 OOD):** low-OOD samples are more accurate than high-OOD (confidence gate generalizes).
Decision: each Rᵢ PASS = pre-set threshold met; a finding is "externally validated" only if it PASSES here.
A null downgrades the corresponding LEDGER entry honestly.

## Candidate cohorts (in rough priority)
1. **Additional AML functional-precision cohorts** — most direct replication (same disease, same readout type):
   e.g. other ex-vivo AML drug-screen datasets with matched RNA-seq. Mostly dbGaP/EGA controlled.
2. **Solid-tumor ex-vivo / organoid / PDX drug-response** with matched transcriptomics (tests cross-cancer
   generalization) — various controlled + some public.
3. **Clinical trial cohorts with treatment×response + baseline RNA** (tests the falsified selection question at
   power) — dbGaP/EGA.
Selection rule: pick the first cohort that has (a) ≥100 samples, (b) tumor RNA-seq, (c) a per-sample
drug-response readout for ≥5 drugs overlapping GDSC, ideally (d) somatic mutations for the B5/marker tests.

## Data-access application — draft research-use statement (adapt + file under YOUR credentials)
> **Title:** External validation of a cell-line-derived, mechanism-anchored transcriptomic drug-response engine.
> **Aim:** We have developed and internally validated (single cohort) a reproducible engine that predicts
> per-drug response from tumor transcriptomics by transferring cell-line (GDSC/DepMap) models, anchored on
> genome-wide-robust somatic-mutation→drug markers (e.g. FLT3-ITD→FLT3 inhibitors, RAS→MEK). We request access
> to [DATASET] to perform a **pre-registered external replication** (protocol frozen, `docs/SECOND_COHORT_
> VALIDATION.md`) of these predictions against the dataset's drug-response measurements. **No patient-level data
> will be redistributed, published, or committed to any public repository**; only aggregate, de-identified
> summary statistics (per-drug correlations, p-values) will be reported. Analyses are read-only against the
> access-controlled data on an approved secure environment. Public code: github.com/AKULA-PRASAD/intercepta-build.
> **PI / requester:** [your name, institution, dbGaP/EGA credentials].

## Execution readiness
Code is ready: `src/intercepta/engine.py` + `experiments/B3b/B3c` (transfer), `B4`/`engine_v1_validation`
(integration), `B5` (markers), `B6` (OOD). A new-cohort loader (matching `data/MANIFEST.md` conventions) is the
only code to add; the analysis scripts run unchanged. Controlled data stays on your secure environment — never
committed (policy in `data/MANIFEST.md`, `INTEGRITY_SWEEP.md`).
