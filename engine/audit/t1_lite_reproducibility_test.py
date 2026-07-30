#!/usr/bin/env python
"""
INTERCEPTA T1-Lite Reproducibility Test
=========================================

Per locked test plan section 6 (test-plan-locked tag, 2026-05-08):

Procedure:
1. Compute baseline hashes from committed JSONs (excluding 'computed' timestamp)
2. Re-run step6_selectivity_v2.py for all 4 diseases
3. Compute post-rerun hashes
4. Compare. PASS if all match. FAIL if any drift.
5. Write T1_REPRODUCIBILITY_LOG.md with results.

Author: Prasad Akula, 2026-05-08
"""

import json
import hashlib
import subprocess
import shutil
import sys
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path("/Users/kalki/INTERCEPTA")
RESULTS_DIR = REPO_ROOT / "results"
DOCS_DIR = REPO_ROOT / "docs"
CODE_DIR = REPO_ROOT / "code"

DISEASES = ["mcrpc", "aml", "gbm", "nsclc"]

# Reference selectivity values from committed work (real measurements)
# Per: round2-2c-spec-locked, vision-module1-amended, selectivity-redesign-complete,
#      workstream-b-phase0-selectivity-shipped
REFERENCE_VALUES = {
    "mcrpc": {"top_gene": "KLK3", "expected_ratio_min": 16000.0},
    "aml": {"top_gene": "JAK3", "expected_ratio_min": 15.0},
    "gbm": {"top_gene": "FGFR3", "expected_ratio_min": 2.3},
    "nsclc": {"top_gene": "ROS1", "expected_ratio_min": 80.0},
}


def hash_json_excluding_timestamp(json_path):
    """Hash JSON content excluding the 'computed' timestamp field."""
    with open(json_path) as f:
        data = json.load(f)
    # Remove unstable fields for stable hashing
    data_copy = dict(data)
    for unstable_field in ["computed", "computed_at", "timestamp"]:
        data_copy.pop(unstable_field, None)
    canonical = json.dumps(data_copy, sort_keys=True)
    return hashlib.md5(canonical.encode()).hexdigest()


def get_top_gene_value(json_path):
    """Extract the top selectivity gene + ratio from JSON."""
    with open(json_path) as f:
        data = json.load(f)
    # Schema: data['genes'][gene_symbol]['ratio_vs_mean']
    if "genes" not in data:
        return None, None
    sorted_genes = sorted(
        data["genes"].items(),
        key=lambda x: x[1].get("ratio_vs_mean", 0),
        reverse=True,
    )
    if not sorted_genes:
        return None, None
    top_gene, top_data = sorted_genes[0]
    return top_gene, top_data.get("ratio_vs_mean", 0)


def main():
    print("=" * 70)
    print("INTERCEPTA T1-Lite Reproducibility Test")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    # ── Step 1: Baseline hashes ────────────────────────────────
    print("\n[Step 1] Computing baseline hashes from committed JSONs...")
    baseline = {}
    for disease in DISEASES:
        json_path = RESULTS_DIR / f"step6_selectivity_{disease}.json"
        if not json_path.exists():
            print(f"  FAIL: missing {json_path}")
            sys.exit(2)
        h = hash_json_excluding_timestamp(json_path)
        top_gene, top_ratio = get_top_gene_value(json_path)
        baseline[disease] = {
            "hash": h,
            "top_gene": top_gene,
            "top_ratio": top_ratio,
            "path": str(json_path),
        }
        print(f"  {disease}: {h[:16]}... (top: {top_gene}={top_ratio:.2f})")

    # ── Step 2: Backup baseline JSONs ──────────────────────────
    print("\n[Step 2] Backing up baseline JSONs to /tmp...")
    backup_dir = Path("/tmp/intercepta_t1_lite_baseline")
    backup_dir.mkdir(exist_ok=True)
    for disease in DISEASES:
        src = RESULTS_DIR / f"step6_selectivity_{disease}.json"
        dst = backup_dir / f"step6_selectivity_{disease}.json"
        shutil.copy(src, dst)
    print(f"  Backed up to {backup_dir}/")

    # ── Step 3: Re-run selectivity for each disease ────────────
    print("\n[Step 3] Re-running step6_selectivity_v2.py for each disease...")
    selectivity_script = CODE_DIR / "step6_selectivity_v2.py"
    if not selectivity_script.exists():
        print(f"  FAIL: missing {selectivity_script}")
        sys.exit(3)

    rerun_results = {}
    for disease in DISEASES:
        print(f"\n  Re-running for {disease}...")
        result = subprocess.run(
            ["python", str(selectivity_script), "--disease", disease],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        if result.returncode != 0:
            print(f"  FAIL: selectivity_v2 failed for {disease}")
            print(f"  STDERR: {result.stderr[:500]}")
            rerun_results[disease] = {"status": "EXECUTION_FAIL"}
            continue

        # Hash the regenerated JSON
        json_path = RESULTS_DIR / f"step6_selectivity_{disease}.json"
        new_hash = hash_json_excluding_timestamp(json_path)
        new_top_gene, new_top_ratio = get_top_gene_value(json_path)
        rerun_results[disease] = {
            "status": "EXECUTED",
            "hash": new_hash,
            "top_gene": new_top_gene,
            "top_ratio": new_top_ratio,
        }
        print(f"  {disease}: regenerated hash {new_hash[:16]}...")

    # ── Step 4: Compare hashes ─────────────────────────────────
    print("\n[Step 4] Comparing baseline vs regenerated...")
    comparisons = {}
    for disease in DISEASES:
        b = baseline[disease]
        r = rerun_results.get(disease, {})

        if r.get("status") == "EXECUTION_FAIL":
            comparisons[disease] = {
                "match": False,
                "reason": "Execution failed during rerun",
            }
            print(f"  {disease}: FAIL (execution error)")
            continue

        match = (b["hash"] == r["hash"])
        ref = REFERENCE_VALUES[disease]

        # Also check the top gene matches reference
        top_gene_correct = (r["top_gene"] == ref["top_gene"])
        ratio_above_threshold = (r["top_ratio"] >= ref["expected_ratio_min"])

        comparisons[disease] = {
            "hash_match": match,
            "baseline_hash": b["hash"],
            "rerun_hash": r["hash"],
            "baseline_top_gene": b["top_gene"],
            "baseline_top_ratio": b["top_ratio"],
            "rerun_top_gene": r["top_gene"],
            "rerun_top_ratio": r["top_ratio"],
            "reference_top_gene": ref["top_gene"],
            "reference_threshold": ref["expected_ratio_min"],
            "top_gene_matches_reference": top_gene_correct,
            "ratio_meets_reference": ratio_above_threshold,
            "overall_pass": match and top_gene_correct and ratio_above_threshold,
        }
        status = "PASS" if comparisons[disease]["overall_pass"] else "FAIL"
        print(f"  {disease}: {status}")
        print(f"    baseline: {b['top_gene']}={b['top_ratio']:.2f}, hash={b['hash'][:16]}")
        print(f"    rerun:    {r['top_gene']}={r['top_ratio']:.2f}, hash={r['hash'][:16]}")

    # ── Step 5: Overall verdict ────────────────────────────────
    n_pass = sum(1 for c in comparisons.values() if c.get("overall_pass"))
    n_total = len(DISEASES)
    overall_pass = (n_pass == n_total)

    print("\n" + "=" * 70)
    print(f"OVERALL: {n_pass}/{n_total} diseases reproduced")
    print(f"Verdict: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 70)

    # ── Step 6: Write log ──────────────────────────────────────
    log_path = DOCS_DIR / "T1_REPRODUCIBILITY_LOG.md"
    write_reproducibility_log(log_path, baseline, rerun_results, comparisons,
                              n_pass, n_total, overall_pass)
    print(f"\nLog written: {log_path}")

    sys.exit(0 if overall_pass else 1)


def write_reproducibility_log(log_path, baseline, rerun_results, comparisons,
                              n_pass, n_total, overall_pass):
    """Write structured log of T1-Lite results."""
    timestamp = datetime.now(timezone.utc).isoformat()
    overall_str = "PASS" if overall_pass else "FAIL"

    content = f"""# T1-Lite Reproducibility Test — Execution Log

**Test:** T1 Reproducibility (lite scope per test plan section 6)
**Subject:** Reproducibility of step6_selectivity_v2.py outputs across 4 diseases
**Authors:** Prasad Akula
**Date:** {timestamp}
**Tag reference:** test-plan-locked
**Overall verdict:** {overall_str} ({n_pass}/{n_total} diseases reproduced)

---

## What this test checked

Per locked test plan section 6:

> Re-run `step6_selectivity_v2.py` for all 4 diseases. Verify outputs match committed JSONs (excluding `computed` timestamp).

This is the lightest reproducibility check we can do — runs the selectivity computation, verifies the result matches what's in git.

## What this test does NOT prove

- Does NOT verify the multi-modal predictor reproduces (separate test, requires HPC + BeatAML data)
- Does NOT verify the KAALCURA cross-dataset signal reproduces (separate test, requires BeatAML + Van Galen)
- Does NOT verify Round 2.2c findings reproduce
- Does NOT verify Workstream B Phase 0 outputs (still in flight)

## Procedure

1. Hashed committed JSONs (excluding 'computed' timestamp field)
2. Backed up baseline JSONs to /tmp/intercepta_t1_lite_baseline/
3. Re-ran step6_selectivity_v2.py for each disease
4. Hashed regenerated JSONs
5. Compared (a) hash match, (b) top gene matches reference, (c) ratio above reference threshold

## Results per disease

| Disease | Baseline top | Rerun top | Reference | Hash match | Verdict |
|---|---|---|---|---|---|
"""

    for disease in DISEASES:
        c = comparisons.get(disease, {})
        if c.get("hash_match") is None:
            row = f"| {disease} | — | — | — | — | EXEC_FAIL |\n"
        else:
            b_top = f"{c.get('baseline_top_gene', '?')}={c.get('baseline_top_ratio', 0):.2f}"
            r_top = f"{c.get('rerun_top_gene', '?')}={c.get('rerun_top_ratio', 0):.2f}"
            ref_str = f"{c.get('reference_top_gene', '?')} >= {c.get('reference_threshold', '?')}"
            hash_str = "✓" if c.get("hash_match") else "✗"
            verdict = "PASS" if c.get("overall_pass") else "FAIL"
            row = f"| {disease} | {b_top} | {r_top} | {ref_str} | {hash_str} | {verdict} |\n"
        content += row

    content += f"""

## Hash details

"""
    for disease in DISEASES:
        c = comparisons.get(disease, {})
        if "baseline_hash" in c:
            content += f"### {disease}\n"
            content += f"- Baseline hash: `{c['baseline_hash']}`\n"
            content += f"- Rerun hash:    `{c['rerun_hash']}`\n"
            content += f"- Match: {'yes' if c.get('hash_match') else 'NO'}\n\n"
        else:
            content += f"### {disease}\n- {c.get('reason', 'unknown')}\n\n"

    content += f"""## Overall verdict

**{overall_str}**: {n_pass} of {n_total} diseases reproduced their committed outputs identically (excluding timestamp).

## What this means

"""

    if overall_pass:
        content += """All 4 selectivity computations are reproducible from the current Mac environment. Tag `test-plan-locked` reproducibility precondition met.

This is the lightest possible reproducibility test. Heavier tests (T2-T5 per test plan) require additional infrastructure (HPC, BeatAML data, baseline implementations) and will be executed in future sessions when their preconditions are met.
"""
    else:
        content += """One or more selectivity computations did NOT reproduce. This is a HALT condition per test plan anti-scope-creep clause: do not proceed with other tests until this is resolved.

Possible causes:
- Random state not seeded
- Environment drift (package version change)
- Code change since baseline was committed
- Data file change since baseline was committed

Investigation required before proceeding.
"""

    content += f"""

## Process audit

| Principle | Applied as |
|---|---|
| P3 (research before code) | Test plan locked before this test was written. |
| P4 (fix structure) | If FAIL, fix root cause; do not adjust thresholds. |
| P15 (honest science) | FAIL is logged honestly with no goalpost moves. |
| P16 (preserve past work) | Baseline hashes preserved as ground truth before any rerun. |

---

*T1-Lite reproducibility log. Generated by t1_lite_reproducibility_test.py*
"""

    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(content)


if __name__ == "__main__":
    main()
