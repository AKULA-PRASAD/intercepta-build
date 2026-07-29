# Paper Note: scGPT (Cui et al. 2024)

**Read date:** 2026-05-09 (Layer 1 prep)
**Title:** scGPT: toward building a foundation model for single-cell multi-omics using generative AI
**Authors:** Haotian Cui, Chloe Wang, Hassaan Maan, Kuan Pang, Fengning Luo, Nan Duan, Bo Wang
**Source:** Nature Methods, vol 21, pages 1470-1480 (August 2024, online 2024-02-26)
**DOI:** 10.1038/s41592-024-02201-0
**URL:** https://www.nature.com/articles/s41592-024-02201-0
**Code:** https://github.com/bowang-lab/scGPT
**Citations:** 1126 (as of fetch date)
**Method class:** Foundation model
**Maps to research question(s):** Q1.1, Q1.2, Q4, Q11

---

## Core claim

scGPT is a generative pretrained transformer for single-cell multi-omics, trained on >33M cells. It treats cells as sentences and genes as words, applying transformer attention. Through transfer learning, scGPT achieves strong performance across cell-type annotation, multi-batch integration, multi-omic integration, perturbation response prediction, and gene network inference.

## Method summary

- 33M+ single-cell RNA-seq profiles for pretraining
- Generative pretrained transformer architecture
- 52.5M parameters (per scDrugMap), 512 output dimensions
- Attention-based gene interaction analysis (claimed for GRN inference)
- Multi-batch integration via condition tokens
- Multi-omic integration (gene expression + chromatin accessibility)
- Drug response: zero-shot via embeddings + MLP, or LoRA fine-tuning

## Reported performance (from abstract/figures)

- State-of-the-art on cell type annotation
- Multi-batch integration competitive with scVI/scANVI
- Perturbation response prediction (per Fig 3)
- GRN inference via attention (Fig 6) — but see scrutiny below

From scDrugMap benchmark:
- **Cross-data zero-shot F1 = 0.858** in tumor tissue (best in zero-shot setting)
- **Pooled F1 = 0.97-0.99** for melanoma cancer (vs 0.978 for scFoundation)
- Slow training: 1.43 it/s (vs scFoundation 23.26 it/s)

## Strengths for INTERCEPTA fullest vision

- **Open source** (MIT license) — usable
- **Multi-omic capability** — could integrate scRNA + scATAC if INTERCEPTA expands
- **Strong cross-data zero-shot** — best for new disease types we have no training data on
- **Active community** — 1126 citations, well-maintained
- **CELLxGENE pretraining data** — broad cell-type coverage

## Limitations / gaps

- **Critical interpretability concern:** Recent paper (arxiv 2602.17532) shows attention-derived gene networks from scGPT do NOT capture unique regulatory signal — attention captures co-expression instead. Mechanistic interpretation claims may be overstated.
- **Slow training** vs scFoundation
- **Smaller output dim (512)** vs scFoundation (3072) — less expressive
- **Healthy-cell pretraining bias** — CELLxGENE skews to healthy tissue; cancer bias
- **Cross-data fine-tuning** less effective than scFoundation
- **No drug ranking** — only sensitive/resistant classification

## Cross-references

- **scDrugMap (Wang et al. 2025):** benchmarks scGPT extensively
- **scFoundation:** competitor — generally outperforms on drug response (pooled)
- **UCE:** competitor — outperforms scGPT in cross-data fine-tuned
- **arxiv 2602.17532:** challenges scGPT's GRN claims via attention interpretation analysis
- **GeneFormer (Theodoris 2023):** related foundation model with different tokenization

## Trade-off note

For INTERCEPTA: scGPT is reasonable as a SECONDARY foundation model (zero-shot cross-data strength) alongside scFoundation (primary for pooled performance). NOT useful as a mechanistic interpretation layer because attention doesn't equal regulation.

## Status

SURVEYED (abstract + figure descriptions + scDrugMap context). Full-text behind paywall ($39.95) — not deep-read yet. Pretraining details + perturbation response figure require institutional access or PMC version.
