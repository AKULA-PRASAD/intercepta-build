# Paper Note: scAgent (Mao et al. 2025)

**Read date:** 2026-05-09 (Layer 1, overnight session)
**Title:** scAgent: Universal Single-Cell Annotation via a LLM Agent
**Source:** arxiv 2504.04698 (April 2025)
**Method class:** Agentic (autonomous LLM agent)
**Maps to research question(s):** Q11 (A4 active learning, A5 operational autonomy)

---

## Core claim

scAgent is a universal LLM-based autonomous agent for cell annotation. Achieves:
- Cross-tissue generalization
- Novel cell type discovery
- Efficient incremental learning
- Outperforms existing methods in accuracy, macro F1, weighted F1 across diverse tissues
- Robust under batch effects

## Method summary

Three core components:
1. **Planning module** (LangGraph framework): graph-based agent construction, formalized operational dynamics
2. **Extensible action space**: tools the agent can call
3. **Dynamic memory module**: enables incremental learning

Built on LLMs as foundation (which LLM not specified in abstract).

## Reported performance

- State-of-the-art on universal cell annotation across tissues
- Cross-tissue generalization
- Novel cell type discovery (matches charter A1 partially — discovers novel CELL TYPES, not novel DRUGS)
- Incremental learning (matches charter A2 — continuous learning)

## Strengths for INTERCEPTA fullest vision

- **DIRECT PRECEDENT for charter A4 (active learning):** Dynamic memory + planning module = active learning machinery
- **DIRECT PRECEDENT for charter A2 (continuous learning):** "Efficient incremental learning"
- **DIRECT PRECEDENT for charter A5 (operational autonomy):** End-to-end agent
- **Shows novel-discovery is achievable** by LLM agents — supports A1 (novel candidate ranking)
- **LangGraph framework** is open source — usable infrastructure

## Limitations / gaps

- Cell annotation, NOT drug response (different downstream task)
- Doesn't address A3 (drift detection)
- Doesn't address A6 (self-aware uncertainty)
- Single task focus (annotation) vs INTERCEPTA needs multi-task
- LLM dependency means inference cost scales with LLM API cost

## Cross-references

- Surveyed in LLM4Cell (Acharjee Dip et al. 2025)
- Sister method: scAgents (ICML 2025) — multi-agent framework for perturbation analysis

## Trade-off note

For INTERCEPTA: scAgent's architecture (planning + action + memory) is the cleanest existing precedent for our charter §8.1 Layer 5 (Autonomous Learning Loop). Adopt the pattern, extend to drug response + autonomous learning.

Open question: build on top of scAgent vs build from scratch with LangGraph. Worth comparing in Layer 2 architecture phase.

## Status

SURVEYED via search results. Full arxiv PDF (2504.04698) essential for Layer 5 architecture work.
