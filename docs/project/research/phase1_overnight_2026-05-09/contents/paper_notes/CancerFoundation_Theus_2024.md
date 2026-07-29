# Paper Note: CancerFoundation (Theus et al. 2024)

**Read date:** 2026-05-09 (Layer 1 prep, overnight session)
**Title:** CancerFoundation: A single-cell RNA sequencing foundation model to decipher drug resistance in cancer
**Authors:** Alexander Theus, Florian Barkmann, David Wissel, Valentina Boeva
**Source:** bioRxiv 2024.11.01.621087 (Nov 2024)
**DOI:** 10.1101/2024.11.01.621087
**Code:** https://github.com/BoevaLab/CancerFoundation
**Method class:** Foundation model (cancer-specific)
**Maps to research question(s):** Q1.1, Q1.4, Q4

---

## Core claim

First single-cell foundation model trained EXCLUSIVELY on malignant cells. Addresses critical limitation of generic scFMs (scGPT, UCE, scFoundation): they are trained mostly on healthy cells and fail to capture cancer-specific transcriptional states (e.g., copy number alterations rare in normal cells but common in cancer).

Despite using ~1M cells (50x less than scFoundation), CancerFoundation outperforms existing scFMs in cancer-specific integration and drug response tasks with 10x fewer parameters.

## Method summary

- 6 transformer layers, embedding dim 256, hidden dim 512
- ~10x SMALLER than other scFMs (per paper's claim)
- Trained on Curated Cancer Cell Atlas (Gavish et al. 2023): ~1,500 individual tumors, 112+ studies
- **Tissue + technology aware oversampling** to mitigate dataset imbalance
- Implemented without positional encoding (architectural choice)
- Trained ONLY on malignant cells (filtered out non-cancer cells)

## Reported performance

- **Outperforms scGPT, UCE, scFoundation on cancer-specific drug response prediction**
- 10x fewer parameters
- 50x less training data
- Better integration on cancer-only datasets
- Novel downstream task introduced: **survival prediction** as evaluation of FM generalizability to bulk RNA + clinical applicability

**BUT** see limitations below — Empirical Evaluation paper (2025) provides important counter-evidence.

## Strengths for INTERCEPTA fullest vision

- **Cancer-specific** — directly addresses the scFM limitation we discovered tonight (healthy-cell bias from CELLxGENE)
- **Smaller model = faster inference** — 10x fewer parameters, more practical at scale
- **Validates per-cancer-type oversampling** — could inform our universality strategy across cancer types
- **Survival prediction as downstream** — interesting evaluation pattern for clinical relevance

## Limitations / gaps

- **CRITICAL counter-evidence:** Elmarakeby et al. 2025 (bioRxiv 2025.10.31.685892, Dana Farber) systematically evaluated 9 scFMs across 6 cancer-specific tasks. Result: "scFMs had limited advantages in predicting clinical and biological outcomes of cancer patients compared to simpler baseline models." CancerFoundation specifically: embeddings did not consistently outperform models trained directly on gene expression.
- **Smaller training data (~1M cells)** — vs scFoundation 50M, scGPT 33M. Less robust to OOD.
- **Cancer-only training limits transferability** to non-cancer diseases (autoimmune, neurodegenerative) — VIOLATES our universality vision Q8 if we adopt this as primary.
- **Limited downstream tasks evaluated** — drug response, survival, but not autonomous learning A1-A6.
- **No mechanistic interpretation** — same black-box issue as other scFMs.

## Cross-references

- **scDrugMap (Wang et al. 2025):** does not include CancerFoundation in benchmark (predates)
- **Empirical Evaluation paper (Elmarakeby et al. 2025):** important COUNTER-EVIDENCE — scFMs (including CancerFoundation) underperform simple baselines on patient-level cancer outcomes
- **scGPT, UCE, scFoundation:** generic alternatives that CancerFoundation explicitly aims to improve

## Trade-off note

For INTERCEPTA: CancerFoundation is **interesting for cancer-only deployment** but **VIOLATES our universal vision** (Q8 demands ≥5 disease categories including non-cancer). Adopting CancerFoundation as primary would commit us to cancer-only — directly contradicts charter §1.1 universality.

**Honest CSO call:** Don't adopt CancerFoundation as primary. Consider as an OPTIONAL specialization layer that can be activated when cancer is detected, alongside generic UCE/scFoundation for cross-disease coverage.

**Counter-evidence concern:** If Elmarakeby et al. 2025 is correct that scFMs (including CancerFoundation) don't beat simple baselines on patient-level outcomes, this challenges the entire foundation-model-primary architecture in charter §8.1. **This needs deep follow-up reading before any architectural commitment.**

## Status

SURVEYED via search results. Full bioRxiv PDF available for deep read. Counter-evidence (Elmarakeby 2025) flagged for follow-up reading.
