# INTERCEPTA — the real path to the breakthrough (Phase C: new-data generation)

The honest premise (earned, not assumed). Every in-silico lead on **existing public/ex-vivo data has been tested
to the ceiling** (LEDGER B1–B11): cell-line transfer is real but weak and capped (+0.212); AML mutation→drug
markers are robust only for textbook axes (FLT3-ITD, RAS) and novel candidates do **not** replicate cross-system
(B11, 0/13); ex-vivo drug-specificity is weak/borderline; and **human clinical response is a well-powered NULL,
driven by cancer-type confounding** (B10). Therefore **the breakthrough is not extractable by more computation on
public data** — pursuing it there would be p-hacking, which the Constitution forbids. The breakthrough requires
**generating the right new data.** This document specifies exactly what, why, how, and what would count as success
or failure. The computational engine (`src/intercepta`, validated + tested) is the analysis layer that plugs into
each track unchanged.

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
**Pre-registered test (protocol frozen, `prereg/` pattern):** the engine (trained on cell lines) predicts ex-vivo
AUC per drug (replicate V9 at n≥300, powered); and — the new part — ex-vivo response predicts *clinical* outcome
(closing the ex-vivo→clinic gap). Confound control: within-cancer, proliferation-residualized, permutation.
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

## The one honest, no-p-hacking computational step still available (Track-2a, public)
Test whether the engine's mechanism markers align with **DepMap CRISPR gene-dependencies** — a *different data
modality*, so it is genuine cross-modality validation, not re-mining the same drug-response data. This is the
single remaining public analysis that could add real signal without fabrication; it is queued as experiment B12.

## Honest probabilities
- P(Track 1 yields a powered, confound-controlled drug-specific patient signal): moderate — our best real signal
  (V9) is genuine but weak; n and prospective design are the variables.
- P(Track 2 yields a validated novel vulnerability): low–moderate (B11 already argues against the current novel hits).
- P(Track 3 clinical win): unknown; contingent on Tracks 1–2.
No track is guaranteed. What IS guaranteed: each is pre-registered and honest, so a null is a real result and the
program never overclaims. That integrity is the asset that makes the breakthrough — if it exists — believable.
