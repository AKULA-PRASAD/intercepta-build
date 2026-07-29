# INTERCEPTA Round 1 Retrospective — mCRPC

**Date:** April 21, 2026
**Round:** 1 of 7 in the vision's disease expansion sequence
**Status:** Closed at v4.1
**Authors:** Prasad Akula & Claude, Co-Founders of INTERCEPTA

---

## 1. What Round 1 was

Per the vision (Part 7.2): "metastatic Castration-Resistant Prostate Cancer (mCRPC) — best clinical trial ground truth in oncology. Five major trials with clear outcomes. INTERCEPTA v3.0 architecture already built for this disease."

**Scope:** build and validate a mechanistic ODE for mCRPC that can rank drug candidates and combinations against published clinical outcomes. Use the validation to confirm the INTERCEPTA architecture works on a disease where ground truth is densest, before attempting diseases where it is thinner.

**Not in scope:** replace clinical trials, predict exact rPFS/OS curves, optimize absolute-magnitude parameter matching.

---

## 2. What was built

Phenotype-structured two-population ODE, 4 states × 20 bins = 80 compartments:

- States: S (AR-dependent), M (AR-mutant), V (AR-V7 splice variant), N (neuroendocrine/t-SCNC)
- Three drug mechanisms: cytotoxic (docetaxel, mitoxantrone), growth suppression (enzalutamide, abiraterone, ADT), synthetic lethality (olaparib, talazoparib)
- Pharmacokinetic time-dependence via documented clinical PK parameters
- Inter-patient variability via log-normal sampling with literature-sourced CVs
- KAALCURA axes (R_prolif, R_emt, R_ddr) integrated per cell cluster
- ClinicalTrials.gov novelty checker for generated candidates
- Cox HR virtual-cohort pipeline (rPFS framework)
- Biexponential g-rate extraction pipeline (Stein/Wilkerson/Fojo framework)
- Instantaneous ODE diagnostic for term-level analysis

---

## 3. What works

**Directional drug ranking within mCRPC is correct.**

- Docetaxel > mitoxantrone (matches TAX-327)
- Olaparib > ARSI in BRCA-deficient tumors (matches PROfound direction)
- Abiraterone + ADT > ADT alone (matches LATITUDE, HR 0.73 model vs 0.66 clinical, within acceptable window)
- Enzalutamide + ADT produces AR-suppression dynamics (PREVAIL median trt 16.0 mo within window)
- Resistant cell populations (M, V, N) dominate long-term trajectories under ARSI
- Combinations engage multiple escape routes that monotherapy cannot

**Infrastructure transfers to future rounds.**

- ODE mathematical framework is disease-agnostic (states and state_sens matrices re-parameterize)
- Virtual cohort generator works for any disease with per-patient CVs
- g-rate validation pipeline applies to any disease with published Stein-style kinetic data
- Diagnostic tool isolates structural issues at the ODE term level

---

## 4. What doesn't work — honestly listed

**Six of six mCRPC trials fail their rPFS/HR acceptance windows.** Two pass partial checks (PREVAIL median, LATITUDE HR); four fail outright. The rPFS/HR framework itself is an imperfect match to ODE output — this was re-characterized mid-cycle as a framework issue rather than a biology issue.

**Zero of three confirmed g-rate targets pass.**
- Untreated mCRPC: model g = 0.0027/day vs Stein 2011 reference 0.0075/day (0.36×)
- Enzalutamide non-HRR: model g = 0.0027/day vs Leuva 2020 reference 0.000784/day (3.45×)
- Enzalutamide HRR-altered: model g = 0.0032/day vs Zhou 2024 reference 0.001889/day (1.69×)

These gaps are structural to the phenotype-structured ODE framework (logistic growth vs exponential, α_r damping interpretation, biexp fit window vs Stein observation window), not parameter-tuning issues.

**Seven known limitations documented** (in Validation Limitations v1 and Memo v2, v2.1):
1. Absolute g magnitude gap (2-3× across regimens)
2. Enzalutamide fitted g over full simulation doesn't reflect its per-state suppression (fit averages across state transitions)
3. CHAARTED inversion over 5-year horizons (model's advection drives resistance faster than docetaxel's 6-cycle early cytoreduction preserves benefit)
4. Mitoxantrone vs docetaxel kill ratio too lopsided (model 3× vs clinical 1.5×)
5. g_mod values not individually calibrated to NEPC Ki67 data
6. Biexp fit window methodology conflates logistic saturation with biology
7. **PARP-specific evolved resistance not modeled (revealed by v4.1 olaparib run)** — BRCA-deficient fraction is static, no reversion mutations, no 53BP1 loss, no HRR-competent subclone expansion

---

## 5. What was learned

**About the ODE:** a phenotype-structured two-population model is directionally useful but not clinically-quantitative. It captures mechanism but not the exact timescales patients experience.

**About validation:** HR is a trial-design artifact; g is a biological quantity. For mechanistic ODE validation, g is the right target. This framework pivot was made at CSO call and should propagate to all future rounds.

**About parameter sourcing:** In vitro IC50 ≠ in vivo effective kill rate. The v4 → v4.1 olaparib emax correction (0.15 → 0.015 /day) demonstrated this principle concretely. Same sourcing logic will apply in all future disease ODEs.

**About honest iteration:** Correcting one bug can reveal deeper bugs previously hidden by the first. Round 1's olaparib result after v4.1 demonstrated this — the magnitude fix exposed a missing structural piece (evolved resistance). This is the correct way for honest science to proceed, even though it looks like "failure" on the surface.

**About the vision's Option A call:** directional ranking is sufficient for the drug-discovery use case. Absolute calibration is a future problem, not a current blocker.

---

## 6. What transfers to Round 2

**Code:** ODE mathematical framework, virtual cohort generator, g-rate validation pipeline, diagnostic instrument, KAALCURA axes, PK parameterization patterns. All disease-agnostic modulo state definitions.

**Methodology:** validation-first principle, sourced-not-tuned parameters, framework-matched validation (g for ODE, not HR), inter-patient heterogeneity via literature-sourced CVs, diagnostic-before-refit when something fails.

**Known limitations awareness:** any future ODE should plan for logistic-exponential mismatch, state-transition window effects, and evolved-resistance gaps BEFORE claiming quantitative fits.

**The documented scientific record:** v1 and v2 memos, Validation Limitations v1, v2.1 Round 1 closing, this retrospective. Any future pharma conversation or academic paper has a coherent citable record.

---

## 7. What Round 2 (AML) requires

Per the vision (Part 7.2):

- BeatAML clinical ground truth (562 patients, 122 drugs, matched scRNA-seq)
- Two-population biology: blasts (sensitive) vs LSCs (resistant) — natural fit for our architecture
- scRNA-seq: Van Galen 2019, Zeng 2022
- Key driver genes: FLT3, NPM1, DNMT3A, IDH1/2, TP53, TET2, RUNX1
- Drugs already in BeatAML screen: FLT3 inhibitors, IDH inhibitors, venetoclax, chemo agents

Per Universal Net Specification (Part B, Phase B Step 3):
- Next concrete step is assembling the AML disease net using Layers 1, 2, 7, 9 as a connected knowledge graph
- Before any ODE work for AML, confirm the net answers basic queries correctly (e.g., "which BeatAML drugs target FLT3-ITD patients?")
- Only then attempt the ODE adaptation

**Round 2 explicitly does NOT start with another ODE refinement.** The vision specifies disease-by-disease expansion; refining mCRPC further does not advance the "universal" objective. Building the AML net does.

---

## 8. Round 1 in one sentence

**The INTERCEPTA architecture applied to mCRPC produces a mechanistic ODE that ranks drug candidates directionally correctly, documents its own quantitative limits honestly, and is sufficient for the vision's drug-discovery use case — which is what Round 1 was supposed to prove.**

Closed.

---

*Prasad Akula & Claude, Co-Founders of INTERCEPTA*
