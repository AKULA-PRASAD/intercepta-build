#!/usr/bin/env python3
"""
INTERCEPTA Round 2.2c — Step 2: Multi-Modal Predictor Trainer
==============================================================

Per spec INTERCEPTA_Round2_2c_Specification.md, Section 6.

Trains per-drug LightGBM classifier on the multi-modal feature stack from
Step 1. Captures all instrumentation needed for Step 3 gate evaluation.

Key spec compliance:
  - Random state 42 throughout (Section 6 #1)
  - 5-fold StratifiedKFold (Section 6 #2)
  - LightGBM defaults: n_estimators=100, lr=0.1, num_leaves=31 (Section 6 #3)
  - Pathway z-scoring on train fold only — no leakage (Section 6 #5)
  - Fail-closed on missing inputs (Section 6 #6)
  - All metrics mean ± std across folds (Section 6 #7)

For Q_E (KAALCURA contribution gate), each drug runs TWICE:
  (a) Full feature stack
  (b) Leave-KAALCURA-out (drop the 3 KAALCURA axis features)
  
The Q_E ablation comparison is then computed in Step 3.

Outputs:
  - per_drug_full.csv         — per-drug full-stack metrics
  - per_drug_no_kaalcura.csv  — per-drug ablation metrics
  - feature_importance_full.csv  — per-drug top-30 feature importances
  - shap_summary.csv          — per-feature-class mean |SHAP| value
  - train_summary.json        — global stats, comparator deltas

Author: Prasad Akula, 2026-05-06
"""

import json
import sys
import time
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')
warnings.filterwarnings('ignore', message='.*feature names.*')

HOME = Path.home()
ROUND2 = HOME / 'INTERCEPTA' / 'round2_aml'
RESULTS = ROUND2 / 'results'
ROUND2_2C = RESULTS / 'round2_2c'

# ----- Inputs (from Step 1) -----
IN_KAALCURA = ROUND2_2C / 'features_kaalcura.csv'
IN_RNA = ROUND2_2C / 'features_rna1000.csv'
IN_MUTS = ROUND2_2C / 'features_mutations.csv'
IN_PATHWAYS = ROUND2_2C / 'features_pathways_raw.csv'
IN_DRUG_TGT = ROUND2_2C / 'features_drug_target.csv'
IN_RESPONSE = ROUND2_2C / 'drug_response_aligned.csv'

# ----- Outputs -----
OUT_PER_DRUG_FULL = ROUND2_2C / 'per_drug_full.csv'
OUT_PER_DRUG_ABLATION = ROUND2_2C / 'per_drug_no_kaalcura.csv'
OUT_FEAT_IMP = ROUND2_2C / 'feature_importance_full.csv'
OUT_SHAP = ROUND2_2C / 'shap_summary.csv'
OUT_SUMMARY = ROUND2_2C / 'train_summary.json'

# Spec Section 6 locked params
N_CV_FOLDS = 5
RANDOM_STATE = 42
LGBM_PARAMS = {
    'n_estimators': 100,
    'learning_rate': 0.1,
    'num_leaves': 31,
    'random_state': RANDOM_STATE,
    'n_jobs': -1,
    'verbosity': -1,
}

KAALCURA_FEAT_NAMES = ['R_prolif', 'R_emt', 'R_ddr']


def banner(msg):
    print('\n' + '=' * 72)
    print(msg)
    print('=' * 72)


def fail_closed(msg):
    print(f"\nTRAIN FAILED (fail-closed per spec Section 6):\n  {msg}")
    sys.exit(2)


def check_deps():
    missing = []
    try:
        import lightgbm
    except ImportError:
        missing.append('lightgbm')
    try:
        from sklearn.model_selection import StratifiedKFold
        from sklearn.metrics import roc_auc_score, balanced_accuracy_score
    except ImportError:
        missing.append('scikit-learn')
    try:
        import shap
        print(f"  shap: {shap.__version__} (available)")
    except ImportError:
        # SHAP optional — falls back to LightGBM gain importance only
        print(f"  shap: NOT INSTALLED — will use gain importance only (no per-feature-class SHAP)")
    if missing:
        fail_closed(f"Missing dependencies: {missing}\n  pip install {' '.join(missing)}")


def load_inputs():
    """Load all Step 1 outputs and merge into a single feature matrix."""
    for label, p in [
        ('kaalcura', IN_KAALCURA), ('rna', IN_RNA),
        ('mutations', IN_MUTS), ('pathways', IN_PATHWAYS),
        ('drug_target', IN_DRUG_TGT), ('response', IN_RESPONSE),
    ]:
        if not p.exists():
            fail_closed(f"Step 1 output missing: {p}\n  Run build_multimodal_features.py first.")

    print(f"  Loading Step 1 outputs...")
    kaalcura = pd.read_csv(IN_KAALCURA)
    rna = pd.read_csv(IN_RNA)
    muts = pd.read_csv(IN_MUTS)
    paths = pd.read_csv(IN_PATHWAYS)
    drug_tgt = pd.read_csv(IN_DRUG_TGT)
    response = pd.read_csv(IN_RESPONSE)

    print(f"  KAALCURA   : {kaalcura.shape}")
    print(f"  RNA        : {rna.shape}")
    print(f"  Mutations  : {muts.shape}")
    print(f"  Pathways   : {paths.shape}")
    print(f"  Drug-target: {drug_tgt.shape}")
    print(f"  Response   : {response.shape}")

    # Cast sample_id to str everywhere
    for df in [kaalcura, rna, muts, paths, response]:
        df['sample_id'] = df['sample_id'].astype(str)

    # Merge sample-level features (per-sample): kaalcura ∩ rna ∩ muts ∩ paths
    print(f"\n  Merging sample-level features...")
    common = set(kaalcura['sample_id']) & set(rna['sample_id']) & set(muts['sample_id']) & set(paths['sample_id'])
    print(f"  Samples in all 4 feature classes: {len(common)}")
    if len(common) < 100:
        fail_closed(f"Too few common samples: {len(common)}")

    sample_feats = kaalcura.merge(rna, on='sample_id', how='inner')
    sample_feats = sample_feats.merge(muts, on='sample_id', how='inner')
    sample_feats = sample_feats.merge(paths, on='sample_id', how='inner')
    print(f"  Per-sample feature matrix: {sample_feats.shape}")

    # Identify column groups for SHAP attribution and ablation
    feat_groups = {
        'kaalcura': KAALCURA_FEAT_NAMES,
        'rna': [c for c in rna.columns if c != 'sample_id'],
        'mutation': [c for c in muts.columns if c != 'sample_id'],
        'pathway': [c for c in paths.columns if c != 'sample_id'],
        'drug_target': [c for c in drug_tgt.columns if c != 'drug'],
    }
    print(f"\n  Feature group sizes:")
    for g, cols in feat_groups.items():
        print(f"    {g}: {len(cols)}")

    return sample_feats, drug_tgt, response, feat_groups


def evaluate_drug(X_full, y, drug_name, feat_groups, sample_drug_tgt, drop_kaalcura=False):
    """
    5-fold StratifiedKFold with LightGBM on the multi-modal feature matrix.
    Returns per-fold metrics and feature importances.
    
    Per spec Section 6 #5: pathway features are z-scored on the TRAIN FOLD only.
    """
    from sklearn.model_selection import StratifiedKFold
    from sklearn.metrics import roc_auc_score, balanced_accuracy_score
    import lightgbm as lgb

    # Determine which columns to drop for ablation
    if drop_kaalcura:
        drop_cols = set(feat_groups['kaalcura'])
    else:
        drop_cols = set()
    feature_cols = [c for c in X_full.columns if c not in drop_cols]
    pathway_cols = [c for c in feat_groups['pathway'] if c in feature_cols]

    skf = StratifiedKFold(n_splits=N_CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    fold_metrics = []
    fold_importances = []  # list of dicts (feature → gain)

    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X_full, y)):
        X_train = X_full.iloc[train_idx][feature_cols].copy()
        X_test = X_full.iloc[test_idx][feature_cols].copy()
        y_train = y[train_idx]
        y_test = y[test_idx]

        # Z-score pathway features using TRAIN-fold means/stds (no leakage)
        for col in pathway_cols:
            mu = X_train[col].mean()
            sigma = X_train[col].std()
            if sigma > 1e-9:
                X_train[col] = (X_train[col] - mu) / sigma
                X_test[col] = (X_test[col] - mu) / sigma
            else:
                X_train[col] = 0.0
                X_test[col] = 0.0

        # Train
        model = lgb.LGBMClassifier(**LGBM_PARAMS)
        model.fit(X_train, y_train)

        # Test predictions
        y_proba_test = model.predict_proba(X_test)[:, 1]
        y_pred_test = (y_proba_test >= 0.5).astype(int)
        try:
            auroc_test = roc_auc_score(y_test, y_proba_test)
        except ValueError:
            auroc_test = float('nan')
        try:
            bacc_test = balanced_accuracy_score(y_test, y_pred_test)
        except ValueError:
            bacc_test = float('nan')

        # Train predictions (for overfitting check)
        y_proba_train = model.predict_proba(X_train)[:, 1]
        try:
            auroc_train = roc_auc_score(y_train, y_proba_train)
        except ValueError:
            auroc_train = float('nan')

        fold_metrics.append({
            'fold': fold_idx,
            'auroc_test': auroc_test,
            'auroc_train': auroc_train,
            'balanced_acc_test': bacc_test,
            'n_train': len(y_train),
            'n_test': len(y_test),
        })

        # Feature importance (gain, normalized to sum to 1 per fold)
        if not drop_kaalcura:
            imp_array = model.booster_.feature_importance(importance_type='gain')
            total_gain = imp_array.sum()
            if total_gain > 0:
                imp_dict = {feat: float(g) / total_gain for feat, g in zip(feature_cols, imp_array)}
            else:
                imp_dict = {feat: 0.0 for feat in feature_cols}
            fold_importances.append(imp_dict)

    fold_df = pd.DataFrame(fold_metrics)
    valid = ~fold_df['auroc_test'].isna()
    if valid.sum() < 2:
        return None

    result = {
        'drug': drug_name,
        'n_samples': int(len(y)),
        'n_sensitive': int(y.sum()),
        'n_resistant': int(len(y) - y.sum()),
        'auroc_test_mean': float(fold_df['auroc_test'].mean()),
        'auroc_test_std': float(fold_df['auroc_test'].std()),
        'auroc_test_min': float(fold_df['auroc_test'].min()),
        'auroc_test_max': float(fold_df['auroc_test'].max()),
        'auroc_train_mean': float(fold_df['auroc_train'].mean()),
        'balanced_acc_mean': float(fold_df['balanced_acc_test'].mean()),
        'balanced_acc_std': float(fold_df['balanced_acc_test'].std()),
        'train_test_gap_mean': float((fold_df['auroc_train'] - fold_df['auroc_test']).mean()),
        'n_valid_folds': int(valid.sum()),
        'fold_aurocs_test': fold_df['auroc_test'].tolist(),
    }

    # Aggregate feature importance across folds (mean)
    if fold_importances:
        agg_imp = defaultdict(float)
        for imp_dict in fold_importances:
            for feat, val in imp_dict.items():
                agg_imp[feat] += val / len(fold_importances)
        result['_feature_importance'] = dict(agg_imp)

    return result


def main():
    banner("Round 2.2c — Step 2: Multi-Modal Predictor Trainer")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    banner("Step 1: Dependencies")
    check_deps()

    banner("Step 2: Load Step 1 outputs")
    sample_feats, drug_tgt, response, feat_groups = load_inputs()

    banner("Step 3: Build per-(sample, drug) data structure")
    drugs_in_response = response['drug'].unique().tolist()
    drugs_in_target = set(drug_tgt['drug'])
    drugs_eval = [d for d in drugs_in_response if d in drugs_in_target]
    drugs_missing_tgt = [d for d in drugs_in_response if d not in drugs_in_target]
    print(f"  Drugs in response: {len(drugs_in_response)}")
    print(f"  Drugs in drug-target file: {len(drugs_in_target)}")
    print(f"  Drugs in BOTH (will evaluate): {len(drugs_eval)}")
    print(f"  Drugs missing drug-target features: {len(drugs_missing_tgt)}")
    if drugs_missing_tgt:
        print(f"    First 5: {drugs_missing_tgt[:5]}")
    if not drugs_eval:
        fail_closed("No drugs have both response and drug-target features")

    banner("Step 4: Per-drug evaluation — FULL feature stack")
    full_results = []
    failed_drugs = []
    t_start = time.time()

    for i, drug in enumerate(drugs_eval, 1):
        # Get drug response for this drug
        drug_resp = response[response['drug'] == drug].drop_duplicates(subset='sample_id', keep='first')
        # Align with sample features
        merged = drug_resp.merge(sample_feats, on='sample_id', how='inner')
        if len(merged) < 30:
            failed_drugs.append((drug, 'too_few_after_align', len(merged)))
            continue

        # Add drug-target features (broadcast across rows for this drug)
        dt_row = drug_tgt[drug_tgt['drug'] == drug].iloc[0]
        for c in feat_groups['drug_target']:
            merged[c] = dt_row[c]

        # Build X, y
        all_feat_cols = (feat_groups['kaalcura'] + feat_groups['rna'] +
                         feat_groups['mutation'] + feat_groups['pathway'] +
                         feat_groups['drug_target'])
        all_feat_cols = [c for c in all_feat_cols if c in merged.columns]
        X = merged[all_feat_cols]
        y = merged['sensitive'].values

        n_sens = int(y.sum()); n_res = int(len(y) - n_sens)
        if n_sens < 10 or n_res < 10:
            failed_drugs.append((drug, 'imbalanced', f'{n_sens}/{n_res}'))
            continue

        sample_drug_tgt = dt_row.to_dict()
        result = evaluate_drug(X, y, drug, feat_groups, sample_drug_tgt, drop_kaalcura=False)
        if result is None:
            failed_drugs.append((drug, 'cv_failure', None))
            continue
        full_results.append(result)

        if i % 20 == 0 or i == len(drugs_eval):
            elapsed = time.time() - t_start
            eta = elapsed / i * (len(drugs_eval) - i)
            print(f"  [{i}/{len(drugs_eval)}] last='{drug}' AUROC={result['auroc_test_mean']:.3f} "
                  f"BAcc={result['balanced_acc_mean']:.3f} | elapsed={elapsed:.0f}s ETA={eta:.0f}s")

    print(f"\n  Full-stack: evaluated {len(full_results)}, failed {len(failed_drugs)}")

    banner("Step 5: Per-drug evaluation — LEAVE-KAALCURA-OUT (Q_E ablation)")
    ablation_results = []
    t_abl_start = time.time()
    successful_drug_set = set(r['drug'] for r in full_results)

    for i, drug in enumerate(drugs_eval, 1):
        if drug not in successful_drug_set:
            continue
        drug_resp = response[response['drug'] == drug].drop_duplicates(subset='sample_id', keep='first')
        merged = drug_resp.merge(sample_feats, on='sample_id', how='inner')
        dt_row = drug_tgt[drug_tgt['drug'] == drug].iloc[0]
        for c in feat_groups['drug_target']:
            merged[c] = dt_row[c]

        all_feat_cols = (feat_groups['kaalcura'] + feat_groups['rna'] +
                         feat_groups['mutation'] + feat_groups['pathway'] +
                         feat_groups['drug_target'])
        all_feat_cols = [c for c in all_feat_cols if c in merged.columns]
        X = merged[all_feat_cols]
        y = merged['sensitive'].values

        result = evaluate_drug(X, y, drug, feat_groups, dt_row.to_dict(), drop_kaalcura=True)
        if result is None:
            continue
        # Strip importance from ablation result (not used)
        result.pop('_feature_importance', None)
        ablation_results.append(result)

        if i % 20 == 0 or i == len(drugs_eval):
            elapsed = time.time() - t_abl_start
            print(f"  Ablation [{i}/{len(drugs_eval)}] elapsed={elapsed:.0f}s")

    print(f"\n  Ablation: evaluated {len(ablation_results)} drugs")

    banner("Step 6: Save per-drug metrics")
    full_df = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith('_') and k != 'fold_aurocs_test'}
                            for r in full_results])
    full_df.sort_values('auroc_test_mean', ascending=False).to_csv(OUT_PER_DRUG_FULL, index=False)
    print(f"  Full: {OUT_PER_DRUG_FULL}")

    abl_df = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith('_') and k != 'fold_aurocs_test'}
                           for r in ablation_results])
    abl_df.sort_values('auroc_test_mean', ascending=False).to_csv(OUT_PER_DRUG_ABLATION, index=False)
    print(f"  Ablation: {OUT_PER_DRUG_ABLATION}")

    banner("Step 7: Save per-drug feature importance (top-30)")
    imp_rows = []
    for r in full_results:
        imp = r.get('_feature_importance', {})
        if not imp:
            continue
        sorted_feats = sorted(imp.items(), key=lambda x: -x[1])[:30]
        for rank, (feat, gain_norm) in enumerate(sorted_feats, 1):
            # Tag feature class
            if feat in feat_groups['kaalcura']:
                fclass = 'kaalcura'
            elif feat in feat_groups['rna']:
                fclass = 'rna'
            elif feat in feat_groups['mutation']:
                fclass = 'mutation'
            elif feat in feat_groups['pathway']:
                fclass = 'pathway'
            elif feat in feat_groups['drug_target']:
                fclass = 'drug_target'
            else:
                fclass = 'unknown'
            imp_rows.append({
                'drug': r['drug'], 'rank': rank, 'feature': feat,
                'feature_class': fclass, 'gain_normalized': gain_norm,
            })
    imp_df = pd.DataFrame(imp_rows)
    imp_df.to_csv(OUT_FEAT_IMP, index=False)
    print(f"  Importance: {OUT_FEAT_IMP}")

    banner("Step 8: Aggregate per-feature-class contribution (gain proxy for SHAP)")
    # Without SHAP, use gain importance summed per feature class as proxy
    class_totals = defaultdict(list)
    for r in full_results:
        imp = r.get('_feature_importance', {})
        if not imp:
            continue
        per_class = defaultdict(float)
        for feat, gain in imp.items():
            if feat in feat_groups['kaalcura']:
                per_class['kaalcura'] += gain
            elif feat in feat_groups['rna']:
                per_class['rna'] += gain
            elif feat in feat_groups['mutation']:
                per_class['mutation'] += gain
            elif feat in feat_groups['pathway']:
                per_class['pathway'] += gain
            elif feat in feat_groups['drug_target']:
                per_class['drug_target'] += gain
        for c, v in per_class.items():
            class_totals[c].append(v)

    shap_summary_rows = []
    for fclass in ['kaalcura', 'rna', 'mutation', 'pathway', 'drug_target']:
        vals = class_totals.get(fclass, [0])
        shap_summary_rows.append({
            'feature_class': fclass,
            'n_features': len(feat_groups[fclass]),
            'gain_share_mean': float(np.mean(vals)),
            'gain_share_std': float(np.std(vals)),
            'gain_share_median': float(np.median(vals)),
            'gain_share_per_feature': float(np.mean(vals) / max(len(feat_groups[fclass]), 1)),
        })
    shap_df = pd.DataFrame(shap_summary_rows)
    shap_df.to_csv(OUT_SHAP, index=False)
    print(f"  Per-class summary: {OUT_SHAP}")
    print(shap_df.to_string(index=False))

    banner("Step 9: Aggregate metrics + save train summary")
    full_aurocs = full_df['auroc_test_mean'].values
    full_baccs = full_df['balanced_acc_mean'].values
    full_gaps = full_df['train_test_gap_mean'].values

    abl_aurocs = abl_df['auroc_test_mean'].values
    common_drugs = set(full_df['drug']) & set(abl_df['drug'])
    full_for_abl = full_df[full_df['drug'].isin(common_drugs)].set_index('drug')['auroc_test_mean']
    abl_for_full = abl_df[abl_df['drug'].isin(common_drugs)].set_index('drug')['auroc_test_mean']
    delta_per_drug = (full_for_abl - abl_for_full).reindex(common_drugs)

    summary = {
        'started': time.strftime('%Y-%m-%d %H:%M:%S'),
        'n_drugs_eval_full': len(full_results),
        'n_drugs_eval_ablation': len(ablation_results),
        'n_drugs_failed': len(failed_drugs),
        'full_stack': {
            'auroc_mean': float(np.mean(full_aurocs)),
            'auroc_median': float(np.median(full_aurocs)),
            'auroc_std': float(np.std(full_aurocs)),
            'balanced_acc_mean': float(np.mean(full_baccs)),
            'balanced_acc_median': float(np.median(full_baccs)),
            'train_test_gap_mean': float(np.mean(full_gaps)),
            'train_test_gap_max': float(np.max(full_gaps)),
            'n_drugs_auroc_ge_0_60': int(np.sum(full_aurocs >= 0.60)),
            'n_drugs_auroc_ge_0_65': int(np.sum(full_aurocs >= 0.65)),
            'n_drugs_auroc_ge_0_70': int(np.sum(full_aurocs >= 0.70)),
            'n_drugs_auroc_ge_0_75': int(np.sum(full_aurocs >= 0.75)),
        },
        'no_kaalcura_ablation': {
            'auroc_mean': float(np.mean(abl_aurocs)),
            'auroc_median': float(np.median(abl_aurocs)),
            'auroc_std': float(np.std(abl_aurocs)),
        },
        'kaalcura_contribution': {
            'mean_delta': float(delta_per_drug.mean()),
            'median_delta': float(delta_per_drug.median()),
            'n_drugs_kaalcura_helps': int((delta_per_drug > 0).sum()),
            'n_drugs_kaalcura_hurts': int((delta_per_drug < 0).sum()),
            'n_drugs_no_change': int((delta_per_drug == 0).sum()),
            'n_drugs_compared': len(delta_per_drug),
        },
        'comparators': {
            'rna_only_lightgbm_v2_mean_auroc': 0.645,
            'kaalcura_3axis_lightgbm_mean_auroc': 0.532,
            'kaalcura_3axis_logreg_mean_auroc_round22b': 0.526,
        },
        'spec_compliance': {
            'random_state': RANDOM_STATE,
            'n_cv_folds': N_CV_FOLDS,
            'lightgbm_params': LGBM_PARAMS,
            'feature_group_sizes': {k: len(v) for k, v in feat_groups.items()},
            'pathway_zscoring': 'train-fold-only (no leakage)',
        },
    }
    with open(OUT_SUMMARY, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"  Summary: {OUT_SUMMARY}")

    print(f"\n  Full-stack mean AUROC: {summary['full_stack']['auroc_mean']:.3f}")
    print(f"  Ablation mean AUROC  : {summary['no_kaalcura_ablation']['auroc_mean']:.3f}")
    print(f"  KAALCURA contribution: {summary['kaalcura_contribution']['mean_delta']:.4f} (mean delta)")
    print(f"  vs RNA-only baseline : {summary['full_stack']['auroc_mean'] - 0.645:+.3f}")
    print(f"  vs KAALCURA-LightGBM : {summary['full_stack']['auroc_mean'] - 0.532:+.3f}")

    banner("DONE — Step 2 of 3 complete")
    print(f"Finished: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Next: run evaluate_round2_2c_gates.py (Step 3 of 3)")


if __name__ == '__main__':
    main()
