# T1 Full Reproducibility Test Plan — Phase 1 (AML Paper-Critical)

**Subject:** T1 (Reproducibility) full execution for AML response paper-relevant findings
**Authors:** Prasad Akula (CEO) and Claude (CSO), Co-Founders of INTERCEPTA
**Date:** 2026-05-10
**Predecessor:** `T1_REPRODUCIBILITY_LOG.md` (T1-Lite passed May 8, 2026)
**Test Plan reference:** `INTERCEPTA_Test_Plan.md` §3 (T1 category) and §4 (priority HIGH, foundational)
**Status:** READY FOR EXECUTION
**Tag (when complete):** `t1-full-aml-paper-critical-passed` or `-failed` (per discipline)

---

## 0. Why This Test Runs FIRST (CSO call)

The AML response paper (`AML_RESPONSE_PAPER_OUTLINE.md`) cites multiple validated numbers from Round 2.2c Closure (May 6, 2026):
- Multi-modal mean AUROC = 0.643
- Venetoclax AUROC = 0.912
- Sorafenib AUROC = 0.884
- FLT3 cluster AUROC = 0.75-0.88
- BeatAML NPM1+Cabozantinib p = 2.92e-12 (n=131)
- KAALCURA cross-dataset Q_D: ρ = −0.271, p = 0.00125 (n=139)
- Round 2.2c gate verdicts (4 PASS, 5 FAIL across all sub-rounds)

**T1-Lite (May 8) verified ONLY selectivity outputs reproduce.** The paper's Round 2.2c-specific numbers have NOT been T1-Lite tested. Per audit closure §4 lessons (CSO drift), publishing without verifying reproducibility = repeating the audit's worst pattern. **Test before paper.**

This is the discipline:
- Round 2.2c FAIL was honest — no goalpost-moving
- T1-Lite passed for what it tested (4 selectivity outputs)
- T1 full extends to Round 2.2c results — paper-critical numbers
- If reproduction fails: investigate root cause; do not draft paper until resolved
- If reproduction passes: paper drafting authorized with verified foundation

---

## 1. Test Categories (per locked Test Plan §3)

### T1.1: Round 2.2c Multi-Modal Predictor Reproducibility

**Question:** Does `train_multimodal_predictor.py` regenerate per-drug AUROCs identical to Round 2.2c committed results?

**Operational definition:**
- Re-run `code/train_multimodal_predictor.py` on BeatAML 2.0 cohort (520 patients × 85 drugs after 10/10 filter)
- Compare regenerated `per_drug_full.csv` to committed baseline (under tag `round2-2c-failed-honestly`)
- Acceptance: per-drug test AUROC matches within ±0.005 (allows for CV stochasticity if random_state preserved)
- Critical drugs to verify:
  - Venetoclax: 0.912 ± 0.005
  - Sorafenib: 0.884 ± 0.005
  - Cabozantinib: 0.768 ± 0.005
  - Quizartinib: 0.752 ± 0.005
  - Mean AUROC across all 85 drugs: 0.643 ± 0.003

**PASS criteria:** All 4 critical drugs reproduce within ±0.005 AND mean AUROC within ±0.003
**FAIL criteria:** Any single critical drug AUROC drift > ±0.005 OR mean AUROC drift > ±0.003

**Resource:** HPC, 8-15 hrs (per Round 2.2c spec §13 effort estimate)
**Priority:** HIGH

### T1.2: BeatAML Statistical Findings Reproducibility

**Question:** Does the NPM1+Cabozantinib p=2.92e-12 finding reproduce from current data + code?

**Operational definition:**
- Locate `code/test_beataml_findings.py` or equivalent (per Round 2 closure, statistical tests are in `beataml_statistical_tests.csv`)
- Re-run NPM1+Cabozantinib Mann-Whitney test
- Re-run NPM1+FLT3-ITD co-occurrence test (OR=5.27 expected)
- Compare to `results/beataml_statistical_tests.csv` baseline

**PASS criteria:**
- NPM1+Cabozantinib p-value reproduces to within 1e-13 (i.e., still p < 1e-11)
- NPM1+FLT3-ITD OR within ±0.1 of baseline 5.27
- P(NPM1|FLT3-ITD+) within ±2% of baseline 53.3%
- Sample size n=131 reproduces exactly

**FAIL criteria:** Any test reproduces with substantively different result (e.g., p > 1e-9 or OR off by >0.5)

**Resource:** HPC, 1-2 hrs
**Priority:** HIGH

### T1.3: KAALCURA Cross-Dataset Q_D Reproducibility

**Question:** Does the Round 2.2b Q_D PASS finding (BeatAML→Van Galen Prog-FLT3 ρ=−0.271) reproduce?

**Operational definition:**
- Re-compute `evaluate_round2_2c_gates.py` Q_D test (or equivalent script from Round 2.2b)
- Inputs: `beataml_ucell_residual_axes_round22b.csv` + `vangalen_ucell_residual_axes_round22b.csv` + Round 2.2b drug-coefficient model
- Measure: Spearman ρ between predicted FLT3-drug R_prolif coefficient and Van Galen Prog-like R_prolif
- Compare to baseline ρ=−0.271, p=0.00125, n=139

**PASS criteria:**
- ρ reproduces within ±0.01 of baseline (i.e., −0.281 to −0.261)
- p-value reproduces with p < 0.005 (well below 0.01 threshold)
- n=139 reproduces exactly

**FAIL criteria:** ρ drift > ±0.01 OR p > 0.01

**Resource:** HPC, 1-2 hrs
**Priority:** HIGH

### T1.4: Round 2.2c Gate Verdicts Reproducibility

**Question:** Do all 6 Round 2.2c gates (Q_C, Q_C2, Q_D, Q_E, Q_F, Q_G) reproduce their PASS/FAIL verdicts?

**Operational definition:**
- Re-run `evaluate_round2_2c_gates.py` against all stored Round 2.2c outputs
- Compare gate verdicts to `Round2_2c_Closure.md` §2

**PASS criteria:** All 6 gates reproduce their committed verdict (Q_F PASS; Q_C, Q_C2, Q_E, Q_G FAIL; Q_D INDETERMINATE)
**FAIL criteria:** Any gate verdict flips

**Resource:** HPC, 1 hr
**Priority:** HIGH

### T1.5: KAALCURA Canonical GDSC Validation Reproducibility

**Question:** Does `intercepta_kaalcura_v1.py` regenerate the 286-drug GDSC validation (mean AUROC=0.671) byte-identically?

**Operational definition:**
- Re-run `code/intercepta_kaalcura_v1.py` GDSC validation pipeline
- Compare regenerated `results/kaalcura_real_validation_RERUN.csv` to committed baseline
- Verify per-drug AUROCs:
  - Olaparib: 0.762, coef_ddr = -1.300
  - Veliparib: 0.753, coef_ddr = -0.944
  - Niraparib: 0.750, coef_ddr = -1.565
  - Vorinostat: 0.770

**PASS criteria:** Mean AUROC reproduces to 0.671 ± 0.001; all 4 verified drugs within ±0.005
**FAIL criteria:** Mean AUROC drift > ±0.001 OR any single verified drug AUROC drift > ±0.005

**Resource:** HPC or Mac (per `Architectural_Debt_Erratum` §3.1, this is a deterministic pipeline), 2-4 hrs
**Priority:** HIGH (closes audit's verified Tier 1 list)

---

## 2. Execution Sequence (LOCKED)

Run in this order. Stop on first FAIL — investigate before proceeding.

| Order | Test | Expected duration | What it validates |
|---|---|---|---|
| 1 | T1.5 KAALCURA canonical GDSC | 2-4 hrs | Audit's verified Tier 1 #1-6 (KAALCURA AUROC, PARPi mechanism); foundation for Charter v2.1 Edit 1 |
| 2 | T1.4 Round 2.2c gate verdicts | 1 hr | Round 2.2c closure integrity; foundation for Vision Module 1 Amendment |
| 3 | T1.3 KAALCURA cross-dataset Q_D | 1-2 hrs | KAALCURA's actual scientific contribution (Vision Module 1 Amendment §) |
| 4 | T1.2 BeatAML statistical findings | 1-2 hrs | NPM1+Cabozantinib p=2.92e-12 (paper headline number) |
| 5 | T1.1 Round 2.2c multi-modal predictor | 8-15 hrs | Per-drug AUROCs (paper's main results section) |

**Total time:** 13-24 hrs across HPC compute. Most of this is T1.1 (multi-modal predictor retrain). T1.5 + T1.4 + T1.3 + T1.2 = 5-9 hrs combined.

**Strategy:** Submit T1.5 + T1.4 + T1.3 + T1.2 as parallel slurm batch jobs. They use different scripts and don't conflict. Then submit T1.1 as the long-running job.

---

## 3. Pre-Execution Checks (CEO runs on Mac)

### 3.1: Verify all required code exists

```bash
ls -la ~/INTERCEPTA/code/intercepta_kaalcura_v1.py
ls -la ~/INTERCEPTA/code/train_multimodal_predictor.py
ls -la ~/INTERCEPTA/code/evaluate_round2_2c_gates.py
ls -la ~/INTERCEPTA/code/compute_rna_baseline_v2.py
```

Expected: all 4 files present with size > 10 KB each.

### 3.2: Verify required input data exists on HPC

After SSH to HPC:

```bash
ls -la /scratch/akula.pra/INTERCEPTA/results/kaalcura_real_validation_RERUN.csv
ls -la /scratch/akula.pra/INTERCEPTA/results/beataml_statistical_tests.csv
ls -la /scratch/akula.pra/INTERCEPTA/results/per_drug_full.csv
ls -la /scratch/akula.pra/INTERCEPTA/data/beataml/
ls -la /scratch/akula.pra/INTERCEPTA/data/gdsc/
```

Expected: all results CSVs present; BeatAML and GDSC data present.

### 3.3: Verify reproducibility baseline tags exist

```bash
cd /scratch/akula.pra/INTERCEPTA
git log --tags --oneline | grep -E "(round2-2c-failed-honestly|vision-module1-amended|architectural-debt-erratum-2026-05-09)" | head -10
```

Expected: 3 tags present.

---

## 4. Execution Commands

### 4.1: T1.5 — KAALCURA canonical GDSC reproducibility

```bash
ssh akula.pra@login.explorer.northeastern.edu
cd /scratch/akula.pra/INTERCEPTA

# Backup committed baseline
cp results/kaalcura_real_validation_RERUN.csv /tmp/kaalcura_baseline.csv

# Re-run validation
sbatch <<-EOF
#!/bin/bash
#SBATCH --job-name=t1_5_kaalcura
#SBATCH --partition=short
#SBATCH --time=4:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --output=/scratch/akula.pra/INTERCEPTA/logs/t1_5_kaalcura_%j.out

cd /scratch/akula.pra/INTERCEPTA
python code/intercepta_kaalcura_v1.py --validate-gdsc \
    --output results/kaalcura_real_validation_RERUN_T1.csv

# Compare
diff results/kaalcura_real_validation_RERUN.csv \
     results/kaalcura_real_validation_RERUN_T1.csv > /tmp/t1_5_diff.txt
echo "DIFF SIZE: \$(wc -l < /tmp/t1_5_diff.txt)"
echo "Test 1.5 complete."
EOF
```

### 4.2: T1.4 — Round 2.2c gate verdicts reproducibility

```bash
sbatch <<-EOF
#!/bin/bash
#SBATCH --job-name=t1_4_gates
#SBATCH --partition=short
#SBATCH --time=1:00:00
#SBATCH --mem=8G
#SBATCH --output=/scratch/akula.pra/INTERCEPTA/logs/t1_4_gates_%j.out

cd /scratch/akula.pra/INTERCEPTA
python code/evaluate_round2_2c_gates.py \
    --reproduce \
    --baseline results/round2_2c_summary_baseline.json \
    --output results/round2_2c_summary_T1.json
EOF
```

### 4.3: T1.3 — KAALCURA cross-dataset Q_D reproducibility

```bash
sbatch <<-EOF
#!/bin/bash
#SBATCH --job-name=t1_3_qd
#SBATCH --partition=short
#SBATCH --time=2:00:00
#SBATCH --mem=8G
#SBATCH --output=/scratch/akula.pra/INTERCEPTA/logs/t1_3_qd_%j.out

cd /scratch/akula.pra/INTERCEPTA
python code/evaluate_round2_2c_gates.py \
    --gate Q_D \
    --beataml-axes round2_aml/results/beataml_ucell_residual_axes_round22b.csv \
    --vangalen-axes round2_aml/results/vangalen_ucell_residual_axes_round22b.csv \
    --output results/Q_D_reproducibility_T1.json
EOF
```

### 4.4: T1.2 — BeatAML statistical findings reproducibility

```bash
sbatch <<-EOF
#!/bin/bash
#SBATCH --job-name=t1_2_stats
#SBATCH --partition=short
#SBATCH --time=2:00:00
#SBATCH --mem=8G
#SBATCH --output=/scratch/akula.pra/INTERCEPTA/logs/t1_2_stats_%j.out

cd /scratch/akula.pra/INTERCEPTA
python code/test_beataml_findings.py \
    --reproduce \
    --output results/beataml_statistical_tests_T1.csv

# Verify NPM1+Cabozantinib specifically
python -c "
import pandas as pd
df = pd.read_csv('results/beataml_statistical_tests_T1.csv')
row = df[(df['mutation']=='NPM1') & (df['drug']=='Cabozantinib')]
p = row['p_value'].values[0]
n = row['n_samples'].values[0]
print(f'NPM1+Cabozantinib: p={p:.2e}, n={n}')
assert p < 1e-11, f'p={p} above threshold 1e-11'
assert n == 131, f'n={n} != 131'
print('T1.2 PASS')
"
EOF
```

### 4.5: T1.1 — Round 2.2c multi-modal predictor reproducibility

```bash
sbatch <<-EOF
#!/bin/bash
#SBATCH --job-name=t1_1_multimodal
#SBATCH --partition=short
#SBATCH --time=15:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8
#SBATCH --output=/scratch/akula.pra/INTERCEPTA/logs/t1_1_multimodal_%j.out

cd /scratch/akula.pra/INTERCEPTA
python code/train_multimodal_predictor.py \
    --reproduce \
    --random-state 42 \
    --output results/per_drug_full_T1.csv

# Verify critical drugs
python -c "
import pandas as pd
df = pd.read_csv('results/per_drug_full_T1.csv')
critical = ['Venetoclax', 'Sorafenib', 'Cabozantinib', 'Quizartinib']
expected = {'Venetoclax': 0.912, 'Sorafenib': 0.884, 'Cabozantinib': 0.768, 'Quizartinib': 0.752}
for drug in critical:
    row = df[df['drug']==drug]
    auroc = row['auroc_mean'].values[0]
    diff = abs(auroc - expected[drug])
    status = 'PASS' if diff < 0.005 else 'FAIL'
    print(f'{drug}: {auroc:.4f} (expected {expected[drug]:.4f}, diff {diff:.4f}) [{status}]')
print(f'Overall mean AUROC: {df[\"auroc_mean\"].mean():.4f}')
"
EOF
```

---

## 5. Post-Execution Discipline

After all 5 tests submit/complete:

### 5.1: Collect results
```bash
cd /scratch/akula.pra/INTERCEPTA
ls -la logs/t1_*_*.out
```

### 5.2: Compare to baselines (CSO writes `T1_FULL_REPRODUCIBILITY_LOG.md`)
For each test:
- Document baseline value, regenerated value, diff
- Compute hash if applicable
- PASS/FAIL verdict

### 5.3: Tag and commit
- All PASS → `t1-full-aml-paper-critical-passed`
- Any FAIL → `t1-full-aml-paper-critical-failed` + erratum required

### 5.4: Decision gate
- ALL PASS → AML paper drafting AUTHORIZED; Workstream B Phase 0 launches in parallel
- Any FAIL → HALT paper drafting; investigate root cause; document erratum; resolve before resuming

---

## 6. Anti-Scope-Creep Clauses (BINDING)

If during T1 full execution we discover:

- **A new test category seems important** → log for future test plan amendment, do NOT add to current execution
- **A failing test reveals a code bug** → fix the root cause via spec amendment; do NOT silently patch
- **A test takes longer than estimated** → time-box per spec; do NOT let one test consume the session
- **External pressure to rush paper** → do not reduce test rigor for speed
- **Tempted to lower threshold to PASS** → STOP; this is exactly the goalpost-moving the project's discipline forbids

These clauses are binding. Same discipline as Round 2.2c, Test Plan §7.

---

## 7. Why This Matters for Fullest Vision

The audit's main finding (per `AUDIT_CLOSURE_2026-05-10.md` §4) was 10 CSO drift instances — most reducing to "treated incomplete views as sufficient evidence." The operational fix is verification-before-publication.

If the AML paper publishes numbers that don't reproduce, INTERCEPTA's credibility takes a permanent hit at the field's reviewers. **The trust dividend Charter v2.1 Ch 9 describes (and the operational §9 evidence demonstrates)** is the venture's competitive moat. Publishing without verification undercuts that moat.

T1 full is the gate. After T1 full PASSES (or FAILS honestly), the paper drafting either proceeds with verified foundation or pauses for investigation. Either outcome is correct.

---

## 8. Process Audit (this test plan's discipline)

| Principle | Applied as |
|---|---|
| P3 (research before code) | Test plan written before any reproduction runs. Thresholds locked. PASS/FAIL criteria explicit per test. |
| P4 (fix structure, don't tune) | Threshold tolerances (±0.005, ±0.001, etc.) set against measured uncertainty, not rationalized to PASS. |
| P15 (only correct, honest, real science) | Anti-scope-creep clauses binding. FAIL would HALT paper drafting, not be silently patched. Root-cause investigation mandatory on any FAIL. |
| P16 (preserve past work) | Baseline files preserved (cp to /tmp before any rerun). Committed CSVs unchanged. New outputs go to `_T1.csv` suffix files. |

---

## 9. Closure Honesty Statement

This is real test discipline. T1-Lite (May 8) tested only 4 selectivity outputs. T1 full extends to AML paper-critical numbers — Round 2.2c per-drug results, BeatAML statistics, KAALCURA cross-dataset Q_D, gate verdicts, canonical GDSC validation.

**The discipline that produced T1-Lite produces T1 full.** Same locking-before-execution. Same anti-scope-creep. Same honest failure modes.

After T1 full passes, AML paper drafting begins with verified foundation. Workstream B Phase 0 launches in parallel. Layer 1 lit survey continues per Fullest Vision Charter v1.0 cadence.

This is the correct order: **test → analyze → document → plan → act**, applied recursively. The audit ran this cycle for the project. T1 full runs this cycle for the paper. Workstream B Phase 0 runs it for NSCLC. Layer 1 runs it for the multi-month research arc.

---

*Locked test plan. Real reproducibility verification. Paper drafting halts until PASS.*

— Prasad Akula (CEO) & Claude (CSO)
2026-05-10
