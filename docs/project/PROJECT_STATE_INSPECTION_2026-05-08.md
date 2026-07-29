# INTERCEPTA Project State Inspection

**Path:** `/Users/kalki/INTERCEPTA`
**Date:** Fri May  8 21:33:05 EDT 2026

---

## 1. Top-level directory structure

```
drwxr-xr-x   45 kalki  staff    1440 May  8 21:02 .
drwxr-x---+  54 kalki  staff    1728 May  8 21:17 ..
-rw-r--r--@   1 kalki  staff   10244 May  6 02:24 .DS_Store
drwxr-xr-x   15 kalki  staff     480 May  8 21:02 .git
-rw-r--r--    1 kalki  staff     876 May  8 21:02 .gitignore
-rw-r--r--    1 kalki  staff     893 Apr  8 14:07 AUDIT_ACTION_PLAN.md
-rw-r--r--@   1 kalki  staff    6923 Apr 18 23:19 CLAUDE.md
drwxr-xr-x   86 kalki  staff    2752 May  8 21:02 code
drwxr-xr-x   10 kalki  staff     320 May  8 08:02 configs
drwxr-xr-x   25 kalki  staff     800 May  8 21:02 data
drwxr-xr-x   29 kalki  staff     928 May  8 21:33 docs
-rw-r--r--    1 kalki  staff   19793 Apr 21 12:23 EXHAUSTIVE_AUDIT.txt
-rw-r--r--    1 kalki  staff   17738 Apr 18 23:27 intercepta_100_results.txt
-rw-r--r--@   1 kalki  staff   66031 Apr 18 23:26 intercepta_100_test.py
-rw-r--r--    1 kalki  staff    4178 Apr 19 10:07 intercepta_2000x_test_system.py
-rw-r--r--@   1 kalki  staff   39436 Apr 18 23:17 intercepta_44_test.py
-rw-r--r--@   1 kalki  staff   68946 Apr 19 09:19 intercepta_part1_test.py
-rw-r--r--@   1 kalki  staff   80906 Apr 19 09:29 intercepta_part2_test.py
-rw-r--r--@   1 kalki  staff   44479 Apr 19 09:34 intercepta_part3_test.py
-rw-r--r--@   1 kalki  staff  101896 Apr 19 09:46 intercepta_part4_test.py
-rw-r--r--@   1 kalki  staff   47982 Apr 19 18:07 intercepta_part5_test.py
-rw-r--r--@   1 kalki  staff   57043 Apr 20 22:27 intercepta_part6_test.py
-rw-r--r--    1 kalki  staff    1822 Apr 18 23:00 INTERCEPTA_STATUS.md
-rw-r--r--    1 kalki  staff    3264 Apr 20 22:40 kaalcura_revalidate_results.txt
-rw-r--r--@   1 kalki  staff    8537 Apr 18 21:39 MASTER_FIXES.md
-rw-r--r--    1 kalki  staff    1500 Apr  8 12:50 NEXT_SESSION.md
-rw-r--r--    1 kalki  staff   18955 Apr 19 09:21 part1_results.txt
-rw-r--r--    1 kalki  staff    4957 Apr 19 09:29 part2_results.txt
-rw-r--r--    1 kalki  staff   13973 Apr 19 09:35 part3_results.txt
-rw-r--r--    1 kalki  staff   19231 Apr 19 09:46 part4_results.txt
-rw-r--r--    1 kalki  staff   14252 Apr 19 18:10 part5_results.txt
-rw-r--r--    1 kalki  staff   17193 Apr 20 22:44 part6_results.txt
-rw-r--r--    1 kalki  staff   11909 Apr 21 12:55 PRE_REBUILD_AUDIT.txt
-rw-r--r--    1 kalki  staff    4079 Mar 29 16:08 PROJECT_STATUS.md
-rw-r--r--    1 kalki  staff    3081 Apr  8 09:14 PUBLICATION_OUTLINE.md
-rw-r--r--    1 kalki  staff    4983 Mar 14 07:40 README.md
-rw-r--r--    1 kalki  staff     414 Mar 14 07:39 requirements.txt
drwxr-xr-x  178 kalki  staff    5696 May  8 17:08 results
drwxr-xr-x    6 kalki  staff     192 Apr 21 21:43 round2_aml
drwxr-xr-x   12 kalki  staff     384 May  8 21:02 round3_gbm_live_test
drwxr-xr-x    3 kalki  staff      96 Mar 29 08:29 scripts
-rwxr-xr-x    1 kalki  staff    2543 Mar 29 16:08 setup_hpc.sh
-rw-r--r--    1 kalki  staff    3547 Mar 14 07:40 setup_mac.sh
drwxr-xr-x    2 kalki  staff      64 Mar 29 08:29 src
-rw-r--r--    1 kalki  staff   21977 Apr 21 12:30 VISION_AUDIT.txt
```

## 2. Project size and file counts

**Total project size:** 13G

**Files by type:**

```
  .py files:             112
  .json files:           120
  .md files:              42
  .csv files:            112
  .tsv files:             11
  .txt files:             81
  .slurm files:            4
  .h5ad files:             1
  .pdf files:              1
  .docx files:            10
```

## 3. Subdirectory sizes

```
  8.2G       data/
  3.0G       round2_aml/
  265M       results/
  29M        round3_gbm_live_test/
  1.8M       code/
  728K       docs/
  60K        scripts/
  32K        configs/
  0B         src/
```

## 4. Git state

```
Branch: main
HEAD: e3cac92
Origin: https://github.com/AKULA-PRASAD/kaalcura.git

Sync state with origin/main:
  Ahead:  0 commits
  Behind: 0 commits

Working tree status:
?? docs/PROJECT_STATE_INSPECTION_2026-05-08.md

Total uncommitted changes:        1
```

## 5. Last 15 commits

```
e3cac92 hygiene: comprehensive .gitignore + recover unrecorded scientific work
c7035c2 phase0(workstream-b): closure — 4 cohorts downloaded, env verified, atlas loadable
26e0c4c test(T1-Lite): reproducibility PASS for 4 disease selectivity outputs
45cd85d docs: lock comprehensive test plan (5 categories, priority ordering, anti-scope-creep)
e3e3f28 Workstream B spec erratum — cohort design amended to LuCA + Wu (2-cohort scRNA). Phase 0 inventory caught: (1) Lambrechts 2018 Rds-only, not Python-readable; (2) Kim 2020 + Laughney 2020 are already in Salcher LuCA's 29 source studies, so using them separately would double-count cells in cross-cohort analyses. Bounded search per termination contract found Salcher LuCA 2022 (Cancer Cell, doi:10.1016/j.ccell.2022.10.008) - 1.2M cells, 309 patients, 29 harmonized studies, scanpy-native h5ad on cellxgene + Zenodo. Meets all 6 required criteria. Wu 2021 retained as INDEPENDENT validation cohort (not in LuCA source list). Amended H2/H4 thresholds STRICTER than original (require PASS in both cohorts, not 2-of-3). Original 4-cohort design had hidden statistical-independence flaw the erratum exposes. Tier A guaranteed unchanged. Anti-scope-creep still binding.
cb7d65b Workstream B Phase 0 — NSCLC selectivity layer integrated. configs/genes_nsclc.json (33 genes from Open Targets disease net top + LUSC-specific FGFR1/SOX2/NFE2L2 + LUAD drivers EGFR/KRAS/ALK/ROS1/MET/BRAF/RET/NTRK1-3 + immune checkpoints CD274/PDCD1). disease_tissue_mapping.json schema_version 1.2 with NSCLC active (Lung primary tissue, single_tissue strategy). GTEx audit verified 16/16 tissues exact match. step6_selectivity_v2.py produces NSCLC selectivity output: ROS1 selectivity_vs_mean=83 (HIGHLY_SELECTIVE matching biology - ROS1 fusions are NSCLC drug target), CD274/PDCD1 elevated (immune checkpoint expression in lung), FLT4/KDR elevated (angiogenesis targets). KLK3=16696 mCRPC regression preserved. All 4 diseases (mCRPC/AML/GBM/NSCLC) now produce disease-aware selectivity CSVs. AML/GBM/mCRPC JSONs re-emitted today with same numerical values, only computed timestamps updated.
6ee0076 Workstream B Phase 0 prep: HPC env created and ready for downloads. Conda env intercepta-nsclc created at /scratch/akula.pra/INTERCEPTA/envs/intercepta-nsclc with full scientific Python stack (scanpy 1.11.5, anndata 0.12.13, lightgbm 4.6.0, pandas 2.3.3, numpy 2.4.4, scipy 1.17.1, scikit-learn 1.8.0, h5py 3.16.0, pyarrow 24.0.0). 48 packages, all imports verified. 6 dataset directories created on HPC scratch. Phase 0 entry conditions all cleared. Issues documented: home dir quota required scratch envs, login node OOM required compute node for installs, SSH drops require slurm batch jobs for long ops. Phase 0 implementation (downloads + processing) deferred to next session.
ec50724 Workstream B (NSCLC) specification LOCKED. Multi-cohort design with 6 datasets (TCGA-LUAD + TCGA-LUSC + Kim 2020 + Lambrechts 2018 + Laughney 2020 + Wu 2021). Both LUAD and LUSC subtypes. 6 falsifiable hypotheses (H1 cell-type Jaccard, H2 cross-cohort Spearman, H3 multi-modal AUROC, H4 high-confidence drug set, H5 subtype distinguishability, H6 KAALCURA contribution analog). Binding anti-scope-creep clauses across 8 scenarios. 5-phase plan estimated 40-60 hours active coding across 6-7 sessions. Tier A guaranteed deliverable (Genome Medicine / Briefings in Bioinformatics). Tier B aspired post-closure pending external collaboration. Tier C out of scope per resource constraints. HPC verified reachable. Implementation begins after this tag commits per spec entry conditions.
64d507d Selectivity layer redesign FINAL CLOSURE. Phase 1-4-mCRPC complete with bug fixed. Phase 4-AML and Phase 4-GBM de-scoped after diagnostic revealed disease nets use disease-agnostic disease_net_builder.py (no prostate_tpm bug exists). 11 implementation tags shipped, this is tag 12. Round 1 mCRPC pipeline integrity verified end-to-end (KLK3=16696, 8/8 gates PASS). AML JAK3=15.84 and GBM FGFR3=2.43 produce meaningful tissue selectivity for first time. Disease-aware CSVs available for future Layer 15 consumers. Layer 15b-e (ADMET, off-target binding, toxicophores, DDI) explicitly NOT in this redesign scope - future work.
17c2dfc Phase 4-mCRPC — Unified net regeneration. Wrapper run_phase4_mcrpc.py backs up existing mcrpc_unified_net.json (51.2MB), runs build_unified_net.py with Phase 3 CSV inputs, performs 8-gate structural+numerical equivalence check. ALL 8 GATES PASS: top-level keys identical (genes/drugs/pathways/cell_populations/velocity_clusters/escape_routes/metadata/statistics/ode_parameters_from_data), counts identical (28454 genes, 0 drugs, 2984 pathways, 8 cell populations, 13 velocity clusters, 5 escape routes), KLK3/AR/BRCA2/TP53/PTEN selectivity values verified within rounding tolerance against Phase 3 CSV. Runtime 28s. mCRPC end-to-end Round 1 pipeline confirmed working with new selectivity layer. AML and GBM disease net regeneration deferred to dedicated future sessions where their respective builders (build_aml_net.py and unknown GBM builder in round3_gbm_live_test/) will be inspected before running.
8772db9 Phase 3 — Selectivity v2 CSV backward-compat exports. step6_selectivity_v2_csv_export.py reads Phase 2 JSONs and writes (a) legacy step6_selectivity_map.csv and step6_full_selectivity.csv for mCRPC with EXACT old column schema and old hyphenated safety labels (HIGHLY-SELECT, PROSTATE-SEL etc.) translated from new module underscored format - preserves Round 1 mCRPC consumer behavior 100%, (b) disease-aware CSVs for all 3 diseases with new disease-agnostic schema. KLK3 regression PASS at ratio_vs_mean=16696. BRCA2 and KLK3 numerical values identical to old module within rounding (6 decimals). Low-TPM genes (A1CF=0.014737) preserve precision. Downstream consumers (build_unified_net.py, intercepta_pipeline.py) read legacy CSVs unchanged.
b9d3b51 Phase 2 — step6_selectivity_v2.py disease-parameterized module SHIPPED. Replaces mCRPC-hardcoded step6_gtex_selectivity.py and step6_fix_gtex.py with config-driven module. Reads disease_tissue_mapping.json + genes_<disease>.json. Handles single-tissue (mCRPC, AML) and multi-tissue (GBM 13 brain regions). Output schema disease-agnostic. ALL three falsifiable success criteria from spec Section 10 PASS. mCRPC validation: KLK3 selectivity_vs_mean=16696 (matches Round 1 known biology). AML JAK3=15.84 (HIGHLY_SELECTIVE). GBM FGFR3=2.43 (top brain-tissue selective). TERT correctly NOT_EXPRESSED in GBM (matches biology - TERT promoter mutations matter, expression itself is low).
04fba4f Phase 1.5 — GTEx column audit + tissue mapping fix. Audit revealed config used underscored tissue names (Brain_Cortex, Whole_Blood) but GTEx v8 actual headers use spaces and dashes (Brain - Cortex, Whole Blood). Updated disease_tissue_mapping.json schema_version 1.1 with verbatim GTEx names. Audit now reports OK status across all 15 config-referenced tissues. Prevents Phase 2 from silently producing zero output for AML and GBM.
c24a702 Selectivity redesign Phase 1: config files. disease_tissue_mapping.json (master config, 3 production diseases + 3 future). genes_mcrpc.json (38 genes from step6_fix_gtex.py preserves Round 1 behavior). genes_aml.json (31 genes from Round 2.2c MUTATION_GENES + AML KEGG pathway). genes_gbm.json (top 30 genes from gbm_disease_net_action1.json). All disease-tissue mappings verified against GTEx v8 (54 tissues, 11 brain regions, no bone marrow - AML uses Whole_Blood with documented caveat).
bb678eb Selectivity layer redesign spec. Locked design before code per Round 2 discipline. Disease-parameterized step6_selectivity_v2 replacing mCRPC-hardcoded step6_gtex_selectivity.py and step6_fix_gtex.py. Disease-tissue mapping verified against GTEx v8 (54 tissues, 11 brain regions, no bone marrow - AML uses Whole_Blood with documented caveat). Lists 7 downstream consumers requiring update. 5-phase migration plan estimated 3-5 hours across 1-2 sessions.
```

## 6. Tags (chronological)

```
Total tags:       26

Last 25 tags by creation time:
2026-04-22  round2.1a-validated
2026-04-22  round2.1b-validated
2026-04-22  round2.1c-validated
2026-04-22  round2.1d-closed-methodology-finding
2026-04-22  round2.2a-closed-partial-success
2026-05-06  round2-closed
2026-05-06  round2-closure-erratum
2026-05-06  round2-2c-spec-locked
2026-05-06  round2-2c-failed-honestly
2026-05-06  vision-module1-amended
2026-05-06  selectivity-redesign-spec
2026-05-07  selectivity-configs-shipped
2026-05-07  selectivity-gtex-audit
2026-05-07  selectivity-module-v2-shipped
2026-05-07  selectivity-phase3-csv-shipped
2026-05-07  selectivity-phase4-mcrpc-shipped
2026-05-07  selectivity-redesign-complete
2026-05-07  workstream-b-spec-locked
2026-05-08  workstream-b-phase0-prep-shipped
2026-05-08  workstream-b-phase0-selectivity-shipped
2026-05-08  workstream-b-spec-erratum-luca
2026-05-08  test-plan-locked
2026-05-08  t1-lite-passed
2026-05-08  workstream-b-phase0-complete
2026-05-08  repo-hygiene-shipped
```

## 7. Data directory status

```
total 13584
drwxr-xr-x  25 kalki  staff      800 May  8 21:02 .
drwxr-xr-x  45 kalki  staff     1440 May  8 21:02 ..
drwxr-xr-x  22 kalki  staff      704 Apr  8 01:06 alphafold
drwxr-xr-x   3 kalki  staff       96 May  4 22:55 alphafold_cache
drwxr-xr-x   6 kalki  staff      192 Apr  8 09:08 beataml
drwxr-xr-x   3 kalki  staff       96 May  5 08:04 chembl
drwxr-xr-x   3 kalki  staff       96 May  6 01:59 clinicaltrials
drwxr-xr-x   3 kalki  staff       96 Apr  8 01:19 dice
drwxr-xr-x  66 kalki  staff     2112 Apr  8 11:43 docking
drwxr-xr-x   3 kalki  staff       96 Apr  8 01:24 encode
drwxr-xr-x   2 kalki  staff       64 Apr  9 00:22 epigenome
drwxr-xr-x   9 kalki  staff      288 Apr 19 20:07 gdsc
-rw-r--r--   1 kalki  staff  6952331 Mar 29 11:20 gtex_median_tpm.gct.gz
drwxr-xr-x   2 kalki  staff       64 Apr  8 00:42 hmdb
drwxr-xr-x   6 kalki  staff      192 Apr  8 00:55 human_gem
drwxr-xr-x   8 kalki  staff      256 May  8 21:02 manifests
drwxr-xr-x   8 kalki  staff      256 May  8 21:02 manifests_v2
drwxr-xr-x  48 kalki  staff     1536 Apr  7 23:47 opentargets
drwxr-xr-x   3 kalki  staff       96 Apr  9 00:26 pathogen

  756K              1 files  alphafold_cache/
  10M              20 files  alphafold/
  22M               4 files  beataml/
  6.8M              1 files  chembl/
  468K              1 files  clinicaltrials/
  11M               1 files  dice/
  3.2M             64 files  docking/
  4.0K              1 files  encode/
  0B                0 files  epigenome/
  6.5G             10 files  gdsc/
  0B                0 files  hmdb/
  4.4M              4 files  human_gem/
  676K              6 files  manifests_v2/
  2.2M              6 files  manifests/
  693M             54 files  opentargets/
  4.4M              1 files  pathogen/
  0B                0 files  scrna_seq/
  834M              8 files  scrna/
  19M               1 files  signor/
  98M               2 files  string/
  3.1M              3 files  su2c/
  0B                0 files  tcga_prad/
```

## 8. Top-level documents

```
-rw-r--r--  1 kalki  staff   893 Apr  8 14:07 /Users/kalki/INTERCEPTA/AUDIT_ACTION_PLAN.md
-rw-r--r--@ 1 kalki  staff  6923 Apr 18 23:19 /Users/kalki/INTERCEPTA/CLAUDE.md
-rw-r--r--  1 kalki  staff  1822 Apr 18 23:00 /Users/kalki/INTERCEPTA/INTERCEPTA_STATUS.md
-rw-r--r--@ 1 kalki  staff  8537 Apr 18 21:39 /Users/kalki/INTERCEPTA/MASTER_FIXES.md
-rw-r--r--  1 kalki  staff  1500 Apr  8 12:50 /Users/kalki/INTERCEPTA/NEXT_SESSION.md
-rw-r--r--  1 kalki  staff  4079 Mar 29 16:08 /Users/kalki/INTERCEPTA/PROJECT_STATUS.md
-rw-r--r--  1 kalki  staff  3081 Apr  8 09:14 /Users/kalki/INTERCEPTA/PUBLICATION_OUTLINE.md
-rw-r--r--  1 kalki  staff  4983 Mar 14 07:40 /Users/kalki/INTERCEPTA/README.md
```

## 9. docs/ directory

```
total 1480
drwxr-xr-x  29 kalki  staff     928 May  8 21:33 .
drwxr-xr-x  45 kalki  staff    1440 May  8 21:02 ..
-rw-r--r--   1 kalki  staff   15346 Mar 14 22:04 INTERCEPTA_Complete_Status_Report.docx
-rw-r--r--   1 kalki  staff   61768 Mar 14 07:38 INTERCEPTA_COMPLETE_VISION_v1_0.docx
-rw-r--r--@  1 kalki  staff    7945 Apr 21 21:14 INTERCEPTA_CSO_Parameter_Memo_v2_1.md
-rw-r--r--@  1 kalki  staff   13476 Apr 21 20:53 INTERCEPTA_CSO_Parameter_Memo_v2.md
-rw-r--r--   1 kalki  staff   51709 Mar 14 07:38 INTERCEPTA_DOCC.docx
-rw-r--r--   1 kalki  staff   25222 Mar 14 07:38 INTERCEPTA_Net_Architecture_v2_0.docx
-rw-r--r--   1 kalki  staff   30143 Mar 14 07:38 INTERCEPTA_Phase1_DataSourceAudit_v1_0.docx
-rw-r--r--   1 kalki  staff   17150 Mar 14 07:38 INTERCEPTA_Phase1_GroundTruth_v1_0.docx
-rw-r--r--   1 kalki  staff   19405 Mar 14 07:38 INTERCEPTA_Phase1_MathSpec_v1_0.docx
-rw-r--r--   1 kalki  staff   11144 Mar 14 07:38 INTERCEPTA_Phase1_Validation_Report.docx
-rw-r--r--@  1 kalki  staff    9472 Apr 21 21:34 INTERCEPTA_Round1_Errata_v1_0.md
-rw-r--r--@  1 kalki  staff    7835 Apr 21 21:14 INTERCEPTA_Round1_Retrospective.md
-rw-r--r--@  1 kalki  staff    6317 Apr 21 21:14 INTERCEPTA_Round2_AML_Kickoff.md
-rw-r--r--@  1 kalki  staff   14523 May  7 22:13 INTERCEPTA_Selectivity_Redesign_Closure.md
-rw-r--r--@  1 kalki  staff   15738 May  6 23:53 INTERCEPTA_Selectivity_Redesign_Specification.md
-rw-r--r--   1 kalki  staff   14472 Mar 14 07:38 INTERCEPTA_Strategic_Roadmap_v1_0.docx
-rw-r--r--@  1 kalki  staff   12335 May  8 16:58 INTERCEPTA_Test_Plan.md
```

