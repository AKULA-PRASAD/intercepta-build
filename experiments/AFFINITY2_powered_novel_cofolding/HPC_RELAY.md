# AFFINITY2 — Explorer HPC relay (exact commands)

*I cannot reach the HPC; you run these on Explorer and paste back the outputs (relay model). The Boltz-2 env
was already built for AFFINITY1 — reuse it. Everything here is deterministic + restartable. ~522 complexes,
~1–3 min each on a V100/A100 → ~10–26 GPU-hours, run as a 24-way array (max 8 concurrent) → ~1–3 h wall.*

## 0. One-time (already done for AFFINITY1 — skip if `/scratch/$USER/envs/boltz2` exists)
Boltz-2 conda/venv at `$BENV=/scratch/$USER/envs/boltz2`, and `$BOLTZ_CACHE=/scratch/$USER/boltz_cache`
(weights). If missing, see `../AFFINITY1_cofolding_zeroshot/hpc/` setup notes.

## 1. On the Mac — push the benchmark YAMLs to Explorer
```bash
cd /Users/kalki/INTERCEPTA_BUILD/experiments/AFFINITY2_powered_novel_cofolding
rsync -av benchmark/yamls/  akula.pra@login.explorer.northeastern.edu:/scratch/akula.pra/affinity2/yamls/
# also push the two reusable scripts if the repo isn't cloned on Explorer:
rsync -av hpc/  akula.pra@login.explorer.northeastern.edu:/scratch/akula.pra/affinity2/hpc/
```

## 2. On Explorer (login node) — chunk + submit the array
The runner `hpc/boltz_chunk.sh` is now AFFINITY2's OWN (globs `*.yaml`, self-contained — no AFFINITY1 path
dependency). SUBMIT-DIR CONTRACT: submit from a dir that contains `./hpc/boltz_chunk.sh`. Two equivalent ways:
```bash
# FIRST: get the fixed scripts. In the repo clone:
cd /scratch/$USER/intercepta-build && git pull        # -> commit with the AFFINITY2 hpc/ fix
# then EITHER (a) submit from the repo experiment dir (code+logs there, data via $A2):
cd /scratch/$USER/intercepta-build/experiments/AFFINITY2_powered_novel_cofolding
#   OR (b) keep your scratch workspace, but re-copy the fixed hpc/ into it and submit there:
#   rsync -av /scratch/$USER/intercepta-build/experiments/AFFINITY2_powered_novel_cofolding/hpc/ /scratch/$USER/affinity2/hpc/ ; cd /scratch/$USER/affinity2

export A2=/scratch/$USER/affinity2                    # DATA workspace (where chunks/ already exist)
ls "$A2/chunks" | wc -l                               # expect 24 (already built; do NOT re-chunk)
mkdir -p hpc/logs                                     # REQUIRED before sbatch (--output dir must pre-exist)
sbatch hpc/affinity2_array.slurm                      # array 0-23%8; passes A2 through env
squeue -u $USER                                       # watch; logs in ./hpc/logs/aff2_*.log
```
Restartable: re-`sbatch` the same array — chunks whose every YAML already has an `affinity_*.json` are skipped
(verified). Per-task exit code = number of still-missing compounds (0 = that chunk fully done).

## 3. When complete — verify count + pull outputs back to the Mac
```bash
# on Explorer: how many affinity JSONs produced (expect up to 522)
find "$A2/out" -name 'affinity_*.json' | wc -l
```
```bash
# on the Mac: pull the predictions back (structure preserved; cmpd_ids are globally unique)
cd /Users/kalki/INTERCEPTA_BUILD/experiments/AFFINITY2_powered_novel_cofolding
mkdir -p benchmark/boltz_out
rsync -av akula.pra@login.explorer.northeastern.edu:/scratch/akula.pra/affinity2/out/  benchmark/boltz_out/
```

## 4. On the Mac — score + apply the pre-registered two-tier gate
```bash
INTERCEPTA_DATA=/Users/kalki/intercepta_data \
  /Users/kalki/miniforge3/envs/intercepta/bin/python score.py     # run twice -> byte-identical sha
```
`results/AFFINITY2_metrics.json` reports, per target: co-folding novel-split AUROC (+95% CI) vs QSAR vs
property, and the verdict:
- **TIER1 (≥2 targets, cofold CI-lo>0.60)** → zero-data co-folding signal → **R5 OPENS**.
- **TIER2 (also cofold−max(QSAR,property)>0.10)** → co-folding beats ligand-ML → strong open.
- **neither** → **D2 CLOSED DEFINITIVELY at power** (co-folding, the last untried method, fails the zero-data
  novel-chemotype wall even with target-side leakage in its favor).

## Notes / integrity
- Bar to beat (baselines already computed, `results/`): QSAR novel-AUROC ALDH1 0.71 / PKM2 0.78 / FEN1 0.89.
- Target-side leakage caveat (PREREG): LIT-PCBA receptors predate Boltz's cutoff → any co-folding pass is
  optimistic; a FAIL is strong. A definitive PASS needs re-confirmation on a post-cutoff target.
- Raw Boltz outputs stay in `$INTERCEPTA_DATA`/scratch — never committed; only aggregate metrics are.
