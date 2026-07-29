#!/bin/bash
# Conda environment drift check per L4.3 §3.1 I1 prevention
# Run daily via cron OR before each session to catch drift early

set -euo pipefail

EXPECTED_ENV="intercepta"
LOG_DIR="${LOG_DIR:-$HOME/INTERCEPTA/docs/operational}"
mkdir -p "$LOG_DIR"

echo "===== Conda Env Drift Check ====="
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Hostname: $(hostname)"

# Verify env exists
if ! conda env list | grep -q "^${EXPECTED_ENV} "; then
    echo "ERROR: Conda env '$EXPECTED_ENV' not found"
    exit 1
fi

source activate "$EXPECTED_ENV" 2>/dev/null || conda activate "$EXPECTED_ENV"

# Export current env
TODAY=$(date -u +%Y%m%d)
EXPORT_FILE="$LOG_DIR/env_export_${TODAY}_$(hostname -s).yml"

conda env export --name "$EXPECTED_ENV" --no-builds > "$EXPORT_FILE"
echo "Env exported to: $EXPORT_FILE"

# Compare against pinned environment.yml (manual review)
echo ""
echo "Compare with environment.yml for drift:"
echo "  diff $EXPORT_FILE environment.yml"
echo ""
echo "If drift detected, document in $LOG_DIR/env_drift_log.md per L4.3 §3.1 recovery procedure."
