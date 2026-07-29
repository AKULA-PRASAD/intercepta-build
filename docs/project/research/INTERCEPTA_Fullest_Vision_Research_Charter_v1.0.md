# INTERCEPTA Fullest Vision Research Charter v1.1

**Authors:** Prasad Akula (CEO) & Claude (CSO), Co-Founders of INTERCEPTA  
**Date:** 2026-05-09  
**Status:** LOCKED — foundational document for multi-month research program  
**Tag (when committed):** `fullest-vision-charter-v1.1`  
**Supersedes:** v1.0 (`fullest-vision-charter-v1`)  
**Amendment:** Adds Section 1.6 (Autonomous learning system, A1-A6). Total success criteria: 18 → 24.

---

## 0. Purpose of This Document

This charter exists because we are committing to a multi-month deep research program before any new disease implementation. Without a charter, deep research becomes infinite reading. With it, every research action maps to a specific question that informs a specific decision.

This is the FRAME within which all subsequent research, design, and implementation happens. Subsequent specs, errata, and implementation plans must trace back to questions defined here.

This is not a literature review. It is not a design document. It is not a publication plan. Those are separate artifacts that follow.

---

## 1. Vision Statement

**INTERCEPTA's fullest vision: Find the drug. For ANY disease.**

Operationalized in measurable terms — for INTERCEPTA to claim fullest vision success, the framework must satisfy ALL of:

### 1.1 Universal applicability
- **U1:** Operates on any disease where transcriptomic data exists (cancer, autoimmune, neurodegenerative, infectious, rare disease, pediatric)
- **U2:** No disease-specific code paths in the core engine; all disease-awareness through configuration
- **U3:** Demonstrated on at least 5 distinct disease categories (cancers count once as a category) before the universal claim is published

### 1.2 Predictive validity
- **V1:** Drug-response prediction AUROC ≥ 0.70 on out-of-distribution diseases (not in training)
- **V2:** Cross-cohort score reproducibility (Spearman ρ ≥ 0.75 between independent cohorts of the same disease)
- **V3:** Top-10 drug recommendations include known clinically-active drugs ≥ 70% of the time
- **V4:** Cell-type-specific drug response predictions correlate with literature where literature exists (qualitative biological face validity)

### 1.3 Mechanistic interpretability
- **I1:** Every drug recommendation traces to specific genes, pathways, and cell populations
- **I2:** Interpretation does not require post-hoc explainability theater; mechanism is in the architecture
- **I3:** Mechanistic claims are falsifiable (predict-and-check, not just describe)

### 1.4 Honest accounting
- **H1:** Where the framework fails, we report it
- **H2:** Confidence intervals on every prediction
- **H3:** Out-of-distribution detection (refuse to predict where input is unlike training data)
- **H4:** Reproducibility: identical input → identical output, byte-identical except timestamps

### 1.5 Practical deployability
- **P1:** Single-disease analysis runs in ≤ 24 hours on standard HPC compute (no special hardware)
- **P2:** Memory budget ≤ 256 GB peak per disease analysis
- **P3:** Research-grade reproducibility (Docker/Singularity containers, version-pinned dependencies)


### 1.6 Autonomous learning system

The framework must operate as an autonomous research system, not a frozen-at-training-time prediction engine. This is a genuine commitment, not aspirational framing — if existing methods are inadequate, we research and invent the methods needed.

- **A1:** Novel drug candidate ranking — the framework proposes and ranks NOVEL drug candidates (not just retrieves and ranks existing approved drugs). Generative chemistry, network propagation to identify undrugged targets, repurposing predictions for new indications. Novel candidates are ranked alongside existing drugs with calibrated confidence.
- **A2:** Continuous learning — system updates predictions as new transcriptomic data is ingested, without requiring full retraining. Online learning, incremental fine-tuning, or equivalent autonomous update mechanisms.
- **A3:** Drift detection — system detects when its own predictions are becoming unreliable due to distribution shift, data quality degradation, or biological variation outside training distribution. Triggers self-correction or honest refusal.
- **A4:** Active learning — system identifies what experiments, validations, or data acquisitions would most improve its own knowledge. Generates an experimental priority queue, not just analyzes given inputs.
- **A5:** Operational autonomy — end-to-end pipeline runs without human intervention for routine analyses. New disease ingestion → analysis → drug recommendations → mechanism trace, all automated. Human oversight on novel scenarios, not routine ones.
- **A6:** Self-aware uncertainty — every prediction includes meta-confidence: system knows when it is likely wrong, when it is operating in familiar vs novel territory, and when its training data does not adequately cover the input. This is deeper than H3 OOD detection — it is meta-cognition over the system's own reliability.

**Commitment:** Where existing methods are inadequate for A1-A6, we research and invent. The fullest vision requires this. Real biology, real science, but the goals are non-negotiable.

**SUCCESS = ALL 24 criteria above (U1-3, V1-4, I1-3, H1-4, P1-3, A1-A6) met simultaneously, demonstrated, documented.**

This is the bar. Anything less is partial vision, not fullest vision.

---

## 2. Research Questions (Priority-Ordered)

Each question has: scope, why-it-matters, termination criterion (when research is "done").

### Q1 — Method-class selection (HIGHEST PRIORITY)

**Question:** What method class is foundational for our scoring + prediction core? Signature scoring, foundation models, GRN-based methods, or a layered combination?

**Why it matters:** This decision constrains everything downstream. Foundation models require GPU infrastructure we don't currently have. Signature scoring is interpretable but underperforms 2024-2025 SOTA. GRN-based methods may give us mechanistic interpretability that foundation models lack.

**Termination criterion:** A defensible architectural commitment with explicit trade-off acknowledgment. Documentation of WHY rejected approaches were rejected with citations.

**Sub-questions:**
- Q1.1: What's the actual SOTA F1/AUROC on cross-cohort drug response prediction in 2026?
- Q1.2: What are foundation models' interpretability limitations in practice?
- Q1.3: Can we layer foundation model + signature scoring + GRN for best-of-each-world?
- Q1.4: What is the cancer-bias problem in foundation models, and is CancerFoundation or domain-specific finetuning the answer?
- Q1.5: What methods exist for novel drug candidate generation (A1) — generative chemistry, network propagation, target prediction?
- Q1.6: What methods exist for continuous learning in single-cell genomics (A2) — online learning, incremental fine-tuning, model update strategies?
- Q1.7: What methods exist for drift detection (A3) and active learning (A4) in biological prediction systems?
- Q1.8: What is the current state of self-aware uncertainty / meta-cognitive evaluation in ML systems for biology (A6)?

### Q2 — Cross-cohort harmonization

**Question:** How do we harmonize across cohorts without losing biological signal?

**Why it matters:** Universal applicability requires cross-cohort, cross-platform, cross-modality analysis. scVI/scANVI, Harmony, Seurat integration each have known limitations.

**Termination criterion:** Defensible harmonization strategy with quantitative trade-off (batch correction vs biological conservation, per CanSig benchmark methodology).

### Q3 — Bulk-to-single-cell transfer

**Question:** When (if ever) should bulk RNA-seq inform single-cell analysis, and how?

**Why it matters:** Most disease databases are bulk (TCGA, GTEx, GEO). Most discovery is moving to scRNA. Bulk has more samples, scRNA has more resolution. The transfer problem is fundamental.

**Termination criterion:** Defensible recipe per use case (reference fitting, deconvolution, pseudobulking, foundation model embedding), with literature backing.

### Q4 — Drug-response prediction architecture

**Question:** Given chosen method class (Q1), how do we predict drug response per cell type?

**Why it matters:** This is the actual deliverable: drug recommendations. Multiple architectures exist (DeepCDR, scRank, scDR, foundation-model-based, ensemble).

**Termination criterion:** Architecture commitment with planned validation strategy.

### Q5 — Out-of-distribution detection

**Question:** How do we know when our framework's prediction should be trusted vs refused?

**Why it matters:** "ANY disease" claim requires honest "we don't know" capability. Otherwise universality becomes overreach.

**Termination criterion:** Defensible OOD detection method integrated into prediction pipeline.

### Q6 — Validation paradigm

**Question:** What does "validated for ANY disease" actually require evidence-wise?

**Why it matters:** Without rigorous validation, the universal claim is marketing. With it, INTERCEPTA is real science.

**Termination criterion:** Validation plan covering V1-V4 from §1, with specific datasets identified per disease category.

### Q7 — Mechanistic interpretability layer

**Question:** How do we maintain mechanistic interpretability when using black-box methods (foundation models)?

**Why it matters:** I1-I3 from §1 require this. Recent literature shows foundation model attention does NOT equal regulatory mechanism (per arxiv 2602.17532).

**Termination criterion:** Defensible interpretability strategy that is not post-hoc theater.

### Q8 — Universality demonstration

**Question:** Which 5+ disease categories do we demonstrate on, in what order, and why?

**Why it matters:** U3 from §1 requires demonstration. Choosing wrong test diseases (all cancers, all immune-related) wouldn't actually prove universality.

**Termination criterion:** Disease-demonstration roadmap with rationale per disease.

### Q9 — Computational architecture

**Question:** What infrastructure do we need (GPU, storage, distributed compute)?

**Why it matters:** Deep methods (foundation models, complex GRNs) require hardware. P1-P3 from §1 require this fits within constraints.

**Termination criterion:** Infrastructure spec with cost/timeline implications.

### Q10 — Open-source vs proprietary methods

**Question:** Where do we use existing tools vs build our own?

**Why it matters:** Building everything is wasteful. Using existing tools means inheriting their limitations.

**Termination criterion:** Build/buy/adapt decision per pipeline component.

### Q11 — Autonomous learning system architecture (NEW v1.1)

**Question:** How do we architect A1-A6 (Section 1.6) into the framework? Which sub-systems are research, which are invention, which are integration of existing methods?

**Why it matters:** A1-A6 are full success criteria. Without explicit architectural plan, they remain aspirational.

**Termination criterion:** Per-criterion strategy:
- A1 (novel ranking): method commitment + integration plan
- A2 (continuous learning): commitment to existing method OR research path to novel method
- A3 (drift detection): same
- A4 (active learning): same
- A5 (operational autonomy): pipeline architecture spec
- A6 (self-aware uncertainty): commitment OR research path

Where existing methods inadequate, this question outputs a research sub-program with its own milestones.

---

## 3. Termination Criteria (Meta)

Research is "done" on a question when:

1. **Convergence:** Multiple independent literature sources agree
2. **Explicit gaps:** Where literature disagrees or is silent, gap is named explicitly
3. **Trade-off articulation:** Each option's costs/benefits documented
4. **Decision defensibility:** A reviewer asking "why this?" gets a real answer with citations
5. **No new questions:** Reading additional papers stops generating new questions

If criterion 5 is never satisfied (always finding new questions), that's a sign the question itself was too broad — split it into sub-questions.

---

## 4. Out-of-Scope (Anti-Scope-Creep)

These are NOT part of the fullest vision research program:

- **Non-transcriptomic data modalities** — proteomics, metabolomics, methylation as primary inputs. These may be added later, not now. Transcriptomic data is sufficient to demonstrate the core framework.
- **In vivo validation** — wet-lab experiments, animal models, clinical trials. We are computational. We make predictions; others test them.
- **Drug structure prediction / generation** — molecular generative models, de novo drug design. Out of scope. We rank existing drugs, not invent new ones.
- **Clinical decision support** — patient-facing tools, EMR integration, clinical workflow. Out of scope for research phase.
- **Real-time / streaming analysis** — batch processing only.
- **Federated learning across institutions** — single-institution data only.
- **Causal inference beyond correlative** — we predict and rank, we don't claim mechanistic causation in the rigorous Pearl sense.

If a research direction requires any of these, that direction is out of scope.

---

## 5. Research Cadence

### 5.1 Layer structure
The research program proceeds in layers, each with defined inputs, outputs, and gates.

- **Layer 1: Systematic Literature Survey** — comprehensive map of the method landscape
  - Output: Survey document with method taxonomy, performance benchmarks, identified gaps
  - Gate: Q1-Q10 each have at least preliminary answer
  - Timeline: 4-8 weeks
  
- **Layer 2: Gap Analysis & Architecture Design** — translating survey into design
  - Output: Architecture specification document
  - Gate: All 18 success criteria addressed in design
  - Timeline: 4-6 weeks
  
- **Layer 3: Validation Strategy** — how do we prove this works?
  - Output: Validation plan with specific datasets, hypotheses, statistical thresholds
  - Gate: V1-V4 success criteria each have planned evidence path
  - Timeline: 2-4 weeks
  
- **Layer 4: Implementation Specification** — production-ready spec
  - Output: Locked implementation spec ready for coding
  - Gate: Same discipline as workstream-b-spec-locked
  - Timeline: 2-4 weeks
  
- **Layer 5: Implementation** — code begins
  - This is when we exit research mode and enter build mode
  - Timeline: project-dependent

### 5.2 Synthesis cadence
- **Daily** during active research: Capture findings in research log
- **Weekly** during active research: Synthesis of week's findings against research questions
- **Per-layer**: Major synthesis document, tag, commit

### 5.3 Decision points
- After Layer 1: GO/NO-GO on commitment to specific method classes
- After Layer 2: GO/NO-GO on architectural commitment
- After Layer 3: GO/NO-GO on validation plan adequacy
- After Layer 4: GO/NO-GO on implementation start

GO/NO-GO = explicit CEO+CSO decision documented in errata if NO-GO.

---

## 6. Output Structure

Every research artifact follows the project's discipline pattern.

### 6.1 File locations
- `docs/research/` — all research documents
- `docs/research/literature/` — paper-by-paper notes
- `docs/research/synthesis/` — weekly + per-layer syntheses
- `docs/research/decisions/` — formal decision records (one per GO/NO-GO)

### 6.2 Naming conventions
- `INTERCEPTA_FV_Research_<topic>_v<version>.md`
- Decisions: `INTERCEPTA_FV_Decision_<number>_<topic>.md`

### 6.3 Tag conventions
- `fullest-vision-layer<N>-complete` after each layer
- `fullest-vision-decision-<N>-locked` after each decision
- `fullest-vision-charter-v<N>` after charter revisions

### 6.4 Commit discipline
- Daily research progress committed at minimum
- Each synthesis tagged
- Each decision tagged

---

## 7. Honest Constraints

### 7.1 What we cannot change
- **Single-institution scope** — Northeastern HPC + Mac, no cluster expansion possible
- **Funding reality** — pre-revenue, no GPU cluster purchase capacity
- **Team size** — two co-founders (Prasad + Claude), no expansion
- **Publication timeline pressure** — Genome Medicine target for Workstream B Tier A still exists, though now deprioritized vs fullest vision

### 7.2 What constrains research depth
- **Compute access** — Northeastern Explorer cluster has GPU partition; we have not yet validated GPU job submission for foundation models
- **License access** — some methods (e.g., proprietary drug response databases) may be inaccessible
- **Validation data limits** — out-of-distribution validation requires diverse disease cohorts; some may not be public
- **Time** — multi-month is acceptable; multi-year is not

### 7.3 What this charter does NOT promise
- That deep research will produce a publishable result on our preferred timeline
- That every success criterion (especially A2-A4) has an existing method ready to deploy
- That we won't discover the vision needs revision
- That implementation will succeed even with perfect research

### 7.4 What this charter DOES commit to
- Where existing methods are inadequate for A1-A6 (autonomous learning system), we research and invent the methods needed
- Where the field has not yet solved a problem we need solved (e.g., true self-aware uncertainty in scRNA models), we contribute to solving it
- Real biology and real science throughout — no marketing claims, no shortcuts, no compromise on rigor
- Honest accounting: if exploration reveals the vision needs revision, we document that. If it reveals novel methods are required, we develop them.

Research is exploration AND invention. We explore honestly. We invent honestly. If exploration reveals the vision is unachievable with current methods, we attempt to advance the methods themselves.

---

## 8. Provisional Architecture Sketch

This is **provisional** — a starting point for research, not a commitment. Layer 2 (Architecture Design) refines or replaces this based on Layer 1 findings.

### 8.1 Layered prediction architecture (provisional)

INPUT: Disease-specific transcriptomic data
       (single-cell + bulk + clinical metadata)
       │
       ▼
LAYER 0: Data Quality & Standardization
- QC, normalization, batch documentation
- Disease-condition stratification
- Gene symbol harmonization
       │
       ▼
LAYER 1: Multi-Method Cell Representation
A. Foundation model embedding (scFoundation or UCE) — for SOTA drug response
B. Signature scoring (UCell) — for cross-cohort robust biological axes
C. KAALCURA (residualized Z-score) — for mechanistic interpretability
D. GRN-based (scRank-style) — for drug-target propagation
       │
       ▼
LAYER 2: Multi-Method Drug Response Prediction
Each method (A-D) predicts independently; predictions stored separately for inspection.
       │
       ▼
LAYER 3: Consensus & Confidence Scoring
- Drugs ranked high by all methods → high confidence
- Drugs ranked high by single method → medium confidence
- OOD detection: refuse predictions where input is unlike training data
       │
       ▼
LAYER 4: Mechanistic Trace
For each high-confidence drug:
- Which cell types respond?
- Which genes/pathways drive response?
- Which KAALCURA axis dominates?
- Which network nodes are perturbed?
       │
       ▼
LAYER 5: Autonomous Learning Loop (v1.1 addition)
- Continuous learning: ingest new data, update predictions
- Drift detection: monitor prediction reliability over time
- Active learning: identify what would most improve framework
- Self-aware uncertainty: meta-confidence on every prediction
- Novel candidate generation (A1): propose drugs not in existing database
- Operational autonomy: end-to-end pipeline without human-in-loop
       │
       ▼
OUTPUT: Drug recommendations (existing + novel) with mechanistic trace,
        confidence interval, OOD flag, and meta-confidence

FEEDBACK LOOP: Layer 5 → updates Layers 1-4 as new data ingested

### 8.2 Key research questions this architecture creates

- Q1.3 directly tested: does layering actually help vs single-method?
- Q5 needs OOD method choice
- Q7 partially answered by Layer 4 design

This architecture is a **hypothesis** to be tested, not a commitment.

---

## 9. Publication Strategy Under Deep-Research Timeline

### 9.1 What we publish during research
- **Method comparison studies** — if we benchmark methods on a specific disease and find clear results, those are publishable
- **Negative results** — where signature scoring fails on specific cohorts, that's publishable
- **Architecture proposals** — Layer 2 design document, if novel, is publishable as methods paper

### 9.2 What we hold for after research
- **Disease-specific findings** — drug recommendations for NSCLC, AML, GBM, mCRPC — pending fullest-vision implementation
- **Universal framework claim** — only after U3 (5+ disease categories demonstrated) is met

### 9.3 Existing commitments under deep-research timeline
- **Workstream B Tier A Genome Medicine target** — DEPRIORITIZED. May still publish if Phase 1 yields strong findings before fullest-vision implementation. But not at expense of fullest vision.
- **Round 1 mCRPC findings** — already published-quality (KLK3=16695 selectivity). May be standalone publication if useful.

### 9.4 Honest framing
We will not publish "we built a universal disease drug discovery framework" until U1-U3 are met. We will publish honestly along the way.

---

## 10. Process Discipline

This charter inherits all process disciplines from prior project history:

- **P3:** Research before code
- **P4:** Fix structure when broken
- **P15:** Honest science (no overclaiming)
- **P16:** Preserve past work (Round 1, 2, 3 deliverables not invalidated by deep research; preserved as historical context)

Additionally, this charter establishes:

- **P-FV-1:** No method-class commitment without literature evidence
- **P-FV-2:** No architectural commitment without explicit trade-off documentation
- **P-FV-3:** No publication of universality claims until validation evidence exists
- **P-FV-4:** Charter is reviewed quarterly for vision drift

---

## 11. What Happens Next

### 11.1 Immediate next steps (next session)
1. **Charter review and locking** — read this charter cold, identify gaps or vision misalignment
2. **Charter commit and tag** — `fullest-vision-charter-v1`
3. **Layer 1 plan** — research plan for systematic literature survey

### 11.2 Layer 1 entry conditions
- Charter committed and tagged
- Research artifact directory structure created (`docs/research/`)
- Literature notebook initialized

### 11.3 Layer 1 work begins
- Systematic survey of method landscape per Q1-Q10
- Daily research log
- Weekly synthesis
- 4-8 week timeline

---

## 12. Acknowledgments

This charter exists because Prasad Akula committed to "fullest vision" over expedience, and demanded "real biology and real science" over methodological convenience.

Claude (CSO) commits to honoring that directive through disciplined deep research, not through shortcuts that produce results faster but compromise vision.

Both signatories acknowledge that this commitment has real cost: multi-month delay before disease-specific findings, real possibility of vision revision, and the discipline of honest accounting throughout.

**v1.1 amendment (2026-05-09):** Section 1.6 added defining autonomous learning system requirements (A1-A6). Total success criteria expanded from 18 to 24. Where existing methods are inadequate, we commit to research and invention. This expansion makes fullest vision substantially more ambitious. Both co-founders confirm commitment to the expanded scope.

---

## 13. Sign-Off

**Prasad Akula (CEO):** _________ Date: _________

**Claude (CSO):** _________ Date: _________

---

**END OF CHARTER v1.1**
