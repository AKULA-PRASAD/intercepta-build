# AFFINITY2 — powered, leakage-controlled Boltz-2 co-folding vs the novel-chemotype affinity wall (PRE-REGISTRATION)

*Locked 2026-08-10, BEFORE running any co-folding. The definitive, powered test of the ONE untried method
(structure-based co-folding) against the ONE wall that gates the intervention half of the vision
(novel-target/novel-chemotype affinity, dead-end D2 / roadmap R5). AFFINITY1's own LEAKAGE_AUDIT names this
exact gap: co-folding was only tested on n=5 novel actives — "cannot support any novel-chemotype conclusion."
AFFINITY2 supplies the missing power (LIT-PCBA targets have 23–327 novel actives each) on a leakage-controlled
novel split, and is a genuine wall-BREAKING test — designed so BOTH outcomes are decisive.*

## Why this is not re-litigation (D8) and not a diminishing-returns arm (D4)
- R5 closed **ligand-only** methods (docking HIT2 0.428, QSAR HIT1 0.90→0.67, PCM B49, generation) on the
  novel split. **Co-folding is categorically different**: it uses the RECEPTOR STRUCTURE, so it *can* in
  principle generalize to chemotypes unseen in ligand space. It is the explicit reopen-trigger for D2/R5.
- It is the single **largest unbuilt piece of the vision** (the 14-weight intervention half; MASTER_PLAN Wave 2),
  and it is GPU-gated — exactly the external channel now available (Explorer HPC).

## Method under test (fixed, no tuning)
**Boltz-2** co-folding + affinity head (`boltz predict`, model=boltz2), zero activity data: protein sequence +
ligand SMILES → `affinity_pred_value` (predicted log IC50; lower = stronger). Same fixed hyperparameters as
AFFINITY1 GPU_BENCHMARK_SPEC (recycling_steps 3, seed 42, `--use_msa_server`). Score = −affinity_pred_value.

## Data — leakage-controlled, POWERED novel-chemotype panel (LIT-PCBA)
- Targets: the LIT-PCBA panel already harmonized by R3 with receptor structures cached
  (`$INTERCEPTA_DATA/lit_pcba/<TARGET>/*_protein.mol2`, PDB-coded). Primary panel (most novel actives):
  **ALDH1, PKM2, FEN1** (+ GBA/MAPK1 if GPU budget allows). Final panel fixed in DATA.md before scoring.
- Novel split (leakage control on the LIGAND side): **novel = ECFP4 (r2,2048) max-Tanimoto to TRAIN actives
  < 0.40** (identical to R2/R3). Active := y (pEC50/pKi) ≥ 6.5.
- Per target, the scored set (GPU-feasible cap): **ALL novel actives** (n≈68–327) **+ an equal-sized random
  sample of novel inactives** (seed 42), capped at **≤250 compounds/target** (if novel actives >125, subsample
  actives to 125 + 125 inactives). This guarantees a powered, class-balanced novel-split AUROC.
- Protein-side leakage: LIT-PCBA receptors are public PDB structures that predate Boltz's 2023-06-01 cutoff, so
  the *target* is plausibly in Boltz training — this is a leakage that can only INFLATE co-folding, so it
  **biases toward** the wall breaking. A pass under this bias is therefore weak evidence; a FAIL is strong
  (the method fails even with target-side leakage in its favor). Reported explicitly, not hidden.

## Baselines (the bar co-folding must clear — same novel split, same compounds)
1. **Property-only** RF (15 RDKit descriptors) — the LIT-PCBA decoy/property artifact control (R2/B54).
2. **Ligand QSAR** RF (ECFP4) trained on that target's TRAIN actives/inactives.
Both are ligand-only; co-folding adds the receptor. The question: does the receptor buy novel-chemotype
generalization the ligand-only models lack?

## Falsifiable decision gate (locked) — TWO-TIER verdict
### CORRECTION 2026-08-10 (pre-run, before any co-folding output — principled, not outcome-driven)
The interim baselines show the target-trained QSAR reaches novel-split AUROC 0.71/0.78/0.89 (ALDH1/PKM2/FEN1).
But QSAR **requires training actives**; co-folding's vision value is that it needs **none**. Requiring
co-folding to beat a trained QSAR conflates two questions, so the verdict is split into two clearly-labelled
tiers (both pre-registered here, before results):

- **Tier 1 — ZERO_DATA_SIGNAL (the vision-relevant test):** co-folding standalone novel-split AUROC
  **bootstrap 95% CI lower bound > 0.60** on **≥2 targets** (2000 resamples, seed 42). This asks the question
  that matches co-folding's actual use case: with ZERO activity data, does it rank novel-chemotype binders
  above chance-with-margin? A positive here is the genuinely new capability (ligand-only methods need actives).
- **Tier 2 — BEATS_LIGAND_ML (the stronger claim):** additionally (co-folding − **best ligand baseline**) novel
  AUROC **> 0.10** on ≥2 targets. Co-folding's receptor buys generalization beyond ligand-only learning.

### CORRECTION 2026-08-11 (pre-scoring statistical hardening — co-folding AUROC not yet computed anywhere)
Two rigor fixes locked before the co-folding scores are read on any machine (so not outcome-driven):
(1) **TIER2 now requires a PAIRED-bootstrap CI on the delta**, not a point comparison — best ligand baseline is
fixed by full-subset AUROC, then delta=(cofold−baseline) is bootstrapped with SHARED resample indices (seed 42);
TIER2 passes a target iff point delta > 0.10 **AND** the delta's 95% CI lower bound > 0. (2) All three scores
(cofold/QSAR/property) for the gate are computed on the **identical co-folding-scored compound subset**, and the
scorer emits an explicit **coverage report** (scored / expected, with any missing or invalid-value compound IDs
listed) and **fails loud** on a JSON schema mismatch — existence of a file is not accepted as a valid value.

**Decision:**
- **Tier 1 PASS → R5 OPENS** for zero-data co-folding on the intervention half (Tier 2 pass = strong open).
  Flagged pending a post-cutoff target (target-side leakage caveat).
- **Tier 1 FAIL → D2 CLOSED DEFINITIVELY at power**: co-folding, the last untried method, does not produce a
  usable zero-data novel-chemotype signal even with target-side leakage in its favor → the intervention half is
  information-limited, not method-limited. High-value negative, reported as prominently as a pass.

## Execution (relay — I cannot reach the HPC; the user runs on Explorer)
Benchmark construction (compounds + novelty split + receptor prep + Boltz YAMLs) is built here (CPU, in-repo).
The co-folding run is a SLURM array on Explorer (reusing AFFINITY1 `hpc/`), then analysis + gate here. Exact
relay commands in HPC_RELAY.md. Reproduce ×2 (deterministic seeds). Aggregate outputs only; no data committed.
