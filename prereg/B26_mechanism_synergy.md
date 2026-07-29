# Pre-registration — B26: mechanism-anchored synergy — do TARGET-DEPENDENCY features generalize to NOVEL drugs where chemistry fails? (FINALIZED 2026-07-29, PRE-RESULT)

## The hypothesis (novel; ours, from V22 + B25)
V22: a drug's *own target dependency* is the only real generalizable functional signal. B25: generic chemical
fingerprints fail to generalize synergy to **novel drugs** (leave-drug-out ρ collapsed 0.25→0.025). Mechanistic
idea: encode each drug by its **target's CRISPR gene-dependency** in the cell line — a low-dimensional,
biology-grounded representation that is DEFINED even for a drug the model never saw (we look up the target's
dependency in DepMap, external to the synergy labels — no leakage). Biological rationale: a pair is synergistic when
the cell is **co-dependent on both drugs' targets** (hitting two needed vulnerabilities is more-than-additively
lethal). Decisive test: do mechanism features **generalize to novel drugs better than chemical fingerprints**?

## Data (OPEN + LOCAL; no collaboration)
- Synergy: O'Neil/OncoPolyPharmacology (TDC), Loewe; cleanest single-study labels. 33 cell lines mapped to DepMap
  CRISPR; drugs restricted to those with a curated target gene present in DepMap (targeted + enzyme-directed
  agents; pure DNA-alkylators/antimetabolites without a clean gene target are excluded — stated a priori).
- Mechanism features from DepMap CRISPR gene-effect (Chronos) of the targets; cell context from DepMap expression
  PCA (≤20 comps). Drug→target map curated from established pharmacology (committed in the run script).

## Feature sets (identical CV/splits; only features change)
- **FP (baseline, = B24/B25):** order-invariant Morgan fingerprints (sum + bitwise-AND) + cell-expression PCA.
- **MECH (novel):** for each drug, target-dependency = min CRISPR gene-effect over its target genes in that cell
  (strongest dependency). Features = [dep1, dep2, dep1·dep2, dep1+dep2, |dep1−dep2|, min, max, and cross-cell
  co-dependency corr(t1,t2)] + cell-expression PCA.
- **FP+MECH:** concatenation.
Model: HistGradientBoostingRegressor, deterministic seed=42.

## Splits & hypotheses (assumed FALSE)
- Leave-drug-COMBINATION-out (grouped by pair) and **leave-DRUG-out** (both drugs of a test pair held out).
- **H_mech (the novel claim):** under LEAVE-DRUG-OUT, MECH Spearman ρ(pred,Loewe) **> FP** Spearman AND MECH ρ>0
  (bootstrap CI excludes 0) — target-dependency features generalize to novel drugs where fingerprints fail.
- **H_add:** FP+MECH > FP on leave-combination-out (mechanism adds beyond chemistry).
- **H_sanity:** MECH beats a cell-only (no-drug-feature) baseline.
- H0: MECH ≤ FP for novel drugs and adds nothing → the co-dependency hypothesis does not yield transferable
  synergy signal (honest negative).

## Decision rule & interpretation (fixed)
- **H_mech PASS** → mechanism-anchoring is a genuine, novel advance: biology-grounded target-dependency features
  transfer to novel drugs (with known targets) where chemistry cannot → a real, useful, mechanistic contribution
  (not a benchmark reproduction). Report effect size honestly.
- **H_mech FAIL** → honest: target co-dependency does not encode transferable synergy beyond chemistry; novel-drug
  synergy remains hard. First-class negative; the combination-of-known-drugs capability (V23) still stands.

## Honesty / scope
Cell-line Loewe synergy (not clinical). Restricted to targeted/enzyme-directed drugs with a curated target in
DepMap (mechanism-anchoring is FOR such drugs — chemo alkylators are out of scope by design). Curated target map
is committed and inspectable. A null is fully expected and first-class.

## Reproducibility
Deterministic (seed=42); reproduce ×2. Output: experiments/B26_mechanism_synergy/results/B26_metrics.json.
