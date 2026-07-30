# Pre-registration — B36: multi-outcome integration benchmark (does S+M beat S across many held-out outcomes?) (FINALIZED 2026-07-30, PRE-RESULT)

## Why (the power B35 lacked)
B35 showed feature-level fusion (S+M) beats structure (S) on ClinTox in a per-seed paired test (Δ+0.019, p=0.019)
but NOT under the conservative molecule-level bootstrap (p=0.30) — because ClinTox has only ~70 positives. The fix
is POWER: test S vs S+M across MANY held-out binary outcomes (several with hundreds of positives) and META-ANALYZE
the paired deltas. If the modules add real orthogonal signal, S+M>S should hold consistently across outcomes with a
combined CI excluding 0; if not, structure is sufficient across the board (decisive negative).

## Outcomes (9 held-out binary tasks; all DISTINCT from the module training endpoints)
Modules (M) are trained only on the B30 ADMET panel {herg, ames, dili, ld50, cyp3a4_veith, bioavailability, bbb,
ppbr, clearance_microsome, half_life} + B31 RAscore. Held-out outcomes (none is a module training target; TDC):
`clintox` (~70 pos), `skin_reaction` (274 pos), `carcinogens_lagunin` (60 pos), and 6 tox21 assays
{NR-AR, NR-AhR, NR-ER, SR-ARE, SR-MMP, SR-p53} (~100–500 pos each, ~7k molecules). Each outcome is leakage-controlled
(exclude molecules present in any module training set).

## Features / model (identical to B32b/B35)
S = Morgan2048 + physchem (2065-d); M = 12 module transfer features (10 ADMET-panel predicted values +
synth solvable_prob + SAscore); S+M = concat. SAME model class (HistGradientBoostingClassifier, seed=42) on S and S+M.

## Per-outcome analysis
Bemis–Murcko scaffold split, 5 seeds → per-seed paired ΔAUROC(S+M − S); report per-outcome mean Δ and a molecule-
level pooled out-of-fold bootstrap 95% CI (now better powered for the tox21 outcomes).

## Meta-analysis (the decisive test — unit = outcome)
Across the 9 outcome-level mean deltas: (a) one-sided **Wilcoxon signed-rank** (Δ>0); (b) fraction of outcomes with
Δ>0; (c) combined mean Δ with a **bootstrap 95% CI over outcomes**; (d) count of outcomes whose own molecule-level
bootstrap CI excludes 0.

## Hypotheses (assumed FALSE)
- **H1 (integration adds value robustly):** meta mean Δ > 0 AND Wilcoxon-across-outcomes p<0.05 AND ≥⅔ of outcomes
  Δ>0 AND combined bootstrap CI excludes 0.
- **H0:** meta Δ ≈ 0 / CI includes 0 → the modules do NOT reliably add over raw structure across outcomes →
  structure-sufficient is the decisive, well-powered conclusion (a first-class negative, closing the integration thread).

## Decision rule & interpretation (fixed)
- **H1 PASS** → feature-level integration is a VALIDATED, multi-outcome-robust (if small) platform benefit → report
  the pooled effect size honestly and enable a validated `fusion=True` mode in `DevelopabilityPrioritizer`.
- **H1 FAIL** → well-powered decisive negative: the ADMET/synth modules do not reliably augment raw structure for
  downstream outcome prediction → the platform's value is in the STANDALONE modules, not their late/feature fusion.

## Honesty / scope
Effect sizes are expected small; a positive meta-result means "modules add a small, real, orthogonal signal on top
of structure across diverse safety/tox outcomes," NOT a large advantage. Outcomes are in-vitro/curated tox/clinical
proxies; scaffold-split; no clinical claim.

## Reproducibility
Deterministic (seed=42; fixed CV seeds; module fits + bootstraps seeded). Reproduce ×2 byte-identical (payload
sha256). Output: `experiments/B36_integration_multioutcome/results/B36_metrics.json`.
