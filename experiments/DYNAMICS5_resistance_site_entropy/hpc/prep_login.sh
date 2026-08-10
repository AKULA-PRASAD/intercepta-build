#!/bin/bash
# DYNAMICS5 Explorer prep -- run on a LOGIN node (needs internet). Idempotent; safe to re-run.
# Stages everything the OFFLINE compute job needs: transformers in the env, CARD card.json, and the
# esm2_t30_150M weights pre-cached (run.py forces HF_HUB_OFFLINE=1, so the model must exist first).
set -uo pipefail
export INTERCEPTA_DATA="${INTERCEPTA_DATA:-/scratch/$USER/intercepta_data}"
export BENV="${BENV:-/scratch/$USER/envs/boltz2}"
mkdir -p "$INTERCEPTA_DATA/card" "$INTERCEPTA_DATA/hf_cache" "$INTERCEPTA_DATA/dynamics5"

echo "[1/3] transformers present in $BENV ?"
"$BENV/bin/python" -c "import transformers,torch;print('transformers',transformers.__version__,'torch',torch.__version__)" \
  || { echo "  installing transformers..."; "$BENV/bin/pip" install -q transformers; }

echo "[2/3] CARD card.json (public, ~5 MB)"
if [ ! -f "$INTERCEPTA_DATA/card/card.json" ]; then
  ( cd "$INTERCEPTA_DATA/card" && curl -sL -A "Mozilla/5.0" -o card-data.tar.bz2 "https://card.mcmaster.ca/latest/data" && tar xjf card-data.tar.bz2 )
fi
ls -l "$INTERCEPTA_DATA/card/card.json" || { echo "CARD FETCH FAILED"; exit 1; }

echo "[3/3] pre-download esm2_t30_150M into HF_CACHE (online now; run.py runs offline)"
HF_HUB_OFFLINE=0 TRANSFORMERS_OFFLINE=0 "$BENV/bin/python" - "$INTERCEPTA_DATA/hf_cache" <<'PY'
import sys
from transformers import AutoTokenizer, AutoModelForMaskedLM
c = sys.argv[1]
AutoTokenizer.from_pretrained("facebook/esm2_t30_150M_UR50D", cache_dir=c)
AutoModelForMaskedLM.from_pretrained("facebook/esm2_t30_150M_UR50D", cache_dir=c)
print("esm2_t30_150M cached OK ->", c)
PY
echo "PREP DONE.  Next:  sbatch hpc/dynamics5.slurm"
