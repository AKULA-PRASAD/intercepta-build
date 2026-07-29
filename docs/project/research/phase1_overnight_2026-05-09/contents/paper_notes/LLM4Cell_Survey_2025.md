# Paper Note: LLM4Cell Survey (Acharjee Dip et al. 2025)

**Read date:** 2026-05-09 (Layer 1, overnight session)
**Title:** LLM4Cell: A Survey of Large Language and Agentic Models for Single-Cell Biology
**Authors:** Sajib Acharjee Dip + 6 others (Virginia Tech)
**Source:** arxiv 2510.07793 (Oct 2025, v2 Oct 28 2025)
**Method class:** SURVEY (58 models)
**Maps to research question(s):** Q1, Q11 (especially A1-A6 autonomous learning)

---

## Core claim

First unified survey of 58 foundation and agentic models for single-cell biology. Categorizes into 5 families and maps to 8 analytical tasks. Identifies the field's current state, fragmentation, and open challenges.

## Method summary

5 model families:
- Foundation (scGPT, Geneformer, scFoundation, UCE, scBERT, CellLM, CellPLM)
- Text-bridge (GenePT, Cell2Text — link embeddings to ontology terms)
- Spatial/multimodal (TransformerST, spaLLM, scMMGPT)
- Epigenomic (EpiFoundation, EpiBERT, ChromFound)
- **Agentic (scAgent, CellVerse, scAgents, CellAgent, EpiAgent, Teddy)**

8 tasks: annotation, trajectory, perturbation, drug response, integration, etc.
10 domain dimensions including biological grounding, fairness, privacy, **explainability**, **interpretability**.

## Reported findings

- **Agentic systems achieve highest scores in explainability and cross-modal planning** but lack standardized evaluation
- **NO standardized evaluation across modalities** — metrics emphasize reconstruction over biological plausibility
- **Few studies offer independent replication** (corroborates Elmarakeby concerns)
- **Training corpora dominated by human/mouse atlases** — limits cross-species generalization
- **Rare-cell, plant, microbial systems underrepresented** — biological bias

## Open challenges identified by survey

1. Need for standardized evaluation and community leaderboards
2. Addressing data biases (over-representation of human/immune cells)
3. Cross-modal and dynamic integration (beyond pairwise)
4. **Enhancing interpretability and CAUSAL inference (moving beyond statistical correlations)**
5. Ethical and privacy-preserving methods (e.g., federated learning)
6. **Robust benchmarks for agentic reasoning fidelity and reproducibility**

## Strengths for INTERCEPTA fullest vision

- **DIRECTLY ADDRESSES CHARTER Q11 (autonomous learning architecture)** — survey of agentic systems shows the field is grappling with exactly our A1-A6 challenges
- **Validates our charter §7.4 commitment to invent:** "few studies offer independent replication" + "lack standardized evaluation of reasoning fidelity" = field is fragmented, gaps remain
- **Identifies relevant precedent agents** for our autonomous learning vision: scAgent, scAgents, CellVerse, EpiAgent, Teddy
- **Cross-references our other readings** — confirms scGPT, scFoundation, UCE, Geneformer, CancerFoundation as the foundation model landscape
- **Confirms interpretability gap** — corroborates FM Interpretability Critique (arxiv 2602.17532)

## Limitations / gaps

- Survey, not original methodology
- Doesn't propose architecture
- Doesn't resolve scDrugMap vs Elmarakeby conflict
- Field maturity varies by family — agentic systems are very early

## Cross-references

- All 6 papers we've already read are in this survey's taxonomy
- Connects to scAgents (ICML 2025) — fully autonomous multi-agent framework
- Connects to CellAgent (ICLR 2026) — natural-language driven analysis
- Connects to scAgent (2025) — universal cell annotation agent

## Trade-off note

For INTERCEPTA Layer 5 (Autonomous Learning Loop) of charter §8.1: this survey provides taxonomy and precedent agents to study. Specifically:
- A4 (active learning) ← scAgents (autonomous design)
- A5 (operational autonomy) ← CellAgent (natural language, GPT-4 driven)
- A6 (self-aware uncertainty) ← STILL NOT ADDRESSED by any surveyed agent

Charter Q11 termination criterion path:
- A1 (novel ranking): integrate generative chemistry — survey does NOT cover
- A2 (continuous learning): online learning frameworks — survey does NOT specifically cover
- A3 (drift detection): NOT in survey
- A4 (active learning): scAgents-style multi-agent
- A5 (operational autonomy): CellAgent-style LLM controller
- A6 (self-aware uncertainty): NOT in survey, INVENT REQUIRED

## Status

SURVEYED via search results + arxiv abstract. Full PDF deep read essential for charter Q11 architecture. Should be highest priority next-paper after this overnight session.
