# Pre-registration — B19: is V19 real cross-lineage transfer, or AML-lineage memorization? (FINALIZED 2026-07-29, PRE-RESULT)

## The strongest critic's objection to V19 (the falsification target)
The RNA→FLT3-dependency model is trained on **pan-cancer DepMap, which includes 25 AML lines**. BeatAML is
entirely AML. So inferred-FLT3-dependency could merely be **re-detecting AML lineage / expression state** the model
learned from those AML lines — making V19 partly circular rather than a genuine functional transfer.

## The decisive test
Retrain the dependency model **excluding all AML lines** (a model that has NEVER seen AML), re-infer FLT3-
dependency on BeatAML patient RNA, and re-run the V19 tests. If the signal survives with an AML-naive model, the
RNA→FLT3-dependency relationship is **genuinely cross-lineage** — the memorization critique is defeated. If it
collapses, V19 is (at least partly) AML-lineage-driven — an honest bound.

## Biology caveat (fixed a priori, so results aren't misread)
Strong FLT3-dependence is hematopoietic: of DepMap's 9 lines with FLT3 gene-effect < −0.5, 4 are AML, 3 non-AML
heme, 2 solid. Excluding AML leaves 1070 training cells with 5 FLT3-dependent anchors (learnable). Excluding **all**
blood/lymphocyte lines leaves only 2 dependent (solid) anchors — so an all-heme-excluded collapse would reflect the
*biology of FLT3-dependence being hematopoietic*, NOT that V19 is false. All-heme-excluded is therefore a stringent
secondary bound, not the primary test.

## Scenarios (deterministic; same engine + BeatAML as B16/V19)
- **S0 CONTROL (full DepMap):** must reproduce V19 (meta β≈+7.6, ITD-WT ρ≈+0.22) — sanity check.
- **S1 PRIMARY (exclude 25 AML lines):** dependency model never sees AML.
- **S2 STRINGENT (exclude all blood+lymphocyte lines):** near the biological floor for FLT3; reported with the
  caveat above.
Each scenario: `fit_dependency(["FLT3"], crispr_df=CRISPR_without_excluded)`, infer on BeatAML, then the exact
V19 tests: H1 = OLS `AUC ~ z(dep) + FLT3_ITD + z(R_prolif)`, DL-meta of the dep coefficient across the 4 FLT3
inhibitors (sorafenib, quizartinib, gilteritinib, crenolanib); H2 = pooled Spearman(dep, AUC) within FLT3-ITD-
wildtype patients. Sign: β>0 / ρ>0 = more-dependent → sensitive (V19 convention).

## Hypotheses (assumed FALSE = memorization)
- **H_primary:** in S1 (AML-excluded), H1 meta β>0 with p<0.05 AND H2 ITD-WT ρ>0 with p<0.05 — V19 survives an
  AML-naive dependency model ⇒ genuine cross-lineage transfer.
- H0: S1 signal is null / wrong-signed ⇒ V19 was AML-lineage-driven (memorization).

## Decision rule & interpretation (fixed)
- S0 must reproduce V19 (else pipeline error — halt). **H_primary PASS** iff S1 H1 (β>0, p<0.05) AND S1 H2
  (ρ>0, p<0.05). Report S1 effect sizes vs S0 (attenuation is expected and fine; sign+significance is the test).
- H_primary PASS → V19 is real cross-lineage functional transfer, not AML memorization — materially strengthens the
  claim. H_primary FAIL → honest downgrade: V19 depends on AML lines in the dependency-model training (lineage-
  entangled). S2 interpreted only through the biology caveat.

## Honesty / scope
BeatAML ex-vivo (unchanged from V19; B17 already bounds the clinical endpoint). This tests provenance of the
inferred-dependency signal, not clinical validity. A fail is first-class and would revise V19's strength downward.

## Reproducibility
Deterministic; reproduce ×2. Output: experiments/B19_lineage_leakage/results/B19_metrics.json.
