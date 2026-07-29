# INTERCEPTA — MASTER FIX LIST
# Generated: April 18, 2026
# Purpose: Every bug, weak claim, and missing piece with exact file + fix

---

## PRIORITY 1 — BREAKS CORE CLAIMS (fix before anything else)

### FIX-001: HR estimator is mathematically wrong
- **File:** `code/intercepta_engine_v1.py` → `estimate_hr()` method
- **File:** `code/intercepta_phenotype_ode_v1.py` → `VirtualCohort.estimate_hr()`
- **Bug:** `hr = median_ctrl / median_trt` — this is NOT a hazard ratio.
  Only valid under exponential survival. Actual trials use log-rank / Cox.
- **Impact:** ALL HR outputs (TAX-327, CHAARTED, PROpel) could be wrong by 20-40%.
- **Fix:** Replace with `lifelines` library:
  ```python
  from lifelines import KaplanMeierFitter
  from lifelines.statistics import logrank_test
  # or for proper Cox HR:
  from lifelines import CoxPHFitter
  ```
  Use `logrank_test(ctrl_ttps, trt_ttps, event_observed_A, event_observed_B)`
  and `CoxPHFitter` for the actual HR estimate with confidence intervals.
- **Effort:** 1 day. HIGH PRIORITY — this either confirms or breaks TAX-327 validation.

---

### FIX-002: AML ODE never predicts relapse
- **File:** `results/aml_ode_v6_validation.json`
- **Bug:** Every treated arm shows `"rel_mo": null` — no relapse predicted.
  Real AML relapses in 40-60% of patients after 7+3 induction.
- **Impact:** AML model is biologically wrong. Cannot be presented as AML modeling.
- **Root cause:** Likely the resistant cell population (R) never regrows
  because mu (S→R transition) is too low, or emax_r kills R too efficiently.
- **Fix needed:**
  1. Check `aml_ode_v6_resistance.py` — print R(t) separately over 24 months
  2. Calibrate mu and emax_r so R regrows after induction clearance
  3. Target: ~50% relapse at 12-18 months post-CR (matches NEJM data)
- **Effort:** 2-3 days.

---

### FIX-003: KAALCURA never validated on real GDSC data
- **File:** `code/intercepta_kaalcura_v1.py` → `run_full_validation()`
- **Bug:** The entire validation runs on `create_synthetic_gdsc_data()` — 
  fake data where axes ARE correct by construction. This proves nothing.
  Claimed AUROCs (0.600, 0.585, 0.629) are from synthetic data, not GDSC.
- **Impact:** The core sensitivity prediction claim is unvalidated on real data.
- **Fix:** Run KAALCURA on real GDSC expression + IC50 data already in:
  `data/gdsc/GDSC2_fitted_dose_response.xlsx`
  `data/gdsc/sanger_model_gene_expression.csv.gz`
  If real AUROC < 0.55, the axis framework needs rethinking.
- **Effort:** 1-2 days. CRITICAL for any external presentation.

---

### FIX-004: Scout 4 compensation logic is WRONG
- **File:** `code/scout4_boolean_network.py` and `code/scout4_network_perturbation.py`
- **Bug:** From NEXT_SESSION.md: "Scout 4 v1: Dependency works, compensation WRONG"
- **Fix needed:**
  1. Implement proper Boolean network with directed edges from SIGNOR
     (`data/signor/signor_all_data.tsv` — already downloaded)
  2. Boolean rule: `gene ON if (activator1 OR activator2) AND NOT inhibitor`
  3. Find steady-state attractors (disease vs healthy)
  4. Perturbation: set target OFF → find new attractor
  5. Compensation = genes that flip ON in new attractor
  6. Validate: FLT3 perturbation → compensators match BeatAML resistance
- **Reference:** Montagud et al. eLife 2022
- **Effort:** 3-4 days.

---

## PRIORITY 2 — WEAK CLAIMS (fix before publishing or presenting)

### FIX-005: Axis independence threshold silently relaxed
- **File:** `code/intercepta_kaalcura_v1.py` → `validate_axes_independence()`
- **Line:** `passed = abs(r) < 0.05  # Relaxed from 0.02 for initial validation`
- **Bug:** MathSpec Section 2.3 claims `|r| < 0.02`. Code actually uses 0.05.
  The claim in STATUS.md is based on the relaxed threshold.
- **Fix:** Either achieve |r| < 0.02 with proper residualization on real GDSC,
  OR update MathSpec to say |r| < 0.05 and justify it statistically.

---

### FIX-006: Emax values are not fully data-derived
- **File:** `code/intercepta_phenotype_ode_v1.py` → `DRUG_EFFECT_LIBRARY`
- **From phenotype_ode_v1_1_verified.json:** `"Emax=0.08/day not data-derived"`
- **Lines:** docetaxel emax=0.153 comment says "0.85/day x 0.18 in vivo correction (data-derived)"
  but the 0.18 correction factor is assumed, not from a published source.
- **Fix:** Find published in vitro → in vivo PD scaling ratios for docetaxel.
  Suggested source: Simeoni et al. 2004 (J Pharmacol Exp Ther) TGI model.
- **Effort:** 1 day research + update.

---

### FIX-007: AR_SLOPE=3.0 is assumed, not data-derived
- **File:** `code/intercepta_phenotype_ode_v1.py` → `_derivatives()` method
- **Line:** `AR_SLOPE = 3.0  # approximate (not as rigorously data-derived...)`
- **Fix:** Derive from KAALCURA R_emt axis — slope of AR-gene expression
  vs EMT score in GDSC prostate lines, or from Beltran 2016 NEPC data.
- **Effort:** 1 day.

---

### FIX-008: INTC002 novelty overclaimed
- **File:** `results/lead_candidate_INTC002.json`
- **Bug:** ChEMBL novelty = 0.266 (73.4% similar to known molecules).
  The lead candidate section still uses "novel" language in other docs.
- **Fix:** Global rename in all docs/results: "INTC002 (scaffold-hopped AURKA inhibitor)"
  NOT "novel de novo designed molecule."
- **Files to update:** All docs/*.docx, README.md, PUBLICATION_OUTLINE.md

---

### FIX-009: Cisplatin result exposes model limitation
- **File:** `results/phenotype_ode_v1_1_verified.json`
- **Issue:** `cisplatin_vs_nothing: HR=0.937, benefit=0.5 months`
  Cisplatin has clinical HR ~0.7-0.8 in mCRPC settings. Model predicts
  almost no benefit. This could mean EC50 parameters are off for cisplatin,
  OR the model is correctly showing it doesn't work in mCRPC (cisplatin
  is not standard mCRPC therapy — this may actually be CORRECT biology).
- **Action:** Verify: is cisplatin expected to work in mCRPC? If no, 
  document this as a correct negative prediction. If yes, fix EC50.

---

## PRIORITY 3 — NOT STARTED (build next)

### BUILD-001: Unified ODE
- **Status:** NOT STARTED (from NEXT_SESSION.md)
- **What it needs:** Combine mCRPC and AML ODEs into a disease-agnostic framework
  that takes disease network as input
- **Depends on:** FIX-001 (HR estimator), FIX-002 (AML relapse)

### BUILD-002: Synergy scoring module
- **Status:** NOT STARTED
- **What it needs:** Implement Bliss independence, Loewe additivity, HSA
  as proper mathematical models (not just sum of individual effects)
- **Reference:** Yadav et al. 2015 (Computational Drug Combination)

### BUILD-003: Synthesizability scoring
- **Status:** NOT STARTED (ADMET partial — RDKit only)
- **What it needs:** SA score (Ertl & Schuffenhauer) + SCScore integration
  Both available in RDKit. Add to ADMET pipeline.

### BUILD-004: Pareto ranking
- **Status:** NOT STARTED
- **What it needs:** Multi-objective optimization across (efficacy, ADMET,
  selectivity, synthesizability) — use pymoo or DEAP library

---

## DATA GAPS (cannot fix with code alone)

| Gap | Impact | Path forward |
|-----|--------|--------------|
| INTC002 has no IC50 assay | Lead candidate unvalidated | Wet lab collaborator needed |
| Olaparib GDSC IC50 wrong mechanism | PARPi predictions unreliable | Use SL-specific datasets |
| AML relapse needs scRNA-seq | AML model incomplete | GSE datasets or collaborator |
| Only 6 prostate lines for docetaxel | EC50 poorly constrained | Add all GDSC prostate lines |

---

## WHAT IS SOLID RIGHT NOW (do not re-derive, just use)

1. **PK models** — FDA parameters correct, implementation verified
2. **Phenotype ODE math** — Lorz/Greene/Lorenzi basis, correct implementation
3. **TAX-327 bootstrap validation** — HR=0.687, CI [0.58-0.79] ✓ (after FIX-001 re-run)
4. **Disease network builder** — steps 1-14 complete with real data
5. **AlphaFold structures** — 20 targets downloaded and ready for docking
6. **BeatAML data pipeline** — drug sensitivity + mutations correctly processed
7. **scRNA velocity** — 46235 cells, latent_time distribution real and usable

---

## SUGGESTED FIX ORDER FOR NEXT SESSION

```
Day 1: FIX-001 (HR estimator) → re-run TAX-327 → know if core claim holds
Day 2: FIX-003 (KAALCURA on real GDSC) → know if axes actually work
Day 3: FIX-002 (AML relapse) → fix biology
Day 4: FIX-004 (Scout 4 Boolean network) → biggest build task
Day 5: BUILD-002 (Synergy scoring) + BUILD-003 (Synthesizability)
Day 6: BUILD-004 (Pareto ranking) → then full pipeline re-run
Day 7: FIX-005, FIX-006, FIX-007 (clean up parameter claims)
```
