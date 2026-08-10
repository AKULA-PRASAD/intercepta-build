# AFFINITY2 — powered novel-chemotype co-folding vs the affinity wall: STATUS

**Status: BUILT & HPC-ready; co-folding run PENDING on Explorer (relay).** The decisive, powered test of the
one untried method (Boltz-2 structure-based co-folding) against the one wall gating the intervention half of
the vision (novel-chemotype affinity, D2/R5). Supplies the power AFFINITY1 lacked (n=5 → here 68–125 novel
actives/target). Pre-registered two-tier gate locked before any co-folding (`PREREG.md`).

## What is built + verified (CPU, in-repo, reproducible)
- **Benchmark (522 complexes):** leakage-controlled novel split (ECFP4 max-Tanimoto to train actives < 0.40),
  class-balanced — ALDH1 125a/125i, PKM2 68a/68i, FEN1 68a/68i (`build_benchmark.py`, manifest sha-stable).
- **Receptors:** ALDH1 4wp7 (501aa), PKM2 3gqy (550aa), FEN1 5fv7 (353aa), from RCSB.
- **Co-folding inputs:** 522 Boltz-2 YAMLs (protein seq + ligand SMILES + affinity head; `prep_yamls.py`).
- **Baselines already scored (the bar to beat; `results/AFFINITY2_metrics.json`, reproduced ×2):**
  target-trained QSAR novel-split AUROC **ALDH1 0.714 / PKM2 0.780 / FEN1 0.893**; property-only
  0.569 / 0.650 / 0.824.
- **HPC campaign:** `hpc/affinity2_array.slurm` + `hpc/make_chunks.py` (reuse AFFINITY1's robust, restartable,
  NFS-safe `boltz_chunk.sh`); exact relay commands in `HPC_RELAY.md`.

## The pre-registered two-tier verdict (applied by `score.py` once outputs return)
- **TIER1 — ZERO_DATA_SIGNAL** (co-folding standalone novel AUROC CI-lo > 0.60 on ≥2 targets): co-folding, with
  ZERO activity data, ranks novel-chemotype binders above chance — its actual vision use case → **R5 OPENS**.
- **TIER2 — BEATS_LIGAND_ML** (also cofold − max(QSAR,property) > 0.10): the receptor buys generalization beyond
  ligand-only learning → strong open.
- **neither → D2 CLOSED DEFINITIVELY at power** (high-value negative; intervention half is information-limited,
  not method-limited).

## Honest caveats (locked in PREREG)
Target-side leakage: LIT-PCBA receptors predate Boltz's 2023-06-01 cutoff → a co-folding PASS is optimistic
(re-confirm on a post-cutoff target); a FAIL is strong. Ligand-side is leakage-controlled by the novel split.

## Next action
Run `HPC_RELAY.md` steps 1–4 on Explorer → paste back the affinity-JSON count → I score + report the verdict.
