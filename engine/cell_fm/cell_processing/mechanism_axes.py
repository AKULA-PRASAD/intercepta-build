"""
mechanism_axes.py — KAALCURA-style mechanism axis projection on FM embeddings.

INTERCEPTA's mechanism axes encode disease-relevant biology that drug
responses operate through. For cancer (Round 1-3 validated), we use the
KAALCURA-3 axes:
    R_prolif : proliferation axis (cell-cycle, growth signaling)
    R_emt    : epithelial-mesenchymal transition axis (invasion, metastasis)
    R_ddr    : DNA damage response axis (PARP, ATM, BRCA biology)

These axes are validated mechanistically: PARP inhibitors have negative
R_ddr coefficients in our GDSC validation (Olaparib -1.300, Veliparib -0.944,
Niraparib -1.565 — Charter §3.5).

Charter §6.4 (M1 — MC-FMA): "Mechanism axes emerge from constrained
fine-tuning, not from hand-crafted projections. Full MC-FMA learns axes
that maximize predictive performance on drug response while remaining
interpretable through their mechanism-anchored loss terms."

Charter §10.2 (Dynamic Universality): "Mechanism axes are disease-specific.
Cancer uses KAALCURA-3. Autoimmune disease will use different axes
(inflammation, autoreactivity, tolerance). The framework is universal;
the axes are learned per disease."

This file (Step B scope):
  - Provides KAALCURA-3 axes as gene-marker sets
  - Computes axis scores by projecting FM embeddings onto axis directions
  - Implements axis directions via mean-of-marker-cells embedding (simple,
    pre-MC-FMA approach — replaced when M1 fully ships)
  - Honest: results are correlational, not causal until MC-FMA fine-tuning

Future (M1):
  - Replace `compute_mechanism_axes` body with MC-FMA inference
  - Add `compute_axes_for_disease(adata, disease="autoimmune")` for
    dynamic universality (Charter §10)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# KAALCURA-3 axis definitions
# ---------------------------------------------------------------------------
# Marker genes per axis. These are validated cancer biology markers; full
# definitions are in INTERCEPTA's KAALCURA documentation. Symbol form is
# canonical here; resolution to FM-vocab tokens happens at use time.
@dataclass(frozen=True)
class MechanismAxis:
    """Definition of one mechanism axis."""
    name: str
    description: str
    markers_up: tuple[str, ...]      # genes high in cells with this axis active
    markers_down: tuple[str, ...]    # genes low in cells with this axis active


KAALCURA_3_AXES: tuple[MechanismAxis, ...] = (
    MechanismAxis(
        name="R_prolif",
        description="Proliferation: cell-cycle progression, growth signaling.",
        markers_up=(
            "MKI67", "PCNA", "MCM2", "MCM5", "MCM6", "TOP2A", "CCNB1",
            "CCNB2", "CCNA2", "CCNE1", "CDK1", "CDK2", "AURKA", "AURKB",
            "BIRC5", "FOXM1", "E2F1", "MYC",
        ),
        markers_down=(
            "CDKN1A", "CDKN1B", "CDKN2A", "RB1", "TP53",
        ),
    ),
    MechanismAxis(
        name="R_emt",
        description="Epithelial-mesenchymal transition: invasion, metastasis.",
        markers_up=(
            "VIM", "FN1", "SNAI1", "SNAI2", "ZEB1", "ZEB2", "TWIST1",
            "CDH2", "S100A4", "MMP2", "MMP9", "TGFB1", "TGFBR2",
        ),
        markers_down=(
            "CDH1", "CLDN3", "CLDN4", "CLDN7", "EPCAM", "OCLN", "KRT8",
            "KRT18", "KRT19",
        ),
    ),
    MechanismAxis(
        name="R_ddr",
        description="DNA damage response: PARP, ATM/ATR, BRCA-pathway biology.",
        markers_up=(
            "ATM", "ATR", "BRCA1", "BRCA2", "PARP1", "PARP2", "RAD51",
            "RAD52", "MRE11", "RAD50", "NBN", "CHEK1", "CHEK2", "TP53BP1",
            "H2AFX", "PALB2", "FANCD2", "FANCA",
        ),
        markers_down=(),
    ),
)


# ---------------------------------------------------------------------------
# Axis score computation
# ---------------------------------------------------------------------------
@dataclass
class MechanismAxisScores:
    """Per-cell scores along each mechanism axis."""
    axis_names: tuple[str, ...]
    scores: np.ndarray          # shape (n_cells, n_axes)
    method: str                 # how scores were computed
    diagnostics: dict = field(default_factory=dict)


def compute_mechanism_axes(
    embeddings: np.ndarray,
    adata,
    axes: tuple[MechanismAxis, ...] = KAALCURA_3_AXES,
    method: str = "marker_centroid_projection",
    var_index_is_symbol: bool = True,
) -> MechanismAxisScores:
    """
    Compute mechanism axis scores for each cell.

    Pre-MC-FMA approach (Step B scope):
      For each axis, identify cells whose marker_up genes are highly
      expressed and marker_down genes are lowly expressed. Average those
      cells' FM embeddings to get an "axis centroid". Project all cell
      embeddings onto the unit vector from origin (mean embedding) toward
      the axis centroid. The projection length is the axis score.

      This is correlational, not causal. It says "cells along this
      direction in embedding space tend to express these markers." MC-FMA
      will replace this with mechanism-constrained fine-tuning that
      produces axes optimized for predictive performance.

    Args:
        embeddings: (n_cells, hidden_dim) FM cell embeddings
        adata: AnnData with same n_cells; used to read marker expression
        axes: tuple of MechanismAxis definitions; defaults to KAALCURA-3
        method: only "marker_centroid_projection" supported in Step B scope
        var_index_is_symbol: True if adata.var.index has gene symbols

    Returns:
        MechanismAxisScores with per-cell scores and diagnostics.
    """
    if method != "marker_centroid_projection":
        raise NotImplementedError(
            f"Method {method!r} not implemented in pre-MC-FMA scope. "
            f"Only 'marker_centroid_projection' is supported."
        )

    if embeddings.shape[0] != adata.shape[0]:
        raise ValueError(
            f"embeddings has {embeddings.shape[0]} cells, "
            f"adata has {adata.shape[0]} cells."
        )

    n_cells, hidden_dim = embeddings.shape
    axis_names = tuple(ax.name for ax in axes)
    scores = np.zeros((n_cells, len(axes)), dtype=np.float32)

    # Compute the dataset-wide mean embedding (used as origin)
    mean_emb = embeddings.mean(axis=0)

    diagnostics = {
        "n_cells": n_cells,
        "hidden_dim": hidden_dim,
        "method": method,
        "per_axis": {},
    }

    var_symbols = adata.var.index.astype(str).tolist() if var_index_is_symbol else None

    for axis_idx, axis in enumerate(axes):
        # Resolve marker symbols to AnnData column indices
        markers_up_idx = []
        markers_up_found = []
        if var_symbols is not None:
            for m in axis.markers_up:
                if m in var_symbols:
                    markers_up_idx.append(var_symbols.index(m))
                    markers_up_found.append(m)

        markers_down_idx = []
        markers_down_found = []
        if var_symbols is not None:
            for m in axis.markers_down:
                if m in var_symbols:
                    markers_down_idx.append(var_symbols.index(m))
                    markers_down_found.append(m)

        if not markers_up_idx:
            # No up-markers found; axis is undefined for this dataset
            scores[:, axis_idx] = np.nan
            diagnostics["per_axis"][axis.name] = {
                "status": "no_markers_found",
                "markers_up_found": [],
                "markers_down_found": [],
            }
            continue

        # Compute per-cell marker score = mean(up) - mean(down) on raw expression
        X = adata.X
        if hasattr(X, "toarray"):
            up_expr = np.asarray(X[:, markers_up_idx].toarray()).mean(axis=1)
            if markers_down_idx:
                down_expr = np.asarray(X[:, markers_down_idx].toarray()).mean(axis=1)
            else:
                down_expr = np.zeros(n_cells)
        else:
            up_expr = X[:, markers_up_idx].mean(axis=1)
            down_expr = (
                X[:, markers_down_idx].mean(axis=1)
                if markers_down_idx else np.zeros(n_cells)
            )
        marker_score = np.asarray(up_expr - down_expr).flatten()

        # Identify "axis-positive" cells = top quintile of marker score
        threshold = np.percentile(marker_score, 80)
        axis_pos_mask = marker_score >= threshold
        n_axis_pos = int(axis_pos_mask.sum())

        if n_axis_pos < 5:
            # Not enough axis-positive cells to define a direction
            scores[:, axis_idx] = np.nan
            diagnostics["per_axis"][axis.name] = {
                "status": "too_few_axis_positive_cells",
                "n_axis_positive": n_axis_pos,
                "markers_up_found": markers_up_found,
                "markers_down_found": markers_down_found,
            }
            continue

        # Centroid embedding of axis-positive cells
        centroid = embeddings[axis_pos_mask].mean(axis=0)

        # Direction = centroid - mean
        direction = centroid - mean_emb
        norm = np.linalg.norm(direction)
        if norm < 1e-9:
            scores[:, axis_idx] = np.nan
            diagnostics["per_axis"][axis.name] = {
                "status": "degenerate_direction",
                "markers_up_found": markers_up_found,
            }
            continue
        direction = direction / norm

        # Project every cell embedding onto this direction (relative to mean)
        cell_proj = (embeddings - mean_emb) @ direction
        scores[:, axis_idx] = cell_proj.astype(np.float32)

        diagnostics["per_axis"][axis.name] = {
            "status": "ok",
            "n_axis_positive": n_axis_pos,
            "markers_up_found": markers_up_found,
            "markers_down_found": markers_down_found,
            "marker_score_threshold": float(threshold),
            "direction_norm": float(norm),
            "score_mean": float(scores[:, axis_idx].mean()),
            "score_std": float(scores[:, axis_idx].std()),
        }

    return MechanismAxisScores(
        axis_names=axis_names,
        scores=scores,
        method=method,
        diagnostics=diagnostics,
    )
