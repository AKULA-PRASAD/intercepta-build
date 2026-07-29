# Chapter 13: Technical Implementation — Milestones and Methods

*PART FIVE: OPERATIONS*

---

This chapter specifies the concrete technical milestones that build INTERCEPTA from current state to fullest vision. The milestones are labeled M0 through M7, with three additional capabilities (PTS, CIM, CCP) integrated across them. Each milestone has a positive gate (what must be proven to advance) and a falsification gate (what would prove the approach wrong).

The milestone framework operates without calendar dates. Each milestone advances when its gates clear; not before, not on schedule. This discipline protects against the field's characteristic failure mode of advancing on schedule despite incomplete validation. It also means progress is determined by science and engineering, not by external timelines.

The milestones build in dependency order. M0 is foundational; M1 builds on M0; M2 and M3 build on M1; subsequent milestones build on what came before. Some milestones can run in parallel where dependencies permit.

## 13.1 Milestone M0 — Data Infrastructure and Tooling

The foundational milestone establishes the infrastructure on which all subsequent work depends. Without M0, no other milestone has the data, compute, or tooling it needs.

**Objectives.** Stage cross-disease cellular cohorts. Integrate biological knowledge databases (KEGG, Reactome, MSigDB, DrugBank, STITCH). Establish GPU compute environment on HPC. Build data processing pipelines. Establish version control, experiment tracking, and reproducibility infrastructure.

**Specific deliverables.** TCGA cancer cohorts integrated. LuCA non-small-cell lung cancer atlas integrated (already substantially done — 3 million cells across 30 studies). Foundational cohorts for autoimmune (synovial single-cell data), neurodegenerative (brain single-cell data), and infectious disease integrated. Pathway databases ingested in machine-readable form. Drug-target databases ingested. GPU environment on Northeastern Explorer HPC operational with PyTorch and Hugging Face Transformers. Foundation models scFoundation, Geneformer, UCE downloaded and verified. Pipeline tooling (Snakemake or equivalent) for reproducible analysis.

**Positive gate.** Cross-disease data is staged and accessible. Foundation models load and produce embeddings. Biological knowledge is queryable. Compute environment runs end-to-end test pipelines successfully.

**Falsification gate.** If cross-disease data cannot be obtained at appropriate quality and scale, the milestone fails. Without cross-disease data, dynamic universality is not achievable.

**Status as of charter writing.** Substantially complete. LuCA integration done. Pathway databases available. Foundation models downloaded. HPC environment functional. Remaining work: explicit autoimmune, neurodegenerative, and infectious disease cohort integration; full pipeline operationalization.

## 13.2 Milestone M1 — MC-FMA Core

The first major capability milestone. MC-FMA — Mechanism-Constrained Foundation Model Adaptation — is the core technical contribution of INTERCEPTA's adaptive layer. Subsequent milestones depend on M1 working.

**Objectives.** Implement mechanism-constrained fine-tuning of foundation model embeddings. Combine FM representations with KAALCURA-style mechanistic axes (dynamically inferred per disease). Validate that resulting representations support both downstream task performance and biological interpretability.

**Method specification.** MC-FMA takes a foundation model embedding as input. Mechanism inference produces disease-specific axis decomposition. Fine-tuning optimizes a representation that performs well on downstream tasks (e.g., drug response prediction) while regularizing toward biological interpretability (alignment with mechanism axes). The fine-tuning uses standard gradient-based optimization with an objective combining task loss and mechanism alignment loss.

**Specific deliverables.** MC-FMA codebase. Trained MC-FMA models for cancer (using LuCA + GDSC), with extension paths for autoimmune and neurodegenerative disease. Validation showing MC-FMA representations support drug response prediction with mechanism interpretability.

**Positive gate.** Cell-level F1 score for drug response prediction exceeds 0.7 on Travaglini-Krasnow LuCA single-cell data. Mechanism axes produced are biologically interpretable (verifiable by domain experts). Representations transfer across closely related contexts (same disease, different cohort).

**Falsification gate.** If mechanism constraints reduce performance below FM-only baselines without compensating interpretability gains, the approach is wrong. Either mechanism formulation or constraint methodology must be revisited.

## 13.3 Milestone M2 — PACE

Pathway-Anchored Cellular Embedding (PACE). M2 develops representations explicitly aligned with biological pathway structure rather than gene-level features.

**Objectives.** Develop cellular embeddings where dimensions correspond to pathway activities. Validate that PACE representations support downstream tasks while being more interpretable and lower-dimensional than gene-level embeddings.

**Method specification.** PACE projects gene expression onto pathway activity scores using known pathway structure. Pathway activities are weighted by their relevance to the disease context. The result is a low-dimensional embedding where each dimension has a biological interpretation.

**Specific deliverables.** PACE codebase. PACE embeddings for cancer cohorts. Comparison against gene-level embeddings for downstream tasks.

**Positive gate.** PACE recovers MC-FMA performance with fewer than 500 dimensions (compared to thousands of gene-level dimensions). Each dimension has a clear biological interpretation.

**Falsification gate.** If pathway projection loses too much signal — if PACE substantially underperforms gene-level embeddings on downstream tasks — pathway structure does not capture relevant biology adequately. Approach revisited.

## 13.4 Milestone M3 — MFMD

Mechanistic Failure Mode Detection (MFMD). M3 develops the uncertainty layer that signals when predictions should not be trusted.

**Objectives.** Implement out-of-distribution detection, mechanism mismatch detection, internal disagreement detection, and calibration audit. Validate that MFMD correctly identifies cases where predictions are unreliable.

**Method specification.** OOD detection using density estimation in FM embedding space. Mechanism mismatch detection using goodness-of-fit metrics for mechanism representation against cellular data. Internal disagreement using variance across ensemble or method variations. Calibration audit using held-out validation data with known outcomes.

**Specific deliverables.** MFMD codebase. Validation showing MFMD detects 80%+ of OOD test cases. Calibration plots demonstrating that flagged predictions have lower empirical accuracy than non-flagged predictions.

**Positive gate.** MFMD detects 80%+ of synthetic OOD cases. Predictions flagged as low confidence have empirically lower accuracy than predictions flagged as high confidence. Calibration is within acceptable tolerance on validation data.

**Falsification gate.** If MFMD flags do not predict actual error rates — if flagged predictions are not actually less accurate — the methodology fails to provide useful uncertainty signal. Approach revisited.

## 13.5 Milestone M4 — CSTDP

Cellular State Trajectory Drug Prediction (CSTDP). M4 extends static drug response prediction to temporal dynamics.

**Objectives.** Implement trajectory inference for cellular state evolution under drug treatment. Validate that trajectory predictions outperform static response predictions.

**Method specification.** CSTDP combines static drug response prediction with trajectory models. Training data includes longitudinal samples where available; pseudo-time inference is used where longitudinal data is sparse. The model predicts not just response level but response dynamics: time to response, response duration, relapse probability.

**Specific deliverables.** CSTDP codebase. Trained models for cancer drug response trajectories. Validation against longitudinal cohorts.

**Positive gate.** Trajectory predictions outperform static predictions on longitudinal validation cohorts. Predictions of relapse probability are calibrated.

**Falsification gate.** If trajectory modeling does not add predictive signal beyond static prediction, the additional complexity is not justified. Static prediction sufficient.

## 13.6 Milestone M5 — DA-DMG

Disease-Agnostic Drug Mechanism Graph (DA-DMG). M5 develops the structured knowledge that supports cross-disease intervention exploration.

**Objectives.** Build a knowledge graph organizing drugs by their mechanisms (targets, pathways, cellular effects) rather than by indication. Validate that mechanism-based drug retrieval supports disease-agnostic prediction.

**Method specification.** DA-DMG ingests drug-target databases (DrugBank, STITCH, ChEMBL), pathway databases (KEGG, Reactome), and clinical use information. The graph encodes drugs as nodes with mechanism attributes; relationships encode target binding, pathway modulation, cellular effects. Queries by mechanism return drugs regardless of indication.

**Specific deliverables.** DA-DMG knowledge graph. Query infrastructure. Validation showing mechanism-based retrieval enables cross-disease drug repositioning hypotheses.

**Positive gate.** Cancer-trained models predict non-cancer drug responses with AUROC above 0.65 when DA-DMG enables mechanism-based transfer.

**Falsification gate.** If cross-disease transfer through DA-DMG fails — if mechanism similarity does not predict cross-disease transferability — the cross-disease vision needs alternative approach.

## 13.7 Milestone M6 — AHG

Autonomous Hypothesis Generator (AHG). M6 develops the system component that orchestrates mechanism discovery.

**Objectives.** Build an agent that monitors INTERCEPTA's data, identifies novel patterns suggesting unknown mechanisms, generates testable hypotheses, suggests validation experiments. Validate that AHG produces hypotheses that domain experts judge worth investigating.

**Method specification.** AHG combines the surveillance layer outputs (cross-patient pattern detection, drift monitoring) with mechanism inference and structured biological knowledge. Patterns not explained by current mechanism understanding are flagged. The agent generates hypotheses about novel mechanisms that would explain the patterns. Hypotheses are structured for experimental review.

**Specific deliverables.** AHG codebase. Hypothesis generation pipeline. Validation showing AHG identifies hypotheses domain experts confirm as worth experimental investigation.

**Positive gate.** AHG generates at least one novel drug-disease mechanism hypothesis judged by independent experts to merit experimental validation. Generated hypotheses have specific, testable predictions.

**Falsification gate.** If AHG only repeats known mechanisms or produces hypotheses experts judge implausible, the approach fails to add value beyond pattern recognition humans could perform.

## 13.8 Milestone M7 — Closed-Loop Deployment

The capstone milestone. Real patient data flows through INTERCEPTA, predictions are made, outcomes are observed, the system learns from outcomes, and the loop closes.

**Objectives.** Operate INTERCEPTA in a deployment context (initially research-grade, eventually clinical) where the full loop runs. Validate that closed-loop operation produces sustained capability improvement.

**Method specification.** Patient samples are processed through the operational pipeline (Chapter 12). Predictions are made and recorded. Outcomes are observed and integrated. Calibration updates, mechanism understanding refines, system improves. The loop operates continuously.

**Specific deliverables.** Operational deployment in research or clinical context. Validation of closed-loop operation. Documentation of system improvement over time through closed-loop learning.

**Positive gate.** Closed loop operates for at least one disease end-to-end with documented system improvement over time. Patient stratification predictions show improved calibration as outcomes accumulate.

**Falsification gate.** If closed-loop operation does not produce capability improvement — if outcomes do not translate into better predictions — the architectural commitment to scaling intelligence is not realized.

## 13.9 Three Additional Capabilities — PTS, CIM, CCP

Three capabilities are integrated across milestones rather than as separate milestones:

**PTS — Phenotype Target Specification (Chapter 7.3).** Integrated into M1 (mechanism inference includes target inference) and refined in M5 (cross-disease target patterns inform DA-DMG queries). PTS is operationally part of mechanism inference; its development tracks with mechanism inference development.

**CIM — Combinatorial Intervention Modeling (Chapter 7.8).** Integrated into M5 (DA-DMG supports combination retrieval) and M6 (AHG can generate combinatorial hypotheses). CIM extends the single-agent prediction methodology with combination-specific models. Its development depends on accumulating combination training data, which is sparser than single-agent data.

**CCP — Causal Counterfactual Prediction (Chapter 7.7).** Integrated across M1 (mechanism inference supports causal reasoning), M3 (uncertainty quantification includes counterfactual uncertainty), and M5 (mechanism graph supports causal traversal). CCP is methodologically demanding — causal inference is harder than correlational prediction. Its development uses interventional data where available and mechanism-aware methods where interventional data is sparse.

These three capabilities are essential to fullest vision. They are not separated as standalone milestones because they integrate naturally with multiple milestones rather than standing alone.

## 13.10 Falsification Gates at Every Milestone

Each milestone has both a positive gate (what must be proven to advance) and a falsification gate (what would prove the approach wrong). Both gates are essential.

The positive gate is what most engineering organizations track: success criteria that must be met. The falsification gate is what most organizations skip: what would constitute failure that justifies abandoning or revisiting the approach.

INTERCEPTA's commitment to falsification at every milestone is part of the discipline that protects against sunk-cost fallacy. When an approach fails its falsification gate, the appropriate response is to abandon or revisit, not to patch and continue. The discipline is hard because abandonment looks like failure; in reality, abandoning what does not work is what enables progress to what does work.

Falsification gates are pre-registered before milestone work begins. They are not invented at the end to justify whatever was achieved. Pre-registration prevents the natural tendency to gerrymander gate definitions to fit results.

When falsification gates are triggered, the response process includes: investigation of why the approach failed, characterization of what was learned, decision about whether to abandon or revisit, and communication to relevant stakeholders. The response is documented; lessons are published.

## 13.11 Dependency Graph and Parallel Paths

The milestones have dependencies that determine which can run in parallel.

M0 is foundational. Nothing else proceeds without M0.

M1 builds on M0. M1 must be substantially complete before downstream milestones depending on MC-FMA can advance.

M2 (PACE) and M3 (MFMD) can run in parallel after M1. Both build on M1 but in different directions: M2 develops alternative representation; M3 develops uncertainty layer.

M4 (CSTDP) and M5 (DA-DMG) can run in parallel after M2/M3 complete. M4 extends to temporal dynamics; M5 extends to cross-disease knowledge structure.

M6 (AHG) requires significant dependencies: M3 (uncertainty layer for filtering hypotheses), M5 (knowledge graph for hypothesis generation). M6 follows M3 and M5.

M7 (closed-loop deployment) requires substantial M1-M6 completion. The full pipeline must be operational for closed-loop to work.

The critical path runs M0 → M1 → M3 → M5 → M6 → M7. Parallel paths add capability but do not shorten critical path.

The pacing is determined by science and engineering, not calendar. Each milestone advances when its gates clear. Some milestones may take much longer than others. Some may need to be revisited if falsification triggers.

This roadmap provides the framework for INTERCEPTA's technical implementation. The chapters that follow address the human dimensions (Chapter 14 — the team), economic dimensions (Chapter 15 — sustainability), and risk dimensions (Chapter 16 — failure modes). Together with the architecture, capabilities, and commitments, they constitute the full specification of INTERCEPTA from vision to execution.

---

## Figures Planned for This Chapter

**F13.1: Milestone Dependency Graph** — Network diagram showing M0 → M1 → (M2 || M3) → (M4 || M5) → M6 → M7. Critical path highlighted. Parallel paths shown explicitly. Each milestone labeled with its positive and falsification gates.

**F13.2: M1-M7 Detailed Architectures** — One detailed architecture diagram per milestone showing inputs, components, outputs. The diagrams allow readers to understand each milestone's technical content concretely.

**F13.3: Falsification Protocol** — Process diagram showing how each milestone's falsification gate is designed, pre-registered, evaluated, and acted upon. Visualizes the discipline of falsification at every stage.
