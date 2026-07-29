#!/usr/bin/env python3
"""
GTEx column audit — Phase 2 prep for selectivity redesign.

Reads ~/INTERCEPTA/data/gtex_median_tpm.gct.gz and:
  1. Lists all tissue column names verbatim
  2. Verifies that disease_tissue_mapping.json's tissue references exist
  3. Saves output to configs/gtex_columns_audit.txt for Phase 2 consumption

This is the verification step that prevents Phase 2 from wasting time
on string-matching surprises (Brain_Cortex vs Brain - Cortex etc.).
"""
import gzip
import json
import sys
from pathlib import Path

HOME = Path.home()
GTEX = HOME / 'INTERCEPTA' / 'data' / 'gtex_median_tpm.gct.gz'
CONFIG = HOME / 'INTERCEPTA' / 'configs' / 'disease_tissue_mapping.json'
OUTPUT = HOME / 'INTERCEPTA' / 'configs' / 'gtex_columns_audit.txt'

print(f"Reading GTEx: {GTEX}")
if not GTEX.exists():
    sys.exit(f"GTEx file missing: {GTEX}")

# GCT format: line 1 = "#1.2", line 2 = "<n_genes>\t<n_tissues>", line 3 = header
with gzip.open(GTEX, 'rt') as f:
    f.readline()  # version line
    dim_line = f.readline().strip()
    header = f.readline().strip()

print(f"Dimensions line: {dim_line}")
cols = header.split('\t')
print(f"Total columns in header: {len(cols)}")
print(f"First 2 columns (metadata): {cols[:2]}")
tissues = cols[2:]
print(f"Tissue columns: {len(tissues)}")
print()

# Load expected tissues from config
print(f"Loading config: {CONFIG}")
if not CONFIG.exists():
    sys.exit(f"Config missing: {CONFIG}")
config = json.load(open(CONFIG))

# Collect all tissues referenced in the config
expected = set()
for d_id, d_cfg in config['diseases'].items():
    expected.add(d_cfg['gtex_primary_tissue'])
    for t in d_cfg['gtex_comparator_tissues']:
        expected.add(t)

print(f"Tissues expected by config: {sorted(expected)}")
print()

# Verify each
missing = []
present = []
for t in sorted(expected):
    if t in tissues:
        present.append(t)
    else:
        missing.append(t)

print(f"PRESENT in GTEx ({len(present)}/{len(expected)}):")
for t in present:
    print(f"  ✓ {t}")
if missing:
    print(f"\nMISSING from GTEx ({len(missing)}):")
    for t in missing:
        # Try fuzzy match
        candidates = [c for c in tissues if t.split('_')[0].lower() in c.lower()]
        print(f"  ✗ {t}  candidates: {candidates[:5]}")
else:
    print(f"\nNo missing tissues. All {len(expected)} expected tissues present in GTEx.")

# Write audit file
print(f"\nWriting audit: {OUTPUT}")
with open(OUTPUT, 'w') as f:
    f.write("GTEx Column Audit — Phase 2 Prep\n")
    f.write("=" * 60 + "\n")
    f.write(f"GTEx file: {GTEX}\n")
    f.write(f"Dimensions: {dim_line}\n")
    f.write(f"Total tissue columns: {len(tissues)}\n\n")
    f.write("All tissue columns (verbatim):\n")
    for t in tissues:
        f.write(f"  {t}\n")
    f.write(f"\nConfig-expected tissues:\n")
    f.write(f"  Present: {len(present)}/{len(expected)}\n")
    if missing:
        f.write(f"  Missing: {missing}\n")
    f.write(f"\n=== STATUS: {'OK' if not missing else 'NEEDS FIX'} ===\n")

print(f"Done. Status: {'OK' if not missing else 'NEEDS FIX (config tissue names dont match GTEx)'}")
