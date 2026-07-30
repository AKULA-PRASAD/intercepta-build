#!/usr/bin/env python3
"""
INTERCEPTA Round 2.1a — BeatAML 2.0 Schema Inspector
=====================================================

Purpose
-------
Before writing code that joins, filters, and analyzes BeatAML data, look
at the actual files and report what's in them. No claims. No filtering.
No analysis. Just schema inventory.

Once the output of this inspector is known, we write the validation-query
script against the real column names, not guessed ones.

Principle 3 applied: deep research before code.
Principle 15 applied: don't write a script that assumes column names
we haven't verified.

Run
---
    cd ~/INTERCEPTA/round2_aml/code
    python3 inspect_beataml.py 2>&1 | tee ~/INTERCEPTA/round2_aml/results/beataml_schema_inspection.txt

Paste the output back to CSO. Then the real ingestion script is written
against the verified schema.

Author: Prasad Akula
Date:    April 21, 2026
"""
import os
import sys
from pathlib import Path


DATA_ROOT = Path(os.environ.get(
    'BEATAML_DATA_DIR',
    str(Path(__file__).resolve().parent.parent / 'data' / 'beataml2.0_data-2.0')
))


def banner(s):
    print()
    print('=' * 72)
    print(s)
    print('=' * 72)


def inspect_tsv(path, nrows_head=5, show_dtypes=True):
    import pandas as pd
    banner(f"FILE: {path.name}  ({path.stat().st_size / (1024*1024):.1f} MB)")
    # Read with low_memory=False to get stable dtype inference
    df = pd.read_csv(path, sep='\t', low_memory=False)
    print(f"Rows: {len(df):,}")
    print(f"Cols: {len(df.columns)}")
    print(f"Column names:")
    for i, c in enumerate(df.columns):
        print(f"  [{i:2d}]  {c}")
    if show_dtypes:
        print(f"\nColumn dtypes:")
        for c in df.columns:
            nn = df[c].notna().sum()
            nunique = df[c].nunique(dropna=True)
            sample = df[c].dropna().iloc[0] if nn > 0 else '(all NaN)'
            sample_str = str(sample)[:40]
            print(f"  {str(df[c].dtype):12s} non-null={nn:>7d}  "
                  f"unique={nunique:>7d}  first={sample_str}  col={c}")
    print(f"\nFirst {nrows_head} rows:")
    with pd.option_context('display.max_columns', None,
                           'display.width', 200,
                           'display.max_colwidth', 30):
        print(df.head(nrows_head).to_string())
    return df


def inspect_xlsx(path):
    import pandas as pd
    banner(f"FILE: {path.name}  ({path.stat().st_size / 1024:.1f} KB)")
    xl = pd.ExcelFile(path)
    print(f"Sheets: {xl.sheet_names}")
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        print(f"\n--- Sheet: '{sheet}' ---")
        print(f"  Rows: {len(df):,}  Cols: {len(df.columns)}")
        print(f"  Column names:")
        for i, c in enumerate(df.columns):
            print(f"    [{i:2d}]  {c}")
        # For each col, report non-null count, unique count, sample value
        print(f"  Column stats:")
        for c in df.columns:
            nn = df[c].notna().sum()
            nunique = df[c].nunique(dropna=True)
            sample = df[c].dropna().iloc[0] if nn > 0 else '(all NaN)'
            print(f"    {str(df[c].dtype):12s} non-null={nn:>5d}  "
                  f"unique={nunique:>5d}  first={str(sample)[:40]}  col={c}")
        print(f"  First 3 rows:")
        with pd.option_context('display.max_columns', None,
                               'display.width', 200,
                               'display.max_colwidth', 25):
            print(df.head(3).to_string())


def main():
    # Check files exist
    required = [
        ('curve_fits',     'beataml_probit_curve_fits_v4_dbgap.txt'),
        ('clinical',       'beataml_wv1to4_clinical.xlsx'),
        ('sample_mapping', 'beataml_waves1to4_sample_mapping.xlsx'),
        ('drug_families',  'beataml_drug_families.xlsx'),
        ('mutations',      'beataml_wes_wv1to4_mutations_dbgap.txt'),
    ]
    missing = []
    paths = {}
    for label, name in required:
        p = DATA_ROOT / name
        if not p.exists():
            missing.append((label, p))
        paths[label] = p
    if missing:
        print("ERROR: files missing from expected location.")
        for label, p in missing:
            print(f"  missing ({label}): {p}")
        sys.exit(1)

    print(f"Data root: {DATA_ROOT}\n")
    for label, name in required:
        print(f"  ✓ {label:15s}  {name}")

    # Dependencies
    try:
        import pandas as pd  # noqa
    except ImportError:
        print("\nERROR: pandas not installed. Run: pip install pandas openpyxl")
        sys.exit(2)
    try:
        import openpyxl  # noqa
    except ImportError:
        print("\nERROR: openpyxl missing. Run: pip install openpyxl")
        sys.exit(2)

    # Inspect each file.
    # Order: small-and-structural first, large-and-data last.
    inspect_xlsx(paths['sample_mapping'])
    inspect_xlsx(paths['drug_families'])
    inspect_xlsx(paths['clinical'])
    inspect_tsv(paths['curve_fits'])
    inspect_tsv(paths['mutations'])


if __name__ == '__main__':
    main()
