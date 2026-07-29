# T1-Lite Reproducibility Test — Execution Log

**Test category:** T1 Reproducibility (lite scope per test plan section 6)
**Subject:** Reproducibility of `step6_selectivity_v2.py` outputs across 4 diseases (mCRPC, AML, GBM, NSCLC)
**Authors:** Prasad Akula and Claude (CSO), Co-Founders of INTERCEPTA
**Date:** 2026-05-08
**Tag references:** `test-plan-locked` (precondition); this document closes with `t1-lite-passed`

---

## 1. Verdict

**PASS. 4 of 4 diseases reproduced their committed selectivity JSONs identically (excluding `computed` timestamp field).**

This satisfies the lightest reproducibility precondition specified in test plan section 6.

## 2. What this test checked

Per locked test plan section 6:

> Re-run `step6_selectivity_v2.py` for all 4 diseases. Verify outputs match committed JSONs (excluding `computed` timestamp).

This was the lightest reproducibility check possible:

- Confirms script runs end-to-end without errors
- Confirms script produces same numerical outputs from same inputs
- Confirms environment did not silently drift between baseline (08:10) and rerun (17:05)

## 3. What this test does NOT prove

Honest scope statement:

- Does NOT verify the multi-modal predictor reproduces (separate test, requires HPC + BeatAML data)
- Does NOT verify the KAALCURA cross-dataset signal reproduces (separate test, requires BeatAML + Van Galen)
- Does NOT verify Round 2.2c findings reproduce
- Does NOT verify Workstream B Phase 0 outputs (still in flight)
- Does NOT verify computational correctness (only consistency with itself)

These are explicitly future tests in the locked test plan.

## 4. Procedure executed

1. Listed committed JSONs and confirmed all 4 present (08:10 timestamp from earlier today)
2. Ran `python code/step6_selectivity_v2.py` (single invocation, processes all 4 diseases internally)
3. Confirmed script's internal validation reported "Overall: PASS" (criteria 1, 3, 4 all PASS)
4. Used `git diff` to verify byte-level output stability against committed baseline
5. Confirmed all diffs were timestamp-only (single line changed per file)
6. Reverted timestamp-only diffs to keep working tree clean

## 5. Results per disease

| Disease | Genes found | Primary tissue | Diff vs baseline | Verdict |
|---|---|---|---|---|
| mCRPC  | 38/38 | Prostate          | 1 line: timestamp only | PASS |
| AML    | 32/32 | Whole Blood       | 1 line: timestamp only | PASS |
| GBM    | 30/30 | Brain - Cortex    | 1 line: timestamp only | PASS |
| NSCLC  | 33/33 | Lung              | 1 line: timestamp only | PASS |

## 6. Specific numerical preservation

Real measurements from committed JSONs that are now confirmed reproducible:

| Disease | Top selectivity gene | Ratio vs mean | Classification |
|---|---|---|---|
| mCRPC  | KLK3  | 16695.58 | HIGHLY_SELECTIVE |
| AML    | JAK3  | 15.84    | HIGHLY_SELECTIVE |
| GBM    | FGFR3 | 2.43     | MODERATE_TISSUE_SELECTIVE |
| NSCLC  | ROS1  | 83.08    | HIGHLY_SELECTIVE |

These are the values committed at tags `selectivity-redesign-complete`, `selectivity-phase4-mcrpc-shipped`, `vision-module1-amended`, and `workstream-b-phase0-selectivity-shipped`. They are now confirmed to regenerate identically from current Mac environment.

## 7. Internal script self-validation (separate signal)

The script also runs its own validation criteria from the spec (Section 10 of the selectivity redesign spec):

- Criterion 1 (no `prostate_tpm` field in non-mCRPC results): PASS
- Criterion 3 (AML has non-zero target genes — FLT3, NPM1, IDH1, IDH2 found): PASS
- Criterion 4 (GBM has non-zero target genes — EGFR, IDH1, PTEN, TP53 found): PASS

These are independent of T1-Lite hash-comparison but provide additional reproducibility evidence.

## 8. Diff evidence

Sample diff (mCRPC; same shape for all 4):

```
@@ -355,7 +355,7 @@
       "safety_classification": "HIGHLY_SELECTIVE"
     }
   },
-  "computed": "2026-05-08T08:10:21",
+  "computed": "2026-05-08T17:05:08",
   "module_version": "step6_selectivity_v2",
   "spec_reference": "..."
}
```

Single line changed. Only `computed` timestamp field. Test plan section 6 explicitly excludes this field from match check.

## 9. Process audit

| Principle | Applied as |
|---|---|
| P3 (research before code) | Test plan was locked before this test was written. T1-Lite was section 6 of locked plan. |
| P4 (fix structure, don't tune) | No threshold adjustment. PASS criteria locked before execution. |
| P15 (only correct, honest, real science) | Diff evidence shown. Limitations explicitly stated. Does-not-prove section included. |
| P16 (preserve past work) | Baseline JSONs preserved unchanged in git. Working tree reset post-test. |

## 10. What this means for next steps

- **T1-Lite precondition met.** Other tests in plan can now proceed when their preconditions are met.
- **No code or data drift detected** in selectivity layer between morning (08:10) and afternoon (17:05) of 2026-05-08.
- **Heavier tests (T2-T5) remain unexecuted** per their preconditions. Test plan section 5 explicitly listed what cannot be done tonight.

## 11. Honest limitations of this test

- Time gap between baseline and rerun was only ~9 hours within same session, same machine, same conda environment. This does not test reproducibility across:
  - Different machines (Mac vs HPC)
  - Different package versions (would need fresh conda env)
  - Different Python versions
  - Different OS (Linux vs macOS)
  - Time spans of weeks/months
- The test only verifies output consistency, not computational correctness. A bug that always produces the same wrong answer would PASS this test.
- Internal randomness or floating point variation was not stress-tested.

These are acknowledged as out of scope for T1-Lite. Heavier T1 tests (cross-machine, cross-environment) deferred to future sessions per test plan.

## 12. Closure

T1-Lite reproducibility test executed and PASSED. Committed selectivity outputs for all 4 diseases reproduce identically (excluding timestamp field). Working tree restored to clean state.

This is the first executed test in the locked test plan. Per plan priority order, T4 (biological face validity) is next high-priority test, but its NSCLC component requires LuCA data (still downloading on HPC). Other T4 components (mCRPC, AML, GBM) executable independently in future sessions.

---

*T1-Lite reproducibility log. Real evidence. Real PASS. Real boundaries.*

— Prasad Akula & Claude (CSO)
2026-05-08
