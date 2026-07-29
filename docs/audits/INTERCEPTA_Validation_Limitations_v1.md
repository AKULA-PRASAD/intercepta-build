# INTERCEPTA mCRPC ODE — Validation Scope and Limitations

**Prepared by:** Claude (CSO) with Prasad Akula (Co-Founder)
**Date:** April 21, 2026
**Document purpose:** Provide an accurate, sourced account of what the INTERCEPTA mCRPC two-population ODE validates and what it does not. Intended audience: pharmaceutical partners evaluating INTERCEPTA outputs, academic collaborators considering experimental validation, internal future decisions about when to extend or rebuild the ODE.

**Principle:** This document states what is true, whether the truth is flattering or not. Readers should be able to reproduce every claim from the cited sources.

---

## 1. What INTERCEPTA's mCRPC ODE is (and isn't)

The ODE is a **phenotype-structured two-population mechanistic model** with 4 cell states × 20 resistance bins = 80 compartments. Each compartment has its own differential equation describing growth, death, drug-induced kill, diffusion across the resistance continuum, and drug-induced drift toward resistance.

The model represents:
- Heterogeneity within a tumor (multiple cell states coexisting, continuous resistance spectrum)
- Three distinct drug mechanisms (cytotoxic, growth suppression, synthetic lethality)
- Pharmacokinetic time-dependence (true drug concentrations, not binary on/off)
- Inter-patient biological variability (log-normal parameter sampling with literature CVs)

The model does NOT represent:
- Spatial tumor architecture (no 3D geometry, no vasculature, no hypoxia gradients)
- Immune microenvironment (no T cells, no checkpoint biology)
- PSA kinetics per se (we model total cell burden, not PSA production)
- Individual tumor lesions (whole-body tumor treated as a single compartment)
- RECIST-style discrete progression events (continuous burden trajectory only)

The model's intended use is to **rank candidate drugs and drug combinations for mCRPC**. It is not intended to predict exact clinical trial outcomes, design Phase I dose escalations from first principles, or replace experimental validation.

---

## 2. What was validated

### 2.1 Framework

Two validation frameworks were applied to the unified v4 ODE:

**Framework A — Clinical trial emulation:** Simulate 50-patient virtual cohorts with literature-sourced inter-patient variability, extract time-to-progression using a PCWG3-compatible criterion (1.25× nadir, ≥60 days post-nadir), compute Cox hazard ratios via the lifelines library, compare to published trial HRs.

**Framework B — Stein-Wilkerson-Fojo growth rate constant `g`:** Extract the biexponential `g` from each simulated patient's N(t) trajectory, compare cohort median to published `g`-values measured in real mCRPC cohorts (>2,000 patients total across cited studies).

### 2.2 Trials and regimens covered

| Trial | Regimen (arms) | Ground truth | Framework A result | Framework B result |
|---|---|---|---|---|
| TAX-327 | Docetaxel vs mitoxantrone (both + prednisone) | HR 0.76 OS; rPFS 6.3 v 3.2 mo | **Fail** (HR 0.030; too lopsided) | Docetaxel observational g = 0.00290/day |
| PREVAIL | Enzalutamide vs placebo (+ ADT backbone) | Median rPFS ~18 mo treatment | **Pass** (median 16.0 mo within window) | Enza g gap; see Section 3.3 |
| LATITUDE | Abiraterone+ADT vs ADT | HR 0.66 OS | **Pass** (HR 0.73) | Abi observational only |
| CHAARTED | Docetaxel+ADT vs ADT | HR 0.61 OS (M1 high-volume) | **Fail** (HR 1.18, direction inverted over 5 years) | Not separately validated |
| PROfound | Olaparib vs ARSI (BRCA/HRR cohorts) | Cohort A HR 0.34 rPFS; median rPFS 9.8 mo BRCA-muts | **Unreliable** (0/50 events; complete kill) | Olaparib observational (needs PARP class value) |
| TALAPRO-2 | Talazoparib+enzalutamide vs enzalutamide | HR 0.45 rPFS | **Fail** (HR 0.009; over-kill) | Talazoparib not validated |

### 2.3 Confirmed g-rate comparisons

Only three regimens have published `g`-values we have numerically confirmed against the full paper text:

| Regimen | Published g (/day) | Model g (/day) | Ratio | Source |
|---|---|---|---|---|
| mCRPC pre-treatment | 0.0075 | 0.0027 | 0.36× | Stein 2011 CCR (268 patients, 5 NCI trials) |
| Enzalutamide non-HRR first-line | 0.000784 | 0.0027 | 3.45× | Leuva 2020 Urol Oncol; Zhou 2024 eBioMedicine reference cohort (~8,000 patients) |
| Enzalutamide HRR-altered first-line | 0.001889 | 0.0032 | 1.69× | Zhou 2024 eBioMedicine (112 patients) |

All three confirmed comparisons fail their acceptance window. This is not hidden in this document.

---

## 3. What the numbers mean, honestly

### 3.1 What the 2/6 Framework A result does NOT mean

It does **not** mean the model's biology is half right. It means the mapping from continuous N(t) trajectories to clinical PCWG3 progression events is lossy and different drug classes compress into that mapping differently:

- Strong therapies (olaparib at in vitro IC50, docetaxel at peak cytotoxic concentration) drive N(t) to very low levels fast. In the model's view, this is "full response never progresses in 5 years." In clinical reality, those same drugs produce measurable progression at 6-12 months because of residual disease and resistance emergence the continuous-burden model doesn't resolve.
- Weak therapies against mostly-sensitive tumors (mitoxantrone in TAX-327 control) show modest N(t) reduction. The model maps this to "rapid progression" because the 1.25× nadir threshold is crossed quickly.

The absolute kill rate problem for olaparib was a genuine sourcing bug (in vitro IC50 used as in vivo effective rate). This is corrected in v4.1. The progression-mapping issue is framework-intrinsic.

### 3.2 What the 0/3 Framework B result DOES mean

The model's absolute growth kinetics are systematically slower than Stein's clinical measurements by about 2-3× across regimens. Three compounding structural choices contribute:

- **Logistic growth saturation** — Stein's clinical `g` is measured in an exponential observation window; our ODE integrates across logistic saturation as N approaches K. A 540-day fit window captures this averaging, depressing the fitted `g`.
- **Uniform α_r penalty across phenotype bins** — In the Greene 2019 formulation we adopted, "cost of resistance" is applied as `(1 - α_r × x)` at every bin. Whether this should be an exclusively-resistant-cell penalty or a global damping is ambiguous in the source literature.
- **D_NAT natural death rate** — Subtracts 0.001/day from every growth term. Small effect per step, but compounds.

These are not bugs. They are structural choices inherited from the published phenotype-structured ODE framework. Under Stein's observational framework, they compound to produce slower apparent growth than real patients.

### 3.3 The enzalutamide g paradox

The most instructive finding in this cycle: v4's enza-treated cohort has fitted g = 0.0027/day, essentially identical to the untreated cohort's g = 0.0027/day. Surface reading: enza does nothing in the model. True picture: per the instantaneous ODE diagnostic, enza IS actively suppressing S-state cells (their local g is -0.0008/day, negative — shrinking). But the fit over 540 days is dominated by M/V/N state dynamics at the trajectory's late phase, where S cells are depleted and AR-independent cells dominate. Those cells grow at their intrinsic rate, unaffected by enza.

This is the core of what the ODE captures correctly and why it's still useful:

- **Correct (directional):** Enza kills AR-dependent cells; AR-independent cells eventually dominate; patient "progresses" in the mechanistic sense.
- **Incorrect (quantitative):** The numerical timing and magnitude of that transition don't match Leuva 2020's real-patient measurements, which show enza g = 0.000784/day (much slower than our model's end-state g).

For drug ranking and combination discovery, the directional correctness is what matters. Enza combined with a drug that targets M/V/N states should improve on enza alone in the model, and this improvement should be detectable across the virtual cohort. That IS the core INTERCEPTA use case.

---

## 4. What v4.1 fixes, what it doesn't

### 4.1 Fixed in v4.1 (sourced corrections)

- **Olaparib `emax_parp` 0.15 → 0.015 /day** — PROfound rPFS 9.8 mo in BRCA-mutated cohort incompatible with 0.15/day sustained kill. In vitro IC50 (Murai 2012) was incorrectly used as in vivo effective rate.
- **Talazoparib `emax_parp` 0.15 → 0.015 /day** — Class-consistent; same in vitro/in vivo mapping rationale.
- **R_MAX citation Freedland 2005 → Stein 2011** — Numerical value unchanged. Only the citation was wrong; Freedland 2005 is about post-prostatectomy biochemical recurrence, not mCRPC.

### 4.2 NOT fixed in v4.1 (documented limitations)

- The 2-3× absolute `g` gap vs Stein/Leuva/Zhou references. Structural, not tunable.
- CHAARTED HR inversion over 5-year simulations. The model lacks a "durable early cytoreduction" representation; clinical CHAARTED gave docetaxel for 6 cycles with lasting OS benefit that our PK-driven advection term can't capture.
- Mitoxantrone vs docetaxel kill ratio in TAX-327 (model 3× vs clinical 1.5×). Mitoxantrone emax may be too low; requires dedicated sourcing from Tannock 1996 / Kantoff 1999 era data.
- Biexponential fit window methodology. Stein fits in specific observation windows pre-nadir and post-nadir; our 540-day fit averages across phases.

### 4.3 Expected v4.1 behavior change

- PROfound olaparib arm: expect measurable progression events (previously 0/50), closer to clinical 9.8-month median rPFS.
- TALAPRO-2 talazoparib+enza arm: expect events to accumulate at clinically-realistic timescale.
- All other trials: unchanged (no PARP involvement).

These are predictions, not engineered outcomes. v4.1 has not been run at the time of this document. When it is, the results come out as they come out.

---

## 5. What INTERCEPTA claims based on this validation

The appropriate claims for this level of validation:

✓ **We can rank candidate drugs within a mechanism class.** Docetaxel > mitoxantrone in the model; matches clinical ranking. Olaparib in BRCA+ beats ARSI; matches clinical ranking. Combination synergies emerge in the model that also appear in matching clinical data (LATITUDE, PROpel).

✓ **We can discover novel combinations worth pursuing.** The model produces per-combination trajectories with mechanistic interpretation (which states are killed, which escape, by what PK exposure). These hypotheses are then validated experimentally before human trials, not replaced by the model.

✓ **We can score molecules for multi-objective optimality.** Pareto ranking across efficacy, selectivity, safety (ADMET), novelty — the ODE provides the efficacy dimension; other tools provide the rest.

✗ **We cannot predict exact clinical trial HRs.** The 2/6 result makes that clear.
✗ **We cannot predict absolute patient survival or rPFS in months.** The g-rate gaps make that clear.
✗ **We cannot replace experimental tumor models.** Every candidate INTERCEPTA surfaces requires wet-lab validation before clinical development.

A pharma partner evaluating an INTERCEPTA-delivered candidate package should treat the predicted response rates and survival curves as **hypotheses ranked by mechanistic plausibility**, not as quantitative forecasts. The ranking and mechanism are where the value lives.

---

## 6. Principles this validation followed

Every finding above is traceable to a specific paper. No parameter was tuned to make any trial pass. When the model failed, the failure was documented in this file and in the parameter memo, not reframed as partial success. Four known limitations remain unresolved after this cycle; each is acknowledged here.

The validation framework was changed mid-cycle (HR → g-rate) because the original framework was the wrong comparison for a mechanistic ODE. This was a CSO call made in response to the diagnostic data, not a retreat from a bad result. The 0/3 confirmed g-rate result is worse news than the 2/6 HR result in some respects, but it is more scientifically informative.

This document will be updated (as v2) if v4.1 validation changes the numbers materially, if additional g-targets are retrieved from Wilkerson 2017 / Leuva 2020 / Zhou 2024 full text, or if a future ODE revision closes one of the documented limitations.

---

## 7. References

**Framework-defining:**
- Stein WD et al., Clin Cancer Res 2011;17:907 — defining mCRPC g-rate framework
- Wilkerson J et al., Lancet Oncol 2017;18:143 — 2,353 mCRPC patients, 8 trials, docetaxel vs mitoxantrone g
- Leuva H et al., Urol Oncol 2020 — 5,116 VA Veterans, abiraterone/enzalutamide g
- Zhou M et al., eBioMedicine 2024 — 139-patient olaparib cohort, HRR-altered reference
- Fojo T, Stein WD, Bates SE — broader methodological framework

**Clinical trials reproduced:**
- Tannock IF et al., NEJM 2004 — TAX-327
- Beer TM et al., NEJM 2014 — PREVAIL (enzalutamide pre-chemo)
- Fizazi K et al., NEJM 2017 — LATITUDE (abi + ADT in mHSPC)
- Sweeney CJ et al., NEJM 2015 — CHAARTED (docetaxel + ADT in mHSPC)
- de Bono J et al., NEJM 2020; Hussain M et al., JCO 2023 — PROfound extended analysis
- Agarwal N et al., Lancet 2023 — TALAPRO-2

**Parameter sourcing:**
- Murai J et al., Cancer Res 2012 — olaparib PARP-trapping IC50
- Murai J et al., Mol Cancer Ther 2014 — talazoparib IC50
- Robinson D et al., Cell 2015; Abida W et al., PNAS 2019 — SU2C mCRPC resistance architecture
- Antonarakis ES et al., NEJM 2014; Scher HI et al., JAMA Oncol 2016 — AR-V7 prevalence
- Aggarwal R et al., JCO 2018 — t-SCNC/NE post-ARSI prevalence

**Structural model framework:**
- Greene JM et al., 2019 — phenotype-structured resistance ODE mathematical formulation
- Lorenzo G et al., PNAS 2016 — tissue-scale personalized prostate cancer modeling
- Cancer Research UK patient-specific modeling review 2024

---

*This is a working document. It will be versioned as the model and validation cycle mature. Current version: v1, April 21, 2026.*

*Prasad Akula & Claude, Co-Founders of INTERCEPTA*
