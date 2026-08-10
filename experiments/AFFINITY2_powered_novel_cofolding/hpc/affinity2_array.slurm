#!/bin/bash
# AFFINITY2 powered novel-chemotype co-folding as a restartable GPU array.
# Uses AFFINITY2's OWN hpc/boltz_chunk.sh (self-contained; globs *.yaml). EDIT --array to (N-1)%concurrency.
# SUBMIT DIR CONTRACT: submit from a dir that contains ./hpc/boltz_chunk.sh (either the repo experiment dir
#   experiments/AFFINITY2_powered_novel_cofolding, or the scratch workspace $A2 if you copied hpc/ there).
#   Set A2=<data workspace with chunks/> if it differs from the submit dir. `mkdir -p hpc/logs` BEFORE sbatch
#   (the --output dir must exist at submit time). Example:  A2=/scratch/$USER/affinity2 sbatch hpc/affinity2_array.slurm
#SBATCH --job-name=aff2
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=04:00:00
#SBATCH --array=0-23%8
#SBATCH --output=hpc/logs/aff2_%A_%a.log
#SBATCH --error=hpc/logs/aff2_%A_%a.log
set -uo pipefail
cd "${SLURM_SUBMIT_DIR:-.}"; mkdir -p hpc/logs
export BENV="${BENV:-/scratch/$USER/envs/boltz2}"
export BOLTZ_CACHE="${BOLTZ_CACHE:-/scratch/$USER/boltz_cache}"
export A2="${A2:-/scratch/$USER/affinity2}"
C="$(printf '%02d' "$SLURM_ARRAY_TASK_ID")"
# AFFINITY2's own per-chunk runner (success = every YAML has affinity_*.json, NFS-safe, restartable)
bash hpc/boltz_chunk.sh "$A2/chunks/chunk_$C" "$A2/out/chunk_$C"
echo "task=$SLURM_ARRAY_TASK_ID rc=$? end=$(date)"
