#!/bin/bash
# AFFINITY1 full 553-compound benchmark as a restartable GPU array.
# EDIT before submit: --array (n_chunks-1, must match make_chunks.py), --time (from Phase-3 rate),
#   --partition/--gres (prefer a100; v100 fine). Submit from the experiment dir:
#     sbatch hpc/affinity_array.slurm
#SBATCH --job-name=aff1
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1                 # prefer: --gres=gpu:a100:1  (native bf16, faster)
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=04:00:00              # per task; size so (chunk_size * per_complex_min) < this
#SBATCH --array=0-23%8               # 24 chunks, max 8 concurrent GPUs (match make_chunks.py N)
#SBATCH --output=hpc/logs/aff1_%A_%a.log
#SBATCH --error=hpc/logs/aff1_%A_%a.log
set -uo pipefail
mkdir -p hpc/logs
export BENV="${BENV:-/scratch/$USER/envs/boltz2}"
export INTERCEPTA_DATA="${INTERCEPTA_DATA:-/scratch/$USER/intercepta_data}"
export BOLTZ_CACHE="${BOLTZ_CACHE:-/scratch/$USER/boltz_cache}"
export INTERCEPTA_HW="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
echo "task=$SLURM_ARRAY_TASK_ID node=$(hostname) gpu=$INTERCEPTA_HW start=$(date)"
C="$(printf '%02d' "$SLURM_ARRAY_TASK_ID")"
bash hpc/affinity/boltz_chunk.sh \
  "$INTERCEPTA_DATA/affinity1/yamls/chunk_$C" \
  "$INTERCEPTA_DATA/affinity1/out/chunk_$C"
rc=$?
echo "task=$SLURM_ARRAY_TASK_ID rc=$rc end=$(date)"
exit $rc
