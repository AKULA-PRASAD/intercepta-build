#!/bin/bash
# Run scoring + bootstrap analysis on a COMPUTE node (never the login node -> no policy SIGKILL).
# Submit from the experiment dir:  sbatch hpc/analyze.slurm
#SBATCH --job-name=aff1_analyze
#SBATCH --partition=short          # any CPU-capable partition; change if 'short' is GPU-only on your cluster
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:15:00
#SBATCH --output=hpc/logs/analyze_%j.log
#SBATCH --error=hpc/logs/analyze_%j.log
set -uo pipefail
cd "${SLURM_SUBMIT_DIR:-.}"; mkdir -p hpc/logs
export BENV="${BENV:-/scratch/$USER/envs/boltz2}"
export INTERCEPTA_DATA="${INTERCEPTA_DATA:-/scratch/$USER/intercepta_data}"
echo "node=$(hostname) start=$(date)"
"$BENV/bin/python" run.py score
"$BENV/bin/python" hpc/analyze.py
# copy the small result tables into the tracked results/ dir so they can be committed for reproducibility
cp -f "$INTERCEPTA_DATA/affinity1/scored.csv" results/scored.csv 2>/dev/null || true
echo "done=$(date)"
