# INTERCEPTA Decision 3 v2 — Q3 Bulk-to-Single-Cell Transfer: The Charter §1.1 Universality Bridge with Cross-Decision Identity (PROPOSED)

**Status:** PROPOSED (Layer 1 Decision Record, Charter §5.3 class)
**Grounding:** 7 verified primary-source Q3 anchors (6,681 words across anchors) + Q3 synthesis v2 (~4,500 words)
**Supersedes:** Decision 3 v1 (421 words, pre-v2-decision-framework, archived in `_archive/`)
**CSO:** Claude
**Date:** 2026-05-10 (Phase 9 audit remediation)

---

## Charter Anchor

Charter §8.1 Layer 2 bulk-to-scRNA bridge requires that INTERCEPTA's training-time bulk pharmacogenomic data (GDSC/CCLE, cancer-only) transfer to deployment-time single-cell scenarios. Charter §1.1 universality (U1: any disease; U3: 5+ disease categories) requires that this transfer extend beyond cancer to non-cancer diseases where bulk pharmacogenomic resources do not exist at scale.

Decision 3 v2 is **architecturally co-bound to Decisions 1 v2, 2 v2, 4 v2, 5 v2, 6 v2, 7 v2, and 8.** The most consequential cross-decision binding is **architectural identity:** Decision 3 v2's scRank component IS Decision 4 v2 Slot 4 graph-augmented module AND Decision 7 v2 Scale 4 GRN interpretability. Decision 3 v2's Beyondcell component IS Decision 7 v2 Scale 3 pathway interpretability. These are not redundant components — they are the same architectural primitives serving multiple roles.

Decision 8 V6 cross-disease pass criterion depends operationally on Decision 3 v2's scRank component for non-cancer scenarios. Without Decision 3 v2's scRank, Charter §1.1 universality V6 cannot be tested for non-cancer.

---

## Empirical Foundation

The 7 Q3 anchors collectively establish:

1. **Three operational paradigms** (Domain Adaptation: SCAD/scDEAL/scAdaDrug; GRN Perturbation: scRank; Signature Enrichment: Beyondcell) — complementary
2. **DA family progression** (scDEAL 2022 MMD → SCAD 2023 adversarial → scAdaDrug 2024 multi-source adaptive)
3. **Bulk training substrate** (GDSC 138-142 drugs × ~700 cell lines; CCLE 1,072 cell lines) — **cancer-only**
4. **No equivalent non-cancer pharmacogenomic resource** at scale exists
5. **scRank uniquely validated on non-cancer** (cardiovascular; depression)
6. **No Q3 method tests FM integration** — INTERCEPTA novelty
7. **scRank + Beyondcell serve double duty** as Q3 methods AND Q7 interpretability scales

See `INTERCEPTA_FV_Synthesis_Layer1_Q3_2026-05-10.md` for full anchor-by-anchor evidence.

---

## The Decision

INTERCEPTA's Q3 bulk-to-single-cell transfer layer commits to a **MULTI-PARADIGM SCENARIO-AWARE ARCHITECTURE** with explicit architectural identity recognition (scRank ↔ Decision 4 v2 Slot 4; Beyondcell ↔ Decision 7 v2 Scale 3) and chemCPA architecture surgery integration.

### Q3 Architecture Diagram

```
Bulk training data (GDSC + CCLE)
                            ↓
Decision 4 v2 Phase 1 — Bulk pretraining
                            ↓
Decision 4 v2 Phase 2 — Architecture surgery (chemCPA pattern)
                            ↓
Decision 4 v2 Phase 3 — Single-cell fine-tuning (sci-Plex)
                            ↓
[Q3 Paradigm routing based on scenario]
    ┌──────────────────────┬────────────────────┐
    ↓                      ↓                     ↓
Cancer + labels:    Cancer + target:      Non-cancer:
[scAdaDrug DA]      [scRank GRN]         [scRank GRN PRIMARY]
                                          [Beyondcell signature
                                           if signatures exist]
    ↓                      ↓                     ↓
    └──────────────────────┬────────────────────┘
                            ↓
        Quantitative + mechanism drug response prediction
                            ↓
                Decision 4 v2 Slot 6 — Patient aggregation
                            ↓
        Decision 5 v2 stack wraps for uncertainty + Decision 7 v2 stack provides interpretation
```

### Five Operational Components

**Component 1 — scAdaDrug-style multi-source adversarial DA (default cancer scenario):**
- Multi-source adaptive weighting (per-target sample contribution from multiple bulk sources)
- Shared encoder + adversarial gradient reversal
- Applied to FM-embedded inputs (Decision 1 v2 substrate) — novelty
- Quantitative IC50 prediction at single-cell level
- Training is GPU-heavy; inference is light

**Component 2 — scRank GRN perturbation propagation (cancer + non-cancer):**
- In silico drug-target perturbation propagated through cell-type-specific GRN
- **Operational without bulk pharmacogenomic training data**
- **The only viable Q3 mechanism for non-cancer scenarios**
- **Architectural identity:** IS Decision 4 v2 Slot 4 + Decision 7 v2 Scale 4

**Component 3 — Beyondcell signature enrichment (fast screening):**
- Beyondcell Score (BCS) per cell against pre-computed drug signatures (LINCS-derived)
- Operationally lightweight — no training required
- **Architectural identity:** IS Decision 7 v2 Scale 3 pathway interpretability

**Component 4 — Bulk training substrate (GDSC + CCLE):**
- GDSC: 138-142 anti-cancer drugs × ~700 cell lines (IC50/AUC at standardized concentrations)
- CCLE: 1,072 cancer cell lines (RNA-seq + WES + methylation + RPPA)
- LINCS Connectivity Map for broader chemical perturbation signatures
- Disease-specific scRNA-seq atlases for non-cancer scenarios

**Component 5 — chemCPA architecture surgery (training pipeline):**
- Phase 1: Bulk RNA HTS pretraining
- Phase 2: Architecture surgery between bulk and single-cell phases
- Phase 3: Single-cell fine-tuning
- Phase 4: Cross-disease fine-tuning (INTERCEPTA novelty)
- **Architectural identity:** This IS Decision 4 v2's Phase 1-3 training protocol

### Scenario Routing Logic

| Scenario | Primary Q3 Method | Secondary/Auxiliary |
|---|---|---|
| **Cancer + drug with GDSC label coverage** | scAdaDrug-FM | scRank (mechanism); Beyondcell (screening) |
| **Cancer + drug with known target** | scAdaDrug-FM (quantitative) | scRank (mechanism + interpretability) |
| **Non-cancer disease + drug with known target** | **scRank (PRIMARY)** | Beyondcell if disease signatures exist |
| **Drug repurposing screening (any disease)** | Beyondcell (PRIMARY) | scRank if targets known |
| **Combinatorial drug testing** | scAdaDrug-FM extension | Beyondcell-FM extension |

### Architectural Identity Recognition (BINDING — NEW IN V2)

**Identity #1:** scRank IS Decision 4 v2 Slot 4 (graph-augmented module)
- Both implement gene-gene graph + perturbation propagation
- Drug-target ontology serves as the graph for scRank
- Same architectural primitive at different framing levels

**Identity #2:** scRank IS Decision 7 v2 Scale 4 (GRN interpretability)
- GRN perturbation propagation natively produces gene-level attribution
- Cell-type-specific propagation enables cell-type-resolved interpretability

**Identity #3:** Beyondcell IS Decision 7 v2 Scale 3 (Pathway interpretability)
- BCS scores ARE pathway-level mechanism attributions
- Signature-based scoring IS pathway enrichment analysis

**Identity #4:** chemCPA architecture surgery IS Decision 3 v2's bulk → scRNA bridge operationalized
- Decision 4 v2 Phase 1-3 training protocol = Decision 3 v2 transfer mechanism
- Same answer to bulk-to-single-cell at different framings

**Operational implication:** INTERCEPTA's implementation has **fewer distinct components than the seven-decision count suggests** because architectural identities reduce redundancy. **3 Q3 methods + 6 L7 slots + 7 Q7 scales = NOT 16 distinct components.** Real component count is closer to 10-12 due to identity overlaps. **This is architectural efficiency.**

---

## Pass Criteria (Binding GO/NO-GO per Charter §5.3)

Decision 3 v2 must satisfy the following empirical criteria before LOCK:

### Pass 1 — scAdaDrug-FM Replicates Cancer Baseline

**Criterion:** On INTERCEPTA's cancer drug response evaluation (GDSC held-out cell lines), **scAdaDrug-FM achieves AUROC ≥ 0.85** matching or beating published scAdaDrug-on-raw-expression baseline.

**Rationale:** Validates FM-integration adds value rather than degrading performance. If FM-DA fails to match raw-expression-DA, the novelty hypothesis fails.

### Pass 2 — scRank Recovers Known Drug-Target Mechanism

**Criterion:** scRank applied to ≥ 5 well-characterized cancer drug-target pairs (e.g., trastuzumab → HER2; imatinib → BCR-ABL; ibrutinib → BTK; cetuximab → EGFR; vemurafenib → BRAF) **ranks the target gene in top-10 per drug**.

**Rationale:** Biological validity test. If scRank doesn't recover known mechanism, its non-cancer extension is not credible.

### Pass 3 — scRank Cross-Disease Transfer (Decision 8 V6 Critical)

**Criterion:** scRank applied to ≥ 2 non-cancer diseases (e.g., autoimmune + neurodegeneration) **identifies biologically plausible drug-responsive gene patterns** validated against published mechanism literature.

**Rationale:** **The single most consequential Decision 3 v2 test.** Charter §1.1 U3 (5+ disease categories) depends operationally on this. If scRank fails cross-disease transfer, INTERCEPTA's non-cancer claims are empirically unsupported.

### Pass 4 — Beyondcell Signature Database Coverage

**Criterion:** Beyondcell signature database covers ≥ 70% of drugs in INTERCEPTA's evaluation set for at least cancer + 1 non-cancer disease.

**Rationale:** Operational requirement. Without signature coverage, Beyondcell paradigm cannot run.

### Pass 5 — Multi-Paradigm Output Coherence

**Criterion:** For each drug-disease scenario, **at least 2 of 3 paradigms (scAdaDrug, scRank, Beyondcell) produce concordant predictions** (rank correlation ≥ 0.6) where all three are applicable.

**Rationale:** Cross-paradigm consistency is the falsifiability mechanism. If three paradigms disagree, INTERCEPTA cannot adjudicate which is correct — operational impasse.

### Pass 6 — chemCPA Architecture Surgery Operational

**Criterion:** Decision 4 v2 Phase 1-3 training protocol (= Decision 3 v2's bulk → scRNA bridge) completes end-to-end on INTERCEPTA's reference dataset without convergence failure.

**Rationale:** Decision 3 v2 ↔ Decision 4 v2 architectural identity must be operationally validated. If training fails, the identity claim is theoretical.

### Pass 7 — V6 Cross-Disease Drug Response (Decision 8 Binding)

**Criterion:** Per Decision 8 Commitment 3: **AUROC ≥ 0.65 on held-out disease spanning ≥ 2 therapeutic areas**, achieved primarily via scRank for non-cancer scenarios.

**Rationale:** Charter §1.1 universality empirical test. Decision 8 V6 pass criterion operationally depends on Decision 3 v2's scRank component.

---

## Trade-offs and Rejected Alternatives

### Why not single-method commitment (e.g., scAdaDrug only)?

**Rejected reason:** Fails for non-cancer diseases (no bulk training data). Single-method commitment forecloses Charter §1.1 U3 (5+ disease categories). **Multi-paradigm is empirically necessary** for universality.

### Why not DA-only (any DA family member)?

**Rejected reason:** Same non-cancer failure. All DA methods require bulk pharmacogenomic training data that doesn't exist for non-cancer at scale.

### Why not GRN-only (scRank only)?

**Rejected reason:** Loses quantitative IC50 prediction (DA family strength). scRank produces ranked mechanism scores but not direct dose-response. **For cancer scenarios with bulk labels, scAdaDrug is the more powerful method.**

### Why not signature-only (Beyondcell only)?

**Rejected reason:** Loses both quantitative DA capability AND mechanism trace. Beyondcell is operationally lightweight for screening but insufficient for clinical-grade drug response prediction.

### Why include FM integration when no Q3 method tests it?

**Rationale:** **INTERCEPTA's novelty contribution.** Layering Decision 1 v2 substrate on Q3 methods is the architectural integration the field has not yet benchmarked. Decision 4 v2 Slot 1 + chemCPA architecture surgery operationalize this integration.

### Why include architectural identity recognition (NEW)?

**Rationale:** Architectural efficiency. Without identity recognition, INTERCEPTA's system has redundant components (scRank as Q3 method + separate Slot 4 + separate Scale 4 = 3 components). With identity recognition, single scRank implementation serves three roles. **Reduces system complexity ~30%** while maintaining functional coverage.

---

## Cross-Decision Implications

Decision 3 v2 affects and is affected by:

- **Decision 1 v2 (cell representation):** OPERATIONALLY CO-BOUND. Q3 methods wrap Decision 1 v2 substrate; FM-integration is novelty contribution.

- **Decision 2 v2 (cross-cohort):** COMPLEMENTARY. Q3 (bulk → scRNA) operates before or in parallel with Q2 (scRNA cross-cohort). Together cover Charter §1.1 cross-resolution + cross-cohort dimensions.

- **Decision 4 v2 (drug response architecture):** DEEPLY CO-BOUND via three architectural identities. scRank = Slot 4; Beyondcell pattern = pathway-aware predictions; chemCPA architecture surgery = Decision 3 v2 bridge operationalized.

- **Decision 5 v2 (OOD detection):** OPERATIONALLY CO-BOUND. Q3 methods lack native uncertainty; Decision 5 v2 N=5 Deep Ensembles + conformal compensates.

- **Decision 6 v2 (validation cascade):** REINFORCED. V1 (cross-cell-line) → V3 (cell line → tumor) → V4 (cell line → PDX) all test Q3 transfer; V6 (cross-disease) tests scRank specifically.

- **Decision 7 v2 (mechanistic interpretability):** DEEPLY CO-BOUND via two architectural identities. scRank = Scale 4; Beyondcell = Scale 3. Q3 methods provide 3 of 7 Q7 scales for free.

- **Decision 8 (universality):** **CRITICAL DEPENDENCY.** V6 cross-disease pass criterion depends operationally on scRank for non-cancer scenarios. Decision 3 v2 ↔ Decision 8 are non-substitutable.

- **Decision 9 (compute):** RELEVANT. scAdaDrug training is GPU-heavy; scRank + Beyondcell inference is light. Total Q3 compute envelope dominated by training phase.

- **Decision 10 (open-source):** REINFORCED. No license blockers across Q3 anchor methods.

---

## What Decision 3 v2 Does NOT Decide

To be honest about scope:

1. **Specific DA loss formulation** (MMD vs adversarial vs Wasserstein) — Layer 5 ablation

2. **Drug-target ontology choice** for scRank GRN augmentation — DrugBank vs TWOSIDES vs compound-similarity, Layer 5

3. **Signature database choice** for Beyondcell — LINCS L1000 vs CMap vs CREEDS, Layer 5 ablation

4. **Multi-paradigm output fusion architecture** — how to combine scAdaDrug + scRank + Beyondcell outputs, Layer 5 work

5. **FM-Q3 integration order** — Q3 before or after FM substrate, Layer 5 ablation

6. **Production routing logic** — scenario detection → method selection, Layer 5 implementation

7. **scRank cell-type-specific GRN construction** — which GRN inference method (SCENIC vs GENIE3 vs CellOracle), Layer 5 ablation

8. **Cross-disease scRank fine-tuning protocol** — whether to retrain GRN per disease or use shared GRN with disease-specific weights, Layer 5 architecture work

These require Layer 5 implementation, not more Layer 1 reading.

---

## Discipline Check

- [x] **P3 (research before code):** ✅ Decision grounded in 7 verified primary-source anchor reads (6,681 words) + Q3 synthesis v2
- [x] **P15 (only correct/honest/real science):** ✅ Non-cancer Q3 universality gap honestly named as field-wide constraint; FM-integration novelty acknowledged as unbenchmarked; bulk training cancer bias preserved as binding constraint
- [x] **P16 (preserve past work):** ✅ Decision 3 v1 (421 words) + Q3 synthesis v1 (947 words) archived in `_archive/`; v1 structural commitments preserved in v2 with additions, not contradicted
- [x] **P-FV-1 to P-FV-3:** ✅ Decision 3 v2 directly serves Charter §1.1 universality (especially U3 5+ disease categories) + §8.1 Layer 2 bulk-to-scRNA bridge
- [x] **Charter §5.3 GO/NO-GO:** ✅ Pass 1-7 criteria explicit and binding
- [x] **Charter §8.1 layered architecture:** ✅ Q3 layer architecturally co-bound with Decisions 1 v2, 2 v2, 4 v2, 5 v2, 6 v2, 7 v2, 8
- [x] **Cross-decision integration:** ✅ All v2 decisions operationally co-bound; **four architectural identities explicit** (scRank = Slot 4 + Scale 4; Beyondcell = Scale 3; chemCPA surgery = Decision 3 v2 bridge)
- [x] **Souza-Mehta methodological bar (Decision 8 Commitment 5):** ✅ Parameter-free + signature-based architectural similarity acknowledged; methodological bar implications addressed

## Drift Catalog This Phase 9 Decision 3 v2 Write

- **New drift instances:** 0
- **v1 commitments preserved:** Multi-paradigm scenario-aware structure intact
- **v2 additions:** four architectural identities; chemCPA architecture surgery integration; Decision 8 V6 critical dependency; cross-decision double-duty efficiency
- **Architectural efficiency surfaced (NEW):** scRank + Beyondcell each serving multiple decision roles simultaneously — reduces system complexity ~30%

---

— Claude (CSO), 2026-05-10 (Phase 9 Decision 3 v2 record)
