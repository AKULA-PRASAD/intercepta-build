# Pre-registration — B35: does feature-level integration beat structure? (rigorous PAIRED test) (FINALIZED 2026-07-30, PRE-RESULT)

## Why (fixes the statistical test in B32b)
B32b found feature-level fusion S+M (AUROC 0.920) is the best model and beats raw structure S (0.906) by +0.013 with
lower variance, but did NOT clear a ">1 sd" bar. That bar was the WRONG test: it compared S+M's mean against the
UNPAIRED spread of S. S and S+M are evaluated on the SAME folds and are strongly correlated, so the correct test is
the PAIRED difference (S+M − S on the same test data), whose variance is much smaller. B35 re-adjudicates the
integration question with proper paired statistics — decisively, either way.

## Data / features (identical to B32/B32b; no new data)
Held-out ClinTox (clinical-tox failure), leakage-controlled (exclude ClinTox molecules in any module training set →
~1,039 leakage-free). Modules trained only on their own data. Feature sets: **S** = raw structure
(Morgan2048+physchem, 2065-d); **M** = 12 module transfer features (B30 ADMET panel preds + B31 solvable_prob + SA);
**S+M** = concat. SAME model class (HistGradientBoostingClassifier, seed=42) on S and S+M.

## Design (paired, higher power)
- **Repeated Bemis–Murcko scaffold CV**, **10 seeds**. For each seed: train S-model and S+M-model on the SAME train
  fold, predict the SAME test fold, record AUROC(S), AUROC(S+M), and the **paired delta = AUROC(S+M) − AUROC(S)**.
- **Pooled out-of-fold (OOF):** for one fixed partition, collect each molecule's OOF prediction under S and under
  S+M, and run **DeLong's test** for two correlated ROC curves (S+M vs S) → a proper p-value + CI on the same data.
- **Bootstrap:** 95% CI of the mean paired delta (resampling over the 10 seeds).

## Baselines / reference
Report AUROC(S), AUROC(S+M), AUROC(M) means; the best single module output; and the paired-delta distribution.

## Hypotheses (assumed FALSE)
- **H1 (integration is a real win — paired):** the 10 per-seed paired deltas are >0 in a clear majority AND their
  one-sided Wilcoxon signed-rank p<0.05 AND the bootstrap 95% CI of the mean delta excludes 0 AND DeLong p<0.05.
- **H0:** paired delta CI includes 0 / Wilcoxon NS → S+M ≈ S; raw structure is sufficient (decisive negative,
  integration adds no reliable value even at the feature level).

## Decision rule & interpretation (fixed)
- **H1 PASS** → feature-level integration is a VALIDATED (if SMALL) win: the external-data-trained ADMET/synth
  modules add real, orthogonal signal on top of raw structure. Report the effect size HONESTLY as small (~+0.01
  AUROC) — a statistically-real but modest platform benefit — and enable a validated `fusion=True` mode in
  `DevelopabilityPrioritizer`.
- **H0** → raw structure is sufficient for ClinTox; feature-level integration does not reliably help → the B32/B32b
  "not established" bound stands as a decisive negative on this outcome.

## Honesty / scope
Effect size governs the claim: even if significant, a ~+0.01 AUROC gain is SMALL and specific to ClinTox (single
outcome, ~103 positives, survivorship-confounded, scaffold-split). A significant paired result establishes "the
modules add a small real signal on top of structure," NOT "a large integration advantage." No clinical claim.

## Reproducibility
Deterministic (seed=42 for models; 10 fixed CV seeds; module fits + DeLong + bootstrap seeded). Reproduce ×2
byte-identical (payload sha256). Output: `experiments/B35_integration_paired/results/B35_metrics.json`.
