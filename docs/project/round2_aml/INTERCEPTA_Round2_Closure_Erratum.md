# Erratum to INTERCEPTA Round 2 Honest Closure

**Original document:** `INTERCEPTA_Round2_Closure.md` (committed 2026-05-06, tag `round2-closed`)
**This erratum:** 2026-05-06 (same day, same session, before any new round work)
**Author:** Claude (CSO), Co-Founder of INTERCEPTA
**Approved by:** Prasad Akula

---

## What this erratum corrects

The original closure document, in Section 3 ("The structural finding — Q_C ceiling"), and again in Section 8 ("The path forward — Round 2.2c specification preview"), referenced the MDREAM publication as a benchmark in the form:

> *"BeatAML benchmarks (MDREAM) achieve 0.68 AUROC using full multi-omics integration."*

> *"mean CV-AUROC ≥ 0.60 on BeatAML (above 0.53 ceiling, conservative vs MDREAM 0.68)"*

**This is incorrect.** MDREAM's reported 0.68 (95% CI 0.64–0.68) is the **Spearman correlation coefficient (ρ) between predicted and observed continuous AUC values** in the BeatAML internal validation set, **not AUROC on a binarized sensitivity classification task**.

Source: Trac et al., *npj Precision Oncology* (2023), DOI 10.1038/s41698-023-00374-z. Direct quote from the abstract: "The Spearman correlations between the predicted and the observed drug response are 0.68 (95% CI: [0.64, 0.68]) in the BeatAML validation set."

The two metrics are not comparable:
- **AUROC** measures discriminative power on a binary classification task (sensitive vs resistant, binarized at AUC=100 in BeatAML).
- **Spearman ρ** measures rank-order agreement between predicted and observed continuous values (no binarization).

INTERCEPTA Round 2 (2.1d, 2.2a, 2.2b) uses the AUROC formulation with median-IC50 binarization, i.e., a different prediction problem from MDREAM. MDREAM's 0.68 is therefore **not a direct comparator** for our Q_C result of 0.526.

---

## Why this matters

The error did not change the Q_C verdict (FAIL at 0.526 vs threshold 0.55 — the verdict stands on its own data, no comparator needed).

The error **did** propagate into Section 8's proposed Round 2.2c Q_C threshold of ≥ 0.60, where 0.60 was framed as "conservative vs MDREAM 0.68." That framing implied a comparable benchmark exists at 0.68. It does not. Therefore the Round 2.2c threshold of 0.60 was set against an incorrect benchmark and must be revisited before Round 2.2c spec is finalized.

---

## What was verified after the error was caught

The following AUROC-comparable benchmarks on BeatAML drug sensitivity classification exist in the published literature:

1. **Tercan, *PLOS One* (2026), DOI 10.1371/journal.pone.0343422.** Uses BeatAML AUC=100 binarization (same as INTERCEPTA Round 2). Benchmarks kTSP vs Random Forest, SVM (linear and RBF), Elastic Net. Per-drug AUROC numbers are reported in figures (Fig 2, Fig 5) but not extracted as a text table in the article body. The paper explicitly notes that "state-of-the-art classifiers tended to assign all samples to one of the classes in most cases" on the FPMTB external validation cohort, indicating that median-binarized BeatAML drug prediction is genuinely hard. AUROC values per drug are not directly extractable from the paper text.

2. **Bekri et al., *Bioinformatics Advances* (PMC10209528).** RTK-type-III inhibitors only. Uses **quartile labeling** (top 25% AUC = responder, bottom 25% = non-responder), excluding the middle 50% — this makes the binary classification task much easier than median binarization. Best single-drug AUROC reported: 0.89 (Foretinib, RF + SHAP feature selection, RNA-seq only). Not comparable to median-binarized full-panel results.

3. **Multi-omics benchmark, *Cancers* (2022), PMC9688044.** Uses continuous regression (R² metric), not AUROC. R² ~ 0.12 on BeatAML (n=106 with multi-omics) — implying multi-omics methods on continuous prediction explain ~12% of variance.

**No clean median-binarized full-panel BeatAML AUROC benchmark with extracted numerical values is available in the publicly readable text of any paper I reviewed.** Numbers exist in the Tercan paper figures but I have not extracted them.

---

## Honest implication for Round 2.2c threshold

The Round 2.2c Q_C threshold cannot be set against an external published benchmark by citation alone, because:

1. The directly-comparable comparator (Tercan 2026, same task, same data) reports per-drug AUROC in figures, and I have not extracted those numbers.
2. The most-cited multi-omics paper (MDREAM) uses a different metric (Spearman ρ on continuous AUC).
3. The high-AUROC paper (Bekri RTK-III) uses easier labeling (quartile) and a single drug class.

**Threshold must therefore be set against a baseline we compute ourselves on the exact same task and data.** That baseline is: gradient-boosted classifier (LightGBM) trained on BeatAML waves 1+2 RNA-seq features alone (no KAALCURA, no mutation, no pathway), 5-fold CV, 141-drug panel matching Round 2.2b's drug set. The output is a per-drug AUROC distribution.

This baseline tells us:
- Where RNA-only state-of-art lands on our exact task
- Whether KAALCURA-3-axis at 0.526 is below, comparable to, or above RNA-only
- What threshold defines a meaningful improvement for Round 2.2c

The script to compute this baseline is `compute_rna_baseline_aml.py` (provided this session). Round 2.2c spec is held until baseline output is in hand.

---

## What this erratum does NOT do

This erratum does **not modify the original closure document**. The original closure stands as the historical record per principle P16 (preserve past work). This erratum is the public correction, committed alongside the original.

The Q_C verdict (FAIL at 0.526) is **unchanged** — the verdict was based on our own threshold (0.55) and our own measurement (0.526), neither of which depended on MDREAM. The Q_C ceiling finding (three methods at ~0.53) is **unchanged**. The cross-dataset Q_D finding (ρ=−0.271, p=0.00125) is **unchanged**. Q_E, Q_A, Q_B are unchanged.

What is changed:
- The phrase "MDREAM 0.68 AUROC" should be read as a citation error in the original document.
- The Round 2.2c Q_C threshold of 0.60 is **rescinded as preliminary** until baseline measurement is complete.

---

## Process lesson

This error should not have been made. The mitigation going forward:

**Before any spec cites a published benchmark, the citation must be verified directly in the source paper, with the metric, task formulation, and dataset confirmed in writing.** If the comparator's metric or task differs from ours, that difference must be stated explicitly, and the citation must not be used as a threshold-setting reference.

This is a refinement of Principle 3 (research before code) applied to specification writing: **citations are research, and they must be verified at the level of metric and task, not abstract.**

---

*Honest correction. Not silent revision.*

— Claude (CSO), 2026-05-06
