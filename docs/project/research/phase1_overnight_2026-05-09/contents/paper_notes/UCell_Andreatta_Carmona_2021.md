# Paper Note: UCell (Andreatta & Carmona 2021)

**Read date:** 2026-05-09 (Layer 1 prep)
**Title:** UCell: Robust and scalable single-cell gene signature scoring
**Authors:** Massimo Andreatta, Santiago J. Carmona
**Source:** Computational and Structural Biotechnology Journal, 2021
**PMC:** PMC8271111
**Code:** https://github.com/carmonalab/UCell
**Method class:** Signature scoring
**Maps to research question(s):** Q1.3, Q2

---

## Core claim

UCell is a robust gene signature scoring method for single-cell RNA-seq based on Mann-Whitney U statistic. UCell scores depend ONLY on relative gene expression in individual cells (rank-based), therefore robust to dataset composition.

## Method summary

For matrix M (m genes x n cells):
1. Calculate relative ranks r_{m,n} of expression values per cell (column-wise sort)
2. To mitigate dropout long-tail: set r_{m,n} = r_max + 1 for ranks > r_max (default r_max = 1500)
3. Compute U statistic for signature genes vs background

Cell-by-cell scoring. No dataset-level normalization required.

## Reported performance

- **Robust to dataset composition:** CD8 T cell signature on full T cell dataset vs CD8-only subset → IDENTICAL score distributions
- **Compare to AddModuleScore (Seurat):** AddModuleScore median ~1 in full vs ~0 in subset (composition-dependent — bad)
- **3x faster than AUCell**, 10x less memory: AUCell needs >64 GB for 100K cells, UCell uses 5.5 GB
- Dropout-robust by design (r_max threshold)

## Strengths for INTERCEPTA fullest vision

- **Cross-cohort comparable** — same cell, same score regardless of cohort composition. SOLVES the problem we identified with canonical KAALCURA Z-score (which is composition-dependent).
- **Composition-invariant** — exactly what cross-cohort hypothesis testing (charter Q2) needs.
- **Memory efficient** — feasible on our HPC compute nodes (16-64 GB available).
- **Open source** (R package, easily ported to Python).
- **Mechanistically interpretable** (rank-based, transparent).
- **Aligns with KAALCURA gene sets** — can score the same 48 genes (prolif/emt/ddr) without modification.

## Limitations / gaps

- **R package primary** — Python port (pyUCell) less mature; we'd need to validate.
- **Signature scoring class limitation:** Cannot achieve foundation model performance on drug response (per scDrugMap, traditional methods including signature scoring lag FMs).
- **No drug ranking** — produces signature scores, not drug rankings.
- **No autonomous learning** — fixed algorithm.
- **No novel drug generation (A1)** — purely descriptive.

## Cross-references

- **AUCell (Aibar et al. 2017):** predecessor, also rank-based but slower/memory-heavy.
- **AddModuleScore (Seurat):** predecessor, composition-dependent.
- **JASMINE (Noureen et al. 2022):** alternative single-cell-aware signature scoring, less established.
- **Round 2.2a (INTERCEPTA history):** pyUCell variant tested, mixed results (Q_C 0.532, ρ=-0.235) — but those failures may have been data issues (cross-modality bulk → scRNA), not UCell limitations.

## Trade-off note

For INTERCEPTA: UCell as the SECONDARY signature scoring layer (cross-cohort robust biological axes). KAALCURA primary for mechanistic interpretation; UCell secondary for cross-cohort transfer. Foundation model layer (scFoundation/UCE) for SOTA drug response.

## Status

SURVEYED (abstract + methods read in earlier search). Full-text would clarify performance benchmarks beyond CD8 T cell example.
