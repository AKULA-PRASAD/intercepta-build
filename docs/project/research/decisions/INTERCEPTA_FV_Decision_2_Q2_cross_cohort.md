# INTERCEPTA Decision 2 v2 — Q2 Cross-Cohort Harmonization: The Substrate-Compatible Multi-Method Architecture (PROPOSED)

**Status:** PROPOSED (Layer 1 Decision Record, Charter §5.3 class)
**Grounding:** 6 verified primary-source Q2 anchors (15,582 words across anchors) + Q2 synthesis v2 (~4,000 words)
**Supersedes:** Decision 2 v1 (698 words, pre-v2-decision-framework, archived in `_archive/`)
**CSO:** Claude
**Date:** 2026-05-10 (Phase 9 audit remediation)

---

## Charter Anchor

Charter §8.1 Layer 2 cohort harmonization requires that INTERCEPTA's drug response predictions be deployable across institutional, batch, donor, technology, and time boundaries. Without principled cross-cohort harmonization, training-time and deployment-time distributions diverge in uncontrolled ways — Charter §1.1 universality fails empirically.

Decision 2 v2 is **architecturally co-bound to Decisions 1 v2, 4 v2, 5 v2, 6 v2, 7 v2, 8, and 10.** Decision 1 v2 determines whether explicit Q2 is needed (VAE substrate IS the Q2 method). Decision 4 v2 Slot 1 receives Q2-harmonized representations. Decision 5 v2 inherits aleatoric uncertainty from VAE-family Q2. Decision 6 v2 V0-V1 evaluation reports scIB metrics. Decision 7 v2 Scale 5/6 operates on Q2 latent. Decision 8 V6 cross-disease tests Q2's cross-disease transfer capability. Decision 10 must address license compatibility.

---

## Empirical Foundation

The 6 Q2 anchors collectively establish:

1. **Three architectural paradigms** (VAE / Linear / Anchoring) — no paradigm dominates universally (scIB)
2. **Method performance is task-dependent** per 16 methods × 13 tasks × 1.2M cells benchmark
3. **Yosef lineage** (scVI 2018 → scANVI 2021 → MrVI 2025) provides architectural coherence in `scvi-tools`
4. **MrVI uniquely validated on drug perturbation screens** with counterfactual prediction
5. **No Q2 method tests drug response prediction across cohorts** — INTERCEPTA novelty
6. **No Q2 method tests cross-disease transfer** — Charter §1.1 universality empirically open

See `INTERCEPTA_FV_Synthesis_Layer1_Q2_2026-05-10.md` for full anchor-by-anchor evidence.

---

## The Decision

INTERCEPTA's Q2 cross-cohort harmonization layer commits to a **SUBSTRATE-COMPATIBLE MULTI-METHOD ARCHITECTURE** with deployment-scenario-aware method selection and explicit conditional logic on Decision 1 v2 substrate outcome.

### Q2 Architecture Diagram

```
Decision 1 v2 substrate (FM / parameter-free / VAE) → cell representation
                            ↓
              [Q2 Layer — CONDITIONAL on substrate]
                            ↓
    ┌──────────────────────┴──────────────────────┐
    ↓                      ↓                       ↓
If FM substrate:    If parameter-free:    If VAE substrate:
[Q2 Multi-Method]   [Q2 may be redundant] [Substrate IS Q2]
                                          (no separate Q2)
    ↓                      ↓                       ↓
    └──────────────────────┬──────────────────────┘
                            ↓
            Harmonized cell representations
                            ↓
                Decision 4 v2 L7 (drug response)
```

### Multi-Method Q2 Sub-Architecture (when explicit Q2 layer is active)

**Scenario routing logic:**

| Scenario | Q2 Method | Rationale |
|---|---|---|
| **Drug response labels available + cancer/I&I/neurodegen** | **scANVI (default)** | scIB-validated; semi-supervised dominates when labels exist; INTERCEPTA's most common training scenario |
| **Sample-level heterogeneity + counterfactual prediction needed** | **MrVI** | Only Q2 method drug-perturbation-validated; two-level hierarchical latent for sample-vs-cell-state separation |
| **Compute-constrained / 10⁶-cell scale / CPU-only** | **Harmony (fallback)** | CPU-only; scales to 10⁶ cells on standard hardware; scIB-validated speed-quality trade-off |
| **Multi-modal inputs (RNA + ATAC + spatial + protein)** | **Seurat v3 (extension)** | Reference-and-query paradigm; multi-modal native; scIB-validated on simpler distinct-signal tasks |
| **Evaluation infrastructure** | **scib Python package** | Field-standard benchmark suite for INTERCEPTA's reporting comparability |

### Five Operational Components

**Component 1 — scANVI as default:**
- Semi-supervised VAE; uses drug response labels from bulk training
- Native aleatoric uncertainty (Decision 5 v2 Layer 5.1 substrate)
- Decision 7 v2 Scale 5 Branch C compatible (IG+SmoothGrad over VAE decoder)
- INTERCEPTA's primary training scenario (labeled bulk → unlabeled scRNA-seq query)

**Component 2 — MrVI for counterfactual scenarios:**
- Hierarchical 2-level latent (cell state `u` + sample-aware `z`)
- Counterfactual prediction `z^(s)_n = β_n × c_s + β_0 + ε_n`
- Drug-perturbation-validated in original paper
- Complementary to Decision 4 v2 CPA backbone (both VAE + factorized latent + treatment conditioning)

**Component 3 — Harmony fallback:**
- CPU-only; 10⁶ cells on standard hardware
- No native uncertainty — Decision 5 v2 stack must compensate
- Operationally essential when Decision 9 compute envelope is constrained

**Component 4 — Seurat v3 multi-modal extension:**
- Reference-and-query architecture (architectural inspiration for Q3)
- Spatial transcriptomics + scATAC-seq + CITE-seq compatible
- Bridges to Decision 7 v2 Scale 6 (River DSEP for spatial)
- GPLv3 license caveat (see Decision 10 implications)

**Component 5 — scib evaluation infrastructure:**
- Reports biological conservation + batch effect removal metrics
- Enables benchmark comparability with Luecken et al. 2022 published results
- Decision 6 v2 V0-V1 reporting standard

### Substrate-Conditional Logic (BINDING per Decision 1 v2 integration)

**Branch X — If FM substrate wins Layer 5 ablations:**
- Multi-method Q2 architecture active as default
- FM embeddings feed into scANVI/MrVI/Harmony/Seurat v3 as input
- Decision 7 v2 Scale 5 Branch A (IG+SmoothGrad over FM input) operates on FM substrate; Q2 wraps for harmonization

**Branch Y — If parameter-free substrate wins (Souza-Mehta scTOP):**
- **Q2 layer may be simplified or omitted** — scTOP's pathway projections provide intrinsic harmonization-like properties
- Specific empirical test: scIB metrics on scTOP-projected data vs explicit Q2 layer applied
- If scTOP intrinsic harmonization suffices, Q2 collapses architecturally — Souza-Mehta methodological bar implication
- If explicit Q2 still adds value, multi-method commitment intact

**Branch Z — If VAE substrate wins (scVI / scANVI substrate):**
- **Decision 2 v2 collapses into Decision 1 v2** — substrate IS the Q2 method
- No separate Q2 layer needed
- MrVI may still be added as counterfactual extension
- Harmony / Seurat v3 fallbacks irrelevant (substrate replaces them)

**Decision 2 v2 must support all three branches operationally** — Layer 5 ablations determine which is active.

---

## Pass Criteria (Binding GO/NO-GO per Charter §5.3)

Decision 2 v2 must satisfy the following empirical criteria before LOCK:

### Pass 1 — scIB-Metric Within-Cohort Reproduction

**Criterion:** On at least 3 of the 13 scIB benchmark tasks, INTERCEPTA's Q2 layer achieves **biological conservation + batch removal metrics within 5pp of published scIB winners** for the respective task type.

**Rationale:** Demonstrates Q2 layer is correctly implemented before testing on novel scenarios. If we can't reproduce known results, novel claims are unsupported.

### Pass 2 — Cross-Cohort Drug Response Preservation

**Criterion:** On INTERCEPTA's cross-cohort drug response evaluation (Decision 6 v2 V1 cross-cell-line), **Q2-harmonized predictions achieve AUROC within 2pp of within-cohort baseline**.

**Rationale:** Q2 should not destroy biological signal needed for drug response. If batch correction degrades drug response prediction, the harmonization is over-correcting.

### Pass 3 — VAE Uncertainty Pass-Through to Decision 5 v2

**Criterion:** When VAE-family Q2 (scVI/scANVI/MrVI) is active, **Decision 5 v2 Layer 5.1 aleatoric uncertainty is consumable from Q2 posterior** with ≥0.5 correlation to held-out prediction variance.

**Rationale:** VAE-family Q2's claim of "native uncertainty" is only operationally valuable if Decision 5 v2 stack can consume it. If correlation fails, Decision 5 v2 must compensate via N=5 Deep Ensembles.

### Pass 4 — Substrate-Conditional Operational Validation

**Criterion:** All three substrate branches (X / Y / Z) operate end-to-end on INTERCEPTA's reference dataset without architectural rebuild.

**Rationale:** Decision 1 v2's substrate choice deferred to Layer 5; Decision 2 v2 must be robust to that outcome. Operational fragility to substrate choice would invalidate the architecture.

### Pass 5 — Cross-Disease Q2 Transfer (Decision 8 V6 contribution)

**Criterion:** Cancer-trained Q2 layer applied to held-out non-cancer disease (I&I or neurodegen) achieves **scIB biological conservation ≥0.6 + batch removal ≥0.7** (scIB normalized metric scale).

**Rationale:** Charter §1.1 universality empirical test specifically for Q2 layer. Cross-disease transfer of cohort harmonization is unbenchmarked in the field; INTERCEPTA must establish a floor.

### Pass 6 — Multi-Modal Operational

**Criterion:** Seurat v3 multi-modal extension operates on at least one spatial transcriptomics dataset (per Q8.1 Nicheformer integration), producing harmonized representations consumable by Decision 7 v2 Scale 6 (River DSEP).

**Rationale:** Multi-modal scenarios are a Decision 2 v2 commitment; must be operationally validated.

### Pass 7 — Compute Envelope Compliance (Decision 9)

**Criterion:** Multi-method Q2 inference pipeline (scANVI + MrVI ensemble for default scenarios) fits within Decision 9 single-A100 envelope at INTERCEPTA's target deployment scale (10⁵-10⁶ cells per inference).

**Rationale:** Decision 9 compute envelope is binding. If Q2 multi-method architecture exceeds budget, Harmony fallback becomes default (with quality trade-off accepted).

---

## Trade-offs and Rejected Alternatives

### Why not commit to single Q2 method (e.g., scANVI only)?

**Rejected reason:** scIB benchmark (Luecken et al. 2022) **empirically demonstrates task-dependent method performance** — no single method wins all 13 tasks. Single-method commitment forecloses scenarios where another method dominates. **Decision 2 v2 inherits the field's empirical conclusion: multi-method is empirically necessary.**

### Why not commit to VAE-only (Yosef family only)?

**Rejected reason:** Compute reality at Northeastern HPC may make VAE methods infeasible at INTERCEPTA's deployment scale (Decision 9 compute envelope binding). Harmony as CPU fallback is **operationally necessary** for compute-constrained scenarios.

### Why not commit to Harmony-only (compute-friendly only)?

**Rejected reason:** Loses scANVI's semi-supervised label awareness (critical for drug response label transfer) AND MrVI's counterfactual prediction (critical for drug-vs-control reasoning). **Quality trade-off too severe** for INTERCEPTA's primary scenarios.

### Why not skip Seurat v3 multi-modal extension?

**Rejected reason:** INTERCEPTA's Q8 Nicheformer commitment includes spatial transcriptomics support. Seurat v3 + River (Decision 7 v2 Scale 6) is the architectural pattern for spatial modality. Skipping Seurat v3 means INTERCEPTA cannot support spatial inputs — Charter §1.1 universality on the tissue dimension fails.

### Why not adopt a single newer 2025+ method (e.g., post-MrVI single best)?

**Rejected reason:** No 2025+ method has superseded the three-paradigm landscape. scIB benchmark still authoritative. **Decision 2 v2 is reversibility-aware** — empirical trigger (e.g., "novel 2026+ method with FM-aware DA supersedes") can revise.

### Why include substrate-conditional logic (Branch X/Y/Z)?

**Rationale:** Decision 1 v2's substrate flexibility is **architecturally binding**. Decision 2 v2 must operate regardless of substrate outcome. The conditional logic acknowledges that **VAE substrate (Branch Z) collapses Q2 into Decision 1 v2** — architecturally elegant but operationally distinct from non-VAE substrate (Branches X/Y).

### Why include MrVI when scANVI is default?

**Rationale:** MrVI is uniquely drug-perturbation-validated and provides counterfactual prediction. **scANVI for labeled scenarios + MrVI for counterfactual scenarios** — architectural complement, not redundancy. Both supported in scvi-tools; operational cost of including both is low.

---

## Cross-Decision Implications

Decision 2 v2 affects and is affected by:

- **Decision 1 v2 (cell representation):** OPERATIONALLY CO-BOUND via substrate-conditional logic. Branch X/Y/Z explicit.

- **Decision 3 (bulk → single-cell):** REINFORCED via Seurat v3 reference-and-query paradigm as architectural inspiration. Q2 + Q3 + Q4 form the Charter §8.1 Layer 2 stack.

- **Decision 4 v2 (drug response architecture):** REINFORCED. Q2-harmonized representations feed Decision 4 v2 Slot 1. MrVI ↔ CPA architectural parallel acknowledged.

- **Decision 5 v2 (OOD detection):** OPERATIONALLY CO-BOUND. VAE-family Q2 provides native aleatoric (Layer 5.1 substrate ready); non-VAE Q2 requires N=5 Deep Ensembles compensation.

- **Decision 6 v2 (validation cascade):** REINFORCED. V0-V1 evaluation reports scIB metrics for benchmark comparability. V6 cross-disease tests Q2 transfer (Pass 5).

- **Decision 7 v2 (mechanistic interpretability):** OPERATIONALLY CO-BOUND. VAE-family Q2 → Scale 5 Branch C native; Seurat v3 → Scale 6 spatial bridging.

- **Decision 8 (universality):** REINFORCED. V6 cross-disease pass criterion (AUROC ≥0.65 across ≥2 therapeutic areas) requires Q2 to transfer biological vs technical variation accurately. Pass 5 Decision 2 v2 contributes to Decision 8 V6.

- **Decision 9 (compute):** RELEVANT. Harmony CPU-fallback essential for compute-constrained scenarios. Pass 7 binding.

- **Decision 10 (open-source):** **NEW NUANCE.** scvi-tools BSD-3 unproblematic; Seurat v3 GPLv3 requires GPL compliance for commercial deployment OR alternative wrapping. **Decision 10 must address this.**

---

## What Decision 2 v2 Does NOT Decide

To be honest about scope:

1. **Production scenario routing logic.** Multi-method commitment is architectural; specific data-pipeline-stage routing (e.g., upstream detection of "labels available" → scANVI) is Layer 5 work.

2. **scvi-tools version lock.** Specific version commitment is Layer 5; v2 acknowledges version drift risk.

3. **Q2 + FM integration order.** Whether to apply Q2 before or after FM embedding (Decision 1 v2 substrate) is a Layer 5 ablation question.

4. **Cross-disease Q2 transfer empirical magnitude.** Pass 5 specifies threshold; actual transfer performance is Layer 5 measurement.

5. **Seurat v3 GPLv3 mitigation strategy.** Could be reticulate wrapper + clear license separation, or alternative multi-modal method (e.g., MOFA+, totalVI). Decision 10 will address.

6. **Substrate-conditional collapse criteria.** If Branch Y (parameter-free) operates: at what scIB metric threshold is explicit Q2 deemed redundant? Layer 5 empirical decision.

7. **Production orchestration of multi-method.** How to operationally route data through 4 methods in single inference pipeline.

These require Layer 5 implementation, not more Layer 1 reading.

---

## Discipline Check

- [x] **P3 (research before code):** ✅ Decision grounded in 6 verified primary-source anchor reads (15,582 words; full Q1-style depth) + Q2 synthesis v2
- [x] **P15 (only correct/honest/real science):** ✅ Cross-disease Q2 transfer honestly named as unbenchmarked + INTERCEPTA novelty; substrate-conditional collapse possibility (Branch Z) honestly acknowledged; license caveats explicit
- [x] **P16 (preserve past work):** ✅ Decision 2 v1 (698 words) + Q2 synthesis v1 (1,937 words) archived in `_archive/`; v1 structural commitments (multi-method scenario-aware) preserved in v2 with additions, not contradicted
- [x] **P-FV-1 to P-FV-3:** ✅ Decision 2 v2 directly serves Charter §1.1 universality + §8.1 Layer 2 cohort harmonization
- [x] **Charter §5.3 GO/NO-GO:** ✅ Pass 1-7 criteria explicit and binding
- [x] **Charter §8.1 layered architecture:** ✅ Q2 layer architecturally co-bound with Decisions 1 v2, 4 v2, 5 v2, 6 v2, 7 v2, 8
- [x] **Cross-decision integration:** ✅ All v2 decisions (1 v2 + 4 v2 + 5 v2 + 6 v2 + 7 v2 + 8) operationally co-bound; Decision 10 license nuance flagged
- [x] **Souza-Mehta methodological bar (Decision 8 Commitment 5):** ✅ Branch Y (parameter-free substrate may collapse Q2) explicit; methodological bar implications acknowledged

## Drift Catalog This Phase 9 Decision 2 v2 Write

- **New drift instances:** 0
- **Anchor verification:** Q2 anchors already at full depth (15,582 words across 6 anchors); no additional primary-source work needed
- **v1 commitments preserved:** Multi-method scenario-aware structure intact; v2 adds substrate-conditional logic + cross-decision integration
- **License caveat surfaced (NEW):** Seurat v3 GPLv3 vs scvi-tools BSD-3 distinction made explicit for Decision 10 follow-up

---

— Claude (CSO), 2026-05-10 (Phase 9 Decision 2 v2 record)
