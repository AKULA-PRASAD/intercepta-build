# INTERCEPTA Phase 2 Closeout — Q4 Drug Response Architecture: Synthesis v2 + Decision 4 v2

**Date:** 2026-05-10
**CSO:** Claude
**Phase:** 2 of audit remediation
**Scope:** scGen deepening + chemCPA new anchor + CPA/GEARS Decision 4 v2 integration + Q4 synthesis v2 + Decision 4 v2 (modular 6-slot L7 architecture with binding pass criteria)

---

## Phase 2 Deliverables

### 1. scGen Deepening (1,248 words added)

| Anchor | Before (audit-flagged) | After (Phase 2 standard) | Δ |
|---|---|---|---|
| scGen (Q4.6 foundational) | 497w | **1,745w** | +1,248w |

Specific items now properly captured per primary-source verification:
- Full author affiliations (Lotfollahi, Wolf, Theis — Helmholtz Munich)
- Specific funding sources (BMBF + Helmholtz Association + CZI + Joachim Herz)
- **Quantitative result: R² = 0.954 average across 6 held-out cell types** on IFN-β stimulation
- Dataset specifics: Kang et al. PBMCs (16,893 cells, 7 cell types, 2,437 IFN-β-stimulated)
- ISG15 distribution capture (mean + variance, not just mean)
- Cross-species LPS prediction methodology (δ_LPS = mouseLPS − mousecontrol)
- MMD regularization mechanism explained
- Mode collapse risk from Diversity-by-Design 2025 critique acknowledged
- scvi-tools BSD-3 license verified

### 2. chemCPA Added as Q4 Anchor 7 (NEW — 2,035 words)

**Rationale for new anchor:** chemCPA is the architectural slot for FM-derived chemical embeddings in Decision 4 v2. CPA's perturbation dictionary is limited to compounds seen during training; chemCPA replaces this with a 3-component perturbation network (G molecule encoder + M perturbation encoder + S dosage scaler) that takes any pretrained chemical embedding. This is the drug-side analog of Decision 1 v2's cell-substrate flexibility.

Primary-source verification:
- Hetzel L, Böhm S, Kilbertus N, Günnemann S, Lotfollahi M, Theis FJ — NeurIPS 2022, arXiv 2204.13545
- TUM + Helmholtz Munich institutional credibility
- 9 held-out compounds (HDAC, Aurora kinase, HSP90, CDK MoA classes) on sci-Plex3 evaluation
- Architecture surgery for bulk-to-single-cell transfer learning
- theislab/chemCPA GitHub with multiple molecular embedding implementations

### 3. CPA + GEARS Decision 4 v2 Integration

CPA (Q4.4) and GEARS (Q4.5) had Phase 1 grounding (~900w each) but lacked integration with the v2 decision framework. Added Decision 4 v2 architectural integration sections:

**CPA (943w → 1,208w):** Added integration section bridging to chemCPA, Decision 1 v2 substrate flexibility, Decision 5 v2 ensembleability, Decision 6 v2 pass criteria, mode collapse mitigation requirement.

**GEARS (843w → 1,216w):** Added integration section detailing graph-augmentation role, chemCPA architectural fusion for drug perturbations, V6 cross-disease applicability via substrate-agnostic biological priors, mode collapse risk.

### 4. Q4 Anchor Set Final State (7 anchors, 8,512 words)

| Anchor | Words | Quality | Architectural Role |
|---|---|---|---|
| Srivatsan 2020 sci-Plex (Q4.1) | 836 | Adequate | Training/evaluation substrate |
| Manica 2019 PaccMann (Q4.2) | 795 | Adequate | Bulk-level attention DRP reference |
| Liu 2020 DeepCDR (Q4.3) | 677 | Adequate | GCN-based DRP reference |
| Lotfollahi 2023 CPA (Q4.4) | **1,208** | Standard | **Compositional VAE backbone (driver)** |
| Roohani 2024 GEARS (Q4.5) | **1,216** | Standard | **Graph-augmented prediction (driver)** |
| Lotfollahi 2019 scGen (Q4.6) | **1,745** | Standard | **Foundational architectural primitive (driver)** |
| Hetzel 2022 chemCPA (Q4.7) | **2,035** | Standard | **Modular molecular embedding for unseen drugs (driver, NEW)** |

**Triage discipline applied (consistent with Q5):**
- Architectural drivers (CPA, GEARS, scGen, chemCPA): 1,208-2,035w
- Supporting references (sci-Plex, PaccMann, DeepCDR): 677-836w
- Average per anchor: 1,216 words
- Foundational ML/methodology papers kept at moderate depth; INTERCEPTA architectural drivers at full depth

### 5. Q4 Synthesis v2 (2,647 words)

`/mnt/user-data/outputs/layer_1/synthesis/INTERCEPTA_FV_Synthesis_Layer1_Q4_2026-05-10.md`

Supersedes v1 (455 words, archived). Structure:
- Executive summary with 7 key findings + architectural fusion thesis
- Anchor-by-anchor synthesis (7 anchors)
- 7 convergent patterns (A through G) including the unresolved cross-disease V6 gap
- 7 honest field gaps that propagate to Layer 5
- Cross-decision implications for Decisions 1 v2, 2, 3, 5 v2, 6 v2, 7, 8, 9, 10
- Decision 4 v2 architecture summary (6-slot modular L7 engine)

### 6. Decision 4 v2 Record (2,269 words)

`/mnt/user-data/outputs/layer_1/decisions/INTERCEPTA_FV_Decision_4_Q4_drug_response.md`

Supersedes v1 (252 words, archived). **MODULAR L7 ARCHITECTURE** with six binding slots:

| Slot | Component | Decision Family | Layer 5 ablation |
|---|---|---|---|
| 1 | Cell encoder | Decision 1 v2 substrate (scFoundation default; scTOP/scVI/PCA baselines) | YES |
| 2 | Drug molecule encoder G | chemCPA: chem-FM candidates (MoLFormer/ChemBERTa/Uni-Mol) + RDKit baseline | YES |
| 3 | Perturbation network M + S | chemCPA perturbation network | Architecture fixed |
| 4 | Graph-augmented module | GEARS: gene-gene + GO + drug-target ontology | Ontology choice YES |
| 5 | Mode collapse mitigation | Diversity loss default; energy-based + mixture-of-experts alternatives | YES |
| 6 | Patient-level aggregation | PaSCient-style attention default; mean/max/weighted alternatives | YES |

**Architecture surgery protocol (chemCPA pattern):**
- Phase 1: Bulk RNA HTS pretraining (LINCS L1000)
- Phase 2: Architecture surgery between bulk and single-cell phases
- Phase 3: Single-cell fine-tuning (sci-Plex3)
- Phase 4: Cross-disease fine-tuning (INTERCEPTA novelty)

**Pass Criteria (binding GO/NO-GO):**
1. V0 scGen reproduction: R² ≥ 0.90 on Kang IFN-β PBMCs
2. V0/V1 chemCPA-style unseen drug evaluation: above chemCPA RDKit/GNN baseline floor
3. V3 cell line → tumor: AUROC ≥ 0.77 (Tang 2022 floor)
4. V4 cell line → PDX: RMSE ≤ 0.11 TNBC; ≤ 0.20 broad (Tang 2022 + Kim 2020)
5. V5 calibration: ECE ≤ 0.05 (Decision 5 v2 Pass 3)
6. V6 cross-disease: AUROC ≥ 0.65 across ≥2 therapeutic areas (Decision 8 Commitment 3)
7. Mode collapse mitigation: ≥50% training-data prediction diversity preserved

---

## Critical Finding from Phase 2: The Architectural Fusion Thesis

The single most important deliverable of Phase 2 is the **modular L7 architecture** that fuses multiple Q4 anchor paradigms.

Prior to Phase 2, Decision 4 v1 specified "CPA + GEARS + FM-derived encoders" without architectural specifics. The v2 makes the integration explicit:

- **CPA's compositional VAE** = backbone
- **chemCPA's 3-component perturbation network** = drug-encoder side (Slots 2-3)
- **GEARS's graph-attention** = biological prior signal (Slot 4)
- **Decision 1 v2 substrate flexibility** = cell-encoder side (Slot 1)
- **Mode collapse mitigation** = architectural requirement, not optional (Slot 5)
- **PaSCient-style patient aggregation** = deployment unit (Slot 6)

This is **the architectural fusion no single Q4 anchor specifies** — it is INTERCEPTA's contribution to assemble. Decision 4 v2 makes the assembly principled rather than ad-hoc, with explicit slots that survive Layer 5 ablations.

**The cross-question coherence:** Decision 4 v2 simultaneously operationalizes:
- Decision 1 v2's substrate flexibility (Slot 1)
- Decision 5 v2's N=5 ensembleability requirement (modular L7 head)
- Decision 6 v2's V0-V6 pass criteria (Pass 1-6)
- Decision 8's 4-paradigm framework (Slot 1 + Slot 6 compatible with all paradigms)

**This is what audit-driven CSO discipline produces:** an architecture that is empirically grounded in 7 verified anchors AND operationally coherent across 4 previously-closed decisions. The v1 specified "CPA + GEARS + FM" as a slogan; the v2 specifies the assembly.

---

## What Phase 2 Does NOT Close

### Q7 Synthesis + Decision 7 v2

Still pending Phase 5. Q7 (mechanistic interpretability) synthesis at 340w; Decision 7 at 142w. Needs first-author attributions + deeper integration with Decision 4 v2's Slot 4 (graph attention) interpretability + Decision 1 v2's substrate-dependent interpretability (gene attribution if parameter-free; spectral analysis if FM).

### Q9/Q10 Reclassification

Both still have 0 paper anchors. Phase 7 work — requires CEO consent on Operational Decision taxonomy.

### Layer 5 Implementation

Cannot be executed autonomously per Charter §8. All seven Decision 4 v2 pass criteria require HPC empirical work.

---

## Cumulative State After Phase 2

### Layer 1 Word Count Progression

| Phase | Cumulative Layer 1 words |
|---|---|
| Pre-audit | 73,889 |
| Phase 1 (errata) | +14,500 net → 88,402 |
| Phase 6 (Q8 + Decision 1 v2) | +9,300 net |
| Phase 3 (Q5 deepening + synthesis + Decision 5 v2) | +9,300 net |
| Phase 4 (Q6 deepening + synthesis + Decision 6 v2) | +7,000 net |
| **Phase 2 (Q4 deepening + chemCPA new anchor + synthesis + Decision 4 v2)** | **+8,100 net** |
| **Total now** | **112,855** |

### Per-Question State

| Q | Anchors | Synthesis | Decision | Status |
|---|---|---|---|---|
| Q1 | 8 (~17K words) | 3,910w | 2,709w v1 + 1,873w v2 REVISED | **CLOSED** |
| Q2 | 6 (~15.5K words) | 1,937w | 698w | Defensible PROPOSED |
| Q3 | 7 (~6.7K words) | 947w | 421w | Defensible PROPOSED |
| **Q4** | **7 (8,512w) — added chemCPA** | **2,647w v2** | **2,269w v2** | **CLOSED Phase 2** |
| Q5 | 6 (8,486w) | 2,773w v2 | 2,066w v2 | **CLOSED Phase 3** |
| Q6 | 4 (5,131w) | 2,814w v2 | 2,807w v2 | **CLOSED Phase 4** |
| Q7 | 4 | 340w | 142w | Awaits Phase 5 |
| Q8 | 5 (~10.2K words) | 2,482w | 1,838w | **CLOSED Phase 6** |
| Q9 | 0 paper anchors | 233w | 147w | Awaits Phase 7 reclassification |
| Q10 | 0 paper anchors | 227w | 136w | Awaits Phase 7 reclassification |

### Decisions Status

| Decision | Status |
|---|---|
| Decision 1 v1 | Preserved per P16; superseded operationally by v2 |
| Decision 1 v2 | REVISION PROPOSED (Phase 6) |
| Decision 2 | PROPOSED (defensible) |
| Decision 3 | PROPOSED (defensible) |
| **Decision 4 v2** | **PROPOSED (Phase 2 — rigorous)** |
| Decision 5 v2 | PROPOSED (Phase 3 — rigorous) |
| Decision 6 v2 | PROPOSED (Phase 4 — rigorous) |
| Decision 7 | PROPOSED (thin — awaits Phase 5) |
| Decision 8 | PROPOSED (Phase 6 — rigorous) |
| Decision 9 | PROPOSED (CSO operational, awaits Phase 7 reclassification) |
| Decision 10 | PROPOSED (CSO operational, awaits Phase 7 reclassification) |

**FIVE DECISIONS now PROPOSED at rigorous Layer 1 standard:** 1 v2, 4 v2, 5 v2, 6 v2, 8.
These five are **architecturally coherent** — they reference each other consistently and are ready for CEO LOCK consideration as a coherent set.

---

## Drift Catalog Update

Cumulative drift: **31 instances** (unchanged from Phase 4; no new drift in Phase 2)

**Phase 2 resolved:**
- Q4 anchor depth gaps (scGen 497→1745w deepening; chemCPA new at 2035w; CPA + GEARS integration sections added)
- Q4 synthesis thinness (455w → 2647w)
- Decision 4 v1 thinness (252w → 2269w)
- Implicit Decision 4 v1 vs Decision 1 v2 inconsistency resolved via Slot 1 substrate-flexibility commitment
- Decision 4 architectural fusion thesis made explicit (was previously slogan-level)

**New drift introduced in Phase 2:** ZERO. Every claim primary-source verified before integration; chemCPA's quantitative claims (3-component architecture, 9 held-out compounds, 4 MoA classes) verified via NeurIPS proceedings + CPA paper §4 + theislab GitHub; scGen's R² = 0.954 verified via bioRxiv Figure 2d.

---

## CSO Discipline Check for Phase 2

- [x] **P3 (research before code):** ✅ scGen + chemCPA primary-source verified before writing; CPA + GEARS extant grounding preserved + integration sections added
- [x] **P15 (only correct/honest/real science):** ✅ Mode collapse risk explicitly named as binding architectural requirement; cross-disease V6 honestly named as INTERCEPTA novelty; chemCPA's scope (sci-Plex3 only, 4 MoA classes) honestly described
- [x] **P16 (preserve past work):** ✅ Q4 synthesis v1 + Decision 4 v1 archived in `_archive/`; v2 supersedes operationally
- [x] **P-FV-1 to P-FV-3:** ✅ Decision 4 v2 directly serves Charter §1.1 + §8.1 (multi-method drug response prediction)
- [x] **Charter §5.3 GO/NO-GO:** ✅ Pass 1-7 criteria explicit and binding
- [x] **Charter §8.1 layered architecture:** ✅ 6-slot modular design instantiates Charter §8.1 Layer 2 specification
- [x] **Cross-decision integration:** ✅ Decisions 1 v2 + 5 v2 + 6 v2 + 8 all operationally co-bound via Slot architecture
- [x] **Drift catalog watch:** 31 cumulative; zero new drift in Phase 2
- [x] **Compaction summary verification:** State verified on disk before proceeding
- [x] **Souza & Mehta methodological bar (Decision 8 Commitment 5):** ✅ V3 floor binding Decision 4 v2 to clear simpler pathway methodology

---

## Next Phase Options

Remaining audit phases:

- **Phase 5:** Q7 deepening + synthesis + Decision 7 v2 (mechanistic interpretability; first-author attributions + integration with Decision 4 v2 Slot 4 graph attention + Decision 1 v2 substrate-dependent interpretability)
- **Phase 7:** Q9/Q10 reclassification as Operational Decisions (cannot do autonomously — needs CEO consent)
- **Phase 8:** Rebuild Layers 2-4 with corrected Layer 1 foundations (if needed)

### CSO Recommendation for Phase Sequencing

**Recommended next: Phase 5 (Q7 mechanistic interpretability + Decision 7 v2).**

Reasoning:
1. **Q7 closes the Charter §1.3 falsifiability requirement** — drug response predictions must be mechanistically interpretable for clinical adoption
2. **Decision 4 v2 just specified GEARS-style graph attention (Slot 4)** as a key interpretability mechanism — Decision 7 v2 should integrate this while operationally fresh
3. **Decision 1 v2's substrate flexibility** affects Decision 7 (spectral analysis if FM; gene attribution if parameter-free) — must be integrated coherently
4. **Q7 is the last paper-anchor question requiring deepening** before Phase 7 reclassification can begin

Then **Phase 7 (Q9 + Q10 reclassification with CEO)** — completes the audit. Q9 (compute) and Q10 (open-source) are operational decisions, not paper-anchored research questions; require CEO consent on the taxonomy.

Then **Phase 8 (Layer 2-4 rebuild) only if needed** — Layer 5 implementation may obviate Layer 2-4 work.

---

— Claude (CSO), 2026-05-10 (Phase 2 closeout)
