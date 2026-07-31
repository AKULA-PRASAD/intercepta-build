# Pre-registration — B59: does the residual differ by assay format (biochemical vs cell-based)? (FINALIZED 2026-07-31, PRE-RESULT for the test; residuals already known — CONFIRMATORY)

## Status & honesty (stated up front)
This is a **confirmatory / post-hoc** analysis: the A1B1 residuals are already committed (B58). B58 flagged a
*suggestive* assay-type signal (Spearman −0.44) driven by only **2 phenotypic (whole-cell antiviral) targets**. The
question here: does that signal **generalize** to a proper, powerable dichotomy — **biochemical (cell-free isolated
protein/enzyme) vs cell-based (cellular functional + phenotypic)** — or was it an artifact of 2 points? The **pure
phenotypic-vs-biochemical test the ideal design wants is NOT powerable** (only 2 phenotypic VS datasets exist); this is
the closest powerable proxy. The assay-format classification is fixed by external assay documentation, independent of
the residual values (guarding against fishing).

## First principles
An isolated-protein biochemical assay measures a single binding/enzymatic event → activity is a purer function of ligand
structure → potentially higher irreducible (structure-learnable) signal. A cell-based/phenotypic assay integrates
permeability, off-targets, functional coupling, cytotoxicity → activity is a more complex function → potentially lower
residual. H1 predicts biochemical > cell-based.

## Data & classification (from B58's 19 targets; residual = committed A1B1)
Classification by documented assay format (justification per target in code):
- **Biochemical (cell-free enzyme/protein):** FEN1 (nuclease), MAPK1 (ERK2 kinase), ALDH1 (dehydrogenase), GBA
  (glucocerebrosidase), KAT2A (acetyltransferase), PKM2 (pyruvate kinase), tyrosyl-dna_phosphodiesterase (TDP1),
  VDR (nuclear-receptor binding — *ambiguous*, flagged), ESR1_ant (nuclear-receptor binding — *ambiguous*, flagged).
- **Cell-based functional (single target, cellular readout):** m1_agonists, m1_antagonists (Ca²⁺ mobilization),
  orexin1 (GPCR fluorescence), kir2.1, kcnq2, cav3 (ion-channel functional), choline_transporter (uptake),
  stk33 (*ambiguous* — kinase-activity/cell readout, flagged).
- **Phenotypic (whole-cell integrated):** hiv (viral replication), sarscov2_vitro (cytopathic antiviral).

## Analysis (Phase 9)
- **Test 1 (powered):** Mann–Whitney U on residuals, biochemical vs (cell-based-functional ∪ phenotypic); report U,
  two-sided p, one-sided p (H1: biochem > cell-based), and **rank-biserial effect size**; group medians.
- **Test 2 (descriptive, underpowered):** phenotypic (n=2) residual vs the rest — reported descriptively only (no test).
- **Sensitivity:** repeat Test 1 with the 3 ambiguous targets (VDR, ESR1, STK33) excluded.

## Hypotheses
- **H1:** biochemical residual > cell-based, Mann–Whitney one-sided p < 0.05 AND |rank-biserial| ≥ 0.3.
- **H0 (expected):** no significant difference → B58's assay-type signal does NOT generalize to a biochemical/cell-based
  dichotomy; it was driven by the 2 antiviral phenotypic points → the phenotypic mechanism is NOT supported at power
  (a first-class null that correctly bounds B58's suggestive signal).

## Honesty / scope
Confirmatory/post-hoc (residuals known); classification is external-fact-based but 3 targets are genuinely ambiguous
(sensitivity reported). n=19 (9 biochemical vs 10 cell-based) — modest power; pure-phenotypic contrast infeasible
(n=2). Correlation/association ≠ causation. Not wet-lab. A null is the expected, valuable outcome.

## Reproducibility
Deterministic (reads committed B58 residuals + fixed classification + Mann–Whitney). Reproduce ×2 byte-identical
(payload sha256 over summary+groups). Output: `experiments/B59_assayclass_residual/results/B59_metrics.json`.
Env: intercepta-build; INTERCEPTA_DATA owned.
