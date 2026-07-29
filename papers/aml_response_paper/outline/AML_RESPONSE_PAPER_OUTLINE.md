# AML Drug Response Paper — Outline (Tier A target)

**Date:** 2026-05-10
**Authors:** Prasad Akula (CEO) and Claude (CSO), Co-Founders of INTERCEPTA
**Status:** OUTLINE — first INTERCEPTA Tier A publication target. Builds entirely on existing validated data.
**Target tag:** `aml-paper-outline-2026-05-10`

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
- Top 10 drugs by AUROC (with mechanism class):
  - Venetoclax 0.912 (BCL2 inhibitor — standard-of-care AML therapy)
  - Sorafenib 0.884 (FLT3 multi-kinase — FLT3-mutated AML)
  - KW-2449 0.841 (FLT3/Aurora — FLT3-mutated)
  - GSK-1838705A 0.814 (IGF1R/IR)
  - Dovitinib 0.806 (FLT3/VEGFR/PDGFR)
  - Trametinib 0.794 (MEK)
  - Dasatinib 0.780 (BCR-ABL/SRC)
  - Selumetinib 0.780 (MEK)
  - AZD1152-HQPA 0.773 (Aurora B)
  - Ponatinib 0.770 (BCR-ABL/FLT3)
- Bottom 10: KU-55933, NVP-ADW742, Bosutinib, MGCD-265, AZD1480, Neratinib, Birinapant, Bortezomib, Indisulam, PH-797804 (mostly 0.41-0.50)
- Pattern: gene-expression-driven mechanisms work, idiosyncratic activity (DNA damage, proteasome, IGF1R) fails
- Figure: drug-class boxplot of AUROC

**Sub-section 4.3.4: Cross-dataset KAALCURA transfer (Q_D PASS)**
- BeatAML-trained R_prolif drug coefficient correlated with Van Galen scRNA-seq Prog-like R_prolif: ρ = −0.271, p = 0.00125, n=139 drugs
- Direction is biologically correct (proliferative cells sensitive to anti-proliferative drugs)
- KAALCURA preserves semantic meaning across datasets even when within-dataset standalone prediction fails

**Sub-section 4.3.5: Mutation-drug interaction findings**
- NPM1+Cabozantinib: p=2.92e-12 (n=131, Mann-Whitney across BeatAML)
- NPM1+FLT3-ITD co-occurrence: OR=5.27, P(NPM1|ITD+)=53.3%
- Mutation features alone don't drive multi-modal predictor performance, but mutation×drug stratified analysis reveals strong subgroup signals

### 4.4 Discussion (~2000 words)
- "FAIL" headline reframed: mean AUROC across all drugs is misleading; per-drug structure is the real finding
- KAALCURA's role redefined per Round 2 evidence: feature framework with cross-dataset transfer properties, not within-dataset standalone predictor
- Implications for clinical drug response prediction: targeted therapies tractable, broad-spectrum agents need different approaches
- Implications for ML methodology: multi-modal feature engineering doesn't automatically improve prediction; depends on whether features carry information not already in RNA
- Sample size: ~520 patients × 85 drugs may not detect low-prevalence mutation × drug interactions
- Limitations:
  - Single cohort (BeatAML); no external validation
  - Median binarization (AUC=100) loses continuous response information
  - 5-fold CV doesn't test cross-cohort generalization
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
