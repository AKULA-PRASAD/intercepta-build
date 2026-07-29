# Technical Implementation — Milestones and Methods

*PART FIVE: OPERATIONS*

---

This chapter specifies the concrete technical milestones that build INTERCEPTA from current state to fullest vision. The milestones are labeled M0 through M7, with three additional capabilities (PTS, CIM, CCP) integrated across them. Each milestone has a positive gate (what must be proven to advance) and a falsification gate (what would prove the approach wrong).

The milestone framework operates without calendar dates. Each milestone advances when its gates clear; not before, not on schedule. This discipline protects against the field's characteristic failure mode of advancing on schedule despite incomplete validation. It also means progress is determined by science and engineering, not by external timelines.

The milestones build in dependency order. M0 is foundational; M1 builds on M0; M2 and M3 build on M1; subsequent milestones build on what came before. Some milestones can run in parallel where dependencies permit.

**Cross-reference to project's Round-by-Round execution (added Charter v2.1, May 2026).** The M0-M7 milestone framework in this chapter is a forward-looking architectural roadmap. The project has been building toward these milestones through Round-by-Round disease cycles since project inception. Readers of Charter v2.0 alone may not see how M0 progress maps to the project's actual execution history. The mapping for context:

| Charter v2.0 milestone | Built across Rounds and Workstreams | Operational evidence |
|---|---|---|
| **M0** (Data Infrastructure and Tooling) | Round 1 mCRPC + Round 2 AML + Round 3 GBM live test + Selectivity Redesign + Workstream B Phase 0 prep | Substantially complete (see M0 status section below); filesystem evidence + HPC verification |
| **M1** (MC-FMA Core) | cell_processing v0.1.2 module (Layer 1 exploration per Fullest Vision Research Charter v1.0); HPC Geneformer pipeline | First-contact smoke test PASS (May 9, 2026); full MC-FMA implementation pending v1.0 Layer 2 architecture design |
| **M2** (PACE — Pathway-Anchored Cellular Embedding) | Not yet designed; Layer 5 pathway databases ingested (KEGG, Reactome, MSigDB) at M0 stage | Pending v1.0 Layer 2 |
| **M3** (MFMD — Mechanistic Failure Mode Detection) | OOD detection partial: HPC Step B run produces ood_distances.npy (mean=6.74, p95=8.32) | Layer 1 evidence exists; Layer 2 design pending per v1.0 Q5 (out-of-distribution detection) |
| **M4** (CSTDP — Cellular State Trajectory Drug Prediction) | Round 2.2b Q_D PASS (cross-dataset Prog-FLT3 ρ=−0.271, p=0.00125, BeatAML→Van Galen) provides early evidence that cross-context transfer is real for KAALCURA features | Layer 1 evidence exists; Layer 2 design pending |
| **M5** (DA-DMG — Disease-Agnostic Drug Mechanism Graph) | Disease nets exist: 4,558 AML genes, 458 GBM genes, 1,530 pathways across multiple disease nets at `~/INTERCEPTA/data/...` | Partial; Layer 2 integration design pending |
| **M6** (AHG — Autonomous Hypothesis Generator) | Out-of-distribution testing infrastructure (per v1.0 H3); Scout 4 Boolean network + perturbation logic implemented | Pending; v1.0 Q5 (OOD detection) addresses precondition |
| **M7** (Closed-Loop Deployment) | Not yet designed; long-term goal | Pending Layer 5 implementation in v1.0 cadence |

**Why this mapping matters.** Charter v2.0's M0-M7 framework names the destination architecture. The Fullest Vision Research Charter v1.0 (`docs/research/INTERCEPTA_Fullest_Vision_Research_Charter_v1.0.md`) specifies the research discipline (5-layer cadence: Lit Survey → Architecture Design → Validation Strategy → Implementation Spec → Code) by which M0-M7 are designed and implemented. The project's existing Round 1 (mCRPC closed v4.1, April 21, 2026) + Round 2 (AML closed at 2.2c FAIL with valuable findings, May 6, 2026) + Round 3 (GBM live test for architectural verification) + Selectivity Redesign (May 7, 2026) + Workstream B Phase 0 prep (May 8, 2026) work has built foundational components for these milestones.

**The three layers operate together.** Charter v2.0 (this book) describes the destination architecture and the vision. Fullest Vision Research Charter v1.0 describes the research path with measurable success criteria (U1-3, V1-4, I1-3, H1-4, P1-3). Operational artifacts (Errata, T1-Lite log, Round closures, Vision Module 1 Amendment, Architectural Debt Erratum) document progress along the path with §9 honesty discipline. None supersedes the others. Charter v2.1's amendments are cross-references making this multi-layer structure explicit.

## Milestone M0 — Data Infrastructure and Tooling

The foundational milestone establishes the infrastructure on which all subsequent work depends. Without M0, no other milestone has the data, compute, or tooling it needs.

**Objectives.** Stage cross-disease cellular cohorts. Integrate biological knowledge databases (KEGG, Reactome, MSigDB, DrugBank, STITCH). Establish GPU compute environment on HPC. Build data processing pipelines. Establish version control, experiment tracking, and reproducibility infrastructure.

**Specific deliverables.** TCGA cancer cohorts integrated. LuCA non-small-cell lung cancer atlas integrated (already substantially done — 3 million cells across 30 studies). Foundational cohorts for autoimmune (synovial single-cell data), neurodegenerative (brain single-cell data), and infectious disease integrated. Pathway databases ingested in machine-readable form. Drug-target databases ingested. GPU environment on Northeastern Explorer HPC operational with PyTorch and Hugging Face Transformers. Foundation models scFoundation, Geneformer, UCE downloaded and verified. Pipeline tooling (Snakemake or equivalent) for reproducible analysis.

**Positive gate.** Cross-disease data is staged and accessible. Foundation models load and produce embeddings. Biological knowledge is queryable. Compute environment runs end-to-end test pipelines successfully.

**Falsification gate.** If cross-disease data cannot be obtained at appropriate quality and scale, the milestone fails. Without cross-disease data, dynamic universality is not achievable.

**Status as of charter writing.** Substantially complete. LuCA integration done. Pathway databases available. Foundation models downloaded. HPC environment functional. Remaining work: explicit autoimmune, neurodegenerative, and infectious disease cohort integration; full pipeline operationalization.

**M0 evidence base (amended Charter v2.1, May 2026).** The "substantially complete" claim is grounded in concrete filesystem and HPC verification:

- **Data sources integrated** at `~/INTERCEPTA/data/`: AlphaFold (protein structures), BeatAML 2.0 (AML drug sensitivity, 520 patients × 141 drugs), ChEMBL (bioactives), ClinicalTrials database, DICE (immune cell expression), GDSC (cell line drug response), GTEx v8 (tissue expression, 54 tissues), HMDB (metabolome), Human GEM (genome-scale metabolic model), NSCLC LuCA atlas at `data/nsclc/luca_salcher2022/` (Salcher 2022 *Cancer Cell*, 309 patients, 538 samples, 1,283,972 cells across 29 source studies), OpenTargets (26,288 diseases × 23,422 targets), plus AlphaFold cache, docking, encode, epigenome, manifests directories.

- **Foundation models** at `~/INTERCEPTA/models/Geneformer/`: Geneformer-V2-104M_CLcancer (104,386,867 parameters, 768-dim embeddings, cancer fine-tuned per Theodoris 2024 — pretraining corpus "Genecorpus-30M + cancer fine-tuning"). HPC verification job 6699287 (May 9, 2026, V100, 1015 seconds end-to-end on 9,409 cells from Travaglini-Krasnow Lung SS2 atlas).

- **HPC environment functional** at `/scratch/akula.pra/INTERCEPTA/`: V100 GPU access verified, conda environment at `/scratch/akula.pra/INTERCEPTA/envs/intercepta-nsclc` (48 packages including scanpy 1.11.5, anndata 0.12.13, lightgbm 4.6.0, pyarrow 24.0.0). Step B Geneformer pipeline ran end-to-end May 9, 2026; full outputs at `/scratch/akula.pra/INTERCEPTA/results/step_B_hpc_v0_1_2/` (metrics.txt, run_report.json, embeddings.npy, axis_scores.csv, ood_distances.npy, prepared.h5ad, tokenized/).

- **Selectivity layer** at Layer 15a (GTEx tissue selectivity) shipped per `docs/INTERCEPTA_Selectivity_Redesign_Closure.md` (May 7, 2026, tag `selectivity-redesign-complete`): mCRPC (KLK3=16695.58 selectivity_vs_mean), AML (JAK3=15.84), GBM (FGFR3=2.43), NSCLC (ROS1=83.08) all disease-parameterized; T1-Lite reproducibility test PASS May 8 (`docs/T1_REPRODUCIBILITY_LOG.md`, tag `t1-lite-passed`).

- **Pathway databases** ingested: KEGG, Reactome, MSigDB integrated per Layer 5 of canonical 15-layer Universal Net Specification (`docs/INTERCEPTA_Universal_Net_Specification_v1.0.docx`).

**Operational artifacts tracking M0 progress** (per principle P15 — honest science): `docs/research/INTERCEPTA_Architectural_Debt_Erratum_2026-05-09.md` (KAALCURA gene coverage analysis on LuCA HVGs, FIX-003 closure, literature SOTA acknowledgment); `docs/INTERCEPTA_Workstream_B_Phase0_Prep_Log.md` (HPC environment setup, May 8); `docs/INTERCEPTA_Workstream_B_Spec_Erratum_LuCA.md` (cohort design amendment with hypothesis thresholds tightened, May 8).

**M0 incomplete components honestly deferred:** Layer 15b-e (ADMET, off-target binding, toxicophore detection, drug-drug interaction) — explicitly deferred per Selectivity Redesign Closure §5; autoimmune and neurodegenerative cohort integration — pending Layer 1 literature survey selection per Fullest Vision Research Charter v1.0 (`docs/research/INTERCEPTA_Fullest_Vision_Research_Charter_v1.0.md`). Charter v2.1 acknowledges these openly rather than narrating completion.

## Milestone M1 — MC-FMA Core

The first major capability milestone. MC-FMA — Mechanism-Constrained Foundation Model Adaptation — is the core technical contribution of INTERCEPTA's adaptive layer. Subsequent milestones depend on M1 working.

**Objectives.** Implement mechanism-constrained fine-tuning of foundation model embeddings. Combine FM representations with KAALCURA-style mechanistic axes (dynamically inferred per disease). Validate that resulting representations support both downstream task performance and biological interpretability.

**Method specification.** MC-FMA takes a foundation model embedding as input. Mechanism inference produces disease-specific axis decomposition. Fine-tuning optimizes a representation that performs well on downstream tasks (e.g., drug response prediction) while regularizing toward biological interpretability (alignment with mechanism axes). The fine-tuning uses standard gradient-based optimization with an objective combining task loss and mechanism alignment loss.

**Specific deliverables.** MC-FMA codebase. Trained MC-FMA models for cancer (using LuCA + GDSC), with extension paths for autoimmune and neurodegenerative disease. Validation showing MC-FMA representations support drug response prediction with mechanism interpretability.

**Positive gate.** Cell-level F1 score for drug response prediction exceeds 0.7 on Travaglini-Krasnow LuCA single-cell data. Mechanism axes produced are biologically interpretable (verifiable by domain experts). Representations transfer across closely related contexts (same disease, different cohort).

**Positive gate (amended Charter v2.1, May 2026).** The original positive gate referenced "Travaglini-Krasnow LuCA single-cell data" which conflates two distinct datasets. Charter v2.1 separates the gate into three runnable sub-gates with correct dataset assignments:

*Sub-gate 1 — Smoke test (passes by completion, not threshold).* The MC-FMA pipeline runs end-to-end on a healthy lung reference atlas: Travaglini-Krasnow 2020 *Nature* Lung SS2 atlas (9,409 cells, FACS gates Epcam+/Epcam−/CD45+). Pipeline produces embeddings, mechanism axes computable, no NaN failures. **Status:** PASS (May 9, 2026; HPC job 6699287; Geneformer-V2-104M_CLcancer; silhouette_label = −0.007924 against FACS gate labels — at the low-bar smoke-test threshold honestly framed in `code/cell_processing/README` as "coarse Epcam gating won't be much higher; real validation comes with proper cell-type labels and MC-FMA fine-tuning"). Documented in `/scratch/akula.pra/INTERCEPTA/results/step_B_hpc_v0_1_2/metrics.txt` and `step_B_travaglini_run_report.json`.

*Sub-gate 2 — Cell-type face validity (F1 ≥ 0.6 against author labels).* MC-FMA cell embeddings cluster meaningfully by author-provided cell type labels on a labeled cancer scRNA cohort: LuCA Salcher 2022 *Cancer Cell* atlas at `~/INTERCEPTA/data/nsclc/luca_salcher2022/` (1,283,972 cells from 29 source studies), with LuCA's own cell type annotations as ground truth. **Status:** Pending Workstream B Phase 1 implementation (per `docs/INTERCEPTA_Workstream_B_NSCLC_Specification.md` H1, amended per `docs/INTERCEPTA_Workstream_B_Spec_Erratum_LuCA.md`).

*Sub-gate 3 — Drug response F1 ≥ 0.7 (the actual MC-FMA commitment).* Per-drug AUROC on a cohort with measured drug response: BeatAML 2.0 for AML drug response (520 patients × 85 drugs after 10/10 filter); GDSC for cell-line drug response (286 drugs validated for canonical KAALCURA per `results/kaalcura_real_validation_RERUN.csv`); TCGA-LUAD + GDSC alignment for NSCLC (per Workstream B Specification H3). **Note:** The Travaglini-Krasnow 2020 atlas (healthy lung) is not a valid test substrate for this gate because it has no drug response labels; using it would be category-error. **Status:** Pending Workstream B Phase 3 implementation. Comparator baselines: KAALCURA canonical AUROC=0.671 (286 drugs); RNA-1000 LightGBM AUROC=0.645 (BeatAML, 85 drugs); Round 2.2c multi-modal AUROC=0.643 (BeatAML, FAIL gate 0.70 — reframed as comparator baseline for MC-FMA).

**Falsification gate.** If mechanism constraints reduce performance below FM-only baselines without compensating interpretability gains, the approach is wrong. Either mechanism formulation or constraint methodology must be revisited.

**Falsification gate (amended Charter v2.1, May 2026).** Specifically: if MC-FMA-trained embeddings fail to exceed FM-only Geneformer-V2-104M_CLcancer baseline AUROC by ≥0.02 on Sub-gate 3's BeatAML test set, AND mechanism axes produced are not domain-expert-validatable as biologically interpretable, M1 falsifies. The path forward in falsification: per Fullest Vision Research Charter v1.0 §10 P-FV-2 (no architectural commitment without explicit trade-off documentation), document the failure honestly and revisit either the mechanism-constraint formulation (Q1.4 in v1.0: cancer-bias problem in foundation models) or the constraint methodology (Q7 in v1.0: interpretability strategies that are not post-hoc theater).

## Milestone M2 — PACE

Pathway-Anchored Cellular Embedding (PACE). M2 develops representations explicitly aligned with biological pathway structure rather than gene-level features.

**Objectives.** Develop cellular embeddings where dimensions correspond to pathway activities. Validate that PACE representations support downstream tasks while being more interpretable and lower-dimensional than gene-level embeddings.

**Method specification.** PACE projects gene expression onto pathway activity scores using known pathway structure. Pathway activities are weighted by their relevance to the disease context. The result is a low-dimensional embedding where each dimension has a biological interpretation.

**Specific deliverables.** PACE codebase. PACE embeddings for cancer cohorts. Comparison against gene-level embeddings for downstream tasks.

**Positive gate.** PACE recovers MC-FMA performance with fewer than 500 dimensions (compared to thousands of gene-level dimensions). Each dimension has a clear biological interpretation.

**Falsification gate.** If pathway projection loses too much signal — if PACE substantially underperforms gene-level embeddings on downstream tasks — pathway structure does not capture relevant biology adequately. Approach revisited.

## Milestone M3 — MFMD

Mechanistic Failure Mode Detection (MFMD). M3 develops the uncertainty layer that signals when predictions should not be trusted.

**Objectives.** Implement out-of-distribution detection, mechanism mismatch detection, internal disagreement detection, and calibration audit. Validate that MFMD correctly identifies cases where predictions are unreliable.

**Method specification.** OOD detection using density estimation in FM embedding space. Mechanism mismatch detection using goodness-of-fit metrics for mechanism representation against cellular data. Internal disagreement using variance across ensemble or method variations. Calibration audit using held-out validation data with known outcomes.

**Specific deliverables.** MFMD codebase. Validation showing MFMD detects 80%+ of OOD test cases. Calibration plots demonstrating that flagged predictions have lower empirical accuracy than non-flagged predictions.

**Positive gate.** MFMD detects 80%+ of synthetic OOD cases. Predictions flagged as low confidence have empirically lower accuracy than predictions flagged as high confidence. Calibration is within acceptable tolerance on validation data.

**Falsification gate.** If MFMD flags do not predict actual error rates — if flagged predictions are not actually less accurate — the methodology fails to provide useful uncertainty signal. Approach revisited.

## Milestone M4 — CSTDP

Cellular State Trajectory Drug Prediction (CSTDP). M4 extends static drug response prediction to temporal dynamics.

**Objectives.** Implement trajectory inference for cellular state evolution under drug treatment. Validate that trajectory predictions outperform static response predictions.

**Method specification.** CSTDP combines static drug response prediction with trajectory models. Training data includes longitudinal samples where available; pseudo-time inference is used where longitudinal data is sparse. The model predicts not just response level but response dynamics: time to response, response duration, relapse probability.

**Specific deliverables.** CSTDP codebase. Trained models for cancer drug response trajectories. Validation against longitudinal cohorts.

**Positive gate.** Trajectory predictions outperform static predictions on longitudinal validation cohorts. Predictions of relapse probability are calibrated.

**Falsification gate.** If trajectory modeling does not add predictive signal beyond static prediction, the additional complexity is not justified. Static prediction sufficient.

## Milestone M5 — DA-DMG

Disease-Agnostic Drug Mechanism Graph (DA-DMG). M5 develops the structured knowledge that supports cross-disease intervention exploration.

**Objectives.** Build a knowledge graph organizing drugs by their mechanisms (targets, pathways, cellular effects) rather than by indication. Validate that mechanism-based drug retrieval supports disease-agnostic prediction.

**Method specification.** DA-DMG ingests drug-target databases (DrugBank, STITCH, ChEMBL), pathway databases (KEGG, Reactome), and clinical use information. The graph encodes drugs as nodes with mechanism attributes; relationships encode target binding, pathway modulation, cellular effects. Queries by mechanism return drugs regardless of indication.

**Specific deliverables.** DA-DMG knowledge graph. Query infrastructure. Validation showing mechanism-based retrieval enables cross-disease drug repositioning hypotheses.

**Positive gate.** Cancer-trained models predict non-cancer drug responses with AUROC above 0.65 when DA-DMG enables mechanism-based transfer.

**Falsification gate.** If cross-disease transfer through DA-DMG fails — if mechanism similarity does not predict cross-disease transferability — the cross-disease vision needs alternative approach.

## Milestone M6 — AHG

Autonomous Hypothesis Generator (AHG). M6 develops the system component that orchestrates mechanism discovery.

**Objectives.** Build an agent that monitors INTERCEPTA's data, identifies novel patterns suggesting unknown mechanisms, generates testable hypotheses, suggests validation experiments. Validate that AHG produces hypotheses that domain experts judge worth investigating.

**Method specification.** AHG combines the surveillance layer outputs (cross-patient pattern detection, drift monitoring) with mechanism inference and structured biological knowledge. Patterns not explained by current mechanism understanding are flagged. The agent generates hypotheses about novel mechanisms that would explain the patterns. Hypotheses are structured for experimental review.

**Specific deliverables.** AHG codebase. Hypothesis generation pipeline. Validation showing AHG identifies hypotheses domain experts confirm as worth experimental investigation.

**Positive gate.** AHG generates at least one novel drug-disease mechanism hypothesis judged by independent experts to merit experimental validation. Generated hypotheses have specific, testable predictions.

**Falsification gate.** If AHG only repeats known mechanisms or produces hypotheses experts judge implausible, the approach fails to add value beyond pattern recognition humans could perform.

## Milestone M7 — Closed-Loop Deployment

The capstone milestone. Real patient data flows through INTERCEPTA, predictions are made, outcomes are observed, the system learns from outcomes, and the loop closes.

**Objectives.** Operate INTERCEPTA in a deployment context (initially research-grade, eventually clinical) where the full loop runs. Validate that closed-loop operation produces sustained capability improvement.

**Method specification.** Patient samples are processed through the operational pipeline (Chapter 12). Predictions are made and recorded. Outcomes are observed and integrated. Calibration updates, mechanism understanding refines, system improves. The loop operates continuously.

**Specific deliverables.** Operational deployment in research or clinical context. Validation of closed-loop operation. Documentation of system improvement over time through closed-loop learning.

**Positive gate.** Closed loop operates for at least one disease end-to-end with documented system improvement over time. Patient stratification predictions show improved calibration as outcomes accumulate.

**Falsification gate.** If closed-loop operation does not produce capability improvement — if outcomes do not translate into better predictions — the architectural commitment to scaling intelligence is not realized.

## Three Additional Capabilities — PTS, CIM, CCP

Three capabilities are integrated across milestones rather than as separate milestones:

**PTS — Phenotype Target Specification (Chapter 7.3).** Integrated into M1 (mechanism inference includes target inference) and refined in M5 (cross-disease target patterns inform DA-DMG queries). PTS is operationally part of mechanism inference; its development tracks with mechanism inference development.

**CIM — Combinatorial Intervention Modeling (Chapter 7.8).** Integrated into M5 (DA-DMG supports combination retrieval) and M6 (AHG can generate combinatorial hypotheses). CIM extends the single-agent prediction methodology with combination-specific models. Its development depends on accumulating combination training data, which is sparser than single-agent data.

**CCP — Causal Counterfactual Prediction (Chapter 7.7).** Integrated across M1 (mechanism inference supports causal reasoning), M3 (uncertainty quantification includes counterfactual uncertainty), and M5 (mechanism graph supports causal traversal). CCP is methodologically demanding — causal inference is harder than correlational prediction. Its development uses interventional data where available and mechanism-aware methods where interventional data is sparse.

These three capabilities are essential to fullest vision. They are not separated as standalone milestones because they integrate naturally with multiple milestones rather than standing alone.

## Falsification Gates at Every Milestone

Each milestone has both a positive gate (what must be proven to advance) and a falsification gate (what would prove the approach wrong). Both gates are essential.

The positive gate is what most engineering organizations track: success criteria that must be met. The falsification gate is what most organizations skip: what would constitute failure that justifies abandoning or revisiting the approach.

INTERCEPTA's commitment to falsification at every milestone is part of the discipline that protects against sunk-cost fallacy. When an approach fails its falsification gate, the appropriate response is to abandon or revisit, not to patch and continue. The discipline is hard because abandonment looks like failure; in reality, abandoning what does not work is what enables progress to what does work.

Falsification gates are pre-registered before milestone work begins. They are not invented at the end to justify whatever was achieved. Pre-registration prevents the natural tendency to gerrymander gate definitions to fit results.

When falsification gates are triggered, the response process includes: investigation of why the approach failed, characterization of what was learned, decision about whether to abandon or revisit, and communication to relevant stakeholders. The response is documented; lessons are published.

## Dependency Graph and Parallel Paths

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
