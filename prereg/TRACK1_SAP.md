# Track-1 Statistical Analysis Plan (SAP) — prospective functional-precision cohort (FROZEN 2026-07-29, PRE-DATA)

**Status:** frozen analysis plan, written before any Track-1 data exists. It locks endpoints, tests, confound
controls, power, and success/falsification thresholds so the analysis cannot be tuned to the result. It operationalizes
`docs/TRACK1_PROTOCOL.md` and `docs/BREAKTHROUGH_ROADMAP.md`, using the validated engine + falsification battery
(`src/intercepta`) unchanged. Power figures are from `experiments/track1_power/` (planning simulation, reproduced ×2).

## 1. Rationale (evidence-forced, not assumed)
On public data the program exhausted the baseline-omics avenue across five pre-registered fronts (LEDGER B1–B22):
RNA transfer is capped (+0.212); mutations add nothing; proteomics does not break the ceiling (modality-general,
B22); human clinical response is cancer-type-confounded null (B10); and an *inferred* functional layer beat the
FLT3-ITD biomarker within one cohort but FAILED external replication (B20/B21). The decisive lesson: **functional
response must be MEASURED in the patient, not inferred.** Track-1 measures it.

## 2. Objectives, endpoints, hypotheses (pre-specified; all H assumed FALSE)
- **Aim 1 — specificity-transfer replication (internal validity).** Endpoint: proliferation-residualized drug-
  SPECIFICITY = mean(diagonal) − mean(off-diagonal) of the engine-prediction × measured-ex-vivo-AUC correlation
  matrix. **H1:** specificity > 0, one-sided permutation p<0.05.
- **Aim 2a — measured functional → BINARY clinical response (translational).** Endpoint: AUROC of a pre-specified
  measured-functional score for responder vs non-responder (RECIST-style, pre-defined). **H2a:** AUROC>0.5,
  p<0.05, within-cancer-stratified.
- **Aim 2b — measured functional → SURVIVAL (translational).** Endpoint: per-SD hazard ratio of the measured-
  functional score in a Cox model. **H2b:** HR≠1, p<0.05, treatment-conditioned (see §4).
- **Aim 3 — measured beats inferred (the B20 lesson, decisive).** Endpoint: paired difference in predictive
  performance (Aim-2a AUROC and Aim-1 specificity) between the MEASURED functional readout and the
  INFERRED-from-baseline dependency layer. **H3:** measured > inferred, paired test p<0.05.
- H0 (each): null / wrong sign.

## 3. Statistical methods (exact, frozen)
- Per-drug models: engine trained on public cell lines (frozen), applied to patient RNA; per-drug Spearman vs
  measured ex-vivo AUC. Specificity via diagonal−off-diagonal with a **patient-label permutation null** (≥10,000).
- Multiplicity: Benjamini–Hochberg FDR across drugs (q<0.05); pooling via sample-size-weighted Fisher-z and
  DerSimonian–Laird random-effects meta-analysis.
- Aim 2a: logistic regression / Mann–Whitney, within-cancer stratified, permutation for pooled AUROC.
- Aim 2b: Cox proportional hazards; PH assumption checked (Schoenfeld); per-SD standardized covariate.
- All effects **proliferation-residualized** (frozen R_prolif axis) and **within-cancer** where >1 tumor type.
- Reproducibility: fixed seed (42); every result reproduced ×2 (byte-identical); code + this SAP committed before
  unblinding; analysis is run blinded to outcome for Aim 1.

## 4. Confound controls (each maps to a specific prior failure)
- **Cancer-type confounding (B10):** within-cancer stratification is mandatory for all clinical endpoints.
- **Proliferation (V2):** residualize on R_prolif; report both raw and adjusted; a signal that vanishes on
  adjustment is reported as proliferation-driven.
- **Immortal-time / confounding-by-indication (B17):** survival analyses are **treatment-timed** (exposure defined
  at a landmark or with time-varying covariates); no cumulative-regimen exposure without timing. First-line /
  defined-regimen arms preferred.
- **Single-cohort over-fitting (B20/B21):** the analysis is pre-registered and, where a second site exists, the
  primary claim requires cross-site consistency, not single-cohort significance.
- **Measured-vs-inferred (Aim 3):** the inferred layer is included precisely so its (expected) underperformance is
  quantified, not assumed.

## 5. Sample size & power (from experiments/track1_power/, reproduced ×2; PLANNING simulation)
Realistic model (imperfect proliferation estimate, reliability 0.8; pan-drug correlation 0.15), panel K=20 drugs:
- **Aim 1** (permutation): N≈**100** for ≥80% power at the observed effect size r=0.07; N≈200 at conservative r=0.05.
- **Aim 2a** (binary response, prevalence 0.35): N≈**100** at AUROC 0.65; N≈300 at AUROC 0.60; N≈75 at 0.70.
- **Aim 2b** (survival, Hsieh–Lavori): per-SD **HR 1.6** needs ~36 events (N≈60 at 60% events, ≈89 at 40%);
  HR 1.4 needs ~70 events (N≈116–174).
- **DESIGN TARGET: N≈200** (one or two tumor types; AML first). This powers Aim 1 at r=0.07 and all clinical
  endpoints at moderate effect sizes with margin; the **clinical endpoints, not Aim 1, dominate** the requirement.
  Honest caveat: power figures assume the stated effect sizes; the true clinical effect size is unknown (that is
  what Track-1 measures), so N=200 is a floor, not a guarantee.

## 6. Success / falsification (fixed in advance — both outcomes publishable)
- **Success:** Aim 1 replicates (specificity>0, p<0.05, FDR-controlled) AND at least one clinical endpoint (2a or
  2b) is significant within-cancer/treatment-timed AND Aim 3 shows measured ≥ inferred.
- **Falsification (first-class):** if at N≈200 Aim-1 specificity is again ≈0.07 and does not beat proliferation,
  AND clinical endpoints are null under confound control, the transcriptomic-functional-transfer thesis is formally
  bounded — a definitive negative that redirects to Track-2 (perturbation mechanism discovery). The design cannot
  produce an uninformative answer.

## 7. Missing data, deviations, integrity
Pre-specified handling: complete-case for primary; sensitivity analysis with multiple imputation for missing
covariates. Any deviation from this SAP is logged with date/rationale in the repo before unblinding. No endpoint,
covariate, or threshold may be added or changed after outcome data are seen. Controlled/patient data are never
committed; only aggregate metrics + this SAP are public.
