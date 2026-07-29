# Paper Note: UCE — Universal Cell Embeddings (Rosen et al. 2023/2024)

**Read date:** 2026-05-09 (Layer 1 prep, overnight session)
**Title:** Universal Cell Embeddings: A Foundation Model for Cell Biology
**Authors:** Yanay Rosen, Yusuf Roohani, Ayush Agrawal, Leon Samotorcan, Tabula Sapiens Consortium, Stephen R. Quake, Jure Leskovec
**Source:** bioRxiv 2023.11.28.568918 (v2, Oct 2024)
**DOI:** 10.1101/2023.11.28.568918
**Code:** https://github.com/snap-stanford/UCE
**HuggingFace:** minwoosun/uce-100m
**Method class:** Foundation model (zero-shot, multi-species)
**Maps to research question(s):** Q1.1, Q1.4, Q2, Q4, Q8

---

## Core claim

UCE is a foundation model providing universal cell representations across tissues, species, and conditions. Trained completely self-supervised (no annotations) on cell atlas data from 8 species. Per scDrugMap benchmark: best model in cross-data fine-tuned drug response prediction (F1 ~0.77 in tumor tissue).

## Method summary

- Sample expressed genes weighted by expression level
- Each gene tokenized via ESM2 protein embeddings (15B parameter protein language model)
- Genes sorted by genomic location, grouped by chromosome
- Chromosome boundaries delineated by special start/end tokens
- Pass through transformer
- Cell embedding from final-layer CLS token
- Training: mask portion of expressed genes, predict masked genes from cell + gene embeddings

Two variants: 4-layer model (faster) vs 33-layer model (best). Embeddings between variants are NOT compatible.

## Reported performance

- **Integrated Mega-scale Atlas:** 36 million cells, >1,000 cell types, hundreds of datasets, dozens of tissues, 8 species
- **Best in cross-data fine-tuned drug response** (per scDrugMap 2025): F1 0.77 (tumor tissue), F1 0.55 (targeted therapy)
- Emergent behavior: identifies developmental lineages, embeds novel species not in training
- Cross-species capability via ESM2 protein tokenization

## Strengths for INTERCEPTA fullest vision

- **TRUE cross-data generalization** — beats other FMs on cross-data per scDrugMap (closest to our universality vision Q8)
- **Cross-species** — could enable extrapolation to model organisms (mouse, zebrafish) for validation
- **Public weights** (HuggingFace minwoosun/uce-100m, 100M parameters)
- **Open source** (snap-stanford/UCE, MIT license)
- **Zero-shot capable** — no fine-tuning required for many tasks
- **CLS token cell embedding** — clean single-vector representation per cell

## Limitations / gaps

- **Cross-data F1 still <0.8** — even SOTA cross-data does not generalize fully (per scDrugMap)
- **Healthy-cell training bias** — trained on cell atlases (mostly healthy tissue)
- **No drug response specialization** — generic foundation model, drug response is a downstream task
- **Two model versions incompatible** — embeddings between 4-layer and 33-layer cannot be compared
- **No mechanistic interpretation** — black-box embeddings
- **No autonomous learning (A2-A6)** — frozen after pretraining

## Cross-references

- **scDrugMap (Wang et al. 2025):** validates UCE as cross-data winner
- **scFoundation:** competitor, better in pooled-data
- **scGPT:** competitor, better in zero-shot cross-data
- **CancerFoundation (Theus et al. 2024):** cancer-specific alternative addressing healthy-cell bias
- **arxiv 2602.17532:** challenges interpretability claims of all FM-class methods

## Trade-off note

For INTERCEPTA: UCE is the **primary candidate for cross-cohort generalization** (charter Q2) and **multi-disease generalization** (charter Q8). Combined with scFoundation (pooled-data winner) gives best-of-both. CancerFoundation may improve on cancer-specific, but UCE's universality matches our vision better.

## Status

SURVEYED via search results + scDrugMap benchmark context. Full bioRxiv text not deep-read yet; methods + results from abstract + GitHub README.
