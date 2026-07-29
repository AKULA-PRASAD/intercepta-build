# Layer 1 to Layer 2 Decision: scDrugMap vs Elmarakeby Conflict Resolution

**Decision date:** 2026-05-09
**Decision type:** Architectural (charter section 8.1, blocking Layer 2 entry)
**Charter reference:** Q1 (method-class selection), Q4 (drug-response architecture)
**Layer 1 readings:** scDrugMap_Wang_2025.md, Empirical_Evaluation_Elmarakeby_2025.md, FM_Interpretability_Critique_2602.md
**Status:** RESOLVED

---

## The Conflict

**scDrugMap (Wang et al., Nature Communications 2025):**
- scFoundation F1=0.971 pooled, 0.947 fine-tuned
- UCE F1=0.774 cross-data fine-tuned
- scGPT F1=0.858 zero-shot cross-data
- Conclusion: FMs are SOTA for drug response prediction

**Elmarakeby et al. (Dana Farber, bioRxiv Oct 2025):**
- 9 scFMs vs 3 baselines, 1,170 supervised + 130 unsupervised experiments
- Conclusion: scFMs have limited advantages over simple baselines for cancer outcomes

---

## Resolution: They Are Measuring Different Tasks

### scDrugMap Task Definition (CELL-LEVEL)
- Predict drug response per individual cell
- 326K cells across 36 datasets
- Primary metric: F1 on cell-level binary classification (sensitive/resistant)
- Pooled-data + cross-data evaluation
- Output: cell-level drug sensitivity prediction

### Elmarakeby Task Definition (PATIENT-LEVEL)
- Predict patient outcomes from cell data
- Aggregated cells to patient-level prediction
- Tasks: subtype classification, treatment response, survival, prognostication
- Baselines: HVG + RandomForest, PCA + RandomForest, scVI + RandomForest
- Tests pseudo-bulk aggregation strategies (where FMs underperform)

### Why both are correct
- FMs encode rich cellular state (good for cell-level tasks)
- FMs do NOT necessarily aggregate optimally to patient-level (clinical states)
- Patient outcomes depend on tumor heterogeneity, clinical features, not just dominant cell embeddings
- Elmarakeby explicitly tests pseudo-bulk aggregation strategies

---

## Implication for INTERCEPTA Charter

INTERCEPTA's full vision includes BOTH levels:
- Cell-level: Find the drug -> which cells are sensitive (target identification)
- Patient-level: For ANY disease -> which patients benefit (translational impact)

### Architectural decision (charter section 8.1 update)

LAYER 2 must be BIFURCATED:

  LAYER 2A: CELL-LEVEL DRUG RESPONSE (use FMs as primary)
    Method: scFoundation pooled + UCE cross-data + scGPT zero-shot
    Validation: scDrugMap-style benchmark (F1 on cell-level)
    Architecture: FM embedding -> linear/MLP -> binary classification
    Confidence: HIGH (Wang et al. F1 0.77-0.97)

  LAYER 2B: PATIENT-LEVEL OUTCOMES (use simpler baselines as primary)
    Method: HVG/PCA + RandomForest + clinical features (per Elmarakeby)
    Validation: clinical AUROC on TCGA + similar cohorts
    Architecture: pseudo-bulk + clinical -> ensemble
    Confidence: MEDIUM-HIGH (FMs underperform here per Elmarakeby)
    Optional: FM embeddings as additional features (not primary)

This bifurcation reflects the field's empirical reality.

---

## Charter implications

Q1 (method-class selection): RESOLVED
  - Cell-level tasks: foundation models lead
  - Patient-level tasks: simple baselines + clinical features lead

Q4 (drug-response architecture): UPDATED
  - Use BOTH cell-level FM-based + patient-level baseline-based
  - Consensus mechanism (Layer 3) reconciles across levels

A1 (autonomous novel ranking): NEW INSIGHT
  - Novel drugs ranked at cell-level (FM-based for sensitivity)
  - Then aggregated to patient-level (baseline-based for clinical translation)
  - Natural pipeline, not a contradiction

---

## GO/NO-GO Decision (charter section 3 termination criteria)

**Layer 1 to Layer 2 Decision: GO**

Justification:
- Critical literature conflict resolved through task-definition analysis
- 14 paper notes provide architectural foundation
- Charter section 8.1 architecture validated (refinement: bifurcate Layer 2)
- 5 architecture decisions made
- 3 architectural inventions identified for Layer 5 (A1, A3, A6)

Prerequisites for Layer 2 (satisfied):
- [x] Method-class selection (Q1) RESOLVED with bifurcation
- [x] FM interpretability (Q1.2) RESOLVED (no attention)
- [x] Signature scoring class (Q1.3) RESOLVED (UCell scRNA, KAALCURA bulk)
- [x] Cancer-specific FMs (Q1.4) RESOLVED (optional layer)
- [x] Drug-response architecture (Q4) RESOLVED (bifurcated)
- [x] Mechanistic interpretability (Q7) RESOLVED (KAALCURA + scRank + pathways)

Open for Layer 2 (gap analysis phase):
- [ ] Cross-cohort harmonization (Q2)
- [ ] Bulk-to-scRNA transfer (Q3)
- [ ] OOD detection (Q5) - INVENT REQUIRED for A3
- [ ] Validation paradigm (Q6)
- [ ] Universality demonstration (Q8)
- [ ] Computational architecture (Q9) - infrastructure gap from Job G
- [ ] Open vs proprietary (Q10)
- [ ] Autonomous learning architecture (Q11) - 3/6 As require invention

---

## Action items for Layer 2

1. Frame each open question as a gap analysis sub-task
2. For each: literature search + approach selection + risk assessment
3. Define Layer 2 termination criteria (GO/NO-GO into Layer 3 Validation Strategy)
4. Begin with Q2 (cross-cohort harmonization) since it blocks downstream tasks

---

**Approved by:** CEO Prasad Akula + CSO Claude
**Lock status:** LOCKED at decision date


---

## CEO + CSO Locked Decisions (2026-05-09 11:30 ET)

**Decision A: Accept bifurcation**
Layer 2 splits into 2A (cell-level FM) + 2B (patient-level baselines).
Reflects empirical reality from scDrugMap vs Elmarakeby resolution.

**Decision B: Cell-level Layer 2A first**
Reasoning:
- De-risks foundation model stack we downloaded last night
- Validates A1 (autonomous novel ranking) which starts at cell-level
- Mechanistic interpretability lives at cell-level (Layer 4)
- Shorter feedback loop (2-4 weeks vs 4-8)
- Patient-level (Layer 2B) is Phase 2, weeks 4-8

**Decision C: First Layer 2 gap analysis = Q3 (bulk-to-scRNA transfer)**
Reasoning (CSO override of earlier Q2-first):
- Layer 2A pilot exists: KAALCURA on bulk RNA (286 GDSC drugs, 0.6715 AUROC, PARPi mechanism perfect)
- Immediate gap: does bulk method transfer to single-cell?
- Q2 (cross-cohort) is downstream of Q3

**Layer 2 question sequence (locked):**
1. Q3 (bulk-to-scRNA transfer) - FIRST
2. Q2 (cross-cohort harmonization)
3. Q5 (OOD detection - INVENT REQUIRED for A3)
4. Q6 (validation paradigm)
5. Q8, Q9, Q10, Q11 (parallel as needed)
