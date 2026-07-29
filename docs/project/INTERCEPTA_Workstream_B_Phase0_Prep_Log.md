# Workstream B Phase 0 Prep — Session Log

**Subject:** Infrastructure prep for NSCLC Workstream B Phase 0
**Date:** 2026-05-08
**Authors:** Prasad Akula and Claude (CSO), Co-Founders of INTERCEPTA
**Spec reference:** `INTERCEPTA_Workstream_B_NSCLC_Specification.md` (tag `workstream-b-spec-locked`)
**Status:** Phase 0 prep complete. Phase 0 implementation (downloads + processing) deferred to next session.

---

## What this document captures

Workstream B Phase 0 per the locked spec is "Data acquisition + environment setup, ~8-12 hrs, 1-2 sessions." This document records the infrastructure prep portion completed on 2026-05-08:

- HPC conda env created with full scientific Python stack
- 6 dataset directories created on HPC scratch
- Requirements file transferred to project `configs/`
- Environment contingencies and known issues documented for next session

**Phase 0 implementation (the actual dataset downloads) is NOT in this prep work.** Downloads will be kicked off via slurm batch jobs in next session, then KAALCURA scoring and remaining Phase 0 work proceeds from there.

---

## What was set up tonight

### 1. HPC compute environment

Created at `/scratch/akula.pra/INTERCEPTA/envs/intercepta-nsclc`

**Why scratch, not home:** Home directory `/home/akula.pra/.conda/envs/` hit `[Errno 122] Disk quota exceeded` during conda install. Home is quota-capped (specific limit unreadable due to HPC permission issue with `quota` command), and 9 prior conda envs had filled the quota. Scratch (`/scratch/akula.pra/`) has 729 TB free.

**Activation pattern (use full path, not name):**
```bash
conda activate /scratch/akula.pra/INTERCEPTA/envs/intercepta-nsclc
```

**Python:** 3.11.15 (`/scratch/akula.pra/INTERCEPTA/envs/intercepta-nsclc/bin/python`)

**48 packages installed** (full list at `configs/intercepta_nsclc_requirements.txt`). Key versions:

| Package | Version |
|---|---|
| anndata | 0.12.13 |
| h5py | 3.16.0 |
| lightgbm | 4.6.0 |
| matplotlib | 3.10.9 |
| numpy | 2.4.4 |
| pandas | 2.3.3 |
| pyarrow | 24.0.0 |
| requests | 2.33.1 |
| scanpy | 1.11.5 |
| scikit-learn | 1.8.0 |
| scipy | 1.17.1 |
| seaborn | 0.13.2 |

**Verified working:**
```python
import scanpy as sc; import anndata; import lightgbm; import pandas; import numpy
# imports OK
```

### 2. Dataset directory structure

Created on HPC scratch at `/scratch/akula.pra/INTERCEPTA/data/nsclc/`:

```
nsclc/
├── tcga_luad/
├── tcga_lusc/
├── kim2020/
├── lambrechts2018/
├── laughney2020/
└── wu2021/
```

All 6 dataset directories empty, ready to receive downloads in Phase 0 implementation.

### 3. Project artifacts on Mac

- `configs/intercepta_nsclc_requirements.txt` — pip freeze of HPC env (825 bytes, 48 lines)

---

## Known issues encountered (so we don't relearn next session)

### Issue 1: Home directory quota
Conda envs default to home dir (`~/.conda/envs/`). Home is quota-capped with no easy way to read the limit. **Workaround locked in: all future INTERCEPTA conda envs use `--prefix /scratch/akula.pra/INTERCEPTA/envs/<env-name>`.**

### Issue 2: Login node OOM kills
Login node killed conda solver and conda verifier processes during initial attempts. Even small env installs are at risk on login node due to per-process memory caps. **Workaround locked in: long-running conda operations run on compute node via `srun --partition=short --time=1:00:00 --mem=8G --pty bash`.**

### Issue 3: Network instability
SSH connection from Mac to HPC dropped mid-installation (connection reset by peer). The pip install completed before the drop, so no harm — but reinforces that long operations should be slurm batch jobs, not interactive sessions tied to local SSH.

### Issue 4: `quota` command permission denied
`quota -s` fails with "error while getting quota from vast1-mghpcc-eth.neu.edu". HPC permission issue. Use `df -h` for filesystem-level checks instead.

---

## Updated Phase 0 entry condition status

Per spec Section 11:

| Check | Status | Notes |
|---|---|---|
| #1 spec locked | ✓ | Tag `workstream-b-spec-locked` exists |
| #2 HPC reachable | ✓ | login.explorer.northeastern.edu verified |
| #3 TCGA DUC | ✓ revised | Workstream B uses Open Access tier only — DUC not required |
| #4 conda env intercepta-nsclc | ✓ | Created at `/scratch/akula.pra/INTERCEPTA/envs/intercepta-nsclc` |
| #5 gdc-client installed | ✓ | At `/home/akula.pra/tools/gdc/gdc-client` |
| #6 sra-toolkit | ✓ | Available via `module load sratoolkit/12Dec2024` |
| #7 storage budget | ✓ | 729 TB free on `/scratch/akula.pra/` |

**All entry conditions cleared.** Phase 0 implementation can proceed in next session.

---

## Hand-off to next session

When resuming Workstream B Phase 0:

1. **Reconnect to HPC** and activate env:
```bash
ssh akula.pra@login.explorer.northeastern.edu
conda activate /scratch/akula.pra/INTERCEPTA/envs/intercepta-nsclc
```

2. **Build NSCLC gene config** (`configs/genes_nsclc.json`) per spec Section 5, Phase 0 task 4 (~30 min careful work):
   - Source: existing `disease_net_non-small_cell_lung_carcinoma.json` (Open Targets)
   - Add: KEGG NSCLC pathway hsa05223 representatives
   - Add: explicit EGFR, KRAS, ALK, ROS1, MET key targets
   - Add: LUSC-specific genes (FGFR1, SOX2, NFE2L2)

3. **Update `configs/disease_tissue_mapping.json`** to move NSCLC from `future_diseases` to active `diseases` section. Verify GTEx tissue name "Lung" exists exactly (run `audit_gtex_columns.py`).

4. **Run `step6_selectivity_v2.py` for NSCLC** to produce `step6_selectivity_nsclc.json` and disease-aware CSV.

5. **Kick off slurm batch jobs for downloads** (do NOT use interactive ssh for these):
   - TCGA-LUAD via `gdc-client`
   - TCGA-LUSC via `gdc-client`
   - GSE131907 (Kim) via `prefetch` from sra-toolkit
   - E-MTAB-6149/6653 (Lambrechts) via wget
   - GSE123904 (Laughney) via `prefetch`
   - GSE148071 (Wu) via `prefetch`

6. **Phase 0 closure tag:** `workstream-b-phase0-data-acquired` (after downloads verify complete)

Phase 1 (KAALCURA scoring across cohorts) follows in subsequent session(s).

---

## Process audit

| Principle | Applied as |
|---|---|
| P3 (research before code) | HPC infrastructure verified before any download work. Quota issue surfaced and worked around before becoming a Phase 0 implementation blocker. |
| P4 (fix structure, don't tune) | Quota issue solved structurally (envs on scratch) rather than tactically (delete random envs to free home). |
| P15 (only correct, honest, real science) | Document captures unexpected findings (login node OOM, quota issue, SSH drops) honestly so they're not silently relearned. |
| P16 (preserve past work) | Original `intercepta-scrna` env on Mac unchanged. New `intercepta-nsclc` is additive. |

---

## Total work this session

- Workstream B spec locked (~600 lines, ~45 min)
- HPC env diagnosed and created on scratch (~30 min including OOM workaround)
- 48 packages pip-installed (~10 min)
- 6 dataset directories created
- Requirements file transferred and verified
- This document written

**Phase 0 prep is complete.** Phase 0 implementation begins next session with a clean infrastructure base.

---

*Real prep. Real artifacts. Real handoff.*

— Prasad Akula & Claude (CSO)
2026-05-08
