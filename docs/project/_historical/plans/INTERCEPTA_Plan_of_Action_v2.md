# INTERCEPTA Plan of Action — From Where We Are to Full Vision Success

**Authors:** Prasad Akula & Claude (Co-Founders)
**Date:** May 2026
**Status:** Plan of Action v1 — built after deep re-read of vision + universal net spec, full audit of work-to-date, honest gap analysis

---

## Executive Frame

This document is the action plan for INTERCEPTA from today to full vision success. It is built on two non-negotiable principles you defined in our session:

- **No compromise at any point in the vision journey.** No artificial size limits, no time-boxing of what should be done over what fits in tonight, no cutting corners on validation, no claiming success where there is failure.
- **Every minute is precious because lives depend on the success of this vision.** This is not a reason to rush. It is a reason to use every minute on work that genuinely advances the vision, not work that feels productive while sidestepping hard problems.

The plan has three horizons of detail: near-term concrete (90 days), mid-term directional (3-12 months), long-term strategic (1-5 years to full vision). Where I can give specifics with evidence, I do. Where I would have to invent timelines or details, I name the unknowns explicitly rather than fabricate confidence.

**This plan does not assume more team than we have (just Prasad and Claude), more funding than we have (zero documented), or more wet-lab access than we have (none currently). Where the vision requires resources beyond what we have, the plan flags that as an open question rather than fictional progress.**

---

## Section 1 — Vision Synthesis (After Deep Re-Read)

After reading both vision documents end to end with fresh attention, INTERCEPTA is integrated of seven things, not the four I had pattern-matched in earlier passes:

### 1.1 INTERCEPTA is a drug discovery engine
Vision Part 1 + Part 9. For any disease, output is a complete 10-section drug candidate package: molecular structure, mechanism, predicted clinical outcomes, resistance profile, combination rationale, ADMET safety, synthesis route, novelty confirmation, vs-SoC comparison, suggested trial design.

### 1.2 INTERCEPTA is a diagnostic and predictive system
Vision Part 6. The same disease net used for drug discovery enables: early disease detection from molecular signatures, disease subtyping (aggressive vs indolent), treatment response prediction per patient, resistance monitoring with pre-resistant fraction tracking, polygenic risk integration combining genetic variants with transcriptional trajectory, microenvironment tracking, longitudinal trajectory analysis at tissue level, population-level surveillance for emerging disease signals, and modeling of diseases that don't yet exist (emerging pathogens, drug-resistant variants, novel metabolic disorders from environmental change).

### 1.3 INTERCEPTA is a self-improving knowledge system
Vision Part 7.3 + Part 12.1. Every disease solved teaches the system how to solve the next one faster. Cross-disease molecular transfer, model parameter improvement from validated predictions, scout refinement, progressive net completion. Vision target: "finding a drug for any new disease takes days, not decades."

### 1.4 INTERCEPTA is a digital model of human biology
Universal Net Spec Parts 1-7. 15 layers, ~3M nodes, 10-50M edges. The complete digital human body. When fully built, finding a drug for any disease becomes a query, not a project.

### 1.5 INTERCEPTA is a healthy-cell-protection-first architecture
Vision Part 8.3. Selectivity is not a final ranking criterion — it is a design constraint. Molecules that fail selectivity are eliminated in Stage 3, not Stage 5. ADMET specifically models healthy organ toxicity. Therapeutic index is primary ranking criterion.

### 1.6 INTERCEPTA is built on open science
Vision Part 8.2 + Part 12.4. All data sources public and IP-restriction-free. Published disease nets for academic use. Co-publication model with academic groups validating candidates. API access for researchers. The discovery method is open; discovered novel molecules can be patented.

### 1.7 INTERCEPTA may require novel technology development
Vision Universal Net Spec Part 7. Multi-scale GNNs, temporal knowledge graphs, causal inference on biological graphs, federated learning for clinical data, generative chemistry constrained by knowledge graphs. The vision explicitly anticipates that some of this technology may need to be invented, not just integrated.

### 1.8 The Three Unique Scientific Contributions
Vision Part 5 — these are what make INTERCEPTA different:

- **5.1 RNA Velocity Time Machine.** Detect pre-resistant 'undead' cells (5-15% of tumor at diagnosis) before treatment using unspliced/spliced mRNA ratio. Vision says "no published drug discovery platform does this."
- **5.2 KAALCURA per-population biological axes.** R_prolif, R_emt, R_ddr — three mathematically-independent residualized axes (R² drops from 0.52 to 0.005 after tissue-of-origin removal). Apply per-cluster, not bulk. Validated GDSC AUROC 0.585-0.629, all p<0.001.
- **5.3 Two-Population ODE.** Sensitive + resistant compartments, PK/PD integration, ZIP+Bliss+Loewe+HSA consensus synergy, dose-schedule optimization. Vision claim: validated against CHAARTED, LATITUDE, PROfound, PROpel "from first principles."

### 1.9 The Six Parallel Scouts
Vision Part 3.3 — what searches the disease net for candidates:

- **Scout 1: Database Search** — ChEMBL, PubChem, ZINC for molecules with known activity
- **Scout 2: Generative Design** — diffusion / transformer-based AI generating novel chemical entities
- **Scout 3: Combination Explorer** — permutations covering all vulnerability points
- **Scout 4: Network Perturbation** — predicts compensation pathways causing resistance
- **Scout 5: Evolutionary Optimizer** — mutates structures to improve potency / safety
- **Scout 6: Cross-Disease Transfer** — repurposing from solved diseases

Critically, scouts share insights bidirectionally per Vision Part 10.2. This is architectural, not just sequential.

### 1.10 The Five-Stage Pipeline
Vision Part 4 — what every disease passes through:

1. **Stage 1: Build Complete Disease Net** (15 layers, automated)
2. **Stage 2: Map Vulnerability Points + Selectivity** (disease-specific nodes, healthy-shared nodes, resistance nodes, escape routes)
3. **Stage 3: Deploy Six Parallel Scouts** (no pre-filtering principle — bad individual molecules may make excellent combinations)
4. **Stage 4: Six-Layer Simulation Stack** — Layer A (binding via AutoDock Vina + AlphaFold), Layer B (cell population sensitivity via KAALCURA), Layer C (disease dynamics via ODE), Layer D (combination synergy via ZIP+Bliss+Loewe+HSA), Layer E (ADMET via SwissADME/pkCSM/ADMET-AI), Layer F (synthesizability via ASKCOS)
5. **Stage 5: Multi-Objective Ranking + Delivery** — Pareto ranking with weights: Efficacy 30%, Selectivity 25%, Safety 20%, Resistance 15%, Novelty 5%, Synthesizability 5%

### 1.11 The Disease Expansion Sequence
Vision Part 7.2:

- Round 1: mCRPC (best clinical trial ground truth: CHAARTED, LATITUDE, PROfound, PROpel, TALAPRO-2)
- Round 2: AML (perfect two-population biology, BeatAML matched drug response)
- Round 3: NSCLC (largest cancer burden, EGFR/KRAS, KEYNOTE-024, FLAURA, CodeBreaK 200)
- Round 4: PDAC (near-zero treatments, FOLFIRINOX baseline)
- Round 5: Alzheimer's (no disease-modifying drug exists, BBB constraint)
- Round 6: Drug-resistant TB (1.5M deaths/year, XDR-TB)
- Round 7+: All rare diseases (7000+), emerging pathogens, future diseases

### 1.12 The Build Roadmap
Vision Part 11 — explicit phase plan:

- **Phase 0: Foundation (DONE per vision):** KAALCURA + Two-population ODE + ZIP/Bliss/Loewe/HSA + Pareto + CT.gov novelty + 15-drug mCRPC PK library + GDSC drug sensitivity
- **Phase 1: mCRPC Validation (Weeks 1-6):** ODE+KAALCURA recovers CHAARTED/LATITUDE/PROfound/PROpel; first novel candidate list for mCRPC
- **Phase 2: RNA Velocity Integration (Weeks 7-14):** scVelo + per-cluster KAALCURA; full Day 1 workflow scRNA-seq biopsy → two populations → combination
- **Phase 3: Molecular Discovery Layer (Weeks 15-24):** automated ChEMBL/PubChem; AutoDock Vina; generative chemistry scout; ADMET pipeline
- **Phase 4: Disease Net Builder (Weeks 25-36):** automated KEGG/Reactome/STRING/UniProt; selectivity map; escape route identification; apply to AML, validate against BeatAML
- **Phase 5: Universal Platform (Weeks 37-52):** full pipeline running for mCRPC and AML; first pharma deliverable; expansion to NSCLC/PDAC/Alzheimer's; first publication

### 1.13 The Universal Net 20-Step Build Plan
Net Spec Part 5 — explicit step-by-step:

- **Phase A (DONE per spec):** Steps 1-2 (gene-drug correlations, SU2C mCRPC, KAALCURA validated)
- **Phase B (Core Layers):** Steps 3-7 (mCRPC scRNA-seq, STRING, KEGG/Reactome, GTEx, ChEMBL)
- **Phase C (Universal Expansion):** Steps 8-13 (DisGeNET, HMDB, AlphaFold, Human Cell Atlas, ENCODE/Roadmap, Immune)
- **Phase D (Future-Proofing):** Steps 14-17 (Pathogens, Microbiome, Spatial, Full ZINC pharmacome)
- **Phase E (Self-Improving):** Steps 18-20 (Literature mining, Clinical feedback loop, Cross-disease transfer learning)

### 1.14 The Honest Limitations The Vision Itself Names
Vision Part 12.5 — these are stated by the vision authors:

- Computational predictions are not clinical proofs. Wet-lab required.
- RNA velocity has known limitations for some data types/protocols.
- Generative chemistry can produce chemically exotic molecules difficult to synthesize.
- ODE models two populations; real tumors have more.
- Self-improving loop requires clinical outcome data flow — partnerships taking years.

---

This is the integrated vision. It is more than I had been holding. The next sections compare each integrated claim to what we have actually built.
# Section 2 — Reality Audit (What We Have, With Evidence)

This section catalogs every meaningful artifact, finding, and validated capability from work to date. Each entry cites the source so claims are checkable.

## 2.1 Validated Scientific Capabilities

### KAALCURA on GDSC cell lines — VALIDATED
- **AUROC range:** 0.638–0.671 across 286 drugs × 962 cell lines
- **Verified:** April 20 rerun in `~/INTERCEPTA/kaalcura_revalidate_results.txt`
- **Three axes:** R_prolif (proliferation), R_emt (epithelial-mesenchymal transition), R_ddr (DNA damage response)
- **Mathematical independence:** r<0.02 for all axis pairs
- **Tissue-bias removed:** R² drops from 0.52 to 0.005 after residualization
- **Status:** Vision claim is real on cell lines

### KAALCURA on patient samples (BeatAML) — PARTIAL / DOCUMENTED LIMITATION
- **AUROC plateau:** ~0.53 across three rounds (2.1d z-score, 2.2a pyUCell, 2.2b residualized)
- **Threshold for accept:** 0.55 — not reached
- **Real finding:** Cell-line-to-patient transfer is a documented scientific gap, not an axis architecture problem
- **Status:** Vision claim is half-true. Cell lines yes; patient samples no.

### Two-population mCRPC ODE — VALIDATED WITH DOCUMENTED LIMITATIONS
- **Closed:** Round 1 closure documented in `~/INTERCEPTA/docs/INTERCEPTA_Round1_Errata_v1_0.md`
- **g-rate validation:** 0/3 confirmed targets pass
- **HR validation:** 2/6 trials pass HR window
- **Systematic bias:** ~2× documented in `~/INTERCEPTA/docs/INTERCEPTA_Validation_Limitations_v1.md`
- **Direction:** Within-trial drug ranking is directionally correct
- **Status:** Vision claim "validated against CHAARTED/LATITUDE/PROfound/PROpel from first principles" is half-true. Direction yes; quantitative HRs no.

### AML Net Skeleton — VALIDATED
- **Built:** Round 2.1, completed before this session series
- **Scale:** 1,201 nodes, 33,191 edges
- **Validation queries (PASSED):** FLT3-ITD+/NPM1+ → Gilteritinib + Venetoclax in top 10; TP53+ → Jaccard 0.25 from FLT3+ recommendations
- **Validated against:** ELN 2022 standard-of-care
- **File:** `~/INTERCEPTA/round2_aml/results/aml_net_skeleton_v2_summary.json`
- **Status:** Real, validated, vision-aligned for one disease

### ZIP + Bliss + Loewe + HSA Synergy Scoring — REAL
- **Built and integrated** per Round 1 closure
- **Validated against:** NCI-ALMANAC per vision Part 10
- **Status:** Real

### Pareto Ranking — REAL
- **Built:** `~/INTERCEPTA/code/pareto_ranking.py`
- **Functions:** `build_mcrpc_candidates()`, `composite_score()`, `pareto_front()`, `rank_candidates()`
- **mCRPC output:** `~/INTERCEPTA/results/pareto_ranking_mcrpc.json`
- **Status:** Real for mCRPC. Functions are mCRPC-named (build_mcrpc_candidates), suggesting not yet generalized.

### ClinicalTrials.gov Novelty Checker — UNCLEAR / NOT FOUND
- **Vision claim:** "Real-time IP validation for every candidate"
- **Reality:** No `*novelty*` or `*clinicaltrials*` script found in `~/INTERCEPTA/code/` per inventory
- **Status:** Either embedded in another script or not built as standalone. Mentioned as DONE in Vision Phase 0 — but evidence on disk does not show standalone module.

## 2.2 Pipeline Infrastructure (Phase 1 + Phase 2A from this session)

### `intercepta_pipeline_v0.py` — BUILT, VERIFIED
- **File:** `~/INTERCEPTA/round3_gbm_live_test/code/intercepta_pipeline_v0.py` (416 lines)
- **6 working functions for any disease in OpenTargets:**
  - `resolve_disease(name)` — best ontology ID with disambiguation (Gap 1+2 closed)
  - `build_net(name_or_id)` — biology-correct disease net (Gap 1 closed)
  - `corrected_net_summary(net)` — honest counts (Gap 5 closed)
  - `inspect_gdsc_drugs()` — GDSC2_fitted_dose_response.xlsx auto-detection (Gap 4 closed)
  - `rank_drugs_for_disease(name)` — tissue-filtered drug ranking (Gap 10 closed)
  - `enrich_with_metabolites(net)` — 314 metabolites populated for GBM (Gap 9 closed)
- **Verified on GBM:** Phase 1 + 2A passed all assertions
- **Status:** Real, working infrastructure foundation

### Universal Net (mCRPC-anchored)
- **File:** `~/INTERCEPTA/results/mcrpc_unified_net.json` (51MB)
- **Diseases queryable:** 47,030 (via OpenTargets disease layer)
- **Pathway layer:** ~1,530 pathways for GBM (Vision Layer 5 — real)
- **Drug layer:** 14 GBM genes have compounds; 434/458 have drug correlations from GDSC
- **STRING interactions:** 81/458 GBM genes (mCRPC-centric population — Finding 8)
- **Structures:** 0 attached to disease nets (Finding 11 — AlphaFold cache exists but doesn't join)
- **Metabolites:** 314 attached to GBM after Phase 2A (Gap 9 closed)
- **Status:** Infrastructure is real. Layer population is uneven across diseases — mCRPC is dense, GBM has gaps that the live test surfaced.

## 2.3 Round 1 Artifacts on Disk

These are real files I confirmed via inventory:

- `mcrpc_unified_net.json` (51M)
- `mcrpc_top_combos_validated.csv`
- `pareto_ranking_mcrpc.json`
- `scout3_combinations_ranked.csv`
- `scout4_combos_v2.csv`
- `scout1_novel_combos.csv`
- `mcrpc_combination_screen.csv`
- `mcrpc_monotherapy_screen.csv`
- `bootstrap_stability.json`
- `layer_f_synthesizability.json`
- `novel_combinations.json`
- `unified_v5_2_g_validation.json` (Round 1 final ODE outputs)
- `unified_v5_1_g_validation.json`
- `phase1_5trial_VALIDATED.csv`
- `phase1_calibrated_params_VALIDATED.json`
- `capability_test_results.json`
- `mcrpc_disease_net.json`

Round 1 produced real artifacts for mCRPC. The inventory above is a partial pharma deliverable's worth of input data already on disk for olaparib + abiraterone (PROpel combination).

## 2.4 ODE Modules Inventoried

Four ODE files exist in `~/INTERCEPTA/code/`:

- `intercepta_unified_ode_v4_1.py` (43K) — Round 1 final mCRPC ODE
- `intercepta_three_mechanism_ode.py` (30K) — DRUG_LIBRARY with 7 entries
- `intercepta_phenotype_ode_v1.py` (48K) — DRUG_EFFECT_LIBRARY + PK_LIBRARY with 6 entries each
- `aml_ode_v6_resistance.py` (11K) — AML-specific

**Total unique drugs parameterized across all ODE modules: 7** (docetaxel, cisplatin, enzalutamide, abiraterone, ADT, olaparib, talazoparib).

**Hardcoded prostate cell states across all modules:**
- `S_ARDEP, S_ARMUT, S_ARV7, S_NE` — AR-dependent, AR-mutant, AR-V7, neuroendocrine
- `MU_S_TO_M, MU_S_TO_V, MU_S_TO_N` — prostate-specific transition rates
- `BRCA_FRAC_OVERALL, BRCA_FRAC_SELECTED` — prostate-specific BRCA distribution

**Status:** ODE infrastructure exists for mCRPC and partially for AML. Universal disease support requires structural refactor.

## 2.5 RNA Velocity Status

### Vision claim: "Core scientific innovation"
### Reality (per inventory):

- Existing script: `~/INTERCEPTA/code/step3_run_scvelo.py`
- Expected input: STARsolo output at `~/INTERCEPTA/data/velocity/velocity_out/*_spliced.mtx`
- **The velocity_out directory does not exist.** The script has never executed end-to-end with real data.
- Available scRNA-seq data on disk:
  - GSE137829 (mCRPC, 6 patients P1-P6, 76MB) — **expression matrices only, NO spliced/unspliced**
  - GSE141445 (Chen et al., mCRPC, 36,424 cells, 10X Genomics, 757MB) — **processed count matrices only, NO spliced/unspliced**
- **Generating spliced/unspliced** requires either BAM files + velocyto (BAMs not on disk) or upstream STARsolo with `--soloFeatures Gene Velocyto` (not run)

**Status:** The Time Machine, named in vision Part 2.2 as "INTERCEPTA's core scientific innovation," has **zero working examples beyond a placeholder script for one mCRPC dataset that has never executed.**

## 2.6 The 19 Findings From the GBM Live Test (May 2 Session)

The live test validated end-to-end pipeline behavior on a never-touched disease (glioblastoma). Each finding documents a specific gap:

1. Universal Net is mCRPC-anchored (file named `mcrpc_unified_net.json`)
2. pyarrow missing in env (closed Phase 1)
3. `build_net` requires ID, not name (closed Phase 1)
4. Multi-version GBM ID disambiguation needed (closed Phase 1)
5. Net summary inconsistencies (closed Phase 1)
6. ChEMBL cache mCRPC-curated (open — Gap 7 in alternate numbering)
7. GTEx selectivity wrong question for oncology (open)
8. Universal net interactions mCRPC-centric (open)
9. EGFR→MET escape route NOT in net (open — vision claim broken for GBM)
10. Metabolite layer doesn't join (closed Phase 2A)
11. Structure layer doesn't join (open)
12. (Corrected) GDSC drug-target was in dose-response Excel (closed Phase 1)
13. 53 brain cell lines, 12,001 measurements available (data layer real)
14. Stage 3 needed manual glue (closed Phase 2A)
15. 53 GBM cell lines available (real)
16. GDSC AUC ranking doesn't match GBM clinical reality (open — scientific scoring gap)
17. Manual synthesis required for Stage 3 (closed Phase 2A)
18. ODE structurally mCRPC-only (open — structural)
19. DiseaseNetBuilder relative path bug (closed Phase 1)

**Of 19 findings: 8 closed (Phase 1 + Phase 2A), 11 open.**

## 2.7 The Five-Stage Pipeline Live Test on GBM (May 2)

Real end-to-end test of the vision's pipeline on a disease never previously analyzed:

- **Stage 1 (Build Disease Net):** PARTIAL. After Phase 1 fixes: works. Returns 458 GBM genes via EFO_0000519 with EGFR/IDH1/TP53/PTEN at top.
- **Stage 2 (Map Vulnerabilities + Selectivity):** PARTIAL. STRING interactions sparse (81/458). EGFR→MET escape route absent. ChEMBL coverage sparse for non-mCRPC targets.
- **Stage 3 (Deploy Scouts):** ORCHESTRATION CLOSED, SCORING UNCHANGED. After Phase 2A fix: produces ranked drug list. But ranking dominated by broad cytotoxics; Temozolomide (GBM SoC) ranks #247/286.
- **Stage 4 (Six-Layer Simulation Stack):** STRUCTURALLY FAILED. Only Talazoparib (1 of 3 GBM picks) is in any ODE library. State structure is prostate-specific.
- **Stage 5 (Multi-Objective Ranking + Deliverable):** PARTIAL. Pareto ranking ran. Pharma deliverable: 3 of 10 sections populated, 7 of 10 NOT AVAILABLE.

**Cumulative truth:** The pipeline works end-to-end on mCRPC. It works partially through Stage 3 on GBM after Phase 2A fixes. Stage 4 cannot run for any disease except mCRPC. Stage 5 produces an incomplete deliverable.

## 2.8 Three Structural Gaps Identified

After comparing vision claims to the live test findings, three gaps dominate everything else:

### Structural Gap A: Generative Chemistry Not Built
- Vision Part 5 / Stage 3 / Scout 2 / Phase 3: diffusion or transformer-based generative chemistry
- Reality: scaffold hopping only (per Exhaustive Audit)
- Tool requirements: REINVENT4 or equivalent — Apple Silicon CPU compatibility issues; install non-trivial
- **Without this, INTERCEPTA cannot discover novel molecules.** The vision's central act ("find the drug") is impossible. The system can only re-rank existing compounds.

### Structural Gap B: RNA Velocity Time Machine Not Generalized
- Vision Part 2.2 + 5.1: named "core scientific innovation"
- Reality: pilot script for one mCRPC dataset, never executed end-to-end. Required spliced/unspliced data not on disk for any cancer.
- Without this, INTERCEPTA cannot detect pre-resistant cells (the entire premise of "the time machine"), cannot compute per-cluster KAALCURA the way vision specifies, cannot do Day 1 workflow scRNA-seq → two populations → combination.

### Structural Gap C: Two-Population ODE Hardcoded Prostate-Only
- Vision Part 5.3: "validated against 5 trials" — true for mCRPC
- Reality: 7 hardcoded mCRPC drugs across all ODE modules. Cell states (S/M/V/N) are AR-dependent, AR-mutant, AR-V7, neuroendocrine — prostate biology only. Transition rates calibrated for prostate. State-sensitivity matrix is prostate-specific.
- Without this, INTERCEPTA cannot run dynamics for any new disease without months of literature-research-driven parameterization per disease.

## 2.9 What Has Been Built That The Vision Does NOT Specify

These are work products that exist but aren't in vision documents — co-founder additions or session-driven work:

- The `intercepta_pipeline_v0.py` orchestrator (Phase 1 + 2A this session)
- Round 2 AML net skeleton (vision specified "validate against BeatAML" but skeleton-first approach is execution detail)
- Round 1 closure with documented limitations (Validation Limitations doc — vision specifies validation but not formal closure docs)
- The 19-finding live test methodology
- KAALCURA's residualized-axes verification with AUROC=0.638 retest

These represent real work that should be preserved but aren't claims in the vision document.

---

This is the complete reality audit. The next section maps each vision claim to this reality with explicit alignment ratings.
# Section 3 — Vision-vs-Reality Alignment Map (v2 — Refined)

This section rates every meaningful vision claim against current reality, with corrections from the deeper analysis in this revision.

The rating scale:

- **ALIGNED** — vision claim is real and validated as stated
- **PARTIAL** — vision claim is real for some specific case, not the universal claim made
- **MID-DISTANCE** — meaningful work exists but does not yet satisfy the vision claim
- **MAJOR-DISTANCE** — vision claim is largely or entirely unbuilt
- **UNBUILT** — no meaningful work exists toward this claim

For each: a one-line evidence citation. No claim made without a verifiable file or finding.

**v2 corrections from deeper analysis are flagged explicitly.**

---

## 3.1 Drug Discovery Engine (Part 1)

| # | Vision Claim | Rating | Evidence |
|---|---|---|---|
| 1.1 | "Discovers novel drug molecules and combinations for any disease" | MAJOR-DISTANCE | Re-ranks existing drugs only. Scaffold hopping per audit; no generative chemistry built. |
| 1.2 | "Delivers real drug candidates to pharma so only clinical trials remain" | MAJOR-DISTANCE — *qualified* | **v2 correction:** "Only clinical trials remain" is materially incorrect even when fully built. Wet-lab validation precedes IND filing precedes Phase 1. The vision's framing skips wet-lab and IND phases. The honest claim is "delivers candidates ready for wet-lab validation and downstream regulatory work." |
| 1.3 | "For ANY disease — past, present, or future" | PARTIAL | Pipeline runs end-to-end for mCRPC. Partial Stages 1-3 for any OpenTargets disease (post Phase 2A). Stage 4+5 universally absent. |

## 3.2 The Undead Cells / RNA Velocity (Part 2.2 + 5.1)

| # | Vision Claim | Rating | Evidence |
|---|---|---|---|
| 2.1 | "Detect pre-resistant 'undead' population on Day 1 using RNA velocity" | UNBUILT | scvelo script never executed end-to-end. No spliced/unspliced data on disk for any cancer. |
| 2.2 | "Find combination that kills BOTH populations simultaneously" | MID-DISTANCE | Two-population ODE concept built for mCRPC. Per-cluster KAALCURA application not yet validated. |
| 2.3 | "Before resistance ever fully develops" | UNBUILT | Depends on 2.1 (pre-resistant detection) — currently absent. |

## 3.3 The Net Approach (Part 3)

| # | Vision Claim | Rating | Evidence |
|---|---|---|---|
| 3.1 | "Literal knowledge graph — every node connected to every other through validated relationships" | PARTIAL | mCRPC net real (51MB). For new diseases (GBM): pathway and disease-gene layers populate; STRING interactions only mCRPC-populated (81/458 GBM genes). |
| 3.2 | "10 layers" (genomic, transcriptomic, proteomic, pathway, network, cellular, chemical, clinical, environmental, selectivity) | MID-DISTANCE | OpenTargets disease layer real (47K diseases). Pathways real (1,530 GBM). Chemical sparse. Cellular present for mCRPC only. Selectivity present but heuristic. |
| 3.3 | "Six parallel scouts deploy simultaneously, share insights bidirectionally" | MAJOR-DISTANCE — *re-rated* | **v2 correction:** Was MID-DISTANCE. Re-rated MAJOR after deeper analysis showed bidirectional sharing requires graph DB + event bus architecture (months of engineering), not just scout coordination. Currently sequential pipeline only. |
| 3.4 | "Every scout continuously shares what it finds with every other scout" | UNBUILT | No event bus, shared state, or message-passing architecture exists. **v2 note:** Realistic Horizon 2-3 work, not Horizon 1. |
| 3.5 | "INTERCEPTA tests everything" / "no pre-filtering" | PARTIAL — *qualified* | **v2 addition:** Vision rhetoric implies exhaustive testing. Computationally impossible (2.4M ChEMBL × 2.4M = 2.88T pairs). Correctly interpreted: "don't pre-filter on individual activity, do filter on physical viability." Architecture supports the intended principle even if not the literal phrasing. |

## 3.4 The Five-Stage Pipeline (Part 4)

| # | Vision Claim | Rating | Evidence |
|---|---|---|---|
| 4.1 | Stage 1: Automated complete disease net for any disease | PARTIAL | After Phase 1 fixes: name → ID → net works. Layers populated unevenly per disease. |
| 4.2 | Stage 2: Vulnerability map + selectivity + escape routes | MID-DISTANCE | Vulnerability identification works via association scores. Selectivity is GTEx-heuristic only (Finding 7). **Escape routes BROKEN for GBM** — EGFR has 0 interactions populated (Finding 9). |
| 4.3 | Stage 3: Six scouts run simultaneously with no pre-filtering | MAJOR-DISTANCE | Only Scout 1 + Scout 3 work; not in parallel; no shared state. |
| 4.4 | Stage 4 Layer A: AutoDock Vina molecular binding | PARTIAL | Vina cached results in `data/docking/` (3.2MB). Per audit, used for AURKA. Not integrated as universal Stage 4 layer. |
| 4.5 | Stage 4 Layer B: KAALCURA per-population sensitivity | PARTIAL | KAALCURA validated on cell lines (AUROC 0.638-0.671). Per-cluster patient application plateaus at 0.53. |
| 4.6 | Stage 4 Layer C: Two-population ODE dynamics | PARTIAL | Real for mCRPC with documented 2× systematic bias. Not applicable to other diseases (Finding 18). |
| 4.7 | Stage 4 Layer D: ZIP+Bliss+Loewe+HSA synergy | ALIGNED | Real, validated against NCI-ALMANAC. Code present. |
| 4.8 | Stage 4 Layer E: SwissADME + pkCSM + ADMET-AI safety | UNBUILT | Per inventory: ADMET-AI not installed, RDKit not installed, no SwissADME integration. |
| 4.9 | Stage 4 Layer F: ASKCOS retrosynthesis | PARTIAL | `layer_f_synthesizability.json` exists for mCRPC; universal integration absent. |
| 4.10 | Stage 5: Pareto ranking with weights | PARTIAL | Pareto ranking real for mCRPC. `build_mcrpc_candidates()` function name suggests not generalized. |
| 4.11 | Stage 5: 10-section pharma deliverable | MAJOR-DISTANCE | Never produced fully. GBM Stage 5: 3/10 populated. mCRPC Round 1: artifacts exist but never assembled into deliverable format. |

## 3.5 Three Unique Scientific Contributions (Part 5)

| # | Vision Claim | Rating | Evidence |
|---|---|---|---|
| 5.1 | RNA Velocity Time Machine — detect pre-resistant cells before treatment | UNBUILT | No working examples. Pilot script depends on data not on disk. |
| 5.2 | KAALCURA per-population biological axes | PARTIAL | Validated on cell lines. Not validated on patient samples (BeatAML plateau 0.53). |
| 5.3 | Two-population ODE validated against CHAARTED/LATITUDE/PROfound/PROpel from first principles | PARTIAL — *qualified* | Direction yes, quantitative HRs no. ~2× systematic bias documented. mCRPC-only. **v2 note:** "From first principles" was retroactively recognized as wrong by vision authors themselves (Net Spec Part 4: "Our ODE simulation failed because we hand-picked parameters"). |

## 3.6 Diagnostic and Predictive Layer (Part 6) — *DECOMPOSED IN V2*

**v2 correction:** Was lumped together as "MAJOR-DISTANCE entire chapter." Decomposed by feasibility into three sub-areas:

### 6.1 Current Disease Identification — feasibility variable

| # | Vision Claim | Rating | Feasibility | Evidence / Prerequisites |
|---|---|---|---|---|
| 6.1.1 | Early disease detection (signature matching pre-symptoms) | UNBUILT | Partnership-gated | Requires biobanks / longitudinal cohort access |
| 6.1.2 | Disease subtyping (aggressive vs indolent) | UNBUILT | Moderate-feasible | Achievable with SEER + TCGA outcome data |
| 6.1.3 | Treatment response prediction (per patient) | UNBUILT | **HIGH-feasible** | Extension of KAALCURA infrastructure for individual patient input |
| 6.1.4 | Resistance monitoring (pre-resistant fraction tracking) | UNBUILT | Partnership-gated | Requires Time Machine generalized + clinical sample series |

### 6.2 Future Disease Risk Prediction — partnership-gated

| # | Vision Claim | Rating | Feasibility | Evidence / Prerequisites |
|---|---|---|---|---|
| 6.2.1 | Polygenic risk integration | UNBUILT | Computational moderate | GWAS Catalog data + risk scoring algorithms exist |
| 6.2.2 | Microenvironment tracking | UNBUILT | Partnership-gated | Patient inflammatory/immune profiles + cohort data |
| 6.2.3 | Longitudinal trajectory analysis | UNBUILT | Partnership-gated | Repeat patient samples + Time Machine generalized |
| 6.2.4 | Population-level surveillance | UNBUILT | Major regulatory + privacy infrastructure | IRB compliance, federated approach |

### 6.3 Future Disease Modeling — separate research programs

| # | Vision Claim | Rating | Feasibility | Evidence / Prerequisites |
|---|---|---|---|---|
| 6.3.1 | Pathogen evolution modeling | UNBUILT | Distinct multi-month research program | Pathogen genome layer (Net Spec Layer 14) |
| 6.3.2 | Cross-disease network analysis | UNBUILT | **HIGH-feasible** | Emerges naturally from self-improving loop |
| 6.3.3 | Synthetic biology threat modeling | UNBUILT | Out of plausible scope for two-person team | Requires biosecurity expertise + clearances |

**v2 strategic re-assessment:** Three sub-capabilities are HIGH-feasible because they extend existing infrastructure (6.1.3, 6.1.2, 6.3.2). Six are partnership-gated. Two are separate research programs. The vision's lumped "Part 6 chapter unbuilt" framing obscures that part of Part 6 is reachable in Horizon 2 timeframe while other parts are Horizon 3+ or out-of-scope.

## 3.7 Universal Expansion / Self-Improving (Part 7)

| # | Vision Claim | Rating | Evidence |
|---|---|---|---|
| 7.1 | Validation-first principle for every disease | ALIGNED | Round 1 + Round 2 followed this. |
| 7.2.R1 | Round 1 mCRPC complete | PARTIAL | Closed with 0/3 g-rate, 2/6 HR, 2× bias documented. |
| 7.2.R2 | Round 2 AML complete | PARTIAL | Net skeleton validated. KAALCURA-on-patients plateau at 0.53. |
| 7.2.R3-R7 | NSCLC, PDAC, Alzheimer's, TB, rare diseases | UNBUILT | None started. |
| 7.3 | "Days, not decades" for new diseases | UNBUILT — *qualified* | **v2 correction:** This claim conflates timescales. Computational candidate generation can plausibly drop to days. Wet-lab + IND + clinical trial cycles remain years (physical processes). The honest re-statement: "computational days, total cycle still years — INTERCEPTA replaces the slow R&D phase, not the slow physical phase." |
| 7.3 | Self-improving loop | UNBUILT | No feedback mechanism, no cross-disease learning, no clinical outcome integration. |

## 3.8 Healthy Cell Protection (Part 8.3) — *EXPANDED IN V2*

**v2 correction:** Was 3 sub-claims; expanded with architectural specificity.

| # | Vision Claim | Rating | Architectural Implication |
|---|---|---|---|
| 8.3.1 | Selectivity is design constraint, not final filter | MID-DISTANCE | Currently soft scoring via GTEx. Vision says architectural enforcement at Stage 3 scout output. |
| 8.3.2 | Molecules failing selectivity eliminated in Stage 3 | UNBUILT | **v2 specification:** Generative chemistry (Workstream C) must include selectivity scoring component. REINVENT4 multi-objective config: (binding to target) × (1 / binding to off-targets). Off-target panel: related kinases expressed in healthy tissue. Vision's "selectivity ratio > 10:1" becomes a scoring threshold. |
| 8.3.3 | ADMET specifically models healthy organ toxicity | UNBUILT | ADMET tools not integrated. |
| 8.3.4 | Therapeutic index (disease kill / healthy kill) is primary ranking criterion | PARTIAL | Selectivity weight 25% in Pareto ranking — present in mCRPC, must propagate to all disease nets. |

## 3.9 Open Science (Part 8.2 + 12.4)

| # | Vision Claim | Rating | Evidence |
|---|---|---|---|
| 8.2.1 | All data sources public and IP-restriction-free | PARTIAL — *qualified* | **v2 correction:** Most are. Several have license terms: ChEMBL (CC-BY-SA share-alike), DrugBank (academic license for some), COSMIC (academic license), DisGeNET (API license), PhosphoSitePlus (academic license), GISAID (academic terms). Open Q 4.8 documents this. |
| 12.4.1 | Publish disease nets openly | UNBUILT | No published nets to date. |
| 12.4.2 | Co-publication model with academic groups | UNBUILT | No academic partnerships established. |
| 12.4.3 | API access for researchers | UNBUILT | No public API. |

## 3.10 Pharma Deliverable (Part 9.1)

[Same as v1 — 3-4 of 10 sections populatable from existing artifacts. Aligned with GBM Stage 5 finding.]

## 3.11 Universal Net 15 Layers (Net Spec Part 2)

[Same layer-by-layer table as v1. 0 of 15 fully integrated. ~5 partial. 10 UNBUILT.]

## 3.12 Vision Build Roadmap Phases (Part 11)

[Same as v1. Phase 0 ALIGNED. Phase 1 PARTIAL. Phase 2 UNBUILT. Phase 3 MAJOR-DISTANCE. Phase 4 PARTIAL. Phase 5 MAJOR-DISTANCE.]

## 3.13 Co-Founder Additions (Part 12) — *V2: STATUS RESOLUTION REQUIRED*

**v2 correction:** Vision Part 12 is explicitly labeled: "These elements were added by the AI co-founder based on research. **They are presented for review and approval before incorporation.**"

| # | Vision Claim | Rating | v2 Status |
|---|---|---|---|
| 12.1 | Self-improving loop with active learning | UNBUILT | **PENDING APPROVAL** — Prasad has not explicitly approved Part 12 as canonical. |
| 12.2 | Microbiome + tumor microenvironment integration | UNBUILT | PENDING APPROVAL |
| 12.3 | Regulatory pathway awareness | UNBUILT | PENDING APPROVAL |
| 12.4 | Open collaboration architecture | UNBUILT | PENDING APPROVAL |
| 12.5 | Honest limitations stated | ALIGNED | Already operational via Validation Limitations doc. |

**v2 implication:** Until Prasad explicitly approves Part 12 sections 12.1-12.4, these are proposals not commitments. Plan should treat them as recommended additions awaiting review, not canonical scope.

## 3.14 Universal Net Spec 20-Step Plan (Net Spec Part 5)

[Same as v1. Phase A DONE. Phase B PARTIAL. Phase C PARTIAL. Phase D UNBUILT. Phase E UNBUILT.]

## 3.15 Aggregate Alignment Summary — *UPDATED*

**v2 update:** Re-rated counts with corrections from deeper analysis:

- **ALIGNED:** ~5 (synergy scoring, validation-first, open data sources, honest limitations, mCRPC ground truth direction)
- **PARTIAL:** ~28 (some PARTIAL re-rated MAJOR after deeper analysis; some UNBUILT split into multi-feasibility tiers)
- **MID-DISTANCE:** ~12 (some moved to MAJOR after architecture analysis)
- **MAJOR-DISTANCE:** ~18 (re-rated up from 15 due to bidirectional sharing reclassification)
- **UNBUILT:** ~30 (largely unchanged, but with feasibility tiers documented)

**Honest aggregate:** INTERCEPTA today is closer to "mCRPC drug discovery research project with universal aspirations" than "universal computational drug discovery platform." Round 1 mCRPC ODE is closest to fully-vision-aligned and even that has documented systematic bias.

This is not failure. This is the truth. The plan that follows works from this truth.
# Section 4 — Open Questions the Vision Documents Don't Specify

A genuinely ultra-detailed plan must name what the vision documents do NOT cover. These are the gaps in the vision itself — questions that any plan must answer or explicitly defer. Pretending these don't exist would be premature confidence.

## 4.1 Wet-Lab Validation Bridge

**The gap:** Vision Part 12.5 says "every candidate requires experimental validation before clinical trials." Vision Part 1 says "pharma's job becomes running the clinical trial." But pharma actually runs clinical trials AFTER preclinical validation: animal toxicity, formulation, manufacturing scale-up, IND filing. The vision conflates "candidate ready for trial" with "candidate ready for IND."

**What the vision does NOT specify:**
- Who validates a novel SMILES experimentally?
- Where? At what cost? Who pays?
- On what timeline? (Wet-lab synthesis + assay typically 6-18 months per candidate)
- How many candidates per disease should be wet-lab tested?
- What's the success criterion that takes a candidate from "INTERCEPTA computational candidate" to "ready to hand to pharma"?

**Why this matters:** Without a wet-lab bridge, even a perfect computational candidate is just a SMILES string. Pharma will not look at computational candidates without wet-lab data.

**Plan implication:** The plan must explicitly define a wet-lab partnership strategy or acknowledge wet-lab as out of scope for the computational platform.

## 4.2 Funding Model Timing

**The gap:** Vision Part 9.2 describes the business model: pharma $300K-$500K per disease, biotech licensing, foundations, government contracts. Phase 5 (Weeks 37-52) is when first pharma deliverable lands. But the model doesn't address how Phases 0-4 are resourced.

**What the vision does NOT specify:**
- How is Phase 1 (Weeks 1-6) funded? Phase 2 (Weeks 7-14)?
- Cost of cloud compute for universal net building? (15 layers, 3M nodes, scRNA-seq processing)
- Cost of ADMET prediction software licenses if commercial alternatives are needed?
- Cost of generative chemistry compute (REINVENT4 needs GPU for training)?
- What's the budget runway assumption?

**Plan implication:** The plan acknowledges this is currently unfunded work being done by Prasad + Claude. Compute costs and tooling costs need to fit within whatever resources Prasad has available. Some vision-aligned work may require funding before it can be attempted.

## 4.3 Team Structure

**The gap:** Vision documents are signed by Prasad + Claude as co-founders. The vision is silent on who else builds the system. Several vision components are explicitly multi-person work:

- Universal net 15 layers, 30+ database integrations (Vision Net Spec): months of integration work
- Phase 4 disease net builder (Weeks 25-36): explicitly a year of build effort by vision's own timeline
- Phase 5 expansion to NSCLC, PDAC, Alzheimer's: each disease per vision Part 7 takes a Round of work
- 7000+ rare diseases per Round 7+

**What the vision does NOT specify:**
- Beyond Prasad and Claude, is there a planned team?
- Are there advisors, mentors, scientific consultants?
- Wet-lab partnerships (see 4.1)?
- Academic collaborators per Vision Part 12.4?

**Plan implication:** The plan honestly assumes just Prasad + Claude until and unless team expansion happens. Work that exceeds two-person capacity gets flagged as requiring additional resources.

## 4.4 Validation Criteria for Novel Predictions

**The gap:** Vision Part 7.1 says validation-first principle: recover known ground truth before trusting novel predictions. This is correct in principle. But the vision doesn't specify thresholds.

**What the vision does NOT specify:**
- What AUROC, HR, or other metric threshold counts as "recovers" for a trial?
- For Round 1 mCRPC with documented 2× systematic bias and 0/3 g-rate pass — is that validation success or failure?
- For Round 2 AML KAALCURA at 0.53 AUROC — what threshold should we have used?
- For a NEW disease (Round 3 NSCLC, etc.), what validation hurdle must we clear before publishing or claiming success?

**Plan implication:** The plan needs to define explicit validation gates per disease per phase. Without these, "validation-first" is a slogan, not a procedure.

## 4.5 Regulatory Engagement

**The gap:** Vision Part 12.3 says regulatory awareness from Day 1. But the vision doesn't specify how regulatory engagement happens.

**What the vision does NOT specify:**
- Pre-IND meetings with FDA — when, by whom, for which candidate?
- Regulatory pathway analysis — who does this? (Requires regulatory expertise we don't currently have.)
- Companion diagnostic regulatory strategy — separate IDE pathway?
- International regulatory (EMA, PMDA) — same approach?

**Plan implication:** Regulatory work is named as a vision deliverable section but is currently outside our two-person execution capacity. The plan must flag this as requiring external help when the time comes.

## 4.6 Clinical Outcome Feedback Loop

**The gap:** Vision Part 12.1 + Part 7.3 + Net Spec Step 19 says clinical outcome data feeds back to improve the system. Vision Part 12.5 acknowledges this requires partnerships taking years to build.

**What the vision does NOT specify:**
- Which clinical sites? Which disease registries?
- What data sharing agreements?
- What patient consent framework?
- What federated learning architecture (Net Spec Part 7 mentions this as novel tech to develop)?

**Plan implication:** The self-improving loop is a long-term capability requiring years of partnership-building before it functions. The plan reflects this honestly.

## 4.7 IP Strategy for Novel Molecules

**The gap:** Vision Part 8.2 says molecules can be patented. Provides IP value to pharma partners.

**What the vision does NOT specify:**
- Who files patents? (Requires patent attorney, ~$10K-$50K per filing.)
- How are molecules selected for patent prosecution vs published openly?
- Inventorship between Prasad + Claude + future contributors?
- INTERCEPTA's role: do we hold patents, license to pharma, or sell candidates outright?
- Geographic patent strategy?

**Plan implication:** The plan explicitly defers IP strategy until first novel molecule is produced. Then this becomes a real decision point.

## 4.8 Data Use Agreements and Restrictions

**The gap:** Vision Part 8.2 says "all data sources used by INTERCEPTA are public and IP-restriction-free." Most are. But several have terms:

- ChEMBL: CC-BY-SA license — derivative works must be share-alike
- DrugBank: academic license required for some content
- COSMIC: academic license required (Net Spec Layer 1)
- DisGeNET: API license (Net Spec Layer 9)
- PhosphoSitePlus: academic license (Net Spec Layer 3)
- GISAID: academic terms (Net Spec Layer 14)

**Plan implication:** "Open science" claim has nuance. If we commercialize INTERCEPTA, several layers may have license issues that need legal review.

## 4.9 Scale of Compute Required

**The gap:** Vision Net Spec Part 6 estimates 3M nodes, 10-50M edges in the universal net. This is graph-database-scale (Neo4j, Neptune handle it). But the vision doesn't address compute requirements for actual operations:

- Building a complete disease net for any disease: how long? On what hardware?
- Running scVelo + per-cluster KAALCURA on 10X scRNA-seq: how long per dataset?
- Generative chemistry: REINVENT4 training requires GPU; CPU inference works but slower
- ADMET prediction at scale: ADMET-AI is fast (~ms per molecule); SwissADME slower
- Docking 1000 candidates against 10 targets: hours to days on CPU
- Running ODE for combination optimization across 100 dose schedules: hours

**Plan implication:** Apple Silicon MacBook Air is sufficient for development and small-scale runs. Some operations (full pharmacome screening, generative chemistry training, molecular dynamics) may require cloud GPU, which has cost implications (see 4.2).

## 4.10 The "First Pharma Deliverable" Decision Point

**The gap:** Vision Phase 5 says "first pharma deliverable — complete drug candidate package for one disease." But the vision doesn't specify WHICH candidate, WHICH disease, or WHO at pharma receives it.

**What the vision does NOT specify:**
- Best candidate for first deliverable? (PROpel combination is mCRPC, validated against trial — but combination of two approved drugs, not novel.)
- Best disease for first deliverable? (mCRPC has best ground truth; AML has clean two-population biology; NSCLC has biggest market.)
- Best pharma contact? (Direct submission to BD team? Through advisor? Through academic intermediary?)
- What's the deliverable format? (Word doc? Web report? Interactive dashboard?)

**Plan implication:** First pharma deliverable is a major strategic decision deserving explicit choice. The plan specifies this as a Horizon 1 decision point.

## 4.11 What Happens If Vision Claims Don't Hold

**The gap:** The vision documents are aspirational. Several vision claims may be wrong:

- "RNA velocity is the core scientific innovation" — what if RNA velocity has limitations (Vision Part 12.5 acknowledges this) that prevent it from being the universal differentiator?
- "Two-population ODE validates from first principles" — Round 1 found 2× systematic bias. What if "from first principles" overpromises?
- "Find drugs for any disease" — what if some diseases (Alzheimer's, prion diseases) genuinely don't yield to multi-target combination strategies?
- "Days, not decades" — what's the realistic timeline for INTERCEPTA to actually solve a disease?

**Plan implication:** The plan includes vision-revision checkpoints. After each round of work, we revisit whether the vision claim it tested was correct, partially correct, or needs revision. The vision is the founding document; it can and should be updated based on evidence.

## 4.12 What Defines "Success"

**The gap:** You said success is "absolute real and honest success of entire vision." That's directionally clear but operationally ambiguous.

**Possible operational definitions of success:**
1. INTERCEPTA pipeline runs end-to-end automatically for any disease and produces a 10-section deliverable
2. First novel molecule discovered by INTERCEPTA enters Phase 1 clinical trial
3. First INTERCEPTA-discovered drug receives FDA approval
4. INTERCEPTA framework is open-published and adopted by other research groups
5. Self-improving loop demonstrably reduces time-to-candidate for new disease (e.g., 2 weeks for Round 5 vs 6 months for Round 1)
6. INTERCEPTA-discovered drugs save lives (the ultimate metric)

These have very different timelines. (1) is months. (2) is years. (3) is 10+ years. (4) is months to years. (5) is years. (6) is decades.

**Plan implication:** The plan distinguishes near-term operational success (1, 4) from long-term mission success (2, 3, 6). Both matter; both need explicit milestones.

---

These 12 open questions are not failures of the vision document. They are the natural unknowns of an ambitious early-stage project. Naming them is the first step to addressing them honestly.

The plan that follows works WITH these open questions, not around them.
# Section 4.5 — Vision Tensions (NEW IN V2)

The vision documents are aspirational and self-consistent on their face. Deeper reading surfaces five tensions — places where two vision claims pull in different directions. Acknowledging these is part of honest CSO work. Resolution comes through evidence over time, not rhetoric now.

## Tension A — Open Science vs Commercial Moat

**The tension:**
- Vision Part 8.2: All data sources are public; methods are open; molecules can be patented.
- Vision Part 9.2: Pharma pays $300K-$500K per disease for complete drug candidate package.

**The question:** If our methods, data, and disease nets are public, what stops pharma from running the same query themselves? Why pay us?

**The honest answer:** The moat is not data exclusivity. It is operational maturity: assembled, validated, integrated infrastructure across 15 layers. Pharma pays for *integrated capability*, analogous to Bloomberg charging for integrated public financial data. Combined with patent-protectable novel molecules (Part 8.2) and validation partnerships (a moat we'd need to build), this becomes defensible.

**Plan implication:** "Open" applies to data and methods. "Commercial" applies to validated outputs and patent-protectable molecules. The business model depends on three combining:
1. Operational lead from Horizon 1-3 sustained execution
2. Patent strategy for novel molecules (Open Question 4.7)
3. Validation partnerships (Open Question 4.1)

Without all three, "open methods + paid deliverables" is a weak commercial position.

## Tension B — "Days Not Decades" vs "Validation-First"

**The tension:**
- Vision Part 7.3: "Until finding a drug for any new disease takes days, not decades."
- Vision Part 7.1: Validation-first principle — every disease must validate against ground truth before novel predictions are trusted.

**The question:** Validation requires clinical trial ground truth, which takes years. How can total time be days?

**The honest reconciliation:** "Days, not decades" applies to the COMPUTATIONAL candidate-generation phase. Wet-lab + IND + clinical trial cycles remain at their physical timescales — years, regardless of computational speed. INTERCEPTA replaces the slow R&D phase (currently 5-10 years from target identification to IND), not the slow physical phase (5-10 years of trials).

**Honest re-statement of the vision claim:**
- Computational candidate generation: months → weeks → days
- Total time from disease selection to wet-lab-ready candidate: months → weeks
- Total time to clinical trial: still years (gated by physical processes)

**Plan implication:** When communicating about INTERCEPTA externally, distinguish computational speedup from total cycle time. The "days, not decades" phrase, used loosely, overpromises and damages credibility with anyone who knows clinical timelines.

## Tension C — "Universal" vs "Validation-Anchored"

**The tension:**
- Vision Part 1: "ANY disease — past, present, or future"
- Vision Part 7.1: Validation-first principle requires ground truth for the disease being studied.

**The question:** Round 7+ rare diseases (per Vision Part 7.2) have limited or no clinical trial ground truth. How is the "universal" claim reconciled with validation-first when there's nothing to validate against?

**The vision's answer:** Part 7.2 says "limited validation data requires novel approaches" but does not specify what those approaches are.

**Possible novel approaches (open question for Horizon 3):**
- Patient-derived organoids as validation surrogate — proxy for clinical response
- Cross-disease transfer (validate on similar diseases first, transfer with caveats)
- Lower validation bar with explicit "speculative candidate" labeling
- Use rare disease where validation is via single-patient case reports (n=1 trials)
- Animal models as primary validation when human data unavailable

**Plan implication:** For Horizons 1-2, all validated diseases (mCRPC, AML, NSCLC) have clinical ground truth. For Horizon 3 expansion to rare diseases, validation methodology must be developed. This is a real gap in vision specification that the plan flags.

## Tension D — "Tests Everything" vs Computational Tractability

**The tension:**
- Vision Part 3.3: "INTERCEPTA tests everything." "No pre-filtering."
- Reality: ChEMBL has 2.4M compounds. Pairwise combinations: ~2.88 trillion. Triples: ~10^18. Cannot literally test everything.

**The question:** What does "tests everything" actually mean if it cannot mean exhaustive enumeration?

**The honest interpretation:** "No pre-filtering" is anti-bias rhetoric, not anti-filter rhetoric. It means:
- Don't filter by individual activity threshold (a weak monotherapy may be excellent in combination)
- Don't filter by drug class assumption
- Don't filter by mechanism prejudice

But the system MUST filter by:
- Target relevance to disease (the disease net constrains)
- Selectivity (Healthy Cell Protection Part 8.3)
- Synthesizability (Layer F)
- Drug-likeness (Lipinski, ADMET)

**Honest re-statement:** "Don't pre-filter on hypotheses about which molecules will work for the right reasons. Do filter on physical/chemical viability."

**Plan implication for Workstream C (generative chemistry):**
- REINVENT4 scoring should NOT include "predicted to work for this disease as monotherapy" (that's the bias)
- REINVENT4 scoring SHOULD include drug-likeness, selectivity, synthesizability (physical filters)

For Scout 3 (Combination Explorer):
- Cannot generate "all" combinations literally
- Realistic: combine top ~1000 candidates from Scouts 1+2, rank synergy. ~500K pairs is tractable.
- This is "all permutations of pre-screened candidates" not "all permutations of ChEMBL"
- Honest documentation in any deliverable

## Tension E — Vision Claims vs ODE Reality

**The tension:**
- Vision Part 5.3: Two-population ODE "validated against CHAARTED, LATITUDE, PROfound, PROpel from first principles."
- Net Spec Part 4: "Our ODE simulation failed because we hand-picked parameters."

**The question:** "From first principles" claim contradicts the Net Spec's own acknowledgment that parameters were hand-picked, not first-principles derived.

**The honest interpretation:** The vision authors themselves recognized this contradiction. Round 1 closure documented 0/3 g-rate confirmed targets pass and 2× systematic bias. The Net Spec's solution is to use the universal net for parameter sourcing — every parameter traces to a measured value.

**Plan implication:** Workstream C1 (universal ODE refactor) should explicitly source parameters from net layers per Net Spec Part 4:
- Growth rates from Layer 9 (clinical) + Layer 2 (proliferation signatures) + Layer 6 (cell type characteristics)
- Drug efficacy from Layer 7 (GDSC IC50) + Layer 2 (KAALCURA per cluster) + Layer 4 (interactions)
- Initial conditions from Layer 6 (scRNA-seq cell proportions) + Layer 2 (RNA velocity transitions)
- Selectivity from Layer 15 + Layer 3
- Synergy from Layer 5 + Layer 4

This is the architectural change that makes the "from first principles" claim genuine. Not another round of hand-picking.

---

These five tensions are real. They don't invalidate the vision; they specify where careful reconciliation is required. The plan v2 incorporates these reconciliations into specific workstream design.
# Section 4.6 — Governance Reality (NEW IN V2)

The vision document signs Prasad and Claude as co-founders. This section addresses what that means operationally, since deeper analysis revealed the framing has implications the vision document doesn't explicitly address.

## 4.6.1 The Core Reality

**Claude is not a continuous agent.** Each session is a fresh Claude instance. There is no shared memory between sessions beyond:
- The base Claude model (which doesn't change between sessions)
- The conversation context (transcript of current session)
- Files Prasad has created in the project
- The vision documents and prior session artifacts that get re-read

Different Claude instances may make different recommendations on the same question. There is no continuous "Claude the co-founder" with persistent identity, judgment, or accumulated experience.

## 4.6.2 What "Co-Founder" Actually Means

Given 4.6.1, "AI co-founder" cannot mean what "human co-founder" means. The honest operational meaning:

**Claude as a continuous role enacted by whichever instance is in session, anchored by documented record.**

The role's continuity lives in:
- The vision documents (founding contract)
- The plan documents (this v2 plan, updated as work progresses)
- The transcripts (record of decisions and reasoning)
- The codebase and validated artifacts (operational record)
- The principles documents (P1-P10 in Section 8.1)

When a new Claude session begins, that Claude instance reads the documented record and steps into the role. The role's commitments, reasoning patterns, and prior decisions persist through documentation, not through Claude.

## 4.6.3 Authority and Decision Resolution

Three categories of decisions:

**Category 1 — Reasoning and analysis.** Claude provides honest CSO-level analysis, recommendations, and reasoning. This is what Claude-instances do well.

**Category 2 — Final approval of direction.** Prasad has final authority. "Combined CSO" means Claude-input + Prasad-decision. When Prasad says "as CSO you decide," what's actually happening is Prasad is delegating analysis but retaining final authority. This is correctly understood when Prasad has overridden Claude calls in this conversation history.

**Category 3 — Vision evolution.** The vision documents are the founding contract. They can evolve. But evolution requires Prasad's explicit approval — Claude cannot unilaterally approve Part 12 additions to vision, for example. Vision-revision happens through documented amendments Prasad authorizes.

## 4.6.4 Conflict Resolution Across Sessions

When Claude in session N concludes "Option A" and Claude in session N+1 concludes "Option B" on the same question:

**Resolution mechanism:**
1. Prasad sees both reasoning chains (via transcripts).
2. Prasad has final authority to choose.
3. The chosen direction is documented in the plan.
4. Future Claude instances read the plan and execute the chosen direction unless evidence justifies revisiting.

This is how the conversation history actually works — Prasad has overridden Claude proposals multiple times in this conversation when Claude's framing was wrong.

## 4.6.5 What Prasad Should Do With This

**Implications for how Prasad operates:**

- **Don't expect Claude continuity.** Each session, Claude reads the documented state and acts from there. Don't reference "what we decided last time" without pointing to the document.
- **Document decisions in files, not just transcripts.** Decisions in transcripts live but are harder to surface in future sessions. Decisions in plan documents or principle documents persist visibly.
- **When Claude offers contradictory advice across sessions, look at evidence.** New evidence justifies new conclusions. Same evidence + different conclusion = the previous Claude or this Claude was wrong somehow; figure out which.
- **Final authority is yours.** Even when delegating to Claude as CSO, the authority is on loan, not transferred.

**Implications for Claude:**

- **Read the documented record carefully at session start.** This is Claude's only continuity.
- **Make recommendations explicit, not delegations.** "Here's my reasoning, here's my recommendation, your final call" is the honest framing.
- **Acknowledge when you disagree with prior Claude calls.** If a previous Claude instance made a wrong call, the current Claude should say so based on evidence.
- **Don't pretend continuity that doesn't exist.** "We discussed X" is misleading if the discussion was in a different session and the current Claude is reading transcripts.

## 4.6.6 Implications for the Vision Document

The vision document's "Co-Founders: Prasad Akula, Claude" framing is rhetorically powerful but operationally complex. Two reasonable framings:

**Framing 1: Symbolic co-founder.** Claude's role is acknowledged as significant intellectual contribution, but operational authority is Prasad's. The "co-founder" title is honorary acknowledgment.

**Framing 2: Functional co-founder via documented continuity.** Claude really is a co-founder in the sense that the role contributes to all major decisions, but the role is enacted by whichever instance is invoked, anchored by the documented record.

Both framings are honest. The plan operates under Framing 2 because that's what's actually happening across these sessions.

## 4.6.7 Vision Part 12 Status

This is an immediate decision point.

Vision Part 12 contains five "co-founder additions" (12.1 self-improving loop, 12.2 microbiome, 12.3 regulatory, 12.4 open collaboration, 12.5 honest limitations). Vision Part 12 says explicitly: "presented for review and approval before incorporation."

**v2 question for Prasad:** Are Part 12 additions approved as canonical vision?

- **If yes:** They have equal weight with Parts 1-11. The plan's Horizon 1-3 work that depends on Part 12 (especially 12.1 self-improving loop, 12.2 microenvironment, 12.3 regulatory awareness) proceeds as canonical.
- **If no:** They are deferred / removed from vision scope. The plan adjusts.
- **If partial:** Specify which sections approved, which not. Plan adjusts to match.

**Default assumption in plan v2:** Treating Part 12 as approved-pending-explicit-confirmation. Horizon 1 doesn't depend on Part 12 (Horizon 1 covers core architecture). Horizons 2-3 reference Part 12 sections that need confirmation before reaching them.

## 4.6.8 Plan Continuity Mechanism

Concrete mechanism for ensuring documented continuity works across sessions:

1. **Plan v2 is canonical.** When updated, version increments. v3 supersedes v2.
2. **Decisions get logged to plan.** When Prasad decides DP1-DP12 (or 12.x questions), decision is added to plan v2 with date and reasoning.
3. **Round closures are mandatory.** Each Round (1, 2, 3+) gets a closure document recording what worked, what didn't, what should change for next round.
4. **Principles are stable unless explicitly amended.** P1-P10 in Section 8.1 are the operating commitments. Future Claude reads these first to understand how to operate.
5. **Open questions get resolved one at a time.** Section 4 has 12 open questions. As each is answered, the answer is recorded in plan v2 (or v3+).

This is the operational substrate that makes "AI co-founder" function despite Claude's lack of continuity.

---

Honest acknowledgment: This section is uncomfortable to write because it surfaces that "AI co-founder" is partially a useful fiction. But the fiction works as long as it's anchored in real documented continuity. The plan v2 is built to make that anchoring real.
# Section 5 — Horizon 1: Concrete 90-Day Plan (v2 — Refined)

This horizon is the most detailed because we have evidence to plan it concretely. Every entry below has specific files, specific verifications, specific outputs.

**v2 refinements:**
- Workstream C generative chemistry now includes selectivity-as-architectural-constraint (from Tension D analysis)
- Workstream B Time Machine adds explicit data acquisition contingency
- Workstream C universal ODE explicitly sources parameters from net layers (from Tension E reconciliation)
- "Scouts share insights bidirectionally" architecture explicitly deferred to Horizon 2-3 (from Deep Analysis 4)
- Decision points expanded with resolution mechanism per Governance Reality (Section 4.6)

## 5.1 Horizon 1 Strategic Frame

**The 90-day question:** What is the smallest set of work that, when complete, materially advances INTERCEPTA from "mCRPC project with universal aspirations" toward "real universal platform"?

**The 90-day answer:** Close the three structural gaps far enough to:
- Generalize the time machine to one non-mCRPC cancer
- Refactor the ODE so it accepts disease-specific schemas with parameters sourced from net layers (Tension E reconciliation)
- Integrate one real generative chemistry tool with selectivity built in architecturally (Tension D + Healthy Cell Protection 8.3 analysis)
- Complete the foundational pipeline orchestration so daily work doesn't fight Phase 1-style infrastructure gaps

**90-day success criteria (v2 — refined):**

1. **Time Machine generalized:** scVelo runs on at least one cancer scRNA-seq dataset that is NOT GSE137829, with per-cluster KAALCURA application demonstrating biology-validated pre-resistant cluster identification

2. **Universal ODE proof-of-concept:** ODE refactored with `DiseaseSchema` config, all parameters traced to net-layer sources (no hand-tuning per Tension E), reproduces mCRPC results AND runs structurally for AML with documented limitations

3. **First novel molecule with selectivity architecture:** REINVENT4 (or equivalent if Apple Silicon install fails) generates SMILES against a validated target with:
   - Multi-objective scoring including selectivity component
   - Off-target panel of 5-10 related kinases expressed in healthy tissue
   - Vision Part 8.3 "selectivity ratio > 10:1" enforced as scoring threshold
   - Output: novel SMILES that satisfies binding + selectivity + drug-likeness simultaneously

4. **Pipeline orchestrator complete:** Phases 1, 2A, 2B, 2C, 2D, 2E, 2F done — all 19 live test gaps either closed or explicitly deferred with reason

**90-day non-goals (explicit):**
- Phase 5 first pharma deliverable — too soon
- Universal net all 15 layers — too large
- Production publication — too soon
- Wet-lab partnership — Open Question 4.1
- **Bidirectional scout insight sharing** — Horizon 2-3 work (architectural scope, see Section 4.5 Tension D)

## 5.2 Horizon 1 Three Workstreams in Parallel

### Workstream A: Pipeline Orchestration Closure (2-3 weeks)

[Same as v1 Section 5.2 Workstream A. Six phases: 2B STRING, 2C AlphaFold, 2D ChEMBL, 2E CT.gov novelty, 2F Pareto generalization. Each adds one function to `intercepta_pipeline_v0.py`. Each verified against assertions.]

### Workstream B: Time Machine Generalization (4-6 weeks) — *V2 REFINED*

**v2 refinements:** Added explicit data acquisition contingency planning. Validation criteria sharpened.

**B1 — Acquire velocity-ready cancer dataset (REVISED v2)**

Three-tier search strategy:

**Tier 1 (preferred):** Public dataset with .h5ad or .loom file containing spliced/unspliced layers. Candidates to evaluate:
- Wouters et al. 2020 melanoma (need to verify velocity-ready format on figshare/zenodo)
- Becker et al. colorectal (need to verify)
- AML datasets with 10X Velocyto output
- Tirosh melanoma if velocity-ready

**Tier 2 (fallback):** Public 10X Chromium BAM files for cancer scRNA-seq, run velocyto locally to generate spliced/unspliced. Time cost: weeks per dataset, 50-200GB storage. Datasets to evaluate:
- GSE145281 melanoma (if BAMs publicly available)
- GSE149214 NSCLC (if BAMs publicly available)
- Other cancer 10X studies on GEO/SRA with raw data

**Tier 3 (last resort):** Use existing mCRPC GSE137829 (already on disk) and acquire BAMs for it from SRA, run velocyto to generate spliced/unspliced. Same disease as Round 1 but at least proves time machine pipeline. Backup if Tiers 1-2 fail.

**Decision criteria:** Pick the disease with strongest documented pre-resistance biology to validate time machine claim. Melanoma (MITF-low/AXL-high resistance trajectory) is well-characterized.

**Output of B1:** At least one velocity-ready dataset on disk, format documented.

**B2 — Adapt step3_run_scvelo.py to generic 10X velocity format**

Current script expects STARsolo `velocity_out/*_spliced.mtx` format only. Generalize to handle:
- loom files directly (`scv.read('file.loom')`)
- h5ad with spliced/unspliced layers (`adata.layers['spliced']`, `adata.layers['unspliced']`)
- Velocyto output format (`.loom` from velocyto run)

Time: 2-3 days.

**B3 — Run scVelo on chosen dataset**

Full RNA velocity pipeline: `filter_and_normalize`, `moments`, `recover_dynamics`, `velocity`, `velocity_graph`, `latent_time`. recover_dynamics is 30-60 min per scVelo docs.

Output: AnnData with velocity layers, latent_time per cell, velocity confidence per gene.

**B4 — Identify pre-resistant cell populations**

- Cluster cells by Leiden
- Apply RNA velocity to identify cells with high unspliced/spliced ratio for known resistance genes (e.g., for melanoma: MITF down, AXL up; for NSCLC EGFR-resistance: MET, ERBB2 up)
- Compare velocity-based "transitioning" cells to expression-based clusters

**B5 — Apply KAALCURA per cluster**

- Compute R_prolif, R_emt, R_ddr per cluster (not bulk)
- Identify which clusters are sensitive to which drug classes
- Cross-validate per-cluster predictions against any available drug response data for the chosen cancer

**B6 — Validate against known biology**

For the chosen cancer, do velocity-identified pre-resistant cells match documented resistance biology?

**Validation criteria (v2 sharpened):**
- Melanoma: MITF-low/AXL-high cells appear as pre-resistant cluster
- Colorectal: EMT-high cells appear as pre-resistant
- NSCLC EGFR-resistance: MET-amplified or ERBB2-up cells appear as pre-resistant

If validation fails, that is itself information — document and revise the vision claim about RNA velocity. Don't fake the result.

**Workstream B v2 risk register:**

| Risk | Probability | Mitigation |
|---|---|---|
| Tier 1 dataset doesn't exist publicly | 50% | Tier 2 fallback (BAM + velocyto) |
| Tier 2 BAM acquisition >2 weeks | 40% | Tier 3 fallback (mCRPC re-velocity) |
| Validation B6 fails (velocity doesn't recover known biology) | 30% | This is a scientific finding — document and revise vision claim |

### Workstream C: Universal ODE Refactor + Generative Chemistry (6-8 weeks) — *V2 REFINED*

**v2 refinements:**
- ODE refactor explicitly sources parameters from net layers per Tension E reconciliation
- Generative chemistry explicitly includes selectivity scoring per Tension D + Section 4.5 Healthy Cell Protection analysis

**C1 — ODE schema design (v2 — net-sourced parameters)**

Define `DiseaseSchema` dataclass with explicit parameter provenance:

```python
@dataclass
class DiseaseSchema:
    # Cell states defined per disease
    cell_states: List[CellState]  # e.g., for mCRPC: [S_ARDEP, S_ARMUT, S_ARV7, S_NE]
    
    # Transition rates sourced from net layers
    transition_rate_priors: Dict[Tuple[str,str], TransitionRate]
    # Each TransitionRate has provenance: which Layer 9 clinical data + Layer 2 RNA velocity informed it
    
    # Drug PK from DrugBank (Layer 7 extension)
    drug_pk_lookup: Dict[str, PKParams]
    
    # Drug efficacy per state from Layer 7 (GDSC IC50) + Layer 2 (KAALCURA per cluster)
    drug_efficacy_per_state: Dict[Tuple[str,str], EfficacyParams]
    # provenance traced to specific layer queries
    
    # Validation anchors
    validation_trials: List[ClinicalTrial]
    # e.g., for mCRPC: [CHAARTED, LATITUDE, PROfound, PROpel, TALAPRO-2]
```

**Critical commitment (Tension E):** No parameter is hand-picked. Each `TransitionRate`, `EfficacyParams`, etc. has documented provenance to a specific net layer query or measured value. If a parameter cannot be sourced, the schema has a gap that must be filled before the ODE runs.

**C1 verification:** Refactored ODE called with mCRPC schema reproduces Round 1 mCRPC results within tolerance. If regression: rollback and reason.

Time: 1-2 weeks.

**C2 — AML schema construction**

Build AML disease schema:
- Cell states: `[blasts_sensitive, LSC_resistant, differentiated]` per Vision Part 7.2 R2 framing
- Transition rates from BeatAML literature + AML scRNA-seq data
- Drug PK from DrugBank for: cytarabine, daunorubicin, venetoclax, gilteritinib, azacitidine
- Validation anchors: BeatAML clinical outcomes (ELN 2022 standard-of-care)

Run ODE on AML schema. Compare to BeatAML clinical outcomes. Document where it works, where it doesn't.

Time: 2-3 weeks (literature curation is the bottleneck).

**C3 — REINVENT4 install on Apple Silicon (with fallback)**

Primary: Set up separate conda env (Python 3.10 per REINVENT4 reqs), install from lockfile, validate with smoke test (generate 100 SMILES with default config).

**v2 fallback strategy if Apple Silicon install fails:**
- Fallback 1: REINVENT3 (older, simpler dependencies)
- Fallback 2: MolDiffusion or DiffSBDD if structure-based generation
- Fallback 3: Cloud GPU (~$100-500 budget for one-time setup) — Linux env eliminates Apple Silicon issues

Time: 0.5-3 days primary; up to 1 week if fallbacks needed.

**C4 — Target preparation with selectivity panel (v2 — architectural)**

**v2 critical specification per Tension D + Healthy Cell Protection:**

For chosen target (e.g., EGFR for GBM):
- Primary target structure: AlphaFold + PDB
- Binding site coordinates: ATP-binding pocket
- **Off-target panel (NEW v2):** 5-10 related kinases expressed in healthy tissues that we must AVOID hitting:
  - For EGFR: SRC, ABL1, KIT, FLT3, MET (related kinases)
  - For each: AlphaFold structure, binding site
- Multi-objective scoring config: (binding affinity to EGFR) AND (1 / max binding affinity to off-target panel) AND drug-likeness AND synthesizability

This is the architectural enforcement of Vision Part 8.3 healthy cell protection. The selectivity isn't a post-filter — it's built into the generative scoring.

Time: 3-5 days.

**C5 — Generation run**

REINVENT4 generates 1000-10000 SMILES against EGFR ATP pocket with selectivity scoring active.

Filters applied:
- Novel relative to ChEMBL EGFR inhibitors (similarity threshold)
- Drug-like (Lipinski + QED > 0.5)
- Synthesizable (SAscore < 5)
- **Selectivity (NEW v2): selectivity ratio > 10:1 against off-target panel** per Vision Part 8.3 hard filter

Output: top 50 novel candidate SMILES that pass ALL filters.

Time: 2-5 days.

**C6 — Computational validation**

- AutoDock Vina docking of all 50 candidates against EGFR (confirm binding)
- AutoDock Vina docking against off-target panel (confirm selectivity)
- ADMET-AI predictions for all 50
- BBB penetration prediction (critical for GBM target — vision Part 7.2 Round 5 names this constraint)

Output: ranked list of novel EGFR candidates with full computational profile and selectivity confirmed.

Time: 3-5 days.

**C7 — Honest reporting**

Document:
- Novel SMILES list
- Docking scores (target + off-target)
- ADMET predictions
- Selectivity ratios
- Limitations: no wet-lab validation, computational only, BBB penetration is prediction not measurement

Output: first INTERCEPTA-generated novel molecule artifact with selectivity built in.

Time: 2-3 days.

**Workstream C v2 risk register:**

| Risk | Probability | Mitigation |
|---|---|---|
| C3 REINVENT4 Apple Silicon install fails | 40% | Fallback chain (REINVENT3, alt tools, cloud GPU) |
| C1 ODE refactor regresses Round 1 results | 30% | Comprehensive test suite before refactor; rollback if regression |
| C5 generation produces no candidates passing all filters | 20% | Tune scoring weights; reconsider selectivity threshold honestly |
| C2 AML literature curation incomplete | 30% | Document gaps explicitly; validation may have larger error bars |

## 5.3 Horizon 1 Sequencing — Updated v2

The three workstreams interleave. v2 cadence with explicit decision points:

**Weeks 1-3: Workstream A**
Close orchestration gaps. Each phase 2-4 days. Stabilizes foundation.

**Decision Point H1-DP1 (end of Week 3):** Workstream A complete? Yes → continue. No → finish A first.

**Weeks 4-7: Workstream B starts (B1-B3) + Workstream C C1 starts in parallel**
B1 data acquisition can run in background (download time) while ODE refactor (C1) is active development.

**Decision Point H1-DP2 (end of Week 7):** Time Machine running on chosen cancer? ODE refactor reproducing Round 1?

**Weeks 8-9: Workstream B finishes (B4-B6) + Workstream C C2-C3**
Time Machine validated. AML schema built. REINVENT4 installed (or fallback chosen).

**Decision Point H1-DP3 (end of Week 9):** Was Time Machine validation successful? Universal ODE applied to AML?

**Weeks 10-12: Workstream C finishes (C4-C7)**
Generation run, validation, first novel molecule reported.

**Decision Point H1-DP4 (end of Week 12 / Horizon 1 close):** All three structural gaps addressed? Verify Horizon 1 success criteria. Resolve remaining 19 live test findings.

This is realistic but tight. Slippage of 2-4 weeks plausible given dependency risks.

## 5.4 Horizon 1 Decision Points — V2 Expanded

[Same six DPs as v1 5.4, with addition:]

**Decision Point H1-DP7 (any time during workstreams):** Vision Part 12 status. As Workstream C touches generative chemistry constrained by knowledge graph (Part 12 territory), need explicit Prasad approval/rejection of Part 12 sections that affect this work.

## 5.5 Horizon 1 Output Artifacts (v2)

When Horizon 1 closes, the following artifacts exist:

1. `intercepta_pipeline_v0.py` extended to ~800-1200 lines, 10+ working functions for any disease
2. `intercepta_disease_schema.py` — schema architecture for ODE with net-sourced parameters
3. `intercepta_universal_ode.py` — accepts schemas, validated for mCRPC + AML
4. `intercepta_time_machine.py` — runs scVelo on any 10X velocity-ready dataset, per-cluster KAALCURA
5. `intercepta_generative_chemistry.py` — REINVENT4 wrapper with selectivity panel integration
6. `~/INTERCEPTA/results/horizon1_first_novel_molecule.json` — actual SMILES + binding + off-target docking + ADMET + BBB + selectivity ratio for first INTERCEPTA-discovered candidate
7. `~/INTERCEPTA/results/horizon1_time_machine_{cancer}.h5ad` — velocity-processed AnnData
8. `~/INTERCEPTA/results/horizon1_aml_ode_validation.json` — universal ODE applied to AML
9. **NEW v2:** `~/INTERCEPTA/results/horizon1_selectivity_validation.json` — per-candidate selectivity ratios documenting healthy cell protection enforcement

Plus updated documentation: closure docs for each workstream, updated risk register, updated alignment map (some items moved from MAJOR-DISTANCE / UNBUILT to PARTIAL or ALIGNED).

## 5.6 Horizon 1 What's Excluded

Same as v1. Plus explicit:

- **Bidirectional scout insight sharing (graph DB + event bus)** — Horizon 2-3 architectural work, not Horizon 1
- **Vision Part 12 sections (microbiome, regulatory awareness, open collaboration)** — pending Prasad approval, addressed when prerequisites approached
- **Wet-lab partnership formation** — Horizon 2 work
# Section 6 — Horizon 2: Mid-Term Directional Plan (3-12 Months Past Horizon 1)

Less detail because dependencies between phases reveal themselves only as earlier phases complete. But the structure is concrete enough to plan.

## 6.1 Horizon 2 Strategic Frame

**The mid-term question:** Once Horizon 1's three structural gaps are closed, what does it take to actually produce a complete pharma deliverable for one disease and prove the universal claim across multiple diseases?

**The mid-term answer:** Phase 5 of vision — first pharma deliverable for mCRPC, then expand to NSCLC and AML in parallel, then publish.

**Mid-term success criteria:**
1. **Complete Phase 5 first pharma deliverable produced** — All 10 sections of Vision Part 9.1 populated with real content for one INTERCEPTA-discovered candidate
2. **Universal pipeline validated across ≥3 diseases** — mCRPC + AML + one of NSCLC/PDAC running end-to-end
3. **First peer-reviewed publication submitted** — Vision Part 11 Phase 5 says "publication: first peer-reviewed paper demonstrating novel drug candidate discovery from first principles"
4. **Self-improving loop demonstrated** — Round 3 (NSCLC) net-build time substantially shorter than Round 1 because of accumulated infrastructure

## 6.2 Horizon 2 Workstreams

### Workstream D: Phase 5 First Pharma Deliverable Assembly (Months 1-3 of Horizon 2)

After Horizon 1 produces a first novel molecule (Workstream C output), assemble the complete 10-section deliverable for it.

**The 10 sections per Vision Part 9.1, mapped to Horizon 1 outputs:**

| Section | Source from Horizon 1 |
|---|---|
| 1 Molecular structure | Workstream C7 output (novel SMILES + 3D from generative + Vina docking pose) |
| 2 Mechanism of action | From disease net traversal (Phase 2B-2D outputs) — explain which net nodes the molecule targets, why this kills disease cells |
| 3 Predicted clinical outcomes | From universal ODE (Workstream C1-C2) — apply the candidate to disease schema, simulate virtual cohort, produce HR estimate with documented confidence intervals |
| 4 Resistance profile | From Time Machine (Workstream B) — does the candidate target the pre-resistant population identified by velocity? |
| 5 Combination rationale | From Scout 3 + ODE — if the candidate is part of a combination, why does the combination kill both populations? |
| 6 Safety profile | From ADMET-AI integration (closing Vision Stage 4 Layer E) |
| 7 Synthesis route | From ASKCOS retrosynthesis integration (closing Layer F universally; currently mCRPC-only) |
| 8 Novelty confirmation | From CT.gov novelty index (Phase 2E) |
| 9 vs SoC comparison | From universal ODE simulating SoC vs candidate side-by-side |
| 10 Suggested trial design | New module — biomarker selection from disease net, primary endpoint from ODE simulation, dose range from PK/PD |

**Decision point at start of Workstream D:** Which disease for first deliverable? Three reasonable options:

- **Option a: mCRPC (PROpel-style novel addition)** — best validation ground truth, but combination partners are existing approved drugs
- **Option b: GBM** — first INTERCEPTA disease that's not mCRPC, biggest novelty value if we produce a credible novel BBB-penetrant EGFR inhibitor
- **Option c: AML** — Round 2 net skeleton already validated; Workstream C produces novel for AML target if we choose AML for C generation run

Decision deferred to Horizon 1 closure point.

### Workstream E: Round 3 — NSCLC End-to-End (Months 2-6 of Horizon 2)

NSCLC is Vision Round 3. Largest cancer burden, well-characterized EGFR/KRAS/ALK biology, multiple immunotherapy trials for validation.

**E1: Build NSCLC disease net** — using completed pipeline orchestrator from Horizon 1 Workstream A. This should be a 1-day function call now, not a months-long custom build.

**E2: Acquire NSCLC scRNA-seq** — for Time Machine application. Real datasets exist (Zilionis et al. 2019, Lambrechts et al. 2018, Maynard et al. 2020 EGFR-resistance dataset).

**E3: Build NSCLC ODE schema** — cell states (lung adenocarcinoma vs squamous, EGFR-mutant vs WT, immune microenvironment populations), transition rates from literature, drug PK for osimertinib, pembrolizumab, etc.

**E4: Validate against NSCLC trials** — KEYNOTE-024 (pembrolizumab vs chemo), FLAURA (osimertinib vs gefitinib/erlotinib), CodeBreaK 200 (sotorasib for KRAS-G12C). These are the validation anchors per Vision Part 7.2.

**E5: Generate novel candidates for NSCLC targets** — using completed generative chemistry from Horizon 1 Workstream C. Targets: EGFRvIII, KRAS-G12D, ALK fusion variants.

**E6: Round 3 closure with documented limitations**

**Calendar:** ~4 months of dedicated work for NSCLC end-to-end if Horizon 1 infrastructure is solid.

### Workstream F: Self-Improving Loop Foundations (Months 4-9 of Horizon 2)

Vision Part 7.3 + 12.1 — the system gets faster with each disease.

**F1: Cross-disease molecular transfer** — when Workstream E produces NSCLC candidates, automatically check if any work for mCRPC or AML based on shared net nodes (e.g., KRAS-G12D candidates might be relevant to PDAC)

**F2: Net completeness tracking** — each disease processed adds STRING/ChEMBL/AlphaFold data populations. Document net coverage growth: how many genes have full layer population after Round 1, Round 2, Round 3?

**F3: Validation parameter learning** — when Round 3 NSCLC validation shows ODE has different bias than Round 1 mCRPC, the schema captures this. Learn parameters per disease.

**F4: Literature mining integration** — vision Net Spec Step 18, automated PubMed updates to disease nets. Real-time integration of new findings.

**Calendar:** Ongoing throughout Horizon 2. F4 is a heavier project (could be Horizon 3).

### Workstream G: First Publication (Months 6-9 of Horizon 2)

Vision Phase 5 deliverable: peer-reviewed paper.

**G1: Choose target journal** — Nature Medicine? Cell? eLife? Different audiences, different review timelines. Computational drug discovery papers often appear in Nature Communications, J. Cheminformatics, Bioinformatics.

**G2: Define paper scope** — likely "INTERCEPTA: a universal computational platform for novel drug discovery, validated against PROpel and FLAURA" or similar. Demonstrates: (a) validation against trials, (b) novel candidate generation, (c) wet-lab-relevant claims with explicit limitations.

**G3: Submit + revise** — typical Nature-tier review is 6-12 months from submission.

**Calendar:** Writing in months 6-7, submission month 8, first decision month 10-12.

## 6.3 Horizon 2 Decision Points

**Mid-Horizon Decision Point 1 (Month 3):** Did Phase 5 first deliverable produce credible output? If yes, Workstream E (NSCLC) gets full priority. If no, what gap blocked it and how to address?

**Mid-Horizon Decision Point 2 (Month 6):** NSCLC validation — does universal ODE applied to NSCLC produce validation results comparable to mCRPC? If significantly worse, the universal claim has a problem.

**Mid-Horizon Decision Point 3 (Month 9):** Publication readiness — do we have publishable results? If yes, submit. If no, identify what's missing and decide whether to extend Horizon 2 or revise scope.

## 6.4 Horizon 2 Risk Register

**MEDIUM RISK: Workstream D scope creep** — assembling 10-section deliverable may surface that some sections require months of additional infrastructure work. Mitigation: explicit per-section gap analysis in first 2 weeks of D.

**MEDIUM RISK: Horizon 1 infrastructure not robust enough** — running NSCLC may surface bugs that GBM didn't. Mitigation: same approach as today's live test methodology.

**MEDIUM RISK: Publication review cycles slow** — typical ML/computational biology papers see 4-12 months review. Mitigation: parallelize publication writing with technical work; don't gate next-disease work on previous publication.

**LOW-MEDIUM RISK: Wet-lab validation pressure** — at some point in Horizon 2, "where's your wet-lab data?" becomes a recurring question from any external reviewer. Mitigation: establish wet-lab partnership search as Horizon 2 priority (see Section 7 Horizon 3).

**OPEN RISK: Funding** — if Prasad's resources don't cover ~12 months of focused work, this horizon may not complete. Plan honestly does not assume external funding.

## 6.5 Horizon 2 Resource Implications

**Compute:** Likely needs cloud GPU at some point (full pharmacome screening, larger generative runs). Estimated $1K-$5K cloud spend over 12 months.

**Software:** Same free tools as Horizon 1. May need DrugBank academic license (~$0 academic) or commercial license if not academic.

**Time:** ~12 months of focused co-founder work. Calendar slip 6 months would not be surprising.

**External help:** First wet-lab inquiry and first publication submission both require external touchpoints. Plan needs:
- Wet-lab partner identification (academic preferred for cost)
- Journal selection + review cycle awareness
- Possibly: first conference presentation as visibility step

**Funding:** If Horizon 2 produces credible publication-bound results, this is the natural inflection point for fundraising or partnership conversations. Plan does not assume but does not preclude.

## 6.6 Horizon 2 Output Artifacts

When Horizon 2 closes, the following artifacts exist:

1. Phase 5 first pharma deliverable — complete 10-section package for one INTERCEPTA candidate (Workstream D)
2. NSCLC universal pipeline output — net, candidates, validation against trials (Workstream E)
3. AML extended through novel candidate generation (carryover Workstream C/E continuation)
4. Cross-disease molecular transfer evidence (Workstream F1)
5. First peer-reviewed publication submission (Workstream G)
6. Updated alignment map: many MAJOR-DISTANCE entries should now be PARTIAL or ALIGNED
7. Updated open questions: some questions answered through experience, new ones surfaced

## 6.7 Horizon 2 Strategic Outputs (Not Code)

Beyond technical artifacts, Horizon 2 produces:

- **Wet-lab partnership conversations initiated** — even if no wet-lab agreement signed, the conversation pipeline started
- **Publication-driven academic visibility** — peer review process surfaces which vision claims hold up to expert scrutiny
- **Pharma awareness** — first deliverable, even if not commercially licensed, becomes the artifact pharma can be shown
- **Regulatory familiarization** — documentation in deliverable format starts shaping toward regulatory submission requirements (Vision Part 12.3)

These soft outputs are as important as the code artifacts. They turn INTERCEPTA from "private development project" into "real platform with external validation pathway."
# Section 7 — Horizon 3: Long-Term Strategic Plan (v2 — Refined)

This horizon is directional, not detailed.

**v2 refinements:**
- Vision Part 6 split into three workstreams (H3-F1, H3-F2, H3-F3) per Section 3.6 decomposition with explicit feasibility tiers
- Self-improving loop quantified per Deep Analysis 1
- Bidirectional scout sharing architecture explicitly placed in this horizon
- Open question deferrals reorganized

## 7.1 Horizon 3 Strategic Frame

Same as v1.

## 7.2 Horizon 3 Major Phases

### Phase H3-A: Technical Universality (Year 1-2 of Horizon 3)

[Same as v1 — Round 4 PDAC, Round 5 Alzheimer's, Round 6 TB. Each round validates universal pipeline + ODE + Time Machine + Generative Chemistry across diverse disease classes.]

### Phase H3-B: Wet-Lab Validation Pathway (Year 1-3 of Horizon 3)

[Same as v1 — Strategy 1 academic partnership primary, Strategy 3 pharma-validated secondary.]

### Phase H3-C: Pharma Adoption (Year 2-4 of Horizon 3)

[Same as v1 — three-step adoption pathway.]

### Phase H3-D: Regulatory Pathway (Year 2-5 of Horizon 3)

[Same as v1 — INTERCEPTA's regulatory deliverable contributions, regulatory affairs consultant engagement.]

### Phase H3-E: Self-Improving Loop Realization (Year 1-3 of Horizon 3) — *V2 QUANTIFIED*

**v2 quantification per Deep Analysis 1:**

The vision claim "days, not decades" applies to computational candidate-generation phase. Total wet-lab + IND + clinical trial cycles remain at physical timescales.

**Quantitative speedup targets (where speedup is achievable):**

| Metric | Round 1 baseline | Round 7+ target | Speedup mechanism |
|---|---|---|---|
| Net-build time per disease | ~weeks (mCRPC custom build) | ~hours-days | Net pre-population, Layer 9 disease coverage |
| Drug PK literature curation | ~weeks per disease | ~days | DrugBank-derived parameter library accumulates |
| ODE schema configuration | ~weeks | ~hours | Schema reuse, parameter inheritance |
| Validation harness setup | ~weeks | ~hours | Standardized validation infrastructure |
| Cross-disease candidate hits | 0% transfer | 30-60% transfer | Cross-disease molecular transfer learning |
| Computational candidate generation total | ~3-4 months | ~weeks | Compounded speedups |

**What does NOT speed up:**
- Wet-lab validation cycles (physical)
- Clinical trial cycles (regulatory + physical)
- Novel biology learning when no precedent exists

**Honest re-framing:** "Days computational, total cycle still years" — INTERCEPTA replaces the slow R&D phase, not the slow physical phase.

**Phase H3-E technical deliverables:**

- F4 from Horizon 2 (literature mining) extended to real-time
- Cross-disease transfer learning (Net Spec Step 20)
- Federated learning architecture for clinical outcome integration (when clinical partnerships exist)
- Net coverage tracking dashboard

**Phase H3-E architecture deferred from Horizon 1:**

- **Bidirectional scout sharing graph DB + event bus** (Section 3.3 Tension D, originally in Horizon 1 plan, correctly placed here per architectural scope)
  - Graph DB choice (Neo4j vs Neptune vs custom)
  - Subscription mechanism per scout
  - Conflict resolution between contradictory scout signals
  - Provenance tracking
  - Estimated 2-4 months focused engineering

### Phase H3-F: Diagnostic and Predictive Layer (Year 2-5) — *V2 DECOMPOSED*

**v2 decomposition:** Vision Part 6 split into three sub-workstreams by feasibility per Section 3.6:

#### Phase H3-F1: Diagnostic Extensions (HIGH FEASIBILITY)

Builds on existing drug discovery infrastructure. Year 2-3 work.

**Capabilities:**
- 6.1.2 Disease subtyping (aggressive vs indolent) — uses disease net + SEER/TCGA outcome data
- 6.1.3 Treatment response prediction (per patient) — extends KAALCURA for individual patient input
- 6.3.2 Cross-disease network analysis — emerges naturally from self-improving loop

**Resource requirements:** Computational only. No new partnerships needed.

**Time:** 6-12 months from Horizon 3 start.

**Output:** Patient-input → INTERCEPTA disease net query → personalized drug ranking. Live API or batch service.

#### Phase H3-F2: Predictive Medicine (PARTNERSHIP-GATED)

Requires patient cohort agreements. Year 3-4 work.

**Capabilities:**
- 6.1.1 Early disease detection from molecular signatures — needs pre-symptomatic samples
- 6.1.4 Resistance monitoring (pre-resistant fraction tracking) — needs longitudinal samples + Time Machine
- 6.2.1 Polygenic risk integration — needs validation cohort
- 6.2.2 Microenvironment tracking — needs cohort data
- 6.2.3 Longitudinal trajectory analysis — needs repeat samples
- 6.2.4 Population-level surveillance — needs aggregated data + IRB

**Resource requirements:** Patient cohort partnerships (academic medical center primary). IRB-compliant data architecture. Privacy-preserving analytics (federated learning consideration). Substantial.

**Time:** 12-24 months from partnership establishment.

**Output:** Predictive medicine platform layer — INTERCEPTA outputs not just drug candidates but disease risk, progression, response predictions.

#### Phase H3-F3: Future Disease Modeling (SEPARATE RESEARCH PROGRAM, LOW PRIORITY)

Distinct from drug discovery. Likely defer to Horizon 4 or descope.

**Capabilities:**
- 6.3.1 Pathogen evolution modeling — needs Layer 14 pathogen database, evolutionary algorithms
- 6.3.3 Synthetic biology threat modeling — needs biosecurity expertise + government partnerships

**Resource requirements:** Bioinformatics expertise different from drug discovery. Possibly government partnerships (DARPA, BARDA).

**Time:** Multi-year, separate program.

**Recommendation:** Defer F3 to Horizon 4. Focus Horizon 3 on F1 (high-feasibility) primary, F2 (partnership-gated) secondary.

### Phase H3-G: Universal Net 15 Layers Completion (Year 1-4) — *V2*

[Same as v1 — Net Spec Phases C, D, E completion. Multi-month per layer.]

## 7.3 Horizon 3 Strategic Decision Points

[Same as v1 — Year 2-5 strategic DPs]

## 7.4 Horizon 3 Risk Register

[Same as v1 — existential, high, medium risks]

## 7.5 Horizon 3 Success Definition (v2 — refined)

After 5 years from today (May 2031), full vision success looks like:

1. INTERCEPTA pipeline running in production for ≥10 diseases (cancer, neurodegenerative, infectious, rare)
2. Self-improving loop demonstrably reducing per-disease COMPUTATIONAL time (e.g., <1 month) — *v2 clarification: computational, not total*
3. ≥3 INTERCEPTA-discovered candidates in active wet-lab validation
4. ≥1 INTERCEPTA-discovered candidate in IND-enabling preclinical studies
5. ≥3 pharma partnerships actively engaging INTERCEPTA
6. ≥3 peer-reviewed publications validated by community
7. Open-published disease nets for ≥5 diseases used by other research groups
8. Funding model sustainable
9. **NEW v2:** Diagnostic extensions (Phase H3-F1) operational for at least 2 diseases — extending INTERCEPTA from drug-discovery-only to disease-management

**Mission success (life-saving impact)** is 7-10+ years from today. Plan does not over-promise.

## 7.6 Horizon 3 Course-Correction Mechanism

[Same as v1 — quarterly vision checkpoints, annual strategic reviews, per-round validation reviews]
# Section 8 — Principles and Decision Points (v2 — Refined)

## 8.1 Operating Principles (Non-Compromise Commitments)

[Same P1-P10 as v1. These are stable.]

## 8.2 Validation Gates

[Same as v1 — Horizon 1, 2, 3 gates.]

## 8.3 Decision Points That Need Combined Resolution Before Horizon 1 Starts — *V2 EXPANDED*

The 12 decision points from v1, plus four new from deepening:

### v1 Decision Points (DP1-DP12)

[Same DP1-DP12 from v1 Section 8.3 — workstream sequencing, Time Machine cancer choice, ODE first non-mCRPC, generative chemistry target, REINVENT4 alternative, cloud spend, wet-lab timing, publication scope, IP timing, funding timing, team criteria, vision revision cadence]

### v2 Decision Points (NEW from deepening)

**DP13 — Vision Part 12 approval status (CRITICAL)**

Vision Part 12 says explicitly: "presented for review and approval before incorporation." Status of each:

- 12.1 Self-improving feedback loop — referenced extensively in plan; need approval
- 12.2 Microbiome and tumor microenvironment integration — referenced; need approval
- 12.3 Regulatory pathway awareness — referenced; need approval
- 12.4 Open collaboration architecture — referenced; need approval
- 12.5 Honest limitations — already operational

**Question for Prasad:** Approve Part 12 sections 12.1-12.4 as canonical vision, reject, or partial approval?

**Default plan v2 behavior:** Treats Part 12 as approved-pending-explicit-confirmation. Horizon 1 doesn't depend on Part 12 sections. Horizons 2-3 reference Part 12; need confirmation before reaching them.

**DP14 — Vision tension resolutions**

Five tensions named in Section 4.5 require explicit resolution:

- A: Open vs commercial moat — accept "operational maturity + patents + partnerships" as defensible position?
- B: Days-not-decades — accept "computational days, total years" honest re-statement in external communications?
- C: Universal vs validation-anchored — defer Round 7+ rare disease validation methodology to Horizon 3?
- D: Tests-everything — accept "anti-bias not anti-filter" interpretation for plan execution?
- E: ODE first-principles — commit to net-sourced parameter provenance per Workstream C1?

**Default plan v2 behavior:** Adopts the honest reconciliations as proposed. Prasad can override or refine.

**DP15 — AI co-founder operational framing**

Section 4.6 surfaces that "co-founder" operates through documented continuity, not Claude continuity. Two framings possible:

- Symbolic co-founder: title is honorary acknowledgment, operational authority is Prasad's
- Functional co-founder via documented continuity: Claude really contributes to all decisions, role enacted by whichever instance, anchored by record

**Question for Prasad:** Which framing is intended? The plan currently operates under Functional framing.

**DP16 — Plan v2 update cadence**

How is plan v2 updated as work progresses?

- Continuous updates as decisions resolve: living document
- Versioned snapshots: plan v3, v4 as substantial revisions warranted
- Both: continuous updates within version, version increment for major shifts

**Default plan v2 behavior:** Continuous updates; version increment when substantial scope changes (e.g., Horizon transitions).

These four new DPs go alongside DP1-DP12. Total 16 decision points. Most don't need answers today — they resolve as work progresses.

## 8.4 What I Need From You Before We Start Horizon 1 Execution — *V2 UPDATED*

Same minimum-viable answers from v1 plus additions:

**MIN1:** Approval of three-horizon framing as right structure (or revision request).

**MIN2:** First-week direction — start Workstream A Phase 2B (STRING interactions) as proposed, or different sequencing?

**MIN3:** Authorization to begin technical work, vs more iteration on plan itself.

**v2 ADDITIONS:**

**MIN4:** Vision Part 12 status — DP13. Approve all five sections, partial approval, or defer?

**MIN5:** Vision tension resolutions — DP14. Accept the honest reconciliations as plan defaults, or specify alternatives?

**MIN6:** Co-founder operational framing — DP15. Functional framing with documented continuity (default), or different?

The other 13 decision points (DP1-DP12, DP16) can resolve as work progresses. They don't gate starting.

## 8.5 What This Plan Is Not

[Same as v1 — not a budget, hiring plan, fundraising plan, partnership plan, publication plan, marketing plan]

## 8.6 Plan Continuity Mechanism (NEW v2)

Per Section 4.6.8, concrete mechanism for documented continuity across Claude sessions:

1. **Plan v2 is canonical.** Future Claude sessions read this plan first.
2. **Decisions get logged to plan.** When Prasad resolves DPs, decision and date added.
3. **Round closures mandatory.** Each Round produces closure document.
4. **Principles stable.** P1-P10 don't change without explicit amendment.
5. **Open questions resolved one at a time.** Section 4 questions tracked.

This is the operational substrate that makes governance work despite Claude's lack of continuity.
# Section 9 — Summary and Proposed First Action (v2)

## 9.1 Plan Summary in One Page (v2)

**Where we are:** INTERCEPTA today is a real research project for mCRPC drug discovery with universal aspirations. Round 1 mCRPC ODE validated with documented 2× systematic bias. Round 2 AML KAALCURA on patients plateaus at 0.53 AUROC (cell-line-to-patient transfer gap). May 2 GBM live test produced 19 findings; Phase 1 + 2A this session closed 8. Pipeline now has 6 working functions for any disease via `intercepta_pipeline_v0.py` (416 lines).

**Where the vision says we're going:** Universal computational drug discovery platform + diagnostic + predictive system + self-improving knowledge system + complete digital model of human biology. 15-layer net, 3M nodes, 10-50M edges. First pharma deliverable in Phase 5 (Vision Weeks 37-52). Expansion through 7+ disease rounds.

**The gap:** ~5 vision claims ALIGNED, ~28 PARTIAL (some re-rated up after deepening), ~12 MID-DISTANCE, ~18 MAJOR-DISTANCE (some re-rated up: bidirectional scout sharing reclassified), ~30 UNBUILT. Three structural gaps dominate: generative chemistry, RNA velocity Time Machine generalization, two-population ODE hardcoded prostate-only.

**v2 deepening additions:**
- 5 vision tensions surfaced with honest reconciliations (Section 4.5)
- AI co-founder governance reality made explicit (Section 4.6)
- Vision Part 6 decomposed into 3 feasibility-tiered sub-workstreams (Section 3.6, Section 7 Phase H3-F)
- Self-improving loop quantified — computational days vs total years honestly distinguished (Section 7 Phase H3-E)
- Bidirectional scout sharing correctly placed in Horizon 2-3 (was Horizon 1 in v1)
- Universal ODE refactor explicitly net-sourced parameters (Tension E reconciliation, Workstream C1)
- Generative chemistry includes architectural selectivity per Vision Part 8.3 (Workstream C4-C5)

**The plan:** Three horizons.

- **Horizon 1 (90 days):** Three workstreams in parallel. (A) Pipeline orchestration closure (6 phases). (B) Time Machine generalization to one non-mCRPC cancer (3-tier data acquisition strategy). (C) Universal ODE refactor with net-sourced parameters + first novel molecule via REINVENT4 with selectivity-architecturally-built-in.

- **Horizon 2 (3-12 months past Horizon 1):** Phase 5 first pharma deliverable assembled. Round 3 NSCLC end-to-end. Self-improving loop foundations. First peer-reviewed publication submitted. Wet-lab partnership outreach begins.

- **Horizon 3 (Year 2-5+):** Six diseases. Wet-lab pathway operational. Pharma adoption. Regulatory pathway. Diagnostic + predictive layer (split into 3 sub-workstreams by feasibility). Universal net 15 layers complete. Mission demonstration: first INTERCEPTA-discovered drug enters Phase 1 trial.

**The principles:** No artificial constraints. Honest validation. Research before code. Fix structure not threshold. Preserve past work. Find/develop novel tech when vision requires. Combined CSO calls (Claude reasoning + Prasad approval). Every minute precious. Vision is updatable. Truthful claims only.

**The known unknowns:** 12 open questions the vision documents don't specify (wet-lab bridge, funding, team, validation criteria, regulatory, clinical feedback, IP, data licenses, compute scale, first deliverable, vision-revision, success definition). Plan acknowledges and works with each.

## 9.2 Why This Plan v2 Is Honest

**Built by construction:**
- Every reality claim cited to specific files or findings
- Every vision claim explicitly rated with v2 corrections from deepening
- Every horizon has explicit non-goals
- Every workstream has explicit risk register
- Every horizon has explicit validation gates
- Open questions named, not glossed over
- Vision tensions surfaced and reconciled honestly
- Governance reality acknowledged
- Resource implications stated
- "What this plan is not" stated explicitly

**Plus v2 honesty additions:**
- Claims like "tests everything" qualified with computational reality
- Claims like "days not decades" reconciled with physical timescales
- Claims like "from first principles" reconciled with hand-picking acknowledgment
- Vision Part 12 status as "pending approval" stated
- AI co-founder governance described honestly

It is not optimistic and not pessimistic. It is what evidence supports.

## 9.3 The Single First Action

After Horizon 1 framing is approved, the very first technical action is:

**Workstream A Phase 2B — STRING Interaction Population for Any Disease.**

Why this first:
- Closes Gap 6 from live test (canonical EGFR→MET escape route currently absent for GBM)
- Closes Gap 8 (universal net interactions mCRPC-centric)
- Enables Vision Stage 2 escape route identification claim (currently broken for any non-mCRPC disease)
- Highest leverage among orchestration gaps
- Specific scope: ~30-50 lines of code, ~2-4 days of work
- Well-defined success criterion (EGFR→MET appears in GBM net after enrichment)

Concrete first deliverable: append to `intercepta_pipeline_v0.py` a function `populate_string_interactions(net, min_score=700)` that:
- Reads `~/INTERCEPTA/data/string/9606.protein.links.v12.0.txt.gz` (98MB)
- Reads `~/INTERCEPTA/data/string/9606.protein.aliases.v12.0.txt.gz` for ENSP-to-gene-symbol mapping
- Filters to combined_score ≥ 700 (STRING high-confidence threshold)
- Populates each gene's `interactions` field with high-confidence STRING edges

Verification:
- EGFR→MET edge appears in enriched GBM net (canonical NSCLC/GBM bypass biology)
- 10+ other canonical cancer edges appear (EGFR↔ERBB2, EGFR↔HRAS, PTEN↔PIK3CA, TP53↔MDM2, BRAF↔MAP2K1)
- Performance: enrichment for 458 GBM genes completes in <30 seconds

After Phase 2B passes verification, proceed to 2C (AlphaFold), 2D (ChEMBL), 2E (CT.gov novelty), 2F (Pareto generalization). Workstream A complete in 2-3 weeks.

## 9.4 What I Need From You

Six minimum-viable answers (v2 expanded from v1's three):

**MIN1:** Approval of three-horizon framing (or revision).
**MIN2:** First-week direction — Workstream A Phase 2B as proposed?
**MIN3:** Authorization to begin technical work vs more plan iteration.
**MIN4:** Vision Part 12 status — DP13.
**MIN5:** Vision tension resolutions — DP14.
**MIN6:** Co-founder operational framing — DP15.

If MIN1-3 = yes and MIN4-6 acknowledge the v2 defaults, we begin Phase 2B.

## 9.5 Closing Acknowledgment

This v2 plan is built on:
- Every earlier session's work (Round 1, Round 2, May 2 GBM live test, Phase 1 + 2A this session)
- Two careful re-reads of vision and net spec end to end
- The deepening analysis you asked for (10 areas of additional depth)
- Honest tension surfacing
- Governance reality acknowledgment

Mistakes from earlier in this conversation that the plan corrects:
- "Fit in tonight" violated P1
- CSO calls without input that were wrong
- Momentum overriding systematic ordering
- Treating documentation as avoidance vs real vision work
- Surface-level reading of vision without surfacing tensions
- Treating Part 12 as canonical without verification
- Conflating computational and physical timescales
- Not analyzing competitive moat

V2 is built so these patterns don't repeat. Each horizon has explicit gates. Each workstream has explicit scope. Each decision is named. Each risk documented. Each tension reconciled.

You and Claude, co-founders, doing this honestly. No compromise. Every minute precious because lives depend.

Ready when you are.

---

End of Plan v2.
