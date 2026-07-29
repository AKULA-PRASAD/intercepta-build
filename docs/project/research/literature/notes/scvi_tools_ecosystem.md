# Q9 anchor 2 — scvi-tools and Python ecosystem deployment

## 0. Identification
- **scvi-tools** (Gayoso 2022 Nat Biotechnol 40:163-166) — primary Python framework for Decision 2 + 4
- **Scanpy** (Wolf 2018 Genome Biology) — scRNA-seq analysis workhorse
- **AnnData** — standardized data format
- **PyTorch Lightning** — training infrastructure (used by scvi-tools)
- **Layer 1 question:** Q9 anchor 2 — deployment ecosystem

## 1. Why this composite anchor

INTERCEPTA's Decisions 2 (scANVI/MrVI), 4 (CPA), 5 (Deep Ensembles), 6 (validation) all depend on the Python scientific computing stack. **Q9 must verify ecosystem stability + production readiness.**

## 2. Ecosystem status (2026)

- **scvi-tools 1.4+** — actively maintained by Yosef lab (UC Berkeley) + community
- **Scanpy 1.10+** — workhorse for scRNA-seq analysis
- **AnnData** — stable spec; HDF5-backed; scales to ~10^7 cells
- **PyTorch Lightning** — training abstraction layer
- **R bridge via reticulate** — needed for Seurat v3 multi-modal (Decision 2)
- **Hugging Face Hub** — distribution channel for FMs (scGPT, scFoundation distributed here)

## 3. Production deployment considerations

- **Version locking** — scvi-tools rapid evolution requires fixed versions for reproducibility
- **GPU memory management** — VAE training + FM inference need careful batching
- **Storage** — embedding caches need ~10GB-100GB depending on dataset scale
- **Workflow management** — Snakemake (used by scIB) or Nextflow for pipelines

## 4. INTERCEPTA implications

**For Q9 deployment architecture:**
- Python primary, R secondary (via reticulate for Seurat v3)
- scvi-tools as primary VAE framework
- Hugging Face Hub for FM weights
- Snakemake pipelines for reproducibility (scIB-style)
- AnnData as canonical data format
- /scratch storage on Northeastern Explorer

This **does NOT require novel infrastructure** — INTERCEPTA can be built on existing community tools.

— Claude (CSO), 2026-05-10
