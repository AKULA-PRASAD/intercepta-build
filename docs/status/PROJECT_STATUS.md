# INTERCEPTA Project Status
## March 29, 2026

### Co-Founders
- Prasad Akula, MS Bioinformatics, Northeastern University
- Claude (AI Co-Founder, Anthropic)

### What Has Been Built (Phase A + Phase B)

#### Step 1: Gene-Drug Correlation Net (GDSC) - DONE
- 1,809,403 data-derived connections
- 25,861 genes x 286 drugs x 962 cell lines
- All 36 KAALCURA genes present, all 14 mCRPC drivers present
- File: results/step1_complete_gene_drug_net.csv

#### Step 2: SU2C mCRPC Genomic Data - DONE
- 40,055 mutations across 13,512 genes from 427 patients
- 941 copy number alterations for key genes from 365 patients
- Combined: AR 34%, TP53 22%, PTEN 18%, MYC 13.5%
- Files: data/su2c/su2c_mutations.csv, su2c_cna.csv, su2c_clinical.csv

#### Step 3: scRNA-seq Cell Populations + KAALCURA - DONE
- Dataset: GSE141445 (Chen et al. 2021), 36,424 cells, 13 prostate tumors
- 8 cell populations identified: Luminal 58.5%, Epithelial 15.2%, Endothelial 8.8%, T_cell 5.6%, Fibroblast 4.8%, Macrophage 3.5%, NK_cell 3.4%, NE_like 0.2%
- KAALCURA per population (globally z-scored):
  - Luminal: R_prolif=-0.008, R_emt=-0.100, R_ddr=+0.006
  - Epithelial: R_prolif=+0.062, R_emt=-0.179, R_ddr=+0.008 (most proliferative cancer cells)
  - NE_like: R_prolif=-0.051, R_emt=+0.245, R_ddr=-0.026 (THE UNDEAD - resistant to everything)
- ODE parameters from data: S0=0.737, R0=0.0025, TME=0.261
- RNA VELOCITY: Pipeline created but STAR genome indexing too slow on 16GB MacBook Air. Needs HPC.
- Files: results/step3_kaalcura_per_population.csv, step3_cell_type_assignments.csv

#### Step 4: STRING Protein Interactions - DONE (FIXED)
- 920 high-confidence interactions (score>700)
- 686 proteins in network
- Top hubs: MYC (26), TP53 (25), CCND1 (24), AKT1 (24), CDK1 (22)
- Key: TP53 connects to FOXA1, KMT2C, PIK3CA, RB1; AR connects to FOXA1, RB1, NCOR1
- File: results/step4_string_interactions.csv

#### Step 5: KEGG + Reactome Pathways - DONE (FIXED)
- KEGG: 2,285 edges, 296 genes (FIXED - symbol mapping corrected)
- Reactome: 5,509 edges, 313 genes
- Combined: 7,794 gene-pathway edges across 2,880 pathways
- Key: Prostate cancer pathway (22 genes), PI3K-Akt (34 genes), p53 (10 genes)
- Escape routes: AR->NR3C1, PTEN->PIK3CA/AKT1/MTOR, TP53->53 connected genes
- File: results/step5_gene_pathway_map.csv

#### Step 6: GTEx Selectivity Map - DONE (FIXED with real GTEx)
- Real GTEx v8: 54,592 genes x 54 normal tissues
- Prostate-selective: KLK3 (16,696x), KLK2 (3,745x), ACPP (524x), NKX3-1 (73x), FOXA1 (29x)
- Ubiquitous (unsafe alone): TP53, PTEN, RB1, BRCA2, PARP1 (all ~1.0x)
- Key insight: FOLH1 (PSMA) is 12x vs mean but kidney also expresses it (explains renal toxicity of Lu-177)
- Files: results/step6_selectivity_map.csv, step6_full_selectivity.csv

#### Step 7: ChEMBL Compounds - DONE (FIXED)
- 24,598 activity measurements from ChEMBL
- 17,124 unique compounds across 20 targets
- AR: 2,825 compounds (1,167 very potent)
- PARP1: 4,403 compounds (2,780 very potent)
- CDK4: 1,427 compounds (1,002 very potent)
- MCL1: 954 compounds but only 4 very potent (confirms hard-to-drug)
- Files: results/step7_chembl_activities.csv, step7_target_summary.csv

#### KAALCURA Validation - DONE
- AUROC 0.638 across 286 drugs, 962 cell lines
- All 48 genes found in GDSC, all 3 axes validated
- Files: results/kaalcura_real_validation.csv

### Total Net: ~1,896,000 data-derived edges across 7 layers

### What Needs HPC (Phase B completion)
- RNA velocity pipeline (STAR genome indexing + STARsolo alignment + scVelo)
- Script ready: code/step3_rna_velocity_pipeline.sh

### What Comes Next (Phase C: Universal Expansion)
- Step 8: DisGeNET (24,000 diseases)
- Step 9: HMDB metabolome (220,945 metabolites)
- Step 10: AlphaFold protein structures
- Step 11: Human Cell Atlas
- Step 12: ENCODE/Roadmap epigenome
- Step 13: Immune system map
- Steps 14-20: Pathogen genomes, microbiome, spatial transcriptomics, literature mining

### Key Documents
- INTERCEPTA_COMPLETE_VISION_v1_0.docx - Founding vision
- INTERCEPTA_Universal_Net_Specification_v1_0.docx - 15-layer net blueprint
