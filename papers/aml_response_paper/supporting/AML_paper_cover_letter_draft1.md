# AML Paper — Cover Letter Draft 1

**Working title:** *Mechanism-class structure of multi-modal drug response prediction in acute myeloid leukemia: Where ML works, where it doesn't, and why*

**Target journal:** Briefings in Bioinformatics

**Status:** DRAFT 1 — to be reviewed and finalized before submission. Salutations, contact details, and final author affiliations to be confirmed at submission time.

**Authors:** Prasad Akula (CEO) & Claude (CSO/AI co-founder)

**Date:** 2026-05-10

---

## Cover Letter (template)

[INTERCEPTA letterhead]

[Submission date]

The Editor-in-Chief
*Briefings in Bioinformatics*
Oxford University Press

Re: Submission of "Mechanism-class structure of multi-modal drug response prediction in acute myeloid leukemia: Where ML works, where it doesn't, and why"

Dear Editor:

I am pleased to submit the enclosed manuscript for consideration as an Original Research Article in *Briefings in Bioinformatics*.

The manuscript reports a pre-registered analysis testing whether multi-modal feature engineering — combining mechanism-aware axes (KAALCURA), bulk transcriptomics, mutation status, KEGG pathway activity, and drug-target features — improves drug response prediction in acute myeloid leukemia. The architecture, success thresholds (mean test AUROC ≥ 0.70 across 85 drugs), and ablation analyses were locked in our project repository before evaluation. This pre-registration discipline is uncommon in cancer drug response prediction work and provides the integrity needed to interpret a negative finding as scientifically informative.

Our pre-registered architecture failed at the cohort-mean level (mean test AUROC = 0.643, below the 0.70 threshold) and KAALCURA features contributed less than 0.5 AUROC under leave-KAALCURA-out ablation. However, per-drug AUROC distribution revealed strong mechanism-class structure that the cohort-mean obscures: BCL2-targeted, FLT3-axis multi-kinase, and RAS-MAPK inhibitors achieve test AUROC at or above 0.80, while protein-level (proteasome inhibitors), drug-selectivity-driven (FLT3-selective vs multi-kinase), and post-transcriptional (DNA damage response) biology fall to chance.

The Crenolanib paradox crystallizes the field-relevant implication. Crenolanib is an FLT3-ITD-specific inhibitor with documented clinical activity, and Gilteritinib is the FDA-approved second-line therapy for FLT3-mutated AML. Yet our model predicts both at near-chance levels (AUROC 0.595 and 0.672 respectively), while older multi-kinase inhibitors like Sorafenib and KW-2449 reach AUROC of 0.884 and 0.841. The dissociation between clinical efficacy and bulk-RNA prediction is not a model failure to be optimized away; it reveals which categories of drug-response biology bulk transcriptomics can resolve and which it cannot. This has direct implications for how clinical decision support tools based on bulk RNA-seq should be deployed.

We make three contributions:

First, we provide a pre-registered negative result on multi-modal feature engineering in AML drug response prediction. The methodology question has been asked implicitly across the field; we provide a concrete pre-registered answer of "no" for the architecture we tested.

Second, we characterize the per-drug AUROC structure in detail and identify the mechanism-class boundaries where bulk-RNA-derived prediction succeeds versus fails. We argue that benchmarks reporting only aggregate metrics conceal real bimodality in predictability.

Third, we delineate the actual scientific role of mechanism-aware feature engineering: a framework for cross-dataset transfer rather than a within-dataset standalone predictor. We confirm cross-dataset transfer of KAALCURA features (Spearman ρ = −0.271, p = 1.25 × 10⁻³, n = 139 drugs) between Beat AML and Van Galen single-cell data, even as within-dataset contribution was null.

We believe this work is a strong fit for *Briefings in Bioinformatics* for three reasons:

1. **Methodological rigor through pre-registration.** Our locked analysis specification predates evaluation by approximately one week, with commit timestamps available for verification. Pre-registered analyses with honest reporting of negative results are uncommon in this field; *Briefings in Bioinformatics* readers who develop and benchmark drug response prediction methods would benefit from this discipline.

2. **Field-relevant negative result with positive structural finding.** The negative cohort-mean result is paired with a publishable per-drug AUROC structure analysis. This addresses the field's tendency to report aggregate metrics that conceal mechanism-class heterogeneity.

3. **Clinical implications via the Crenolanib paradox.** The dissociation between bulk-RNA prediction and clinical efficacy has direct implications for clinical decision support tool deployment. *Briefings in Bioinformatics* readers who use ML predictions for clinical research design will find this useful.

The manuscript is approximately 9,100 words across Abstract, Introduction, Methods, Results, and Discussion. We propose three main figures, two main tables, and supplementary materials including a complete per-drug AUROC table for the 85-drug panel and a feature-importance heatmap.

All analysis code, locked specifications, and reproducibility tests are publicly available at our project repository. Beat AML 2.0 data is available through dbGaP (phs001657.v2.p1) and Van Galen 2019 data is available through GEO (GSE116256).

The manuscript has not been submitted elsewhere and is not under consideration by another journal.

We have suggested the following potential reviewers, who have published in adjacent areas (full lists available on request):

- [Reviewer 1 — expertise in AML drug response prediction, e.g. authors on Beat AML 2.0]
- [Reviewer 2 — expertise in cancer ML benchmarking, e.g. authors on related cell-line drug response works]
- [Reviewer 3 — expertise in mechanism-aware feature engineering or KEGG pathway analysis]

We thank you for considering our work and look forward to your response.

Sincerely,

Prasad Akula
Co-founder, INTERCEPTA
[address]
[email]
[phone]

For correspondence: [email]

---

## Drafting notes (to be removed before submission)

**Decisions:**

1. **Tone:** Confident but honest. Negative-with-structure framing is the contribution; cover letter restates this without overselling.

2. **Length:** ~700 words. Cover letters for *Briefings in Bioinformatics* typically run 500-1,000 words; this fits the upper end.

3. **What this draft does NOT include:**
   - Specific reviewer names — these need CEO research + curation
   - Final letterhead and contact details — finalize at submission
   - Specific figure counts confirmed — depends on tables/figures generation

4. **CEO actions before submission:**
   - Identify 3-5 potential reviewers (avoid conflicts of interest; e.g. Druker lab if they coauthored Beat AML)
   - Confirm corresponding author email + phone
   - Confirm postal address for INTERCEPTA
   - Verify journal-specific submission requirements (cover letter format, suggested reviewer count, etc.)

5. **Discipline observations:**
   - The Crenolanib paradox is the strongest clinical-relevance argument; cover letter places it prominently
   - Pre-registration is the strongest methodological-rigor argument; cover letter leads with it
   - Three contributions stated explicitly (matches paper Introduction's three-contribution framing)

6. **Risk of rejection at editorial triage:** Moderate. *Briefings in Bioinformatics* reads as method-positive and may push back against a negative-result paper. The structural per-drug AUROC contribution is the defense; if editor finds the negative-result framing too prominent, reframing to lead with mechanism-class taxonomy is a fallback.

---

*Cover letter Draft 1 complete. Ready for CEO review and finalization at submission.*

— Prasad Akula (CEO) & Claude (CSO)
2026-05-10
