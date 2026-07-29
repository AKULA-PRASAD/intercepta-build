#!/usr/bin/env python
"""
step_B_travaglini_geneformer_mac.py

Real CSO Step B — first foundation-model cell embeddings on INTERCEPTA single-cell data.

Inputs:
    Travaglini_Krasnow_2020_Lung_SS2.h5ad  (9409 cells, 57133 gene symbols)
    Geneformer-V2-104M_CLcancer             (cancer-pretrained 104M-param FM)

Pipeline:
    1. Load AnnData
    2. Tokenize via Geneformer's TranscriptomeTokenizer (handles symbol->Ensembl->token_id,
       rank-based per-cell encoding — Geneformer's canonical input format)
    3. Forward through Geneformer-V2-104M_CLcancer on MPS (Apple Silicon GPU)
    4. Extract [CLS] cell embeddings via Geneformer's EmbExtractor
    5. UMAP via scanpy
    6. Silhouette score against `label` column (Epcam gating — coarse but real)
    7. Save embeddings, UMAP coords, plot to ~/INTERCEPTA/results/step_B_travaglini_geneformer/

This is the M1 falsification gate first contact — checks whether Geneformer produces
sensible embeddings on real INTERCEPTA data (cells separate by biology, not artifacts).
Pass criterion: silhouette > 0.05 (extremely low bar — coarse gating won't yield much
better; we just want to verify embeddings aren't garbage). Real validation comes later
with proper cell type annotations.

Runtime: ~10-30 min on M-series Mac.
"""

from __future__ import annotations

import os
import sys
import time
import shutil
import pickle
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import numpy as np
import pandas as pd
import torch
import anndata as ad
import scanpy as sc

# --------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------
HOME = Path.home()
DATA_PATH = HOME / "INTERCEPTA/data/nsclc/luca_salcher2022/Travaglini_Krasnow_2020_Lung_SS2.h5ad"
GENEFORMER_REPO = HOME / "INTERCEPTA/models/Geneformer"
MODEL_DIR = GENEFORMER_REPO / "Geneformer-V2-104M_CLcancer"

# Geneformer tokenizer dictionaries (the gc104M variants for V2-104M models)
GENEFORMER_PKG = GENEFORMER_REPO / "geneformer"
TOKEN_DICT_PATH = GENEFORMER_PKG / "token_dictionary_gc104M.pkl"
GENE_MEDIAN_PATH = GENEFORMER_PKG / "gene_median_dictionary_gc104M.pkl"
ENSEMBL_MAPPING_PATH = GENEFORMER_PKG / "ensembl_mapping_dict_gc104M.pkl"
GENE_NAME_ID_PATH = GENEFORMER_PKG / "gene_name_id_dict_gc104M.pkl"

OUT_DIR = HOME / "INTERCEPTA/results/step_B_travaglini_geneformer"
TOKENIZED_DIR = OUT_DIR / "tokenized"
TOKENIZED_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------
# Banner
# --------------------------------------------------------------------
print("=" * 70)
print("INTERCEPTA Step B — Geneformer embeddings on Travaglini SS2")
print("=" * 70)
t_start = time.time()

# --------------------------------------------------------------------
# Phase 1: Sanity check files
# --------------------------------------------------------------------
print("\nPhase 1: file checks")
for label, path in [
    ("Data h5ad", DATA_PATH),
    ("Geneformer repo", GENEFORMER_REPO),
    ("V2-104M_CLcancer dir", MODEL_DIR),
    ("token_dictionary", TOKEN_DICT_PATH),
    ("gene_median", GENE_MEDIAN_PATH),
    ("ensembl_mapping", ENSEMBL_MAPPING_PATH),
    ("gene_name_id", GENE_NAME_ID_PATH),
]:
    exists = path.exists()
    sym = "✓" if exists else "✗"
    print(f"  {sym} {label}: {path}")
    if not exists:
        print(f"\nFATAL: missing required file: {path}")
        sys.exit(1)

# Verify model has actual weights, not just LFS pointers
sft = MODEL_DIR / "model.safetensors"
if sft.exists():
    sft_size = sft.stat().st_size
    print(f"  model.safetensors size: {sft_size / 1e6:.1f} MB")
    if sft_size < 100_000_000:
        print(f"FATAL: model.safetensors is too small — likely LFS pointer not pulled")
        sys.exit(1)

# --------------------------------------------------------------------
# Phase 2: Device selection
# --------------------------------------------------------------------
print("\nPhase 2: torch device")
if torch.backends.mps.is_available():
    device = torch.device("mps")
    print(f"  ✓ MPS available — using Apple Silicon GPU")
elif torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"  ✓ CUDA available — using NVIDIA GPU")
else:
    device = torch.device("cpu")
    print(f"  ⚠  No GPU — falling back to CPU (slow)")
print(f"  torch: {torch.__version__}  device: {device}")

# --------------------------------------------------------------------
# Phase 3: Inspect input AnnData
# --------------------------------------------------------------------
print("\nPhase 3: inspect input data")
adata = ad.read_h5ad(DATA_PATH)
print(f"  Shape: {adata.shape}")
print(f"  X dtype: {adata.X.dtype}, sparse: {hasattr(adata.X, 'toarray')}")
print(f"  obs columns: {list(adata.obs.columns)}")
print(f"  First 5 var (gene symbols): {list(adata.var.index[:5])}")
print(f"  label distribution:")
for v, c in adata.obs.label.value_counts().head(10).items():
    print(f"    {v}: {c}")

# --------------------------------------------------------------------
# Phase 4: Prepare AnnData for Geneformer tokenization
# --------------------------------------------------------------------
# Geneformer's TranscriptomeTokenizer expects:
#   - .var index = Ensembl IDs (column name "ensembl_id" by default)
#   - .obs containing required metadata + custom_attr_name_dict mapping
#   - X as raw integer counts (which we have)
#
# Travaglini var index = HGNC symbols. We need to map symbols -> Ensembl IDs
# using the gc104M gene_name_id dictionary that ships with the Geneformer package.
print("\nPhase 4: map gene symbols -> Ensembl IDs")

with open(GENE_NAME_ID_PATH, "rb") as f:
    gene_name_id = pickle.load(f)
print(f"  gene_name_id_dict has {len(gene_name_id)} symbol->Ensembl mappings")

symbols = adata.var.index.astype(str).tolist()
ensembl_ids = [gene_name_id.get(s, None) for s in symbols]
n_mapped = sum(1 for e in ensembl_ids if e is not None)
print(f"  symbols mapped: {n_mapped} / {len(symbols)} ({100*n_mapped/len(symbols):.1f}%)")

if n_mapped < 1000:
    print("FATAL: too few symbols mapped — tokenization would fail")
    sys.exit(1)

# Filter to mapped genes only and assign ensembl_id column
mapped_mask = np.array([e is not None for e in ensembl_ids])
adata = adata[:, mapped_mask].copy()
adata.var["ensembl_id"] = [gene_name_id[s] for s in adata.var.index]
print(f"  filtered to {adata.shape[1]} genes with Ensembl IDs")

# Geneformer requires `n_counts` per cell in obs (raw library size)
if "n_counts" not in adata.obs.columns:
    if hasattr(adata.X, "sum"):
        n_counts = np.asarray(adata.X.sum(axis=1)).flatten()
    else:
        n_counts = adata.X.sum(axis=1)
    adata.obs["n_counts"] = n_counts.astype(np.int64)
print(f"  added n_counts (median: {int(np.median(adata.obs.n_counts))})")

# Save prepared AnnData for the tokenizer
prepared_h5ad = TOKENIZED_DIR / "travaglini_ss2_prepared.h5ad"
adata.write_h5ad(prepared_h5ad)
print(f"  wrote prepared h5ad: {prepared_h5ad}")

# --------------------------------------------------------------------
# Phase 5: Tokenize via Geneformer's TranscriptomeTokenizer
# --------------------------------------------------------------------
print("\nPhase 5: tokenize for Geneformer")
from geneformer import TranscriptomeTokenizer

# We pass label so it ends up in cell_metadata. The tokenizer also requires n_counts.
tk = TranscriptomeTokenizer(
    custom_attr_name_dict={"label": "label"},  # carry label column through
    nproc=4,
    chunk_size=512,
    model_input_size=2048,
    special_token=True,
    collapse_gene_ids=True,
    gene_median_file=str(GENE_MEDIAN_PATH),
    token_dictionary_file=str(TOKEN_DICT_PATH),
    gene_mapping_file=str(ENSEMBL_MAPPING_PATH),
)

tokenized_out_prefix = "travaglini_tokenized"
# tokenize_data takes a directory of h5ads + writes a HuggingFace .dataset
tk.tokenize_data(
    data_directory=str(TOKENIZED_DIR),
    output_directory=str(TOKENIZED_DIR),
    output_prefix=tokenized_out_prefix,
    file_format="h5ad",
)
tokenized_dataset_path = TOKENIZED_DIR / f"{tokenized_out_prefix}.dataset"
print(f"  tokenized dataset at: {tokenized_dataset_path}")

# --------------------------------------------------------------------
# Phase 6: Extract embeddings via Geneformer's EmbExtractor
# --------------------------------------------------------------------
print("\nPhase 6: extract cell embeddings (this is the actual FM forward pass)")
from geneformer import EmbExtractor

emb_dir = OUT_DIR / "embeddings"
emb_dir.mkdir(exist_ok=True)

# EmbExtractor signature varies by Geneformer version — try v0.1 API
# It writes embeddings to a CSV by default
embex = EmbExtractor(
    model_type="Pretrained",
    num_classes=0,          # zero-shot embedding extraction (no fine-tuning head)
    emb_mode="cell",        # cell-level [CLS] embeddings
    cell_emb_style="mean_pool",
    filter_data=None,
    max_ncells=None,        # use all cells
    emb_layer=-1,           # last hidden layer
    emb_label=["label"],    # carry label through to output
    labels_to_plot=["label"],
    forward_batch_size=16 if device.type == "mps" else 32,
    nproc=4,
    token_dictionary_file=str(TOKEN_DICT_PATH),
)

# Force MPS via env (Geneformer doesn't expose device arg on extractor)
if device.type == "mps":
    os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

t0 = time.time()
embs = embex.extract_embs(
    model_directory=str(MODEL_DIR),
    input_data_file=str(tokenized_dataset_path),
    output_directory=str(emb_dir),
    output_prefix="travaglini_geneformer",
)
t_emb = time.time() - t0
print(f"  embedding extraction took {t_emb:.1f}s")
print(f"  embeddings type: {type(embs)}")
if hasattr(embs, "shape"):
    print(f"  embeddings shape: {embs.shape}")

# --------------------------------------------------------------------
# Phase 7: load embeddings, run UMAP, compute silhouette
# --------------------------------------------------------------------
print("\nPhase 7: UMAP + silhouette")

# EmbExtractor saves CSV with rows=cells, cols=embedding_dims + label cols
csv_candidates = list(emb_dir.glob("*.csv"))
print(f"  CSV files in emb_dir: {[p.name for p in csv_candidates]}")

if csv_candidates:
    emb_csv = csv_candidates[0]
    emb_df = pd.read_csv(emb_csv)
    print(f"  loaded emb CSV: {emb_df.shape}")
    print(f"  columns sample: {list(emb_df.columns[:5])} ... {list(emb_df.columns[-3:])}")

    # Separate embeddings from metadata
    label_col = "label" if "label" in emb_df.columns else None
    if label_col:
        labels = emb_df[label_col].values
        emb_matrix = emb_df.drop(columns=[label_col]).select_dtypes(include=[np.number]).values
    else:
        labels = None
        emb_matrix = emb_df.select_dtypes(include=[np.number]).values

    print(f"  emb_matrix shape: {emb_matrix.shape}")

    # UMAP via scanpy
    emb_adata = ad.AnnData(X=emb_matrix)
    if labels is not None:
        emb_adata.obs["label"] = pd.Categorical(labels)
    sc.pp.neighbors(emb_adata, n_neighbors=15, use_rep="X")
    sc.tl.umap(emb_adata)
    emb_adata.write_h5ad(OUT_DIR / "travaglini_geneformer_embeddings.h5ad")
    print(f"  saved embeddings AnnData: {OUT_DIR / 'travaglini_geneformer_embeddings.h5ad'}")

    # Silhouette
    if labels is not None and len(set(labels)) > 1:
        from sklearn.metrics import silhouette_score
        # filter out nan/na labels
        mask = pd.Series(labels).astype(str).isin(["na", "nan", "NA", "NaN"])
        if mask.sum() < len(labels):
            keep = ~mask.values
            sil = silhouette_score(emb_matrix[keep], pd.Series(labels)[keep])
            print(f"\n  ★ Silhouette (label gating, n={keep.sum()}): {sil:.4f}")
            with open(OUT_DIR / "metrics.txt", "w") as f:
                f.write(f"silhouette_label\t{sil:.6f}\n")
                f.write(f"n_cells_used\t{keep.sum()}\n")
                f.write(f"n_emb_dim\t{emb_matrix.shape[1]}\n")
                f.write(f"emb_extraction_seconds\t{t_emb:.2f}\n")

    # UMAP plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        sc.pl.umap(emb_adata, color="label" if labels is not None else None,
                   save="_step_B_travaglini.png", show=False)
        # scanpy saves to ./figures/ by default; move to OUT_DIR
        fig_src = Path("figures/umap_step_B_travaglini.png")
        if fig_src.exists():
            shutil.copy(fig_src, OUT_DIR / "umap_step_B_travaglini.png")
            print(f"  saved UMAP plot: {OUT_DIR / 'umap_step_B_travaglini.png'}")
    except Exception as e:
        print(f"  (plot save skipped: {e})")
else:
    print("  ⚠  no CSV embeddings found in emb_dir — check EmbExtractor output")

# --------------------------------------------------------------------
# Done
# --------------------------------------------------------------------
t_total = time.time() - t_start
print(f"\n{'=' * 70}")
print(f"Step B complete in {t_total/60:.1f} min")
print(f"  Outputs in: {OUT_DIR}")
for p in sorted(OUT_DIR.iterdir()):
    if p.is_file():
        sz = p.stat().st_size
        print(f"    {p.name}: {sz/1024:.1f} KB" if sz < 1e6 else f"    {p.name}: {sz/1e6:.1f} MB")
    elif p.is_dir():
        n = len(list(p.iterdir()))
        print(f"    {p.name}/  ({n} items)")
print("=" * 70)
