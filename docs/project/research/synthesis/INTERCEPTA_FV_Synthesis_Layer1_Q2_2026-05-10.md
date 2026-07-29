# INTERCEPTA Layer 1 Q2 Synthesis v2 — Cross-Cohort Harmonization: The Substrate-Compatible Layer

**CSO:** Claude
**Date:** 2026-05-10
**Phase:** 9 (audit remediation)
**Scope:** Integrating 6 verified primary-source anchor reads (15,582 words across anchors) + v1 synthesis structure with the now-existing six v2 decisions (1 v2, 4 v2, 5 v2, 6 v2, 7 v2, 8)
**Supersedes:** Q2 Synthesis v1 (1,937 words, pre-v2-decision-framework, archived in `_archive/`)

---

## Executive Summary

Q2 (cross-cohort harmonization) is **the integration substrate that enables INTERCEPTA's drug response predictions to be deployed across institutional, batch, donor, technology, and time boundaries.** Without principled cross-cohort harmonization, INTERCEPTA's training-time and deployment-time data distributions diverge in uncontrolled ways — Charter §1.1 universality fails empirically not because the models can't generalize, but because we can't distinguish biological variation from technical batch effects.

The 6 verified Q2 anchors (15,582 words at full depth — comparable to Q1's 17K and exceeding Q5's 8,486w) collectively establish:

1. **Three architectural paradigms exist** (Deep-generative VAE family scVI/scANVI/MrVI; Linear correction Harmony; Anchoring-based Seurat v3) — no paradigm dominates universally
2. **Method performance is task-dependent** per scIB benchmark (Luecken et al. 2022; 16 methods × 13 tasks × 1.2M cells)
3. **The Yosef lab maintains a 7-year continuous research lineage** (scVI 2018 → scANVI 2021 → MrVI 2025) where capabilities accumulate without invalidating predecessors
4. **MrVI is the only Q2 method explicitly validated on drug perturbation screens** with counterfactual prediction (`z^(s)_n = β_n × c_s + β_0 + ε_n`)
5. **No Q2 method tests drug response prediction across cohorts** — this is INTERCEPTA's novelty contribution
6. **No Q2 method tests cross-disease transfer** — Charter §1.1 universality is empirically open

**The most consequential v2 finding:** Q2 is **substrate-compatible** with Decision 1 v2's substrate flexibility commitment. Whether INTERCEPTA's Layer 5 ablations select FM substrate (scFoundation/UCE/scGPT/Geneformer), parameter-free substrate (Souza-Mehta scTOP), or VAE substrate (scVI/scANVI), the Q2 layer wraps the cell representation without architectural conflict. **scANVI as default + MrVI for counterfactual + Harmony for compute-constrained + Seurat v3 for multi-modal** remains the operational commitment, now made cross-decision coherent.

**Two cross-decision tensions resolved in v2:**

- **Decision 1 v2 ↔ Decision 2 v2:** If Decision 1 v2 selects scVI/scANVI as substrate (Branch C in Decision 7 v2 Scale 5), Decision 2 v2's scANVI default becomes architecturally redundant — the substrate IS the harmonization layer. **v2 makes the conditional logic explicit.**

- **Decision 5 v2 ↔ Decision 2 v2:** Decision 5 v2's N=5 Deep Ensembles operates over Decision 4 v2's L7 head. **The Q2 layer is INSIDE the ensemble unit** — different ensemble members can use the same Q2 harmonization without that being a source of disagreement. v2 specifies the ensemble boundary.

---

## What Each Anchor Establishes

### Anchor 1 — Lopez et al. 2018 scVI (UC Berkeley Yosef lab, *Nature Methods* 15:1053-1058)

**Established empirically and architecturally:**
- VAE backbone for scRNA-seq with negative-binomial / zero-inflated negative-binomial noise model
- Latent-space batch marginalization via learned batch embeddings
- Probabilistic foundation enables aleatoric uncertainty quantification natively
- Foundational architecture for the Yosef lab Q2 lineage (precursor to scANVI, MrVI)

**What this contributes to Decision 2 v2:** The VAE backbone architecture. scVI serves as the **baseline VAE** in INTERCEPTA's Q2 layer — operationally available when no labels are present (unsupervised).

**What this does NOT establish:** Drug response prediction. Cross-disease transfer. Counterfactual prediction.

### Anchor 2 — Xu et al. 2021 scANVI (Yosef lab, *Mol Syst Biol* 17:e9620)

**Established empirically and architecturally:**
- Semi-supervised extension of scVI for label-aware integration
- Annotation transfer from labeled reference to unlabeled query cohorts
- Per scIB benchmark: **scANVI dominates when labels are available** — INTERCEPTA's most common scenario
- Outperforms scVI when label information is partially available

**What this contributes to Decision 2 v2:** **The default Q2 method when drug response labels are available** from bulk cell line training. INTERCEPTA's training scenario is "labeled bulk → unlabeled scRNA-seq query" — scANVI's semi-supervised framework is exactly this use case.

**What this does NOT establish:** Drug response classification (cell type focus). Counterfactual prediction.

### Anchor 3 — Boyeau et al. 2025 MrVI (Yosef lab, *Nature Methods* 22:2264-2274)

**Established empirically and architecturally:**
- **Multi-resolution** VAE: hierarchical 2-level latent (cell state `u` + sample-aware `z`)
- **Counterfactual prediction:** `z^(s)_n = β_n × c_s + β_0 + ε_n` predicts what cell n's response would be under sample s's condition
- **Validated on drug perturbation screens** — the only Q2 method with this property
- Supports sample-level heterogeneity analysis beyond standard batch correction

**What this contributes to Decision 2 v2:** **The counterfactual prediction primitive** for INTERCEPTA's drug-vs-control reasoning. MrVI's two-level hierarchy maps directly to INTERCEPTA's drug response scenario: cell state (latent `u`) modulated by treatment condition (latent `z`).

**For Decision 4 v2 integration:** MrVI's counterfactual framework is operationally similar to CPA's disentangled latent (Decision 4 v2 backbone). **Architectural pattern matches** — both use VAE + factorized latent + treatment-aware conditioning. INTERCEPTA can apply CPA OR MrVI for counterfactual; they are complementary not competitive.

### Anchor 4 — Korsunsky et al. 2019 Harmony (Broad Institute / Raychaudhuri lab, *Nat Methods* 16:1289-1296)

**Established empirically and architecturally:**
- PCA + soft-clustering + linear cluster-specific batch correction
- **Fastest method available** — CPU-only, scales to 10⁶ cells on standard hardware
- Deterministic (no stochastic training)
- Per scIB benchmark: wins on simpler ATAC-seq integration tasks

**What this contributes to Decision 2 v2:** **The compute-constrained fallback method.** When INTERCEPTA's HPC compute is insufficient for full VAE training (Decision 9 budget), Harmony provides CPU-scale operability without architectural rebuild.

**For Decision 5 v2 integration:** Harmony provides **point estimates only** — no native uncertainty quantification. **If Harmony is used as Q2 substrate, Decision 5 v2's Layer 5.2 Deep Ensembles + Layer 5.3 conformal must compensate** for the missing uncertainty layer. Decision 5 v2's stacked architecture handles this — but operational cost is higher (no native Q2 uncertainty to consume).

### Anchor 5 — Stuart, Butler et al. 2019 Seurat v3 (Satija lab NYGC, *Cell* 177:1888-1902.e21)

**Established empirically and architecturally:**
- Canonical Correlation Analysis (CCA) + Mutual Nearest Neighbors (MNN) + anchor scoring
- **Reference-and-query paradigm** — operationally distinct architecture
- Non-linear transformation in anchor space
- Multi-modal capable (RNA + ATAC + spatial + protein)
- R-language ecosystem (with reticulate Python interop)

**What this contributes to Decision 2 v2:** **The multi-modal extension** for spatial transcriptomics, scATAC-seq, and protein-coupled inputs. INTERCEPTA's Nicheformer (Q8.1) spatial inputs benefit from Seurat v3's multi-modal anchoring.

**For Decision 7 v2 Scale 6 (spatial) integration:** Seurat v3 + River (Decision 7 v2 Scale 6) is operationally complementary — Seurat v3 harmonizes across spatial slices; River performs DSEP gene prioritization within the harmonized space. **Architectural pattern: Q2 (harmonize) → Q7 Scale 6 (attribute).**

### Anchor 6 — Luecken et al. 2022 scIB benchmark (Helmholtz Munich Theis lab, *Nat Methods* 19:41-50)

**Established empirically:**
- **Field-defining benchmark:** 16 methods × 13 tasks × 1.2M cells × 23 publications
- **Task-dependent winner pattern:**
  - scGen and scANVI win when labels available
  - Scanorama and scVI win on complex RNA integration tasks
  - Seurat v3 wins on simpler tasks with distinct biological signals
  - Harmony and LIGER win for scATAC-seq integration
- **Empirical justification for multi-method architecture** — no single method dominates 13 tasks

**What this contributes to Decision 2 v2:** **The empirical foundation for multi-method commitment.** Decision 2 v2's scANVI-default + MrVI-counterfactual + Harmony-fallback + Seurat-multimodal structure is **scIB-validated** — each method assigned to the task class where scIB shows it dominates.

**For Decision 6 v2 V0-V6 validation cascade integration:** scIB provides the methodological template for INTERCEPTA's Q2 evaluation. Decision 6 v2's V0 (within-dataset) and V1 (cross-dataset) levels should report scIB metrics (biological conservation + batch effect removal balance) on INTERCEPTA's data — providing comparability with the published benchmark.

---

## Convergent Patterns Across the 6 Anchors

### Pattern A — Three paradigms exist; no paradigm dominates universally (preserved from v1)

scIB confirms task-dependent performance. Decision 2 v2 commits to **multi-method scenario-aware deployment** — not because of indecision, but because the field has empirically established that no single method wins all scenarios.

### Pattern B — Yosef lineage provides architectural coherence (preserved from v1)

scVI → scANVI → MrVI form a coherent 7-year research program. All three supported in `scvi-tools` Python package. **For INTERCEPTA, multi-method deployment within the Yosef family is operationally feasible** — shared infrastructure, consistent APIs, common documentation.

### Pattern C — MrVI is uniquely drug-perturbation-validated (preserved from v1)

The only Q2 method with explicit drug perturbation validation. Its counterfactual framework `z^(s)_n = β_n × c_s + β_0 + ε_n` directly maps to INTERCEPTA's drug-vs-control reasoning. **This makes MrVI architecturally privileged** for counterfactual scenarios within the multi-method commitment.

### Pattern D — Q2 methods provide native uncertainty to varying degrees (NEW in v2)

| Method | Native uncertainty | Decision 5 v2 integration cost |
|---|---|---|
| scVI / scANVI / MrVI | **Yes (VAE posterior)** | Low — aleatoric extractable directly |
| Harmony | **No (point estimate)** | High — Decision 5 v2 ensembles must compensate |
| Seurat v3 | **No (point estimate)** | High — same compensation needed |

**For Decision 5 v2 integration:** VAE-family Q2 substrates provide built-in aleatoric uncertainty (Layer 5.1 of Decision 5 v2 stack); Harmony and Seurat v3 do not. **This is a non-trivial cost differential.** Choosing VAE family substrate is architecturally cheaper because Decision 5 v2's stacked architecture has less compensation work to do.

### Pattern E — Q2 is substrate-compatible with Decision 1 v2's flexibility (NEW in v2)

Decision 1 v2 commits to substrate flexibility (FM / parameter-free / VAE). **Q2 is operationally compatible with all three:**

| Decision 1 v2 substrate | Q2 method compatibility |
|---|---|
| **FM (scFoundation/UCE/scGPT/Geneformer)** | Q2 wraps FM embeddings; scVI/Harmony/Seurat operate on FM-derived input |
| **Parameter-free (scTOP per Souza-Mehta)** | scTOP projections are themselves a form of harmonization — Q2 redundant or simplified |
| **VAE (scVI/scANVI)** | **Substrate IS the Q2 method** — no separate Q2 layer needed |

**Critical observation:** if Decision 1 v2 Layer 5 ablations select scVI/scANVI substrate, **Q2 collapses into Decision 1 v2 architecturally.** Decision 2 v2 acknowledges this — the multi-method commitment is **conditional** on which substrate wins.

### Pattern F — Cross-cohort harmonization is necessary but not sufficient for cross-disease transfer (preserved from v1)

scIB tasks are within-condition cross-batch (pancreatic islets, immune atlases, mouse brain). **None test cancer-trained → autoimmune-applied scenarios.** Combined with Q1 finding that only Geneformer demonstrates non-cancer FM application, **cross-disease transfer is consistently absent across both Q1 and Q2.** Charter U3 (5+ disease categories) requires INTERCEPTA's empirical contribution — Q2 alone cannot solve this.

### Pattern G — Q2 architecturally bridges to Q3, Q5, Q7 (extended in v2)

**For Q3 (bulk → single-cell):** Seurat v3's reference-and-query paradigm maps directly: bulk cell line data as "reference," patient scRNA-seq as "query."

**For Q5 (OOD detection):** VAE-family Q2 provides native posterior uncertainty (Decision 5 v2 Layer 5.1 substrate). Harmony/Seurat v3 require post-hoc OOD scoring.

**For Q7 (interpretability, NEW in v2):** scANVI's labeled latent supports gene-level attribution per Decision 7 v2 Scale 5 Branch C (VAE-decoder IG+SmoothGrad). MrVI's two-level hierarchy enables sample-level + cell-level attribution simultaneously.

---

## What the Field Has NOT Resolved (Honest Gaps)

Reading across all 6 Q2 anchors, the field's open questions:

1. **Drug response prediction across cohorts.** All scIB tasks are cell type integration / batch correction / biological conservation. Drug response is downstream of Q2's published scope — INTERCEPTA's novelty.

2. **Bulk-to-scRNA bridge.** Q2 methods integrate multiple scRNA-seq datasets; the bulk-cell-line → patient-scRNA-seq gap is unaddressed by Q2 family (Q3's scope).

3. **Cross-disease transfer.** Within-condition cross-batch only; cancer-trained → autoimmune-applied unbenchmarked.

4. **FM integration.** No published Q2 method combines FM embeddings (Q1) with Q2 cross-cohort harmonization in a layered architecture.

5. **Compute-quality trade-off at INTERCEPTA's deployment scale.** scIB documents method scalability at atlas-building scale; INTERCEPTA's drug response prediction scale is different.

6. **Multi-method orchestration in production.** All Q2 papers benchmark single methods; **how to operationally deploy scANVI + MrVI + Harmony + Seurat v3 in a single inference pipeline** is unbenchmarked.

7. **Cross-disease scIB-style benchmark.** scIB stops at cell-type-integration tasks; an analogous benchmark for cross-disease drug response would empirically resolve Q2 + Q3 + Q4 simultaneously — doesn't exist.

These require Layer 5 implementation or new benchmark construction, not more Layer 1 reading.

---

## Cross-Decision Architectural Patterns (NEW IN V2)

The Q2 anchors inform decisions beyond Decision 2:

### For Decision 1 v2 (cell representation) — OPERATIONALLY CO-BOUND

**Conditional logic:**
- If FM substrate wins Layer 5: Q2 wraps FM embeddings; multi-method Q2 architecture intact
- If parameter-free substrate wins: scTOP projections provide intrinsic harmonization-like properties; Q2 layer may be simplified
- If VAE substrate wins: **Decision 1 v2 substrate IS the Q2 method** — Decision 2 v2 collapses into Decision 1 v2 architecturally

**Decision 2 v2 commitment:** Multi-method Q2 architecture is **default** but **conditional on Decision 1 v2 outcome**. The operational pipeline must support all three branches.

### For Decision 4 v2 (drug response architecture) — REINFORCED

Decision 4 v2 Slot 1 (cell encoder) inherits the Decision 1 v2 substrate. **Q2 layer operates upstream of Decision 4 v2 L7** — harmonized cell representations feed into the L7 backbone. The 6-slot L7 architecture is unchanged regardless of Q2 method choice.

**MrVI ↔ CPA architectural parallel:** Both use VAE + factorized latent + treatment conditioning. Decision 4 v2's CPA backbone and MrVI's counterfactual framework are **architecturally complementary** — MrVI for sample-level heterogeneity; CPA for drug-class disentanglement. Layer 5 may evaluate combining both.

### For Decision 5 v2 (OOD detection) — OPERATIONALLY CO-BOUND

**Q2 substrate determines Decision 5 v2 Layer 5.1 cost:**
- VAE-family Q2 (scVI/scANVI/MrVI): native aleatoric uncertainty (Layer 5.1 substrate ready)
- Non-VAE Q2 (Harmony/Seurat v3): no native uncertainty; Decision 5 v2 must compensate via N=5 Deep Ensembles + conformal

**Decision 5 v2 architecture is robust to Q2 choice** — its 4-layer stack works regardless. But operational cost differs.

### For Decision 6 v2 (validation cascade) — REINFORCED

Decision 6 v2 V0-V1 evaluation should report **scIB metrics on INTERCEPTA's data** — biological conservation (ARI for cell types preserved) + batch effect removal (kBET for batch mixing). This provides **direct comparability with the published Q2 benchmark** (Luecken et al. 2022).

### For Decision 7 v2 (mechanistic interpretability) — OPERATIONALLY CO-BOUND

- **VAE-family Q2** → Decision 7 v2 Scale 5 Branch C (IG+SmoothGrad over VAE decoder) operates natively on Q2 latent
- **MrVI specifically** → sample-level attribution + cell-level attribution simultaneously per two-level hierarchy
- **Seurat v3** → spatial-aware Q2; integrates with Decision 7 v2 Scale 6 (River DSEP) for spatial modality

### For Decision 8 (universality) — REINFORCED

Decision 8 V6 cross-disease pass criterion (AUROC ≥ 0.65 across ≥2 therapeutic areas) requires that **Q2 layer transfer biological vs technical variation accurately across diseases.** Cross-disease scIB-style benchmark doesn't exist — INTERCEPTA contribution.

**Decision 8 Paradigm A (FM portfolio) ↔ Q2:** FMs trained on broad cell type diversity may provide intrinsic harmonization-like properties; whether explicit Q2 layer is still needed for FM substrate is a Layer 5 ablation question.

**Decision 8 Paradigm D (parameter-free scTOP) ↔ Q2:** scTOP's pathway projections operate at a level of abstraction (pathway activity, not gene expression) that may make explicit Q2 redundant. **Parameter-free substrate may collapse Q2 + part of Q7 architecturally** — a Souza-Mehta methodological bar implication.

### For Decision 9 (compute) — RELEVANT

- Harmony: CPU-only, 10⁶ cells on standard hardware
- VAE family: GPU-dependent, hours-days for 10⁵-10⁶ cells
- Seurat v3: CPU/R, intermediate

**Decision 9 must allocate Q2 compute per substrate choice.** If VAE family substrate (Decision 1 v2) wins, Q2 compute is included in substrate training. If non-VAE Q2 (Harmony fallback), separate budget needed.

### For Decision 10 (open-source) — REINFORCED

- scVI / scANVI / MrVI: **scvi-tools BSD-3** license, fully open
- Harmony: MIT license (harmonypy Python implementation)
- Seurat v3: GPLv3 (R package — copyleft consideration for commercial deployment)

**Charter §1.1 open-source commitment:** scvi-tools + harmonypy are unproblematic. Seurat v3 requires either GPL compliance or alternative wrapping. **Decision 10 must address this nuance.**

---

## Decision 2 — REVISED PROPOSED (v2 formalized below)

Decision 2 v1 specified **multi-method scenario-aware Q2 architecture** with scANVI default + MrVI counterfactual + Harmony fallback + Seurat v3 multi-modal. This v1 commitment is **architecturally preserved in v2** with these additions:

1. **Substrate-conditional logic** (NEW): Q2 architecture conditional on Decision 1 v2 substrate outcome
2. **Decision 5 v2 uncertainty integration** (NEW): VAE-family Q2 provides native aleatoric; non-VAE requires compensation
3. **Decision 6 v2 V0-V1 evaluation** (NEW): scIB-metric reporting for benchmark comparability
4. **Decision 7 v2 Scale 5/6 interpretability** (NEW): VAE-family Q2 enables Branch C gene attribution; Seurat v3 enables spatial modality bridging
5. **Decision 10 license caveat** (NEW): Seurat v3 GPLv3 vs scvi-tools BSD-3 distinction

See `INTERCEPTA_FV_Decision_2_Q2_cross_cohort.md` v2 for formalized Decision Record.

---

## What This Synthesis Does NOT Resolve

Honest gaps that propagate to Layer 5 implementation:

1. **Specific Q2 method per scenario in production.** Multi-method commitment is architectural; specific scenario-to-method routing logic is Layer 5 work.

2. **scvi-tools version lock for reproducibility.** Decision 2 v1 acknowledged version drift risk; specific version commitment is Layer 5.

3. **Cross-disease Q2 transfer empirical evaluation.** Charter §1.1 universality test for Q2 specifically (not just downstream prediction) is Layer 5 work.

4. **Q2 + FM integration architectural choice.** Whether to apply Q2 before or after FM embedding is a Layer 5 ablation question.

5. **Production orchestration of multi-method Q2.** How to operationally route data through scANVI vs MrVI vs Harmony vs Seurat v3 in a single inference pipeline.

These require Layer 5 implementation, not more Layer 1 reading.

---

## Drift Catalog This Phase 9 Q2 Cycle

- **New drift instances introduced:** 0
- **Anchor depth audit:** Q2 anchors already at 15,582 words (~2,600w avg) — no anchor deepening needed; existing anchors retained as-is
- **v1 structure preserved:** v1's 3-paradigm framework + scIB synthesis + 4 gaps + multi-method commitment all preserved
- **v2 additions:** substrate-conditional logic; Decision 5 v2 / 6 v2 / 7 v2 / 10 cross-decision integration; cross-disease universality empirical openness made explicit

---

— Claude (CSO), 2026-05-10 (Phase 9 synthesis Q2 v2)
