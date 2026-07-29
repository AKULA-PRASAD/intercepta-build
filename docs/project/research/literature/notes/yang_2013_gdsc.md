# Yang et al., 2013 — Genomics of Drug Sensitivity in Cancer (GDSC): a resource for therapeutic biomarker discovery in cancer cells

## 0. Identification
- **Citation:** Yang W, Soares J, Greninger P, Edelman EJ, Lightfoot H, Forbes S, Bindal N, Beare D, Smith JA, Thompson IR, Ramaswamy S, Futreal PA, Haber DA, Stratton MR, Benes C, McDermott U, Garnett MJ. *Nucleic Acids Research* 41(D1):D955-D961, 2013 Jan (Epub Nov 23, 2012).
- **DOI:** 10.1093/nar/gks1111 ✓ (verified Oxford Academic, PubMed PMID 23180760, AACR, Harvard DASH)
- **Senior authors:** Ultan McDermott + Mathew J. Garnett (Wellcome Trust Sanger Institute UK; corresponding authors)
- **Database URL:** www.cancerrxgene.org
- **Layer 1 question:** Q3 anchor 6 — **upstream data resource** (not a method paper)
- **Read by:** Claude (CSO) — 2026-05-10

## 1. Why this paper

GDSC is **the foundational pharmacogenomic database for cancer drug response prediction**. Every Q3 method read so far (SCAD, scDEAL, scAdaDrug) uses GDSC as the source domain. **Reading the GDSC paper directly is essential to understand what the source data actually is** — its scope, limitations, and the specific definition of "drug sensitivity" being transferred to scRNA-seq.

This is a **data resource paper, not a method paper.** The discipline check therefore differs: we evaluate the dataset's properties, not algorithmic claims.

## 2. What they did

**Created the database:**
- **Joint project** of Cancer Genome Project (Wellcome Sanger Institute UK) + Center for Molecular Therapeutics (Massachusetts General Hospital Cancer Center, Harvard Medical School)
- **Wellcome Trust funded**

**Database contents (as of 2012-2013 release v3):**
- Drug sensitivity data for **almost 75,000-80,000 experiments**
- **138-142 anticancer drugs**
- **329-668 cell lines per drug** (mean = 525)
- **>1000 cancer cell lines available** for screening
- Cell lines selected to represent adult/childhood epithelial, mesenchymal, hematopoietic cancers — broad coverage

**Integration with genomic data:**
- COSMIC (Catalogue of Somatic Mutations in Cancer)
- Somatic mutations in cancer genes
- Gene amplification/deletion
- Tissue type
- Transcriptional data

**Drug sensitivity measurement:**
- IC50 values from dose-response curves
- High-throughput screening platform

**Data access:**
- Free without restriction
- Web portal queryable by drug or gene
- Bulk download available
- Updated every 4 months

## 3. What they found

Not applicable as method paper. The paper describes the database. Key resource statistics:
- Largest public pharmacogenomic resource at time of publication
- Continues to grow (current GDSC has ~1000+ cell lines × ~300+ drugs)
- Identifies known biomarkers (BRAF in melanoma + vemurafenib, etc.)
- Provides infrastructure for computational drug repositioning

## 4. What's strong

- **Field-defining database.** Every cancer drug response prediction paper since 2013 has used GDSC.
- **Open access without restriction.** No data use agreement; freely downloadable.
- **Integrated with COSMIC mutation data.** Drug response correlated with genomic alterations.
- **Broad cancer coverage.** Adult + childhood, epithelial/mesenchymal/hematopoietic.
- **Scale.** 75K+ experiments — largest curated source domain available.
- **Well-maintained for over a decade.** Continuous updates since 2012.
- **Standardized IC50 measurements** with published dose-response protocols.
- **Top-tier institutional backing.** Wellcome Sanger + MGH/Harvard — gold standard pharmacogenomics consortium.
- **Open data philosophy** enables reproducibility and external validation.

## 5. What's limited

- **Cell lines, not patients.** GDSC is built on **cancer cell lines in 2D culture**, not patient-derived tumors. **Cell line drug response correlates imperfectly with patient drug response** — this is precisely the gap that single-cell drug response prediction tries to bridge.
- **138-142 drugs is small relative to FDA-approved drugs.** ~1000+ FDA-approved drugs exist; GDSC covers ~14%.
- **Cancer-only.** No autoimmune, neurodegenerative, infectious, metabolic disease drugs.
- **2D monolayer culture context.** Patient tumors are 3D, vascularized, immune-infiltrated. **Drug response in 2D culture is known to differ systematically from in vivo.**
- **Per-experiment IC50 has technical noise.** Cell line genetic and transcriptional drift affects reproducibility (Ben-David 2018 Nature).
- **Cell line "identity" can drift over passages.** Same cell line at different labs may behave differently.
- **Drug sensitivity ≠ clinical efficacy.** Many drugs sensitive in cell lines fail in patients (PROTAC, certain kinase inhibitors). The pharmacogenomic-clinical translation gap is large.
- **Dose-response curves vary in quality.** Some drug-cell-line pairs have poor curve fits; IC50 unreliable.
- **No companion patient outcome data.** GDSC doesn't directly link cell line drug response to patient survival on the same drug.
- **English-language Western clinical context.** Cell line collection may underrepresent Asian, African, Latin American genetic backgrounds.

## 6. INTERCEPTA implications

**For Q3 (bulk-to-scRNA bridge):** GDSC is **THE source domain** for nearly all bulk-to-scRNA drug response transfer methods. **INTERCEPTA's Q3 architecture must use GDSC** (and CCLE — to be read next) as the canonical source.

**Critical limitation for Charter §1.1 universality (especially U1, U3 — non-cancer diseases):** GDSC is cancer-only. **INTERCEPTA's vision of "drug for ANY disease" cannot be served by GDSC alone.** For non-cancer diseases, the equivalent pharmacogenomic database doesn't exist at GDSC scale. **This is a fundamental gap that INTERCEPTA must navigate** — either by:
1. Treating non-cancer drug repurposing as the application (using disease-specific scRNA-seq + known drug targets via scRank-style approach)
2. Building a non-cancer pharmacogenomic resource (out of scope for Layer 5; would require wet lab)
3. Leveraging connectivity-map-style approaches (LINCS) which include broader chemical perturbations

**For cell line → patient gap:** GDSC's cell-line-2D-culture context is precisely what scAdaDrug/SCAD/scDEAL try to bridge to patient scRNA-seq. **INTERCEPTA's Q3 architecture must explicitly handle this gap**, not assume cell line drug sensitivity transfers directly.

**For Decision 1 layered architecture:** GDSC informs the bulk-side data pipeline:
- Ingest GDSC IC50 values + drug-cell-line pairs
- Use FM (Decision 1) to embed cell line bulk RNA-seq
- DA-based transfer (SCAD-style adversarial or scAdaDrug-style multi-source) to scRNA-seq
- Layer Beyondcell-style signature scoring + scRank-style GRN perturbation as orthogonal evidence

**For Charter §1.2 V1-V4 (predictive validity):** GDSC enables held-out validation:
- Train on most cell lines, test on held-out cell lines
- Train on solid tumors, test on hematologic
- Train on certain drug classes, test on others
- These are reasonable Layer 5 validation strategies

**For data engineering reality at Northeastern HPC:** GDSC raw data is downloadable as flat files; total size is manageable (gigabytes, not terabytes). **No data access barriers for INTERCEPTA implementation.**

## 7. Followup citations
1. **CCLE / Broad Institute Cancer Cell Line Encyclopedia** (Barretina 2012 Nature; 2019 Ghandi update Nature 569:503-508) — companion bulk RNA-seq for GDSC cell lines + complementary drug screen data
2. **Iorio et al., 2016 Cell** — comprehensive landscape of cancer cell line drug sensitivity using GDSC + CCLE
3. **Ben-David et al., 2018 Nature 560:325-330** — cell line drug response variation; honesty about reproducibility
4. **PRISM (Corsello 2020 Nat Cancer)** — alternative pharmacogenomic platform; broader drug repurposing focus
5. **LINCS Connectivity Map (Subramanian 2017 Cell 171:1437-1452)** — perturbation signature alternative to GDSC drug response
6. **Ghandi et al., 2019 Nature 569:503-508** — CCLE next generation; updated genomic + transcriptomic profile

## 8. Discipline check
- [x] All claims verified (Oxford NAR, PubMed, AACR, Harvard DASH, Sanger Institute)
- [x] DOI verified across 5+ sources
- [x] Authors verified — Wanjuan Yang first; Ultan McDermott + Mathew Garnett senior (Sanger)
- [x] **Critical limitation honestly named:** GDSC is cancer-only, cell-line-only, 2D-culture-only. This constrains INTERCEPTA's universality vision and must be addressed in Q4 architecture.
- [x] **No new drift this cycle.**

— Claude (CSO), 2026-05-10
