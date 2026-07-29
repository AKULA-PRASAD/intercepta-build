#!/bin/bash
# MLflow tracking server initialization per L4.1 §2.2 deliverable 1.5
# Per L4.1 §10.1: every training run + evaluation run logs to MLflow

set -euo pipefail

# Local MLflow file backend (sufficient for Phase B; remote Phase F)
MLFLOW_BACKEND_DIR="${MLFLOW_BACKEND_DIR:-/scratch/akula.pra/INTERCEPTA/mlflow}"
MLFLOW_PORT="${MLFLOW_PORT:-5000}"

mkdir -p "$MLFLOW_BACKEND_DIR"

echo "Starting MLflow tracking server"
echo "  Backend: $MLFLOW_BACKEND_DIR"
echo "  Port:    $MLFLOW_PORT"
echo "  Access:  http://localhost:$MLFLOW_PORT"

# Run via ssh tunnel from local Mac:
#   ssh -L 5000:localhost:5000 akula.pra@login.explorer.northeastern.edu
# Then visit http://localhost:5000 in browser

mlflow server \
    --backend-store-uri "file://$MLFLOW_BACKEND_DIR" \
    --default-artifact-root "$MLFLOW_BACKEND_DIR" \
    --host 0.0.0.0 \
    --port "$MLFLOW_PORT"
