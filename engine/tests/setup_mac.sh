#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# INTERCEPTA — Mac Setup & Quick Validation
# ═══════════════════════════════════════════════════════════════
# 
# Usage:
#   cd INTERCEPTA
#   chmod +x setup_mac.sh
#   ./setup_mac.sh
#
# Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
# ═══════════════════════════════════════════════════════════════

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║            INTERCEPTA — Mac Setup                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
echo "[1/4] Checking Python..."
if command -v python3 &> /dev/null; then
    PY=$(python3 --version 2>&1)
    echo "  Found: $PY"
else
    echo "  ERROR: Python 3 not found. Install: brew install python3"
    exit 1
fi

# Install dependencies
echo ""
echo "[2/4] Installing dependencies..."
pip3 install -r requirements.txt --quiet 2>/dev/null || \
pip install -r requirements.txt --quiet 2>/dev/null || \
echo "  WARNING: pip install failed. Try: pip3 install -r requirements.txt"

# Quick validation
echo ""
echo "[3/4] Running 5-trial validation (30s)..."
python3 scripts/run_5trial_validation.py

# Show project structure
echo ""
echo "[4/4] Project structure:"
echo ""
echo "  INTERCEPTA/"
echo "  ├── docs/           9 documents (vision, mathspec, reports)"
echo "  ├── src/            6 Python modules (production code)"
echo "  │   ├── intercepta_kaalcura_v1.py      KAALCURA axes"
echo "  │   ├── intercepta_engine_v2.py        Validated ODE engine"
echo "  │   ├── intercepta_synergy_v1.py       Synergy scoring"
echo "  │   ├── intercepta_bridge_v1.py        KAALCURA→ODE bridge"
echo "  │   ├── intercepta_timemachine_v1.py   RNA velocity pipeline"
echo "  │   └── intercepta_data_loaders_v1.py  Data loaders"
echo "  ├── results/        8 validation result files"
echo "  ├── scripts/        3 run scripts"
echo "  ├── archive/        8 superseded files (reference only)"
echo "  ├── data/           (empty — download GDSC/scRNA-seq here)"
echo "  ├── requirements.txt"
echo "  ├── setup_mac.sh"
echo "  └── README.md"
echo ""
echo "Quick commands:"
echo "  python3 scripts/run_5trial_validation.py    # Reproduce 5/5 trials"
echo "  python3 scripts/run_timemachine.py           # Time Machine demo"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Setup complete. INTERCEPTA is ready."
echo "═══════════════════════════════════════════════════════════════"
