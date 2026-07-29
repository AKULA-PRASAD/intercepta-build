"""
embeddings.py — Device-agnostic forward pass for foundation model cell embedding extraction.

This module is the architectural reason we wrote our own pipeline rather than
using Geneformer's upstream EmbExtractor. The upstream extractor hardcodes
`device="cuda"` (geneformer/emb_extractor.py:101), which fails on Apple Silicon
and any other non-CUDA system. Our implementation:

  - Detects the device from the model itself (via the `device` argument).
  - Iterates batches with proper padding.
  - Mean-pools across the gene tokens (excluding [CLS], [SEP], [PAD] which
    are not biological).
  - Returns a single numpy array.

Input formats accepted (v0.1.2):
  1. list[dict]  with each dict having "input_ids" key  ← preferred (no-HF path)
  2. str/Path    pointing to a HuggingFace .dataset directory  ← legacy
  3. datasets.Dataset object  ← legacy

The list[dict] format is preferred on macOS to avoid the multiprocessing.resource_tracker
hang that HuggingFace Datasets memory-mapping triggers (see _patches.py).

Reference (Charter §6.6, §9): "The system runs on whatever hardware the user
has. CUDA is not assumed. MPS, CPU, and future accelerators are first-class.
Hardcoded device strings are bugs."
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Optional, Union, Sequence

import numpy as np
import torch


# Geneformer special token names (the gc104M token dict has these as keys)
SPECIAL_TOKEN_NAMES = ("<pad>", "<mask>", "<cls>", "<eos>")


def _load_special_token_ids(token_dict_path: Union[str, Path]) -> set[int]:
    """
    Load the gc104M token dictionary and return the set of special token IDs
    (CLS, EOS, PAD, MASK) so we can exclude them from the mean pool.
    """
    with open(token_dict_path, "rb") as f:
        token_dict = pickle.load(f)
    special_ids = set()
    for name in SPECIAL_TOKEN_NAMES:
        if name in token_dict:
            special_ids.add(int(token_dict[name]))
    return special_ids


def _normalize_input_to_list(tokenized_input) -> list[dict]:
    """
    Accept any of the three supported input formats and return a list[dict]
    with each dict containing at minimum an "input_ids" key.

    Returns:
        list[dict] - each dict has "input_ids" (sequence of int)
    """
    # Already a list of dicts?
    if isinstance(tokenized_input, list):
        if len(tokenized_input) == 0:
            raise ValueError("tokenized_input is an empty list.")
        if not isinstance(tokenized_input[0], dict):
            raise TypeError(
                f"List input must contain dicts; first element is "
                f"{type(tokenized_input[0]).__name__}"
            )
        if "input_ids" not in tokenized_input[0]:
            raise ValueError(
                f"First dict missing 'input_ids' key; keys: {list(tokenized_input[0].keys())}"
            )
        return tokenized_input

    # Path or string — load HuggingFace Dataset from disk
    if isinstance(tokenized_input, (str, Path)):
        from datasets import load_from_disk
        path = Path(tokenized_input).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Tokenized dataset not found: {path}")
        ds = load_from_disk(str(path))
        return [{"input_ids": list(ds[i]["input_ids"]),
                 "length": len(ds[i]["input_ids"])}
                for i in range(len(ds))]

    # Probably a HuggingFace Dataset object
    if hasattr(tokenized_input, "column_names"):
        if "input_ids" not in tokenized_input.column_names:
            raise RuntimeError(
                f"Dataset missing 'input_ids' column. "
                f"Available columns: {tokenized_input.column_names}"
            )
        return [{"input_ids": list(tokenized_input[i]["input_ids"]),
                 "length": len(tokenized_input[i]["input_ids"])}
                for i in range(len(tokenized_input))]

    raise TypeError(
        f"Unsupported tokenized_input type: {type(tokenized_input).__name__}. "
        f"Pass list[dict], path to .dataset directory, or datasets.Dataset object."
    )


def extract_cell_embeddings(
    model,
    tokenized_input: Union[list[dict], str, Path, "datasets.Dataset"],
    device: torch.device,
    batch_size: int = 16,
    token_dict_path: Optional[Union[str, Path]] = None,
    pad_token_id: int = 0,
    progress: bool = True,
    progress_every: int = 50,
) -> np.ndarray:
    """
    Forward a tokenized cell collection through a foundation model and return
    cell-level embeddings.

    Args:
        model: a loaded FM (e.g. BertForMaskedLM); must already be on `device`
               and in `eval()` mode.
        tokenized_input: one of:
            - list[dict] with "input_ids" key per element  (preferred, macOS-safe)
            - path to a HuggingFace .dataset directory
            - HuggingFace Dataset object
        device: the torch device the model lives on (the function does NOT
                move the model; caller is responsible).
        batch_size: forward-pass batch size. 8 is conservative for MPS;
                    32-64 is reasonable for V100.
        token_dict_path: path to the FM's token dictionary pickle. If provided,
                         we exclude its special tokens from the mean pool.
                         If None, only PAD (id=0) is excluded.
        pad_token_id: token ID used for padding (default 0, Geneformer convention).
        progress: print progress at intervals.
        progress_every: how often to print batch progress (every N batches).

    Returns:
        np.ndarray of shape (n_cells, hidden_dim) with float32 embeddings.
    """
    # Normalize input to list[dict]
    cells = _normalize_input_to_list(tokenized_input)
    n_cells = len(cells)

    if n_cells == 0:
        raise ValueError("Tokenized input has zero cells.")

    # Determine special token IDs to exclude from mean pool
    excluded_ids = {pad_token_id}
    if token_dict_path is not None:
        excluded_ids |= _load_special_token_ids(token_dict_path)

    hidden_dim = model.config.hidden_size
    embeddings = np.zeros((n_cells, hidden_dim), dtype=np.float32)

    if progress:
        print(f"  extracting embeddings: {n_cells} cells, hidden_dim={hidden_dim}, "
              f"device={device}, batch_size={batch_size}")
        print(f"  excluded token IDs: {sorted(excluded_ids)}")

    n_batches = (n_cells + batch_size - 1) // batch_size

    with torch.no_grad():
        for batch_idx in range(n_batches):
            start = batch_idx * batch_size
            end = min(start + batch_size, n_cells)
            batch_cells = cells[start:end]

            # Pad input_ids to common length within the batch
            input_ids_list = [list(c["input_ids"]) for c in batch_cells]
            max_len = max(len(seq) for seq in input_ids_list)
            input_ids = torch.full(
                (len(input_ids_list), max_len),
                pad_token_id,
                dtype=torch.long,
            )
            attention_mask = torch.zeros((len(input_ids_list), max_len), dtype=torch.long)
            for i, seq in enumerate(input_ids_list):
                input_ids[i, : len(seq)] = torch.as_tensor(seq, dtype=torch.long)
                attention_mask[i, : len(seq)] = 1

            input_ids = input_ids.to(device)
            attention_mask = attention_mask.to(device)

            # Forward, request hidden states
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True,
                return_dict=True,
            )
            # Last hidden state: (batch, seq_len, hidden_dim)
            last_hidden = outputs.hidden_states[-1]

            # Mean pool excluding special tokens
            non_special_mask = torch.ones_like(input_ids, dtype=torch.float32)
            for excl_id in excluded_ids:
                non_special_mask = non_special_mask * (input_ids != excl_id).float()
            non_special_mask = non_special_mask * attention_mask.float()

            non_special_mask_3d = non_special_mask.unsqueeze(-1)  # (b, s, 1)
            summed = (last_hidden * non_special_mask_3d).sum(dim=1)  # (b, h)
            counts = non_special_mask.sum(dim=1, keepdim=True).clamp(min=1)  # (b, 1)
            pooled = summed / counts  # (b, h)

            embeddings[start:end] = pooled.detach().cpu().float().numpy()

            if progress and (batch_idx + 1) % progress_every == 0:
                print(f"    batch {batch_idx + 1}/{n_batches}")

    if progress:
        print(f"  ✓ embeddings extracted, shape {embeddings.shape}")

    return embeddings


def attach_embeddings_to_anndata(
    embeddings: np.ndarray,
    adata,
    obsm_key: str = "X_geneformer",
):
    """
    Attach extracted embeddings to an AnnData's `.obsm` for downstream use.

    Args:
        embeddings: (n_cells, hidden_dim) float32 array
        adata: AnnData; must have same n_cells as embeddings
        obsm_key: key under which to store the embeddings (default "X_geneformer";
                  use "X_scfoundation" for scFoundation, etc.)

    Returns:
        the AnnData (modified in place AND returned for chaining)
    """
    if embeddings.shape[0] != adata.shape[0]:
        raise ValueError(
            f"Embedding rows ({embeddings.shape[0]}) != adata cells ({adata.shape[0]})"
        )
    adata.obsm[obsm_key] = embeddings
    return adata
