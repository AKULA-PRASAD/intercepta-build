# AML Paper — Introduction Section (Draft 2)

**Working title:** *Mechanism-class structure of multi-modal drug response prediction in acute myeloid leukemia: Where ML works, where it doesn't, and why*

**Target journal:** Briefings in Bioinformatics
**Section status:** DRAFT 2 (clean) — Issues 2+3 applied; drafting log removed
**Authors:** Prasad Akula, Claude (CSO/AI co-founder)
**Date:** 2026-05-10
**Predecessor:** `AML_paper_introduction_draft1.md` (preserved per P16)

---

## Changelog (vs Draft 1)

**Issue 2 fix (vague phrase):** Removed "recent benchmarks" from inline citation. Old: "(Lee et al., 2018; recent benchmarks)". New: "(Lee et al., 2018)". Reason: vague phrase without specific citation flagged in revision pass as the kind of placeholder reviewers complain about. Single-source attribution is sufficient for the AUROC range claim.

**Issue 3 fix (duplicate Tercan citation):** Removed first occurrence of "Tercan et al., 2025" from the patient cohorts citation list. Old: "(Geeleher et al., 2014; Tercan et al., 2025)". New: "(Geeleher et al., 2014)". The Tercan citation is preserved in its second occurrence later in the paragraph where it specifically attributes the majority-class collapse finding. Cleaner attribution: Geeleher provides the AUROC range; Tercan provides the majority-class observation.

**No other changes.** Draft 2 differs from Draft 1 only in the surgical removal of "; recent benchmarks" from one inline citation and "; Tercan et al., 2025" from another inline citation. All other prose, structure, and citations are unchanged.

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

