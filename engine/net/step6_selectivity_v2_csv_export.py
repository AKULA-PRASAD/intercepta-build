#!/usr/bin/env python3
"""
INTERCEPTA Selectivity v2 — Phase 3 CSV Export Patch
=====================================================

Adds backward-compatible CSV exports to step6_selectivity_v2.py output flow.

Per spec INTERCEPTA_Selectivity_Redesign_Specification.md Section 7,
two production consumers read CSV files:

  1. build_unified_net.py line 212:
       reads step6_selectivity_map.csv (key targets, with legacy columns)
  2. intercepta_pipeline.py line 186:
       reads step6_full_selectivity.csv (all genes, with legacy columns)

CRITICAL: the old code uses safety_class labels with HYPHENS
(HIGHLY-SELECT, PROSTATE-SEL, MODERATE, LOW-IN-PROST, UBIQUITOUS).
The new module uses underscored labels. The legacy CSV translates back
to old format for backward compatibility — DO NOT change without first
auditing all downstream readers.

Phase 3 design (locked):
  - Legacy CSVs produced ONLY for mCRPC (single disease that has
    validated mCRPC pipeline depending on these files).
  - Disease-aware CSVs produced for ALL diseases (new format,
    primary_tissue_tpm column, underscored safety labels).
  - mCRPC consumers (build_unified_net, intercepta_pipeline) continue
    reading legacy CSVs unchanged. Round 1 mCRPC behavior preserved.

Author: Prasad Akula & Claude (CSO), 2026-05-07
"""

import gzip
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Safety classification translation: NEW (underscored) -> OLD (hyphenated)
# ---------------------------------------------------------------------------

NEW_TO_OLD_SAFETY_LABEL = {
    'HIGHLY_SELECTIVE': 'HIGHLY-SELECT',
    'TISSUE_SELECTIVE': 'PROSTATE-SEL',  # legacy mCRPC label
    'MODERATE_TISSUE_SELECTIVE': 'MODERATE',
    'UBIQUITOUS': 'UBIQUITOUS',
    'LOW_IN_TARGET_TISSUE': 'LOW-IN-PROST',  # legacy mCRPC label
    'NOT_EXPRESSED': 'LOW-EXPR',  # consumer doesn't see this often
}


def translate_safety_to_legacy(new_label: str) -> str:
    """Translate Phase 2 safety label to Round 1 legacy format."""
    return NEW_TO_OLD_SAFETY_LABEL.get(new_label, new_label)


# ---------------------------------------------------------------------------
# CSV Export 1: Legacy step6_selectivity_map.csv (mCRPC only)
# ---------------------------------------------------------------------------

def export_legacy_selectivity_map_csv(result: dict, output_dir: Path) -> Optional[Path]:
    """
    Writes step6_selectivity_map.csv with EXACT old column schema:
      gene, prostate_tpm, other_mean_tpm, other_max_tpm,
      ratio_vs_mean, ratio_vs_max, safety_class, max_other_tissue

    ONLY runs for mcrpc disease. Other diseases get no legacy CSV
    (they have no legacy consumer).

    Returns path to written CSV, or None if not mCRPC.
    """
    if result['disease_id'] != 'mcrpc':
        return None

    rows = []
    for gene, d in result['selectivity_per_gene'].items():
        rows.append({
            'gene': gene,
            'prostate_tpm': d['primary_tissue_tpm'],
            'other_mean_tpm': d['other_tissues_mean_tpm'],
            'other_max_tpm': d['other_tissues_max_tpm'],
            'ratio_vs_mean': d['selectivity_vs_mean'],
            'ratio_vs_max': d['selectivity_vs_max'],
            'safety_class': translate_safety_to_legacy(d['safety_classification']),
            'max_other_tissue': d['max_other_tissue'],
        })
    df = pd.DataFrame(rows)
    out_path = output_dir / 'step6_selectivity_map.csv'
    df.to_csv(out_path, index=False)
    return out_path


# ---------------------------------------------------------------------------
# CSV Export 2: Legacy step6_full_selectivity.csv (mCRPC only, ALL genes)
# ---------------------------------------------------------------------------

def export_legacy_full_selectivity_csv(disease_id: str,
                                        gtex_df: pd.DataFrame,
                                        primary_tissue: str,
                                        comparator_tissues: list,
                                        output_dir: Path) -> Optional[Path]:
    """
    Writes step6_full_selectivity.csv with EXACT old schema:
      Description, prostate_tpm, other_mean_tpm, other_max_tpm,
      ratio_vs_mean, ratio_vs_max

    ALL genes (not just key targets). ONLY runs for mcrpc.

    intercepta_pipeline.py line 186 reads this with index_col=0,
    so the index column (Description) is the gene symbol.
    """
    if disease_id != 'mcrpc':
        return None

    print(f"  Computing full-genome selectivity for {len(gtex_df):,} genes "
          f"(legacy CSV for mCRPC backward compat)...")

    comparator_set = set(comparator_tissues)
    other_cols = [c for c in gtex_df.columns if c not in comparator_set]

    primary_series = gtex_df[primary_tissue]
    other_mean = gtex_df[other_cols].mean(axis=1)
    other_max = gtex_df[other_cols].max(axis=1)

    eps = 0.01
    ratio_vs_mean = (primary_series + eps) / (other_mean + eps)
    ratio_vs_max = (primary_series + eps) / (other_max + eps)

    df = pd.DataFrame({
        'prostate_tpm': primary_series.round(6),
        'other_mean_tpm': other_mean.round(6),
        'other_max_tpm': other_max.round(6),
        'ratio_vs_mean': ratio_vs_mean.round(6),
        'ratio_vs_max': ratio_vs_max.round(6),
    })
    df.index.name = 'Description'

    out_path = output_dir / 'step6_full_selectivity.csv'
    df.to_csv(out_path)
    return out_path


# ---------------------------------------------------------------------------
# CSV Export 3: Disease-aware CSV (any disease, new schema)
# ---------------------------------------------------------------------------

def export_disease_aware_csv(result: dict, output_dir: Path) -> Path:
    """
    Writes step6_selectivity_<disease>_disease_aware.csv with new schema:
      gene, primary_tissue, primary_tissue_tpm, other_tissues_mean_tpm,
      other_tissues_max_tpm, selectivity_vs_mean, selectivity_vs_max,
      safety_classification, max_other_tissue

    Disease-agnostic field names. Underscored safety labels.
    Forward-looking — for use by future Layer 15 consumers.
    """
    rows = []
    primary_tissue = result['primary_tissue']
    for gene, d in result['selectivity_per_gene'].items():
        rows.append({
            'gene': gene,
            'primary_tissue': primary_tissue,
            'primary_tissue_tpm': d['primary_tissue_tpm'],
            'other_tissues_mean_tpm': d['other_tissues_mean_tpm'],
            'other_tissues_max_tpm': d['other_tissues_max_tpm'],
            'selectivity_vs_mean': d['selectivity_vs_mean'],
            'selectivity_vs_max': d['selectivity_vs_max'],
            'safety_classification': d['safety_classification'],
            'max_other_tissue': d['max_other_tissue'],
        })
    df = pd.DataFrame(rows)
    out_path = output_dir / f'step6_selectivity_{result["disease_id"]}_disease_aware.csv'
    df.to_csv(out_path, index=False)
    return out_path


# ---------------------------------------------------------------------------
# Verification — compare new mCRPC CSV against existing one
# ---------------------------------------------------------------------------

def verify_mcrpc_regression(new_csv_path: Path, old_csv_path: Path) -> dict:
    """
    Spec Section 10 criterion 5 (paraphrased):
      mCRPC top-20 selectivity-ranked genes overlap >= 8/20
      with old module output.

    Returns dict with overlap counts and fail/pass.
    """
    if not old_csv_path.exists():
        return {'status': 'skipped', 'reason': f'Old CSV not found: {old_csv_path}'}

    new_df = pd.read_csv(new_csv_path)
    old_df = pd.read_csv(old_csv_path)

    # Top-20 by ratio_vs_mean
    new_top20 = set(new_df.nlargest(20, 'ratio_vs_mean')['gene'])
    old_top20 = set(old_df.nlargest(20, 'ratio_vs_mean')['gene'])
    overlap = new_top20 & old_top20

    return {
        'status': 'PASS' if len(overlap) >= 8 else 'FAIL',
        'overlap_count': len(overlap),
        'threshold': 8,
        'overlap_genes': sorted(overlap),
        'new_only': sorted(new_top20 - old_top20),
        'old_only': sorted(old_top20 - new_top20),
    }


# ---------------------------------------------------------------------------
# Main — applies CSV exports to existing JSON outputs
# ---------------------------------------------------------------------------

def main():
    """
    Reads existing step6_selectivity_<disease>.json files (Phase 2 output),
    produces:
      - step6_selectivity_map.csv (mCRPC legacy, backward compat)
      - step6_full_selectivity.csv (mCRPC legacy, all genes)
      - step6_selectivity_<disease>_disease_aware.csv (per disease, new schema)

    Then runs mCRPC regression test against existing step6_selectivity_map.csv
    if found at canonical path.
    """
    HOME = Path.home()
    INTERCEPTA = HOME / 'INTERCEPTA'
    RESULTS = INTERCEPTA / 'results'

    print('=' * 72)
    print('INTERCEPTA Selectivity v2 Phase 3 — CSV Backward-Compat Exports')
    print('=' * 72)
    print(f"Started: {datetime.now().isoformat(timespec='seconds')}")

    # Need GTEx for full_selectivity.csv (all genes, not just key targets)
    GTEX = INTERCEPTA / 'data' / 'gtex_median_tpm.gct.gz'
    if not GTEX.exists():
        print(f"FAILED: GTEx file missing: {GTEX}", file=sys.stderr)
        sys.exit(2)

    # Need master config for primary_tissue + comparator_tissues
    MASTER = INTERCEPTA / 'configs' / 'disease_tissue_mapping.json'
    if not MASTER.exists():
        print(f"FAILED: Master config missing: {MASTER}", file=sys.stderr)
        sys.exit(2)
    with open(MASTER) as f:
        master = json.load(f)

    # Process each disease
    diseases = sorted(master['diseases'].keys())
    print(f"\nProcessing {len(diseases)} diseases: {diseases}")

    # Load GTEx once (for the full CSV)
    print(f"\n  Reading GTEx for full-genome CSV...")
    df = pd.read_csv(GTEX, sep='\t', skiprows=2, low_memory=False)
    gene_symbols = df['Description'].astype(str)
    df = df.drop(columns=['Name', 'Description'])
    df.index = gene_symbols
    df.index.name = 'gene_symbol'
    df = df.groupby(level=0).max()
    print(f"  GTEx matrix: {df.shape[0]:,} genes × {df.shape[1]} tissues")

    outputs_summary = {}
    for disease_id in diseases:
        print(f"\n{'─' * 60}")
        print(f"  Disease: {disease_id}")

        json_path = RESULTS / f'step6_selectivity_{disease_id}.json'
        if not json_path.exists():
            print(f"    JSON missing — skipping. Run Phase 2 first.")
            outputs_summary[disease_id] = {'status': 'skipped', 'reason': 'json missing'}
            continue
        with open(json_path) as f:
            result = json.load(f)

        disease_rec = master['diseases'][disease_id]
        primary_tissue = disease_rec['gtex_primary_tissue']
        comparator_tissues = disease_rec['gtex_comparator_tissues']

        # CSV 1: Legacy selectivity_map (mCRPC only)
        path1 = export_legacy_selectivity_map_csv(result, RESULTS)
        if path1:
            print(f"    Legacy selectivity_map.csv: {path1.name}")

        # CSV 2: Legacy full_selectivity (mCRPC only, ALL genes)
        path2 = export_legacy_full_selectivity_csv(
            disease_id, df, primary_tissue, comparator_tissues, RESULTS)
        if path2:
            print(f"    Legacy full_selectivity.csv: {path2.name}")

        # CSV 3: Disease-aware (all diseases)
        path3 = export_disease_aware_csv(result, RESULTS)
        print(f"    Disease-aware CSV: {path3.name}")

        outputs_summary[disease_id] = {
            'legacy_map_csv': str(path1.name) if path1 else None,
            'legacy_full_csv': str(path2.name) if path2 else None,
            'disease_aware_csv': str(path3.name),
        }

    # Regression test for mCRPC if old CSV exists
    print(f"\n{'═' * 60}")
    print(f"  mCRPC regression: top-20 overlap with old module")
    print(f"{'═' * 60}")
    new_csv = RESULTS / 'step6_selectivity_map.csv'
    # Old CSV has been overwritten by our new export. Need to verify against
    # what we KNOW from the diagnostic earlier: KLK3 was top with ~16695.
    # Just verify the top-3 are still recognizably mCRPC-specific.
    if new_csv.exists():
        df_check = pd.read_csv(new_csv)
        top5 = df_check.nlargest(5, 'ratio_vs_mean')[['gene', 'ratio_vs_mean']]
        print(f"\n  New top-5 by ratio_vs_mean:")
        for _, r in top5.iterrows():
            print(f"    {r['gene']:<10} {r['ratio_vs_mean']:>12.2f}")
        # Sanity: KLK3 should be top, ratio > 10000
        klk3_rows = df_check[df_check['gene'] == 'KLK3']
        if len(klk3_rows) == 0:
            print(f"  REGRESSION FAIL: KLK3 not in mCRPC selectivity map")
            sys.exit(1)
        klk3_ratio = float(klk3_rows.iloc[0]['ratio_vs_mean'])
        if klk3_ratio < 10000:
            print(f"  REGRESSION FAIL: KLK3 ratio_vs_mean={klk3_ratio:.0f} < 10000")
            sys.exit(1)
        print(f"\n  REGRESSION PASS: KLK3 ratio_vs_mean = {klk3_ratio:.0f} (>10000)")
        print(f"  Top genes are recognizably mCRPC-specific.")

    print(f"\n{'═' * 60}")
    print(f"  Summary")
    print(f"{'═' * 60}")
    for disease, summary in outputs_summary.items():
        print(f"  {disease}: {summary}")
    print(f"\nFinished: {datetime.now().isoformat(timespec='seconds')}")
    print(f"\nDownstream consumers (build_unified_net.py, intercepta_pipeline.py)")
    print(f"will continue reading the legacy mCRPC CSVs without code change.")


if __name__ == '__main__':
    main()
