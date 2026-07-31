# Pre-registration — B54: decomposing ligand-based VS enrichment — are decoy-bias and analog-bias independent, and what survives both? (FINALIZED 2026-07-30, PRE-RESULT; supersedes an earlier draft)

## The scientific gap (Phase 1–4, after a focused literature review)
Two enrichment biases are well established and studied **separately**: **physicochemical/decoy bias** (property-matched
decoys reduce it — DUD-E 2012, DeepCoy 2021; but ML still exploits residual bias — Chen 2019, Sieg 2019) and
**analog/similarity bias** (similar train/test actives inflate performance — Wallach & Heifets 2018 "benchmarks reward
memorization"; AVE debiasing; MUV). What the literature does **not** cleanly resolve: **are these two biases
independent, additive sources of enrichment inflation or the same underlying phenomenon — and what is the *irreducible*
binding-relevant signal that survives BOTH controls simultaneously?** Each is corrected one-at-a-time; there is no clean
factorial *attribution* with an interaction term on the same actives, nor a reported doubly-controlled residual. This is
the precise gap. It also unifies our own working principles P2 (analog-inflation, B45) and the T2 wild-card
(decoy-artifact) into ONE decomposition instead of two anecdotes — and it decides practice (if the biases are the same,
one control suffices; if independent, you need both).

## Design (2×2 factorial; Phase 9)
Same targets/model; cross two controls, measure held-out AUROC in all four cells:
- **Factor A — decoy matching:** A0 random decoys · A1 property-matched decoys (greedy NN in z-scored 6-D physchem:
  MolWt, Crippen logP, HBD, HBA, TPSA, rot-bonds; 3 decoys per active).
- **Factor B — analog control (train/test active similarity):** B0 random active split (analog bias PRESENT) ·
  B1 novel-chemistry split (scaffold-disjoint AND test actives restricted to Morgan-Tanimoto NN < 0.40 vs train actives
  — analog bias CONTROLLED).
Per cell: Morgan-1024 → HistGradientBoosting (seed=42) on train, AUROC on test (rdkit.ML.Scoring), mean over 5 seeds.

## Data (OPEN; LIT-PCBA, cached; no docking)
8 targets with enough actives: ALDH1, VDR, PKM2, FEN1, MAPK1, GBA, KAT2A, ESR1_ant. ≤300 actives (seeded); decoys 1:3
from the target's inactives. A target is included only if its B1 (novel-chemistry) test set has ≥15 actives; else
excluded and reported.

## Decomposition & hypotheses (Phase 9)
Let cell AUROCs be A0B0 (standard/biased), A1B0, A0B1, A1B1 (doubly-controlled). Report:
- **decoy-bias effect** = mean_B(A0 − A1); **analog-bias effect** = mean_A(B0 − B1);
- **interaction** = (A0B0 − A1B0) − (A0B1 − A1B1) — the independence test;
- **irreducible signal** = A1B1.
Pre-registered hypotheses:
- **H1 (biases INDEPENDENT/additive):** |interaction| < 0.03 (panel mean) — the decoy effect is the same with or without
  analog control. → the two biases are separate; both controls are needed.
- **H2 (biases OVERLAP/subadditive):** interaction ≤ −0.03 — controlling analog removes much of the decoy effect (or
  vice versa) → they are largely the *same* phenomenon; one control suffices.
- **H3 (irreducible signal exists):** A1B1 panel-mean > 0.60 — ligand-based VS retains real binding-relevant enrichment
  after BOTH biases are controlled. **H3-catastrophe (T2-strong):** A1B1 → 0.5 → ligand-based enrichment is essentially
  entirely bias-driven (a foundational, theory-reframing negative).
- **Reported regardless:** the full 2×2 per target + panel, the three decomposition terms, and A1B1.

## Honesty / scope
Retrospective, in-silico. 6-descriptor property matching is standard but not exhaustive (finer matching removes more →
A1 is a *lower bound* on residual decoy artifact, i.e. conservative). NN<0.40 is one analog-control threshold. Decoys
are assay-inactives (label noise). 8 targets. Enrichment ≠ proven activity; not wet-lab. Every outcome (independent /
overlapping / catastrophic collapse) is first-class and pre-committed.

## Reproducibility
Deterministic: active cap seed=42, split/decoy/scaffold seeds [1..5] fixed, greedy matching deterministic, model
seed=42. Reproduce ×2 byte-identical (payload sha256 over summary+per-target). Output:
`experiments/B54_decoy_artifact_discriminator/results/B54_metrics.json`. Env: intercepta-build; INTERCEPTA_DATA owned.
