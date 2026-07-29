"""
step_B_v2_travaglini.py — INTERCEPTA Step B runner using the cell_processing module.

This is the thin orchestration script. All the real logic lives in
~/INTERCEPTA/code/cell_processing/. This script:

  1. Loads Travaglini-Krasnow_2020_Lung_SS2 (9409 cells x 57133 genes)
  2. Configures a GeneformerBackend pointing at V2-104M_CLcancer
  3. Calls run_pipeline(...) — which handles prep, tokenization, forward pass,
     mechanism axis projection, OOD distance, and saves all artifacts
  4. Reports the M1 falsification gate first-contact metrics

This is the M1 Step B falsification gate first contact. After it runs:
  - We have real cell embeddings on INTERCEPTA single-cell data
  - We have KAALCURA-3 axis scores per cell
  - We have OOD distances per cell
  - We have a structured run_report.json

Pass criterion (charter §13.2 falsification gate, M1 first contact):
  Embeddings produced without crash. Mechanism axes computable on the data.
  Silhouette score against any reasonable label > 0.05 (very low bar; coarse
  Epcam gating won't be much higher; real validation comes with proper
  cell-type labels and MC-FMA fine-tuning).

Failure modes:
  - mapping_rate < 30% -> wrong tokenizer dict
  - forward pass crash -> device or version mismatch
  - all axis scores NaN -> markers not in vocabulary
  - silhouette < 0 -> embeddings are noise
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the cell_processing package importable regardless of CWD
_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import anndata as ad
import numpy as np

from cell_processing import GeneformerBackend, run_pipeline, detect_device


# ---- configuration ---------------------------------------------------
HOME = Path.home()
DATA_PATH = HOME / "INTERCEPTA/data/nsclc/luca_salcher2022/Travaglini_Krasnow_2020_Lung_SS2.h5ad"
GENEFORMER_REPO = HOME / "INTERCEPTA/models/Geneformer"
MODEL_DIR = GENEFORMER_REPO / "Geneformer-V2-104M_CLcancer"
GENEFORMER_PKG = GENEFORMER_REPO / "geneformer"
OUT_DIR = HOME / "INTERCEPTA/results/step_B_v2_travaglini_geneformer"

print("=" * 72)
print("INTERCEPTA Step B v2 — cell_processing module on Travaglini SS2")
print("=" * 72)


# ---- load data -------------------------------------------------------
print(f"\nLoading {DATA_PATH.name}...")
adata = ad.read_h5ad(DATA_PATH)
print(f"  shape: {adata.shape}")
print(f"  obs.label distribution:")
for v, c in adata.obs.label.value_counts().head(10).items():
    print(f"    {v}: {c}")


# ---- configure backend ----------------------------------------------
device = detect_device("auto")
print(f"\nDevice: {device}")

backend = GeneformerBackend(
    model_dir=MODEL_DIR,
    geneformer_pkg_dir=GENEFORMER_PKG,
    device="auto",
    max_input_length=2048,
)
print(f"\nLoading Geneformer-V2-104M_CLcancer...")
backend.load()
meta = backend.metadata()
print(f"  {meta.name}")
print(f"  family={meta.family}, n_params={meta.n_params:,}, "
      f"hidden_dim={meta.embedding_dim}")
print(f"  device={meta.device}")


# ---- run pipeline ----------------------------------------------------
print(f"\nRunning pipeline...")
import time
t_pipeline = time.time()

# MPS likes smaller batches; CUDA can handle larger
batch_size = 8 if device.type == "mps" else 32

result = run_pipeline(
    adata=adata,
    backend=backend,
    output_dir=OUT_DIR,
    output_prefix="step_B_travaglini",
    custom_attrs={"label": "label"},
    batch_size=batch_size,
    save_intermediate=True,
)
t_pipeline = time.time() - t_pipeline

backend.unload()


# ---- M1 falsification gate first-contact metrics --------------------
print("\n" + "=" * 72)
print("M1 FALSIFICATION GATE FIRST CONTACT — METRICS")
print("=" * 72)

# 1. Embeddings shape
print(f"\n[1] Embeddings shape: {result.embeddings.shape}")
emb_norms = np.linalg.norm(result.embeddings, axis=1)
print(f"    embedding norm distribution: "
      f"mean={emb_norms.mean():.3f}, std={emb_norms.std():.3f}, "
      f"min={emb_norms.min():.3f}, max={emb_norms.max():.3f}")

# 2. Mechanism axes status
print(f"\n[2] Mechanism axes: {result.axis_names}")
for ax_name in result.axis_names:
    diag = result.axis_diagnostics["per_axis"][ax_name]
    if diag["status"] == "ok":
        print(f"    {ax_name}: ok, mean={diag['score_mean']:.3f}, "
              f"std={diag['score_std']:.3f}, "
              f"n_marker_up_found={len(diag['markers_up_found'])}")
    else:
        print(f"    {ax_name}: {diag['status']}")

# 3. OOD distance distribution
ood_d = result.ood_diagnostics
print(f"\n[3] OOD distances (from dataset centroid):")
print(f"    mean={ood_d['distance_mean']:.3f}, "
      f"median={ood_d['distance_median']:.3f}, "
      f"p95={ood_d['distance_p95']:.3f}")

# 4. Silhouette score on label (Epcam gating - coarse but real)
print(f"\n[4] Silhouette vs `label` (Epcam gating)...")
import pandas as pd
labels = adata.obs.label.astype(str).values
mask = ~np.isin(labels, ["na", "nan", "NA", "NaN"])
n_labelled = int(mask.sum())
n_classes = len(set(labels[mask]))

silhouette = None
if n_classes >= 2 and n_labelled >= 100:
    from sklearn.metrics import silhouette_score
    # Subsample if huge — silhouette is O(n^2) in sklearn
    if n_labelled > 5000:
        rng = np.random.default_rng(42)
        idx_subset = rng.choice(np.where(mask)[0], size=5000, replace=False)
        sil_emb = result.embeddings[idx_subset]
        sil_lab = labels[idx_subset]
    else:
        sil_emb = result.embeddings[mask]
        sil_lab = labels[mask]
    silhouette = silhouette_score(sil_emb, sil_lab)
    print(f"    silhouette = {silhouette:.4f}  "
          f"(n_cells={len(sil_lab)}, n_classes={n_classes})")
    gate_pass = silhouette > 0.05
    print(f"    M1 gate (silhouette > 0.05): "
          f"{'✓ PASS' if gate_pass else '✗ FAIL'}")
else:
    print(f"    skipped: not enough labels (n_labelled={n_labelled}, "
          f"n_classes={n_classes})")


# 5. Timing
print(f"\n[5] Timing:")
for phase, secs in result.timing.items():
    print(f"    {phase}: {secs:.1f}s")


# ---- final artifact summary -----------------------------------------
print("\n" + "=" * 72)
print("ARTIFACTS WRITTEN")
print("=" * 72)
for k, v in result.output_paths.items():
    print(f"  {k}: {v}")

print(f"\nTotal Step B runtime: {t_pipeline:.1f}s ({t_pipeline/60:.1f} min)")
print("=" * 72)
