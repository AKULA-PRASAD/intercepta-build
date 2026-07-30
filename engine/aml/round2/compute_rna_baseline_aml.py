#!/usr/bin/env python3
"""
INTERCEPTA — RNA-Only LightGBM Baseline on BeatAML
====================================================

Purpose
-------
Compute a per-drug AUROC distribution for binarized BeatAML drug response
prediction using RNA-seq features alone (no KAALCURA, no mutation, no
pathway). This baseline is the comparator for Round 2.2c Q_C threshold
setting.

Why this exists
---------------
Round 2 closure cited "MDREAM 0.68 AUROC" as a benchmark — that was
incorrect (MDREAM reports Spearman ρ on continuous AUC, not AUROC on
binary). See INTERCEPTA_Round2_Closure_Erratum.md.

The honest path is to compute our own RNA-only baseline on the EXACT
same task as Round 2.2b (median-binarized AUC, 141-drug panel) so we
can set Round 2.2c's Q_C threshold meaningfully:
  - If RNA-only baseline mean AUROC ≈ 0.55, KAALCURA-3-axis at 0.526
    is not far behind RNA-only and Round 2.2c needs only modest
    multi-modal lift to beat both.
  - If RNA-only baseline mean AUROC ≈ 0.65, KAALCURA-3-axis at 0.526
    is far behind RNA-only and the multi-modal model needs to clearly
    exceed RNA-only.

Method
------
1. Load BeatAML waves 1-4 normalized expression (norm_exp_dbgap.txt)
2. Load BeatAML probit curve fits (drug response, AUC metric)
3. Filter drugs to match Round 2.2b set (≥20 sensitive AND ≥20 resistant
   samples after binarizing AUC at 100, BeatAML's standard threshold)
4. For each filtered drug:
   a. Align expression and response on dbgap_rnaseq_sample
   b. Use top-1000 most variable genes as features (standard practice)
   c. 5-fold stratified CV with LightGBM
   d. Record per-fold AUROC; report mean ± std
5. Save per-drug AUROC distribution to CSV
6. Print summary statistics (mean, median, IQR, n drugs ≥ 0.60)

Reproducibility
---------------
- Random state: 42 (matches KAALCURA Round 1)
- 5-fold StratifiedKFold (matches KAALCURA train_drug_models default)
- Drug binarization: AUC < 100 = sensitive, AUC ≥ 100 = resistant
  (BeatAML standard, matches Round 2.2b)
- Drug filter: ≥20 sensitive AND ≥20 resistant samples
  (matches Tercan 2026 PLOS One; relaxed from Round 2.2b's 10/10)
  Using 20/20 makes our baseline directly comparable to Tercan paper.
- LightGBM defaults — no hyperparameter tuning. This is a baseline,
  not a tuned competitor. Tuned LightGBM would be a stronger comparator
  but ALSO would risk overfitting and be a moving target. Defaults are
  honest: the bar Round 2.2c must clear with multi-modal features.

Author: Prasad Akula, 2026-05-06
"""

import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')
warnings.filterwarnings('ignore', message='.*feature names.*')


# ---------------------------------------------------------------------------
# Paths — matches Round 2.2 codebase conventions
# ---------------------------------------------------------------------------
HOME = Path.home()
BEATAML_ROOT = HOME / 'INTERCEPTA' / 'round2_aml' / 'data' / 'beataml2.0_data-2.0'
BEATAML_EXPR = BEATAML_ROOT / 'beataml_waves1to4_norm_exp_dbgap.txt'
BEATAML_FITS = BEATAML_ROOT / 'beataml_probit_curve_fits_v4_dbgap.txt'

OUTPUT_DIR = HOME / 'INTERCEPTA' / 'round2_aml' / 'results'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = OUTPUT_DIR / 'rna_baseline_auroc_per_drug.csv'
OUT_SUMMARY = OUTPUT_DIR / 'rna_baseline_auroc_summary.json'

# Method parameters — locked, no tuning
N_TOP_VAR_GENES = 1000
N_CV_FOLDS = 5
RANDOM_STATE = 42
MIN_SENSITIVE = 20
MIN_RESISTANT = 20
AUC_THRESHOLD = 100.0  # BeatAML standard: AUC<100 = sensitive

# ---------------------------------------------------------------------------
# Dependencies — verify before doing anything expensive
# ---------------------------------------------------------------------------

def banner(msg):
    print('\n' + '=' * 72)
    print(msg)
    print('=' * 72)


def check_deps():
    """Fail fast on missing dependencies, with install hints."""
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
        print("Install via:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(2)


def check_files():
    """Verify input files exist before loading anything."""
    for label, p in [('expression', BEATAML_EXPR), ('curve_fits', BEATAML_FITS)]:
        if not p.exists():
            sys.exit(f"MISSING: {label} file at {p}")
        size_mb = p.stat().st_size / 1024 / 1024
        print(f"  {label}: {p.name} ({size_mb:.1f} MB)")


# ---------------------------------------------------------------------------
# Data loading — reuses Round 2.2 conventions (verified in code/audit)
# ---------------------------------------------------------------------------

def load_expression():
    """
    Load BeatAML norm_exp wide-format file.

    Format: rows = genes (with metadata columns), columns = samples.
    Returns DataFrame indexed by sample, columns = gene symbols.
    """
    print(f"  Reading {BEATAML_EXPR.name}...")
    raw = pd.read_csv(BEATAML_EXPR, sep='\t', low_memory=False)
    print(f"  Raw shape: {raw.shape}")
    print(f"  First 5 columns: {list(raw.columns[:5])}")

    # BeatAML format: metadata columns include stable_id, display_label,
    # description, biotype. display_label is the gene symbol.
    metadata_cols = {'stable_id', 'display_label', 'description', 'biotype'}
    gene_col = 'display_label' if 'display_label' in raw.columns else raw.columns[0]
    if gene_col != 'display_label':
        print(f"  WARNING: 'display_label' not found, using '{gene_col}' as gene column")

    # Sample columns are everything except metadata
    sample_cols = [c for c in raw.columns if c not in metadata_cols]
    print(f"  Gene column: '{gene_col}'")
    print(f"  Sample columns: {len(sample_cols)} samples")

    # Build expression matrix: samples × genes
    # Drop genes with missing or duplicate symbols
    raw = raw.dropna(subset=[gene_col])
    # If duplicates, keep the row with highest mean expression
    expr_data = raw[[gene_col] + sample_cols].copy()
    expr_data['_mean'] = raw[sample_cols].mean(axis=1)
    expr_data = expr_data.sort_values('_mean', ascending=False)
    expr_data = expr_data.drop_duplicates(subset=[gene_col], keep='first')
    expr_data = expr_data.drop(columns=['_mean'])

    # Pivot
    expr_data = expr_data.set_index(gene_col)
    expr_matrix = expr_data[sample_cols].T  # samples × genes
    print(f"  Final expression matrix: {expr_matrix.shape[0]} samples × {expr_matrix.shape[1]} genes")
    return expr_matrix


def load_drug_response():
    """
    Load BeatAML probit curve fits.

    Returns DataFrame with columns: dbgap_rnaseq_sample, inhibitor, auc
    """
    print(f"  Reading {BEATAML_FITS.name}...")
    fits = pd.read_csv(BEATAML_FITS, sep='\t', low_memory=False)
    print(f"  Raw shape: {fits.shape}")
    print(f"  Columns: {list(fits.columns)}")

    # Required columns (verified in Round 2.2 codebase)
    sample_col = 'dbgap_rnaseq_sample'
    drug_col = 'inhibitor'
    auc_col = 'auc'

    for col in [sample_col, drug_col, auc_col]:
        if col not in fits.columns:
            sys.exit(f"MISSING column '{col}' in {BEATAML_FITS.name}. "
                     f"Available: {list(fits.columns)}")

    fits = fits[[sample_col, drug_col, auc_col]].dropna()
    print(f"  After dropna: {len(fits)} (sample, drug, auc) rows")
    print(f"  Unique drugs: {fits[drug_col].nunique()}")
    print(f"  Unique samples: {fits[sample_col].nunique()}")
    return fits


# ---------------------------------------------------------------------------
# Per-drug evaluation
# ---------------------------------------------------------------------------

def select_top_var_genes(expr_matrix, n_top):
    """Select n_top most variable genes by variance across samples."""
    gene_var = expr_matrix.var(axis=0)
    top_genes = gene_var.nlargest(n_top).index.tolist()
    return top_genes


def evaluate_drug(X, y, drug_name, n_folds, random_state):
    """
    5-fold stratified CV with LightGBM defaults.
    Returns mean AUROC, std AUROC, n_sensitive, n_resistant.
    """
    from sklearn.model_selection import StratifiedKFold
    from sklearn.metrics import roc_auc_score
    import lightgbm as lgb

    n_sensitive = int(y.sum())
    n_resistant = int(len(y) - n_sensitive)

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)
    fold_aurocs = []

    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # LightGBM defaults — no tuning
        model = lgb.LGBMClassifier(
            n_estimators=100,
            learning_rate=0.1,
            num_leaves=31,
            random_state=random_state,
            n_jobs=-1,
            verbosity=-1,
        )
        model.fit(X_train, y_train)
        y_proba = model.predict_proba(X_test)[:, 1]

        try:
            auroc = roc_auc_score(y_test, y_proba)
        except ValueError:
            # Single-class fold — should be rare with stratified CV but possible
            auroc = float('nan')
        fold_aurocs.append(auroc)

    fold_aurocs = np.array(fold_aurocs)
    valid = ~np.isnan(fold_aurocs)
    if valid.sum() < 2:
        return None  # Insufficient valid folds

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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    banner("RNA-Only LightGBM Baseline — BeatAML Drug Sensitivity")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Method:")
    print(f"  Top-{N_TOP_VAR_GENES} most variable genes as features")
    print(f"  {N_CV_FOLDS}-fold StratifiedKFold")
    print(f"  LightGBM defaults (n_estimators=100, lr=0.1, num_leaves=31)")
    print(f"  AUC threshold: {AUC_THRESHOLD} (BeatAML standard)")
    print(f"  Drug filter: ≥{MIN_SENSITIVE} sensitive AND ≥{MIN_RESISTANT} resistant")

    banner("Step 1: Dependencies")
    check_deps()

    banner("Step 2: File availability")
    check_files()

    banner("Step 3: Load expression matrix")
    expr_matrix = load_expression()

    banner("Step 4: Load drug response")
    fits = load_drug_response()

    banner("Step 5: Filter drugs (≥20 sensitive AND ≥20 resistant)")
    drug_stats = []
    for drug, group in fits.groupby('inhibitor'):
        n_sens = int((group['auc'] < AUC_THRESHOLD).sum())
        n_res = int((group['auc'] >= AUC_THRESHOLD).sum())
        if n_sens >= MIN_SENSITIVE and n_res >= MIN_RESISTANT:
            drug_stats.append({
                'drug': drug,
                'n_sensitive': n_sens,
                'n_resistant': n_res,
                'n_total': n_sens + n_res,
            })
    drug_df = pd.DataFrame(drug_stats).sort_values('n_total', ascending=False)
    print(f"  Drugs passing filter: {len(drug_df)}")
    if len(drug_df) == 0:
        sys.exit("No drugs pass filter. Check data or relax thresholds.")
    print(f"  Sample sizes: median {drug_df['n_total'].median():.0f}, "
          f"range [{drug_df['n_total'].min()}, {drug_df['n_total'].max()}]")

    banner("Step 6: Sample alignment between expression and drug response")
    # Get samples that exist in both expression matrix index and drug fits
    expr_samples = set(expr_matrix.index.astype(str))
    fits_samples = set(fits['dbgap_rnaseq_sample'].astype(str))
    common_samples = expr_samples & fits_samples
    print(f"  Expression samples: {len(expr_samples)}")
    print(f"  Drug response samples: {len(fits_samples)}")
    print(f"  Common: {len(common_samples)}")
    if len(common_samples) < 100:
        sys.exit("Too few common samples. Check sample ID encoding (str vs int).")

    # Restrict to common samples
    expr_matrix.index = expr_matrix.index.astype(str)
    expr_matrix = expr_matrix.loc[expr_matrix.index.isin(common_samples)]
    print(f"  Expression matrix restricted: {expr_matrix.shape}")

    banner(f"Step 7: Select top {N_TOP_VAR_GENES} most variable genes")
    top_genes = select_top_var_genes(expr_matrix, N_TOP_VAR_GENES)
    expr_top = expr_matrix[top_genes]
    print(f"  Feature matrix: {expr_top.shape}")
    print(f"  First 5 selected genes: {top_genes[:5]}")

    banner("Step 8: Per-drug evaluation")
    results = []
    failed_drugs = []
    t_start = time.time()
    for i, row in enumerate(drug_df.itertuples(), 1):
        drug = row.drug
        # Get this drug's response
        drug_fits = fits[fits['inhibitor'] == drug].copy()
        drug_fits['_sid'] = drug_fits['dbgap_rnaseq_sample'].astype(str)
        # Align with expression
        common = drug_fits[drug_fits['_sid'].isin(expr_top.index)]
        if len(common) < (MIN_SENSITIVE + MIN_RESISTANT):
            failed_drugs.append((drug, 'too_few_after_alignment', len(common)))
            continue

        # Take first occurrence per sample (a sample might have multiple test wells)
        common = common.drop_duplicates(subset=['_sid'], keep='first')
        X = expr_top.loc[common['_sid']].values
        y = (common['auc'].values < AUC_THRESHOLD).astype(int)

        n_sens = int(y.sum())
        n_res = int(len(y) - n_sens)
        if n_sens < MIN_SENSITIVE or n_res < MIN_RESISTANT:
            failed_drugs.append((drug, 'imbalanced_after_alignment', f'{n_sens}/{n_res}'))
            continue

        result = evaluate_drug(X, y, drug, N_CV_FOLDS, RANDOM_STATE)
        if result is None:
            failed_drugs.append((drug, 'cv_failure', None))
            continue
        results.append(result)

        if i % 10 == 0 or i == len(drug_df):
            elapsed = time.time() - t_start
            avg_per = elapsed / i if i > 0 else 0
            eta = avg_per * (len(drug_df) - i)
            print(f"  [{i}/{len(drug_df)}] last drug='{drug}' "
                  f"AUROC={result['auroc_mean']:.3f} | "
                  f"elapsed={elapsed:.0f}s ETA={eta:.0f}s")

    print(f"\n  Successfully evaluated: {len(results)} drugs")
    print(f"  Failed: {len(failed_drugs)} drugs")
    if failed_drugs:
        print("  Failure reasons:")
        from collections import Counter
        reasons = Counter([f[1] for f in failed_drugs])
        for reason, count in reasons.items():
            print(f"    {reason}: {count}")

    banner("Step 9: Save results")
    df = pd.DataFrame(results)
    # Drop fold_aurocs column for CSV (kept in JSON)
    df_csv = df.drop(columns=['fold_aurocs']).sort_values('auroc_mean', ascending=False)
    df_csv.to_csv(OUT_CSV, index=False)
    print(f"  Per-drug AUROC: {OUT_CSV}")

    banner("Step 10: Summary statistics — RNA-only state-of-art baseline")
    aurocs = df['auroc_mean'].values
    summary = {
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
        'method': 'LightGBM defaults, top-1000 variable genes, 5-fold StratifiedKFold',
        'task': 'binarized AUC<100 sensitivity prediction',
        'random_state': RANDOM_STATE,
        'n_top_var_genes': N_TOP_VAR_GENES,
        'n_cv_folds': N_CV_FOLDS,
        'auc_threshold': AUC_THRESHOLD,
        'min_sensitive': MIN_SENSITIVE,
        'min_resistant': MIN_RESISTANT,
        'comparators': {
            'kaalcura_round22b_mean_auroc': 0.526,
            'kaalcura_round22b_n_drugs_trained': 141,
            'kaalcura_round22b_n_drugs_ge_0_60': 27,
            'note': 'Round 2.2b filter was looser (>=10 each class). This baseline uses >=20 each class.',
        },
    }
    with open(OUT_SUMMARY, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"  Summary JSON: {OUT_SUMMARY}")

    print(f"\n  RNA-only baseline AUROC distribution ({len(results)} drugs):")
    print(f"    mean   = {summary['auroc_mean']:.3f}")
    print(f"    median = {summary['auroc_median']:.3f}")
    print(f"    IQR    = [{summary['auroc_q25']:.3f}, {summary['auroc_q75']:.3f}]")
    print(f"    range  = [{summary['auroc_min']:.3f}, {summary['auroc_max']:.3f}]")
    print(f"    ≥0.55: {summary['n_drugs_auroc_ge_0_55']} drugs ({100*summary['n_drugs_auroc_ge_0_55']/len(results):.0f}%)")
    print(f"    ≥0.60: {summary['n_drugs_auroc_ge_0_60']} drugs ({100*summary['n_drugs_auroc_ge_0_60']/len(results):.0f}%)")
    print(f"    ≥0.65: {summary['n_drugs_auroc_ge_0_65']} drugs ({100*summary['n_drugs_auroc_ge_0_65']/len(results):.0f}%)")
    print(f"    ≥0.70: {summary['n_drugs_auroc_ge_0_70']} drugs ({100*summary['n_drugs_auroc_ge_0_70']/len(results):.0f}%)")

    print(f"\n  Comparator: KAALCURA Round 2.2b mean AUROC = 0.526 (3 axes only)")
    print(f"  This baseline tells us where RNA-only state-of-art lands on the SAME task.")
    print(f"  Round 2.2c Q_C threshold should exceed BOTH KAALCURA-only AND RNA-only.")

    banner("DONE")
    print(f"Finished: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Files saved:")
    print(f"  {OUT_CSV}")
    print(f"  {OUT_SUMMARY}")


if __name__ == '__main__':
    main()
