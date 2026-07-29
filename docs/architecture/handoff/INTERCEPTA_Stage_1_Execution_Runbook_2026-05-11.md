# INTERCEPTA Phase B Layer 5 — Stage 1 Execution Runbook

**Status:** READY FOR CEO EXECUTION
**Date:** 2026-05-11
**Author:** Claude (CSO)
**Stage:** Layer 5 Stage 1 — Foundation
**Prerequisite:** Phase 8 Audit COMPLETE; Audit Cleanup Amendment LOCKED
**Effort estimate:** 2-4 working days CEO+CSO
**Filename:** INTERCEPTA_Stage_1_Execution_Runbook_2026-05-11.md

---

## §0 What This Runbook Is

This runbook walks through the **operational steps** to execute Layer 5 Stage 1 per L4.1 §2. The starter kit (`INTERCEPTA_Stage_1_Starter_Kit.tar.gz`) contains 25 files implementing the full Stage 1 deliverable set. This runbook tells you (CEO Akula) exactly what to do, in what order, with what verification at each step.

## §1 The 7 Stage 1 Operational Steps

```
Step 1: Extract starter kit + copy specs to local
   ↓
Step 2: Push to GitHub
   ↓
Step 3: Create conda env on Mac (CEO local dev)
   ↓
Step 4: Verify local smoke test passes
   ↓
Step 5: Onboard Northeastern Explorer
   ↓
Step 6: SLURM smoke test on Explorer
   ↓
Step 7: MLflow tracking server up
   ↓
[Stage 1 Handoff Criteria Met → Stage 2 begins]
```

---

## §2 Step 1 — Extract Starter Kit + Copy Specs Locally

### 2.1 On your Mac

```bash
# Choose where INTERCEPTA lives (default: ~/INTERCEPTA)
INTERCEPTA_ROOT=~/INTERCEPTA
mkdir -p "$INTERCEPTA_ROOT"
cd "$INTERCEPTA_ROOT"

# Extract starter kit
tar -xzf /path/to/INTERCEPTA_Stage_1_Starter_Kit.tar.gz
# Creates: code/ directory with 25 files
ls -la code/
```

### 2.2 Copy Phase B specs into the repo

The 12 Phase B specifications (10 + audit report + cleanup amendment) currently live in `/mnt/user-data/outputs/`. Copy them into the repo:

```bash
# From your Mac, after downloading the spec files locally:
cp INTERCEPTA_FV_L*.md "$INTERCEPTA_ROOT/code/docs/research/phase_b/"
cp INTERCEPTA_Phase_B_Phase_8_Audit_Report_*.md "$INTERCEPTA_ROOT/code/docs/research/phase_b/"
cp INTERCEPTA_Phase_B_Audit_Cleanup_Amendment_*.md "$INTERCEPTA_ROOT/code/docs/research/phase_b/"

# Verify all 12 specs in place
ls "$INTERCEPTA_ROOT/code/docs/research/phase_b/" | wc -l
# Should output: 13 (12 spec files + .gitkeep)
```

### 2.3 Step 1 Verification

- [ ] `~/INTERCEPTA/code/` exists with 25 files
- [ ] `~/INTERCEPTA/code/docs/research/phase_b/` contains 12 spec files
- [ ] `cat ~/INTERCEPTA/code/README.md` shows expected content

---

## §3 Step 2 — Push to GitHub

### 3.1 Initialize git in the repo

```bash
cd ~/INTERCEPTA/code

# Initialize as git repo
git init
git branch -M main

# Stage everything (respecting .gitignore)
git add .

# Verify what is staged (should NOT include any *.pyc, mlruns/, *.pt)
git status

# First commit
git commit -m "Stage 1 Foundation — initial repository skeleton

Per L4.1 §2.2 Stage 1 deliverables 1.1-1.5:
- Repository structure (intercepta/, tests/, scripts/, configs/)
- Python 3.11 environment.yml pinned per L4.1 + L4.3 §3.1
- GitHub Actions CI workflow
- Pre-commit hooks (ruff format + lint)
- SLURM smoke test for Northeastern Explorer
- MLflow tracking server scripts

Ensemble seeds {42, 1337, 2023, 9, 31337} per Audit Cleanup Amendment D13.

Phase 8 Audit COMPLETE; 8 of 8 audit passes CLEAN after cleanup.
"
```

### 3.2 Push to GitHub

```bash
# Per existing repo convention (github.com/AKULA-PRASAD/kaalcura)
git remote add origin git@github.com:AKULA-PRASAD/kaalcura.git
# OR if using HTTPS:
# git remote add origin https://github.com/AKULA-PRASAD/kaalcura.git

# Push
git push -u origin main
```

### 3.3 Step 2 Verification

- [ ] Repository visible on GitHub
- [ ] All 25 starter kit files + 12 spec files committed
- [ ] No model weights, no notebooks/.ipynb_checkpoints, no .pyc files
- [ ] First commit message includes Stage 1 reference

### 3.4 If You Encounter Issues

- **Permission denied on git push:** verify SSH key or use HTTPS + personal access token
- **Large file warnings:** check `.gitignore` is working; large binary files should not be in commit
- **Pre-commit hook errors on commit:** install hooks first: `pip install pre-commit && pre-commit install`

---

## §4 Step 3 — Create Conda Env on Mac (Local Dev)

### 4.1 Install Mambaforge (recommended) or Miniconda

Mambaforge is faster than vanilla conda for solving the env:

```bash
# Mambaforge install (if not already installed)
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-MacOSX-arm64.sh"
bash Mambaforge-MacOSX-arm64.sh
# Follow prompts; restart shell after install
```

### 4.2 Create the env

```bash
cd ~/INTERCEPTA/code

# Mamba (fast):
mamba env create -f environment.yml

# OR conda (slower):
conda env create -f environment.yml

# Activation
conda activate intercepta

# Verify version
python --version  # Should be 3.11.x
```

### 4.3 Install INTERCEPTA in editable mode

```bash
pip install -e .

# Should install with no errors
```

### 4.4 Step 3 Verification

- [ ] `conda env list` shows `intercepta`
- [ ] `python --version` reports Python 3.11.x
- [ ] `python -c "import intercepta; print(intercepta.__version__)"` outputs `0.0.1.dev0`
- [ ] `python -c "import torch; print(torch.__version__)"` outputs `2.2.x`
- [ ] `python -c "import scvi; print(scvi.__version__)"` outputs `1.1.x`

### 4.5 If You Encounter Issues

- **conda solver hangs:** use mamba; OR `conda config --set channel_priority strict`
- **pytorch-cuda not available on macOS:** Mac doesn't have CUDA; comment out `pytorch-cuda` and `cudatoolkit` in environment.yml (Mac uses MPS, not CUDA). Document this in `env_drift_log.md` per L4.3 §3.1.
- **scvi-tools install fails:** check Python is 3.11; scvi-tools requires Python ≥3.10

---

## §5 Step 4 — Verify Local Smoke Test Passes

### 5.1 Run pytest

```bash
cd ~/INTERCEPTA/code
conda activate intercepta

# Install pre-commit hooks
pre-commit install

# Run smoke test
pytest tests/test_smoke.py -v
```

Expected output:

```
tests/test_smoke.py::test_intercepta_imports PASSED
tests/test_smoke.py::test_python_version_compatible PASSED
tests/test_smoke.py::test_subpackages_importable PASSED
tests/test_smoke.py::test_pytorch_installed PASSED
tests/test_smoke.py::test_anndata_installed PASSED

5 passed in X.XX s
```

### 5.2 Run ruff lint + format check

```bash
ruff check intercepta tests
ruff format --check intercepta tests
```

Expected: no errors.

### 5.3 Step 4 Verification

- [ ] All 5 smoke tests pass
- [ ] ruff lint clean
- [ ] ruff format check clean

---

## §6 Step 5 — Onboard Northeastern Explorer

### 6.1 SSH to Explorer

```bash
ssh akula.pra@login.explorer.northeastern.edu
```

### 6.2 Verify GPU access via interactive session

```bash
# Request a small interactive GPU session
srun --partition=gpu --gres=gpu:a100:1 --time=00:10:00 --pty bash

# Inside the session:
nvidia-smi
# Should show A100 80GB (or A100 40GB) with no GPU processes running

# Exit when done
exit
```

### 6.3 Verify scratch quota

```bash
df -h /scratch/akula.pra/
# Should show ≥ 2 TB available per L4.1 §2.2 requirement 1.4
```

### 6.4 Clone repo on Explorer

```bash
cd /home/akula.pra
git clone git@github.com:AKULA-PRASAD/kaalcura.git INTERCEPTA
cd INTERCEPTA/code

# Verify all 25 files present
ls -la
```

### 6.5 Install conda env on Explorer

```bash
# If miniconda/mambaforge not already installed:
# curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh"
# bash Mambaforge-Linux-x86_64.sh

mamba env create -f environment.yml
conda activate intercepta
pip install -e .

# Verify
pytest tests/test_smoke.py -v
```

### 6.6 Create scratch dirs

```bash
mkdir -p /scratch/akula.pra/INTERCEPTA/{embeddings,kde,conformal,attribution,validation,mlflow,logs,beyondcell}
ls /scratch/akula.pra/INTERCEPTA/
```

### 6.7 Step 5 Verification

- [ ] SSH to Explorer works
- [ ] Interactive GPU session yields A100
- [ ] Scratch quota ≥ 2 TB
- [ ] Repo cloned at `/home/akula.pra/INTERCEPTA/`
- [ ] Conda env `intercepta` works on Explorer
- [ ] Local smoke test passes on Explorer
- [ ] All 8 scratch subdirs created

---

## §7 Step 6 — SLURM Smoke Test on Explorer

### 7.1 Submit the SLURM job

```bash
cd ~/INTERCEPTA/code
sbatch scripts/smoke_test.sh

# Note the job ID; e.g., "Submitted batch job 12345"
```

### 7.2 Monitor

```bash
# Check status
squeue -u akula.pra

# Once complete (or to view live):
tail -f /scratch/akula.pra/INTERCEPTA/logs/smoke_<JOBID>.out
```

### 7.3 Verify output

Expected contents of `smoke_<JOBID>.out`:
- "INTERCEPTA Stage 1 Smoke Test"
- nvidia-smi output showing A100
- Conda env info (Python 3.11, PyTorch 2.2, CUDA available)
- 5 pytest tests passing
- "Stage 1 Smoke Test COMPLETE"

### 7.4 Step 6 Verification

- [ ] SLURM job submitted successfully
- [ ] Job completed (state: COMPLETED, not FAILED)
- [ ] nvidia-smi output confirms A100 acquired
- [ ] pytest output shows 5/5 tests passing
- [ ] No errors in stderr log

### 7.5 If You Encounter Issues

- **Job stuck in PD (pending):** wait or check `sinfo` for partition availability
- **Job FAILED:** check stderr log; common: conda activation fails (adjust source path in smoke_test.sh)
- **OOM:** unlikely for smoke test; reduce batch size if any

---

## §8 Step 7 — MLflow Tracking Server Up

### 8.1 Start MLflow on Explorer login node

In one Explorer SSH session:

```bash
cd ~/INTERCEPTA/code
conda activate intercepta

# Start MLflow server in background
nohup ./scripts/mlflow_init.sh > /scratch/akula.pra/INTERCEPTA/logs/mlflow_server.log 2>&1 &

# Verify it's running
ps -ef | grep mlflow
```

### 8.2 Tunnel to your Mac

In a NEW terminal on your Mac:

```bash
ssh -L 5000:localhost:5000 akula.pra@login.explorer.northeastern.edu
# Keep this terminal open
```

Open browser to `http://localhost:5000` — should see MLflow UI.

### 8.3 Run MLflow test logging

Back in your Explorer session (or via SSH command):

```bash
cd ~/INTERCEPTA/code
conda activate intercepta
python scripts/mlflow_test_log.py
```

Refresh the MLflow UI in your browser. You should see:
- Experiment: `intercepta_stage_1_smoke`
- Run: `stage_1_smoke_test`
- Logged param: `stage = 1_foundation`
- Logged metric: `smoke_test_passed = 1.0`

### 8.4 Step 7 Verification

- [ ] MLflow server process running on Explorer
- [ ] MLflow UI accessible via SSH tunnel
- [ ] Test experiment logged and visible in UI

### 8.5 If You Encounter Issues

- **Port 5000 in use:** change `MLFLOW_PORT` in `scripts/mlflow_init.sh` to 5001; adjust tunnel accordingly
- **MLflow file backend permission errors:** verify `/scratch/akula.pra/INTERCEPTA/mlflow` exists and is writable

---

## §9 Stage 1 Handoff Criteria — Final Checklist

Per L4.1 §2.3:

- [ ] Repository structure created and pushed to GitHub
- [ ] Conda environment installs cleanly on Mac
- [ ] Conda environment installs cleanly on Explorer login node
- [ ] CI workflow runs and reports pass on a trivial test
- [ ] First SLURM job runs and writes output to scratch
- [ ] MLflow tracking server logs a test experiment

**When all 6 boxes checked: Stage 1 → Stage 2 handoff signed.** CEO and CSO joint sign-off.

Document the handoff in:
```
~/INTERCEPTA/code/docs/operational/stage_handoff_log.md
```

Example entry:
```
## Stage 1 → Stage 2 Handoff
Date: 2026-XX-XX
CEO signoff: Prasad Akula
CSO signoff: Claude

All 6 handoff criteria met:
- [x] Repository at github.com/AKULA-PRASAD/kaalcura (main branch, tag: stage-1-complete)
- [x] Conda env created on Mac (Python 3.11.x) and Explorer
- [x] CI workflow passes (workflow run #X)
- [x] SLURM job 12345 completed successfully
- [x] MLflow UI accessible; test experiment logged

Issues encountered + resolutions:
- [list any I-codes per L4.3 here]

Next: Stage 2 (Data Layer) begins.
```

After handoff: push git tag `stage-1-complete` to mark the milestone.

```bash
git tag -a stage-1-complete -m "Stage 1 Foundation complete — handoff to Stage 2"
git push origin stage-1-complete
```

---

## §10 What Happens After Stage 1

Per L4.1 §3, Stage 2 (Data Layer) begins:

- **Effort: 1-2 weeks**
- **Deliverables:** dataset loaders (GDSC, CCLE, CTRP, ...), cache layer, harmonization placeholder, IMPROVE splits
- **Handoff criterion added per Audit Cleanup Amendment D15:** scTOP V0+V1 on small subset validates harmonization sufficiency OR triggers L4.4 spec writing

Stage 2 is also CEO-heavy operational work (downloading GDSC, configuring data paths). CSO produces Stage 2 starter kit (code skeleton for loaders + cache + tests) once Stage 1 hands off.

The path to first empirical V0 AUROC result remains: **Stage 1 → 2 → 3 → 4 → 5 → 6 → 7 Day 1 (first V0 result)**.

---

## §11 Critical Reminders

### 11.1 Discipline

- **No commits to main without CI passing.** PR-based workflow if possible; if direct-to-main, run `pytest tests/` and `ruff check` BEFORE pushing.
- **No skipping handoff criteria.** All 6 must be checked off; if one fails, debug and re-execute that step.
- **Document every I-code encountered.** Per L4.3 §5.3, the operational log is the canonical record.

### 11.2 What You Are NOT Doing in Stage 1

- NOT downloading datasets (Stage 2)
- NOT training models (Stages 4-7)
- NOT writing substrate adapters (Stage 3)
- NOT running V0 evaluations (Stage 7)

Stage 1 is purely infrastructure. Resist the urge to "while we are at it, let me also..." — that scope creep is exactly what L4.1's stage discipline prevents.

### 11.3 Communication

- After each Step (1-7) completion: send CSO a brief status (1-2 sentences)
- After Stage 1 handoff: CSO produces Stage 2 starter kit
- If any step blocks > 1 day: escalate to CSO with the specific I-code per L4.3 detection matrix

---

## §12 Quick Reference

### 12.1 Key Paths

- **Mac repo:** `~/INTERCEPTA/code/`
- **Explorer repo:** `/home/akula.pra/INTERCEPTA/code/`
- **Explorer scratch:** `/scratch/akula.pra/INTERCEPTA/`
- **MLflow backend:** `/scratch/akula.pra/INTERCEPTA/mlflow`
- **Operational logs:** `~/INTERCEPTA/code/docs/operational/`

### 12.2 Key Commands

```bash
# Activate env
conda activate intercepta

# Run smoke test
pytest tests/test_smoke.py -v

# Lint
ruff check intercepta tests
ruff format --check intercepta tests

# SLURM smoke test
sbatch scripts/smoke_test.sh

# Conda env drift check (run before each session)
bash scripts/conda_env_check.sh
```

### 12.3 Anti-Patterns to Avoid

- ❌ Modifying environment.yml without documenting in `env_drift_log.md`
- ❌ Committing model weights, datasets, or large binaries
- ❌ Skipping the SLURM smoke test (Step 6) — Explorer integration must be validated in Stage 1
- ❌ Starting Stage 2 work before Stage 1 handoff signed

---

## §13 Provenance

### 13.1 Provenance

Runbook written by Claude (CSO, 2026-05-11) following Phase 8 Audit COMPLETE + Audit Cleanup Amendment LOCKED + CEO "do whichever best for our fullest vision true success proceed" signal indicating execution path forward.

### 13.2 Discipline Check Per Charter v1.2

- **P3 (research before code):** ✅ all 12 specs are read by Layer 5 (specs copied to repo at Step 1.2)
- **P15 (only honest science):** ✅ Step 7 verification + operational log requirements explicit
- **P16 (preserve past work):** ✅ specs preserved in repo; supersession discipline applies to future Stage amendments
- **Charter §5.3:** ✅ Stage 1 handoff criteria are the GO/NO-GO for Stage 2

### 13.3 What This Runbook IS and IS NOT

- IS: step-by-step operational execution guide for CEO
- IS NOT: a deviation from L4.1 §2 (it EXECUTES L4.1 §2)
- IS NOT: new architecture (purely operational)

### 13.4 Drift Catalog This Session

New drift instances introduced: 0.

### 13.5 Files Delivered This Session

- `INTERCEPTA_Stage_1_Starter_Kit.tar.gz` (25 files; the deployable repo skeleton)
- `INTERCEPTA_Stage_1_Execution_Runbook_2026-05-11.md` (this document)

---

— Stage 1 Execution Runbook PROPOSED 2026-05-11 by Claude (CSO).
— Awaiting CEO execution.
— After Stage 1 handoff: Stage 2 (Data Layer) begins. CSO produces Stage 2 starter kit.
