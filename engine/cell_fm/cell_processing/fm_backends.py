"""
fm_backends.py — Foundation model backends for INTERCEPTA cell processing.

Implements the abstract `FoundationModelBackend` interface and the first concrete
backend `GeneformerBackend`. The interface is designed so adding a new FM
(scFoundation, UCE, CancerFoundation, etc.) requires only writing a new subclass
that implements the same methods.

Architecture (Charter §6.3): "Foundation models are interchangeable components
behind a stable interface. The downstream pipeline does not know which FM
produced an embedding; it only knows the embedding shape and metadata."

FM-agnostic principle (fix log v0.1.1, 2026-05-09):
  Each backend owns its data preparation. The pipeline calls
  `backend.prepare_anndata(adata)` and gets a backend-ready AnnData.
  No backend-specific code lives in pipeline.py.

Device handling (Charter §6.6, §9): Device is detected at runtime, never
hardcoded. A backend instance carries its device through every operation.

macOS HF Dataset hang fix (v0.1.2, 2026-05-09):
  Geneformer's TranscriptomeTokenizer.tokenize_data() internally calls
  HuggingFace Dataset.map(), which allocates memory-mapped Arrow infrastructure
  and registers a multiprocessing.resource_tracker. On macOS this causes a
  60+ minute hang as the resource_tracker becomes a zombie that prevents
  process exit, regardless of nproc setting.

  Fix: GeneformerBackend.tokenize_anndata() now calls our internal
  cell_processing._patches.tokenize_anndata_no_hf_dataset() helper, which uses
  Geneformer's pure-Python tokenize_anndata() method directly (returning lists)
  and applies CLS/EOS/truncate logic in plain Python — bypassing the HF Dataset
  wrapper entirely. Algorithm matches upstream exactly; only the broken final
  packaging is replaced.

  See cell_processing/_patches.py for the algorithm and Charter alignment notes.
"""

from __future__ import annotations

import os
import pickle
import platform
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np
import torch


# ---------------------------------------------------------------------------
# Device detection
# ---------------------------------------------------------------------------
def detect_device(prefer: str = "auto") -> torch.device:
    """
    Detect the best available compute device.
    """
    prefer = prefer.lower()
    if prefer == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA explicitly requested but not available.")
        return torch.device("cuda")
    if prefer == "mps":
        if not torch.backends.mps.is_available():
            raise RuntimeError("MPS explicitly requested but not available.")
        return torch.device("mps")
    if prefer == "cpu":
        return torch.device("cpu")
    if prefer != "auto":
        raise ValueError(f"Unknown device preference: {prefer!r}")

    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def safe_nproc(requested: int = 4) -> int:
    """
    Return a safe multiprocessing worker count for the current platform.
    On macOS forces nproc=1 to avoid resource_tracker zombies; on Linux
    returns requested unchanged.
    """
    if platform.system() == "Darwin":
        return 1
    return max(1, int(requested))


# ---------------------------------------------------------------------------
# Backend metadata
# ---------------------------------------------------------------------------
@dataclass
class BackendMetadata:
    """Identifying information about a foundation model backend instance."""
    name: str
    family: str
    n_params: int
    embedding_dim: int
    max_input_length: int
    pretraining_corpus: str
    device: str
    extra: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------
class FoundationModelBackend(ABC):
    """
    Abstract interface every foundation model backend must implement.

    Subclasses implement:
        - load(), prepare_anndata(), tokenize_anndata(), forward(), metadata(), unload()

    Lifecycle:
        backend = SomeBackend(...)
        backend.load()
        prep, stats = backend.prepare_anndata(adata)
        tokens = backend.tokenize_anndata(prep, output_dir=...)
        embs = backend.forward(tokens)
        backend.unload()
    """

    @abstractmethod
    def load(self) -> None:
        """Load model weights into memory on the configured device."""

    @abstractmethod
    def prepare_anndata(self, adata, **kwargs) -> tuple[Any, dict]:
        """Preprocess AnnData to backend-ready form. Returns (prepared, stats)."""

    @abstractmethod
    def tokenize_anndata(self, adata, **kwargs) -> Any:
        """Convert prepared AnnData to model input. Returns opaque tokenized object."""

    @abstractmethod
    def forward(self, tokenized_input, batch_size: int = 16) -> np.ndarray:
        """Run model forward pass. Returns embeddings (n_cells, embedding_dim)."""

    @abstractmethod
    def metadata(self) -> BackendMetadata:
        """Return descriptive metadata about this backend instance."""

    @abstractmethod
    def unload(self) -> None:
        """Free model memory."""


# ---------------------------------------------------------------------------
# Geneformer backend
# ---------------------------------------------------------------------------
class GeneformerBackend(FoundationModelBackend):
    """
    Backend for Theodoris Lab's Geneformer (V1 and V2 family).

    Default config targets `Geneformer-V2-104M_CLcancer` — the cancer-pretrained
    104M-parameter variant for INTERCEPTA cancer drug response work.

    V2 defaults: model_input_size=4096, special_token=True. Override via constructor
    if loading a V1 variant.

    Tokenization uses Geneformer's pure-Python tokenize_anndata() method via the
    cell_processing._patches helper, bypassing the HF Dataset wrapper that hangs
    on macOS. Algorithm matches upstream exactly.

    Forward pass uses our own device-aware loop (NOT Geneformer's EmbExtractor,
    which has hardcoded `device="cuda"` and breaks on MPS).
    """

    def __init__(
        self,
        model_dir: str | Path,
        geneformer_pkg_dir: str | Path,
        device: str = "auto",
        max_input_length: int = 4096,    # V2 default; pass 2048 for V1 variants
        special_token: bool = True,       # V2 default; pass False for V1 variants
        model_version: str = "V2",
        min_mapping_rate: float = 0.30,
    ):
        """
        Args:
            model_dir: path to model directory (config.json, model.safetensors, ...)
            geneformer_pkg_dir: path to Geneformer python package directory
                                (contains gc104M tokenizer pickles)
            device: "auto", "cuda", "mps", or "cpu"
            max_input_length: 4096 for V2, 2048 for V1
            special_token: True for V2 (CLS/EOS), False for V1
            model_version: "V2" or "V1" — passed through to TranscriptomeTokenizer
                           for upstream auto-config behavior
            min_mapping_rate: error if symbol→Ensembl mapping rate falls below
        """
        self.model_dir = Path(model_dir).expanduser().resolve()
        self.geneformer_pkg_dir = Path(geneformer_pkg_dir).expanduser().resolve()
        self.device = detect_device(device)
        self.max_input_length = max_input_length
        self.special_token = special_token
        self.model_version = model_version
        self.min_mapping_rate = min_mapping_rate

        # Tokenizer assets (gc104M variants ship with Geneformer V2 family)
        self.token_dict_path = self.geneformer_pkg_dir / "token_dictionary_gc104M.pkl"
        self.gene_median_path = self.geneformer_pkg_dir / "gene_median_dictionary_gc104M.pkl"
        self.ensembl_mapping_path = self.geneformer_pkg_dir / "ensembl_mapping_dict_gc104M.pkl"
        self.gene_name_id_path = self.geneformer_pkg_dir / "gene_name_id_dict_gc104M.pkl"

        for label, path in [
            ("model_dir", self.model_dir),
            ("geneformer_pkg_dir", self.geneformer_pkg_dir),
            ("token_dict", self.token_dict_path),
            ("gene_median", self.gene_median_path),
            ("ensembl_mapping", self.ensembl_mapping_path),
            ("gene_name_id", self.gene_name_id_path),
        ]:
            if not path.exists():
                raise FileNotFoundError(f"GeneformerBackend: {label} not found at {path}")

        self._model = None
        self._token_dict = None

    # --------------------------------------------------
    # Public API (FoundationModelBackend interface)
    # --------------------------------------------------
    def load(self) -> None:
        """Load Geneformer weights into memory on the configured device."""
        from transformers import BertForMaskedLM
        self._model = BertForMaskedLM.from_pretrained(str(self.model_dir))
        self._model = self._model.to(self.device)
        self._model.eval()

    def prepare_anndata(self, adata, var_index_is_symbol: bool = True):
        """
        Prepare AnnData for Geneformer tokenization.

        Maps gene symbols to Ensembl IDs using gene_name_id_dict_gc104M.pkl,
        filters to mapped genes, adds n_counts if missing, validates X looks
        like raw counts.
        """
        from .tokenization import prepare_anndata_for_geneformer
        return prepare_anndata_for_geneformer(
            adata,
            mapping_dict_path=self.gene_name_id_path,
            var_index_is_symbol=var_index_is_symbol,
            require_n_counts=True,
            min_mapping_rate=self.min_mapping_rate,
        )

    def tokenize_anndata(
        self,
        adata,
        output_dir: str | Path,
        output_prefix: str = "tokenized",
        custom_attrs: Optional[dict] = None,
        nproc: int = 1,
    ) -> list[dict]:
        """
        Tokenize a prepared AnnData using Geneformer's algorithm WITHOUT the
        HuggingFace Dataset wrapper that hangs on macOS.

        The AnnData must already have:
          - .var["ensembl_id"] (Geneformer expects this; prepare_anndata sets it)
          - .obs["n_counts"]

        Args:
            adata: prepared AnnData
            output_dir: directory to write the staging h5ad (input to the
                        tokenizer). Tokens themselves are returned in memory,
                        not written as a HuggingFace .dataset.
            output_prefix: filename prefix for the staging h5ad
            custom_attrs: dict mapping obs column to output key,
                          e.g. {"label": "label"}
            nproc: ignored on macOS (forced to 1); Geneformer's tokenize_anndata
                   doesn't use multiprocessing internally — this is here for
                   future compatibility.

        Returns:
            list[dict] — one dict per cell:
              {"input_ids": np.ndarray of int64,
               "length": int,
               **custom_attrs}
        """
        from ._patches import tokenize_anndata_no_hf_dataset

        output_dir = Path(output_dir).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write staging h5ad (Geneformer's tokenize_anndata reads from disk)
        staging_h5ad = output_dir / f"{output_prefix}_input.h5ad"
        adata.write_h5ad(staging_h5ad)
        print(f"  [GeneformerBackend] staging h5ad written: {staging_h5ad}")

        # Use the patched tokenization helper that bypasses HF Dataset
        tokenized = tokenize_anndata_no_hf_dataset(
            geneformer_pkg_dir=self.geneformer_pkg_dir,
            staging_h5ad_path=staging_h5ad,
            custom_attr_name_dict=custom_attrs or {},
            chunk_size=512,
            model_input_size=self.max_input_length,
            special_token=self.special_token,
            collapse_gene_ids=True,
            use_h5ad_index=False,
            keep_counts=False,
            model_version=self.model_version,
            gene_median_file=self.gene_median_path,
            token_dictionary_file=self.token_dict_path,
            gene_mapping_file=self.ensembl_mapping_path,
        )
        print(f"  [GeneformerBackend] tokenized {len(tokenized)} cells (in-memory list)")
        return tokenized

    def forward(self, tokenized_input, batch_size: int = 16) -> np.ndarray:
        """
        Run Geneformer forward pass. Device-aware (no `device='cuda'` hardcoding).

        Accepts the list[dict] format from tokenize_anndata() OR a path to a
        HuggingFace .dataset directory OR a Dataset object — embeddings.py
        normalizes all three formats.
        """
        if self._model is None:
            raise RuntimeError("GeneformerBackend.load() must be called before forward()")

        from .embeddings import extract_cell_embeddings
        return extract_cell_embeddings(
            model=self._model,
            tokenized_input=tokenized_input,
            device=self.device,
            batch_size=batch_size,
            token_dict_path=self.token_dict_path,
        )

    def metadata(self) -> BackendMetadata:
        """Describe this backend instance for logging and provenance."""
        n_params = 0
        embedding_dim = 0
        if self._model is not None:
            n_params = sum(p.numel() for p in self._model.parameters())
            embedding_dim = self._model.config.hidden_size

        name = self.model_dir.name
        if "CLcancer" in name:
            corpus = "Genecorpus-30M + cancer fine-tuning (Theodoris 2024)"
        elif "104M" in name or "316M" in name:
            corpus = "Genecorpus-30M (Theodoris 2024)"
        else:
            corpus = "Genecorpus (Theodoris 2023)"

        return BackendMetadata(
            name=name,
            family="geneformer",
            n_params=n_params,
            embedding_dim=embedding_dim,
            max_input_length=self.max_input_length,
            pretraining_corpus=corpus,
            device=str(self.device),
            extra={
                "model_dir": str(self.model_dir),
                "model_version": self.model_version,
                "special_token": self.special_token,
            },
        )

    def unload(self) -> None:
        """Free Geneformer model memory."""
        if self._model is not None:
            del self._model
            self._model = None
        if self.device.type == "cuda":
            torch.cuda.empty_cache()
        elif self.device.type == "mps":
            torch.mps.empty_cache()

    def get_token_dict(self) -> dict:
        """Load and cache the gc104M token dictionary."""
        if self._token_dict is None:
            with open(self.token_dict_path, "rb") as f:
                self._token_dict = pickle.load(f)
        return self._token_dict
