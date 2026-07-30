#!/usr/bin/env python3
"""
INTERCEPTA Round 2.2a — pyUCell-based AML Net Integration
==========================================================

Implementation of the specification at
  round2_aml/docs/INTERCEPTA_Round2_2a_Specification.md
committed as c257b8d (amendment v2 — Q_F demoted to diagnostic).

This code is a mechanical translation of the spec. If it ever diverges
from the spec, the spec wins. Any design choice not here is a bug.

Addresses the Round 2.1d methodology finding (scale-mismatch between
bulk-trained KAALCURA z-score parameters and scRNA-seq pseudobulk) by
replacing z-score axis computation with pyUCell rank-based Mann-Whitney U
scoring. Drug models are trained on BeatAML UCell axes (not KAALCURA
z-score axes) and applied to Van Galen cell-type pseudobulk UCell axes.

Five validation queries gate the round (all must pass):
  Q_A — LSC quiescence (HSC-like prolif_UCell < Mono-like prolif_UCell)
  Q_B — Axis non-redundancy (max pairwise |r| < 0.9 across 21 cell types)
  Q_C — Mean CV-AUROC >= 0.55 AND all three axes contribute non-zero
        coefficient in at least one drug with AUROC >= 0.60
  Q_D — Spearman(Prog-like predictions, FLT3-ITD+/- AUC differential)
        rho < 0 AND p < 0.05 (negative correlation expected from first
        principles)
  Q_E — HSC-like vs Prog-like top-10 drug Jaccard < 0.6

One diagnostic metric reported but not gated:
  Q_F — Per-axis Van Galen / BeatAML range ratio

Environment: intercepta-scrna conda env (see code/environment_round2_2.txt)
Round 1 KAALCURA module imported unchanged.

Run:
    conda activate intercepta-scrna
    cd ~/INTERCEPTA/round2_aml/code
    python3 build_aml_net_round22a_ucell.py 2>&1 | tee \\
        ../results/aml_net_round22a_build.txt

Author: Prasad Akula
Date:    April 22, 2026
Spec:    commit c257b8d (amendment v2)
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

# Output paths (spec section 7)
OUT_NET_PATH = RESULTS_DIR / 'aml_net_round22a_ucell.gpickle'
OUT_SUMMARY = RESULTS_DIR / 'aml_net_round22a_summary.json'
OUT_KAALCURA_STATE = RESULTS_DIR / 'kaalcura_ucell_state_round22a.pkl'
OUT_BEATAML_AXES = RESULTS_DIR / 'beataml_ucell_axes_round22a.csv'
OUT_VANGALEN_AXES = RESULTS_DIR / 'vangalen_celltype_ucell_axes_round22a.csv'

# Locked by spec amendment v2 (commit c257b8d), section 3.3 and 5
MAX_RANK = 17663  # empirical median non-zero gene count (BeatAML)
MIN_CV_AUROC_PASS = 0.55
AXIS_REDUNDANCY_MAX_ABS_R = 0.9
PER_AXIS_MIN_AUROC_THRESHOLD = 0.60
JACCARD_MAX = 0.6

# Verified column structure (from Round 2.1d session)
BEATAML_METADATA_COLS = {'stable_id', 'display_label', 'description', 'biotype'}
BEATAML_GENE_SYMBOL_COL = 'display_label'
BEATAML_CURVE_SAMPLE_COL = 'dbgap_rnaseq_sample'
BEATAML_CLIN_SAMPLE_COL = 'dbgap_rnaseq_sample'
BEATAML_CLIN_SHEET = 'summary'
BEATAML_CLIN_FLT3_COL = 'FLT3-ITD'
BEATAML_CLIN_FLT3_POS = 'positive'
BEATAML_CLIN_FLT3_NEG = 'negative'

# Gene sets — reuse Round 1 KAALCURA gene sets verbatim (spec section 3.2)
# EMT gets +/- suffix to preserve inverted gene semantics in pyUCell
SIGNATURES = {
    'prolif': [
        'MKI67', 'TOP2A', 'PCNA', 'CDK1', 'CCNB1', 'AURKA', 'BUB1',
        'PLK1', 'MCM2', 'MCM6', 'FOXM1', 'BIRC5', 'NUSAP1', 'TPX2',
        'CDC20', 'CENPF', 'KIF11', 'PRC1', 'HMGA1', 'MYBL2',
    ],
    'emt': [
        # positive EMT genes
        'VIM', 'CDH2', 'SNAI1', 'SNAI2', 'ZEB1', 'ZEB2', 'TWIST1',
        'FN1', 'MMP2', 'MMP9',
        # inverted (epithelial) genes - pyUCell - suffix means negative
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
    beataml_df = beataml_wide.T  # rows = samples, cols = genes
    beataml_df.index = beataml_df.index.astype(str)
    print(f"    Matrix after dedupe/transpose: {beataml_df.shape}")

    # Wrap BeatAML in AnnData for pyUCell (spec 4.2)
    print("  Wrapping BeatAML as AnnData for pyUCell...")
    beataml_adata = ad.AnnData(
        X=beataml_df.values,
        obs=pd.DataFrame(index=beataml_df.index),
        var=pd.DataFrame(index=beataml_df.columns),
    )
    print(f"    BeatAML AnnData: {beataml_adata.n_obs} samples x {beataml_adata.n_vars} genes")

    # Apply pyUCell
    print(f"  Running pyUCell on BeatAML (max_rank={MAX_RANK})...")
    t0 = time.time()
    uc.compute_ucell_scores(
        beataml_adata,
        signatures=SIGNATURES,
        max_rank=MAX_RANK,
        missing_genes='impute',
        n_jobs=1,  # avoids joblib loky read-only bug
        suffix='_UCell',
    )
    print(f"    pyUCell computed in {time.time()-t0:.1f}s")

    # Extract axes as DataFrame
    beataml_axes = pd.DataFrame({
        'R_prolif': beataml_adata.obs['prolif_UCell'],
        'R_emt':    beataml_adata.obs['emt_UCell'],
        'R_ddr':    beataml_adata.obs['ddr_UCell'],
    }, index=beataml_adata.obs.index)
    print(f"\n  BeatAML axes summary:")
    print(beataml_axes.describe().round(3).to_string())
    beataml_axes.to_csv(OUT_BEATAML_AXES)
    print(f"\n  Saved: {OUT_BEATAML_AXES}")

    beataml_axis_corr = beataml_axes.corr()
    print(f"\n  Pairwise Pearson correlations (BeatAML):")
    print(beataml_axis_corr.round(3).to_string())

    # ---------------------------------------------------------
    banner("Step 2: Load BeatAML curve_fits, train drug models on UCell axes")
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
    print(f"    Sample overlap (expression <-> curve_fits): {len(overlap)}")
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

    # KAALCURA.train_drug_models expects a "fitted" KAALCURA instance.
    # We fit it on BeatAML expression (ignored for training), then train
    # drug models by passing the UCell axes. This reuses Round 1 code
    # without modification (Principle 16).
    print("  Training drug models via Round 1 KAALCURA.train_drug_models...")
    kaalcura = KAALCURA(random_state=42)

    # We still need to "fit_reference" to set _is_fitted=True, but we use
    # BeatAML expression as the reference (mechanism-independent step).
    # train_drug_models only uses axes_df and drug_sensitivity_df.
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
    print(f"\n  Mean CV-AUROC:   {mean_auroc:.3f}")
    print(f"  Median CV-AUROC: {median_auroc:.3f}")
    print(f"  Drugs with AUROC >= {PER_AXIS_MIN_AUROC_THRESHOLD}: "
          f"{n_auroc_above_60}/{len(auroc_values)}")

    # Per-axis contribution check (spec Q_C second part)
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
        print(f"    {axis}: {mag:.3f} ({drug})")

    # ---------------------------------------------------------
    banner("Step 3: Van Galen cell-type pseudobulk + UCell + drug prediction")
    print("  Loading Van Galen AnnData...")
    t0 = time.time()
    adata = ad.read_h5ad(str(ANNDATA_PATH))
    print(f"    {adata.n_obs:,} cells x {adata.n_vars:,} genes  ({time.time()-t0:.1f}s)")

    adata.obs['CellType'] = adata.obs['CellType'].astype('category')
    celltypes = list(adata.obs['CellType'].cat.categories)
    print(f"    Cell types: {len(celltypes)}")

    # Pseudobulk: mean expression per cell type
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
    ).T  # rows = cell types, cols = genes

    print(f"    Pseudobulk matrix: {pseudobulk_df.shape}")

    # Wrap Van Galen pseudobulk in AnnData for pyUCell
    print("  Wrapping Van Galen pseudobulk as AnnData for pyUCell...")
    vg_adata = ad.AnnData(
        X=pseudobulk_df.values,
        obs=pd.DataFrame(index=pseudobulk_df.index),
        var=pd.DataFrame(index=pseudobulk_df.columns),
    )

    # Apply pyUCell with THE SAME max_rank (spec 3.3)
    print(f"  Running pyUCell on Van Galen pseudobulk (max_rank={MAX_RANK})...")
    t0 = time.time()
    uc.compute_ucell_scores(
        vg_adata,
        signatures=SIGNATURES,
        max_rank=MAX_RANK,
        missing_genes='impute',
        n_jobs=1,  # avoids joblib loky read-only bug
        suffix='_UCell',
    )
    print(f"    pyUCell computed in {time.time()-t0:.1f}s")

    vangalen_axes = pd.DataFrame({
        'R_prolif': vg_adata.obs['prolif_UCell'],
        'R_emt':    vg_adata.obs['emt_UCell'],
        'R_ddr':    vg_adata.obs['ddr_UCell'],
    }, index=vg_adata.obs.index)
    print(f"\n  Van Galen cell-type UCell axes:")
    print(vangalen_axes.round(3).to_string())
    vangalen_axes.to_csv(OUT_VANGALEN_AXES)

    # Predict drug sensitivity per cell type
    print(f"\n  Predicting drug sensitivity per cell type...")
    drug_list = list(drug_models.keys())
    celltype_drug_pred = kaalcura.predict_sensitivity_multi_drug(
        vangalen_axes, drug_list
    )
    print(f"  Predictions: {celltype_drug_pred.shape[0]} cell types "
          f"x {celltype_drug_pred.shape[1]} drugs")

    # ---------------------------------------------------------
    banner("Step 4: Validation queries (five gates + one diagnostic)")

    # Q_A: LSC quiescence
    print("\n  Query A: HSC-like R_prolif < Mono-like R_prolif (LSC quiescence)")
    hsc_rprolif = float(vangalen_axes.loc['HSC-like', 'R_prolif'])
    mono_rprolif = float(vangalen_axes.loc['Mono-like', 'R_prolif'])
    print(f"    HSC-like R_prolif:  {hsc_rprolif:.4f}")
    print(f"    Mono-like R_prolif: {mono_rprolif:.4f}")
    Q_A_pass = hsc_rprolif < mono_rprolif
    print(f"    Q_A: {'PASS' if Q_A_pass else 'FAIL'}")

    # Q_B: Axis non-redundancy
    print(f"\n  Query B: Axis non-redundancy (|r| < {AXIS_REDUNDANCY_MAX_ABS_R})")
    ct_axis_corr = vangalen_axes.corr()
    print(ct_axis_corr.round(3).to_string())
    max_abs_r = float(ct_axis_corr.abs().values[np.triu_indices(3, k=1)].max())
    print(f"    Max pairwise |r|: {max_abs_r:.3f}")
    Q_B_pass = max_abs_r < AXIS_REDUNDANCY_MAX_ABS_R
    print(f"    Q_B: {'PASS' if Q_B_pass else 'FAIL'}")

    # Q_C: Mean CV-AUROC + per-axis contribution
    print(f"\n  Query C: Mean CV-AUROC >= {MIN_CV_AUROC_PASS} AND three-axis contrib")
    q_c_mean_pass = mean_auroc >= MIN_CV_AUROC_PASS
    q_c_axes_pass = all(per_axis_max_coef[a] > 0 for a in per_axis_max_coef)
    Q_C_pass = q_c_mean_pass and q_c_axes_pass
    print(f"    Mean CV-AUROC: {'PASS' if q_c_mean_pass else 'FAIL'} "
          f"(mean={mean_auroc:.3f})")
    print(f"    Three-axis contribution: {'PASS' if q_c_axes_pass else 'FAIL'}")
    print(f"    Q_C: {'PASS' if Q_C_pass else 'FAIL'}")

    # Q_D: Prog-like vs FLT3-ITD+ differential correlation
    print(f"\n  Query D: Prog-like predictions correlate with FLT3-ITD+ differential")
    print("    Loading clinical data...")
    clin = pd.read_excel(BEATAML_CLIN, sheet_name=BEATAML_CLIN_SHEET)
    print(f"    Clinical shape: {clin.shape}")
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
    print(f"    Samples with FLT3-ITD status: {len(sample_to_flt3)} "
          f"(pos={pos_count}, neg={neg_count})")

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
    print(f"    Drugs with >=5 ITD+/ITD- samples each: {len(observed_diff)}")

    progLike_pred = celltype_drug_pred.loc['Prog-like']
    common_drugs = [d for d in observed_diff if d in progLike_pred.index]
    print(f"    Drugs aligned with Prog-like predictions: {len(common_drugs)}")

    if len(common_drugs) >= 10:
        obs_vals = [observed_diff[d] for d in common_drugs]
        pred_vals = [float(progLike_pred[d]) for d in common_drugs]
        rho, p = stats.spearmanr(pred_vals, obs_vals)
        print(f"    Spearman rho: {rho:.3f}, p: {p:.3e}")
        print(f"    (Expected: negative rho; high P_sensitive -> low AUC)")
        Q_D_pass = (p < 0.05) and (rho < 0)
    else:
        rho, p = float('nan'), float('nan')
        Q_D_pass = False
        print(f"    Insufficient aligned drugs")
    print(f"    Q_D: {'PASS' if Q_D_pass else 'FAIL'}")

    # Q_E: Distinguishability
    print(f"\n  Query E: HSC-like vs Prog-like Jaccard < {JACCARD_MAX}")
    hsc_top = celltype_drug_pred.loc['HSC-like'].sort_values(ascending=False).head(10).index.tolist()
    prog_top = celltype_drug_pred.loc['Prog-like'].sort_values(ascending=False).head(10).index.tolist()
    hsc_set = set(hsc_top)
    prog_set = set(prog_top)
    intersection = hsc_set & prog_set
    union = hsc_set | prog_set
    jaccard = len(intersection) / len(union) if union else 1.0
    print(f"    HSC-like top 10:  {sorted(hsc_set)}")
    print(f"    Prog-like top 10: {sorted(prog_set)}")
    print(f"    Overlap ({len(intersection)}): {sorted(intersection)}")
    print(f"    Jaccard: {jaccard:.3f}")
    Q_E_pass = jaccard < JACCARD_MAX
    print(f"    Q_E: {'PASS' if Q_E_pass else 'FAIL'}")

    # Q_F: DIAGNOSTIC (not a gate)
    print(f"\n  Q_F (DIAGNOSTIC — not a pass/fail gate)")
    print(f"  Per-axis range ratio: Van Galen / BeatAML")
    vg_ranges = vangalen_axes.max() - vangalen_axes.min()
    ba_ranges = beataml_axes.max() - beataml_axes.min()
    range_ratios = (vg_ranges / ba_ranges).to_dict()
    for axis in ['R_prolif', 'R_emt', 'R_ddr']:
        vg_r = float(vg_ranges[axis])
        ba_r = float(ba_ranges[axis])
        ratio = float(range_ratios[axis])
        print(f"    {axis}: VG range={vg_r:.4f}, BA range={ba_r:.4f}, "
              f"ratio={ratio:.2f}")
    print(f"  (Reported only; does not gate the round per spec v2)")

    # ---------------------------------------------------------
    banner("Step 5: Verdict")
    results_table = [
        ("Q_A (LSC quiescence)",                Q_A_pass),
        ("Q_B (axis non-redundancy |r|<0.9)",    Q_B_pass),
        ("Q_C (mean AUROC + 3-axis contrib)",    Q_C_pass),
        ("Q_D (Prog-FLT3 correlation)",          Q_D_pass),
        ("Q_E (distinguishability)",             Q_E_pass),
    ]
    for name, passed in results_table:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
    all_pass = all(p for _, p in results_table)
    verdict = 'PASS' if all_pass else 'FAIL'
    print(f"\n  VERDICT: {verdict}")

    # Always write the summary JSON (whether pass or fail)
    summary = {
        'verdict': verdict,
        'version': 'round2.2a-v2',
        'spec_commit': 'c257b8d',
        'mechanism': 'pyUCell rank-based Mann-Whitney U scoring',
        'max_rank': MAX_RANK,
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
        'beataml_axis_correlations': beataml_axis_corr.to_dict(),
        'vangalen_axis_per_celltype': vangalen_axes.to_dict(orient='index'),
        'vangalen_axis_correlations': ct_axis_corr.to_dict(),
        'queries': {
            'Q_A_LSC_quiescence': {
                'hsc_like_rprolif': hsc_rprolif,
                'mono_like_rprolif': mono_rprolif,
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
    banner("Step 6: Integrate Layer 2 and save net (all five gates passed)")
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
            R_ddr=float(axes_row['R_ddr']),
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
    print(f"  Final net: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

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
    print(f"\n  Round 2.2a complete — Layer 2 integrated via pyUCell.")


if __name__ == '__main__':
    main()
