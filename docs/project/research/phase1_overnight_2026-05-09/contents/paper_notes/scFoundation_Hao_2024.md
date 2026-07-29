# Paper Note: scFoundation (Hao et al. 2024)

**Read date:** 2026-05-09 (Layer 1 prep, surveyed via citations)
**Title:** Large-scale foundation model on single-cell transcriptomics
**Authors:** Minsheng Hao et al.
**Source:** Nature Methods, vol 21, 1481-1491 (June 2024)
**DOI:** 10.1038/s41592-024-02305-7
**Code:** https://github.com/biomap-research/scFoundation
**Method class:** Foundation model (encoder-decoder)
**Maps to research question(s):** Q1.1, Q4

---

## Core claim

scFoundation is an encoder-decoder transformer with 100M+ parameters trained on 50M+ human single-cell transcriptomes. Specifically designed with drug response prediction as a target downstream task.

## Method summary (per scDrugMap reference)

- Encoder-decoder architecture
- 121.2M parameters (per scDrugMap benchmark)
- Output dimension 3072 (largest among FMs)
- Input includes 'S' (source), 'T' (target) tokens for total/observed gene expression
- Encodes only non-zero genes; decodes both expressed and non-expressed
- Cell embedding = concat(S, T, max(genes), avg(genes))
- Training: 23.26 it/s, Inference: 69.98 it/s — fastest among FMs in scDrugMap

## Reported performance

Per scDrugMap benchmark (Wang et al. 2025):
- **Best in pooled-data evaluation** across most categories
- Cell line F1 = 0.971 (layer-freezing) / 0.947 (FT)
- Tumor tissue F1 = 0.990 (FT)
- Bone marrow F1 = 0.962 (FT)  
- PBMCs F1 = 0.940 (FT)
- Targeted therapy F1 = 0.953
- Chemotherapy F1 = 0.996
- Immunotherapy F1 = 0.832

But:
- **Cross-data fine-tuning REDUCES generalizability** vs pooled
- Worst on ibrutinib regimen in cross-data
- Strong only when pooled with similar studies

## Strengths for INTERCEPTA fullest vision

- **Best benchmark performance** in pooled-data drug response per scDrugMap
- **Encoder-decoder** allows reconstruction tasks (autoencoder properties)
- **Largest output dim (3072)** — most expressive cell representation
- **Fastest training/inference** among FMs — practical
- **Open source** with public model weights
- **Drug response specifically targeted** in design

## Limitations / gaps

- **Cross-data underperforms** UCE for true generalization
- **Healthy-cell bias** in pretraining (CELLxGENE)
- **No mechanistic interpretation** — black box embeddings
- **No drug ranking** — only sensitive/resistant classification
- **No novel drug generation (A1)**
- **No autonomous learning (A2-A6)** — frozen after pretraining
- **GPU required** for inference at scale (~24GB VRAM minimum)

## Cross-references

- **scDrugMap (Wang et al. 2025):** primary source — benchmarked as best in pooled
- **CancerFoundation (2024 bioRxiv):** addresses cancer-bias limitation
- **Charter Q9:** scFoundation requires GPU infrastructure — needs Northeastern Explorer GPU partition validation

## Trade-off note

scFoundation is the obvious primary engine choice for drug response prediction in pooled-data scenarios (within-disease, multi-cohort). UCE is better for cross-disease generalization. Combined hybrid is the best architecture for our universality vision.

## Status

SURVEYED via scDrugMap citations + Nature Methods abstract. Full-text deep read scheduled. Code download required for hands-on testing.
