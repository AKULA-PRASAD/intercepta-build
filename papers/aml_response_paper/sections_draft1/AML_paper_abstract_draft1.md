# AML Paper — Abstract (Draft 1)

**Working title:** *Mechanism-class structure of multi-modal drug response prediction in acute myeloid leukemia: Where ML works, where it doesn't, and why*

**Target journal:** Briefings in Bioinformatics
**Section status:** DRAFT 1 — drafted last after Methods/Results/Discussion/Introduction
**Authors:** Prasad Akula, Claude (CSO/AI co-founder)
**Date:** 2026-05-10
**Predecessors:** All other section drafts

---

## Abstract (target 300 words; structured per Briefings in Bioinformatics conventions)

**Background.** Predicting drug response from patient-level molecular features in acute myeloid leukemia (AML) has been pursued through increasingly sophisticated machine learning architectures, but aggregate benchmarks have not consistently demonstrated cohort-wide predictability that would support clinical deployment. Whether the limitation is primarily methodological or biological — whether bulk RNA expression and mutation status capture some categories of drug-response biology well and others poorly — has not been examined with pre-registered methodology.

**Methods.** We constructed a multi-modal LightGBM predictor combining KAALCURA mechanistic axes (proliferation, EMT, DNA damage response signatures), AML-relevant mutation status, KEGG pathway activity scores, drug-target features, and the 1,000 most variable autosomal genes (1,034 features per patient × drug pair). The architecture, success thresholds, and ablation analyses were pre-registered before evaluation. We trained per-drug 5-fold stratified cross-validation on Beat AML 2.0 (520 patients × 85 drugs after a 10/10 sensitivity-resistance filter) and compared against KAALCURA-only and RNA-only baselines.

**Results.** The multi-modal predictor achieved mean test AUROC = 0.643, falsifying the pre-registered ≥ 0.70 threshold. Multi-modal feature engineering provided no measurable improvement above the RNA-only baseline (0.645). KAALCURA features contributed 0.3 percent of LightGBM gain importance and produced −0.0004 mean AUROC change under leave-KAALCURA-out ablation. However, per-drug AUROC distribution revealed strong mechanism-class structure: 5 drugs achieved AUROC ≥ 0.80 (BCL2 inhibitor Venetoclax 0.913, FLT3-axis multi-kinase Sorafenib 0.884) while 18 drugs (21 percent) were near chance, with the failure set spanning post-transcriptional and selectivity-dependent biology. The FLT3 inhibitor cluster spanned AUROC 0.595 (Crenolanib) to 0.884 (Sorafenib), with FDA-approved FLT3-selective drugs (Gilteritinib 0.672, Crenolanib 0.595) achieving lower predictability than older multi-kinase agents. KAALCURA features transferred across datasets at biologically expected direction (Spearman ρ = −0.271, p = 1.25 × 10⁻³, n = 139 drugs).

**Conclusions.** Multi-modal feature engineering does not automatically improve drug response prediction in AML; mechanism-class predictability is bimodal and per-drug structure is more methodologically informative than cohort-mean AUROC. Bulk-RNA-detectable mechanisms are predictable; protein-level, mutation-subtype-dependent, and drug-selectivity-driven biology are not. KAALCURA's role is cross-dataset feature transfer, not within-dataset standalone prediction. The Crenolanib paradox — clinical efficacy without RNA-detectable predictors — has implications for how clinical decision support based on bulk RNA-seq should be deployed.

**Key words:** acute myeloid leukemia; drug response prediction; machine learning; LightGBM; mechanistic axes; pre-registered analysis; mechanism-class structure; cross-dataset transfer

---

## Notes on this draft (drafting log)

*This section will be removed before submission. Tracking decisions made during this drafting session for transparency.*

**Decisions made in this draft:**

1. **Structure:** Background, Methods, Results, Conclusions — standard for *Briefings in Bioinformatics* and structured abstracts generally. Some journals prefer "Introduction/Aims" instead of "Background"; can adapt at submission.

2. **Length:** Approximately 350 words including key words. Target was 300; slightly over. The Conclusions section is the critical anchor; Methods and Background were trimmed if needed.

3. **Numerical anchors included:**
   - 520 patients × 85 drugs (cohort scale)
   - 1,034 features (architecture scale)
   - mean AUROC = 0.643 (headline result)
   - ≥ 0.70 threshold (pre-registered, anchors honesty)
   - 0.3 percent KAALCURA gain importance
   - 5 drugs ≥ 0.80, 18 drugs ≤ 0.55 (per-drug structure)
   - Spearman ρ = −0.271, p = 1.25 × 10⁻³ (cross-dataset)
   - FLT3 cluster range 0.595 to 0.884

4. **Honest framing:**
   - "falsifying the pre-registered ≥ 0.70 threshold" — opens with the negative
   - "However, per-drug AUROC distribution revealed strong mechanism-class structure" — pivots to the positive contribution
   - "KAALCURA's role is cross-dataset feature transfer, not within-dataset standalone prediction" — defines what we learned

5. **Crenolanib paradox in Conclusions:** Reviewers will read the abstract and understand the paper's argument: this is the field-relevant implication that motivates the work.

6. **Key words:** Selected for indexing — covers methodology (machine learning, LightGBM, pre-registered), application (AML, drug response prediction), and contribution (mechanism-class structure, cross-dataset transfer).

---

*Abstract Draft 1 complete. ~350 words. Honest framing. All numerical anchors verified.*

— Prasad Akula (CEO) & Claude (CSO)
2026-05-10
