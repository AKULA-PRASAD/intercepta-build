#!/bin/bash
# AFFINITY2 powered novel-chemotype co-folding as a restartable GPU array.
# Reuses AFFINITY1's boltz_chunk.sh. EDIT --array to (N-1)%concurrency to match make_chunks N.
# Submit from the AFFINITY2 experiment dir:  sbatch hpc/affinity2_array.slurm
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
# reuse AFFINITY1's robust per-chunk runner (success = every YAML has affinity_*.json, NFS-safe)
bash ../AFFINITY1_cofolding_zeroshot/hpc/boltz_chunk.sh "$A2/chunks/chunk_$C" "$A2/out/chunk_$C"
echo "task=$SLURM_ARRAY_TASK_ID rc=$? end=$(date)"
