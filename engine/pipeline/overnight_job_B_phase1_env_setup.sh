#!/bin/bash
# INTERCEPTA Layer 1 Job B Phase 1: GPU Environment Setup
# Creates intercepta-fm conda environment with PyTorch + foundation model deps
# Per Job G result (2026-05-09): current intercepta-nsclc env has no PyTorch/transformers

set -e
set -o pipefail

LOG_DIR="/scratch/akula.pra/INTERCEPTA/logs"
LOG_FILE="${LOG_DIR}/job_B_phase1_env_setup_$(date +%Y%m%d_%H%M%S).log"
ENV_PATH="/scratch/akula.pra/INTERCEPTA/envs/intercepta-fm"

mkdir -p "${LOG_DIR}"

exec > >(tee -a "${LOG_FILE}") 2>&1

echo "============================================================"
echo "Job B Phase 1: GPU Environment Setup"
echo "Started: $(date)"
echo "Log: ${LOG_FILE}"
echo "Target env: ${ENV_PATH}"
echo "============================================================"

# Source conda
source /shared/EL9/explorer/miniconda3/24.11.1/miniconda3/etc/profile.d/conda.sh

# Check if env already exists
if [ -d "${ENV_PATH}" ]; then
    echo ""
    echo "Env already exists at ${ENV_PATH}"
    echo "Checking package status..."
    conda activate "${ENV_PATH}"
    python -c "import torch; print(f'  torch={torch.__version__}, cuda={torch.cuda.is_available()}')" 2>&1 || echo "  torch NOT working"
    python -c "import transformers; print(f'  transformers={transformers.__version__}')" 2>&1 || echo "  transformers NOT installed"
    echo ""
    echo "If env is good, skipping recreation. If broken, manually rm -rf and rerun."
    exit 0
fi

echo ""
echo "[1/4] Creating fresh env at ${ENV_PATH}"
echo "------------------------------------------------------------"
conda create --prefix "${ENV_PATH}" python=3.10 -y

echo ""
echo "[2/4] Activating new env"
echo "------------------------------------------------------------"
conda activate "${ENV_PATH}"
which python
python --version

echo ""
echo "[3/4] Installing PyTorch with CUDA"
echo "------------------------------------------------------------"
# PyTorch 2.x with CUDA 11.8 (broadly compatible across HPC GPU generations)
pip install --no-cache-dir torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cu118

echo ""
echo "[4/4] Installing foundation model dependencies"
echo "------------------------------------------------------------"
pip install --no-cache-dir \
    transformers==4.41.2 \
    huggingface_hub==0.23.0 \
    accelerate==0.30.1 \
    peft==0.11.1 \
    scanpy==1.10.1 \
    anndata==0.10.7 \
    scvi-tools==1.1.2 \
    scikit-learn==1.5.0 \
    pandas==2.2.2 \
    numpy==1.26.4 \
    scipy==1.13.0 \
    matplotlib==3.8.4 \
    seaborn==0.13.2 \
    h5py==3.11.0 \
    tqdm==4.66.4 \
    requests==2.32.3

echo ""
echo "============================================================"
echo "VERIFICATION"
echo "============================================================"
python << 'EOF'
import sys
print("Python:", sys.version)

packages = ["torch", "transformers", "huggingface_hub", "accelerate", "peft",
            "scanpy", "anndata", "scvi", "sklearn", "pandas", "numpy"]
for pkg in packages:
    try:
        m = __import__(pkg)
        v = getattr(m, "__version__", "unknown")
        print(f"  {pkg:20s}: {v}")
    except ImportError as e:
        print(f"  {pkg:20s}: FAILED - {e}")

try:
    import torch
    print()
    print(f"PyTorch CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  Device count: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            print(f"  [{i}] {props.name} ({props.total_memory / 1e9:.2f} GB)")
except Exception as e:
    print(f"PyTorch check failed: {e}")
EOF

echo ""
echo "============================================================"
echo "Job B Phase 1 COMPLETE: $(date)"
echo "Env path: ${ENV_PATH}"
echo "Log: ${LOG_FILE}"
echo "============================================================"
