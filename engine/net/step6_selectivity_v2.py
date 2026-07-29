#!/usr/bin/env python3
"""
INTERCEPTA Selectivity Layer v2 — Disease-Parameterized GTEx Module
=====================================================================

Per spec INTERCEPTA_Selectivity_Redesign_Specification.md
(committed under tag selectivity-redesign-spec).

Replaces mCRPC-hardcoded step6_gtex_selectivity.py and step6_fix_gtex.py.
Computes tumor/normal selectivity ratios from GTEx v8 median TPM data
for any disease whose tissue mapping is registered in
configs/disease_tissue_mapping.json.

Key spec compliance (binding per Section 6):
  1. Random state — N/A (deterministic computation, no randomness)
  2. Locked LightGBM params — N/A (no ML)
  3. Fail-closed on missing inputs (no silent zeros)
  4. No data leakage (no train/test split — pure descriptive statistics)
  5. No hardcoded disease names in logic (search source for "prostate"
     should find only docstrings/comments)
  6. Disease-agnostic output schema (no prostate_tpm field)
  7. Substring matching forbidden — exact GTEx column lookup only
  8. Multi-tissue averaging for GBM brain regions

Output schema (per spec Section 5):
{
  "disease_id": "...",
  "disease_full_name": "...",
  "primary_tissue": "...",
  "comparator_tissues": [...],
  "tissue_proxy_caveat": "..." | null,
  "n_genes_evaluated": N,
  "selectivity_per_gene": {
    "<gene>": {
      "primary_tissue_tpm": ...,
      "other_tissues_mean_tpm": ...,
      "other_tissues_max_tpm": ...,
      "selectivity_vs_mean": ...,
      "selectivity_vs_max": ...,
      "max_other_tissue": "...",
      "safety_classification": "..."
    }
  },
  "computed": "<ISO timestamp>",
  "module_version": "step6_selectivity_v2"
}

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
# Paths (locked per spec Section 5)
# ---------------------------------------------------------------------------
HOME = Path.home()
INTERCEPTA = HOME / 'INTERCEPTA'
CONFIGS = INTERCEPTA / 'configs'
GTEX_PATH = INTERCEPTA / 'data' / 'gtex_median_tpm.gct.gz'

# Output directory parameterized at call time (spec Section 5)
DEFAULT_OUTPUT_DIR = INTERCEPTA / 'results'

MODULE_VERSION = 'step6_selectivity_v2'

# Safety classification thresholds (mirrored from
# disease_tissue_mapping.json for transparency in code)
def classify_safety(primary_tpm: float, ratio_vs_mean: float) -> str:
    """Disease-agnostic safety classification per spec Section 5."""
    if primary_tpm < 1.0:
        return 'NOT_EXPRESSED'
    if ratio_vs_mean > 10:
        return 'HIGHLY_SELECTIVE'
    if ratio_vs_mean > 3:
        return 'TISSUE_SELECTIVE'
    if ratio_vs_mean > 1.5:
        return 'MODERATE_TISSUE_SELECTIVE'
    if ratio_vs_mean >= 0.5:
        return 'UBIQUITOUS'
    return 'LOW_IN_TARGET_TISSUE'


# ---------------------------------------------------------------------------
# Fail-closed helpers (spec Section 6 #6)
# ---------------------------------------------------------------------------

def fail_closed(msg: str) -> None:
    """Per spec Section 6 #6: fail-closed on any missing input."""
    print(f"\nSELECTIVITY V2 FAILED (fail-closed):\n  {msg}", file=sys.stderr)
    sys.exit(2)


def banner(msg: str) -> None:
    print('\n' + '=' * 72)
    print(msg)
    print('=' * 72)


# ---------------------------------------------------------------------------
# Config loading (per spec Section 4 + 5)
# ---------------------------------------------------------------------------

def load_master_config() -> dict:
    """Load disease_tissue_mapping.json — the source of truth."""
    p = CONFIGS / 'disease_tissue_mapping.json'
    if not p.exists():
        fail_closed(f"Master config missing: {p}\n"
                    f"  Expected per spec Section 4. Run Phase 1 first.")
    with open(p) as f:
        return json.load(f)


def load_disease_config(disease_id: str, master: dict) -> tuple[dict, dict]:
    """
    Returns (disease_record_from_master, gene_config).
    Fails closed if disease_id is not registered or gene config missing.
    """
    diseases = master.get('diseases', {})
    if disease_id not in diseases:
        registered = sorted(diseases.keys())
        fail_closed(f"Unknown disease_id '{disease_id}'.\n"
                    f"  Registered: {registered}\n"
                    f"  To add: edit configs/disease_tissue_mapping.json")
    disease_rec = diseases[disease_id]

    gene_path = INTERCEPTA / disease_rec['gene_list_path']
    if not gene_path.exists():
        fail_closed(f"Gene config missing for {disease_id}: {gene_path}")
    with open(gene_path) as f:
        gene_cfg = json.load(f)

    # Sanity-check gene config matches disease_id
    if gene_cfg.get('disease_id') != disease_id:
        fail_closed(f"Gene config disease_id mismatch: file says "
                    f"'{gene_cfg.get('disease_id')}', expected '{disease_id}'")

    return disease_rec, gene_cfg


# ---------------------------------------------------------------------------
# GTEx loading (per spec Section 6 #3 — exact lookup, no substring match)
# ---------------------------------------------------------------------------

def load_gtex_matrix(gtex_path: Path = GTEX_PATH) -> pd.DataFrame:
    """
    Load GTEx median TPM gct.gz file as DataFrame indexed by gene symbol,
    columns = tissue names (verbatim, with spaces/dashes/parens preserved).

    Duplicates handled by taking max (matches step6_fix_gtex.py behavior
    per P16).
    """
    if not gtex_path.exists():
        fail_closed(f"GTEx file missing: {gtex_path}")

    print(f"  Reading {gtex_path.name} ({gtex_path.stat().st_size/1024/1024:.1f} MB)...")
    # GCT format: line 1 = '#1.2', line 2 = '<n_genes>\t<n_tissues>',
    # line 3+ = data with header
    df = pd.read_csv(gtex_path, sep='\t', skiprows=2, low_memory=False)
    print(f"  Raw shape: {df.shape}")

    if 'Description' not in df.columns:
        fail_closed(f"GTEx file missing 'Description' column. "
                    f"Got: {list(df.columns[:5])}")
    if 'Name' not in df.columns:
        fail_closed(f"GTEx file missing 'Name' column. "
                    f"Got: {list(df.columns[:5])}")

    # Use Description (gene symbol) as index. Drop Name (Ensembl ID).
    gene_symbols = df['Description'].astype(str)
    df = df.drop(columns=['Name', 'Description'])
    df.index = gene_symbols
    df.index.name = 'gene_symbol'

    # Handle duplicate gene symbols (max per gene)
    n_dup_before = len(df)
    df = df.groupby(level=0).max()
    n_dup_after = len(df)
    if n_dup_before > n_dup_after:
        print(f"  Deduplicated by gene symbol: {n_dup_before} → {n_dup_after}")

    print(f"  Final matrix: {df.shape[0]} genes × {df.shape[1]} tissues")
    return df


def verify_tissues_present(gtex_df: pd.DataFrame, tissues: list[str],
                           context: str) -> None:
    """Per spec Section 6 #7: exact tissue name match required."""
    available = set(gtex_df.columns)
    missing = [t for t in tissues if t not in available]
    if missing:
        fail_closed(f"GTEx tissues missing for {context}: {missing}\n"
                    f"  This indicates config/GTEx mismatch.\n"
                    f"  Run audit_gtex_columns.py to diagnose.")


# ---------------------------------------------------------------------------
# Selectivity computation (the heart of the module)
# ---------------------------------------------------------------------------

def compute_selectivity_for_disease(disease_id: str,
                                     output_dir: Optional[Path] = None,
                                     verbose: bool = True) -> dict:
    """
    Public API per spec Section 5.

    Reads master config, loads disease record, loads GTEx, computes
    selectivity per gene in the disease's key_target_genes list, and
    writes JSON per spec output schema.

    Returns the result dict (also written to disk).
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    master = load_master_config()
    disease_rec, gene_cfg = load_disease_config(disease_id, master)

    primary_tissue = disease_rec['gtex_primary_tissue']
    comparator_tissues = disease_rec['gtex_comparator_tissues']
    strategy = disease_rec['gtex_comparator_strategy']
    proxy_caveat = disease_rec.get('tissue_proxy_caveat')
    target_genes = gene_cfg['key_target_genes']

    if verbose:
        banner(f"Computing selectivity: {disease_id}")
        print(f"  Disease: {disease_rec['disease_full_name']}")
        print(f"  Primary tissue: '{primary_tissue}'")
        print(f"  Comparator strategy: {strategy}")
        if strategy == 'multi_tissue':
            print(f"  Comparator tissues ({len(comparator_tissues)}): "
                  f"{comparator_tissues[:3]}...")
        if proxy_caveat:
            print(f"  Proxy caveat: {proxy_caveat}")
        print(f"  Target genes: {len(target_genes)}")

    # Load GTEx
    gtex_df = load_gtex_matrix()

    # Verify all referenced tissues exist in GTEx (exact match)
    all_tissues = list(set([primary_tissue] + comparator_tissues))
    verify_tissues_present(gtex_df, all_tissues, context=disease_id)

    # Compute per-gene selectivity
    if verbose:
        print(f"\n  Computing selectivity for {len(target_genes)} target genes...")

    selectivity_per_gene = {}
    n_found = 0
    n_missing = 0
    missing_genes = []

    for gene in target_genes:
        if gene not in gtex_df.index:
            n_missing += 1
            missing_genes.append(gene)
            continue
        n_found += 1

        # Primary tissue value
        if strategy == 'single_tissue':
            primary_tpm = float(gtex_df.at[gene, primary_tissue])
        elif strategy == 'multi_tissue':
            # Average across all comparator tissues for the "primary" value
            primary_tpm = float(gtex_df.loc[gene, comparator_tissues].mean())
        else:
            fail_closed(f"Unknown comparator strategy: {strategy}")

        # Other tissues = all GTEx tissues minus the comparator set
        comparator_set = set(comparator_tissues)
        other_tissue_cols = [c for c in gtex_df.columns
                             if c not in comparator_set]
        other_values = gtex_df.loc[gene, other_tissue_cols]

        other_mean = float(other_values.mean())
        other_max = float(other_values.max())
        max_other_tissue = str(other_values.idxmax())

        # Selectivity ratios (small epsilon to avoid div-by-zero)
        eps = 0.01
        sel_vs_mean = (primary_tpm + eps) / (other_mean + eps)
        sel_vs_max = (primary_tpm + eps) / (other_max + eps)

        # Safety classification
        safety = classify_safety(primary_tpm, sel_vs_mean)

        selectivity_per_gene[gene] = {
            'primary_tissue_tpm': round(primary_tpm, 4),
            'other_tissues_mean_tpm': round(other_mean, 4),
            'other_tissues_max_tpm': round(other_max, 4),
            'selectivity_vs_mean': round(sel_vs_mean, 4),
            'selectivity_vs_max': round(sel_vs_max, 4),
            'max_other_tissue': max_other_tissue,
            'safety_classification': safety,
        }

    if verbose:
        print(f"  Found in GTEx: {n_found}/{len(target_genes)}")
        if n_missing:
            print(f"  Missing from GTEx: {missing_genes}")

    # Falsifiable success criterion check (spec Section 10)
    if n_found == 0:
        fail_closed(f"No target genes found in GTEx for {disease_id}. "
                    f"Either gene list is wrong or GTEx data is corrupt.")

    # Build output dict per spec Section 5 schema
    result = {
        'disease_id': disease_id,
        'disease_full_name': disease_rec['disease_full_name'],
        'primary_tissue': primary_tissue,
        'comparator_tissues': comparator_tissues,
        'comparator_strategy': strategy,
        'tissue_proxy_caveat': proxy_caveat,
        'n_target_genes': len(target_genes),
        'n_genes_found_in_gtex': n_found,
        'n_genes_missing_from_gtex': n_missing,
        'missing_genes': missing_genes if missing_genes else None,
        'selectivity_per_gene': selectivity_per_gene,
        'computed': datetime.now().isoformat(timespec='seconds'),
        'module_version': MODULE_VERSION,
        'spec_reference': 'INTERCEPTA_Selectivity_Redesign_Specification.md '
                          '(tag: selectivity-redesign-spec)',
    }

    # Write to disk per spec Section 6 #5
    out_path = output_dir / f'step6_selectivity_{disease_id}.json'
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)

    if verbose:
        print(f"  Saved: {out_path}")

    return result


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------

def print_top_selectivity(result: dict, n_top: int = 10) -> None:
    """Pretty-print top-N most selective genes for a disease."""
    sel = result['selectivity_per_gene']
    if not sel:
        return
    sorted_genes = sorted(sel.items(),
                          key=lambda kv: kv[1]['selectivity_vs_mean'],
                          reverse=True)
    print(f"\n  Top {min(n_top, len(sorted_genes))} most selective genes "
          f"(by selectivity_vs_mean):")
    print(f"  {'Gene':<10} {'Primary TPM':>12} {'Other Mean':>11} "
          f"{'Sel vs Mean':>12} {'Safety':<25}")
    print(f"  {'-'*10} {'-'*12} {'-'*11} {'-'*12} {'-'*25}")
    for gene, d in sorted_genes[:n_top]:
        print(f"  {gene:<10} {d['primary_tissue_tpm']:>12.2f} "
              f"{d['other_tissues_mean_tpm']:>11.2f} "
              f"{d['selectivity_vs_mean']:>12.2f} "
              f"{d['safety_classification']:<25}")


# ---------------------------------------------------------------------------
# Main — runs all 3 production diseases per spec Section 10
# ---------------------------------------------------------------------------

def main():
    banner("INTERCEPTA Selectivity Layer v2 — Disease-Parameterized")
    print(f"Started: {datetime.now().isoformat(timespec='seconds')}")
    print(f"Spec: INTERCEPTA_Selectivity_Redesign_Specification.md")
    print(f"Tag:  selectivity-redesign-spec")

    # Load master to determine which diseases to process
    master = load_master_config()
    diseases_to_process = sorted(master['diseases'].keys())
    print(f"\nProcessing {len(diseases_to_process)} diseases: "
          f"{diseases_to_process}")

    results = {}
    for disease_id in diseases_to_process:
        result = compute_selectivity_for_disease(disease_id)
        results[disease_id] = result
        print_top_selectivity(result, n_top=10)

    # ------------------------------------------------------------------
    # Spec Section 10 — falsifiable success criteria check
    # ------------------------------------------------------------------
    banner("Falsifiable success criteria (spec Section 10)")

    all_pass = True

    # Criterion 3: AML — at least 1 of [FLT3, NPM1, IDH1, IDH2, FLT3-ITD]
    # has non-zero primary_tissue_tpm
    aml_check_genes = ['FLT3', 'NPM1', 'IDH1', 'IDH2']
    if 'aml' in results:
        aml_sel = results['aml']['selectivity_per_gene']
        non_zero = [g for g in aml_check_genes
                    if g in aml_sel
                    and aml_sel[g]['primary_tissue_tpm'] > 0]
        status = 'PASS' if non_zero else 'FAIL'
        print(f"  Criterion 3 (AML non-zero target gene): {status}")
        print(f"    Non-zero genes: {non_zero}")
        if not non_zero:
            all_pass = False

    # Criterion 4: GBM — at least 1 of [EGFR, IDH1, PTEN, TP53]
    if 'gbm' in results:
        gbm_check_genes = ['EGFR', 'IDH1', 'PTEN', 'TP53']
        gbm_sel = results['gbm']['selectivity_per_gene']
        non_zero = [g for g in gbm_check_genes
                    if g in gbm_sel
                    and gbm_sel[g]['primary_tissue_tpm'] > 0]
        status = 'PASS' if non_zero else 'FAIL'
        print(f"  Criterion 4 (GBM non-zero target gene): {status}")
        print(f"    Non-zero genes: {non_zero}")
        if not non_zero:
            all_pass = False

    # Criterion 1: All disease results have no 'prostate_tpm' field
    print(f"  Criterion 1 (no prostate_tpm field for non-mCRPC):", end=' ')
    found_prostate_tpm = False
    for disease_id, result in results.items():
        if disease_id == 'mcrpc':
            continue
        # Check that primary_tissue is not 'Prostate' for non-mCRPC
        if result['primary_tissue'] == 'Prostate':
            print(f"FAIL — {disease_id} primary_tissue is Prostate")
            found_prostate_tpm = True
            all_pass = False
        # Check no per-gene field is named 'prostate_tpm'
        for gene, d in list(result['selectivity_per_gene'].items())[:3]:
            if 'prostate_tpm' in d:
                print(f"FAIL — {disease_id}/{gene} has prostate_tpm field")
                found_prostate_tpm = True
                all_pass = False
                break
    if not found_prostate_tpm:
        print(f"PASS")

    banner("Final summary")
    for disease_id, result in results.items():
        print(f"  {disease_id}: {result['n_genes_found_in_gtex']}/"
              f"{result['n_target_genes']} genes found, "
              f"primary_tissue='{result['primary_tissue']}'")
    print(f"\n  Overall: {'PASS' if all_pass else 'FAIL'}")
    print(f"  Outputs in: {DEFAULT_OUTPUT_DIR}/step6_selectivity_<disease>.json")
    print(f"\nFinished: {datetime.now().isoformat(timespec='seconds')}")

    sys.exit(0 if all_pass else 1)


if __name__ == '__main__':
    main()
