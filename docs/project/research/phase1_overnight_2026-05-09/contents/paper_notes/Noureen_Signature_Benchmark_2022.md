# Paper Note: Signature Scoring Benchmark (Noureen et al. 2022)

**Read date:** 2026-05-09 (Layer 1 prep)
**Title:** Signature-scoring methods developed for bulk samples are not adequate for cancer single-cell RNA sequencing data
**Authors:** Naim Noureen et al.
**Source:** eLife (2022), article 71994
**Maps to research question(s):** Q1.3, Q4

---

## Core claim

**Bulk-sample-based methods (ssGSEA, GSVA) are systematically biased** by gene-count differences between cancer and normal cells in scRNA-seq. Single-cell-based methods (AUCell, SCSE, JASMINE) are largely spared this bias. Cautions strongly against bulk-sample methods for scRNA scoring.

## Method summary

Benchmark of 5 methods (ssGSEA, GSVA, AUCell, SCSE, JASMINE) on 10 cancer scRNA-seq datasets across cancer types and platforms.

Key finding mechanism: **Cancer cells consistently express more genes than normal cells.** This imbalance affects bulk methods that use gene-count-aware aggregation (e.g., ssGSEA's signature enrichment normalization).

## Reported performance

- **Cancer cells higher gene count** than normal cells: p < 2.2e-16 across 10 datasets
- **ssGSEA and GSVA scores are biased** by this imbalance — produces false signal
- **AUCell, SCSE, JASMINE largely spared** — rank-based or count-aware
- JASMINE: novel method, second-fastest, memory same as ssGSEA, robust across signature sizes
- AUCell: slightly faster than ssGSEA, most memory-intensive

## Strengths for INTERCEPTA fullest vision

- **Validates our gut concern about Z-score canonical KAALCURA** — bulk-style normalization in scRNA has known bias problems.
- **Provides honest method comparison** for our Q1.3 (signature scoring class).
- **Recommends single-cell-aware methods** (UCell, AUCell) for scRNA — directly informs our hybrid architecture choice.
- **Real evidence** for why we should NOT extend canonical KAALCURA (Z-score bulk-style) to scRNA cohorts directly. We must use UCell-class instead.

## Limitations / gaps

- Doesn't address foundation model methods (predates scGPT, scFoundation).
- Doesn't address cross-cohort transfer specifically.
- Cancer-only — doesn't address autoimmune, neurodegenerative.

## Cross-references

- **UCell (Andreatta & Carmona 2021):** named single-cell-aware method, robust per this benchmark
- **AUCell (Aibar et al. 2017):** rank-based, robust per this benchmark
- **ssGSEA, GSVA:** bulk-sample methods to AVOID for scRNA per this paper
- **Pont et al. 2019 SCSE:** another single-cell-aware method tested

## Trade-off note

This paper is the strongest single piece of evidence that our PROVISIONAL architecture in charter §8.1 (UCell as cross-cohort scoring) is correct over the alternative (canonical KAALCURA Z-score extended to scRNA). The Z-score approach has known bias when applied to scRNA.

For canonical KAALCURA's remaining role: it works on BULK RNA (TCGA, GTEx, GDSC validation at AUROC 0.671) — that domain is appropriate for Z-score. For scRNA cohorts (LuCA, Wu), we use UCell-class methods.

## Status

SURVEYED (abstract + introduction read in earlier search). Full-text figures would clarify quantitative bias magnitude.
