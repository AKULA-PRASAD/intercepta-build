# Paper Note: Empirical Evaluation of scFMs for Cancer Outcomes (Elmarakeby et al. 2025)

**Read date:** 2026-05-09 (Layer 1 prep, overnight session)
**Title:** Empirical Evaluation of Single-Cell Foundation Models for Predicting Cancer Outcomes
**Authors:** Haitham Elmarakeby, Ahmed Roman, Shreya Johri, Eliezer M. Van Allen
**Affiliations:** Dana Farber Cancer Institute, Boston, MA
**Source:** bioRxiv 2025.10.31.685892 (Nov 2025)
**DOI:** 10.1101/2025.10.31.685892
**PMC:** PMC12637420
**Method class:** Critical empirical evaluation
**Maps to research question(s):** Q1.1, Q1.4, V1, V4 (predictive validity)

---

## Core claim

**MAJOR COUNTER-EVIDENCE TO FOUNDATION MODEL HYPE:** Systematic evaluation of 9 scFMs across 6 cancer-specific tasks under zero-shot, continual training, and fine-tuning conditions. **1,170 supervised + 130 unsupervised experiments.**

Finding: scFMs **have limited advantages in predicting clinical and biological outcomes of cancer patients compared to simpler baseline models**. They excel at certain tasks (tumor microenvironment cell annotation) but underperform on patient-level clinical/biological outcome prediction.

This is from Dana Farber Cancer Institute — high-credibility source.

## Method summary

- 9 scFMs evaluated (likely including scGPT, scFoundation, UCE, Geneformer, CancerFoundation, etc.)
- 3 alternative baseline approaches
- 6 cancer-specific tasks: subtype classification, treatment response prediction, etc.
- 3 evaluation regimes: zero-shot, continual training, fine-tuning
- Total: 1,170 supervised experiments + 130 unsupervised

## Reported findings

- **scFMs limited advantage on patient-level outcomes** vs simpler baselines (raw gene expression + clinical models)
- Strong on: tumor microenvironment cell annotation
- Weak on: clinical outcome prediction
- Cited corroboration: Theus et al. 2024 (CancerFoundation) showed CancerFoundation + scGPT embeddings DON'T outperform models trained directly on gene expression for survival prediction across most cancer types
- Bioinformatics Advances 2026 paper: "mRNA + Clin" (gene expression + clinical) achieved C-index 0.681, marginally beat "Embed-pan + Clin" (FM embeddings + clinical) at 0.678

## Strengths for INTERCEPTA fullest vision

- **DECISIVE COUNTER-EVIDENCE to scDrugMap claim:** Foundation models may not actually be SOTA for clinically-relevant tasks. Resolves the conflict between two visions: scDrugMap (FMs are best) vs Elmarakeby (FMs barely beat baselines).
- **Validates importance of explicit methods (KAALCURA):** If FMs don't beat raw gene expression on clinical outcomes, then explicit gene/pathway-level models (KAALCURA) may have practical equivalence with much better interpretability.
- **Honest evaluation methodology:** 1,170 experiments is rigorous, much more comprehensive than scDrugMap (495K cells / 60 datasets but fewer eval scenarios).
- **Dana Farber credibility:** Independent academic medical center evaluation.

## Limitations / gaps

- Doesn't fully replace scDrugMap — different evaluation focus (patient outcomes vs cell-level drug response)
- Patient-level vs cell-level evaluation are genuinely different tasks
- Doesn't propose architectural alternative
- "1,170 experiments" doesn't tell us conclusively WHICH method wins on every task

## Cross-references

- **scDrugMap (Wang et al. 2025):** primary FM-supportive evidence — this paper challenges
- **CancerFoundation (Theus et al. 2024):** evaluated by this paper, found to underperform
- **scGPT (Cui et al. 2024):** evaluated, similar finding
- **Bioinformatics Advances 2026 survival prediction paper:** corroborating evidence — raw gene expression beats FM embeddings on cancer survival

## Trade-off note for INTERCEPTA

**This paper's existence is the most important Layer 1 finding for fullest vision charter.**

It means we cannot uncritically adopt foundation models as primary engine. The scDrugMap-supported architecture (charter §8.1 provisional) needs scrutiny:
- Cell-level drug response: FMs may be SOTA (per scDrugMap)
- Patient-level outcome: simple baselines may equal or beat FMs (per Elmarakeby + corroborating papers)

**Architectural implication:** Hybrid architecture more important than ever:
- FM layer for cell-level drug response
- KAALCURA / signature scoring / GRN methods for patient-level outcomes
- Confidence weighting between methods based on task

**Charter §3 termination criterion #2 (gap articulation) HIT:** Where literature disagrees, gap is named. THIS IS THE GAP. Resolution requires:
1. Deep read of both scDrugMap + Elmarakeby methodologies
2. Understanding what specific tasks favor FMs vs baselines
3. Possibly: contributing to gap resolution via INTERCEPTA's own evaluation

## Status

SURVEYED via search results (PMC version available). Full read essential before any architectural commitment in charter §8.1.
