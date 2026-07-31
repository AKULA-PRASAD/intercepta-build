# B64 — END-TO-END DISCOVERY DEMONSTRATION on FEN1 (finalized 2026-07-31, PRE-RESULT)

## What this is (and is NOT)
This is a **capability demonstration**, not a hypothesis test — so it has no H1/H0. It wires every validated INTERCEPTA
module into ONE closed pipeline and runs it end-to-end on a single real disease target, producing a ranked, calibrated,
applicability-domain-annotated candidate shortlist. The deliverable is a set of **computational hypotheses** (ranked by a
composite developability × predicted-activity score, each flagged reliable/low-confidence), **NOT validated actives, NOT
drugs**. Nothing here is prospectively confirmed. It demonstrates that the pieces compose into a usable discovery engine.

## Why FEN1 (flap endonuclease 1)
- **Real disease target:** FEN1 is a structure-specific nuclease essential to DNA replication/repair; it is a
  synthetic-lethality / DNA-damage-response oncology target (over-expressed in multiple cancers). A meaningful, live target.
- **Where our signal is MOST real (honesty-driven choice):** across our whole program, FEN1 has the strongest
  *doubly-controlled* ligand signal — B45 novel-chemistry (scaffold-disjoint + NN-Tanimoto<0.4) residual AUROC ≈ 0.80,
  the highest of any target we benchmarked. We demonstrate on the target where the activity channel is genuinely
  informative, not on one where enrichment is similarity-inflated (P2). Data: LIT-PCBA FEN1 (369 actives / 355k inactives).

## Pipeline composed (all validated modules; strictly reused, no new science)
1. **Activity QSAR** — `admet._TaskModel("FEN1","roc-auc", conformal=True)` on LIT-PCBA FEN1 (actives + seeded 10k
   inactive subsample), Morgan-1024 → HGB, Tanimoto applicability domain + Mondrian conformal. [B30/B42/B45]
2. **QSAR validation (reported honestly, up front):** random 80/20 held-out AUROC AND a novel-chemistry held-out AUROC
   (test compounds with NN-Tanimoto<0.4 to train) — so the demo states the activity channel's *validated* skill in both
   the easy and the hard (novel-chemistry) regime before using it. [B45 lens]
3. **Target-conditioned generation** — `DiscoveryPipeline.discover()` = BRICS-GA (`generate.MoleculeOptimizer`) maximizing
   the composite objective F = QED × synthesizability × predicted-safety × P(FEN1-active), over a seeded ChEMBL seed set.
   [B33/B40]
4. **Multi-channel scoring / profiling** — per candidate: P(FEN1-active) + conformal set + AD in/out-domain,
   safety = 1−mean(hERG, AMES, DILI) [B30], synthesizability solvable-prob [B31], QED, SA score, composite F. [B39/B40]
5. **Ranked shortlist** (top 20 by F) written to CSV, each row honestly annotated reliable (in-domain) vs low-confidence
   (out-of-domain) — because P9/AD work says OOD predictions are untrustworthy.

## Honesty / scope (binding)
- Retrospective, in-silico, open data only. Output = ranked COMPUTATIONAL HYPOTHESES; enrichment/predicted-activity is
  NOT measured activity (P2: retrospective enrichment is ~half bias). No wet-lab, no prospective confirmation.
- Generated molecules are BRICS recombinations of known chemistry; many will be near known actives (that is expected and
  is stated per-candidate via the AD flag + nearest-training-Tanimoto).
- The activity channel is only trustworthy in-domain; out-of-domain candidates are reported but explicitly down-weighted
  in the honest read (B60–B62: the novel-chemistry regime is an information ceiling, not a solved problem).
- This raises the "usable platform" bar, NOT the "% of a real drug" bar — the drug still needs wet-lab (resource-gated).

## Reproducibility
Deterministic: inactive subsample seed=42, QSAR seed=42, split seeds fixed, generation seed=42, ChEMBL seed set seed=42.
Reproduce ×2 byte-identical — payload sha256 over {QSAR validation metrics + the full ranked shortlist (smiles + rounded
scores)}. Output: `experiments/B64_endtoend_fen1_demonstration/results/B64_metrics.json`. Env: intercepta-build;
INTERCEPTA_DATA owned.
