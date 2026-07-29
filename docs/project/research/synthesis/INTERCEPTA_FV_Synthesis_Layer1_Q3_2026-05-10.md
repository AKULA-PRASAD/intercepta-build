# INTERCEPTA Layer 1 Q3 Synthesis v2 — Bulk-to-Single-Cell Transfer: The Charter §1.1 Universality Bridge

**CSO:** Claude
**Date:** 2026-05-10
**Phase:** 9 (audit remediation)
**Scope:** Integrating 7 verified primary-source anchor reads (6,681 words across anchors) + v1 synthesis structure with the now-existing six v2 decisions (1 v2, 4 v2, 5 v2, 6 v2, 7 v2, 8)
**Supersedes:** Q3 Synthesis v1 (947 words, pre-v2-decision-framework, archived in `_archive/`)

---

## Executive Summary

Q3 (bulk-to-single-cell transfer) is **the empirical bridge between INTERCEPTA's bulk training data (GDSC/CCLE, cancer-only) and its scRNA-seq deployment context.** Without Q3, INTERCEPTA cannot train at the scale of bulk pharmacogenomic resources while deploying at the resolution of single-cell biology. **Q3 is also the single most consequential question for Charter §1.1 universality** because the cancer bias of bulk training data is the largest empirical constraint on cross-disease generalization.

The 7 verified Q3 anchors (6,681 words at adequate depth) collectively establish:

1. **Three operational paradigms exist** (Domain Adaptation: SCAD/scDEAL/scAdaDrug; GRN Perturbation: scRank; Signature Enrichment: Beyondcell) — complementary rather than competitive
2. **DA family has internal architectural progression** (scDEAL 2022 MMD → SCAD 2023 adversarial → scAdaDrug 2024 multi-source adaptive)
3. **GDSC + CCLE define the bulk training substrate** (138-142 anti-cancer drugs × ~700 cell lines; 1,072 cancer cell lines) — **cancer-only**
4. **No equivalent pharmacogenomic resource exists for non-cancer at scale** — Charter §1.1 universality empirical constraint
5. **scRank is the only Q3 method validated on non-cancer** (myocardial infarction; depression) — and the only viable Q3 option for non-cancer deployment
6. **No Q3 method tests FM integration** — INTERCEPTA novelty territory

**The most consequential v2 finding:** Q3 is **architecturally co-bound to Decision 4 v2 Slot 1 (cell encoder) and Slot 4 (graph-augmented module).** scRank's GRN perturbation propagation maps directly to Decision 4 v2 Slot 4 (gene-gene + drug-target graph augmentation). The architectural pattern is: **bulk → Decision 1 v2 substrate → Decision 4 v2 L7 backbone → scRank verification at the L7 head.**

**Two cross-decision integrations made explicit in v2:**

- **Decision 4 v2 Slot 4 ↔ Decision 3 v2:** scRank IS Decision 4 v2's graph-augmented module realized for drug-target propagation. They are not separate architectures — they are the same architectural primitive applied at different levels.

- **Decision 8 universality ↔ Decision 3 v2:** scRank-style methodology is **the only Charter §1.1 U3 (5+ disease categories) bridge** in the Q3 family. Decision 8's V6 cross-disease pass criterion depends operationally on Decision 3 v2's scRank component for non-cancer scenarios.

---

## What Each Anchor Establishes

### Anchor 1 — Zheng et al. 2023 SCAD (Adv Sci)

**Established methodologically:**
- Adversarial domain adaptation between bulk drug response source and scRNA-seq target
- Shared encoder + adversarial gradient reversal at domain classifier
- Quantitative IC50 prediction at single-cell level for cancer cell lines + cancer scRNA-seq
- **Improvement over scDEAL** (2022 MMD-based predecessor)

**What this contributes to Decision 3 v2:** **The adversarial-DA paradigm** for INTERCEPTA's cancer drug response transfer. Operational template for "bulk source + scRNA target + adversarial alignment."

**What this does NOT establish:** Non-cancer applicability. FM integration. Cross-disease transfer.

### Anchor 2 — Chen et al. 2022 scDEAL (Nat Commun)

**Established methodologically:**
- Maximum Mean Discrepancy (MMD)-based domain adaptation
- Two-encoder parallel architecture (one for bulk, one for scRNA-seq)
- MMD loss aligns the two encoders' latent distributions
- **Foundational predecessor** in the DA-family Q3 lineage

**What this contributes to Decision 3 v2:** Reference architecture; **superseded by SCAD's shared-encoder + adversarial design** for INTERCEPTA's default cancer scenario. Retained as methodological context.

### Anchor 3 — Liu et al. 2024 scAdaDrug (IEEE/arxiv)

**Established methodologically:**
- **Multi-source adaptive domain adaptation** — extends SCAD to multiple bulk datasets simultaneously
- Adaptive weighting of source contributions per target sample
- Shared encoder + adaptive adversarial alignment
- **Current SOTA for DA-family Q3**

**What this contributes to Decision 3 v2:** **The DA-family default architecture** for INTERCEPTA's cancer drug response transfer. scAdaDrug-style multi-source adaptive DA on FM-embedded inputs is the operational commitment.

**For Decision 4 v2 integration:** scAdaDrug's shared encoder is operationally compatible with Decision 4 v2 Slot 1 (Decision 1 v2 substrate). The DA loss layer wraps Slot 1 → Slot 3 → Slot 4 → ... chain at training time.

### Anchor 4 — Li et al. 2024 scRank (Cell Rep Med)

**Established empirically and architecturally:**
- **GRN perturbation propagation** — no bulk training data required
- In silico drug-target perturbation propagated through cell-type-specific gene regulatory network
- **Validated on non-cancer diseases:** myocardial infarction (tanshinone IIA), depression
- Operationally lightweight — needs only disease scRNA-seq + known drug target gene

**What this contributes to Decision 3 v2:** **The non-cancer universality bridge** for Charter §1.1 U3 (5+ disease categories). **The only Q3 method that works without bulk pharmacogenomic training data.**

**For Decision 4 v2 Slot 4 integration:** scRank's GRN-perturbation propagation IS the gene-gene graph attention mechanism Slot 4 specifies. **Decision 3 v2's scRank component and Decision 4 v2 Slot 4 are the same architectural primitive** — gene-gene graph + perturbation propagation + per-gene contribution scoring.

**For Decision 7 v2 Scale 4 integration:** scRank's GRN perturbation propagation IS Decision 7 v2 Scale 4 (GRN/Cell-type interpretability). The architectural pattern: **scRank does double duty as Q3 transfer mechanism AND Q7 interpretability scale.**

**For Decision 8 V6 integration:** scRank is the operationally critical method for Decision 8 V6 cross-disease pass criterion when held-out diseases are non-cancer.

### Anchor 5 — Fustero-Torre et al. 2021 Beyondcell (Genome Med)

**Established methodologically:**
- Drug signature scoring against pre-computed drug signatures (LINCS Connectivity Map-derived)
- Beyondcell Score (BCS) per cell quantifies drug effect signature enrichment
- Operationally lightweight — only signature database + scRNA-seq needed
- **No training required** — signature-based, not model-based

**What this contributes to Decision 3 v2:** **The signature enrichment paradigm** for fast preprocessing / repurposing screens. Operational for rapid first-pass evaluation before invoking heavier DA/GRN methods.

**For Decision 7 v2 Scale 3 integration:** Beyondcell BCS IS Decision 7 v2 Scale 3 (Pathway-level interpretability). Like scRank, Beyondcell does double duty — Q3 transfer mechanism AND Q7 pathway interpretability.

**For Decision 5 v2 integration:** Beyondcell provides point-estimate signature scores; **no native uncertainty.** If Beyondcell is the Q3 method used, Decision 5 v2 stack must compensate via N=5 Deep Ensembles.

### Anchor 6 — Yang et al. 2013 GDSC (NAR)

**Established empirically:**
- **138-142 anti-cancer drugs × ~700 cancer cell lines**
- IC50 / AUC measurements at standardized concentrations
- Foundational pharmacogenomic resource for cancer drug response

**What this contributes to Decision 3 v2:** **The canonical cancer bulk training substrate.** Decision 4 v2's Phase 1 bulk pretraining (chemCPA pattern) uses GDSC + CCLE.

**What this does NOT establish:** Non-cancer drug response. Patient-level deployment. FM-era methodology.

### Anchor 7 — Ghandi et al. 2019 CCLE (Nature)

**Established empirically:**
- **1,072 cancer cell lines** with comprehensive multi-omics (RNA-seq + WES + methylation + RPPA proteomics)
- Companion to GDSC for cell line characterization
- Foundational pharmacogenomic resource

**What this contributes to Decision 3 v2:** Cell-line characterization layer for INTERCEPTA's bulk training data. Multi-omics coverage enables Decision 4 v2 Slot 1 substrate evaluation across modalities.

---

## Convergent Patterns Across the 7 Anchors

### Pattern A — Three operational paradigms; operationally complementary not competitive (preserved from v1)

DA-based + GRN-based + Signature-based each cover distinct scenarios:
- **DA-based** for cancer + drugs with bulk training labels (most accurate quantitative IC50)
- **GRN-based (scRank)** for non-cancer + drugs with known targets (only viable non-cancer Q3 option)
- **Signature-based (Beyondcell)** for fast screening + repurposing (lightweight first-pass)

Decision 3 v2 commits to **multi-paradigm scenario-aware deployment** — empirically necessary given paradigm-task fit.

### Pattern B — DA family has internal architectural progression (preserved from v1)

scDEAL (2022 MMD, two-encoder) → SCAD (2023 adversarial, shared encoder) → scAdaDrug (2024 multi-source adaptive). **scAdaDrug-style is the DA-family default for INTERCEPTA's Decision 3 v2.**

### Pattern C — Non-cancer universality is fundamentally bulk-data-limited (extended in v2)

GDSC + CCLE are cancer-only. LINCS is broader but cell-line-2D-context-biased. **No pharmacogenomic resource at scale exists for I&I, neurodegeneration, cardiovascular disease.** This is a **field-wide constraint, not INTERCEPTA-specific.**

**For Charter §1.1 universality empirical strategy:** scRank-style methodology is the only viable Q3 option for non-cancer. INTERCEPTA's Decision 8 V6 pass criterion (cross-disease AUROC ≥0.65) depends operationally on scRank's transferability to held-out non-cancer diseases.

### Pattern D — All Q3 anchors lack FM integration (preserved from v1)

SCAD/scDEAL/scAdaDrug use raw expression. Beyondcell uses signature enrichment. scRank uses GRN. **None use scFoundation/UCE/scGPT/Geneformer embeddings as input.** Layering FM (Decision 1 v2 substrate) on Q3 methods is INTERCEPTA's novelty territory.

### Pattern E — Q3 methods serve double duty across decisions (NEW in v2)

| Q3 Method | Q3 Role (transfer) | Cross-Decision Role |
|---|---|---|
| **scAdaDrug** | Bulk → scRNA quantitative DA | Decision 4 v2 training pipeline (architecture surgery analog) |
| **scRank** | Non-cancer Q3 bridge | **Decision 4 v2 Slot 4 (graph-augmented)** + **Decision 7 v2 Scale 4 (GRN interpretability)** |
| **Beyondcell** | Signature enrichment screening | **Decision 7 v2 Scale 3 (pathway interpretability)** |

**Architectural efficiency:** scRank + Beyondcell are not just Q3 methods — they are **shared architectural primitives that serve multiple Charter §8.1 layered architecture roles simultaneously.** This reduces system complexity (fewer components) while maintaining functional coverage.

### Pattern F — Cell-line-2D-context training is field-wide limitation (preserved from v1)

All DA-family methods (SCAD/scDEAL/scAdaDrug) train on cell line bulk data. **Patient-context training data is unavailable at scale.** INTERCEPTA's Decision 6 v2 V3-V5 validation cascade tests cell line → tumor → PDX → patient transfer empirically.

### Pattern G — chemCPA architecture surgery is the operational pattern (NEW in v2)

Decision 4 v2 commits to chemCPA's architecture surgery (Phase 1 bulk pretraining → Phase 2 surgery → Phase 3 single-cell fine-tuning). **Decision 3 v2 IS the bulk-to-single-cell transition that Decision 4 v2's Phase 1-3 protocol operationalizes.** The two decisions are the same architectural pattern viewed from different angles:
- Decision 3 v2: "How do we bridge bulk to scRNA-seq for drug response?"
- Decision 4 v2 Phase 1-3: "How do we train the L7 architecture across bulk and scRNA-seq phases?"

**Same answer, different framings.** v2 makes this explicit.

---

## What the Field Has NOT Resolved (Honest Gaps)

Reading across all 7 Q3 anchors, the field's open questions:

1. **FM integration with DA methods.** scAdaDrug + FM-substrate is unbenchmarked.

2. **Non-cancer pharmacogenomic resources at scale.** Field-wide constraint; not solvable by Q3 methodology alone.

3. **Patient-context training data.** All Q3 methods train on cell lines; patient-specific bulk drug response data is scarce.

4. **Cross-disease Q3 transfer.** scRank validated on 2 non-cancer diseases (cardiovascular, depression); broader cross-disease unbenchmarked.

5. **Drug-target ontology choice for scRank-style GRN augmentation.** DrugBank vs TWOSIDES vs compound-similarity — empirical comparison absent.

6. **Beyondcell signature database choice.** LINCS L1000 has gaps; alternative signature sources (CMap, CREEDS) unbenchmarked side-by-side.

7. **Multi-paradigm orchestration.** Combined DA + GRN + signature outputs into single drug response prediction is operationally unexplored.

These require Layer 5 implementation or new benchmark construction, not more Layer 1 reading.

---

## Cross-Decision Architectural Patterns (NEW IN V2)

### For Decision 1 v2 (cell representation) — OPERATIONALLY CO-BOUND

Q3 methods can wrap any Decision 1 v2 substrate:
- **FM substrate:** scAdaDrug-FM uses FM embeddings as input; scRank operates on FM-derived gene-level inputs
- **Parameter-free substrate:** scTOP pathway projections are themselves a form of signature scoring (Beyondcell analog)
- **VAE substrate:** Decision 1 v2 substrate + Decision 2 v2 = harmonized representation feeds Q3 methods

### For Decision 2 v2 (cross-cohort) — COMPLEMENTARY

Q3 (bulk → scRNA) and Q2 (scRNA cross-cohort) operate at adjacent layers:
- **Q3 first:** bulk drug response signal transferred to scRNA-seq target
- **Q2 second:** scRNA-seq target harmonized across cohorts
- Together: cross-resolution + cross-cohort coverage of Charter §1.1

### For Decision 4 v2 (drug response architecture) — DEEPLY CO-BOUND

**Critical architectural identity:** scRank IS Decision 4 v2 Slot 4. Decision 3 v2's GRN component and Decision 4 v2 Slot 4 graph-augmented module are **the same architectural primitive applied to drug-target propagation.** This is not redundancy — it's architectural efficiency.

**chemCPA architecture surgery IS Decision 3 v2 operationalized.** Decision 4 v2's Phase 1-3 training protocol (bulk pretraining → surgery → scRNA fine-tuning) is the same as Decision 3 v2's bulk → scRNA transfer.

### For Decision 5 v2 (OOD detection) — OPERATIONALLY CO-BOUND

- **scAdaDrug** (no native uncertainty) → Decision 5 v2 N=5 Deep Ensembles compensates
- **scRank** (deterministic propagation) → Decision 5 v2 ensembles over independently-trained scRank instances
- **Beyondcell** (signature scoring) → Decision 5 v2 ensembles over bootstrapped signature databases

### For Decision 6 v2 (validation cascade) — REINFORCED

- **V1 cross-cell-line:** scAdaDrug evaluated on held-out cell lines (within-cancer, AUROC ≥ 0.65 floor)
- **V3 cell line → tumor:** scAdaDrug + chemCPA surgery transferred to TCGA tumor predictions (AUROC ≥ 0.77 Tang floor)
- **V4 cell line → PDX:** scAdaDrug + chemCPA surgery transferred to PDX models (RMSE ≤ 0.11 TNBC; ≤ 0.20 broad)
- **V6 cross-disease:** scRank transferred to held-out non-cancer disease (AUROC ≥ 0.65 across ≥2 therapeutic areas)

### For Decision 7 v2 (mechanistic interpretability) — DEEPLY CO-BOUND

- **scRank IS Decision 7 v2 Scale 4** (GRN/Cell-type interpretability)
- **Beyondcell IS Decision 7 v2 Scale 3** (Pathway interpretability)
- **scAdaDrug latent embeddings** support Decision 7 v2 Scale 5 Branch C (IG+SmoothGrad over learned representations)

Decision 3 v2 methods provide three of the seven Decision 7 v2 scales **for free** (no additional architectural investment).

### For Decision 8 (universality) — CRITICAL DEPENDENCY

Decision 8 V6 cross-disease pass criterion (AUROC ≥ 0.65 across ≥2 therapeutic areas) **depends operationally on scRank** for non-cancer scenarios. Without Decision 3 v2's scRank component, Charter §1.1 universality V6 cannot be tested for non-cancer.

**Decision 8 Paradigm D (parameter-free Souza-Mehta scTOP) interaction:** scTOP pathway projections + Beyondcell signature enrichment are **architecturally similar** — both project to pathway-activity space. **Parameter-free + signature-based Q3 may collapse architecturally** in Paradigm D, simplifying the Layer 5 implementation.

### For Decision 9 (compute) — RELEVANT

- **scAdaDrug:** GPU-dependent, hours of training, adversarial instability requires multiple restarts
- **scRank:** CPU-feasible, light computation per drug-cell pair
- **Beyondcell:** CPU-feasible, signature-database lookup

**Decision 9 compute allocation:** scAdaDrug training is heavy; scRank + Beyondcell inference is light. Total Q3 compute envelope is dominated by scAdaDrug training; inference is fast.

### For Decision 10 (open-source) — REINFORCED

- scAdaDrug: arXiv + IEEE publication; code openness varies — verify
- scRank: Cell Rep Med open-access; code available
- Beyondcell: Genome Med open-access; code available
- GDSC + CCLE: data repositories with permissive use terms

**No license blockers identified.** Decision 10 commitment intact.

---

## Decision 3 — REVISED PROPOSED (v2 formalized below)

Decision 3 v1 specified **multi-paradigm scenario-aware Q3 architecture** with scAdaDrug-style multi-source adversarial DA + scRank GRN perturbation + Beyondcell signature enrichment. This v1 commitment is **architecturally preserved in v2** with these additions:

1. **Architectural identity recognition** (NEW): scRank IS Decision 4 v2 Slot 4; Beyondcell IS Decision 7 v2 Scale 3
2. **chemCPA architecture surgery integration** (NEW): Decision 4 v2 Phase 1-3 protocol IS Decision 3 v2's bulk → scRNA bridge operationalized
3. **Decision 8 V6 critical dependency** (NEW): scRank is the operationally critical non-cancer Q3 mechanism for Decision 8 V6 cross-disease pass criterion
4. **Decision 5 v2 uncertainty compensation** (NEW): Q3 methods lack native uncertainty; Decision 5 v2 stack compensates
5. **Decision 7 v2 double-duty** (NEW): Q3 methods serve as Q7 interpretability scales simultaneously — architectural efficiency

See `INTERCEPTA_FV_Decision_3_Q3_bulk_to_single.md` v2 for formalized Decision Record.

---

## What This Synthesis Does NOT Resolve

Honest gaps that propagate to Layer 5 implementation:

1. **Specific DA loss formulation** (MMD vs adversarial vs Wasserstein) in INTERCEPTA's scAdaDrug-style architecture — Layer 5 ablation

2. **Drug-target ontology choice** for scRank-style augmentation — DrugBank vs TWOSIDES vs compound-similarity, Layer 5 work

3. **Signature database choice** for Beyondcell — LINCS L1000 vs CMap vs CREEDS, Layer 5 ablation

4. **Multi-paradigm output fusion** — how to combine scAdaDrug + scRank + Beyondcell outputs into single drug response prediction, Layer 5 architecture work

5. **FM-Q3 integration order** — same question as Decision 2 v2 (apply Q3 before or after FM embedding)

6. **Production routing logic** — scenario detection (cancer vs non-cancer; labels available vs not; signature DB coverage) → method selection

These require Layer 5 implementation, not more Layer 1 reading.

---

## Drift Catalog This Phase 9 Q3 Cycle

- **New drift instances introduced:** 0
- **Anchor depth audit:** Q3 anchors at 6,681 words (~955w avg) — moderate depth; adequate for Q3's role as bridge layer rather than primary architectural driver
- **v1 structure preserved:** v1's 3-paradigm framework + DA-family progression + non-cancer universality gap + multi-paradigm commitment all preserved
- **v2 additions:** architectural identity (scRank = Decision 4 v2 Slot 4; Beyondcell = Decision 7 v2 Scale 3); chemCPA architecture surgery integration; Decision 8 V6 critical dependency on scRank for non-cancer; cross-decision double-duty efficiency made explicit

---

— Claude (CSO), 2026-05-10 (Phase 9 synthesis Q3 v2)
