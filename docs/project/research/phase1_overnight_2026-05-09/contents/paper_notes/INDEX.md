# Layer 1 Paper Notes -- Index (Updated)

**Charter reference:** fullest-vision-charter-v1.1
**Notes generated:** 2026-05-09 (overnight session, ~00:00-02:00 ET)
**Total papers surveyed:** 14

## Notes by category

### Foundation models (4)
- scGPT_Cui_2024.md
- scFoundation_Hao_2024.md
- UCE_Rosen_2023.md
- CancerFoundation_Theus_2024.md

### Benchmarks / evaluations (3)
- scDrugMap_Wang_2025.md
- Empirical_Evaluation_Elmarakeby_2025.md
- LLM4Cell_Survey_2025.md

### Signature scoring (2)
- UCell_Andreatta_Carmona_2021.md
- Noureen_Signature_Benchmark_2022.md

### Critique / interpretability (1)
- FM_Interpretability_Critique_2602.md

### GRN / drug response (1)
- scRank_Cheng_2024.md

### Agentic / autonomous (3) -- Charter Q11
- scAgent_Mao_2025.md
- scAgents_ICML_2025.md
- CellAgent_Xiao_2025.md

---

## CRITICAL FINDINGS (14-paper Layer 1 survey)

### Finding 1: Literature conflict -- scDrugMap vs Elmarakeby
- scDrugMap: scFoundation/UCE/scGPT achieve F1 0.77-0.97 on drug response
- Elmarakeby (Dana Farber): scFMs show limited advantages vs simple baselines for patient outcomes
- Resolution required before charter section 8.1 architectural commitment

### Finding 2: FM attention is NOT regulatory mechanism (DECIDED)
- arxiv 2602.17532: attention captures co-expression, not unique regulatory signal
- Trivial gene-level baselines beat attention edges (AUROC 0.81-0.88 vs 0.70)
- Architecture decision: NOT use FM attention for mechanistic trace
- Use KAALCURA + scRank + pathway enrichment instead

### Finding 3: Bulk-style sig scoring biased for scRNA (DECIDED)
- Noureen 2022: ssGSEA, GSVA biased by gene count differences cancer vs normal
- UCell, AUCell rank-based methods spared
- Architecture decision: Z-score canonical KAALCURA only for bulk RNA
- UCell for scRNA cohorts

### Finding 4: Cancer-specific FMs violate universality
- CancerFoundation trained only on malignant cells
- Doesnt extend to autoimmune, neurodegenerative diseases
- Decision: Optional specialization layer, NOT primary engine

### Finding 5: Field converging on agentic systems for autonomy
- LLM4Cell surveys 58 models -- agentic family is newest and fastest-growing
- scAgents: 49 percent reduction in error vs scGPT on perturbation
- Charter section 1.6 A1-A6 partially addressed:
  - A4 active learning: scAgents pattern usable
  - A5 operational autonomy: CellAgent pattern usable
  - A2 continuous learning: scAgent dynamic memory module
  - A1 novel drug ranking: NOT addressed -- INVENT REQUIRED
  - A3 drift detection: NOT addressed -- INVENT REQUIRED
  - A6 self-aware uncertainty: NOT addressed -- INVENT REQUIRED

---

## Updated charter section 8.1 architecture (validated by Layer 1)

LAYER 1 -- Multi-method representation
  1A: Foundation model (scFoundation pooled, UCE cross-data)
  1B: Signature scoring (UCell for scRNA)
  1C: KAALCURA (BULK RNA ONLY per Noureen)
  1D: GRN-based (scRank pattern, NOT FM attention)

LAYER 2 -- Multi-method drug response prediction
  2A: scDrugMap-style benchmark on cell-level drug response
  2B: Simple baseline + clinical for patient outcomes (per Elmarakeby)

LAYER 3 -- Consensus + confidence weighting
  Adaptive weighting based on task type

LAYER 4 -- Mechanistic interpretation
  KAALCURA axes (validated PARPi mechanism)
  scRank GRN-based cell type
  Pathway enrichment over differential genes
  NOT FM attention (decided)

LAYER 5 -- Autonomous Learning Loop
  A4: scAgents-style multi-agent
  A5: CellAgent-style natural language interface
  A2: scAgent-style dynamic memory
  A1: INVENT REQUIRED -- generative chemistry + network propagation
  A3: INVENT REQUIRED -- distribution shift detection on cell embeddings
  A6: INVENT REQUIRED -- meta-cognition over prediction reliability

---

## Reading queue for next sessions

High priority (resolve open questions):
1. Elmarakeby et al. 2025 -- DEEP READ for FM vs baseline gap
2. scAgents ICML 2025 -- DEEP READ for Layer 5 architecture
3. scAgent Mao 2025 -- Layer 5 architecture
4. CellAgent Xiao 2025 -- Layer 5 architecture
5. CancerFoundation Theus 2024 FULL bioRxiv -- survival prediction

Medium priority:
6. DREEP Pellecchia et al. 2023 -- alternative drug response method
7. scKAN 2025 -- interpretable architecture
8. DrugFormer 2024 -- graph + LLM

---

## Charter Q1-Q11 status

Q1 method class selection: 80 percent (gap: scDrugMap vs Elmarakeby)
Q1.1 SOTA on drug response: KNOWN (FMs leading per scDrugMap, contested per Elmarakeby)
Q1.2 FM interpretability: RESOLVED (attention is not regulation)
Q1.3 Signature scoring class: RESOLVED (UCell for scRNA)
Q1.4 Cancer-bias in FMs: KNOWN (CancerFoundation, but violates universality)
Q2 Cross-cohort harmonization: OPEN
Q3 Bulk-to-scRNA transfer: OPEN
Q4 Drug-response architecture: 50 percent
Q5 OOD detection: OPEN -- INVENT REQUIRED for A3
Q6 Validation paradigm: OPEN
Q7 Mechanistic interpretability: RESOLVED (NOT FM attention)
Q8 Universality demonstration: OPEN -- limits revealed by CancerFoundation
Q9 Computational architecture: INFRASTRUCTURE GAP IDENTIFIED (Job G)
Q10 Open vs proprietary: OPEN
Q11 Autonomous learning architecture: 60 percent (3/6 As have precedent, 3 require invention)
