# INTERCEPTA Layer 4 — Implementation Specification

**Status:** Layer 4 INITIAL DRAFT
**Date:** 2026-05-10
**Tag (when complete):** `fullest-vision-layer-4-locked`

---

## 0. Context

Layer 4 specifies **code-level architecture** for INTERCEPTA — the bridge between Layer 2/3 design + Layer 5 build. This is **the last layer the CSO can fully produce autonomously** — Layer 5 requires CEO terminal access to Northeastern Explorer.

---

## 1. Repository Structure

```
INTERCEPTA/
├── README.md
├── LICENSE (MIT)
├── pyproject.toml
├── environment.yml (conda)
├── Singularity.def (containers)
├── data/                      # Symlinks to /scratch/akula.pra/INTERCEPTA/data/
│   ├── raw/                   # Versioned raw datasets
│   ├── processed/             # Preprocessed AnnData
│   └── embeddings/            # Cached FM embeddings (Zarr)
├── src/
│   ├── intercepta/
│   │   ├── __init__.py
│   │   ├── data/              # L1 ingestion
│   │   │   ├── ingest_gdsc.py
│   │   │   ├── ingest_ccle.py
│   │   │   ├── ingest_sciplex.py
│   │   │   └── ingest_atlases.py
│   │   ├── preprocess/        # L2
│   │   │   ├── qc.py
│   │   │   ├── normalize.py
│   │   │   └── hvg.py
│   │   ├── represent/         # L3 FM portfolio
│   │   │   ├── scfoundation_wrapper.py
│   │   │   ├── uce_wrapper.py
│   │   │   ├── scgpt_wrapper.py
│   │   │   ├── geneformer_wrapper.py
│   │   │   ├── nicheformer_wrapper.py
│   │   │   ├── pca_baseline.py
│   │   │   └── embedding_cache.py
│   │   ├── aggregate/         # L4 patient-level
│   │   │   └── pascient_aggregator.py
│   │   ├── harmonize/         # L5 cohort harmonization
│   │   │   ├── scanvi_runner.py
│   │   │   ├── mrvi_runner.py
│   │   │   ├── harmony_runner.py
│   │   │   └── seurat_v3_bridge.py    # via reticulate
│   │   ├── bridge/            # L6 bulk-to-scRNA
│   │   │   ├── scadadrug_da.py
│   │   │   ├── scrank_grn.py
│   │   │   └── beyondcell_signature.py
│   │   ├── predict/           # L7 drug response prediction
│   │   │   ├── cpa_predictor.py        # Core CPA + GEARS hybrid
│   │   │   ├── chem_fm_encoder.py      # MoLFormer wrapper
│   │   │   ├── disentangled_vae.py
│   │   │   └── graph_priors.py         # GEARS-style
│   │   ├── ood/               # L8 OOD detection
│   │   │   ├── deep_ensemble.py
│   │   │   ├── conformal.py
│   │   │   ├── energy_score.py
│   │   │   └── vae_posterior.py
│   │   ├── interpret/         # L8 interpretability
│   │   │   ├── ig_smoothgrad.py
│   │   │   ├── shap_attribution.py
│   │   │   ├── deeplift_runner.py
│   │   │   ├── borda_aggregator.py
│   │   │   └── consistency_check.py
│   │   ├── validate/          # Validation cascade
│   │   │   ├── v0_within_cv.py
│   │   │   ├── v1_cross_cell_line.py
│   │   │   ├── v2_organoid.py
│   │   │   ├── v3_tcga_tumor.py
│   │   │   ├── v4_pdx.py
│   │   │   ├── v5_clinical.py
│   │   │   └── v6_cross_disease.py
│   │   └── utils/
│   │       ├── stats.py        # Bootstrap CI, significance testing
│   │       ├── logging.py
│   │       └── reproducibility.py
├── pipelines/                  # Snakemake workflows
│   ├── full_training.smk
│   ├── cross_disease_grid.smk
│   └── inference.smk
├── tests/
│   ├── unit/
│   ├── integration/
│   └── regression/
├── notebooks/                  # Exploration only (not in production path)
└── docs/                       # ReadTheDocs source
```

---

## 2. Module Specifications

### 2.1 `intercepta.represent.scfoundation_wrapper`

```python
class scFoundationEncoder:
    """Wrapper for scFoundation FM (Decision 1, default for cancer scenarios)."""
    
    def __init__(self, model_path: str, device: str = "cuda"):
        """Load frozen scFoundation weights from Hugging Face Hub or local."""
        ...
    
    def encode(self, adata: AnnData, batch_size: int = 64) -> np.ndarray:
        """Embed cells → returns (n_cells, embed_dim) array."""
        ...
    
    def encode_with_cache(
        self, adata: AnnData, cache_path: str
    ) -> np.ndarray:
        """Embed with disk caching for reuse."""
        ...
```

Per Decision 1: deployment-scenario-aware. UCE/scGPT/Geneformer wrappers follow same interface.

### 2.2 `intercepta.predict.cpa_predictor` (Core Decision 4 component)

```python
class INTERCEPTAPredictor(LightningModule):
    """CPA + GEARS hybrid with FM-derived encoders.
    
    Per Decision 4:
    - VAE backbone with disentangled latents
    - Drug embedding: chem-FM (MoLFormer)
    - Cell embedding: cell-FM (frozen scFoundation/UCE/etc.)
    - GEARS-style graph priors (gene-gene + GO)
    - Mode-collapse mitigation: diversity loss
    """
    
    def __init__(
        self,
        cell_embed_dim: int = 512,    # From L3 FM
        drug_embed_dim: int = 768,    # From chem-FM
        latent_dim: int = 128,
        n_dose_covariates: int = 1,
        n_celltype_covariates: int = 100,
        gene_graph: Optional[GeneGraph] = None,
        go_graph: Optional[GOGraph] = None,
        diversity_loss_weight: float = 0.1,
    ):
        ...
    
    def encode(self, x, drug_id, dose, celltype):
        """Returns disentangled latent."""
        ...
    
    def decode(self, latent):
        """Returns predicted post-perturbation expression."""
        ...
    
    def predict_response(self, x, drug_id, dose, celltype):
        """Full pipeline: encode → apply perturbation → decode + IC50 head."""
        ...
```

### 2.3 `intercepta.ood.deep_ensemble` (Decision 5)

```python
class INTERCEPTAEnsemble:
    """N=5 Deep Ensemble per Decision 5."""
    
    def __init__(self, model_class, n_members: int = 5, seeds: list = None):
        self.models = [model_class(seed=s) for s in seeds]
    
    def predict(self, x) -> dict:
        """Returns:
        - mean: ensemble mean prediction
        - std: ensemble std (epistemic uncertainty)
        - members: per-member predictions
        """
        ...
```

### 2.4 `intercepta.validate.v6_cross_disease` (Decision 6, 8)

```python
def run_v6_cross_disease_grid(
    model_factory: Callable,
    disease_classes: list = ["cancer", "autoimmune", "neuro", "cardio", "rare"],
    metrics: list = ["auroc", "auprc", "rmse"],
    output_dir: Path = Path("results/v6/"),
):
    """Universality grid: N×(N-1) train-test scenarios."""
    
    for train_disease in disease_classes:
        for test_disease in disease_classes:
            if train_disease == test_disease:
                # V0 within-disease CV
                ...
            else:
                # V6 cross-disease evaluation
                ...
            # Log all results to output_dir/
            # Include OOD flag rate (Decision 5)
            # Include mechanism trace fidelity (Decision 7)
```

---

## 3. Configuration Management

All hyperparameters in `configs/` YAML files (Hydra-style):

```yaml
# configs/architecture/default.yaml
model:
  cell_embed_dim: 512
  drug_embed_dim: 768
  latent_dim: 128
  diversity_loss_weight: 0.1

training:
  batch_size: 64
  learning_rate: 1e-4
  max_epochs: 100
  
validation:
  v0_n_folds: 5
  v6_disease_classes: ["cancer", "autoimmune", "neuro", "cardio", "rare"]

ood:
  ensemble_size: 5
  conformal_alpha: 0.05
  
interpretability:
  smoothgrad_n_samples: 50
  borda_methods: ["ig", "shap", "deeplift"]
```

---

## 4. Snakemake Pipeline

```python
# pipelines/full_training.smk

rule all:
    input:
        "results/v6_cross_disease_grid_complete.flag"

rule data_ingestion:
    output:
        "data/processed/{dataset}.h5ad"
    script:
        "src/intercepta/data/ingest_{dataset}.py"

rule fm_embedding:
    input:
        data="data/processed/{dataset}.h5ad",
    output:
        embedding="data/embeddings/{dataset}_{fm}.zarr"
    script:
        "src/intercepta/represent/{fm}_wrapper.py"

rule train_predictor:
    input:
        embeddings=expand("data/embeddings/{dataset}_scfoundation.zarr", 
                          dataset=["gdsc", "ccle", "sciplex"]),
    output:
        model="models/intercepta_v1.ckpt"
    script:
        "src/intercepta/predict/train.py"

rule v0_through_v6_validation:
    input:
        model="models/intercepta_v1.ckpt",
    output:
        results=expand("results/{level}.parquet", 
                       level=["v0", "v1", "v2", "v3", "v4", "v6"])
    script:
        "src/intercepta/validate/run_cascade.py"

rule cross_disease_grid:
    input:
        results="results/v6.parquet",
    output:
        flag="results/v6_cross_disease_grid_complete.flag"
    script:
        "src/intercepta/validate/v6_cross_disease.py"
```

---

## 5. Testing Strategy

- **Unit tests:** every function with <100 LOC; pytest
- **Integration tests:** verify L1→L2→L3→...→L8 pipeline runs end-to-end on toy data
- **Regression tests:** lock in known-good results on small public benchmarks; fail on drift
- **Smoke tests:** verify FM weights download correctly + can be loaded
- **Statistical tests:** verify validation cascade reports CI + significance correctly

---

## 6. Reproducibility Infrastructure

- **Seed control:** global `intercepta.utils.reproducibility.set_seeds(seed)` called at every entry point
- **Version locking:** `requirements.txt` with pinned versions; conda lock files; pip-compile
- **Containers:** Singularity definitions tested on Northeastern Explorer
- **Data versioning:** explicit version strings in metadata of all AnnData files
- **Model versioning:** semantic versioning (intercepta-v0.1, v0.2, ...); release notes

---

## 7. Logging + Observability

- **Structured logging:** JSON-formatted logs to stderr; aggregated by SLURM jobs
- **Metrics:** Per-run hyperparameters + final metrics → MLflow tracking server (or simple parquet logs)
- **Failure mode instrumentation:** every F1-F7 failure mode (Layer 3) logged with diagnostic info
- **Long-run monitoring:** training loss + validation metrics every epoch; early-stopping if collapsing

---

## 8. Layer 4 Deliverables

When Layer 4 is LOCKED:
- ✅ Repository structure (this document)
- ✅ Module API specifications (this document)
- ✅ Configuration schema (this document)
- ✅ Pipeline specifications (this document)
- ✅ Testing strategy (this document)
- ✅ Reproducibility infrastructure spec (this document)
- ⏳ Actual code implementation = **Layer 5 (requires CEO terminal access)**

---

## 9. Layer 5 Entry Conditions

**Layer 5 (Build) requires:**
1. Decisions 1-10 LOCKED (CEO sign-off)
2. Layer 2 LOCKED
3. Layer 3 LOCKED
4. Layer 4 LOCKED (this document)
5. CEO terminal access to `ssh akula.pra@login.explorer.northeastern.edu`
6. CEO/CSO joint working session to begin code implementation

**The CSO cannot autonomously execute Layer 5.** Building INTERCEPTA requires:
- Running code on Northeastern HPC (CSO doesn't have terminal access)
- Downloading FM weights (CSO can't initiate HTTP downloads from arbitrary hosts in agentic environment)
- Submitting SLURM jobs (requires user credentials)
- Iterating on real data results (requires sustained human-AI collaboration over weeks-months)

**This is the natural boundary where autonomous execution stops and human-in-the-loop building begins.**

---

## 10. Discipline Check

- P3 ✅ (specification, not implementation)
- P15 ✅ (specifications grounded in Layer 1 decisions + Layer 2 architecture)
- P16 ✅ (builds on Layers 1-3)
- 24 cumulative drift instances; **0 new drift this Layer 4 cycle**

---

## 11. Sign-off

**Prasad Akula (CEO):** _________ Date: _________
**Claude (CSO):** Claude (CSO) Date: 2026-05-10

---

*Layer 4 INITIAL DRAFT COMPLETE. This is the last layer the CSO can produce autonomously. Layer 5 build begins with CEO terminal access.*

— Claude (CSO), 2026-05-10
