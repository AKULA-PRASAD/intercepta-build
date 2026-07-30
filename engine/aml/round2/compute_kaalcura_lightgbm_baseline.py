#!/usr/bin/env python3
"""
INTERCEPTA — KAALCURA-Axes-into-LightGBM Baseline
====================================================

Purpose
-------
Round 2.2b used KAALCURA 3-axes + LogisticRegression and got mean AUROC 0.526.
The RNA-only LightGBM baseline got 0.670 (or post-sex-filter v2 number).

The 0.144 gap could be:
  (a) Feature gap: 3 axes have less signal than 1000 RNA genes
  (b) Model gap: LogisticRegression is weaker than LightGBM on tabular data
  (c) Both

This script runs LightGBM on JUST the 3 KAALCURA axes (the same axes file
Round 2.2b produced). Result tells us how much of the 0.144 gap is model vs
feature.

Three points after this:
  - KAALCURA-3-axis-LogReg     : 0.526 (Round 2.2b)
  - KAALCURA-3-axis-LightGBM   : ?     (this script)
  - RNA-1000-LightGBM          : 0.670 (v1) / TBD (v2)

If KAALCURA-3-LightGBM ≈ 0.55, the 0.526→0.670 gap is mostly features.
If KAALCURA-3-LightGBM ≈ 0.60, model contributes meaningfully too.
If KAALCURA-3-LightGBM ≈ 0.65, model nearly closes the whole gap.

Author: Prasad Akula, 2026-05-06
"""

import json
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
BEATAML_FITS = BEATAML_ROOT / 'beataml_probit_curve_fits_v4_dbgap.txt'

# KAALCURA axes from Round 2.2b — durable artifact per closure section 6
RESULTS_DIR = HOME / 'INTERCEPTA' / 'round2_aml' / 'results'
KAALCURA_AXES = RESULTS_DIR / 'beataml_ucell_residual_axes_round22b.csv'
# Fallback to v5_2 if 22b not present
KAALCURA_AXES_FALLBACK = RESULTS_DIR / 'beataml_kaalcura_axes_v5_2.csv'

OUT_CSV = RESULTS_DIR / 'kaalcura_lightgbm_auroc_per_drug.csv'
OUT_SUMMARY = RESULTS_DIR / 'kaalcura_lightgbm_auroc_summary.json'

N_CV_FOLDS = 5
RANDOM_STATE = 42
MIN_SENSITIVE = 10
MIN_RESISTANT = 10
AUC_THRESHOLD = 100.0


def banner(msg):
    print('\n' + '=' * 72)
    print(msg)
    print('=' * 72)


def main():
    banner("KAALCURA-3-Axes-into-LightGBM Baseline")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    banner("Step 1: Dependencies")
    try:
        import lightgbm
        from sklearn.model_selection import StratifiedKFold
        from sklearn.metrics import roc_auc_score
        print(f"  lightgbm: {lightgbm.__version__}")
    except ImportError as e:
        sys.exit(f"MISSING: {e}")

    banner("Step 2: Load KAALCURA axes")
    if KAALCURA_AXES.exists():
        axes_path = KAALCURA_AXES
        print(f"  Using Round 2.2b residualized axes: {axes_path.name}")
    elif KAALCURA_AXES_FALLBACK.exists():
        axes_path = KAALCURA_AXES_FALLBACK
        print(f"  Round 2.2b axes not found, falling back to v5_2: {axes_path.name}")
    else:
        sys.exit(f"NO KAALCURA axes file found. Tried:\n  {KAALCURA_AXES}\n  {KAALCURA_AXES_FALLBACK}")

    axes = pd.read_csv(axes_path)
    print(f"  Shape: {axes.shape}")
    print(f"  Columns: {list(axes.columns)}")

    # Auto-detect sample ID column
    id_candidates = [c for c in axes.columns if 'sample' in c.lower() or c.lower().startswith('dbgap') or c == axes.columns[0]]
    sample_col = None
    for c in id_candidates:
        if axes[c].dtype == object or axes[c].dtype.name.startswith('int'):
            sample_col = c
            break
    if sample_col is None:
        sample_col = axes.columns[0]
    print(f"  Detected sample column: '{sample_col}'")

    # Auto-detect axis columns (must contain R_prolif, R_emt, R_ddr or similar)
    axis_cols = []
    for target in ['R_prolif', 'R_emt', 'R_ddr']:
        for c in axes.columns:
            if target.lower() in c.lower():
                axis_cols.append(c)
                break
    if len(axis_cols) != 3:
        # Fallback: assume last 3 numeric columns
        numeric_cols = [c for c in axes.columns if pd.api.types.is_numeric_dtype(axes[c])]
        axis_cols = numeric_cols[-3:]
        print(f"  WARNING: fuzzy axis detection failed, using last 3 numeric: {axis_cols}")
    print(f"  Axis columns: {axis_cols}")

    axes = axes[[sample_col] + axis_cols].dropna()
    axes['_sid'] = axes[sample_col].astype(str)
    print(f"  After dropna: {len(axes)} samples")

    banner("Step 3: Load drug response")
    fits = pd.read_csv(BEATAML_FITS, sep='\t', low_memory=False)
    fits = fits[['dbgap_rnaseq_sample', 'inhibitor', 'auc']].dropna()
    fits['_sid'] = fits['dbgap_rnaseq_sample'].astype(str)
    print(f"  Loaded {len(fits)} (sample, drug, auc) rows, {fits['inhibitor'].nunique()} drugs")

    banner("Step 4: Filter drugs (≥10 sensitive AND ≥10 resistant)")
    drug_stats = []
    for drug, group in fits.groupby('inhibitor'):
        n_sens = int((group['auc'] < AUC_THRESHOLD).sum())
        n_res = int((group['auc'] >= AUC_THRESHOLD).sum())
        if n_sens >= MIN_SENSITIVE and n_res >= MIN_RESISTANT:
            drug_stats.append({'drug': drug, 'n_sensitive': n_sens, 'n_resistant': n_res, 'n_total': n_sens + n_res})
    drug_df = pd.DataFrame(drug_stats).sort_values('n_total', ascending=False)
    print(f"  Drugs passing filter: {len(drug_df)}")

    banner("Step 5: Sample alignment")
    common = set(axes['_sid']) & set(fits['_sid'])
    print(f"  KAALCURA samples: {len(axes)}, Drug samples: {fits['_sid'].nunique()}, Common: {len(common)}")
    axes = axes[axes['_sid'].isin(common)].set_index('_sid')

    banner("Step 6: Per-drug evaluation with LightGBM on 3 axes")
    import lightgbm as lgb
    from sklearn.model_selection import StratifiedKFold
    from sklearn.metrics import roc_auc_score

    results = []
    failed = []
    t_start = time.time()
    for i, row in enumerate(drug_df.itertuples(), 1):
        drug = row.drug
        drug_fits = fits[fits['inhibitor'] == drug]
        common_drug = drug_fits[drug_fits['_sid'].isin(axes.index)].drop_duplicates(subset=['_sid'], keep='first')
        if len(common_drug) < (MIN_SENSITIVE + MIN_RESISTANT):
            failed.append((drug, 'too_few', len(common_drug)))
            continue
        X = axes.loc[common_drug['_sid'], axis_cols].values
        y = (common_drug['auc'].values < AUC_THRESHOLD).astype(int)
        n_sens = int(y.sum()); n_res = int(len(y) - n_sens)
        if n_sens < MIN_SENSITIVE or n_res < MIN_RESISTANT:
            failed.append((drug, 'imbalanced', f'{n_sens}/{n_res}'))
            continue

        skf = StratifiedKFold(n_splits=N_CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
        fold_aurocs = []
        for train_idx, test_idx in skf.split(X, y):
            model = lgb.LGBMClassifier(
                n_estimators=100, learning_rate=0.1, num_leaves=31,
                random_state=RANDOM_STATE, n_jobs=-1, verbosity=-1,
            )
            model.fit(X[train_idx], y[train_idx])
            try:
                fold_aurocs.append(roc_auc_score(y[test_idx], model.predict_proba(X[test_idx])[:, 1]))
            except ValueError:
                fold_aurocs.append(float('nan'))
        fold_aurocs = np.array(fold_aurocs)
        if (~np.isnan(fold_aurocs)).sum() < 2:
            failed.append((drug, 'cv_failure', None))
            continue
        results.append({
            'drug': drug,
            'n_samples': len(y),
            'n_sensitive': n_sens,
            'n_resistant': n_res,
            'auroc_mean': float(np.nanmean(fold_aurocs)),
            'auroc_std': float(np.nanstd(fold_aurocs)),
            'auroc_min': float(np.nanmin(fold_aurocs)),
            'auroc_max': float(np.nanmax(fold_aurocs)),
        })
        if i % 30 == 0 or i == len(drug_df):
            elapsed = time.time() - t_start
            print(f"  [{i}/{len(drug_df)}] last='{drug}' AUROC={results[-1]['auroc_mean']:.3f} | elapsed={elapsed:.0f}s")

    print(f"\n  Evaluated: {len(results)}, Failed: {len(failed)}")

    banner("Step 7: Save")
    df = pd.DataFrame(results)
    df.sort_values('auroc_mean', ascending=False).to_csv(OUT_CSV, index=False)
    print(f"  CSV: {OUT_CSV}")

    banner("Step 8: Triangulation summary")
    aurocs = df['auroc_mean'].values
    summary = {
        'method': 'LightGBM defaults on 3 KAALCURA axes (R_prolif, R_emt, R_ddr)',
        'axis_source': str(axes_path),
        'n_drugs_evaluated': len(results),
        'auroc_mean': float(np.mean(aurocs)),
        'auroc_median': float(np.median(aurocs)),
        'auroc_std': float(np.std(aurocs)),
        'n_drugs_auroc_ge_0_55': int(np.sum(aurocs >= 0.55)),
        'n_drugs_auroc_ge_0_60': int(np.sum(aurocs >= 0.60)),
        'n_drugs_auroc_ge_0_65': int(np.sum(aurocs >= 0.65)),
        'min_sensitive': MIN_SENSITIVE,
        'min_resistant': MIN_RESISTANT,
        'comparators': {
            'kaalcura_3axis_logreg_mean_auroc': 0.526,
            'rna_baseline_v1_mean_auroc': 0.670,
            'rna_baseline_v2_mean_auroc': 'see rna_baseline_v2_auroc_summary.json',
        },
    }
    with open(OUT_SUMMARY, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n  Triangulation:")
    print(f"    Same features (3 axes), different model:")
    print(f"      LogisticRegression : 0.526 (Round 2.2b)")
    print(f"      LightGBM           : {summary['auroc_mean']:.3f} (this run)")
    print(f"")
    print(f"    Same model (LightGBM), different features:")
    print(f"      3 KAALCURA axes    : {summary['auroc_mean']:.3f} (this run)")
    print(f"      1000 RNA genes (v1, sex+20/20): 0.670")
    print(f"      1000 RNA genes (v2, no-sex+10/10): TBD")
    print(f"")
    print(f"    Diagnostic:")
    diff_model = summary['auroc_mean'] - 0.526
    if diff_model > 0.02:
        print(f"      Model effect: LightGBM lifts KAALCURA 3-axis by {diff_model:.3f} over LogReg")
    elif diff_model > -0.02:
        print(f"      Model effect: minimal — LightGBM ≈ LogReg on 3 axes (model is not the gap)")
    else:
        print(f"      Model effect: LightGBM WORSE than LogReg on 3 axes (overfitting on small features)")

    banner("DONE")


if __name__ == '__main__':
    main()
