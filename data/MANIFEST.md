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
| O'Neil 2016 drug-combination synergy (OncoPolyPharmacology) | Therapeutics Data Commons (TDC) → Harvard Dataverse | **PUBLIC (open)** | experiments/B24 synergy generalization |
| DrugComb drug-combination synergy | Therapeutics Data Commons (TDC) | **PUBLIC (open)** | experiments/B25/B28 synergy scale-up + cross-corpus |
| **TDC ADMET Benchmark Group** (22 ADME/Tox tasks: SMILES + label; scaffold splits + public leaderboard) | Therapeutics Data Commons — `tdc.benchmark_group.admet_group` (auto-downloaded to `$INTERCEPTA_DATA/tdc_admet`, ~1.5 MB) | **PUBLIC (open)** | experiments/B30 ADMET module; `src/intercepta/admet.py` |
| **RAscore synthesizability labels** (`data.zip`; SMILES + AiZynthFinder retrosynthetic-solvability label; 179,413 train / 19,935 test ChEMBL) | RAscore GitHub reymond-group/RAscore `data/data.zip` (MIT code; ChEMBL-derived; Thakkar et al. Chem Sci 2021) — sha256 `f73b3028592ff95feeeb2f4e0285005d956976c810a3818fc399c20480979ef3`; at `$INTERCEPTA_DATA/rascore/` | **PUBLIC (open)** | experiments/B31 synthesizability; `src/intercepta/synth.py` |
| **ClinTox** (SMILES + clinical-trial toxicity / FDA-approval label; 1,478 drugs) | Therapeutics Data Commons `tdc.single_pred.Tox(name='clintox')` (MoleculeNet; auto-download to `$INTERCEPTA_DATA/tdc_tox`) | **PUBLIC (open)** | experiments/B32 integration MVP (held-out developability outcome) |
| **Open Targets target-disease associations** (12,000 pairs × 40 diseases; per-datatype evidence scores) | Open Targets Platform GraphQL API v26.06 (fetched by `experiments/B34_target_id/collect_data.py` → `$INTERCEPTA_DATA/opentargets/ot_target_disease.parquet`) — sha256 `d14006e8ec9cf292349e1c5b2a9db5f902e82ba532674b71bdaaf2001fbeb1ba` | **PUBLIC (open)** | experiments/B34 target identification |
| **tox21** (12-assay toxicity multi-label; SMILES + labels) | Therapeutics Data Commons `tdc.single_pred.Tox(name='tox21')` (MoleculeNet; `$INTERCEPTA_DATA/tdc_tox`) | **PUBLIC (open)** | experiments/B36/B37/B38 (held-out outcomes; B37 representation pretraining) |
| **ChemBERTa-77M-MLM** (deep molecular foundation model; RoBERTa pretrained unsupervised on 77M molecules) | HuggingFace `DeepChem/ChemBERTa-77M-MLM` (downloaded to `$INTERCEPTA_DATA/hf_cache`; third-party pretrained weights, never vendored) | **PUBLIC (open, third-party)** | experiments/B38 deep foundation-model integration test |
| **HIV activity** (SMILES + replication-inhibition label; 41,127 molecules, 1,443 active) | Therapeutics Data Commons `tdc.single_pred.HTS(name='hiv')` (MoleculeNet; `$INTERCEPTA_DATA/tdc_bio`) | **PUBLIC (open)** | experiments/B40 target-conditioned generation (activity QSAR) |
| LINCS L1000 consensus drug signatures (dhimmel/lincs v2.0) | Zenodo 47223 + dhimmel/drugbank slim (GitHub) | **PUBLIC (open)** | experiments/B27 connectivity repurposing |
| CCLE quantitative proteomics (normalized) | gygi.hms.harvard.edu/data/ccle (Nusinow et al. Cell 2020) | **PUBLIC** — sha256 b72a9ff3…c80 | experiments/B22 modality-ceiling test |
| **SU2C-PCF** (mutations, clinical, CNA) | cBioPortal / SU2C-PCF | **🔒 patient-level — treat as controlled** | engine/net (step2) — never committed |
| **TCGA raw** (BAM/germline) | GDC controlled | **🔒 CONTROLLED** | not used in committed results |

**Rule:** anything marked 🔒 is individual-level patient data and is excluded from git by `.gitignore` and by
policy. Reproducing 🔒-dependent results requires the user's own dbGaP/cBioPortal access (a human gate,
DECISIONS.md D7/D8). All PUBLIC rows are freely downloadable and are the basis of every committed result.

## LIT-PCBA (unbiased virtual-screening benchmark) — B46
- Source: https://drugdesign.unistra.fr/LIT-PCBA/ (Tran-Nguyen, Jacquemard & Rognan, J. Chem. Inf. Model. 2020)
- File: full_data.tgz (53,808,890 bytes), sha256 93467a5b… ; extracted to `$INTERCEPTA_DATA/lit_pcba/`
- Content: 15 targets, per target `actives.smi` + `inactives.smi` (SMILES + PubChem CID) + co-crystal `*_protein.mol2`/`*_ligand.mol2`
- Access class: PUBLIC / OPEN. Never committed to git (data cache only).
- Caveats (documented): extreme active:inactive imbalance (1:1000–1:20000); known analog leakage/redundancy across splits (arXiv:2507.21404) — handled via our NN<0.4 novel-band lens + cross-label dedup.

## ESM-2 protein embeddings + UniProt sequences — B49
- ESM-2: facebook/esm2_t30_150M_UR50D (HuggingFace, open); cached `$INTERCEPTA_DATA/hf_cache`, embeddings `$INTERCEPTA_DATA/esm_cache/`.
- Sequences: UniProt REST `{acc}.fasta` for 14 accessions (P07550,P00352,P03372,P39748,P04062,O75874,Q92830,P28482,P42345,P41145,P14618,P37231,P04637,P11473). PUBLIC/OPEN. Cached, never committed.

## GuacaMol benchmark + ChEMBL seeds — B52
- guacamol 0.5.2 (pip, open); goal-directed scoring functions used with a scipy.histogram compat shim. Published baselines = Brown et al., JCIM 2019 (hard-coded reference).
- ChEMBL seeds: `$INTERCEPTA_DATA/tdc_gen/chembl.tab` (already logged). PUBLIC/OPEN; never committed.

## DUD-E (Directory of Useful Decoys, Enhanced) — B55
- Source: https://dude.docking.org (Mysinger et al., J. Med. Chem. 2012). 8 targets (egfr,vgfr2,akt1,aa2ar,fa10,hivpr,ppara,gcr): actives_final.ism + decoys_final.ism.
- ChEMBL actives + property-matched (topology-dissimilar) ZINC decoys, 50/active. Cached `$INTERCEPTA_DATA/dude/` (~19 MB). PUBLIC/OPEN; never committed.

## MoleculeACE (continuous-potency ChEMBL benchmark) — B60
- Source: https://github.com/molML/MoleculeACE (van Tilborg et al., JCIM 2022; ChEMBL v29). 30 targets, continuous potency (pKi/pIC50/pEC50) + activity-cliff flags.
- Files: CHEMBL{id}_{Ki,IC50,EC50}.csv (cols: smiles, exp_mean[nM], y, cliff_mol, split, y[pEC50/pKi]). Cached `$INTERCEPTA_DATA/moleculeace/` (~5.1 MB). PUBLIC/OPEN; never committed.

## UniProt proteomes + ChEMBL-xref drug targets (TID1 — front-half target-ID)
- Source: UniProt REST (https://rest.uniprot.org), 2026-07-31. Full reference proteomes (FASTA) + per-organism drug-target
  accession lists (UniProt entries carrying a ChEMBL cross-reference).
- Panel proteomes `$INTERCEPTA_DATA/tid1/proteomes/`: mtb 8133534fc2c1 (3997 prot), ecoli edc6d75adaef (4403),
  paeruginosa 4a4590a3d029 (5563), pfalciparum 3f28eb812794 (5361), sarscov2 ce74ba3a605d (17),
  human(reviewed) d624e83ef467 (20431).
- Drug-target lists `$INTERCEPTA_DATA/tid1/targets/*_chembl.txt`: mtb aff79bed1c4c (131), ecoli 374f2e126cb8 (182),
  paeruginosa c431976f41a8 (46 in-proteome), pfalciparum 08f14b5d4fc2 (52), human b770a6d2c6e0, sarscov2 fb5a841fee13.
- PUBLIC/OPEN (UniProt CC-BY 4.0); cached (~26 MB), never committed. Essentiality (OGEE/DEG) deferred — endpoints unreachable 2026-07-31.

## AlphaFold DB v6 structures + fpocket druggability (TID2 — structural target-ID)
- Source: AlphaFold DB v6 per-accession models (https://alphafold.ebi.ac.uk/files/AF-{ACC}-F1-model_v6.pdb), fetched 2026-07-31.
- `$INTERCEPTA_DATA/tid2/structures/` = 1990 PDBs (497M) for the TID2 eval set (411 ChEMBL targets + seeded ~400 non-targets/org).
- `$INTERCEPTA_DATA/tid2/druggability.tsv` (sha256 aab3c3f3cbd4, 2011 rows: accession, organism, is_target, max_druggability, n_pockets, has_structure)
  = fpocket 4.2.3 max Druggability Score per protein (deterministic intermediate; regenerable via experiments/TID2_.../build_druggability_cache.py).
- PUBLIC/OPEN (AlphaFold DB CC-BY 4.0); never committed.

## Cross-kingdom pathogen proteomes + ChEMBL-xref targets (TID3 — breadth)
- Source: UniProt REST reference proteomes + ChEMBL-xref target lists, fetched 2026-08-01. Added to $INTERCEPTA_DATA/tid1/.
- calbicans(fungus) proteome 518a55bfe7d0 6036prot/19tgt · tbrucei(parasite) 316f1286886c 8588/13 · lmajor(parasite) 032b2248cacb 8039/12.
- K. pneumoniae fetched but DROPPED (0 in-proteome ChEMBL targets — strain mismatch). Viruses excluded (species-level proteomes strain-fragmented/near-empty).
- PUBLIC/OPEN (UniProt CC-BY 4.0); never committed.

## TID4 expanded panel (UniProt reviewed proteomes + ChEMBL-xref targets, 11 organisms)
- Source: UniProt REST reviewed proteomes + ChEMBL-xref targets by organism_id (targets ⊆ proteome by construction), 2026-08-02.
- $INTERCEPTA_DATA/tid4/{proteomes,targets}/: 7 bacteria (mtb/ecoli/paeruginosa/saureus/hpylori/ngonorrhoeae/kpneumoniae)
  + 2 parasites (pfalciparum/tcruzi) + 2 fungi (calbicans/afumigatus). Filter: reviewed proteome >=100 & >=5 in-proteome targets.
  Most pathogens excluded: ChEMBL drug-target ground truth is sparse/strain-fragmented (a data limit, stated). PUBLIC/OPEN; never committed.

## MET1 FBA gene-essentiality (BiGG GEMs via COBRApy)
- Source: BiGG Models (bigg.ucsd.edu) genome-scale metabolic models loaded via COBRApy 0.31.1; FBA single-gene-deletion, 2026-08-02.
- $INTERCEPTA_DATA/met1/essentiality.tsv (organism, uniprot, gene_id, essential, growth_ratio). E. coli iML1515: 1515 genes
  w/ UniProt xref, 195 FBA-essential (13%). S. aureus iYS854 / K. pneumoniae iYL1228 loaded but genes lack UniProt
  annotations (0 mapped) -> MET1 scoped to E. coli. PUBLIC/OPEN (BiGG); deterministic; never committed.

## MET2 de-novo CarveMe GEMs + FBA essentiality (3 bacteria)
- CarveMe 1.6.6 (SCIP/pyscipopt + diamond 2.2.4, arm64) GEMs built de-novo from TID1 full proteomes (genes = UniProt
  accessions by construction), 2026-08-02. $INTERCEPTA_DATA/met2/gems/{ecoli,mtb,paeruginosa}.xml + essentiality.tsv
  (default/complete medium, single-gene-deletion). Regenerable via carve + build_essentiality_cache.py. PUBLIC/OPEN; never committed.

## MET4 STRING v12 E. coli PPI network (mechanism-beyond-metabolism test)
- Source: STRING v12.0 (stringdb-downloads.org), E. coli K-12 taxid 511145, fetched 2026-08-03.
  $INTERCEPTA_DATA/met4/links.full.txt.gz (per-channel scores; sha256 159c78d4…) + aliases.txt.gz (UniProt_AC map;
  sha256 9379c356…). 984,760 edges, 4,091 UniProt-mapped proteins. Channels used: combined(≥700), experiments-direct(≥400),
  coexpression-direct(≥400), textmining-direct(≥400, = study-intensity proxy). PUBLIC/OPEN (STRING CC-BY 4.0); never committed.

## HIT1 molecule-half ligand data (MoleculeACE) + LIT-PCBA docking subset
- MoleculeACE (github.com/molML/MoleculeACE, CC-BY): 30 curated ChEMBL targets, 48,714 compounds, fetched 2026-08-04.
  $INTERCEPTA_DATA/hit1/moleculeace/CHEMBL*.csv — per compound: SMILES, pActivity (y[pKi/pEC50]), cliff_mol, train/test split.
- LIT-PCBA 9-target subset (Zenodo record 10682034, Berenger strain study, 16.4 MB), fetched 2026-08-04:
  $INTERCEPTA_DATA/hit1/litpcba/ — crystal structures + GOLD-docked poses + docking/strain scores + active/decoy labels.
  NOTE: this is a docking/strain-STUDY subset (compound-selection-biased) → reserved for HIT2 relative analysis only, NOT
  headline enrichment. Full LIT-PCBA (unistra) was 404 at fetch time. PUBLIC/OPEN; never committed.

## FRONT1 front-half inputs (chokepoint cache + human core-essential genes)
- $INTERCEPTA_DATA/front1/chokepoints.tsv — metabolic chokepoint genes per bacterium, computed by build_chokepoint.py from
  the MET2 CarveMe GEMs (COBRApy stoichiometry pass; regenerable). Deterministic.
- $INTERCEPTA_DATA/front1/CEGv2.txt — Hart lab CEG2 human core-essential genes (684 gene symbols; github hart-lab/bagel,
  fetched 2026-08-04) — H2 host-toxicity ground truth. Human proteome = existing tid1/proteomes/human.fasta (UniProt, GN=).
  PUBLIC/OPEN; never committed.

## HIT2 thrombin docking (physics floor)
- Thrombin receptor: RCSB PDB 1OYT (recombinant human thrombin + inhibitor FSN), fetched 2026-08-04. $INTERCEPTA_DATA/hit2/
  {1oyt.pdb, receptor.pdbqt (obabel -xr -p7.4), vina.conf (box from FSN centroid)}. Cognate FSN redocked −11.21 kcal/mol.
- $INTERCEPTA_DATA/hit2/thrombin_vina.tsv — AutoDock Vina 1.2.7 (seed 42, exh 16) best-pose scores for the 553 MoleculeACE
  CHEMBL204 test compounds (regenerable via build_dock_cache.py; deterministic). PUBLIC/OPEN; never committed.

## FRONT2 structural selectivity (fpocket druggability of pathogen targets + human homologs)
- $INTERCEPTA_DATA/front2/druggability.tsv — fpocket max Druggability Score for host-homologous pathogen metabolic genes
  (Mtb+E.coli; pathogen side reuses TID2 AF structures) AND their best human homologs (AlphaFold v6 fetched + fpocket),
  built by build_druggability.py. Human homolog structures = AlphaFold DB (alphafold.ebi.ac.uk, CC-BY). Regenerable;
  deterministic (seeded non-target sample). PUBLIC/OPEN; never committed.

## SUBSTRATE4 pandemic stress test (SARS-CoV-1 reference proteome)
- $INTERCEPTA_DATA/substrate4/sars1.fasta — SARS-CoV-1 proteome (UniProt UP000000354, 15 proteins), fetched 2026-08-04 —
  the "prior coronavirus knowledge" reference (Spike P59594 / Nucleoprotein P59595 / Replicase P0C6X7). SARS-CoV-2 proteome
  + targets reuse existing tid1/proteomes/sarscov2.fasta + tid1/targets/sarscov2_chembl.txt. PUBLIC/OPEN; never committed.

## NEWBUG held-out pathogen (K. pneumoniae) — de-novo GEM + essentiality
- $INTERCEPTA_DATA/newbug/kpneumoniae.fasta — K. pneumoniae MGH 78578 proteome (UniProt organism_id 272620, 5126 proteins),
  fetched 2026-08-05. A WHO critical-priority pathogen NOT in the 7-panel (genuinely held out).
- $INTERCEPTA_DATA/newbug/kpneumoniae.xml — de-novo CarveMe GEM (2795 rxns / 1927 genes; UniProt-keyed via gid2acc).
- $INTERCEPTA_DATA/newbug/{essentiality.tsv,chokepoints.tsv} — FBA essentiality + chokepoint (build.py). Regenerable;
  deterministic. PUBLIC/OPEN; never committed.

## NEWBUG2 second held-out pathogen (A. baumannii) — de-novo GEM + essentiality
- $INTERCEPTA_DATA/newbug2/abaumannii.fasta — A. baumannii AB0057 proteome (UniProt organism_id 480119, 3711 proteins),
  fetched 2026-08-05. WHO #1 critical-priority pathogen, NOT in the 7-panel (second held-out organism).
- $INTERCEPTA_DATA/newbug2/abaumannii.xml — de-novo CarveMe GEM (2835 rxns / 1138 genes; UniProt-keyed via gid2acc).
- $INTERCEPTA_DATA/newbug2/{essentiality.tsv,chokepoints.tsv} — FBA essentiality + chokepoint. Regenerable; deterministic.
  PUBLIC/OPEN; never committed.

## VALIDATE_essentiality (Tier-0 experimental truth — E. coli essentiality; PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/expval/PECData.dat — PEC (Profiling of E. coli Chromosome; NBRP/NIG, shigen.nig.ac.jp) systematic
  single-gene-knockout essentiality table (4497 ORFs; Class 1=essential=302). sha256 6a6f98af…. Source of ground truth.
- $INTERCEPTA_DATA/expval/ersilia_ess.csv — independent multi-source consensus cross-check (Keio;Goodall;Rousset18;
  Wang18; ersilia-os/gradi-target-prioritization). sha256 1996d05f…. 209 experimentally-essential rows.
- $INTERCEPTA_DATA/expval/ecoli_essential.txt — derived: PEC Class-1 gene symbols + b-numbers (605 tokens) the validator
  consumes. Regenerable from PECData.dat. PUBLIC/OPEN; never committed.

## VALIDATE_essentiality Mtb generalization (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/expval_mtb/dejesus2017.xlsx — DeJesus et al. 2017 mBio Table 1 ORF essentiality calls (Rv_ID/Name/
  Final Call; ES=461 strict-essential), via ajinich/mtb_tn_db. sha256 989848da…
- $INTERCEPTA_DATA/expval_mtb/rvmap.tsv — UniProt Rv-number->accession+symbol map (rest.uniprot.org, taxid 83332, 4059).

## VALIDATE_essentiality K. pneumoniae HELD-OUT generalization (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/expval_kp/kp_ess.csv — genome-wide K. pneumoniae essentiality (ersilia-os/gradi-target-prioritization;
  aggregates published CRISPRi KPNIH1 + Tn-seq experimental essentiality; 'experimentally_essential' 353 True/5728).
  sha256 52a258ed…. Only its EXPERIMENTAL label used (its own fba_* columns IGNORED).

## VALIDATE_essentiality A. baumannii (held-out) + P. aeruginosa via DEG (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/expval_deg/deg_bacteria.csv, deg_annotation_p.csv, DEG10.aa.gz — DEG (Database of Essential Genes,
  tubic.org) bulk downloads. Used: DEG1043 (A. baumannii ATCC 17978, Wang 2014 INSeq lung-persistence, 458) + DEG1036
  (P. aeruginosa PAO1, Turner 2015 Tn-seq, 336). Gene-name essential symbols extracted from deg_annotation_p.csv.

## REACH1 non-metabolic recall (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/reach1/breadth.tsv — per-E.coli-gene conservation breadth (0-6 diverse panel bacteria with a homolog;
  mmseqs2). Regenerable from tid1 proteomes via build_conservation.py. Reuses PEC essentials + MET2 GEM.

## ENGINE end-to-end (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/engine/kpneumoniae_breadth.tsv, reference_targets.fasta — on-the-fly inputs for the held-out K. pneumoniae
  DiscoveryEngine demo (conservation breadth vs 7 panel; other-org known-target sequences). Regenerable via ENGINE prep.py.

## SYNLETH1 resistance-robustness (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/synleth/iML1515.xml — curated E. coli genome-scale model iML1515 (BiGG, bigg.ucsd.edu; Monk et al. 2017).
  Used for single-reaction/gene deletion + double-gene-deletion (metabolic bypass / synthetic-lethal classification).

## ENGINE A. baumannii multi-axis run (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/engine/abaumannii_breadth.tsv, $INTERCEPTA_DATA/synleth/abaumannii_condition_robust.tsv — AB-native
  conservation-breadth (mmseqs vs 7-panel) + condition-robustness (multi-medium FBA on the AB CarveMe GEM). Regenerable.

## SAUREUS Gram-positive generalization (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/newbug3/saureus.fasta — S. aureus NCTC 8325 proteome (UniProt taxid 93061, 2891 proteins).
- $INTERCEPTA_DATA/newbug3/saureus.xml — de-novo CarveMe GEM (860 genes). Regenerable. Essential-gene truth = DEG1032
  (S. aureus NCTC 8325, TMDH/Tn-based) from the DEG bulk download. engine/synleth S. aureus breadth/resistance/condition
  are derived. PUBLIC/OPEN; never committed.

## CROSSVAL_curated cross-phylum validation (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/crossval/gems/{iYL1228,iCN718,iEK1008,iYS854,iYO844,STM_v1_0}.xml — curated BiGG genome-scale models
  (bigg.ucsd.edu) for K. pneumoniae / A. baumannii / M. tuberculosis / S. aureus USA300 / B. subtilis / Salmonella LT2.
- $INTERCEPTA_DATA/expval_mtb/dejesus_es_ids.txt — pre-extracted DeJesus 2017 ES ids. Experimental sets: PEC, DEG (1001/1011/
  1062), ersilia KP, DeJesus. All PUBLIC/OPEN; never committed.

## INTERVENE1 repurposing intervention layer (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/intervene/drug_targets.{tsv,fasta} — ChEMBL drug-mechanism knowledge base (7561 drug->target
  mechanisms; 2148 drug-target protein sequences via UniProt). Open (ChEMBL REST + UniProt); regenerable; never committed.

## GENERALIZE3 viral structural blind (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/generalize3/ — experimental RCSB PDB structures for 21/30 SARS-CoV-2 mature proteins
  (query_clean/) + a frozen corona-free 31-structure drug-target panel across 13 classes (ref_clean/) +
  Foldseek aln.m8. Open (RCSB PDB); regenerable; never committed.

## GENERALIZE5 parasite FBA (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/generalize5/ — iPfal19.xml (curated P. falciparum GEM, PARADIGM/GitHub maureencarey/paradigm),
  Zhang 2018 piggyBac essentiality via PlasmoDB (zhang2018_essentiality.csv + Pf3D7 annotations/aliases). Open;
  regenerable; never committed.

## GENERALIZE4 eukaryote FBA (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/generalize4/ — iMM904.xml (curated S. cerevisiae GEM, BiGG), deg_euk/deg_annotation_e.csv
  (DEG2001 Giaever 2002 essential set), SGD_features.tab (SGD R64 ID map). Open; regenerable; never committed.

## HOSTCTX1 E-Flux malaria (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/hostctx1/malariacellatlas_bloodstage_expression.csv — P. falciparum asexual blood-stage
  mean expression per PF3D7_ gene (Malaria Cell Atlas, Howick 2019; via PlasmoDB annotation table). Reuses
  GENERALIZE5's iPfal19 GEM + Zhang 2018 truth read-only. Open; regenerable; never committed.

## HOSTCTX2 exchange curation malaria (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/hostctx2/ — reuses GENERALIZE5's iPfal19 GEM + Zhang 2018 truth read-only; host-available
  nutrient sets derived from published RPMI 1640 (Moore 1967) + P. falciparum salvage biology citations (no
  new bulk data). Regenerable; never committed.

## STRUCTREPURPOSE1 structural repurposing (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/structrepurpose1/ — AlphaFold v6 structures for 2009 ChEMBL drug-target accessions +
  2009 organism-matched random NON-drug proteins (null reference) + query target structures. ~1.3 GB. Open
  (AlphaFold DB / UniProt); regenerable; never committed.

## DEPEND1 functional-dependency layer (PUBLIC/OPEN, never committed)
- DepMap/CCLE public (22Q2-era Chronos): depmap_crispr_gene_effect.csv (1095 lines x 17931 genes),
  depmap_expression.csv, sample metadata, somatic MAF — at /Users/kalki/kaalcura/data/ (pre-existing open
  cache; hashes frozen in DEPEND1 PREREG.md). Open (depmap.org); regenerable; never committed.

## TRANSFER1 label-free zero-screen transfer (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/transfer1/ — S. cerevisiae proteome + P.falciparum<->human and <->yeast mmseqs RBH ortholog
  TSVs. Reuses DepMap (kaalcura/data), Zhang 2018 + P.falciparum proteome (generalize5/tid1), yeast essentials
  (generalize4) read-only. Open; regenerable; never committed.

## HARDENV1 virus structural n>1 (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/hardenv1/ — experimental RCSB PDB structures for 9 drugged viral targets (HIV/Flu/HCV/HSV)
  + a frozen 37-structure/14-class drugged-enzyme reference panel (GENERALIZE3's 31 + 6 cross-family analogs).
  Open (RCSB); regenerable; never committed.

## HARDENP1 parasite FBA n>1 Toxoplasma (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/hardenp1/ — iTgo2020 curated T. gondii GEM (Krishnan 2020, PARADIGM models/published) +
  Sidik 2016 genome-wide CRISPR phenotype table (Cell, open Elsevier suppl mmc3.xlsx). Open; regenerable; never committed.

## HARDENF1 fungal pathogen FBA n>1 Candida (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/hardenf1/ — C. albicans curated GEM (Mirhakkak & Schäuble 2021, BioModels MODEL2110210002)
  + CGD curated inviable/loss-of-function essentiality (Roemer 2003 GRACE + later) + CGD A22 ID map. Open;
  regenerable; never committed.

## F3CLIN1 dependency->patient-driver relevance (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/f3clin1/ — IntOGen Compendium of Cancer Genes (2024-06-18, CC0) driver set + CancerMine
  citation counts (study-bias proxy). Reuses DepMap (kaalcura/data) read-only. Open; regenerable; never committed.

## PARARESOLVE1 parasite GEM-vs-biology confound (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/pararesolve1/ — independent P. falciparum GEMs (Chiappino-Pepe 2017; Abdel-Haleem 2018
  iAM-Pf480) via PARADIGM redistribution + same-lineage gf_ variants. Reuses Zhang 2018 (generalize5) +
  iTgo2020 (hardenp1) read-only. Open; regenerable; never committed.

## PARARESOLVE2 screen-tech probe Bushell (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/pararesolve2/ — Bushell et al. 2017 (Cell, PMC5509546 open-access) P. berghei PlasmoGEM
  barseq knockout essentiality (Table S1/mmc1.xlsx, authors' Phenotype label) via Europe PMC. Reuses iPfal19 +
  iAM-Pf480 (pararesolve1) read-only. Open; regenerable; never committed.

## INTERVENE2 cancer repurposing (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/intervene2/chembl_max_phase.json — ChEMBL max_phase for 4450 human drug ids (ChEMBL REST,
  frozen cache for deterministic scoring). Reuses DepMap (kaalcura) + intervene/drug_targets.tsv + IntOGen
  (f3clin1) read-only. Open; regenerable; never committed.

## INTERVENE3 synthetic-lethal (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/intervene3/ — human paralog pairs + curated known-SL set (Ryan/De Kegel cancergenetics
  paralog_seq_similarity, Ensembl-111). Reuses DepMap (kaalcura) + INTERVENE2 ChEMBL mapper read-only. Open; regenerable; never committed.

## BLIND2 C. jejuni prospective-blind #2 (PUBLIC/OPEN, never committed)
- $INTERCEPTA_DATA/blind2/ — C. jejuni NCTC 11168 proteome (UniProt UP000000799) + de-novo CarveMe GEM +
  DEG1049 Tn-seq essentiality (Mandal 2017). Open; regenerable; never committed.
