# AFFINITY1 — Zero-shot deep co-folding for novel-target binding-affinity ranking

**Frontier 2 (docs/INVENTION_ROADMAP.md) — OPEN-PROBLEM, do NOT fake.**
Pre-registered BEFORE any scoring. UTC authored: 2026-08-07.

## The open problem
To go target→drug for the ~93% undrugged validated targets we must RANK binding affinity for a
target with ZERO activity data. Every standard tool has been proven to fail on our own setups:
- docking ≈ random for within-series potency (HIT2: thrombin overall AUROC **0.43**, anti-predictive)
- ligand methods are analog-bound (HIT1)
- proteochemometric transfer adds ~nothing (B49: protein features Δ −0.038)
- active-learning on novel chemotypes is a null (B65)

The one credible UNTRIED zero-shot candidate that is open-source and *possibly* CPU-runnable is a
**deep co-folding model** (Boltz / Chai — AlphaFold3-class protein-ligand co-folding). It predicts
the bound complex + a confidence/affinity signal directly, with no activity data.

## Hypothesis
**H1 (the invention):** a co-folding model's affinity/confidence proxy ranks thrombin (CHEMBL204)
potency BETTER than the docking baseline (HIT2) AND better than random, with a stated margin —
ESPECIALLY on scaffold-NOVEL chemotypes (the case that actually matters).

**H0 (first-class negative):** the co-folding proxy does NOT beat docking/random → the wall stands;
a negative that further bounds the molecule-half information ceiling.

## Feasibility gate (STEP 1 — decided BEFORE the science; see FEASIBILITY.md)
Pre-registered CPU caps on this Apple-Silicon M4 / 16 GB / arm64 / NO GPU/CUDA machine:
- **G1 install:** boltz (or chai_lab) pip-installs into a fresh CPU venv (no CUDA-only blocker).
- **G2 single-complex wall-clock:** one small protein+ligand complex (thrombin ~250 aa + one SMILES)
  completes inference in **≤ 20 min** and does **NOT OOM** (≤ ~15 GB RSS; hard fail on MemoryError/kill).
- If G1 & G2 PASS → proceed to STEP 2.
- If G1 or G2 FAIL → declare **CPU-INFEASIBLE** honestly, STOP the compute, and deliver the exact,
  ready-to-run GPU benchmark SPEC (roadmap item i) so it runs the instant GPU is available. This is a
  first-class deliverable, not a failure to hide.

## STEP 2 — pre-registered zero-shot potency-ranking test (only if feasible)
- **Target / data (HEAD-TO-HEAD vs docking):** thrombin CHEMBL204 — the SAME target, receptor (1OYT),
  and MoleculeACE test compounds HIT2 docked, so co-folding is compared to docking on identical ground.
  MoleculeACE `CHEMBL204_Ki.csv` (553 test compounds; active := pKi ≥ 6.5, matching HIT1/HIT2).
- **Method:** for each compound, run co-folding (thrombin sequence + ligand SMILES). Extract the model's
  affinity/confidence proxy — Boltz-2 predicted-affinity head if present, else ipTM / complex-confidence.
- **Scoring:** Spearman ρ (proxy vs true pKi, continuous) and active-vs-inactive AUROC; overall + the
  HIT1/HIT2 novelty split (analog nearest-seed Tanimoto ≥ 0.4 vs novel < 0.4).
- **Compute budget:** if 20 min/complex, 553 complexes is ~7.7 days — INFEASIBLE for the full set on CPU.
  Contingency (pre-registered): if per-complex time ∈ (cap]) but the full set is infeasible, run a
  PRE-SPECIFIED **stratified subsample** — ALL novel actives (n=5) + a fixed-seed (seed=42) random draw
  balancing actives/inactives up to a wall-clock budget of ≤ 24 h total — and report it as an explicitly
  underpowered pilot, NOT the full head-to-head. Full-set head-to-head is then part of the GPU SPEC.

## Pre-registered GATE (decided BEFORE scoring — no tuning-to-pass)
- **PASS (genuine advance on the open wall):** co-folding overall AUROC > docking (0.43) AND > random
  by margin ≥ **+0.10** (i.e. AUROC ≥ 0.60), AND on scaffold-NOVEL actives AUROC ≥ 0.60. Analog-only
  wins do NOT count as cracking the wall.
- **FAIL / BOUNDED-NEGATIVE:** does not clear the above → first-class negative bounding the wall.
- **CPU-INFEASIBLE:** feasibility gate fails → deliver GPU SPEC.

## Reproducibility
Neural inference may be non-deterministic. Set fixed seeds (seed=42) + deterministic flags. If inference
is still not byte-identical, CACHE raw model outputs to $INTERCEPTA_DATA/affinity1/ and reproduce the
DOWNSTREAM scoring/analysis ×2 BYTE-IDENTICAL (payload sha256). Disclose any inference-nondeterminism
openly in SUMMARY — never hide it.

## Scope guards (every claim)
in-silico; one target (thrombin, docking's most favourable case); CPU-constrained; a confidence/affinity
PROXY, not measured affinity; enrichment ≠ proven activity; not wet-lab; no SOTA claim.

## Environment
Apple M4, 10 cores, 16 GB RAM, arm64, macOS; NO GPU/CUDA. Fresh venv at
$INTERCEPTA_DATA/affinity1/venv_affinity1. Baseline: HIT2 (experiments/HIT2_physics_floor).

---

## STEP-2 CONTINGENCY EXECUTED — pre-registered subsample composition (recorded BEFORE running boltz)
Realistic use-case reframe: rank a SMALL candidate set for one target (not the 553-library) — CPU-feasible.
Deterministic (seed=42) via `run.py prep 20`. Composition FIXED before any inference:
- **20 compounds total** = ALL **5 novel actives** + **7 analog actives** + **8 inactives** (12 active / 8 inactive; 6 novel / 14 analog by nearest-seed Tanimoto).
- idxs (MoleculeACE CHEMBL204 test order): [21, 67, 167, 173, 217, 248, 256, 329, 340, 347, 367, 384, 399, 409, 428, 467, 472, 529, 535, 549]
- Boltz-2 defaults (NO tuning): recycling 3, sampling_steps 200, diffusion_samples 1, sampling_steps_affinity 200, diffusion_samples_affinity 5, MSA=colabfold server, seed 42, --accelerator cpu.
- **Pre-registered pilot read (UNDERPOWERED, n=20):** does co-folding affinity (proxy = -affinity_pred_value and affinity_probability_binary) beat docking (HIT2 AUROC 0.4285) and random (0.5) on active-vs-inactive AUROC, AND show Spearman>0 vs true pKi, ESPECIALLY on the 5 novel actives? This is a PILOT, not the definitive benchmark (that remains the GPU spec on all 553). No overclaim from n=20; n_novel_active=5 is severely underpowered by construction.
