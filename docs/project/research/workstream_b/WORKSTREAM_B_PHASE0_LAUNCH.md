# Workstream B Phase 0 — Launch Instructions

**Date:** 2026-05-10
**Authors:** Prasad Akula (CEO) and Claude (CSO), Co-Founders of INTERCEPTA
**Status:** Ready to launch. Slurm scripts pre-existing per `INTERCEPTA_Workstream_B_Phase0_Prep_Log.md` (May 8, 2026).
**Predecessor:** `audit-closure-2026-05-10` halt lift; Charter v2.1 amendments per `CHARTER_V2_1_EDIT_PLAN.md`

---

## 0. Overview

Workstream B Phase 0 implementation = downloading the 4 datasets needed for NSCLC analysis:

1. **LuCA Salcher 2022** (NSCLC harmonized atlas, ~1.2M cells, 29 source studies)
2. **Wu 2021 GSE148071** (independent validation cohort, 89,887 cells, LUAD/LUSC labeled)
3. **TCGA-LUAD** (bulk RNA + mutations + clinical, ~600 patients)
4. **TCGA-LUSC** (bulk RNA + mutations + clinical, ~500 patients)

Per `INTERCEPTA_Workstream_B_Spec_Erratum_LuCA.md` (May 8, 2026), the original 4-cohort design (Kim, Lambrechts, Laughney, Wu) was amended to 2-cohort (LuCA + Wu) plus TCGA-LUAD/LUSC. **LuCA already includes Kim and Laughney as source studies; Lambrechts is R-only (not Python-readable).** The amended design has cleaner statistical independence than original.

These are slurm batch jobs — they run in background on HPC and don't block other CSO work. **Launch now; downloads complete over hours-to-days.**

---

## 1. Pre-Flight Check (CEO runs on Mac)

Confirm slurm scripts exist on HPC:

```bash
ssh akula.pra@login.explorer.northeastern.edu
ls -la /scratch/akula.pra/INTERCEPTA/code/slurm/ | grep -E "(luca|tcga|wu)"
```

Expected output: `download_luca.slurm`, `download_tcga.slurm` or `download_tcga_v2.slurm`, `download_wu.slurm`.

If scripts missing on HPC (only in local sandbox), CEO syncs first:

```bash
# Run from Mac terminal (not HPC)
rsync -avz ~/INTERCEPTA/code/slurm/ akula.pra@login.explorer.northeastern.edu:/scratch/akula.pra/INTERCEPTA/code/slurm/
```

---

## 2. Launch Sequence (CEO runs on HPC after SSH)

After SSH'd into HPC, submit jobs in this order:

### Step 2.1: Create logs directory
```bash
mkdir -p /scratch/akula.pra/INTERCEPTA/logs
```

### Step 2.2: Submit LuCA download (longest, ~4 hours)
```bash
cd /scratch/akula.pra/INTERCEPTA/code/slurm
sbatch download_luca.slurm
```

Expected response: `Submitted batch job NNNNNN` (note the job ID).

### Step 2.3: Submit TCGA-LUAD/LUSC download (~8 hours)
```bash
sbatch download_tcga_v2.slurm
```

(Use `download_tcga_v2.slurm` — the v2 fixes the manifest format issue from v1 per `Workstream B Phase 0 Prep Log` Issue 4.)

### Step 2.4: Submit Wu 2021 download (~2 hours)
```bash
sbatch download_wu.slurm
```

### Step 2.5: Verify jobs submitted
```bash
squeue -u akula.pra
```

Expected output: 3 jobs with status `PD` (pending) or `R` (running).

---

## 3. Monitoring (run periodically)

Check job status:
```bash
squeue -u akula.pra
```

Check job output (after job starts):
```bash
tail -f /scratch/akula.pra/INTERCEPTA/logs/luca_download_NNNNNN.out
tail -f /scratch/akula.pra/INTERCEPTA/logs/tcga_download_v2_NNNNNN.out
tail -f /scratch/akula.pra/INTERCEPTA/logs/wu_download_NNNNNN.out
```

Replace `NNNNNN` with actual job IDs from Step 2.2-2.4.

Verify download success:
```bash
ls -la /scratch/akula.pra/INTERCEPTA/data/nsclc/luca_salcher2022/
ls -la /scratch/akula.pra/INTERCEPTA/data/nsclc/wu2021/
ls -la /scratch/akula.pra/INTERCEPTA/data/nsclc/tcga_luad/
ls -la /scratch/akula.pra/INTERCEPTA/data/nsclc/tcga_lusc/
```

Each directory should contain dataset files (h5ad for LuCA/Wu; counts/mutations/clinical for TCGA).

---

## 4. Phase 0 Closure Conditions

Phase 0 closes when ALL of:

- [ ] LuCA download complete and h5ad file readable in scanpy
- [ ] Wu 2021 download complete and per-sample matrices readable
- [ ] TCGA-LUAD download complete with RNA + MAF + clinical files
- [ ] TCGA-LUSC download complete with RNA + MAF + clinical files
- [ ] Disk space verified (no failed-mid-download artifacts)
- [ ] Logs reviewed for any errors

When all check, **CEO commits and tags `workstream-b-phase0-data-acquired`**. CSO then begins Phase 1 (KAALCURA scoring across cohorts).

---

## 5. What CSO Does in Parallel

While downloads run, CSO produces the AML response paper draft (`AML_RESPONSE_PAPER_OUTLINE.md`). Both tracks advance simultaneously without resource conflict:

- **Workstream B downloads**: HPC batch jobs (background)
- **AML paper drafting**: CSO/CEO chat session work (foreground)

Estimated time to AML paper outline complete: 1 session.
Estimated time to all Workstream B downloads complete: hours-to-days (unattended).

When both complete:
- Workstream B Phase 1 begins (KAALCURA scoring)
- AML paper drafting continues (results/methods sections)

---

## 6. If Downloads Fail

Per `Workstream B Phase 0 Prep Log` Issue 1-4:

- **Quota issues**: `df -h /scratch/akula.pra` to verify space; 729 TB free expected
- **Login node OOM**: not relevant for batch jobs (compute nodes have larger memory)
- **Network instability**: slurm jobs survive SSH disconnections (that's why we use slurm)
- **gdc-client manifest format**: v2 script uses correct `manifests_v2/` directory (GDC API return_type=manifest format)

If a job fails:
```bash
cat /scratch/akula.pra/INTERCEPTA/logs/<job>_NNNNNN.err
```
Diagnose, fix, resubmit. Document the failure in a follow-up erratum if it required spec amendment.

---

## 7. Process Audit

| Principle | Applied as |
|---|---|
| P3 (research before code) | Workstream B Spec locked May 7 (`workstream-b-spec-locked`); Erratum amended May 8 (`workstream-b-spec-erratum-luca`); Phase 0 Prep Log captured infrastructure issues May 8. Downloads launch only after spec is locked and amended. |
| P4 (fix structure, don't tune) | LuCA cohort substitution fixes statistical independence flaw in original 4-cohort design (Kim and Laughney already in LuCA). Hypothesis thresholds tightened, not loosened. |
| P15 (only correct, honest, real science) | Cohort design honest about Lambrechts incompatibility. AML → Whole_Blood proxy disclosed. Phase 0 closure conditions explicit (4 datasets verified before Phase 1 begins). |
| P16 (preserve past work) | Original Workstream B spec preserved at tag `workstream-b-spec-locked`; erratum amends without rewriting history. Phase 0 Prep Log preserves infrastructure issues for future reference. |

---

## 8. Closure Honesty Statement

This is mechanical execution work. Phase 0 Prep Log (May 8) did the planning. The slurm scripts exist. The HPC environment is ready. All that's left is to submit the jobs and wait.

The discipline that applied to spec-writing applies here too: **submit per spec, monitor, document failures openly, don't move forward until all 4 datasets verified.**

After Phase 0 closes, Phase 1 (KAALCURA scoring across LuCA + Wu + TCGA-LUAD/LUSC) begins. That's where new science happens. This launch is plumbing, but it's the plumbing without which the science can't.

---

*Real launch instructions. Pre-existing slurm scripts. Background batch execution. Phase 0 implementation begins now.*

— Prasad Akula (CEO) & Claude (CSO)
2026-05-10
