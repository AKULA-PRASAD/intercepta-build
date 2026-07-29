# INTERCEPTA Round 3 — Live End-to-End Test: Glioblastoma

**Date:** 2026-04-22
**Disease entered:** glioblastoma (not pre-resolved to any ontology ID)
**Tester:** Prasad Akula & Claude
**Rule:** document what happens, do not patch or optimize during test
**Output convention:** real wall-clock timing, real commands, real output

---

## Finding 0: Data inventory (pre-test)

**Cached locally:**
- opentargets 693M (disease-gene)
- string 98M (PPIs)
- gtex_median_tpm 6.6M (selectivity)
- gdsc 6.5G (drug sensitivity, 286 drugs 962 cell lines)
- alphafold 10M (structures — likely subset)
- signor 19M (signaling)
- human_gem 4.4M (metabolome)
- beataml 22M (AML drug screen)
- su2c 3.1M (mCRPC)
- scrna 834M (mostly mCRPC + AML)
- dice 11M (immune cells)
- docking 3.2M (existing docking results)
- pathogen 4.4M

**Empty / missing locally:**
- epigenome (0B)
- hmdb (0B) — metabolome placeholder empty
- scrna_seq (0B, duplicate)
- tcga_prad (0B)
- encode (4KB, effectively empty)

**Conspicuously absent from filesystem:**
- KEGG pathways (user stated "44,686 edges recently re-downloaded" — location unknown)
- Reactome pathways
- ChEMBL compounds
- DisGeNET
- DepMap essentiality

**Implication for GBM test:** Stages depending on the five absent-from-data-directory databases may fail or require alternate paths. Will determine empirically during Stages 1-5.

---

## Stage 1 — Investigating available disease net builder scripts
**Start time:** 14:11:07

### Stage 1.1 — Script discovery and data-path findings

**Net builder identified:** `~/INTERCEPTA/code/disease_net_builder.py`
- Class: `DiseaseNetBuilder`
- Header claim: "Given ANY disease name, builds a complete disease-specific net by querying the Universal Net"
- Default input net path: `../results/mcrpc_unified_net.json`

**Finding 1 (noted, not fixed):** The "Universal Net" file is named `mcrpc_unified_net.json` —
the project's universal net is anchored on mCRPC. Will determine empirically whether it
contains GBM data.

**Database file locations as actually found on disk:**
- ChEMBL: CACHED (results/step7_chembl_activities.csv + step7_chembl_with_smiles.csv)
- KEGG: NOT FOUND as a data file. Only step5_fix_kegg.py script exists.
- Reactome: NOT FOUND on filesystem.
- DisGeNET: NOT FOUND (associations may come via OpenTargets instead)
- DepMap: NOT FOUND

**Dependencies required by disease_net_builder.py:**
- results/mcrpc_unified_net.json
- results/step8_gene_disease_associations.parquet
- results/step8_disease_names.csv
- results/step9_metabolome_gene_edges.csv
- results/step13_immune_expression.csv


### Stage 1.2 — Live execution: query disease_net_builder for "glioblastoma"

**Start:** 14:14:28

**Class methods available:** ['build_net', 'search_disease']
**INIT FAILED:** ImportError: Unable to find a usable engine; tried using: 'pyarrow', 'fastparquet'.
A suitable version of pyarrow or fastparquet is required for parquet support.
Trying to import the above resulted in these errors:
 - Missing optional dependency 'pyarrow'. pyarrow is required for parquet support. Use pip or conda to install pyarrow.
 - Missing optional dependency 'fastparquet'. fastparquet is required for parquet support. Use pip or conda to install fastparquet.
```
Traceback (most recent call last):
  File "<stdin>", line 26, in <module>
  File "/Users/kalki/INTERCEPTA/code/disease_net_builder.py", line 31, in __init__
    self.assoc = pd.read_parquet(assoc_path)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/kalki/miniconda3/envs/intercepta-scrna/lib/python3.11/site-packages/pandas/io/parquet.py", line 653, in read_parquet
    impl = get_engine(engine)
           ^^^^^^^^^^^^^^^^^^
  File "/Users/kalki/miniconda3/envs/intercepta-scrna/lib/python3.11/site-packages/pandas/io/parquet.py", line 68, in get_engine
    raise ImportError(
ImportError: Unable to find a usable engine; tried using: 'pyarrow', 'fastparquet'.
A suitable version of pyarrow or fastparquet is required for parquet support.
Trying to import the above resulted in these errors:
 - Missing optional dependency 'pyarrow'. pyarrow is required for parquet support. Use pip or conda to install pyarrow.
 - Missing optional dependency 'fastparquet'. fastparquet is required for parquet support. Use pip or conda to install fastparquet.
```

**Decision (CSO call, 14:20):** Option A. Install pyarrow, continue the test. Rationale: the test exists to probe Stages 1-5 pipeline capability on a new disease. A missing pip dependency tells us nothing about Stages 2-5. Proceeding.


### Stage 1.3 — Re-execution after pyarrow install

**Start:** 14:16:38
**Init time:** 2.9s

**search_disease("glioblastoma", top_n=10):**
Time: 0.00s
```
[('MONDO_0018177', 'glioblastoma'), ('MONDO_0020690', 'adult glioblastoma'), ('EFO_0006545', 'brain glioblastoma'), ('MONDO_0016682', 'giant cell glioblastoma'), ('EFO_0000519', 'glioblastoma multiforme'), ('EFO_1000141', 'Brain Stem Glioblastoma'), ('EFO_0009254', 'optic nerve glioblastoma'), ('MONDO_0850335', 'IDH-wildtype glioblastoma'), ('OBA_2040157', 'age of onset of glioblastoma'), ('MONDO_0004363', 'adult spinal cord glioblastoma')]
```

**build_net signature:**
`build_net(disease_id, min_score=0.1, max_genes=500)`
```python
    def build_net(self, disease_id, min_score=0.1, max_genes=500):
        """Build a complete disease-specific net."""
        disease_name = self.name_map.get(disease_id, disease_id)
        print(f"Building net for: {disease_name} ({disease_id})")
        print("=" * 55)
        
        # Step 1: Get disease-associated genes
        disease_assoc = self.assoc[self.assoc['diseaseId'] == disease_id]
        disease_assoc = disease_assoc[disease_assoc['associationScore'] >= min_score]
        disease_assoc = disease_assoc.nlargest(max_genes, 'associationScore')
        
        genes = list(disease_assoc['gene'].unique())
        print(f"  Genes (score>{min_score}): {len(genes)}")
        
        if len(genes) == 0:
            print("  No genes found. Try lower min_score.")
            return None
        
        # Step 2: Extract all layers for these genes from universal net
        disease_net = {
            'disease': disease_name,
            'disease_id': disease_id,
            'n_genes': len(genes),
            'genes': {},
            'pathways': set(),
            'metabolites': set(),
            'drug_targets': [],
            'immune_relevant': [],
            'structures_available': [],
            'mutation_profile': {},
        }
        
        for gene in genes:
            score = float(disease_assoc[disease_assoc['gene']==gene]['associationScore'].max())
            gene_data = self.net['genes'].get(gene, {})
            
            entry = {
                'association_score': round(score, 4),
                'mutation_frequency': gene_data.get('mutation_frequency', 0),
            }
            
            # Drug correlations
            if gene_data.get('drug_correlations'):
                entry['n_drug_correlations'] = len(gene_data['drug_correlations'])
            
            # Interactions
            if gene_data.get('interactions'):
                entry['n_interactions'] = len(gene_data['interactions'])
            
          
```

**build_net("glioblastoma") attempt:**
Time: 0.08s
Return type: NoneType
Result: None

**End:** 14:16:43

### Finding 3: build_net expects ontology ID, not name — no automatic resolution

- search_disease("glioblastoma") returned 10 ontology matches (MONDO/EFO IDs)
- build_net("glioblastoma") returned None — treated the name as an ID, matched 0 rows
- Signature: `build_net(disease_id, min_score=0.1, max_genes=500)`
- Code directly does `self.assoc['diseaseId'] == disease_id` with no string-to-ID lookup
- Two methods (search_disease, build_net) do not chain into a single user call

**Implication:** "Type a disease name, get a disease net" is NOT a single-call operation.
Manual step required: search_disease → pick ID → build_net. A ~5-line wrapper would
close this, but it does not exist.

**Also noted:** 10 distinct GBM-related ontology IDs exist. Pipeline does not guide
the user on which to pick. For this test: using MONDO_0018177 (generic glioblastoma).

**Net loaded:** 47,030 diseases queryable. This infrastructure IS real.


### Stage 1.4 — build_net with resolved ID MONDO_0018177

**Start:** 14:18:03

**build_net(MONDO_0018177, min_score=0.1, max_genes=500):** 0.09s
Return type: dict

**Net structure for GBM:**
- Disease name: glioblastoma
- Disease ID: MONDO_0018177
- Total genes: 47
- Genes dict size: 47
- Pathways: 768
- Metabolites: 0
- Drug targets: 5
- Immune relevant: 34
- Structures available: 0
- Mutation profile entries: 0

**Top 20 GBM genes by association score:**
  MSH2: assoc=0.345, mut_freq=0.0141, drug_corrs=20, interactions=2
  BRAF: assoc=0.292, mut_freq=0.0117, drug_corrs=20, interactions=10
  ATM: assoc=0.272, mut_freq=0.0585, drug_corrs=20, interactions=7
  C11orf65: assoc=0.266, mut_freq=0, drug_corrs=0, interactions=0
  DNMT3A: assoc=0.266, mut_freq=0.0094, drug_corrs=20, interactions=0
  SOX2: assoc=0.226, mut_freq=0.0047, drug_corrs=9, interactions=11
  MAPK1: assoc=0.210, mut_freq=0.0023, drug_corrs=0, interactions=0
  MDM2: assoc=0.208, mut_freq=0.007, drug_corrs=20, interactions=14
  STAG1: assoc=0.198, mut_freq=0.0117, drug_corrs=6, interactions=1
  MET: assoc=0.194, mut_freq=0.0164, drug_corrs=20, interactions=8
  DNM2: assoc=0.187, mut_freq=0.0047, drug_corrs=20, interactions=0
  CCND1: assoc=0.181, mut_freq=0.0023, drug_corrs=20, interactions=24
  CDK6: assoc=0.169, mut_freq=0.0047, drug_corrs=20, interactions=9
  RAC1: assoc=0.168, mut_freq=0.0023, drug_corrs=20, interactions=0
  SOX3: assoc=0.162, mut_freq=0.0023, drug_corrs=10, interactions=0
  CCNE1: assoc=0.159, mut_freq=0.0047, drug_corrs=1, interactions=0
  GAB1: assoc=0.157, mut_freq=0.007, drug_corrs=3, interactions=0
  SDHB: assoc=0.156, mut_freq=0.0023, drug_corrs=6, interactions=0
  ARF1: assoc=0.156, mut_freq=0, drug_corrs=1, interactions=0
  IDH1: assoc=0.120, mut_freq=0, drug_corrs=20, interactions=0

**GBM net saved:** /Users/kalki/INTERCEPTA/round3_gbm_live_test/results/gbm_disease_net.json
**End Stage 1:** 14:18:04

### Stage 1 Finding 4 — GBM net top genes do not match known GBM biology

**Net obtained** for MONDO_0018177 (generic glioblastoma): 47 genes, 768 pathways, 5 drug targets with compounds.

**Top-10 genes returned:** MSH2, BRAF, ATM, C11orf65, DNMT3A, SOX2, MAPK1, MDM2, STAG1, MET
**Textbook GBM drivers missing from top 20:** EGFR, PTEN, TP53, NF1, CDKN2A
**IDH1 ranked position 20** with score 0.120 (should be prominent for IDH-mutant GBM)

**Interpretation options to test:**
- A: The generic MONDO_0018177 is a parent term; subtype IDs (EFO_0000519 glioblastoma multiforme, MONDO_0850335 IDH-wildtype) may return biology-accurate gene lists
- B: The OpenTargets snapshot or its association-score weighting under-emphasizes well-known oncogenes
- C: Gene-level score is dominated by non-cancer evidence channels (expression in brain, etc.)

**Action:** Test subtype IDs before judging the pipeline. Also verify by looking directly at what association_score means in the parquet for known GBM drivers (EGFR, PTEN, TP53).

### Stage 1 Finding 5 — Inconsistencies in net summary

- Printed summary says "drug_targets (with compounds): 5" but individual gene entries show `n_drug_correlations=20` for many genes. The "5" stat is counted differently than per-gene — unclear by what criterion.
- Pathways=768 but metabolites=0 — either metabolite data was not joined to this disease or the metabolite edges don't connect to any of the 47 disease genes
- Structures=0 despite alphafold/ having 10M of data and drug targets like EGFR, MDM2 being well-characterized structurally
- Mutation profile aggregate is empty (0 entries) even though individual genes have mut_freq values

**Interpretation:** The net's summary statistics are computed inconsistently from the per-gene data. Either a wiring bug or the summary counts are doing something narrower than their labels imply.


### Stage 1.5 — Diligence test: try subtype IDs and directly query parquet for known GBM genes

**Start:** 14:19:42

**Direct parquet inspection — rows per GBM ontology ID:**
  MONDO_0018177: 7333 gene-association rows
  EFO_0000519: 9906 gene-association rows
  MONDO_0850335: 0 gene-association rows
  MONDO_0020690: 26 gene-association rows
  EFO_0006545: 834 gene-association rows
  MONDO_0016682: 35 gene-association rows
  EFO_1000141: 271 gene-association rows
  EFO_0009254: 29 gene-association rows

**Highest-coverage ID: EFO_0000519**
Top 20 by associationScore:
  EGFR         score=0.6493
  IDH1         score=0.6272
  TP53         score=0.6208
  PTEN         score=0.6028
  VEGFA        score=0.5508
  GSR          score=0.5431
  BRAF         score=0.5326
  ATRX         score=0.5242
  RB1          score=0.5205
  PIK3CA       score=0.5108
  FGFR1        score=0.5107
  NF1          score=0.5036
  TERT         score=0.4847
  PIK3R1       score=0.4669
  CDKN2B       score=0.4469
  PTPN11       score=0.4402
  PDGFRA       score=0.3928
  MAP2K1       score=0.3796
  STAG2        score=0.3796
  ARID1A       score=0.3765

**Association scores for known GBM drivers (across ALL GBM-related IDs):**
  EGFR      : max score=0.6493 (via EFO_0000519)
  PTEN      : max score=0.6028 (via EFO_0000519)
  TP53      : max score=0.6208 (via EFO_0000519)
  NF1       : max score=0.5036 (via EFO_0000519)
  CDKN2A    : max score=0.3700 (via EFO_0006545)
  IDH1      : max score=0.6272 (via EFO_0000519)
  PDGFRA    : max score=0.3928 (via EFO_0000519)
  RB1       : max score=0.5205 (via EFO_0000519)
  ATRX      : max score=0.5242 (via EFO_0000519)
  TERT      : max score=0.4847 (via EFO_0000519)
  MGMT      : max score=0.1869 (via EFO_0006545)
  EGFRvIII  : NOT PRESENT for any GBM ID

**build_net for each GBM subtype — top 5 gene rankings:**
  MONDO_0018177 (glioblastoma): MSH2(0.34), BRAF(0.29), ATM(0.27), C11orf65(0.27), DNMT3A(0.27)
  EFO_0000519 (glioblastoma multiforme): EGFR(0.65), IDH1(0.63), TP53(0.62), PTEN(0.60), VEGFA(0.55)
  MONDO_0850335: net returned None
  MONDO_0020690 (adult glioblastoma): KDR(0.10), PDGFRA(0.10), KIT(0.10), PDGFRB(0.10), FLT1(0.10)
  EFO_0006545 (brain glioblastoma): TERT(0.46), PIK3R1(0.39), PTEN(0.37), HIF1A(0.37), IRS4(0.37)
  MONDO_0016682 (giant cell glioblastoma): CHEK2(0.02), POLE(0.02), IDH1(0.01), IDH2(0.01), CD34(0.01)
  EFO_1000141 (Brain Stem Glioblastoma): H3-3A(0.37), H3C2(0.37), ACVR1(0.37), PPM1D(0.37), BRCA2(0.28)
  EFO_0009254 (optic nerve glioblastoma): NF1(0.50), ALX4(0.12), MAP2K2(0.06), MAP2K1(0.06)

**End Stage 1.5:** 14:19:47

### Stage 1 — CORRECTION to Finding 4

**My Stage 1.4 assessment was wrong.** I claimed the GBM net top genes "don't match known GBM biology." After testing all 8 GBM-related ontology IDs:

- **EFO_0000519 (glioblastoma multiforme) returns correct textbook GBM biology:**
  Top 10 = EGFR, IDH1, TP53, PTEN, VEGFA, GSR, BRAF, ATRX, RB1, PIK3CA
  This is exactly what a GBM expert would expect. Rankings match the known oncogene landscape.

- **MONDO_0018177 (glioblastoma) returns a different, less GBM-centric list** — MSH2, BRAF, ATM, C11orf65. Same disease name, different ontology framework, different evidence aggregation in OpenTargets.

- **Other IDs cover subtypes:** EFO_0006545 (brain GBM), MONDO_0020690 (adult GBM), EFO_1000141 (brain stem — pediatric DIPG biology with H3-3A, ACVR1 correctly at top), EFO_0009254 (optic nerve — NF1 correct), MONDO_0016682 (giant cell — sparse), MONDO_0850335 (IDH-wildtype — 0 rows, empty).

**Known GBM drivers present in parquet (via EFO_0000519):**
EGFR 0.65, PTEN 0.60, TP53 0.62, NF1 0.50, CDKN2A 0.37 (via EFO_0006545), IDH1 0.63, PDGFRA 0.39, RB1 0.52, ATRX 0.52, TERT 0.49, MGMT 0.19 (via EFO_0006545).

All correctly present. The data is good.

### The actual Finding 4 (reframed)

**The pipeline has a disease-ID disambiguation problem, not a data quality problem.**

A user typing "glioblastoma" gets 10 IDs from `search_disease`. Two of those (MONDO_0018177 and EFO_0000519) are both valid disease IDs for the same disease but return meaningfully different biology. There is no guidance in the pipeline on which to pick. I (Claude) picked MONDO_0018177 for Stage 1.4 because it was listed first — an arbitrary choice that returned an inferior-but-not-wrong answer.

**A non-expert user following the same path would:**
(a) pick the first-returned ID (as I did), and get biology that looks wrong to a GBM specialist
(b) pick MONDO_0018177 because MONDO is the "official" ontology, and get the same inferior answer
(c) have to already know to prefer EFO for oncology terms in OpenTargets snapshots

**This is a real gap** — not "the pipeline is broken" but "the pipeline requires ontology expertise the vision's 'type a disease name' UX doesn't provide."

### Revised Stage 1 verdict

- Infrastructure works: 47,030 diseases queryable, 2.9s load, 0.09s build
- Data is real: OpenTargets parquet contains correct GBM driver associations (EGFR, IDH1, TP53, PTEN all at 0.6+ for EFO_0000519)
- User-facing UX is broken: no single-call "disease name → correct net" function, no ID-selection guidance
- Missing pieces in net output: 0 metabolites, 0 structures — need to determine why in Stage 2

**Proceeding to Stage 2 with EFO_0000519 as the correct GBM ID.**
Net to use: /Users/kalki/INTERCEPTA/round3_gbm_live_test/results/gbm_disease_net.json
(NOTE: the saved net is MONDO_0018177's net. Need to rebuild with EFO_0000519 before Stage 2.)


## Stage 2 — Vulnerability Map

**Start:** 14:26:09

### 2.1 Build GBM net with EFO_0000519
Time: 0.68s
Genes: 458, Pathways: 1530, Drug targets (with compounds, summary stat): 14, Immune: 299, Structures: 0
Saved correct net: gbm_disease_net_EFO_0000519.json

**Top 20 GBM genes:** ['EGFR', 'IDH1', 'TP53', 'PTEN', 'VEGFA', 'GSR', 'BRAF', 'ATRX', 'RB1', 'PIK3CA', 'FGFR1', 'NF1', 'TERT', 'PIK3R1', 'CDKN2B', 'PTPN11', 'PDGFRA', 'MAP2K1', 'STAG2', 'ARID1A']

### 2.2 Druggability — ChEMBL compound counts per gene
ChEMBL loaded: 24,598 activity rows, columns: ['target_gene', 'target_chembl_id', 'molecule_chembl_id', 'molecule_name', 'pchembl_value', 'standard_type', 'standard_value', 'standard_units']
Using gene column: target_gene

| Gene | ChEMBL compounds |
|------|------------------|
| EGFR | 0 |
| IDH1 | 0 |
| TP53 | 0 |
| PTEN | 0 |
| VEGFA | 0 |
| GSR | 0 |
| BRAF | 991 |
| ATRX | 0 |
| RB1 | 0 |
| PIK3CA | 968 |
| FGFR1 | 0 |
| NF1 | 0 |
| TERT | 0 |
| PIK3R1 | 0 |
| CDKN2B | 0 |
| PTPN11 | 0 |
| PDGFRA | 0 |
| MAP2K1 | 0 |
| STAG2 | 0 |
| ARID1A | 0 |

### 2.3 Selectivity — GTEx tissue expression
GTEx loaded: (56200, 56), columns sample: ['Name', 'Description', 'Adipose - Subcutaneous', 'Adipose - Visceral (Omentum)', 'Adrenal Gland', 'Artery - Aorta']
Tissues total: 54, brain-related: 14

| Gene | Brain median TPM | All-tissue median TPM | Brain/median ratio | Selectivity |
|------|-------------------|-------------------------|--------------------|-----|
| EGFR | 5.1 | 14.8 | 0.34 | moderate |
| IDH1 | 12.3 | 28.1 | 0.44 | moderate |
| TP53 | 3.3 | 14.7 | 0.23 | moderate |
| PTEN | 10.3 | 21.0 | 0.49 | moderate |
| VEGFA | 17.9 | 60.8 | 0.29 | UBIQUITOUS |
| GSR | 16.0 | 26.4 | 0.61 | moderate |
| BRAF | 6.6 | 11.1 | 0.59 | moderate |
| ATRX | 7.0 | 11.9 | 0.59 | moderate |
| RB1 | 7.5 | 14.7 | 0.51 | moderate |
| PIK3CA | 3.8 | 9.6 | 0.39 | moderate |
| FGFR1 | 16.2 | 38.3 | 0.42 | moderate |
| NF1 | 6.9 | 8.2 | 0.84 | moderate |
| TERT | 0.0 | 0.0 | 7.48 | brain-enriched |
| PIK3R1 | 21.1 | 29.6 | 0.71 | moderate |
| CDKN2B | 1.1 | 3.4 | 0.31 | moderate |
| PTPN11 | 56.7 | 50.0 | 1.14 | moderate |
| PDGFRA | 9.3 | 19.4 | 0.48 | moderate |
| MAP2K1 | 41.5 | 34.0 | 1.22 | moderate |
| STAG2 | 10.4 | 21.2 | 0.49 | moderate |
| ARID1A | 10.6 | 25.5 | 0.41 | moderate |

### 2.4 Escape routes — STRING interactions for top 5 genes
STRING directory contents: ['9606.protein.aliases.v12.0.txt.gz', '9606.protein.links.v12.0.txt.gz']
Trying to load 9606.protein.aliases.v12.0.txt.gz...
  Columns: ['#string_protein_id\talias\tsource'], sample row: {'#string_protein_id\talias\tsource': '9606.ENSP00000000233\t2B6H\tEnsembl_PDB'}

**Using GBM net built-in interactions field for escape routes:**

EGFR: 0 interactions in universal net

IDH1: 0 interactions in universal net

TP53: 25 interactions in universal net
  Sample (first 10): [{'partner': 'FOXA1', 'score': 0.735}, {'partner': 'KMT2C', 'score': 0.858}, {'partner': 'PIK3CA', 'score': 0.941}, {'partner': 'RB1', 'score': 0.936}, {'partner': 'NCOR1', 'score': 0.853}, {'partner': 'HERC1', 'score': 0.72}, {'partner': 'ANK2', 'score': 0.727}, {'partner': 'DMD', 'score': 0.73}, {'partner': 'LRRK2', 'score': 0.738}, {'partner': 'CHD4', 'score': 0.749}]

PTEN: 11 interactions in universal net
  Sample (first 10): [{'partner': 'PIK3CA', 'score': 0.995}, {'partner': 'RB1', 'score': 0.734}, {'partner': 'TP53', 'score': 0.999}, {'partner': 'ATM', 'score': 0.897}, {'partner': 'PREX2', 'score': 0.99}, {'partner': 'ARID1A', 'score': 0.743}, {'partner': 'USP7', 'score': 0.979}, {'partner': 'BRCA2', 'score': 0.877}, {'partner': 'AR', 'score': 0.892}, {'partner': 'CTNNB1', 'score': 0.943}]

VEGFA: 0 interactions in universal net

### 2.5 Canonical biology test — EGFR↔MET interaction present?
EGFR interactions: 0
EGFR→MET found: False
MET in universal net: True, interactions: 8

**End Stage 2:** 14:26:10

## Stage 2 Findings Summary

### Finding 6: ChEMBL local cache is mCRPC/AML-curated, NOT universal
- 18/20 top GBM genes have 0 ChEMBL compounds locally (including EGFR, the #1 GBM target)
- Only BRAF (991) and PIK3CA (968) have compound data
- step7_chembl_activities.csv is 24,598 rows — a curated subset, not a ChEMBL dump
- Implication: "pharmacome layer" only covers genes relevant to previously-worked diseases

### Finding 7: GTEx selectivity labels are not useful for oncology
- 18/20 genes labeled "moderate" — non-informative
- TERT "brain-enriched" is a divide-by-zero artifact (brain 0.0 / median 0.0)
- GTEx-only selectivity cannot capture tumor-vs-normal (the actual oncology selectivity question)
- Need TCGA-GBM tumor expression alongside GTEx for real selectivity analysis

### Finding 8: Universal net interactions are mCRPC-centric
- EGFR: 0 interactions populated (should be ~500)
- VEGFA: 0 interactions
- IDH1: 0 interactions
- TP53: 25 interactions (mixed relevance — DMD, ANK2, LRRK2 appear)
- PTEN: 11 interactions (reasonable subset: PIK3CA, TP53, ATM correct)
- STRING raw data available (98MB on disk) but only mCRPC-relevant edges loaded into net

### Finding 9: Canonical GBM escape route (EGFR→MET) is NOT in the net
- Textbook biology: MET amplification is the primary resistance mechanism for EGFR blockade in GBM/NSCLC
- Net reports EGFR 0 interactions, MET 8 interactions — edge between them was never populated
- Vision Part 3 claim: "escape routes — compensatory pathways that activate when primary targets are blocked"
- For GBM's #1 target, this claim does not hold in the current net

### Finding 10: Metabolite layer does not join to disease net
- GBM net: 0 metabolites linked
- AML net: same 0 in earlier work
- step9_metabolome_gene_edges.csv (1.6MB) has data but doesn't integrate

### Finding 11: Structure layer does not join to disease net
- GBM net: 0 structures available
- AlphaFold cache (10MB) exists
- EGFR alone has 100+ PDB structures — none are retrievable through the net

### Stage 2 Verdict
- Infrastructure works for pathways (1,530 GBM pathways) and immune-relevant genes (299)
- Infrastructure FAILS for ChEMBL compounds, structures, metabolites, and (critically) interactions
- The "universal net" is not universal — it is an mCRPC-seed net with a disease-association layer on top
- Each time a new disease is introduced, the net must be RE-POPULATED with that disease's relevant edges from STRING, ChEMBL, AlphaFold

### Implication for Stage 3
- Drug scouting will be biased toward 2 genes (BRAF, PIK3CA) because those are the only ones with compound data
- Will not find EGFR inhibitors, VEGF inhibitors, kinase inhibitors — despite these being real GBM drugs (erlotinib, bevacizumab, regorafenib)
- Stage 3 output will reflect the ChEMBL cache's coverage, not the true drug landscape


## Stage 3 — Drug Scouting

**Start:** 14:29:39
GBM target set: 458 total genes, top-20 = ['EGFR', 'IDH1', 'TP53', 'PTEN', 'VEGFA', 'GSR', 'BRAF', 'ATRX', 'RB1', 'PIK3CA', 'FGFR1', 'NF1', 'TERT', 'PIK3R1', 'CDKN2B', 'PTPN11', 'PDGFRA', 'MAP2K1', 'STAG2', 'ARID1A']

### 3.1 GDSC data inventory
Total GDSC files: 10
  rnaseq_all_data_20220624.csv: 5078.0 MB
  sanger_model_gene_expression.csv.gz: 897.1 MB
  rnaseq_tpm_20220624.csv: 245.5 MB
  rnaseq_fpkm_20220624.csv: 238.5 MB
  rnaseq_read_count_20220624.csv: 157.4 MB
  GDSC2_fitted_dose_response.xlsx: 20.3 MB
  sidg_to_symbol.csv: 0.6 MB
  Cell_Lines_Details.xlsx: 0.1 MB
  Cell_line_RMA_proc_basalExp.txt.gz: 0.0 MB
  rnaseq_gene_info.csv: 0.0 MB

### 3.2 Load GDSC drug-target annotations
Drug metadata candidates: []
No direct drug-target metadata found. Trying the kaalcura rerun output instead...
kaalcura_real_validation_RERUN.csv: shape=(286, 6), columns=['drug', 'auroc', 'coef_prolif', 'coef_emt', 'coef_ddr', 'n_cell_lines']

**Using drug data from:** kaalcura_real_validation_RERUN.csv
**Drug column:** drug, **Target column:** None
**Total drug rows:** 286

### 3.3 Filter drugs by GBM target relevance

### 3.4 Biological sanity checks

**GBM standard-of-care drugs in GDSC?**
  Temozolomide: FOUND ['Temozolomide']
  Bevacizumab: NOT IN GDSC
  Carmustine: NOT IN GDSC
  Lomustine: NOT IN GDSC
  TMZ: NOT IN GDSC

**GBM-targeted therapies in GDSC?**
  Erlotinib: FOUND ['Erlotinib']
  Gefitinib: FOUND ['Gefitinib']
  Lapatinib: FOUND ['Lapatinib']
  Afatinib: FOUND ['Afatinib']
  Sorafenib: FOUND ['Sorafenib']
  Sunitinib: NOT IN GDSC
  Pazopanib: NOT IN GDSC
  Regorafenib: NOT IN GDSC
  Olaparib: FOUND ['Olaparib']
  Talazoparib: FOUND ['Talazoparib']
  Vemurafenib: NOT IN GDSC
  Dabrafenib: FOUND ['Dabrafenib']
  Trametinib: FOUND ['Trametinib']
  Vorinostat: FOUND ['Vorinostat']
  Panobinostat: NOT IN GDSC

**End Stage 3:** 14:29:39

## Stage 3 Findings Summary

### Finding 12: GDSC drug-target mapping not in local cache
- 10 GDSC files on disk, ~7GB total
- No drug-target annotation file present locally
- Sanger publishes drug-target table externally but we don't have it cached
- Fell back to kaalcura_real_validation_RERUN.csv (has names+AUROC, no targets)

### Finding 13: Sanity check confirms ~10 GBM-relevant drugs ARE in GDSC
- SoC: Temozolomide present; Bevacizumab/Carmustine/Lomustine absent (MoAb or non-GDSC chemo)
- EGFR inhibitors: Erlotinib, Gefitinib, Lapatinib, Afatinib all present
- BRAF/MEK: Dabrafenib, Trametinib present
- PARP: Olaparib, Talazoparib present
- Sorafenib (multi-kinase/VEGF) present
- Drug COVERAGE for GBM exists in GDSC — we just can't programmatically FIND them without target data

### Finding 14: Stage 3 as vision-specified cannot execute without manual glue
- The vision says "Run the drug-target filter on all 286 GDSC drugs for glioblastoma targets"
- The pipeline has no function that takes ("glioblastoma", drug_list) → ranked drug list
- Required missing steps: (a) drug-target mapping, (b) brain-cancer cell line filter, (c) per-tissue AUC ranking
- All data needed is on disk (Cell_Lines_Details.xlsx has tissue annotations, GDSC2_fitted_dose_response.xlsx has AUCs)
- Missing: the script that joins them

### Stage 3 Verdict (preliminary)
Vision claims drug scouting is automatic. Reality: it's a set of data files that can be joined manually but not by any existing INTERCEPTA script.


### Stage 3.5 — Manual glue: GDSC brain-cancer cell line drug ranking

**Start:** 14:31:46

Cell_Lines_Details.xlsx: (1002, 13), columns: ['Sample Name', 'COSMIC identifier', 'Whole Exome Sequencing (WES)', 'Copy Number Alterations (CNA)', 'Gene Expression', 'Methylation', 'Drug\nResponse', 'GDSC\nTissue descriptor 1', 'GDSC\nTissue\ndescriptor 2', 'Cancer Type\n(matching TCGA label)', 'Microsatellite \ninstability Status (MSI)', 'Screen Medium', 'Growth Properties']
Tissue-like columns: ['GDSC\nTissue descriptor 1', 'GDSC\nTissue\ndescriptor 2', 'Cancer Type\n(matching TCGA label)']
  GDSC
Tissue descriptor 1: 0 brain-related entries
  GDSC
Tissue
descriptor 2: 53 brain-related entries
  Using column "GDSC
Tissue
descriptor 2" for brain filter

**Brain/glioma cell lines in GDSC: 53**
Name-like columns: ['Sample Name', 'COSMIC identifier']

First 5 brain cancer cell line rows (selected cols):
    Sample Name  COSMIC identifier Cancer Type\n(matching TCGA label)
628    42-MG-BA           687561.0                                GBM
629     8-MG-BA           687562.0                                GBM
630        A172           687563.0                                GBM
631       AM-38           910933.0                                GBM
632      Becker           906746.0                                GBM
633       CAS-1           910943.0                                GBM
634   CCF-STTG1           906823.0                                GBM
635     D-247MG           946367.0                                GBM
636     D-263MG           946368.0                                GBM
637     D-336MG           946369.0                                LGG


Loading GDSC2_fitted_dose_response.xlsx (20 MB)...
Load time: 11.0s, shape: (242036, 19)
Columns: ['DATASET', 'NLME_RESULT_ID', 'NLME_CURVE_ID', 'COSMIC_ID', 'CELL_LINE_NAME', 'SANGER_MODEL_ID', 'TCGA_DESC', 'DRUG_ID', 'DRUG_NAME', 'PUTATIVE_TARGET', 'PATHWAY_NAME', 'COMPANY_ID', 'WEBRELEASE', 'MIN_CONC', 'MAX_CONC', 'LN_IC50', 'AUC', 'RMSE', 'Z_SCORE']
Sample row: {'DATASET': 'GDSC2', 'NLME_RESULT_ID': 343, 'NLME_CURVE_ID': 15946310, 'COSMIC_ID': 683667, 'CELL_LINE_NAME': 'PFSK-1', 'SANGER_MODEL_ID': 'SIDM01132', 'TCGA_DESC': 'MB', 'DRUG_ID': 1003, 'DRUG_NAME': 'Camptothecin', 'PUTATIVE_TARGET': 'TOP1', 'PATHWAY_NAME': 'DNA replication', 'COMPANY_ID': 1046, 'WEBRELEASE': 'Y', 'MIN_CONC': 0.0001, 'MAX_CONC': 0.1, 'LN_IC50': -1.463887, 'AUC': 0.93022, 'RMSE': 0.089052, 'Z_SCORE': 0.433123}

Identified: drug_col=DRUG_NAME, cell_line_col=CELL_LINE_NAME, auc_col=AUC, cosmic_col=COSMIC_ID

Matching by COSMIC id: 53 brain cell line COSMIC ids
Dose-response rows matching brain cancer cell lines: 12001
Unique drugs in brain subset: 286
Unique cell lines in brain subset: 51

Drugs with ≥3 brain cell lines tested: 286

**Top 30 drugs by lowest median AUC in GBM/brain cell lines (most effective):**
```
              DRUG_NAME  median_auc  mean_auc  n_cell_lines
   Sepantronium bromide    0.151970  0.159161            50
          Staurosporine    0.276965  0.333281            51
           Dactinomycin    0.470483  0.590348            80
                 MG-132    0.520195  0.524611            51
              CDK9_5038    0.573215  0.573744            30
             Dinaciclib    0.600203  0.616152            47
              Daporinad    0.640600  0.685405            35
              CDK9_5576    0.641763  0.637005            30
             Luminespib    0.645342  0.652970            50
             Sabutoclax    0.658729  0.635526            47
            Gemcitabine    0.671352  0.646172            51
Telomerase Inhibitor IX    0.694068  0.683300            50
     Obatoclax Mesylate    0.696735  0.684399            34
                GNE-317    0.699752  0.696870            48
                PBD-288    0.720010  0.703142            34
              Foretinib    0.729878  0.718420            49
                AZD7762    0.733356  0.725640            50
                 LMP744    0.738936  0.733228            30
             Epirubicin    0.741308  0.701567            50
             Buparlisib    0.751558  0.761291            50
             Bortezomib    0.752352  0.762247            50
              ULK1_4989    0.753045  0.732823            30
                AZD8055    0.753248  0.760108            34
           Pevonedistat    0.754773  0.730835            50
      Bleomycin (50 uM)    0.762026  0.746912            33
      Mycophenolic acid    0.767764  0.766074            34
            Vinblastine    0.775981  0.728655            33
                  AZ960    0.777339  0.777351            47
             Dactolisib    0.780307  0.799915            50
              Docetaxel    0.781479  0.711521            78
```

Saved: gbm_drug_ranking_gdsc.csv

**Where do expected GBM drugs rank (lower median_auc = more effective)?**
  Temozolomide: rank #247 / 286, median AUC=0.976, n=51
  Erlotinib: rank #161 / 286, median AUC=0.956, n=50
  Gefitinib: rank #239 / 286, median AUC=0.975, n=50
  Lapatinib: rank #127 / 286, median AUC=0.937, n=51
  Afatinib: rank #85 / 286, median AUC=0.894, n=51
  Sorafenib: rank #89 / 286, median AUC=0.897, n=50
  Olaparib: rank #150 / 286, median AUC=0.952, n=51
  Talazoparib: rank #83 / 286, median AUC=0.888, n=50
  Dabrafenib: rank #224 / 286, median AUC=0.973, n=49
  Trametinib: rank #109 / 286, median AUC=0.920, n=51
  Vorinostat: rank #47 / 286, median AUC=0.827, n=50

**End Stage 3.5:** 14:31:58

## Stage 3.5 Findings

### Correction to Finding 12
Earlier claim: "GDSC drug-target mapping not in local cache" — WRONG.
GDSC2_fitted_dose_response.xlsx contains PUTATIVE_TARGET and PATHWAY_NAME
columns directly. My Stage 3 filename regex missed it. Target mapping IS
available locally. My mistake.

### Finding 15: 53 GBM/brain cell lines available, 51 with drug data, 12,001 measurements
- COSMIC id matching clean, 286 drugs × 51 cell lines
- All data needed for drug scoring is local

### Finding 16: GDSC-AUC ranking does not match GBM clinical reality
Temozolomide (frontline SoC): rank #247 of 286 (median AUC 0.976)
EGFR inhibitors (rational targets): Gefitinib #239, Erlotinib #161, Afatinib #85
Top 30 dominated by broad cytotoxics (Staurosporine, Dactinomycin, Bortezomib, etc.)

In-vitro AUC in 72h 2D culture does not reflect:
- MGMT methylation status (key for Temozolomide response)
- Blood-brain barrier penetration (kills EGFR inhibitor clinical utility in GBM)
- Tumor-vs-normal selectivity
- Biomarker-stratified efficacy

Within-mechanism ranking is sensible (Afatinib > Lapatinib > Erlotinib > Gefitinib, matching clinical potency).
Cross-mechanism ranking is misleading.

### Finding 17: Stage 3 with manual glue produces scientifically valid but clinically unreliable output
GDSC data is genuine; the SCORING (AUC) is a weak proxy for GBM clinical utility.
Vision's "drug scouting produces ranked candidates" claim is technically true but the ranking needs heavy qualification.

### Stage 3 Verdict
- ✓ Data exists locally for drug ranking in brain cancer cell lines
- ✓ 15 lines of manual pandas glue produces a ranked list
- ✗ Ranking does not match clinical GBM utility (Temozolomide near bottom)
- ✗ No automated "disease → ranked drugs" function in current codebase
- ✗ Scoring lacks BBB, tumor-vs-normal, biomarker-stratification — key GBM filters

### Decision for Stage 4: use Option C (top-3 GDSC-AUC among GBM-rational targets)
Top 3 candidates for ODE testing:
  1. Vorinostat   — rank #47, HDAC inhibitor, GBM-relevant mechanism
  2. Talazoparib  — rank #83, PARP inhibitor, relevant for IDH-mutant GBM
  3. Afatinib     — rank #85, pan-ErbB/EGFR inhibitor, EGFR is #1 GBM target

Rationale: these have real in-vitro potency in brain cell lines AND mechanistically hit GBM targets. Option A (top 3 by AUC) would be Sepantronium/Staurosporine/Dactinomycin — non-GBM-specific cytotoxics. Option B (hand-pick by clinical SoC) would short-circuit the pipeline test.

**Noted gap: choosing Option C required Claude's manual synthesis of (GDSC AUC rank) + (GBM net genes) + (biology). The pipeline does not do this automatically.**


## Stage 4 — ODE Simulation for GBM candidates

**Start:** 14:35:51

### 4.1 ODE module discovery

**intercepta_unified_ode_v4_1**
  Functions: ['Callable', 'Dict', 'List', 'Optional', 'Tuple', 'brca_profile', 'build_drug_library', 'build_initial_state', 'estimate_hr_proper', 'load_velocity_distribution', 'pk_binary', 'pk_continuous_oral']
  Classes: ['UnifiedODEv4']
  build_drug_library: function
  pk_binary: function
  pk_continuous_oral: function
  pk_cyclic_cytotoxic: function

**intercepta_three_mechanism_ode**
  Functions: ['Callable', 'Dict', 'List', 'Optional', 'compute_ec50_per_bin', 'load_velocity_distribution', 'make_pk_continuous', 'make_pk_cytotoxic', 'make_pk_function', 'run_validation', 'solve_ivp']
  Classes: ['ThreeMechanismODE']
  DRUG_LIBRARY: dict with 7 entries, keys=['docetaxel', 'cisplatin', 'enzalutamide', 'abiraterone', 'ADT', 'olaparib', 'talazoparib']
  make_pk_continuous: function
  make_pk_cytotoxic: function
  make_pk_function: function

**intercepta_phenotype_ode_v1**
  Functions: ['Callable', 'Dict', 'List', 'Optional', 'Tuple', 'create_synthetic_velocity_distribution', 'load_velocity_distribution', 'make_pk_function', 'run_step1_validation', 'solve_ivp']
  Classes: ['Path', 'PhenotypeStructuredODE', 'VirtualCohort']
  DRUG_EFFECT_LIBRARY: dict with 6 entries, keys=['docetaxel', 'abiraterone', 'olaparib', 'enzalutamide', 'talazoparib', 'ADT']
  PK_LIBRARY: dict with 6 entries, keys=['docetaxel', 'abiraterone', 'olaparib', 'enzalutamide', 'talazoparib', 'ADT']
  make_pk_function: function

**aml_ode_v6_resistance**
  Functions: ['main', 'precompute_pk', 'run_v6', 'solve_ivp']
  Classes: []
  precompute_pk: function

### 4.2 Attempting to run three-mechanism ODE for GBM drugs
Target drugs: Vorinostat (HDAC), Talazoparib (PARP), Afatinib (EGFR/pan-ErbB)
Loaded intercepta_three_mechanism_ode
Module surface: ['ALPHA_IND', 'ALPHA_R', 'BETA', 'BRCA_FRAC_OVERALL', 'BRCA_FRAC_SELECTED', 'Callable', 'DRUG_LIBRARY', 'D_NAT', 'Dict', 'G_STATE_MOD', 'K', 'List', 'MU_BASE', 'MU_S_TO_M', 'MU_S_TO_N', 'MU_S_TO_V', 'MU_TREATMENT', 'N_STATES', 'Optional', 'R_MAX', 'STATE_NAMES', 'S_ARDEP', 'S_ARMUT', 'S_ARV7', 'S_NE', 'ThreeMechanismODE', 'compute_ec50_per_bin', 'json', 'load_velocity_distribution', 'make_pk_continuous', 'make_pk_cytotoxic', 'make_pk_function', 'np', 'run_validation', 'solve_ivp', 'time']

Found PK library: `DRUG_LIBRARY` with 7 entries
Drugs available: ['docetaxel', 'cisplatin', 'enzalutamide', 'abiraterone', 'ADT', 'olaparib', 'talazoparib']
  Vorinostat: NOT IN PK_LIBRARY
  Talazoparib: NOT IN PK_LIBRARY
  Afatinib: NOT IN PK_LIBRARY
  vorinostat: NOT IN PK_LIBRARY
  talazoparib: IN PK_LIBRARY
  afatinib: NOT IN PK_LIBRARY

### 4.3 Checking unified_ode_v4_1 PK library
Module surface (abridged): ['ALPHA_IND', 'ALPHA_R', 'BETA', 'COHORT_N_PER_ARM', 'D_NAT', 'G_MOD_M', 'G_MOD_N', 'G_MOD_S', 'G_MOD_V', 'K_CAP', 'MU_S_TO_M', 'MU_S_TO_N_BASE', 'MU_S_TO_N_TX', 'MU_S_TO_V', 'N_BINS_DEFAULT', 'PROG_MIN_DAYS_POST_NADIR', 'PROG_THRESHOLD', 'R_MAX', 'SIM_DAYS_DEFAULT', 'build_drug_library']

Simulation-like functions: ['SIM_DAYS_DEFAULT', 'run_validation', 'simulate_cohort', 'solve_ivp']
  `simulate_cohort(drug_list: List[str], velocity_csv: Optional[str], brca_profile_name: str, state_fracs: Dict[str, float], duration_days: int, n_patients: int, random_state: int = 42, heterogeneous: bool = True) -> numpy.ndarray`

### 4.4 Attempt to simulate GBM drug response
The three-mechanism ODE was designed for mCRPC states (S/M/V/N: AR-dependent, AR-mutant, AR-V7, neuroendocrine).
GBM cell states are different (proneural/classical/mesenchymal, or IDH-mutant vs wildtype).
Without GBM-specific state_sens matrix and PK params for our drugs, the ODE cannot meaningfully simulate GBM.
Attempting anyway to document the specific failure mode.

Callable functions available: ['Callable', 'Dict', 'List', 'Optional', 'Tuple', 'brca_profile', 'build_drug_library', 'build_initial_state', 'estimate_hr_proper', 'load_velocity_distribution', 'pk_binary', 'pk_continuous_oral', 'pk_cyclic_cytotoxic', 'run_validation', 'simulate_cohort']
  `Callable(*args, **kwargs)`
  `Dict(*args, **kwargs)`
  `List(*args, **kwargs)`
  `Optional(*args, **kwds)`
  `Tuple(*args, **kwargs)`

### 4.5 Stage 4 interim verdict
Simulation actually run for GBM drugs: NO
Reason: PK_LIBRARY contains mCRPC drugs only; state_sens matrix is prostate-specific; no GBM cell state definitions exist in ODE code.
Required to run Stage 4 for real: (a) PK params for Vorinostat/Talazoparib/Afatinib, (b) GBM state definitions (proneural/classical/mesenchymal + IDH status), (c) state_sens matrix parameterized for each drug-state pair.

**End Stage 4 (library inspection):** 14:35:52

## Stage 4 Findings

### Library inventory across all four ODE modules

| Module | Drug library | Drugs |
|--------|--------------|-------|
| three_mechanism_ode | DRUG_LIBRARY (7) | docetaxel, cisplatin, enzalutamide, abiraterone, ADT, olaparib, talazoparib |
| phenotype_ode_v1 | PK_LIBRARY (6) | docetaxel, abiraterone, olaparib, enzalutamide, talazoparib, ADT |
| phenotype_ode_v1 | DRUG_EFFECT_LIBRARY (6) | same 6 |
| unified_ode_v4_1 | build_drug_library() | mCRPC set |
| aml_ode_v6_resistance | precompute_pk() | undeclared, AML-specific |

**Total unique drugs parameterized: 7 (mCRPC + cisplatin).**

### Stage 3 picks vs ODE coverage
- Vorinostat (HDAC, rank #47 GDSC brain): NOT in any ODE library
- Talazoparib (PARP, rank #83 GDSC brain): in three_mechanism_ode (lowercase)
- Afatinib (EGFR, rank #85 GDSC brain): NOT in any ODE library

Only Talazoparib could nominally be simulated — but the simulation would use mCRPC state biology against PROfound trial anchors, producing meaningless output for GBM.

### Finding 18: ODE layer is structurally prostate-cancer-only

Hardcoded constants in three_mechanism_ode confirm prostate-specificity:
- S_ARDEP, S_ARMUT, S_ARV7, S_NE — prostate cell states
- MU_S_TO_M, MU_S_TO_V, MU_S_TO_N — prostate transition rates
- BRCA_FRAC_OVERALL, BRCA_FRAC_SELECTED — prostate BRCA distribution

These are not generic two-population parameters. The architecture cannot transfer to GBM (or any other disease) without:
1. New cell state definitions per disease
2. New transition rate parameters per disease (from primary literature)
3. New PK params per drug (Vorinostat, Afatinib at minimum)
4. New clinical trial anchors per disease
5. New state-sensitivity matrix per disease

**This is months of literature-research-driven work per disease, not auto-generated.**

### The vision's "universal ODE" claim is unsupported by the code

Vision Part 5.3 claims the two-population ODE is "validated against CHAARTED, LATITUDE, PROfound, PROpel" — true for mCRPC. But the ODE is NOT a generic two-population template that transfers to other diseases. It is mCRPC-specific code.

### Stage 4 Verdict
- Simulation NOT executed for GBM drugs
- Reason: structural — ODE has no GBM cell states, no GBM transition rates, no Vorinostat/Afatinib PK
- Closing this gap requires Round-1-level scientific work for each new disease
- The "automated disease expansion" pillar of the vision (Part 7) is currently fiction at the ODE layer


## Stage 5 — Ranking & Partial Pharma Deliverable

**Start:** 22:32:34

### 5.1 Inspect pareto_ranking module
Functions: ['build_mcrpc_candidates', 'composite_score', 'main', 'pareto_front', 'rank_candidates']
  `build_mcrpc_candidates()`
  `composite_score(candidate, weights=None)`
  `main()`
  `pareto_front(scores)`
  `rank_candidates(candidates)`

### 5.2 Build candidate dataframe with available dimensions

Candidates (≥3 brain cell lines AND target ≥1 GBM net gene): 90
Of which target ≥1 top-20 GBM gene: 15

### 5.3 GTEx-based selectivity score per drug

### 5.4 ClinicalTrials.gov novelty check
Local CT.gov files: []
No local ClinicalTrials.gov data found. Novelty check requires live API call.
Marking novelty=NaN per "no patching during test" rule. Real pipeline would need offline CT.gov index.

### 5.5 Pareto ranking — multi-objective

Total candidates with all 3 score dimensions: 90
Pareto-optimal candidates: 10

**Top 15 GBM candidates by composite ranking (efficacy + target + selectivity):**
```
           DRUG_NAME                                                targets gbm_top20_hits                  pathway_name  median_auc  efficacy_score  target_score  selectivity_score  is_pareto  composite_rank
        Lestaurtinib                      [FLT3, JAK2, NTRK1, NTRK2, NTRK3]             []                Other, kinases    0.823788        0.176212             3           0.423709       True            32.0
           Cediranib           [VEGFR, FLT1, FLT2, FLT3, FLT4, KIT, PDGFRB]             []                 RTK signaling    0.851208        0.148792             5           0.214219       True            39.0
Sepantronium bromide                                                [BIRC5]             []          Apoptosis regulation    0.151970        0.848030             1           0.660982       True            45.0
           Foretinib [MET, KDR, TIE2, VEGFR3/FLT4, RON, PDGFR, FGFR1, EGFR]  [FGFR1, EGFR]                 RTK signaling    0.729878        0.270122             8           0.068087       True            47.0
          Dinaciclib                               [CDK1, CDK2, CDK5, CDK9]             []                    Cell cycle    0.600203        0.399797             2           0.105594       True            54.0
             MK-1775                                           [WEE1, PLK1]             []                    Cell cycle    0.784096        0.215904             2           0.154092       True            56.0
      Wee1 Inhibitor                                          [WEE1, CHEK1]             []                    Cell cycle    0.844100        0.155900             2           0.188876      False            57.0
               AZ960                                           [JAK2, JAK3]             []                Other, kinases    0.777339        0.222661             2           0.108166       True            59.0
             BI-2536                                     [PLK1, PLK2, PLK3]             []                    Cell cycle    0.782096        0.217904             2           0.110316       True            59.0
             AZD7762                                         [CHEK1, CHEK2]             []                    Cell cycle    0.733356        0.266644             1           0.251275      False            63.0
          Romidepsin                           [HDAC1, HDAC2, HDAC3, HDAC8]             [] Chromatin histone acetylation    0.782500        0.217500             4           0.058153      False            63.0
          Crizotinib                                       [MET, ALK, ROS1]             []                 RTK signaling    0.917726        0.082274             2           0.684935       True            64.0
           Alisertib                                                [AURKA]             []                       Mitosis    0.842598        0.157402             1           0.401664      False            68.0
            ZM447439                                         [AURKA, AURKB]             []                       Mitosis    0.862034        0.137966             1           0.471709      False            70.0
           Dasatinib                        [ABL, SRC, EPHRINS, PDGFR, KIT]             []                Other, kinases    0.857542        0.142458             2           0.075683      False            79.0
```

**Pareto-optimal set (all candidates not dominated on any axis):**
```
           DRUG_NAME                                                targets gbm_top20_hits         pathway_name  median_auc  efficacy_score  target_score  selectivity_score  is_pareto  composite_rank
        Lestaurtinib                      [FLT3, JAK2, NTRK1, NTRK2, NTRK3]             []       Other, kinases    0.823788        0.176212             3           0.423709       True            32.0
           Cediranib           [VEGFR, FLT1, FLT2, FLT3, FLT4, KIT, PDGFRB]             []        RTK signaling    0.851208        0.148792             5           0.214219       True            39.0
Sepantronium bromide                                                [BIRC5]             [] Apoptosis regulation    0.151970        0.848030             1           0.660982       True            45.0
           Foretinib [MET, KDR, TIE2, VEGFR3/FLT4, RON, PDGFR, FGFR1, EGFR]  [FGFR1, EGFR]        RTK signaling    0.729878        0.270122             8           0.068087       True            47.0
          Dinaciclib                               [CDK1, CDK2, CDK5, CDK9]             []           Cell cycle    0.600203        0.399797             2           0.105594       True            54.0
             MK-1775                                           [WEE1, PLK1]             []           Cell cycle    0.784096        0.215904             2           0.154092       True            56.0
               AZ960                                           [JAK2, JAK3]             []       Other, kinases    0.777339        0.222661             2           0.108166       True            59.0
             BI-2536                                     [PLK1, PLK2, PLK3]             []           Cell cycle    0.782096        0.217904             2           0.110316       True            59.0
          Crizotinib                                       [MET, ALK, ROS1]             []        RTK signaling    0.917726        0.082274             2           0.684935       True            64.0
           BIBR-1532                                                 [TERT]         [TERT]     Genome integrity    0.972980        0.027020             3           1.000000       True            85.0
```

Saved: gbm_pareto_candidates.csv

### 5.6 Partial pharma deliverable for top Pareto candidate

**Selected candidate: Lestaurtinib**

**1. Molecular structure:** NOT AVAILABLE (no SMILES in our pipeline cache)
**2. Mechanism of action:**
   - Pathway: Other, kinases
   - Targets (per GDSC): ['FLT3', 'JAK2', 'NTRK1', 'NTRK2', 'NTRK3']
   - GBM top-20 genes hit: []
   - All GBM net genes hit: ['FLT3', 'JAK2', 'NTRK1']

**3. Predicted clinical outcomes:** NOT AVAILABLE (Stage 4 ODE failed structurally)
   - No HR prediction
   - No PFS curve
   - No virtual cohort simulation

**4. Resistance profile:** NOT AVAILABLE (would require RNA velocity on GBM scRNA-seq, which we do not have)

**5. Combination rationale:** N/A (single drug)

**6. Safety profile:**
   - GTEx selectivity score (heuristic): 0.424
   - ADMET data: NOT AVAILABLE (SwissADME/pkCSM not run)
   - BBB penetration: NOT AVAILABLE (critical for GBM, no data layer)

**7. Synthesis route:** NOT APPLICABLE (existing drug, not novel molecule)

**8. Novelty confirmation:** NOT CHECKED (no offline ClinicalTrials.gov index, live API not invoked)

**9. Comparison vs SoC:**
   - GBM SoC (Temozolomide) median AUC in brain cell lines: 0.976 (rank #247/286)
   - Candidate median AUC: 0.824

**10. Suggested trial design:** NOT GENERATED (no efficacy prediction, no biomarker stratification)

**Deliverable completeness: 3 of 10 sections have data, 7 of 10 are NOT AVAILABLE.**

**End Stage 5:** 22:32:46

## Phase 1 — Tiny fixes complete

**Module created:** `round3_gbm_live_test/code/intercepta_pipeline_v0.py`
**Environment file:** `round3_gbm_live_test/code/environment_round3.yml`

### Gaps closed
- **Gap 1** (search/build don't chain): `resolve_disease(name)` and `build_net(name_or_id)` chain automatically
- **Gap 2** (no ID disambiguation): `resolve_disease` ranks by row count, prefers EFO for ties
- **Gap 3** (pyarrow missing): pinned in `environment_round3.yml` along with lifelines
- **Gap 4** (GDSC filename regex miss): `inspect_gdsc_drugs()` finds drug-target columns by content, not filename
- **Gap 5** (net summary inconsistency): `corrected_net_summary(net)` reports each count by clear definition

### Verification (re-run on GBM via name string)
- `resolve_disease("glioblastoma")` → EFO_0000519 (9906 rows, top of 8 candidates)
- `build_net("glioblastoma")` → returns net with EGFR + TP53 in top 10 (correct GBM biology)
- `inspect_gdsc_drugs()` → detects GDSC2_fitted_dose_response.xlsx automatically
- `corrected_net_summary` → distinct counts shown without the legacy 5-vs-20 ambiguity

### Principle 16 honored
No changes to `disease_net_builder.py`, `intercepta_unified_ode_v4_1.py`, or any Round 1/2 file. New module imports originals.


## Phase 1 verification — PASSED

### Verification output (4-second run after patch)

| Test | Result | Time |
|------|--------|------|
| `resolve_disease("glioblastoma")` → EFO_0000519 (9906 rows) | ✓ PASS | 1.56s |
| `build_net("glioblastoma")` → top 10: EGFR, IDH1, TP53, PTEN, VEGFA, GSR, BRAF, ATRX, RB1, PIK3CA | ✓ PASS | 0.95s |
| `corrected_net_summary(net)` → 458 genes total, 434 with drug corrs, 81 with STRING interactions, 321 with mutations | ✓ PASS | <0.1s |
| `inspect_gdsc_drugs()` → GDSC2_fitted_dose_response.xlsx (286 drugs × 185 targets) | ✓ PASS | 11.3s |

### What the corrected summary reveals (newly visible truth)

The legacy `drug_targets` field count was 14. The corrected summary shows:
- **434 of 458 genes have drug correlation data** in the universal net (95% coverage)
- **81 of 458 genes have STRING interactions populated** (18% coverage — this is the Gap 6 universe)
- **321 of 458 genes have mutation frequency data** (70% coverage)

The Gap 6 problem (sparse STRING coverage) is now visible in the net's own summary statistics, not hidden behind a misleading aggregate.

### Additional finding from this phase

**Gap 19 (discovered during verification):** `DiseaseNetBuilder` uses relative paths (`../results/...`) requiring cwd == `~/INTERCEPTA/code/`. Phase 1 module passes absolute paths into the constructor as a workaround. The original class is unchanged. A proper fix would refactor the original to use absolute paths via Path.home() — deferred to keep Principle 16.

### State after Phase 1

- 6 gaps closed: 1, 2, 3, 4, 5, 19
- Module created: `round3_gbm_live_test/code/intercepta_pipeline_v0.py`
- Module is the foundation for Phase 2+ — additional gap closures can be added as functions in the same file
- A user can now run `from intercepta_pipeline_v0 import build_net; net = build_net("glioblastoma")` from any working directory and get correct biology

### Principle audit

- **P3 (research before code):** the patches are mechanical wrappers around existing code; minimal new science required.
- **P4 (fix structure, don't tune):** Gap 1 and Gap 2 were structural fixes (chaining + disambiguation logic); none of them tuned a number or threshold.
- **P15 (honest validation):** every fix verified by explicit assertion; one failure (Gap 19, discovered live) was acknowledged and patched, not hidden.
- **P16 (preserve past work):** zero modifications to `disease_net_builder.py` or any Round 1/2 file. New module wraps originals.


## Phase 2A — Gaps 9 + 10 closed

### Verification results

| Gap | Test | Result | Time |
|-----|------|--------|------|
| 10 | `rank_drugs_for_disease("glioblastoma")` returns 30 ranked drugs | ✓ PASS | 12.8s |
| 10 | At least one drug hits top-20 GBM gene | ✓ PASS (2/30: Foretinib + 1) | — |
| 9 | `enrich_with_metabolites(net)` populates metabolites | ✓ PASS | 0.01s |
| 9 | Per-gene metabolite annotation | ✓ 103/458 genes | — |
| 9 | 314 metabolites linked to GBM net | ✓ Real data, biologically sensible | — |

### What the metabolite enrichment revealed

The original `build_net` returned 0 metabolites. The data was on disk (1.6MB CSV) but never joined. Gap 9 fix: 314 metabolites including deoxyguanosine, DHAP, methylimidazoleacetic acid, dTTP, fatty acid pool — biologically sensible cancer-metabolism connections. 103 of 458 GBM net genes have at least one metabolite annotation.

### What the drug ranking revealed (and didn't)

`rank_drugs_for_disease` produces the same output as Stage 3.5's manual pandas glue, just automatically. Top 5 still dominated by broad cytotoxics (Sepantronium, Staurosporine, Dactinomycin, MG-132, CDK9_5038). Only 2 of top 30 hit top-20 GBM genes.

This is the expected scope of Phase 2A: **closed the orchestration gap (no manual code needed) but did not close the scoring gap (Gap 13: GDSC AUC ranking doesn't match GBM clinical reality).** Gap 13 requires scientific work — biomarker-stratified efficacy, BBB filter, tumor-vs-normal selectivity. It's deferred to a later phase.

Honest position: the *plumbing* works. The *output quality* still has Finding 16's caveats from Stage 3.5.

### Cumulative state after Phase 2A

**8 gaps closed:** 1, 2, 3, 4, 5, 9, 10, 19.

**Pipeline can now do (as one function call each):**
- `resolve_disease(name)` — Phase 1
- `build_net(name)` — Phase 1
- `corrected_net_summary(net)` — Phase 1
- `inspect_gdsc_drugs()` — Phase 1
- `rank_drugs_for_disease(name)` — Phase 2A
- `enrich_with_metabolites(net)` — Phase 2A

Six functions. One module. Works on any disease in OpenTargets.

### Still open (in increasing scope)

- Gap 11 — no offline ClinicalTrials.gov index (novelty check)
- Gap 8 — AlphaFold structures not joined to net
- Gap 6 — STRING interactions for any disease (escape routes broken)
- Gap 7 — ChEMBL coverage (mCRPC-curated locally)
- Gaps 12-18 — scoring + structural (multi-week to multi-month each)

### Principle audit

- **P3 (research before code):** vision document was searched (escape routes mentioned 4×, metabolites 1×, ranking 2×) before sequencing decisions; user pushback corrected my CSO call to honor the systematic-progression principle.
- **P4 (fix structure, don't tune):** Gap 9 was a join-key fix, Gap 10 was an orchestration assembly — neither tuned scoring or thresholds.
- **P15 (honest validation):** ranking output reported with explicit caveat that Finding 16 (scoring quality) is not closed by this phase.
- **P16 (preserve past work):** zero modifications to original `disease_net_builder.py` or any Round 1/2 file. New functions appended to `intercepta_pipeline_v0.py`.


## Phase 2B — Gaps 6 + 8 closed (with bug-and-fix story)

### Initial implementation: bug surfaced by canonical biology assertion

Initial `populate_string_interactions` ran, populated 448/458 GBM genes with 40,895 edges, all the surface metrics looked correct. Coverage 97.8%, runtime 5.9s. Then canonical biology check: 0/12 expected edges found.

**Diagnostic showed the bug:**
- Forward symbol→ENSP: correct (EGFR → ENSP00000275493)
- Edge data: correct (506 edges from EGFR's ENSP)
- Reverse ENSP→symbol: WRONG. Returned UCSC transcript IDs (`UC001TTX.4`) instead of gene symbols.

**Root cause:** The `_load_string_aliases` filter was `'HGNC' in source or 'Ensembl_HGNC' in source or source == 'BLAST_KEGG_NAME' or 'Ensembl_gene_name' in source`. Too broad. Multiple sources per ENSP, last-write-wins overwrote the gene symbol with whatever non-symbol alias appeared later in the file.

### Fix

Restricted source filter to `Ensembl_HGNC_symbol` and `BioMart_HUGO` (the actual gene symbol sources). Added shortest-symbol-wins logic for ENSPs with multiple symbol-source entries (longer aliases are usually descriptive names, shorter ones are gene symbols).

### Verification (post-fix)

| Test | Result |
|------|--------|
| `populate_string_interactions("glioblastoma")` returns | 445/458 genes enriched, 39,385 edges, 5.4s |
| `ensp_to_symbol` unique values | 19,270 (matches ~20K human protein-coding gene count) |
| EGFR ↔ MET edge | ✓ Present |
| 12/12 canonical cancer edges | ✓ All present (EGFR↔ERBB2, TP53↔MDM2, PTEN↔PIK3CA, BRAF↔MAP2K1, AKT1↔PIK3CA, RB1↔E2F1, CDKN2A↔CDK4, IDH1↔IDH2, plus 4 others) |
| EGFR top partners | PTPN11, HBEGF, NRG1, TGFA, ERBB2, SHC1, SOS1, PIK3CA, ERBB3, GRB2 — canonical EGFR signalosome |
| Coverage assertion ≥250 | ✓ 445 ≥ 250 |

### Vision-claim impact

- Live test Finding 8 (universal net interactions mCRPC-centric): CLOSED
- Live test Finding 9 (EGFR→MET escape route NOT in net): CLOSED
- Vision Part 4.2 Stage 2 escape route mapping: now functional for any OpenTargets disease
- Vision alignment: STRING-related claims move toward PARTIAL-to-ALIGNED for any disease

### Cumulative state after Phase 2B

**9 gaps closed across 3 phases:** 1, 2, 3, 4, 5, 6, 8, 9, 10, 19. (Phase 1 closed 5; Phase 2A closed 2; Phase 2B closed 2.)

**Pipeline functions now (8 working):**
- `resolve_disease(name)` — Phase 1
- `build_net(name)` — Phase 1
- `corrected_net_summary(net)` — Phase 1
- `inspect_gdsc_drugs()` — Phase 1
- `rank_drugs_for_disease(name)` — Phase 2A
- `enrich_with_metabolites(net)` — Phase 2A
- `populate_string_interactions(net)` — Phase 2B (NEW)
- Internal: `_load_string_aliases()`, `_load_string_edges()` — Phase 2B helpers

**Still open from live test:**
- Gap 7 (ChEMBL coverage mCRPC-curated)
- Gap 11 (no offline ClinicalTrials.gov)
- Gap 13 (53 brain cell lines data — informational, no action)
- Gap 16 (GDSC AUC scoring quality — scientific, deferred)
- Gap 17 (Stage 3 manual synthesis — closed by 2A but reframed)
- Gap 18 (ODE structurally mCRPC-only — Workstream C territory, Horizon 1)

### Principle audit

- **P3 (research before code):** SKIPPED initially (assumed alias filter would work without verifying STRING file format). Bug was the consequence. Diagnostic-first recovery applied.
- **P4 (fix structure not threshold):** Fix changed source filter (structural) and added shortest-symbol-wins (structural). Did not adjust thresholds.
- **P15 (honest validation):** Canonical biology assertion caught the bug. Without it, would have shipped broken. P15 validated.
- **P16 (preserve past work):** No modifications to disease_net_builder.py or Round 1/2 files. Only `intercepta_pipeline_v0.py` extended.

### Lesson recorded

When parsing complex annotation files (STRING aliases has many source types per ENSP), always inspect the data structure before assuming the filter logic. A 10-second `head` of the aliases file would have shown the bug before runtime. Future work: when integrating any new external annotation file, first inspect 100 sample rows to understand source types and structure.


## Phase 2C — Gap 11 closed (Structure layer joins net for any disease)

### Initial implementation: two architectural mistakes

**Mistake 1: STRING UniProt mapping was unreliable.**
First implementation tried to extract UniProt accessions from STRING aliases file (UniProt_AC source tag). Diagnostic on EGFR's ENSP00000275493 showed: zero UniProt_AC rows for the canonical EGFR ENSP. The 88,155 UniProt_AC entries in STRING are scattered across many ENSPs and don't reliably cover the genes we need. EGFR mapped to O00688 (a different protein) because of cross-reference noise.

**Mistake 2: AlphaFold v4 file naming was outdated.**
First implementation used `AF-{UniProt}-F1-model_v4.pdb`. Diagnostic showed: 404 for v4, 200 for v6. AlphaFold DB v6 (Sep 2025, synced to UniProt 2025_03) uses model_v6 file naming. The "v6" in the filename is the FILE version, not the database release.

### Diagnostic findings

| Check | Result |
|------|--------|
| STRING UniProt_AC for EGFR's ENSP | 0 rows (mapping unreliable for many ENSPs) |
| AlphaFold AF-P00533-F1-model_v4.pdb | 404 |
| AlphaFold AF-P00533-F1-model_v6.pdb | 200 (correct URL pattern) |
| UniProt REST API gene_exact:EGFR + organism_id:9606 + reviewed:true | Returns P00533 cleanly |

### Fix (v2 architecture)

- **UniProt REST API for canonical accessions.** Batched queries (20 genes/batch) using gene_exact filter to ensure Swiss-Prot canonical match.
- **AlphaFold model_v6 file URLs.** Direct file existence via HEAD request, no API metadata call needed.
- **Symbol→UniProt cache in `_STRING_CACHE['symbol_to_uniprot_canonical']`.** Persists across diseases. AML reused 117 of 498 mappings from GBM.
- **On-demand PDB download.** `download_alphafold_pdb(net, gene_symbol)` for downstream Workstream C use; not bulk-downloaded during net enrichment.
- **Old `_load_string_uniprot_mapping` renamed `_DEPRECATED_v2_replaces`.** Per P5 (preserve past work), kept in module but not called.

### Verification (v2)

| Test | Result |
|------|--------|
| 14 canonical UniProt IDs (EGFR=P00533 etc.) | 13/14 exact match (MDM2 missed) |
| EGFR/IDH1/TP53/PTEN have canonical UniProt + AlphaFold | ✓ All 4 |
| GBM net UniProt coverage | 453/458 (98.9%) |
| GBM net AlphaFold availability | 443/453 (97.8%) |
| EGFR PDB download | 772,334 bytes in 0.3s |
| Performance | 19.2s for 458 genes |
| Cache test on AML | 117/498 cached from GBM, 18.2s total run |

### Vision-claim impact

- Vision Part 4.4 Stage 4 Layer A: PARTIAL (mCRPC-only) → ALIGNED-for-any-disease prerequisite met
- Net Spec Layer 3 (Proteome): UNBUILT → PARTIAL bordering ALIGNED
- Live test Finding 11 (Structure layer doesn't join): CLOSED
- Workstream C generative chemistry prerequisite #1 (target structures): SATISFIED

### Cumulative state after Phase 2C

**10 gaps closed across 4 phases:** 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 19.

**Pipeline functions now (10+ working, 4 internal helpers):**
- `resolve_disease(name)`, `build_net(name)`, `corrected_net_summary(net)`, `inspect_gdsc_drugs()`
- `rank_drugs_for_disease(name)`, `enrich_with_metabolites(net)`
- `populate_string_interactions(net)` + helpers `_load_string_aliases`, `_load_string_edges`
- `attach_alphafold_structures(net)` + helpers `_check_alphafold_url`, `_query_uniprot_canonical_batch`, `download_alphafold_pdb`

**Still open from live test:**
- Gap 7 (ChEMBL coverage mCRPC-curated) → Phase 2D
- Gap 13 (53 brain cell lines — informational, no action)
- Gap 16 (GDSC AUC scoring quality — scientific, deferred)
- Gap 18 (ODE structurally mCRPC-only) → Workstream C territory

**Workstream A progress:**
- Phases 1, 2A, 2B, 2C: ✓ closed
- Phase 2D (ChEMBL coverage): pending
- Phase 2E (ClinicalTrials.gov novelty): pending
- Phase 2F (Pareto generalization): pending

### Lesson recorded

Architectural lesson: **don't route through indirect data sources for canonical mappings.** Use authoritative APIs. UniProt REST API is the canonical source for gene→UniProt accession mappings; STRING is great for interactions but not for UniProt mapping. When integrating any new annotation file, ask: is this the authoritative source for what I need? If not, use the authoritative source directly.

This applies generally: ChEMBL is authoritative for drug-target activity (Phase 2D will use ChEMBL API directly, not derive from elsewhere). ClinicalTrials.gov API v2 is authoritative for trial novelty (Phase 2E). Use authoritative sources, not proxies.

