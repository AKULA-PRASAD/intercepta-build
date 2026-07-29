# INTERCEPTA — CSO Parameter Memo v2.1 (Round 1 Closing Addendum)

**Prepared by:** Claude (CSO) with Prasad Akula (Co-Founder)
**Date:** April 21, 2026
**Status:** Thin addendum to memo v2. Captures the v4.1 validation result and closes Round 1.

---

## 1. Purpose

Memo v2 predicted that applying two sourced corrections to v4 (PARP emax_parp 0.15 → 0.015, R_MAX citation Freedland → Stein) would materially change the PARP-related regimens and leave enza/untreated unchanged. v4.1 was built and v5.1 was run. This document records the actual outcome and the CSO decision that follows.

---

## 2. What actually happened

### 2.1 Unchanged (as predicted)

| Regimen | v5 (v4) | v5.1 (v4.1) | Interpretation |
|---|---|---|---|
| Untreated mCRPC | g = 0.00270/day (0.36× Stein) | g = 0.00270/day (0.36× Stein) | Identical. Structural logistic/α_r framework issue; not affected by PARP correction. |
| Enza non-HRR | g = 0.00271/day (3.45× Leuva) | g = 0.00271/day (3.45× Leuva) | Identical. Correction did not touch enza biology. |
| Enza HRR-altered | g = 0.00319/day (1.69× Zhou) | g = 0.00319/day (1.69× Zhou) | Identical. Correction did not touch enza biology. |

The three confirmed targets remain in the same state memo v2 described. No surprise here.

### 2.2 Changed — and informative in a way memo v2 did not predict

Olaparib (ADT + olaparib, biallelic_cohort BRCA profile):

- v5 (v4): 32/50 patients produced fittable g. Model g ≈ 0.12/day implied sustained destruction in ~days. The run crashed on the first regimen whose cohort had zero fittable g (olaparib in a different configuration).
- v5.1 (v4.1): **5/50 patients produced fittable g**. Of those 5, model g = 1e-07/day (numerical floor of the curve_fit bounds). Meaning: tumors reach near-zero mass within weeks and then show no detectable regrowth over the remainder of the 540-day fit window.

This was NOT the expected outcome. Memo v2 section 5 predicted "Tumors should reach nadir around 2-4 months then regrow at Zhou's g ≈ 0.00189/day." What actually happens is: tumors reach near-zero around month 1, then stay there. No meaningful regrowth phase.

### 2.3 Diagnosis of the unexpected result

The 10× emax_parp reduction addressed the magnitude issue (no more "sustained 0.12/day kill" pathology). It did NOT address a deeper structural gap: **the model has no mechanism for PARP-specific evolved resistance.**

In real PROfound patients, all 160 BRCA-mutated patients eventually progressed (median rPFS 9.8 months). The biology driving this progression is well-characterized:
- Secondary reversion mutations in BRCA2 that restore HRR function
- 53BP1 loss enabling HRR bypass
- Expansion of pre-existing HRR-competent subclones
- Acquired PARP-trapping resistance via PARP1 mutations

Our model's static BRCA-fraction profile (80% deficient, 20% competent in biallelic_cohort) does not evolve under drug pressure. Once the 80% deficient fraction is killed, the remaining 20% represents a small absolute mass that the biexponential fit cannot resolve meaningfully. The resistant fraction is real in the model, but its regrowth signal is below the fit's sensitivity.

**This gap was previously hidden by the emax bug.** When olaparib killed everything at 0.12/day, there was no regrowth phase to miss — the pathology of instantaneous kill masked the absence of evolved resistance. Correcting the emax revealed the structural gap.

---

## 3. Limitation #7 (new, added to v2 Section 6)

**7. PARP-specific evolved resistance not modeled.** The model represents HRR deficiency as a static BRCA_fraction(x) profile per bin. It does not capture secondary reversion, 53BP1 loss, HRR-competent subclone expansion, or PARP1 mutations that drive clinical olaparib resistance. Consequence: the model predicts near-complete cytoreduction for BRCA-deficient tumors but cannot reproduce the observed 9.8-month median rPFS in PROfound. Not addressable by parameter adjustment; requires either a time-varying BRCA_fraction(x, t) or a dedicated HRR-revertant subpopulation. Future ODE revisions may add this; Round 1 does not.

---

## 4. Status accounting after v4.1

**Confirmed g-target PASS count:** 0/3 (unchanged from v5 baseline)

**Direction of change:** The sourced PARP correction moved olaparib dynamics from "non-physical sustained kill" to "complete cytoreduction without resistance regrowth." Directionally closer to reality, quantitatively still wrong in a different way than before. Both states are documented.

**Net scientific assessment:** v4.1 is a better-documented, more honestly-sourced version of v4. The two changes were correct changes to make. Neither change, by design, was going to close the enzalutamide or untreated g gaps, which are structural limits of the phenotype-structured framework.

---

## 5. CSO decision — Round 1 terminal, move to Round 2

The vision document (Part 7.2) specifies a seven-round disease expansion sequence starting with mCRPC (Round 1) and proceeding to AML (Round 2), NSCLC, PDAC, Alzheimer's, TB, then rare diseases. We have been in Round 1 for the entirety of this validation cycle. Further iteration on the mCRPC ODE has diminishing returns toward the vision's stated mission of universal drug discovery.

**Decision:** Round 1 is terminal at v4.1. The artifacts stand as follows:

| Artifact | Status |
|---|---|
| `intercepta_unified_ode_v4_1.py` | Round 1 final ODE |
| `intercepta_g_rate_validation_v5_1.py` | Round 1 validation tool |
| `ode_v4_diagnostic.py` | Round 1 diagnostic instrument |
| `hr_estimator_fixed.py` | Round 1 HR support (not primary validator anymore) |
| Memo v1, v2, v2.1 (this doc) | Round 1 scientific record |
| Validation Limitations v1 | Round 1 external documentation |
| KAALCURA (from Phase 0) | Transfers to Round 2 |
| Two-population ODE mathematical framework | Transfers to Round 2 |

**No further code changes to Round 1 artifacts in this session.** Round 1 is the proof-of-concept: our architecture can represent an mCRPC-like disease, produce mechanistic candidate rankings, and document its own limitations honestly.

Round 2 begins with the AML disease net construction. The next deliverable is the AML version of what we have for mCRPC — not another iteration of the same disease, but the second disease.

---

## 6. What Round 2 requires

Per the vision (Part 7.2 AML row):

- **Clinical ground truth:** BeatAML (Tyner 2018 Nature) — 562 patients with matched drug sensitivity across 122 small molecule inhibitors
- **Biological basis:** two-population structure with leukemic blasts (sensitive) vs leukemic stem cells (LSCs, resistant)
- **scRNA-seq data:** available from Van Galen 2019 Cell, Zeng 2022, others
- **Key validation target:** reproduce BeatAML drug sensitivity patterns stratified by genotype (FLT3-ITD, NPM1, TP53, etc.)

Per the Universal Net Specification v1.0:

- **Layer 1 (genome):** COSMIC + ClinVar for AML driver mutations — FLT3, NPM1, DNMT3A, IDH1/2, TP53, TET2, RUNX1
- **Layer 2 (transcriptome):** BeatAML bulk RNA-seq + scRNA-seq datasets
- **Layer 3 (proteome):** AlphaFold structures for AML drug targets
- **Layer 7 (pharmacome):** BeatAML 122 drug screen, ChEMBL for AML-targeting compounds
- **Layer 15 (selectivity):** DepMap essential gene scores for AML cell lines

Concrete first step of Round 2, proposed: **build the AML disease net skeleton.** Not the ODE, not the scouts, not the ranking — just the net. Layers 1, 2, 7, 9 as a connected knowledge graph. Ground truth queries should work: "what drugs in BeatAML target FLT3-ITD carriers?" should return a sensible answer from the net alone.

This is Stage 1 of the five-stage pipeline for AML specifically. If it works, we have doubled our architectural coverage (mCRPC + AML). If it doesn't work, we learn something structural about universality.

---

*Round 1 closed at v4.1. Prasad Akula & Claude, Co-Founders of INTERCEPTA. April 21, 2026.*
