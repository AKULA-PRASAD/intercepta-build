# AFFINITY1 — Independent Scientific Review

*Reconstructed from the repository (`results/scored.csv`, `results/AFFINITY1_stats.json`, `run.py`) and
verified from first principles with sklearn + an independent DeLong implementation. Last updated
2026-08-09. Companion: `LEAKAGE_AUDIT.md`.*

## 1. Independent verification of the statistics (all reproduce exactly)
Recomputed from `scored.csv` with `sklearn.roc_auc_score`; per-metric NaN-masking:

| Metric | Independent recompute | Committed | Match |
|---|---|---|---|
| Boltz affinity-value AUROC | 0.6001 | 0.6001 | ✓ |
| Boltz probability-head AUROC | 0.6818 | 0.6818 | ✓ |
| Docking (Vina) AUROC | 0.4590 | 0.4590 | ✓ |
| analog-actives vs inactives (prob) | 0.6847 | 0.6847 | ✓ |
| novel-actives vs inactives (prob) | 0.5157 | 0.5157 | ✓ |

`n_scored=551` (2 excluded: cmpd_0046, cmpd_0336, ligand >128 heavy atoms — the affinity module's hard
limit), 290 actives / 261 inactives, **5 novel actives**. **Independent DeLong** (prob vs docking,
n=529 both-defined): ΔAUC=0.240, **z=8.4, p≈0** — corroborates the bootstrap ΔAUC CI [0.085, 0.197],
p<1e-4. **The pipeline and statistics are trustworthy.**

## 2. Two corrections to earlier conclusions (including our own)
1. **Retract "the 0.68 is leakage-inflated interpolation; true zero-shot ≈ chance."** The leakage-signature
   test shows AUROC is roughly **flat** across chemical-similarity bins (0.60–0.68 across `nn_tan`;
   Spearman(nn_tan, prob | actives)=0.095). No steep similarity gradient → the score is **not** demonstrably
   "just recall." (See `LEAKAGE_AUDIT.md` for the bounded-unknown position.)
2. **Retract "novel split answered negative (≈ chance)."** With **n=5 novel actives**, the novel AUROC
   (0.52) is statistically meaningless. Honest status: **unpowered — no conclusion on novel chemotypes.**

## 3. Methodological weaknesses
- **Single target (thrombin).** No basis for any general claim about co-folding vs docking.
- **Docking baseline is sub-random (0.459 < 0.5).** A competent Vina on thrombin should not be
  anti-predictive; "beats docking" may partly be "beats a weak/broken baseline." The **absolute** claim
  (Boltz ≈0.68, moderate) is more trustworthy than the **relative** one until the baseline is audited or a
  competent baseline (Gnina/rescoring) is added.
- **Not zero-shot w.r.t. Boltz-2** (thrombin/ChEMBL in training) — see `LEAKAGE_AUDIT.md`.
- **n=5 novel actives** → the decisive novel-chemotype question is unanswerable here.
- **Single seed; ensemble collapsed to a point estimate** (affinity head emits value/_1/_2 — uncertainty discarded).
- 22 Vina failures (NaN) → the strict same-set comparison is on the common 529 (DeLong used 529).

## 4. Fact / inference / speculation
- **Fact:** all AUROCs reproduce; Boltz≫docking is significant (DeLong z=8.4 / bootstrap p<1e-4);
  exclusions are exactly the 2 heavy>128 ligands; similarity–AUROC relationship is flat here; Boltz-2
  trained on ChEMBL/BindingDB/PubChem; thrombin structure in PDB pre-cutoff.
- **Inference (strong):** thrombin + ligands in Boltz training → not zero-shot.
- **Speculation (do not assert):** magnitude of any memorization inflation; whether Boltz fails on novel
  chemotypes (n=5 cannot say).

## 5. Fit to the INTERCEPTA vision
The vision is **novel** therapeutic discovery. This benchmark is **silent on that**: contaminated (not
zero-shot) and unpowered on novel chemistry (n=5). Its genuine value is (a) proof the co-folding pipeline
runs rigorously/reproducibly end-to-end, and (b) a **methodological cautionary result** — a single-target,
leakage-exposed, weak-baseline comparison showing how easily "beats docking" misleads. **Not publishable as
a positive discovery result**; it is scaffolding + an honest boundary marker.

## 6. Prioritized recommendations (next experiments)
1. **Decisive redesign — a contamination-controlled AND novel-chemotype-powered benchmark.** Temporal
   holdout (affinities published after Boltz's data window) or a target with *many* novel-chemotype actives,
   so the novel question is powered (not n=5). The only experiment that speaks to the vision. **Highest value.**
2. **Fix/strengthen the baseline** — audit HIT2's Vina (0.459 is a red flag) and/or add a competent
   docking/rescoring baseline, so "beats docking" is honest.
3. **Do not over-invest further in affinity ranking.** Contaminated, crowded, interpolation-ceilinged.
   **Redirect toward INTERCEPTA's differentiated white space — durability / mechanism / essentiality-based
   target prioritization** — where we are not competing with a foundation model trained on all of ChEMBL.

## 7. Scientific value (honest)
Moderate, and mostly negative-as-a-caution. It validated the engineering, verified the statistics to the
decimal, and — most usefully — required correcting our framing twice (the naive positive *and* the
over-strong leakage claim). That self-correcting rigor is the deliverable; the 0.68 is not. Real signal
will come from the contamination-controlled, novelty-powered, fair-baseline successor experiment.
