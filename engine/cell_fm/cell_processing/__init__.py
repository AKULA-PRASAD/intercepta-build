"""
INTERCEPTA cell_processing — Layer 2A foundation model adaptation for single-cell data.

This package implements the cell-level component of MC-FMA (Mechanism-Constrained
Foundation Model Adaptation), per Charter v2.0 Chapter 6 (architecture) and
Chapter 13 (M1 milestone).

Architecture (Charter §6.3, §6.4):
    1. Foundation models produce cell-level embeddings (this layer).
    2. Embeddings are adapted via mechanism-constrained fine-tuning (M1 core).
    3. Adapted embeddings feed mechanism inference, drug response prediction,
       and uncertainty quantification.
    4. Multiple FMs run in ensemble; disagreement informs MFMD uncertainty.

Public API:
    from cell_processing import (
        FoundationModelBackend,
        GeneformerBackend,
        run_pipeline,
        compute_mechanism_axes,
        compute_ensemble_uncertainty,
    )

Design principles (Charter §6.6, §9):
    - Device-agnostic (CUDA / MPS / CPU detected at runtime; never hardcoded)
    - FM-agnostic (adding scFoundation, UCE, or new FMs is one backend file;
      pipeline.py never reaches into backend internals)
    - Honest about failure modes (each function documents what it cannot do)
    - Reproducible (random seeds, version pins, deterministic where possible)
    - Platform-aware (multiprocessing forced to nproc=1 on macOS to avoid
      resource_tracker hang; full nproc on Linux)
"""

from .fm_backends import (
    FoundationModelBackend,
    GeneformerBackend,
    BackendMetadata,
    detect_device,
    safe_nproc,
)
from .tokenization import (
    map_symbols_to_ensembl,
    prepare_anndata_for_geneformer,
    report_unmapped_symbols,
)
from .embeddings import (
    extract_cell_embeddings,
    attach_embeddings_to_anndata,
)
from .mechanism_axes import (
    compute_mechanism_axes,
    KAALCURA_3_AXES,
    MechanismAxis,
    MechanismAxisScores,
)
from .uncertainty import (
    compute_ensemble_uncertainty,
    compute_ood_distance,
    EnsembleUncertainty,
    OODDistance,
)
from .pipeline import (
    run_pipeline,
    PipelineResult,
)

__version__ = "0.1.2"  # bumped from 0.1.0 after FM-agnostic + macOS multiprocessing fixes
__all__ = [
    # Backends
    "FoundationModelBackend",
    "GeneformerBackend",
    "BackendMetadata",
    "detect_device",
    "safe_nproc",
    # Tokenization
    "map_symbols_to_ensembl",
    "prepare_anndata_for_geneformer",
    "report_unmapped_symbols",
    # Embeddings
    "extract_cell_embeddings",
    "attach_embeddings_to_anndata",
    # Mechanism axes
    "compute_mechanism_axes",
    "KAALCURA_3_AXES",
    "MechanismAxis",
    "MechanismAxisScores",
    # Uncertainty
    "compute_ensemble_uncertainty",
    "compute_ood_distance",
    "EnsembleUncertainty",
    "OODDistance",
    # Pipeline
    "run_pipeline",
    "PipelineResult",
]
