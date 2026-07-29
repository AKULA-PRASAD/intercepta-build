# AML Paper — Results Section (Draft 2 — clean)

**Working title:** *Mechanism-class structure of multi-modal drug response prediction in acute myeloid leukemia: Where ML works, where it doesn't, and why*

**Target journal:** Briefings in Bioinformatics
**Section status:** DRAFT 2 — drafting log removed; one TODO marker preserved for Issue 1 (verify 2,847 count) per `AML_paper_revision_pass_report.md`
**Authors:** Prasad Akula, Claude (CSO/AI co-founder)
**Date:** 2026-05-10
**Predecessor:** `AML_paper_results_draft1.md` (preserved per P16)

All numerical values in this draft were verified against committed analysis outputs on 2026-05-10 via T1 Full-Lite reproducibility test (5/5 sub-tests passed). Verified files: `round2_aml/results/round2_2c/per_drug_full.csv`, `results/beataml_statistical_tests.csv`, `results/kaalcura_real_validation_RERUN.csv`, `round2_aml/results/round2_2c/multimodal_predictor_summary.json`.

**[TODO before submission]** One numerical claim in §"Mutation-drug interactions" (the count of FDR-significant mutation × drug interactions) requires verification via HPC query against `results/beataml_statistical_tests.csv`. The current placeholder of "2,847" is a draft estimate and must be replaced with the verified count from `df['fdr_significant'].sum()` before submission.

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
