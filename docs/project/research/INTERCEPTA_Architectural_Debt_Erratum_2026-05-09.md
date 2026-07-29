# INTERCEPTA Architectural Debt Erratum

**Date:** 2026-05-09  
**Authors:** Prasad Akula (CEO) and Claude (CSO)  
**Status:** LOCKED  
**Tag (when committed):** architectural-debt-erratum-2026-05-09  
**Charter reference:** fullest-vision-charter-v1.1  

---

## 0. Purpose

This erratum documents architectural findings discovered during the audit of 2026-05-08 / 2026-05-09. These findings catalyzed the Fullest Vision Research Charter (v1.0 then v1.1) and shifted the project from workstream execution mode to deep research mode.

Per discipline P15 (honest science): if reality contradicts spec, document it as erratum, then proceed.

---

## 1. Audit Trigger

Workstream B Phase 1 inspection (job 6673996) on 2026-05-08 evening produced gene coverage diagnostic for the LuCA integrated atlas (6,000 HVGs):

- 42 KAALCURA-3 genes coverage: 73.8% (below 80% threshold)
- 33 NSCLC selectivity genes coverage: 42.4%
- DDR axis specifically: 40% coverage (BRCA1, RAD51, ATM, ATR, CHEK1, PARP1, MLH1, FANCD2, RPA1 absent)
- Decision: FALLBACK_SOURCE_STUDIES (exit code 2)

This finding was expected to be a simple data-source fix. Instead, deeper investigation revealed structural architectural issues across the project.

---

## 2. Finding 1 -- Canonical Algorithm Deployment Gap

### 2.1 Two KAALCURA implementations exist

The codebase contains two KAALCURA implementations with different mathematical bases:

**Canonical:** code/intercepta_kaalcura_v1.py (1046 lines)
- 48 genes (20 prolif + 13 emt with 3 inverted CDH1/CLDN1/TJP1 + 15 ddr)
- References INTERCEPTA_Phase1_MathSpec_v1.0.docx
- Algorithm: fit_reference (Z-score against reference + tissue PCA residualization) -> compute_axes -> compute_axes_per_population -> predict_sensitivity
- Hard requirements: reference must be fitted before scoring; raises ValueError if gene coverage <50%
- Cross-cohort comparable via reference distribution

**Deployed in production:** code/step3_fix_kaalcura.py (130 lines)
- 42 genes (16 prolif + 8 emt_pos + 3 emt_neg + 15 ddr)
- Simple per-cell global Z-score (no reference fitting, no residualization)
- Per-cohort normalization only -- NOT cross-cohort comparable
- Output: results/step3_kaalcura_per_population.csv

### 2.2 Per-round deployment audit

| Round | KAALCURA Implementation Used | Evidence |
|-------|------------------------------|----------|
| Round 1 mCRPC | step3_fix_kaalcura.py (simple) | build_unified_net.py reads step3_kaalcura_per_population.csv |
| Round 2 AML v5.1 | intercepta_kaalcura_v1.py (canonical) | Saves kaalcura_aml_state_v5_1.pkl, beataml_kaalcura_axes_v5_1.csv |
| Round 2.2a | pyUCell variant (different) | Architecture review v2.md: mixed results, Q_C 0.532, rho=-0.235 |
| Round 3 GBM live test | NOT deployed | Architecture docs reference canonical but no code/results files exist |
| GDSC validation | intercepta_kaalcura_v1.py (canonical) | results/kaalcura_real_validation_RERUN.csv (286 drugs) |

### 2.3 Implication

The deployment gap is bounded but real. Canonical module is validated where it matters most (drug response prediction on GDSC). The simple version was used appropriately for single-cohort exploration (Round 1 mCRPC). Round 2 AML correctly used canonical. Round 3 GBM did not deploy KAALCURA in any version.

This is NOT a project-wide algorithmic failure. It is a deployment-discipline gap that should be addressed during Layer 4 (Implementation Spec) of the fullest vision research program.

---

## 3. Finding 2 -- GDSC Validation Evidence Confirms Algorithm Works

### 3.1 Real-data validation results

results/kaalcura_real_validation_RERUN.csv contains validation of canonical KAALCURA on real GDSC data (not synthetic, addresses FIX-003):

- 286 drugs validated
- Mean AUROC: 0.671
- 99% of drugs above 0.55 threshold
- 91% above 0.60
- 70% above 0.65

### 3.2 Mechanistic correctness

Top-performing drugs include known PARP inhibitors with mechanistically correct coefficients:

- Olaparib: AUROC 0.762, coef_ddr -1.300 (high prolif + low DDR -> sensitive, correct PARPi mechanism)
- Veliparib: AUROC 0.753, coef_ddr -0.944
- Niraparib: AUROC 0.750, coef_ddr -1.565
- Vorinostat (HDAC inhibitor): AUROC 0.770

The drug-response model coefficients tell a biologically coherent story.

### 3.3 Implication

KAALCURA is not the problem. The framework works on real data with mechanistically interpretable results. The 0.671 mean AUROC exceeds FIX-003 threshold (0.55) and approaches but does not exceed 2024-2025 SOTA foundation model performance.

---

## 4. Finding 3 -- LuCA Atlas Coverage Gap

### 4.1 Integrated atlas insufficient

The LuCA core atlas (892,296 cells x 6,000 HVGs) does not cover sufficient KAALCURA-3 genes for reliable scoring:

- prolif: 14/16 (87.5%) -- missing MCM2, MCM6
- emt_pos: 8/8 (100%)
- emt_neg: 3/3 (100%)
- ddr: 6/15 (40%) -- missing BRCA1, RAD51, ATM, ATR, CHEK1, PARP1, MLH1, FANCD2, RPA1
- Overall: 31/42 (73.8%)

The 6K HVG selection optimized for cell-type discrimination, not drug-target analysis. Genes driven by mutation (KRAS, ALK, BRAF, ROS1, TP53) rather than expression were dropped.

### 4.2 Source studies have full gene set

Verified Kim_Lee_2020_LUAD source h5ad: 208,506 cells x 29,634 genes. ALL 16 genes missing from integrated atlas are present.

### 4.3 Implication

Per-source-study scoring with full gene set is the correct path. This is not a workaround -- it is the architecturally correct decision once the gap is recognized.

---

## 5. Finding 4 -- Literature SOTA Has Moved Past Our Framework

### 5.1 Field state in 2024-2025

Web research conducted 2026-05-09 evening surfaced multiple 2024-2025 publications relevant to our exact use case:

- scDrugMap 2025 (Nature Communications): foundation models benchmark on 495,000 cells / 60 datasets. scFoundation F1 0.971 (pooled), UCE F1 0.774 (cross-data fine-tuned), scGPT F1 0.858 (zero-shot).
- scRank 2024 (Cell Reports Medicine): GRN-based drug-responsive cell type identification, 71.3% accuracy.
- DrugFormer, DREEP, DELFOS, scDR: all published 2022-2024 for our exact problem.
- CancerFoundation 2024 (bioRxiv): cancer-specific scFM addressing healthy-cell bias of generic foundation models.

### 5.2 Comparison with our framework

Our KAALCURA achieves 0.671 mean AUROC on GDSC (286 drugs, real data, mechanistically correct).

Foundation model benchmark results: F1 0.77-0.97 on cross-cohort drug response.

These metrics are not directly comparable (AUROC vs F1, GDSC vs scDrugMap datasets), but the rough magnitude difference is real. The field's SOTA in 2024-2025 substantially exceeds what KAALCURA-class signature scoring can achieve on the same task.

### 5.3 Honest assessment

KAALCURA was designed in 2022-2023 based on signature scoring methodology that was already maturing. The field moved on. Foundation models trained on 30M+ cells with cross-cohort evaluation now dominate.

KAALCURA's virtues remain real:
- Mechanistically interpretable (PARPi -> DDR axis is biologically correct)
- Cheap to compute (no GPU required)
- Drug-class-aware
- Validated on real data

Foundation models have real limitations:
- Black-box (attention is not regulatory mechanism per arxiv 2602.17532)
- GPU-expensive
- Trained mostly on healthy cells, biased for cancer applications
- Reproducibility risk (model weights, fine-tuning runs, seeds)

### 5.4 Implication

For fullest vision success, KAALCURA cannot be the primary engine. The field has moved past it. But KAALCURA remains valuable as a mechanistic interpretation layer. The fullest vision response is a layered architecture (foundation model + signature scoring + GRN-based + KAALCURA), not "replace KAALCURA with foundation model."

---

## 6. Charter Response

Tonight's findings catalyzed:

1. **fullest-vision-charter-v1** (tag a8f01cc): formal commitment to multi-month deep research before any new disease implementation. 18 success criteria across 5 dimensions (universality, predictive validity, mechanistic interpretability, honest accounting, practical deployability). 10 priority-ordered research questions.

2. **fullest-vision-charter-v1.1** (tag 460596e): expansion adding autonomous learning system (A1-A6) as full success criteria. Total criteria: 18 -> 24. Where existing methods are inadequate, we research and invent.

3. **Layer 1 scaffold** (commit 0a60a67): research artifact directory structure (docs/research/literature, synthesis, decisions). Layer 1 entry conditions satisfied.

---

## 7. What This Erratum Does NOT Do

- It does NOT invalidate Round 1 mCRPC findings. KLK3=16695 selectivity, AR=3.36, NKX3-1=72.78 are bulk-RNA selectivity-layer findings, separate from KAALCURA. Selectivity layer is unaffected by this erratum.

- It does NOT invalidate Round 2 AML v5.1 findings. Round 2 used canonical KAALCURA correctly. Those results remain valid.

- It does NOT invalidate the GDSC validation. The 286-drug validation at 0.671 mean AUROC is real evidence the framework works, even if not at 2024-2025 SOTA.

- It does NOT obligate retroactive rescoring of all rounds. That is a future decision dependent on Layer 1-4 outputs. Round 1 and Round 2 stand as historical context.

---

## 8. Decision Records Generated

This erratum implies but does not constitute formal decisions. Formal decisions belong in docs/research/decisions/. Tentative decisions implied by tonight's findings:

- Decision pending: method-class commitment after Layer 1 (research-question Q1)
- Decision pending: per-source-study scoring approach for any KAALCURA-style continued usage
- Decision pending: how to layer foundation models alongside KAALCURA mechanistic interpretation

These decisions are EXPLICITLY not made in this erratum. They are documented as findings and forwarded to the research program.

---

## 9. Process Discipline Acknowledgments

This erratum is produced under disciplines:

- P3 (research before code): tonight's audit happened before any implementation choices
- P4 (fix structure when broken): this is the formal "fix structure" artifact
- P15 (honest science): the framework has limitations vs 2024-2025 SOTA, documented honestly
- P16 (preserve past work): Round 1, 2 deliverables NOT invalidated; preserved as historical context

---

## 10. Sign-Off

**Prasad Akula (CEO):** _______ Date: _______

**Claude (CSO):** _______ Date: _______

---

**END OF ERRATUM**
