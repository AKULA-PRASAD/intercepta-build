# Pre-registration — B41: applicability-domain-constrained Pareto multi-objective discovery (FINALIZED 2026-07-30, PRE-RESULT)

## Why (fix the two honest problems B40 surfaced, with literature-grounded methods)
B40 target-conditioned generation worked (steered HIV-activity 3.96×) but (a) used a **scalar-product** objective —
which the MOO literature shows is dominated by Pareto non-dominated sorting (Fromer & Coley 2022) — and (b) drifted
partly OUT of the applicability domain (only 63% in-domain), so its "safety drop" (0.80→0.43) is confounded with
**reward hacking**: optimizers exploiting QSAR blind spots where predictions are unreliable (Nat Commun 2025). B41
applies the correct methods: **NSGA-II Pareto selection + an applicability-domain reliability constraint**, and asks
whether the activity↔safety trade-off is real or partly an OOD artifact.

## Method (deterministic, reused validated modules)
Generator: BRICS fragment recombination (B33). Objectives (kept SEPARATE, all higher=better):
`P(HIV-active | QSAR-B40)`, `safety = 1 − mean P_tox(herg,ames,dili)`, `QED`, `synth = (10−SA)/9`.
- **Arm A (baseline ≈ B40):** scalar product objective, unconstrained (elitist scalar GA).
- **Arm B (Pareto):** NSGA-II selection — fast non-dominated sorting + crowding distance on the 4 objectives.
- **Arm C (Pareto + AD-constrained):** as B, but candidates are gated to the RELIABLE region — in the Tanimoto
  applicability domain of BOTH the QSAR and the ADMET models (out-of-domain candidates are infeasible / down-ranked),
  per the reliable-design framework that mitigates reward hacking.
New `ParetoOptimizer` in `intercepta.generate` (leaves the scalar `MoleculeOptimizer` untouched ⇒ B33/B39/B40
reproduce). Same ChEMBL seeds, seed=42, pop/generations as B40.

## Metrics
Per arm: **dominated hypervolume** (standard MOO metric, ref point = origin), Pareto-front size, mean & max of each
objective, **in-domain fraction**, and the **best balanced candidate** (highest min(activity, safety) among
in-domain non-dominated points). Validity/uniqueness/novelty.

## Hypotheses (assumed FALSE)
- **H1 (reliability):** arm C's in-domain fraction is much higher than arm A's (B40 ≈ 63%) → the AD constraint yields
  candidates whose activity/safety predictions are reliable (reward-hacking mitigated).
- **H2 (balance):** Pareto (B/C) yields candidates that are simultaneously active AND safe — a non-dominated point
  with both P(active) and safety above the seed medians — which the scalar arm A collapses away from.
- **H3 (trade-off re-examined, honest):** quantify the activity↔safety relationship WITHIN the reliable (in-domain)
  set of arm C vs arm A's unconstrained set — report whether the trade-off shrinks (partly OOD artifact) or persists
  (real). Effect size reported; no forced sign.
- **H4 (Pareto ≥ scalar):** arm B/C hypervolume ≥ arm A hypervolume (Pareto recovers a better/wider frontier).

## Decision rule & interpretation (fixed)
- **H1 ∧ H2 ∧ H4 pass** → AD-constrained Pareto discovery is a genuine improvement: it produces reliable,
  well-balanced (active AND safe) candidates and a better frontier → ship it (`intercepta discover --pareto`), and
  report H3's honest quantification of the (reliable) trade-off.
- Otherwise → report which failed honestly (e.g. Pareto no better than scalar here; or AD constraint too strict).

## Honesty / scope
Activity/safety/synth are all in-silico PREDICTIONS (QSAR + ADMET + SAscore); the AD constraint improves reliability
but does not make them ground truth. Candidates are hypotheses over KNOWN chemistry; NOT validated actives, novel, or
safe drugs; no wet-lab/clinical claim. Hypervolume/frontier are computational MOO metrics, not experimental outcomes.

## Reproducibility
Deterministic (seed=42; module + QSAR fits + GA + NSGA-II selection seeded). Reproduce ×2 byte-identical (payload
sha256). Output: `experiments/B41_pareto_reliable_discovery/results/B41_metrics.json`.
