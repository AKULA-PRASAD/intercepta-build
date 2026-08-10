#!/bin/bash
# AFFINITY2 per-chunk Boltz-2 runner. Restartable + NFS-safe. Self-contained (no AFFINITY1 dependency).
# Args: $1 = chunk YAML dir, $2 = chunk out dir. Requires env: BENV, BOLTZ_CACHE.
# NOTE vs AFFINITY1's runner: AFFINITY2 YAMLs are named <TARGET>_NNNN.yaml (e.g. ALDH1_0000.yaml),
#   NOT cmpd_*.yaml, so we glob *.yaml. All 522 ligands are <=44 heavy atoms (Boltz affinity limit 128),
#   so there is NO oversized-exclusion list. Success = every input YAML has an affinity_*.json (NOT the boltz
#   exit code): boltz can throw a benign NFS ".nfs Errno 16" during tmp cleanup AFTER a successful prediction.
set -uo pipefail                      # deliberately NOT -e (tolerate the cleanup OSError)
CHUNK_DIR="$1"; OUT_DIR="$2"
BOLTZ="${BENV:?set BENV}/bin/boltz"
mkdir -p "$OUT_DIR"
shopt -s nullglob                     # unmatched glob -> empty list (never a literal pattern)

# node-local scratch for tmp -> avoids NFS .nfs cleanup races on /scratch
export TMPDIR="${SLURM_TMPDIR:-/tmp}/boltz.${SLURM_ARRAY_TASK_ID:-x}.$$"; mkdir -p "$TMPDIR"

# restart: if every YAML already has its affinity JSON, skip the GPU entirely
need=0
for y in "$CHUNK_DIR"/*.yaml; do
  n="$(basename "$y" .yaml)"
  find "$OUT_DIR" -path "*/predictions/$n/affinity_$n.json" 2>/dev/null | grep -q . || need=1
done
if [ "$need" -eq 0 ]; then echo "SKIP (all outputs present): $CHUNK_DIR"; exit 0; fi

echo "RUN boltz on $CHUNK_DIR -> $OUT_DIR  ($(date))"
"$BOLTZ" predict "$CHUNK_DIR" --out_dir "$OUT_DIR" --cache "${BOLTZ_CACHE:?set BOLTZ_CACHE}" \
    --model boltz2 --accelerator gpu --devices 1 --seed 42 --use_msa_server || \
    echo "boltz returned nonzero (checking outputs; may be benign NFS cleanup) ..."

# verify by OUTPUTS, not exit code
missing=0
for y in "$CHUNK_DIR"/*.yaml; do
  n="$(basename "$y" .yaml)"
  if find "$OUT_DIR" -path "*/predictions/$n/affinity_$n.json" 2>/dev/null | grep -q .; then :; else
    echo "MISSING affinity json: $n"; missing=$((missing+1)); fi
done
echo "chunk_summary dir=$CHUNK_DIR missing=$missing ($(date))"
rm -rf "$TMPDIR" 2>/dev/null || true
exit "$missing"          # 0 = all compounds produced output; >0 = that many still missing
