# INTERCEPTA Layer 1 Q10 Operational Synthesis v2 — Open-Source Strategy: Components, Licenses, and the Single GPL Caveat

**CSO:** Claude
**Date:** 2026-05-10
**Phase:** 7 (audit remediation — Operational Decision class)
**Scope:** Operational analysis of license commitments and open-source strategy for Decisions 1 v2 through 8 component inventory, grounded in INTERCEPTA-specific constraints (Charter §1.1 open-science commitment; commercial vs academic deployment scenarios)
**Supersedes:** Q10 synthesis v1 (227 words, archived in `_archive/`)

**Status:** OPERATIONAL DECISION format (different from Research Decision format used for Q1-Q8) — pending CEO taxonomy consent

---

## Executive Summary

Q10 (open-source strategy) is **not a research question** — it does not ask what the field empirically establishes about open-source vs proprietary tradeoffs. It asks what INTERCEPTA should operationally commit to given its constraints:

1. Charter §1.1 open-science commitment
2. Component inventory from Decisions 1 v2 through 8 architectural commitments
3. License compatibility audit across the full stack
4. Commercial vs academic deployment scenario considerations

**The operational reality:** Almost the entire INTERCEPTA stack is open-source compatible. The component inventory across all eight decisions reveals:
- BSD-3, MIT, Apache 2.0, CC BY 4.0, CC0: all freely combinable for any deployment
- **GPL-3 caveat:** Harmony (Decision 2 v2 Q2 component) under GPL-3 requires careful handling
- **CC BY-NC-ND caveat:** DiSyn (Decision 6 v2 reference) non-commercial restriction
- **EVA partial open** (Decision 8 reference): 60M-parameter variant on Hugging Face open; larger variants commercial — academic research uses open variant

**Two cross-decision license integrations now explicit in v2:**

- **Decision 2 v2 ↔ Decision 10 v2 (GPL-3 Harmony):** Decision 2 v2's Seurat v3 GPLv3 + Harmony GPL-3 components require either GPL-compliant deployment OR alternative wrapping strategy. Decision 10 v2 specifies the resolution.

- **Decision 9 v2 ↔ Decision 10 v2 (reproducibility):** Decision 9 v2 Pass 7 requires open-source compute infrastructure stack (SLURM + containers + reproducible environments). Decision 10 v2 must ensure all components meet this reproducibility floor.

---

## Component License Inventory (Decisions 1 v2 through 8)

### Decision 1 v2 — Cell Representation (Substrate Flexibility)

| Component | Implementation | License | Status |
|---|---|---|---|
| scFoundation 100M | github.com/biomap-research/scFoundation | Open (license TBD per repo) | Production-ready; verify per repo |
| UCE | github.com/snap-stanford/UCE | Open | Production-ready |
| scGPT 51M | github.com/bowang-lab/scGPT | MIT | Production-ready |
| Geneformer ~10M | huggingface.co/ctheodoris/Geneformer | Apache 2.0 | Production-ready |
| scTOP (Souza-Mehta) | Open algorithm; reference implementation needed | Open methodology | Algorithm publicly described |
| scVI/scANVI substrate option | scvi-tools | BSD-3 | Production-ready |

**Decision 1 v2 license summary:** All substrate candidates are open. License compatibility is **permissive across all options**. No GPL contamination.

### Decision 2 v2 — Cross-Cohort Harmonization

| Component | Implementation | License | Status |
|---|---|---|---|
| scVI/scANVI/MrVI | scvi-tools | BSD-3 | Production-ready |
| **Harmony** | github.com/immunogenomics/harmony | **GPL-3** | **GPL-3 CAVEAT** |
| **Seurat v3** | satijalab/seurat | **GPL-3** | **GPL-3 CAVEAT** |
| scIB | github.com/theislab/scib | MIT | Production-ready |

**Decision 2 v2 license summary:** scvi-tools BSD-3 unproblematic. **Harmony + Seurat v3 GPL-3 require careful handling for commercial deployment.** Academic research deployment is unconstrained (GPL-3 source distribution requirements only bind on redistribution, not internal use).

### Decision 3 v2 — Bulk-to-Single-Cell Transfer

| Component | Implementation | License | Status |
|---|---|---|---|
| SCAD | github.com/Linwei-Z/SCAD | Open (verify per repo) | Research code |
| scDEAL | github.com/OSU-BMBL/scDEAL | Open (verify per repo) | Research code |
| scAdaDrug | github.com/hliulab/scAdaDrug | Open (verify per repo) | Research code |
| scRank | github.com/ZJUFanLab/scRank | Open (verify per repo) | Research code |
| Beyondcell | gitlab.com/bu_cnio/beyondcell | Open (verify per repo) | Production-ready |
| GDSC | cancerrxgene.org | CC0 (effectively) | Open data |
| CCLE/DepMap | depmap.org | CC BY 4.0 | Open data |

**Decision 3 v2 license summary:** Mostly open research code. Specific license per repository should be audited (Pass 4 below).

### Decision 4 v2 — Drug Response Architecture

| Component | Implementation | License | Status |
|---|---|---|---|
| Sci-Plex (Q4.1) | trapnell-lab data | Open | Open data |
| PaccMann (Q4.2) | github.com/PaccMann | Apache 2.0 | Production-ready (IBM) |
| DeepCDR (Q4.3) | github.com/kimmo1019/DeepCDR | Open (verify per repo) | Research code |
| CPA (Q4.4) | github.com/facebookresearch/CPA | MIT | Production-ready (Meta) |
| GEARS (Q4.5) | github.com/snap-stanford/GEARS | Open (verify per repo) | Research code |
| scGen (Q4.6) | scvi-tools | BSD-3 | Production-ready |
| chemCPA (Q4.7) | github.com/theislab/chemCPA | Open (verify per repo) | NeurIPS-standard |
| MoLFormer (chem-FM candidate) | IBM-released open | Open | Verify per release |
| ChemBERTa (chem-FM candidate) | seyonechithrananda/ChemBERTa | Open | Production-ready |

**Decision 4 v2 license summary:** Permissive across all anchor components. CPA's MIT (Meta) and PaccMann's Apache 2.0 (IBM) are production-quality. **Slot 2 chem-FM choice has license flexibility.**

### Decision 5 v2 — OOD Detection

| Component | Implementation | License | Status |
|---|---|---|---|
| Deep Ensembles | PyTorch standard | Open | Production-ready |
| MC Dropout | PyTorch standard | Open | Production-ready |
| Conformal prediction | mapie + crepes libraries | Open (MIT/Apache 2.0) | Production-ready |
| MIMO8 | implementation per Havasi et al. paper | Open methodology | Research code |
| Energy scoring | implementation per Liu 2020 paper | Open methodology | Production-ready |

**Decision 5 v2 license summary:** Universally permissive. No license issues.

### Decision 6 v2 — Validation Cascade

| Component | Implementation | License | Status |
|---|---|---|---|
| IMPROVE | Partin 2026 | Open (verify per Argonne release) | Production-ready |
| Tang 2022 | Open code release | Open (verify) | Research code |
| Kim 2020 PDXGEM | Open code release | Open (verify) | Research code |
| **DiSyn (Li-Shen 2024)** | Open code release | **CC BY-NC-ND** | **NON-COMMERCIAL** |

**Decision 6 v2 license summary:** Mostly permissive. **DiSyn CC BY-NC-ND restricts commercial use** of DiSyn-derived models. INTERCEPTA's academic research deployment is unaffected; commercial deployment must avoid DiSyn-derived components or relicense.

### Decision 7 v2 — Mechanistic Interpretability

| Component | Implementation | License | Status |
|---|---|---|---|
| IG / SmoothGrad / SHAP / DeepLIFT | captum (PyTorch) + shap library | BSD-3 / MIT | Production-ready |
| EIG (Jha 2020) | per Genome Biology paper | CC BY (paper) | Open methodology |
| River (Cui-Yuan 2025) | per Nature Communications | Open access | Open methodology |
| DeepStrataAge | per npj Aging 2026 | Open access | Reference methodology |
| Kendiukhov spectral | per Q1 anchor | Open methodology | Reference methodology |

**Decision 7 v2 license summary:** Universally permissive. captum (BSD-3) and shap (MIT) are production-ready open libraries.

### Decision 8 — Universality

| Component | Implementation | License | Status |
|---|---|---|---|
| Nicheformer | github | Open | Research code |
| TEDDY | not yet released | TBD | Pre-publication |
| PaSCient | per Cell Systems 2026 | Open (verify) | Reference methodology |
| **EVA** | huggingface.co/Scienta-Lab (60M variant) + commercial deployment | **Partially open** | 60M variant open; larger variants commercial |
| Souza & Mehta scTOP | per BU Physics 2026 | Open methodology | Reference methodology |

**Decision 8 license summary:** Mostly open. **EVA partial open** — 60M variant on Hugging Face accessible for academic use; larger commercial variants out of scope.

---

## License Compatibility Analysis

### Permissive License Cluster (Default Path)

**BSD-3 + MIT + Apache 2.0 + CC BY + CC0:** Freely combinable. Used by scvi-tools, scGPT, Geneformer, PaccMann, CPA, scIB, captum, shap, MoLFormer, ChemBERTa.

**INTERCEPTA's default deployment uses only this cluster.** No license restrictions on commercial OR academic use; minimal attribution requirements; source disclosure optional.

### GPL-3 Cluster (Conditional Path)

**Harmony + Seurat v3** are GPL-3. GPL-3 viral copyleft means:
- **Academic internal use:** unconstrained (use without distribution)
- **Distribution of derivative works:** must be GPL-3 (copyleft requirement)
- **Embedding in commercial closed-source software:** prohibited

**Resolution strategies for INTERCEPTA:**

1. **Strategy A — Academic-only Harmony/Seurat v3:** Use these components only in academic research deployment; do not include in commercial product. Acceptable for Layer 5 evaluation phase.

2. **Strategy B — Reticulate / subprocess wrapping:** Call Harmony/Seurat v3 as external processes (R subprocess; reticulate Python bridge) without statically linking. Clean license boundary; product remains non-GPL.

3. **Strategy C — Alternative methods:** If commercial deployment requires GPL-free stack:
   - Harmony → harmonypy (MIT-licensed Python reimplementation; verify exact license per repo)
   - Seurat v3 → totalVI / MOFA+ / alternative multi-modal method (BSD-3 / MIT)

**Decision 10 v2 commitment:** Strategy A for Layer 5 evaluation; Strategy B or C deferred to Layer 5+ as commercial deployment requirement emerges.

### CC BY-NC-ND Cluster (Non-Commercial Restriction)

**DiSyn (Decision 6 v2 reference)** is CC BY-NC-ND. Non-commercial restriction means:
- **Academic research use:** unconstrained
- **Commercial use:** prohibited under license

**INTERCEPTA implications:**
- Layer 5 evaluation can use DiSyn as reference benchmark
- Commercial deployment must avoid DiSyn-derived models or relicense
- DiSyn is reference methodology, not a binding architectural component — no critical dependency

### Partial Open Cluster (EVA Pattern)

**EVA (Decision 8 reference):**
- 60M-parameter variant on Hugging Face: open weights, license terms per HF Scienta-Lab/EVA-RNA-60M page
- Larger variants: commercial deployment via Scienta partnerships

**INTERCEPTA implications:**
- Layer 5 evaluation uses the 60M open variant
- Decision 8 Paradigm B (disease-area-specific) compatible with 60M variant
- Larger EVA variants out of scope for INTERCEPTA's open-science commitment

---

## Cross-Decision License Patterns

### Pattern A — Default deployment uses permissive-cluster components only

Decisions 1 v2 / 4 v2 / 5 v2 / 7 v2 architectural commitments can be satisfied entirely within BSD-3 + MIT + Apache 2.0 + CC BY cluster. **No GPL contamination required.**

### Pattern B — Decision 2 v2 GPL components are operationally optional

Harmony + Seurat v3 are *fallback / multi-modal extension* in Decision 2 v2, not default. The default Decision 2 v2 method (scANVI / MrVI) is BSD-3. **GPL components are conditional on scenarios that may not be invoked at all.**

### Pattern C — INTERCEPTA's open-science commitment is operationally tractable

Across the full Decisions 1 v2 through 8 component inventory, **no proprietary dependencies are architecturally required.** Charter §1.1 open-science commitment is satisfiable without functional compromise.

### Pattern D — Open data resources align with open methods

GDSC (CC0 effectively) + CCLE/DepMap (CC BY 4.0) + sci-Plex (open) + LINCS (open) — INTERCEPTA's training data substrates are all openly available.

### Pattern E — Reference implementations exist for all anchor methods

Every Decision 1 v2 through 8 anchor method has an open-source reference implementation on GitHub / GitLab / Hugging Face. **No implementations need to be built from paper alone** — this dramatically reduces Layer 5 implementation risk.

---

## INTERCEPTA Release Strategy

### Layer 5 Code Release Plan

**Open release of INTERCEPTA's implementation code** at Layer 5 V0 pass criterion achievement (Decision 4 v2 Pass 1; scGen reproduction). Specifically:

1. **License:** MIT or BSD-3 (permissive; align with scvi-tools BSD-3 to avoid friction with default substrate option)
2. **Repository:** GitHub under Northeastern or personal organization
3. **Components released:**
   - L7 architecture implementation (Decision 4 v2)
   - Decision 5 v2 OOD stack implementation
   - Decision 7 v2 interpretability stack implementation
   - Training pipelines (Phase 1-4 chemCPA architecture surgery)
   - V0-V6 evaluation scripts
4. **Documentation:** README + Tutorial notebooks + API docs
5. **Reproducibility:** environment.yml / containerfile; locked dependency versions

### Layer 5+ Model Weight Release Plan

**Model weight release** at Layer 5 V3 pass criterion achievement (Decision 6 v2 V3 = AUROC ≥ 0.77 on TCGA tumor):

1. **License:** open weights via Hugging Face under Northeastern organization
2. **Variants released:** at least one substrate variant (e.g., scTOP-based or scFoundation-based)
3. **Disease coverage:** initial cancer-only at V3; expand to non-cancer per V6 progress

### Community Engagement Strategy

- **Conference presentations:** target NeurIPS / ICML / ISMB / MICCAI as Layer 5 results emerge
- **Pre-print release:** bioRxiv / arXiv first; peer review parallel
- **Reproducibility:** community contributions welcomed via standard GitHub PR workflow

---

## What Q10 v2 Does NOT Resolve

To be honest about scope:

1. **Specific license choice for INTERCEPTA's released code** (MIT vs BSD-3 vs Apache 2.0). Layer 5+ operational decision; current preference is MIT or BSD-3.

2. **Repository organization** (Northeastern vs personal vs new org). Layer 5+ operational decision.

3. **Tutorial notebook scope and depth.** Layer 5+ documentation work.

4. **Commercial licensing strategy for Layer 5+ outputs.** Outside Layer 1 scope.

5. **GPL-3 component replacement timeline.** Strategy A (academic-only) is current; Strategies B or C are deferred to commercial-deployment-driven decisions.

6. **Per-repository license verification for "Open (verify per repo)" entries.** Pass 4 below requires systematic audit.

These require Layer 5 implementation execution, not more Layer 1 reading.

---

## Drift Catalog This Phase 7 Q10 Cycle

- **New drift instances introduced:** 0
- **Format reclassification:** Q10 reclassified from Research Decision (paper-anchored) to Operational Decision (constraint-anchored) per CEO consent taxonomy
- **v1 commitments preserved:** Open-source default + permissive license cluster + GPL caveat acknowledgment + EVA partial open status — all from v1 reasoning, now formalized
- **v2 additions:** explicit per-decision license inventory; explicit license compatibility analysis; explicit cross-decision license patterns; explicit release strategy phased to Decision 6 v2 pass criteria
- **Erratum preserved from v1:** EVA classification corrected from "Closed/proprietary" to "Partially open" (60M variant on HF) per Drift Instance #5 resolution

---

— Claude (CSO), 2026-05-10 (Phase 7 Q10 operational synthesis v2)
