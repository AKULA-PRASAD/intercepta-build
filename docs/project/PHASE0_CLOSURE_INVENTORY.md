# INTERCEPTA Workstream B Phase 0 Closure Inventory

**Generated:** Fri May  8 08:25:59 PM EDT 2026
**Specs:** workstream-b-spec-locked + workstream-b-spec-erratum-luca

## Cohorts downloaded

### LuCA Salcher 2022 (primary scRNA atlas)
- Source: Zenodo 7227571
- Files: 33 h5ad (29 source studies + harmonized atlas)
- Size: 76 GB
- Core atlas: full_atlas_hvg_integrated_scvi_integrated_scanvi.h5ad
  - Shape: 892,296 cells × 6,000 HVGs
  - 36 obs columns including sample, patient, dataset, condition, cell_type, driver_genes, ever_smoker, uicc_stage, age, sex, tissue, origin, pct_counts_mito
  - First sample: Adams_Kaminski_2020_001C (29-study harmonization confirmed)
- Load time: 14.7s in backed mode on compute node
- Status: COMPLETE & VERIFIED

### Wu 2021 (independent validation scRNA)
- Source: GEO GSE148071
- Files: 42 per-patient .exp.txt.gz
- Size: 344 MB
- Status: COMPLETE

### TCGA-LUAD (bulk RNA-seq + mutations + clinical)
- Source: GDC API + gdc-client (manifest format: return_type=manifest)
- RNA-seq: 601 STAR-Counts files (2.4 GB)
- Mutations: 618 Masked Somatic Mutation files (60 MB)
- Clinical: 1146 files (298 MB)
- Status: COMPLETE

### TCGA-LUSC (bulk RNA-seq + mutations + clinical)
- Source: GDC API + gdc-client
- RNA-seq: 562 STAR-Counts files (2.3 GB)
- Mutations: 549 Masked Somatic Mutation files (54 MB)
- Clinical: 1081 files (193 MB)
- Status: COMPLETE

## Infrastructure verified

- Conda env: /scratch/akula.pra/INTERCEPTA/envs/intercepta-nsclc
  - scanpy 1.11.5, anndata 0.12.13, numba 0.65.1
  - lightgbm 4.6.0, scikit-learn 1.8.0, scipy 1.17.1
  - Activates correctly via full path
  - Requires PYTHONNOUSERSITE=1 to suppress ~/.local shadow
- LuCA load test executed on compute node (job 6672975): PASSED in 14.7s

## Lessons captured

1. GDC API requires return_type=manifest parameter for gdc-client compatibility — earlier awk-based conversion produced "Invalid manifest" errors that gdc-client silently exited on
2. Login nodes OOM-kill scanpy import — all heavy data work runs on compute nodes via slurm
3. ~/.local user-installed packages shadow conda env — must use PYTHONNOUSERSITE=1
4. LuCA core atlas uses 6000 HVGs (not full 30K gene set) — Phase 1 scoring may need to expand to full gene set if KAALCURA target genes are missing
5. LuCA integrated h5ad has scVI labels in obs (_scvi_labels) and presumably scVI latent in obsm — usable for cross-cohort transfer

## Total: 4 cohorts, ~80 GB on HPC scratch, 0 download failures
