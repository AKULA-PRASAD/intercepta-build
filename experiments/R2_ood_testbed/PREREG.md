# R2 — OOD-generalization testbed — Pre-Registration (locked BEFORE scoring)

*The roadmap's top compute bet (`COMPUTATIONAL_MASTER_ROADMAP.md` R2). Not a claim to prove — an
**instrument** that measures the vision's core question and alarms if the extrapolation wall ever breaks.
Locked 2026-08-10.*

## Question the instrument measures
Can a method predict bioactivity for **genuinely novel chemotypes it never saw in training** — i.e., does any
signal exist OUTSIDE the training/similarity manifold? Every frontier wall in this program reduces to this.

## Design (leakage-controlled)
- **Data:** a target's compounds with a train/test split + continuous potency (first target: MoleculeACE
  CHEMBL204 thrombin, 2201 train / 553 test). `active := pKi ≥ 6.5`.
- **Novelty split (the leakage control):** for each TEST compound, max ECFP4 Tanimoto to TRAIN **actives**.
  **NOVEL** = max-Tanimoto < **0.40**; **SEEN(analog)** = ≥ 0.40. (Scaffold-disjoint Murcko split reported as sensitivity.)
- **Methods evaluated:**
  1. `similarity` — score = max Tanimoto to train actives. **Definitionally interpolation** → EXCLUDED from the alarm (control).
  2. `qsar_rf` — RandomForest on ECFP4 (2048b, r2), trained on TRAIN actives/inactives, predict_proba on TEST.
  3. `external` (slot) — any precomputed per-compound score CSV (e.g., a foundation model), for future drop-in.
- **Metrics (per method × per split ALL/SEEN/NOVEL):** AUROC + **bootstrap 95% CI** (B=2000, seed 42) via
  sklearn; enrichment EF@10%. Deterministic scoring → reproduce ×2 byte-identical (SHA-256 sorted-key payload).
- **Leakage audit:** report the TEST→TRAIN max-Tanimoto distribution (min/median/frac<0.4) so any external
  method's "novelty" is quantified, not assumed (the AFFINITY1 lesson).

## PRE-REGISTERED ALARM GATE (locked)
For any **non-`similarity`** method with no privileged access to the novel region:
- **WALL_BREAKING** (alarm fires) iff its **NOVEL-split AUROC bootstrap CI lower bound > 0.60**.
- **WALL_HOLDS** otherwise (novel ≈ chance).
The instrument's value is the same whether it fires or not: WALL_HOLDS quantifies the distance to the vision;
WALL_BREAKING is the signal that a paradigm/dataset finally extrapolates → then and only then invest in the
molecule half (roadmap R5).

## Honest pre-registered expectation
On thrombin today, **WALL_HOLDS** (qsar_rf strong on SEEN, ≈ chance on NOVEL) — consistent with HIT1
(`0.90→0.67`). The point is not this result; it is a permanent, re-runnable monitor for every future
model/dataset (roadmap R3 feeds it). Reported honestly either way; no tuning to a target outcome.
