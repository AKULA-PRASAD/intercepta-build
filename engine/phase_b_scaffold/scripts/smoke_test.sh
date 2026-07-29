#!/bin/bash
#SBATCH --job-name=intercepta_smoke
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --time=00:30:00
#SBATCH --mem=16G
#SBATCH --output=/scratch/akula.pra/INTERCEPTA/logs/smoke_%j.out
#SBATCH --error=/scratch/akula.pra/INTERCEPTA/logs/smoke_%j.err

# Stage 1 Northeastern Explorer SLURM smoke test
# Per L4.1 §2.3 Stage 1 handoff criterion 5: "First SLURM job runs and writes output to scratch"

set -euo pipefail

echo "===================================================================="
echo "INTERCEPTA Stage 1 Smoke Test"
echo "Job ID: $SLURM_JOB_ID"
echo "Node:   $SLURMD_NODENAME"
echo "Date:   $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "===================================================================="

# Verify GPU access
echo ""
echo "--- GPU Verification (per L4.1 §2.2 deliverable 1.4) ---"
nvidia-smi

# Verify scratch quota
echo ""
echo "--- Scratch Quota Verification (≥2 TB required per L4.1 §2.2) ---"
df -h /scratch/akula.pra/

# Verify conda env
echo ""
echo "--- Conda Environment ---"
source ~/miniconda3/etc/profile.d/conda.sh  # adjust to your install
conda activate intercepta

python --version
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU device count: {torch.cuda.device_count()}')"

# Run smoke test inside conda env
echo ""
echo "--- INTERCEPTA Smoke Test ---"
cd /home/akula.pra/INTERCEPTA/code  # adjust to your clone path
pytest tests/test_smoke.py -v

echo ""
echo "===================================================================="
echo "Stage 1 Smoke Test COMPLETE"
echo "===================================================================="
