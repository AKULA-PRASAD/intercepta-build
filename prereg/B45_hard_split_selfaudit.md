# Pre-registration — B45: honest self-audit of our enrichment under a leakage-controlled hard split (FINALIZED 2026-07-30, PRE-RESULT)

## Why (turn the rigor on ourselves; "bar before boast")
Our validated retrospective enrichment (B42 HIV, B43 6-target panel) used **Bemis–Murcko scaffold splits**. Recent
work shows scaffold splits **overestimate** virtual-screening performance because train/test still share high 2D
similarity (analogs, near-duplicate scaffolds), letting models win by memorization rather than generalization
(Li et al., "Scaffold Splits Overestimate Virtual Screening Performance", arXiv:2406.00873; and documented leakage in
community benchmarks, arXiv:2507.21404). Before we build ANY new module on top of these numbers, we must know how much
of our reported EF/AUROC is real generalization vs split-induced optimism. B45 re-evaluates the SAME targets under a
harder, similarity-controlled split and reports the honest degradation — no new data, no installs.

## Data (OPEN; already local; identical to B42/B43)
The B43 panel (TDC HTS single-target): `hiv`, `m1_muscarinic_receptor_antagonists_butkiewicz`,
`orexin1_receptor_butkiewicz`, `potassium_ion_channel_kir2.1_butkiewicz`, `serine_threonine_kinase_33_butkiewicz`,
`sarscov2_3clpro_diamond`. Per target: all actives + a seeded inactive subsample (≤6,000; random_state=42) — same
construction as B43 so the ONLY changed variable is the split.

## Method (identical model + metrics to B43; the split is the treatment)
For each target, featurize (Morgan2048+physchem). Train `admet._TaskModel` (roc-auc), score held-out test, compute
**AUROC, BEDROC(α=80.5), EF@1%, EF@5%** (rdkit.ML.Scoring), mean over 3 seeds — under TWO split regimes:
1. **Scaffold split** (Bemis–Murcko, our prior B43 protocol) — reproduces the optimistic baseline.
2. **Cluster split (leave-cluster-out)** — Butina clustering on Morgan Tanimoto distance (cutoff 0.65 → distance 0.35),
   assign whole clusters to the ~20% test fold (seeded), so train/test compounds are dissimilar. Actives required in
   both partitions (else skip seed). This controls train↔test similarity leakage.
Plus a **2D near-duplicate audit**: report, for each split, the distribution of each test compound's MAX Tanimoto to
any train compound (mean + fraction with NN-Tanimoto > 0.4). The cluster split must show materially LOWER cross-set
similarity — this PROVES the stressor is genuinely harder (not just a relabeling).

## Metrics & aggregate
Per target & split: AUROC, BEDROC, EF@1%, EF@5%, mean/frac(>0.4) cross-set NN-Tanimoto. Panel: mean AUROC/BEDROC/EF
under each split, and the **degradation Δ = scaffold − cluster** per metric.

## Hypotheses (pre-registered)
- **H1 (capability is real, not memorization):** under the HARDER cluster split, the panel still shows meaningful
  enrichment — panel-mean AUROC > 0.70 AND ≥4/6 targets keep EF@1% > 3. (If TRUE, our enrichment is robust to the
  split critique; if FALSE, our prior numbers were substantially split-inflated — reported honestly either way.)
- **H2 (the stressor is valid):** the cluster split has materially lower cross-set NN-Tanimoto than the scaffold split
  (mean Δ ≥ 0.05), confirming train/test are more dissimilar (the split is genuinely harder).
- **Reported regardless:** the magnitude of EF/AUROC degradation scaffold→cluster (the honest "optimism tax").

## Honesty / scope
Retrospective, in-silico, real-actives-vs-decoys. This is a self-critique experiment: the expected/allowed outcome
includes our own numbers dropping. No spin — we report the degraded numbers as the honest operating estimate going
forward. Butina cutoff fixed a priori (0.65 similarity); not tuned to a result. Decoys not property-matched (same
caveat as B43). Enrichment ≠ proven activity; not wet-lab.

## Reproducibility
Deterministic: seed=42 (model + inactive subsample), split seeds fixed [1,2,3], Butina deterministic given distances.
Reproduce ×2 byte-identical (payload sha256 over summary+per-target). Output:
`experiments/B45_hard_split_selfaudit/results/B45_metrics.json`. Env: intercepta-build; INTERCEPTA_DATA owned path.

---

## AMENDMENT (2026-07-30, after RUN_A — transparent redesign; original design above left intact as the record)
**Why amended:** RUN_A's pre-registered VALIDITY check **H2 FAILED**. The Butina cluster split (0.65-similarity cutoff)
did **not** produce a materially harder split: cross-set nearest-neighbor Tanimoto was 0.428 (cluster) vs 0.425
(scaffold) — reduction −0.003, i.e. *not harder*. On these dense HTS libraries, leave-cluster-out at that cutoff still
leaves ~0.43 mean train↔test similarity, so H1 ("enrichment survives a harder split") was **untestable** as run —
committing the "survives" verdict would itself be the split-inflation artifact B45 exists to expose. Rather than tune
the cutoff (which risks tuning-to-outcome), I switch to a **direct, tuning-free** design, fixed BEFORE its own run:

**New method (NN-similarity-stratified enrichment).** Keep the Bemis–Murcko scaffold split ×3 (same model/features).
For each seed's test set, compute every test compound's **max Tanimoto to any training compound (cross-set NN)**.
Stratify test compounds into similarity bands **[<0.3, 0.3–0.4, 0.4–0.5, ≥0.5]** (pooled across the 3 seeds per
target). Within each band with n_total≥20 and n_actives≥5, compute **AUROC and EF@5%** (actives-vs-decoys ranking
inside the band; EF@1% omitted per-band as bands are small). Report per target and panel, per band. This measures
directly whether the model separates **genuinely-novel actives (NN<0.4)** from novel decoys — the real robustness
question — without engineering (or tuning) a hard split.

**New hypotheses (fixed pre-run of the amended analysis):**
- **H1' (capability is real on novel chemistry):** on the pooled **NN<0.4** test compounds, panel-mean AUROC > 0.65
  AND ≥4/6 targets have band AUROC > 0.65. (Robust to the split critique if TRUE.)
- **H2' (a genuine similarity gradient exists to test):** the panel shows a monotone-ish drop in AUROC from the ≥0.5
  band to the <0.3 band (mean AUROC[≥0.5] − AUROC[<0.3] ≥ 0.03), confirming performance does depend on train↔test
  similarity (i.e. there IS optimism to quantify). Report the magnitude regardless.
- **Reported regardless:** per-band AUROC/EF@5% and n_actives — the honest performance-vs-novelty curve.

Output unchanged path; reproduce ×2 byte-identical.
