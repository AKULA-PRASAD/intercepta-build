"""
pipeline.py — End-to-end orchestration of cell_processing.

Takes an AnnData and a FoundationModelBackend; produces a PipelineResult
containing embeddings, mechanism axis scores, OOD distances, and provenance.

Charter §6.4 commits to this shape: foundation models -> embeddings ->
mechanism axes -> downstream prediction. This file is the canonical
orchestration of the first three stages.

FM-agnostic principle (fix log v0.1.1, 2026-05-09):
  This pipeline calls the backend's interface methods only. It does NOT
  reach into backend-specific attributes (e.g. backend.gene_name_id_path).
  Adding a new backend never requires changes here.

Outputs:
  - <prefix>_embeddings.npy        (cells x hidden_dim, float32)
  - <prefix>_axis_scores.csv       (cells x KAALCURA-3 axes)
  - <prefix>_ood_distances.npy     (cells, float32)
  - <prefix>_run_report.json       (provenance)
  - <prefix>_prepared.h5ad         (input AnnData with embeddings/scores
                                    attached under .obsm and .obs)
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

import numpy as np


@dataclass
class PipelineResult:
    """Structured result of a cell_processing pipeline run."""
    embeddings: np.ndarray              # (n_cells, hidden_dim)
    axis_scores: np.ndarray             # (n_cells, n_axes)
    axis_names: tuple[str, ...]
    ood_distances: np.ndarray           # (n_cells,)
    backend_metadata: dict              # asdict() of BackendMetadata
    prep_stats: dict                    # from backend.prepare_anndata
    axis_diagnostics: dict              # from compute_mechanism_axes
    ood_diagnostics: dict               # from compute_ood_distance
    timing: dict                        # phase_name -> seconds
    output_paths: dict = field(default_factory=dict)


def run_pipeline(
    adata,
    backend,
    output_dir: str | Path,
    output_prefix: str = "step_B",
    custom_attrs: Optional[dict] = None,
    batch_size: int = 16,
    save_intermediate: bool = True,
    obsm_key: Optional[str] = None,
    skip_prepare: bool = False,
    skip_tokenize: bool = False,
    tokenized_path_override: Optional[str | Path] = None,
) -> PipelineResult:
    """
    Run the cell_processing pipeline end-to-end (or resume partway).

    Args:
        adata: input AnnData (raw counts, gene symbols in .var.index by default)
        backend: a loaded FoundationModelBackend instance (call backend.load()
                 before passing — pipeline does NOT call load() to let the
                 caller manage GPU memory across multiple pipeline runs).
        output_dir: where to write all artifacts
        output_prefix: filename prefix for outputs
        custom_attrs: dict mapping AnnData obs columns to carry through
                      tokenization, e.g. {"label": "label"}
        batch_size: forward pass batch size
        save_intermediate: write tokenized dataset and prepared h5ad
        obsm_key: key under which to attach embeddings to adata.obsm.
                  If None, derived from backend metadata as "X_<family>".
        skip_prepare: if True, skip Phase A (caller has already prepared).
                      Useful for resuming from a saved prepared h5ad.
        skip_tokenize: if True, skip Phase B (caller provides tokenized_path).
                       Useful for resuming after Phase B output is on disk.
        tokenized_path_override: if skip_tokenize=True, path to existing
                                  tokenized HF .dataset directory.

    Returns:
        PipelineResult with all outputs.
    """
    from .embeddings import attach_embeddings_to_anndata
    from .mechanism_axes import compute_mechanism_axes, KAALCURA_3_AXES
    from .uncertainty import compute_ood_distance

    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    timing: dict = {}
    output_paths: dict = {}
    t_start = time.time()

    # ----- Phase A: prepare AnnData (FM-agnostic — backend handles its specifics) -----
    if skip_prepare:
        print("[pipeline] Phase A: SKIPPED (caller passed prepared adata)")
        prep_adata = adata
        prep_stats = {"skipped": True}
        timing["prepare"] = 0.0
    else:
        print(f"[pipeline] Phase A: prepare AnnData ({adata.shape})")
        t0 = time.time()
        prep_adata, prep_stats = backend.prepare_anndata(adata)
        timing["prepare"] = time.time() - t0
        rate = prep_stats.get("mapping_rate")
        rate_str = f"{rate:.1%}" if rate is not None else "n/a"
        print(f"  -> {prep_adata.shape} after preparation (mapping_rate={rate_str})")

    # ----- Phase B: tokenize -----
    if skip_tokenize:
        if tokenized_path_override is None:
            raise ValueError(
                "skip_tokenize=True requires tokenized_path_override to point "
                "to an existing HF .dataset directory."
            )
        tokenized_path = Path(tokenized_path_override).expanduser().resolve()
        if not tokenized_path.exists():
            raise FileNotFoundError(f"tokenized_path_override not found: {tokenized_path}")
        print(f"[pipeline] Phase B: SKIPPED (using existing tokenized at {tokenized_path})")
        timing["tokenize"] = 0.0
    else:
        print("[pipeline] Phase B: tokenize")
        t0 = time.time()
        tokenized_dir = output_dir / "tokenized"
        tokenized_dir.mkdir(exist_ok=True)
        tokenized_path = backend.tokenize_anndata(
            prep_adata,
            output_dir=tokenized_dir,
            output_prefix=f"{output_prefix}_tokenized",
            custom_attrs=custom_attrs,
        )
        timing["tokenize"] = time.time() - t0
        print(f"  -> tokenized at {tokenized_path}")
    output_paths["tokenized_dataset"] = str(tokenized_path)

    # ----- Phase C: forward pass (extract embeddings) -----
    print("[pipeline] Phase C: forward pass (extract cell embeddings)")
    t0 = time.time()
    embeddings = backend.forward(tokenized_path, batch_size=batch_size)
    timing["forward_pass"] = time.time() - t0
    print(f"  -> embeddings shape {embeddings.shape}, "
          f"forward pass took {timing['forward_pass']:.1f}s")

    # Attach to AnnData
    backend_meta = backend.metadata()
    if obsm_key is None:
        obsm_key = f"X_{backend_meta.family}"
    attach_embeddings_to_anndata(embeddings, prep_adata, obsm_key=obsm_key)

    # Save embeddings
    emb_path = output_dir / f"{output_prefix}_embeddings.npy"
    np.save(emb_path, embeddings)
    output_paths["embeddings"] = str(emb_path)

    # ----- Phase D: mechanism axes -----
    print("[pipeline] Phase D: mechanism axis projection (KAALCURA-3)")
    t0 = time.time()
    axis_result = compute_mechanism_axes(
        embeddings=embeddings,
        adata=prep_adata,
        axes=KAALCURA_3_AXES,
    )
    timing["mechanism_axes"] = time.time() - t0
    print(f"  -> axes: {axis_result.axis_names}")
    for ax_name, diag in axis_result.diagnostics["per_axis"].items():
        status = diag.get("status", "?")
        n_pos = diag.get("n_axis_positive", "?")
        print(f"    {ax_name}: {status} (n_positive={n_pos})")

    # Attach axis scores to AnnData
    prep_adata.obsm["axis_scores"] = axis_result.scores
    for i, ax_name in enumerate(axis_result.axis_names):
        prep_adata.obs[ax_name] = axis_result.scores[:, i]

    # Save axis scores CSV
    import pandas as pd
    ax_df = pd.DataFrame(axis_result.scores, columns=list(axis_result.axis_names))
    ax_df.index = prep_adata.obs.index
    ax_csv = output_dir / f"{output_prefix}_axis_scores.csv"
    ax_df.to_csv(ax_csv)
    output_paths["axis_scores_csv"] = str(ax_csv)

    # ----- Phase E: OOD distance -----
    print("[pipeline] Phase E: OOD distance from dataset centroid")
    t0 = time.time()
    ood_result = compute_ood_distance(embeddings)
    timing["ood_distance"] = time.time() - t0
    prep_adata.obs["ood_distance"] = ood_result.distances
    print(f"  -> distance mean={ood_result.diagnostics['distance_mean']:.3f}, "
          f"median={ood_result.diagnostics['distance_median']:.3f}, "
          f"p95={ood_result.diagnostics['distance_p95']:.3f}")

    ood_path = output_dir / f"{output_prefix}_ood_distances.npy"
    np.save(ood_path, ood_result.distances)
    output_paths["ood_distances"] = str(ood_path)

    # ----- Phase F: save prepared AnnData with everything attached -----
    if save_intermediate:
        adata_path = output_dir / f"{output_prefix}_prepared.h5ad"
        prep_adata.write_h5ad(adata_path)
        output_paths["prepared_h5ad"] = str(adata_path)

    # ----- Phase G: write provenance report -----
    timing["total"] = time.time() - t_start
    report = {
        "output_prefix": output_prefix,
        "backend_metadata": asdict(backend_meta),
        "input_shape": list(adata.shape),
        "prepared_shape": list(prep_adata.shape),
        "embedding_shape": list(embeddings.shape),
        "prep_stats": prep_stats,
        "axis_diagnostics": axis_result.diagnostics,
        "ood_diagnostics": ood_result.diagnostics,
        "timing_seconds": timing,
        "output_paths": output_paths,
        "pipeline_options": {
            "skip_prepare": skip_prepare,
            "skip_tokenize": skip_tokenize,
            "batch_size": batch_size,
        },
    }
    report_path = output_dir / f"{output_prefix}_run_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    output_paths["run_report"] = str(report_path)

    print(f"[pipeline] complete in {timing['total']:.1f}s — outputs in {output_dir}")

    return PipelineResult(
        embeddings=embeddings,
        axis_scores=axis_result.scores,
        axis_names=axis_result.axis_names,
        ood_distances=ood_result.distances,
        backend_metadata=asdict(backend_meta),
        prep_stats=prep_stats,
        axis_diagnostics=axis_result.diagnostics,
        ood_diagnostics=ood_result.diagnostics,
        timing=timing,
        output_paths=output_paths,
    )
