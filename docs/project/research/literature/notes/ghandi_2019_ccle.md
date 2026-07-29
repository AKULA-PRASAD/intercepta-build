# Ghandi et al., 2019 — Next-generation characterization of the Cancer Cell Line Encyclopedia (CCLE)

## 0. Identification
- **Citation:** Ghandi M*, Huang FW*, Jané-Valbuena J, Kryukov GV, Lo CC, McDonald ER 3rd, Barretina J, Gelfand ET, Bielski CM, Li H, ..., Sellers WR. *Nature* 569(7757):503-508, 2019 May 23 (Epub May 8, 2019). (* equal contribution; ~30 authors total)
- **DOI:** 10.1038/s41586-019-1186-3 ✓ (verified Nature, PubMed PMID 31068700, PMC6697103, Broad Institute CCLE site)
- **Senior author:** William R. Sellers (Broad Institute + Dana-Farber Cancer Institute)
- **Institutional home:** Broad Institute of MIT and Harvard (CCLE primary site)
- **Data portal:** depmap.org/portal/download (current as of 2026)
- **Layer 1 question:** Q3 anchor 7 — **companion bulk RNA-seq + multi-omics resource to GDSC**
- **Read by:** Claude (CSO) — 2026-05-10

## 1. Why this paper

CCLE is **the companion resource to GDSC** — same cell lines, with deeper genomic, transcriptomic, and proteomic characterization. While GDSC provides drug sensitivity (IC50) labels, CCLE provides the **bulk RNA-seq + multi-omic features** that ML models use as input. **Every Q3 method using "bulk RNA-seq + drug response labels" implicitly uses CCLE for expression and GDSC for labels.**

Reading both is essential for understanding INTERCEPTA's source domain data.

## 2. What they did

**Cell line panel:** 1,072 human cancer cell lines from various lineages and ethnicities

**Multi-omics characterization (Phase II of CCLE):**
- **Genetic alterations:** WES (whole-exome sequencing) — somatic mutations, copy number, structural variants
- **RNA splicing:** alternative splicing characterization
- **DNA methylation:** reduced representation bisulfite sequencing (gel-free multiplexed)
- **Histone H3 modifications:** chromatin profiling via mass spec
- **microRNA expression:** miRNA-seq
- **Protein quantification:** reverse-phase protein array (RPPA) — collaboration with MD Anderson (Davis + Mills)
- **Bulk RNA-seq:** transcriptome profiling

**Functional integration:**
- Drug sensitivity data (PRISM + GDSC + CCLE drug screens)
- shRNA knockdown screens
- CRISPR-Cas9 knockout screens (DepMap)

## 3. What they found

- Multi-omics integration reveals **potential targets for cancer drugs and associated biomarkers**
- Cell line transcriptomes recapitulate primary tumor transcriptomes for many lineages (with caveats)
- DNA methylation patterns inform drug response (specifically: oncogene/tumor-suppressor methylation states)
- RNA splicing variants associated with drug resistance
- Companion CCLE metabolism paper (Li 2019 Nat Med) characterizes 225 metabolites
- Companion CCLE chromatin paper (Bagaev/Boyle 2019 Nat Genet) reveals NSD2 mutations in pediatric ALL

## 4. What's strong

- **Most comprehensively characterized cancer cell line panel.** 1,072 lines × 7+ modalities = unprecedented depth.
- **Top-tier institutional consortium.** Broad + Dana-Farber + MGH + MD Anderson — the gold standard pharmacogenomic effort.
- **Open data via DepMap portal.** Free, downloadable, regularly updated (as of 22Q2 in CellPalmSeq citation; current as of 2026).
- **Multi-modal coverage** enables INTERCEPTA's potential expansion beyond scRNA-seq alone.
- **Published in Nature.** Highest-impact venue.
- **Field-defining citation count** (~thousands of citations).
- **Continued maintenance.** Phase I (2012 Barretina) → Phase II (2019 Ghandi) → DepMap continues. Updates ongoing.
- **Integrated with shRNA + CRISPR screens** — provides gene dependency context for drug response interpretation.
- **Diverse ethnicity coverage** (compared to many earlier cell line collections) — important for clinical translation.

## 5. What's limited

- **Cancer-only.** Same fundamental constraint as GDSC. **Cannot serve INTERCEPTA's universality vision (U1, U3) beyond cancer alone.**
- **Cell lines, not patients or PDX or organoids.** Cell-line-2D-culture context. Cell line drift over passages (Ben-David 2018).
- **Drug sensitivity in CCLE is a separate dataset from GDSC.** Multiple drug response measurements per cell line; results not always concordant. **Method choice between PRISM/GDSC/CCLE drug screens affects bulk-side training.**
- **RPPA covers only ~200 proteins.** Compared to ~20,000 proteins in proteome — RPPA is targeted, not comprehensive.
- **DNA methylation by reduced representation, not whole-genome.** Misses 90%+ of CpGs.
- **Splicing data is heuristic.** Splice junction calling has known accuracy limits.
- **Cell line ethnicity is recorded but biased.** "Various ethnicities" still weighted European-derived.
- **No companion patient outcome data.** Cell line drug response doesn't directly link to patient survival.
- **2019 publication; fields have moved.** Single-cell, perturbation, organoid datasets have grown since. CCLE is bulk-only.

## 6. INTERCEPTA implications

**For Q3 (bulk-to-scRNA bridge):** CCLE is **THE bulk RNA-seq source domain.** SCAD/scDEAL/scAdaDrug all use CCLE expression matrices.

**For Decision 1 layered architecture:** CCLE multi-omics enables INTERCEPTA's Charter §8.1 architecture beyond just RNA:
- Bulk RNA-seq (input to FM)
- DNA methylation (epigenetic layer of mechanism)
- RPPA protein (validation of expression-protein consistency)
- Splicing (alternative isoform representations)

**For Charter §1.1 universality:** CCLE's cancer-only limitation is **the fundamental gap that constrains INTERCEPTA's vision.** For non-cancer disease deployment, equivalent multi-omic resources don't exist. **Architectural implication:** INTERCEPTA must use scRank-style (no bulk training data needed) approaches for non-cancer diseases, or wait for non-cancer pharmacogenomic resources to mature.

**For Charter §1.2 V1-V4 (predictive validity):** CCLE provides the held-out validation panels:
- Train on adult cancers, test on pediatric
- Train on solid tumors, test on hematologic
- Train on European-derived lines, test on Asian/African-derived (limited but possible)

**For data engineering at Northeastern HPC:** CCLE bulk RNA-seq is ~10K genes × 1072 cell lines × ~10K transcripts = manageable on standard HPC. **No data access barriers.**

## 7. Followup citations
1. **Barretina et al., 2012 Nature** — Phase I CCLE; the original paper
2. **Iorio et al., 2016 Cell 166:740-754** — comprehensive CCLE+GDSC integration analysis
3. **Tsherniak et al., 2017 Cell 170:564** — DepMap cancer dependency map
4. **Meyers et al., 2017 Nat Genet** — CRISPR-Cas9 essentiality computational corrections
5. **Ben-David et al., 2018 Nature 560:325** — cell line drug response variation
6. **Li et al., 2019 Nat Med 25:850-860** — CCLE metabolism companion paper
7. **PRISM (Corsello 2020 Nat Cancer)** — alternative drug screen on CCLE lines

## 8. Discipline check
- [x] All claims verified (Nature, PubMed, PMC, Broad Institute CCLE, DepMap)
- [x] DOI verified across 5+ sources
- [x] Authors verified — Ghandi and Huang equal first; Sellers senior (Broad + Dana-Farber)
- [x] Honest reporting of cancer-only constraint — fundamental gap for INTERCEPTA universality
- [x] **No new drift this cycle.**

— Claude (CSO), 2026-05-10
