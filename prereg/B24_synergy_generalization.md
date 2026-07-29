# Pre-registration — B24: can we predict drug-combination SYNERGY for UNSEEN combinations? (FINALIZED 2026-07-29, PRE-RESULT)

## The question (a genuinely-new task; open data; just us)
A drug-discovery platform must predict drug COMBINATIONS, not just single agents. Synergy (excess over additivity)
is a fundamentally different signal than single-agent response — so it is NOT automatically bound by the +0.212
single-agent ceiling. The decisive, honest question (the field's real bar): can molecular + drug-structure features
predict synergy for **drug combinations the model has never seen**, beating an informed drug-identity baseline? A
random-split "success" is largely leakage (the model memorizes which pairs are synergistic); generalization to
novel combinations is the property that would actually be useful.

## Data (OPEN — O'Neil 2016 / OncoPolyPharmacology via Therapeutics Data Commons; downloaded by us)
23,052 measurements: 583 drug pairs × 39 cancer cell lines; **Y = Loewe synergy score** (mean 5.1, sd 22.9; 35%
"synergistic" at Y>10). Per-row: cell-line expression feature vector (8,785-dim), and SMILES for both drugs.
Cached locally: oneil_synergy.parquet, oneil_cellfeat.parquet, oneil_smiles.parquet.

## Features & model
- Drug: Morgan/ECFP fingerprints (radius 2, 1024-bit) from SMILES, combined **order-invariantly** (sum + bitwise-AND
  of the two drugs' fingerprints) so synergy(a,b)=synergy(b,a).
- Cell: expression features reduced by PCA (unsupervised; 39 distinct cell lines) to ≤30 components.
- Model: HistGradientBoostingRegressor (nonlinear; sklearn; deterministic seed=42). Target: Y.

## Splits (the crux)
1. **Random 5-fold (rows)** — easy/leaky reference.
2. **Leave-drug-combination-out (grouped 5-fold by pair)** — hold out entire combinations → predict synergy for
   UNSEEN pairs. This is the real generalization test.
3. Secondary: leave-cell-line-out (grouped by cell line).

## Baselines (must beat)
- Global mean; cell-line mean; **drug-pair mean** (random split) / **drug-marginal mean** (LOCO: mean training Y
  over rows sharing either drug — the informed trivial baseline for an unseen pair).

## Hypotheses (assumed FALSE)
- **H1 (sanity, random split):** model out-of-fold Pearson r>0 and beats the pair-mean baseline.
- **H2 (generalization — the real test):** under leave-drug-combination-out, model Spearman ρ(pred,Y) > 0 AND
  beats the drug-marginal-mean baseline (Δ Spearman > 0), permutation/bootstrap p<0.05; and synergistic-class
  (Y>10) AUROC > 0.5 beyond baseline.
- H0: under LOCO, model ≈ drug-marginal baseline → synergy for novel combinations is not predictable from features
  (the "signal" is drug identity, not generalizable synergy).

## Decision rule & interpretation (fixed)
- **H2 PASS** → we can predict synergy for unseen combinations beyond drug-identity averages → a genuine, useful
  positive in a hard task (real forward progress for the discovery vision). Report effect size honestly.
- **H2 FAIL** (but H1 pass) → synergy prediction is largely drug-identity memorization; novel-combination synergy
  is not generalizably predictable from these features — an honest ceiling consistent with the program's theme
  (generalization is the wall). First-class negative.

## Honesty / scope
Cell-line synergy (not patient/clinical). 38 drugs / 39 cell lines is modest chemical+context diversity; LOCO is
the honest generalization probe within it. A null is fully expected and first-class. No clinical claim.

## Reproducibility
Deterministic (seed=42); reproduce ×2. Data provenance in results. Output:
experiments/B24_synergy_generalization/results/B24_metrics.json.
