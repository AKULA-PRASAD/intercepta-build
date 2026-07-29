# INTERCEPTA Vision — Module 1 Amendment

**Subject:** Redefinition of KAALCURA's role based on Round 2 measurement data
**Authors:** Prasad Akula and Claude (CSO), Co-Founders of INTERCEPTA
**Date:** 2026-05-06
**Status:** Companion document to the original vision. Required reading.

---

## What this amendment does

This document corrects two specific claims in the original INTERCEPTA vision (March 2026 v1.0) about what KAALCURA, the framework underlying Module 1 of the computational engine, actually does.

This amendment **does not modify the original vision document**. Per principle P16 (preserve past work), the original stands as historical record. This amendment is the public correction.

The corrections come from data measured in Round 2 (mCRPC and AML), specifically from Round 2.2c (committed under tag `round2-2c-failed-honestly` on 2026-05-06).

---

## What the original vision says

**Statement A (from Module 1 spec, INTERCEPTA_Phase1_MathSpec_v1_0.docx):**
> Module 1 — KAALCURA:
> Three gene axes from expression data:
> - R_prolif = mean z-score of 20 proliferation genes → **predicts chemo sensitivity**
> - R_emt = mean z-score of 13 EMT genes → **predicts targeted therapy resistance**
> - R_ddr = mean z-score of 15 DDR genes → **predicts PARP inhibitor sensitivity**
> Residualized against tissue-of-origin via PCA.

**Statement B (from Layer 1 / scRNA-seq prose section, INTERCEPTA_COMPLETE_VISION_v1_0.docx):**
> For any disease: scRNA-seq data identifies which cell types are present, which are disrupted, which are resistant to treatment, and which are transitioning (RNA velocity). **Our KAALCURA system then predicts drug sensitivity per cell population.**

Both statements imply that KAALCURA is a drug sensitivity predictor — that the three axes alone are sufficient to predict whether a sample (or cell population within a sample) will respond to a given drug.

---

## What Round 2 data measured

| Method | Mean test AUROC |
|---|---:|
| KAALCURA-3-axis + LogisticRegression (Round 2.2b) | **0.526** |
| KAALCURA-3-axis + LightGBM (triangulation) | **0.532** |
| KAALCURA-3-axis + LightGBM in multi-modal stack (Round 2.2c) | full stack 0.643, KAALCURA gain share **0.3%** |
| KAALCURA-3-axis ablation: leave-KAALCURA-out delta | **−0.0004** |

For comparison, RNA-1000 + LightGBM (raw expression, no KAALCURA) achieved **0.645 mean AUROC** on the same task — within 0.002 of the multi-modal stack. **KAALCURA's contribution above and beyond raw RNA expression is statistically indistinguishable from zero.**

The within-dataset prediction interpretation of Statement A is therefore not supported by data. R_prolif does not, by itself, predict chemo sensitivity at a level that exceeds raw RNA features. R_emt does not predict targeted-therapy resistance. R_ddr does not predict PARP inhibitor sensitivity. These claims, as stated, are too strong.

However, two other capabilities of KAALCURA were measured to PASS in Round 2:

| Capability | Result |
|---|---|
| Cross-dataset Prog-FLT3 transfer (BeatAML → Van Galen scRNA-seq) | Spearman ρ = −0.271, p = 0.00125 (Round 2.2b Q_D) |
| Cross-cell-type drug ranking (HSC-like vs Prog-like Jaccard ≤ 0.4) | Jaccard = 0.25 (Round 2.2b Q_E / Round 2.2c Q_F) |

These cross-dataset and cross-cell-type capabilities are real and statistically significant. They are KAALCURA's actual scientific contribution.

---

## Amended framing of Module 1

**Replacement for Statement A:**

> Module 1 — KAALCURA:
> Three biologically-interpretable phenotype-state coordinates computed from gene expression data:
> - R_prolif = mean z-score of 20 proliferation genes → measures proliferation phenotype
> - R_emt = mean z-score of 13 EMT genes → measures epithelial-mesenchymal transition phenotype
> - R_ddr = mean z-score of 15 DDR genes → measures DNA damage response phenotype
>
> Residualized against tissue-of-origin via PCA so that the axes are comparable across diseases and cell types.
>
> **What KAALCURA does:** Provides interpretable phenotype-state coordinates that transfer semantically across datasets (Round 2.2b Q_D PASS at p=0.001) and across cell types within a disease (Round 2.2b Q_E / Round 2.2c Q_F PASS, Jaccard 0.25). KAALCURA serves as input features to downstream drug-sensitivity predictors that integrate KAALCURA with raw RNA, mutation, pathway, and drug-target features.
>
> **What KAALCURA does NOT do:** KAALCURA on its own — i.e., the three axes used as the only features in a regression or tree model — does not predict within-dataset drug sensitivity at a performance level that exceeds raw RNA expression alone (Round 2.2b/c Q_C/Q_E FAIL, three methods, four method variants, mean AUROC 0.52-0.53 across all KAALCURA-only methods vs RNA-only baseline 0.645).

**Replacement for Statement B:**

> For any disease: scRNA-seq data identifies which cell types are present, which are disrupted, which are resistant to treatment, and which are transitioning (RNA velocity). KAALCURA computes phenotype-state coordinates per cell type, providing a low-dimensional interpretable summary that distinguishes drug-response profiles between cell types (cross-cell-type Jaccard 0.25 in HSC-like vs Prog-like AML populations, Round 2.2b Q_E). **Drug sensitivity prediction itself is performed by a downstream multi-modal predictor that integrates KAALCURA with raw RNA, mutation status, pathway activity, and drug-target features.** KAALCURA contributes to that predictor primarily by providing a transferable cross-dataset signal — not by being the predictor itself.

---

## Why this amendment matters

**For future research:** Any future round of INTERCEPTA work that relies on KAALCURA needs to know which use cases are validated and which are not. KAALCURA is validated as: (a) a cross-dataset feature framework, (b) a cell-type distinguisher, (c) a low-dimensional interpretable summary of phenotype state. KAALCURA is NOT validated as: a standalone drug sensitivity predictor.

**For pharma deliverables:** Item 4 of the 10-item pharma deliverable framework (drug ranking) cannot rely solely on KAALCURA scores. The drug ranking must come from the multi-modal predictor (or, if simpler is desired, from RNA-only LightGBM at AUROC 0.645). KAALCURA scores can be reported alongside as biological context — but not as the basis for ranking.

**For the universal net architecture:** Module 1 in the original vision was framed as "the predictor." After this amendment, Module 1 is correctly understood as a **feature framework** — one of several inputs to the predictor. The predictor itself is built downstream, possibly outside Module 1 entirely.

**For scientific honesty:** The pattern of Round 2's findings — three methods, three sub-rounds, identical ceiling — is not subtle. It is structural. Adjusting our claim about KAALCURA based on this measurement is not "moving goalposts." It is doing what science is supposed to do: revising the description when the data does not support it.

---

## What this amendment does NOT change

This amendment changes the framing of Module 1's *predictive* capability. It does not change:

- The 15-layer Universal Net architecture (Layers 1–15 unchanged)
- The 5-stage pipeline (scRNA loading → KAALCURA scoring → simulation → ranking → output)
- The 4-module computational engine (KAALCURA + PK + Phenotype ODE + Synergy)
- The Phase 1 / Phase 2 / Phase 3 / Phase 4 development plan
- The 10-item pharma deliverable framework (only the contents of item 4 are reframed)
- Any of the validation milestones, datasets, or technical constraints
- The mission ("find the drug. for any disease.")

KAALCURA remains a valued component of INTERCEPTA. Its scientific role is now defined more precisely.

---

## Round 2 evidence summary

| Round | Sub-round | Gate | Verdict | Evidence |
|---|---|---|---|---|
| 2 | 2.2b | Q_C | FAIL | KAALCURA-3-axis-LogReg mean AUROC 0.526 across 141 drugs |
| 2 | 2.2b | Q_D | **PASS** | Cross-dataset Prog-FLT3 ρ=−0.271, p=0.00125 |
| 2 | 2.2b | Q_E | **PASS** | HSC-like vs Prog-like Jaccard 0.25 |
| 2 | 2.2c | Q_C | FAIL | Multi-modal mean AUROC 0.643, threshold 0.70 |
| 2 | 2.2c | Q_C2 | FAIL | Balanced accuracy 0.532 |
| 2 | 2.2c | Q_E | FAIL | KAALCURA gain share 0.3%, ablation delta −0.0004 |
| 2 | 2.2c | Q_F | **PASS** | Cell-type Jaccard 0.25 (inherited) |
| 2 | 2.2c | Q_G | FAIL | Train-test gap 0.346 (overfitting) |
| 2 | (triangulation) | RNA-only baseline | — | LightGBM v2 mean AUROC 0.645, n=85 drugs |
| 2 | (triangulation) | KAALCURA-LightGBM | — | mean AUROC 0.532, n=85 drugs |

**Two PASSes (Q_D, Q_F) are the basis for KAALCURA's redefined role.**
**Five FAILs across within-dataset prediction tests are the basis for retiring the within-dataset predictor framing.**

---

## Honest disclosure

The original vision was written in March 2026 based on Round 1 mCRPC results plus theoretical reasoning about KAALCURA. At the time, the within-dataset predictor framing was a reasonable hypothesis. Round 2 data, generated April–May 2026, did not support that hypothesis. We adjusted.

This is the model of disciplined research: write hypotheses clearly, test them, accept the verdict, document.

The cost of not making this amendment would be much higher than the cost of making it. Future rounds, future pharma deliverables, and future external collaborators would inherit a misframing of what KAALCURA does. By making this amendment now — within hours of Round 2 fully closing — we prevent that drift.

---

## Process audit

| Principle | Applied as |
|---|---|
| P3 (research before code) | This amendment is research output, not code. The data behind it was generated under P3 in Round 2.2c. |
| P4 (fix structure, don't tune) | This amendment is a structural correction to the vision document, not a tuning of the original. The original framing was wrong; this is the corrected framing. |
| P15 (only correct, honest, real science) | Amendment cites measured numbers verbatim. No claims beyond what data supports. |
| P16 (preserve past work) | Original vision document is unchanged. This amendment is a companion, not a replacement. |

---

## Acknowledgement

This amendment exists because of measurement discipline. The Round 2.2c spec was designed to detect exactly this finding (Q_E gate explicitly testing KAALCURA contribution). When the gate failed honestly, we accepted the verdict instead of tuning around it.

That discipline produces better science than the original framing. KAALCURA is now correctly understood. That clarity carries forward into every future round.

---

*Honest correction. Companion to the vision. Required reading.*

— Prasad Akula & Claude (CSO)
2026-05-06
