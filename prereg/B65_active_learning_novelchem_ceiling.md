# B65 — Does active learning's label-efficiency advantage COLLAPSE in the novel-chemistry regime? (finalized 2026-07-31, PRE-RESULT)

## Phase-0 provenance (why THIS experiment, and why not the obvious one)
A deep literature sweep (3 parallel research threads) established: (1) "active learning / iterative screening beats random
for hit-finding" is **solved/canonical** (Reker & Schneider 2015; Deep Docking 2021; prospective industrial iterative
screening recovering 43% of actives from 5.9% of a 2M library) — **reproducing it is worthless**; (2) the genuinely OPEN,
high-value question is whether AL's advantage **survives in the novel-chemistry / OOD regime** — the only prior art
(a 2026 OOD-AL paper) is on solvation *energy* (signal-rich physics), one acquisition function, modest effect; **nobody
has quantified it for potency/hit-finding in the low-Tanimoto (<0.4) regime where WE showed an information ceiling**
(B60–B62). This experiment is the discriminating test that our own theory uniquely motivates.

## The theory this tests (disposable, as always)
P4 says acquisition dominates combination (data > modeling). P9/B62 say novel-chemistry potency error is **signal-loss /
regression-to-the-mean**, NOT a calibration bug, and applicability-domain distance does not predict it (B61). AL
acquisition (uncertainty or greedy) is *driven by the model's own predictions/uncertainty* — which B61/B62 showed are
**uninformative on novel chemistry**. **Sharp falsifiable prediction:** AL should densify signal-rich near-training
chemistry and its advantage over random should **vanish when performance is measured specifically on novel-chemistry
test compounds** — you cannot acquire your way past a signal-loss barrier. If instead AL's advantage SURVIVES on novel
chemistry, that overturns the pessimistic reading and reveals a cheap path to novel chemistry — either outcome is decisive.

## Hypothesis space (enumerated → eliminated → selected)
Mechanisms by which AL could relate to novel-chemistry generalization:
- (M1) **AL builds a better model everywhere** (advantage uniform across in-domain AND novel test) — would contradict B62.
- (M2) **AL advantage is a near-domain phenomenon** — real for interpolation, ~0 for novel-chemistry extrapolation
  (our prediction, from P9/B62). ← selected as H2.
- (M3) **AL is actively WORSE than random on novel chemistry** (acquisition biases the training set toward a narrow
  region, hurting extrapolation) — a stronger negative; tested as a signed contrast.
- (M4) AL advantage depends entirely on acquisition function (uncertainty vs greedy) — controlled by running BOTH.
- (M5) Effect is a class-balance/threshold artifact — controlled by using continuous potency + rank metrics (Spearman),
  not a fixed active threshold.
Rejected as low-information: re-testing M1 alone (known); testing greedy-only hit-count curves (reproduction). Selected:
the **domain-stratified** learning-curve contrast (in-domain vs novel) with a mechanism probe (M2 vs M3), both acquisition
functions, mechanistically tied to the information ceiling.

## Data (OPEN; MoleculeACE, cached — SAME targets/pipeline as B60–B62 for continuity)
Per target: continuous potency (pKi/pIC50), Morgan-1024. **Scaffold-disjoint split:** TEST_novel = held-out
Bemis–Murcko scaffolds further restricted to NN-Tanimoto<0.40 vs the acquisition pool (the extrapolation test);
TEST_indomain = a random held-out subset from the pool's scaffold space (interpolation test); POOL = the remainder
(the acquirable set, labels hidden except a seed). Targets with <15 TEST_novel compounds skipped (the B55 lesson).

## Design (simulated pool-based active learning)
- Model: **ensemble of HGB regressors** (query-by-committee); per-compound uncertainty = std across the committee.
- Loop: seed n0 labeled (random, seeded) → each round retrain ensemble → acquire batch b from POOL by
  **(a) uncertainty sampling** (max committee-std) and, as a separate arm, **(b) greedy** (max predicted potency) →
  reveal labels → repeat to a fixed label budget. Baseline: **random** acquisition of the same batch sizes.
- Evaluate every round: Spearman(pred,true) on TEST_novel AND TEST_indomain.
- 3 seeds; panel = median over targets. FIRST-TARGET TIMING CHECKED before full run (B63 lesson — no blind long runs).

## Metrics (per target, mean over seeds)
- **Learning-curve AUC** (area under Spearman-vs-#labels) for {AL-uncertainty, AL-greedy, random} on each test set.
- **advantage_indomain** = AUC(AL) − AUC(random) on TEST_indomain; **advantage_novel** = same on TEST_novel.
- **labels-to-target**: #labels for AL vs random to reach Spearman 0.5 (in-domain) — efficiency gain.
- **acquired_novelty** (mechanism M2/M3): mean NN-Tanimoto of AL-acquired vs random-acquired compounds to the current
  labeled set (higher = more densification of known chemistry).

## Hypotheses (pre-registered)
- **H1 (sanity/reproduction):** panel-median **advantage_indomain > 0** (AL beats random for interpolation) — confirms
  the canonical result and that our AL is implemented correctly.
- **H2 (KEY — collapse on novel chemistry):** panel-median **advantage_novel ≈ 0** and **advantage_novel <
  advantage_indomain** by a clear margin (report the paired difference + sign test across targets) → AL's efficiency
  gain is a near-domain phenomenon; acquisition cannot buy novel-chemistry generalization (consistent with P9/B62).
- **H3 (mechanism):** AL-acquired compounds have **higher mean similarity to the labeled set than random-acquired**
  (densification) → explains H2.
- **H0 / alternative (hopeful, first-class):** panel-median **advantage_novel > 0** at a meaningful margin → AL DOES
  improve novel-chemistry generalization → a cheap path to novelty; would REVISE the pessimistic P9/B62 reading.

## Honesty / scope
Retrospective, in-silico, MoleculeACE (ChEMBL medchem), simulated AL on a fixed pool (an optimistic upper bound vs real
prospective synthesis). Ensemble-std is one uncertainty proxy (uncertainty + greedy both run; not exhaustive). "Novel"
= NN<0.4 + scaffold-disjoint (our standard). Basic AL-beats-random is known — the novelty is strictly the
**domain-stratified collapse** and its mechanistic tie to the information ceiling. n≈15–24 targets; correlation≠causation;
not wet-lab.

## Reproducibility
Deterministic (split seeds, seed-set seed, ensemble seeds, acquisition ties broken by index). Reproduce ×2 byte-identical
(payload sha256 over summary + per-target). Output: `experiments/B65_active_learning_novelchem_ceiling/results/B65_metrics.json`.
Env: intercepta-build; INTERCEPTA_DATA owned.
