#!/bin/zsh
cd /Users/kalki/INTERCEPTA_BUILD/experiments/PLMSTRUCT1_structure_aware_plm_nonmetabolic
PY=/Users/kalki/miniforge3/envs/intercepta/bin/python
export OMP_NUM_THREADS=10 MKL_NUM_THREADS=10 TOKENIZERS_PARALLELISM=false HF_HUB_OFFLINE=1
echo "=== DRIVER START $(date) ==="
echo "=== ESM650 (ARM B) ==="
$PY run.py embed_esm650 10 || { echo "ESM650 FAILED rc=$?"; exit 1; }
echo "=== SAPROT (ARM A) ==="
$PY run.py embed_saprot 10 || { echo "SAPROT FAILED rc=$?"; exit 1; }
echo "=== SCORE ==="
$PY run.py score || { echo "SCORE FAILED rc=$?"; exit 1; }
echo "=== DRIVER DONE $(date) ==="
