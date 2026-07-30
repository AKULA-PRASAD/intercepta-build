#!/usr/bin/env python3
"""
INTERCEPTA — RNA-Only LightGBM Baseline v2 (sex-filtered, 10/10 drug filter)
=============================================================================

What changed from v1
--------------------
v1 found XIST, RPS4Y1, KDM5D, TXLNG2P, DDX3Y as top-5 most variable genes —
all sex-linked. The 0.670 mean AUROC may have been partially driven by
sex-based stratification, not biology.

v2 fixes:
  1. Drop chrX and chrY genes BEFORE variance selection.
  2. Use Round 2.2b's exact filter: ≥10 sensitive AND ≥10 resistant
     (matches the 141-drug panel KAALCURA was actually trained on).

Why this matters
----------------
- v1 0.670 mean AUROC over 56 drugs may include sex confound + easier-task bias
- v2 result is a clean apples-to-apples comparator for KAALCURA Round 2.2b
- If v2 still beats KAALCURA, the gap is real (not artifact)
- If v2 narrows substantially, KAALCURA's competitiveness improves

Author: Prasad Akula, 2026-05-06
"""

import json
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')
warnings.filterwarnings('ignore', message='.*feature names.*')

HOME = Path.home()
BEATAML_ROOT = HOME / 'INTERCEPTA' / 'round2_aml' / 'data' / 'beataml2.0_data-2.0'
BEATAML_EXPR = BEATAML_ROOT / 'beataml_waves1to4_norm_exp_dbgap.txt'
BEATAML_FITS = BEATAML_ROOT / 'beataml_probit_curve_fits_v4_dbgap.txt'

OUTPUT_DIR = HOME / 'INTERCEPTA' / 'round2_aml' / 'results'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = OUTPUT_DIR / 'rna_baseline_v2_auroc_per_drug.csv'
OUT_SUMMARY = OUTPUT_DIR / 'rna_baseline_v2_auroc_summary.json'

# v2 parameters
N_TOP_VAR_GENES = 1000
N_CV_FOLDS = 5
RANDOM_STATE = 42
MIN_SENSITIVE = 10  # v1 was 20; v2 matches Round 2.2b
MIN_RESISTANT = 10  # v1 was 20; v2 matches Round 2.2b
AUC_THRESHOLD = 100.0


def banner(msg):
    print('\n' + '=' * 72)
    print(msg)
    print('=' * 72)


def check_deps():
    missing = []
    try:
        import lightgbm
        print(f"  lightgbm   : {lightgbm.__version__}")
    except ImportError:
        missing.append('lightgbm')
    try:
        from sklearn.model_selection import StratifiedKFold
        from sklearn.metrics import roc_auc_score
        import sklearn
        print(f"  scikit-learn: {sklearn.__version__}")
    except ImportError:
        missing.append('scikit-learn')
    print(f"  numpy      : {np.__version__}")
    print(f"  pandas     : {pd.__version__}")
    if missing:
        print("\nMISSING:", missing)
        sys.exit(2)


def check_files():
    for label, p in [('expression', BEATAML_EXPR), ('curve_fits', BEATAML_FITS)]:
        if not p.exists():
            sys.exit(f"MISSING: {label} file at {p}")
        size_mb = p.stat().st_size / 1024 / 1024
        print(f"  {label}: {p.name} ({size_mb:.1f} MB)")


def load_expression_with_chrom_filter():
    """
    Load BeatAML norm_exp and drop chrX/chrY genes by symbol.
    
    BeatAML uses Ensembl-style 'display_label' = HGNC symbol. We can't
    look up chromosome from symbol alone without an annotation file —
    but we CAN drop the obvious sex-chromosome genes that v1 surfaced
    as top-variance offenders, plus a curated list of well-known
    sex-linked highly-variable genes.
    
    For a more rigorous solution we'd join with Ensembl gene-info,
    but for a baseline this is sufficient: the goal is to remove the
    sex confound that dominated v1's variance ranking.
    """
    print(f"  Reading {BEATAML_EXPR.name}...")
    raw = pd.read_csv(BEATAML_EXPR, sep='\t', low_memory=False)
    print(f"  Raw shape: {raw.shape}")

    metadata_cols = {'stable_id', 'display_label', 'description', 'biotype'}
    gene_col = 'display_label'
    sample_cols = [c for c in raw.columns if c not in metadata_cols]
    print(f"  Sample columns: {len(sample_cols)} samples")

    # Curated list of well-known chrX/chrY genes that are differentially
    # expressed by sex and dominate variance in mixed-sex cohorts.
    # Sources: Ensembl chrX/chrY annotations, escape-from-X-inactivation
    # reviews (Tukiainen 2017 Nature, Carrel & Willard 2005)
    SEX_LINKED_GENES = {
        # X-inactivation / X escape
        'XIST', 'TSIX', 'KDM6A', 'DDX3X', 'EIF1AX', 'ZFX', 'USP9X',
        'KDM5C', 'UTX', 'JPX', 'FTX', 'RPS4X', 'EIF2S3', 'SMC1A',
        'HUWE1', 'NLGN4X', 'STS',
        # Y-chromosome
        'RPS4Y1', 'RPS4Y2', 'KDM5D', 'DDX3Y', 'EIF1AY', 'UTY',
        'NLGN4Y', 'USP9Y', 'ZFY', 'SRY', 'TBL1Y', 'AMELY', 'TMSB4Y',
        'TSPY1', 'TSPY2', 'TSPY3', 'TSPY4', 'TSPY8', 'TSPY10',
        'TXLNGY', 'TXLNG2P',  # v1 surfaced TXLNG2P
        'PRKY', 'PRY', 'PRY2', 'XKRY',
        # X-Y homologs that show sex-dimorphic expression
        'BCORL1', 'BCORL2',
    }

    raw = raw.dropna(subset=[gene_col])
    n_before = len(raw)
    raw = raw[~raw[gene_col].isin(SEX_LINKED_GENES)]
    n_after = len(raw)
    print(f"  Sex-linked genes filtered: {n_before - n_after} dropped, {n_after} remain")

    # Deduplicate by keeping highest-mean
    expr_data = raw[[gene_col] + sample_cols].copy()
    expr_data['_mean'] = raw[sample_cols].mean(axis=1)
    expr_data = expr_data.sort_values('_mean', ascending=False)
    expr_data = expr_data.drop_duplicates(subset=[gene_col], keep='first')
    expr_data = expr_data.drop(columns=['_mean'])

    expr_data = expr_data.set_index(gene_col)
    expr_matrix = expr_data[sample_cols].T
    print(f"  Final expression matrix: {expr_matrix.shape[0]} samples × {expr_matrix.shape[1]} genes")
    return expr_matrix


def load_drug_response():
    print(f"  Reading {BEATAML_FITS.name}...")
    fits = pd.read_csv(BEATAML_FITS, sep='\t', low_memory=False)
    print(f"  Raw shape: {fits.shape}")
    fits = fits[['dbgap_rnaseq_sample', 'inhibitor', 'auc']].dropna()
    print(f"  After dropna: {len(fits)} (sample, drug, auc) rows")
    print(f"  Unique drugs: {fits['inhibitor'].nunique()}")
    print(f"  Unique samples: {fits['dbgap_rnaseq_sample'].nunique()}")
    return fits


def select_top_var_genes(expr_matrix, n_top):
    gene_var = expr_matrix.var(axis=0)
    return gene_var.nlargest(n_top).index.tolist()


def evaluate_drug(X, y, drug_name, n_folds, random_state):
    from sklearn.model_selection import StratifiedKFold
    from sklearn.metrics import roc_auc_score
    import lightgbm as lgb

    n_sensitive = int(y.sum())
    n_resistant = int(len(y) - n_sensitive)

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)
    fold_aurocs = []

    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        model = lgb.LGBMClassifier(
            n_estimators=100, learning_rate=0.1, num_leaves=31,
            random_state=random_state, n_jobs=-1, verbosity=-1,
        )
        model.fit(X_train, y_train)
        y_proba = model.predict_proba(X_test)[:, 1]
        try:
            fold_aurocs.append(roc_auc_score(y_test, y_proba))
        except ValueError:
            fold_aurocs.append(float('nan'))

    fold_aurocs = np.array(fold_aurocs)
    valid = ~np.isnan(fold_aurocs)
    if valid.sum() < 2:
        return None
    return {
        'drug': drug_name,
        'n_samples': int(len(y)),
        'n_sensitive': n_sensitive,
        'n_resistant': n_resistant,
        'auroc_mean': float(np.nanmean(fold_aurocs)),
        'auroc_std': float(np.nanstd(fold_aurocs)),
        'auroc_min': float(np.nanmin(fold_aurocs)),
        'auroc_max': float(np.nanmax(fold_aurocs)),
        'n_valid_folds': int(valid.sum()),
        'fold_aurocs': fold_aurocs.tolist(),
    }


def main():
    banner("RNA-Only LightGBM Baseline v2 — Sex-filtered + Round 2.2b drug filter")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Method:")
    print(f"  Top-{N_TOP_VAR_GENES} most variable genes AFTER chrX/chrY filter")
    print(f"  {N_CV_FOLDS}-fold StratifiedKFold")
    print(f"  Drug filter: ≥{MIN_SENSITIVE} sens AND ≥{MIN_RESISTANT} res (matches Round 2.2b)")

    banner("Step 1: Dependencies")
    check_deps()

    banner("Step 2: Files")
    check_files()

    banner("Step 3: Load expression with sex-chromosome filter")
    expr_matrix = load_expression_with_chrom_filter()

    banner("Step 4: Load drug response")
    fits = load_drug_response()

    banner("Step 5: Filter drugs (≥10 sensitive AND ≥10 resistant)")
    drug_stats = []
    for drug, group in fits.groupby('inhibitor'):
        n_sens = int((group['auc'] < AUC_THRESHOLD).sum())
        n_res = int((group['auc'] >= AUC_THRESHOLD).sum())
        if n_sens >= MIN_SENSITIVE and n_res >= MIN_RESISTANT:
            drug_stats.append({'drug': drug, 'n_sensitive': n_sens,
                               'n_resistant': n_res, 'n_total': n_sens + n_res})
    drug_df = pd.DataFrame(drug_stats).sort_values('n_total', ascending=False)
    print(f"  Drugs passing filter: {len(drug_df)}")
    print(f"  Sample sizes: median {drug_df['n_total'].median():.0f}, "
          f"range [{drug_df['n_total'].min()}, {drug_df['n_total'].max()}]")
    print(f"  Round 2.2b reported 141 trained drugs — we expect similar count here.")

    banner("Step 6: Sample alignment")
    expr_matrix.index = expr_matrix.index.astype(str)
    fits['_sid'] = fits['dbgap_rnaseq_sample'].astype(str)
    common = set(expr_matrix.index) & set(fits['_sid'])
    print(f"  Expression samples: {len(expr_matrix)}, Drug samples: {fits['_sid'].nunique()}, Common: {len(common)}")
    expr_matrix = expr_matrix.loc[expr_matrix.index.isin(common)]

    banner(f"Step 7: Select top {N_TOP_VAR_GENES} most variable genes (post sex-filter)")
    top_genes = select_top_var_genes(expr_matrix, N_TOP_VAR_GENES)
    expr_top = expr_matrix[top_genes]
    print(f"  Feature matrix: {expr_top.shape}")
    print(f"  First 5 selected genes: {top_genes[:5]}")
    print(f"  (v1 had: XIST, RPS4Y1, KDM5D, TXLNG2P, DDX3Y — all sex-linked)")

    banner("Step 8: Per-drug evaluation")
    results = []
    failed_drugs = []
    t_start = time.time()
    for i, row in enumerate(drug_df.itertuples(), 1):
        drug = row.drug
        drug_fits = fits[fits['inhibitor'] == drug].copy()
        common_drug = drug_fits[drug_fits['_sid'].isin(expr_top.index)]
        if len(common_drug) < (MIN_SENSITIVE + MIN_RESISTANT):
            failed_drugs.append((drug, 'too_few_after_alignment', len(common_drug)))
            continue
        common_drug = common_drug.drop_duplicates(subset=['_sid'], keep='first')
        X = expr_top.loc[common_drug['_sid']].values
        y = (common_drug['auc'].values < AUC_THRESHOLD).astype(int)
        n_sens = int(y.sum()); n_res = int(len(y) - n_sens)
        if n_sens < MIN_SENSITIVE or n_res < MIN_RESISTANT:
            failed_drugs.append((drug, 'imbalanced_after_alignment', f'{n_sens}/{n_res}'))
            continue
        result = evaluate_drug(X, y, drug, N_CV_FOLDS, RANDOM_STATE)
        if result is None:
            failed_drugs.append((drug, 'cv_failure', None))
            continue
        results.append(result)
        if i % 20 == 0 or i == len(drug_df):
            elapsed = time.time() - t_start
            avg = elapsed / i
            eta = avg * (len(drug_df) - i)
            print(f"  [{i}/{len(drug_df)}] last='{drug}' AUROC={result['auroc_mean']:.3f} | elapsed={elapsed:.0f}s ETA={eta:.0f}s")

    print(f"\n  Evaluated: {len(results)} drugs, Failed: {len(failed_drugs)}")

    banner("Step 9: Save")
    df = pd.DataFrame(results)
    df_csv = df.drop(columns=['fold_aurocs']).sort_values('auroc_mean', ascending=False)
    df_csv.to_csv(OUT_CSV, index=False)
    print(f"  CSV: {OUT_CSV}")

    banner("Step 10: Summary — RNA-only baseline v2 (sex-filtered, 10/10)")
    aurocs = df['auroc_mean'].values
    summary = {
        'version': 'v2_sex_filtered_10_10',
        'n_drugs_evaluated': len(results),
        'n_drugs_failed': len(failed_drugs),
        'auroc_mean': float(np.mean(aurocs)),
        'auroc_median': float(np.median(aurocs)),
        'auroc_std': float(np.std(aurocs)),
        'auroc_q25': float(np.percentile(aurocs, 25)),
        'auroc_q75': float(np.percentile(aurocs, 75)),
        'auroc_min': float(np.min(aurocs)),
        'auroc_max': float(np.max(aurocs)),
        'n_drugs_auroc_ge_0_55': int(np.sum(aurocs >= 0.55)),
        'n_drugs_auroc_ge_0_60': int(np.sum(aurocs >= 0.60)),
        'n_drugs_auroc_ge_0_65': int(np.sum(aurocs >= 0.65)),
        'n_drugs_auroc_ge_0_70': int(np.sum(aurocs >= 0.70)),
        'method': 'LightGBM, top-1000 var genes after chrX/chrY filter, 5-fold CV',
        'task': 'binarized AUC<100 sensitivity prediction',
        'min_sensitive': MIN_SENSITIVE,
        'min_resistant': MIN_RESISTANT,
        'comparators': {
            'kaalcura_round22b_mean_auroc': 0.526,
            'kaalcura_round22b_n_drugs_trained': 141,
            'kaalcura_round22b_n_drugs_ge_0_60': 27,
            'rna_baseline_v1_mean_auroc': 0.670,
            'rna_baseline_v1_n_drugs': 56,
            'rna_baseline_v1_top5_genes': ['XIST', 'RPS4Y1', 'KDM5D', 'TXLNG2P', 'DDX3Y'],
        },
    }
    with open(OUT_SUMMARY, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"  JSON: {OUT_SUMMARY}")

    print(f"\n  v2 RNA-only baseline (sex-filtered, 10/10 filter):")
    print(f"    n drugs   = {len(results)}")
    print(f"    mean      = {summary['auroc_mean']:.3f}")
    print(f"    median    = {summary['auroc_median']:.3f}")
    print(f"    IQR       = [{summary['auroc_q25']:.3f}, {summary['auroc_q75']:.3f}]")
    print(f"    range     = [{summary['auroc_min']:.3f}, {summary['auroc_max']:.3f}]")
    print(f"    ≥0.55: {summary['n_drugs_auroc_ge_0_55']} ({100*summary['n_drugs_auroc_ge_0_55']/len(results):.0f}%)")
    print(f"    ≥0.60: {summary['n_drugs_auroc_ge_0_60']} ({100*summary['n_drugs_auroc_ge_0_60']/len(results):.0f}%)")
    print(f"    ≥0.65: {summary['n_drugs_auroc_ge_0_65']} ({100*summary['n_drugs_auroc_ge_0_65']/len(results):.0f}%)")
    print(f"    ≥0.70: {summary['n_drugs_auroc_ge_0_70']} ({100*summary['n_drugs_auroc_ge_0_70']/len(results):.0f}%)")

    print(f"\n  Three-way comparison:")
    print(f"    KAALCURA-3-axis-LR  (R2.2b)        : 0.526 mean over 141 drugs")
    print(f"    RNA-1000-LightGBM   (v1, sex+20/20): 0.670 mean over 56 drugs")
    print(f"    RNA-1000-LightGBM   (v2, no-sex+10/10): {summary['auroc_mean']:.3f} mean over {len(results)} drugs")

    banner("DONE")


if __name__ == '__main__':
    main()
