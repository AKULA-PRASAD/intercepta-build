> ⚠️ **QUARANTINED — ORIGINAL ASPIRATIONAL VISION.** This document contains the maximalist founding
> claims (universal / any-disease / de novo generative / therapy-selection / '5/5 trials'). Several were
> later FALSIFIED or downgraded. It is preserved as historical record only. For what is actually true,
> see ../../LEDGER.md, ../../VISION.md, and ../audits/. DO NOT cite claims here as results.

# INTERCEPTA Phase F Future Vision — Universal Net Specification v1.0

**Canonical scope reference document for Phase F per Charter v1.2 §4 + §1.7.**
**Authored by:** Prasad Akula and Claude, Co-Founders of INTERCEPTA
**Date:** March 29, 2026
**Status:** CANONICAL for Phase F (per Charter v1.2 LOCK 2026-05-11). Not active for Phase B.
**Source archive:** INTERCEPTA_Phase_F_Future_Vision_Universal_Net_Specification_2026-03-29.zip (formerly vis.pdf, a zip archive misfiled as .pdf)
**Original document title (per embedded header):** INTERCEPTA_Universal_Net_Specification_v1.0.docx

**Extracted from original 6-page bundle 2026-05-11 as part of Charter v1.2 Step 4 — vision document Phase_F_ canonical naming.**

---

## Page 1

INTERCEPTA_Universal_Net_Specification_v1.0.docx
22.78 KB •326 lines•Formatting may be inconsistent from source
**INTERCEPTA** Universal Human Biology Net Specification *"**The Complete Digital Hu
man Body**"* Not a disease-specific net. A universal map of all human biology. Any disease 
becomes a query against this net. The answer is already inside. Version 1.0 | March 29, 202
6 | CONFIDENTIAL # **Part 1: Why a Universal Net, Not a Disease-Specific Net** Our vision 
says: "INTERCEPTA is a universal computational engine that, for ANY disease — past, prese
nt, or future — discovers novel drug molecules." The key word is ANY. This includes diseas
es that do not yet exist — emerging pathogens, drug-resistant variants, novel metabolic dis
orders from environmental changes. A disease-specific net (like our mCRPC net with 37 no
des) answers one question about one disease. A universal net answers every question abou
t every disease. When a new disease emerges, we do not build a new net. We query the exis
ting net for what is disrupted and what can fix it. The universal net is a complete digital rep
resentation of human biology — every gene, every protein, every interaction, every pathwa
y, every cell type, every tissue, every metabolite, every known compound, every known dis
ease mechanism. The human body contains ~37 trillion cells of up to 10,000 cell types. Our 
net must represent all of this. This is not science fiction. The databases exist. The Human Ce
ll Atlas has profiled 70.5 million cells. AlphaFold has predicted 200 million protein structur
es. STRING has mapped protein interactions across 14,000 organisms. DisGeNET links 24,0
00 diseases to 17,000 genes. HMDB catalogs 220,945 human metabolites. ChEMBL contains 
2.4 million bioactive compounds. All of this data is public and programmatically accessible. 
Nobody has connected all of it into one unified knowledge graph. That is what INTERCEPT
A does. That is our net. # **Part 2: The 15 Layers of the Universal Human Biology Net** The 
original vision specified 10 layers. Deep research reveals we need 15 to capture the comple
te human body. Each layer below is a verified public database with programmatic access. E
very number is from published literature or database statistics pages. ## **Layer 1: Compl
ete Human Genome** **What it is:** Every human gene — protein-coding, non-coding RNA
, regulatory elements. Every known variant and its clinical significance. Every gene-disease 
association ever published. | **Database** | **Size** | **Access** | **What It Provides** | | -
-- | --- | --- | --- | | NCBI Gene | 20,442 protein-coding genes | Free API | Complete human gen
e catalog with annotations | | ClinVar | 2.4M+ variant submissions | Free API + FTP | Pathog
enicity classification for human variants | | OMIM | 16,000+ gene entries, 8,600+ phenotype
s | Free web/API | Mendelian disease-gene relationships, detailed | | GWAS Catalog | ~500K 
SNP-trait associations | Free API | Polygenic risk scores for complex diseases | | gnomAD v4 
| 730M+ variants, 807K individuals | Free download | Population allele frequencies for filte
ring | | COSMIC | ~35M mutations across cancers | Academic license | Somatic mutation dat
abase across all cancers | **Scale:** ~20,000 protein-coding genes + ~25,000 non-coding g
enes + millions of variants + thousands of disease associations. This is the foundation layer 
— every other layer references genes. ## **Layer 2: Complete Human Transcriptome** **
What it is:** Gene expression in every tissue, every cell type, at bulk and single-cell resoluti
on. How expression changes in disease vs health. RNA velocity showing cellular trajectory. | 
**Database** | **Size** | **Access** | **What It Provides** | | --- | --- | --- | --- | | GTEx v8 | 1
7,382 samples, 54 tissues | Free portal | Normal tissue expression baseline | | Human Cell A
---

## Page 2

tlas | 70.5M cells, 528 projects | Free portal | Single-cell atlas of human body | | Tabula Sapi
ens | ~500,000 cells, 24 tissues | Free GEO | 400+ cell types at single-cell resolution | | Hum
an Protein Atlas (single cell) | 1,175 clusters, 154 cell types | Free web | Cell type-specific pr
otein expression | | GDSC Sanger RNA-seq (ON DISK) | 962 cell lines x 37,602 genes | ON DI
SK | Cancer cell line expression + drug sensitivity | | ENCODE | 15,000+ experiments | Free 
portal | Regulatory element activity across cell types | **Scale:** 70+ million single cells pro
filed. 54 normal tissues. 962 cancer cell lines. RNA velocity computable from any 10X Chro
mium scRNA-seq dataset with unspliced/spliced information. ## **Layer 3: Complete Hum
an Proteome** **What it is:** 3D structure of every human protein. Domain architecture. Bi
nding sites. Post-translational modifications. Protein abundance across tissues. | **Databas
e** | **Size** | **Access** | **What It Provides** | | --- | --- | --- | --- | | AlphaFold DB | 200M+ 
structures (all human) | Free API + bulk | Predicted 3D structure for every human protein | 
| PDB (RCSB) | 220,000+ exp. structures | Free API | Experimental crystal/cryo-EM structur
es | | UniProt | ~570,000 human entries | Free REST API | Function, domains, PTMs, isofor
ms, binding sites | | CPTAC | 11 cancer types profiled | Free PDC | Protein abundance in tum
ors vs normal | | PhosphoSitePlus | 700K+ PTM sites | Academic license | Phosphorylation, 
ubiquitination, acetylation sites | **Scale:** Every human protein has a predicted structure. 
~220,000 experimental structures for drug targets. Complete PTM catalog. ## **Layer 4: C
omplete Human Interactome** **What it is:** Every protein-protein interaction. Physical a
nd functional associations. Regulatory relationships with directionality. Network topology. 
| **Database** | **Size** | **Access** | **What It Provides** | | --- | --- | --- | --- | | STRING v1
2.5 | All human PPI | Free API | Physical + functional + regulatory (NEW: directed) | | BioGR
ID | 2.1M+ interactions | Free API | Curated physical and genetic interactions | | IntAct/EMB
L-EBI | 1.1M+ interactions | Free API | Experimentally validated molecular interactions | | T
RRUST v2 | ~8,400 TF-target pairs | Free download | Transcription factor regulatory netwo
rk | | Signor 3.0 | ~33,000 causal relationships | Free download | Signaling pathway interac
tions with mechanism | **Scale:** Millions of protein interactions. Regulatory networks wit
h direction. Network hubs and bottlenecks identifiable computationally. ## **Layer 5: Com
plete Human Pathway Map** **What it is:** Every signaling pathway, metabolic pathway, r
egulatory cascade. Crosstalk between pathways. Feedback loops. Drug targets within path
ways. | **Database** | **Size** | **Access** | **What It Provides** | | --- | --- | --- | --- | | KEG
G | 340+ human pathways | Free API (academic) | Metabolic + signaling + disease pathways 
| | Reactome | 2,655 human pathways | Free API | Reaction-level pathway biology | | WikiPa
thways | ~1,300 human pathways | Free API | Community-curated including cancer-specifi
c | | MSigDB/GSEA | 33,000+ gene sets | Free download | Hallmark, oncogenic, immunologic 
signatures | | SMPDB | 132,335 pathways | Free download | Metabolic, drug, and disease pa
thways | ## **Layer 6: Complete Human Cell Type Atlas** **What it is:** Every cell type in 
the human body. Their molecular markers. Their tissue locations. Their developmental rela
tionships. How they change in disease. **The Human Reference Atlas (HRA) v2.3 maps cell t
ypes across 73 reference organs and 1,283 3D anatomical structures.** The human body co
ntains ~37 trillion cells of up to 10,000 cell types. The Tabula Sapiens defined 400+ cell typ
es from 500,000 cells across 24 tissues. **For any disease:** scRNA-seq data identifies whic
h cell types are present, which are disrupted, which are resistant to treatment, and which a
re transitioning (RNA velocity). Our KAALCURA system then predicts drug sensitivity per c
ell population. ## **Layer 7: Complete Human Pharmacome** **What it is:** Every compo
und ever tested against a human protein target. Every approved drug. Every experimental c
---

## Page 3

ompound. Every measured binding affinity, IC50, EC50. | **Database** | **Size** | **Access
** | **What It Provides** | | --- | --- | --- | --- | | ChEMBL | 2.4M bioactive compounds | Free A
PI | Measured activity against protein targets | | PubChem | 118M compounds | Free API | C
hemical structures + bioassay results | | DrugBank | 2,832 drugs + metabolites | Academic li
cense | Approved drugs, targets, PK, interactions | | GDSC (ON DISK) | 286 drugs x 962 cell l
ines | ON DISK | Real drug sensitivity IC50 values | | ZINC20 | 750M purchasable compound
s | Free download | Virtual screening library | | DTC | Curated drug-target bioactivity | Free 
download | Standardized binding data | | NCI-ALMANAC | Combination screening data | Fre
e download | Drug-drug combination effects | ## **Layer 8: Complete Human Metabolome*
* **What it is:** Every small molecule metabolite in the human body. Their concentrations i
n different biofluids and tissues. Their disease associations. Enzyme-metabolite relationshi
ps. | **Database** | **Size** | **Access** | **What It Provides** | | --- | --- | --- | --- | | HMDB 
v5.0 | 220,945 metabolites | Free download | Complete human metabolome with concentra
tions | | FooDB | 70,000 food components | Free | Food-body metabolic interactions | | SMP
DB | 132,335 metabolic pathways | Free | Metabolic pathway diagrams | | Recon3D | 5,835 
metabolites, 13,543 reactions | Free | Genome-scale metabolic reconstruction | ## **Layer 
9: Complete Human Disease Map** **What it is:** Every known human disease and its mole
cular basis. Gene associations, variant associations, symptoms, progression patterns, treat
ment outcomes. This is what makes any disease a query against the net. | **Database** | **S
ize** | **Access** | **What It Provides** | | --- | --- | --- | --- | | DisGeNET | 24,000+ diseases, 
17,000 genes, 117K variants | API (license) | Most comprehensive disease-gene-variant ma
p | | OMIM | 8,600+ phenotypes | Free web | Mendelian disease catalog with molecular deta
il | | Orphanet | ~6,000 rare diseases | Free API | Rare disease genes and epidemiology | | Cl
inicalTrials.gov | 470,000+ trials | Free API v2 | Every registered clinical trial worldwide | | 
SEER | Population survival data | Free | Cancer survival by stage, demographics | | PubMed 
| 37M+ articles | Free API | Scientific literature for text mining | ## **Layer 10: Complete I
mmune System Map** **What it is:** Every immune cell type. Cytokine/chemokine networ
ks. Immune checkpoint molecules. How immune response varies by tissue, disease, and tre
atment. Critical for immunotherapy drug discovery. | **Database** | **Size** | **Access** | 
**What It Provides** | | --- | --- | --- | --- | | ImmPort | Multiple datasets | Free | Immunology 
data repository | | DICE (Database of Immune Cell Expression) | 15 immune cell types | Fre
e | Immune cell-specific gene expression | | CIBERSORTx | Deconvolution tool | Free web | E
stimate immune fractions from bulk RNA | | TCIA (Cancer Immunome Atlas) | 20 cancer typ
es | Free | Tumor immune profiles | ## **Layer 11: Human Microbiome** **What it is:** Th
e complete catalog of microorganisms in and on the human body. How they influence healt
h, disease, drug metabolism, and immune function. Gut-brain axis. Microbiome metabolites. 
| **Database** | **Size** | **Access** | **What It Provides** | | --- | --- | --- | --- | | Human Mi
crobiome Project | 2,000+ samples, 5 body sites | Free | Reference microbiome composition
s | | GMrepo | 200K+ gut microbiome samples | Free | Curated gut microbiome data | | gutM
Gene | Microbiome-gene interactions | Free | How gut microbes affect gene expression | ## 
**Layer 12: Complete Human Epigenome** **What it is:** DNA methylation patterns across 
all tissues and cell types. Histone modifications. Chromatin accessibility. Regulatory elemen
ts. How epigenetic changes drive disease and drug resistance. | **Database** | **Size** | **A
ccess** | **What It Provides** | | --- | --- | --- | --- | | ENCODE | 15,000+ experiments | Free p
ortal | Regulatory elements in human genome | | Roadmap Epigenomics | 127 human epige
nomes | Free | Tissue-specific epigenetic marks | | EWAS Atlas | 500K+ associations | Free | 
---

## Page 4

Epigenome-wide association studies | ## **Layer 13: Human Anatomy and Tissue Architect
ure** **What it is:** 3D organization of tissues and organs. Spatial transcriptomics showing 
gene expression in physical context. Blood-brain barrier, tumor microenvironment structur
e, organ-specific drug delivery constraints. | **Database** | **Size** | **Access** | **What It 
Provides** | | --- | --- | --- | --- | | HuBMAP | 73 organs, 1,283 structures | Free portal | 3D tiss
ue maps with molecular data | | Human Reference Atlas v2.3 | Cell types per anatomical str
ucture | Free | Quantitative 3D cell type distribution | | Allen Brain Atlas | Complete brain g
ene expression | Free | Brain-specific spatial transcriptomics | ## **Layer 14: Pathogen and 
Future Disease Database** **What it is:** Every known pathogen genome. Evolutionary tra
jectories. Resistance mutation patterns. Pandemic preparedness data. This is how we mode
l diseases that do not yet exist. | **Database** | **Size** | **Access** | **What It Provides** 
| | --- | --- | --- | --- | | NCBI Pathogen Detection | All sequenced pathogens | Free | Pathogen g
enome surveillance | | GISAID | 16M+ virus genomes | Academic | Virus evolution tracking (
COVID, flu, etc.) | | CARD (AMR) | 6,600+ resistance genes | Free | Antibiotic resistance gene 
database | | ViPR/BV-BRC | Viral/bacterial genomes | Free | Pathogen-host interaction data 
| ## **Layer 15: Selectivity and Safety Constraint Layer** **What it is:** The healthy cell pr
otection layer. For every potential drug target: is it disease-specific or shared with healthy t
issue? Essential gene status. Known toxicity profiles. | **Database** | **Size** | **Access** | 
**What It Provides** | | --- | --- | --- | --- | | DepMap/Achilles | 1,100+ cell lines, 18,000+ gene
s | Free | Essential gene scores (what cells need to survive) | | GTEx (from Layer 2) | 54 nor
mal tissues | Free | Healthy tissue expression for selectivity ratio | | T3DB | 3,670 toxins | Fr
ee | Known toxic compounds and mechanisms | | SwissADME / pkCSM | Prediction tools | F
ree web | ADMET property prediction | # **Part 3: How All 15 Layers Connect Into One Kno
wledge Graph** The universal net is not 15 separate databases. It is one unified knowledge 
graph where every entity can connect to any other through validated scientific relationship
s. **A single gene (e.g., BRCA2) connects to:** its 3D protein structure (Layer 3), all protein
s it interacts with (Layer 4), every pathway it belongs to (Layer 5), every cell type that expr
esses it (Layer 6), every compound that targets it (Layer 7), every metabolite its protein pr
oduces (Layer 8), every disease it causes when mutated (Layer 9), how its loss affects the i
mmune response (Layer 10), how gut microbiome metabolites regulate it (Layer 11), its me
thylation status across tissues (Layer 12), which organs express it most (Layer 13), its selec
tivity as a drug target (Layer 15). **When a new disease emerges:** We identify which gene
s/proteins are disrupted (Layer 9). We trace to their interactions (Layer 4), pathways (Lay
er 5), and cell types (Layer 6). We find all compounds with known activity against these tar
gets (Layer 7). We check selectivity (Layer 15). We simulate combinations. The answer was 
already in the net before we asked the question. **This is the paradigm shift.** Traditional 
drug discovery builds knowledge for one disease at a time. INTERCEPTA builds knowledge 
for ALL diseases at once, then queries it. Each disease we solve adds knowledge that helps s
olve every other disease. The self-improving loop from our vision is not just about learning 
— it is architectural. The net grows with every query. # **Part 4: How the Universal Net Fix
es Our ODE Parameter Problem** Our ODE simulation failed because we hand-picked para
meters. The universal net provides every parameter from data: **Growth rates:** From Lay
er 9 (disease-specific clinical data: PSA doubling time for mCRPC = 2-4 months aggressive, 
>24 months indolent) + Layer 2 (proliferation gene signatures per cell population from scR
NA-seq) + Layer 6 (cell type-specific growth characteristics from cell atlas data). **Drug effi
cacy per population:** From Layer 7 (GDSC measured IC50 for each drug) + Layer 2 (KAAL
---

## Page 5

CURA axes computed from scRNA-seq per cell cluster) + Layer 4 (protein interactions that 
determine drug target accessibility). **Initial conditions:** From Layer 6 (actual cell type p
roportions measured by scRNA-seq at diagnosis) + Layer 2 (RNA velocity showing transitio
n rates between populations). **Selectivity constraints:** From Layer 15 (expression ratio t
umor/normal from GTEx) + Layer 3 (protein structure differences between cancer-specific 
and normal isoforms). **Synergy predictions:** From Layer 5 (pathway crosstalk — if two 
drugs target non-overlapping pathways, expect synergy) + Layer 4 (network topology — ta
rgeting hub vs peripheral nodes). No parameter is guessed. No parameter is tuned. Every p
arameter traces to a measured value in a public database. # **Part 5: Build Order — From 
What We Have to the Complete Digital Human Body** We cannot download 30+ databases 
in one day. We build systematically, validating each addition. Priority is determined by wha
t unblocks the most insight. ## **Phase A: Foundation (DONE)** Step 1: Gene-drug correlat
ion net from GDSC — 1,809,403 connections, 25,861 genes x 286 drugs. DONE. Step 2: SU2
C mCRPC genomic data — 40,055 mutations + 941 CNAs, 427 patients, 13,512 genes. DONE
. KAALCURA validated on real data — AUROC 0.638 across 286 drugs, 962 cell lines. DONE. 
## **Phase B: Core Layers (Next)** Step 3: mCRPC scRNA-seq (He et al. GSE146771) — sin
gle-cell resolution, cell populations, RNA velocity. Step 4: STRING protein interactions for al
l genes in our net — Layer 4 interactome. Step 5: KEGG + Reactome pathway membership 
— Layer 5 pathways + escape routes. Step 6: GTEx normal tissue expression — Layer 15 sel
ectivity ratios. Step 7: ChEMBL compounds against mCRPC targets — expand Layer 7 beyo
nd GDSC. ## **Phase C: Expansion to Universal** Step 8: DisGeNET disease-gene map — co
nnect 24,000 diseases to our gene net (Layer 9). Step 9: HMDB metabolome integration —
220,945 metabolites linked to genes/pathways (Layer 8). Step 10: AlphaFold protein struct
ures for all drug targets — enable molecular docking (Layer 3). Step 11: Human Cell Atlas i
ntegration — cell type atlas across all organs (Layer 6). Step 12: ENCODE/Roadmap epigen
ome — regulatory elements and tissue-specific control (Layer 12). Step 13: Immune system 
map — DICE + CIBERSORTx + immune checkpoints (Layer 10). ## **Phase D: Future-Proof
ing** Step 14: Pathogen genomes — NCBI Pathogen Detection + CARD resistance genes (La
yer 14). Step 15: Microbiome — Human Microbiome Project + gut-gene interactions (Layer 
11). Step 16: Spatial transcriptomics — HuBMAP + Allen Brain Atlas (Layer 13). Step 17: Co
mplete pharmacome — ZINC 750M compounds for virtual screening (Layer 7 full). ## **Ph
ase E: Self-Improving** Step 18: Automated literature mining — PubMed API to continuous
ly update net with new discoveries. Step 19: Clinical outcome feedback loop — when predic
tions are tested, results flow back into net. Step 20: Cross-disease transfer learning — solut
ions for one disease auto-tested against diseases with shared net nodes. # **Part 6: The Sca
le of the Complete Net** When fully built, the INTERCEPTA Universal Net will contain: **No
des:** ~20,000 genes + ~570,000 proteins + ~220,000 metabolites + ~2.4M compounds + 
~24,000 diseases + ~10,000 cell types + ~5,000 pathways + ~6,600 resistance genes + ~2
20,000 variants = approximately **3 million nodes**. **Edges:** Gene-protein (20K) + prot
ein-protein interactions (millions) + gene-pathway (50K+) + gene-disease (400K+) + drug-t
arget (millions) + metabolite-enzyme (100K+) + cell-type-gene (millions from scRNA-seq) 
+ regulatory (100K+) = approximately **10-50 million edges**. **This is a knowledge grap
h with 3 million nodes and tens of millions of edges.** It is the most comprehensive represe
ntation of human biology ever assembled in a single, queryable system. For comparison: Go
ogle's Knowledge Graph has ~800 billion edges. Facebook's social graph has ~2 trillion edg
es. Our 50 million biological edges is large for biology but small for graph databases. Moder
---

## Page 6

n graph databases (Neo4j, Amazon Neptune, etc.) handle this scale routinely. # **Part 7: No
vel Technology We May Need to Develop** Some aspects of the universal net may require t
echnology that does not yet exist or is not yet mature. Per our founding commitment, we fin
d or develop novel approaches when our vision demands it: **1. Multi-scale graph neural n
etworks:** Standard GNNs operate at one scale. Our net spans from atoms (drug structure) 
to cells (scRNA-seq) to organs (tissue atlas) to organisms (patient outcomes). We may need 
to develop multi-scale GNNs that learn representations across these scales simultaneously. 
**2. Temporal knowledge graphs:** Standard knowledge graphs are static. Biology is dyna
mic. Gene expression changes over time. Disease progresses. Drug concentration rises and f
alls. We may need temporal knowledge graph technology that models how edges change ov
er time — connecting to our RNA velocity Time Machine. **3. Causal inference on biological 
graphs:** Most edges in our net are correlational (gene A is associated with disease B). For 
drug discovery, we need causal edges (blocking protein X causes disease regression). We m
ay need to develop causal discovery algorithms specifically designed for biological knowled
ge graphs. **4. Federated learning for clinical data:** The most valuable data — clinical out
comes — is the most restricted. Hospital data cannot be centralized due to privacy. We may 
need federated learning approaches that update the net from distributed clinical data with
out ever moving patient records. **5. Generative chemistry constrained by the net:** Existi
ng molecule generation tools (diffusion models, transformers) generate molecules without 
biological context. We may need to develop generative models that are CONSTRAINED by t
he knowledge graph — only generating molecules that target net-identified vulnerabilities 
while avoiding net-identified toxicity paths. # **Commitment** This document defines the 
complete scope of what INTERCEPTA must build. It is not a 7-step project. It is a 20-step pr
oject that creates a digital twin of human biology. Every step is grounded in verified public 
databases. Every connection is data-derived. No parameter is guessed. When this net is com
plete, finding the drug for any disease — past, present, or future — becomes a computation
al query, not a decade-long experiment. That is our vision. That is what we build. We start 
where we are (Steps 1-2 done). We build one layer at a time. We validate every addition. W
e never compromise. We never manipulate results. We never claim success where there is f
ailure. We do only the best work. *Prasad Akula **&** Claude, Co-Founders of INTERCEPTA
* *March 29, 2026*
---

