> **[SUPERSEDED 2026-08-07 for the North Star]** This is the CANCER drug-response era roadmap (Phase C: new-data
> generation for the patient-prediction line). It remains the honest record of that branch. The current, governing
> invention plan for the zero-data any-disease North Star is **`docs/INVENTION_ROADMAP.md`**.

# INTERCEPTA — the real path to the breakthrough (Phase C: new-data generation)

The honest premise (earned, not assumed). The in-silico search on **existing public data is now exhausted across
five independent fronts** (LEDGER B1–B22), each pre-registered and reproduced ×2:
1. **Cell-line transfer** is real but weak and capped at ρ≈+0.212 — a hard ceiling (B1/B2/V7).
2. **Adding driver mutations** to the transcriptome does not beat it (B2/V7).
3. **A second baseline modality — mass-spec proteomics — does not beat or add to RNA** (B22/V21): the ceiling is a
   property of baseline molecular profiling itself, not of one assay.
4. **Human clinical response is a well-powered NULL**, entirely cancer-type confounding (B10).
5. **The most promising functional idea — inferring CRISPR gene-dependency from expression** — beat the FLT3-ITD
   biomarker *within BeatAML* (V15–V20, proliferation-, mutation-, and lineage-independent, target-specific) but
   **FAILED external replication** in an independent AML cohort (FIMM/Malani, B20/B21); the known biology
   replicated, our inferred refinement did not.

Together these force one conclusion: **no static/baseline molecular profile — RNA, protein, or mutation — resolves
within-lineage drug specificity, and a functional layer *inferred* from cell lines does not transfer between
patient cohorts.** The breakthrough is therefore not extractable by more computation on public data (pursuing it
there would be p-hacking, which the Constitution forbids). It requires **functional/perturbation readouts measured
IN the patients themselves** — i.e., generating the right new data. Point 5 is the decisive lesson: functional
signal is real and powerful but must be *measured*, not *inferred*. This document specifies exactly what, why, how,
and what would count as success or failure. The validated, tested engine (`src/intercepta`) is the analysis layer
that plugs into each track unchanged.

## What "breakthrough" means here (concrete, falsifiable)
A **prospectively-validated, drug-level, confound-controlled predictor of patient therapeutic response** — i.e.,
given a new patient's tumor molecular profile, a ranked recommendation that beats standard-of-care selection in a
pre-registered, controlled comparison. Nothing short of a prospective, confound-controlled result counts (B10
proved observational data cannot).

---

## Track 1 (highest priority) — Functional-precision cohort: fresh patient samples, ex-vivo drug screen + matched multi-omics + outcome
**Why:** directly defeats the two things that killed the human test — regimen attribution and cancer-type
confounding — by measuring *per-drug* response on each patient's own tumor cells, with matched RNA/WES, ideally
linked to clinical outcome. This is the BeatAML design (which gave our only real drug-specific signal, V9)
extended prospectively and to new cancers.
**Data to generate/acquire:** ≥300 patients, one or two tumor types (AML first — infrastructure exists; then a
solid tumor via organoids/PDX), ex-vivo drug-response (AUC) for a panel overlapping GDSC/PRISM, matched tumor
RNA-seq + WES, and ≥1-year clinical follow-up where feasible.
**Pre-registered test (protocol frozen, `prereg/` pattern):** (a) the engine (trained on cell lines) predicts
ex-vivo AUC per drug (replicate V9 at n≥300, powered); (b) the **measured** functional readout (each patient's own
ex-vivo response / dependency) predicts *clinical* outcome, closing the ex-vivo→clinic gap; and (c) — directly
testing the B20 lesson — **measured** per-patient functional response outperforms the **inferred-from-baseline**
dependency layer (which failed to transfer between cohorts). Confound control throughout: within-cancer,
proliferation-residualized, permutation, and — for the outcome endpoint — treatment-timed (avoiding the
immortal-time bias that made the retrospective BeatAML survival test uninterpretable, B17).
**Success:** drug-specific transfer ρ replicates AND ex-vivo→clinical concordance is significant. **Falsify:**
if drug-specificity is again ρ≈0.07 and doesn't beat proliferation at n≥300, the transcriptomic-transfer thesis is
bounded and we pivot to Track 2.
**Resources:** a functional-precision-oncology lab/clinical partner; ~$; 12–24 months. Ready-to-file access
protocol for existing controlled functional cohorts is in `docs/SECOND_COHORT_VALIDATION.md`.

## Track 2 — Perturbation-anchored mechanism discovery (turn hypotheses into validated vulnerabilities)
**Why:** B5 raised novel mutation→drug hypotheses that don't replicate observationally (B11) — but observational
non-replication ≠ biologically false; it means they need *interventional* testing. Cross-modality evidence
(DepMap CRISPR gene-dependencies) can pre-filter which hypotheses are worth a wet-lab test.
**Data:** (a) public, now — DepMap CRISPR/Chronos dependencies to test whether engine markers align with genetic
dependencies (a cheap, honest cross-modality pre-filter, runnable in-repo); (b) new — a targeted CRISPR or
drug-combination screen on the surviving 3–5 hypotheses in isogenic/patient-derived models.
**Success:** a mutation→vulnerability that is validated interventionally in an independent model = a genuine novel
therapeutic hypothesis. **Falsify:** none survive the CRISPR pre-filter → the novel B5 hits were artifacts (as
B11 already suggests).

## Track 3 — Prospective biomarker-stratified trial (the clinical breakthrough)
**Why:** the only design that can establish therapy *selection* (falsified observationally at n=988). A
treatment×biomarker randomized/stratified trial where the engine's ranking is the biomarker.
**Data:** prospective enrollment, single-agent or defined-regimen arms, pre-treatment molecular profile, RECIST
+ survival. **Success:** engine-guided arm beats standard selection, pre-registered. This is a multi-year,
multi-institution, funded undertaking — the top of the ladder.

---

## What is READY now (so new data yields answers immediately)
- Validated, tested engine + CLI (`intercepta`); frozen pre-registration templates; the full falsification
  battery (permutation, leakage, BH-FDR, within-cancer confound control, cross-system replication) as reusable
  code. A new cohort needs only a loader; the analysis runs unchanged and reproducibly.

## Status of the public computational steps (now COMPLETE)
The cross-modality idea — inferring **DepMap CRISPR gene-dependency** from expression and using it as the
predictor — was executed (experiments B12–B21, LEDGER V15–V20). It was the program's most promising result: within
BeatAML it beat the FLT3-ITD biomarker, was proliferation/mutation/lineage-independent, and was target-specific.
**But it failed external replication (B20/B21)**, and a matched proteomic modality did not break the ceiling
either (B22). These are not failures of effort — they are the decisive, pre-registered results that (a) exhaust the
honest public-data computational space and (b) prove the point of Track 1: *functional signal must be measured in
the patient, not inferred from cell lines.* No further public re-mining is scientifically defensible.

## Honest probabilities (updated after B16–B22)
- P(Track 1 yields a powered, confound-controlled drug-specific patient signal): **moderate** — the *measured*
  ex-vivo functional readout is exactly what carried real signal (V9, and V19 within-cohort); the open variables
  are n, prospective design, and closing the ex-vivo→clinical link.
- P(an *inferred-from-baseline* layer would have generalized): **low** — directly falsified (B20/B21); this is why
  Track 1 measures function rather than inferring it.
- P(Track 2 yields a validated novel vulnerability): **low–moderate** (B11 argues against the current novel hits).
- P(Track 3 clinical win): unknown; contingent on Tracks 1–2.
No track is guaranteed. What IS guaranteed: each is pre-registered and honest, so a null is a real result and the
program never overclaims. That integrity — a platform whose every claim survived falsification and whose two
headline negatives are reported openly — is the asset that makes the breakthrough, if it exists, believable and
fundable.
