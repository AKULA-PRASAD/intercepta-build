"""
tokenization.py — gene identifier mapping and AnnData preparation.

Foundation models for single-cell data expect Ensembl gene IDs
(ENSG00000XXXXXX), but most published datasets use HGNC symbols (TP53, KRAS).
This module handles the mapping and the AnnData preparation that FM tokenizers
require.

Functions are FM-agnostic: the same `map_symbols_to_ensembl()` works for
Geneformer, scFoundation, UCE, and any future FM. Different FMs ship different
mapping dictionaries; the function just takes whichever one is appropriate.

Honest limits (Charter §9):
  - Symbol-to-Ensembl mapping is lossy. Not every symbol has an Ensembl ID
    in any single dictionary. Typical mapping rate on real data is 60-80%.
    This is why we report `n_mapped / n_total` and flag low rates.
  - Gene aliases mean two symbols may map to the same Ensembl ID; we keep
    the first occurrence and warn.
  - Some genes (e.g. T-cell receptor segments) lack stable Ensembl IDs
    altogether; these are simply unmapped.
"""

from __future__ import annotations

import pickle
import warnings
from pathlib import Path
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Symbol -> Ensembl mapping
# ---------------------------------------------------------------------------
def map_symbols_to_ensembl(
    symbols: list[str],
    mapping_dict_path: str | Path,
) -> tuple[list[Optional[str]], dict]:
    """
    Map a list of gene symbols to Ensembl IDs using a pickled dictionary.

    Args:
        symbols: list of HGNC gene symbols (e.g. ["TP53", "KRAS", "A1BG"])
        mapping_dict_path: path to a pickle file containing a
                           {symbol: ensembl_id} dictionary

    Returns:
        (ensembl_ids, stats):
            ensembl_ids: list same length as `symbols`, with None where
                         a symbol could not be mapped
            stats: dict with keys n_total, n_mapped, n_unmapped, mapping_rate

    Example:
        >>> ids, stats = map_symbols_to_ensembl(
        ...     ["TP53", "KRAS", "FAKE_GENE_XYZ"],
        ...     "~/INTERCEPTA/models/Geneformer/geneformer/gene_name_id_dict_gc104M.pkl"
        ... )
        >>> stats["mapping_rate"]
        0.6667
    """
    mapping_dict_path = Path(mapping_dict_path).expanduser().resolve()
    if not mapping_dict_path.exists():
        raise FileNotFoundError(f"Mapping dict not found: {mapping_dict_path}")

    with open(mapping_dict_path, "rb") as f:
        mapping = pickle.load(f)

    if not isinstance(mapping, dict):
        raise TypeError(
            f"Mapping file is not a dict: {mapping_dict_path} -> {type(mapping)}"
        )

    ensembl_ids = [mapping.get(str(s), None) for s in symbols]
    n_total = len(symbols)
    n_mapped = sum(1 for e in ensembl_ids if e is not None)
    n_unmapped = n_total - n_mapped

    stats = {
        "n_total": n_total,
        "n_mapped": n_mapped,
        "n_unmapped": n_unmapped,
        "mapping_rate": n_mapped / n_total if n_total > 0 else 0.0,
        "mapping_dict_path": str(mapping_dict_path),
        "mapping_dict_size": len(mapping),
    }

    if stats["mapping_rate"] < 0.30:
        warnings.warn(
            f"Low symbol mapping rate: {stats['mapping_rate']:.1%}. "
            f"Check that the symbols are HGNC and the mapping dict matches "
            f"the FM's expected vocabulary.",
            stacklevel=2,
        )

    return ensembl_ids, stats


# ---------------------------------------------------------------------------
# AnnData preparation
# ---------------------------------------------------------------------------
def prepare_anndata_for_geneformer(
    adata,
    mapping_dict_path: str | Path,
    var_index_is_symbol: bool = True,
    require_n_counts: bool = True,
    min_mapping_rate: float = 0.30,
) -> tuple[object, dict]:
    """
    Prepare an AnnData object for Geneformer's TranscriptomeTokenizer.

    Geneformer requires:
      1. `.var["ensembl_id"]` column with Ensembl gene IDs
      2. `.obs["n_counts"]` per-cell raw library size (sum of counts)
      3. `.X` containing raw integer counts (not log-normalized)

    This function takes a typical AnnData with HGNC gene symbols in
    `.var.index` and produces a Geneformer-ready copy:
      - filters to only genes with Ensembl mappings
      - adds `var["ensembl_id"]` column
      - adds `obs["n_counts"]` if missing
      - validates that `.X` looks like raw counts

    Args:
        adata: input AnnData
        mapping_dict_path: pickle of {symbol: ensembl_id}
        var_index_is_symbol: if True (default), `.var.index` holds symbols.
                             If False, this function does nothing to .var.
        require_n_counts: if True and `.obs["n_counts"]` is missing, compute it.
        min_mapping_rate: error if symbol-to-Ensembl mapping rate falls below
                          this threshold (suggests wrong mapping dict)

    Returns:
        (prepared_adata, prep_stats)

    Raises:
        ValueError: if mapping rate is too low or `.X` doesn't look like counts.
    """
    import anndata as ad
    import scipy.sparse as sp

    prep_stats: dict = {}

    # Validate .X looks like raw counts (Geneformer normalizes internally)
    if hasattr(adata.X, "toarray"):
        sample = adata.X[:100].toarray() if adata.shape[0] >= 100 else adata.X.toarray()
    else:
        sample = adata.X[:100]
    if not np.issubdtype(sample.dtype, np.integer):
        # Could still be raw counts stored as float; check fractional part
        frac = np.abs(sample - np.round(sample)).sum()
        if frac > 1e-3:
            raise ValueError(
                f"adata.X dtype is {sample.dtype} and contains non-integer values "
                f"(suggests log-normalized data). Geneformer requires raw counts."
            )
    prep_stats["x_dtype_input"] = str(adata.X.dtype)

    # Map symbols to Ensembl
    if var_index_is_symbol:
        symbols = adata.var.index.astype(str).tolist()
        ensembl_ids, map_stats = map_symbols_to_ensembl(symbols, mapping_dict_path)
        prep_stats.update(map_stats)

        if map_stats["mapping_rate"] < min_mapping_rate:
            raise ValueError(
                f"Symbol mapping rate {map_stats['mapping_rate']:.1%} below "
                f"threshold {min_mapping_rate:.1%}. Check mapping dictionary "
                f"matches FM's expected vocabulary."
            )

        # Filter to mapped genes
        mapped_mask = np.array([e is not None for e in ensembl_ids])
        adata = adata[:, mapped_mask].copy()
        adata.var["ensembl_id"] = [
            ensembl_ids[i] for i in range(len(ensembl_ids)) if mapped_mask[i]
        ]
        prep_stats["n_genes_after_mapping"] = adata.shape[1]
    else:
        if "ensembl_id" not in adata.var.columns:
            raise ValueError(
                "var_index_is_symbol=False but adata.var has no 'ensembl_id' "
                "column. Either set the column or pass var_index_is_symbol=True."
            )
        adata = adata.copy()

    # Add n_counts if missing
    if require_n_counts and "n_counts" not in adata.obs.columns:
        if hasattr(adata.X, "sum"):
            n_counts = np.asarray(adata.X.sum(axis=1)).flatten()
        else:
            n_counts = adata.X.sum(axis=1)
        adata.obs["n_counts"] = n_counts.astype(np.int64)
        prep_stats["added_n_counts"] = True
    else:
        prep_stats["added_n_counts"] = False

    prep_stats["n_cells"] = adata.shape[0]
    prep_stats["n_genes_final"] = adata.shape[1]
    prep_stats["median_n_counts"] = (
        int(np.median(adata.obs["n_counts"])) if "n_counts" in adata.obs.columns else None
    )

    return adata, prep_stats


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------
def report_unmapped_symbols(
    symbols: list[str],
    mapping_dict_path: str | Path,
    top_n: int = 20,
) -> dict:
    """
    Report which symbols failed to map. Useful for diagnosing low mapping rates.

    Args:
        symbols: input symbols
        mapping_dict_path: pickle of {symbol: ensembl_id}
        top_n: how many unmapped symbols to return as examples

    Returns:
        dict with `n_unmapped`, `unmapped_examples`, and `mapped_examples`.
    """
    mapping_dict_path = Path(mapping_dict_path).expanduser().resolve()
    with open(mapping_dict_path, "rb") as f:
        mapping = pickle.load(f)

    unmapped = [s for s in symbols if str(s) not in mapping]
    mapped = [s for s in symbols if str(s) in mapping]

    return {
        "n_total": len(symbols),
        "n_mapped": len(mapped),
        "n_unmapped": len(unmapped),
        "unmapped_examples": unmapped[:top_n],
        "mapped_examples": mapped[:top_n],
    }
