# Pre-registration — B31: an honest synthesizability module (retrosynthetic-solvability prediction) (FINALIZED 2026-07-29, PRE-RESULT)

## The question (pipeline module #5)
A drug-discovery platform must estimate whether a proposed molecule can actually be MADE. The field-standard,
label-grounded target is **retrosynthetic solvability**: can an automated CASP tool (AiZynthFinder, USPTO reaction
templates) find a synthesis route to the molecule? The honest question: can a structure-only classifier predict
solvability, beating (a) a trivial base-rate baseline and (b) the standard SAscore heuristic — and how does it
compare to the published RAscore — on BOTH the original random split AND a harder scaffold split (generalization to
novel chemistry)?

## Data (OPEN — RAscore / Thakkar et al., Chem Sci 2021; downloaded by us)
RAscore `data/data.zip` (MIT code; labels = AiZynthFinder on ChEMBL compounds, USPTO policy; ChEMBL-derived, open).
`uspto_chembl_classification_{train,test}.csv`: **179,413 train / 19,935 test** molecules; columns `smi` (SMILES),
`activity` (1 = a retrosynthetic route was found = "solvable", 0 = not; **75.2% positive**). sha256 recorded in
`data/MANIFEST.md`. (GDB-ChEMBL / GDB-MedChem variants also present; ChEMBL is the drug-relevant primary.)

## Features & model (unified with ADMET, per the integration plan)
- **Featurization:** Morgan/ECFP4 2048-bit + 17 RDKit physchem descriptors (identical to `intercepta.admet`, so the
  chemistry modules share one representation).
- **Model:** HistGradientBoostingClassifier (deterministic, seed=42), emitting `predict_proba`.
- For tractability, deterministic seeded subsample (seed=42) of the training pool to ~50k (well-powered); recorded.

## Splits
1. **Original random split** (RAscore's own train/test) — comparable to the published RAscore numbers.
2. **Bemis–Murcko scaffold split** (train/test scaffolds disjoint) — generalization to NOVEL chemistry, the honest
   bar (consistent with the ADMET scaffold-split discipline). Primary.

## Baselines (must beat) & SOTA reference
- **Trivial:** predict the base rate (prevalence 0.752) → AUROC 0.5, AUPRC ≈ 0.752.
- **SAscore heuristic** (RDKit / TDC SA oracle), correctly oriented (higher SA = harder → less solvable, so the
  classifier score = −SA). Report its AUROC/AUPRC on each split.
- **Published RAscore SOTA reference** (Thakkar et al. 2021, ChEMBL test, retrieved 2026-07-29): RAscore XGBoost
  **AUC 0.95**, DNN **0.93**; heuristics-as-classifiers SAscore 0.15 (= 0.85 oriented), SCscore 0.39, SYBA 0.74.
  Recorded for honest comparison; NO SOTA claim.

## Hypotheses (assumed FALSE)
- **H1 (usefulness — the real bar):** learned AUROC > 0.5 AND > the oriented-SAscore baseline, on BOTH splits, by
  more than the seed sd.
- **H2 (generalization gap, honesty):** scaffold-split AUROC < random-split AUROC (expected; report the true gap —
  novel-chemistry solvability is harder).
- **H3 (comparability):** on the RANDOM split, our AUROC is within a stated margin of the published RAscore (same
  model family; a sanity check, not a SOTA claim).
- **H0:** learned ≈ SAscore/trivial → structure adds nothing beyond the heuristic (first-class negative).

## Decision rule & interpretation (fixed)
- **H1 PASS on the scaffold split** → a validated, honestly-scoped synthesizability screening filter → SHIP
  `intercepta.synth.SynthesizabilityScorer` (solvability probability from SMILES + SAscore + Tanimoto
  applicability-domain flag + B30b-style conformal prediction-set), + CLI `intercepta synth` + data-free tests.
- **H1 FAIL** → learned solvability adds nothing beyond SAscore here → first-class negative; ship SAscore-only or abstain.

## Honesty / scope
Predicts **algorithmic retrosynthetic solvability** (AiZynthFinder + USPTO templates + a fixed building-block
stock) — a *computational proxy* for synthesizability, NOT a guarantee that a molecule can be made in a real lab,
and dependent on the CASP tool/template/stock choices baked into the labels. Scaffold-split generalization only. A
research screening signal, not a chemistry verdict.

## Reproducibility
Deterministic (seed=42; seeded subsample; scaffold split deterministic). Reproduce ×2 byte-identical (payload
sha256). Provenance JSON: git_sha, python, libs, input sha256, seeds, timestamp. Output:
`experiments/B31_synthesizability/results/B31_metrics.json`.
