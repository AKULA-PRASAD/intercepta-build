# Pre-registration — B42: retrospective known-drug re-discovery validation (external truth) (FINALIZED 2026-07-30, PRE-RESULT)

## Why (the credibility-defining test the pipeline lacks)
Every prior "positive" (B39–B41) validated the pipeline against ITS OWN predictors (circular / reward-hackable).
B42 tests it against **external ground truth — real, known drugs/actives** — the single most important computational
validation short of wet-lab. Two complementary retrospective tests, both standard in the field:

## Arm 1 — Generative RE-DISCOVERY (GuacaMol-style; tests the generator's reach)
Can the BRICS goal-directed GA (B33 generator) **regenerate known drug molecules** it was not given? For each target
drug T in {Celecoxib, Troglitazone, Thiothixene} (the canonical GuacaMol rediscovery set), run the GA with
objective = **Tanimoto(ECFP4) similarity to T**, seeded from a 3,000-molecule ChEMBL sample with T (and exact
duplicates) EXCLUDED. Deterministic. Report per-target **max Tanimoto** achieved + mean of top candidates; baseline =
best Tanimoto in the seed pool.
- **H1 (rediscovery):** the GA reaches max Tanimoto to T well above the seed-pool baseline, and ≥0.40 (a close
  analog) for the majority of targets. (Honest expectation, pre-declared: pure fragment-recombination has LIMITED
  reach vs graph-crossover GAs — full rediscovery (≥0.9) may NOT be achieved; the max-similarity value is reported
  truthfully either way, characterizing the generator's real reach and its recombination limitation.)

## Arm 2 — Virtual-screening ENRICHMENT (tests the scoring on real actives vs decoys)
Does the target-activity QSAR rank **real held-out actives** above decoys, with early recognition? On HIV (TDC HTS),
Bemis–Murcko scaffold split: train the QSAR on train scaffolds, score the held-out test (real actives + inactives as
decoys), rank, and compute the standard retrospective-VS metrics (rdkit.ML.Scoring): **AUROC, BEDROC(α=80.5)
(early recognition), and Enrichment Factor EF@1% / EF@5%.** 5 scaffold seeds, mean±sd.
- **H2 (enrichment):** AUROC > 0.70 AND BEDROC(80.5) > 0.3 AND EF@1% > 3 — i.e. the pipeline enriches REAL actives
  early, not just at chance. Assumed FALSE.

## Baselines / honesty
Arm 1 baseline: max seed-pool Tanimoto (the GA must beat "pick the most-similar seed"). Arm 2 baseline: random
ranking (AUROC 0.5, EF 1, BEDROC ≈ fraction). External truth throughout — real drug structures (Arm 1) and real
measured actives (Arm 2), NOT model outputs. A weak result (generator can't reach real drugs; or scoring doesn't
enrich) is a decisive, first-class NEGATIVE and is reported as such.

## Decision rule & interpretation (fixed)
- **H1 ∧ H2 pass** → the pipeline genuinely recovers external truth: the scoring enriches real actives early AND the
  generator reaches real drug chemistry → the strongest computational-validation evidence to date (still not wet-lab).
- **Partial** → report exactly which holds; if the generator can't rediscover (Arm 1 fails) but scoring enriches
  (Arm 2 passes), that honestly bounds the generator's reach while validating the scorer — a useful, truthful split.

## Scope / honesty
Retrospective, in-silico, external-truth validation — NOT prospective and NOT wet-lab. Rediscovery similarity ≠
proof of activity; enrichment on one target (HIV) ≠ generality. ECFP4-Tanimoto and QSAR are the standard but
imperfect proxies. No clinical/efficacy claim.

## Reproducibility
Deterministic (seed=42; scaffold seeds fixed; GA seeded). Reproduce ×2 byte-identical (payload sha256). Output:
`experiments/B42_retrospective_rediscovery/results/B42_metrics.json`.
