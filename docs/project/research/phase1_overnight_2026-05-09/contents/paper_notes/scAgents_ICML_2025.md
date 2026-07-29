# Paper Note: scAgents (ICML 2025)

**Read date:** 2026-05-09 (Layer 1, overnight session)
**Title:** scAgents: A Multi-Agent Framework for Fully Autonomous End-to-End Single-Cell Perturbation Analysis
**Source:** ICML 2025 / GenBio 2025 Poster, OpenReview HGJQvwGtfJ
**Method class:** Agentic (multi-agent, fully autonomous)
**Maps to research question(s):** Q4, Q11 (A4 active learning, A5 operational autonomy)

---

## Core claim

**scAgents is a fully autonomous multi-agent framework that transforms raw single-cell data + task description directly into optimized computational solutions.** Given only dataset + research objective, scAgents outputs both:
- Novel model architecture
- Executable code for training and inference

WITHOUT human intervention.

This is the most aligned existing system with charter A4 (active learning) + A5 (operational autonomy).

## Reported performance

- Up to **49% reduction in prediction error vs scGPT** for gene knockouts
- Pearson correlation increase of up to 20% vs ChemCPA for drug perturbations
- Adapts effectively to scRNA-seq, scATAC-seq, CITE-seq
- Different perturbation categories handled with consistent performance

## Strengths for INTERCEPTA fullest vision

- **MOST IMPORTANT PRECEDENT FOR FULLEST VISION CHARTER §1.6 (autonomous learning system A1-A6):**
  - A4 (active learning): scAgents identifies optimal architecture per task — matches "system identifies what experiments would most improve its own knowledge"
  - A5 (operational autonomy): "without human intervention" exactly matches our requirement
  - Partial A1 (novel ranking): outputs novel MODEL ARCHITECTURES — analog of novel drug ranking
- **Outperforms scGPT** which is the SOTA per scDrugMap — this is genuine progress over current state
- **Code available** at https://anonymous.4open.science/r/scAgents-2025-242E/

## Limitations / gaps

- Perturbation analysis, not drug response prediction (closely related, not identical)
- Doesn't explicitly address A3 (drift detection)
- Doesn't address A6 (self-aware uncertainty)
- Multi-agent overhead — slower than single-model inference
- LLM dependency for agent reasoning

## Cross-references

- Surveyed in LLM4Cell (Acharjee Dip et al. 2025)
- Outperforms scGPT (Cui et al. 2024) on perturbation
- Outperforms ChemCPA on drug perturbations
- Sister method: scAgent (Mao et al. 2025) for cell annotation

## Trade-off note

For INTERCEPTA: scAgents is the **closest existing methodology to our charter A4+A5 commitments**. Two paths:

Path A: Build on top of scAgents as foundation for Layer 5
Path B: Build INTERCEPTA's own multi-agent framework, informed by scAgents

CSO recommendation: Path A. Don't reinvent multi-agent infrastructure. Extend scAgents for drug response + add A1 (novel drug generation), A3 (drift detection), A6 (self-aware uncertainty) as new modules.

## Status

SURVEYED via OpenReview + ICML 2025 abstract. Full PDF + code repo deep read essential for charter §8.1 Layer 5 architecture.
