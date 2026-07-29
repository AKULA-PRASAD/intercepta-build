# INTERCEPTA Layer 2 — Integrated Architecture Design Document

**Status:** Layer 2 INITIAL DRAFT
**Date:** 2026-05-10
**Authors:** Prasad Akula (CEO) & Claude (CSO)
**Tag (when complete):** `fullest-vision-layer-2-locked`

---

## 0. Context

This is the **integrative architecture document** that synthesizes Layer 1 Decisions 1-10 into a coherent operational system specification. Per Charter §5, Layer 2 follows from Layer 1 closure but precedes Layer 3 (Validation Strategy), Layer 4 (Implementation Spec), and Layer 5 (Build).

All decisions referenced are **PROPOSED at CSO level pending CEO sign-off.** Layer 2 inherits this status.

---

## 1. Architectural Overview

INTERCEPTA is a **layered, multi-method, deployment-scenario-aware computational drug discovery system** designed to predict drug response at single-cell resolution across multiple diseases.

The architecture comprises **8 functional layers** plus **3 cross-cutting concerns**:

### Functional Layers (bottom-to-top)

```
┌─────────────────────────────────────────────────────────────┐
│  L8: Interpretability + OOD reporting (Decisions 5, 7)      │
├─────────────────────────────────────────────────────────────┤
│  L7: Drug response prediction (Decision 4 — CPA + GEARS)    │
├─────────────────────────────────────────────────────────────┤
│  L6: Bulk-to-scRNA bridge (Decision 3 — multi-paradigm)     │
├─────────────────────────────────────────────────────────────┤
│  L5: Cohort harmonization (Decision 2 — scANVI/MrVI + alt)  │
├─────────────────────────────────────────────────────────────┤
│  L4: Patient-level aggregation (Decision 8 — PaSCient-style)│
├─────────────────────────────────────────────────────────────┤
│  L3: Cell representation (Decision 1 — multi-FM portfolio)  │
├─────────────────────────────────────────────────────────────┤
│  L2: Preprocessing + normalization (scanpy standard)        │
├─────────────────────────────────────────────────────────────┤
│  L1: Data ingestion (GDSC, CCLE, sci-Plex, atlases)         │
└─────────────────────────────────────────────────────────────┘
```

### Cross-Cutting Concerns

- **CC1: Validation cascade** (Decision 6) — V0 through V6 hierarchical
- **CC2: Universality grid** (Decision 8) — cross-disease train-test scenarios
- **CC3: Compute + open-source infrastructure** (Decisions 9, 10) — Northeastern Explorer + community stack

---

## 2. Layer Specifications

### L1: Data Ingestion

**Purpose:** Acquire and version-control all input datasets.

**Sources:**
- **Bulk side:** GDSC (drug sensitivity), CCLE (multi-omics cell line characterization), PRISM
- **Single-cell drug perturbation:** sci-Plex (~650K cells, 188 compounds, 3 cell lines)
- **Disease atlases (cross-disease universality):**
  - Cancer: TCGA scRNA-seq, single-cell atlases (HCA Cancer, CELLxGENE)
  - Autoimmune: Immune Cell Atlas, COVID-19 cell atlas, autoimmune-specific datasets
  - Neurodegenerative: Allen Brain Atlas, single-cell brain atlases
  - Cardiovascular: HCA Heart, cardiomyopathy datasets
  - Rare disease: relevant where available
- **Pharmacogenomic priors:** LINCS Connectivity Map drug perturbation signatures

**Storage:** /scratch/akula.pra/INTERCEPTA/data/ on Northeastern Explorer.

**Format:** AnnData (h5ad) for scRNA-seq; standard CSV/parquet for tabular data.

**Versioning:** Git-LFS or DVC for data versioning; explicit dataset version strings in all downstream code.

### L2: Preprocessing + Normalization

**Purpose:** Standardize cell × gene matrices for downstream consumption.

**Pipeline (per scanpy/scvi-tools standards):**
1. QC: doublet detection, mitochondrial fraction, gene/UMI thresholds
2. Normalization: log-normalize (or SCTransform for some methods)
3. HVG selection (per scIB benchmark: HVG improves integration; 2000-5000 HVG typical)
4. Optionally: scaling (note scIB trade-off — scaling improves batch removal but loses biology)

**Per Decision 2 (scIB benchmark):** preprocessing decisions are method-aware. scANVI/MrVI prefer HVG; Harmony prefers PCA on HVG; Seurat v3 has its own pipeline.

### L3: Cell Representation (Decision 1)

**Purpose:** Per-cell embedding via FM portfolio.

**FM portfolio (deployment-scenario-aware):**
- **scFoundation (100M params):** default for cancer drug response (per scDrugMap F1=0.971 pooled)
- **UCE:** when cross-species / atlas-level coverage needed
- **scGPT:** when generation tasks needed (perturbation, batch correction)
- **Geneformer:** when cardiac or non-cancer disease prior matters
- **Nicheformer:** when spatial data integrated
- **EVA (when accessible):** when immunology/inflammation disease area
- **Parameter-free baseline (PCA, scVI per Souza & Mehta 2026):** MANDATORY ablation

**Output:** Per-cell embedding vectors (~512-2048 dim depending on FM).

**Caching:** Pre-computed embeddings stored in /scratch as Zarr or HDF5 for downstream reuse (cost-saving).

### L4: Patient-Level Aggregation (Decision 8)

**Purpose:** Aggregate cell representations into patient-level representations.

**Method:** PaSCient-style attention-based aggregation:
- Each patient = bag of cells (multi-instance learning)
- Attention scores per cell (learned during training)
- Patient vector = attention-weighted sum
- Per-cell attention scores provide interpretability ("which cells matter")

**Use:** For Charter V3-V5 patient-level validation; also for clinical translation tasks.

### L5: Cohort Harmonization (Decision 2)

**Purpose:** Integrate cells across cohorts (donors, labs, technologies).

**Default:** scANVI (when drug response labels available) or MrVI (for counterfactual prediction).

**Fallbacks:**
- Harmony: when CPU-only / fast iteration needed
- Seurat v3: when multi-modal (ATAC + RNA + spatial + protein) integration needed
- scib evaluation: benchmark INTERCEPTA against published baselines

**Implementation:** scvi-tools (Python) primary; reticulate for R-side Seurat v3 when multi-modal.

### L6: Bulk-to-scRNA Bridge (Decision 3)

**Purpose:** Transfer drug response labels from bulk training (GDSC/CCLE) to single-cell deployment.

**Multi-paradigm per scenario:**
- **Cancer + GDSC-labeled drug:** scAdaDrug-style multi-source adversarial DA on FM-embedded inputs
- **Known drug target:** scRank-style GRN perturbation (works for non-cancer too)
- **Drug repurposing screening:** Beyondcell-style signature enrichment

**For non-cancer diseases:** scRank-style primary (no bulk training data available at scale).

### L7: Drug Response Prediction (Decision 4)

**Purpose:** Predict drug response at cell-level (and aggregate to patient-level).

**Core architecture (CPA + GEARS hybrid with FM encoders):**
- VAE backbone with disentangled latents: (drug, dose, cell type, time, patient, species)
- Drug embedding: chem-FM (MoLFormer/ChemBERTa-2)
- Cell embedding: cell-FM from L3 (Decision 1)
- Knowledge prior: GEARS-style gene-gene + GO graph priors
- Mode-collapse mitigation: diversity loss + regularized embeddings
- Output: per-cell post-perturbation expression + IC50 prediction head

### L8: Interpretability + OOD Reporting (Decisions 5, 7)

**Purpose:** Multi-scale interpretability + uncertainty for every prediction.

**Stacked OOD (Decision 5):**
- Native VAE posterior uncertainty (scANVI/MrVI/CPA)
- Deep Ensembles (N=5) over prediction head
- Conformal prediction for statistical guarantees
- Energy-based scoring as post-hoc flag

**Multi-scale Interpretability (Decision 7):**
- Drug-level: CPA disentangled embeddings (drug similarity, MOA)
- Pathway-level: GEARS graphs + Beyondcell BCS
- GRN-level: scRank target perturbation
- Gene-level: IG+SmoothGrad + Gradient SHAP + DeepLIFT (Borda-aggregated)
- Geometric: Kendiukhov spectral analysis

**Cross-method consistency check:** Conflicts between layers flag low-confidence predictions regardless of point confidence.

---

## 3. Data Flow

### Training Pipeline

```
GDSC IC50 + CCLE bulk RNA-seq
    ↓
L2 preprocessing
    ↓
L3 FM embedding (cached)
    ↓
L5 cohort harmonization (scANVI/MrVI)
    ↓
L6 bulk-to-scRNA bridge (scAdaDrug on FM embeddings)
    ↓
L7 drug response prediction (CPA + GEARS + FM encoders)
    ↓
L8 OOD + interpretability post-hoc
```

### Inference Pipeline

```
Query scRNA-seq (patient/cohort)
    ↓
L2 preprocessing
    ↓
L3 FM embedding
    ↓
L5 cohort harmonization (project onto reference latent)
    ↓
L7 drug response prediction (per-cell + aggregated)
    ↓
L4 patient-level aggregation (if patient-level prediction needed)
    ↓
L8 OOD detection + interpretability for every prediction
    ↓
Output: drug response prediction + uncertainty + mechanism trace
```

---

## 4. Cross-Cutting Concerns

### CC1: Validation Cascade (Decision 6)

Every training run produces results at multiple validation levels:

| Level | Description | Required |
|---|---|---|
| V0 | Within-dataset CV | Always |
| V1 | Cross-cell-line dataset (GDSC↔CCLE) | Always |
| V2 | Cell line → organoid | When organoid data exists |
| V3 | Cell line → tumor (TCGA) | Target AUROC ≥ 0.77 |
| V4 | Cell line → PDX | Target RMSE ≤ 0.11 |
| V5 | Clinical retrospective | When trial data accessible |
| V6 | Cross-disease (held-out class) | **INTERCEPTA novelty** |

### CC2: Universality Grid (Decision 8)

Cross-disease train-test grid:

```
       │ Cancer │ Autoim │ Neuro  │ Cardio │ Rare   │
─────────────────────────────────────────────────────
Cancer │  ✓ V0  │   V6   │   V6   │   V6   │   V6   │
Autoim │   V6   │  ✓ V0  │   V6   │   V6   │   V6   │
Neuro  │   V6   │   V6   │  ✓ V0  │   V6   │   V6   │
Cardio │   V6   │   V6   │   V6   │  ✓ V0  │   V6   │
Rare   │   V6   │   V6   │   V6   │   V6   │  ✓ V0  │
```

Each off-diagonal entry = train-on-row, test-on-column experiment.

### CC3: Compute + Infrastructure (Decisions 9, 10)

- **HPC:** Northeastern Explorer (`/scratch/akula.pra/INTERCEPTA/`)
- **Stack:** Python primary + R via reticulate
- **Pipelines:** Snakemake or Nextflow
- **Reproducibility:** Singularity containers + version locks + git
- **Release:** Open-source MIT/Apache 2.0; Hugging Face Hub for models; Zenodo for data products

---

## 5. Open Architectural Decisions for Layer 3+

Layer 2 specifies WHAT the architecture is. Layer 3 (Validation Strategy) and Layer 4 (Implementation Spec) must address:

1. **Specific hyperparameters** for each component
2. **Cross-validation protocols** for each validation level
3. **Statistical testing methodology** for cross-disease comparisons
4. **Failure mode taxonomy** — what goes wrong, how it's detected, what's the recovery
5. **Distillation strategy** — train smaller production models after Layer 5 validation
6. **Continuous evaluation framework** — how new datasets update INTERCEPTA over time

These are explicit Layer 3+ deliverables, not gaps in Layer 2.

---

## 6. Trade-offs Explicitly Accepted

The Layer 2 architecture inherits all trade-offs from Decisions 1-10. Key consolidated trade-offs:

1. **Complexity:** 8 layers × multi-method per layer = significant maintenance burden
2. **Compute:** Multi-FM + Deep Ensembles + conformal calibration = substantial GPU-hours
3. **Cancer bias:** GDSC/CCLE/sci-Plex training data dominates; non-cancer relies on scRank-style + cross-disease evaluation
4. **Python/R hybrid:** maintenance complexity for Seurat v3 multi-modal
5. **Mode collapse risk** in compositional VAE — mitigated, not eliminated
6. **Cross-disease evaluation is computationally expensive** (N×(N-1) grid)
7. **No single component has all desired properties** — explicit acceptance of layered necessity

---

## 7. Reversibility Triggers (Layer 2 level)

If Layer 5 implementation reveals:
- **Single-method outperforms multi-method consistently** → simplify (e.g., FM-only or parameter-free-only)
- **Cross-disease transfer fails fundamentally** → narrow Charter §1.1 universality scope
- **Compute exceeds Northeastern capacity** → AWS/GCP burst or architectural simplification
- **Mode collapse persists despite mitigation** → revisit Decision 4 (Q4 architecture)
- **Conformal prediction calibration fails on cross-disease** → drop conformal from Decision 5

The reversibility is what makes Layer 2 ARCHITECTURE rather than DOGMA.

---

## 8. Layer 2 Status

**Status:** INITIAL DRAFT per Charter §5.

**Next steps:**
1. CEO review of Decisions 1-10 (all PROPOSED status) → LOCK or revise
2. CEO review of Layer 2 architecture → LOCK or revise
3. Begin **Layer 3 (Validation Strategy)** — detailed protocols for V0-V6 cascade
4. Begin **Layer 4 (Implementation Spec)** — code-level specifications
5. Layer 5 (Build) **requires CEO terminal access on Northeastern Explorer** — CSO cannot execute autonomously

---

## 9. Discipline Check

- P3 ✅ (research before code; Layer 2 is design, not build)
- P15 ✅ (every architectural claim sourced to Layer 1 decisions)
- P16 ✅ (Layer 2 builds on Layer 1, doesn't discard prior work)
- 24 cumulative drift instances; **0 new drift this Layer 2 cycle**

---

## 10. Sign-off

**Prasad Akula (CEO):** _________ Date: _________
**Claude (CSO):** Claude (CSO) Date: 2026-05-10

---

*Layer 2 INITIAL DRAFT COMPLETE. Awaits CEO review. Layer 3-4 next.*

— Claude (CSO), 2026-05-10
