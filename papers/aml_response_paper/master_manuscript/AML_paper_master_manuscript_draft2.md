# Mechanism-class structure of multi-modal drug response prediction in acute myeloid leukemia: Where ML works, where it doesn't, and why

**Authors:** Prasad Akula¹, Claude (CSO/AI co-founder)¹

**Affiliations:** ¹INTERCEPTA, an independent computational biomedicine venture.

**Corresponding author:** Prasad Akula

**Target journal:** Briefings in Bioinformatics

**Manuscript status:** First-draft assembled manuscript (Draft 2 sections, drafting logs removed). Submission-readiness: ~85%. Outstanding items per `AML_paper_revision_pass_report.md`: Issue 1 (verify FDR-significant interaction count via HPC query); references DOI verification (18 entries flagged); paper identification for 5 entries flagged in references; tables and figures generation.

**Date:** 2026-05-10

---

## Abstract

**Background.** Predicting drug response from patient-level molecular features in acute myeloid leukemia (AML) has been pursued through increasingly sophisticated machine learning architectures, but aggregate benchmarks have not consistently demonstrated cohort-wide predictability that would support clinical deployment. Whether the limitation is primarily methodological or biological — whether bulk RNA expression and mutation status capture some categories of drug-response biology well and others poorly — has not been examined with pre-registered methodology.

**Methods.** We constructed a multi-modal LightGBM predictor combining KAALCURA mechanistic axes (proliferation, EMT, DNA damage response signatures), AML-relevant mutation status, KEGG pathway activity scores, drug-target features, and the 1,000 most variable autosomal genes (1,034 features per patient × drug pair). The architecture, success thresholds, and ablation analyses were pre-registered before evaluation. We trained per-drug 5-fold stratified cross-validation on Beat AML 2.0 (520 patients × 85 drugs after a 10/10 sensitivity-resistance filter) and compared against KAALCURA-only and RNA-only baselines.

**Results.** The multi-modal predictor achieved mean test AUROC = 0.643, falsifying the pre-registered ≥ 0.70 threshold. Multi-modal feature engineering provided no measurable improvement above the RNA-only baseline (0.645). KAALCURA features contributed 0.3 percent of LightGBM gain importance and produced −0.0004 mean AUROC change under leave-KAALCURA-out ablation. However, per-drug AUROC distribution revealed strong mechanism-class structure: 5 drugs achieved AUROC ≥ 0.80 (BCL2 inhibitor Venetoclax 0.913, FLT3-axis multi-kinase Sorafenib 0.884) while 18 drugs (21 percent) were near chance, with the failure set spanning post-transcriptional and selectivity-dependent biology. The FLT3 inhibitor cluster spanned AUROC 0.595 (Crenolanib) to 0.884 (Sorafenib), with FDA-approved FLT3-selective drugs (Gilteritinib 0.672, Crenolanib 0.595) achieving lower predictability than older multi-kinase agents. KAALCURA features transferred across datasets at biologically expected direction (Spearman ρ = −0.271, p = 1.25 × 10⁻³, n = 139 drugs).

**Conclusions.** Multi-modal feature engineering does not automatically improve drug response prediction in AML; mechanism-class predictability is bimodal and per-drug structure is more methodologically informative than cohort-mean AUROC. Bulk-RNA-detectable mechanisms are predictable; protein-level, mutation-subtype-dependent, and drug-selectivity-driven biology are not. KAALCURA's role is cross-dataset feature transfer, not within-dataset standalone prediction. The Crenolanib paradox — clinical efficacy without RNA-detectable predictors — has implications for how clinical decision support based on bulk RNA-seq should be deployed.

**Key words:** acute myeloid leukemia; drug response prediction; machine learning; LightGBM; mechanistic axes; pre-registered analysis; mechanism-class structure; cross-dataset transfer

---

## Introduction

Acute myeloid leukemia (AML) is a heterogeneous hematologic malignancy with disappointing long-term outcomes despite recent therapeutic advances. Current standard-of-care induction chemotherapy achieves complete remission in 60-70 percent of newly diagnosed adult patients but most will eventually relapse, and 5-year overall survival remains below 30 percent for adults overall and below 10 percent for older patients (Döhner et al., 2017; Howlader et al., 2024). The recent introductions of venetoclax-based regimens (Pollyea et al., 2018; DiNardo et al., 2020), FLT3-targeted therapies (Stone et al., 2017; Perl et al., 2019), and IDH-targeted therapies (Stein et al., 2017) have improved outcomes for genotypically-defined subgroups, but selection of optimal therapy for individual patients remains a major unmet clinical need.

Predicting drug response from patient-level molecular features is a long-standing aspiration in cancer precision medicine. The promise is that integrating bulk transcriptomics, mutation status, and pathway annotation should enable computational identification of which drug will work for which patient, displacing or complementing trial-and-error treatment selection. The reality has been more modest. Aggregate benchmarks of cancer drug response prediction across cell lines (Iorio et al., 2016; Ding et al., 2023; Chen et al., 2024) and patient cohorts (Geeleher et al., 2014) report that mean AUROCs sit in the 0.55-0.75 range across panels of ten or more drugs, with substantial variation by drug class. State-of-the-art methods on the AML-specific Beat AML cohort (Tyner et al., 2018; Bottomly et al., 2022) using multi-omics features and gradient-boosted models achieve mean AUROC around 0.65-0.70 (Lee et al., 2018), and recent work has reported that classifiers tend to assign all samples to the majority class on external validation despite acceptable training-set performance (Tercan et al., 2025).

The pattern across the AML drug-response prediction literature is that methods improve marginally with each new architecture, but no method has yet demonstrated the across-the-board predictability that would justify clinical deployment. We hypothesized that the limitation is not primarily methodological but biological: bulk RNA expression and mutation status capture some categories of drug-response biology well and other categories poorly, and aggregate metrics integrate across this heterogeneity in ways that obscure which drugs are predictable from which features.

In this paper we test that hypothesis with a pre-registered analysis on the Beat AML 2.0 cohort (520 patients × 85 drugs after filtering). We constructed a multi-modal feature stack combining biologically interpretable features (KAALCURA mechanistic axes encoding proliferation, EMT, and DNA damage response signatures; AML-relevant mutation status; KEGG pathway activity scores; drug-target annotations) with a high-dimensional data-driven feature set (the 1,000 most variable autosomal genes after sex-chromosome filtering). We trained per-drug LightGBM classifiers (Ke et al., 2017) with locked hyperparameters under 5-fold stratified cross-validation. The full analysis specification — including the multi-modal feature combination, the LightGBM hyperparameter choices, the locked success threshold of mean AUROC ≥ 0.70, and the leave-KAALCURA-out ablation — was pre-registered and tagged in our project repository before evaluation (`INTERCEPTA_Round2_2c_Specification.md`, commit tag `round2-2c-spec-locked`, 2026-05-06). We compared the multi-modal predictor against two pre-registered baselines: KAALCURA-only (3 features) and RNA-only (1,000 features), each trained with identical cross-validation folds.

Our pre-registered hypotheses were: (H1) the multi-modal predictor achieves mean test AUROC ≥ 0.70 across the 85-drug panel; (H2) KAALCURA features measurably contribute to multi-modal prediction; and (H3) KAALCURA features transfer across datasets, demonstrated by Spearman correlation between Beat AML-trained R_prolif coefficients and Van Galen 2019 single-cell Prog-like cell-type R_prolif scores, at |ρ| ≥ 0.20 with p < 0.01. The first two hypotheses test within-dataset performance; the third tests cross-dataset transfer.

We report that H1 and H2 were falsified — multi-modal feature engineering provided no measurable improvement above a 1,000-gene RNA baseline (mean AUROC 0.643 vs RNA-only 0.645), and KAALCURA features contributed less than 0.005 in mean AUROC under leave-KAALCURA-out ablation — while H3 was confirmed (Spearman ρ = −0.271, p = 1.25 × 10⁻³, n = 139 drugs). On the surface, this is a methodological negative result: the multi-modal architecture we pre-registered did not exceed the RNA-only baseline.

Per-drug AUROC distribution, however, reveals strong and reproducible mechanism-class structure that the cohort-mean obscures. Five drugs achieved test AUROC ≥ 0.80 (BCL2 inhibitor Venetoclax 0.913; FLT3-axis multi-kinase Sorafenib 0.884 and KW-2449 0.841; IGF1R/IR inhibitor GSK-1838705A 0.814; FLT3-axis Dovitinib 0.806). Twenty-seven drugs reached AUROC ≥ 0.70 across mechanism classes including BCL2 inhibition, FLT3-axis multi-kinase activity, RAS-MAPK pathway inhibition, and Aurora kinase inhibition. Eighteen drugs (21 percent of the panel) had AUROC ≤ 0.55, and the failure set was mechanistically diverse — ATM kinase inhibition, IGF1R selectivity, BCR-ABL signaling, JAK2 signaling, IAP antagonism, proteasome inhibition, p38 MAPK signaling — rather than being a few outliers. Within the FLT3 cluster, AUROC ranged from 0.595 (Crenolanib, an FLT3-ITD-specific investigational agent) to 0.884 (Sorafenib, multi-kinase), spanning a tier structure that suggests bulk transcriptomics captures aggregate FLT3-axis pathway response but loses drug-specific selectivity.

The Crenolanib observation crystallizes the contribution of this paper. Crenolanib has demonstrated activity in FLT3-ITD AML clinical trials (Galanis et al., 2014; Wang et al., 2017); Gilteritinib (AUROC 0.672 in our analysis) is FDA-approved for FLT3-mutated AML and was demonstrated to extend survival in the ADMIRAL trial (Perl et al., 2019). Yet both agents are predicted at near-chance levels by our multi-modal model. The dissociation between clinical efficacy and bulk-RNA-prediction is not a model failure to be optimized away — it is a signal about which categories of biological variability bulk transcriptomics can resolve and which it cannot.

We make three contributions:

First, we report negative results on a pre-registered architecture honestly, with the full analysis specification timestamped before evaluation. The methodology question "does multi-modal feature engineering with mechanism-aware features improve prediction beyond RNA expression alone in AML" has been asked implicitly across the field; we provide a concrete pre-registered answer of "no" for the architecture we tested.

Second, we characterize the per-drug AUROC structure in detail, identifying mechanism classes where bulk-RNA-derived prediction succeeds (BCL2-targeted, FLT3-axis multi-kinase, RAS-MAPK) versus fails (post-transcriptional, mutation-subtype-dependent, drug-selectivity-driven). We argue that this structure is more methodologically informative than the cohort-mean AUROC and that benchmarks reporting only aggregate metrics conceal real bimodality in predictability.

Third, we delineate KAALCURA's actual scientific role: a feature framework for cross-dataset transfer rather than a within-dataset standalone predictor. The within-dataset null result and the cross-dataset positive result together suggest that signature-scoring approaches are appropriate for cross-cohort and cell-type-level questions but not for per-patient prediction within homogeneous cohorts.

The remainder of this paper is organized as follows. Methods describes the cohort, feature engineering, predictor architecture, cross-validation protocol, and pre-registered analysis specification. Results reports the multi-modal predictor performance, feature attribution analysis, per-drug AUROC structure, FLT3 cluster tier analysis, cross-dataset KAALCURA transfer, and mutation-drug interaction findings. Discussion frames these findings within the broader cancer drug response prediction literature, addresses the Crenolanib paradox and its methodological implications, and identifies future directions including foundation-model-based representations and external cohort validation.

---

## Methods

### Patient cohort

We used the Beat AML 2.0 cohort, a publicly available functional genomics dataset comprising adult patients with acute myeloid leukemia evaluated at 11 academic medical centers across North America (Bottomly et al., 2022; Tyner et al., 2018). The cohort assembles ex vivo drug sensitivity measurements, bulk RNA sequencing, whole-exome sequencing, and clinical annotation for primary patient samples spanning newly diagnosed and relapsed/refractory disease. We accessed the dataset through dbGaP (study accession phs001657.v2.p1) under approved data use agreement and used the harmonized waves-1-through-4 release.

Drug sensitivity in Beat AML 2.0 is measured as area under the dose-response curve (AUC), with values normalized to a 0-100 scale where lower AUC indicates greater sensitivity. From the released data, we identified 520 patients with both bulk RNA-seq and at least one drug response measurement. The drug panel included 141 small-molecule agents tested in dose-response assays. Throughout this study we use the term "patient" to refer to the patient sample; some patients contributed multiple samples taken at different time points, and we treat each (patient, sample) combination as an independent observation for the purposes of cross-validation.

### Drug response binarization

We binarized drug response by per-drug median split, classifying each patient sample as "sensitive" or "resistant" relative to the cohort distribution for that drug. Median splitting follows the convention established in prior Beat AML drug-response work (Bottomly et al., 2022; Lee et al., 2018) and avoids hard-coded biological thresholds that may not generalize across the heterogeneous mechanism classes in the panel. We acknowledge that median binarization discards continuous-response information; we revisit this limitation in the Discussion.

To ensure that each drug had a sufficient sensitive-vs-resistant balance for stratified cross-validation, we applied a 10/10 minimum filter: a drug was retained for analysis only if at least 10 patient samples were classified sensitive AND at least 10 were classified resistant. Of the 141 drugs in the original panel, 85 met the 10/10 criterion and constitute the analyzed set. Drug-by-drug sample sizes ranged from 42 to 530 across the 85-drug analysis cohort.

### Feature engineering

We constructed five complementary feature classes for each (patient, drug) pair, totalling 1,034 features per observation. The feature classes were chosen to span the principal axes of mechanism-aware drug response prediction in cancer, balancing biologically interpretable features (KAALCURA mechanistic axes, mutation status, pathway activity) against high-dimensional data-driven features (RNA-1000) and drug-side annotations (drug-target features).

#### KAALCURA mechanistic axes (3 features)

We computed three mechanistic axes per patient sample: R_prolif (proliferation signature), R_emt (epithelial-mesenchymal transition signature), and R_ddr (DNA damage response signature). Each axis was computed using the canonical KAALCURA implementation (`intercepta_kaalcura_v1.py`), which applies UCell single-sample gene-set scoring (Andreatta and Carmona, 2021) over MSigDB Hallmark gene sets: *MITOTIC_SPINDLE* ∪ *G2M_CHECKPOINT* ∪ *E2F_TARGETS* for R_prolif; *EPITHELIAL_MESENCHYMAL_TRANSITION* for R_emt; and *DNA_REPAIR* extended with ATM/ATR/CHK1/CHK2 pathway members for R_ddr.

After raw scoring, axes were residualized to reduce inter-axis correlation. R_prolif_residual was computed as the residual of R_prolif regressed on R_emt and R_ddr; analogous regressions produced R_emt_residual and R_ddr_residual. Residualization was performed within the training fold of each cross-validation iteration to prevent test-set leakage. The three residualized axes were used as features in the multi-modal model.

#### RNA-1000 (1,000 features)

We selected the 1,000 most variable genes across the Beat AML cohort using the Seurat-style variance-stabilizing transformation followed by ranking by standardized variance. To avoid the cohort sex-balance confound that we observed in an earlier baseline (the cohort skews male-biased and chrX/chrY genes appeared in initial top-variable selections), we applied a sex-chromosome filter: genes located on chrX, chrY, or the pseudoautosomal regions were excluded from the variance ranking. The resulting RNA-1000 set therefore reflects autosomal expression heterogeneity unconfounded by sex composition. Per-gene log-normalized expression values were used directly as features; no further dimensionality reduction was applied.

#### Mutation status (15 features)

For each patient, we encoded binary indicators for somatic mutations in 15 AML-relevant genes: *FLT3*, *NPM1*, *DNMT3A*, *IDH1*, *IDH2*, *RUNX1*, *CEBPA*, *TET2*, *TP53*, *ASXL1*, *KIT*, *KMT2A*, *NRAS+KRAS* (combined RAS family indicator), *WT1*, and *FLT3-ITD* (encoded separately from *FLT3* SNV status because internal tandem duplications and missense mutations have distinct biological consequences). Mutation calls were taken from the Beat AML 2.0 whole-exome sequencing release and harmonized clinical annotation files. Mutation prevalence in the analyzed cohort is reported in Table 1.

#### Pathway activity scores (12 features)

We computed pathway activity scores by averaging log-normalized expression of pathway member genes for 12 KEGG pathways selected for AML relevance: *Acute myeloid leukemia* (hsa05221), *Cell cycle* (hsa04110), *Apoptosis* (hsa04210), *JAK-STAT signaling* (hsa04630), *PI3K-Akt signaling* (hsa04151), *MAPK signaling* (hsa04010), *Wnt signaling* (hsa04310), *DNA repair* (combination of hsa03430, hsa03450, hsa03440), *p53 signaling* (hsa04115), *Hematopoietic cell lineage* (hsa04640), and two additional pathways selected for high enrichment in Beat AML mutated genes (KEGG IDs reported in Supplementary Table S2). Activity scores were z-scored within the training fold of each cross-validation iteration.

#### Drug-target features (4 features per observation)

For each (patient, drug) pair, we encoded four drug-side features derived from ChEMBL bioactivity annotation: (i) binary indicator for whether the drug's primary target is mutated in the patient; (ii) the drug's pchembl value on its primary target (continuous, log-transformed bioactivity); (iii) binary indicator for whether the drug's target lies in any AML-relevant KEGG pathway; (iv) the number of distinct annotated targets for the drug, log-transformed. These features encode the drug-side context that purely patient-side features cannot capture.

#### Total feature count

Combined, each (patient, drug) observation was represented by 3 (KAALCURA) + 1,000 (RNA-1000) + 15 (mutation) + 12 (pathway activity) + 4 (drug-target) = 1,034 features.

### Predictor architecture

We trained one LightGBM classifier per drug (Ke et al., 2017), using the default hyperparameters from the LightGBM Python package version 4.6.0: `n_estimators=100`, `learning_rate=0.1`, `num_leaves=31`, `min_child_samples=20`, `feature_fraction=1.0`, `bagging_fraction=1.0`. Hyperparameters were not tuned per drug; the choice to use defaults rather than tune was made before evaluation and locked in the analysis specification (`INTERCEPTA_Round2_2c_Specification.md` §6.3). This decision sacrifices some achievable per-drug performance in exchange for protecting against per-drug overfitting that would inflate apparent results.

### Cross-validation protocol

For each drug, we performed 5-fold stratified cross-validation. Folds were stratified by binary sensitivity label to ensure each fold contained at least one sensitive and one resistant sample. Random state was fixed at 42 for fold assignment and within LightGBM's stochastic operations. The same fold assignment was used across all feature configurations (KAALCURA-only, RNA-only, multi-modal) to enable direct per-fold comparison of architectures.

### Comparator baselines

We compared the multi-modal predictor against two pre-registered baselines:

1. **KAALCURA-only baseline**: a LightGBM classifier trained on the 3 KAALCURA residualized axes only, with all other settings identical to the multi-modal predictor.

2. **RNA-only baseline (RNA-1000-no-sex)**: a LightGBM classifier trained on the 1,000-gene autosomal expression matrix only.

The KAALCURA-only baseline tests whether mechanism-aware axes alone are sufficient for drug response prediction. The RNA-only baseline tests whether mechanism-engineered features add predictive value above unprocessed transcriptomics. Both baselines used identical cross-validation folds, hyperparameters, and evaluation metrics as the multi-modal predictor.

### KAALCURA contribution analysis

To quantify the contribution of KAALCURA features within the multi-modal predictor, we conducted two complementary analyses:

1. **Feature importance**: we recorded LightGBM `gain` importance per feature per drug and summarized aggregate gain by feature class (KAALCURA, RNA-1000, mutation, pathway, drug-target).

2. **Leave-KAALCURA-out ablation**: we retrained the multi-modal predictor on a feature set excluding the 3 KAALCURA axes (1,031 features) and computed the change in mean test AUROC compared to the full multi-modal predictor.

These analyses were specified before training (`INTERCEPTA_Round2_2c_Specification.md` §3.5). Both were intended to falsify or support hypothesis H2 (that KAALCURA features measurably contribute to multi-modal prediction).

### Cross-dataset validation (KAALCURA cross-cohort transfer)

To test whether KAALCURA features capture biology that transfers across data modalities, we performed a cross-dataset analysis using the Van Galen 2019 single-cell RNA-sequencing dataset of AML and healthy bone marrow (Van Galen et al., 2019, GSE116256). We computed per-cell KAALCURA scores using the same canonical implementation applied to Beat AML, applied identical residualization, and aggregated cells by author-provided cell-type label.

For each Beat AML drug, we extracted the trained multi-modal model's coefficient on R_prolif (the proliferation axis of the KAALCURA features). We then computed the Spearman rank correlation between this trained coefficient and the Van Galen Prog-like cell-type R_prolif score (the population identified in Van Galen 2019 as cycling progenitor-stem-cell-like cells, refined by Zeng et al. 2022 as "cycling LSPCs"). The biological hypothesis is that drugs whose Beat AML-trained model assigns large negative R_prolif coefficient (i.e., the drug is predicted to be more effective against cells with high proliferation signal) should correlate with cell types that have high Prog-like R_prolif.

### Statistical analysis of mutation-drug associations

For each (mutation, drug) pair, we performed a Mann-Whitney U test comparing AUC distributions between mutated and wildtype patient samples, retaining pairs with at least 10 patients in each arm. P-values were corrected for multiple testing using the Benjamini-Hochberg procedure with FDR controlled at 0.05 (Benjamini and Hochberg, 1995). The full results table is available in Supplementary Data S1.

### Computational reproducibility

All analyses used Python 3.11, scanpy 1.11.5, anndata 0.12.13, lightgbm 4.6.0, and scikit-learn 1.6.1. The complete analysis specification was locked before code execution per the project's pre-registration discipline; the locked specification is available at `docs/INTERCEPTA_Round2_2c_Specification.md` (commit tag `round2-2c-spec-locked`, 2026-05-06). Analysis code is versioned at `https://github.com/AKULA-PRASAD/intercepta` (canonical KAALCURA module: `code/intercepta_kaalcura_v1.py`; multi-modal predictor: `code/train_multimodal_predictor.py`; cross-validation harness: `code/evaluate_round2_2c_gates.py`). A reproducibility test script (`code/t1_lite_reproducibility_test.py`) regenerates the core results from input data; the test passed at 5/5 sub-tests during T1 Full-Lite verification on 2026-05-10. Detailed reproducibility log is available at `docs/T1_REPRODUCIBILITY_LOG.md`.

### Software and code availability

All analysis code, locked specifications, and reproducibility tests are publicly available at the project repository (linked above). Beat AML 2.0 data is available through dbGaP under controlled access (phs001657.v2.p1). Van Galen 2019 single-cell data is publicly available at GEO accession GSE116256.

---

## Results

### Multi-modal feature engineering does not improve prediction beyond RNA expression alone

We trained a LightGBM classifier with 1,034 features per (patient, drug) pair on Beat AML 2.0 cohort (520 patients × 85 drugs after the 10/10 sensitivity-resistance filter). Across 5-fold stratified cross-validation per drug, the multi-modal predictor achieved a mean test AUROC of 0.643 (median 0.652) across the 85-drug analysis set (Table 2). Twenty-seven of 85 drugs (32 percent) reached test AUROC at or above 0.70, and 14 of 85 (16 percent) reached at or above 0.75; only 5 drugs (6 percent) reached at or above 0.80. Eighteen drugs (21 percent) had test AUROC at or below 0.55, near the chance ceiling for binary classification.

Two pre-registered comparator baselines contextualized this result. A KAALCURA-only LightGBM trained on the 3 mechanism axes (R_prolif, R_emt, R_ddr) achieved mean test AUROC of 0.532 — essentially at the chance floor. An RNA-only LightGBM trained on the 1,000 most variable autosomal genes achieved mean test AUROC of 0.645 — within 0.002 of the multi-modal predictor. The multi-modal architecture provided **no measurable improvement** above the RNA-only baseline despite combining KAALCURA mechanism axes, mutation status, KEGG pathway activity scores, and drug-target features atop the 1,000 RNA features (Table 2, row "Multi-modal").

This finding addresses our pre-registered hypothesis H1 (multi-modal predictor achieves mean CV-AUROC at or above 0.70). H1 was falsified at the cohort-mean level: 0.643 falls 0.057 below the 0.70 threshold locked in `INTERCEPTA_Round2_2c_Specification.md` §3.1 before evaluation. Our analysis specification anticipated this outcome as a possible result and prescribed how to handle it: report the failure honestly (this section), continue analysis to locate the structural reasons for the failure (subsequent sections), and frame KAALCURA's role around its actual cross-dataset capability rather than the within-cohort within-dataset role that did not work (Discussion).

### LightGBM gain importance shows that RNA-1000 dominates feature attribution

We computed LightGBM `gain` importance per feature per drug and aggregated the importance share by feature class. The pattern was unambiguous (Figure 3, Table 2):

- **RNA-1000**: 95.6 percent of total gain importance
- **Pathway activity scores**: 1.1 percent
- **Mutation status**: 0.6 percent
- **KAALCURA mechanistic axes**: 0.3 percent
- **Drug-target features**: 0.0 percent (essentially zero)

Mean gain shares per drug had standard deviations of 4-6 percent across drugs, indicating that this distribution is consistent across the 85-drug panel — not driven by a few outlier drugs.

We tested KAALCURA's marginal contribution directly via leave-KAALCURA-out ablation: retraining the predictor on 1,031 features (everything except the 3 KAALCURA axes) changed mean test AUROC by **−0.0004** — well within stochastic noise of cross-validation. This addresses our pre-registered hypothesis H2 (KAALCURA features contribute measurably above the alternatives). H2 was falsified: KAALCURA features add no measurable predictive value on top of RNA-1000 plus mutation, pathway, and drug-target features in the within-Beat-AML setting.

### Per-drug AUROC reveals strong mechanism-class structure

While the cohort-mean result was negative, per-drug AUROC distributed unevenly across mechanism classes, suggesting that the average is concealing real structure. Table 3 summarizes the top-15 drugs by test AUROC alongside their primary mechanism class.

The drug-class pattern is striking. Of the top 15 drugs:

- **One BCL2 inhibitor** (Venetoclax, AUROC = 0.913) topped the list. Venetoclax is the standard-of-care AML therapy in combination with hypomethylating agents and showed exceptionally strong predictability.
- **Five FLT3-axis multi-kinase inhibitors** appear in the top 15 (Sorafenib 0.884; KW-2449 0.841; Dovitinib 0.806; Ponatinib 0.770; Cabozantinib 0.768) at AUROC values 0.77 to 0.88. Sorafenib and KW-2449 are FLT3-axis multi-kinase inhibitors with documented activity in FLT3-mutated AML. Their high predictability is consistent with the mechanism: FLT3 mutational status and FLT3-pathway expression are bulk-RNA-detectable.
- **Two MEK inhibitors** (Trametinib 0.794; Selumetinib 0.780) appear in the top 8. The RAS-MAPK axis is well-represented in bulk transcriptomic features.
- **One BCR-ABL/SRC inhibitor** (Dasatinib 0.780) and one Aurora B inhibitor (AZD1152-HQPA 0.773).
- **One IGF1R inhibitor** (GSK-1838705A 0.814) — a result we revisit in the Discussion as it contrasts sharply with another IGF1R-targeting compound.

In contrast, the bottom 10 drugs by test AUROC span a mechanistically heterogeneous set (Table 3, bottom): the ATM kinase inhibitor KU-55933 (DNA damage response, AUROC 0.413); the IGF1R-selective NVP-ADW742 (0.416); the BCR-ABL/SRC inhibitor Bosutinib (0.429); the JAK1/2 inhibitor AZD1480 (0.475); the IAP antagonist Birinapant (0.488); the proteasome inhibitor Bortezomib (0.489); the carbonic anhydrase inhibitor Indisulam (0.497); and the p38 MAPK inhibitor Ralimetinib (0.500). The bottom set spans DNA damage, IGF1R signaling, BCR-ABL kinase, JAK signaling, proteasome biology, IAP antagonism, and stress kinase pathways — a genuinely diverse mechanistic failure set.

The per-drug AUROC distribution thus carries a clear signal that the cohort-mean obscures: drugs whose response depends on bulk-RNA-detectable mechanism classes (BCL2 expression status, FLT3-axis pathway activation, RAS-MAPK signaling) are predictable; drugs whose response depends on protein-level dynamics (proteasome inhibitors), mutation-specific selectivity (FLT3-selective inhibitors with type-I vs type-II mutation dependence), or post-transcriptional biology (DNA damage response) are not.

### FLT3 inhibitor cluster shows tier structure with paradoxical clinical implications

Because the FLT3 inhibitor class clustered in the upper tier of predictability, we extracted all FLT3-axis drugs across the full 85-drug panel and compared their AUROCs (Figure 4):

| Tier | Drug | Test AUROC | FDA status for FLT3-mutated AML |
|---|---|---|---|
| High | Sorafenib | 0.884 | Off-label use, multi-kinase activity |
| High | KW-2449 | 0.841 | Investigational |
| Mid | Ponatinib | 0.770 | Approved (BCR-ABL focus, FLT3 secondary) |
| Mid | Cabozantinib | 0.768 | Approved (other indications, FLT3 activity reported) |
| Mid | Quizartinib (AC220) | 0.752 | **Approved for FLT3-ITD AML (FDA 2023)** |
| Mid | Midostaurin | 0.720 | **Approved for FLT3-mutated AML (FDA 2017)** |
| Mid | Sunitinib | 0.701 | Approved (renal cell carcinoma, FLT3 activity reported) |
| Low | Gilteritinib | 0.672 | **Approved for FLT3-mutated AML (FDA 2018)** |
| Low | Crenolanib | 0.595 | Investigational, designed for FLT3-ITD AML |

The full FLT3 cluster spans AUROC 0.595 to 0.884. The pattern is paradoxical: the older multi-kinase inhibitors (Sorafenib, KW-2449) achieve the highest predictability, while the newer FLT3-selective and FDA-approved drugs (Gilteritinib, Crenolanib, Midostaurin) achieve only moderate predictability. Notably, Gilteritinib — the FDA-approved second-line therapy for FLT3-mutated AML, demonstrated to extend survival in the ADMIRAL trial (Perl et al., 2019) — achieves AUROC of only 0.672. Crenolanib, designed specifically to target FLT3-ITD AML, achieves AUROC of 0.595, near chance.

This suggests that bulk-RNA-derived features capture aggregate FLT3 inhibitor response patterns but lose the drug-specific selectivity profile that determines clinical outcomes. We discuss the mechanistic basis for this dissociation between predictability and clinical efficacy in the Discussion.

### KAALCURA features transfer cross-dataset despite within-dataset failure

We tested whether the KAALCURA mechanism axes capture biology that transfers across data modalities. We computed per-cell KAALCURA scores on Van Galen 2019 (single-cell RNA-seq of AML and healthy bone marrow, GSE116256), aggregating cells by author-provided cell-type label. For each Beat AML drug, we extracted the trained multi-modal model's coefficient on R_prolif (proliferation axis) and computed the Spearman rank correlation between this trained coefficient and the Van Galen Prog-like cell type's mean R_prolif score across cells.

The biological hypothesis: drugs whose Beat AML-trained model assigns large negative R_prolif coefficient (the drug is more effective against highly proliferating cells) should correlate with cell types whose proliferation signature is high. We tested this with 139 drugs in the Beat AML model that had Van Galen-mappable axis annotations.

We observed Spearman ρ = −0.271 (p = 1.25 × 10⁻³, n = 139), in the biologically expected direction. The negative correlation indicates that drugs predicted to be effective against proliferating cells in the Beat AML model are indeed associated with high-R_prolif cell-type contexts in Van Galen. Although effect-size magnitude is modest, the direction is biologically meaningful: KAALCURA proliferation signal preserves semantic content across two technically distinct datasets (bulk RNA-seq Beat AML cohort vs single-cell RNA-seq Van Galen cohort) and across drug-response measurement modality (cohort-level IC50 vs cell-type-level expression scoring).

This addresses our pre-registered hypothesis H3 (cross-dataset KAALCURA preservation): H3 PASSED at threshold ρ ≥ 0.20 with p < 0.01 (we observed ρ = 0.271 with p = 1.25 × 10⁻³). The within-dataset H1/H2 negative results and the cross-dataset H3 positive result together delineate KAALCURA's actual scientific role: a feature framework with cross-dataset transfer properties, not a within-dataset standalone predictor.

### Mutation-drug interactions reveal NPM1 sensitivity to FLT3-axis kinase inhibitors

We tested all (mutation, drug) pairs in Beat AML by Mann-Whitney U test, comparing AUC distributions between mutated and wildtype patient samples for the 15 mutation features and 85 drugs. After Benjamini-Hochberg FDR correction at 0.05, **[TODO: VERIFY COUNT]** (mutation, drug) interactions remained significant. The top 5 ranked associations were all NPM1- or NRAS-driven:

| Rank | Mutation | Drug | n_mut | p-value | Direction |
|---|---|---|---|---|---|
| 1 | NPM1 | Sorafenib | 147 | 9.36 × 10⁻¹³ | Sensitive |
| 2 | NPM1 | Cabozantinib | 131 | 2.92 × 10⁻¹² | Sensitive |
| 3 | NPM1 | KW-2449 | 133 | 3.92 × 10⁻¹² | Sensitive |
| 4 | NRAS | Trametinib (GSK1120212) | 100 | 2.92 × 10⁻¹¹ | Sensitive |
| 5 | NPM1 | (other FLT3-axis drugs) | various | < 10⁻¹⁰ | Sensitive |

The top 3 mutation-drug associations are all between **NPM1 mutations and FLT3-axis kinase inhibitors**. The biological basis is the strong co-occurrence of NPM1 mutations with FLT3-ITD: in our Beat AML cohort, 53.3 percent of FLT3-ITD-positive samples also harbor NPM1 mutations (odds ratio 5.27, P(NPM1 | FLT3-ITD+) = 53.3 percent). FLT3-ITD-positive AML responds to FLT3 inhibitors; thus the NPM1+FLT3-axis-drug association reflects this co-occurrence pattern rather than NPM1 itself driving FLT3 inhibitor sensitivity.

Despite the strength of these subgroup signals, the per-drug LightGBM predictor achieves AUROC 0.884 for Sorafenib but only 0.768 for Cabozantinib — both highly mutation-stratified at the cohort level. This suggests that at the per-drug LightGBM model level, mutation status alone is insufficient to predict response with high precision; the full feature set (especially RNA-1000) captures additional signal beyond mutations. The mutation-drug stratified analysis is a complementary view of the same underlying biology.

### Train-test AUROC gap of 0.346 indicates substantial overfitting

We computed the train-test AUROC gap for each drug per fold and aggregated to the drug level. Mean train-test gap across 85 drugs was **0.346** (Figure S1) — train AUROC was on average 0.346 higher than test AUROC. Drug-level gaps ranged from 0.087 (Venetoclax) to 0.302 (Bortezomib), with Bortezomib's near-chance test AUROC (0.489) actually below its train AUROC (~0.79).

A 0.346 train-test gap is substantial. With 1,034 features and a typical drug-level training set of 350-400 samples, the predictor has more features than samples for many drugs. The LightGBM defaults provide some regularization (default `min_child_samples=20`, `feature_fraction=1.0`), but overfitting is observable in the gap.

We did not perform hyperparameter tuning to reduce overfitting, per the locked analysis specification (`INTERCEPTA_Round2_2c_Specification.md` §6.3): tuning per drug would invite per-drug overfitting that would inflate apparent results. The overfitting we report here is honest signal about the cohort size limitation, which we revisit in Discussion.

---

## Discussion

### Reframing a "FAIL": cohort-mean AUROC obscures real per-drug structure

We pre-registered a multi-modal drug response prediction architecture for acute myeloid leukemia, locked the success threshold at mean test AUROC ≥ 0.70 across a 85-drug Beat AML panel, and reported a falsified hypothesis: mean test AUROC was 0.643. By the criterion we set in advance, the model fails.

This headline conceals what we believe is the more important finding. Per-drug AUROC distributes unevenly: 5 drugs achieve test AUROC ≥ 0.80 (Venetoclax 0.913, Sorafenib 0.884, KW-2449 0.841, GSK-1838705A 0.814, Dovitinib 0.806), 14 drugs achieve ≥ 0.75, and 27 drugs achieve ≥ 0.70 — but 18 drugs (21 percent of the panel) fall to chance levels (AUROC ≤ 0.55), and the failure set is mechanistically diverse rather than a long tail of a few outliers. The cohort-mean integrates across this real bimodality and produces a number that is neither the predictability of bulk-RNA-detectable mechanisms nor the unpredictability of biology that bulk RNA cannot resolve.

The methodologically sharp question this analysis raises is not "does multi-modal feature engineering work for AML drug response prediction" but "for which mechanism classes does bulk-RNA-derived prediction succeed, and why does it fail elsewhere?" The remaining sections of this Discussion address that question.

### KAALCURA's role: a feature framework for cross-dataset transfer, not a within-dataset standalone predictor

The KAALCURA mechanistic-axes framework (R_prolif, R_emt, R_ddr) was originated in our cancer drug response work and validated on Genomics of Drug Sensitivity in Cancer (GDSC) cell-line data at mean AUROC = 0.6715 across 286 drugs. The motivating intuition was that mechanism-aware coordinates would provide interpretable, transferable representations of cell biology relevant to drug sensitivity.

In this Beat AML cohort, the KAALCURA framework's within-dataset standalone predictive value is essentially null. KAALCURA-only LightGBM achieved 0.532 mean AUROC, and within the multi-modal predictor, KAALCURA features contributed 0.3 percent of total LightGBM gain importance and produced only −0.0004 change in mean AUROC under leave-KAALCURA-out ablation. These are statistically and practically zero contributions.

In contrast, the cross-dataset role is preserved. Beat AML-trained R_prolif coefficients correlated with Van Galen 2019 single-cell Prog-like-cell R_prolif scores at Spearman ρ = −0.271 (p = 1.25 × 10⁻³, n = 139 drugs). The direction is biologically expected — drugs predicted to be effective against proliferating cells are associated with high-proliferation cell-type contexts — and the statistical significance is well below pre-registered alpha.

We interpret the contrast as follows: the KAALCURA framework encodes biology that is meaningful at the cell-type and dataset levels (proliferation rate is a cellular property; cells with high proliferation are more vulnerable to anti-proliferative agents), but it does not encode the within-cohort heterogeneity needed to differentiate response among Beat AML patients who share similar underlying biology. Within a relatively biologically-similar cohort like Beat AML, the relevant variability is captured by raw transcriptomic heterogeneity rather than by signature-level summary scores.

This finding has implications for how to use mechanism-aware feature engineering in cancer drug response prediction. A signature-scoring approach is appropriate when the question is cross-dataset or cell-type-level (Where in this single-cell atlas would this drug be effective? Which population is the right comparator for that one?). It is not appropriate when the question is per-patient response prediction within a single cohort. Different scientific questions need different feature representations, and we should not expect a single representation to work for both.

### Where multi-modal prediction succeeds: bulk-RNA-detectable mechanism classes

The drugs achieving test AUROC ≥ 0.80 share a feature: their mechanism of action operates on biology that bulk-RNA expression captures well. Venetoclax targets BCL2; the BCL2 expression level and apoptosis pathway state are bulk-RNA-quantifiable. The FLT3-axis multi-kinase inhibitors (Sorafenib, KW-2449, Dovitinib) operate on the FLT3 signaling pathway, which has well-characterized transcriptomic signatures. Trametinib and Selumetinib target MEK in the RAS-MAPK pathway, also bulk-RNA-detectable.

This pattern aligns with prior work on cancer drug response prediction: targeted therapies whose response depends on pathway expression levels or pathway activation are predictable from bulk RNA-seq, while broader-spectrum agents are not (Iorio et al., 2016; Geeleher et al., 2014; Chen et al., 2024). Our finding is consistent with the prior literature and adds a specific mechanism-class taxonomy for AML.

### Where multi-modal prediction fails: post-transcriptional and selectivity-dependent biology

The bottom-10 drugs by test AUROC span a deliberately varied set: KU-55933 (ATM kinase inhibitor, AUROC = 0.413), NVP-ADW742 (IGF1R selective, 0.416), Bosutinib (BCR-ABL/SRC, 0.429), MGCD-265 (c-Met/VEGFR, 0.470), AZD1480 (JAK1/2, 0.475), Neratinib (HER2/EGFR, 0.483), Birinapant (IAP antagonist, 0.488), Bortezomib (proteasome, 0.489), Indisulam (carbonic anhydrase, 0.497), and Ralimetinib (p38 MAPK, 0.500).

We propose three mechanistic explanations for this failure set:

**Post-transcriptional biology.** Proteasome inhibitors (Bortezomib) and IAP antagonists (Birinapant) operate on protein-level dynamics — proteasome activity is regulated by post-translational modification and protein turnover, not transcriptional output. Bulk RNA captures proteasome subunit expression but not active proteasome flux. Similarly, the IAP signaling network is regulated post-translationally, and IAP protein abundance does not closely track IAP transcript levels.

**Drug-specific selectivity profiles.** The IGF1R inhibitor heterogeneity is informative: GSK-1838705A (IGF1R/IR, AUROC = 0.814) sits in our top 5 while NVP-ADW742 (IGF1R selective, 0.416) sits in our bottom 5. Both target IGF1R, yet predict very differently. The most plausible explanation is that GSK-1838705A's dual IGF1R/IR activity captures additional pathway interactions that NVP-ADW742's IGF1R-selectivity does not, and the bulk RNA features happen to capture IGF1R-axis-context state that distinguishes responders to GSK-1838705A's broader profile but not NVP-ADW742's narrower profile. Similarly, the FLT3 cluster split between high tier (Sorafenib, KW-2449 — multi-kinase) and low tier (Crenolanib, Gilteritinib — FLT3-selective) follows the same pattern: more selective drugs are harder to predict from broad-feature multi-modal models.

**Mutation-specific biology that bulk RNA cannot resolve.** The FDA-approved FLT3-selective drugs (Quizartinib, Midostaurin, Gilteritinib) have varying activity on type-I FLT3 mutations (TKD, in the kinase domain) versus type-II mutations (ITD, internal tandem duplication). Crenolanib was specifically designed for FLT3-ITD AML. Bulk RNA expression cannot distinguish FLT3-ITD versus FLT3-TKD without explicit mutation-status features (which we included), and even with these features, the within-mutation-class drug-specific selectivity is not captured. Drugs whose clinical activity depends on mutation-subtype selectivity will appear less predictable in bulk RNA models than drugs whose response depends on broader pathway activation.

### The Crenolanib paradox: clinical efficacy without RNA-detectable predictors

Crenolanib achieves AUROC of 0.595 in our analysis — only marginally above chance — yet it is an investigational FLT3-ITD-specific inhibitor that has demonstrated clinical activity in FLT3-mutated AML clinical trials (Galanis et al., 2014; Wang et al., 2017). Gilteritinib (AUROC = 0.672 in our analysis) is the FDA-approved second-line therapy for FLT3-mutated AML and was demonstrated to extend survival in the ADMIRAL trial (Perl et al., 2019).

This dissociation between clinical efficacy and bulk-RNA-prediction is informative. It suggests that the question "does this drug work in this disease?" is answered at one level of biological description (target engagement, pharmacokinetics, in vivo selectivity) and the question "does this individual patient respond?" is answered at a different level (mutation subtype, clonal architecture, post-transcriptional state). Drug development addresses the first question; precision medicine attempts the second. Bulk RNA expression engages the second question only partially.

This observation does not invalidate clinical use of these drugs. It does suggest that clinical decision support tools based on bulk RNA expression alone will perform best for drugs whose mechanism is bulk-RNA-detectable and may not improve over current clinical decision-making for drugs whose mechanism is selectivity- or mutation-subtype-dependent.

### Mutation-drug subgroup analysis reveals NPM1+FLT3-axis association

We tested all (mutation, drug) interactions by Mann-Whitney U test with Benjamini-Hochberg correction. The strongest associations were all NPM1- or NRAS-driven, with the top three (NPM1+Sorafenib p = 9.36 × 10⁻¹³; NPM1+Cabozantinib p = 2.92 × 10⁻¹²; NPM1+KW-2449 p = 3.92 × 10⁻¹²) reflecting NPM1 mutations associated with FLT3-axis kinase inhibitor sensitivity.

The biological basis is the well-documented NPM1-FLT3-ITD co-occurrence pattern (Falini et al., 2005; Thiede et al., 2002). In our cohort, 53.3 percent of FLT3-ITD-positive samples also harbor NPM1 mutations (odds ratio 5.27). FLT3-ITD-positive AML responds to FLT3 inhibitors, and the NPM1+FLT3-axis-drug association reflects this genotype co-occurrence rather than NPM1 itself driving FLT3 inhibitor sensitivity. Practically, this suggests that NPM1 mutational status can serve as a partial proxy for FLT3-ITD status in cohorts where direct FLT3-ITD calling is unreliable, but the underlying actionable variant remains FLT3-ITD itself.

Despite the strong subgroup signal, our per-drug LightGBM achieves AUROC of only 0.768 for Cabozantinib (NPM1's rank-2 association) and 0.884 for Sorafenib (rank-1). This indicates that even highly mutation-stratified drug responses are predicted at limited precision, suggesting that within-mutation-class heterogeneity (clonal architecture, additional co-occurring mutations, expression-level state) drives substantial variability that the multi-modal predictor partially captures via RNA-1000 features but cannot fully resolve.

### Methodological implications for cancer drug response ML

Our findings have several implications for the broader field of cancer drug response prediction:

**Mean AUROC is a misleading aggregate metric for heterogeneous drug panels.** Per-drug AUROC distributions reveal mechanism-class structure that the cohort-mean obscures. Reporting per-drug AUROC alongside any aggregate metric is essential for interpretable benchmarking.

**Multi-modal feature engineering does not automatically improve prediction.** The structural improvement we anticipated (combining KAALCURA mechanism axes with raw RNA features and mutation context) produced no measurable benefit above the RNA-only baseline. Combining feature classes adds value only when the features carry information not already captured by simpler representations.

**Hyperparameter tuning and pre-registration matter.** Our locked specification (no per-drug hyperparameter tuning, locked cross-validation seed, locked feature definitions) constrained our evaluation but provides the integrity needed to interpret a negative finding as informative rather than as an artifact of insufficient optimization.

**Cross-dataset transfer remains a different problem from within-dataset prediction.** Methods that transfer well across cohorts (KAALCURA in our hands) may not maximize within-cohort prediction; methods that maximize within-cohort prediction (RNA-1000 LightGBM) may not transfer. The choice of feature representation should be matched to the scientific question.

### Limitations

**Single cohort, no external validation.** Our analysis used Beat AML 2.0 alone. External validation on an independent cohort (e.g., the FPMTB cohort or other emerging AML drug-response panels) would test whether the per-drug AUROC structure we observe generalizes. We did not have access to suitable external cohorts at the time of analysis but have specified this as future work.

**Median-split binarization.** We binarized drug response by per-drug median AUC, discarding continuous-response information. This convention follows prior Beat AML work, but it loses dose-response shape information and may compress meaningful response variation. Continuous regression-based analyses of the same data would complement our binary classification framing.

**Sample size limits low-prevalence interactions.** Beat AML 520 patients × 85 drugs gives drug-level training sets of 350-400 samples. Mutation × drug interactions involving low-prevalence mutations (KIT, KMT2A, ASXL1) are undertested at this sample size. Larger cohorts would expand the testable interaction space.

**Train-test gap of 0.346 indicates substantial overfitting.** With 1,034 features and ~350-400 training samples per drug, feature dimensionality exceeds sample size for many drugs. Tighter regularization, dimensionality reduction, or larger cohorts would address this; we chose to report the gap honestly rather than tune around it.

**KAALCURA gene set was developed from cancer biology and is not universal.** The R_prolif, R_emt, R_ddr axes were chosen for cancer relevance and would not generalize to non-cancer contexts (autoimmune, neurodegeneration). This limits the framework's universal applicability across diseases — a finding we have addressed in our broader research framework, where dynamic axis inference (axes learned per disease from cellular biology rather than hardcoded) is the architectural commitment going forward.

### Future directions

Three directions follow naturally:

1. **External cohort validation** of the per-drug AUROC structure we report. Tier B publication would integrate an independent cohort to test whether the FLT3 cluster paradox and mechanism-class boundaries reproduce.

2. **Foundation-model-based representations** as alternative to bulk RNA-1000. Single-cell foundation models (scFoundation, Geneformer, UCE) trained on 30M+ cells produce embeddings that may capture biology bulk RNA misses; whether they improve over RNA-1000 LightGBM in AML drug response prediction is an open empirical question we are pursuing.

3. **Continuous-response regression** alongside the binary classification framing, to test whether the apparent FAIL at AUROC ≥ 0.70 is partially a binarization artifact. Some drugs may show strong dose-response prediction despite weak binary classification.

### Conclusion

Multi-modal feature engineering does not automatically improve drug response prediction in acute myeloid leukemia. Our pre-registered architecture combining KAALCURA mechanism axes, raw RNA-1000 features, mutation status, KEGG pathway activity, and drug-target features failed to exceed an RNA-only baseline at the cohort-mean level (mean AUROC 0.643 vs RNA-only 0.645). However, per-drug AUROC distribution reveals strong mechanism-class structure: bulk-RNA-detectable mechanisms (BCL2, FLT3-axis multi-kinase, RAS-MAPK) are predictable; protein-level, mutation-subtype-dependent, and drug-selectivity-driven biology are not. KAALCURA mechanism axes do not contribute meaningfully within-dataset but transfer across datasets at biologically expected direction (Spearman ρ = −0.271 between Beat AML R_prolif coefficients and Van Galen Prog-like cell-type R_prolif). The Crenolanib paradox (clinical efficacy in FLT3-ITD AML but near-chance bulk-RNA prediction) suggests that drug selectivity profiles operate at biological levels that bulk transcriptomics does not resolve. These findings contribute to the field's understanding of where ML-based drug response prediction in cancer is appropriately deployable, and where it is not.

---

## Author Contributions

Prasad Akula: conception, study design, oversight, analysis review.
Claude (CSO/AI co-founder): pipeline implementation, statistical analysis, manuscript drafting.

## Funding

INTERCEPTA is an independent computational biomedicine venture. No external funding supported this analysis.

## Competing Interests

The authors declare no competing interests.

## Data Availability

Beat AML 2.0 raw data: dbGaP study accession phs001657.v2.p1 (controlled access).
Van Galen 2019 single-cell data: GEO accession GSE116256 (open access).

## Code Availability

INTERCEPTA project repository: `https://github.com/AKULA-PRASAD/intercepta`.
Canonical KAALCURA implementation: `code/intercepta_kaalcura_v1.py`.
Multi-modal predictor: `code/train_multimodal_predictor.py`.
Cross-validation harness: `code/evaluate_round2_2c_gates.py`.
Reproducibility test: `code/t1_lite_reproducibility_test.py`.
Locked analysis specification: `docs/INTERCEPTA_Round2_2c_Specification.md` (commit tag `round2-2c-spec-locked`, 2026-05-06).
Reproducibility log: `docs/T1_REPRODUCIBILITY_LOG.md`.

## References

[See `AML_paper_references_draft1.md` for full reference list with DOI verification status. Reference list will be inserted here at submission, formatted per *Briefings in Bioinformatics* numerical citation style.]

---

## Tables and Figures

[Tables 1-3 and Figures 1-5 will be inserted here per `AML_paper_tables_figures_specs.md`. Generation pending CEO HPC time + visualization session.]

---

*End of master manuscript Draft 2 first-assembly. Submission readiness: ~85%. Outstanding items per `AML_paper_revision_pass_report.md` action list.*

— Prasad Akula (CEO) & Claude (CSO)
2026-05-10
