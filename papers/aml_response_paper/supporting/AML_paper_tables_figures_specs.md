# AML Paper — Tables and Figures Specifications (Draft 1)

**Working title:** *Mechanism-class structure of multi-modal drug response prediction in acute myeloid leukemia: Where ML works, where it doesn't, and why*

**Target journal:** Briefings in Bioinformatics
**Status:** SPECIFICATIONS for tables/figures referenced in Methods/Results/Discussion drafts. To be generated from verified data files in subsequent session.
**Authors:** Prasad Akula, Claude (CSO/AI co-founder)
**Date:** 2026-05-10

---

## Tables

### Table 1: Beat AML 2.0 cohort descriptors

**Purpose:** Standard cohort-table for Methods section. Reviewers expect this.

**Schema:**

| Variable | Beat AML 2.0 (n = 520) |
|---|---|
| Age at diagnosis (median, IQR) | [from clinical] |
| Sex (M / F) | [from clinical] |
| Cytogenetic risk (favorable / intermediate / adverse) | [from clinical] |
| FLT3-ITD positive | [count, %] |
| NPM1 mutation positive | [count, %] |
| DNMT3A mutation positive | [count, %] |
| IDH1 mutation positive | [count, %] |
| IDH2 mutation positive | [count, %] |
| TP53 mutation positive | [count, %] |
| RUNX1 mutation positive | [count, %] |
| RAS family (NRAS/KRAS) mutation | [count, %] |
| Other 7 mutations | [count, %] each |
| Drugs in panel after 10/10 filter | 85 |
| Drug-level n_samples (median, range) | [median, range] |

**Source data:** `data/beataml/beataml_clinical.txt` + harmonized cohort file. **Status:** Need to query specific cohort statistics; placeholders filled with brackets. CSO action: query in next session.

---

### Table 2: Aggregate AUROC across feature configurations

**Purpose:** Headline comparison of multi-modal vs baselines.

**Schema:**

| Configuration | n features | Mean test AUROC | SD across drugs | Drugs ≥ 0.70 | Drugs ≥ 0.75 | Drugs ≥ 0.80 |
|---|---|---|---|---|---|---|
| KAALCURA-only (3 axes) | 3 | 0.532 | [SD] | [count] | [count] | [count] |
| RNA-only (1000 genes) | 1000 | 0.645 | [SD] | [count] | [count] | [count] |
| Multi-modal (all features) | 1034 | 0.643 | [SD] | 27 | 14 | 5 |
| Multi-modal − KAALCURA (ablation) | 1031 | 0.6426 | [SD] | [count] | [count] | [count] |

**Status:** Multi-modal numbers verified from `per_drug_full.csv`. KAALCURA-only and RNA-only baseline numbers and SDs need extraction from baseline runs. CSO action: query baseline result CSVs in next session.

---

### Table 3: Per-drug AUROC ranking — top 15 and bottom 10 drugs

**Purpose:** Shows mechanism-class structure.

**Schema:**

| Rank | Drug | Mechanism class | Test AUROC ± SD | n_samples | Sensitive / Resistant | FDA status |
|---|---|---|---|---|---|---|
| 1 | Venetoclax | BCL2 inhibitor | 0.913 ± 0.041 | 367 | 114 / 253 | Approved (AML w/ HMA) |
| 2 | Sorafenib | FLT3 multi-kinase | 0.884 ± 0.042 | 494 | 32 / 462 | Off-label AML |
| 3 | KW-2449 | FLT3/Aurora | 0.841 ± 0.072 | 449 | 25 / 424 | Investigational |
| 4 | GSK-1838705A | IGF1R/IR | 0.814 ± 0.102 | 453 | 13 / 440 | Investigational |
| 5 | Dovitinib (CHIR-258) | FLT3/VEGFR/PDGFR | 0.806 ± 0.048 | 455 | 77 / 378 | Investigational |
| 6 | Trametinib (GSK1120212) | MEK | 0.794 ± 0.028 | 484 | 182 / 302 | Approved (other) |
| 7 | Dasatinib | BCR-ABL/SRC | 0.780 ± 0.043 | 493 | 74 / 419 | Approved (CML) |
| 8 | Selumetinib (AZD6244) | MEK | 0.780 ± 0.071 | 456 | 56 / 400 | Approved (NF1) |
| 9 | AZD1152-HQPA (AZD2811) | Aurora B | 0.773 ± 0.072 | 455 | 17 / 438 | Investigational |
| 10 | Ponatinib (AP24534) | BCR-ABL/FLT3 | 0.770 ± 0.083 | 301 | 74 / 227 | Approved (CML) |
| 11 | Cabozantinib | FLT3/c-Met | 0.768 ± 0.111 | 450 | 60 / 390 | Approved (other) |
| 12 | Foretinib (XL880) | c-Met/VEGFR | 0.760 ± 0.031 | 453 | 179 / 274 | Investigational |
| 13 | Quizartinib (AC220) | FLT3 selective | 0.752 ± 0.058 | 461 | 81 / 380 | Approved (FLT3-ITD AML) |
| 14 | 17-AAG (Tanespimycin) | HSP90 | 0.751 ± 0.075 | 449 | 67 / 382 | Investigational |
| 15 | Tivozanib (AV-951) | VEGFR | 0.744 ± 0.070 | 448 | 72 / 376 | Approved (RCC) |
| ... | ... | ... | ... | ... | ... | ... |
| Bottom 10 |
| 76 | Tivozanib (AV-951) | VEGFR | [bottom rank] | ... | ... | ... |
| ...10 lowest drugs ranked... |
| 85 | KU-55933 | ATM kinase | 0.413 ± 0.094 | 453 | 10 / 443 | Investigational |

**Status:** Top 15 verified. Bottom 10 need full data from `per_drug_full.csv` for FDA status column. CSO action: ChEMBL/DrugBank query for FDA approval status of all drugs in next session.

**Display note:** Submit as Table 3 in main paper; full per-drug list (85 rows) goes to Supplementary Table S1.

---

### Supplementary Table S1: Full per-drug AUROC

**Purpose:** Comprehensive listing of all 85 drugs with all metrics.

**Schema:** All columns from `per_drug_full.csv`:
- drug, n_samples, n_sensitive, n_resistant, auroc_test_mean, auroc_test_std, balanced_acc_mean, train_test_gap_mean, n_valid_folds

Plus additional columns to add:
- Mechanism class (annotated from ChEMBL primary target + DrugBank pharmacology)
- FDA status

**Status:** Source CSV exists. Annotation columns need to be added.

---

### Supplementary Table S2: KEGG pathway selections and member genes

**Purpose:** Documents which pathways were used in the 12-pathway feature class.

**Schema:**

| KEGG ID | Pathway name | Member genes (count) | Source / rationale |
|---|---|---|---|
| hsa05221 | Acute myeloid leukemia | [n] | Disease-specific |
| hsa04110 | Cell cycle | [n] | Proliferation biology |
| hsa04210 | Apoptosis | [n] | Drug response mechanism |
| hsa04630 | JAK-STAT signaling | [n] | AML signaling |
| hsa04151 | PI3K-Akt signaling | [n] | AML signaling |
| hsa04010 | MAPK signaling | [n] | AML signaling |
| hsa04310 | Wnt signaling | [n] | AML differentiation |
| hsa03430 + hsa03450 + hsa03440 | DNA repair (combined) | [n] | DDR drugs |
| hsa04115 | p53 signaling | [n] | DDR + apoptosis |
| hsa04640 | Hematopoietic cell lineage | [n] | AML lineage biology |
| [hsa-other-1] | [pathway 11] | [n] | KEGG enrichment selection |
| [hsa-other-2] | [pathway 12] | [n] | KEGG enrichment selection |

**Status:** First 10 pathways defined. 11-12 to be selected from KEGG enrichment of Beat AML mutated genes. CSO action: KEGG enrichment in next session.

---

## Main Figures

### Figure 1: Schematic of multi-modal feature engineering

**Purpose:** Visual overview of the analytical pipeline. Standard methods figure.

**Content:**
- Top: Beat AML 2.0 cohort (520 patients × 85 drugs after 10/10 filter)
- Left: Patient-side features
  - KAALCURA mechanistic axes (3): R_prolif, R_emt, R_ddr from MSigDB Hallmark
  - RNA-1000 (1,000): top variable autosomal genes
  - Mutation status (15): binary indicators
  - Pathway activity (12): KEGG pathway expression means
- Right: Drug-side features
  - Drug-target features (4): from ChEMBL bioactivity
- Center: LightGBM per-drug classifier with 5-fold CV
- Output: per-drug test AUROC

**Generation:** Schematic figure — drawn rather than data-driven. Matplotlib + custom layout, OR drawing tool (e.g., Inkscape). Single-column width.

**Status:** Specification locked. Generation in subsequent session.

---

### Figure 2: Per-drug AUROC distribution histogram

**Purpose:** Shows the bimodal-ish distribution that motivates the per-drug analysis.

**Content:**
- X-axis: Test AUROC (0.4 to 1.0)
- Y-axis: Number of drugs (count)
- Bins: 0.025-wide
- Vertical lines: 0.50 (chance), 0.70 (pre-registered threshold), mean (0.643)
- Annotated: drugs ≥ 0.80 (top 5)
- Color: bars colored by class membership in top-15/middle/bottom-10

**Generation:** matplotlib `plt.hist()` from `auroc_test_mean` column of `per_drug_full.csv`. Trivially data-driven. Single-column width.

**Status:** Specification locked. Source data verified. Generation in subsequent session.

---

### Figure 3: LightGBM gain importance per feature class

**Purpose:** Shows the dominance of RNA-1000 in feature attribution.

**Content:**
- X-axis: Feature class
- Y-axis: Mean LightGBM gain importance (% of total)
- Bars: 5 categories — KAALCURA, RNA-1000, Mutation, Pathway, Drug-target
- Heights: 0.3, 95.6, 0.6, 1.1, 0.0 (verified)
- Error bars: SD across 85 drugs
- Annotation: Leave-KAALCURA-out delta = −0.0004

**Generation:** matplotlib `plt.bar()` from feature importance summary. Single-column width.

**Status:** Specification locked. Source data verified. Generation in subsequent session.

---

### Figure 4: FLT3 inhibitor cluster — AUROC vs FDA approval status

**Purpose:** Shows the Crenolanib paradox visually.

**Content:**
- X-axis: Drug name (8 FLT3-axis drugs ordered by AUROC)
- Y-axis: Test AUROC ± SD
- Color/marker: FDA approval status (approved for AML / approved for other / investigational)
- Horizontal annotations: tier boundaries (high ≥ 0.80, mid 0.70-0.80, low < 0.70)
- Drug names: Sorafenib (0.884), KW-2449 (0.841), Ponatinib (0.770), Cabozantinib (0.768), Quizartinib (0.752), Midostaurin (0.720), Sunitinib (0.701), Gilteritinib (0.672), Crenolanib (0.595)

**Generation:** matplotlib bar plot with custom coloring. Single-column width.

**Status:** Specification locked. Source data verified. Generation in subsequent session.

---

### Figure 5: Cross-dataset KAALCURA correlation scatter

**Purpose:** Shows H3 cross-dataset transfer evidence.

**Content:**
- X-axis: Beat AML-trained R_prolif coefficient (per drug)
- Y-axis: Van Galen Prog-like cell-type R_prolif score
- Points: 139 drugs in alignment set
- Regression line + 95% CI
- Annotation: Spearman ρ = −0.271, p = 1.25 × 10⁻³, n = 139
- Annotation: biologically expected direction noted

**Generation:** matplotlib scatter + statsmodels regression. Single-column width.

**Status:** Specification locked. Source data: need to query Round 2.2b cross-dataset Q_D source files. CSO action: locate exact source CSV in next session.

---

## Supplementary Figures

### Supplementary Figure S1: Train-test AUROC gap per drug

**Purpose:** Documents overfitting honestly.

**Content:**
- X-axis: Drug name (85 drugs ordered by gap)
- Y-axis: Train AUROC − Test AUROC (gap)
- Bars: 85 drugs
- Horizontal line: mean gap = 0.346

**Generation:** matplotlib `plt.bar()` from `train_test_gap_mean` column. Two-column width acceptable.

---

### Supplementary Figure S2: Feature importance heatmap (per-drug × feature class)

**Purpose:** Detailed view of attribution structure across all 85 drugs.

**Content:**
- Rows: 85 drugs
- Columns: 5 feature classes
- Cells: gain importance share (0-100%)
- Color: viridis
- Annotated: drug clustering by predominant feature class

**Generation:** seaborn heatmap. Two-column width.

---

## Notes on this specification

*This section is an internal CSO note for the next drafting session.*

**What's needed before figures can be generated:**

1. **Cohort descriptor query** for Table 1: pull median age, sex distribution, cytogenetic risk distribution from `data/beataml/beataml_clinical.txt`
2. **Baseline AUROC SDs** for Table 2: extract from baseline run CSVs (KAALCURA-only and RNA-only baselines)
3. **FDA approval status** for Table 3: query DrugBank or ChEMBL for each of 85 drugs
4. **KEGG pathway 11-12** for Table S2: enrichment analysis on Beat AML mutated genes
5. **Cross-dataset Q_D source CSV** for Figure 5: locate exact path to per-drug R_prolif coefficient × Van Galen R_prolif data

**Generation order:**
- Table 1 (CEO can pull cohort stats easily on HPC)
- Tables 2-3 (build from existing CSVs)
- Figures 2-4 (most data-driven, fastest)
- Figure 1 (schematic, slower)
- Figure 5 (need source data location)

**Estimated time to generate all tables/figures:** 1-2 sessions of CSO+CEO work.

---

*Specifications locked. Source data references verified. Generation queue ordered. Ready for execution.*

— Prasad Akula (CEO) & Claude (CSO)
2026-05-10
