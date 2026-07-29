#!/usr/bin/env python3
"""
INTERCEPTA Round 2.1c Step 2 — AnnData assembly + validation
=============================================================

Purpose
-------
Take the 5 files exported from the Van Galen Seurat V5 RDS in Step 1,
assemble them into an AnnData (.h5ad) object that Python / scanpy /
scVelo can use, and validate the result against Van Galen 2019 biology
before declaring Round 2.1c passed.

Input (from export_vangalen_components_v3.R)
---------------------------------------------
  counts.mtx          Sparse UMI counts, MatrixMarket, 27899 x 44823
  data.mtx            Log-normalized expression, same shape
  gene_names.txt      27,899 HGNC gene symbols
  cell_barcodes.txt   44,823 cell IDs ({sample}_{barcode})
  cell_metadata.csv   44,823 rows, 11 columns of per-cell metadata

Output
------
  vangalen_aml.h5ad   Full AnnData object
    .X           = log-normalized data (Python convention: the main
                   matrix is the one downstream tools expect to work on)
    .layers['counts'] = raw UMI counts preserved for reference
    .obs         = all per-cell metadata (CellType, orig.ident,
                   PredictionRefined, MutTranscripts, ...)
    .var_names   = gene symbols

Validation — THE PASS CRITERION
-------------------------------
Van Galen 2019 Cell paper established a "Leukemic Stem Cell (LSC) score"
signature built from genes over-expressed in HSC-like malignant cells
relative to committed malignant blasts (GMP-like, ProMono-like, Mono-like).

Classic LSC-signature genes with well-published upregulation in HSC-like
AML cells (Eppert 2011 Nat Med; Ng 2016 Nature; Van Galen 2019 Cell):
  HLF, HOPX, CD34, MEIS1, CDK6, MLLT3

If our AnnData preserves the biology, these genes must be:
  (a) present in the gene list
  (b) expressed at higher mean level in HSC-like cells than in
      GMP-like / ProMono-like / Mono-like malignant cells

Pass criteria:
  - At least 4 of the 6 LSC-signature genes show >1.3x mean expression
    ratio (HSC-like / committed-blast) with Mann-Whitney p < 0.01
  - Cell count, gene count, and cell-type distribution match the
    inspector output

If any check fails, the assembly or the underlying data is suspect
and we do not progress to Round 2.1d until resolved.

Dependencies
------------
  pip install anndata scanpy scipy pandas numpy

Run
---
    cd ~/INTERCEPTA/round2_aml/code
    python3 assemble_vangalen_anndata.py 2>&1 | tee \\
        ../results/vangalen_anndata_assembly.txt

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
Date:    April 22, 2026
"""
import os
import sys
import json
from pathlib import Path


EXPORT_DIR = Path(os.environ.get(
    'VANGALEN_EXPORT_DIR',
    str(Path(__file__).resolve().parent.parent / 'data' / 'vangalen2019' / 'exported')
))
RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'
H5AD_OUT = EXPORT_DIR.parent / 'vangalen_aml.h5ad'

# LSC signature (Eppert 2011 Nat Med; Ng 2016 Nature; Van Galen 2019 Cell)
LSC_SIGNATURE = ['HLF', 'HOPX', 'CD34', 'MEIS1', 'CDK6', 'MLLT3']

# Van Galen 2019 cell-type labels that represent malignant blast populations
# (not HSC-like, not normal cell types)
COMMITTED_MALIGNANT_BLASTS = ['GMP-like', 'ProMono-like', 'Mono-like', 'cDC-like']
# HSC-like is the LSC-enriched malignant population (comparison target)
HSC_LIKE_LABEL = 'HSC-like'

# Expected values from the v3 export log
EXPECTED_N_CELLS = 44823
EXPECTED_N_GENES = 27899
EXPECTED_N_NNZ = 50456694  # same for counts and data (log transform preserves zeros)


def banner(s):
    print('\n' + '=' * 72)
    print(s)
    print('=' * 72)


def main():
    # --------------------------------------------------------------
    # Dependency check
    # --------------------------------------------------------------
    banner("Step 0: Dependency check")
    try:
        import numpy as np
        import pandas as pd
        import scipy.io
        import scipy.sparse
        import anndata as ad
        print(f"  numpy    : {np.__version__}")
        print(f"  pandas   : {pd.__version__}")
        print(f"  scipy    : {scipy.__version__}")
        print(f"  anndata  : {ad.__version__}")
    except ImportError as e:
        print(f"  MISSING DEPENDENCY: {e}")
        print("  Install with: pip install anndata scanpy scipy pandas numpy")
        sys.exit(1)

    # --------------------------------------------------------------
    # Verify input files
    # --------------------------------------------------------------
    banner("Step 1: Verify input files")
    required = {
        'counts.mtx': EXPORT_DIR / 'counts.mtx',
        'data.mtx': EXPORT_DIR / 'data.mtx',
        'gene_names.txt': EXPORT_DIR / 'gene_names.txt',
        'cell_barcodes.txt': EXPORT_DIR / 'cell_barcodes.txt',
        'cell_metadata.csv': EXPORT_DIR / 'cell_metadata.csv',
    }
    for name, path in required.items():
        if not path.exists():
            print(f"  MISSING: {path}")
            sys.exit(2)
        size_mb = path.stat().st_size / (1024 * 1024)
        print(f"  [OK] {name:25s} {size_mb:>8.1f} MB  {path}")

    # --------------------------------------------------------------
    # Load components
    # --------------------------------------------------------------
    banner("Step 2: Load components")
    print("  Reading gene_names.txt...")
    gene_names = [line.strip() for line in open(required['gene_names.txt'])]
    print(f"    {len(gene_names):,} genes  (first 3: {gene_names[:3]})")
    assert len(gene_names) == EXPECTED_N_GENES, (
        f"Gene count {len(gene_names)} != expected {EXPECTED_N_GENES}")

    print("  Reading cell_barcodes.txt...")
    cell_barcodes = [line.strip() for line in open(required['cell_barcodes.txt'])]
    print(f"    {len(cell_barcodes):,} cells  (first 3: {cell_barcodes[:3]})")
    assert len(cell_barcodes) == EXPECTED_N_CELLS, (
        f"Cell count {len(cell_barcodes)} != expected {EXPECTED_N_CELLS}")

    print("  Reading cell_metadata.csv...")
    metadata = pd.read_csv(required['cell_metadata.csv'])
    print(f"    {len(metadata):,} rows x {metadata.shape[1]} columns")
    print(f"    columns: {list(metadata.columns)}")
    assert len(metadata) == EXPECTED_N_CELLS
    assert list(metadata['barcode']) == cell_barcodes, (
        "Metadata barcode order does not match cell_barcodes.txt order")

    print("  Reading counts.mtx (this takes 30-60 sec for 50M nnz)...")
    import time
    t0 = time.time()
    counts_mat = scipy.io.mmread(str(required['counts.mtx']))
    print(f"    loaded in {time.time()-t0:.1f}s, shape {counts_mat.shape}, "
          f"nnz {counts_mat.nnz:,}, dtype {counts_mat.dtype}")
    # MM files are loaded as COO; convert to CSR for AnnData
    counts_mat = counts_mat.tocsr()
    assert counts_mat.shape == (EXPECTED_N_GENES, EXPECTED_N_CELLS)
    assert counts_mat.nnz == EXPECTED_N_NNZ, (
        f"Counts nnz {counts_mat.nnz} != expected {EXPECTED_N_NNZ}")

    print("  Reading data.mtx (this takes 60-120 sec for log-norm values)...")
    t0 = time.time()
    data_mat = scipy.io.mmread(str(required['data.mtx']))
    print(f"    loaded in {time.time()-t0:.1f}s, shape {data_mat.shape}, "
          f"nnz {data_mat.nnz:,}, dtype {data_mat.dtype}")
    data_mat = data_mat.tocsr()
    assert data_mat.shape == (EXPECTED_N_GENES, EXPECTED_N_CELLS)
    assert data_mat.nnz == EXPECTED_N_NNZ

    # --------------------------------------------------------------
    # Build AnnData
    # --------------------------------------------------------------
    banner("Step 3: Build AnnData")
    # AnnData convention: obs=cells, var=genes, so matrix is cells x genes
    # Our matrices are genes x cells, so we transpose
    print("  Transposing matrices (genes x cells -> cells x genes)...")
    counts_T = counts_mat.T.tocsr()  # now cells x genes
    data_T   = data_mat.T.tocsr()

    # Set up obs and var
    obs = metadata.set_index('barcode', drop=False).copy()
    # Make CellType and PredictionRefined categorical (memory + AnnData-friendly)
    for col in ['CellType', 'PredictionRefined', 'CyclingBinary', 'orig.ident']:
        if col in obs.columns:
            obs[col] = obs[col].astype('category')

    var = pd.DataFrame(index=gene_names)
    var['gene_symbol'] = gene_names

    print("  Creating AnnData...")
    adata = ad.AnnData(
        X=data_T,
        obs=obs,
        var=var,
    )
    adata.layers['counts'] = counts_T
    adata.uns['source'] = (
        'Van Galen et al. Cell 2019 (DOI: 10.1016/j.cell.2019.01.031); '
        'Figshare DOI: 10.6084/m9.figshare.30581066.v1. '
        'Converted from Seurat V5 RDS via component export + AnnData assembly.'
    )

    print(f"  AnnData: {adata.n_obs:,} cells x {adata.n_vars:,} genes")
    print(f"  X shape: {adata.X.shape}, dtype {adata.X.dtype}")
    print(f"  layers['counts'] shape: {adata.layers['counts'].shape}, "
          f"dtype {adata.layers['counts'].dtype}")
    print(f"  obs columns: {list(adata.obs.columns)}")

    # --------------------------------------------------------------
    # Integrity validation — non-scientific
    # --------------------------------------------------------------
    banner("Step 4: Integrity validation")
    checks = []

    # Check 1: cell-type distribution matches inspector
    expected_celltypes = {
        'T': 7105, 'Prog-like': 7021, 'GMP-like': 3937, 'Mono': 2758,
        'Mono-like': 2731, 'ProMono-like': 2603, 'cDC-like': 2218,
        'HSC-like': 2175, 'NK': 1969, 'HSC': 1709, 'Prog': 1709,
        'CTL': 1338, 'lateEry': 1329, 'ProMono': 1146, 'Plasma': 1146,
        'earlyEry': 1119, 'GMP': 918, 'cDC': 849, 'B': 520,
        'ProB': 298, 'pDC': 225,
    }
    observed = adata.obs['CellType'].value_counts().to_dict()
    mismatches = []
    for ct, expected_n in expected_celltypes.items():
        obs_n = observed.get(ct, 0)
        if obs_n != expected_n:
            mismatches.append(f"{ct}: obs={obs_n}, exp={expected_n}")
    if mismatches:
        print(f"  Cell type distribution MISMATCH: {mismatches}")
        checks.append(('cell_type_distribution', False))
    else:
        print(f"  Cell type distribution: all 21 types match inspector counts ✓")
        checks.append(('cell_type_distribution', True))

    # Check 2: PredictionRefined distribution (normal / malignant / unclear)
    pr_dist = adata.obs['PredictionRefined'].value_counts().to_dict()
    print(f"  PredictionRefined distribution: {pr_dist}")
    pr_ok = set(pr_dist.keys()) == {'normal', 'malignant', 'unclear'}
    checks.append(('prediction_refined_values', pr_ok))
    if pr_ok:
        print(f"  PredictionRefined values match expected set ✓")

    # Check 3: X values look like log-normalized (max should be ~10-15, not huge)
    # Sample a subset to avoid loading full matrix
    sample_max = adata.X[:1000, :].max()
    print(f"  X sample max (first 1000 cells): {sample_max:.2f}")
    x_ok = 5 < sample_max < 20  # log-normalized should be in this range
    checks.append(('X_is_log_normalized', x_ok))
    if x_ok:
        print(f"  X values consistent with log-normalized data ✓")

    # --------------------------------------------------------------
    # Scientific validation — the LSC signature test
    # --------------------------------------------------------------
    banner("Step 5: Scientific validation — LSC signature in HSC-like cells")
    print(f"  Testing: are LSC-signature genes over-expressed in '{HSC_LIKE_LABEL}'")
    print(f"  cells vs committed malignant blasts {COMMITTED_MALIGNANT_BLASTS}?")
    print(f"  Signature: {LSC_SIGNATURE}")
    print()

    # Find cell indices for each population
    hsc_mask = adata.obs['CellType'] == HSC_LIKE_LABEL
    blast_mask = adata.obs['CellType'].isin(COMMITTED_MALIGNANT_BLASTS)
    print(f"  HSC-like cells:          {hsc_mask.sum():,}")
    print(f"  Committed blast cells:   {blast_mask.sum():,}")

    from scipy.stats import mannwhitneyu
    signature_results = []
    for gene in LSC_SIGNATURE:
        if gene not in adata.var_names:
            print(f"  [WARN] {gene}: NOT IN GENE LIST")
            signature_results.append({
                'gene': gene, 'in_list': False,
                'mean_hsc': np.nan, 'mean_blast': np.nan,
                'ratio': np.nan, 'p_value': np.nan, 'pass': False,
            })
            continue

        gene_idx = list(adata.var_names).index(gene)
        # Pull the column for this gene from X (log-normalized)
        hsc_expr = np.asarray(adata.X[hsc_mask.values, gene_idx].todense()).flatten()
        blast_expr = np.asarray(adata.X[blast_mask.values, gene_idx].todense()).flatten()

        mean_hsc = float(hsc_expr.mean())
        mean_blast = float(blast_expr.mean())
        ratio = mean_hsc / mean_blast if mean_blast > 0 else float('inf')

        # Mann-Whitney U (non-parametric, robust to zero-inflation in scRNA-seq)
        if hsc_expr.sum() > 0 or blast_expr.sum() > 0:
            _, pval = mannwhitneyu(hsc_expr, blast_expr, alternative='greater')
        else:
            pval = float('nan')

        gene_pass = (ratio > 1.3) and (pval < 0.01)
        signature_results.append({
            'gene': gene, 'in_list': True,
            'mean_hsc': mean_hsc, 'mean_blast': mean_blast,
            'ratio': ratio, 'p_value': pval, 'pass': gene_pass,
        })

        flag = '✓' if gene_pass else '✗'
        print(f"  {flag} {gene:7s}  mean(HSC-like)={mean_hsc:6.3f}  "
              f"mean(blast)={mean_blast:6.3f}  "
              f"ratio={ratio:5.2f}  p={pval:.2e}")

    n_pass = sum(1 for r in signature_results if r['pass'])
    n_total = sum(1 for r in signature_results if r['in_list'])
    print(f"\n  Passing LSC genes: {n_pass} / {n_total}")
    sig_ok = n_pass >= 4
    checks.append(('lsc_signature_4_of_6', sig_ok))

    # --------------------------------------------------------------
    # Final verdict
    # --------------------------------------------------------------
    banner("Step 6: Verdict")
    for name, passed in checks:
        flag = '✓ PASS' if passed else '✗ FAIL'
        print(f"  {flag}  {name}")

    all_pass = all(p for _, p in checks)
    verdict = 'PASS' if all_pass else 'FAIL'
    print(f"\n  VERDICT: {verdict}")

    if not all_pass:
        print("\n  Any FAIL above must be investigated before Round 2.1c closure.")
        print("  Not saving h5ad — fix upstream and re-run.")
        sys.exit(3)

    # --------------------------------------------------------------
    # Save h5ad
    # --------------------------------------------------------------
    banner("Step 7: Save AnnData")
    print(f"  Writing {H5AD_OUT} ...")
    t0 = time.time()
    adata.write_h5ad(str(H5AD_OUT), compression='gzip')
    dt = time.time() - t0
    size_mb = H5AD_OUT.stat().st_size / (1024 * 1024)
    print(f"  Wrote in {dt:.1f}s, size {size_mb:.1f} MB")

    # Summary JSON
    summary = {
        'verdict': verdict,
        'n_cells': int(adata.n_obs),
        'n_genes': int(adata.n_vars),
        'cell_type_distribution': {str(k): int(v) for k, v in
                                    adata.obs['CellType'].value_counts().items()},
        'prediction_refined_distribution': {str(k): int(v) for k, v in
                                            adata.obs['PredictionRefined'].value_counts().items()},
        'lsc_signature_results': [
            {k: (v if not isinstance(v, (float, np.floating)) or np.isfinite(v) else None)
             for k, v in r.items()}
            for r in signature_results
        ],
        'integrity_checks': {name: passed for name, passed in checks},
        'output_file': str(H5AD_OUT),
    }
    with open(RESULTS_DIR / 'vangalen_anndata_summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"  Summary JSON: {RESULTS_DIR / 'vangalen_anndata_summary.json'}")


if __name__ == '__main__':
    main()
