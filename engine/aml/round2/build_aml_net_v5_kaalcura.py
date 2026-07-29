#!/usr/bin/env python3
"""
INTERCEPTA Round 2.1d v5 — AML Net Integration via KAALCURA-per-cell-type
==========================================================================

Purpose
-------
Extend the Round 2.1b AML net skeleton with single-cell transcriptome
data from Round 2.1c by applying the KAALCURA module (from Round 1,
preserved unchanged) to per-cell-type pseudobulks.

The vision (Part 5.2) explicitly specifies this:
  "Apply KAALCURA independently to the sensitive cell cluster and the
   resistant cell cluster. This tells us exactly which drugs kill
   sensitive cells and which drugs kill resistant cells."

Why v5 (not v3 or v4)
---------------------
v3 used rank_genes_groups DE scores — failed, biased toward lineage
    markers that aren't druggable targets
v4 used mean target-gene expression — failed, biased toward drugs with
    many broadly-expressed targets; also BCL2 dropout meant venetoclax
    couldn't rank even though biology says it should
v5 uses KAALCURA — the validated module from Round 1 that the vision
    specifies. Three biologically interpretable axes, trained via
    logistic regression on real drug response. This is the vision's
    specified mechanism, not a substitute.

Design — five steps
-------------------
Step 1: Fit KAALCURA reference on BeatAML bulk RNA-seq (805 AML samples).
        Pass tissue_labels=None — single tissue = bone marrow, so
        residualization is correctly skipped.

Step 2: Compute (R_prolif, R_emt, R_ddr) per BeatAML sample.

Step 3: Train drug response models on BeatAML AUC data
        (beataml_probit_curve_fits, 166 drugs).
        Pass criterion: mean CV-AUROC >= 0.55 (honest bar for
        single-tissue retraining on smaller cohort than Round 1's GDSC).

Step 4: Compute pseudobulk per Van Galen cell type (21 populations),
        apply KAALCURA to get per-cell-type axes, apply trained drug
        models to get P(sensitive) per (cell type, drug).

Step 5: Five validation queries. Graph saved only if all pass.

Validation queries
------------------
Q_A: HSC-like R_prolif < Mono-like R_prolif (Van Galen LSC quiescence)
Q_B: Axis independence: pairwise |r| < 0.5 among R_prolif/R_emt/R_ddr
     across 21 cell types (residualization off, so relaxed from 0.02)
Q_C: Mean CV-AUROC across BeatAML drug models >= 0.55
Q_D: Predicted Prog-like drug sensitivity correlates with observed
     BeatAML differential response (FLT3-ITD+ vs FLT3-ITD-) across
     drugs; Spearman p < 0.05
Q_E: Top 10 drugs for HSC-like vs Prog-like differ, Jaccard < 0.6

Honest commitments
------------------
- intercepta_kaalcura_v1.KAALCURA imported UNCHANGED (Principle 16)
- No threshold tuning to make the test pass
- If any validation fails, we diagnose honestly and do not rewrite
  to hide the finding
- If KAALCURA produces AUROC of 0.52 on AML, we report 0.52 and stop
  before adding unreliable drug predictions to the net

Run
---
    cd ~/INTERCEPTA/round2_aml/code
    python3 build_aml_net_v5_kaalcura.py 2>&1 | tee \\
        ../results/aml_net_v5_build.txt

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
Date:    April 22, 2026
"""
import os
import sys
import json
import pickle
import time
import logging
from pathlib import Path


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
HOME = Path.home()
CODE_ROOT = HOME / 'INTERCEPTA' / 'code'  # where Round 1 KAALCURA lives
ROUND2_ROOT = HOME / 'INTERCEPTA' / 'round2_aml'
DATA_ROOT = ROUND2_ROOT / 'data'
RESULTS_DIR = ROUND2_ROOT / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Round 1 KAALCURA — import path
sys.path.insert(0, str(CODE_ROOT))

# Inputs
SKELETON_PATH = RESULTS_DIR / 'aml_net_skeleton_v2.gpickle'
ANNDATA_PATH = DATA_ROOT / 'vangalen2019' / 'vangalen_aml.h5ad'
BEATAML_ROOT = DATA_ROOT / 'beataml2.0_data-2.0'
BEATAML_EXPR = BEATAML_ROOT / 'beataml_waves1to4_norm_exp_dbgap.txt'
BEATAML_FITS = BEATAML_ROOT / 'beataml_probit_curve_fits_v4_dbgap.txt'
BEATAML_CLIN = BEATAML_ROOT / 'beataml_wv1to4_clinical.xlsx'
BEATAML_DRUG_FAM = BEATAML_ROOT / 'beataml_drug_families.xlsx'

# Outputs
OUT_NET_PATH = RESULTS_DIR / 'aml_net_v5_kaalcura.gpickle'
OUT_SUMMARY = RESULTS_DIR / 'aml_net_v5_summary.json'
OUT_KAALCURA_STATE = RESULTS_DIR / 'kaalcura_aml_state.pkl'
OUT_BEATAML_AXES = RESULTS_DIR / 'beataml_kaalcura_axes.csv'
OUT_VANGALEN_AXES = RESULTS_DIR / 'vangalen_celltype_kaalcura_axes.csv'

# Config
MIN_CV_AUROC_PASS = 0.55  # honest floor for validation
AXIS_INDEPENDENCE_MAX_ABS_R = 0.5  # relaxed vs Round 1's 0.02 (residualization off)
TOP_N_DRUGS = 15
JACCARD_MAX = 0.6


def banner(s):
    print('\n' + '=' * 72)
    print(s)
    print('=' * 72)


def main():
    # ---------------------------------------------------------
    # Dependency check
    # ---------------------------------------------------------
    banner("Step 0: Dependencies and Round 1 KAALCURA import")
    try:
        import numpy as np
        import pandas as pd
        import networkx as nx
        import anndata as ad
        import scipy.sparse as sp
        from scipy import stats
        print(f"  numpy    : {np.__version__}")
        print(f"  pandas   : {pd.__version__}")
        import scipy as _scipy; print(f"  scipy    : {_scipy.__version__}")
        print(f"  networkx : {nx.__version__}")
    except ImportError as e:
        sys.exit(f"MISSING: {e}")

    import numpy as np
    import pandas as pd
    import networkx as nx
    import anndata as ad
    import scipy.sparse as sp
    from scipy import stats

    # Import Round 1 KAALCURA — must NOT be modified
    try:
        from intercepta_kaalcura_v1 import KAALCURA, GENE_SETS
        print(f"  KAALCURA imported from {CODE_ROOT / 'intercepta_kaalcura_v1.py'}")
        print(f"  Gene sets: {list(GENE_SETS.keys())}")
        n_genes_total = sum(len(GENE_SETS[g]['genes']) for g in GENE_SETS)
        print(f"  Total KAALCURA genes: {n_genes_total}")
    except ImportError as e:
        sys.exit(f"Cannot import Round 1 KAALCURA: {e}")

    # Enable logging so KAALCURA's info messages appear
    logging.basicConfig(
        level=logging.INFO,
        format='  [KAALCURA] %(message)s',
    )

    # ---------------------------------------------------------
    # Input verification
    # ---------------------------------------------------------
    banner("Step 0.5: Verify input files exist")
    required = {
        'Round 2.1b skeleton': SKELETON_PATH,
        'Round 2.1c AnnData': ANNDATA_PATH,
        'BeatAML expression': BEATAML_EXPR,
        'BeatAML curve fits': BEATAML_FITS,
        'BeatAML clinical': BEATAML_CLIN,
        'BeatAML drug families': BEATAML_DRUG_FAM,
    }
    for label, path in required.items():
        if not path.exists():
            sys.exit(f"MISSING: {label}: {path}")
        size_mb = path.stat().st_size / (1024 * 1024)
        print(f"  [OK] {label:25s} {size_mb:>8.1f} MB  {path}")

    # ---------------------------------------------------------
    # STEP 1: Load BeatAML bulk RNA-seq and fit KAALCURA reference
    # ---------------------------------------------------------
    banner("Step 1: Load BeatAML RNA-seq, fit KAALCURA reference")
    print("  Loading BeatAML normalized expression (281 MB, ~30 sec)...")
    t0 = time.time()
    # BeatAML norm_exp format: first column = gene, remaining columns = samples
    beataml_expr_raw = pd.read_csv(BEATAML_EXPR, sep='\t', low_memory=False)
    print(f"    Raw shape: {beataml_expr_raw.shape}  ({time.time()-t0:.1f}s)")
    print(f"    First columns: {list(beataml_expr_raw.columns[:5])}")

    # Detect gene column and pivot
    gene_col_candidates = [c for c in beataml_expr_raw.columns
                           if c.lower() in ('gene', 'gene_symbol', 'symbol',
                                            'display_label', 'hgnc_symbol',
                                            'stable_id', 'gene_id')]
    if not gene_col_candidates:
        # BeatAML uses 'display_label' for gene symbol in some releases
        gene_col_candidates = [beataml_expr_raw.columns[0]]
    gene_col = gene_col_candidates[0]
    print(f"    Using gene column: '{gene_col}'")

    # Identify sample columns (dbgap_sample_id numeric-like or starts with patterns)
    non_gene_cols = [c for c in beataml_expr_raw.columns if c != gene_col]
    # Convert: rows = samples, cols = genes
    # First: dedupe genes by taking max (or first) per symbol
    beataml_expr_raw[gene_col] = beataml_expr_raw[gene_col].astype(str).str.upper()
    beataml_expr_raw = beataml_expr_raw.dropna(subset=[gene_col])
    beataml_expr_raw = beataml_expr_raw[beataml_expr_raw[gene_col] != 'NAN']

    # In case of duplicate gene symbols, take max expression per sample
    beataml_wide = beataml_expr_raw.groupby(gene_col)[non_gene_cols].max()
    # Transpose to samples x genes
    beataml_df = beataml_wide.T  # samples (rows) x genes (cols)
    print(f"    After dedupe/transpose: {beataml_df.shape} (samples x genes)")
    print(f"    Sample ID examples: {list(beataml_df.index[:3])}")
    print(f"    Gene symbol examples: {list(beataml_df.columns[:10])}")

    # Check KAALCURA gene coverage
    kaalcura_genes = set()
    for axis_name, axis_info in GENE_SETS.items():
        kaalcura_genes.update(axis_info['genes'])
    available = kaalcura_genes & set(beataml_df.columns)
    print(f"    KAALCURA gene coverage in BeatAML: {len(available)}/{len(kaalcura_genes)} "
          f"({100*len(available)/len(kaalcura_genes):.1f}%)")

    if len(available) / len(kaalcura_genes) < 0.5:
        sys.exit("FATAL: <50% KAALCURA gene coverage in BeatAML")

    # Fit KAALCURA with tissue_labels=None (single tissue = bone marrow)
    print("  Fitting KAALCURA reference (residualization OFF, single-tissue AML)...")
    t0 = time.time()
    kaalcura = KAALCURA(random_state=42)
    kaalcura.fit_reference(beataml_df, tissue_labels=None)
    print(f"  Reference fit in {time.time()-t0:.1f}s")

    # ---------------------------------------------------------
    # STEP 2: Compute axes per BeatAML sample
    # ---------------------------------------------------------
    banner("Step 2: Compute KAALCURA axes per BeatAML sample")
    t0 = time.time()
    beataml_axes = kaalcura.compute_axes(beataml_df, residualize=False)
    print(f"  Computed axes for {beataml_axes.shape[0]} samples in {time.time()-t0:.1f}s")
    print(f"\n  Axis summary statistics:")
    print(beataml_axes.describe().round(3).to_string())

    # Save BeatAML axes for future use
    beataml_axes.to_csv(OUT_BEATAML_AXES)
    print(f"\n  Saved: {OUT_BEATAML_AXES}")

    # Axis independence check on BeatAML
    print(f"\n  Pairwise Pearson correlations among axes (BeatAML):")
    axis_corr = beataml_axes.corr()
    print(axis_corr.round(3).to_string())

    # ---------------------------------------------------------
    # STEP 3: Train drug response models on BeatAML AUC
    # ---------------------------------------------------------
    banner("Step 3: Train drug response models on BeatAML AUC")
    print("  Loading BeatAML curve fits for drug sensitivity matrix...")
    t0 = time.time()
    fits = pd.read_csv(BEATAML_FITS, sep='\t', low_memory=False)
    print(f"    Raw rows: {len(fits):,}  ({time.time()-t0:.1f}s)")
    fits_ok = fits[fits['paper_inclusion'] & fits['converged'] &
                   (fits['curve_type'] == 'decreasing') & (~fits['all_gt_50']) &
                   (fits['type'] == 'single-agent')].copy()
    print(f"    After QC filters: {len(fits_ok):,}")

    # We need sample-level drug response. BeatAML curve_fits is per
    # (dbgap_sample_id, inhibitor). Our expression is indexed by some
    # sample identifier — need to match.
    # BeatAML norm_exp columns are 'dbgap_sample_id' values (as strings)
    # curve_fits.dbgap_sample_id is the join key
    print(f"    curve_fits sample examples: {fits_ok['dbgap_sample_id'].dropna().astype(str).head(3).tolist()}")
    print(f"    expression index examples:  {list(beataml_df.index[:3])}")

    # Normalize both to string
    fits_ok['_sid'] = fits_ok['dbgap_sample_id'].astype(str)
    beataml_df.index = beataml_df.index.astype(str)
    overlap = set(fits_ok['_sid']) & set(beataml_df.index)
    print(f"    Sample overlap: {len(overlap)} (curve_fits <-> expression)")

    if len(overlap) < 50:
        sys.exit(f"FATAL: Only {len(overlap)} samples overlap between BeatAML "
                 "expression and drug response — not enough for training")

    # Build drug sensitivity matrix: samples x drugs, values = AUC
    fits_ok_joined = fits_ok[fits_ok['_sid'].isin(overlap)]
    drug_matrix = fits_ok_joined.pivot_table(
        index='_sid',
        columns='inhibitor',
        values='auc',
        aggfunc='median'
    )
    print(f"    Drug sensitivity matrix: {drug_matrix.shape}")

    # Restrict axes to overlap samples
    axes_overlap = beataml_axes.loc[list(overlap & set(beataml_axes.index))]
    drug_matrix_overlap = drug_matrix.loc[list(set(axes_overlap.index) & set(drug_matrix.index))]
    axes_final = axes_overlap.loc[drug_matrix_overlap.index]
    print(f"    Final training set: {axes_final.shape[0]} samples, "
          f"{drug_matrix_overlap.shape[1]} drugs")

    # Train drug models via KAALCURA's built-in method
    # Note: BeatAML uses AUC (lower = more potent) like log(IC50).
    # KAALCURA's train_drug_models binarizes "below threshold = sensitive",
    # so AUC fits the same convention.
    print("  Training drug models (CV=5, binarize at median per drug)...")
    t0 = time.time()
    drug_models = kaalcura.train_drug_models(
        axes_final, drug_matrix_overlap,
        ic50_threshold='median', n_cv_folds=5
    )
    print(f"  Trained {len(drug_models)} drug models in {time.time()-t0:.1f}s")

    # Compute mean CV-AUROC
    auroc_values = [info['auroc'] for info in drug_models.values()]
    mean_auroc = float(np.mean(auroc_values)) if auroc_values else 0.0
    median_auroc = float(np.median(auroc_values)) if auroc_values else 0.0
    print(f"\n  Mean CV-AUROC:   {mean_auroc:.3f}")
    print(f"  Median CV-AUROC: {median_auroc:.3f}")
    print(f"  Drugs with AUROC >= 0.60: "
          f"{sum(1 for a in auroc_values if a >= 0.60)}/{len(auroc_values)}")

    # ---------------------------------------------------------
    # STEP 4: Compute Van Galen cell-type pseudobulks + axes + drug pred
    # ---------------------------------------------------------
    banner("Step 4: Van Galen cell-type pseudobulk + KAALCURA + drug prediction")
    print("  Loading Van Galen AnnData...")
    t0 = time.time()
    adata = ad.read_h5ad(str(ANNDATA_PATH))
    print(f"    {adata.n_obs:,} cells x {adata.n_vars:,} genes  ({time.time()-t0:.1f}s)")

    # Pseudobulk: mean expression per cell type
    adata.obs['CellType'] = adata.obs['CellType'].astype('category')
    celltypes = list(adata.obs['CellType'].cat.categories)
    print(f"    Cell types: {len(celltypes)}")

    pseudobulk = {}
    X = adata.X
    if not sp.issparse(X):
        X = sp.csr_matrix(X)

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

    # KAALCURA coverage check on Van Galen
    vg_coverage = len(set(pseudobulk_df.columns) & kaalcura_genes) / len(kaalcura_genes)
    print(f"    KAALCURA gene coverage in Van Galen: {vg_coverage:.1%}")

    # Compute axes for cell-type pseudobulks
    print("  Computing KAALCURA axes per cell type...")
    t0 = time.time()
    vangalen_axes = kaalcura.compute_axes(pseudobulk_df, residualize=False)
    print(f"  Computed in {time.time()-t0:.1f}s")
    print(f"\n  Van Galen cell-type axes:")
    print(vangalen_axes.round(3).to_string())
    vangalen_axes.to_csv(OUT_VANGALEN_AXES)

    # Predict drug sensitivity for each cell type
    print(f"\n  Predicting drug sensitivity per cell type...")
    drug_list = list(drug_models.keys())
    celltype_drug_pred = kaalcura.predict_sensitivity_multi_drug(
        vangalen_axes, drug_list
    )
    print(f"  Predicted sensitivity: {celltype_drug_pred.shape[0]} cell types "
          f"x {celltype_drug_pred.shape[1]} drugs")

    # ---------------------------------------------------------
    # STEP 5: Validation queries
    # ---------------------------------------------------------
    banner("Step 5: Validation queries")

    # Q_A: LSC quiescence — HSC-like R_prolif < Mono-like R_prolif
    print("\n  Query A: HSC-like R_prolif < Mono-like R_prolif")
    print("           (Van Galen LSC quiescence finding)")
    hsc_rprolif = vangalen_axes.loc['HSC-like', 'R_prolif']
    mono_rprolif = vangalen_axes.loc['Mono-like', 'R_prolif']
    print(f"    HSC-like R_prolif:  {hsc_rprolif:.3f}")
    print(f"    Mono-like R_prolif: {mono_rprolif:.3f}")
    Q_A_pass = hsc_rprolif < mono_rprolif
    print(f"    Q_A: {'PASS' if Q_A_pass else 'FAIL'}")

    # Q_B: Axis independence on cell-type data
    print(f"\n  Query B: Axis independence (|r| < {AXIS_INDEPENDENCE_MAX_ABS_R}) across cell types")
    ct_axis_corr = vangalen_axes.corr()
    print(ct_axis_corr.round(3).to_string())
    max_abs_r = float(ct_axis_corr.abs().values[
        np.triu_indices(3, k=1)
    ].max())
    print(f"    Max pairwise |r|: {max_abs_r:.3f}")
    Q_B_pass = max_abs_r < AXIS_INDEPENDENCE_MAX_ABS_R
    print(f"    Q_B: {'PASS' if Q_B_pass else 'FAIL'}")

    # Q_C: Mean CV-AUROC
    print(f"\n  Query C: Mean CV-AUROC >= {MIN_CV_AUROC_PASS}")
    print(f"    Mean:   {mean_auroc:.3f}")
    print(f"    Median: {median_auroc:.3f}")
    Q_C_pass = mean_auroc >= MIN_CV_AUROC_PASS
    print(f"    Q_C: {'PASS' if Q_C_pass else 'FAIL'}")

    # Q_D: Prog-like drug sensitivity correlates with FLT3-ITD+ differential
    print(f"\n  Query D: Prog-like predictions correlate with FLT3-ITD+ differential")
    clin = pd.read_excel(BEATAML_CLIN, sheet_name='summary')
    clin_per_patient_flt3 = (
        clin.dropna(subset=['FLT3-ITD'])
            .groupby('dbgap_subject_id')['FLT3-ITD']
            .apply(lambda s: 'positive' if (s == 'positive').any() else 'negative')
    )
    # Match clinical patient to sample via sample mapping
    sample_patient = clin[['dbgap_subject_id', 'dbgap_sample_id']].dropna()
    sample_patient['dbgap_sample_id'] = sample_patient['dbgap_sample_id'].astype(str)
    sample_to_flt3 = {}
    for _, row in sample_patient.iterrows():
        pid = row['dbgap_subject_id']
        if pid in clin_per_patient_flt3.index:
            sample_to_flt3[row['dbgap_sample_id']] = clin_per_patient_flt3[pid]
    print(f"    Samples with FLT3-ITD status: {len(sample_to_flt3)}")

    # Observed: median AUC differential (ITD+ minus ITD-) per drug
    observed_diff = {}
    for drug in drug_list:
        if drug not in drug_matrix_overlap.columns:
            continue
        drug_series = drug_matrix_overlap[drug].dropna()
        itd_plus = [v for sid, v in drug_series.items()
                    if sample_to_flt3.get(sid) == 'positive']
        itd_minus = [v for sid, v in drug_series.items()
                     if sample_to_flt3.get(sid) == 'negative']
        if len(itd_plus) < 5 or len(itd_minus) < 5:
            continue
        # negative diff = ITD+ more potent (lower AUC) than ITD-
        observed_diff[drug] = float(np.median(itd_plus) - np.median(itd_minus))

    # Predicted: Prog-like P(sensitive) per drug (higher = more sensitive)
    progLike_pred = celltype_drug_pred.loc['Prog-like']

    # Align
    common_drugs = [d for d in observed_diff if d in progLike_pred.index]
    if len(common_drugs) < 30:
        print(f"    WARNING: only {len(common_drugs)} aligned drugs for correlation")
    obs_vals = [observed_diff[d] for d in common_drugs]
    # predictions are P(sensitive); higher P means more potent = lower AUC
    # so we expect NEGATIVE correlation between pred P(sensitive) and observed AUC diff
    # (when ITD+ is more sensitive, AUC diff is negative, P(sensitive) is high -> negative corr)
    pred_vals = [float(progLike_pred[d]) for d in common_drugs]
    if len(common_drugs) >= 10:
        rho, p = stats.spearmanr(pred_vals, obs_vals)
        print(f"    {len(common_drugs)} drugs aligned")
        print(f"    Spearman rho: {rho:.3f}, p: {p:.3e}")
        # Negative correlation expected (see reasoning above)
        Q_D_pass = p < 0.05 and rho < 0
    else:
        print(f"    Not enough drugs aligned — cannot test")
        rho, p = float('nan'), float('nan')
        Q_D_pass = False
    print(f"    Q_D: {'PASS' if Q_D_pass else 'FAIL'}")

    # Q_E: distinguishability
    print(f"\n  Query E: HSC-like vs Prog-like drug ranking Jaccard < {JACCARD_MAX}")
    # Rank drugs by P(sensitive) descending
    hsc_top = celltype_drug_pred.loc['HSC-like'].sort_values(ascending=False).head(10).index.tolist()
    prog_top = celltype_drug_pred.loc['Prog-like'].sort_values(ascending=False).head(10).index.tolist()
    hsc_set = set(hsc_top)
    prog_set = set(prog_top)
    intersection = hsc_set & prog_set
    union = hsc_set | prog_set
    jaccard = len(intersection) / len(union) if union else 1.0
    print(f"    HSC-like top 10:  {sorted(hsc_set)}")
    print(f"    Prog-like top 10: {sorted(prog_set)}")
    print(f"    Jaccard: {jaccard:.3f}")
    Q_E_pass = jaccard < JACCARD_MAX
    print(f"    Q_E: {'PASS' if Q_E_pass else 'FAIL'}")

    # ---------------------------------------------------------
    # Verdict
    # ---------------------------------------------------------
    banner("Step 6: Verdict")
    results_table = [
        ("Q_A (LSC quiescence)",          Q_A_pass),
        ("Q_B (axis independence)",       Q_B_pass),
        ("Q_C (mean CV-AUROC >= 0.55)",   Q_C_pass),
        ("Q_D (Prog-FLT3 correlation)",   Q_D_pass),
        ("Q_E (distinguishability)",      Q_E_pass),
    ]
    for name, passed in results_table:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
    all_pass = all(p for _, p in results_table)
    verdict = 'PASS' if all_pass else 'FAIL'
    print(f"\n  VERDICT: {verdict}")

    # Summary (saved regardless of pass/fail for diagnostic)
    summary = {
        'verdict': verdict,
        'mechanism': 'KAALCURA per cell-type pseudobulk, trained on BeatAML AUC',
        'training_stats': {
            'n_beataml_samples_train': int(axes_final.shape[0]),
            'n_drugs_trained': len(drug_models),
            'mean_cv_auroc': mean_auroc,
            'median_cv_auroc': median_auroc,
            'n_drugs_auroc_ge_0.60': sum(1 for a in auroc_values if a >= 0.60),
        },
        'beataml_axis_stats': beataml_axes.describe().to_dict(),
        'vangalen_axis_per_celltype': vangalen_axes.to_dict(orient='index'),
        'axis_correlations_vangalen': ct_axis_corr.to_dict(),
        'queries': {
            'Q_A_LSC_quiescence': {
                'hsc_like_rprolif': float(hsc_rprolif),
                'mono_like_rprolif': float(mono_rprolif),
                'pass': bool(Q_A_pass),
            },
            'Q_B_axis_independence': {
                'max_abs_r': max_abs_r,
                'pass': bool(Q_B_pass),
            },
            'Q_C_mean_auroc': {
                'mean_auroc': mean_auroc,
                'threshold': MIN_CV_AUROC_PASS,
                'pass': bool(Q_C_pass),
            },
            'Q_D_correlation_prog_flt3': {
                'n_drugs_aligned': int(len(common_drugs)),
                'spearman_rho': float(rho) if not np.isnan(rho) else None,
                'spearman_p': float(p) if not np.isnan(p) else None,
                'pass': bool(Q_D_pass),
            },
            'Q_E_jaccard': {
                'jaccard': float(jaccard),
                'threshold': JACCARD_MAX,
                'hsc_top10': sorted(hsc_set),
                'prog_top10': sorted(prog_set),
                'pass': bool(Q_E_pass),
            },
        },
    }
    with open(OUT_SUMMARY, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  Summary JSON: {OUT_SUMMARY}")

    if not all_pass:
        print(f"\n  Graph NOT saved — validation failed.")
        print(f"  Diagnostic outputs preserved for investigation.")
        sys.exit(3)

    # ---------------------------------------------------------
    # Step 7: Integrate into net and save
    # ---------------------------------------------------------
    banner("Step 7: Integrate Layer 2 and save net")
    with open(SKELETON_PATH, 'rb') as f:
        G = pickle.load(f)
    print(f"  Loaded skeleton: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

    # Add cell-type nodes
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

    # Add drug -> celltype edges via KAALCURA predictions
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

    # Save
    with open(OUT_NET_PATH, 'wb') as f:
        pickle.dump(G, f)
    # Save KAALCURA state for reuse
    try:
        with open(OUT_KAALCURA_STATE, 'wb') as f:
            pickle.dump(kaalcura, f)
        print(f"  Saved KAALCURA fitted state: {OUT_KAALCURA_STATE}")
    except Exception as e:
        print(f"  WARN: couldn't pickle KAALCURA ({e}) — non-fatal")

    size_mb = OUT_NET_PATH.stat().st_size / (1024 * 1024)
    print(f"  Saved net: {OUT_NET_PATH} ({size_mb:.1f} MB)")
    print(f"\n  Round 2.1d v5 complete — Layer 2 integrated via KAALCURA.")


if __name__ == '__main__':
    main()
