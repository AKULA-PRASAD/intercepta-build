# Pre-registration — B17: does inferred-FLT3-dependency predict CLINICAL OUTCOME (survival) benefit from FLT3 inhibitors? (FINALIZED 2026-07-29, PRE-RESULT)

## The question (the one test that would push V19 toward the clinic)
V19 showed inferred-FLT3-dependency predicts FLT3-inhibitor **ex-vivo** response beyond FLT3-ITD. The next rung is
**clinical outcome**: among BeatAML patients, does higher inferred-FLT3-dependency mark greater *survival benefit*
from receiving a FLT3 inhibitor? A predictive biomarker (benefit differs by marker) — NOT a prognostic one.

## Why this is hard in BeatAML (documented BEFORE running — sets honest interpretation)
1. **No treatment timing / dates.** FLT3i exposure is recoverable only from the cumulative-regimen text, which
   spans the entire disease course. => **Immortal-time bias**: "received FLT3i" partly means "survived long enough
   to reach a later line." This bias inflates *apparent* FLT3i benefit.
2. **No first-line FLT3i.** `typeInductionTx` is "Standard Chemotherapy" for ~550/556; only 3 kinase-inhibitor
   inductions. So a clean t0-anchored (immortal-time-free) exposure is unavailable.
3. **Confounding by indication + non-randomization.** FLT3i was given preferentially to FLT3-mutated / fitter /
   transplant-eligible patients; FLT3i is co-administered with intensive chemo and transplant.
4. Era effects across BeatAML waves.

**Consequence (fixed):** the known biases push toward a *spurious positive* interaction. Therefore a **NULL
interaction is the cleanly interpretable, robust outcome**; a **positive interaction is confounded and CANNOT be
claimed as clinical validation** — at most it is hypothesis-consistent and motivates prospective testing.

## Data (public + controlled BeatAML)
- Inferred FLT3 dependency: engine `fit_dependency(["FLT3"])` (DepMap CRISPR) applied to BeatAML patient RNA;
  oriented as `dep_score = -inferred_gene_effect` (higher = more FLT3-dependent), z-scored.
- FLT3i exposure: `flt3i = 1` if cumulative regimen text names any of sorafenib/midostaurin/gilteritinib/
  quizartinib/crenolanib/lestaurtinib/sunitinib, else 0.
- Outcome: `overallSurvival` (days) + `vitalStatus` (Dead=event / Alive=censored).
- Covariates: FLT3-ITD (0/1), R_prolif (z), age at diagnosis (z, if available).

## Model & hypotheses (assumed FALSE)
Cox PH (statsmodels PHReg) on OS:
`h(t) ∝ exp(β1·dep_score + β2·flt3i + β3·dep_score×flt3i + β4·ITD + β5·R_prolif + β6·age)`
- **Primary H1 (predictive benefit):** interaction β3 < 0 (HR<1) with p<0.05 — more-FLT3-dependent patients gain
  MORE survival benefit from FLT3i. (Direction fixed a priori: dep is prognostically adverse [β1>0 expected], and
  FLT3i is hypothesized to *reverse* that in dependent tumors.)
- Secondary (descriptive, not claims): within FLT3i-treated, dep_score→OS (expect protective if predictive);
  within untreated, dep_score→OS (expect adverse/prognostic).
- H0: β3 not significant / wrong sign — inferred-dependency does not mark FLT3i survival benefit in this cohort.

## Decision rule & interpretation (fixed)
- **H1 fails (null or wrong sign):** honest negative — no evidence in BeatAML that inferred-FLT3-dependency marks
  FLT3i *survival* benefit. Given (1)-(4) bias toward positive, this is a strong, interpretable negative and
  confirms the clinical endpoint needs prospective data (Track-1). First-class result.
- **H1 passes (β3<0, p<0.05):** hypothesis-CONSISTENT but **confounded by immortal-time / indication**; reported
  strictly as exploratory motivation for Track-1, NOT as clinical validation. No clinical claim is made either way.

## Honesty / scope
BeatAML retrospective, non-randomized, no treatment dates. This test cannot establish causal clinical benefit;
its role is to (a) look for a signal and (b) bound what retrospective data can and cannot show — either way the
validated clinical endpoint requires the prospective Track-1 design.

## Reproducibility
Deterministic; reproduce ×2. Output: experiments/B17_clinical_outcome/results/B17_metrics.json.
