#!/usr/bin/env python3
"""
INTERCEPTA Round 2.2b — Corrections Round
==========================================

Implementation of spec at
  round2_aml/docs/INTERCEPTA_Round2_2b_Specification.md
committed as 1333a9d.

Three corrections from Round 2.2a closure:
  - Q_A: comparator fixed (Prog-like, not Mono-like) per Van Galen 2019
    primary-source biology verification.
  - Q_B: R_ddr residualized on R_prolif (Peterson 2019 Cancers method).
    β, α fit on BeatAML, same β, α applied to Van Galen for cross-
    modality commensurability.
  - Q_C: threshold held at 0.55 (not relaxed). If this round also lands
    near 0.53, that's three consecutive rounds documenting a real
    3-axis-plateau finding — earned, not assumed.

Scope tight: corrections only. Therapeutic index deferred to 2.2c.

Environment: intercepta-scrna conda env
Round 1 KAALCURA imported unchanged (Principle 16).

Run:
    conda activate intercepta-scrna
    cd ~/INTERCEPTA/round2_aml/code
    python3 build_aml_net_round22b_residual.py 2>&1 | tee \\
        ../results/aml_net_round22b_build.txt

Author: Prasad Akula
Date:    April 22, 2026
Spec:    commit 1333a9d
"""
import os
import sys
import json
import pickle
import time
import logging
from pathlib import Path


HOME = Path.home()
CODE_ROOT = HOME / 'INTERCEPTA' / 'code'
ROUND2_ROOT = HOME / 'INTERCEPTA' / 'round2_aml'
DATA_ROOT = ROUND2_ROOT / 'data'
RESULTS_DIR = ROUND2_ROOT / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(CODE_ROOT))

SKELETON_PATH = RESULTS_DIR / 'aml_net_skeleton_v2.gpickle'
ANNDATA_PATH = DATA_ROOT / 'vangalen2019' / 'vangalen_aml.h5ad'
BEATAML_ROOT = DATA_ROOT / 'beataml2.0_data-2.0'
BEATAML_EXPR = BEATAML_ROOT / 'beataml_waves1to4_norm_exp_dbgap.txt'
BEATAML_FITS = BEATAML_ROOT / 'beataml_probit_curve_fits_v4_dbgap.txt'
BEATAML_CLIN = BEATAML_ROOT / 'beataml_wv1to4_clinical.xlsx'

# Output paths (spec section 8)
OUT_NET_PATH = RESULTS_DIR / 'aml_net_round22b_ucell_residual.gpickle'
OUT_SUMMARY = RESULTS_DIR / 'aml_net_round22b_summary.json'
OUT_KAALCURA_STATE = RESULTS_DIR / 'kaalcura_ucell_residual_state_round22b.pkl'
OUT_BEATAML_AXES = RESULTS_DIR / 'beataml_ucell_residual_axes_round22b.csv'
OUT_VANGALEN_AXES = RESULTS_DIR / 'vangalen_ucell_residual_axes_round22b.csv'
OUT_RESIDUAL_COEFS = RESULTS_DIR / 'residualization_coefficients_round22b.json'

# Locked by spec 1333a9d
MAX_RANK = 17663
MIN_CV_AUROC_PASS = 0.55
AXIS_REDUNDANCY_MAX_ABS_R = 0.9
PER_AXIS_MIN_AUROC_THRESHOLD = 0.60
JACCARD_MAX = 0.6

# Verified column structure (from prior rounds)
BEATAML_METADATA_COLS = {'stable_id', 'display_label', 'description', 'biotype'}
BEATAML_GENE_SYMBOL_COL = 'display_label'
BEATAML_CURVE_SAMPLE_COL = 'dbgap_rnaseq_sample'
BEATAML_CLIN_SAMPLE_COL = 'dbgap_rnaseq_sample'
BEATAML_CLIN_SHEET = 'summary'
BEATAML_CLIN_FLT3_COL = 'FLT3-ITD'
BEATAML_CLIN_FLT3_POS = 'positive'
BEATAML_CLIN_FLT3_NEG = 'negative'

# Gene sets — Round 1 verbatim, unchanged (Principle 16)
SIGNATURES = {
    'prolif': [
        'MKI67', 'TOP2A', 'PCNA', 'CDK1', 'CCNB1', 'AURKA', 'BUB1',
        'PLK1', 'MCM2', 'MCM6', 'FOXM1', 'BIRC5', 'NUSAP1', 'TPX2',
        'CDC20', 'CENPF', 'KIF11', 'PRC1', 'HMGA1', 'MYBL2',
    ],
    'emt': [
        'VIM', 'CDH2', 'SNAI1', 'SNAI2', 'ZEB1', 'ZEB2', 'TWIST1',
        'FN1', 'MMP2', 'MMP9',
        'CDH1-', 'CLDN1-', 'TJP1-',
    ],
    'ddr': [
        'BRCA1', 'BRCA2', 'RAD51', 'ATM', 'ATR', 'CHEK1', 'CHEK2',
        'PARP1', 'PARP2', 'XRCC1', 'MLH1', 'MSH2', 'FANCA', 'FANCD2',
        'RPA1',
    ],
}


def banner(s):
    print('\n' + '=' * 72)
    print(s)
    print('=' * 72)


def main():
    banner("Step 0: Dependencies and Round 1 KAALCURA import")
    try:
        import numpy as np
        import pandas as pd
        import networkx as nx
        import anndata as ad
        import scipy.sparse as sp
        import scipy as _scipy
        from scipy import stats
        import pyucell as uc
        print(f"  numpy    : {np.__version__}")
        print(f"  pandas   : {pd.__version__}")
        print(f"  scipy    : {_scipy.__version__}")
        print(f"  networkx : {nx.__version__}")
        print(f"  anndata  : {ad.__version__}")
        print(f"  pyucell  : {uc.__version__}")
    except ImportError as e:
        sys.exit(f"MISSING: {e}")

    import numpy as np
    import pandas as pd
    import networkx as nx
    import anndata as ad
    import scipy.sparse as sp
    from scipy import stats
    import pyucell as uc

    try:
        from intercepta_kaalcura_v1 import KAALCURA
        print(f"  KAALCURA imported (for drug training only)")
    except ImportError as e:
        sys.exit(f"Cannot import Round 1 KAALCURA: {e}")

    logging.basicConfig(level=logging.INFO, format='  [KAALCURA] %(message)s')

    # ---------------------------------------------------------
    banner("Step 0.5: Verify input files exist")
    required = {
        'Round 2.1b skeleton': SKELETON_PATH,
        'Round 2.1c AnnData': ANNDATA_PATH,
        'BeatAML expression': BEATAML_EXPR,
        'BeatAML curve fits': BEATAML_FITS,
        'BeatAML clinical': BEATAML_CLIN,
    }
    for label, path in required.items():
        if not path.exists():
            sys.exit(f"MISSING: {label}: {path}")
        size_mb = path.stat().st_size / (1024 * 1024)
        print(f"  [OK] {label:25s} {size_mb:>8.1f} MB")

    # ---------------------------------------------------------
    banner("Step 1: Load BeatAML RNA-seq and compute UCell axes")
    print("  Loading BeatAML normalized expression...")
    t0 = time.time()
    beataml_expr_raw = pd.read_csv(BEATAML_EXPR, sep='\t', low_memory=False)
    print(f"    Raw shape: {beataml_expr_raw.shape}  ({time.time()-t0:.1f}s)")

    missing_metadata = BEATAML_METADATA_COLS - set(beataml_expr_raw.columns)
    if missing_metadata:
        sys.exit(f"FATAL: expected metadata columns missing: {missing_metadata}")

    sample_cols = [c for c in beataml_expr_raw.columns
                   if c not in BEATAML_METADATA_COLS]
    print(f"    Sample columns: {len(sample_cols)}")

    beataml_expr_raw[BEATAML_GENE_SYMBOL_COL] = (
        beataml_expr_raw[BEATAML_GENE_SYMBOL_COL].astype(str).str.strip().str.upper()
    )
    beataml_expr_raw = beataml_expr_raw[
        (beataml_expr_raw[BEATAML_GENE_SYMBOL_COL].notna())
        & (beataml_expr_raw[BEATAML_GENE_SYMBOL_COL] != '')
        & (beataml_expr_raw[BEATAML_GENE_SYMBOL_COL] != 'NAN')
    ]
    beataml_wide = beataml_expr_raw.groupby(BEATAML_GENE_SYMBOL_COL)[sample_cols].max()
    beataml_df = beataml_wide.T
    beataml_df.index = beataml_df.index.astype(str)
    print(f"    Matrix after dedupe/transpose: {beataml_df.shape}")

    print("  Wrapping BeatAML as AnnData for pyUCell...")
    beataml_adata = ad.AnnData(
        X=beataml_df.values,
        obs=pd.DataFrame(index=beataml_df.index),
        var=pd.DataFrame(index=beataml_df.columns),
    )
    print(f"    BeatAML AnnData: {beataml_adata.n_obs} samples x "
          f"{beataml_adata.n_vars} genes")

    print(f"  Running pyUCell on BeatAML (max_rank={MAX_RANK}, n_jobs=1)...")
    t0 = time.time()
    uc.compute_ucell_scores(
        beataml_adata,
        signatures=SIGNATURES,
        max_rank=MAX_RANK,
        missing_genes='impute',
        suffix='_UCell',
        n_jobs=1,  # avoids joblib loky read-only bug (pyucell 0.6.0)
    )
    print(f"    pyUCell computed in {time.time()-t0:.1f}s")

    beataml_axes_raw = pd.DataFrame({
        'R_prolif': beataml_adata.obs['prolif_UCell'],
        'R_emt':    beataml_adata.obs['emt_UCell'],
        'R_ddr':    beataml_adata.obs['ddr_UCell'],
    }, index=beataml_adata.obs.index)
    print(f"\n  BeatAML RAW axes summary:")
    print(beataml_axes_raw.describe().round(3).to_string())

    # ---------------------------------------------------------
    banner("Step 2: Fit residualization on BeatAML, compute R_ddr_residual")
    print("  Fitting: R_ddr = alpha + beta * R_prolif + epsilon  (on BeatAML)")
    regr = stats.linregress(
        beataml_axes_raw['R_prolif'].values,
        beataml_axes_raw['R_ddr'].values,
    )
    beta = float(regr.slope)
    alpha = float(regr.intercept)
    r_value = float(regr.rvalue)
    p_value = float(regr.pvalue)
    print(f"    alpha:          {alpha:.6f}")
    print(f"    beta:           {beta:.6f}")
    print(f"    regression r:   {r_value:.4f}")
    print(f"    regression r^2: {r_value**2:.4f}")
    print(f"    p-value:        {p_value:.3e}")
    print(f"    Interpretation: BeatAML R_prolif explains {r_value**2*100:.1f}% "
          f"of R_ddr variance; {(1-r_value**2)*100:.1f}% remains as residual biology.")

    # Compute residuals for BeatAML
    beataml_axes = pd.DataFrame({
        'R_prolif': beataml_axes_raw['R_prolif'],
        'R_emt':    beataml_axes_raw['R_emt'],
        'R_ddr':    beataml_axes_raw['R_ddr'] - (alpha + beta * beataml_axes_raw['R_prolif']),
    }, index=beataml_axes_raw.index)
    print(f"\n  BeatAML FINAL axes (R_ddr is now residual):")
    print(beataml_axes.describe().round(4).to_string())

    # Sanity check: residualized R_ddr should have ~0 correlation with R_prolif on BeatAML
    check_corr = beataml_axes[['R_prolif', 'R_ddr']].corr().iloc[0, 1]
    print(f"\n  Sanity check: corr(R_prolif, R_ddr_residual) on BeatAML = {check_corr:.6f}")
    print(f"  (Should be essentially zero by construction.)")

    beataml_axes.to_csv(OUT_BEATAML_AXES)
    print(f"  Saved: {OUT_BEATAML_AXES}")

    beataml_axis_corr = beataml_axes.corr()
    print(f"\n  BeatAML pairwise correlations (after residualization):")
    print(beataml_axis_corr.round(3).to_string())

    # Save residualization coefficients for audit
    residual_coefs = {
        'method': 'linear regression R_ddr ~ alpha + beta * R_prolif, fit on BeatAML',
        'reference': 'Peterson & Kovyrshina 2019 Cancers 11:501 (PCNA metagene residualization)',
        'fit_cohort': 'BeatAML (n=707 samples)',
        'alpha': alpha,
        'beta': beta,
        'regression_r': r_value,
        'regression_r_squared': r_value**2,
        'regression_p_value': p_value,
        'sanity_check_corr_after_residualization_on_beataml': float(check_corr),
    }
    with open(OUT_RESIDUAL_COEFS, 'w') as f:
        json.dump(residual_coefs, f, indent=2)
    print(f"  Saved coefficients: {OUT_RESIDUAL_COEFS}")

    # ---------------------------------------------------------
    banner("Step 3: Train drug models on BeatAML (R_prolif, R_emt, R_ddr_residual)")
    print("  Loading BeatAML curve fits...")
    t0 = time.time()
    fits = pd.read_csv(BEATAML_FITS, sep='\t', low_memory=False)
    print(f"    Raw rows: {len(fits):,}  ({time.time()-t0:.1f}s)")

    if BEATAML_CURVE_SAMPLE_COL not in fits.columns:
        sys.exit(f"FATAL: curve_fits missing {BEATAML_CURVE_SAMPLE_COL}")

    fits_ok = fits[fits['paper_inclusion'] & fits['converged'] &
                   (fits['curve_type'] == 'decreasing') & (~fits['all_gt_50']) &
                   (fits['type'] == 'single-agent')].copy()
    print(f"    After QC filters: {len(fits_ok):,}")
    fits_ok['_sid'] = fits_ok[BEATAML_CURVE_SAMPLE_COL].astype(str)
    overlap = set(fits_ok['_sid']) & set(beataml_axes.index)
    print(f"    Sample overlap: {len(overlap)}")
    if len(overlap) < 50:
        sys.exit(f"FATAL: Only {len(overlap)} overlap; cannot train")

    fits_ok_joined = fits_ok[fits_ok['_sid'].isin(overlap)]
    drug_matrix = fits_ok_joined.pivot_table(
        index='_sid', columns='inhibitor', values='auc', aggfunc='median'
    )
    print(f"    Drug sensitivity matrix: {drug_matrix.shape}")

    axes_overlap = beataml_axes.loc[list(overlap & set(beataml_axes.index))]
    drug_matrix_overlap = drug_matrix.loc[
        list(set(axes_overlap.index) & set(drug_matrix.index))
    ]
    axes_final = axes_overlap.loc[drug_matrix_overlap.index]
    print(f"    Training set: {axes_final.shape[0]} samples, "
          f"{drug_matrix_overlap.shape[1]} drugs")
    print(f"    NOTE: R_ddr column passed to KAALCURA = residualized DDR "
          f"(the column rename is a Principle 16 artifact — KAALCURA v1 "
          f"unchanged, but axis semantic changed).")

    print("  Training drug models via Round 1 KAALCURA.train_drug_models...")
    kaalcura = KAALCURA(random_state=42)
    kaalcura.fit_reference(beataml_df, tissue_labels=None)

    t0 = time.time()
    drug_models = kaalcura.train_drug_models(
        axes_final, drug_matrix_overlap,
        ic50_threshold='median', n_cv_folds=5
    )
    print(f"  Trained {len(drug_models)} models in {time.time()-t0:.1f}s")

    auroc_values = [info['auroc'] for info in drug_models.values()]
    mean_auroc = float(np.mean(auroc_values)) if auroc_values else 0.0
    median_auroc = float(np.median(auroc_values)) if auroc_values else 0.0
    n_auroc_above_60 = sum(1 for a in auroc_values if a >= PER_AXIS_MIN_AUROC_THRESHOLD)
    print(f"\n  Mean CV-AUROC:   {mean_auroc:.4f}")
    print(f"  Median CV-AUROC: {median_auroc:.4f}")
    print(f"  Drugs with AUROC >= {PER_AXIS_MIN_AUROC_THRESHOLD}: "
          f"{n_auroc_above_60}/{len(auroc_values)}")

    per_axis_max_coef = {'R_prolif': 0.0, 'R_emt': 0.0, 'R_ddr': 0.0}
    per_axis_best_drug = {'R_prolif': None, 'R_emt': None, 'R_ddr': None}
    for drug, info in drug_models.items():
        if info['auroc'] < PER_AXIS_MIN_AUROC_THRESHOLD:
            continue
        coefs = info['coefficients']
        for axis in per_axis_max_coef:
            mag = abs(coefs.get(axis, 0.0))
            if mag > per_axis_max_coef[axis]:
                per_axis_max_coef[axis] = mag
                per_axis_best_drug[axis] = drug
    print(f"\n  Per-axis max |coef| across drugs with AUROC >= "
          f"{PER_AXIS_MIN_AUROC_THRESHOLD}:")
    for axis in ['R_prolif', 'R_emt', 'R_ddr']:
        mag = per_axis_max_coef[axis]
        drug = per_axis_best_drug[axis]
        label = 'R_ddr (residualized)' if axis == 'R_ddr' else axis
        print(f"    {label}: {mag:.3f} ({drug})")

    # ---------------------------------------------------------
    banner("Step 4: Van Galen pseudobulk + UCell + residualization + prediction")
    print("  Loading Van Galen AnnData...")
    t0 = time.time()
    adata = ad.read_h5ad(str(ANNDATA_PATH))
    print(f"    {adata.n_obs:,} cells x {adata.n_vars:,} genes  "
          f"({time.time()-t0:.1f}s)")

    adata.obs['CellType'] = adata.obs['CellType'].astype('category')
    celltypes = list(adata.obs['CellType'].cat.categories)
    print(f"    Cell types: {len(celltypes)}")

    X = adata.X
    if not sp.issparse(X):
        X = sp.csr_matrix(X)

    pseudobulk = {}
    for ct in celltypes:
        mask = (adata.obs['CellType'] == ct).values
        X_sub = X[mask, :]
        mean_expr = np.asarray(X_sub.mean(axis=0)).flatten()
        pseudobulk[ct] = mean_expr

    pseudobulk_df = pd.DataFrame(
        pseudobulk,
        index=[str(g).upper() for g in adata.var_names]
    ).T
    print(f"    Pseudobulk matrix: {pseudobulk_df.shape}")

    print("  Wrapping Van Galen pseudobulk as AnnData for pyUCell...")
    vg_adata = ad.AnnData(
        X=pseudobulk_df.values,
        obs=pd.DataFrame(index=pseudobulk_df.index),
        var=pd.DataFrame(index=pseudobulk_df.columns),
    )

    print(f"  Running pyUCell on Van Galen (max_rank={MAX_RANK}, n_jobs=1)...")
    t0 = time.time()
    uc.compute_ucell_scores(
        vg_adata,
        signatures=SIGNATURES,
        max_rank=MAX_RANK,
        missing_genes='impute',
        suffix='_UCell',
        n_jobs=1,  # avoids joblib loky read-only bug (pyucell 0.6.0)
    )
    print(f"    pyUCell computed in {time.time()-t0:.1f}s")

    vangalen_axes_raw = pd.DataFrame({
        'R_prolif': vg_adata.obs['prolif_UCell'],
        'R_emt':    vg_adata.obs['emt_UCell'],
        'R_ddr':    vg_adata.obs['ddr_UCell'],
    }, index=vg_adata.obs.index)

    # Apply SAME alpha, beta from BeatAML to Van Galen
    print(f"\n  Applying BeatAML-fit alpha={alpha:.4f}, beta={beta:.4f} "
          f"to Van Galen for R_ddr_residual...")
    vangalen_axes = pd.DataFrame({
        'R_prolif': vangalen_axes_raw['R_prolif'],
        'R_emt':    vangalen_axes_raw['R_emt'],
        'R_ddr':    vangalen_axes_raw['R_ddr'] - (alpha + beta * vangalen_axes_raw['R_prolif']),
    }, index=vangalen_axes_raw.index)
    print(f"\n  Van Galen cell-type FINAL axes (R_ddr is residual):")
    print(vangalen_axes.round(4).to_string())
    vangalen_axes.to_csv(OUT_VANGALEN_AXES)

    print(f"\n  Predicting drug sensitivity per cell type...")
    drug_list = list(drug_models.keys())
    celltype_drug_pred = kaalcura.predict_sensitivity_multi_drug(
        vangalen_axes, drug_list
    )
    print(f"  Predictions: {celltype_drug_pred.shape[0]} cell types x "
          f"{celltype_drug_pred.shape[1]} drugs")

    # ---------------------------------------------------------
    banner("Step 5: Validation queries (5 gates + 1 diagnostic)")

    # Q_A (corrected): HSC-like R_prolif < Prog-like R_prolif
    print("\n  Query A (CORRECTED): HSC-like R_prolif < Prog-like R_prolif")
    print("    (Van Galen 2019: Prog-like is proliferating committed progenitor;")
    print("     HSC-like is quiescent LSC. Mono-like was wrong comparator in 2.2a.)")
    hsc_rprolif = float(vangalen_axes.loc['HSC-like', 'R_prolif'])
    prog_rprolif = float(vangalen_axes.loc['Prog-like', 'R_prolif'])
    gmp_rprolif = float(vangalen_axes.loc['GMP-like', 'R_prolif'])
    mono_rprolif = float(vangalen_axes.loc['Mono-like', 'R_prolif'])
    print(f"    HSC-like R_prolif:   {hsc_rprolif:.4f}")
    print(f"    Prog-like R_prolif:  {prog_rprolif:.4f}  (primary comparator, Q_A)")
    print(f"    GMP-like R_prolif:   {gmp_rprolif:.4f}  (secondary diagnostic)")
    print(f"    Mono-like R_prolif:  {mono_rprolif:.4f}  (Round 2.2a fail, not tested)")
    Q_A_pass = hsc_rprolif < prog_rprolif
    Q_A_margin = prog_rprolif - hsc_rprolif
    q_a_secondary_gmp = hsc_rprolif < gmp_rprolif
    print(f"    Q_A (vs Prog-like):  {'PASS' if Q_A_pass else 'FAIL'} "
          f"(margin = {Q_A_margin:.4f})")
    print(f"    Q_A secondary (vs GMP-like): {'PASS' if q_a_secondary_gmp else 'FAIL'}")

    # Q_B: axis non-redundancy on Van Galen with residualized R_ddr
    print(f"\n  Query B: Max pairwise |r| < {AXIS_REDUNDANCY_MAX_ABS_R} "
          f"(Van Galen, with residualized R_ddr)")
    ct_axis_corr = vangalen_axes.corr()
    print(ct_axis_corr.round(3).to_string())
    max_abs_r = float(ct_axis_corr.abs().values[np.triu_indices(3, k=1)].max())
    print(f"    Max pairwise |r|: {max_abs_r:.4f}")
    print(f"    (Round 2.2a had 0.932 before residualization.)")
    Q_B_pass = max_abs_r < AXIS_REDUNDANCY_MAX_ABS_R
    print(f"    Q_B: {'PASS' if Q_B_pass else 'FAIL'}")

    # Q_C: mean CV-AUROC (held at 0.55)
    print(f"\n  Query C: Mean CV-AUROC >= {MIN_CV_AUROC_PASS} AND three-axis contrib")
    q_c_mean_pass = mean_auroc >= MIN_CV_AUROC_PASS
    q_c_axes_pass = all(per_axis_max_coef[a] > 0 for a in per_axis_max_coef)
    Q_C_pass = q_c_mean_pass and q_c_axes_pass
    print(f"    Mean CV-AUROC: {'PASS' if q_c_mean_pass else 'FAIL'} "
          f"(mean={mean_auroc:.4f})")
    print(f"    Three-axis contribution: {'PASS' if q_c_axes_pass else 'FAIL'}")
    print(f"    Q_C: {'PASS' if Q_C_pass else 'FAIL'}")
    if not q_c_mean_pass:
        print(f"    NOTE: Round 2.1d=0.534, Round 2.2a=0.532, "
              f"Round 2.2b={mean_auroc:.4f}. "
              f"Three rounds near 0.53 = plateau finding for Round 2.2c+.")

    # Q_D: Prog-FLT3 correlation (unchanged from 2.2a)
    print(f"\n  Query D: Prog-like predictions correlate with FLT3-ITD+ differential")
    clin = pd.read_excel(BEATAML_CLIN, sheet_name=BEATAML_CLIN_SHEET)
    if BEATAML_CLIN_SAMPLE_COL not in clin.columns:
        sys.exit(f"FATAL: clinical missing {BEATAML_CLIN_SAMPLE_COL}")
    if BEATAML_CLIN_FLT3_COL not in clin.columns:
        sys.exit(f"FATAL: clinical missing {BEATAML_CLIN_FLT3_COL}")

    sample_to_flt3 = {}
    for _, row in clin.iterrows():
        sid = row[BEATAML_CLIN_SAMPLE_COL]
        flt3 = row[BEATAML_CLIN_FLT3_COL]
        if pd.notna(sid) and pd.notna(flt3):
            sample_to_flt3[str(sid)] = flt3
    pos_count = sum(1 for v in sample_to_flt3.values() if v == BEATAML_CLIN_FLT3_POS)
    neg_count = sum(1 for v in sample_to_flt3.values() if v == BEATAML_CLIN_FLT3_NEG)
    print(f"    FLT3-ITD status: pos={pos_count}, neg={neg_count}")

    observed_diff = {}
    for drug in drug_list:
        if drug not in drug_matrix_overlap.columns:
            continue
        drug_series = drug_matrix_overlap[drug].dropna()
        itd_plus = [v for sid, v in drug_series.items()
                    if sample_to_flt3.get(sid) == BEATAML_CLIN_FLT3_POS]
        itd_minus = [v for sid, v in drug_series.items()
                     if sample_to_flt3.get(sid) == BEATAML_CLIN_FLT3_NEG]
        if len(itd_plus) < 5 or len(itd_minus) < 5:
            continue
        observed_diff[drug] = float(np.median(itd_plus) - np.median(itd_minus))
    print(f"    Drugs with >=5 ITD+/ITD-: {len(observed_diff)}")

    progLike_pred = celltype_drug_pred.loc['Prog-like']
    common_drugs = [d for d in observed_diff if d in progLike_pred.index]
    print(f"    Drugs aligned: {len(common_drugs)}")

    if len(common_drugs) >= 10:
        obs_vals = [observed_diff[d] for d in common_drugs]
        pred_vals = [float(progLike_pred[d]) for d in common_drugs]
        rho, p = stats.spearmanr(pred_vals, obs_vals)
        print(f"    Spearman rho: {rho:.4f}, p: {p:.3e}")
        print(f"    (Round 2.2a: rho=-0.235, p=0.005 — should remain similar)")
        Q_D_pass = (p < 0.05) and (rho < 0)
    else:
        rho, p = float('nan'), float('nan')
        Q_D_pass = False
    print(f"    Q_D: {'PASS' if Q_D_pass else 'FAIL'}")

    # Q_E: distinguishability
    print(f"\n  Query E: HSC-like vs Prog-like Jaccard < {JACCARD_MAX}")
    hsc_top = celltype_drug_pred.loc['HSC-like'].sort_values(
        ascending=False).head(10).index.tolist()
    prog_top = celltype_drug_pred.loc['Prog-like'].sort_values(
        ascending=False).head(10).index.tolist()
    hsc_set = set(hsc_top)
    prog_set = set(prog_top)
    intersection = hsc_set & prog_set
    union = hsc_set | prog_set
    jaccard = len(intersection) / len(union) if union else 1.0
    print(f"    HSC-like top 10:  {sorted(hsc_set)}")
    print(f"    Prog-like top 10: {sorted(prog_set)}")
    print(f"    Jaccard: {jaccard:.4f}")
    Q_E_pass = jaccard < JACCARD_MAX
    print(f"    Q_E: {'PASS' if Q_E_pass else 'FAIL'}")

    # Venetoclax preservation diagnostic
    venetoclax_in_hsc = any('venetoclax' in d.lower() for d in hsc_set)
    print(f"\n  Venetoclax in HSC-like top 10 (diagnostic): "
          f"{'YES — preserved from Round 2.2a' if venetoclax_in_hsc else 'NO — lost'}")

    # Q_F: diagnostic range ratios
    print(f"\n  Q_F (DIAGNOSTIC — not gated)")
    print(f"  Per-axis range ratio: Van Galen / BeatAML")
    vg_ranges = vangalen_axes.max() - vangalen_axes.min()
    ba_ranges = beataml_axes.max() - beataml_axes.min()
    range_ratios = (vg_ranges / ba_ranges).to_dict()
    for axis in ['R_prolif', 'R_emt', 'R_ddr']:
        vg_r = float(vg_ranges[axis])
        ba_r = float(ba_ranges[axis])
        ratio = float(range_ratios[axis])
        label = 'R_ddr (residualized)' if axis == 'R_ddr' else axis
        print(f"    {label}: VG={vg_r:.4f}, BA={ba_r:.4f}, ratio={ratio:.3f}")

    # ---------------------------------------------------------
    banner("Step 6: Verdict")
    results_table = [
        ("Q_A (LSC quiescence vs Prog-like)",       Q_A_pass),
        ("Q_B (axis non-redundancy |r|<0.9)",        Q_B_pass),
        ("Q_C (mean AUROC + 3-axis contrib)",        Q_C_pass),
        ("Q_D (Prog-FLT3 correlation)",              Q_D_pass),
        ("Q_E (distinguishability)",                 Q_E_pass),
    ]
    for name, passed in results_table:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
    all_pass = all(p for _, p in results_table)
    verdict = 'PASS' if all_pass else 'FAIL'
    print(f"\n  VERDICT: {verdict}")

    summary = {
        'verdict': verdict,
        'version': 'round2.2b',
        'spec_commit': '1333a9d',
        'mechanism': 'pyUCell rank-based scoring + PCNA-style R_ddr residualization',
        'max_rank': MAX_RANK,
        'residualization': {
            'method': 'linear regression R_ddr ~ alpha + beta * R_prolif, fit on BeatAML',
            'reference': 'Peterson & Kovyrshina 2019 Cancers',
            'alpha': alpha,
            'beta': beta,
            'r_squared': r_value**2,
            'beataml_post_residualization_corr': float(check_corr),
        },
        'signatures': {k: v for k, v in SIGNATURES.items()},
        'training_stats': {
            'n_beataml_samples_train': int(axes_final.shape[0]),
            'n_drugs_trained': len(drug_models),
            'mean_cv_auroc': mean_auroc,
            'median_cv_auroc': median_auroc,
            'n_drugs_auroc_ge_0_60': n_auroc_above_60,
            'per_axis_max_coef': per_axis_max_coef,
            'per_axis_best_drug': per_axis_best_drug,
        },
        'beataml_axis_correlations_post_residualization': beataml_axis_corr.to_dict(),
        'vangalen_axis_per_celltype_post_residualization': vangalen_axes.to_dict(orient='index'),
        'vangalen_axis_correlations_post_residualization': ct_axis_corr.to_dict(),
        'queries': {
            'Q_A_LSC_quiescence_vs_Prog_like': {
                'hsc_like_rprolif': hsc_rprolif,
                'prog_like_rprolif': prog_rprolif,
                'margin': Q_A_margin,
                'secondary_gmp_like_rprolif': gmp_rprolif,
                'secondary_pass': bool(q_a_secondary_gmp),
                'mono_like_rprolif_for_reference': mono_rprolif,
                'pass': bool(Q_A_pass),
            },
            'Q_B_axis_non_redundancy': {
                'max_abs_r': max_abs_r,
                'threshold': AXIS_REDUNDANCY_MAX_ABS_R,
                'pass': bool(Q_B_pass),
            },
            'Q_C_axis_utility': {
                'mean_auroc': mean_auroc,
                'threshold_mean': MIN_CV_AUROC_PASS,
                'threshold_per_axis_auroc': PER_AXIS_MIN_AUROC_THRESHOLD,
                'per_axis_max_coef': per_axis_max_coef,
                'mean_check_pass': bool(q_c_mean_pass),
                'axes_contrib_pass': bool(q_c_axes_pass),
                'pass': bool(Q_C_pass),
                'historical_comparison': {
                    'round2.1d_z_score': 0.534,
                    'round2.2a_pyucell_raw': 0.532,
                    'round2.2b_pyucell_residualized': mean_auroc,
                },
            },
            'Q_D_prog_flt3_correlation': {
                'n_drugs_aligned': int(len(common_drugs)),
                'spearman_rho': float(rho) if not np.isnan(rho) else None,
                'spearman_p': float(p) if not np.isnan(p) else None,
                'pass': bool(Q_D_pass),
            },
            'Q_E_distinguishability': {
                'jaccard': float(jaccard),
                'threshold': JACCARD_MAX,
                'hsc_top10': sorted(hsc_set),
                'prog_top10': sorted(prog_set),
                'venetoclax_in_hsc_top10_diagnostic': bool(venetoclax_in_hsc),
                'pass': bool(Q_E_pass),
            },
        },
        'Q_F_diagnostic_range_ratios': {
            axis: {
                'vangalen_range': float(vg_ranges[axis]),
                'beataml_range': float(ba_ranges[axis]),
                'ratio': float(range_ratios[axis]),
            }
            for axis in ['R_prolif', 'R_emt', 'R_ddr']
        },
    }
    with open(OUT_SUMMARY, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  Summary JSON: {OUT_SUMMARY}")

    if not all_pass:
        print(f"\n  Graph NOT saved — one or more gates failed.")
        print(f"  Diagnostic preserved for investigation.")
        sys.exit(3)

    # ---------------------------------------------------------
    banner("Step 7: Integrate Layer 2 and save net (all five passed)")
    with open(SKELETON_PATH, 'rb') as f:
        G = pickle.load(f)
    print(f"  Skeleton: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

    for ct in celltypes:
        ct_node = f"celltype::{ct}"
        axes_row = vangalen_axes.loc[ct]
        G.add_node(
            ct_node,
            layer='L2_transcriptome',
            node_kind='cell_type',
            malignant=('-like' in ct),
            n_cells=int((adata.obs['CellType'] == ct).sum()),
            R_prolif=float(axes_row['R_prolif']),
            R_emt=float(axes_row['R_emt']),
            R_ddr_residual=float(axes_row['R_ddr']),
        )

    n_edges = 0
    for ct in celltypes:
        ct_node = f"celltype::{ct}"
        pred_series = celltype_drug_pred.loc[ct]
        for drug, p_sens in pred_series.items():
            drug_node = f"drug::{drug}"
            if drug_node not in G:
                continue
            G.add_edge(drug_node, ct_node,
                       edge_kind='drug_active_on_celltype',
                       p_sensitive=float(p_sens),
                       auroc=float(drug_models[drug]['auroc']))
            n_edges += 1
    print(f"  Added {len(celltypes)} cell-type nodes, {n_edges} drug-celltype edges")

    layer_inv = {}
    for _, d in G.nodes(data=True):
        l = d.get('layer', 'unknown')
        layer_inv[l] = layer_inv.get(l, 0) + 1
    print(f"\n  Final layer inventory:")
    for k, v in sorted(layer_inv.items()):
        print(f"    {k}: {v:,} nodes")
    print(f"  Final net: {G.number_of_nodes():,} nodes, "
          f"{G.number_of_edges():,} edges")

    with open(OUT_NET_PATH, 'wb') as f:
        pickle.dump(G, f)
    try:
        with open(OUT_KAALCURA_STATE, 'wb') as f:
            pickle.dump(kaalcura, f)
        print(f"  Saved KAALCURA state: {OUT_KAALCURA_STATE}")
    except Exception as e:
        print(f"  WARN: couldn't pickle KAALCURA ({e})")

    size_mb = OUT_NET_PATH.stat().st_size / (1024 * 1024)
    print(f"  Saved net: {OUT_NET_PATH} ({size_mb:.1f} MB)")
    print(f"\n  Round 2.2b complete — Layer 2 integrated with residualized R_ddr.")


if __name__ == '__main__':
    main()
