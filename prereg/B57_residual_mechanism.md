# Pre-registration — B57: what explains the target-dependent irreducible VS residual? (FINALIZED 2026-07-31, PRE-RESULT)

## Scientific question (Phase 1)
B54/B56 established that after removing BOTH analog and decoy bias, a small **irreducible binding signal** (the
doubly-controlled cell A1B1) remains — but it is strongly target-dependent (≈chance for HIV/ALDH1/KAT2A ~0.57–0.58;
strong for FEN1 0.80, STK33 0.77). **What determines this?** If we can predict *which targets retain real ligand-based
signal*, P2/P6 turn from "how much enrichment is bias" into a decision rule: *when is ligand-based VS trustworthy?*

## First principles + literature (Phase 2–3)
The residual is "how much of activity is a smooth, learnable function of 2D structure after both biases are removed."
That is exactly **SAR ruggedness / activity-cliff density**: rugged landscapes (many similar molecules with opposite
activity) defeat similarity-based / descriptor QSAR (van Tilborg MoleculeACE 2022; SAR-tolerance & landscape-roughness
literature). The novel connection B57 tests: does **activity-cliff density predict the DOUBLY-DEBIASED residual across
targets?** (Prior work links cliffs to QSAR failure generally, not to the post-debiasing irreducible signal.)

## Data (OPEN; reuses committed, reproduced A1B1 residuals + structural features)
The **13 targets** with an already-reproduced A1B1 residual under identical methodology: B54 (LIT-PCBA:
ALDH1, VDR, PKM2, FEN1, MAPK1, GBA, KAT2A, ESR1_ant) + B56 (TDC HTS: hiv, m1_muscarinic, orexin1, kir2.1, stk33).
Residual read from the committed `B54_metrics.json` / `B56_metrics.json` `per_target[...]["cells"]["A1B1"]`. Structural
predictors computed fresh from the same cached actives/inactives (Morgan r2 1024).

## Predictors (target-level, deterministic)
1. **activity_cliff_density** (the hypothesis): fraction of actives whose nearest **inactive** (Tanimoto, vs a seeded
   2,000-inactive sample) ≥ 0.40 — i.e. actives sitting next to structurally-similar inactives (a locally rugged
   active/inactive boundary). High ⇒ rugged ⇒ predicted LOW residual.
2. **active_diversity**: mean pairwise Tanimoto among a seeded ≤300-active sample (higher sim = tighter cluster).
3. **n_actives** (data richness).
4. **assay_type_phenotypic**: 1 for cell/phenotypic endpoints (hiv), else 0 (biochemical). (Weak — only hiv is
   phenotypic in the set; reported but underpowered.)

## Analysis (Phase 9)
Spearman correlation of each predictor with the residual across the 13 targets; rank predictors by |Spearman|.

## Hypotheses (pre-registered)
- **H1 (activity-cliff mechanism):** activity_cliff_density is the **strongest** correlate of the residual AND its sign
  is **negative** (Spearman ≤ −0.5). ⇒ SAR ruggedness explains when the ligand-based signal survives debiasing.
- **H0 / competing:** another predictor (active_diversity / n_actives / assay_type) is the strongest, or no predictor
  reaches |Spearman| ≥ 0.5 (residual not explained by these target properties — a first-class null, honestly reported).
- **Reported regardless:** all four Spearman correlations + the per-target residual/predictor table.

## Honesty / scope
Retrospective, in-silico, **meta-analysis across only n=13 targets** — small; a strong effect (|r|≳0.55, p<0.05) is
detectable but I will report effect sizes + ranks, NOT lean on p-values, and state the power limit. Activity-cliff
density is one operationalization (Tanimoto-threshold); results may depend on the threshold (a documented caveat).
Correlation ≠ causation across targets (confounds: assay quality, active-count). Enrichment ≠ proven activity; not
wet-lab.

## Reproducibility
Deterministic: seeded inactive/active samples (seed=42), residuals are fixed committed values, Spearman deterministic.
Reproduce ×2 byte-identical (payload sha256 over summary+per-target). Output:
`experiments/B57_residual_mechanism/results/B57_metrics.json`. Env: intercepta-build; INTERCEPTA_DATA owned.
