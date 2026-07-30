# Pre-registration — B40: target/disease-conditioned candidate generation (FINALIZED 2026-07-30, PRE-RESULT)

## Why (aim the pipeline at a specific disease/target)
B39 generates *developable* candidates but with no disease target. The vision needs **target-conditioned** design:
steer generation toward molecules predicted ACTIVE against a chosen target/disease *and* developable. B40 does this
by (i) building and validating a QSAR activity model for a target, then (ii) conditioning the discovery GA on it, and
(iii) showing the conditioning genuinely steers candidates toward the target without collapsing developability.

## Target & data (OPEN)
**HIV replication inhibition** (MoleculeNet/TDC `HTS(name='hiv')`, 41,127 molecules, 1,443 active = 3.5%). A
recognized activity-prediction benchmark and a disease-relevant target. For tractability + balance, the QSAR trains
on ALL 1,443 actives + a seeded 10,000-inactive sample (~11.4k, ~12.5% active); recorded. sha/provenance in MANIFEST.

## Step 1 — build + VALIDATE the QSAR (must be a real activity predictor before conditioning on it)
Featurize (Morgan2048+physchem) → classification model (`admet._TaskModel`, metric roc-auc, with Tanimoto
applicability domain). **Validate on a Bemis–Murcko scaffold split (5 seeds): report AUROC/AUPRC vs trivial.** Gate:
the QSAR is used for conditioning only if scaffold AUROC > 0.65 (a meaningfully-real predictor); else B40 reports the
QSAR as too weak and does not claim conditioning.

## Step 2 — target-conditioned generation
BRICS goal-directed GA (`intercepta.generate`) with objective
`F_cond = developability(QED × synth × safety, B30/B31) × P(HIV-active | QSAR)` — all in [0,1]. Compared against the
UNCONDITIONED pipeline (B39 objective = developability only), same seeds/config/seed=42.

## Metrics & baselines
Per arm (conditioned, unconditioned) and the ChEMBL seed population: mean predicted P(HIV-active); mean developability
and components (QED, SA, safety); validity, uniqueness, novelty; and the fraction of top candidates inside BOTH the
QSAR and ADMET applicability domains (honest reliability).

## Hypotheses (assumed FALSE)
- **H0_QSAR (gate):** scaffold AUROC > 0.65 (the QSAR is a real HIV-activity predictor).
- **H1 (conditioning steers):** conditioned candidates' mean P(HIV-active) > unconditioned candidates' mean
  P(HIV-active) > seed-population mean — i.e. the target signal genuinely biases generation toward the target.
- **H2 (developability preserved):** conditioned candidates remain valid (1.0), novel, and synthesizable/safe
  (developability not collapsed to chase activity) — a multi-objective, not activity-at-all-costs.
- **H0:** conditioned ≈ unconditioned on P(HIV-active) → conditioning does not steer (first-class negative).

## Decision rule & interpretation (fixed)
- **H0_QSAR pass AND H1 AND H2** → target-conditioned generation works: the pipeline aims at a chosen target while
  staying developable → ship it (`intercepta discover --target ...`). Report effect size honestly.
- Otherwise → honest negative/partial (weak QSAR, or conditioning doesn't steer, or developability collapses).

## Honesty / scope (mandatory)
Activity is **QSAR-PREDICTED, not measured**; optimizing against a QSAR invites gaming (candidates may exploit its
blind spots) — reported via QSAR + ADMET applicability-domain flags. Candidates are computational HYPOTHESES over
KNOWN chemistry (fragment recombination), NOT validated actives, novel drugs, or safe/synthesizable-in-practice
molecules; no wet-lab, no clinical/efficacy claim.

## Reproducibility
Deterministic (seed=42; seeded subsample; module + QSAR fits + GA seeded). Reproduce ×2 byte-identical (payload
sha256). Output: `experiments/B40_target_conditioned_generation/results/B40_metrics.json`.
