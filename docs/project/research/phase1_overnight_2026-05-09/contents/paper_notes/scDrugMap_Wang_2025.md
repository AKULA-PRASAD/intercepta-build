# Paper Note: scDrugMap (Wang et al. 2025)

**Read date:** 2026-05-09 (charter v1.1 + Layer 1 prep)
**Title:** scDrugMap: benchmarking large foundation models for drug response prediction
**Authors:** Qing Wang, Yining Pan, Minghao Zhou, Zijia Tang, Yanfei Wang, Guangyu Wang, Qianqian Song
**Source:** Nature Communications, vol 17, Article 730 (2026, online 2025-12-11)
**DOI:** 10.1038/s41467-025-67481-2
**URL:** https://www.nature.com/articles/s41467-025-67481-2
**PDF:** https://www.nature.com/articles/s41467-025-67481-2.pdf
**Method class:** Benchmark study / foundation model evaluation
**Maps to research question(s):** Q1.1, Q1.4, Q4

---

## Core claim

The first systematic benchmark of foundation models for single-cell drug response prediction. Evaluates 8 single-cell foundation models (tGPT, scBERT, Geneformer, CellLM, scFoundation, scGPT, CellPLM, UCE) and 2 general-purpose LLMs (LLaMa3-8B, GPT4o-mini) across 495,000 cells from 60 datasets. Provides "first comprehensive benchmarking" of FMs for single-cell drug response prediction.

## Method summary

Two evaluation regimes:
1. **Pooled-data evaluation:** datasets from multiple studies in same category combined, then split for train/test.
2. **Cross-data evaluation:** train on study A, test on study B (true generalization test).

Two training strategies per model:
1. **Layer-freezing:** FM weights frozen, only MLP classifier trained on embeddings.
2. **LoRA fine-tuning:** Low-Rank Adaptation, rank=8, alpha=8, dropout=0.05, task=SEQ_CLS.

10-fold cross-validation. F1, AUROC, accuracy, precision, recall reported.

## Reported performance

### Pooled-data (best case, F1 score)

| Model | Cell line | Tumor tissue | Bone marrow | PBMCs | Notes |
|-------|-----------|--------------|-------------|-------|-------|
| scFoundation (FT) | 0.947 | 0.990 | 0.962 | 0.940 | Best overall |
| scGPT | 0.978 melanoma | varies | varies | varies | Best for melanoma |
| scBERT | 0.630 | varies | varies | 0.483 | Worst |
| CellLM | varies | varies | varies | 0.461 | Underperforms PBMCs |
| Geneformer | varies | varies | varies | 0.442 immunotherapy | Underperforms immunotherapy |

By drug type (scFoundation FT): targeted therapy 0.953, chemotherapy 0.996, immunotherapy 0.832

### Cross-data (real-world simulation)

Most models F1 < 0.8 in cross-data (compared to >0.9 in pooled).
- **UCE FT** best in tumor tissue (F1 = 0.774), targeted therapy (F1 = 0.549), paclitaxel (F1 = 0.677)
- **scGPT layer-freezing** F1 = 0.858 in tumor tissue
- **scFoundation cross-data** showed REDUCED generalizability vs pooled
- **GPT4o-mini** highest F1 = 0.690 in liver cancer; mostly poor

### Computational scalability (Fig 7)

| Model | Parameters | Output dim | Training speed | Inference speed |
|-------|-----------|-----------|----------------|-----------------|
| scFoundation | 121.2M | 3072 | 23.26 it/s | 69.98 it/s |
| scGPT | 52.5M | 512 | 1.43 it/s | 1.44 it/s |
| UCE | smaller | 1280 | competitive | competitive |
| scBERT | smaller | 200 | slower | slower |
| Geneformer | smaller | 256 | slower | slower |

scFoundation is most parameter-rich AND fastest. Best of both.

### Training data

Validation collection 18,856 cells from 24 datasets across 6 studies (NSCLC, ovarian, pancreatic, colon, BCC, melanoma).
Primary 326,751 cells from 36 datasets across 23 studies.

## Strengths for INTERCEPTA fullest vision

- **Direct answer to Q1.1:** SOTA is foundation models, with scFoundation leading in pooled (F1 ~0.97) and UCE leading in cross-data fine-tuned (F1 ~0.77).
- **Validates our concern:** The 0.671 GDSC AUROC for canonical KAALCURA is below pooled-data SOTA but comparable to cross-data SOTA scenarios.
- **Diverse cancer coverage:** 14 cancer types in benchmark — matches our universal-vision aspiration.
- **Reproducible toolkit:** scDrugMap GitHub + web server (https://scdrugmap.com/) — could integrate.
- **Class imbalance noted:** AUPRC < 0.7 even for SOTA models in cross-data — honest acknowledgment of limits.

## Limitations / gaps

- **Cross-data F1 below 0.8 for ALL models** — even SOTA fails to truly generalize across studies. This is a real ceiling.
- **No autonomous learning** — none of the methods address A2-A6 from charter v1.1 (continuous learning, drift detection, active learning, self-aware uncertainty).
- **No mechanistic interpretation** — purely classification (sensitive vs resistant), no drug ranking with mechanism.
- **No novel drug ranking (A1)** — all methods predict response to existing drugs, not novel candidates.
- **Class imbalance limitation** — AUPRC <0.7 in most settings, real practical concern.
- **No N>1 disease comparison** — diseases evaluated separately, not cross-disease robustness.
- **Foundation model weights freeze** — pretrained models stop learning after pretraining (no continuous learning).

## Cross-references

- **scFoundation (Hao et al. 2024):** primary winner in pooled-data. Need to read directly.
- **scGPT (Cui et al. 2024):** winner in zero-shot cross-data. Need to read directly.
- **UCE (Rosen et al. 2023, bioRxiv):** winner in fine-tuned cross-data. Need to read directly.
- **scDEAL (Chen et al. 2022):** older deep learning baseline outperformed by FMs but not by huge margin.
- **DREEP (Pellecchia et al. 2023):** statistical method baseline.
- **Geneformer (Theodoris et al. 2023):** poor on immunotherapy specifically.

## Trade-off note

For INTERCEPTA fullest vision:
- **Adopting scFoundation as primary engine:** SOTA performance, validated, GPU-required (~121M params)
- **Adopting UCE for cross-cohort robustness:** Best for true generalization scenarios
- **Layered hybrid:** Use scFoundation for pooled within-disease, UCE for cross-disease
- **NOT abandoning KAALCURA:** mechanistic axes (R_prolif, R_emt, R_ddr) provide interpretation layer that FMs lack

## Implications for charter Q1 (method-class selection)

This paper is decisive for Q1. Conclusion: **single-method approach (signature scoring alone, OR foundation model alone) is suboptimal.** Best architecture per literature evidence:
1. Foundation model layer (scFoundation for performance, UCE for cross-cohort)
2. KAALCURA layer (mechanistic interpretation)
3. Signature scoring (UCell) for backwards compatibility

This validates the provisional architecture in charter §8.1.

## Status

SURVEYED (abstract + full-text intro/results/methods read; figures interpreted from descriptions; supplementary not yet read).
