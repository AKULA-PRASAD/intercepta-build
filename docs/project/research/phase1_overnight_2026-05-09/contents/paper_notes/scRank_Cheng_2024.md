# Paper Note: scRank (Cheng et al. 2024)

**Read date:** 2026-05-09 (Layer 1 prep)
**Title:** scRank infers drug-responsive cell types from untreated scRNA-seq data using a target-perturbed gene regulatory network
**Authors:** Cheng et al.
**Source:** Cell Reports Medicine, 2024
**DOI:** 10.1016/j.xcrm.2024.101568
**Method class:** GRN-based drug response prediction
**Maps to research question(s):** Q1.3, Q4, Q7

---

## Core claim

scRank infers which cell types respond to which drugs from UNTREATED scRNA-seq data, using a target-perturbed gene regulatory network (tpGRN) approach. To the authors' knowledge, the FIRST method to infer drug-responsive cell types from untreated data via in silico drug perturbation simulation.

## Method summary

1. Build gene regulatory network from scRNA-seq
2. Identify drug targets (gene-level) for the candidate drug
3. Simulate target perturbation in the GRN
4. Compute network-based propagation effect across cell types
5. Rank cell types by drug responsiveness

Approach simulates drug effect via network alignment and diffusion in the perturbed GRN.

## Reported performance

- **71.3% overall accuracy** ranking drug-responsive cell types
- Tested on simulated and real datasets
- Applied to medulloblastoma and major depressive disorder (cancer + non-cancer!)
- Responsive cell lines significantly ranked higher than non-responsive
- Accommodates pre-labeled cell types AND unlabeled (robust)

## Strengths for INTERCEPTA fullest vision

- **Drug-responsive cell type identification** — directly maps to charter §8.1 Layer 4 (mechanistic trace per drug)
- **Untreated scRNA only** — no treated cells required (huge for clinical applicability)
- **Mechanistically interpretable** — based on GRN, transparent
- **Cross-disease validated** — both cancer (medulloblastoma) and non-cancer (depression) — important for our universality vision (Q8)
- **Could integrate with INTERCEPTA's Layer 4** — provides mechanism trace per drug-cell-type pair

## Limitations / gaps

- **71.3% accuracy** — solid but not high. Foundation models reach 90%+ on related tasks.
- **GRN quality bottleneck** — only as good as the input GRN
- **No drug structure information** — GRN-based, ignores chemical structure
- **No novel drug generation (A1)** — only ranks existing drugs
- **Limited disease coverage** in benchmark — 2 diseases tested, claims generalization

## Cross-references

- **DrugFormer (PMC11516065):** related approach with graph + LLM
- **DREEP (PMC10693176):** drug response from scRNA
- **Charter §8.1 Layer 1D (GRN-based, scRank-style):** this paper directly informs that layer

## Trade-off note

scRank is exactly the type of method we want for the GRN-based interpretation layer in our hybrid architecture. Combine with foundation model embeddings (scFoundation) for performance + UCell for robust cohort transfer + KAALCURA for mechanistic axis interpretation.

## Status

SURVEYED (abstract + key methods/results from earlier search). Full-text deep read would clarify how the tpGRN simulation specifically works and how it could integrate with our pipeline.
