# Pre-registration — B60: does continuous-potency landscape roughness predict novel-chemistry generalization? (FINALIZED 2026-07-31, PRE-RESULT)

## Why (the honest instrument for P7)
B58 found SAR-landscape roughness weakly predicts the doubly-debiased VS residual (ROGI −0.42) — but that used a
**binary** active/inactive label, a noisy proxy for the true structure-**potency** landscape. B60 uses the right
instrument: **continuous potency (pKi/pIC50)** from MoleculeACE (van Tilborg 2022; 30 curated ChEMBL targets), measures
roughness properly (ROGI on real potency), and tests whether it predicts **novel-chemistry generalization** of a
ligand-based potency model. This (a) closes the residual-mechanism arc — is P7 real-but-attenuated (binary noise) or
genuinely weak with proper measurement? — and (b) asks a sharper, decision-relevant question the ROGI paper did not:
does roughness predict **extrapolation to dissimilar chemistry** (not just random-split interpolation)?

## Data (OPEN; MoleculeACE, cached $INTERCEPTA_DATA/moleculeace; MANIFEST)
30 ChEMBL targets; per compound: SMILES + continuous potency `y [pEC50/pKi]`. ~600–3,000 compounds each.

## Method (deterministic; env intercepta-build, RESTORED+verified)
Per target:
- **ROGI (continuous):** our validated reimplementation (1 − ∫SD(t)dt/SD(0), complete-linkage Tanimoto), on the real
  potency values over a seeded ≤500-compound sample. Higher = rougher structure–potency landscape.
- **Novel-chemistry generalization:** Morgan-1024 → HistGradientBoosting **regressor**; **Bemis–Murcko scaffold split**
  ×3; test restricted to **NN<0.40** compounds (novel chemistry vs train); metric = **Spearman(predicted, true potency)**
  on the novel test (mean over seeds). Higher = generalizes better to dissimilar chemistry.
- **Random-split generalization (comparison):** same regressor, random split ×3, Spearman on test (the ROGI-paper-style
  interpolation baseline).
- **cliff_fraction:** fraction of the target's compounds flagged as activity-cliff members (a comparison predictor).
Targets with <15 novel test compounds are reported and excluded (the B55 lesson, enforced).

## Analysis & hypotheses (Phase 9)
Spearman across targets of ROGI vs each generalization metric.
- **H1 (P7 confirmed with proper measurement):** Spearman(ROGI, **novel-chemistry** generalization) ≤ **−0.5** — rougher
  landscape ⇒ worse novel-chemistry generalization; STRONGER than B58's binary −0.42.
- **H2 (roughness matters more for extrapolation):** |Spearman(ROGI, novel)| > |Spearman(ROGI, random-split)|.
- **H0 / null:** |Spearman(ROGI, novel)| < 0.5 → even with continuous potency + n=30 power, roughness only weakly
  predicts novel-chemistry generalization → P7 is genuinely weak/multifactorial (a strong, first-class null).
- **Reported regardless:** both correlations, cliff_fraction correlation, per-target table.

## Honesty / scope
Retrospective, in-silico. ROGI reimplemented (validated, not bit-exact vs the reference package). n≈30 (good power;
|Spearman|≥0.36 significant). MoleculeACE targets are ChEMBL medchem series (may differ from HTS); NN<0.4 novelty may
leave few compounds for some (reported). The random-split arm partially reproduces the known ROGI↔modellability result;
the NOVEL-chemistry arm + the binary-vs-continuous comparison are the new contributions. Correlation ≠ causation. Not
wet-lab. A null is expected-allowed and first-class.

## Reproducibility
Deterministic: sample seed=42, split seeds [1,2,3], model seed=42, ROGI deterministic. Reproduce ×2 byte-identical
(payload sha256 over summary+per-target). Output: `experiments/B60_continuous_potency_roughness/results/B60_metrics.json`.
Env: intercepta-build; INTERCEPTA_DATA owned.
