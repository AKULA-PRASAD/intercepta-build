#!/bin/zsh
# Waits for the main DYNAMICS5 run (PID $1) to finish, then reproduces the downstream
# scoring a 2nd time (pure rescore from the byte-identical entropy cache) and records
# whether the SHA-256 payload is byte-identical across the two runs.
set -e
MAINPID=$1
HERE=/Users/kalki/INTERCEPTA_BUILD/experiments/DYNAMICS5_resistance_site_entropy
export INTERCEPTA_DATA=/Users/kalki/intercepta_data
PY=~/miniforge3/envs/intercepta/bin/python
cd "$HERE"
while kill -0 "$MAINPID" 2>/dev/null; do sleep 30; done
sleep 3
SHA1=$(cat results/payload.sha256 2>/dev/null || echo MISSING)
$PY run.py > /Users/kalki/intercepta_data/dynamics5/rerun_scoring.log 2>&1
SHA2=$(cat results/payload.sha256 2>/dev/null || echo MISSING)
{
  echo "run1_payload_sha256: $SHA1"
  echo "run2_payload_sha256: $SHA2"
  if [ "$SHA1" = "$SHA2" ] && [ "$SHA1" != "MISSING" ]; then
    echo "BYTE_IDENTICAL: YES"
  else
    echo "BYTE_IDENTICAL: NO"
  fi
} > "$HERE/REPRODUCE.txt"
$PY make_summary.py >> /Users/kalki/intercepta_data/dynamics5/rerun_scoring.log 2>&1
echo "done" >> /Users/kalki/intercepta_data/dynamics5/rerun_scoring.log
