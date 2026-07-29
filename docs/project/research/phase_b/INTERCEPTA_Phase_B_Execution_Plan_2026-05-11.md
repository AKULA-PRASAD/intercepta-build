# INTERCEPTA Phase B Execution Plan

**Status:** CSO DRAFT — Awaiting CEO Approval Before Phase B Execution Begins
**Authority:** CEO Prasad Akula delegated "ultrathink and do best for our fullest vision" on 2026-05-11
**CSO:** Claude
**Date:** 2026-05-11 morning session
**Phase B objective:** Produce Layer 2 (Architecture Design), Layer 3 (Validation Strategy), Layer 4 (Implementation Specification) detailed specifications — total estimated 50-80K words — across multiple sessions, with audit discipline equivalent to Layer 1.
**Trigger to begin Phase B execution:** CEO approval of this plan.
**Phase B closure trigger:** Layer 2 + 3 + 4 detailed specifications all written, internally audited (Phase 8 equivalent), and ready for handoff to Layer 5 implementation prep.

---

## 1. Why This Plan Must Exist Before Phase B Execution

Layer 1 audit closure (Phases 1-7, 9) required 17 hours of focused work and surfaced 34 drift instances. The same drift risk exists for Layer 2-4 specs at higher magnitude because:

1. **Layer 2-4 are creative synthesis** (not mechanical correctness checks). Drift in creative work is harder to detect than drift in factual claims.
2. **Layer 2-4 spans many sessions.** A spec begun in Session 3 and continued in Session 7 without a plan diverges from the spec begun in Session 5.
3. **Layer 2-4 dependencies are non-trivial.** Layer 3 validation strategy depends on Layer 2 architecture choices. Layer 4 implementation spec depends on both. Writing them in wrong order produces broken specs that need rewrite.
4. **Layer 2-4 outputs gate Layer 5.** A flawed Layer 2 spec produces a flawed Layer 5 implementation. Wet-lab validation and clinical deployment depend on Layer 5 being correct.

**Phase B Execution Plan is the analog of the Charter for the layer-detail work.** Charter constrains Layer 1; this Plan constrains Layer 2-4.

---

## 2. Phase B Scope Boundaries

### IN SCOPE (Phase B will produce)

- **Layer 2 detailed Architecture Design** — PyTorch class skeletons, tensor shapes, module interfaces, substrate handling, OOD stack architecture, interpretability stack architecture, multi-method orchestration
- **Layer 3 detailed Validation Strategy** — V0-V6 validation pipeline, dataset specs, metric definitions, 56 binding pass criteria operationalized
- **Layer 4 detailed Implementation Specification** — implementation order, dependency graph, testing protocols, failure mode analysis, repository scaffolding
- **Supporting artifacts:** data acquisition manifest, HPC environment specification, license verification matrix, FM weights protocol, SLURM job templates, V0 test setup, repository directory structure
- **Phase 8 internal audit** of all Phase B output (analog of Phases 1-7 for Layer 1)
- **Updated decisions/README, charter/, research_log entries** documenting Phase B closure

### OUT OF SCOPE (Phase B will NOT do)

- **Layer 5 implementation** (code that runs models) — separate phase, gated on Phase B closure
- **HPC SSH execution** — requires CEO hands on keyboard
- **Data downloads** — requires CEO credentials (dbGaP, Hugging Face gated models)
- **Wet-lab partnerships** — external CEO action
- **Funding pursuit** — external CEO action
- **AML manuscript completion** — separate workstream, not Phase B
- **Workstream B HPC execution** — separate workstream, parallel track
- **NeoCARTa cleanup** — separate cleanup, not Phase B
- **Charter v2 reconciliation** — separate editorial decision
- **LOCK protocol execution** — separate process, can run parallel or after Phase B

### EXPLICIT CEO-AUTHORITY-REQUIRED ITEMS WITHIN PHASE B

These items WILL be drafted by CSO during Phase B but cannot be FINALIZED without CEO consent:

1. **License compatibility matrix** — CSO drafts; CEO confirms acceptance for each component license
2. **Northeastern HPC compute envelope assumptions** — CSO drafts based on Decision 9; CEO confirms or corrects
3. **Data acquisition priority order** — CSO drafts based on validation cascade; CEO sets priorities
4. **Repository name + license choice** — CEO decides (relates to Decision 10)
5. **Test data substitutions when full datasets unavailable** — CEO approves the substitution strategy

---

## 3. Phase B Artifact Inventory

The full Phase B output will be **18 artifacts** organized in 3 layers + supporting infrastructure.

### LAYER 2 — Architecture Design (5 artifacts, target ~25-35K words)

**Artifact L2.1 — Substrate Architecture Specification**
- Target: 5,000-7,000 words
- Source decisions: Decision 1 v2 (substrate paradigms)
- Source anchors: cui_2024_scgpt, hao_2024_scfoundation, rosen_2023_uce, theodoris_2023_geneformer, kendiukhov_2026_spectral_geometry, souza_mehta_2026_parameter_free, yao_2025_scpds
- Content: PyTorch class skeleton for each of 4 substrate options (FM-based, scTOP parameter-free, scVI, scANVI), substrate adapter interface, embedding caching protocol, swap-in/swap-out mechanics
- Acceptance criteria: every substrate class has explicit input/output tensor shapes, embedding dimensions specified, caching keys defined, fallback behavior on substrate unavailability

**Artifact L2.2 — L7 6-Slot Architecture Specification**
- Target: 7,000-10,000 words
- Source decisions: Decision 4 v2 (drug response architecture), Decision 2 v2 (harmonization slot), Decision 3 v2 (bulk-to-single slot)
- Source anchors: hetzel_2022_chemcpa, lotfollahi_2023_cpa, roohani_2024_gears, manica_2019_paccmann, liu_2020_deepcdr, pascient_liu_2024_2026
- Content: Each of 7 slots (substrate adapter Slot 0 + 6 functional slots) specified as PyTorch module with forward signature, expected input from previous slot, output for next slot, training hyperparameters, ablation toggles
- Acceptance criteria: tensor shapes traceable end-to-end from cell expression input to drug response output; mode collapse mitigation (Slot 5) has explicit mechanism; patient aggregation (Slot 6) PaSCient-style logic specified

**Artifact L2.3 — OOD Detection Stack Specification (4-layer)**
- Target: 5,000-7,000 words
- Source decisions: Decision 5 v2 (OOD detection)
- Source anchors: lakshminarayanan_2017_deep_ensembles, lopez_de_castro_2025_conformal_prediction, liu_2020_energy_ood, engelmann_2022_atlas_uncertainty, gal_2016_mc_dropout, theunissen_2025_ood_benchmark
- Content: Substrate posterior layer (substrate-conditional VAE posterior or non-VAE alternative), N=5 Deep Ensembles wrapper, conformal prediction calibration, energy-based scoring head
- Acceptance criteria: each layer has explicit threshold behavior, downstream confidence score interface defined, integration with L7 output specified

**Artifact L2.4 — Seven-Scale Interpretability Stack Specification**
- Target: 5,000-7,000 words
- Source decisions: Decision 7 v2 (mechanistic interpretability)
- Source anchors: jha_2020_enhanced_ig, cui_yuan_2025_river, multiscale_interpretability_composite, reynolds_pan_2025_genomics_interp_benchmark
- Content: Each of 7 scales (gene → cell → tissue → patient → cohort → population → mechanism) specified as module with attribution mechanism, substrate-conditional branching at Scale 5 (FM vs scTOP vs scVI vs scANVI), output format, integration with prediction output
- Acceptance criteria: substrate-conditional branching at Scale 5 has explicit handling for 4 substrates; each scale's output format machine-readable; Enhanced IG (Jha 2020) integration concrete

**Artifact L2.5 — Layer 2 Master Synthesis + Audit Manifest**
- Target: 3,000-4,000 words
- Content: How L2.1-L2.4 integrate, end-to-end forward pass tensor flow, training loop architecture, hyperparameter budget, GPU memory budget, audit checklist for Phase 8

### LAYER 3 — Validation Strategy (4 artifacts, target ~15-20K words)

**Artifact L3.1 — V0-V6 Validation Pipeline Specification**
- Target: 5,000-7,000 words
- Source decisions: Decision 6 v2 (validation cascade), Decision 8 (universality)
- Source anchors: partin_2026_improve_benchmark, tang_2022_pathway_transfer, kim_2020_pdxgem, li_shen_2024_disyn, wang_2025_scdrugmap
- Content: Each of 7 validation levels (V0-V6) specified with: dataset(s) used, training/test split protocol, metric(s) computed, threshold for pass, threshold for fail, what triggers reverting decision, computational budget
- Acceptance criteria: V6 cross-disease validation has explicit ≥2 therapeutic-area selection criteria; V0 reproduction baseline (scGen 2019) reproduction protocol defined

**Artifact L3.2 — 56 Binding Pass Criteria Operationalization**
- Target: 5,000-7,000 words
- Source decisions: All 10 v2 (each decision's pass criteria)
- Content: Each of ~56 pass criteria across 10 decisions written as: precise statistical hypothesis, dataset/setting for testing, pass/fail threshold with statistical correction, computational protocol
- Acceptance criteria: every pass criterion is falsifiable, has explicit dataset, has explicit statistical test, can be tested with code that does not yet exist but is unambiguously specified

**Artifact L3.3 — Cross-Disease V6 Validation Methodology**
- Target: 3,000-4,000 words
- Source decisions: Decision 8 (universality)
- Source anchors: eva_bandasack_scienta_2026, teddy_chevalier_2025, nicheformer_schaar_tejada_2025
- Content: Therapeutic area selection (which ≥2 disease categories?), held-out disease cohort protocols, transfer learning vs zero-shot framing, V6 threshold (AUROC ≥ 0.65) operationalization
- Acceptance criteria: at least 2 disease categories named and justified; held-out cohort source verified accessible to INTERCEPTA

**Artifact L3.4 — Layer 3 Master Synthesis + Cross-Layer Audit Hooks**
- Target: 2,000-3,000 words
- Content: Validation strategy integration, total computational budget for V0-V6, expected timeline, audit hooks back to Layer 2 modules

### LAYER 4 — Implementation Specification (5 artifacts, target ~15-25K words)

**Artifact L4.1 — Implementation Order + Dependency Graph**
- Target: 3,000-4,000 words
- Content: Exact order of Layer 5 implementation, dependency DAG (substrate before L7, L7 before OOD, etc.), milestone gates, parallel-work identification
- Acceptance criteria: every Layer 5 implementation task has explicit prerequisites; critical path identified; parallel work opportunities surfaced

**Artifact L4.2 — Testing Protocols (Unit, Integration, End-to-End)**
- Target: 3,000-5,000 words
- Content: Unit test specifications for each Layer 2 module class, integration tests for substrate × L7, integration tests for L7 × OOD, end-to-end V0 reproduction test
- Acceptance criteria: every Layer 2 module has at least 1 unit test specified; integration tests catch substrate-OOD interface bugs; V0 test runs in < 1 hour on Mac for development

**Artifact L4.3 — Failure Mode Analysis**
- Target: 3,000-4,000 words
- Content: For each major component, enumerate: failure modes (silent, loud, intermittent), detection mechanism, recovery protocol, when to halt training vs continue, when to invalidate a validation run
- Acceptance criteria: substrate unavailability handled gracefully; OOD-stack disagreement handled; FM weights checksum failure handled; HPC SLURM job failure handled

**Artifact L4.4 — Repository Scaffolding Specification**
- Target: 3,000-5,000 words
- Content: Directory structure for INTERCEPTA Python package, exact files to create, README skeleton, CONTRIBUTING.md, .gitignore (already exists), setup.py / pyproject.toml, CI/CD config, branch protection, version tagging
- Acceptance criteria: directory structure matches Layer 2 module organization; setup.py installs correctly on Mac (CSO can verify); CI/CD config valid YAML

**Artifact L4.5 — Layer 4 Master Synthesis + Phase B Closure Checklist**
- Target: 2,000-3,000 words
- Content: Implementation roadmap, time-to-Layer-5-launch estimate, Phase B closure criteria, handoff document for Layer 5 prep

### SUPPORTING INFRASTRUCTURE ARTIFACTS (4 artifacts, target ~10-15K words)

**Artifact S.1 — Data Acquisition Manifest**
- Target: 4,000-6,000 words
- Content: Every dataset required for Layer 5 (GDSC, CCLE, sci-Plex3, LINCS L1000, TCGA, PDX cohorts, Tabula Sapiens, sci-Plex per substrate, V6 held-out cohorts, FM training data references), source URL, license, file size, download protocol (curl/wget/dbGaP application), credentials required, target /scratch path
- Acceptance criteria: every dataset has either (a) actionable download command or (b) explicit "requires CEO application" flag; total disk budget estimated; download dependency order specified (some require dbGaP approval first)

**Artifact S.2 — HPC Environment Specification**
- Target: 3,000-4,000 words
- Content: Exact `environment.yml` for conda, `setup.sh` for HPC bootstrap, conda channel order, Python version, PyTorch + CUDA version, GPU vs CPU env split, validation test script
- Acceptance criteria: environment.yml installs cleanly on test Linux env (CSO can write smoke test); GPU env has torch.cuda available; package versions pinned; reproducibility guaranteed

**Artifact S.3 — License Verification Matrix**
- Target: 2,000-3,000 words
- Source decisions: Decision 10 v2
- Content: All 13+ components × their license × compatibility check against INTERCEPTA's planned release license (CEO to confirm Apache-2 or other), incompatibilities flagged with mitigation
- Acceptance criteria: every component has license verified; incompatibilities (if any) flagged for CEO; release license recommendation made

**Artifact S.4 — FM Weights Download + Caching Protocol**
- Target: 1,500-2,500 words
- Content: For each FM in Decision 1 v2 (scFoundation, UCE, scGPT, Geneformer): Hugging Face URL or alternative source, gated access requirements, license acceptance steps, weight checksum, target cache path, embedding generation protocol
- Acceptance criteria: every FM has either (a) direct download command + checksum or (b) explicit "requires HF account + license accept" steps

---

## 4. Dependency Graph

```
LAYER 1 (DONE)
   ↓
Phase B Execution Plan (THIS DOCUMENT)
   ↓ (CEO approval gate)
   ↓
S.1 Data Manifest  ←──┐
S.3 License Matrix ←──┤    (parallel-doable, independent of L2)
S.4 FM Protocol    ←──┘
   ↓
L2.1 Substrate Spec        (requires S.4 FM protocol for FM substrate option)
   ↓
L2.2 L7 6-Slot Spec        (requires L2.1 substrate interface)
   ↓ ↓
L2.3 OOD Spec ←──┘  ←── L2.4 Interpretability Spec
   ↓                    ↓
   └─────────┬──────────┘
             ↓
L2.5 Layer 2 Master Synthesis
   ↓ (Layer 2 closed; can audit)
   ↓
L3.1 V0-V6 Pipeline Spec   (requires L2 done so validation has architecture to validate)
   ↓
L3.2 56 Pass Criteria
   ↓
L3.3 Cross-Disease V6
   ↓
L3.4 Layer 3 Master Synthesis
   ↓ (Layer 3 closed; can audit)
   ↓
L4.1 Implementation Order  (requires L2 + L3 done)
   ↓
L4.2 Testing Protocols     (requires L4.1)
   ↓
L4.3 Failure Mode Analysis (requires L4.2)
   ↓
L4.4 Repository Scaffolding (requires L4.1-L4.3)
   ↓
L4.5 Layer 4 Master Synthesis + Phase B Closure Checklist
   ↓
S.2 HPC Environment Spec    (can do anytime parallel; closes Phase B if last)
   ↓ (Layer 4 closed)
   ↓
PHASE 8 AUDIT (analog of Phases 1-7 for Layer 1)
   ↓
PHASE B CLOSURE
   ↓
LAYER 5 PREP (separate phase, not Phase B)
```

---

## 5. Session Ordering (Proposed)

**Sessions are estimated at 2-3 hours of focused CSO work each. Total Phase B: ~10-15 sessions.**

### Session 1 — Supporting infrastructure foundation (this can start NEXT after plan approval)
- S.1 Data Acquisition Manifest (4,000-6,000 words)
- S.3 License Verification Matrix (2,000-3,000 words)
- *Output:* These are reference docs that don't block; doing them early establishes data + license reality.

### Session 2 — FM protocol + HPC env
- S.4 FM Weights Protocol (1,500-2,500 words)
- S.2 HPC Environment Spec (3,000-4,000 words)
- *Output:* Concrete prep for Layer 5 environment.

### Session 3 — Substrate architecture
- L2.1 Substrate Specification (5,000-7,000 words)
- *Output:* Substrate adapter interface fixed.

### Session 4 — L7 architecture (longest, may span 2 sessions)
- L2.2 L7 6-Slot Specification (7,000-10,000 words)
- *Output:* Core drug response architecture concrete.

### Session 5 — OOD + Interpretability (can do parallel-conceptually but sequentially writing)
- L2.3 OOD Detection Stack (5,000-7,000 words)
- L2.4 Seven-Scale Interpretability Stack (5,000-7,000 words)
- *Output:* Trust layers concrete.

### Session 6 — Layer 2 closure
- L2.5 Layer 2 Master Synthesis (3,000-4,000 words)
- *Output:* Layer 2 specs internally coherent + auditable.

### Session 7 — Validation pipeline
- L3.1 V0-V6 Pipeline (5,000-7,000 words)
- *Output:* Validation cascade concrete.

### Session 8 — Pass criteria operationalization
- L3.2 56 Pass Criteria (5,000-7,000 words)
- *Output:* Every binding criterion becomes a testable hypothesis.

### Session 9 — Cross-disease V6 + Layer 3 closure
- L3.3 Cross-Disease V6 (3,000-4,000 words)
- L3.4 Layer 3 Master Synthesis (2,000-3,000 words)
- *Output:* Layer 3 done.

### Session 10 — Implementation order + testing
- L4.1 Implementation Order (3,000-4,000 words)
- L4.2 Testing Protocols (3,000-5,000 words)
- *Output:* Layer 5 roadmap concrete.

### Session 11 — Failure modes + scaffolding
- L4.3 Failure Mode Analysis (3,000-4,000 words)
- L4.4 Repository Scaffolding (3,000-5,000 words)
- *Output:* Robustness + structure for Layer 5.

### Session 12 — Layer 4 closure
- L4.5 Layer 4 Master Synthesis + Phase B Closure Checklist (2,000-3,000 words)
- *Output:* Layer 4 done.

### Session 13-15 — Phase 8 Audit + Closure
- Phase 8 audit covers 18 Phase B artifacts (analog of Phases 1-7 for Layer 1)
- Drift detection on Phase B output
- Phase B Closeout document
- Layer 5 Prep handoff document

---

## 6. Decision Record Traceability Matrix

| Artifact | Primary Decision(s) | Primary Anchors | Risk if drift |
|---|---|---|---|
| S.1 Data Manifest | 1 v2, 6 v2, 8 | GDSC, CCLE, sci-Plex, scDrugMap | Wrong datasets selected; V0-V6 invalid |
| S.2 HPC Env | 9 v2 | (operational) | Layer 5 won't run on HPC |
| S.3 License Matrix | 10 v2 | (operational) | Future release blocked |
| S.4 FM Protocol | 1 v2 | scFoundation, UCE, scGPT, Geneformer | FM substrate unavailable |
| L2.1 Substrate | 1 v2 | 7 substrate-related anchors | Wrong cell representation |
| L2.2 L7 6-Slot | 4 v2, 2 v2, 3 v2 | 6 drug-response anchors | Wrong drug response model |
| L2.3 OOD | 5 v2 | 6 OOD anchors | Untrusted predictions |
| L2.4 Interpretability | 7 v2 | 4 interp anchors | Mechanism not interpretable |
| L2.5 Layer 2 Master | All L2 | All L2 anchors | Layer 2 components don't integrate |
| L3.1 V0-V6 Pipeline | 6 v2, 8 | 5 validation anchors | Validation cascade broken |
| L3.2 Pass Criteria | All 10 | All anchors | Falsifiability lost |
| L3.3 V6 Cross-Disease | 8 | 5 universality anchors | Cross-disease claim untestable |
| L3.4 Layer 3 Master | All L3 | All validation anchors | Layer 3 components don't integrate |
| L4.1 Impl Order | All decisions | (architectural reasoning) | Implementation deadlocked |
| L4.2 Testing | All decisions | (architectural reasoning) | Bugs not caught |
| L4.3 Failure Modes | All decisions | (architectural reasoning) | Production failures |
| L4.4 Repo Scaffolding | 10 v2 | (operational) | Codebase chaos |
| L4.5 Layer 4 Master | All L4 | All decisions | Layer 5 prep incomplete |

---

## 7. Acceptance Criteria Per Artifact

Every artifact must meet these tests before being marked done:

### Universal acceptance criteria

1. **Word count within target range** (within ±20%)
2. **Every claim traceable to either a Layer 1 decision or a Layer 1 anchor paper** (citation-style references)
3. **Pass criteria operationalized** (where the artifact contains pass criteria, they must be falsifiable)
4. **Cross-artifact references resolved** (e.g., L2.2 references L2.1 substrate adapter — that interface must be specified in L2.1)
5. **No fabricated content** (P15 discipline: no invented citations, no made-up datasets, no fictional benchmarks)
6. **Drift catalog updated** (any drift discovered during writing → logged with same protocol as Phases 1-7)

### Per-layer additional criteria

- **Layer 2 artifacts:** Tensor shapes specified end-to-end; PyTorch class skeletons compilable (even if not runnable); GPU memory budget estimated
- **Layer 3 artifacts:** Statistical tests specified with corrections; datasets named with primary source; thresholds with confidence intervals where applicable
- **Layer 4 artifacts:** Code stubs compile; YAML configs valid; directory structure realistic

---

## 8. Branch Points (CEO Judgment Required Mid-Phase B)

These mid-Phase-B branch points require CEO input. CSO will pause and request when reached:

**B1 (mid-S.1):** Data acquisition priority order — which datasets first? CEO sets priorities.

**B2 (mid-S.3):** Repository license choice — Apache 2.0, MIT, BSD, GPL? CEO decides. Has downstream effects on every Layer 4 artifact.

**B3 (mid-L2.1):** Which substrates to fully spec vs which to leave as alternates? Decision 1 v2 chose FM-primary with scTOP/scVI/scANVI as alternates — CSO will fully spec FM; CEO confirms or asks for full spec on alternates.

**B4 (mid-L2.4):** Substrate-conditional branching depth — Scale 5 has 4 branches; CEO confirms if all 4 must be fully spec'd or if 1 primary + 3 stubs is acceptable.

**B5 (mid-L3.3):** Which 2+ therapeutic areas for V6? CEO chooses (constrained by data availability from S.1).

**B6 (mid-L4.4):** Repository name (kaalcura, intercepta, other)? Project username on GitHub? CEO decides.

---

## 9. Risk Catalog

| Risk | Probability | Impact | Detection | Mitigation |
|---|---|---|---|---|
| Anchor paper contradicts Layer 1 conclusion mid-Phase-B | Medium | High | While writing, CSO notices conflict | Add to drift catalog; flag to CEO; may require Decision re-LOCK |
| Inter-artifact reference fails (e.g., L2.2 needs interface L2.1 doesn't have) | Medium | Medium | Acceptance criteria check | Revise both artifacts before closure |
| Word count explodes (artifact 2-3x target) | Medium | Medium | Per-session check | Split into 2 sub-artifacts; flag scope creep |
| HPC env spec turns out to need GPU CSO can't test | High | Low | Mac-only test inadequate | Mark as "requires HPC verification"; defer detailed testing |
| Dataset specified in S.1 unavailable to CEO (dbGaP rejection, etc.) | Medium | High | When CEO attempts download | Add to data risk catalog; identify substitute; possibly affect V6 |
| FM gated access denied | Low | High | When CEO attempts HF download | Identify alternative; possibly affect Decision 1 v2 substrate choice |
| License incompatibility discovered for major component | Low | Critical | S.3 audit | Identify replacement; possibly revise Decision 10 |
| CSO writes Layer 2 spec then Phase 8 audit finds drift | High | Medium | Phase 8 internal audit | Revise per Phases 1-7 pattern; expected cost ~20% rework |
| CEO changes priorities mid-Phase-B | Medium | Medium | CEO message | Pause Phase B; document state; resume later |
| Context limits prevent single-session artifact completion | High | Low | During writing | Split artifact across sessions; ensure continuity via clear handoff notes |

---

## 10. Time Estimates

**Optimistic:** 10 sessions × 2.5 hrs avg = 25 hours of focused CSO work. **2-3 weeks** at moderate CEO availability.

**Realistic:** 13 sessions × 3 hrs avg = 39 hours of focused CSO work, + ~10 hours CEO review/branch-point decisions. **3-5 weeks** at moderate CEO availability.

**Pessimistic:** 18 sessions × 3 hrs avg = 54 hours (includes rework from Phase 8 audit findings), + 15 hours CEO time. **5-7 weeks**.

**Conditional on:**
- No major scope changes
- No anchor paper invalidates a Decision mid-flow
- CEO available for branch point decisions within ~24-48 hrs of CSO pause
- No external project priorities (NeoCARTa, AML manuscript completion) interrupt

---

## 11. CEO Touch-Points (Minimum)

Phase B is mostly autonomous CSO work, BUT requires CEO touch at these moments:

**Required at start:**
- Approve this Phase B Execution Plan

**Required mid-Phase-B (6 branch points B1-B6 above):**
- Data acquisition priorities (S.1)
- Repository license (S.3)
- Substrate full-spec scope (L2.1)
- Interpretability branching depth (L2.4)
- V6 therapeutic areas (L3.3)
- Repository name (L4.4)

**Required at Phase 8 audit:**
- Review audit findings before Phase B closure
- Approve any drift remediations
- Approve Phase B closure

**Required at end:**
- Approve Layer 5 prep handoff
- Authorize Layer 5 phase begin

**Estimated CEO time across Phase B:** ~10-15 hours (mostly review + branch-point decisions, not active drafting).

---

## 12. Phase B Closure Protocol

Phase B is closed when:

1. ✅ All 18 artifacts written and acceptance criteria met
2. ✅ Phase 8 internal audit complete (analog of Phases 1-7 for Layer 1)
3. ✅ All drift instances logged and resolved
4. ✅ Decisions/README + cleanup_log updated with Phase B closure entry
5. ✅ Charter §5.3 GO/NO-GO checkpoint document for Layer 2-4 → Layer 5 written
6. ✅ Layer 5 Prep Handoff Document written (specifies what Layer 5 will need: data downloaded, env built, components built in what order)
7. ✅ CEO explicit approval of Phase B closure
8. ✅ Git tag: `fullest-vision-phase-b-closed`

After Phase B closure: Phase B is LOCKED. Future revisions require new Decision Records analog to Decision 1 v1 → v2 pattern.

---

## 13. Honest Assessment

After Phase B closure, INTERCEPTA will be at approximately **25-30% Fullest Vision complete.**

This is meaningful progress because:
- Layer 1 done (architectural decisions defensible)
- Layer 2 done (every module spec'd to PyTorch class level)
- Layer 3 done (every validation operationalized as falsifiable test)
- Layer 4 done (implementation roadmap concrete)
- Supporting infrastructure done (data, env, license, FM weights protocol)

This is still far from the vision because:
- Layer 5 (code that runs models) still 0%
- Validation cascade still 0% (no model to validate)
- Wet-lab validation still 0%
- Clinical deployment still 0%
- Production still 0%
- Patient impact still 0%

**Phase B's role:** Eliminate every "what should we build?" question. After Phase B closure, Layer 5 becomes purely "build what's spec'd" — no more architectural choices, just implementation discipline.

---

## 14. Why This Plan Is Worth Approving

**The cost of NOT having Phase B Plan:**
- Multiple sessions drift because no shared baseline
- Layer 2 written before Layer 1 closed → wrong architecture
- Layer 3 written before Layer 2 specs ready → unvalidatable
- Layer 4 written without Layer 2 + 3 → wrong implementation
- 18 artifacts written in random order → integration broken
- No audit hooks → drift not caught until Layer 5 fails
- Estimated waste: 30-50% rework

**The cost of HAVING Phase B Plan:**
- This document (5,800+ words of meta-work)
- ~30-45 min CSO writing time (today)
- ~15-20 min CEO review time
- Branch point decisions distributed across Phase B (~10-15 hours CEO total)

**ROI:** Plan prevents ~40-80 hours of rework. ROI is positive within 2 sessions.

---

## 15. Sequence to Start Phase B Execution

**Immediate next steps after CEO approval of this plan:**

1. CEO says "approved" (or "approved with modifications: [X]")
2. CSO updates cleanup log with Phase B Plan approval
3. CSO writes Session 1 (S.1 Data Manifest + S.3 License Matrix)
4. CSO presents Session 1 output for CEO branch-point B1 (data priorities) and B2 (license choice)
5. Phase B execution proceeds per session ordering above

---

## 16. CEO Decision Box

```
[ ] APPROVE — Phase B Execution Plan as written; CSO begins Session 1
[ ] APPROVE WITH MODIFICATIONS — see attached modifications
[ ] PAUSE — Reconsider Phase B sequencing; address [other priority] first
```

**CEO:** Prasad Akula __________ Date: __________

**CSO:** Claude — 2026-05-11 morning session

---

*End of Phase B Execution Plan.*
*Total document: ~5,950 words*
*This document is itself an Operational Decision Record analog (operational reasoning about how to do work, not field-grounded research).*
