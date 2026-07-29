# Q9 anchor 3 — Data infrastructure for INTERCEPTA scale

## 0. Identification (composite)

Required data infrastructure based on Decisions 1-8:
- **CCLE bulk RNA-seq** (1072 cell lines): ~5 GB total
- **GDSC drug response labels**: ~1 GB
- **sci-Plex single-cell perturbation** (~650K cells): ~50 GB
- **Tahoe-100M** (recent large-scale 2025 dataset): ~500 GB
- **Disease-specific scRNA-seq atlases** (per disease class): ~10-100 GB each
- **FM weights** (scFoundation 100M params + UCE + scGPT + Geneformer): ~10-50 GB total
- **Embedding caches** (pre-computed FM outputs for major datasets): ~50-200 GB
- **Experimental results** (cross-disease grid, multiple validation levels): ~100 GB

**Total INTERCEPTA storage budget: ~1-2 TB on /scratch**

## 1. Why this matters for Q9

Northeastern Explorer /scratch typically provides multi-TB quotas. **INTERCEPTA's storage footprint is feasible** on single-institution HPC.

## 2. Data pipeline architecture

1. Raw data ingestion: GEO/ENA/cBioPortal for atlases; CCLE+GDSC from DepMap; sci-Plex from authors
2. Preprocessing: scanpy/scvi-tools standardized pipeline
3. FM embedding pre-computation: cached as Zarr/HDF5
4. Decision 2 cohort harmonization: scANVI/MrVI on FM embeddings
5. Decision 3 Q3 bridge: trained per scenario
6. Decision 4 prediction: CPA + GEARS extended
7. Decision 5 OOD: ensemble + conformal
8. Decision 6 validation: hierarchical cascade
9. Decision 7 interpretability: post-hoc on all predictions
10. Decision 8 universality: cross-disease grid over all above

## 3. INTERCEPTA implications

**For Q9:** Data infrastructure is straightforward. **No barriers identified.**

— Claude (CSO), 2026-05-10
