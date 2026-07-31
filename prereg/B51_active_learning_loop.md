# Pre-registration — B51: closed-loop in-silico DMTA / active-learning engine (FINALIZED 2026-07-30, PRE-RESULT)

## Why (the flagship — the one lever left after B48/B49)
B48 proved you cannot COMBINE fixed scores past the ceiling; B49 proved you cannot REPRESENT (protein embeddings) past
it. The remaining lever is **changing WHICH data you acquire** — the closed Design–Make–Test–Analyze (DMTA) loop with
model-guided batch selection. This turns INTERCEPTA from a static toolbox into an *engine*, and it is the truest
in-silico miniature of the fullest-vision workflow. B51 simulates the loop against a real-bioactivity oracle (labels
hidden, revealed only when "tested") and asks: does model-guided, uncertainty-aware selection discover real actives in
far fewer "assays" than random — and how do exploit (greedy) vs explore (uncertainty) vs hybrid (UCB) trade off?
Literature: model-guided AL finds ~90–95% of top ligands testing ~2% of a library; UCB/hybrid ≳ greedy for recall;
uncertainty best for model generalization (arXiv/JCIM 2024–2026).

## Data (OPEN; LIT-PCBA, cached) — the hidden oracle
3 targets with enough actives: **FEN1, MAPK1, ALDH1**. Per target the oracle pool = **300 actives (capped) + 10,000
seeded inactives** (random_state=42) → realistic ~2.9% hit rate. Labels are HIDDEN; the oracle reveals a label only
when the loop selects ("tests") that compound. Ligand features = Morgan r2, 1024-bit.

## Method (deterministic; env intercepta-build)
Pool-based active learning. Initialise with a **seeded random labelled batch of 100**. Each of **15 rounds**: train a
`HistGradientBoostingClassifier` (seed=42) on the labelled set → predict P(active) on the unlabelled pool → an
**acquisition function** selects the next **batch of 100** → the oracle reveals their labels → add to labelled set.
Total tested = 100 + 15×100 = **1,600** (~15% of pool). Four acquisition strategies compared under identical seeds:
1. **random** (baseline).
2. **greedy / exploit** — highest predicted P(active).
3. **uncertainty / explore** — highest entropy (closest to 0.5, i.e. max p(1−p)).
4. **UCB / hybrid** — highest `P + κ·sqrt(P(1−P))`, κ=1.0 (exploit + explore).
Run over **3 AL seeds** (initial batch + random-strategy draws). Track, per round: cumulative actives found vs # tested
(the hit-discovery curve), and the end-of-run model AUROC on the still-**untested** pool (generalisation).

## Metrics & aggregate
Per target×seed×strategy: actives found at budget **800** and **1600**; enrichment = strategy_actives / random_actives
at each budget; end-model AUROC on untested pool. Aggregate = mean over targets×seeds.

## Hypotheses (pre-registered)
- **H1 (the loop works):** the best model-guided strategy recovers **≥ 2× more actives than random** at budget 1600
  (closed-loop discovery adds real value). If FALSE → model-guided AL gives no advantage here (first-class negative).
- **H2 (exploit vs explore for RECALL):** for actives-found at 1600, **UCB ≥ greedy ≥ uncertainty** (hybrid/exploit win
  pure recall; pure exploration pays a recall cost). Report the ordering honestly.
- **H3 (explore helps GENERALISATION):** end-of-run model AUROC on the untested pool is **higher for uncertainty than
  for greedy** (exploration builds a better model; exploitation is myopic). Report the tradeoff.

## Honesty / scope
Retrospective simulation on real labels (not a live assay) — an in-silico DMTA proxy, not prospective/wet-lab. Pool is
subsampled (documented). Uncertainty is a single-model entropy proxy (not full Bayesian/committee). 3 targets. A NULL
H1 is expected-allowed and reported first-class. Finding actives fast ≠ finding a drug; enrichment ≠ proven activity.

## Reproducibility
Deterministic: pool subsample seed=42, AL seeds [1,2,3] fixed, model seed=42, deterministic tie-breaking (by index).
Reproduce ×2 byte-identical (payload sha256 over summary+per-target). Output:
`experiments/B51_active_learning_loop/results/B51_metrics.json`. Env: intercepta-build; INTERCEPTA_DATA owned path.
