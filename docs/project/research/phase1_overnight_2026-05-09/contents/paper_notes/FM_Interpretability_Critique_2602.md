# Paper Note: FM Interpretability Critique (arxiv 2602.17532)

**Read date:** 2026-05-09 (Layer 1 prep, overnight session)
**Title:** Systematic Evaluation of Single-Cell Foundation Model Interpretability Reveals Attention Captures Co-Expression Rather Than Unique Regulatory Signal
**Source:** arxiv 2602.17532
**Method class:** Critique / interpretability analysis
**Maps to research question(s):** Q1.2, Q7 (mechanistic interpretability)

---

## Core claim

**DECISIVE FINDING:** Attention patterns in scFMs (specifically scGPT, Geneformer) DO encode structured biological information — but this structure provides **NO incremental value** for perturbation prediction. Trivial gene-level baselines (AUROC 0.81-0.88) outperform attention-based edges (AUROC 0.70). Pairwise edge scores add zero predictive contribution. Causal ablation of "regulatory heads" produces no degradation.

**Implication for the field:** When papers (scGPT, Geneformer, etc.) claim attention captures "regulatory mechanism" as a key application, this claim is empirically unsupported. Attention captures co-expression (which is just gene-level information), not unique regulatory signal.

## Method summary

Systematic evaluation framework:
- 37 analyses
- 153 statistical tests
- 4 cell types
- 2 perturbation modalities
- Compared scGPT and Geneformer attention to:
  - Trivial gene-level baselines
  - Correlation-based edges
  - Causal ablation of putative "regulatory heads"

Cell-State Stratified Interpretability (CSSI): proposed method that addresses scaling failures, improves GRN recovery up to 1.85x.

## Reported performance / findings

- Layer-specific organization observed:
  - Early layers: protein-protein interactions
  - Late layers: transcriptional regulation
- BUT: this organization provides no incremental predictive value
- AUROC: gene-level baselines 0.81-0.88, attention edges 0.70 (gene-level WINS)
- Findings generalize from K562 → RPE1 cell types
- Attention-correlation relationship is context-dependent
- Gene-level dominance is universal

## Strengths for INTERCEPTA fullest vision

- **DECISIVE answer to charter Q7 (mechanistic interpretability):** Foundation model attention is NOT a reliable proxy for regulatory mechanism. We CANNOT use scGPT/Geneformer attention as our mechanistic interpretation layer.
- **Validates KAALCURA's role:** Mechanistic interpretation requires explicit gene-level / pathway-level reasoning, not transformer attention. KAALCURA's R_prolif/R_emt/R_ddr axes are EXACTLY this kind of explicit interpretation.
- **Validates GRN-based methods (scRank):** Direct GRN reasoning likely more interpretable than attention-derived networks.
- **CSSI proposed method** (1.85x improvement) — interesting if we want attention-based interpretation, but still limited.

## Limitations / gaps

- Tested only scGPT and Geneformer (not scFoundation, UCE)
- Tested perturbation prediction (not drug response classification)
- Doesn't propose alternative mechanistic interpretation method, only critiques existing
- Cell-type generalization tested on only 4 cell types

## Cross-references

- **scGPT (Cui et al. 2024):** target of critique, claims attention captures regulatory mechanism
- **Geneformer (Theodoris et al. 2023):** target of critique
- **scKAN (2025):** alternative interpretable architecture using Kolmogorov-Arnold networks for cell-type-specific gene relationships
- **scRank (Cheng et al. 2024):** explicit GRN approach, alternative to attention-based interpretation

## Trade-off note

For INTERCEPTA: This paper directly invalidates one architectural option for charter §8.1. **DO NOT use FM attention for mechanistic trace.** Use instead:
- KAALCURA axes (explicit gene-level interpretation, validated by mechanistically-correct PARPi coefficients in our GDSC data)
- scRank (explicit GRN simulation)
- Pathway enrichment over FM-detected differentially-expressed genes (NOT over attention weights)

This validates our hybrid architecture: FMs for prediction, separate explicit methods for interpretation.

## Status

SURVEYED via search results (full arxiv PDF and HTML available). Most consequential paper of tonight's reading for charter §8.1 architecture decisions.
