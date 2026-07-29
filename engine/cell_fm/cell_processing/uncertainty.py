"""
uncertainty.py — MFMD (Multi-Foundation-Model Disagreement) primitives.

Per Charter §6.5: "Foundation models trained on different corpora with
different objectives produce different embeddings of the same cell. When
they agree, the cellular biology is robustly represented. When they
disagree, predictions made on top of those embeddings carry less weight.
INTERCEPTA monitors this disagreement explicitly as MFMD."

This module provides the building blocks. Step B uses only `compute_ood_distance`
(distance from training-set centroid) since we only have one FM running.
When scFoundation lands as a second backend (next M1 sub-task), the full
ensemble disagreement layer activates.

Honest scope (Charter §9):
  - Single-FM "uncertainty" is fundamentally limited to OOD signals.
  - Real MFMD requires N>=2 independent FMs.
  - Ensemble disagreement is a *necessary but not sufficient* uncertainty
    signal. A single FM that's confidently wrong is undetected by MFMD.
    Cross-validation against held-out labels remains the gold standard.

References:
  - Lakshminarayanan et al. 2017, "Deep ensembles for predictive uncertainty"
  - Geifman & El-Yaniv 2017, "Selective classification for deep networks"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np


@dataclass
class EnsembleUncertainty:
    """Per-cell ensemble disagreement and aggregate statistics."""
    n_models: int
    per_cell_disagreement: np.ndarray   # (n_cells,) — pairwise mean cosine distance
    mean_disagreement: float
    median_disagreement: float
    method: str
    diagnostics: dict = field(default_factory=dict)


@dataclass
class OODDistance:
    """Per-cell distance from a reference centroid (e.g. training set mean)."""
    distances: np.ndarray              # (n_cells,)
    method: str
    reference_centroid_norm: float
    diagnostics: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Ensemble disagreement (multi-FM)
# ---------------------------------------------------------------------------
def compute_ensemble_uncertainty(
    embeddings_per_model: Sequence[np.ndarray],
    method: str = "pairwise_cosine_distance",
    normalize: bool = True,
) -> EnsembleUncertainty:
    """
    Compute MFMD ensemble disagreement across multiple FMs' embeddings.

    Each model contributes one (n_cells, hidden_dim_i) embedding matrix.
    Different models may have different hidden dimensions; we handle this
    by L2-normalizing each per-cell embedding before comparison (cosine
    distance is dimension-invariant after normalization).

    Args:
        embeddings_per_model: list of (n_cells, hidden_dim_i) numpy arrays.
                              Length must be >= 1; values are interesting
                              only when length >= 2.
        method: only "pairwise_cosine_distance" implemented in Step B scope.
        normalize: L2-normalize per-cell embeddings before distance computation.
                   Recommended (different FMs have different embedding scales).

    Returns:
        EnsembleUncertainty with per-cell disagreement scores.

        Special case: when len(embeddings_per_model) == 1, returns zeros
        and method="single_model" with diagnostics noting that disagreement
        is undefined.

    Raises:
        ValueError: if input lengths are inconsistent.
    """
    if len(embeddings_per_model) == 0:
        raise ValueError("Must provide at least one embedding matrix.")

    if method != "pairwise_cosine_distance":
        raise NotImplementedError(
            f"Method {method!r} not implemented in Step B scope."
        )

    n_models = len(embeddings_per_model)
    n_cells = embeddings_per_model[0].shape[0]

    for i, em in enumerate(embeddings_per_model):
        if em.shape[0] != n_cells:
            raise ValueError(
                f"Inconsistent n_cells across models: model {i} has {em.shape[0]}, "
                f"model 0 has {n_cells}."
            )

    if n_models == 1:
        # No disagreement to compute
        return EnsembleUncertainty(
            n_models=1,
            per_cell_disagreement=np.zeros(n_cells, dtype=np.float32),
            mean_disagreement=0.0,
            median_disagreement=0.0,
            method="single_model",
            diagnostics={
                "note": "Only one model provided; ensemble disagreement undefined.",
                "n_cells": n_cells,
                "hidden_dims": [int(em.shape[1]) for em in embeddings_per_model],
            },
        )

    # L2-normalize each model's embeddings (per-cell)
    if normalize:
        normed = []
        for em in embeddings_per_model:
            norms = np.linalg.norm(em, axis=1, keepdims=True)
            norms = np.where(norms < 1e-9, 1.0, norms)  # avoid div-by-zero
            normed.append(em / norms)
        embeddings_per_model = normed

    # Compute pairwise cosine distances per cell, then average
    # cosine_distance(a, b) = 1 - dot(a, b) when a, b are unit vectors
    n_pairs = n_models * (n_models - 1) // 2
    pairwise_distances = np.zeros((n_pairs, n_cells), dtype=np.float32)
    pair_idx = 0
    for i in range(n_models):
        # Different hidden_dim across models = can't directly dot-product.
        # We compare in shared metric: pairwise distance matrix per cell IS
        # only well-defined when hidden dims match. If they don't, fall back
        # to comparing each model's embedding to its OWN centroid distance,
        # which is a degenerate but defined operation.
        for j in range(i + 1, n_models):
            if embeddings_per_model[i].shape[1] != embeddings_per_model[j].shape[1]:
                # Dimension mismatch — use centroid-distance discrepancy instead
                ci = embeddings_per_model[i].mean(axis=0)
                cj = embeddings_per_model[j].mean(axis=0)
                di = np.linalg.norm(embeddings_per_model[i] - ci, axis=1)
                dj = np.linalg.norm(embeddings_per_model[j] - cj, axis=1)
                pairwise_distances[pair_idx] = np.abs(di - dj).astype(np.float32)
            else:
                dots = (embeddings_per_model[i] * embeddings_per_model[j]).sum(axis=1)
                pairwise_distances[pair_idx] = (1.0 - dots).astype(np.float32)
            pair_idx += 1

    per_cell = pairwise_distances.mean(axis=0)

    return EnsembleUncertainty(
        n_models=n_models,
        per_cell_disagreement=per_cell,
        mean_disagreement=float(per_cell.mean()),
        median_disagreement=float(np.median(per_cell)),
        method=method,
        diagnostics={
            "n_cells": n_cells,
            "hidden_dims": [int(em.shape[1]) for em in embeddings_per_model],
            "n_pairs": n_pairs,
        },
    )


# ---------------------------------------------------------------------------
# OOD distance (single-FM)
# ---------------------------------------------------------------------------
def compute_ood_distance(
    embeddings: np.ndarray,
    reference: np.ndarray | None = None,
    method: str = "euclidean",
) -> OODDistance:
    """
    Compute per-cell distance from a reference centroid in embedding space.

    If `reference` is None, the dataset's own mean is used as the reference
    (which gives a within-dataset distribution measure, not a true OOD signal
    — but useful for finding cells that are unusual within the dataset).

    True OOD detection requires `reference` to be the centroid of the FM's
    pretraining distribution or a held-out validation set. We don't have
    direct access to Geneformer's pretraining distribution, but we can
    approximate it later by embedding a known reference dataset (e.g.
    Tabula Sapiens) and using its centroid.

    Args:
        embeddings: (n_cells, hidden_dim) FM embeddings
        reference: (hidden_dim,) reference centroid; if None, use embeddings.mean(0)
        method: "euclidean" (default) or "cosine"

    Returns:
        OODDistance with per-cell scores and diagnostics.
    """
    if method not in ("euclidean", "cosine"):
        raise ValueError(f"Unknown method {method!r}; use 'euclidean' or 'cosine'.")

    n_cells, hidden_dim = embeddings.shape

    if reference is None:
        reference = embeddings.mean(axis=0)
        ref_source = "dataset_mean"
    else:
        if reference.shape != (hidden_dim,):
            raise ValueError(
                f"reference shape {reference.shape} does not match "
                f"embedding hidden_dim {hidden_dim}"
            )
        ref_source = "external"

    if method == "euclidean":
        diffs = embeddings - reference[None, :]
        dists = np.linalg.norm(diffs, axis=1).astype(np.float32)
    else:  # cosine
        ref_norm = np.linalg.norm(reference)
        if ref_norm < 1e-9:
            raise ValueError("Reference centroid has zero norm.")
        ref_unit = reference / ref_norm
        emb_norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        emb_norms = np.where(emb_norms < 1e-9, 1.0, emb_norms)
        emb_unit = embeddings / emb_norms
        cos_sim = (emb_unit * ref_unit[None, :]).sum(axis=1)
        dists = (1.0 - cos_sim).astype(np.float32)

    return OODDistance(
        distances=dists,
        method=method,
        reference_centroid_norm=float(np.linalg.norm(reference)),
        diagnostics={
            "n_cells": n_cells,
            "hidden_dim": hidden_dim,
            "reference_source": ref_source,
            "distance_mean": float(dists.mean()),
            "distance_median": float(np.median(dists)),
            "distance_p95": float(np.percentile(dists, 95)),
        },
    )
