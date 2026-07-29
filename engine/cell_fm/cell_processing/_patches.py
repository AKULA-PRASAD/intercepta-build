"""
_patches.py — surgical patches to Geneformer tokenization that bypass the HuggingFace
Dataset.map step that hangs on macOS.

Why this file exists: Geneformer's TranscriptomeTokenizer.tokenize_data() does:

    tokenized_cells, metadata, counts = self.tokenize_files(...)  # pure Python, fine
    tokenized_dataset = self.create_dataset(...)                    # creates HF Dataset
    tokenized_dataset.save_to_disk(...)                             # writes Arrow files

The create_dataset step internally calls output_dataset.map(format_cell_features,
num_proc=self.nproc), which (a) allocates memory-mapped Arrow files and (b) registers
a multiprocessing.resource_tracker. On macOS, the resource_tracker becomes a zombie
that prevents the Python process from exiting cleanly, causing 60+ minute hangs.

Even with nproc=1, the Dataset.map() call allocates shared memory infrastructure that
triggers the resource_tracker spawn. Forcing nproc=1 doesn't help.

Our fix: use Geneformer's tokenize_files() (which returns plain Python lists),
then apply the truncate/CLS/EOS logic from create_dataset()'s format_cell_features
in pure Python. No HuggingFace Dataset is ever created. No resource_tracker spawns.

This file lives in cell_processing/ as an internal implementation detail. Public
callers should use GeneformerBackend.tokenize_anndata(), which calls into here.

Algorithm verification: The truncate/CLS/EOS logic mirrors lines 739-779 of
geneformer/tokenizer.py exactly. The rank/normalization logic is unchanged
(it lives in tokenize_files which we call directly).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np


def tokenize_anndata_no_hf_dataset(
    geneformer_pkg_dir: str | Path,
    staging_h5ad_path: str | Path,
    custom_attr_name_dict: Optional[dict] = None,
    chunk_size: int = 512,
    model_input_size: int = 4096,
    special_token: bool = True,
    collapse_gene_ids: bool = True,
    use_h5ad_index: bool = False,
    keep_counts: bool = False,
    model_version: str = "V2",
    gene_median_file: Optional[str] = None,
    token_dictionary_file: Optional[str] = None,
    gene_mapping_file: Optional[str] = None,
) -> list[dict]:
    """
    Tokenize a prepared h5ad through Geneformer's pipeline WITHOUT the HuggingFace
    Dataset wrapper that hangs on macOS.

    Args:
        geneformer_pkg_dir: path to the Geneformer python package directory
                            (used only to import TranscriptomeTokenizer cleanly).
        staging_h5ad_path: path to the prepared h5ad. Must have:
            - var["ensembl_id"]
            - obs["n_counts"]
            - .X as raw counts
        custom_attr_name_dict: e.g. {"label": "label"} to carry obs columns through.
        chunk_size: cells per processing chunk (Geneformer default 512).
        model_input_size: 4096 for V2, 2048 for V1.
        special_token: True for V2 (uses CLS/EOS), False for V1.
        collapse_gene_ids: True (Geneformer default).
        use_h5ad_index: False — we set ensembl_id explicitly in our prepare step.
        keep_counts: False — we don't need raw counts in tokenized output.
        model_version: "V2" (default for V2-104M_CLcancer).
        gene_median_file, token_dictionary_file, gene_mapping_file: paths to
            the gc104M tokenizer pickles. If None, Geneformer uses its own
            defaults (which work since the package is editable-installed).

    Returns:
        list[dict] where each dict represents one cell:
          {
            "input_ids": np.ndarray of int64,       # token IDs after CLS/EOS/truncate
            "length": int,                            # len(input_ids)
            **metadata_keys                           # e.g. "label" if requested
          }

    Notes:
        - Empty cells (no genes in token dict) are dropped, matching Geneformer's
          tokenize_anndata behavior at lines 599-617.
        - This function does NOT spawn any subprocesses. It does NOT create any
          HuggingFace Datasets. It does NOT memory-map any files. Safe on macOS.
    """
    from geneformer import TranscriptomeTokenizer

    staging_h5ad_path = Path(staging_h5ad_path).expanduser().resolve()
    if not staging_h5ad_path.exists():
        raise FileNotFoundError(f"Staging h5ad not found: {staging_h5ad_path}")

    # Build the tokenizer with the exact configuration we want.
    # nproc is irrelevant here because we never call Dataset.map(), but we set it
    # to 1 explicitly to be defensive.
    tk_kwargs = dict(
        custom_attr_name_dict=custom_attr_name_dict or {},
        nproc=1,
        chunk_size=chunk_size,
        model_input_size=model_input_size,
        special_token=special_token,
        collapse_gene_ids=collapse_gene_ids,
        use_h5ad_index=use_h5ad_index,
        keep_counts=keep_counts,
        model_version=model_version,
    )
    if gene_median_file is not None:
        tk_kwargs["gene_median_file"] = str(gene_median_file)
    if token_dictionary_file is not None:
        tk_kwargs["token_dictionary_file"] = str(token_dictionary_file)
    if gene_mapping_file is not None:
        tk_kwargs["gene_mapping_file"] = str(gene_mapping_file)

    tk = TranscriptomeTokenizer(**tk_kwargs)

    # Call tokenize_anndata directly. This returns plain Python lists.
    # No HuggingFace Dataset is created here.
    print(f"  [no-hf] tokenize_anndata: {staging_h5ad_path.name}")
    tokenized_cells, cell_metadata, _ = tk.tokenize_anndata(
        staging_h5ad_path, target_sum=10_000, file_format="h5ad"
    )
    print(f"  [no-hf] received {len(tokenized_cells)} tokenized cells (pre-CLS/EOS)")

    # Get special token IDs from Geneformer's token dictionary
    # (we need <cls> and <eos> for V2's special_token=True path)
    cls_token_id = None
    eos_token_id = None
    if special_token:
        # tk.gene_token_dict was loaded by TranscriptomeTokenizer.__init__
        cls_token_id = tk.gene_token_dict.get("<cls>")
        eos_token_id = tk.gene_token_dict.get("<eos>")
        if cls_token_id is None or eos_token_id is None:
            raise RuntimeError(
                "Token dictionary missing <cls> or <eos> tokens; cannot apply "
                "special_token=True formatting."
            )
    print(f"  [no-hf] special_token={special_token} (cls={cls_token_id}, eos={eos_token_id})")

    # Apply truncate + CLS/EOS in plain Python.
    # This mirrors create_dataset()'s format_cell_features at lines 739-779,
    # but as a simple list comprehension — no Dataset.map(), no shared memory.
    formatted = []
    for i, raw_input_ids in enumerate(tokenized_cells):
        # raw_input_ids is np.ndarray of token IDs ranked by expression
        if special_token:
            # Truncate to model_input_size - 2, then prepend <cls> and append <eos>
            truncated = raw_input_ids[: model_input_size - 2]
            input_ids = np.concatenate(
                [
                    np.array([cls_token_id], dtype=raw_input_ids.dtype),
                    truncated,
                    np.array([eos_token_id], dtype=raw_input_ids.dtype),
                ]
            )
        else:
            input_ids = raw_input_ids[:model_input_size]

        record = {
            "input_ids": input_ids,
            "length": int(len(input_ids)),
        }
        # Attach custom attributes (e.g. label)
        if custom_attr_name_dict and cell_metadata:
            for src_key, dst_key in custom_attr_name_dict.items():
                if dst_key in cell_metadata:
                    record[dst_key] = cell_metadata[dst_key][i]
                elif src_key in cell_metadata:
                    record[src_key] = cell_metadata[src_key][i]
        formatted.append(record)

    print(f"  [no-hf] formatted {len(formatted)} cells "
          f"(median length={int(np.median([r['length'] for r in formatted]))})")
    return formatted
