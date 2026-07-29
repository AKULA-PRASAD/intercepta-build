# Data manifest — sha256 of every input (public; not committed)

Point `INTERCEPTA_DATA` at a directory holding these files (default `/Users/kalki/kaalcura/data`).
`src/intercepta/data.py` verifies each file against the sha256 below at load time and refuses to run on a
mismatch. sha256 prefixes match the values recorded in the verified ~/kaalcura V1B run (provenance chain).

| name | sha256 | source |
|---|---|---|
| `gdsc_response.csv` | `b472905ea811c145b1827f382975756a66c2ac5dffbe9ad323148bfdea38cdb5` | GDSC2 drug response (LN_IC50) |
| `gdsc_expression.zip` | `a087c0f703050d86e9f108b03096308e541a70fdc105c6ea0a3c85f8f9b3b0d7` | GDSC cell-line expression |
| `depmap_expression.csv` | `6b8d5f3c00ce73a5e025922d52b74929e19359e323786a0314410762b0c08a16` | DepMap/CCLE 22Q2 expression |
| `depmap_meta.csv` | `382c0c26cf57a2fb82449f797c58cb0dfc2313949908d8f83560ebcf3e5bcbaa` | DepMap sample map (COSMIC↔DepMap) |
| `independent/prism_secondary_screen.csv` | `88d1013506e0cd6f191a51c5f3fdd3fb2be54f8afb4e19a5d1f8538e81fbfec8` | PRISM secondary screen (AUC) |
| `depmap_mut_try1.csv` | `e99e43789c1c4821ccb737a45cd6f4fbbeac709c5a8cca326846d6d9a16cf5c8` | DepMap somatic mutation MAF (B2) |
| `beataml_waves1to4_norm_exp_dbgap.txt` | `d5745b9dbf46dba866a3c7370bb0ba73b363ecdd21e01cc1d916b4e3021e6f87` | BeatAML patient tumor RNA (B3; INTERCEPTA_BEATAML) |
| `beataml_probit_curve_fits_v4_dbgap.txt` | `d4bc5f0d91f66314107411e0f2511adc987e29df5b83d9b03df56d3d12928314` | BeatAML ex-vivo drug AUC (B3; INTERCEPTA_BEATAML) |
| `independent/gdsc1/GDSC1_fitted_dose_response.xlsx` | `837b0686500fde75179e490de08f034abd9f882d8b0253d637bafe83e156dafd` | GDSC1 independent screen (B3c external replication) |
| `beataml_wv1to4_clinical.xlsx` | `bc692f647f93945e1cf883271af5501bf75c8af3e681676241093c198ed167ad` | BeatAML clinical/WES (B4; INTERCEPTA_BEATAML) |
| `beataml_wes_wv1to4_mutations_dbgap.txt` | `5a5a5eb8f492b1385aebe85c490b9333f65590f09391a7c1951b04dd1dba1680` | BeatAML clinical/WES (B4; INTERCEPTA_BEATAML) |
| `pdxe.xlsx` (Gao 2015 nm.3954 MOESM10) | `c4b9a6903a4d1f76e3ddca4199039776d56bb99970aa5b7abe4f3abd732a0c6d` | PUBLIC PDX Encyclopedia — RNAseq_fpkm + PCT curve metrics (B7 external validation); INTERCEPTA_PDXE |
| `depmap_crispr_gene_effect.csv` (DepMap 23Q2 Chronos) | `d1633bfa0bf4719e72e564f15d9bcda7fddbbd3dac2a8a3aebf4898ac9f56f00` | PUBLIC CRISPR gene-dependency (B12); figshare 40448555 |
| `pancan_geneExp.gz` (Xena EB++AdjustPANCAN geneExp) | `a00532ec86af8c07630c618f10f6277f09c484d0a9c17db5901edf95c7714b38` | PUBLIC TCGA pan-cancer expression (B10); INTERCEPTA_TCGA |
| `lifeome drug_response.txt` (TCGA curated) | `6891a1e9ebd966cc60641a52a12b2a8866db2b792f83cff63aa3818c30e534dd` | PUBLIC curated TCGA clinical drug response (B10); INTERCEPTA_TCGA |

The rows above are the reproduced Phase-B inputs with pinned sha256 (verified at load). The table below is the
**full external-data provenance for all of INTERCEPTA** — no data is committed; each row says where to get it
and its ACCESS CLASS. **CONTROLLED rows must NEVER be committed to any repo** (dbGaP/DUA); code references them
via the `INTERCEPTA_BEATAML` env var or a local path only.

## Full external data sources (provenance + access class)
| Dataset | Source / accession | Access | Used by |
|---|---|---|---|
| GDSC2 / GDSC1 | Sanger cancerrxgene.org | PUBLIC | src/, engine/scouts, engine/kaalcura |
| DepMap / CCLE 22Q2 | depmap.org (Broad) | PUBLIC | src/, engine/aml |
| PRISM secondary screen | depmap.org (Broad) | PUBLIC | src/ (B1) |
| STRING v12.0 | string-db.org | PUBLIC | engine/net (step4) |
| SIGNOR | signor.uniroma2.it | PUBLIC | engine/net |
| KEGG pathways | kegg.jp | PUBLIC | engine/net (step5) |
| Open Targets | platform.opentargets.org | PUBLIC | engine/net (step8) |
| ChEMBL | ebi.ac.uk/chembl | PUBLIC | engine/net (step7), engine/scouts |
| GTEx median TPM | gtexportal.org (median only) | PUBLIC | engine/net (step6 selectivity) |
| AlphaFold DB | alphafold.ebi.ac.uk | PUBLIC | engine/net (step10), engine/scouts (docking) |
| Human-GEM | github Human-GEM | PUBLIC | engine/net (step9) |
| DICE immune | dice-database.org | PUBLIC | engine/net (step13) |
| scRNA — prostate | GEO GSE137829, GSE141445 | PUBLIC | engine/velocity, engine/net |
| scRNA — melanoma ICI | GEO GSE78220, GSE91061 | PUBLIC | engine/kaalcura (r_validation) |
| scRNA — AML (Van Galen 2019) | GEO GSE116256 | PUBLIC | engine/aml, engine/velocity |
| scRNA — lung (Travaglini) | cellxgene / Travaglini 2020 | PUBLIC | engine/cell_fm |
| TCGA (processed expr/clinical) | GDC / Firebrowse | PUBLIC (processed) | engine/kaalcura (workstream_b) |
| Geneformer foundation model | HuggingFace ctheodoris/Geneformer | PUBLIC (third-party, ~5.5 GB) | engine/cell_fm — **downloaded externally, never vendored** |
| **BeatAML** (WES mutations, clinical, expression, drug response) | **dbGaP phs001657** | **🔒 CONTROLLED** | engine/aml, verification/, src/ (B3–B4) — env `INTERCEPTA_BEATAML` only |
| FIMM/Malani AML (RNA Log2CPM, DSRT DSS, mutations, clinical) | Zenodo 7370747 (Malani et al. Cancer Discovery 2022) | **PUBLIC (CC-BY 4.0)** — MD5 3db5280e…a9e241 | experiments/B20 external replication of V19/V20 |
| CCLE quantitative proteomics (normalized) | gygi.hms.harvard.edu/data/ccle (Nusinow et al. Cell 2020) | **PUBLIC** — sha256 b72a9ff3…c80 | experiments/B22 modality-ceiling test |
| **SU2C-PCF** (mutations, clinical, CNA) | cBioPortal / SU2C-PCF | **🔒 patient-level — treat as controlled** | engine/net (step2) — never committed |
| **TCGA raw** (BAM/germline) | GDC controlled | **🔒 CONTROLLED** | not used in committed results |

**Rule:** anything marked 🔒 is individual-level patient data and is excluded from git by `.gitignore` and by
policy. Reproducing 🔒-dependent results requires the user's own dbGaP/cBioPortal access (a human gate,
DECISIONS.md D7/D8). All PUBLIC rows are freely downloadable and are the basis of every committed result.
