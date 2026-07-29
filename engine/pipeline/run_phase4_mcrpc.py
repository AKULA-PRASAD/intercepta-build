#!/usr/bin/env python3
"""
INTERCEPTA Selectivity Redesign Phase 4 — mCRPC Unified Net Regeneration
==========================================================================

Per spec INTERCEPTA_Selectivity_Redesign_Specification.md Section 8 Phase 4
(scope reduced to mCRPC only per Phase 4 diagnostic — AML and GBM builders
deferred to dedicated future sessions).

This wrapper:
  1. Backs up existing mcrpc_unified_net.json (~53MB)
  2. Runs build_unified_net.py to regenerate using Phase 3 CSV inputs
  3. Compares OLD vs NEW unified nets for structural equivalence:
     - Same number of genes
     - Same number of drugs
     - Same number of pathways
     - Same number of cell populations
     - Same top-level key schema
     - Specific spot-checks: KLK3, AR, BRCA2 selectivity values match
       what Phase 3 CSVs produce
  4. Reports PASS/FAIL with explicit numerical comparison
  5. Aborts with non-zero exit if FAILS

Per spec Section 6 #6 — fail-closed.

Run only after Phase 1, 2, 3 are committed and tagged.

Author: Prasad Akula & Claude (CSO), 2026-05-07
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

HOME = Path.home()
INTERCEPTA = HOME / 'INTERCEPTA'
RESULTS = INTERCEPTA / 'results'
CODE = INTERCEPTA / 'code'

UNIFIED_NET = RESULTS / 'mcrpc_unified_net.json'
UNIFIED_NET_BACKUP = RESULTS / 'mcrpc_unified_net.json.PHASE4_BACKUP'
BUILDER_SCRIPT = CODE / 'build_unified_net.py'

# Phase 3 CSV (the new selectivity input)
PHASE3_SELECTIVITY_MAP = RESULTS / 'step6_selectivity_map.csv'

# Spot-check genes (must be in mCRPC selectivity map)
SPOT_CHECK_GENES = ['KLK3', 'AR', 'BRCA2', 'TP53', 'PTEN']


def banner(msg):
    print('\n' + '=' * 72)
    print(msg)
    print('=' * 72)


def fail_closed(msg):
    print(f"\nPHASE 4 FAILED (fail-closed):\n  {msg}", file=sys.stderr)
    sys.exit(2)


def main():
    banner("Phase 4-mCRPC: Unified Net Regeneration")
    print(f"Started: {datetime.now().isoformat(timespec='seconds')}")

    # ------------------------------------------------------------------
    # Step 1: Verify entry conditions
    # ------------------------------------------------------------------
    banner("Step 1: Entry conditions")
    if not BUILDER_SCRIPT.exists():
        fail_closed(f"Builder script missing: {BUILDER_SCRIPT}")
    print(f"  Builder script: {BUILDER_SCRIPT.name} ({BUILDER_SCRIPT.stat().st_size} bytes)")

    if not PHASE3_SELECTIVITY_MAP.exists():
        fail_closed(f"Phase 3 CSV missing: {PHASE3_SELECTIVITY_MAP}\n"
                    f"  Run Phase 3 first.")
    print(f"  Phase 3 CSV: {PHASE3_SELECTIVITY_MAP.name} "
          f"({PHASE3_SELECTIVITY_MAP.stat().st_size} bytes)")

    if not UNIFIED_NET.exists():
        fail_closed(f"Existing unified net missing: {UNIFIED_NET}\n"
                    f"  This wrapper expects an existing baseline to compare against.")
    old_size = UNIFIED_NET.stat().st_size
    print(f"  Existing unified net: {old_size/1024/1024:.1f} MB")

    # ------------------------------------------------------------------
    # Step 2: Backup
    # ------------------------------------------------------------------
    banner("Step 2: Backup existing unified net")
    if UNIFIED_NET_BACKUP.exists():
        print(f"  Backup already exists: {UNIFIED_NET_BACKUP.name}")
        print(f"    (existing size: {UNIFIED_NET_BACKUP.stat().st_size/1024/1024:.1f} MB)")
        # Don't overwrite an existing backup — that would lose the safety net
    else:
        print(f"  Copying {UNIFIED_NET.name} -> {UNIFIED_NET_BACKUP.name}...")
        shutil.copy2(UNIFIED_NET, UNIFIED_NET_BACKUP)
        print(f"  Backup created: {UNIFIED_NET_BACKUP.stat().st_size/1024/1024:.1f} MB")

    # ------------------------------------------------------------------
    # Step 3: Load OLD net (for comparison)
    # ------------------------------------------------------------------
    banner("Step 3: Load OLD unified net (pre-regeneration)")
    print(f"  Loading {UNIFIED_NET.name}...")
    with open(UNIFIED_NET) as f:
        old_net = json.load(f)

    old_stats = {
        'top_level_keys': sorted(old_net.keys()),
        'n_genes': len(old_net.get('genes', {})),
        'n_drugs': len(old_net.get('drugs', {})),
        'n_pathways': len(old_net.get('pathways', {})),
        'n_cell_populations': len(old_net.get('cell_populations', {})),
        'n_velocity_clusters': len(old_net.get('velocity_clusters', {})),
        'n_escape_routes': len(old_net.get('escape_routes', {})),
    }
    print(f"  OLD top-level keys: {old_stats['top_level_keys']}")
    print(f"  OLD genes: {old_stats['n_genes']}")
    print(f"  OLD drugs: {old_stats['n_drugs']}")
    print(f"  OLD pathways: {old_stats['n_pathways']}")
    print(f"  OLD cell populations: {old_stats['n_cell_populations']}")
    print(f"  OLD velocity clusters: {old_stats['n_velocity_clusters']}")
    print(f"  OLD escape routes: {old_stats['n_escape_routes']}")

    # Spot-check OLD selectivity values for genes we expect Phase 3 to update
    old_selectivity_spotcheck = {}
    for gene in SPOT_CHECK_GENES:
        if gene in old_net.get('genes', {}):
            sel = old_net['genes'][gene].get('selectivity', {})
            old_selectivity_spotcheck[gene] = {
                'prostate_tpm': sel.get('prostate_tpm'),
                'ratio_vs_mean': sel.get('ratio_vs_mean'),
                'safety_class': sel.get('safety_class'),
            }
    print(f"\n  OLD selectivity for spot-check genes:")
    for g, v in old_selectivity_spotcheck.items():
        print(f"    {g}: prostate_tpm={v['prostate_tpm']}, "
              f"ratio={v['ratio_vs_mean']}, class={v['safety_class']}")

    # ------------------------------------------------------------------
    # Step 4: Run the builder
    # ------------------------------------------------------------------
    banner("Step 4: Run build_unified_net.py")
    print(f"  Running {BUILDER_SCRIPT.name}...")
    print(f"  This will OVERWRITE {UNIFIED_NET.name} (backup exists at "
          f"{UNIFIED_NET_BACKUP.name})\n")

    # Run as subprocess so we capture exit code
    t_start = datetime.now()
    result = subprocess.run(
        [sys.executable, str(BUILDER_SCRIPT)],
        cwd=str(CODE),
        capture_output=True,
        text=True,
    )
    t_elapsed = (datetime.now() - t_start).total_seconds()
    print(f"  Builder finished in {t_elapsed:.0f}s. Exit code: {result.returncode}")

    if result.returncode != 0:
        print(f"\n  STDOUT (last 2000 chars):\n{result.stdout[-2000:]}")
        print(f"\n  STDERR (last 2000 chars):\n{result.stderr[-2000:]}")
        fail_closed(f"build_unified_net.py exited non-zero ({result.returncode}). "
                    f"Original unified net preserved at backup.")
    else:
        # Print last bit of stdout for situational awareness
        print(f"\n  STDOUT (last 1000 chars):\n{result.stdout[-1000:]}")

    # ------------------------------------------------------------------
    # Step 5: Load NEW net
    # ------------------------------------------------------------------
    banner("Step 5: Load NEW unified net (post-regeneration)")
    if not UNIFIED_NET.exists():
        fail_closed(f"NEW unified net not produced. Builder may have changed output path.")
    new_size = UNIFIED_NET.stat().st_size
    print(f"  NEW unified net: {new_size/1024/1024:.1f} MB "
          f"(OLD was {old_size/1024/1024:.1f} MB)")

    print(f"  Loading...")
    with open(UNIFIED_NET) as f:
        new_net = json.load(f)

    new_stats = {
        'top_level_keys': sorted(new_net.keys()),
        'n_genes': len(new_net.get('genes', {})),
        'n_drugs': len(new_net.get('drugs', {})),
        'n_pathways': len(new_net.get('pathways', {})),
        'n_cell_populations': len(new_net.get('cell_populations', {})),
        'n_velocity_clusters': len(new_net.get('velocity_clusters', {})),
        'n_escape_routes': len(new_net.get('escape_routes', {})),
    }
    print(f"  NEW top-level keys: {new_stats['top_level_keys']}")
    print(f"  NEW genes: {new_stats['n_genes']}")
    print(f"  NEW drugs: {new_stats['n_drugs']}")
    print(f"  NEW pathways: {new_stats['n_pathways']}")
    print(f"  NEW cell populations: {new_stats['n_cell_populations']}")
    print(f"  NEW velocity clusters: {new_stats['n_velocity_clusters']}")
    print(f"  NEW escape routes: {new_stats['n_escape_routes']}")

    # ------------------------------------------------------------------
    # Step 6: Compare OLD vs NEW
    # ------------------------------------------------------------------
    banner("Step 6: Comparison gates")

    gates = []

    # Gate A: top-level keys match
    keys_match = old_stats['top_level_keys'] == new_stats['top_level_keys']
    gates.append(('A: top-level keys match', keys_match,
                  f"OLD={old_stats['top_level_keys']}\n         NEW={new_stats['top_level_keys']}"))

    # Gate B-G: counts must be identical (selectivity layer doesn't change counts)
    for label, key in [
        ('B: gene count matches', 'n_genes'),
        ('C: drug count matches', 'n_drugs'),
        ('D: pathway count matches', 'n_pathways'),
        ('E: cell population count matches', 'n_cell_populations'),
        ('F: velocity cluster count matches', 'n_velocity_clusters'),
        ('G: escape route count matches', 'n_escape_routes'),
    ]:
        eq = old_stats[key] == new_stats[key]
        gates.append((label, eq, f"OLD={old_stats[key]}, NEW={new_stats[key]}"))

    # Gate H: spot-check selectivity values for KLK3/AR/BRCA2/TP53/PTEN
    # The NEW selectivity should match what Phase 3 CSV holds.
    sel_csv = pd.read_csv(PHASE3_SELECTIVITY_MAP).set_index('gene')

    spotcheck_pass = True
    spotcheck_msgs = []
    for gene in SPOT_CHECK_GENES:
        if gene not in new_net.get('genes', {}):
            spotcheck_msgs.append(f"  {gene}: not in NEW net (skipped)")
            continue
        new_sel = new_net['genes'][gene].get('selectivity', {})
        new_prostate_tpm = new_sel.get('prostate_tpm')
        new_ratio = new_sel.get('ratio_vs_mean')

        if gene not in sel_csv.index:
            spotcheck_msgs.append(f"  {gene}: not in Phase 3 CSV (skipped)")
            continue

        csv_prostate_tpm = float(sel_csv.at[gene, 'prostate_tpm'])
        csv_ratio = float(sel_csv.at[gene, 'ratio_vs_mean'])

        # Tolerance: build_unified_net.py rounds to 2 decimals (line 212).
        # Phase 3 CSV rounds to 4 decimals. So new_net rounds the CSV value to 2
        # → we expect new_prostate_tpm ≈ round(csv_prostate_tpm, 2).
        expected_prostate_tpm = round(csv_prostate_tpm, 2)
        expected_ratio = round(csv_ratio, 2)

        prostate_ok = abs(new_prostate_tpm - expected_prostate_tpm) < 0.01
        ratio_ok = abs(new_ratio - expected_ratio) < 0.05  # ratios get larger relative tolerance

        if prostate_ok and ratio_ok:
            spotcheck_msgs.append(f"  {gene}: OK (tpm={new_prostate_tpm}, ratio={new_ratio})")
        else:
            spotcheck_pass = False
            spotcheck_msgs.append(
                f"  {gene}: MISMATCH "
                f"NEW(tpm={new_prostate_tpm}, ratio={new_ratio}) vs "
                f"CSV(tpm={expected_prostate_tpm}, ratio={expected_ratio})"
            )

    gates.append(('H: selectivity spot-check (KLK3/AR/BRCA2/TP53/PTEN)',
                  spotcheck_pass,
                  '\n'.join(spotcheck_msgs)))

    # Print gate verdicts
    n_pass = sum(1 for _, ok, _ in gates if ok)
    n_fail = sum(1 for _, ok, _ in gates if not ok)
    print(f"\n  Gate verdicts:")
    for label, ok, detail in gates:
        status = 'PASS' if ok else 'FAIL'
        print(f"    [{status}] {label}")
        if not ok or 'MISMATCH' in detail:
            print(f"         {detail}")
    print(f"\n  Total: {n_pass} PASS, {n_fail} FAIL")

    # ------------------------------------------------------------------
    # Step 7: Final verdict
    # ------------------------------------------------------------------
    banner("Step 7: Final verdict")

    if n_fail == 0:
        print(f"  Phase 4-mCRPC: PASS")
        print(f"\n  NEW unified net is structurally equivalent to OLD with "
              f"updated selectivity values from Phase 3 CSVs.")
        print(f"  Backup preserved at: {UNIFIED_NET_BACKUP.name}")
        print(f"  Safe to commit.")
        sys.exit(0)
    else:
        print(f"  Phase 4-mCRPC: FAIL")
        print(f"\n  {n_fail} gates failed. Review output above.")
        print(f"  To revert: cp {UNIFIED_NET_BACKUP.name} {UNIFIED_NET.name}")
        print(f"  DO NOT commit until investigation complete.")
        sys.exit(1)


if __name__ == '__main__':
    main()
