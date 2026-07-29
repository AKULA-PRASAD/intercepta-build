# Pre-registration — B4: does the mechanism-anchored ENGINE beat its parts? (FINALIZED 2026-07-29, pre-run)

## Question
For the drug–marker pairs we independently VERIFIED (V4–V6), does the cell-line expression-transfer prediction
(V9) add PREDICTIVE value for patient drug response BEYOND the verified mutation marker (and beyond
proliferation and FLT3-ITD)? I.e., are the two verified signal types **complementary** — the core claim of a
"mechanism-anchored engine" — or redundant?

## Frozen drug–marker pairs (declared before running)
1. trametinib ~ **NRAS** mutation (V5, MEK)     — NRAS-mut → sensitive (lower AUC)
2. selumetinib ~ **NRAS** mutation (V5, MEK)     — NRAS-mut → sensitive
3. cabozantinib ~ **NPM1** mutation (V4)         — NPM1-mut → sensitive
4. dasatinib ~ **DNMT3A** mutation (V6)          — DNMT3A-mut → sensitive
5. sorafenib ~ **FLT3-ITD** (established, not ours-verified; labeled) — ITD → sensitive to FLT3i
Markers: NRAS/DNMT3A = non-silent WES variant (VEP classes: missense/frameshift/stop_gained/inframe indel/
splice_acceptor/donor/protein_altering/start_lost/stop_lost); NPM1, FLT3-ITD = clinical positive/negative.
Join: expression+AUC by dbgap_rnaseq_sample; WES DNA sample → RNA sample via clinical dnaseq↔rnaseq map.

## Model (locked, per pair)
OLS: `AUC ~ marker + R_prolif + transfer_pred [+ FLT3_ITD]` where transfer_pred = GDSC2-trained DepMap-RNAseq
expression map prediction for that drug (B3b pipeline). FLT3_ITD covariate included for pairs 1–4 (excluded for
pair 5 where it IS the marker). Patients with the drug's AUC, marker status, and expression.

## Hypotheses (assumed FALSE) + decision rule (fixed)
- **H_add (primary, per pair):** transfer_pred partial p<0.05 with expected sign (positive coef: higher
  predicted LN_IC50 → higher AUC) → expression adds beyond the marker+prolif+ITD.
- **H_marker (per pair):** marker partial p<0.05 with expected sign (negative coef) → marker adds beyond
  expression.
- **Complementary pair** = BOTH H_add and H_marker hold (independent, non-redundant contributions).
- **Engine > parts CONFIRMED** iff ≥ 3 of 5 pairs show H_add (transfer adds beyond the verified marker). A
  DerSimonian–Laird random-effects meta of the standardized transfer_pred effect across pairs is reported
  (secondary). Corroboration: 5-fold CV Spearman of combined vs marker-only vs transfer-only (descriptive).

## Falsification / honesty
Multiple analyses have now been run on BeatAML (B3–B3e); B4 tests a DISTINCT question (mutation×expression
complementarity) on PRE-DECLARED pairs — noted as a limitation (single cohort, accumulating tests). BH-FDR
across the 5 pairs applied to the primary transfer_pred p-values. No claim beyond these specific drugs.

## Honest prior
These are exactly the mutation-DRIVEN drugs, so the marker may dominate and expression may add little →
plausible null (~30–50% that ≥3 pairs show H_add). A null = "for mutation-driven drugs the marker suffices;
expression transfer and mutation markers cover DIFFERENT drug sets" — still a clean, useful engine-design result.

## Reproducibility
Ridge closed-form; OLS deterministic (emitted floats rounded to 6 dp); CV seed=42. Reproduce ×2.
Output: `experiments/B4_mechanism_integration/results/B4_metrics.json`.
