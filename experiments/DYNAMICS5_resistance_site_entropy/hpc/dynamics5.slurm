#!/bin/bash
# DYNAMICS5 on Explorer -- CPU compute job (offline; run prep_login.sh first).
# Submit from the experiment dir:  sbatch hpc/dynamics5.slurm
#SBATCH --job-name=dyn5
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=03:00:00
#SBATCH --output=hpc/logs/dyn5_%j.log
#SBATCH --error=hpc/logs/dyn5_%j.log
# (no --partition -> uses the cluster DEFAULT partition; CPU-only, no GPU requested)
set -uo pipefail
cd "${SLURM_SUBMIT_DIR:-.}"; mkdir -p hpc/logs
export INTERCEPTA_DATA="${INTERCEPTA_DATA:-/scratch/$USER/intercepta_data}"
export BENV="${BENV:-/scratch/$USER/envs/boltz2}"
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}" MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}"
echo "node=$(hostname) start=$(date)  (offline ESM-2 t30 150M masked-marginal entropy)"
"$BENV/bin/python" run.py
echo "--- reproduce x2 (scoring deterministic; SHA over payload only; inference is cached) ---"
cp -f results/payload.sha256 "/tmp/d5_${SLURM_JOB_ID:-x}.sha" 2>/dev/null || true
"$BENV/bin/python" run.py > hpc/logs/dyn5_rerun.log 2>&1
if diff -q "/tmp/d5_${SLURM_JOB_ID:-x}.sha" results/payload.sha256 >/dev/null 2>&1; then
  echo "REPRODUCED_BYTE_IDENTICAL"
else
  echo "WARN: payload sha differs between runs -- inspect"
fi
echo "done=$(date)"; echo "payload sha:"; cat results/payload.sha256 2>/dev/null
