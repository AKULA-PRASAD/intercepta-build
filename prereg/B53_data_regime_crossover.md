# Pre-registration — B53: the data-regime crossover — when does structure-based information beat ligand-based? (FINALIZED 2026-07-30, PRE-RESULT)

## The scientific question (Phase 1)
Ligand-based virtual screening (QSAR / similarity) needs known actives; structure-based docking needs only the
receptor (it is **independent of how many actives you have**). The field agrees the two are complementary and that,
*averaged over targets*, ligand-based ≥ docking — but the **quantitative threshold** at which structure-based
information becomes competitive as known actives grow scarce is, by our literature review, **not addressed in the
published literature** (confirmed across multiple 2024–2025 reviews; the only nearby claim is that ligand-based *may*
stay competitive even at low N via consensus fingerprints). B48 showed orthogonal docking does not help *when the QSAR
is strong*; it never tested the scarce regime. B53 draws the curve: **as the number of known actives N shrinks, is
there a crossover N\* below which docking matches/beats the best ligand-based method — or does ligand-based dominate
down to a handful of actives?** This matters to any practitioner deciding where to spend effort for a
data-poor target, and would remain true if INTERCEPTA disappeared.

## Falsification (Phase 1) — pre-committed
- **H1 (a crossover exists):** on ≥2 of 3 targets, docking AUROC ≥ best-ligand AUROC at N=5 AND best-ligand climbs
  strictly above docking by N=160 → a crossover N\* lies in (5,160). (Structure-based earns its keep when data is scarce.)
- **H0 (ligand dominates even when scarce):** best-ligand AUROC(N=5) ≥ docking AUROC on all 3 targets (no crossover;
  the competing hypothesis — equally publishable, reported as first-class).
- **H2 (fusion in the scarce regime, the regime B48 skipped):** below N\*, a leakage-free rank fusion of
  {QSAR, similarity, docking} beats the best single channel.

## Data (OPEN; already local) — Phase 10 controls
3 LIT-PCBA targets with co-crystal receptors AND enough actives to sweep N + hold out a test set: **FEN1, MAPK1, VDR**.
Per target: **scaffold-aware split** — 20% of Bemis–Murcko scaffolds → held-out TEST (novel-chemistry lens; test
actives are scaffold-distinct from all training actives), the rest → train-pool. Fixed **test set = 50 actives (from
test scaffolds) + 100 seeded decoys**. Sweep **N ∈ {5,10,20,40,80,160}** training actives sampled from the train-pool,
with a **fixed 2,000 training inactives** (so only #actives varies). 5 seeds per N.

## Method (deterministic; env `docking`: rdkit + openbabel + AutoDock Vina 1.2.7)
Three channels scored on the SAME fixed test set (AUROC via rdkit.ML.Scoring):
1. **Ligand-QSAR(N):** HistGradientBoosting on Morgan-1024, trained on N actives + 2,000 inactives → predict test.
2. **Ligand-similarity(N):** max ECFP4 Tanimoto of each test molecule to the N training actives (no training) —
   the fair low-N ligand baseline (the competing-hypothesis method).
3. **Docking (N-INDEPENDENT):** AutoDock Vina (seed=42, cpu=8, exhaustiveness 8) score = −affinity on the test set;
   receptor = LIT-PCBA co-crystal (obabel mol2→pdbqt -xr), box = co-crystal centroid 22³; ligand prep SMILES→ETKDGv3
   (seed)→MMFF→obabel pdbqt. **Docked once per target → a flat line across N.**
Per N: best-ligand = max(QSAR, similarity); rank-fusion = mean percentile-rank of the 3 channels. Crossover
**N\* = smallest N where best-ligand AUROC ≥ docking AUROC**.

## Metrics & aggregate (Phase 12)
Per target: docking AUROC (constant), and QSAR/similarity/best-ligand/fusion AUROC as functions of N (mean±sd over 5
seeds); crossover N\*. Aggregate: how many targets show a crossover; the honest curves.

## Honesty / scope
Retrospective, in-silico, real LIT-PCBA labels, scaffold-controlled (novel-chemistry) test set. Docking is a heuristic
score (rigid receptor, obabel Gasteiger prep) — B53 measures docking AS-CONFIGURED, not docking's ceiling; a stronger
docking protocol could shift N\*. 3 targets, small test set (AUROC is the metric). Enrichment ≠ proven activity; not
wet-lab; no SOTA claim. H0 (no crossover) is an expected-allowed, first-class outcome.

## Reproducibility
Deterministic: scaffold split seed=42, N-subsample seeds [1..5], fixed inactive sample seed=42, Vina seed=42/cpu=8
(byte-deterministic, verified B47), RDKit ETKDG seed. Reproduce ×2 byte-identical (payload sha256 over summary+per
target). Output: `experiments/B53_data_regime_crossover/results/B53_metrics.json`. Env: `docking`; INTERCEPTA_DATA owned.
