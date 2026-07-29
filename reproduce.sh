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
echo "== B2: beat the ceiling? =="
"$PY" experiments/B2_beat_ceiling/run.py
echo "== B3: cell-line -> patient transfer (L1) =="
: "${INTERCEPTA_BEATAML:=/Users/kalki/INTERCEPTA/data/beataml}"
export INTERCEPTA_BEATAML
"$PY" experiments/B3_patient_transfer/run.py
echo "== B3b: matched-platform patient specificity (L1b) =="
"$PY" experiments/B3b_patient_specificity/run.py
echo "== B3c: external replication, independent GDSC1 labels (L1b) =="
"$PY" experiments/B3c_external_replication/run.py
echo "== B3d: L1b robustness battery =="
"$PY" experiments/B3d_robustness/run.py
echo "== B3e: mechanistic coherence (L1b) =="
"$PY" experiments/B3e_mechanistic_coherence/run.py
echo "== B4: mechanism-anchored integration =="
"$PY" experiments/B4_mechanism_integration/run.py
echo "== engine v1 validation =="
"$PY" experiments/engine_v1_validation/run.py
echo "== B5 marker discovery =="
"$PY" experiments/B5_marker_discovery/run.py
echo "== B6 calibration =="
"$PY" experiments/B6_calibration/run.py
echo "== done. metrics in experiments/*/results/*_metrics.json =="
