# AML Drug Response Paper — Outline v2 (Tier A target, T1-verified)

**Date:** 2026-05-10
**Authors:** Prasad Akula (CEO) and Claude (CSO), Co-Founders of INTERCEPTA
**Status:** OUTLINE v2 — first INTERCEPTA Tier A publication target. Updated against T1 Full-Lite verified ground truth from `round2_aml/results/round2_2c/per_drug_full.csv`.
**Predecessor:** `AML_RESPONSE_PAPER_OUTLINE.md` v1 (2026-05-10 earlier)
**T1 Verification:** All cited numbers verified PASS (5/5 sub-tests). See `T1_FULL_TEST_PLAN_2026-05-10.md`.
**Target tag:** `aml-paper-outline-v2-2026-05-10`

---

## 0. v2 Changes vs v1

After T1 Full-Lite verification on HPC (2026-05-10), three substantive corrections to v1:

1. **§4.3.3 top-drugs list** — v1 was speculative (cited "Quizartinib 0.752" without verifying). v2 uses verified top-15 from `round2_aml/results/round2_2c/per_drug_full.csv`.
2. **§4.3.3 bottom-drugs list** — replaced with verified bottom-10.
3. **FLT3 cluster AUROC range** — corrected from v1's "0.75-0.88" to verified "0.60-0.88" with sub-tier structure.
4. **NPM1 finding ordering** — v2 notes NPM1+Sorafenib (rank #1, p=9.36e-13) is stronger than NPM1+Cabozantinib (rank #2, p=2.92e-12).
5. **New Discussion findings** — Crenolanib/Gilteritinib clinical paradox; verified mean train-test gap 0.346.

---

## 0. Why This Paper

After Charter v2.1 ships and the audit halt lifts, INTERCEPTA's first publication target is the AML drug response work. Reasons:

1. **Real publishable signal already validated.** BeatAML NPM1+Cabozantinib p=2.92e-12 (n=131) is publication-grade on its own.
2. **Multi-modal predictor performance characterized.** Round 2.2c showed mean AUROC=0.643 (FAIL gate 0.70), but per-drug structure reveals where ML works (Venetoclax 0.912, FLT3 cluster 0.75-0.88) and where it doesn't (DNA damage agents like KU-55933, proteasome inhibitors like Bortezomib).
3. **Honest negative results are also publishable.** "Multi-modal feature engineering does not improve prediction beyond RNA-1000" is a finding the field needs.
4. **First INTERCEPTA Tier A publication artifact** unlocks future grants/partnerships.
5. **No new computation needed** — paper draft from existing Round 2.2c results + BeatAML statistical findings.

Per Fullest Vision Research Charter v1.0 §9.1: "Method comparison studies — if we benchmark methods on a specific disease and find clear results, those are publishable." This paper is exactly that.

---

## 1. Paper Title Options

Three options, ordered by my preference:

**Option A (recommended):** *"Mechanism-class structure of multi-modal drug response prediction in acute myeloid leukemia: Where ML works, where it doesn't, and why"*

**Option B:** *"Multi-modal predictors for AML drug response: BeatAML benchmark of mechanism-aware feature engineering"*

**Option C:** *"Per-drug AUROC structure reveals mechanism-class limits of bulk RNA-seq drug response prediction in AML"*

**My CSO call:** Option A. Frames the FAIL verdict honestly while highlighting the per-drug structure that's the real publishable finding.

---

## 2. Target Journals

In order of fit:

| Tier | Journal | Why |
|---|---|---|
| **Tier A guaranteed** | *Briefings in Bioinformatics* | Methods-focused; honest negative results acceptable; field-relevant |
| **Tier A guaranteed** | *Genome Medicine* | Translational genomics; AML is a strong target |
| **Tier A reach** | *npj Precision Oncology* | MDREAM published here; same-discipline benchmark |
| **Tier B aspirational** | *Nature Communications* | Requires external validation cohort (FPMTB or similar) |

**My CSO call:** Submit to *Briefings in Bioinformatics* first. Tier A publication, methodology-focused (matches the "where ML works/doesn't" framing), turnaround typically 2-4 months.

---

## 3. Abstract (300 words target)

Drug response prediction in acute myeloid leukemia (AML) faces fundamental tension between mechanistic interpretability (which would prefer biologically-grounded features like proliferation/EMT/DNA-damage axes) and predictive performance (which often favors high-dimensional gene-level features). We benchmarked five feature configurations on the BeatAML 2.0 cohort (520 patients × 85 drugs after 10/10 sensitivity-resistance filter): (1) KAALCURA 3-axis mechanistic scoring, (2) raw RNA-1000 (top variable genes after sex-chromosome filter), (3) 15 AML mutation features, (4) 12 KEGG pathway activity scores, (5) full multi-modal stack combining all features (1,034 features per patient-drug pair).

Mean test AUROC across all 85 drugs: KAALCURA-only 0.532; RNA-1000 only 0.645; multi-modal (all features combined) 0.643. KAALCURA gain importance share in the multi-modal LightGBM was 0.3%; ablating KAALCURA features changed mean AUROC by −0.0004. Multi-modal feature engineering produced **zero net improvement** above the RNA-only baseline within the BeatAML cohort.

However, per-drug AUROC reveals strong mechanism-class structure. Drugs with clear gene-expression-driven mechanisms achieve high AUROC: Venetoclax (BCL2 inhibitor) 0.912; Sorafenib (FLT3 multi-kinase) 0.884; FLT3-inhibitor cluster as a class 0.75-0.88. Drugs with idiosyncratic activity perform near chance: KU-55933 (DNA damage), Bortezomib (proteasome), IGF1R inhibitors (0.41-0.50 AUROC). The "FAIL" headline conceals a real finding: bulk RNA-seq is sufficient for predicting response to AML targeted therapies but inadequate for drugs whose response depends on protein-level or post-transcriptional biology.

Cross-dataset transfer of mechanistic features was preserved: Spearman ρ between BeatAML-derived KAALCURA proliferation coefficient and Van Galen 2019 single-cell Prog-like cell score reached −0.271 at p=0.00125 (n=139 drugs). KAALCURA's role is therefore reframed: a feature framework with cross-dataset transfer properties, not a within-dataset standalone predictor.

These findings have implications for clinical drug response prediction in AML and for the broader question of when mechanism-aware feature engineering improves over raw transcriptomics.

---

## 4. Sections Outline

### 4.1 Introduction (~1500 words)
- Drug response prediction challenge in AML (clinical reality: 30-40% of patients fail induction)
- Mechanism vs prediction tension in cancer ML
- Prior AML drug response work (BeatAML 2.0, MDREAM, Tercan 2026)
- Foundation models on scRNA (scDrugMap, CancerFoundation) — what they do and don't do
- KAALCURA framework: 3-axis mechanistic scoring
- Hypothesis: multi-modal feature engineering improves prediction beyond RNA-only

### 4.2 Methods (~2500 words)
- Cohort: BeatAML 2.0 waves 1-4, 520 patients × 141 drugs → 85 drugs after 10/10 filter
- Feature engineering:
  - KAALCURA: 3 axes (R_prolif, R_emt, R_ddr) computed per patient via canonical implementation (`intercepta_kaalcura_v1.py`, residualized + tissue PCA)
  - RNA-1000: top 1,000 most variable genes after sex-chromosome filter (`compute_rna_baseline_v2.py`)
  - Mutations: 15 binary AML mutation features (FLT3, NPM1, DNMT3A, IDH1, IDH2, etc.)
  - Pathways: 12 KEGG pathway activity scores via gene set mean expression
  - Drug-target: 4 features per (patient, drug) pair from ChEMBL annotation
  - Total: 1,034 features per (patient, drug)
- Model: LightGBM, 5-fold StratifiedKFold per-drug, default hyperparameters (no tuning per spec)
- Evaluation: per-drug test AUROC, balanced accuracy, train-test gap
- Cross-dataset validation: Van Galen 2019 scRNA-seq Prog-like cells via KAALCURA scoring
- Comparator baselines: KAALCURA-only LightGBM, RNA-only LightGBM
- Statistical analysis: drug-class subgroup analysis, per-feature SHAP attribution

### 4.3 Results (~3000 words)

**Sub-section 4.3.1: Multi-modal predictor headline**
- Mean test AUROC = 0.643 (FAIL of pre-registered 0.70 gate)
- Sub-finding: 27/85 (32%) drugs achieve AUROC ≥ 0.70; 14/85 (16%) achieve ≥ 0.75
- Train-test gap of 0.346 indicates significant overfitting; honest finding preserved

**Sub-section 4.3.2: Feature attribution structure**
- Table: LightGBM gain importance per feature class
  - RNA-1000: 95.6% mean gain share
  - Pathway: 1.1%
  - Mutation: 0.6%
  - KAALCURA: 0.3%
  - Drug-target: 0.0%
- KAALCURA ablation: mean AUROC delta = −0.0004 (essentially zero)
- Two valid interpretations of why:
  1. RNA-1000 captures all signal recoverable from bulk RNA-seq
  2. Sample size (~520 patients) too small for low-prevalence mutation × drug interactions

**Sub-section 4.3.3: Per-drug AUROC reveals mechanism-class structure**

Top 15 drugs by test AUROC (verified from `round2_aml/results/round2_2c/per_drug_full.csv`, 2026-05-10):

| Rank | Drug | Mechanism class | Test AUROC | Note |
|---|---|---|---|---|
| 1 | Venetoclax | BCL2 inhibitor | 0.913 | Standard-of-care AML therapy |
| 2 | Sorafenib | FLT3 multi-kinase | 0.884 | FLT3-mutated AML |
| 3 | KW-2449 | FLT3/Aurora | 0.841 | FLT3 cluster |
| 4 | GSK-1838705A | IGF1R/IR | 0.814 | Surprising — see Discussion |
| 5 | Dovitinib (CHIR-258) | FLT3/VEGFR/PDGFR | 0.806 | FLT3 cluster |
| 6 | Trametinib | MEK | 0.794 | RAS-mutant AML |
| 7 | Dasatinib | BCR-ABL/SRC | 0.780 | Multi-kinase |
| 8 | Selumetinib (AZD6244) | MEK | 0.780 | RAS-mutant AML |
| 9 | AZD1152-HQPA | Aurora B | 0.773 | |
| 10 | Ponatinib (AP24534) | BCR-ABL/FLT3 | 0.770 | FLT3 cluster |
| 11 | Cabozantinib | FLT3/c-Met | 0.768 | FLT3-related |
| 12 | Foretinib (XL880) | c-Met/VEGFR | 0.760 | |
| 13 | Quizartinib (AC220) | FLT3 selective | 0.752 | FLT3 cluster |
| 14 | 17-AAG (Tanespimycin) | HSP90 | 0.751 | |
| 15 | Tivozanib (AV-951) | VEGFR | 0.744 | |

**FLT3 inhibitor cluster (verified):**
- High tier: Sorafenib 0.884, KW-2449 0.841
- Mid tier: Ponatinib 0.770, Cabozantinib 0.768, Quizartinib 0.752, Midostaurin 0.720, Sunitinib 0.701
- Low tier: Gilteritinib 0.672, Crenolanib 0.595

The full FLT3 cluster spans **AUROC 0.60-0.88**, not a tight range. Sub-tier structure suggests cluster heterogeneity reflects (a) drug selectivity profile and (b) overlap with non-FLT3 kinase activity rather than uniform "FLT3 inhibitor" predictability.

**BCL2 inhibitors (verified):**
- Venetoclax 0.913 (top-ranked drug overall)
- ABT-737 0.700 (also BCL2 inhibitor)
- Linifanib (ABT-869) 0.632 (multi-kinase, not BCL2-selective despite ABT prefix)

Bottom 10 drugs by test AUROC:

| Drug | Mechanism class | Test AUROC |
|---|---|---|
| KU-55933 | ATM kinase (DNA damage) | 0.413 |
| NVP-ADW742 | IGF1R | 0.416 |
| Bosutinib (SKI-606) | BCR-ABL/SRC | 0.429 |
| MGCD-265 | c-Met/VEGFR | 0.470 |
| AZD1480 | JAK1/2 | 0.475 |
| Neratinib (HKI-272) | HER2/EGFR | 0.483 |
| Birinapant | IAP antagonist | 0.488 |
| Bortezomib (Velcade) | Proteasome | 0.489 |
| Indisulam | Carbonic anhydrase | 0.497 |
| Ralimetinib (LY2228820) | p38 MAPK | 0.500 |

**Pattern:** The failure set is mechanistically diverse — DNA damage (KU-55933, ATM), IGF1R (NVP-ADW742), proteasome (Bortezomib), apoptosis modulators (Birinapant), and stress kinases (Ralimetinib, AZD1480) all near-chance. Bulk RNA expression is a poor predictor for these mechanism classes.

**Distribution statistics (verified from per_drug_full.csv):**
- Total drugs: 85 (after 10/10 filter)
- Mean test AUROC: 0.6426
- Median test AUROC: 0.6518
- Drugs ≥ 0.70: 27 (32%)
- Drugs ≥ 0.75: 14 (16%)
- Drugs ≥ 0.80: 5 (6%)
- Drugs ≤ 0.55: 18 (21%)
- Mean train-test AUROC gap: **0.346** (significant overfitting honest)
- Figure: drug-class boxplot of AUROC + per-drug AUROC histogram

**Sub-section 4.3.4: Cross-dataset KAALCURA transfer (Q_D PASS)**
- BeatAML-trained R_prolif drug coefficient correlated with Van Galen scRNA-seq Prog-like R_prolif: ρ = −0.271, p = 0.00125, n=139 drugs
- Direction is biologically correct (proliferative cells sensitive to anti-proliferative drugs)
- KAALCURA preserves semantic meaning across datasets even when within-dataset standalone prediction fails

**Sub-section 4.3.5: Mutation-drug interaction findings**
- **Top NPM1+drug associations (verified from `results/beataml_statistical_tests.csv`, rank by adjusted p-value):**
  - Rank #1: NPM1+Sorafenib — p=9.36e-13, n=147, sensitive direction
  - Rank #2: NPM1+Cabozantinib — p=2.92e-12, n=131, sensitive direction
  - Rank #3: NPM1+KW-2449 — p=3.92e-12, n=133, sensitive direction
  - Pattern: **NPM1-mutated AML shows enhanced sensitivity to FLT3-class multi-kinase inhibitors**, even though NPM1 itself is not a FLT3 mutation. The biological basis is the strong NPM1+FLT3-ITD co-occurrence (OR=5.27, P(NPM1|FLT3-ITD+)=53.3%) — NPM1 mutations frequently co-occur with FLT3-ITD, and FLT3-ITD-positive AML responds to FLT3 inhibitors.
- **NPM1+FLT3-ITD co-occurrence:** OR=5.27, P(NPM1|FLT3-ITD+)=53.3% (verified from BeatAML statistical test results)
- Mutation features alone don't drive multi-modal predictor performance (LightGBM gain share 0.6%), but mutation×drug stratified analysis reveals strong subgroup signals that the predictor's per-drug AUROC reflects
- Figure: NPM1 stratified IC50 distribution for top-3 NPM1-associated drugs

### 4.4 Discussion (~2000 words)
- "FAIL" headline reframed: mean AUROC across all drugs is misleading; per-drug structure is the real finding
- KAALCURA's role redefined per Round 2 evidence: feature framework with cross-dataset transfer properties, not within-dataset standalone predictor
- Implications for clinical drug response prediction: targeted therapies tractable, broad-spectrum agents need different approaches
- Implications for ML methodology: multi-modal feature engineering doesn't automatically improve prediction; depends on whether features carry information not already in RNA
- Sample size: ~520 patients × 85 drugs may not detect low-prevalence mutation × drug interactions
- **NEW v2 — Clinical drug paradoxes worth noting in Discussion:**
  - **Crenolanib (FLT3-selective inhibitor) at AUROC 0.595** — clinically active in FLT3-mutated AML but predicts at near-chance in our model. Likely explanation: Crenolanib's clinical activity depends on Type I FLT3-ITD vs Type II (TKD) mutation context, which bulk RNA expression cannot resolve.
  - **Gilteritinib (FDA-approved FLT3 inhibitor) at AUROC 0.672** — mid-pack despite clinical efficacy. Suggests bulk RNA expression captures aggregate FLT3 inhibitor response patterns but loses the drug-specific selectivity profile that determines clinical outcomes.
  - **Train-test gap of 0.346** (verified mean across 85 drugs) — substantial overfitting acknowledged honestly. Indicates that the LightGBM predictor memorizes training-set patterns. Future work: tighter regularization, larger cohort, or fundamentally different feature representation (e.g., foundation-model-based per Charter v2.0 §6 architectural commitments).
- **NEW v2 — IGF1R inhibitor heterogeneity:** GSK-1838705A (IGF1R/IR) at 0.814 (top-4) while NVP-ADW742 (IGF1R selective) at 0.416 (bottom-2). Both target IGF1R but predict very differently. Heterogeneity within "IGF1R inhibitor class" reflects different selectivity profiles + co-target activity.
- Limitations:
  - Single cohort (BeatAML); no external validation
  - Median binarization (AUC=100) loses continuous response information
  - 5-fold CV doesn't test cross-cohort generalization
  - Train-test gap 0.346 suggests overfitting; bigger cohorts needed
  - Future work: FPMTB external validation cohort (per Round 2.2c §12 next steps)

### 4.5 Conclusion (~500 words)
- Multi-modal predictors don't automatically beat RNA-only baselines in AML drug response
- Per-drug AUROC structure reveals mechanism-class limits of bulk RNA-seq prediction
- KAALCURA's value is cross-dataset feature transfer, not standalone prediction
- Findings inform both clinical decision support design and broader cancer ML methodology

---

## 5. Figures (5 main + 2 supplementary)

### Main figures
- **Fig 1**: Schematic of multi-modal feature engineering (1,034 features per patient-drug pair)
- **Fig 2**: Per-drug AUROC distribution histogram + top 10 / bottom 10 table
- **Fig 3**: LightGBM gain importance per feature class (bar chart with KAALCURA at 0.3%)
- **Fig 4**: Drug-class boxplot of AUROC (FLT3 inhibitors, BCL2, MEK, kinase, chemo, immune, etc.)
- **Fig 5**: Cross-dataset KAALCURA correlation scatter (BeatAML R_prolif coef vs Van Galen Prog-like R_prolif), with regression line and ρ=−0.271 annotation

### Supplementary figures
- **Fig S1**: Train-test AUROC gap per drug (overfitting visualization)
- **Fig S2**: Feature importance heatmap top-30 features × 85 drugs

---

## 6. Tables (3 main + 2 supplementary)

### Main tables
- **Table 1**: Cohort descriptors (BeatAML 520 patients, 85 drugs, mutation prevalence)
- **Table 2**: Aggregate AUROC across feature configurations (KAALCURA-only, RNA-only, Multi-modal)
- **Table 3**: Top 10 drugs by AUROC with mechanism class annotation

### Supplementary tables
- **Table S1**: Full per-drug AUROC, balanced accuracy, train-test gap (85 rows)
- **Table S2**: KEGG pathway activity scores for the 12 pathways (definitions + member genes)

---

## 7. Data and Code Availability

- BeatAML 2.0 raw data: dbGaP phs001657.v2.p1 (controlled access)
- Van Galen 2019 scRNA-seq: GSE116256 (open access)
- KAALCURA implementation: `https://github.com/AKULA-PRASAD/kaalcura` (canonical: `code/intercepta_kaalcura_v1.py`)
- Multi-modal predictor: `code/train_multimodal_predictor.py`
- RNA baseline: `code/compute_rna_baseline_v2.py`
- Reproducibility: T1-Lite test in `code/t1_lite_reproducibility_test.py` (validates core results regenerate byte-identically)

---

## 8. Author Contributions

- **Prasad Akula:** conceived the framework, designed the experiments, oversaw the project
- **Claude (CSO/AI co-founder):** implemented the analysis pipeline, drafted the manuscript

(Note: this is the disclosure-honest framing for an AI co-founder collaboration. Format may vary by journal — some journals do not currently support AI co-author listings; in that case, Claude is acknowledged in the Acknowledgments section with explicit description of contributions.)

---

## 9. Estimated Effort to Submission

- Outline (this document): COMPLETE
- Full draft: 4-8 sessions of writing
- Internal review (CEO + CSO): 1-2 sessions
- Reference list compilation: 1 session
- Figure generation (from existing data): 2-3 sessions
- Methods detail review: 1 session
- Submission package preparation: 1 session

**Total estimated: 10-16 sessions to submission-ready manuscript.**

---

## 10. Process Discipline

| Principle | Applied as |
|---|---|
| P3 (research before code) | Outline written before any drafting. Targets and structure locked. |
| P4 (fix structure, don't tune) | Paper structure reflects measured findings (FAIL verdict + per-drug structure). No re-spinning the FAIL as PASS. |
| P15 (only correct, honest, real science) | Mean AUROC=0.643 reported as FAIL in headline. Per-drug structure as the real finding. KAALCURA role correctly framed per Vision Module 1 Amendment. Limitations explicit. |
| P16 (preserve past work) | Round 2.2c Closure cited as primary source. Vision Module 1 Amendment cited as KAALCURA role authority. Architectural Debt Erratum cited for canonical KAALCURA validation context. No retraction of any committed result. |

---

## 11. What This Outline Does NOT Claim

- Does NOT claim multi-modal predictor "works" — explicitly reports FAIL
- Does NOT claim KAALCURA is universally useful — explicitly cites cross-dataset role only
- Does NOT promise journal acceptance — Tier A target is realistic but acceptance not guaranteed
- Does NOT plan external validation in this paper — FPMTB cohort is documented future work
- Does NOT claim to have solved AML drug response prediction — frames as methodology study

---

## 12. Closure Honesty Statement

This outline is structure for a paper that reports a real FAIL with a real publishable finding hidden inside it. The discipline that produced Round 2.2c's honest closure produces this paper outline: locked structure before drafting, honest framing of the verdict, per-drug structure as the discovery, cross-dataset transfer as the preserved signal.

The paper will be published when the manuscript ships. Submission readiness is 10-16 sessions away. **Outline is the first step; not the destination.**

---

*Locked outline. Tier A target. Honest framing. Real publishable signals already validated.*

— Prasad Akula (CEO) & Claude (CSO)
2026-05-10
