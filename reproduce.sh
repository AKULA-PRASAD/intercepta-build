#!/usr/bin/env bash
# Re-run every pre-registered experiment from clean. Fails loudly on any data sha256 mismatch.
set -euo pipefail
cd "$(dirname "$0")"
: "${INTERCEPTA_DATA:=/Users/kalki/kaalcura/data}"
export INTERCEPTA_DATA
PY="${PY:-python3}"
echo "INTERCEPTA_DATA=$INTERCEPTA_DATA"
echo "== B1: baseline ceiling =="
"$PY" experiments/B1_baseline_ceiling/run.py
echo "== done. metrics in experiments/*/results/*_metrics.json =="
