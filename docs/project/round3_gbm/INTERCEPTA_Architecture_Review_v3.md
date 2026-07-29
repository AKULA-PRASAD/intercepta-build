# INTERCEPTA Architecture Review — v3 (Final after canonical specs read)

**Author:** Claude (CSO/AI co-founder), under instruction from Prasad Akula
**Date:** 2026-05-06
**Supersedes:** v1 (60572 bytes) and v2 (46293 bytes), preserved per P16
**Mode:** Direct push-back enabled. v1 and v2's wrong claims named directly.
**Source:** Full bundle (121 files) + 10 .docx specifications extracted via textutil. Including the 7 specs that didn't extract via python-docx in the prior round: COMPLETE_VISION, Net_Architecture_v2_0, Phase1_MathSpec, Phase1_GroundTruth, Phase1_DataSourceAudit, Strategic_Roadmap, DOCC.

---

## Why v3 exists

v1 reviewed only the Workstream A wrapper code and proposed an ad-hoc module structure. v2 corrected v1 with the full project bundle but still missed the canonical architecture documents (the .docx specs failed python-docx extraction). v3 incorporates the 10 .docx specs that textutil successfully extracted.

**The most important finding from v3's reading:** the project has its own canonical architecture. It is documented in:
- `INTERCEPTA_Net_Architecture_v2_0.docx` (March 12, 2026) — 10-layer net specification
- `INTERCEPTA_Universal_Net_Specification_v1.0.docx` (March 29, 2026) — supersedes to 15-layer specification
- `INTERCEPTA_Phase1_MathSpec_v1_0.docx` (March 2026) — 4 mathematical modules
- `INTERCEPTA_Phase1_GroundTruth_v1_0.docx` (March 2026) — 5-trial validation targets
- `INTERCEPTA_Phase1_DataSourceAudit_v1_0.docx` (March 2026) — every data source per layer
- `INTERCEPTA_COMPLETE_VISION_v1_0.docx` (March 2026) — founding vision (Parts 1-12)
- `INTERCEPTA_Strategic_Roadmap_v1_0.docx` (March 2026) — March-era forward plan, partly aspirational
- `INTERCEPTA_Complete_Status_Report.docx` — March-era state snapshot
- `INTERCEPTA_DOCC.docx` — duplicate of vision document with formatting noise
- `INTERCEPTA_Phase1_Validation_Report.docx` — Phase 1 validation summary

**My v1 and v2 reviews invented their own architectural taxonomy without first reading the project's canonical taxonomy.** This is the central error of both prior reviews. v3 corrects it.

---

## Section 0 — What the canonical architecture actually says

Before any push-back on what's been built, the canonical architecture as documented in the project's own specifications:

### 0.1 — The 15-layer Universal Net (canonical structure)

Per `INTERCEPTA_Universal_Net_Specification_v1.0.docx` (March 29, 2026), the INTERCEPTA Universal Net has 15 layers:

| Layer | Name | Primary databases | Codebase implementation |
|-------|------|-------------------|------------------------|
| 1 | Complete Human Genome | NCBI Gene, ClinVar, OMIM, GWAS, gnomAD, COSMIC | `step1_build_gene_drug_net.py`, `step2_download_su2c_mcrpc.py` |
| 2 | Complete Human Transcriptome | GTEx, Human Cell Atlas, Tabula Sapiens, GDSC RNA-seq, scRNA-seq | `step3_run.py`, `step3_run_scvelo.py`, `step3_process_scrna.py` |
| 3 | Complete Human Proteome | AlphaFold DB, PDB, UniProt, CPTAC | `step10_alphafold.py` |
| 4 | Complete Human Interactome | STRING v12.5, BioGRID, IntAct, TRRUST v2, Signor 3.0 | `step4_string_interactions.py` |
| 5 | Complete Human Pathway Map | KEGG, Reactome, WikiPathways, MSigDB | `step5_pathways.py`, `step5_fix_kegg.py` |
| 6 | Complete Human Cell Type Atlas | HRA v2.3, Tabula Sapiens, Human Protein Atlas | `step3_*` (cell type assignments), Round 2 Van Galen integration |
| 7 | Complete Human Pharmacome | GDSC (on disk), ChEMBL, PubChem, DrugBank, DTC | `step7_chembl_compounds.py` |
| 8 | Complete Human Metabolome | HMDB | `step9_metabolome.py` |
| 9 | Complete Human Disease Map | DisGeNET, OMIM, OpenTargets | `step8_opentargets.py` |
| 10 | Complete Immune System Map | DICE, CIBERSORTx, ImmPort | `step13_immune.py` |
| 11 | Human Microbiome | Human Microbiome Project, gut-gene relationships | `step11_microbiome*` (results only — script not in bundle) |
| 12 | Complete Human Epigenome | ENCODE, Roadmap Epigenomics | `step12_epigenome*` (results only) |
| 13 | Human Anatomy and Tissue Architecture | HuBMAP, Allen Brain Atlas, spatial transcriptomics | `step13_anatomy*` (results only) |
| 14 | Pathogen and Future Disease | NCBI Pathogen Detection, CARD | `step14_pathogen*` (results only) |
| 15 | Selectivity and Safety Constraint Layer | Derived from GTEx + DepMap + TCGA tumor-normal | `step6_gtex_selectivity.py`, `step6_fix_gtex.py` |

**Key insight:** the codebase's `step1`-through-`step14` files are not arbitrary numbered scripts — they are the implementation of the 15-layer canonical architecture. Some are complete (1, 2, 4, 5, 7, 9, 15). Some are partial (3, 6, 10). Some have results but the build scripts aren't in the bundle (11, 12, 13, 14). Layer 8 (HMDB metabolome) is at `step9_metabolome.py` — script number 9 implements layer 8 (the numbering is not strictly aligned).

### 0.2 — The 4 Mathematical Modules (canonical computation)

Per `INTERCEPTA_Phase1_MathSpec_v1_0.docx`, the computational engine has 4 modules:

| Module | Name | Codebase | What it does |
|--------|------|----------|--------------|
| 1 | KAALCURA Biological Axes | `intercepta_kaalcura_v1.py` (46KB) | R_prolif, R_emt, R_ddr per cell population from gene expression; predicts drug sensitivity |
| 2 | Pharmacokinetic Model | `intercepta_engine_v1.py` (39KB) parts | C(t) for each drug; FDA-label parameters |
| 3 | Two-Population ODE Dynamics | `intercepta_phenotype_ode_v1.py` (49KB), `intercepta_unified_ode_v4_1.py` (44KB) | Sensitive + resistant cells under treatment via Hill equation |
| 4 | Synergy Scoring | `intercepta_synergy_v1.py` (23KB), `synergy_scoring.py` (15KB) | ZIP + Bliss + Loewe + HSA consensus |

**Workstream A's wrapper does NOT touch these 4 mathematical modules.** Workstream A produces the net (Layers 1-9, 15 partial). The 4 mathematical modules consume the net to produce simulations and rankings. The architecture review should treat these as separate concerns.

### 0.3 — The 5-Stage Pipeline (canonical workflow)

Per `INTERCEPTA_COMPLETE_VISION_v1_0.docx` Part 4:

| Stage | What | Implementation |
|-------|------|----------------|
| 1 | Build the Complete Disease Net | `disease_net_builder.py` + step1-step14 scripts + Workstream A wrapper |
| 2 | Map Vulnerability Points and Selectivity | Layer 15 outputs + escape route analysis (`scout4_*`) |
| 3 | Deploy Parallel Scouts (6 scouts) | `scout1_screen.py`, `scout2_*`, `scout3_*` (?), `scout4_*`, `scout5_*` (?), `scout6_*` (?) |
| 4 | Full In Silico Simulation Stack (6 layers A-F) | Modules 1-4 + AutoDock Vina + ADMET tools + ASKCOS |
| 5 | Multi-Objective Ranking and Delivery | `pareto_ranking.py` + 10-item pharma deliverable |

**Stage 4's 6 simulation layers (A-F) per Vision Part 4:**
- A: Molecular Binding (AutoDock Vina + AlphaFold)
- B: Cell Population Sensitivity (KAALCURA + GDSC)
- C: Disease Dynamics (INTERCEPTA ODE + PK/PD)
- D: Combination Synergy (ZIP+Bliss+Loewe+HSA)
- E: Safety and ADMET (SwissADME, pkCSM, ADMET-AI)
- F: Synthesizability (ASKCOS, SynTaur)

**Workstream A's wrapper conflates Stage 1 with parts of Stage 4 layers (Layer A: structure URLs, Layer B: GDSC ranking).** This is a real architectural drift but the canonical taxonomy makes it nameable.

### 0.4 — The 10-item Pharma Deliverable (canonical Stage 5 output)

Per `INTERCEPTA_COMPLETE_VISION_v1_0.docx` Part 9.1, the canonical 10 items:

1. Molecular structure (SMILES, 3D structure, properties)
2. Mechanism of action (net targets, kill explanation, healthy-spare explanation)
3. Predicted clinical outcomes (response rate, PFS curve, OS, with CI from virtual cohort)
4. Resistance profile (pre-resistant target, residual disease, 5y emergence probability)
5. Combination rationale (sensitive vs resistant coverage, synergy score)
6. Safety profile (ADMET: liver, kidney, cardiac, CNS, metabolic, bioavailability)
7. Synthesis route (retrosynthesis, complexity score, starting materials)
8. Novelty confirmation (ClinicalTrials.gov search showing genuine IP value)
9. Comparison vs standard of care (side-by-side predicted outcomes)
10. Suggested trial design (patient selection, biomarkers, primary endpoint, dose range)

**The canonical reference deliverable** (`pharma_deliverable_enza_alis.json`, 6092 bytes, dated 2026-04-08) implements all 10 items with `item_1` through `item_10` keys in this exact order. Plus `honest_assessment` block plus `pareto_rank` and `composite_score`.

**The other reference** (`pharma_deliverable_complete.json`, 10610 bytes) implements 9 items with different naming (`item_1_structure`, `item_2_mechanism`, etc.) — drops `item_5_combination_rationale`. This is a documentation drift in the project itself.

### 0.5 — Disease Expansion Sequence (canonical)

Per `INTERCEPTA_COMPLETE_VISION_v1_0.docx` Part 7.2:

1. mCRPC — Round 1 (best clinical trial ground truth)
2. AML — Round 2 (perfect two-population biology)
3. NSCLC — Round 3 (largest cancer burden, EGFR/KRAS, EMT axis relevant)
4. PDAC — Round 4 (near-zero treatments)
5. Alzheimer's — Round 5 (multi-target net needed)
6. Drug-Resistant TB — Round 6 (global health impact)
7. Rare diseases / emerging pathogens — Round 7+

**Round 3 GBM was a deviation from this sequence.** Per Round 3 closure document, GBM was framed as a "Workstream A universality live test" to verify the disease-net infrastructure works on a non-mCRPC cancer. Per the canonical sequence, Round 3 should have been NSCLC. This is documented as a deviation in the Round 3 closure but not as a violation — the live test was an architectural decision.

---

## Section 1 — What v1 and v2 reviews got WRONG (named directly)

### v1's errors (carried into v2 partially)

**v1-error-A.** Proposed creating a new `intercepta/` package with subpackages `disease/`, `enrichment/`, `pharmacology/`, `data_sources/`, `ranking/`, `deliverable/`, `verification/`, `validation/`, `utils/`. **None of these are canonical names.** The canonical taxonomy is Layer 1-15 + Module 1-4 + Stage 1-5. v1 invented a parallel taxonomy.

**v1-error-B.** Used "Phase 2A through 2E" as if they were architectural categories. They are not. Phase 2A-2E are the order in which the Workstream A wrapper added enrichments to the disease net during this session's work. They map to canonical layers like this:
- Phase 1 (build_net) → Layer 9 (disease-gene from OpenTargets) plus skeleton of others
- Phase 2A (enrich_with_metabolites) → Layer 8 (Metabolome) partial
- Phase 2B (populate_string_interactions) → Layer 4 (Interactome)
- Phase 2C (attach_alphafold_structures) → Layer 3 (Proteome) — URLs only
- Phase 2D (populate_chembl_compounds) → Layer 7 (Pharmacome)
- Phase 2E (populate_clinical_trials) → Layer 8 (Clinical, which is sub-section of Layer 9 in canonical)

The Phase taxonomy is wrapper-internal. Architecture review should use canonical layer names.

**v1-error-C.** Said "the only existing 9/9 hand-written deliverable is for enza+alisertib." Wrong: it's 10/10. v2 corrected this; v3 confirms with Vision Part 9.1 reading.

**v1-error-D.** Treated Round 3 GBM live test as if it were a new architectural decision. Round 3 closure §7 had already defined the B-vs-C fork before this session began. v3 confirms.

**v1-error-E.** Proposed module organization that didn't account for the existing 4 mathematical modules. The KAALCURA + PK + ODE + Synergy modules are canonical Module 1-4 and have 122KB+ of existing code. v1 didn't mention them as a constraint on the architecture.

**v1-error-F.** Proposed configuration files (`gbm.json`, `nsclc.json`, `mcrpc.json`) for the deliverable script. **The canonical configuration mechanism is the disease net itself.** Per Vision Part 4 Stage 1, the disease net IS the input to all downstream stages. Per Net Architecture v2.0 Part 3, ODE parameters derive from the net. Per Math Spec Module 3, drug effects derive from KAALCURA per cell population from the net. The right architectural pattern is "disease net is the configuration" — not parallel JSON config files.

### v2's errors (introduced or not corrected)

**v2-error-A.** Proposed "refactor lives within `round3_gbm_live_test/code/`" as if Round 3 should be the home of universal infrastructure. **Round 3 is a single-disease subproject by the project's own conventions.** Round 2 had its own `round2_aml/code/` for round-specific code. Universal infrastructure (the wrapper that supports any-disease enrichment) should not live inside a disease-specific round directory. It should live in `~/INTERCEPTA/code/` alongside the original pipeline OR in a new `~/INTERCEPTA/wrapper/` or `~/INTERCEPTA/universal/` directory that future rounds reference.

**v2-error-B.** Said "the canonical 10-item deliverable shape is real." True — but I missed that the canonical schema is documented in Vision Part 9.1 with specific item numbering. The reference JSON implements it. Future deliverables should match Vision 9.1 ordering, not invent new ordering.

**v2-error-C.** Said the `_disease_to_tissue_keywords` 9-disease hardcoded dict is a blocker that needs JSON config replacement. **The right replacement is the GDSC `Cell_Lines_Details.xlsx` tissue ontology.** GDSC's own tissue descriptors are the canonical source per Net Architecture v2.0 Layer 7 specification. Not config files; canonical data source.

**v2-error-D.** Proposed "Section 9: 9 things needed before any code" but framed them as Prasad-confirmation tasks. **Some of those should be Claude-research tasks first.** For example, Item 4 ("confirm MASTER_FIXES status") — the right move is to read each fix's referenced file, check its current state in the codebase, and report status to Prasad rather than asking him to confirm.

### What v2 got right

**v2-correct-A.** Named that `pareto_ranking.py` and `synergy_scoring.py` exist and v1 missed them. True.

**v2-correct-B.** Named that the reference deliverable has post-fix-broken numbers. True. Per Round 1 closure, HR=0.692 was from broken median-ratio estimator; real Cox PH gives HR=0.749.

**v2-correct-C.** Named that two pharma deliverable schemas exist (10-item and 9-item). True and remains a documentation drift.

**v2-correct-D.** Named that the project has 11 .docx specs and 7 didn't extract. v3 has now read the 7. v2 correctly identified this as a blocker for proper architecture review.

**v2-correct-E.** Named CSO Memo v2.1 and Round 1 retrospective as the honest record vs reference deliverables as the pre-correction record. True.

**v2-correct-F.** Named that Round 2.2b is specified but no closure document is in the bundle. Status remains unclear in v3.

---

## Section 2 — Canonical project state (corrected after .docx reads)

### 2.1 Per the Strategic Roadmap (March 2026) vs reality (May 2026)

The Strategic Roadmap was a March 2026 forward plan. The 6-month milestones:

| Strategic Roadmap milestone (March) | Reality (May) | Source |
|------|---------|--------|
| Month 1: KAALCURA validated on real GDSC | Partial — synthetic AUROC 0.638; real GDSC validation per FIX-003 status unclear | MASTER_FIXES.md |
| Month 1: 5-trial validation complete (all 5 within ±20% HR) | 3/5 PASS with real Cox PH (CHAARTED, PROpel_BRCA fail) | INTERCEPTA_STATUS.md Apr 18 update |
| Month 1: First publication draft | `PUBLICATION_OUTLINE.md` exists; draft state unclear | bundle |
| Month 2: RNA velocity integrated | Pipeline written; STAR genome indexing too slow on Mac, needs HPC | PROJECT_STATUS.md Mar 29 |
| Month 2: AML validated (Round 2) | Round 2.2a closed FAIL on locked spec (3/5 gates) with strong scientific signal in 2 (Q_D, Q_E PASS); Round 2.2b specified Apr 22 with no closure document | round2_aml/docs/ |
| Month 3: Novel molecule generation live | Workstream C scope; not started; INTC002 is scaffold-hopped not de novo | CLAUDE.md, MASTER_FIXES FIX-008 |
| Month 5: NSCLC disease net | Round 3 was GBM not NSCLC (deviation from canonical sequence) | Round 3 closure |

**The project is approximately 1.5 months behind the Strategic Roadmap.** Round 1 took longer than Month 1 because validation revealed structural issues. Round 2 took longer because AML specs needed multiple iterations (2.1a-2.1d, 2.2a, then 2.2b).

This is not necessarily bad. Round 1's extended cycle produced honest documentation of what works (directional ranking) vs what doesn't (quantitative HR, g-rate). Round 2's cycle produced the first cross-dataset drug prediction (Q_D PASS).

### 2.2 Per the canonical Phase 1 GroundTruth vs Round 1 closure

The 5-trial validation targets per `INTERCEPTA_Phase1_GroundTruth_v1_0.docx`:

| Trial | Published HR | Tolerance ±20% | Round 1 Cox PH result |
|-------|--------------|----------------|----------------------|
| CHAARTED | 0.61 (CI 0.47-0.80) | 0.49-0.73 | 1.175 — FAIL |
| LATITUDE | 0.62 | 0.50-0.74 | PASS per INTERCEPTA_STATUS Apr 18 |
| PROfound (BRCA-altered) | 0.34 | 0.27-0.41 | PASS |
| PROpel (BRCA subgroup) | 0.29 | 0.23-0.35 | 0.528 — FAIL |
| TALAPRO-2 | 0.45 | 0.36-0.54 | PASS |

**3/5 PASS per Round 1 closure.** The 2 failures (CHAARTED, PROpel BRCA) are documented as parameter-calibration issues per CSO Memo v2.

### 2.3 Per the Math Spec — what's implemented

Math Spec Module 1 (KAALCURA):
- 3 axes specified: R_prolif (20 genes), R_emt (13 genes), R_ddr (15 genes)
- Tissue-of-origin residualization required (R² 0.52 → 0.005)
- Mathematical independence required (|r| < 0.02)
- Validated AUROC: 0.600, 0.585, 0.629 per spec
- **Reality:** Round 2.2a found Q_B (axis independence) FAIL at |r|=0.932 (prolif vs DDR). Spec says 0.02; reality 0.932. This is a known biology coupling, not arithmetic — proliferating leukemic cells co-regulate DDR. Round 2.2b specified residualization fix.
- **Status:** spec-vs-reality mismatch on independence threshold; FIX-005 in MASTER_FIXES documents threshold relaxation from 0.02 to 0.05; reality is 0.932 in AML.

Math Spec Module 3 (Two-Population ODE):
- Sensitive + resistant cell compartments
- Hill equation for drug effect
- Per-population Emax from KAALCURA
- **Reality:** Implemented as 4-state × 20-bin (80-compartment) phenotype-structured ODE in `intercepta_phenotype_ode_v1.py`. Round 1 closure documents 0/3 g-rate targets pass. Structural framework gap, not parameter issue.
- **Status:** Module 3 exists at v4.1; quantitatively limited per Round 1 closure.

Math Spec Module 4 (Synergy):
- ZIP + Bliss + Loewe + HSA consensus
- **Reality:** `synergy_scoring.py` (15KB) and `intercepta_synergy_v1.py` (23KB) exist.
- **Status:** Implemented; integration with Stage 5 ranking unclear.

### 2.4 Per the 15-layer Universal Net Spec — what's implemented

| Layer | Implementation status |
|-------|----------------------|
| 1 (Genome) | DONE per Phase A — gene catalog from GDSC + COSMIC |
| 2 (Transcriptome) | PARTIAL — bulk done, scRNA-seq partial, RNA velocity needs HPC |
| 3 (Proteome) | PARTIAL — 20 AlphaFold PDBs downloaded; full-disease URL fetching done in Workstream A Phase 2C |
| 4 (Interactome) | DONE — STRING v12 full integration, 236,838 edges |
| 5 (Pathway) | DONE — KEGG + Reactome integrated |
| 6 (Cell Type Atlas) | PARTIAL — mCRPC + AML cell type assignments done; universal Tabula Sapiens not integrated |
| 7 (Pharmacome) | DONE — GDSC + ChEMBL integrated for any disease via Workstream A Phase 2D |
| 8 (Metabolome) | PARTIAL — HMDB integration script exists at `step9_metabolome.py` |
| 9 (Disease Map) | DONE — OpenTargets 26,288 diseases × 23,422 targets via Workstream A Phase 1 |
| 10 (Immune) | PARTIAL — `step13_immune.py` exists, integration unclear |
| 11 (Microbiome) | PARTIAL — results files exist, build script not in bundle |
| 12 (Epigenome) | PARTIAL — results files exist, build script not in bundle |
| 13 (Anatomy) | PARTIAL — results files exist, build script not in bundle |
| 14 (Pathogen) | PARTIAL — results files exist, build script not in bundle |
| 15 (Selectivity) | PARTIAL — GTEx integrated for mCRPC; Workstream A doesn't compute per-disease selectivity |

**8 of 15 layers are DONE or near-complete; 7 are partial.** Round 3 closure §5.2 lists "8 of 15 universal net layers not integrated" as a known limitation. v3's reading is more granular but consistent.

---

## Section 3 — Honest assessment of Workstream A vs canonical architecture

Workstream A's wrapper code does the following per canonical architecture:
- **Stage 1 (Build the Complete Disease Net):** Yes — for any of 26,288 diseases via OpenTargets
- **Layer 1 partial:** Builds gene list with disease-association scores
- **Layer 4 (Interactome):** Yes via Phase 2B
- **Layer 3 (Proteome):** URL fetching only; no PDB downloads (Workstream C scope)
- **Layer 5 (Pathway):** No — wrapper doesn't pull pathway data per-disease
- **Layer 6 (Cell Type Atlas):** No — wrapper doesn't integrate scRNA-seq per-disease
- **Layer 7 (Pharmacome):** Yes via Phase 2D
- **Layer 9 (Disease):** Yes via Phase 1 + 2E (clinical trials portion)
- **Layer 15 (Selectivity):** Partial — GDSC tissue selectivity only, no per-disease GTEx

**Workstream A produces approximately Layers 1, 3 (URLs), 4, 7, 9, plus Phase 2E (Clinical sub-section of Layer 8 in canonical Net Architecture v2.0).** Five layers of fifteen. Plus partial Layer 15.

This is a meaningful contribution but it's not "the universal net." It's the universal-disease enrichment for the layers that have any-disease APIs (OpenTargets, STRING, AlphaFold URLs, ChEMBL, ClinicalTrials).

The remaining layers require either:
- mCRPC-specific data (SU2C, scRNA-seq for that disease) — Round 1 work
- AML-specific data (BeatAML, Van Galen) — Round 2 work
- Or per-disease integration that's not yet built

**This is the right architectural framing for Workstream A.** Not "the pipeline" but "the cross-disease enrichment layer that handles 5-7 of 15 canonical layers for any of 26,288 diseases."

---

## Section 4 — The canonical configuration mechanism (corrected from v1/v2)

v1 and v2 proposed JSON configs (`gbm.json`, `nsclc.json`, `mcrpc.json`) with hardcoded SOC + biomarkers. **Per the canonical architecture, this is wrong.** The disease net IS the configuration.

Per Net Architecture v2.0 Part 3 ("How ODE Parameters Derive FROM the Net"):
- Tumor growth rate from PSA doubling time (Layer 8) + proliferation gene signature (Layer 2) + cell type characteristics (Layer 6)
- Drug efficacy per population from GDSC IC50 (Layer 7) + KAALCURA from scRNA-seq (Layer 2) + pathway accessibility (Layer 4)
- Initial conditions from cell type proportions in scRNA-seq (Layer 6)
- Selectivity from GTEx ratio (Layer 15) + protein structure differences (Layer 3)
- Synergy from pathway crosstalk (Layer 5) + network topology (Layer 4)

**Every parameter traces to a layer.** The deliverable is generated FROM the net, not from a parallel config file.

This means: a per-disease deliverable generator should query the net for what it needs:
- Item 1 (structure): Layer 3 (AlphaFold) + Layer 7 (ChEMBL)
- Item 2 (mechanism): Layer 4 (interactions) + Layer 5 (pathways)
- Item 3 (predicted outcomes): Module 3 (ODE) consuming Layers 2, 6, 7
- Item 4 (resistance): Module 3 + Layer 6 (cell types)
- Item 5 (combination rationale): Layer 4 + Module 4 (synergy)
- Item 6 (safety): Layer 15 + Module 4 + ADMET tools (Stage 4 Layer E)
- Item 7 (synthesis): Stage 4 Layer F (ASKCOS)
- Item 8 (novelty): Layer 9 (clinical trials)
- Item 9 (vs SOC): Layer 8 (clinical) + comparator from net
- Item 10 (trial design): Layer 6 (biomarker stratification) + Layer 8 (endpoints)

**Where Workstream A currently fails to produce items 3, 4, 7, etc., it's because the upstream Modules and Layers aren't yet integrated for non-mCRPC diseases.** Not because the deliverable script is missing config. The architectural fix is upstream integration, not config.

This is significantly different from what v1 and v2 proposed.

---

## Section 5 — Revised refactor scope

Given the corrections in Sections 1-4, the right refactor scope changes:

### What I previously called "refactor"

v1 said: create `intercepta/` package with 8 subpackages, split god-functions, add JSON configs.

v2 said: refactor within `round3_gbm_live_test/code/`, split god-functions, add JSON configs.

### What v3 says

**The Workstream A wrapper genuinely needs cleanup but the cleanup is internal to the wrapper, not architectural reorganization.**

Internal cleanup tasks (real, valid):
1. Split `populate_chembl_compounds` into 3 functions (fetch, augment, populate-net). Same as v1/v2.
2. Refactor `rank_drugs_for_disease_v2` to require pre-enriched net as input (not call enrichment internally). Same as v1/v2.
3. Replace `_disease_to_tissue_keywords` 9-disease dict with GDSC tissue ontology lookup (canonical source per Net Architecture v2.0). v3 correction: this is canonical, not "a config replacement."
4. Standardize verdict taxonomy across the wrapper (PASS / PARTIAL / GAP / FAIL / N/A).
5. Delete dead code: `GBM_ONCOGENIC_DRIVERS`, `bbb_penetration_likely`, `_get_drug_rank_in_v2`.

**Architectural tasks that are NOT "refactor" but are real:**

A. **Reconcile Workstream A with canonical Layer naming.** Functions named `populate_string_interactions` should be `enrich_layer_4_interactome`. Phase 2A-2E terminology should be retired in favor of Layer naming. This is documentation+naming work, not code restructuring.

B. **Identify which canonical Layers Workstream A produces vs doesn't.** Document explicitly: "Workstream A produces Layer 4 fully, Layer 3 URLs only, Layer 7 partial, Layer 9 fully, Layer 8 clinical-portion." Add this to the Workstream A closure doc.

C. **Identify which canonical Modules consume the Workstream A net.** Right now, the existing 4 Modules (KAALCURA, PK, ODE, Synergy) are built for mCRPC and don't consume Workstream A's any-disease net. Workstream B is the question of generalizing Module 3 (ODE) to any disease. Workstream C is the question of building Module 5 (generative chemistry) plus making Module 1 (KAALCURA) per-disease.

D. **Rebuild reference deliverables with post-fix numbers.** `pharma_deliverable_enza_alis.json` has HR=0.692 from broken median-ratio. Real Cox PH gives 0.749. The reference should be regenerated with the post-fix ODE.

E. **Standardize the deliverable schema.** Choose 10-item (Vision 9.1) as canonical. Update `pharma_deliverable_complete.json` to match (currently 9-item). Add `item_5_combination_rationale` for monotherapy as `{"applicable": false, "reason": "monotherapy"}`.

F. **Resolve the terminology contradiction.** CLAUDE.md says "❌ pharma deliverable; say 'computational hypothesis package'." Vision Part 9 says "deliverable to pharma and researchers." Round 3 closure uses both. Pick one and update all docs.

### What this means for "1-2 sessions of refactor"

**v1 and v2 said 1-2 sessions.** v3 says: 1-2 sessions for Workstream A wrapper internal cleanup (tasks 1-5 above). Plus separately 1-2 sessions for the architectural reconciliation tasks (A-F). Total 2-4 sessions before Workstream B can begin on a clean foundation.

Or alternatively: skip A-F, do tasks 1-5 only, document A-F as "open architectural debts to address later," and proceed to Workstream B. This is faster but accumulates more debt.

**CSO recommendation:** do tasks 1-5 first (internal cleanup), then do A-B-C (canonical naming + Layer accounting + Module accounting) as documentation work in parallel with Workstream B. D-E-F can be addressed when the relevant outputs are next regenerated.

---

## Section 6 — Workstream B vs C readiness (final assessment)

Round 3 closure §7 recommended B before C. v3 confirms this with finer detail:

### Workstream B (ODE generalization to NSCLC)

**Canonical alignment:** This is generalizing Module 3 (Two-Population ODE) per Math Spec from mCRPC-specific to disease-agnostic.

**Required upstream Layers for NSCLC:**
- Layer 1: NSCLC mutations from cBioPortal — feasible, public APIs
- Layer 2: NSCLC scRNA-seq with raw FASTQ for RNA velocity — Kim et al. GSE131907 has this
- Layer 6: NSCLC cell types — derivable from scRNA-seq
- Layer 7: NSCLC drug responses from GDSC — already in disk (962 cell lines covers NSCLC)
- Layer 8: NSCLC clinical trials — KEYNOTE-024, FLAURA, ALEX, CodeBreaK 200 are the canonical 4 per Vision Part 7.2
- Layer 15: NSCLC-specific selectivity (lung tissue baseline from GTEx)

**Required Module 3 changes:**
- Replace mCRPC 4-state hardcoded structure (S, M, V, N) with NSCLC states (e.g., EGFR-sensitive, T790M-mutant, MET-amplified, EMT-resistant)
- Replace mCRPC-specific PK parameters with NSCLC drug PK
- Generalize cell-state definitions to be config-driven (this IS a use case where per-disease config makes sense — for cell state definitions, not net config)

**Locked success criterion (per Round 1 lesson):**
- Directional ranking correct on KEYNOTE-024, FLAURA, ALEX, CodeBreaK 200 (per Vision Part 7.2)
- Cox PH within ±20% of published HR for at least 3 of 4 trials per Phase 1 GroundTruth tolerance bound
- Per-population predictions distinguishable (Round 2.2a Q_E pattern: top-10 drug rankings differ between cell populations with Jaccard < 0.6)

**Estimated time:** 4-6 weeks per Round 3 closure §7.1.

### Workstream C (Universal ODE refactor + first novel molecule)

**Canonical alignment:** Refactor Module 3 to disease-agnostic; build Module 5 (generative chemistry) per Vision Part 4 Stage 3 Scout 2.

**Required upstream:**
- Workstream B output (ODE generalized to one second cancer)
- Module 3 abstractions for state definitions, cell-type couplings, drug-effect couplings
- REINVENT4 setup with selectivity-constrained scoring per Vision Part 4 Stage 4 Layer E
- ASKCOS retrosynthesis integration per Stage 4 Layer F
- A target with AlphaFold structure ready for docking (20 PDBs already on disk)

**Estimated time:** 6-8 weeks per Round 3 closure §7.1.

### Open governance items before B begins

1. **Round 2.2b status check** — implemented or not? closure exists where? This was open in v2; remains open in v3.
2. **Round 2.2c (therapeutic index) scope** — done by Round 2 or moved to B?
3. **Workstream B locked success criterion in writing** — per Round 2 lesson, no code without locked spec
4. **MASTER_FIXES status across 9 fixes** — which are closed, which open
5. **Reference deliverable regeneration** — is there value in regenerating with post-fix numbers, or accept stale-content disclaimer?
6. **Terminology decision** — "pharma deliverable" or "computational hypothesis package"

These should be resolved as documentation work (1 session) before Workstream B begins.

---

## Section 7 — What's actually canonical now (compendium)

For future Claude sessions, here is the canonical compendium per v3 reading:

**Founding documents:**
- `INTERCEPTA_COMPLETE_VISION_v1_0.docx` — Parts 1-12, March 2026
- `INTERCEPTA_Universal_Net_Specification_v1.0.docx` — 15 layers, March 29, 2026
- `INTERCEPTA_Phase1_MathSpec_v1_0.docx` — 4 modules, March 2026
- `INTERCEPTA_Phase1_GroundTruth_v1_0.docx` — 5-trial validation targets, March 2026

**Honest record (post-Round 1):**
- `docs/INTERCEPTA_Round1_Retrospective.md` — Round 1 closed at v4.1, April 21, 2026
- `docs/INTERCEPTA_CSO_Parameter_Memo_v2_1.md` — Round 1 closing addendum, April 21, 2026
- `docs/INTERCEPTA_Validation_Limitations_v1.md` — formal limitations doc

**AI co-founder onboarding (post-fix):**
- `CLAUDE.md` — April 18, 2026, current honest status
- `MASTER_FIXES.md` — 9 fixes documented April 18, 2026

**Round 2 record:**
- `round2_aml/docs/INTERCEPTA_Round2_2a_Closure.md` — FAIL on locked spec, Q_D and Q_E PASS
- `round2_aml/docs/INTERCEPTA_Round2_2b_Specification.md` — pre-code commit April 22, 2026
- (Round 2.2b closure: missing from bundle, status open)

**Round 3 record:**
- `round3_gbm_live_test/INTERCEPTA_Pipeline_v0_Closure.md` — Workstream A operationally closed
- `round3_gbm_live_test/INTERCEPTA_Architecture_Review.md` — v1 (this document supersedes; v1 preserved per P16)
- `round3_gbm_live_test/INTERCEPTA_Architecture_Review_v2.md` — v2 (preserved)
- `round3_gbm_live_test/INTERCEPTA_Architecture_Review_v3.md` — v3 (this document)

**Reference outputs:**
- `results/pharma_deliverable_enza_alis.json` — canonical 10-item shape, 2026-04-08, content stale per Apr 18 fix
- `results/pharma_deliverable_complete.json` — alternative 9-item schema, multi-candidate
- `results/INTERCEPTA_pharma_package.json` — earlier package
- `results/INTERCEPTA_FINAL_package.json` — wrapper output

**Codebase canonical mapping:**
- Modules 1-4 in `~/INTERCEPTA/code/intercepta_kaalcura_v1.py`, `intercepta_engine_v1.py`, `intercepta_phenotype_ode_v1.py` + `intercepta_unified_ode_v4_1.py`, `intercepta_synergy_v1.py`
- Layers 1-15 in `~/INTERCEPTA/code/step1_*.py` through `step14_*.py`
- Workstream A wrapper in `~/INTERCEPTA/round3_gbm_live_test/code/`
- Round 2 AML in `~/INTERCEPTA/round2_aml/code/`

---

## Section 8 — What v3 commits to NOT doing

After v3 reading, I commit to NOT:

- Refactoring code without explicit Prasad approval of v3's analysis
- Proposing module structure changes that don't align with canonical Layer 1-15 + Module 1-4
- Creating per-disease JSON configs (per Section 4, the disease net is the canonical configuration)
- Beginning Workstream B before locked success criterion is written
- Regenerating reference deliverables without explicit decision on stale-content handling
- Using "Phase 2A-2E" or "Workstream A subpackage" terminology going forward

What I commit to DO:

- Use canonical Layer 1-15 + Module 1-4 + Stage 1-5 names in all future work
- Document Workstream A's Layer coverage explicitly in any closure update
- Hold the architecture review at v3 unless Prasad asks for revision
- Preserve v1 and v2 per P16 (already on disk)
- Keep this document at 567 lines or shorter (matching v2's verbosity bound)

---

## Section 9 — What needs to happen next (revised priority)

Down from v2's 9-item list to 6 items, in priority order:

**Immediate (1 session):**
1. Prasad reviews v3. Confirms or pushes back. Identifies anything I still got wrong.
2. Round 2.2b status check — find or create the closure document.
3. MASTER_FIXES status check — read each fix's referenced file, report current state.

**Pre-Workstream B (1 session):**
4. Lock Workstream B success criterion in writing per Round 2 spec-first discipline. Use the locked-criterion structure from Round 2.2a Specification: Q_A/B/C/D criteria with explicit pass thresholds.
5. Decide reference deliverable regeneration policy (regenerate with post-fix numbers, or document stale-content disclaimer).
6. Decide terminology (pharma deliverable vs computational hypothesis package).

**Then Workstream B begins.**

---

## Section 10 — Final honest verdict (v3)

**v1 and v2 reviews invented their own taxonomy without reading the project's canonical taxonomy.** This was the central error of both. v3 corrects it by aligning to the 15-layer net + 4 mathematical modules + 5-stage pipeline + 6 simulation layers + 6 scouts + 10-item deliverable that the project documents specify.

**The Workstream A wrapper is real but smaller-scope than v1 implied.** It produces 5-7 of 15 canonical Layers for any of 26,288 diseases. That's a real contribution. It's not "the universal pipeline"; it's the universal-disease enrichment for the layers that have any-disease APIs.

**The required cleanup is internal to the wrapper plus documentation/naming work.** No new package. Refactor the god-functions (1-2 sessions). Reconcile naming with canonical Layer/Module taxonomy (documentation, parallel session). Then Workstream B.

**Workstream B's central question is generalizing Module 3 (ODE) from mCRPC to NSCLC.** Round 3 closure §7 recommendation B-before-C stands per v3.

**Round 1 closed with directional ranking correct, quantitative validation deferred.** Per the canonical 5-trial GroundTruth, 3/5 PASS with real Cox PH after Apr 18 fix. The honest framing: ranking works; quantitative HR matching is at 60% (3/5) with structural framework limits documented.

**The canonical pharma deliverable is 10 items per Vision 9.1.** The reference at `pharma_deliverable_enza_alis.json` implements all 10. The numbers in it are post-fix-broken; regeneration is a decision for Prasad.

**There is no canonical resolution of the "pharma deliverable" vs "computational hypothesis package" terminology.** Both are used in canonical project documents. CLAUDE.md takes the more conservative position. v3 recommends Prasad picks one.

— Claude (CSO/AI co-founder)
2026-05-06 (Architecture Review v3, after canonical .docx specs read)

— Prior versions: v1 (60572 bytes) and v2 (46293 bytes) preserved per P16 in same directory.
