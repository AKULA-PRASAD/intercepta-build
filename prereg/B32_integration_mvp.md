# Pre-registration — B32: integration MVP — does composing the modules beat any single module on a held-out real-world outcome? (FINALIZED 2026-07-29, PRE-RESULT)

## The question (the "platform" test — whole > parts)
INTERCEPTA has shipped independently-validated modules: ADMET/safety (B30/B30b) and synthesizability (B31). The
honest platform question is NOT "does an ML model predict toxicity" — it is: **do the composed outputs of our
separately-trained modules predict a HELD-OUT real-world developability outcome better than the single best module,
and better than a trivial baseline, on a scaffold split, with leakage controlled?** If yes, the integration adds
genuine value (whole > parts); if no, it is a first-class negative and the modules stand alone.

## Outcome & data (OPEN, held-out — none of our modules trained on it)
**ClinTox** (MoleculeNet, via TDC): 1,478 drugs, label Y=1 = **failed clinical trials for toxicity reasons**
(7.6% positive, 112 toxic), Y=0 = FDA-approved. This is a *real-world* developability endpoint, distinct from any
module's training data. sha/provenance recorded in `data/MANIFEST.md`.

## Module-output features (predicted by modules trained ONLY on their own data)
Per ClinTox molecule, a fixed a-priori panel of interpretable module outputs (~12 features):
- **B30 ADMET** predicted values for developability-relevant tasks: herg, ames, dili, ld50_zhu, cyp3a4_veith,
  bioavailability_ma, bbb_martins, ppbr_az, clearance_microsome_az, half_life_obach (each module fit on its OWN
  full TDC train_val, then applied to ClinTox).
- **B31 synthesizability**: solvable_prob.
- **RDKit SAscore**.

## Leakage control (Constitution rule 3 — mandatory)
Compute canonical-SMILES overlap between ClinTox and EVERY module's training set (union). **Primary evaluation
excludes** all ClinTox molecules present in any module training set (leakage-free); the full set is reported as
secondary. (Measured overlap per task 4–6%.)

## Splits, baselines, model
- **Split:** Bemis–Murcko scaffold split (novel chemistry), k=5 seeds; report mean±sd.
- **Composite (learned):** L2-logistic regression on the ~12 module-output features (standardized), scaffold CV.
- **Baselines (must beat):** (a) trivial base-rate (AUROC 0.5, AUPRC 0.076); (b) **each single module-output** as a
  1-feature classifier — the best of these is "the best single part"; (c) reference: a direct Morgan-2048 GBT
  trained ON ClinTox (scaffold split) — the "train-from-scratch" comparator (does the interpretable 12-feature
  composite approach it?).
- **Metric:** AUROC primary (imbalanced → also AUPRC).

## Hypotheses (assumed FALSE)
- **H1 (whole > parts — the real claim):** composite AUROC > best-single-module-output AUROC AND > 0.5, by more
  than 1 sd across the 5 seeds, on the leakage-free scaffold split.
- **H2 (transfer works):** composite AUROC > 0.6 (the module outputs carry real transferable developability signal).
- **H0:** composite ≈ best single module → integration adds nothing (first-class negative; ship modules standalone).

## Decision rule & interpretation (fixed)
- **H1 PASS** → composing the modules genuinely improves a real-world developability prediction → ship
  `intercepta.integrate.DevelopabilityPrioritizer` (per-molecule module profile + composite risk + AD/conformal) +
  CLI `intercepta prioritize`. Report the honest gap to the direct-trained reference.
- **H1 FAIL** → honest negative: the single best module (likely a tox endpoint) is as good as the composite here;
  record it, ship modules standalone.

## Honesty / scope
Predicts CLINICAL-TOXICITY-FAILURE risk from structure via composed in-silico modules — a research PRIORITIZATION
signal, NOT a clinical or regulatory safety determination. Small positive class (112); scaffold-split; the
approved-vs-failed comparison is confounded by survivorship (approved drugs already passed filters). No claim that
this predicts success — only relative developability risk on this benchmark.

## Reproducibility
Deterministic (seed=42; module fits seeded; scaffold split + CV seeded). Reproduce ×2 byte-identical (payload
sha256). Provenance JSON: git_sha, python, libs, input sha256, seeds, leakage counts, timestamp. Output:
`experiments/B32_integration_mvp/results/B32_metrics.json`.
