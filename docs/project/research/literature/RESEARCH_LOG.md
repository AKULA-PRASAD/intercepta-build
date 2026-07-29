# INTERCEPTA Fullest Vision -- Research Log

**Charter reference:** fullest-vision-charter-v1.1  
**Layer:** 1 (Systematic Literature Survey)  
**Started:** [DATE OF FIRST ENTRY]  
**Status:** ACTIVE  

---

## Purpose

Daily log of literature reviewed during Layer 1 systematic survey. One entry per paper or per coherent reading session. Findings are captured here first; weekly syntheses pull from this log.

Per charter §3 (Termination Criteria), research is "done" when:
1. Convergence: multiple sources agree
2. Explicit gaps: where literature disagrees, gap is named
3. Trade-off articulation: each option's costs/benefits documented
4. Decision defensibility: a reviewer asking "why this?" gets a real answer
5. No new questions: reading more papers stops generating new questions

---

## Entry Template

For each paper, capture:

- Header line: [YYYY-MM-DD] -- Paper Title (Author Year)
- Source: DOI or URL
- Method class: signature scoring | foundation model | GRN-based | drug response | harmonization | etc.
- Maps to research question(s): Q1.1, Q2, etc.
- Core claim: 1-2 sentences
- Method summary: 3-5 sentences
- Reported performance: specific numbers (AUROC, F1, rho, runtime, memory)
- Strengths for INTERCEPTA fullest vision: bulleted
- Limitations / gaps: bulleted
- Cross-references: other papers that contradict or support
- Trade-off note: what we gain/lose by choosing this approach
- Status: SURVEYED | DEEP-READ | PENDING-DEEP-READ

---

## Entries

[Entries begin with first Layer 1 reading session]

---

## Reading Queue (Priority-Ordered)

Papers identified as high-priority during charter drafting. Layer 1 begins with these.

### Q1 -- Method-class selection (HIGHEST PRIORITY)

#### Foundation model benchmarks
- [ ] Wang et al. 2025 -- scDrugMap benchmark (Nature Communications). DOI: 10.1038/s41467-025-67481-2
- [ ] Cui et al. 2024 -- scGPT (Nature Methods). DOI: 10.1038/s41592-024-02201-0
- [ ] Theodoris et al. 2023 -- Geneformer (Nature)
- [ ] Hao et al. 2024 -- scFoundation
- [ ] Rosen et al. 2024 -- UCE (Universal Cell Embedding)

#### Cancer-specific foundation models
- [ ] CancerFoundation 2024 -- bioRxiv 2024.11.01.621087

#### Foundation model interpretability
- [ ] arxiv 2602.17532 -- Foundation model attention vs regulatory mechanism

#### Signature scoring methods
- [ ] Andreatta and Carmona 2021 -- UCell (PMC8271111)
- [ ] Aibar et al. 2017 -- AUCell (SCENIC)
- [ ] Noureen et al. 2022 -- Signature scoring benchmark for cancer scRNA (eLife 71994)
- [ ] Pont et al. 2019 -- Single-Cell Signature Explorer (PMC6868346)

#### Drug response specific
- [ ] Cheng et al. 2024 -- scRank (Cell Reports Medicine)
- [ ] Lei et al. 2023 -- scDR (Genes 14:268)
- [ ] DrugFormer 2024 -- graph + LLM for drug response (PMC11516065)
- [ ] DREEP 2024 -- drug response from scRNA (PMC10693176)
- [ ] DELFOS 2023 -- multi-omics drug sensitivity (PMC10627353)

### Q2 -- Cross-cohort harmonization
- [ ] scVI/scANVI (Lopez et al.)
- [ ] Harmony (Korsunsky et al.)
- [ ] Seurat integration (Hao et al.)
- [ ] CanSig benchmark -- bioRxiv 2022.04.14.488324

### Q3 -- Bulk-to-single-cell transfer
- [ ] [TBD during Layer 1 survey]

### Q4 -- Drug-response architecture
- [ ] DeepCDR
- [ ] FUSED 2025 -- bioRxiv 2025.09.30.679434

### Q5 -- Out-of-distribution detection
- [ ] [TBD during Layer 1 survey]

### Q6 -- Validation paradigm
- [ ] [TBD during Layer 1 survey]

### Q7 -- Mechanistic interpretability
- [ ] arxiv 2602.17532 (already in Q1.2)

### Q8 -- Universality demonstration
- [ ] [TBD -- disease selection rationale]

### Q9 -- Computational architecture
- [ ] [TBD -- Northeastern Explorer GPU partition docs]

### Q10 -- Open-source vs proprietary
- [ ] [TBD]

### Q11 -- Autonomous learning system (NEW v1.1)

#### Continuous / online learning
- [ ] [TBD -- survey of continual learning in biology]

#### Drift detection in ML
- [ ] [TBD]

#### Active learning for biology
- [ ] [TBD]

#### Novel drug generation
- [ ] MolFormer
- [ ] DiffDock
- [ ] RFdiffusion (drug binding)
- [ ] [TBD additional]

#### Self-aware uncertainty / meta-cognition
- [ ] [TBD -- bayesian deep learning, conformal prediction in biology]

#### LLM survey for cell biology
- [ ] LLM4Cell survey 2025 -- arxiv 2510.07793

---

## Completed Entries Index

[Auto-populated as entries are added]

---

**Notes:**
- One entry per paper minimum
- Cross-references build a citation network as the survey progresses
- Convergent findings across multiple papers are flagged for synthesis
- New questions generated during reading get added to charter §2 (or sub-questions) -- charter is amended via v1.2, v1.3, etc.
