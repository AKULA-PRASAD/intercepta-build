# INTERCEPTA Layer 3 — Validation Strategy

**Status:** Layer 3 INITIAL DRAFT
**Date:** 2026-05-10
**Tag (when complete):** `fullest-vision-layer-3-locked`

---

## 0. Context

Layer 3 specifies **HOW INTERCEPTA's claims will be tested.** It operationalizes Charter §1.2 V1-V4 + §3 termination criteria + Decision 6 hierarchical cascade + Decision 8 universality grid.

This is the **falsifiability blueprint.** Every Layer 5 build experiment maps to a Layer 3 validation protocol.

---

## 1. Validation Cascade — Detailed Protocols

### V0: Within-Dataset Cross-Validation (Development)

**Purpose:** Optimize hyperparameters; sanity-check architecture.

**Protocol:**
- 5-fold cross-validation on GDSC (drug × cell line splits)
- Stratification: balance drug classes + cancer types
- Metrics: AUROC, AUPRC, RMSE on IC50 regression, F1 on classification
- **Critical: V0 cannot be the only validation.** Per IMPROVE 2025, V0 overestimates performance.

**Pass criterion:** AUROC > 0.80 on within-dataset CV (lower bound for moving to V1).

### V1: Cross-Cell-Line Dataset

**Purpose:** Test generalization across cell line panels.

**Protocol:**
- Train on GDSC, test on CCLE drug screen data (different platform, different IC50 calibration)
- Train on CCLE, test on PRISM
- 3-fold rotation
- Metrics: AUROC, AUPRC on drug response classification

**Pass criterion:** AUROC ≥ 0.70 cross-dataset (literature baseline; SCAD reports 0.6-0.85 per drug).

### V2: Cell Line → Organoid

**Purpose:** Test transfer to 3D biology.

**Protocol:**
- Train on GDSC/CCLE
- Test on HCMI (Human Cancer Models Initiative) organoid panel + Sanger organoid screens
- Per-cancer-type evaluation (different organoid availability by cancer type)
- Metrics: AUROC, RMSE; concordance with organoid IC50 measurements

**Pass criterion:** AUROC ≥ 0.65 (cell-line-to-organoid is harder; literature baseline lower).

### V3: Cell Line → Primary Tumor (TCGA)

**Purpose:** Test transfer to patient tumor context.

**Protocol:**
- Train on GDSC/CCLE
- Test on TCGA tumor scRNA-seq (where drug response inferable from outcome)
- TCGA's drug response is from clinical records — coarser than IC50
- Metrics: AUROC on responder vs non-responder; concordance with outcome data

**Pass criterion:** AUROC ≥ 0.77 (Tang 2022 baseline).

### V4: Cell Line → PDX

**Purpose:** Test transfer to in vivo patient-derived models.

**Protocol:**
- Train on GDSC/CCLE
- Test on NCI PDXNet panel + published PDX drug response data
- TNBC has best validation data (Tang 2022 PDX work)
- Metrics: RMSE on tumor growth inhibition; AUROC on response/non-response

**Pass criterion:** RMSE ≤ 0.11 (Tang 2022 TNBC baseline).

### V5: Clinical Retrospective

**Purpose:** Test against real patient outcomes.

**Protocol:**
- Acquire retrospective clinical trial data (where possible)
- Apply INTERCEPTA to patient pre-treatment samples
- Compare predicted response to actual clinical outcome
- Metrics: AUROC on response prediction; calibration of confidence

**Pass criterion:** AUROC ≥ 0.65 with calibrated uncertainty intervals.

**Note:** V5 is the gold standard but data access is limited. Layer 5 may achieve V5 for only specific cancer-drug pairs.

### V6: Cross-Disease

**Purpose:** Test INTERCEPTA's Charter §1.1 universality claim.

**Protocol:**
- Universality grid: train on N-1 disease classes, test on held-out
- Disease classes: cancer, autoimmune, neurodegenerative, cardiovascular, rare (5 categories per Charter U3)
- For each held-out disease: report:
  - Performance metrics (AUROC, etc.)
  - OOD flag rate (Decision 5)
  - Mechanism trace fidelity (Decision 7)
- Compare against:
  - Disease-specific FM baselines (EVA for I&I, Geneformer for cardiac)
  - Parameter-free baselines (Decision 8 mandatory ablation)

**Pass criterion:** AUROC > random baseline (0.50) on held-out disease with statistical significance.

**Stretch criterion:** AUROC ≥ 0.65 on held-out disease — would establish INTERCEPTA's universality claim.

---

## 2. Statistical Testing

Every comparison reports:
- Point estimate
- 95% confidence interval (bootstrap on cells/patients depending on level)
- Statistical significance vs baseline (Mann-Whitney U for AUROC differences, paired t-test for RMSE)
- Multiple testing correction (Bonferroni or BH-FDR depending on context)

Effect sizes (Cohen's d, AUROC difference) reported alongside p-values to avoid p-hacking.

---

## 3. Failure Mode Taxonomy

Every model failure must fit one of these documented categories:

| Failure Mode | Detection | Response |
|---|---|---|
| **F1: OOD input** | Decision 5 OOD detection flags | Refuse prediction; report uncertainty |
| **F2: Cross-method conflict** | Decision 7 interpretability layers disagree | Report low confidence |
| **F3: Mode collapse** | Predictions cluster around mean | Diversity loss + regularized embeddings |
| **F4: Calibration failure** | Conformal coverage deviates from target | Recalibrate on held-out data |
| **F5: Distribution shift** | Cross-disease V6 performance collapses | Disease-specific fine-tuning or refuse |
| **F6: Compute timeout** | Training/inference exceeds budget | Distillation or batch reduction |
| **F7: Reproducibility failure** | Different runs give different results | Version locking audit; seed control |

Each failure mode is **expected and instrumented**, not surprising.

---

## 4. Continuous Evaluation Framework

Post-Layer 5 (when INTERCEPTA is deployed):

- **New datasets enter via L1 ingestion** with explicit version tags
- **Automated V0-V6 evaluation** triggers on each new dataset incorporation
- **Performance drift monitoring:** if AUROC degrades >5% on existing benchmarks after new data ingestion, flag for review
- **Annual benchmark refresh:** re-benchmark against latest published methods (scIB-style)

---

## 5. Layer 3 Deliverables

When Layer 3 is LOCKED, the following exist:
- ✅ V0-V6 protocol specifications (this document)
- ✅ Failure mode taxonomy (this document)
- ⏳ Specific evaluation scripts (Layer 4 deliverable)
- ⏳ Statistical testing utilities (Layer 4 deliverable)
- ⏳ Continuous evaluation infrastructure (Layer 4 deliverable)

---

## 6. Discipline Check

- P3 ✅ (specification, not code)
- P15 ✅ (validation thresholds grounded in Layer 1 literature)
- Charter §3 termination criteria 1-5 all served by V0-V6 cascade

---

## Status

**Layer 3 INITIAL DRAFT COMPLETE.** Awaits CEO review. Layer 4 (Implementation Spec) next.

— Claude (CSO), 2026-05-10
