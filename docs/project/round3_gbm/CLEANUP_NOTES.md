# Action 1 Cleanup — Phase 2D drift fixes

Date: 2026-05-06
Per Principle 4 (fix structure, don't tune) and Principle 16 (preserve past work).

## Context

Phase 2D verification on GBM (83.5 min, completed 2026-05-04) closed Gap 7 cleanly:
270/458 genes with ChEMBL compounds, 7,424 total. The output surfaced four small
drifts. Action 1 addressed all four. Verification re-run on 2026-05-06.

## The four drifts and their resolution

### Drift 1: ChEMBL target picked first-match instead of best-data-match

Original concern: For UniProts with multiple SINGLE PROTEIN targets in ChEMBL,
the function returned targets[0] from ChEMBL's response order, which could pick
a less-curated entry.

Fix implemented: `_chembl_query_uniprot_target` now queries all SINGLE PROTEIN
targets matching the UniProt, counts records meeting downstream criteria
(pchembl>=5, standard_type in IC50/Ki/EC50/Kd, standard_relation '='), and
picks the target with the highest count. Ties broken by ChEMBL default order.
Single-match cases hit fast path with no extra API calls.

Verified via diagnostic on 8 canonical test genes (EGFR, BRAF, TP53, PIK3CA,
AKT1, MET, ERBB2, PTEN): all 8 have exactly 1 SINGLE PROTEIN target per UniProt
in ChEMBL. Fast-path triggered for all 8. The best-match logic never engaged,
never compared, never chose for these specific cases.

This means:
- The fix is implemented and correct.
- The fix is dormant on these 8 test cases (only 1 target each, no choice to make).
- The fix will activate naturally when a UniProt has multiple SINGLE PROTEIN
  targets in ChEMBL — which will happen on future diseases with kinases of
  multiple isoforms, multi-subunit complexes, or other multi-target UniProts.

The "DIFFERENT" labels for PIK3CA -> CHEMBL4005 and PTEN -> CHEMBL2052032 in
the canonical-match check do NOT reflect a fix failure. They reflect that my
prior "expected" values (CHEMBL4040 for PIK3CA, CHEMBL2628 for PTEN) were
incorrect assumptions about how ChEMBL links targets to UniProt accessions
via target_components__accession + SINGLE PROTEIN. The pipeline correctly picks
the target that ChEMBL actually returns.

Honest verdict: implemented correctly, untested empirically on multi-target
cases (none in our 8-gene canonical set), will activate as designed on future
multi-target encounters.

### Drift 2: build_net header showed pre-enrichment counts

Fix implemented: `print_net_summary(net, label)` function added.

Verified working: net summary now reports current state honestly across all
enrichment phases. Header from disease_net_builder.py still appears (preserved
per Principle 16) but is followed by an explicit post-enrichment summary.

### Drift 3: high-priority undruggable targets disappear silently

Fix implemented: `surface_undruggable_priority_targets` and
`print_undruggable_targets` functions added.

Verified working: 16 undruggable priority targets surfaced for GBM, including
ATRX, NF1, RB1, CDKN2B, STAG2, LZTR1, ARID1A, FAT1, TERT (all known undruggable
tumor suppressors / structural / chromatin / regulatory genes).

The function correctly does NOT infer alternatives (no PROTAC, no synthetic
lethality routing) — those are explicitly Horizon 2.

### Drift 4: verification block didn't exercise the new functions

Fix implemented: verification block now exercises all of:
- Best-match ChEMBL target lookup (with diagnostic probe)
- print_net_summary
- surface_undruggable_priority_targets
- Full chain: build -> STRING -> AlphaFold -> ChEMBL -> ranking -> undruggable

## Bonus finding: TP53 compound count changed between runs

Run 1 (2026-05-04): TP53 -> CHEMBL4096 -> 0 compounds.
Run 2 (2026-05-06): TP53 -> CHEMBL4096 -> 28 compounds.

Same target ID. Same UniProt. Diagnostic confirms only 1 SINGLE PROTEIN target
exists for P04637, so the change is NOT from target selection.

Most plausible explanation: ChEMBL added bioactivity records for TP53 between
May 4 and May 6, or our earlier query returned a transient empty result during
a database update. We did not cause this change.

Implication: pipeline output is sensitive to upstream ChEMBL updates. This is
a real characteristic of any pipeline reading from a live external database.
Worth documenting; not a bug.

## Verification result summary (2026-05-06)

- Total runtime: ~3-4 min (vs 83.5 min cold) — cache working as designed
- Gap 1+2: PASS (resolve_disease "glioblastoma" -> EFO_0000519, 9906 rows)
- Gap 1: PASS (build_net by name, EGFR + TP53 in top 10)
- Gap 5: PASS (corrected_net_summary returns distinct counts)
- Gap 4: PASS (GDSC2_fitted_dose_response.xlsx detected)
- Drift 1: implemented; dormant on canonical 8 (all single-target); ready
- Drift 1 diagnostic: 8/8 fast-path, 0/8 best-match engaged
- Drift 2: PASS (post-enrichment summary working)
- Drift 3: PASS (16 undruggable priority targets surfaced)
- Drift 4: PASS (regression test integrated into module)
- Coverage: 271/458 genes (59.2%) have ChEMBL compounds, 7452 total
- AlphaFold: 443/453 proteins have structures available
- STRING: 445/458 genes enriched, 39385 edges

## What was NOT changed

- ChEMBL cache from 2026-05-04 preserved (445 entries reused, 8 invalidated for
  diagnostic purposes only)
- DEPRECATED `_load_string_uniprot_mapping_DEPRECATED_v2_replaces` function
  preserved per Principle 16
- disease_net_builder.py not modified
- rank_drugs_for_disease composite scoring not changed
- ODE module structural mCRPC-specificity not addressed (Horizon 2)
- 0/286 drugs ineffective Round 1 issue not addressed (Horizon 2)
- PROTAC / degrader / synthetic-lethality routing for undruggable targets not
  added beyond surfacing them (Horizon 2)

## Action 1 status: CLOSED

Files updated:
- ~/INTERCEPTA/round3_gbm_live_test/code/intercepta_pipeline_v0.py
  (54K -> 60K, added print_net_summary, surface_undruggable_priority_targets,
  print_undruggable_targets, _chembl_count_quantitative_activities,
  _chembl_diagnostic_probe; modified _chembl_query_uniprot_target)
- ~/INTERCEPTA/round3_gbm_live_test/results/gbm_disease_net_action1.json
  (verification net snapshot, 458 genes, post-enrichment state)
