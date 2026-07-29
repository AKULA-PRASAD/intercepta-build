# INTERCEPTA Decision 10 v2 — Open-Source Strategy Commitment: Permissive-License Default + GPL-3 Conditional Handling + Phased Release Plan (PROPOSED — Operational Decision Class)

**Status:** PROPOSED Operational Decision Record (different format from Layer 1 Research Decision Records 1-8; pending CEO taxonomy consent)
**Date:** 2026-05-10
**CSO:** Claude
**Phase:** 7 (audit remediation final phase)
**Supersedes:** Decision 10 v1 (136 words, archived in `_archive/`)

---

## Operational Constraint Foundation

This is **not a Research Decision**. It does not derive from primary-source paper reads or benchmark evidence. It is an **Operational Decision** grounded in INTERCEPTA-specific constraints:

1. **Charter §1.1 open-science:** INTERCEPTA's open-science commitment
2. **Decisions 1 v2 through 8 component inventory:** specific anchor methods + their licenses
3. **Academic vs commercial deployment scenarios:** different license constraints apply
4. **Decision 9 v2 Pass 7 binding:** open-source compute infrastructure stack requirement
5. **CEO + CSO bandwidth:** realistic license audit + compliance maintenance capacity

The empirical state of open-source licensing in computational biology is **inventory data**, not decision grounding. The decision itself is what INTERCEPTA **chooses to operationally commit to** for its specific deployment scenarios.

---

## The Decision

INTERCEPTA's open-source strategy commits to **PERMISSIVE-LICENSE-CLUSTER DEFAULT** for all components where alternatives exist, **CONDITIONAL HANDLING** of the two GPL-3 components (Harmony + Seurat v3), explicit **CC BY-NC-ND BOUNDARY** for DiSyn-derived methods, **PHASED RELEASE PLAN** tied to Decision 6 v2 V0-V3 pass criteria, and **DECISION 9 v2 REPRODUCIBILITY BINDING** for compute infrastructure stack.

### Operational Strategy Diagram

```
INTERCEPTA Layer 5 Stack
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
[Default Permissive Cluster]            [Conditional GPL-3 Cluster]
BSD-3, MIT, Apache 2.0, CC BY, CC0      Harmony, Seurat v3
        ↓                                       ↓
- scvi-tools (Decisions 1 v2/2 v2)      - Strategy A: academic-only use
- scGPT, Geneformer, UCE                  during Layer 5 evaluation
  (Decision 1 v2 substrate)             - Strategy B: subprocess/reticulate
- scTOP (parameter-free substrate)        wrapping if commercial needed
- CPA, chemCPA, GEARS (Decision 4 v2)   - Strategy C: alternative methods
- scAdaDrug/scRank/Beyondcell (Q3)        (harmonypy, totalVI, MOFA+) if
- captum, shap (Decision 7 v2)            license-clean stack required
- mapie, crepes (Decision 5 v2)
- Most chem-FM candidates
        ↓                                       ↓
        └───────────────────┬───────────────────┘
                            ↓
[Excluded — Not Used in Default]
- DiSyn-derived models (CC BY-NC-ND blocks commercial)
- EVA larger variants (commercial-only; not needed)
- TEDDY (pre-publication; awaits release)
                            ↓
[Phased Release Plan]
- V0 pass (Decision 4 v2 Pass 1) → release Layer 5 implementation code
- V3 pass (Decision 6 v2 V3) → release model weights via Hugging Face
- V6 pass (Decision 8 cross-disease) → release universality benchmark suite
```

### Six Operational Commitments

**Commitment 1 — Permissive cluster as default:**
- Default architecture uses BSD-3 / MIT / Apache 2.0 / CC BY / CC0 components only
- Any new component additions audited for license compatibility before adoption
- Operational benefit: deployment-friction-free across academic and commercial scenarios

**Commitment 2 — GPL-3 conditional handling:**
- **Strategy A (Layer 5 evaluation phase, current default):** Harmony + Seurat v3 used in academic research deployment only; no commercial product redistribution
- **Strategy B (conditional — Layer 5+):** If commercial deployment emerges, use subprocess/reticulate wrapping to maintain clean license boundary
- **Strategy C (conditional — Layer 5+):** If Strategy B operationally fragile, switch to permissive alternatives (harmonypy for Harmony; totalVI/MOFA+ for Seurat v3 multi-modal)
- Operational benefit: Layer 5 evaluation unconstrained by GPL-3 while preserving commercial-deployment optionality

**Commitment 3 — CC BY-NC-ND boundary:**
- DiSyn-derived models excluded from default deployment due to non-commercial restriction
- DiSyn usable as reference benchmark during Layer 5 evaluation only
- Operational benefit: clean commercial path; reference benchmark accessibility preserved

**Commitment 4 — Phased release plan tied to Decision 6 v2 pass criteria:**
- **V0 achievement (Decision 4 v2 Pass 1 — scGen reproduction):** open release of INTERCEPTA implementation code (MIT or BSD-3 license)
- **V3 achievement (Decision 6 v2 V3 — AUROC ≥ 0.77 on TCGA):** model weight release via Hugging Face (at least one substrate variant)
- **V6 achievement (Decision 8 cross-disease — AUROC ≥ 0.65 across ≥2 therapeutic areas):** universality benchmark suite release with held-out disease evaluations
- Operational benefit: releases tied to empirical milestones; prevents premature release of unvalidated code

**Commitment 5 — Reproducibility infrastructure (Decision 9 v2 binding):**
- All Decision 9 v2 compute commitments use open-source infrastructure (SLURM scheduler; Singularity/Apptainer or Docker containers; conda/mamba environment specifications)
- Locked dependency versions for all environment files
- Containerized deployment recipes (`environment.yml` + `Dockerfile` or `Apptainer.def`) released with code
- Operational benefit: Layer 5 reproducibility binding made operational

**Commitment 6 — Community engagement:**
- Pre-print release on bioRxiv / arXiv first (parallel to peer review)
- Conference targeting: NeurIPS / ICML / ISMB / MICCAI as Layer 5 results emerge
- Community contributions welcomed via GitHub PR workflow with documented contribution guidelines
- License compliance audit before any external code merge
- Operational benefit: distributed development capability while maintaining license discipline

---

## Pass Criteria (Binding GO/NO-GO per Operational Decision class)

Decision 10 v2 must satisfy the following operational criteria before LOCK:

### Pass 1 — Default Stack License Audit Clean

**Criterion:** Component-by-component license audit confirms that all Decisions 1 v2 / 4 v2 / 5 v2 / 6 v2 (excluding DiSyn) / 7 v2 / 8 / 9 v2 components are within the permissive cluster (BSD-3 / MIT / Apache 2.0 / CC BY / CC0) OR explicitly handled per Commitments 2-3.

**Rationale:** Operational gate. If license audit reveals unhandled non-permissive components, the default deployment claim fails.

### Pass 2 — GPL-3 Component Handling Operational

**Criterion:** During Layer 5 evaluation phase, Decision 2 v2 Harmony + Seurat v3 components used under Strategy A (academic-only) without architectural friction. Specifically: scvi-tools BSD-3 substrate provides the *default* Q2 method; Harmony + Seurat v3 are *fallback* and *multi-modal extension* not invoked unless scenario requires.

**Rationale:** Validates that GPL-3 components remain operationally optional. If default scenarios force GPL-3 invocation, Strategy A is fragile.

### Pass 3 — Permissive-Cluster Sufficient for Default Architecture

**Criterion:** Decision 4 v2 Pass 1 (scGen reproduction baseline) achievable using only permissive-cluster components — no GPL-3, no CC BY-NC-ND, no commercial-only dependencies.

**Rationale:** Operational test of Commitment 1. If V0 pass requires GPL-3 components, the default architecture is operationally GPL-3-bound and Strategy A is misleading.

### Pass 4 — Per-Repository License Verification

**Criterion:** For every component listed as "Open (verify per repo)" in Q10 synthesis v2, the actual license file in the source repository is verified and documented. No assumptions; primary-source license verification.

**Repository list requiring verification:**
- scFoundation, SCAD, scDEAL, scAdaDrug, scRank, DeepCDR, GEARS, chemCPA, Nicheformer, PaSCient, Tang 2022, Kim 2020 PDXGEM, IMPROVE

**Rationale:** Same primary-source verification discipline as Research Decisions. License claims without repo-file verification are fabrication-class drift.

### Pass 5 — V0 Code Release Operational

**Criterion:** At Decision 4 v2 Pass 1 achievement, INTERCEPTA implementation code released on GitHub with:
- MIT or BSD-3 license file
- README + Tutorial notebooks + API docs
- environment.yml or Dockerfile/Apptainer.def
- Locked dependency versions
- Working reproducibility verification (independent reproduction of V0 baseline)

**Rationale:** First release milestone. Subsequent releases (V3 model weights, V6 universality suite) build on this foundation.

### Pass 6 — Decision 9 v2 Reproducibility Cross-Binding

**Criterion:** All Decision 9 v2 compute commitments (Northeastern Explorer SLURM; cached embeddings; multi-stage training; V6 grid SLURM arrays) use only open-source infrastructure tools (no proprietary schedulers, containers, or environment managers).

**Rationale:** Decision 9 v2 Pass 7 ↔ Decision 10 v2 Pass 6 cross-binding. Reproducibility requires open compute stack.

### Pass 7 — Commercial Deployment Path Preserved

**Criterion:** If Layer 5+ commercial deployment scenario emerges, Strategy B (subprocess/reticulate wrapping for GPL-3) OR Strategy C (alternative permissive methods) is demonstrably implementable within ≤ 4 weeks of effort.

**Rationale:** Default deployment is academic-friendly; commercial path must be operationally reachable without architectural rebuild. **This is the optionality preservation test.**

---

## Trade-offs and Rejected Alternatives

### Why not commit to GPL-3 fully (including commercial)?

**Rejected reason:** GPL-3 copyleft forces all derivative works to be GPL-3. INTERCEPTA's eventual commercial deployment (if pursued) would be GPL-bound, restricting customer adoption. **Strategy A (academic-only Harmony/Seurat v3) preserves commercial optionality without sacrificing Layer 5 evaluation utility.**

### Why not commit to permissive-only (exclude GPL-3 components from start)?

**Rejected reason:** Harmony (Decision 2 v2 fallback) and Seurat v3 (Decision 2 v2 multi-modal) provide architectural value for specific scenarios (compute-constrained; spatial transcriptomics). Pre-emptive exclusion forces architectural compromise. **Conditional handling (Strategy A/B/C) preserves architectural value AND license optionality.**

### Why not commit to commercial-friendly proprietary stack?

**Rejected reason:** Charter §1.1 open-science commitment is binding. Proprietary stack violates Charter §1.1. **Not negotiable at Decision 10 v2 level.**

### Why include CC BY-NC-ND boundary (DiSyn exclusion)?

**Rationale:** DiSyn is *reference methodology*, not binding architectural component. Excluding DiSyn from default deployment maintains clean commercial path without functional loss. **Acceptable trade-off.**

### Why include EVA partial-open inclusion?

**Rationale:** EVA 60M variant on Hugging Face is openly accessible. Larger commercial variants are out of scope. **INTERCEPTA uses the open variant; ignores commercial variants.** Decision 8 Paradigm B (disease-area-specific FM) compatible with 60M variant for I&I applications.

### Why phase release to Decision 6 v2 pass criteria?

**Rationale:** Premature code release of unvalidated implementations damages community trust and creates support burden. **Tying releases to empirical milestones (V0 / V3 / V6) ensures released code is empirically grounded.**

### Why not release at LOCK status of decisions?

**Rationale:** LOCKed decisions are architectural; released code/weights require *empirical validation*. LOCK without empirical pass is theoretical. **Empirical pass criteria are the operational release gate.**

---

## Cross-Decision Implications

Decision 10 v2 affects and is affected by:

- **Decision 1 v2 (cell representation):** All substrate options (FM / parameter-free / VAE) are within permissive cluster. License flexibility supports Layer 5 ablation across all substrates.

- **Decision 2 v2 (cross-cohort):** **OPERATIONAL CO-BOUND.** GPL-3 components require Strategy A/B/C handling per Decision 10 v2 Commitment 2. Default Q2 method (scANVI BSD-3) avoids GPL-3 invocation; fallback methods (Harmony + Seurat v3) are conditional.

- **Decision 3 v2 (bulk → single-cell):** All Q3 components are open; specific per-repo license verification needed (Pass 4).

- **Decision 4 v2 (drug response architecture):** All Slot 1-6 candidates are within permissive cluster (chemCPA + CPA + GEARS + PaSCient + chem-FM candidates).

- **Decision 5 v2 (OOD detection):** All OOD stack components (Deep Ensembles + MC Dropout + conformal + energy) are universally permissive.

- **Decision 6 v2 (validation cascade):** **OPERATIONAL CO-BOUND.** Pass 5 release plan tied to Decision 6 v2 V0-V3 pass criteria.

- **Decision 7 v2 (mechanistic interpretability):** All Q7 stack components (captum + shap + EIG + River + DeepStrataAge methodology) are universally permissive.

- **Decision 8 (universality):** EVA partial-open accommodation; PaSCient + Nicheformer open; TEDDY pending release.

- **Decision 9 v2 (compute):** **OPERATIONAL CO-BOUND.** Pass 6 cross-binding: open-source infrastructure stack required. Decision 9 v2 Pass 7 ↔ Decision 10 v2 Pass 6.

---

## What Decision 10 v2 Does NOT Decide

To be honest about scope:

1. **Specific license choice for INTERCEPTA's released code (MIT vs BSD-3 vs Apache 2.0).** Layer 5+ operational decision; current preference is MIT or BSD-3 for permissive-cluster alignment.

2. **Repository organization (Northeastern vs personal vs new org).** Layer 5+ operational decision.

3. **Tutorial notebook scope and depth.** Layer 5+ documentation work.

4. **Commercial licensing strategy for Layer 5+ outputs.** Outside Layer 1 scope; emerges if/when commercial deployment becomes operational priority.

5. **Specific GPL-3 component replacement timing.** Strategy A is current; transition to B/C deferred to commercial-deployment trigger.

6. **Community contribution governance.** Layer 5+ governance design.

7. **Conference target prioritization.** Layer 5+ outreach strategy.

8. **Pre-print embargo strategy if peer review parallel timing.** Layer 5+ publication planning.

These require Layer 5 implementation execution or Layer 5+ operational decisions, not more Layer 1 reading.

---

## Discipline Check

- [x] **P3 (research before code):** ✅ Decision grounded in operational analysis of INTERCEPTA-specific constraints (Charter §1.1; Decisions 1 v2 through 8 component inventory + license audit); not paper-anchored because Q10 is an Operational Decision, not Research Decision (taxonomy pending CEO consent)
- [x] **P15 (only correct/honest/real science):** ✅ GPL-3 caveat honestly preserved; CC BY-NC-ND DiSyn boundary explicit; EVA partial open status accurately characterized; per-repo verification gap honestly named (Pass 4)
- [x] **P16 (preserve past work):** ✅ Decision 10 v1 (136 words) + Q10 synthesis v1 (227 words) archived in `_archive/`; v1 commitments preserved in v2 with formalization
- [x] **P-FV-1 to P-FV-3:** ✅ Decision 10 v2 directly serves Charter §1.1 open-science commitment
- [x] **Charter §5.3 GO/NO-GO:** ✅ Pass 1-7 criteria explicit and binding (operational/license tests)
- [x] **Charter §1.1 (open-science):** ✅ Permissive-cluster default; GPL-3 conditional handling; CC BY-NC-ND boundary explicit
- [x] **Cross-decision integration:** ✅ Decision 2 v2 GPL handling explicit; Decision 6 v2 release-plan binding; Decision 9 v2 reproducibility cross-binding (Pass 6); all other decisions checked for license compatibility
- [x] **Operational Decision class:** ✅ Format distinct from Layer 1 Research Decision Records 1-8; CEO taxonomy consent pending
- [x] **Erratum preserved from v1:** EVA classification corrected from "Closed/proprietary" to "Partially open" per Drift Instance #5 resolution

## Drift Catalog This Phase 7 Decision 10 v2 Write

- **New drift instances:** 0
- **Format reclassification:** Decision 10 reclassified from Research Decision (paper-anchored) to Operational Decision (constraint-anchored) — pending CEO taxonomy consent
- **v1 commitments preserved:** Open-source default + permissive license cluster + GPL caveat + EVA partial open — all from v1 reasoning, now formalized as 6 operational commitments + 7 binding pass criteria
- **v2 additions:** GPL-3 Strategy A/B/C explicit; CC BY-NC-ND DiSyn boundary; phased release plan tied to Decision 6 v2 pass criteria; per-repo license verification gate (Pass 4)
- **EVA erratum preserved:** Drift Instance #5 correction (Closed → Partially open) maintained from Phase 1 errata

---

— Claude (CSO), 2026-05-10 (Phase 7 Decision 10 v2 — Operational Decision Record)
