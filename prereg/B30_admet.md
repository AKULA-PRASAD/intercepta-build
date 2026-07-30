# Pre-registration — B30: an honest ADMET / safety-prediction module on the TDC benchmark (FINALIZED 2026-07-29, PRE-RESULT)

## The question (a new, buildable module of the discovery pipeline)
A universal drug-discovery platform needs an **ADMET / safety** stage: predict a molecule's Absorption, Distribution,
Metabolism, Excretion and Toxicity from its structure alone. Unlike the single-agent response wall (V7) this is a
well-posed, large-OPEN-data supervised problem with a public, standardized leaderboard. The honest question is NOT
"can we win the leaderboard" — it is: **can a rigorous, reproducible, structure-only baseline predict each ADMET
property meaningfully above a trivial baseline, on the field-standard SCAFFOLD split, and where exactly does it land
relative to published SOTA?** Scaffold split = generalization to novel chemistry (the honest test); the leaderboard
tells us truthfully where we stand.

## Data (OPEN — Therapeutics Data Commons ADMET Benchmark Group; downloaded by us)
`from tdc.benchmark_group import admet_group` — **22 tasks**, each a `{train_val, test}` scaffold split with a
5-seed train/valid protocol and an official metric. Whole group is 1.47 MB (feasibility-gated 2026-07-29). Tasks &
official metrics (from `tdc.metadata.admet_metrics`, authoritative):
- **Regression / MAE (lower better):** caco2_wang, lipophilicity_astrazeneca, solubility_aqsoldb, ppbr_az, ld50_zhu
- **Regression / Spearman (higher better):** vdss_lombardo, half_life_obach, clearance_hepatocyte_az, clearance_microsome_az
- **Classification / AUROC:** hia_hou, pgp_broccatelli, bioavailability_ma, bbb_martins, cyp3a4_substrate_carbonmangels, herg, ames, dili
- **Classification / AUPRC (PR-AUC):** cyp2c9_veith, cyp2d6_veith, cyp3a4_veith, cyp2c9_substrate_carbonmangels, cyp2d6_substrate_carbonmangels

Dataset sizes span ~475–13,130 molecules. SMILES + label only; no controlled data (all public, freely usable).

## Features & model (fixed a priori)
- **Structure featurization:** Morgan/ECFP4 fingerprint (radius 2, 2048-bit, RDKit) **+** a fixed panel of RDKit
  physicochemical descriptors (MolWt, MolLogP, TPSA, NumHDonors, NumHAcceptors, NumRotatableBonds, NumAromaticRings,
  FractionCSP3, NumHeavyAtoms, RingCount, plus a small standard set). Descriptors are median-imputed; unparseable
  SMILES → all-zero vector (recorded).
- **Model:** gradient-boosted trees (sklearn HistGradientBoosting — Classifier for classification tasks emitting
  `predict_proba`, Regressor for regression), deterministic `random_state=42`. One model per task. No per-task
  hyperparameter tuning beyond a single fixed config (honest, not leaderboard-chasing).
- **Protocol (official TDC):** for each of 5 seeds, `get_train_valid_split(benchmark, seed)` → train on `train`,
  predict the FIXED scaffold `test`, `evaluate_many` → **mean ± sd** in the task's official metric.

## Baselines (must beat — Constitution rule 8)
- **Trivial baseline:** classification → predict the training base rate (prevalence) → AUROC 0.5, AUPRC ≈ prevalence;
  regression → predict the training mean → the mean-absolute-deviation MAE floor, and Spearman = 0 (a constant has no
  ranking information). Reported per task alongside our model.
- **Published TDC leaderboard rank-1** (retrieved 2026-07-29, recorded in `experiments/B30_admet/leaderboard_ref.json`
  with per-task model name + source URL) — the SOTA reference. NO SOTA claim is made; the gap is reported honestly.

## Applicability domain / uncertainty (shipped with the module)
Per task, an **applicability-domain (AD) flag** from Tanimoto similarity: for a query molecule, `1 − max Tanimoto
similarity to the training set`; flagged out-of-domain if beyond the 95th percentile of the training set's own
nearest-neighbor distances (analogous to the OOD gate in `synergy.py`). A prediction outside the AD is labeled
low-confidence. This is an in-silico *screening filter*, not a safety guarantee.

## Hypotheses (assumed FALSE)
- **H1 (per-task usefulness — the real bar):** on the official scaffold `test`, our model beats the trivial baseline
  in the task's official metric (MAE lower; AUROC/AUPRC/Spearman higher) by more than 1 sd across the 5 seeds.
- **H2 (aggregate honesty):** we quantify, per task, the gap to published SOTA. Pre-declared interpretation (not a
  pass/fail): a structure-only GBT baseline is expected to LAND MID-LEADERBOARD — competitive on some tasks, clearly
  trailing graph/foundation models (MiniMol, MapLight+GNN, CFA) on others. We report where, without overclaiming.
- **H0:** our model ≈ trivial baseline on a task → that ADMET property is not learnable from these features on the
  scaffold split (first-class negative for that task).

## Decision rule & interpretation (fixed)
- **H1 PASS on the majority of tasks** → a genuine, reproducible ADMET module: a structure-only in-silico screening
  filter that meaningfully predicts PK/safety properties, honestly scoped and benchmarked. SHIP `ADMETPredictor`.
- **Per-task H0** (any task at/below trivial) → recorded as a first-class negative for that property; the module
  abstains or flags it as unreliable. No task is hidden.
- **No leaderboard-win claim** regardless of result. The deliverable is a *validated, honestly-scoped* predictor.

## Honesty / scope
Cell-free structure→property prediction on public medicinal-chemistry datasets. Scaffold-split generalization to
novel chemistry only. An in-silico SCREENING FILTER, **NOT** a safety guarantee and **NOT** a clinical or regulatory
determination. Labels are heterogeneous assay readouts (different labs/protocols); metrics are the field-standard
ones so results are comparable, not authoritative biology. A null on any task is fully expected and first-class.

## Reproducibility
Deterministic (model `random_state=42`; TDC seeds fixed [1..5]; SMILES fingerprints cached, order-independent).
Reproduce ×2 (byte-identical metrics). Provenance JSON: `git_sha`, python, lib versions, TDC benchmark version,
per-input row counts, seeds, timestamp. Output: `experiments/B30_admet/results/B30_metrics.json`. Data provenance +
access class logged in `data/MANIFEST.md`.
