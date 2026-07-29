# INTERCEPTA Architecture Review — v2 (Revised on full project bundle)

**Author:** Claude (CSO/AI co-founder), under instruction from Prasad Akula
**Date:** 2026-05-06
**Supersedes:** INTERCEPTA_Architecture_Review.md (v1, 2026-05-06)
**Mode:** Direct push-back enabled. v1 review's wrong claims named directly. No diplomatic softening.
**Source:** Full project bundle read — 121 files including governance docs, deliverable references, .docx specs (where extractable), original pipeline + ODE + KAALCURA + Round 2 AML code, Round 1/2/3 closure documents, CSO memos, audit results.

---

## Executive verdict (read this first)

**The v1 review was too narrow.** It analyzed only the Round 3 GBM wrapper code (`intercepta_pipeline_v0.py`, `generate_pharma_deliverable.py`, `validate_workstream_a_gbm.py`) as if those were the project. They are a small subset. The actual INTERCEPTA project has:

- **~75 Python files in `~/INTERCEPTA/code/`** including the original mCRPC pipeline, four ODE versions, KAALCURA, Pareto ranking, synergy scoring, six audit/test files, scout modules, and step-by-step net builders
- **Round 2 AML in its own subproject** (`~/INTERCEPTA/round2_aml/`) with separate code, data, docs, and 7 closure/specification documents covering Round 2.1a through 2.2b
- **A documentation tier I had not read** including `MASTER_FIXES.md` (8.5KB), `CLAUDE.md` (7KB AI co-founder onboarding), CSO Memo v2 + v2.1, Round 1 Retrospective, Validation Limitations v1, and 11 .docx specifications in `/docs/`
- **A canonical 10-item pharma deliverable** at `pharma_deliverable_enza_alis.json` with real content (SMILES, mechanism, ODE-derived predictions, biomarker stratification) for enza+alisertib in mCRPC
- **A documented honest record of Round 1 closing FAIL** on quantitative validation (0/3 g-rate targets pass, 6/6 trials fail acceptance windows) with directional ranking confirmed and structural limits identified

**Round 3 GBM was framed as a Workstream A universality live test** — not a deviation from the vision sequence as I implied in v1. The Round 3 closure document explicitly defined the B vs C fork before this session began.

**Revised verdict:**

The project foundation has more substance than v1 acknowledged. Specifically:
- The phenotype ODE that produced docetaxel HR=0.675 zero-tuned is real Round 1 work (`intercepta_phenotype_ode_v1.py`, 49KB) — but Round 1 retrospective documents it as directionally correct, quantitatively limited (g-rate 0.36× Stein, etc.)
- Pareto ranking exists at `pareto_ranking.py` (9.5KB) — my v1 said it didn't. CLAUDE.md (Apr 18) lists Pareto as "NOT STARTED" but the file dates from after that.
- The hand-written 10-item deliverable for enza+alisertib is the architectural template Workstream A's deliverable generator should produce automatically. It has 10 items including item_5_combination_rationale, which is N/A in monotherapy candidates.

**The required refactor scope is SMALLER than v1 implied.** Workstream A's three files do need refactoring. But the proposed package structure in v1 was wrong because it ignored what already exists. The right refactor:

1. Don't create `intercepta/` from scratch. Use the existing `~/INTERCEPTA/code/` and `~/INTERCEPTA/round3_gbm_live_test/code/` structure but split the wrapper file's god-functions and extract per-disease config.
2. Reuse the canonical 10-item deliverable shape (from `pharma_deliverable_enza_alis.json`), not the simplified 4-statuses (DELIVERED/PARTIAL/GAP/N/A) shape I built.
3. Recognize the `_disease_to_tissue_keywords` heuristic as a documented limit per Round 3 closure §3.2 Finding 15 — it's a known limit with a path forward (supplementary data sources), not just a 9-disease blocker.

**The B vs C fork is already documented in Round 3 closure §7.** The CSO recommendation already made there is "B before C, sequential" with NSCLC as Workstream B target. Re-deciding this fork is not the architecture review's job. The architecture review's job is to assess whether the foundation supports either workstream and how to refactor only what blocks them.

I will defend this verdict in detail below.

---

## Section 0 — What the v1 review got WRONG (named directly)

For honesty per project Principle 15. Each numbered item is a mistake in v1.

**M1.** v1 said "the only existing 9/9 hand-written deliverable is for enza+alisertib." Incorrect on two counts: it's 10/10 (item_1 through item_10, including item_5_combination_rationale), and there's a second multi-candidate deliverable at `pharma_deliverable_complete.json` with 3 candidates and a 9-item schema (different schema in same project — itself an architectural drift I missed).

**M2.** v1 said "Pareto ranking is missing from the proposed architecture." But `pareto_ranking.py` (9.5KB) exists in `~/INTERCEPTA/code/` and is referenced in `pharma_deliverable_enza_alis.json` (`pareto_rank: 1, composite_score: 76.5`). v1 didn't mention Pareto because v1 hadn't read the existing `code/` directory.

**M3.** v1 framed Round 3 GBM live test as "what we did this session." Round 3 closure document predates this session (dated 2026-05-06 morning, but written before this conversation's deep-work resumed). The B vs C fork was defined in §7 of that closure with CSO recommendation already on record. v1 treated the fork as if it were a new architectural decision.

**M4.** v1 claimed "the foundation is sound for the disease-net infrastructure but ranking and deliverable need work." The actual state is more nuanced: Round 1 closed with mCRPC ODE quantitatively wrong but directionally correct (0/3 g-rate targets pass per CSO Memo v2.1 §4); Round 2 closed Round 2.2a as FAIL on locked spec but produced first validated cross-dataset drug prediction (Q_D PASS, Spearman ρ = −0.235); Round 2.2b was scoped but no closure document exists in the bundle (open question whether 2.2b ran). v1 read "the closure document" too literally as if it were the project's full state.

**M5.** v1 said "v2 ranking was the wrong design choice in Session 2." Partially true but missing context: v2 was a response to v1 ranking failing on GBM SOC recovery (TMZ rank 247/286). The deeper issue isn't v2's god-function structure — it's that GDSC alone cannot produce clinically relevant rankings for any disease where mechanism-of-action is encoded as a string ("DNA alkylation") rather than gene-symbol target. This is named as "Finding 15" in Round 3 closure with documented supplementary-data-source path forward. v1's critique was code-architectural; the deeper critique is data-source-architectural.

**M6.** v1 proposed creating `intercepta/` package from scratch. This ignored the existing `~/INTERCEPTA/code/` directory which has the original pipeline architecture. A refactor that creates a new package without integrating the existing one is just adding a third pipeline (Round 1 + Round 2 + new). The right refactor reorganizes within the existing project structure, preserves Round 1 and Round 2 artifacts, and adds clarity to the wrapper code.

**M7.** v1 said the GBM 2/10 average DELIVERED is "honest baseline." Honest yes, but missing context: the canonical 10/10 reference (enza+alisertib mCRPC) was built when Round 1 considered itself validated. Round 1 retrospective subsequently documented that 6/6 trials fail acceptance windows and 0/3 g-rate targets pass. **The 10/10 reference contains stale post-fix-broken numbers.** The right framing: GBM at 2/10 reflects the pipeline's actual current state for a non-mCRPC disease; the mCRPC 10/10 reflects Round 1 work that has since been honestly downgraded to "directional ranking only."

**M8.** v1 didn't mention `MASTER_FIXES.md` or its 9 P1+P2 fixes. Several of these fixes are directly relevant to the architecture review:
- FIX-001 (HR estimator) — completed Apr 18
- FIX-002 (AML ODE relapse) — status unclear
- FIX-003 (KAALCURA on real GDSC) — status partial per Round 2 documentation
- FIX-004 (Scout 4 Boolean network) — partial; `scout4_boolean_network.py` exists at 12KB
- FIX-005 through FIX-009 — mostly parameter/claim cleanups
v1 implicitly assumed these were done. Several are still open.

**M9.** v1 claimed "the current foundation is sound enough to build Workstream B (ODE generalization to NSCLC) on, with refactor first." This is too strong given Round 1's quantitative failure on its own validation framework. The honest framing: Workstream B's central question (does phenotype ODE generalize?) is more uncertain than v1 implied because Round 1 documented that the mCRPC ODE itself doesn't pass its own g-rate targets. Workstream B may discover that the answer is "the framework needs structural changes, not just parameter generalization" — which is a legitimate scientific outcome, but it changes the work plan.

---

## Section 1 — What Workstream A actually is (corrected scope)

Workstream A per Plan v2 §5 and Round 3 closure §2:

**Workstream A is the any-disease enrichment pipeline.** It takes a disease query (name or ontology ID) and produces an enriched disease net containing gene associations, pathway annotations, STRING interactions, AlphaFold structure URLs, ChEMBL compounds + bioactivity + properties, ClinicalTrials.gov trials, and surfaced undruggable priority targets.

Workstream A is implemented as a wrapper around the existing `disease_net_builder.py` (8KB, in `~/INTERCEPTA/code/`). The wrapper file is `~/INTERCEPTA/round3_gbm_live_test/code/intercepta_pipeline_v0.py` (~2300 lines). The wrapper:
1. Loads the upstream `DiseaseNetBuilder` as a singleton
2. Adds disease resolution by name → EFO ID with EFO preference
3. Adds Phase 2A metabolite joining
4. Adds Phase 2B STRING any-disease enrichment from full STRING v12
5. Adds Phase 2C AlphaFold any-disease enrichment via UniProt REST API
6. Adds Phase 2D ChEMBL bioactivity enrichment with disk caching
7. Adds Phase 2E ClinicalTrials.gov enrichment with disk caching
8. (Session 1 extension) Adds BBB augmentation via CNS MPO 4-component score
9. (Session 2 extension) Adds composite multi-evidence ranking with BBB gating
10. (Action 1 cleanup) Three drift fixes for ChEMBL target lookup, summary printing, undruggable surfacing

What Workstream A is NOT:
- Not a new ODE (existing ODE is mCRPC-specific per Round 3 closure §3.3 Finding 18)
- Not a new ranking layer (the existing Pareto ranking from Round 1 is for combinations; v2 in Workstream A is for monotherapy GDSC drugs)
- Not a refactor of disease_net_builder (preserves it per P16)
- Not a new pharma deliverable spec (the 10-item spec is from Vision 9.1 and reference is `pharma_deliverable_enza_alis.json`)

**This corrects v1's framing.** v1 treated Workstream A as if it were the project's primary pipeline. It's a wrapper layer for any-disease support of the existing infrastructure.

---

## Section 2 — File-by-file audit (revised with full project context)

### 2.1 — Workstream A wrapper (`round3_gbm_live_test/code/intercepta_pipeline_v0.py`)

v1's audit of this file is mostly accurate. 36 functions in ~2300 lines. The 23 architectural drifts I identified for this file in v1 stand, with these revisions:

- **Drift #1 (two ranking functions v1 and v2):** v1 said "overlapping concerns." More precise: v1 ranking is GDSC-only (Phase 2A); v2 ranking is multi-evidence with BBB (Session 2). They serve different purposes per the project's actual development history. Both should be preserved per P16. The architectural fix is to make them clearly named (e.g., `rank_drugs_gdsc_only` and `rank_drugs_multi_evidence_v2`) rather than v1/v2 versioning that hides their semantic difference.

- **Drift #4 (v2 god-function):** Stands. The fix is to require an enriched net as input rather than calling enrichment internally.

- **Drift #11 (populate_chembl_compounds god-function):** Stands. Should split into 3 functions (fetch, augment, populate-net).

- **Drift #15 (cns_disease=False default in undruggable surfacing):** Stands. Should auto-detect from net's disease name, reusing the same logic as v2 ranking.

### 2.2 — Workstream A deliverable (`round3_gbm_live_test/code/generate_pharma_deliverable.py`)

v1's audit is mostly accurate but missed the most important issue:

**The deliverable script's 10-item schema does not match the canonical 10-item schema.** Canonical (from `pharma_deliverable_enza_alis.json`):
1. molecular_structure (with smiles + mechanism + status)
2. mechanism_of_action (escape route + net evidence + literature)
3. predicted_outcomes (model + drug-alone + combination_NE_high + combination_NE_low + honest_limitations)
4. resistance_profile (sensitive_population + resistant_populations + predicted_composition_2y + residual_risk)
5. combination_rationale (drug_a_role + drug_b_role + non_overlapping + synergy_type + synergy_score)
6. safety_profile (per-drug AEs + source + combination_prediction + ADMET_computed)
7. synthesis (per-drug commercial + published synthesis + novel molecules)
8. novelty (clinicaltrials_search + result + note)
9. vs_standard (current_standard + standard_PFS + our_prediction_per_subgroup + key_advantage)
10. trial_design (phase + population + biomarker + arms + primary_endpoint + secondary + sample_size + rationale)

**Plus a top-level `honest_assessment` block** with what_is_real / what_is_predicted / what_is_NOT_done. **Plus pareto_rank and composite_score.**

My GBM deliverable script uses a different shape (item_01 through item_10 with status/content/requirements). The status field (DELIVERED/PARTIAL/GAP/N/A) is my invention, not in the canonical schema.

**Architectural fix:** match the canonical schema. Items where data is unavailable should explicitly say `"available": false, "requires": "Workstream B/C"` inside the existing schema's structure, not introduce a parallel taxonomy.

### 2.3 — Workstream A validation (`round3_gbm_live_test/code/validate_workstream_a_gbm.py`)

v1's audit stands. 6 tests, hardcoded GBM ground truth, Test 1 calls v1 ranking not v2, Test 3 BBB stale. Issues real.

Add: the project has its own validation framework patterns from Round 2 (the Q_A through Q_F gate system per `INTERCEPTA_Round2_2a_Specification.md`). My validation script invented its own pattern instead of following the project's existing pattern. **The right fix is to model validation gates on the Round 2 spec template** (locked spec before code, gates with explicit pass criteria, FAIL-aware closure documents, scientific findings preserved separately from gate outcomes).

### 2.4 — Original pipeline (`code/intercepta_pipeline.py`, 43KB)

I have not read this file in detail in this revision. Bundle includes it. Reading it is the next step before any refactor of the wrapper. v1 review proposed creating new `intercepta/` package; the right move is to FIRST read the original pipeline to understand its module organization, THEN decide what to refactor.

### 2.5 — Original ODE files (`code/intercepta_phenotype_ode_v1.py` 49KB, `_unified_ode_v4_1.py` 43KB)

The phenotype ODE is the Apr 7 mCRPC breakthrough. Round 1 retrospective documents it as quantitatively limited (g = 0.36× Stein for untreated mCRPC) but directionally correct. Workstream B's central question is whether this generalizes.

Architecturally significant facts I missed in v1:
- The unified ODE has 4 cell states with hardcoded constants S_ARDEP, S_ARMUT, S_ARV7, S_NE — Round 3 closure §3.3 Finding 18 confirms this
- 7 drugs total parameterized across all 4 ODE modules
- Generalization requires either adding new state types per disease or refactoring states as configurable input
- Workstream C scope per Plan v2 (6-8 weeks) — the Universal ODE refactor

### 2.6 — KAALCURA + calibration (`code/intercepta_kaalcura_v1.py` 46KB, etc.)

KAALCURA is the gene-axis scoring layer (R_prolif, R_emt, R_ddr) per CLAUDE.md. Validated AUROC 0.638 across 286 drugs × 962 cell lines but on **synthetic data per FIX-003** in MASTER_FIXES.md. Real GDSC validation status: partial. Round 2.2a tested pyUCell-based variant on cross-modality (BeatAML bulk → Van Galen scRNA-seq cell-types) and got mixed results (Q_C mean CV-AUROC 0.532 within-dataset; Q_D Spearman ρ = −0.235 cross-dataset).

**KAALCURA is NOT in Workstream A's wrapper.** The wrapper builds disease nets without invoking KAALCURA. This is a real gap: a wrapper that produces disease nets for any disease but doesn't compute KAALCURA scores for cells in those diseases is missing a layer the vision specifies.

### 2.7 — Pareto ranking (`code/pareto_ranking.py` 9.5KB)

Exists. v1 said it didn't. CLAUDE.md (Apr 18) listed it as "NOT STARTED" but the file is 9.5KB and the canonical deliverable references it (`pareto_rank: 1, composite_score: 76.5`).

**Probable status:** Built between Apr 18 and the end of Round 1 cycle (Apr 21-22). Used in `pharma_deliverable_enza_alis.json` to rank the 3 mCRPC candidates. Not yet integrated into Workstream A (the wrapper) — the wrapper's v2 composite ranking is a different algorithm, not Pareto.

**Architectural drift:** Workstream A's `rank_drugs_for_disease_v2` is a multi-evidence COMPOSITE ranking. The existing `pareto_ranking.py` is a multi-objective PARETO ranking. These are different mathematical operations. The wrapper invented a new ranking function instead of integrating the existing Pareto one. v1 missed this entirely.

### 2.8 — Synergy scoring (`code/synergy_scoring.py` 15KB)

Exists. CLAUDE.md (Apr 18) lists it as "NOT STARTED." Like Pareto, probably built later. The deliverable references "Sequential population targeting (not pharmacological synergy)" — meaning enza+alisertib is NOT scored by synergy because they target different populations. So synergy scoring may not have been used in the canonical mCRPC deliverable, but it exists.

### 2.9 — Round 2 AML build (round2_aml/code/, 9 files)

Round 2 produced multiple AML net versions: skeleton → skeleton_v2 → v3_integrated → v4_integrated → v5_kaalcura → v5_2_kaalcura. Round 2.2a is the latest closed state. Round 2.2b was specified but no closure document is in the bundle.

**This is highly relevant for refactor architecture.** The Round 2 AML team built per-version files preserving each iteration. This is the project's own answer to "how do we organize multiple versions of the same pipeline?" Not a new package; per-version files in a subproject directory. The Workstream A refactor should follow this pattern.

### 2.10 — Audit infrastructure

Six audit-related files in `~/INTERCEPTA/code/`:
- `audit_all_steps.py` (2KB)
- `exhaustive_audit.py` (32KB)
- `vision_alignment_audit.py` (34KB)
- `truth_audit.py` (24KB)
- `pre_rebuild_audit.py` (23KB)
- `intercepta_capability_test.py`

These are how the project audits itself. v1 review didn't mention them. The Apr 9 5-Level Audit and Apr 22 Exhaustive Audit referenced in Round 3 closure are outputs of these scripts. Any refactor that doesn't preserve or update these audit scripts loses the project's ability to self-check.

---

## Section 3 — Documentation tier I had not read in v1

The project has a documentation tier I did not access in v1:

**`CLAUDE.md`** (7KB, Apr 18) — AI co-founder onboarding. Contains the "honest current status," "what to NOT claim," "key validated findings," and "44-level test results." Most critically:
> **❌ "Pharma deliverable" — say "computational hypothesis package"**

This is in direct tension with Vision 9.1's "10-item pharma deliverable." Either CLAUDE.md is more cautious than the vision intends, or the vision aspires beyond what's currently honest. **My v1 review used "pharma deliverable" 47 times without acknowledging this terminology disclaimer.**

**`MASTER_FIXES.md`** (8.5KB, Apr 18) — 9 fixes documented with file locations, root causes, fix references. P1 fixes (4 items) "break core claims." P2 fixes (5 items) are weak claims. P3 builds (4 items) NOT STARTED. The status of each fix is the most honest snapshot I've read.

**`PROJECT_STATUS.md`** (4KB, Mar 29) — Phases A and B build status. Steps 1-7 complete. Phase C (universal expansion) outlined as Steps 8-20.

**`INTERCEPTA_STATUS.md`** (1.8KB, Apr 9 with Apr 18 update) — completion percentage, validated results, honest record. Apr 18 update notes HR estimator fix and 5-trial validation correction (5/5 PASS → 3/5 PASS with real Cox PH).

**`NEXT_SESSION.md`** (1.5KB, Apr 8) — what was planned next. Lists 7 remaining builds. Mostly outdated (Pareto, synergy, ODEs since built).

**`AUDIT_ACTION_PLAN.md`** (893B) — 5 parameter fixes + 5 claim fixes from earlier audit cycle. Most claim fixes done.

**`PUBLICATION_OUTLINE.md`** (3KB) — not yet read in detail. Likely the pre-publication structure.

**`VISION_AUDIT.txt`, `PRE_REBUILD_AUDIT.txt`, `EXHAUSTIVE_AUDIT.txt`** — large text outputs of audit scripts. Not yet read in detail.

**`/docs/` directory:**
- 6 markdown docs (CSO Memo v2 + v2.1, Round 1 Errata, Round 1 Retrospective, Round 2 AML Kickoff, Validation Limitations v1) — read in this revision
- 11 .docx specs — 7 failed to extract (probably encrypted or non-Word format), 3 extracted (Universal Net Spec, Phase 1 Validation Report, Complete Status Report)

The .docx that didn't extract include:
- `INTERCEPTA_COMPLETE_VISION_v1_0.docx` (62KB) — the founding vision document
- `INTERCEPTA_Net_Architecture_v2_0.docx` (25KB) — **architecture document at v2.0 already exists**
- `INTERCEPTA_Phase1_MathSpec_v1_0.docx` (19KB) — math specification
- `INTERCEPTA_Phase1_GroundTruth_v1_0.docx` (17KB) — formal ground truth
- `INTERCEPTA_Phase1_DataSourceAudit_v1_0.docx` (30KB) — data source audit
- `INTERCEPTA_Strategic_Roadmap_v1_0.docx` (14KB) — roadmap
- `INTERCEPTA_DOCC.docx` (52KB) — purpose unclear

**These 7 documents need to be read before any major architectural decisions.** Especially `INTERCEPTA_Net_Architecture_v2_0.docx` which is the project's existing architecture document. v1 architecture review proposed a new structure WITHOUT reading the existing architecture spec. That's a P3 (deep research before code) violation by the architecture review itself.

To extract these, alternative approaches: try LibreOffice headless conversion, try `pandoc`, try opening in Word and re-saving as .docx, or have Prasad export them as .md/.txt.

---

## Section 4 — Honest project chronology (corrected)

Reading bundle in chronological order:

**March 29, 2026** — `PROJECT_STATUS.md` written. Phases A+B complete (Steps 1-7). Phase C (Steps 8-20, universal expansion) outlined.

**April 7, 2026** — Phenotype ODE breakthrough. Docetaxel HR=0.675 zero-tuned per session memory. Round 1 retrospective subsequently confirms this directionally; quantitatively the model g = 0.36× Stein.

**April 8, 2026** — `NEXT_SESSION.md` written. 7 remaining builds (Scout 4 v2, Unified ODE, Synergy, AML ODE, ADMET, Synthesizability, Pareto).

**April 9, 2026** — Apr 9 5-Level Audit. 46% pass rate at deepest level. 3 critical findings (0/286 drugs ineffective, pharma package 1/9 items, novel molecules unverified). `INTERCEPTA_STATUS.md` written: 79% completion claimed.

**April 9-17, 2026** — `pharma_deliverable_enza_alis.json` written (10 items, Pareto rank 1, composite 76.5). `pharma_deliverable_complete.json` written (3 candidates, 9 items each — different schema).

**April 18, 2026** — `CLAUDE.md` and `MASTER_FIXES.md` written. HR estimator fixed (median ratio → Cox PH/log-rank). 5-trial validation re-run: 5/5 PASS → 3/5 PASS with real Cox PH. `hr_estimator_fixed.py` added. 44-level test: 37/44 (84%). emax recalibration found (0.010 → 0.05). ATM PDB found corrupted.

**April 21, 2026** — Round 1 Retrospective written. Round 1 closed at v4.1. CSO Parameter Memo v2.1 written. v4.1 olaparib run produces "complete cytoreduction without resistance regrowth" — limitation #7 added (PARP-specific evolved resistance not modeled).

**April 22, 2026** — Round 2 AML Kickoff. Round 2.2a closure (FAIL on locked spec, 3/5 gates failed but Q_D and Q_E PASS — first validated cross-dataset drug prediction). Round 2.2b specification written, pre-code commit. Apr 22 Exhaustive Audit (103 checks, 3 discrepancies all RESOLVED).

**April 22 → May 4, 2026** — Status unclear. Round 2.2b implementation status not in bundle.

**May 4-6, 2026** — Round 3 GBM live test. Workstream A wrapper built (Phases 1, 2A, 2B, 2C, 2D, 2E). Round 3 closure document drafted (`INTERCEPTA_Pipeline_v0_Closure.md`). Workstream A operationally closed; B vs C fork defined with CSO recommendation B before C.

**May 6, 2026 (today, this session)** — Action 1 cleanup (3 drift fixes), Phase 2E ClinicalTrials integration, Session 1 BBB extension, Session 2 v2 composite ranking, validation against GBM ground truth (5 tests: 2 PASS, 1 FAIL, 1 GAP, 1 PASS), pharma deliverable test on GBM top-5 (2/10 DELIVERED + 4/10 PARTIAL + 3/10 GAP + 1/10 N/A). Architecture review v1. **Architecture review v2 (this document).**

**Open questions:**
- Was Round 2.2b implemented or only specified?
- What's the status of FIX-002 (AML ODE relapse), FIX-003 (KAALCURA real GDSC), FIX-004 (Scout 4 Boolean)?
- How does Round 3 GBM relate to the planned Round 3 NSCLC per CSO Memo v2.1 §6?

These need answering before Workstream B/C decisions become final.

---

## Section 5 — Data source reliability matrix (revised)

Same matrix as v1 but with corrections from full bundle reading:

### OpenTargets associations
v1 verdict HIGH stands. Bundle shows 26,288 diseases × 23,422 targets × 4.5M associations. Correctly used for any-disease gene list.

### GDSC PUTATIVE_TARGET
v1 verdict PARTIAL stands. **Round 3 closure §3.2 Finding 15 already documents this with the correct path forward.** The supplementary data sources path: clinical trial outcomes (now partly via Phase 2E), PDX/organoid response data (not integrated), real-world clinical use patterns (not integrated). v1 review proposed integrating ChEMBL `/mechanism` endpoint as the fix; that's one of several supplementary sources but not necessarily the highest-leverage one.

### GDSC dose-response (`GDSC2_fitted_dose_response.xlsx`)
v1 verdict MODERATE stands. Round 3 closure adds: GDSC is 72-hour in vitro viability — does NOT capture epigenetic mechanisms (TMZ/MGMT methylation), does NOT include BBB permeability. These are fundamental data-source limits, not pipeline bugs.

### ChEMBL (target lookup, bioactivity, properties, mechanism)
v1 verdict HIGH for kinase-inhibitor space stands. Add: `/mechanism` endpoint integration would help with mechanism-class drugs (TMZ → "DNA alkylation") but the deeper issue is data-source coverage, not endpoint choice.

### STRING (aliases, links)
v1 verdict HIGH stands. Reading the original STRING-only step (`step4_string_interactions.py`) would clarify how the original pipeline used STRING; my v1 only reviewed the wrapper's STRING usage.

### UniProt REST API
v1 verdict HIGH stands. 99% mapping rate confirms reliability.

### AlphaFold availability
v1 verdict HIGH for existence stands. Reading `step10_alphafold.py` (in `/code/`) would clarify how the original pipeline organized PDB downloads — relevant for Workstream C.

### ClinicalTrials.gov v2 API
v1 verdict HIGH for volume / LIMITED for per-drug novelty stands. False-positive risk for genes with English-word names (REST, MET, CSF2) is documented in Round 3 closure §5.3.

### GTEx tissue selectivity
v1 verdict PARTIAL stands. Real GTEx v8 (54,592 genes × 54 tissues) integrated per `step6_fix_gtex.py`. Per-drug therapeutic index calculation not done — would require per-drug target list × per-tissue expression.

### BBB MPO 4-component (Wager 2010)
v1 verdict MODERATE stands. Honest scope: passive-diffusion proxy. P-gp efflux not modeled.

**New entries from full bundle reading:**

### KAALCURA gene axes (R_prolif, R_emt, R_ddr)
**Reliable for:** Direction (Round 2.2a Q_D PASS, Spearman ρ = −0.235 cross-dataset).
**NOT reliable for:** Within-dataset prediction (Q_C mean CV-AUROC 0.532, plateaus regardless of scoring method).
**Original validation:** AUROC 0.638 on synthetic data per FIX-003. Real GDSC validation: partial.
**Confidence in INTERCEPTA use:** PARTIAL. Used in Round 2 AML net but with documented limitations.

### Phenotype-structured ODE (mCRPC)
**Reliable for:** Directional ranking, combination failure prediction (Doc+Cis HR=1.003 matches all clinical Doc-combo failures).
**NOT reliable for:** Absolute g-rate quantitation (0/3 confirmed g-targets pass; 0.36× / 3.45× / 1.69× off Stein/Leuva/Zhou references). Round 1 closed at v4.1 with these gaps documented as structural.
**Confidence in INTERCEPTA use:** PARTIAL with documented limits per Round 1 retrospective and CSO Memo v2.1.

### Cox PH HR estimator (post FIX-001)
**Reliable for:** Statistical HR with proper CIs (replaces broken median-ratio).
**Limitations:** 5-trial validation: 3/5 PASS (LATITUDE, PROfound, TALAPRO2_C2). 2/5 FAIL (CHAARTED, PROpel_BRCA). Docetaxel emax may need recalibration.
**Confidence in INTERCEPTA use:** HIGH for what passes; HONEST about what doesn't.

### BeatAML drug sensitivity + mutations
**Reliable for:** Genotype-stratified drug response analysis (Round 2 NPM1+Cabozantinib p=2.9e-12 — strongest finding, called publishable per CLAUDE.md).
**Limitations:** 562 patients, not all cytogenetic strata well-powered. p38 MAPK retracted (FDR not computed initially).
**Confidence in INTERCEPTA use:** HIGH per Round 2 closure documents.

### Van Galen 2019 scRNA-seq + Zeng 2022
**Reliable for:** Cell-type annotations including HSC-like, Prog-like, Mono-like, GMP-like (per Round 2.2a Q_E PASS with Venetoclax surfacing).
**Limitations:** Comparator-biology must be verified per primary source (Mono-like is terminally differentiated, not proliferative — this caused Q_A FAIL in Round 2.2a).
**Confidence in INTERCEPTA use:** HIGH when paired with primary-source verification.

---

## Section 6 — Architectural debt (revised, incorporating full project)

Reorganized from v1's 42-item list. The 42 items are still valid for the wrapper code. Adding:

### Project-wide debt v1 missed

**P-1.** Two pharma deliverable schemas exist (10-item in enza_alis.json, 9-item in complete.json). Schema not standardized within project's own canonical artifacts.

**P-2.** Reference deliverables contain post-fix-broken numbers. `pharma_deliverable_enza_alis.json` has HR=0.692 with CI [0.58-0.79] from broken median-ratio HR estimator. After Apr 18 fix, real Cox PH gives HR=0.749 with CI [0.504-1.112]. **The deliverable JSON has not been re-generated post-fix.**

**P-3.** Terminology contradiction: CLAUDE.md says "❌ Pharma deliverable" and recommends "computational hypothesis package." Vision 9.1 says "pharma deliverable." Closure documents use both interchangeably. Project doesn't have a single canonical term.

**P-4.** Round 2.2b was specified pre-code (as required by Principle 3) but no closure document exists in bundle. Either Round 2.2b was implemented but not closed, or implementation hasn't started yet, or the closure doc lives elsewhere. Open governance question.

**P-5.** KAALCURA is a vision-required Module 1 layer but Workstream A's wrapper does not invoke it. Wrapper produces disease nets without KAALCURA scores. This is a real architectural gap relative to vision spec.

**P-6.** The Workstream A wrapper invented a v2 composite ranking that doesn't integrate with the existing `pareto_ranking.py`. Two ranking systems coexist without integration.

**P-7.** No automated regeneration of reference deliverables. When upstream caches update (ChEMBL bioactivity changes, new ClinicalTrials added), the reference deliverable doesn't refresh. Stale-content risk grows over time.

**P-8.** Three different verdict taxonomies (extending v1's drift #38): pipeline verification uses assert; standalone validation uses PASS/CHECK/FAIL/GAP; Round 2 closures use a 5-gate locked-spec system with FAIL/PASS per gate plus a round-level verdict; my GBM deliverable uses DELIVERED/PARTIAL/GAP/N/A.

**P-9.** 11 .docx specifications in `/docs/` but 7 didn't extract via python-docx. Including the architecture spec (`INTERCEPTA_Net_Architecture_v2_0.docx` 25KB) and the math spec. **Any architecture review that doesn't read the architecture spec is incomplete.**

**P-10.** Vision Part 12 (5 sections including microbiome, regulatory, open collaboration) is documented in Round 3 closure §6.1 as "added by AI co-founder, awaiting Prasad approval." This means part of the vision document set has uncertain canonical status.

### Severity reassessment

**HIGH severity (12 items):**
- P-1, P-2, P-3, P-5, P-6, P-9 from above
- Drift #1, #2, #4, #11, #23, #24 from v1 wrapper-code drifts

**MEDIUM severity (~20 items):** mix of v1's drifts and project-wide issues.

**LOW severity (~20 items):** documentation, dead code, minor inconsistencies.

---

## Section 7 — Revised module structure proposal

v1 proposed creating `intercepta/` package from scratch. This was wrong because it ignored existing structure. Revised proposal:

### Don't create new package; reorganize existing

```
~/INTERCEPTA/
├── code/                                    # Original pipeline (Round 1/2 era)
│   ├── intercepta_pipeline.py               # Original mCRPC pipeline (preserve)
│   ├── disease_net_builder.py               # Upstream net builder (preserve)
│   ├── intercepta_phenotype_ode_v1.py       # Apr 7 breakthrough (preserve)
│   ├── intercepta_unified_ode_v4_1.py       # Round 1 final (preserve)
│   ├── intercepta_kaalcura_v1.py            # KAALCURA (preserve)
│   ├── pareto_ranking.py                    # Pareto multi-objective (preserve)
│   ├── synergy_scoring.py                   # Synergy (preserve)
│   ├── hr_estimator_fixed.py                # Apr 18 fix (preserve)
│   ├── ode_v4_diagnostic.py                 # Round 1 diagnostic (preserve)
│   ├── intercepta_g_rate_validation_v5_2.py # Round 1 g-rate validation (preserve)
│   ├── step[1-14]_*.py                      # Net builder steps (preserve)
│   └── ... (other Round 1/2 files)
├── round2_aml/                              # Round 2 AML subproject
│   ├── code/build_aml_net_v5_2_kaalcura.py  # Latest closed Round 2 build
│   └── ...
├── round3_gbm_live_test/                    # Round 3 GBM subproject
│   ├── code/                                # ← Workstream A wrapper lives here
│   │   ├── intercepta_pipeline_v0.py        # Current wrapper (refactor target)
│   │   ├── generate_pharma_deliverable.py   # Current deliverable (refactor target)
│   │   ├── validate_workstream_a_gbm.py     # Current validation (refactor target)
│   │   └── (refactored modules go here)
│   ├── docs/                                # Round 3 specifications
│   ├── results/                             # Round 3 outputs
│   └── INTERCEPTA_Pipeline_v0_Closure.md    # Closure document
└── round[N]/                                # Future rounds follow same pattern
```

### Refactor scope: split, don't relocate

Inside `round3_gbm_live_test/code/`, refactor the wrapper file into:

```
round3_gbm_live_test/code/
├── disease_resolver.py          # Phase 1: resolve_disease, build_net + helpers
├── enrichment_metabolites.py    # Phase 2A
├── enrichment_string.py         # Phase 2B
├── enrichment_alphafold.py      # Phase 2C (UniProt + AlphaFold)
├── enrichment_chembl.py         # Phase 2D (split from god-function)
├── enrichment_chembl_bbb.py     # Session 1 BBB augmentation
├── enrichment_clinical_trials.py # Phase 2E
├── ranking_gdsc_only.py         # v1 ranking (renamed from rank_drugs_for_disease)
├── ranking_multi_evidence.py    # v2 ranking (renamed, refactored to require enriched net)
├── analysis_undruggable.py      # surface_undruggable_priority_targets
├── pharmacology_bbb.py          # CNS MPO scoring (cross-cutting)
├── deliverable_generator.py     # 10-item pharma deliverable using canonical schema
├── deliverable_configs/
│   ├── gbm.json                 # GBM SOC, biomarkers
│   ├── nsclc.json               # NSCLC SOC, biomarkers (Workstream B prep)
│   └── mcrpc.json               # mCRPC SOC, biomarkers (matches reference deliverable)
├── verify_pipeline.py           # Pipeline self-test (extracted from wrapper's __main__)
├── validate_workstream_a.py     # Disease-agnostic validation framework
├── validation_ground_truth/
│   ├── gbm.py
│   ├── nsclc.py
│   └── mcrpc.py
└── intercepta_pipeline_v0_legacy.py  # Original wrapper preserved per P16
```

**This is smaller scope than v1 proposed.** No new package. Refactor lives within `round3_gbm_live_test/code/`. Original `code/` Round 1/2 work untouched.

### Why this structure (not v1's)

1. **Matches existing Round 2 pattern.** Round 2 has its own `round2_aml/` directory. Round 3 should mirror that pattern. Projects with rounds-as-subdirectories make round-level governance easy.
2. **Preserves Round 1/2 work cleanly per P16.** Original `code/` directory is the established home; not moving files preserves git history, audit script paths, and existing imports.
3. **Refactor target is local.** Only the wrapper code and new disease configs change. No cross-project risk.
4. **Forward-compatible with future rounds.** Round 4 (NSCLC?) gets `round4_nsclc/code/` with parallel structure.

---

## Section 8 — Workstream B vs C readiness (honest)

Round 3 closure §7 already defined this fork with CSO recommendation B before C. The architecture review's job is to confirm or revise that recommendation in light of full project context.

### Workstream B readiness check

**B = test whether phenotype-structured ODE generalizes from mCRPC to one new cancer (NSCLC).**

Required from project foundation:
- The phenotype ODE (`intercepta_phenotype_ode_v1.py`, 49KB) ✓ exists
- Round 1 retrospective documenting its limits ✓ exists
- A non-mCRPC cancer with raw scRNA-seq FASTQ for velocity ✓ NSCLC has GSE131907 (Kim et al.) and others
- Validation trial(s) with measurable endpoints ✓ NSCLC has FLAURA, KEYNOTE-024, ALEX, AURA3
- Disease-net infrastructure that produces enriched NSCLC net ✓ Workstream A delivers this (post-refactor)
- HR estimator that produces real Cox PH outputs ✓ `hr_estimator_fixed.py` per Apr 18 fix

**Risks:**
- Round 1 documents that mCRPC ODE fails 0/3 g-rate targets and 6/6 trial acceptance windows. **The framework's known structural limits will likely manifest in NSCLC too.** Workstream B may produce: directional ranking correct, quantitative validation fails on similar grounds.
- Whether this is "Workstream B succeeds" or "Workstream B fails" depends on the success criterion. Per Round 1 retrospective, "directional ranking is sufficient for the drug-discovery use case" — by that bar, Workstream B should succeed. By the "quantitative HR/PFS prediction" bar, Workstream B will likely fail similarly to Round 1.
- **Pre-Workstream B must lock the success criterion in writing.** This is a Round 2 lesson (locked spec before code). v1 review didn't propose this.

### Workstream C readiness check

**C = Universal ODE refactor + first novel molecule via REINVENT4.**

Required from project foundation:
- Disease-agnostic ODE structure (currently all four ODE versions are mCRPC-specific)
- A target with AlphaFold structure ready for docking ✓ 20 PDB files in `data/alphafold/`
- REINVENT4 setup with selectivity-constrained scoring ✗ not done
- ASKCOS retrosynthesis integration ✗ not done

**Risks:**
- Universal ODE refactor is structural, not parametric. Round 3 closure §3.3 names this. 6-8 weeks per Plan v2 §5.
- REINVENT4 + ASKCOS are real open-source tools but neither is integrated. Days-to-weeks per integration.
- Generating one novel molecule that passes selectivity + ADMET + synthesizability filters is the goal. The vision says this is the breakthrough. Difficult.

### CSO recommendation (revised)

I confirm Round 3 closure's recommendation: **B before C, sequential not parallel.**

Add: **before B begins, complete Round 2.2b OR explicitly defer it.** Round 2.2b was specified Apr 22 with pre-code commit. Either it's been implemented (no closure in bundle) or it hasn't. This is an open governance question that should be answered before Workstream B begins, because:
- Round 2.2b's therapeutic-index test (Q_G, Q_H per spec) is the LSC selectivity validation. If 2.2b reveals KAALCURA doesn't generalize across malignant vs non-malignant cell types, Workstream B's framework choices change.
- Round 2.2c was explicitly scoped to follow 2.2b. Skipping 2.2b breaks Round 2 governance discipline.

**Revised CSO recommendation, sequential:**

1. **Round 2.2b implementation status check.** Either (a) implement and close 2.2b per spec, (b) close 2.2b explicitly as deferred with documented reason, or (c) confirm it's been done and obtain its closure document. Estimated 1 day to clarify.

2. **Workstream A refactor.** Per Section 7 above. 1-2 sessions. Targets: split god-functions, match canonical 10-item deliverable schema, build per-disease config, add NSCLC config alongside GBM and mCRPC.

3. **Workstream A re-validation.** Re-run Workstream A on GBM with refactored code. Confirm 2/10 DELIVERED + 4/10 PARTIAL stable (or improved). Run Workstream A on NSCLC with NSCLC config. Document NSCLC deliverable coverage as baseline before B.

4. **Workstream B.** ODE generalization to NSCLC. Lock success criterion in writing before code. Estimated 4-6 weeks.

5. **Workstream B closure.** With FAIL/PASS per locked spec. Even if FAIL on quantitative criteria, scientific findings preserved separately.

6. **Workstream C decision point.** Based on B closure, decide: (a) C as planned, (b) C with framework changes informed by B, or (c) Workstream A.5 (deliverable auto-generation) before C.

This is a 2-3 month sequence. v1 review proposed 1-2 session refactor → Workstream B. Adding the Round 2.2b clarification + Workstream A re-validation makes it 2-3 weeks before B begins. Worth the rigor.

---

## Section 9 — What needs to happen before any code

In order:

**Before any architectural decisions:**
1. Read the 7 .docx specs that didn't extract. Especially `INTERCEPTA_Net_Architecture_v2_0.docx`. **The project has an architecture document at v2.0; my reviews are v1 and v2 of a NEW architecture analysis. These shouldn't be confused.** Either rename my docs (e.g., "Architecture Audit Round 3") or reconcile with the existing architecture spec.
2. Check Round 2.2b status — closure exists somewhere or it doesn't.
3. Read the 5 chat PDFs (`KAALI_chat.pdf`, `KAALI_sub_chat.pdf`) for full conversation context that I have not accessed.

**Before any refactor:**
4. Prasad confirms or revises the 9 fixes from `MASTER_FIXES.md` — which are done, which are open.
5. Prasad confirms canonical pharma deliverable schema — 10-item or 9-item or revised.
6. Prasad confirms terminology choice — "pharma deliverable" or "computational hypothesis package" project-wide.
7. Prasad confirms whether Workstream A is closed at current 2/10 DELIVERED state, or whether the architectural rebuild for canonical-schema deliverables happens before workstream B begins.

**Before any new science:**
8. Lock the Workstream B success criterion in writing. Round 1 lesson: directional ranking is the drug-discovery use case; quantitative HR is not the right validation framework for this kind of ODE.
9. Confirm Round 2.2c (therapeutic index) scope — whether it's done by Round 2 or moved to Workstream A.5 / B.

---

## Section 10 — Final honest verdict

The v1 review was directionally right (Workstream A's wrapper code needs refactoring; foundation is mostly sound; ODE generalization is the central Workstream B question) but factually too narrow. v1 made architectural recommendations without reading the project's own architecture spec, the existing pipeline, or the existing Pareto ranking module.

**v2 conclusion:**

1. The Workstream A wrapper needs refactoring as v1 outlined, with corrections in Section 7 above. Estimated 1-2 sessions. Lower scope than v1 implied.

2. The Workstream B vs C fork is already documented in Round 3 closure §7. Recommendation B before C stands. Add: clarify Round 2.2b status before B begins.

3. The reference 10-item deliverable schema is real but its content (HR=0.692 numbers) is post-fix stale. Schema is reusable; numbers need re-derivation.

4. **There are 7 .docx specifications I have not read** including the architecture spec at v2.0. Any deeper architectural decision-making should incorporate those.

5. **There are 5 chat PDFs (KAALI_chat.pdf, KAALI_sub_chat.pdf) I have not read.** They contain full project conversation history that I've been inferring instead of reading.

6. **My v1 architecture review made claims about past Claude session decisions ("Mistake 1: Session 2 added v2 ranking as a god-function") that I cannot verify without reading the chat PDFs.** Those criticisms may be right or wrong. I shouldn't have made them confidently in v1.

The right next step before any refactor or workstream code is: extract the 7 .docx specs (try LibreOffice, pandoc, or have Prasad export as .md), read the chat PDFs, and confirm the 9 governance items in Section 9 above. **Architecture review v3 may be needed once those are read.** Or, if they confirm v2's findings, v2 is final and we proceed to refactor.

What I will NOT do without explicit Prasad direction:
- Refactor any code
- Make any final architectural decisions
- Generate any new deliverables
- Begin Workstream B or C

What I commit to do:
- Read whatever Prasad provides next
- Update v2 to v3 if findings change
- Preserve v1 per P16 (it's a documented architectural snapshot, even if partially wrong)
- Continue documenting honest limitations of my own analysis

— Claude (CSO/AI co-founder)
2026-05-06 (Architecture Review v2)
