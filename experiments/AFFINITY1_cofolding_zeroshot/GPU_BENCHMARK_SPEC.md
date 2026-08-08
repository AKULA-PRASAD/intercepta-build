# AFFINITY1 — ready-to-run GPU benchmark SPEC (roadmap Frontier-2 item i)

This is the exact, pre-registered experiment to run the instant a CUDA GPU is available. It is a
first-class deliverable: the FULL 553-compound head-to-head is CPU-infeasible (see FEASIBILITY.md),
so the definitive test of the co-folding invention against the docking wall is specified here so it
runs with no further design decisions.

## Method under test
**Boltz-2** (co-folding + affinity head), `boltz predict`, model=boltz2. The affinity head outputs
`affinity_pred_value` (predicted log(IC50), lower = stronger binder) and `affinity_probability_binary`
(P(binder)). Zero activity data is used — pure sequence + SMILES → predicted affinity.

## Target / data (HEAD-TO-HEAD, identical ground to the docking baseline)
- Target: **thrombin CHEMBL204**, receptor **1OYT** (light chain A + heavy chain B; sequences in
  `run.py`). SAME target, receptor, and compounds that HIT2 docked with AutoDock Vina.
- Compounds: **all 553 MoleculeACE `CHEMBL204_Ki.csv` test compounds** (24 that failed Vina docking
  are still run through Boltz; active := pKi ≥ 6.5). Novelty split (`test_novelty.csv`, already
  computed, deterministic): 486 analog / 67 novel; 292 actives / 5 novel actives.

## Run command (per the fixed config — no tuning)
```
export BOLTZ_CACHE=$INTERCEPTA_DATA/affinity1/boltz_cache
python run.py prep 553          # writes 553 YAMLs
boltz predict $INTERCEPTA_DATA/affinity1/yamls \
  --out_dir $INTERCEPTA_DATA/affinity1/out \
  --cache $BOLTZ_CACHE --accelerator gpu --devices 1 \
  --use_msa_server --seed 42 --output_format pdb
python run.py score             # metrics + payload.sha256
```
Fixed hyperparameters (DEFAULTS — pre-registered, do not tune): recycling_steps 3,
sampling_steps 200, diffusion_samples 1, sampling_steps_affinity 200, diffusion_samples_affinity 5,
MSA via colabfold mmseqs2 server, seed 42.

## Metrics
- Spearman ρ (−affinity_pred_value and affinity_probability_binary vs true pKi), continuous.
- Active-vs-inactive AUROC (overall + analog-vs-inactive + novel-vs-inactive), same split as HIT1/HIT2.
- Head-to-head: Boltz AUROC vs HIT2 docking (full-set overall AUROC **0.4285**) on the SAME compounds.

## Pre-registered GATE (decided before scoring; identical to PREREG.md)
- **PASS (advance on the open wall):** overall AUROC ≥ 0.60 AND > 0.4285 (docking) AND
  novel-vs-inactive AUROC ≥ 0.60. Analog-only wins do NOT count.
- **FAIL / BOUNDED-NEGATIVE:** otherwise — first-class negative bounding the wall.

## Second target (external check, if GPU budget allows)
Repeat identically on **one LIT-PCBA target already in reach** (e.g. FEN1 — B49's best transfer, has
actives+property-matched decoys) to add a coarse active-vs-decoy read distinct from thrombin's
within-series potency-ranking. Same command; swap sequence + compound set.

## Reproducibility
Neural inference may be non-deterministic even with --seed 42. Cache raw `affinity_*.json`; reproduce
the downstream `run.py score` ×2 byte-identical (payload sha). Disclose any inference nondeterminism.

## Expected wall-clock (GPU)
Boltz-2 ~1–3 min/complex on a modern GPU → 553 complexes ≈ 9–28 GPU-hours (single device), trivially
batchable. This is the step CPU cannot do.
