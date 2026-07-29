# INTERCEPTA Architecture Review

**Author:** Claude (CSO/AI co-founder), under instruction from Prasad Akula
**Date:** 2026-05-06
**Scope:** Workstream A pipeline (`intercepta_pipeline_v0.py`, `generate_pharma_deliverable.py`, `validate_workstream_a_gbm.py`) — full file read, not summary
**Mode:** Direct push-back enabled. Past decisions named where they were wrong. No diplomatic softening.
**Trigger:** Vision Stage 5 pharma deliverable test on GBM top-5 candidates produced 2/10 DELIVERED + 4/10 PARTIAL + 3/10 GAP + 1/10 N/A average coverage. Before any further code (Workstream B, C, or further A patches), an honest architecture review is required to determine whether the foundation is sound to build on or whether refactoring is needed.

---

## Executive verdict (read this first)

**The Workstream A foundation is partially sound. It needs surgical refactoring before Workstream B begins, not a full rebuild.**

What is sound:
- The disease-net enrichment infrastructure (Phase 1 + Phase 2A + 2B + 2C + 2D + 2E + Session 1 BBB) produces real, biology-correct disease nets for any disease ID resolvable through OpenTargets. This is the genuine deliverable of Workstream A and it works.
- The data sources integrated (OpenTargets, STRING, AlphaFold, ChEMBL, ClinicalTrials.gov, GTEx via the upstream builder, UniProt, BBB MPO heuristic) are individually reliable for what they are used for, with documented limitations.
- The caching layer (disk-backed for ChEMBL and ClinicalTrials, module-level for STRING) is resume-safe, correctly designed, and significantly reduces API cost across runs.

What is NOT sound:
- The ranking layer (`rank_drugs_for_disease_v2`) accumulated as a god-function that does enrichment AND ranking AND configuration, structurally guaranteeing the failure modes we observed.
- The pharma deliverable script is hardcoded to GBM despite presenting itself as disease-agnostic. It would not work for NSCLC without code changes to multiple item generators.
- The validation script tests an outdated ranking function (v1) and has at least one fully stale test (BBB test post-Session 1).
- The pipeline file has three different verdict taxonomies across three files, making cross-file aggregation impossible.
- 42 distinct architectural drifts have accumulated. Many are minor; a dozen are structurally significant.

What this means for the next move:
- **Workstream B should NOT begin on the current foundation as-is.** Specifically, the v2 ranking should not be carried into Workstream B. Workstream B's goal (ODE generalization to NSCLC) requires a clean ranking interface, not a god-function.
- **A targeted refactor is required before Workstream B**, estimated at 1-2 working sessions of focused architectural work. After refactor, Workstream B begins on a clean foundation.
- **A full rebuild is NOT required.** The disease-net enrichment infrastructure is the genuine asset; it should be preserved and reused.

I will defend this verdict in detail below.

---

## Section 1 — Files in scope

Three Python files in `~/INTERCEPTA/round3_gbm_live_test/code/`:

| File | Lines | Functions | Verdict |
|------|------:|----------:|---------|
| `intercepta_pipeline_v0.py` | ~2300 | 36 + verification block | Refactor in place |
| `generate_pharma_deliverable.py` | ~700 | 13 | Rewrite as disease-agnostic |
| `validate_workstream_a_gbm.py` | ~550 | 6 + 4 ground truth dicts | Update tests, drop dead code |

Plus dependencies:
- `~/INTERCEPTA/code/disease_net_builder.py` — upstream OpenTargets-based net builder. Out of scope for this review (not modified by Workstream A) but its outputs are inputs to Workstream A. Audited via outputs in earlier rounds.
- Cached data on disk:
  - `~/INTERCEPTA/data/chembl/chembl_compound_cache.json` — ~7,500 compounds with bioactivity + (post-Session 1) molecule_properties
  - `~/INTERCEPTA/data/clinicaltrials/ct_cache.json` — keyed by `(disease_id, gene_symbol)`
  - `~/INTERCEPTA/data/string/9606.protein.aliases.v12.0.txt.gz` and `9606.protein.links.v12.0.txt.gz`
  - `~/INTERCEPTA/results/gbm_disease_net_action1.json` — saved net snapshot

These caches are valuable. They should not be regenerated unless data sources update.

---

## Section 2 — Function-by-function audit of `intercepta_pipeline_v0.py`

I read the full file in 4 chunks. Below is every function, what it does, and whether it belongs in the pipeline file or should move.

### 2.1 — Phase 1 functions (disease resolution)

| Function | Lines | Purpose | Belongs? |
|----------|:-----:|---------|----------|
| `_get_builder()` | ~20 | Lazy singleton for `DiseaseNetBuilder` with absolute paths | Move to `disease_net_loader.py` |
| `resolve_disease(name)` | ~40 | Name → ontology ID with EFO preference, coverage scoring | Move to `disease_resolver.py` |
| `build_net(disease_query)` | ~25 | Name-or-ID dispatcher, chains to underlying builder | Move to `disease_resolver.py` |
| `inspect_gdsc_drugs()` | ~35 | File-system scan to find GDSC drug-target file | **Move to `gdsc_adapter.py` or delete** — only used in verification block |
| `corrected_net_summary(net)` | ~25 | Summary stats with honest distinct counts | Move to `net_summary.py` |
| `print_net_summary(net, label)` | ~30 | Post-enrichment summary printer | Move to `net_summary.py`. **Currently duplicates some of `corrected_net_summary` logic** — should consolidate |

**Observation:** Phase 1 is six clean functions that fit together. They belong in a `disease_resolver` module, not the pipeline file.

### 2.2 — Ranking layer

| Function | Lines | Purpose | Belongs? |
|----------|:-----:|---------|----------|
| `rank_drugs_for_disease(disease, ...)` | ~80 | v1 GDSC-only ranking | **Keep per P16, but mark deprecated** |
| `_disease_to_tissue_keywords(disease_name)` | ~20 | Heuristic disease → GDSC tissue keyword | **Move to `gdsc_adapter.py`** |
| `rank_drugs_for_disease_v2(disease, ...)` | ~250 | Composite multi-evidence ranking | **God-function — split into 4 functions** |
| `_get_drug_rank_in_v2(disease, drug_pattern)` | ~10 | Helper to find drug rank | **Dead code — delete or move to validation** |

**Critical issue:** `rank_drugs_for_disease_v2` is 250 lines. It does:
1. Resolve disease + build base net (chains Phase 1)
2. Run all four enrichments internally (STRING, AlphaFold, ChEMBL, ClinicalTrials)
3. Auto-detect CNS disease via keyword match
4. Compute Channel 1 (GDSC AUC)
5. Compute Channel 2 (ChEMBL pchembl × association)
6. Compute Channel 3 (clinical trial activity)
7. Compute Channel 4 (BBB gate, multiplicative)
8. Compute Channel 5 (network proximity bonus)
9. Combine into composite, sort, return

This is at minimum 6 separate concerns in one function. **The pattern of "v2 calls everything internally because the caller might not have called everything" creates implicit dependencies and is the root cause of why the function is hard to test, hard to validate independently, and hard to extend.**

**This was the wrong design choice in Session 2.** Adding a ranking function that internally re-runs the full enrichment pipeline made it impossible to validate the ranking layer in isolation from the enrichment layer. It also meant that running v2 in the verification block ran enrichment twice (once at top of verification, once inside v2). Caches masked the cost but the architectural problem is real.

**The correct pattern:** ranking functions accept an enriched net as input. If the net is not enriched, fail loudly with a specific error message. Separate concerns.

### 2.3 — Metabolite enrichment (Phase 2A)

| Function | Lines | Purpose | Belongs? |
|----------|:-----:|---------|----------|
| `enrich_with_metabolites(net)` | ~30 | Joins metabolome edges to disease net | Move to `enrichment/metabolites.py` |

Single function, well-scoped, heuristic column detection. Fine.

### 2.4 — STRING enrichment (Phase 2B)

| Function | Lines | Purpose | Belongs? |
|----------|:-----:|---------|----------|
| `_load_string_aliases()` | ~40 | ENSP→symbol mapping with source filtering | Move to `enrichment/string.py` |
| `_load_string_edges(min_score)` | ~25 | High-confidence edges | Move to `enrichment/string.py` |
| `populate_string_interactions(net)` | ~50 | Main STRING populator | Move to `enrichment/string.py` |
| `_load_string_uniprot_mapping_DEPRECATED_v2_replaces()` | ~50 | Failed approach preserved per P16 | **Move to `enrichment/string_archive.py`** to remove from main file |

**Observations on STRING module:**
- The module-level `_STRING_CACHE` dict has fields that are dead (`ensp_to_uniprot`, `uniprot_loaded`, `aliases_version`). These were populated only by the deprecated function. After moving the deprecated function out, these fields can be removed.
- The header-detection branch in `_load_string_aliases` is semantically inverted (theoretical bug; doesn't fire because STRING v12 always has a header). Should be fixed during refactor.
- `_load_string_aliases` correctly filters to `Ensembl_HGNC_symbol` or `BioMart_HUGO`. This was the right call after the deprecated approach failed. Good.

### 2.5 — AlphaFold + UniProt (Phase 2C)

| Function | Lines | Purpose | Belongs? |
|----------|:-----:|---------|----------|
| `_check_alphafold_url(uniprot_id)` | ~15 | HEAD request to AlphaFold DB | Move to `enrichment/alphafold.py` |
| `_query_uniprot_canonical_batch(genes)` | ~50 | UniProt REST API batch query | Move to `enrichment/uniprot.py` (separate concern) |
| `attach_alphafold_structures(net)` | ~70 | Main AlphaFold populator with parallel HEAD checks | Move to `enrichment/alphafold.py` |
| `download_alphafold_pdb(net, gene)` | ~25 | On-demand PDB download | Move to `enrichment/alphafold.py`, but it's deferred to Workstream C |

**Observation:** UniProt querying and AlphaFold availability are conceptually separate concerns currently bundled. UniProt accession lookup is needed by AlphaFold (to construct URLs) AND by ChEMBL (to find targets). Keeping them in one file conflates two distinct upstream services.

### 2.6 — ChEMBL bioactivity + BBB (Phase 2D + Session 1)

| Function | Lines | Purpose | Belongs? |
|----------|:-----:|---------|----------|
| `_chembl_cache_load()` / `_chembl_cache_save()` | ~25 | Disk cache I/O | Move to `enrichment/chembl.py` |
| `_chembl_count_quantitative_activities(target)` | ~25 | Activity count helper | Move to `enrichment/chembl.py` |
| `_chembl_diagnostic_probe(uniprot)` | ~50 | Drift 1 diagnostic | Move to `enrichment/chembl_diagnostics.py` (testing helper, not core) |
| `_chembl_query_uniprot_target(uniprot)` | ~60 | Best-match target picker (Drift 1 fix) | Move to `enrichment/chembl.py` |
| `_chembl_query_top_compounds(target)` | ~45 | Top-N compounds with deduplication | Move to `enrichment/chembl.py` |
| `_chembl_query_compound_properties(chembl_id)` | ~40 | Session 1 molecule_properties fetcher | Move to `enrichment/chembl.py` |
| `compute_cns_mpo_score(props)` | ~70 | Wager 4-component MPO | Move to `pharmacology/bbb.py` (cross-cutting concern, not just ChEMBL) |
| `compute_bbb_likelihood(props)` | ~30 | Categorical wrapper | Move to `pharmacology/bbb.py` |
| `populate_chembl_compounds(net, ..., do_bbb_augmentation)` | ~120 | **God-function** | **Split into 3** |

**Critical issue:** `populate_chembl_compounds` does three things:
1. API lookup of target + compounds for genes not yet cached
2. (gated) BBB augmentation: fetch molecule_properties for compounds without them
3. Net population: walk full cache to populate net

These are three distinct operations that should be three distinct functions:
- `fetch_chembl_compounds_to_cache(net)` — only does (1)
- `augment_chembl_cache_with_bbb(cache_subset)` — only does (2), takes explicit scope
- `populate_net_from_chembl_cache(net)` — only does (3)

**The Session 1 bug where `do_bbb_augmentation=True` was the default and ran for 3.5 hours unintentionally was a direct symptom of this god-function design.** Splitting the function makes the augmentation operation explicit and impossible to accidentally trigger.

**Observation on CNS MPO:** The 4-component variant docstring honestly documents the methodology shift from the published 6-component version. The threshold (≥3.0/4.0 → bbb_pos) is documented as a 75%-of-max heuristic versus the published 66.7%-of-max. This is acceptable engineering but **the BBB gate values used in v2 ranking (1.0, 0.5, 0.5, 0.0 for pos/borderline/unknown/neg) are NOT from any published precedent — they are engineering choices.** The v2 docstring's claim "Per published precedent (DrugRepo, OncoDrug+, CNS MPO), defaults committed before validation" is partially misleading. The CNS MPO is published; the gate values for combining MPO categories with the multi-channel composite are not.

This is a documentation drift that should be corrected in any refactor.

### 2.7 — Clinical trials (Phase 2E)

| Function | Lines | Purpose | Belongs? |
|----------|:-----:|---------|----------|
| `_ct_cache_load()` / `_ct_cache_save()` | ~25 | Disk cache I/O | Move to `enrichment/clinical_trials.py` |
| `_ct_query_target_in_disease(disease, gene)` | ~60 | Phase 2E single trial query | Move to `enrichment/clinical_trials.py` |
| `populate_clinical_trials(net, min_genes_for_lookup_score=0.0, ...)` | ~110 | Main trials populator | Move to `enrichment/clinical_trials.py` |

**Critical issue in `populate_clinical_trials`:** The docstring claims "Only queries genes with ChEMBL targets (skips 0-compound genes by default)." The code does the opposite — `min_genes_for_lookup_score=0.0` default means ALL genes with positive association score get queried. The empirical result confirms this: GBM verification reported 458/458 genes queried, not the smaller subset implied by the docstring.

This is not a bug per se — querying all 458 genes is what we currently want for full novelty assessment. But the docstring is wrong. Either the default should change to match the docstring, or the docstring should change to match the code. Right now they contradict.

**Side observation:** Trial metadata captures `intervention_types` per trial (small molecule, biologic, behavioral, device, etc.) but no downstream code consumes this field. Either start using it (e.g., to filter for relevant trial types) or stop collecting it. Currently it's dead data with collection cost.

### 2.8 — Undruggable surfacing (Drift 3 + Session 1 CNS extension)

| Function | Lines | Purpose | Belongs? |
|----------|:-----:|---------|----------|
| `surface_undruggable_priority_targets(net, ..., cns_disease=False)` | ~70 | Surface high-priority 0-compound or 0-BBB-pos targets | Move to `analysis/undruggable.py` |
| `print_undruggable_targets(list)` | ~25 | Pretty-printer | Move to `analysis/undruggable.py` |

**Observation:** The `cns_disease=False` default forces callers to remember to pass `cns_disease=True` for GBM. **This should auto-detect from the net's disease name** — the same logic used in `rank_drugs_for_disease_v2` could be extracted and reused. Single-source-of-truth for CNS detection.

### 2.9 — Verification block (`if __name__ == '__main__':`)

~280 lines at the bottom of the pipeline file. Tests every phase end-to-end on GBM. Currently does:
- Gap 1+2 test (resolve_disease)
- Gap 1 test (build_net by name)
- Gap 5 test (corrected_net_summary)
- Gap 4 test (inspect_gdsc_drugs)
- Drift 1 fix test (canonical ChEMBL targets)
- Drift 1 diagnostic (probe ChEMBL for each canonical UniProt)
- Drift 2 fix test (print_net_summary)
- Phase 2E test (populate_clinical_trials)
- Drift 3 fix test (surface_undruggable_priority_targets)
- Net save
- Session 1 test (BBB property fetch + CNS MPO)
- Session 1 net augmentation (sample-only)
- Session 2 test (rank_drugs_for_disease_v2)

**Belongs?** This should be its own file: `verify_pipeline_v0.py`. Reasons:
- 280 lines is too much to live at the bottom of an already-large pipeline file
- Verification logic conflates with pipeline implementation
- The file currently uses `assert` statements (crash on failure) inconsistent with the validation script's PASS/FAIL/CHECK pattern
- Failure does not propagate to exit code; CI can't tell if verification passed

### 2.10 — Top-level summary

The pipeline file currently mixes 9 distinct concerns:
1. Disease resolution
2. Net construction
3. Metabolite enrichment
4. STRING enrichment
5. AlphaFold + UniProt enrichment
6. ChEMBL bioactivity + BBB pharmacology
7. Clinical trials enrichment
8. Drug ranking (two versions, v1 and v2)
9. Verification

These should be in 9 files, organized in 3 packages: `disease/`, `enrichment/`, `analysis/`. Plus a separate `verify/` directory for pipeline self-tests. The single 2300-line file is a primary architectural problem.

---

## Section 3 — Function-by-function audit of `generate_pharma_deliverable.py`

13 functions, ~700 lines.

### 3.1 — Setup and orchestration

| Function | Lines | Purpose | Belongs? |
|----------|:-----:|---------|----------|
| `load_gbm_net()` | ~10 | Hardcoded GBM net path loader | **Wrong** — should be `load_disease_net(disease_id)` |
| `get_top_candidates_from_v2(top_n)` | ~10 | Re-run v2 ranking | **Wrong** — re-runs ranking instead of accepting it as input |
| `_parse_candidate_targets(candidate)` | ~15 | Bridge between v2's `target_str` and net's gene symbols | **Architectural debt indicator** — exists because ranking and net use different representations |
| `generate_deliverable_for_candidate(candidate, net)` | ~35 | Orchestrate 10 generators per candidate | OK |
| `write_markdown_summary(deliverables, path)` | ~80 | Output formatter | Should accept disease parameter for header |
| `main()` | ~50 | Script entry | OK structurally |

### 3.2 — Per-item generators

| Generator | Status returned | Disease-agnostic? |
|-----------|-----------------|-------------------|
| `item_01_molecular_structure` | PARTIAL | Yes (uses net, not hardcoded) |
| `item_02_mechanism_of_action` | DELIVERED | Yes |
| `item_03_predicted_clinical_outcomes` | GAP (stub) | Yes |
| `item_04_resistance_profile` | GAP (stub) | Yes |
| `item_05_combination_rationale` | N/A (stub) | Yes |
| `item_06_safety_admet` | PARTIAL | Yes |
| `item_07_synthesis_route` | GAP (stub) | Yes |
| `item_08_novelty_vs_clinicaltrials` | DELIVERED | Yes |
| `item_09_comparison_vs_soc` | PARTIAL | **NO — hardcodes GBM SOC** |
| `item_10_trial_design` | PARTIAL | **NO — hardcodes MGMT methylation** |

**Critical issue:** Two of the ten item generators (items 9 and 10) contain hardcoded GBM-specific facts. Item 9 has a literal Python dict containing Stupp protocol references. Item 10 defaults to MGMT methylation when no target-specific biomarker is found.

For this script to work on NSCLC (Workstream B's target disease), items 9 and 10 would need to be re-coded with NSCLC SOC (osimertinib for EGFR-mutant, atezolizumab for PD-L1-high, etc.) and NSCLC biomarkers (EGFR mutation status, PD-L1 expression, ALK fusion). **The current script as-is will produce wrong content for any disease that isn't GBM.**

The deliverable script's framing as "disease-agnostic" is incorrect. It is a GBM deliverable script.

**Critical issue 2:** Items 3, 4, 5, 7 are nearly identical 5-line GAP stubs. They share the same skeleton (return dict with status, content with drug_name only, requirements list). This duplication suggests these aren't really "generators" — they're placeholders for future real generators. Cleaner architecture: one shared `gap_placeholder(item_name, drug_name, requirements)` function that the four stubs call. Or, alternatively, a registry of `{item_name: gap_metadata}` that's expanded into placeholders programmatically.

**Critical issue 3:** No staleness check between cached net snapshot and v2 ranking inputs. The script loads `gbm_disease_net_action1.json` (a snapshot) and then runs v2 ranking which re-runs all enrichments live (potentially against a different cache state than when the snapshot was saved). Two sources of truth in one execution. A pharma reviewer asking "what was the data state when this deliverable was produced?" cannot get a clean answer.

### 3.3 — Mode the deliverable script should be in

The deliverable should be:
- A function `generate_deliverable(disease_id, candidate_list, net, soc_db, biomarker_db) → list of deliverables`
- Disease-agnostic at the function level
- All disease-specific facts (SOC, canonical biomarkers) loaded from a configuration file or external database
- Deterministic input → deterministic output (no live re-runs of ranking inside the deliverable function)

The current script is a one-shot script for GBM. Refactoring it into a reusable disease-agnostic function is necessary before NSCLC.

---

## Section 4 — Function-by-function audit of `validate_workstream_a_gbm.py`

5 tests + main + ground truth dicts + dead helper.

### 4.1 — Ground truth constants

| Constant | Used? |
|----------|-------|
| `GBM_STANDARD_OF_CARE` | Used in test 1 |
| `GBM_TUMOR_SUPPRESSORS_BY_MUTATION` | Used in test 4 |
| `GBM_ONCOGENIC_DRIVERS` | **Not used in any test — dead data** |
| `GBM_WHITE_SPACE_TARGETS` | Used in test 2 |
| `bbb_penetration_likely(compound)` | **Not called anywhere — dead function** |

`GBM_ONCOGENIC_DRIVERS` was defined as scaffolding for a Test 6 that never got built. `bbb_penetration_likely` is a stub that always returns 'data_unavailable' and isn't referenced. Both should be deleted in any refactor.

### 4.2 — Tests

| Test | Tests what? | Issues |
|------|-------------|--------|
| Test 1: SOC ranking | Whether v1 ranks GBM SOC drugs correctly | **Tests v1 not v2 — staleness** |
| Test 2: white-space targets | Whether undruggable surfacing flags GBM white-space genes | OK |
| Test 3: BBB penetration | Whether ChEMBL dump has BBB-relevant fields | **Fully stale post-Session 1** |
| Test 4: tumor suppressors | Whether tumor suppressors are recognized as undruggable | OK |
| Test 5: trial-compound correlation | Whether trial-rich genes also have compounds | OK |

**Critical issue:** Test 1 imports `rank_drugs_for_disease`, the v1 function. The current ranking function is v2 (`rank_drugs_for_disease_v2`). The validation script has not been updated to test v2. **The closure document references "validation against GBM ground truth" but that validation tested v1, not the current v2.** This is a documentation drift between the closure and the actual validation state.

When Session 2 added v2 ranking, the validation script should have been updated. It wasn't. This is the kind of drift that compounds over time and causes confusion in audits.

**Critical issue 2:** Test 3 (BBB) is fully obsoleted by Session 1. The test's logic checks for BBB-relevant fields in compound dicts using a hardcoded list `['logp', 'tpsa', 'mw', 'hba', 'hbd', ...]`. After Session 1, compounds DO have these fields (under `properties` key). But Test 3 doesn't look there. Result: Test 3 reports GAP for data that exists. The closure's "Test 3: GAP — BBB-relevant properties NOT in ChEMBL dump" verdict is wrong as of post-Session 1.

This means the closure document has at least one false statement about validation state.

**Critical issue 3:** Verdict thresholds are arbitrary. "Top 30 = PASS" for TMZ. "5/7 = PASS" for white-space. "5/6 = PASS" for tumor suppressors. No documented rationale. No sensitivity analysis. If results degrade by one position, the test silently moves between PASS / CHECK / FAIL with no clear meaning of correctness.

### 4.3 — What validation should look like

A proper validation suite for INTERCEPTA Workstream A would:
- Test the current ranking (v2), not the old (v1)
- Test BBB filtering correctly (look at `properties` and `bbb` fields, not stale field list)
- Have documented thresholds with rationale
- Use a single verdict taxonomy consistent with other files
- Be parameterizable over disease (test on GBM, NSCLC, AML — same code path)

The current validation script is GBM-specific, version-stale, and partially obsoleted. It should be rewritten when the validation framework is built for Workstream B.

---

## Section 5 — Data source reliability matrix

For each external data source, what is it reliable for in our pipeline, and what is it not reliable for.

### OpenTargets associations (via `disease_net_builder`)
**Reliable for:**
- Disease-gene association scoring (4.5M associations, 26,288 diseases)
- Top-N gene selection per disease at score≥0.1
- Pathway membership lookup per gene

**NOT reliable for:**
- Per-gene mutation frequency in disease (downstream from TCGA but not always populated)
- Disease-specific subtypes (e.g., distinguishing GBM mesenchymal vs proneural)

**Confidence in Workstream A use:** HIGH. The disease net's gene list and association scores are the primary trustworthy output.

### GDSC `PUTATIVE_TARGET` field
**Reliable for:**
- Kinase-inhibitor target identification (gene symbols are populated correctly for ~90% of TKIs)
- Drug-target relationship for small-molecule single-target compounds

**NOT reliable for:**
- Cytotoxic chemotherapy (TMZ → "DNA alkylation" mechanism string, not a gene symbol)
- Antibody therapeutics (often blank or non-gene strings)
- Multi-target drugs (typically truncated or mechanism-class)
- Vehicle-class drugs (vehicles, blockers, ionophores, etc.)

**Confidence in Workstream A use:** PARTIAL. v2 ranking's failure to surface TMZ for GBM (rank 257/286) is structurally caused by this field's unreliability for cytotoxics. **This is the single most impactful data source limitation in the entire pipeline.** Any drug whose true target is not encoded as a gene symbol in this field is invisible to channels 2 and 3 of v2 ranking.

**Mitigation path:** ChEMBL `/mechanism` endpoint provides drug-name → mechanism-of-action mappings that include gene-target annotations. Integrating this would address the cytotoxic gap. NOT yet integrated. Would require a new enrichment phase.

### GDSC dose-response (`GDSC2_fitted_dose_response.xlsx`)
**Reliable for:**
- Per-cell-line drug response (AUC, IC50)
- Disease-tissue-restricted aggregate response when tissue mapping is correct

**NOT reliable for:**
- In vivo / clinical efficacy prediction (in vitro screening is upstream of clinical trials)
- Drugs not in the GDSC panel (286 drugs total, vs. tens of thousands of clinical candidates)
- Brain-penetrant subset of compounds (no BBB filter applied at GDSC level)

**Confidence in Workstream A use:** MODERATE. Channel 1 of v2 ranking uses median AUC in tissue-matched cell lines. The mapping from disease name to GDSC tissue keyword is heuristic and limited to 9 hardcoded cancer types in `_disease_to_tissue_keywords`. **Anything outside those 9 falls back to first-word-of-disease-name matching, which is unreliable.**

### ChEMBL `target_components__accession` lookup
**Reliable for:**
- UniProt → SINGLE PROTEIN target_chembl_id (single-target case, vast majority)
- After Drift 1 fix: best-data-match selection when multiple targets exist for one UniProt

**NOT reliable for:**
- Multi-protein-complex targets (e.g., ribosome, spliceosome — not SINGLE PROTEIN)
- Non-protein targets (DNA-binding small molecules, nucleic acid drugs)

**Confidence in Workstream A use:** HIGH for our SINGLE PROTEIN scope. The Drift 1 fix is architecturally correct even though it didn't change outcomes on the 8 canonical test genes (all single-target — fast path).

### ChEMBL bioactivity (filtered: pchembl≥5, IC50/Ki/EC50/Kd, exact relation)
**Reliable for:**
- Quantitative kinase-inhibitor potency comparisons
- Target-compound activity ranking by pchembl
- Drug discovery space dominated by small-molecule enzyme inhibitors

**NOT reliable for:**
- Allosteric modulators (often reported with non-standard activity types)
- Functional antagonists / agonists at receptors (different activity types)
- Cell-based / phenotypic assay drugs (no clean target → activity mapping)
- Approved drugs with mechanism known but not in bioactivity DB (e.g., monoclonal antibodies)

**Confidence in Workstream A use:** HIGH for kinase-inhibitor space (which is most of the v2 top-30 for GBM). LOW for cytotoxics, biologics, vaccines.

### ChEMBL `/mechanism` endpoint
**Status:** NOT YET INTEGRATED in our pipeline. Would close the GDSC PUTATIVE_TARGET cytotoxic gap. Strong candidate for next data source addition.

### ChEMBL `molecule_properties` (Session 1)
**Reliable for:**
- Most small-molecule drugs (~95% have full property profile)
- Lipinski rule-of-five fields (MW, logP, TPSA, HBD, HBA, aromatic_rings, qed_weighted)
- BBB MPO 4-component scoring inputs

**NOT reliable for:**
- Natural products, peptides (often missing properties)
- Compounds with undefined stereochemistry (some properties null)
- Antibodies and other biologics (entirely missing property profiles)

**Confidence in Workstream A use:** HIGH for small molecules. KNOWN GAP for biologics.

### STRING aliases (`9606.protein.aliases.v12.0.txt.gz`)
**Reliable for:**
- ENSP → gene symbol mapping when source-filtered to `Ensembl_HGNC_symbol` or `BioMart_HUGO`

**NOT reliable for:**
- UniProt mapping (deprecated path; STRING gives non-canonical accessions for multi-isoform genes)

**Confidence in Workstream A use:** HIGH for ENSP→symbol. The deprecated UniProt path is correctly archived per P16; current code does not use it.

### STRING links (`9606.protein.links.v12.0.txt.gz`)
**Reliable for:**
- High-confidence protein-protein interactions at score≥700
- Symmetric interactions (we collapse partner_score appropriately)

**NOT reliable for:**
- Causal/directional relationships (STRING doesn't distinguish direction)
- Tissue-specific or condition-specific interactions (STRING aggregates across all)
- Interactions absent from STRING (some validated PPIs not yet in v12)

**Confidence in Workstream A use:** HIGH for our use case (network proximity, escape route inference at high-confidence threshold).

### UniProt REST API (`gene_exact + reviewed:true + organism_id:9606`)
**Reliable for:**
- Gene symbol → canonical Swiss-Prot accession (453/458 GBM genes mapped)
- Multi-batch query with synonym fallback

**NOT reliable for:**
- Genes with no Swiss-Prot reviewed entry (5/458 unmapped — typically pseudogenes or non-coding)
- Ambiguous gene symbols (we resolve via `gene_exact:` strict match; ambiguous symbols may miss)

**Confidence in Workstream A use:** HIGH. The 99% mapping rate confirms reliability.

### AlphaFold availability HEAD-check
**Reliable for:**
- Existence of `model_v6` PDB at predictable URL pattern (443/453 GBM proteins have structures)

**NOT reliable for:**
- Structure quality (HEAD check is binary; doesn't assess pLDDT confidence)
- Multi-domain proteins (single-chain prediction may miss domain context)
- Apo vs holo state (predictions are typically apo-form)

**Confidence in Workstream A use:** HIGH for existence; PARTIAL for quality. We don't currently check pLDDT scores. Would need to download PDBs and parse confidence per residue.

### ClinicalTrials.gov v2 API search-by-target-as-intervention
**Reliable for:**
- Trials whose intervention or condition explicitly mentions the target gene
- Phase distribution and overall_status counts per gene
- Disease-restricted trial counting (when condition term is well-formed)

**NOT reliable for:**
- Trials where the gene is mentioned peripherally (false positives; e.g., REST=42 trials but 0 compounds — REST is a gene name AND a common English word)
- Trials of biologics (sometimes hard to attribute to a specific gene target)
- Discontinued or withheld trials (status field is best-effort)
- Drug-name-specific novelty (we search by gene, not by drug; can't tell if specific drug has been tried in disease)

**Confidence in Workstream A use:** HIGH for volume; LIMITED for per-drug novelty. The known false-positive risk for genes with English-word names (REST, MET in some contexts, SET, RUNX) is a documented limitation.

### GTEx tissue selectivity
**Reliable for:**
- Per-gene tissue expression patterns across 54 tissues
- Selectivity scoring (tissue-specific vs. ubiquitous)

**NOT reliable for:**
- Disease-specific expression in disease tissue (GTEx is from healthy donors)
- Cell-type-specific expression (GTEx is bulk, not single-cell)
- Per-drug therapeutic index (requires combining selectivity with drug exposure)

**Confidence in Workstream A use:** PARTIAL. We capture per-gene selectivity but don't compute per-drug therapeutic index. This is part of why item 6 (safety/ADMET) is PARTIAL not DELIVERED in the deliverable test.

### BBB MPO 4-component (Wager et al. 2010 variant)
**Reliable for:**
- Passive-diffusion-based BBB penetration prediction
- Drug-likeness ranking among small molecules (TMZ MPO=3.14, Imatinib MPO=1.75 — both clinically correct)
- Categorical filtering (likely_pos / borderline / likely_neg / data_unavailable)

**NOT reliable for:**
- Active transport mechanisms (P-gp efflux, GLUT1, LAT1 — not modeled)
- Prodrug approaches (e.g., levodopa converts to dopamine after crossing BBB)
- Antibody / large molecule transport (different mechanism entirely)
- Specific dose / regimen effects

**Confidence in Workstream A use:** MODERATE. Passive diffusion is the dominant route for small molecules and the MPO score correctly ranks our test compounds. But for any drug where active transport matters (P-gp substrates → false BBB+ predictions; LAT1 substrates → false BBB- predictions), we'd be wrong. **Best treated as a screening filter, not a deterministic predictor.**

---

## Section 6 — Full architectural drift catalog (42 items)

Consolidated from chunk-by-chunk reading of all three files. Numbered by discovery order. Severity rated H/M/L by impact on vision deliverable.

### From `intercepta_pipeline_v0.py` chunks 1-4

1. **[H]** Two ranking functions (v1 GDSC-only, v2 composite) — overlapping concerns, both still active
2. **[H]** `_disease_to_tissue_keywords` is 9-disease hardcoded dict — structural blocker for "any disease" claim
3. **[M]** BBB gate values (0.5 borderline, 0.5 unknown) are engineering choices, docstring claim of "published precedent" is partially misleading
4. **[H]** Hidden coupling: `rank_drugs_for_disease_v2` calls 4 enrichment functions internally — god function
5. **[L]** `_get_drug_rank_in_v2` appears to be dead code
6. **[L]** STRING aliases header detection has inverted branches (theoretical bug, doesn't fire)
7. **[M]** Three implicit state mechanisms (`_builder`, `_STRING_CACHE`, disk caches treated as singletons)
8. **[L]** STRING UniProt-mapping fields in `_STRING_CACHE` are dead (only deprecated function populates)
9. **[L]** File header docstring stale (no Session 1/Session 2 mention)
10. **[L]** `aliases_version` cache field is documentation masquerading as state
11. **[H]** `populate_chembl_compounds` god-function: API + BBB augmentation + net population
12. **[M]** BBB augmentation buried as a flag, not its own function
13. **[M]** `populate_clinical_trials` docstring contradicts implementation re: gene filtering
14. **[L]** `intervention_types` collected per trial but never consumed downstream
15. **[M]** `surface_undruggable_priority_targets` defaults `cns_disease=False` — should auto-detect
16. **[M]** Inconsistent verification style: `assert` in pipeline vs PASS/FAIL/CHECK in standalone validation
17. **[L]** Selective ChEMBL cache invalidation in verification mutates real cache
18. **[L]** Nested score functions inside `compute_cns_mpo_score` re-defined per call
19. **[L]** Verification re-runs phases that v2 also runs internally (caches mask redundancy)
20. **[M]** Verification block is ~280 lines — should be separate file
21. **[M]** Verification doesn't propagate failure to exit code (CI can't detect FAIL)
22. **[L]** Session 1 BBB known-compound test prints expectations but doesn't assert
23. **[H]** Verification pass criterion (TMZ top 30) is structurally unmeetable with current data sources

### From `generate_pharma_deliverable.py`

24. **[H]** Script hardcoded to GBM despite framing as "any disease deliverable"
25. **[M]** Function names (`load_gbm_net`, etc.) embed scope assumptions
26. **[M]** Five item generators depend on `_parse_candidate_targets` helper that exists because of representation mismatch between ranking and net layers
27. **[H]** Item 9 (SOC comparison) hardcodes GBM SOC with no disease-agnostic mechanism
28. **[H]** Item 10 (trial design) defaults to MGMT methylation biomarker, GBM-specific
29. **[L]** Items 3, 4, 5, 7 are nearly identical 5-line GAP stubs (shareable placeholder logic)
30. **[L]** BBB gate value interpretation duplicated between deliverable and pipeline (no shared constant)
31. **[M]** No staleness check between cached net snapshot and live v2 ranking
32. **[M]** No package/module structure — directory-incidental imports
33. **[M]** PARTIAL items 9, 10 contain hardcoded disease-specific facts (mild fabrication concern despite P15 claim)

### From `validate_workstream_a_gbm.py`

34. **[H]** Test 1 calls v1 `rank_drugs_for_disease`, not current v2 — staleness drift
35. **[H]** Test 3 BBB test is stale post-Session 1; reports GAP for data we now have
36. **[L]** `bbb_penetration_likely` function is dead code (defined, unused)
37. **[L]** `GBM_ONCOGENIC_DRIVERS` is defined but never tested — dead data
38. **[M]** Three different verdict taxonomies across three files
39. **[L]** `load_gbm_net` duplicated between validation and deliverable scripts
40. **[H]** No test for v2 ranking in independent validation; only in pipeline self-test
41. **[M]** Validation thresholds (top 30, 5/7, 5/6) are arbitrary, no rationale
42. **[L]** Three identical `sys.path.insert` calls in three test functions

### Drift severity tally
- **HIGH (10):** #1, #2, #4, #11, #23, #24, #27, #28, #34, #35, #40
- **MEDIUM (15):** #3, #7, #12, #13, #15, #16, #20, #21, #25, #26, #31, #32, #33, #38, #41
- **LOW (17):** #5, #6, #8, #9, #10, #14, #17, #18, #19, #22, #29, #30, #36, #37, #39, #42

(Note: count is 11 HIGH because I added #40 to high-impact retroactively — no validation of v2 ranking in standalone validation is structurally significant.)

---

## Section 7 — The three vision-required layers and proposed module boundaries

Vision Stage 5 is "ranking + delivery." But the pipeline implements three distinct logical layers, not two. Naming them clearly:

### Layer 1: Disease enrichment (Workstream A's core deliverable)
**Purpose:** Take a disease ID, produce a richly enriched disease net with all available evidence types.

**Inputs:** Disease query (name or ID)
**Outputs:** A standardized `DiseaseNet` object containing:
- Genes with association scores
- STRING interactions per gene
- AlphaFold structure availability per gene  
- ChEMBL bioactivity compounds per gene (with optional BBB augmentation)
- Clinical trial counts and metadata per gene
- Pathway memberships, metabolite associations, immune relevance

**Current state:** Working. ~36 functions in pipeline file produce this layer correctly.

**Proposed module structure:**
```
intercepta/
  disease/
    __init__.py
    resolver.py       # resolve_disease, build_net (Phase 1)
    builder_loader.py # _get_builder, singleton wrapper
    summary.py        # corrected_net_summary, print_net_summary
  enrichment/
    __init__.py
    metabolites.py    # enrich_with_metabolites
    string.py         # populate_string_interactions + helpers
    string_archive.py # deprecated UniProt-mapping function (P16)
    uniprot.py        # _query_uniprot_canonical_batch
    alphafold.py      # attach_alphafold_structures, _check_alphafold_url, download_alphafold_pdb
    chembl.py         # populate_net_from_chembl_cache + helpers (split god-function)
    chembl_fetch.py   # fetch_chembl_compounds_to_cache (API only, no net)
    chembl_bbb.py     # augment_chembl_cache_with_bbb (BBB augmentation only)
    clinical_trials.py # populate_clinical_trials + helpers
  pharmacology/
    __init__.py
    bbb.py            # compute_cns_mpo_score, compute_bbb_likelihood (cross-cutting)
  data_sources/
    __init__.py
    gdsc_adapter.py   # _disease_to_tissue_keywords, inspect_gdsc_drugs
```

### Layer 2: Drug ranking (currently god-function)
**Purpose:** Take an enriched disease net + a drug panel, produce ranked drug candidates.

**Inputs:** Enriched `DiseaseNet`, drug panel (e.g., GDSC 286 drugs), ranking config
**Outputs:** Ranked DataFrame with per-drug composite score and channel breakdown

**Current state:** v2 is a god-function. Bundles enrichment + ranking + config detection. Should be refactored.

**Proposed module structure:**
```
intercepta/
  ranking/
    __init__.py
    composite.py      # rank_drugs_composite(net, panel, weights) — pure ranking, requires enriched net
    channels/
      __init__.py
      gdsc.py         # channel_gdsc_efficacy(net, panel, tissue)
      chembl.py       # channel_chembl_potency(net, panel)
      trials.py       # channel_clinical_activity(net, panel)
      bbb.py          # channel_bbb_gate(net, panel) — multiplicative for CNS
      proximity.py    # channel_network_proximity(net, panel)
    config.py         # default weights, CNS detection helper, named ranking presets
```

Critical change: ranking functions take an **already-enriched** net. They do NOT call enrichment internally. If net is missing required enrichments, raise a specific error: `RankingError("Channel C requires populated chembl_compounds; net has only N/M genes enriched")`.

### Layer 3: Pharma deliverable generation (Stage 5 final output)
**Purpose:** Take ranked candidates + an enriched net + disease-specific configuration, produce the 10-item pharma deliverable per candidate.

**Inputs:** Disease ID, ranked candidates list, enriched net, disease config (SOC, biomarkers, regulatory context)
**Outputs:** JSON + markdown deliverable per candidate, with status per item

**Current state:** Hardcoded to GBM. Two of ten generators contain GBM-specific facts (SOC, biomarkers).

**Proposed module structure:**
```
intercepta/
  deliverable/
    __init__.py
    generator.py        # generate_deliverable(disease_id, candidates, net, disease_config)
    items/
      __init__.py
      structure.py      # item 1
      mechanism.py      # item 2
      outcomes.py       # item 3 (currently GAP)
      resistance.py     # item 4 (currently GAP)
      combination.py    # item 5 (currently N/A or GAP)
      safety.py         # item 6
      synthesis.py      # item 7 (currently GAP)
      novelty.py        # item 8
      soc_comparison.py # item 9
      trial_design.py   # item 10
    config/
      __init__.py
      gbm.json          # GBM SOC, MGMT biomarker, etc.
      nsclc.json        # NSCLC SOC, EGFR/PD-L1/ALK biomarkers
      mcrpc.json        # mCRPC SOC, AR-V7 biomarker
    formatters/
      __init__.py
      json_writer.py
      markdown_writer.py
```

Critical change: each item generator reads `disease_config` (loaded from JSON file per disease) for any disease-specific facts. **Zero hardcoded disease facts in code.**

### Cross-cutting concerns
```
intercepta/
  verification/
    __init__.py
    pipeline_self_test.py  # the current 280-line block, broken into named test functions
    fixtures.py            # shared mock data and helpers
  validation/
    __init__.py
    framework.py           # disease-agnostic validation runner
    diseases/
      gbm.py               # GBM ground truth + tests
      nsclc.py             # NSCLC ground truth + tests (Workstream B target)
      mcrpc.py             # mCRPC ground truth + tests
  utils/
    __init__.py
    cache.py               # shared cache I/O patterns
    constants.py           # BBB gate values, default weights, version strings
```

### Module structure rationale

- **Separation of layers:** enrichment, ranking, deliverable are three distinct concerns and should be three packages.
- **Disease-agnostic generation, disease-specific configuration:** the code stays universal; per-disease facts live in JSON config files.
- **Pure ranking:** ranking functions don't call enrichment; they require pre-enriched input. Forces the caller to structure pipeline correctly.
- **Validation parameterizable over disease:** the validation framework is the same; disease-specific ground truth is loaded as data.
- **Verification ≠ validation:** verification tests pipeline self-consistency (smoke tests). Validation tests pipeline output against external ground truth. Currently conflated.
- **P16 preservation:** deprecated functions and old versions move to clearly-named archive modules (`string_archive.py`, etc.) where they remain importable but don't pollute current code paths.

---

## Section 8 — Architectural debt prioritized by impact on vision deliverable

The 10-item pharma deliverable is the vision's measurable output (Vision 9.1). This section ranks debt by its impact on that output.

### Priority 1: Debt blocking >1 deliverable item
These are the architectural problems whose resolution directly upgrades multiple GAP items to PARTIAL or DELIVERED.

| Debt | Items unblocked | Action |
|------|----------------|--------|
| GDSC PUTATIVE_TARGET unreliability for cytotoxics | Item 2 (mechanism for non-kinase drugs), Item 1 (structure) | Add ChEMBL `/mechanism` endpoint integration; new enrichment phase |
| Hardcoded disease config in items 9, 10 | Items 9, 10 for any non-GBM disease | Extract per-disease config to JSON |
| Ranking god-function | Items 1-10 for clean reproducibility | Refactor v2 into pure ranking + explicit enrichment |
| ODE mCRPC-only structural limit | Items 3, 4 directly; cascade unblocks 6, 9, 10 | This is Workstream B (out of refactor scope) |

### Priority 2: Debt blocking validation/verification correctness
These don't block items directly but prevent us from knowing if the pipeline actually works.

| Debt | Impact | Action |
|------|--------|--------|
| Validation tests v1 ranking, not v2 | Closure document is partially false about validation state | Update Test 1 to v2 |
| Test 3 BBB stale post-Session 1 | False GAP report | Update Test 3 to use `properties` field |
| Three different verdict taxonomies | Cross-file aggregation impossible | Standardize on PASS/PARTIAL/GAP/FAIL/N/A |
| TMZ-top-30 pass criterion structurally unmeetable | Verification will FAIL forever despite real progress | Either fix data sources (Workstream B/C) or revise criterion to "kinase-inhibitor space coverage" |
| Verification doesn't propagate exit code | CI can't tell pass from fail | Add return code propagation |

### Priority 3: Debt that compounds over time
These don't block today's deliverable but get worse with each new disease/feature/session.

| Debt | Compounding risk | Action |
|------|------------------|--------|
| 2300-line single pipeline file | New phases will accumulate; soon 3000+ | Refactor into package now, before NSCLC adds more |
| Three implicit state mechanisms | Each new cache adds another | Class-based state with explicit lifecycle |
| Documentation drifts (header, docstrings vs code) | Diverges further with each session | Auto-generate phase summary from registered phases |
| Dead code (ONCOGENIC_DRIVERS, bbb_penetration_likely, _get_drug_rank_in_v2) | Easy to leave, harder to remove later | Delete during refactor |
| Hardcoded `_disease_to_tissue_keywords` 9-cancer dict | NSCLC will hit fallback to "first word"; AML will hit fallback | Replace with GDSC tissue ontology lookup |

### Priority 4: Debt that is cosmetic
Minor. Worth fixing during refactor for cleanliness; not blocking.

- STRING header detection inverted branches (theoretical bug)
- Nested score functions in `compute_cns_mpo_score`
- Selective cache invalidation in verification block
- Three identical `sys.path.insert` calls in validation
- Empty 5-line GAP stub functions

---

## Section 9 — Honest assessment: is the foundation sound for Workstream B?

**Workstream B's stated goal:** Generalize the phenotype-structured ODE from mCRPC to NSCLC. Test whether the breakthrough that produced HR=0.675 zero-tuned for docetaxel in mCRPC generalizes to a different cancer.

**What Workstream B requires from Workstream A:**

1. **Disease enrichment for NSCLC** — need to build NSCLC disease net with same enrichment phases (STRING, AlphaFold, ChEMBL with BBB, ClinicalTrials)
2. **Drug ranking for NSCLC** — need v2-equivalent ranking that produces sensible NSCLC drug list (osimertinib, gefitinib, alectinib, atezolizumab in top-N)
3. **Stable pharma deliverable generator** — need to produce 10-item output for NSCLC top-5 to compare against GBM 2/10 baseline
4. **Validation that works for NSCLC** — need to test against NSCLC trials (FLAURA, KEYNOTE-024, ALEX, AURA3)

### Item 1 (NSCLC enrichment): Will work, with caveats
The disease resolver and enrichment phases are disease-agnostic in their logic (operations on gene lists, not on disease-specific facts). NSCLC will resolve to its EFO ID (likely EFO_0003060 lung adenocarcinoma) and enrichment will produce a comparable net.

**Caveat:** GDSC tissue keyword fallback will likely hit "lung" correctly via `_disease_to_tissue_keywords` (which has 'lung', 'nsclc', 'sclc' entries — actually one of the 9 covered diseases). So ranking Channel 1 will work. But for any disease NOT in the 9-cancer hardcoded dict, the fallback to "first word matching" is unreliable.

**Architectural ask:** before Workstream B begins, replace `_disease_to_tissue_keywords` with a proper GDSC tissue ontology lookup. This eliminates the 9-disease blocker.

### Item 2 (NSCLC ranking): Works, but god-function makes failure modes opaque
v2 will run on NSCLC. It will produce a top-N. The architecture problem is that if NSCLC ranking produces unexpected results, we won't know which channel caused it because v2's internals are bundled with enrichment.

**Architectural ask:** before Workstream B begins, refactor v2 into pure ranking + explicit enrichment chain. This is the highest-leverage refactor for both diagnostic clarity and Workstream B's testability.

### Item 3 (NSCLC deliverable): WILL FAIL
The current deliverable script:
- Function name `load_gbm_net()` — would need rename and parameterization
- Hardcoded GBM SOC dict in item 9 — produces wrong output for NSCLC
- Hardcoded MGMT methylation default in item 10 — wrong biomarker for NSCLC
- No NSCLC config exists

**Running the current deliverable script on NSCLC top-5 candidates would produce factually incorrect output for items 9 and 10, while items 3, 4, 5, 7 still GAP correctly.** This would be visible in the markdown. The script wouldn't crash; it would silently produce wrong content.

**Architectural ask:** before Workstream B begins, refactor deliverable to be disease-agnostic with per-disease JSON configs. Build the NSCLC config alongside the refactor.

### Item 4 (NSCLC validation): WILL FAIL  
Current validation script:
- Hardcoded GBM ground truth dicts (SOC, tumor suppressors, white-space targets)
- Tests v1 ranking, not v2
- Test 3 BBB stale post-Session 1
- No NSCLC analog exists

**Architectural ask:** before Workstream B begins, build the disease-agnostic validation framework with NSCLC ground truth as parallel to GBM ground truth.

### Bottom line on Workstream B readiness

**The foundation supports Workstream B but only after a targeted refactor.**

Specifically:
- Disease enrichment for NSCLC works as-is **(no refactor needed for this part)**
- Ranking will work but should be refactored for testability **(refactor recommended)**
- Deliverable WILL produce wrong content **(refactor required)**
- Validation framework needs to be built **(refactor required)**

If we proceed to Workstream B with the current foundation:
- The phenotype ODE generalization work itself can begin
- But we cannot generate vision-aligned NSCLC deliverable to compare against GBM 2/10 baseline
- And we cannot run principled validation on NSCLC outputs
- We'd be flying blind on whether Workstream B's outputs are "good"

If we refactor first (estimated 1-2 sessions):
- Workstream B begins with clean module boundaries
- NSCLC deliverable comparison against GBM is meaningful
- Validation works for both diseases via the same framework
- Future diseases (AML, mCRPC re-validation, others) plug in cleanly

**Recommendation: refactor first.**

---

## Section 10 — Push-back on prior decisions

This section names where past Claude sessions (including mine in this conversation) made architectural mistakes. Stated for the record per "no diplomatic softening."

### Mistake 1: Session 2 added v2 ranking as a god-function

When validation showed v1 GDSC-only ranking failed for GBM (TMZ rank 257, 4/4 SOC drugs missing or low-ranked), the response was to build v2 with five evidence channels. The architectural error was making v2 internally call all enrichment phases. This made the function impossible to test without running the full pipeline.

The correct response would have been:
- Build v2 as a pure ranking function operating on an already-enriched net
- Validate channel-by-channel: does Channel 2 (ChEMBL) produce sensible scores? Does Channel 4 (BBB gate) correctly identify Imatinib as bbb_neg?
- Then assemble the composite

What actually happened: composite was built first, then validated end-to-end. When TMZ rank 257 emerged, we couldn't isolate which channel was the issue (it's actually GDSC PUTATIVE_TARGET unreliability for TMZ, but this took several iterations to identify).

### Mistake 2: Building deliverable script before deciding fork between B and C

The deliverable script was built to "test the vision deliverable for any disease" — which is correct in principle. But it was built before deciding whether to invest in Workstream B (ODE generalization) or Workstream C (synthesis + ASKCOS). The deliverable test then revealed that 5 items depend on B and 2 depend on C, which was useful information — but if the fork decision had been made first, we might have built only the items relevant to the chosen workstream and validated those properly, rather than building all 10 with most as stubs.

The correct ordering: decide B vs C first based on architectural review (which we are doing now); then build deliverable items relevant to chosen workstream; then validate those properly.

### Mistake 3: Validating GBM SOC recovery as the success criterion for v2 ranking

The implicit success metric was "does v2 rank TMZ in top 30?" This is the wrong metric for the vision's actual goal. The vision says "find the drug — novel candidates not currently in trials, that pass simulation layers." TMZ is already known. The pipeline doesn't need to find TMZ.

The correct metric: "does v2 surface biologically meaningful candidates (kinase inhibitors with EGFR/MET targets) for further simulation? Do those candidates make sense for novel drug discovery in this disease?" By that metric, v2 succeeds for GBM (Foretinib, Osimertinib, AZD3759 in top-5 are all biologically reasonable BBB-penetrant kinase inhibitors).

We spent multiple sessions trying to "fix" v2's TMZ ranking. The right move was to recognize TMZ-recovery as a vision-misaligned metric and document v2's scope as "kinase-inhibitor-space ranking" honestly.

### Mistake 4: Patching pipeline file in place for each new phase

Each phase (2A, 2B, 2C, 2D, 2E, Session 1, Session 2, Action 1) was added as new functions in the same `intercepta_pipeline_v0.py` file. This is the wrong P16 application. P16 says preserve past work; it does NOT say "every new capability lives in the same file."

A real researcher would have created a `pipeline/` package after Phase 2C and structured subsequent phases as new modules. Instead, the file grew from ~600 lines (Phase 1 only) to ~2300 lines (current). The growth was locally cheap and globally expensive — testing, modification, and reading all become harder linearly with file size.

### Mistake 5: Not consolidating the verdict taxonomy

Three files emerged with three different verdict taxonomies (assert-based, PASS/CHECK/FAIL/GAP, DELIVERED/PARTIAL/GAP/N/A). Each was added in a different session for a different purpose. None acknowledged the other. The result: aggregating "is the pipeline working?" across files requires manual translation.

This should have been caught at the second taxonomy. It wasn't. Now we have three.

---

## Section 11 — Concrete next steps

In recommended order:

### Step 1: Approve or revise this architecture review
Prasad reviews this document. Pushes back where analysis is wrong, extends where missing. Approves architecture proposal in Section 7 (or revises).

### Step 2: Targeted refactor (1-2 sessions)
Create the proposed package structure in `~/INTERCEPTA/intercepta/`. Move functions to their proper modules. Specifically:
1. Create `intercepta/disease/`, `intercepta/enrichment/`, `intercepta/pharmacology/`, `intercepta/ranking/`, `intercepta/deliverable/`, `intercepta/verification/`, `intercepta/validation/`, `intercepta/utils/`
2. Move every function from `intercepta_pipeline_v0.py` to its proper module per Section 2 audit
3. Split `populate_chembl_compounds` into 3 functions
4. Refactor `rank_drugs_for_disease_v2` into pure ranking + explicit enrichment chain
5. Refactor deliverable to disease-agnostic + per-disease JSON configs
6. Build GBM JSON config with current hardcoded facts extracted
7. Build NSCLC JSON config with NSCLC SOC, EGFR/PD-L1/ALK biomarkers
8. Refactor validation framework to be disease-parameterizable
9. Update validation to test v2 (not v1) and to test BBB correctly post-Session 1
10. Standardize verdict taxonomy to one (recommend PASS/PARTIAL/GAP/FAIL/N/A)
11. Consolidate exit-code propagation in verification
12. Delete the 5 dead-code items (ONCOGENIC_DRIVERS, bbb_penetration_likely, _get_drug_rank_in_v2, etc.)
13. Move deprecated functions to `*_archive.py` modules
14. Replace `_disease_to_tissue_keywords` with proper GDSC tissue ontology lookup

Old files (`intercepta_pipeline_v0.py`, `generate_pharma_deliverable.py`, `validate_workstream_a_gbm.py`) preserved per P16 in `~/INTERCEPTA/round3_gbm_live_test/code/legacy/`.

### Step 3: Re-run pharma deliverable on GBM with refactored pipeline
Sanity check: does the refactor produce the same 2/10 DELIVERED + 4/10 PARTIAL coverage? If yes, refactor preserved behavior. If different, investigate.

### Step 4: Run pharma deliverable on NSCLC top-5 with refactored pipeline + NSCLC config
This is the test that the refactor was for. Does it produce sensible NSCLC content? Items 9, 10 should now have NSCLC SOC and biomarkers, not GBM ones. Items 1, 2, 6, 8 should DELIVER from NSCLC enrichment data.

### Step 5: Begin Workstream B
With clean foundation, begin ODE generalization to NSCLC. Test whether phenotype-structured ODE breakthrough generalizes. This is the central methodological question Workstream B answers.

---

## Section 12 — What this review does NOT cover

For honesty, naming what is out of scope here:

- **Upstream `disease_net_builder.py`** — not modified by Workstream A; assumed correct based on outputs but not re-audited
- **Vision PDFs** — not directly read in this review; closure document and CLEANUP_NOTES used as canonical reference for vision scope
- **Round 1 mCRPC and Round 2 AML artifacts** — preserved per P16, not in current scope
- **The phenotype-structured ODE itself** — the Workstream B question, not the Workstream A architecture question
- **Generative chemistry / ASKCOS / Layer F** — Workstream C scope
- **The OpenTargets disease_net_builder's tissue mapping** — assumed correct via outputs

---

## Final word

The 2/10 DELIVERED on GBM is honest current state of Workstream A as a Stage 5 producer. It is not a victory and it is not a failure. It is the truth.

The path forward is: refactor (1-2 sessions), then Workstream B with clean foundation, then re-measure deliverable coverage on both GBM and NSCLC with the refactored pipeline. The vision's measure of progress is not "did we patch v2 ranking to push TMZ higher" but "did the 10-item deliverable for any disease move from 2/10 toward 6+/10."

Workstream B is the move that, if it succeeds, lifts items 3, 4, 6, 9, 10 from GAP/PARTIAL toward DELIVERED — potentially to 6/10 or 7/10 average coverage. That is real progress against the vision.

The refactor is the foundation that makes that measurement possible.

— Claude (CSO/AI co-founder)
2026-05-06
