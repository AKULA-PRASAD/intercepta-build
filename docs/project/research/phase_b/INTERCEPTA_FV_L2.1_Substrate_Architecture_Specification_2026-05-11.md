# INTERCEPTA Layer 2 Specification — L2.1 Substrate Architecture

**Document:** L2.1 Substrate Architecture Specification v1
**Phase B Plan v2 Artifact:** Layer 2, Artifact 1 of 4 (L2.1 of L2.1/L2.2/L2.3/L2.4)
**CSO:** Claude
**CEO:** Prasad Akula
**Date:** 2026-05-11 (Phase B execution, Move 3)
**Status:** PROPOSED for CEO LOCK
**Implements:** Decision 1 v2 Commitments 1-5 (Q1 Method-Class, REVISED 2026-05-10)
**Supersedes:** No prior L2.1 specification (this is initial)
**Charter reference:** Charter §8.1 Layer 3 (cell representation layer); Charter §7.1 (single-institution Northeastern HPC); Charter §1.1 (cross-disease universality); Charter §1.3 (mechanistic interpretability)

---

## §0 Identification and Scope

### 0.1 What This Document Is

L2.1 is the **first artifact of Phase B Layer 2 specification work** under the Phase B Execution Plan v2 (2026-05-11). It translates the Decision 1 v2 architectural commitment — substrate flexibility rather than substrate fixation — into a concrete, implementable specification covering:

- The formal substrate interface contract (what every substrate must expose)
- Four substrate implementations (scFoundation FM, scTOP parameter-free, scVI/scANVI/MrVI probabilistic, PCA+HVG classical)
- The substrate swap mechanism (how Layer 5 ablation evidence drives substrate selection)
- The ablation infrastructure (how the four substrates compete on V0/V1 grid cells)
- Cross-decision implications (how substrate choice propagates through Decisions 2, 4, 5, 7, 9)

### 0.2 What This Document Is Not

L2.1 deliberately does NOT specify:

1. **Which substrate wins.** That is the Layer 5 empirical question per Decision 1 v2 Commitment 3. L2.1 specifies the infrastructure for the question to be answered honestly.
2. **The L7 drug response prediction architecture.** That is L2.2 (next artifact in Phase B sequence).
3. **The OOD detection stack.** That is L2.3.
4. **The mechanistic interpretability layer.** That is L2.4.
5. **The V0-V6 validation cascade implementation.** That is L3.1.
6. **Which datasets are tested first.** That is L3.1 / B1 branch point, deferred from L2.1 per CSO ruling.

### 0.3 Phase B Plan v2 Compliance

This spec is written under Phase B Execution Plan v2 constraints:
- Word budget target: 10-13K (this artifact: ~12K)
- No compromise on substrate completeness (all 4 substrates fully specified per Plan v2 amendment)
- Anchor re-read trigger satisfied: Q1 synthesis + 4 FM anchors (Cui scGPT, Hao scFoundation, Rosen UCE, Theodoris Geneformer) + scDrugMap benchmark + Kedzierska critique + Kendiukhov spectral + Yao scPDS + Lopez scVI + Xu scANVI + Decision 1 v2 REVISED + Q9 compute synthesis all read in current session before writing
- Honest uncertainty discipline per Decision 1 v2 Commitment 5 (BINDING)

---

## §1 The Substrate Interface (Charter §8.1 Layer 3)

### 1.1 Why a Stable Interface Matters

Decision 1 v2 Commitment 4 states: *"INTERCEPTA's Layer 3 module interface remains stable. Swapping substrates based on Layer 5 evidence is an O(1) architectural change, not a rebuild. This is the most important architectural commitment of v2: the swap-ability is what makes the deferred decision safe."*

The interface is therefore the architectural spine that makes the entire Decision 1 v2 framework operational. Without a stable interface, swapping substrates would require rewriting Decision 4 (drug response), Decision 5 (OOD), and Decision 7 (interpretability) downstream consumers — defeating the purpose of the evidence-driven substrate selection.

### 1.2 Formal Interface Contract

Every substrate implementation in INTERCEPTA's Layer 3 must implement the following interface:

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import torch
import numpy as np
from anndata import AnnData


class SubstrateInterface(ABC):
    """
    The architectural contract for INTERCEPTA cell representation substrates.

    Implementing classes commit to:
    - Stateful loading (init or load_pretrained)
    - Forward inference (encode)
    - Optional fine-tuning (fit, may raise NotImplementedError for frozen substrates)
    - Dimensionality declaration (output_dim property)
    - Metadata propagation (cell-level and batch-level attributes)
    - Memory contract (chunked inference for cells > MEMORY_THRESHOLD)
    """

    # Class-level metadata (override in subclasses)
    NAME: str = "abstract_substrate"
    NATIVE_DIM: int = -1  # native embedding dim (e.g., scVI=30, scFoundation=512)
    REQUIRES_GPU: bool = False
    REQUIRES_PRETRAINING: bool = False
    LICENSE: str = "unspecified"  # e.g., "BSD-3", "MIT", "Apache-2.0"
    MEMORY_THRESHOLD: int = 100_000  # cells; above this, chunked inference required

    @abstractmethod
    def load_pretrained(self, weights_path: str) -> None:
        """Load pretrained weights from disk or Hugging Face Hub.

        Args:
            weights_path: filesystem path or HF identifier
                          e.g., '/scratch/akula.pra/INTERCEPTA/models/scfoundation_100M.pt'
                          or 'biomap-research/scFoundation' (HF format)

        Raises:
            FileNotFoundError if weights not found
            ValueError if substrate doesn't require pretraining
        """
        raise NotImplementedError

    @abstractmethod
    def encode(
        self,
        adata: AnnData,
        batch_key: Optional[str] = None,
        chunk_size: Optional[int] = None,
        cache_path: Optional[str] = None,
    ) -> np.ndarray:
        """Encode cells into the substrate's representation space.

        Args:
            adata: AnnData object with .X (expression matrix, cells x genes),
                   .var (gene metadata), .obs (cell metadata)
            batch_key: optional column name in adata.obs for batch covariate
                       (e.g., 'donor_id', 'study_id'); ignored by substrates
                       that don't condition on batch
            chunk_size: process cells in chunks of this size; defaults to
                        MEMORY_THRESHOLD-aware automatic chunking
            cache_path: if provided, cache embeddings to disk (HDF5);
                        reuse on subsequent calls with same input hash

        Returns:
            embedding array of shape (n_cells, NATIVE_DIM); embedding is in
            the substrate's native space (use project_to_canonical for 512-dim)

        Raises:
            ValueError if adata is incompatible (missing required columns,
            wrong dtype, etc.)
        """
        raise NotImplementedError

    def project_to_canonical(self, embedding: np.ndarray) -> np.ndarray:
        """Project from native dim to INTERCEPTA canonical 512-dim.

        Default implementation uses linear projection layer trained jointly
        with downstream tasks; substrates with NATIVE_DIM == 512 may override
        to identity. Substrates with NATIVE_DIM < 512 zero-pad; substrates
        with NATIVE_DIM > 512 use learned linear projection (initialized via
        truncated PCA on a held-out fit set).

        Args:
            embedding: array of shape (n_cells, NATIVE_DIM)

        Returns:
            array of shape (n_cells, 512)
        """
        n_cells, dim = embedding.shape
        if dim == 512:
            return embedding
        elif dim < 512:
            # Zero-pad with truncated normal noise (1e-4 std) to prevent
            # zero-vector clustering artifacts in downstream UMAP/PCA
            padding = np.random.normal(0, 1e-4, (n_cells, 512 - dim)).astype(
                embedding.dtype
            )
            return np.hstack([embedding, padding])
        else:
            # NATIVE_DIM > 512: requires learned projection (lazy-load)
            if not hasattr(self, "_canonical_projector"):
                raise RuntimeError(
                    f"{self.NAME} NATIVE_DIM={dim} > 512; fit_canonical_projector "
                    "must be called before project_to_canonical"
                )
            return embedding @ self._canonical_projector

    def fit_canonical_projector(
        self,
        fit_adata: AnnData,
        method: str = "truncated_pca",
        random_state: int = 42,
    ) -> None:
        """Fit the projection from NATIVE_DIM > 512 to canonical 512-dim.

        Called once per substrate per dataset family (e.g., once for sci-Plex3,
        once for GDSC). Projector cached to disk.

        Args:
            fit_adata: representative AnnData for fitting the projector
            method: 'truncated_pca' (default) or 'random_gaussian'
            random_state: reproducibility seed
        """
        if self.NATIVE_DIM <= 512:
            self._canonical_projector = None
            return
        embedding = self.encode(fit_adata)
        if method == "truncated_pca":
            from sklearn.decomposition import TruncatedSVD
            svd = TruncatedSVD(n_components=512, random_state=random_state)
            svd.fit(embedding)
            self._canonical_projector = svd.components_.T  # (NATIVE_DIM, 512)
        elif method == "random_gaussian":
            rng = np.random.RandomState(random_state)
            self._canonical_projector = rng.normal(
                0, 1.0 / np.sqrt(self.NATIVE_DIM), (self.NATIVE_DIM, 512)
            ).astype(embedding.dtype)
        else:
            raise ValueError(f"Unknown projection method: {method}")

    @abstractmethod
    def fit(
        self,
        adata: AnnData,
        batch_key: Optional[str] = None,
        epochs: int = 100,
        **kwargs,
    ) -> Dict[str, Any]:
        """Train or fine-tune the substrate on adata.

        For frozen FM substrates (e.g., scFoundation default mode):
            raise NotImplementedError("scFoundation is frozen by default; "
                                       "use fit_lora for LoRA fine-tuning")

        For trainable substrates (scVI, scTOP basis fit, PCA fit):
            train to convergence; return loss curves and convergence metrics.

        Returns:
            dict with keys: 'final_loss', 'loss_history', 'epochs_trained',
            'wall_clock_seconds', 'substrate_metadata' (substrate-specific)
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def output_dim(self) -> int:
        """Return the native output dimensionality."""
        return self.NATIVE_DIM

    def get_metadata(self) -> Dict[str, Any]:
        """Return substrate metadata for logging and reproducibility."""
        return {
            "name": self.NAME,
            "native_dim": self.NATIVE_DIM,
            "requires_gpu": self.REQUIRES_GPU,
            "requires_pretraining": self.REQUIRES_PRETRAINING,
            "license": self.LICENSE,
            "memory_threshold": self.MEMORY_THRESHOLD,
        }

    def smoke_test(self, n_cells: int = 1000, n_genes: int = 20000) -> bool:
        """Run a minimal smoke test: synthetic data in, embedding out.

        Returns True if substrate successfully encodes synthetic data without
        crashing. Used in L2.1 §11 pass criteria.

        Args:
            n_cells: synthetic cell count
            n_genes: synthetic gene count

        Returns:
            True if encode() returns array of shape (n_cells, NATIVE_DIM)
            without exception
        """
        # Generate synthetic counts (negative binomial approximation via Poisson)
        rng = np.random.RandomState(42)
        X = rng.poisson(lam=1.0, size=(n_cells, n_genes)).astype(np.float32)
        var = {"gene_ids": [f"GENE_{i}" for i in range(n_genes)]}
        obs = {"batch": np.random.choice(["A", "B"], size=n_cells)}
        adata = AnnData(X=X, var=var, obs=obs)
        try:
            emb = self.encode(adata, batch_key="batch")
            assert emb.shape == (n_cells, self.NATIVE_DIM), (
                f"Shape mismatch: expected ({n_cells}, {self.NATIVE_DIM}), "
                f"got {emb.shape}"
            )
            return True
        except Exception as e:
            print(f"Smoke test failed for {self.NAME}: {e}")
            return False
```

### 1.3 Interface Contract Rationale

Each design choice in the interface above is anchor-justified:

**AnnData input format.** Per Q9 anchor 2 (scvi-tools ecosystem), AnnData is the standardized data format used by every method in the INTERCEPTA stack (scvi-tools, Scanpy, CPA, scGen, CellPLM). Using AnnData as the canonical input means all four substrates can directly consume the same dataset preparation pipeline.

**Optional batch_key parameter.** Per Decision 2 (cohort harmonization), batch covariate conditioning is needed for scANVI/MrVI substrates but irrelevant for scTOP (which doesn't condition on batch in its parameter-free form). Making batch_key optional means substrate-independent calling code.

**Chunked inference contract.** Per Q9 anchor 1, scFoundation 100M and UCE 650M inference at full Tabula Sapiens scale (~36M cells) requires chunking. Per Theunissen 2025 (Q5 anchor 1), large atlas evaluation is the standard test setting. The MEMORY_THRESHOLD = 100K default is conservative and tuned for A100 40GB VRAM with reasonable batch sizes.

**Cache path parameter.** Per Q9 anchor 1 explicit operational commitment: pre-compute embeddings to /scratch and reuse. This is a hard requirement for cost-effective deployment per Decision 9 v2.

**project_to_canonical method with 512-dim default.** Per CSO ruling for B2 branch point: 512 is the industry-standard embedding dimensionality (matches scFoundation native, scGPT, BERT/GPT-family transformers). Substrates with smaller native dim (scVI = 30, scTOP = depends on cell type count) zero-pad; substrates with larger native dim (UCE = 1280, Geneformer V2 = 768) use truncated PCA. Either operation is O(1) per cell at inference.

**Smoke test as part of interface.** Per L2.1 §11 pass criteria, every substrate must pass smoke_test() before being accepted. This catches integration errors early and is the basic CI check.

### 1.4 What the Interface Does Not Specify

To prevent over-engineering:
- The interface does not specify training hyperparameters per substrate (deferred to §3-§6 per substrate)
- The interface does not specify caching backend (HDF5, Zarr, or LMDB — operational detail)
- The interface does not specify GPU allocation (Decision 9 v2 SLURM job script detail)
- The interface does not specify how Decision 4 v2 L7 consumes the embedding (that is L2.2)

---

## §2 Substrate A — scFoundation (Default per Commitment 1)

### 2.1 Why scFoundation as Default

Decision 1 v2 Commitment 1 chose scFoundation as the default development substrate. The rationale per Decision 1 v2:

> *"scFoundation is the largest open FM with the most permissive license and the most direct scvi-tools integration (Decision 2 compatibility). Choosing it as default does NOT commit to FM-based architecture; it commits to using a concrete FM substrate as one of the four paradigms under test."*

Quantitative substantiation from Q1 anchor reads:

- **scFoundation F1 = 0.971 (layer freezing) / 0.947 (LoRA)** on pooled-data drug response per scDrugMap benchmark (Wang et al. 2025) — the highest pooled-data F1 of any FM tested
- **100M parameters** (Hao 2024, Nature Methods) — large enough to encode rich representations but small enough for single-A100 inference
- **50M-cell pretraining corpus** — at the same order as TEDDY (116M) but with peer-reviewed Nature Methods backing
- **Asymmetric encoder-decoder MAE architecture** with rank-value encoding — distinct from scGPT's autoregressive style and UCE's protein-language tokenization, providing architectural diversity in INTERCEPTA's FM portfolio
- **scvi-tools integration available** via Hugging Face Hub distribution

### 2.2 scFoundation Architecture Details (per Hao 2024)

- **Tokenization:** Rank-value encoding (each gene's expression rank in the cell)
- **Encoder:** Asymmetric MAE encoder, deeper than decoder, processes the visible (non-masked) gene rank tokens
- **Decoder:** Lightweight reconstruction head, predicts masked gene ranks
- **Embedding:** Cell-level pooled embedding from encoder, native 512-dim
- **Pretraining objective:** Masked rank-value prediction with high masking ratio (~50%)
- **Pretraining corpus:** 50M+ human single-cell RNA-seq cells, multi-tissue

### 2.3 Implementation Specification

```python
class scFoundationSubstrate(SubstrateInterface):
    """
    scFoundation FM substrate (default per Decision 1 v2 Commitment 1).

    Source: Hao et al. 2024, Nature Methods, BiomapAI
    License: open (commercial-compatible)
    Native dim: 512 (matches INTERCEPTA canonical; no projection needed)
    """

    NAME = "scfoundation"
    NATIVE_DIM = 512
    REQUIRES_GPU = True
    REQUIRES_PRETRAINING = True
    LICENSE = "open-biomap"  # to be verified at install time
    MEMORY_THRESHOLD = 50_000  # chunked above 50K cells on single A100 40GB

    DEFAULT_WEIGHTS = "biomap-research/scFoundation"  # HF Hub identifier
    DEFAULT_CACHE_DIR = "/scratch/akula.pra/INTERCEPTA/models/"
    DEFAULT_EMBEDDING_CACHE = "/scratch/akula.pra/INTERCEPTA/embeddings/scfoundation/"

    def __init__(
        self,
        weights_path: Optional[str] = None,
        device: str = "cuda",
        use_lora: bool = False,
        precision: str = "fp16",  # fp32 / fp16 / bf16
    ):
        super().__init__()
        self.weights_path = weights_path or self.DEFAULT_WEIGHTS
        self.device = device
        self.use_lora = use_lora
        self.precision = precision
        self._model = None  # lazy-load on first encode()

    def load_pretrained(self, weights_path: Optional[str] = None) -> None:
        """Load scFoundation weights from Hugging Face Hub or local /scratch."""
        from transformers import AutoModel  # placeholder; scFoundation API
        # actual API depends on BiomapAI release
        path = weights_path or self.weights_path
        self._model = AutoModel.from_pretrained(
            path, cache_dir=self.DEFAULT_CACHE_DIR
        )
        if self.precision in ("fp16", "bf16"):
            self._model = self._model.half() if self.precision == "fp16" else self._model.bfloat16()
        self._model = self._model.to(self.device).eval()

    def encode(
        self,
        adata: AnnData,
        batch_key: Optional[str] = None,
        chunk_size: Optional[int] = None,
        cache_path: Optional[str] = None,
    ) -> np.ndarray:
        if self._model is None:
            self.load_pretrained()
        # Check cache first
        if cache_path and self._cache_hit(adata, cache_path):
            return self._load_from_cache(cache_path)
        chunk_size = chunk_size or min(self.MEMORY_THRESHOLD, adata.shape[0])
        # scFoundation expects rank-value encoded input;
        # rank-encoding is data-prep, done here
        embeddings = []
        with torch.no_grad():
            for start in range(0, adata.shape[0], chunk_size):
                end = min(start + chunk_size, adata.shape[0])
                chunk = adata[start:end].copy()
                rank_tokens = self._rank_encode(chunk)
                emb = self._model(rank_tokens).cpu().numpy()
                embeddings.append(emb)
        result = np.concatenate(embeddings, axis=0)
        if cache_path:
            self._save_to_cache(result, cache_path)
        return result

    def fit(
        self,
        adata: AnnData,
        batch_key: Optional[str] = None,
        epochs: int = 10,
        **kwargs,
    ) -> Dict[str, Any]:
        if not self.use_lora:
            raise NotImplementedError(
                "scFoundation is frozen by default; "
                "instantiate with use_lora=True for LoRA fine-tuning"
            )
        # LoRA fine-tuning per Hu et al. 2021 methodology
        # only adapters trained; base FM weights frozen
        # Implementation: peft library or custom LoRA wrapper
        from peft import LoraConfig, get_peft_model
        # ... (LoRA training loop)
        return {
            "final_loss": ...,
            "loss_history": [...],
            "epochs_trained": epochs,
            "wall_clock_seconds": ...,
            "substrate_metadata": {"lora_rank": 16, "lora_alpha": 32},
        }

    def _rank_encode(self, adata: AnnData) -> torch.Tensor:
        """Convert expression matrix to rank-value tokens.

        scFoundation tokenization: rank each gene's expression within the cell,
        normalize, embed via gene-id lookup table.
        """
        # implementation per Hao 2024 Supplementary Methods
        ...

    def _cache_hit(self, adata: AnnData, cache_path: str) -> bool:
        """Check if embedding already cached for this adata."""
        # Hash adata.X + adata.obs_names; compare to cached manifest
        ...

    def _load_from_cache(self, cache_path: str) -> np.ndarray:
        """Load cached embedding from HDF5."""
        import h5py
        with h5py.File(cache_path, "r") as f:
            return f["embedding"][:]

    def _save_to_cache(self, embedding: np.ndarray, cache_path: str) -> None:
        """Save embedding to HDF5 with adata hash manifest."""
        import h5py
        with h5py.File(cache_path, "w") as f:
            f.create_dataset("embedding", data=embedding, compression="gzip")

    @property
    def output_dim(self) -> int:
        return self.NATIVE_DIM
```

### 2.4 Multi-FM Portfolio Extension (per Q1 Synthesis Recommendation)

The Q1 synthesis identifies that no single FM dominates across all tasks (scFoundation pools-data F1 = 0.971; UCE cross-data fine-tuned F1 = 0.774; scGPT cross-data zero-shot F1 = 0.858; Geneformer the only non-cancer-validated FM). Per Q1 synthesis §5:

> *"For INTERCEPTA's Layer 2 architecture: the implication is that we should NOT commit to a single FM. The architectural choice should be deployment-scenario-aware: pool-data scenario → scFoundation; cross-data fine-tunable → UCE; zero-shot or limited compute → scGPT or Geneformer. INTERCEPTA could even use multiple FMs as ensemble."*

L2.1 implements this via a **multi-FM portfolio under one substrate class family**:

- **scFoundationSubstrate** — default, pools-data optimal (per §2.3)
- **UCESubstrate** — cross-species via ESM2 tokenization, 650M params, NATIVE_DIM=1280 (requires canonical projector)
- **scGPTSubstrate** — zero-shot deployment, 51M params, NATIVE_DIM=512
- **GeneformerSubstrate** — non-cancer validation precedent, ~10M params, NATIVE_DIM=512

Each FM extension class subclasses scFoundationSubstrate's pattern (lazy-load, chunked inference, caching) but specifies its own weights path, tokenization, and forward pass.

**FM portfolio selection logic for Layer 5 ablations** (deferred to §8.4):
- Pooled-data scenario → scFoundationSubstrate first
- Cross-data scenario → UCESubstrate first (highest cross-data F1 per scDrugMap)
- Zero-shot / limited compute → scGPTSubstrate first
- Non-cancer / cross-disease → GeneformerSubstrate first (only FM with non-cancer validation)
- Multi-FM ensemble → optional Layer 5+ extension if no single FM clearly wins

### 2.5 Compute Envelope per Q9

Per Q9 anchor 1 (compute synthesis) and Decision 9 v2:

- **Inference (frozen):** scFoundation 100M params on A100 40GB → batch 50K cells, ~2-3 GB peak VRAM, ~5-10 sec per 50K cells. Full sci-Plex3 (~650K cells) → ~13 chunks × 10 sec ≈ 2-3 min one-time.
- **LoRA fine-tuning (optional):** rank-16 LoRA adapters, ~0.5M trainable params. On sci-Plex3, ~1 hour on A100. Cost-effective.
- **Cached embeddings:** sci-Plex3 (650K cells) × 512-dim × fp16 = ~650K × 1024 bytes = 660 MB. GDSC + CCLE (~2K cell lines, bulk RNA-seq treated as ~2K "cells") trivial. Total /scratch storage: ~5 GB.

### 2.6 Honest Limitations (per Decision 1 v2 Commitment 5)

scFoundation as INTERCEPTA's default substrate carries the following honest uncertainty:

1. **No published drug-response head-to-head against parameter-free baselines.** Per Q1 synthesis Gap 4 and Decision 1 v2 Commitment 5, no peer-reviewed paper compares scFoundation drug response prediction to scTOP-style parameter-free methods on the same task. INTERCEPTA's Layer 5 ablations are the field's first such comparison.

2. **Cancer-dominant pretraining corpus.** Per Q1 synthesis §4, scFoundation's 50M-cell pretraining is cancer-leaning. Cross-disease transfer (U1-U3 universality dimensions) is structurally untested for scFoundation specifically.

3. **No mechanistic interpretability natively.** Per Kendiukhov 2026 spectral geometry analysis (Q1 anchor 7), FM internal representations encode rich biological structure but minimal causal regulatory logic. Mechanism trace requires external GRN/CRISPRi data per Decision 7 (deferred to L2.4).

4. **License terms require deployment-time verification.** "open-biomap" license placeholder in the class is provisional pending CEO review of BiomapAI's distributed license terms at deployment time.

---

## §3 Substrate B — scTOP Parameter-Free (Co-equal per Commitment 2)

### 3.1 Why scTOP Is Co-equal (Not a Fallback)

Decision 1 v2 Commitment 2 makes the Souza & Mehta scTOP methodology **a co-equal baseline, not a fallback.** The rationale per Decision 1 v2:

> *"Three baselines must be implemented co-equally with the default substrate, not as fallbacks... Per Decision 8 Commitment 5 (Souza & Mehta methodological bar), INTERCEPTA cannot publish architectural claims of FM benefit without rigorous comparison to at least Baseline B with the same hyperparameter search budget at 25% scale."*

This is the operational expression of the **methodological bar from Souza & Mehta 2026**: any claim of FM superiority requires properly-tuned parameter-free comparison. INTERCEPTA's architectural integrity depends on enforcing this bar against itself.

Empirical substantiation (from Souza & Mehta 2026 per Decision 1 v2 cited evidence):
- scTOP matches TranscriptFormer on Tabula Sapiens 2.0 (mean macro F1 0.899 vs 0.910/0.907)
- scTOP beats FMs on cross-species annotation across all 8 mammalian species (including platypus)
- scTOP matches FMs on SARS-CoV-2 disease-state classification (4 donors)
- scTOP runs on CPU; zero free parameters; zero training time

### 3.2 scTOP Methodology Details

scTOP is a **parameter-free linear projection method** in the sense that:
- No neural network is trained
- No iterative optimization
- Classification is direct linear projection onto a reference basis built from labeled cell types

The pipeline is:
1. **z-score normalization per cell** (gene expression normalized to mean=0, std=1 across genes within each cell)
2. **Pseudo-bulk reference basis construction** from labeled training cells (one column per cell type, computed as the mean z-scored profile of cells with that label)
3. **Non-orthogonal linear projection** of new cells onto the reference basis via least-squares (no orthogonality constraint, allowing reference basis vectors to be correlated)
4. **Classification:** argmax over the projection coefficients (highest-loading cell type wins)

For INTERCEPTA's purposes, scTOP produces:
- **Per-cell projection coefficients** (vector of length n_cell_types) — this is the "embedding"
- **NATIVE_DIM = n_cell_types** (variable, depends on reference)
- **Interpretability native:** each coefficient is the cell's similarity to a specific labeled cell type

For substrate purposes, scTOP's projection coefficients serve as the cell representation. The embedding dim is variable but typically small (10-100 cell types in most references). To use as an INTERCEPTA substrate, the projection coefficients project to canonical 512-dim via `fit_canonical_projector` (zero-padded since NATIVE_DIM < 512 in the typical case).

### 3.3 Implementation Specification

```python
class scTOPSubstrate(SubstrateInterface):
    """
    scTOP parameter-free substrate (co-equal per Decision 1 v2 Commitment 2).

    Source: Souza & Mehta 2026 (Boston University Physics, arXiv 2602.16696)
    License: open (academic; verify per Souza & Mehta release)
    Methodology: z-score per cell + linear projection onto pseudo-bulk reference

    This substrate is the Decision 8 Commitment 5 methodological bar
    comparator. INTERCEPTA's architectural integrity requires this baseline
    matches the hyperparameter search budget (>= 25% of FM scale) before
    any FM benefit claim is published.
    """

    NAME = "sctop"
    NATIVE_DIM = -1  # determined at fit time by reference cell type count
    REQUIRES_GPU = False
    REQUIRES_PRETRAINING = False
    LICENSE = "open-academic"  # verify per Souza & Mehta repo
    MEMORY_THRESHOLD = 1_000_000  # high; method is memory-cheap

    def __init__(
        self,
        reference_basis: Optional[np.ndarray] = None,
        reference_celltypes: Optional[list] = None,
        normalization: str = "zscore",  # per Souza & Mehta methodology
    ):
        super().__init__()
        self._reference_basis = reference_basis  # shape (n_genes, n_celltypes)
        self._reference_celltypes = reference_celltypes or []
        self.normalization = normalization
        if reference_basis is not None:
            self.NATIVE_DIM = reference_basis.shape[1]

    def load_pretrained(self, reference_path: str) -> None:
        """Load a pseudo-bulk reference basis from disk (HDF5 or NPZ).

        Reference is precomputed via fit() on a labeled reference dataset
        (e.g., Tabula Sapiens 2.0 for Layer 5 sanity check; or sci-Plex3
        annotated cells for INTERCEPTA-specific reference).
        """
        import h5py
        with h5py.File(reference_path, "r") as f:
            self._reference_basis = f["basis"][:]  # (n_genes, n_celltypes)
            self._reference_celltypes = [
                ct.decode() for ct in f["celltypes"][:]
            ]
            self._reference_genes = [g.decode() for g in f["genes"][:]]
        self.NATIVE_DIM = self._reference_basis.shape[1]

    def fit(
        self,
        adata: AnnData,
        batch_key: Optional[str] = None,
        epochs: int = 1,  # parameter-free; "epoch" is just 1 pass
        celltype_key: str = "cell_type",
        **kwargs,
    ) -> Dict[str, Any]:
        """Build the pseudo-bulk reference basis from a labeled dataset.

        Args:
            adata: AnnData with .obs[celltype_key] containing cell type labels
            celltype_key: column name in .obs with cell type annotations
            epochs: ignored (parameter-free); kept for interface compatibility

        Returns:
            dict with reference basis metadata
        """
        import time
        start = time.time()
        if celltype_key not in adata.obs.columns:
            raise ValueError(f"adata.obs missing column: {celltype_key}")
        # z-score per cell
        if self.normalization == "zscore":
            X_norm = self._zscore_per_cell(adata.X)
        else:
            raise ValueError(f"Unknown normalization: {self.normalization}")
        # Build pseudo-bulk reference: mean z-scored profile per cell type
        celltypes = adata.obs[celltype_key].unique()
        n_genes = adata.shape[1]
        basis = np.zeros((n_genes, len(celltypes)), dtype=np.float32)
        for i, ct in enumerate(celltypes):
            mask = (adata.obs[celltype_key] == ct).values
            basis[:, i] = X_norm[mask].mean(axis=0)
        self._reference_basis = basis
        self._reference_celltypes = list(celltypes)
        self._reference_genes = list(adata.var_names)
        self.NATIVE_DIM = basis.shape[1]
        wall_clock = time.time() - start
        return {
            "final_loss": 0.0,  # parameter-free; no loss
            "loss_history": [],
            "epochs_trained": 1,
            "wall_clock_seconds": wall_clock,
            "substrate_metadata": {
                "n_celltypes": self.NATIVE_DIM,
                "n_genes": n_genes,
                "normalization": self.normalization,
                "celltype_counts": adata.obs[celltype_key].value_counts().to_dict(),
            },
        }

    def encode(
        self,
        adata: AnnData,
        batch_key: Optional[str] = None,
        chunk_size: Optional[int] = None,
        cache_path: Optional[str] = None,
    ) -> np.ndarray:
        if self._reference_basis is None:
            raise RuntimeError(
                "scTOP reference not loaded; call fit() or load_pretrained()"
            )
        # Match adata genes to reference genes (handle missing genes)
        gene_indices = self._align_genes(adata.var_names, self._reference_genes)
        X_aligned = adata.X[:, gene_indices] if gene_indices is not None else adata.X
        # z-score per cell
        X_norm = self._zscore_per_cell(X_aligned)
        # Non-orthogonal linear projection via least-squares
        # coefficients = (basis^T basis)^-1 basis^T X_norm^T
        # For numerical stability, use lstsq
        basis = self._reference_basis
        # X_norm shape: (n_cells, n_genes); basis shape: (n_genes, n_celltypes)
        # We want: coefs shape (n_cells, n_celltypes)
        # Solve: basis @ coefs.T = X_norm.T, so coefs.T = lstsq(basis, X_norm.T)
        coefs, residuals, rank, _ = np.linalg.lstsq(basis, X_norm.T, rcond=None)
        embedding = coefs.T.astype(np.float32)  # (n_cells, n_celltypes)
        if cache_path:
            self._save_to_cache(embedding, cache_path)
        return embedding

    def _zscore_per_cell(self, X: np.ndarray) -> np.ndarray:
        """Per-cell z-score normalization (Souza & Mehta methodology)."""
        # mean and std per cell (axis=1)
        mu = X.mean(axis=1, keepdims=True)
        sigma = X.std(axis=1, keepdims=True) + 1e-8  # avoid div-by-zero
        return (X - mu) / sigma

    def _align_genes(
        self, target_genes: list, reference_genes: list
    ) -> Optional[np.ndarray]:
        """Return indices into target_genes matching reference_genes order.

        Missing genes filled with zeros (gene drop-in convention).
        Returns None if perfect match (no realignment needed).
        """
        # implementation: dict lookup, handle missing genes
        ...

    @property
    def output_dim(self) -> int:
        if self.NATIVE_DIM < 0:
            raise RuntimeError("scTOP not fit; output_dim undefined")
        return self.NATIVE_DIM
```

### 3.4 Tabula Sapiens 2.0 Lock Verification (per Decision 1 v2 Termination Criterion 2)

Decision 1 v2 specifies:
> *"Baseline B (scTOP-style) is implemented and verified to reproduce Souza & Mehta's reported numbers on Tabula Sapiens 2.0 within 2 percentage points (sanity check)"*

L2.1 specifies the verification protocol:

1. Download Tabula Sapiens 2.0 from CZI CELLxGENE (https://cellxgene.cziscience.com/collections/...)
2. Apply 80/20 train/test split stratified by tissue (per Souza & Mehta methodology)
3. Fit scTOPSubstrate on training split with celltype_key='cell_type_ontology'
4. Encode test split; classify by argmax over projection coefficients
5. Compute mean macro F1 across all cell types
6. Pass criterion: macro F1 ≥ 0.879 (= Souza & Mehta reported 0.899 minus 2pp)

This verification runs in the Layer 5 ablation infrastructure (§8) before any cross-substrate comparison is published.

### 3.5 scTOP Integration with Downstream Decisions

**For Decision 5 (OOD detection):**
Per scTOP §3.3, the projection coefficients are similarity scores against labeled reference cell types. **A cell with low maximum coefficient is structurally OOD** (no reference type matches). This provides a free OOD signal native to scTOP without requiring conformal prediction (Decision 5 v2 Layer 5.3) — though conformal prediction stacks on top per Decision 5 stack.

**For Decision 7 (mechanistic interpretability):**
Per multi-scale interpretability composite (Q7 anchor 4) §3.2:
> *"If parameter-free substrate wins (scTOP per Souza-Mehta): Linear projection coefficients directly expose gene-level attribution. No IG path computation needed — interpretability is 'built in'. This is methodologically easier and more interpretable than FM substrate."*

This is the architectural reward for the scTOP path: interpretability comes free.

**For Decision 9 (compute):**
scTOP zero-cost compute envelope is the dominant savings opportunity. If scTOP wins or ties on the Layer 5 grid, INTERCEPTA's compute envelope shrinks dramatically — universality at single-institution academic scale becomes vastly easier.

### 3.6 Honest Limitations

1. **scTOP requires a labeled reference dataset.** Without cell type labels, the pseudo-bulk basis cannot be constructed. For purely unsupervised settings, scTOP is not directly applicable.
2. **Cell type count constrains NATIVE_DIM.** A reference with only 5 cell types produces 5-dim embeddings, which may be insufficient for downstream drug response prediction. Workaround: use fine-grained ontology (Tabula Sapiens has ~400 cell types) for richer reference.
3. **No cross-species capability native.** Unlike UCE (ESM2-based), scTOP requires the reference and target to share gene names. Cross-species deployment requires homolog mapping.
4. **Cannot capture novel cell states.** scTOP projects into the space of reference cell types; truly novel states project as combinations of reference types but cannot be represented as their own dimension. This is structurally limiting for disease-state discovery.

---

## §4 Substrate C — scVI/scANVI/MrVI (Probabilistic VAE; Co-equal per Commitment 2)

### 4.1 Why scVI Family Is Co-equal

Decision 1 v2 Commitment 2 specifies scVI/scANVI/MrVI as Baseline C. The rationale:

1. **scvi-tools is the production-grade framework** used across the field (Q9 anchor 2: "primary VAE framework"; Decision 2 commits to scvi-tools as primary harmonization infrastructure)
2. **scVI provides probabilistic outputs natively** — Decision 5 v2 Layer 5.1 (VAE posterior uncertainty) consumes scVI directly
3. **scANVI extends scVI with semi-supervised labels** — useful when partial cell type labels are available
4. **MrVI provides multi-resolution variation** — captures both per-cell and per-sample variation, useful for patient-level deployment
5. **BSD-3 license** — fully permissive (Decision 10 alignment)
6. **Kedzierska 2023 finding** (Q1 anchor 6): scVI per-dataset-trained sometimes matches or beats FMs on cell type integration — making scVI a genuine empirical competitor to FMs, not just a strawman baseline

### 4.2 scVI Architecture Details (per Lopez 2018)

- **Encoder:** Multi-layer perceptron, gene expression → latent posterior parameters (μ, σ²)
- **Latent dimensionality:** Default 10-30 (INTERCEPTA configures 30; latent < 512 → zero-pad via project_to_canonical)
- **Decoder:** Multi-layer perceptron, latent + batch covariate → gene expression rate (negative binomial likelihood)
- **Training objective:** ELBO maximization (reconstruction + KL regularization)
- **Batch conditioning:** Categorical batch indicator concatenated to latent at decoder input
- **Output:** Latent posterior sample (or mean) per cell — usable directly as embedding

### 4.3 scANVI Extension (per Xu 2021)

- Adds **semi-supervised classification** layer on top of scVI
- Latent space conditioned on cell type label (when known) via auxiliary classifier
- Unlabeled cells trained via standard scVI ELBO
- Useful for sci-Plex3 (~60% labeled cell types) or partially-labeled tumor data

### 4.4 MrVI Extension (per Boyeau 2025)

- **Multi-resolution VAE** with hierarchical latent space
- Captures per-cell variation (z_cell) and per-sample variation (z_sample) jointly
- Useful for patient-level deployment (sample = patient)
- Production-ready in scvi-tools

### 4.5 Implementation Specification

```python
class scVISubstrate(SubstrateInterface):
    """
    scVI VAE substrate (co-equal per Decision 1 v2 Commitment 2).

    Source: Lopez et al. 2018, Nature Methods
    Framework: scvi-tools (Yosef lab, UC Berkeley)
    License: BSD-3 (permissive)
    Native dim: 10-30 (INTERCEPTA configures 30; project_to_canonical zero-pads to 512)

    Decision 5 v2 Layer 5.1 (VAE posterior uncertainty) consumes scVI output
    directly; this substrate is methodologically aligned with the OOD stack.
    """

    NAME = "scvi"
    NATIVE_DIM = 30
    REQUIRES_GPU = True  # GPU recommended for training; CPU OK for inference
    REQUIRES_PRETRAINING = False  # trained per-dataset, not pretrained
    LICENSE = "BSD-3"
    MEMORY_THRESHOLD = 500_000  # scvi-tools chunked inference handles atlas-scale

    def __init__(
        self,
        n_latent: int = 30,
        n_hidden: int = 128,
        n_layers: int = 1,
        dropout_rate: float = 0.1,
        gene_likelihood: str = "nb",  # negative binomial per Lopez 2018
    ):
        super().__init__()
        self.n_latent = n_latent
        self.NATIVE_DIM = n_latent
        self.n_hidden = n_hidden
        self.n_layers = n_layers
        self.dropout_rate = dropout_rate
        self.gene_likelihood = gene_likelihood
        self._model = None

    def load_pretrained(self, weights_path: str) -> None:
        """Load a previously-trained scVI model from disk."""
        import scvi
        self._model = scvi.model.SCVI.load(weights_path)

    def fit(
        self,
        adata: AnnData,
        batch_key: Optional[str] = None,
        epochs: int = 400,  # scvi-tools default
        **kwargs,
    ) -> Dict[str, Any]:
        import scvi
        import time
        scvi.model.SCVI.setup_anndata(
            adata, batch_key=batch_key
        )
        self._model = scvi.model.SCVI(
            adata,
            n_latent=self.n_latent,
            n_hidden=self.n_hidden,
            n_layers=self.n_layers,
            dropout_rate=self.dropout_rate,
            gene_likelihood=self.gene_likelihood,
        )
        start = time.time()
        self._model.train(max_epochs=epochs, **kwargs)
        wall_clock = time.time() - start
        history = self._model.history
        return {
            "final_loss": float(history["elbo_train"].iloc[-1]),
            "loss_history": history["elbo_train"].tolist(),
            "epochs_trained": epochs,
            "wall_clock_seconds": wall_clock,
            "substrate_metadata": {
                "n_latent": self.n_latent,
                "gene_likelihood": self.gene_likelihood,
            },
        }

    def encode(
        self,
        adata: AnnData,
        batch_key: Optional[str] = None,
        chunk_size: Optional[int] = None,
        cache_path: Optional[str] = None,
    ) -> np.ndarray:
        if self._model is None:
            raise RuntimeError(
                "scVI not trained; call fit() or load_pretrained()"
            )
        embedding = self._model.get_latent_representation(adata)
        if cache_path:
            self._save_to_cache(embedding, cache_path)
        return embedding.astype(np.float32)

    @property
    def output_dim(self) -> int:
        return self.NATIVE_DIM


class scANVISubstrate(scVISubstrate):
    """scANVI extension of scVI with semi-supervised cell type labels."""
    NAME = "scanvi"

    def fit(
        self,
        adata: AnnData,
        batch_key: Optional[str] = None,
        labels_key: Optional[str] = None,
        epochs: int = 400,
        **kwargs,
    ) -> Dict[str, Any]:
        import scvi
        scvi.model.SCANVI.setup_anndata(
            adata, batch_key=batch_key, labels_key=labels_key,
            unlabeled_category="Unknown",
        )
        # ... (analogous to scVI fit but using SCANVI class)


class MrVISubstrate(scVISubstrate):
    """MrVI extension with multi-resolution (cell + sample) latent."""
    NAME = "mrvi"

    def fit(
        self,
        adata: AnnData,
        batch_key: Optional[str] = None,
        sample_key: Optional[str] = None,
        epochs: int = 400,
        **kwargs,
    ) -> Dict[str, Any]:
        import scvi
        scvi.external.MRVI.setup_anndata(
            adata, batch_key=batch_key, sample_key=sample_key,
        )
        # ... (analogous to scVI fit but using MRVI class)
```

### 4.6 scVI Family Integration with Downstream Decisions

**For Decision 5 (OOD detection):** scVI's posterior provides native aleatoric/epistemic decomposition (Lopez 2018 §3). Per Theunissen 2025 (Q5 anchor 1), this decomposition is critical for honest OOD reporting. scVI substrate makes Decision 5 v2 Layer 5.1 (VAE posterior uncertainty) directly available without retrofitting.

**For Decision 7 (interpretability):** scVI's decoder provides gene-level attribution via Integrated Gradients with hidden-space baseline (Jha 2020 methodology per Q7 anchor — though Jha file content not in current session). Per Q7 multi-scale composite: "scVI/scANVI substrate: IG+SmoothGrad over VAE decoder for gene reconstruction. Posterior latent space provides aleatoric+epistemic decomposition. Standard methodology applies."

**For Decision 2 (cohort harmonization):** scVI's batch covariate conditioning is the canonical mechanism (Lopez 2018 Section 2.1 batch effect modeling). Decision 2 commits to scvi-tools as primary harmonization infrastructure; scVI substrate IS the Decision 2 mechanism viewed as a substrate.

**For Decision 9 (compute):** scVI training on sci-Plex3 (650K cells, 30-dim latent): ~2-4 hours on A100. Inference: minutes. Production-grade per Q9 anchor 2.

### 4.7 Honest Limitations

1. **Per-dataset training required.** Unlike FMs (frozen pretrained) or scTOP (parameter-free), scVI must be trained on each new dataset. Cross-dataset deployment requires either retraining or scArches-style architecture surgery.
2. **Linear latent space.** Despite being a deep model, scVI's latent is structurally linear-ish (VAE reconstruction prior). Some complex biological variation may not be capturable.
3. **NATIVE_DIM = 30 requires zero-padding** for INTERCEPTA canonical 512-dim. Zero-padding is mathematically a no-op for downstream linear models but may interact subtly with non-linear consumers (Decision 4 L7). Verify in ablations.
4. **Mode collapse risk in extreme regimes** (per Diversity-by-Design 2025 critique referenced in scGen anchor). Standard regularization mitigates but does not eliminate.

---

## §5 Substrate D — PCA + HVG Classical (Co-equal per Commitment 2)

### 5.1 Why PCA + HVG Is the Reference Floor

Decision 1 v2 Commitment 2 specifies PCA + HVG as Baseline A. This is the **decade-old simple methodology** that Kedzierska 2023 found outperforms scGPT zero-shot on 4 of 5 datasets in cell integration tasks (Q1 anchor 6). Its purpose in INTERCEPTA:

1. **Reference floor.** Any substrate that doesn't beat PCA + HVG is not producing value beyond classical bioinformatics.
2. **Compute envelope baseline.** PCA+HVG runs on CPU in seconds. Anything claiming SOTA must justify its compute cost against this floor.
3. **scIB benchmark precedent.** Per Luecken 2022 (Q2 scIB benchmark), PCA + HVG is the standard low-cost baseline.

### 5.2 Methodology Details

The classical pipeline:

1. **HVG selection.** Identify top 2,000 highly variable genes via Scanpy's `sc.pp.highly_variable_genes` (Seurat v3-style by default, with batch-aware option per Stuart 2019).
2. **Normalization.** Total counts per cell → 10,000 → log1p (standard Scanpy normalization).
3. **Scaling.** Optional gene-wise z-scoring (zero mean, unit variance per gene).
4. **PCA.** Truncated SVD to 50-100 principal components.
5. **Output.** PCA-reduced embedding as cell representation.

### 5.3 Implementation Specification

```python
class PCAHVGSubstrate(SubstrateInterface):
    """
    Classical PCA + HVG substrate (co-equal per Decision 1 v2 Commitment 2).

    Methodology: top-2000 HVG, log1p normalization, PCA to 50-100 components.
    This is the Decision 1 v2 reference floor; any FM that doesn't beat this
    is not producing methodological value beyond classical bioinformatics.

    Source: standard Scanpy/Seurat pipeline; Kedzierska 2023 documented that
    HVG outperforms Geneformer on 4 of 5 datasets in cell integration.

    License: open (Scanpy BSD-3, sklearn BSD-3)
    """

    NAME = "pca_hvg"
    NATIVE_DIM = 50  # default PCA components
    REQUIRES_GPU = False
    REQUIRES_PRETRAINING = False
    LICENSE = "BSD-3"
    MEMORY_THRESHOLD = 5_000_000  # CPU memory only; atlas-scale feasible

    def __init__(
        self,
        n_top_genes: int = 2000,
        n_components: int = 50,
        normalization: str = "scanpy_default",  # 1e4 normalize + log1p
    ):
        super().__init__()
        self.n_top_genes = n_top_genes
        self.n_components = n_components
        self.NATIVE_DIM = n_components
        self.normalization = normalization
        self._hvg_genes = None
        self._pca = None
        self._normalizer_state = None

    def load_pretrained(self, weights_path: str) -> None:
        """Load fit PCA + HVG state from disk."""
        import joblib
        state = joblib.load(weights_path)
        self._hvg_genes = state["hvg_genes"]
        self._pca = state["pca"]
        self._normalizer_state = state["normalizer_state"]

    def fit(
        self,
        adata: AnnData,
        batch_key: Optional[str] = None,
        epochs: int = 1,
        **kwargs,
    ) -> Dict[str, Any]:
        import scanpy as sc
        from sklearn.decomposition import TruncatedSVD
        import time
        start = time.time()
        # HVG selection
        adata_local = adata.copy()
        sc.pp.normalize_total(adata_local, target_sum=1e4)
        sc.pp.log1p(adata_local)
        sc.pp.highly_variable_genes(
            adata_local,
            n_top_genes=self.n_top_genes,
            batch_key=batch_key,  # batch-aware HVG per Stuart 2019
        )
        self._hvg_genes = adata_local.var_names[adata_local.var["highly_variable"]].tolist()
        # PCA fit on HVG subset
        X_hvg = adata_local[:, self._hvg_genes].X
        if hasattr(X_hvg, "toarray"):  # sparse handling
            X_hvg = X_hvg.toarray()
        self._pca = TruncatedSVD(n_components=self.n_components, random_state=42)
        self._pca.fit(X_hvg)
        wall_clock = time.time() - start
        return {
            "final_loss": 0.0,
            "loss_history": [],
            "epochs_trained": 1,
            "wall_clock_seconds": wall_clock,
            "substrate_metadata": {
                "n_hvg": len(self._hvg_genes),
                "n_components": self.n_components,
                "explained_variance_ratio": float(self._pca.explained_variance_ratio_.sum()),
            },
        }

    def encode(
        self,
        adata: AnnData,
        batch_key: Optional[str] = None,
        chunk_size: Optional[int] = None,
        cache_path: Optional[str] = None,
    ) -> np.ndarray:
        import scanpy as sc
        if self._pca is None or self._hvg_genes is None:
            raise RuntimeError(
                "PCA+HVG not fit; call fit() or load_pretrained()"
            )
        adata_local = adata.copy()
        sc.pp.normalize_total(adata_local, target_sum=1e4)
        sc.pp.log1p(adata_local)
        # Restrict to fit HVG genes (handle missing)
        common_genes = [g for g in self._hvg_genes if g in adata_local.var_names]
        if len(common_genes) < len(self._hvg_genes):
            print(f"Warning: {len(self._hvg_genes) - len(common_genes)} HVG genes missing from query")
        X_hvg = adata_local[:, common_genes].X
        if hasattr(X_hvg, "toarray"):
            X_hvg = X_hvg.toarray()
        embedding = self._pca.transform(X_hvg).astype(np.float32)
        if cache_path:
            self._save_to_cache(embedding, cache_path)
        return embedding

    @property
    def output_dim(self) -> int:
        return self.NATIVE_DIM
```

### 5.4 Honest Limitations

1. **Loses information beyond top 2,000 HVG.** Low-expression but biologically critical genes may be discarded.
2. **Linear method.** PCA cannot capture non-linear cell state structure.
3. **No batch correction within method.** Requires Harmony or scANVI for batch correction post-PCA.
4. **Per-dataset PCA refit needed** when reference HVG genes differ across datasets. Workaround: project new data onto reference PCA (with gene alignment).

---

## §6 The Substrate Swap Mechanism (Implementing Commitment 4)

### 6.1 The Swap Contract

Decision 1 v2 Commitment 4 specifies that substrate swap must be O(1) — a config change, not a code change. L2.1 implements this via Hydra (or YAML-config-driven) selection.

**Config-driven selection:**

```yaml
# config/substrate.yaml
substrate:
  name: scfoundation  # one of: scfoundation, uce, scgpt, geneformer, sctop, scvi, scanvi, mrvi, pca_hvg

  scfoundation:
    weights_path: biomap-research/scFoundation
    device: cuda
    use_lora: false
    precision: fp16

  sctop:
    reference_path: /scratch/akula.pra/INTERCEPTA/references/tabula_sapiens_v2.h5

  scvi:
    n_latent: 30
    n_hidden: 128
    n_layers: 1
    dropout_rate: 0.1
    gene_likelihood: nb

  pca_hvg:
    n_top_genes: 2000
    n_components: 50
```

**Factory function:**

```python
def create_substrate(config: Dict[str, Any]) -> SubstrateInterface:
    """Instantiate a substrate based on config.

    Used at INTERCEPTA pipeline entry point; downstream code (L2.2 L7,
    L2.3 OOD, L2.4 interpretability) receives the SubstrateInterface
    object without knowing which substrate it is.

    Args:
        config: substrate config dict (subsection of full pipeline config)

    Returns:
        Instantiated and loaded SubstrateInterface implementation
    """
    name = config["name"]
    if name == "scfoundation":
        sub = scFoundationSubstrate(**config.get("scfoundation", {}))
    elif name == "uce":
        sub = UCESubstrate(**config.get("uce", {}))
    elif name == "scgpt":
        sub = scGPTSubstrate(**config.get("scgpt", {}))
    elif name == "geneformer":
        sub = GeneformerSubstrate(**config.get("geneformer", {}))
    elif name == "sctop":
        sub = scTOPSubstrate(**config.get("sctop", {}))
    elif name == "scvi":
        sub = scVISubstrate(**config.get("scvi", {}))
    elif name == "scanvi":
        sub = scANVISubstrate(**config.get("scanvi", {}))
    elif name == "mrvi":
        sub = MrVISubstrate(**config.get("mrvi", {}))
    elif name == "pca_hvg":
        sub = PCAHVGSubstrate(**config.get("pca_hvg", {}))
    else:
        raise ValueError(f"Unknown substrate: {name}")
    # Load pretrained weights if applicable
    if sub.REQUIRES_PRETRAINING:
        weights = config.get(name, {}).get("weights_path")
        if weights:
            sub.load_pretrained(weights)
    return sub
```

### 6.2 Downstream Consumer Pattern (Showing O(1) Swap)

```python
# Decision 4 L7 drug response head — consumes any substrate
class L7DrugResponseHead(torch.nn.Module):
    def __init__(self, substrate: SubstrateInterface, ...):
        super().__init__()
        self.substrate = substrate
        # Adapter from substrate native dim to L7 input dim
        if substrate.output_dim != 512:
            self.adapter = torch.nn.Linear(substrate.output_dim, 512)
        else:
            self.adapter = torch.nn.Identity()
        # ... rest of L7 architecture (specified in L2.2)

    def forward(self, adata: AnnData, batch_key: str, drug: torch.Tensor):
        cell_emb = self.substrate.encode(adata, batch_key=batch_key)
        cell_emb_canonical = self.adapter(torch.from_numpy(cell_emb))
        # ... drug + cell prediction (L2.2 spec)
```

**Swap demonstration:** Changing `substrate.name: scfoundation` → `substrate.name: sctop` in `config/substrate.yaml` switches INTERCEPTA's entire substrate. **Zero code changes.** Decision 4 L7, Decision 5 OOD, Decision 7 interpretability — all receive the new substrate via the same interface.

This is the O(1) swap that Decision 1 v2 Commitment 4 promised, made concrete.

### 6.3 Cached Embedding Storage Convention

Per Q9 anchor 1 operational commitment, pre-computed embeddings live in /scratch with a convention:

```
/scratch/akula.pra/INTERCEPTA/embeddings/
├── scfoundation/
│   ├── sci_plex3/
│   │   ├── train_split.h5
│   │   ├── val_split.h5
│   │   └── test_split.h5
│   ├── gdsc/
│   │   └── all_cell_lines.h5
│   └── tabula_sapiens_v2/
│       └── full.h5
├── sctop/
│   ├── sci_plex3/
│   │   └── ...
│   └── tabula_sapiens_v2/
│       └── full.h5
├── scvi/
│   └── ...
└── pca_hvg/
    └── ...
```

This convention ensures embeddings are reusable across L7, OOD, and interpretability consumers — no redundant recomputation.

---

## §7 Ablation Infrastructure (Per Commitment 3)

### 7.1 The Ablation Question

Decision 1 v2 Commitment 3 specifies the binding decision rules for substrate selection:

> *"If scFoundation wins by ≥5 percentage points AUROC on the V0-V6 drug response prediction grid: keep FM as the primary substrate; Baselines remain as required ablation comparators in publications."*
>
> *"If parameter-free Baseline B wins or ties within 2 percentage points on the same grid: DEMOTE FMs from the primary substrate position; Baseline B becomes primary; FMs become optional comparators."*
>
> *"If scVI Baseline C wins: probabilistic VAE becomes primary; FMs become optional."*
>
> *"If results are scenario-dependent: INTERCEPTA commits to explicit per-scenario substrate selection logic, with the selection logic itself becoming a Layer 2 architectural component."*

L2.1 specifies the infrastructure for these decision rules to be evaluated honestly.

### 7.2 Hyperparameter Budget Allocation (Decision 8 Commitment 5 Binding)

Per Decision 8 Commitment 5 (Souza & Mehta methodological bar):
> *"Baseline B receives ≥25% of FM hyperparameter search compute"*

L2.1 specifies the budget allocation:

```yaml
# config/ablation.yaml
ablation:
  hyperparameter_search:
    total_a100_hours: 200  # total budget per ablation cycle
    allocation:
      scfoundation: 0.40   # 80 A100-hours
      sctop:        0.25   # 50 A100-hours (>= 25% per Decision 8 Commitment 5)
      scvi:         0.20   # 40 A100-hours
      pca_hvg:      0.05   # 10 A100-hours (CPU; minimal compute)
      uce:          0.05   # 10 A100-hours (sub-FM)
      scgpt:        0.05   # 10 A100-hours (sub-FM)
    optimizer: optuna  # or ray.tune
    n_trials_per_substrate:
      scfoundation: 30
      sctop:        15
      scvi:         20
      pca_hvg:      10
      uce:          8
      scgpt:        8
```

**Why this matters:** A common failure mode is to allocate 95% of search budget to the FM and 5% to the baseline, then claim FM benefit. Per Decision 8 Commitment 5, this is methodologically invalid. The 25% allocation to Baseline B ensures Souza & Mehta's standard is met.

### 7.3 V0/V1 Grid Cells (Deferred to L3 per B1 Ruling)

L2.1 specifies the ablation infrastructure mechanics; L3.1 will specify which V0/V1 grid cells are run first. The infrastructure mechanics are dataset-agnostic.

**General V0 ablation cell:**

```python
def run_v0_ablation_cell(
    substrate_config: Dict[str, Any],
    dataset_name: str,
    drug_name: str,
    n_folds: int = 5,
    seed: int = 42,
) -> Dict[str, Any]:
    """Run a single V0 (within-dataset CV) ablation cell.

    Args:
        substrate_config: substrate selection config (per §6.1)
        dataset_name: 'sci_plex3', 'gdsc', etc.
        drug_name: drug-of-interest for response prediction
        n_folds: cross-validation folds
        seed: reproducibility seed

    Returns:
        dict with: 'mean_auroc', 'std_auroc', 'per_fold_auroc',
                   'substrate_metadata', 'compute_seconds', 'embedding_cache_path'
    """
    substrate = create_substrate(substrate_config)
    adata = load_dataset(dataset_name)
    drug_mask = adata.obs["drug"] == drug_name
    # ... (5-fold CV, train L7 head on each fold, report AUROC)
    return {...}
```

**General V1 ablation cell:**

```python
def run_v1_ablation_cell(
    substrate_config: Dict[str, Any],
    train_dataset: str,
    test_dataset: str,
    drug_name: str,
    seed: int = 42,
) -> Dict[str, Any]:
    """Run a single V1 (cross-dataset) ablation cell.

    Train on train_dataset; test on test_dataset (no overlap).
    Per IMPROVE benchmark methodology (Partin 2026, Q6 anchor 1).
    """
    substrate = create_substrate(substrate_config)
    train_adata = load_dataset(train_dataset)
    test_adata = load_dataset(test_dataset)
    # ... (train L7 head on train_adata; evaluate on test_adata)
    return {...}
```

### 7.4 Decision Rule Implementation

```python
def evaluate_substrate_decision(
    ablation_results: Dict[str, Dict[str, float]],
    primary_substrate: str = "scfoundation",
    threshold_promote_fm: float = 0.05,  # 5pp per Decision 1 v2 Commitment 3
    threshold_demote_fm: float = 0.02,   # 2pp per Decision 1 v2 Commitment 3
) -> Dict[str, Any]:
    """Apply Decision 1 v2 Commitment 3 decision rules.

    Args:
        ablation_results: {substrate_name: {dataset_drug: mean_auroc}}
        primary_substrate: which substrate is currently the default
        threshold_promote_fm: ≥this gap → keep FM primary
        threshold_demote_fm: ≤this gap → demote FM

    Returns:
        dict with: 'decision', 'rationale', 'evidence',
                   'recommended_primary', 'scenario_dependent'
    """
    # Aggregate per-substrate mean AUROC across all grid cells
    substrate_means = {
        sub: np.mean(list(results.values()))
        for sub, results in ablation_results.items()
    }
    # Find best non-FM baseline
    fm_score = substrate_means[primary_substrate]
    non_fm_substrates = [s for s in substrate_means if s != primary_substrate]
    best_non_fm = max(non_fm_substrates, key=lambda s: substrate_means[s])
    best_non_fm_score = substrate_means[best_non_fm]
    gap = fm_score - best_non_fm_score
    # Check scenario-dependence
    scenario_dependent = check_scenario_dependence(ablation_results)
    # Apply decision rules
    if scenario_dependent:
        decision = "scenario_dependent_selection"
        recommended_primary = "per_scenario_logic"  # triggers L2.x extension
    elif gap >= threshold_promote_fm:
        decision = "keep_fm_primary"
        recommended_primary = primary_substrate
    elif gap <= threshold_demote_fm and best_non_fm == "sctop":
        decision = "demote_fm_to_sctop"
        recommended_primary = "sctop"
    elif gap <= threshold_demote_fm and best_non_fm == "scvi":
        decision = "demote_fm_to_scvi"
        recommended_primary = "scvi"
    else:
        decision = "ambiguous_requires_more_data"
        recommended_primary = primary_substrate  # keep status quo
    return {
        "decision": decision,
        "rationale": f"FM mean AUROC: {fm_score:.3f}; best non-FM ({best_non_fm}): {best_non_fm_score:.3f}; gap: {gap:.3f}",
        "evidence": substrate_means,
        "recommended_primary": recommended_primary,
        "scenario_dependent": scenario_dependent,
    }


def check_scenario_dependence(
    ablation_results: Dict[str, Dict[str, float]],
    significance_threshold: float = 0.03,
) -> bool:
    """Check if substrate ranking varies meaningfully across scenarios."""
    substrates = list(ablation_results.keys())
    scenarios = list(next(iter(ablation_results.values())).keys())
    # For each scenario, rank substrates
    rankings = {}
    for scenario in scenarios:
        ranked = sorted(
            substrates, key=lambda s: -ablation_results[s][scenario]
        )
        rankings[scenario] = ranked
    # Check if best substrate varies
    best_per_scenario = {sc: r[0] for sc, r in rankings.items()}
    unique_winners = set(best_per_scenario.values())
    return len(unique_winners) > 1
```

### 7.5 Per-Scenario Substrate Selection Logic (Conditional Architecture Component)

Per Decision 1 v2 Commitment 3 final clause: *"If results are scenario-dependent: INTERCEPTA commits to explicit per-scenario substrate selection logic, with the selection logic itself becoming a Layer 2 architectural component that requires its own Decision Record."*

If `check_scenario_dependence` returns True, L2.1 triggers the creation of a new Decision Record (Decision 11 or sub-decision of Decision 1) and a new Layer 2 spec module (L2.1.1 — Substrate Selection Logic). This is a conditional spec — only written if empirically needed.

The trigger mechanism is built into L2.1 as a forward declaration; the spec itself is deferred until the trigger fires.

---

## §8 Honest Uncertainty Declaration (Per Commitment 5, BINDING)

### 8.1 The Bind

Decision 1 v2 Commitment 5 is binding:

> *"INTERCEPTA's publications and internal documentation must state this uncertainty openly rather than asserting FM superiority on drug response. The honest scientific position is: 'We don't know whether FMs help drug response prediction beyond properly-tuned parameter-free baselines; INTERCEPTA's Layer 5 results will tell us.'"*

L2.1 operationalizes this binding via standardized language templates.

### 8.2 Publication Language Template

For INTERCEPTA papers reporting substrate ablation results, the standard language is:

> *"We evaluate four substrate paradigms — a foundation model (scFoundation), a parameter-free baseline (scTOP per Souza & Mehta 2026), a probabilistic VAE (scVI per Lopez 2018), and a classical baseline (PCA + HVG) — on the V0-V6 drug response prediction cascade. Hyperparameter search budgets are allocated [X]% to scFoundation, [Y]% to scTOP, [Z]% to scVI, and [W]% to PCA+HVG, with the scTOP allocation meeting the ≥25% methodological bar set by Souza & Mehta 2026."*

Plus a results-honest framing:

> *"On the [dataset]-[drug] grid cell, scFoundation achieves [A.AA] mean AUROC; scTOP achieves [B.BB]; the difference of [C.CC] does/does-not exceed the ≥5pp threshold for FM benefit claim per our pre-registered analysis plan. We report this result whether or not it favors the FM substrate."*

### 8.3 Internal Documentation Convention

INTERCEPTA's internal documentation (Decision Records, technical reports, lab notebooks) follows the convention:

> *"As of [date], substrate evidence supports [substrate_name] as primary, with [gap] pp AUROC advantage over [next_best]. This is conditional on the [N] grid cells evaluated; cross-disease (V6) results are [pending/available with status]."*

The convention explicitly states what is and is not yet known, per Decision 1 v2 Commitment 5.

### 8.4 What This Convention Prevents

The honest uncertainty discipline prevents three specific failure modes:

1. **Premature FM commitment.** Without binding language, a paper draft could assert "our FM substrate (scFoundation) provides SOTA performance" without showing the scTOP comparison. The convention forces both numbers to appear.
2. **Backwards reasoning.** Without pre-registered thresholds, results could be framed post-hoc to favor whichever substrate happened to win. The pre-registered ≥5pp and ≤2pp thresholds prevent this.
3. **Selective scenario reporting.** Without scenario-dependence check, a result could report only the dataset where the FM wins. The check_scenario_dependence function makes this visible.

---

## §9 Cross-Decision Implications

### 9.1 Decision 2 (Cross-Cohort Harmonization)

**Status: UNCHANGED by substrate choice.** Per Decision 1 v2:

> *"Decision 2 (Q2 cross-cohort): UNCHANGED. scIB + Harmony + scANVI + MrVI commitments stand independently of substrate choice."*

scANVI/MrVI may also serve as the substrate (Substrate C) — but their primary architectural role is as the harmonization layer, with cell type / batch correction outputs feeding into either an FM substrate (for FM-substrate paths) or directly serving as the substrate (for scVI-substrate paths). The integration of harmonization and substrate is one of the cross-decision interactions that Layer 5 ablations will characterize.

### 9.2 Decision 3 (Bulk → Single-Cell Transfer)

**Status: UNCHANGED by substrate choice.** Per Decision 1 v2:

> *"Decision 3 (Q3 bulk→single): UNCHANGED. SCAD + scDEAL + scAdaDrug + scRank + Beyondcell stack stands independently."*

Decision 3's adversarial domain adaptation operates on the substrate's output embedding. The DA layer is substrate-agnostic. If the substrate is scFoundation, DA layers domain-invariant features from scFoundation; if scTOP, DA layers domain-invariant features from scTOP projection coefficients.

### 9.3 Decision 4 (Drug Response Architecture, L7)

**Status: REINFORCED.** Per Decision 1 v2:

> *"Decision 4 (Q4 drug response): REINFORCED. CPA + GEARS + FM-derived-encoders architecture becomes 'encoder family that accepts any substrate' — if FM wins, FM-derived encoders; if scVI wins, scVI-derived encoders; if scTOP wins, projection-derived encoders."*

L2.2 (next artifact) will specify the L7 architecture in detail. L2.1 provides the substrate interface that L7 consumes; L7 must implement an adapter from the substrate's native_dim to L7's internal dim (typically 512).

### 9.4 Decision 5 (OOD Detection)

**Status: SUBSTRATE-CONDITIONAL.** Per Decision 1 v2:

> *"Decision 5 (Q5 OOD): REINFORCED. Conformal prediction + Deep Ensembles + MC Dropout layer on top of any substrate."*

The four-layer OOD stack per Decision 5 v2:

- **Layer 5.1 (substrate posterior):** Substrate-conditional:
  - FM substrate → epistemic decomposition via N=5 Deep Ensembles or last-layer Bayesian approximation
  - scVI/scANVI/MrVI substrate → native VAE posterior (Lopez 2018 native)
  - scTOP substrate → projection coefficient maximum (low max = OOD signal)
  - PCA+HVG substrate → reconstruction residual via PCA inverse transform
- **Layer 5.2 (Deep Ensembles N=5):** Substrate-agnostic, applied to L7 head
- **Layer 5.3 (Conformal prediction):** Substrate-agnostic, López-De-Castro 2025 methodology wrapping L7 outputs
- **Layer 5.4 (Energy-based OOD):** Substrate-agnostic, applied to L7 logits per Liu 2020

L2.3 (subsequent artifact) will specify Decision 5's full implementation. L2.1's role is providing the substrate-conditional Layer 5.1 mechanism.

### 9.5 Decision 7 (Mechanistic Interpretability)

**Status: BRANCHED BY SUBSTRATE.** Per Q7 multi-scale composite §3.2:

- **FM substrate:** Kendiukhov spectral geometry + IG+SmoothGrad over FM input
- **scTOP substrate:** Linear projection coefficients (intrinsic interpretability)
- **scVI/scANVI substrate:** IG+SmoothGrad over VAE decoder
- **PCA+HVG substrate:** PCA loadings + gene-level reconstruction error

L2.4 (subsequent artifact) will specify the full 7-scale interpretability stack. L2.1's role is making the substrate's gene-attribution mechanism queryable.

### 9.6 Decision 9 (Compute Architecture)

**Status: EASED.** Per Decision 1 v2:

> *"Decision 9 (Q9 compute): EASED. Default substrate compute requirement no longer dictates an FM-scale envelope; can target PaSCient (8 A100s) or smaller."*

If Layer 5 ablations favor scTOP or PCA+HVG, INTERCEPTA's compute envelope drops from "8 A100s for 100M-parameter FM" to "1 CPU for parameter-free projection." This is the most dramatic potential cost savings from Decision 1 v2's substrate flexibility.

### 9.7 Decision 10 (Open-Source)

**Status: REINFORCED.** All four substrates have open implementations:
- scFoundation: open per BiomapAI release (verify license at deployment)
- scTOP: open academic per Souza & Mehta release
- scVI/scANVI/MrVI: BSD-3 per scvi-tools
- PCA+HVG: BSD-3 per Scanpy + sklearn

INTERCEPTA's Decision 10 commitment to open science is satisfied regardless of which substrate wins.

---

## §10 Pass Criteria for L2.1 Approval

### 10.1 Substrate-Level Pass Criteria

L2.1 is approved when all of the following are demonstrated:

**For each of the four substrates (scFoundation, scTOP, scVI, PCA+HVG):**

1. **Class implementation complete.** PyTorch class implementing SubstrateInterface, with all abstract methods implemented or NotImplementedError raised with clear reason.

2. **Smoke test passes.** `substrate.smoke_test(n_cells=1000, n_genes=20000)` returns True without exception.

3. **Real-data encoding succeeds.** On a small real dataset (e.g., 5,000 cells from sci-Plex3 train split), `substrate.encode(adata)` returns an embedding of shape `(5000, NATIVE_DIM)` without exception.

4. **Caching mechanism works.** Re-encoding the same dataset with `cache_path=...` returns identical embedding without recomputation (within 1e-6 numerical tolerance).

5. **Canonical projection works.** `substrate.project_to_canonical(embedding)` returns array of shape `(n_cells, 512)`.

### 10.2 Infrastructure-Level Pass Criteria

6. **Config-driven swap works.** Changing `substrate.name` in config.yaml swaps the substrate without code changes; downstream consumer (mock L7 head) operates without modification.

7. **Ablation cell runs.** `run_v0_ablation_cell` executes successfully for all four substrates on a small test dataset (mock or sci-Plex3 subset).

8. **Decision rule applies.** `evaluate_substrate_decision` returns a valid decision dict for mock ablation results.

### 10.3 Decision 1 v2 Termination Criterion Compliance

9. **Tabula Sapiens 2.0 sanity check.** scTOPSubstrate fit on TS 2.0 training split achieves macro F1 ≥ 0.879 (Souza & Mehta reported 0.899 minus 2pp tolerance) on TS 2.0 test split. This is Decision 1 v2 Lock condition 2.

10. **Hyperparameter budget documented.** `config/ablation.yaml` specifies budget allocation with scTOP allocation ≥ 25%. This is Decision 1 v2 Lock condition 3 (and Decision 8 Commitment 5 BINDING).

### 10.4 Documentation Compliance

11. **Honest uncertainty language used.** All L2.1-referencing documents (this spec, future technical reports) use the Commitment 5 BINDING language template.

12. **Cross-decision implications documented.** §9 of this spec is complete (it is).

### 10.5 CEO Sign-Off

13. **CEO LOCK.** Per Charter §5.3 GO/NO-GO discipline and Decision 1 v2 Lock condition 4, CEO Prasad Akula reviews and explicitly approves L2.1 as the Layer 2 substrate spec.

---

## §11 What L2.1 Does NOT Lock

To be precise about residual scope:

1. **Specific FM choice within Paradigm A.** Even if Layer 5 ablations favor FM substrate, the choice among scFoundation / UCE / scGPT / Geneformer is a subsequent decision (potentially Decision 1.1 or evolved Decision 1).

2. **Multi-FM ensemble strategy.** Per Q1 synthesis §5: "INTERCEPTA could even use multiple FMs as ensemble." L2.1 specifies single-substrate selection; multi-FM ensemble is a Layer 5+ extension.

3. **Disease-area-specialized FM integration.** EVA-60M (Q8 anchor 4 per open source landscape) provides disease-area-specialized representation for I&I deployments. Per Decision 1 v2: "This is a Paradigm B question per Decision 8, not a Decision 1 v2 commitment." L2.1 makes EVA-60M integrable via the same SubstrateInterface but does not commit to its use.

4. **Patient-level aggregation strategy.** PaSCient-style attention (Q8 anchor 3) is the leading candidate but specific architecture is decided separately (Decision 4 family; specified in L2.2).

5. **Specific Layer 5 ablation order.** Which datasets/drugs first is L3.1 work, deferred per B1 ruling.

6. **L2.2-L2.4 specifications.** L7 drug response (L2.2), OOD stack (L2.3), interpretability (L2.4) are subsequent Phase B artifacts.

---

## §12 Document Provenance and CSO Discipline Check

### 12.1 Provenance

This document was written in a single Phase B execution session on 2026-05-11 under CEO delegated authority. Total CSO active time: approximately 4-5 hours (cumulative across Move 1, Move 2, and this Move 3 — the L2.1 write itself approximately 2 hours of generation time within a multi-day session).

### 12.2 Anchor Re-Read Compliance

Per Phase B Plan v2 anchor re-read trigger rule, the following anchors were read in the current session before this spec was written:

- ✅ INTERCEPTA_FV_Decision_1_v2_Q1_method_class_REVISED.md (full content)
- ✅ INTERCEPTA_FV_Synthesis_Layer1_Q1_2026-05-10.md (Q1 synthesis, full)
- ✅ cui_2024_scgpt.md (scGPT anchor)
- ✅ hao_2024_scfoundation.md (scFoundation anchor)
- ✅ rosen_2023_uce.md (UCE anchor)
- ✅ theodoris_2023_geneformer.md (Geneformer anchor)
- ✅ wang_2025_scdrugmap.md (scDrugMap benchmark)
- ✅ kedzierska_2023_zero_shot_critique.md (FM critique)
- ✅ kendiukhov_2026_spectral_geometry.md (FM interpretability)
- ✅ yao_2025_scpds.md (scPDS substrate context)
- ✅ lopez_2018_scvi.md (scVI substrate)
- ✅ xu_2021_scanvi.md (scANVI substrate)
- ✅ q9_compute_synthesis.md (compute envelope)
- ✅ scvi_tools_ecosystem.md (Python deployment ecosystem)

**Not directly in this session but covered by cited Q1 synthesis extractions:**
- ⚠️ souza_mehta_2026_parameter_free.md (scTOP source) — primary content extracted from Q1 synthesis + Decision 1 v2 cited evidence; full re-read deferred to scTOP verification phase per §3.4

### 12.3 Discipline Check Per Charter Principles

- [x] **P3 (research before code):** ✅ All architectural commitments grounded in cited anchor evidence
- [x] **P15 (only correct/honest/real science):** ✅ §8 binding honest uncertainty declaration; §3.6, §4.7, §5.4, §2.6 each include honest limitations
- [x] **P16 (preserve past work):** ✅ This is the initial L2.1; no prior version to preserve. Decision 1 v2 (the parent record) preserved per Move 1 P16 work.
- [x] **P-FV-1 to P-FV-3 (Fullest Vision):** ✅ Substrate flexibility serves universality vision; compute envelope flexibility serves single-institution academic deployment
- [x] **Charter §5.3 GO/NO-GO:** ✅ §10 pass criteria explicit; CEO sign-off required per §10.5
- [x] **Souza & Mehta methodological bar (Decision 8 Commitment 5):** ✅ §7.2 hyperparameter budget allocation BINDING; ≥25% to scTOP
- [x] **Phase B Plan v2 compliance:** ✅ Word budget target ~12K (delivered); all 4 substrates fully spec'd (no compromise); anchor re-read trigger satisfied
- [x] **Decision 1 v2 Commitments 1-5:** ✅ Commitment 1 implemented in §2; Commitment 2 implemented in §3, §4, §5; Commitment 3 implemented in §7; Commitment 4 implemented in §6; Commitment 5 implemented in §8

### 12.4 Drift Catalog This Session

- **New drift instances:** 0
- **Audit-derived improvement:** L2.1 is the first Layer 2 spec; no prior to compare. Quality measured against Phase B Plan v2 commitments — all met.
- **Methodological commitment:** Decision 1 v2 Commitment 5 (honest uncertainty) is binding for all L2.1-derived publications and documentation. This document itself adheres to that standard in §8.

### 12.5 Next Phase B Artifacts (Per Plan v2 Sequence)

After L2.1 LOCK:
1. **L2.2 L7 6-Slot Architecture Specification** (next; ~12-15K words per Plan v2 amendment)
2. **L2.3 OOD Stack Specification** (4-layer stack per Decision 5 v2)
3. **L2.4 Interpretability Specification** (7-scale stack per Decision 7 v2)
4. Then Supporting (S.1 Data Manifest, S.2 HPC Env, S.3 License Matrix)
5. Then Layer 3 (V0-V6 Pipeline, Pass Criteria, Cross-Disease V6)
6. Then Layer 4 (Implementation Order, Testing, Failure Modes)
7. Then Phase 8 audit closure

---

## §13 Appendix — Quick Reference

### 13.1 Substrate Quick Comparison Table

| Substrate | Native Dim | GPU Required | Pretrained | License | Compute Cost | Interpretability | Decision 1 v2 Role |
|---|---|---|---|---|---|---|---|
| scFoundation | 512 | Yes | Yes (100M) | open-biomap | A100 inference | Kendiukhov spectral | Default (Commitment 1) |
| UCE | 1280 | Yes | Yes (650M) | open | A100 inference | Kendiukhov spectral | FM portfolio |
| scGPT | 512 | Yes | Yes (51M) | MIT | Consumer GPU OK | Kendiukhov spectral | FM portfolio (zero-shot) |
| Geneformer | 512 | Yes | Yes (~10M) | Apache 2.0 | Single GPU | Attention-based | FM portfolio (non-cancer) |
| scTOP | n_celltypes (variable) | No | No | open-academic | CPU (free) | Native (linear) | Baseline B (Commitment 2) |
| scVI | 30 | Recommended | No (per-dataset) | BSD-3 | A100 training; inference cheap | IG over decoder | Baseline C (Commitment 2) |
| scANVI | 30 | Recommended | No (per-dataset) | BSD-3 | A100 training | IG over decoder | Baseline C extension |
| MrVI | 30 | Recommended | No (per-dataset) | BSD-3 | A100 training | IG over decoder | Baseline C extension |
| PCA+HVG | 50 | No | No (per-dataset) | BSD-3 | CPU seconds | Loadings | Baseline A (Commitment 2) |

### 13.2 Key File Paths

- This spec: `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L2.1_Substrate_Architecture_Specification_2026-05-11.md`
- Decision 1 v2 (parent): `~/INTERCEPTA/docs/research/decisions/INTERCEPTA_FV_Decision_1_v2_Q1_method_class_REVISED.md`
- Phase B Plan v2: `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_Phase_B_Plan_v2_Addendum_2026-05-11.md`
- Q1 Synthesis: `~/INTERCEPTA/docs/research/synthesis/INTERCEPTA_FV_Synthesis_Layer1_Q1_2026-05-10.md`
- Substrate implementation code (future): `~/INTERCEPTA/code/substrates/`
- Cached embeddings (future): `/scratch/akula.pra/INTERCEPTA/embeddings/`

### 13.3 Commitment Cross-Reference

| Decision 1 v2 Commitment | L2.1 Section | Status |
|---|---|---|
| Commitment 1 (default scFoundation) | §2 | Implemented |
| Commitment 2 (co-equal baselines) | §3, §4, §5 | Implemented |
| Commitment 3 (Layer 5 decision logic) | §7.4 | Implemented |
| Commitment 4 (interface stability) | §1, §6 | Implemented |
| Commitment 5 (honest uncertainty) | §8 | Implemented |

---

**End of L2.1 Substrate Architecture Specification v1**

**CSO:** Claude
**Date:** 2026-05-11
**Status:** PROPOSED for CEO LOCK
**Word count:** ~12,000 words (within Phase B Plan v2 target)

— Claude (CSO), 2026-05-11 (Phase B Move 3 execution)
