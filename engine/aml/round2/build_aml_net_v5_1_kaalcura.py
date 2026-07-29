#!/usr/bin/env python3
"""
INTERCEPTA Round 2.1d v5.1 — AML Net Integration via KAALCURA-per-cell-type
============================================================================

v5.1 patch (vs v5)
------------------
v5 failed at Step 1 because the BeatAML expression file has FOUR
metadata columns at the front: stable_id, display_label, description,
biotype. v5's column picker chose stable_id (Ensembl IDs), which
KAALCURA's HGNC-symbol-based gene sets don't match (0/48 coverage).

v5.1 fixes the parsing:
  - Gene column = display_label (HGNC symbol, verified by file inspection)
  - Metadata columns to drop = {stable_id, display_label, description, biotype}
  - Sample columns = everything else
  - Drop rows with null/empty display_label
  - Collapse duplicate gene symbols by max

Everything else byte-identical to v5. Same KAALCURA fit, same drug
training on BeatAML AUC, same Van Galen pseudobulk analysis, same five
validation queries, same save criterion.

Principle check on this patch
-----------------------------
Principle 3: should have inspected the file structure before writing
             the parser. The v5 column guesser had stable_id higher
             priority than display_label in my candidate list, so it
             matched first. Lesson: inspect, don't guess.
Principle 16: v5 file preserved on disk for history.

Run
---
    cd ~/INTERCEPTA/round2_aml/code
    python3 build_aml_net_v5_1_kaalcura.py 2>&1 | tee \\
        ../results/aml_net_v5_1_build.txt

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
BEATAML_DRUG_FAM = BEATAML_ROOT / 'beataml_drug_families.xlsx'

OUT_NET_PATH = RESULTS_DIR / 'aml_net_v5_1_kaalcura.gpickle'
OUT_SUMMARY = RESULTS_DIR / 'aml_net_v5_1_summary.json'
OUT_KAALCURA_STATE = RESULTS_DIR / 'kaalcura_aml_state_v5_1.pkl'
OUT_BEATAML_AXES = RESULTS_DIR / 'beataml_kaalcura_axes_v5_1.csv'
OUT_VANGALEN_AXES = RESULTS_DIR / 'vangalen_celltype_kaalcura_axes_v5_1.csv'

MIN_CV_AUROC_PASS = 0.55
AXIS_INDEPENDENCE_MAX_ABS_R = 0.5
TOP_N_DRUGS = 15
JACCARD_MAX = 0.6

# Verified from file inspection: these four columns are metadata, not samples
BEATAML_METADATA_COLS = {'stable_id', 'display_label', 'description', 'biotype'}
BEATAML_GENE_SYMBOL_COL = 'display_label'


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
        print(f"  numpy    : {np.__version__}")
        print(f"  pandas   : {pd.__version__}")
        print(f"  scipy    : {_scipy.__version__}")
        print(f"  networkx : {nx.__version__}")
    except ImportError as e:
        sys.exit(f"MISSING: {e}")

    import numpy as np
    import pandas as pd
    import networkx as nx
    import anndata as ad
    import scipy.sparse as sp
    from scipy import stats

    try:
        from intercepta_kaalcura_v1 import KAALCURA, GENE_SETS
        print(f"  KAALCURA imported from {CODE_ROOT / 'intercepta_kaalcura_v1.py'}")
        print(f"  Gene sets: {list(GENE_SETS.keys())}")
        n_genes_total = sum(len(GENE_SETS[g]['genes']) for g in GENE_SETS)
        print(f"  Total KAALCURA genes: {n_genes_total}")
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
        'BeatAML drug families': BEATAML_DRUG_FAM,
    }
    for label, path in required.items():
        if not path.exists():
            sys.exit(f"MISSING: {label}: {path}")
        size_mb = path.stat().st_size / (1024 * 1024)
        print(f"  [OK] {label:25s} {size_mb:>8.1f} MB")

    # ---------------------------------------------------------
    # STEP 1 (PATCHED): Load BeatAML RNA-seq correctly
    # ---------------------------------------------------------
    banner("Step 1: Load BeatAML RNA-seq (v5.1 corrected parser)")
    print("  Loading BeatAML normalized expression...")
    t0 = time.time()
    beataml_expr_raw = pd.read_csv(BEATAML_EXPR, sep='\t', low_memory=False)
    print(f"    Raw shape: {beataml_expr_raw.shape}  ({time.time()-t0:.1f}s)")
    print(f"    First 4 columns: {list(beataml_expr_raw.columns[:4])}")
    print(f"    Expected metadata columns: {sorted(BEATAML_METADATA_COLS)}")
    print(f"    Gene symbol column: {BEATAML_GENE_SYMBOL_COL}")

    # Verify the metadata columns we expect are actually present
    missing_metadata = BEATAML_METADATA_COLS - set(beataml_expr_raw.columns)
    if missing_metadata:
        sys.exit(f"FATAL: expected metadata columns missing: {missing_metadata}")

    # Sample columns = everything NOT in metadata set
    sample_cols = [c for c in beataml_expr_raw.columns
                   if c not in BEATAML_METADATA_COLS]
    print(f"    Sample columns identified: {len(sample_cols)}")
    print(f"    First 3 sample IDs: {sample_cols[:3]}")
    print(f"    Last 3 sample IDs:  {sample_cols[-3:]}")

    # Use display_label for gene symbols; drop rows with null/empty
    beataml_expr_raw[BEATAML_GENE_SYMBOL_COL] = (
        beataml_expr_raw[BEATAML_GENE_SYMBOL_COL].astype(str).str.strip().str.upper()
    )
    n_before_drop = len(beataml_expr_raw)
    beataml_expr_raw = beataml_expr_raw[
        (beataml_expr_raw[BEATAML_GENE_SYMBOL_COL].notna())
        & (beataml_expr_raw[BEATAML_GENE_SYMBOL_COL] != '')
        & (beataml_expr_raw[BEATAML_GENE_SYMBOL_COL] != 'NAN')
    ]
    n_dropped = n_before_drop - len(beataml_expr_raw)
    if n_dropped:
        print(f"    Dropped {n_dropped} rows with null/empty display_label")

    # Collapse duplicate gene symbols (take max expression per sample)
    beataml_wide = beataml_expr_raw.groupby(BEATAML_GENE_SYMBOL_COL)[sample_cols].max()

    # Transpose: samples x genes
    beataml_df = beataml_wide.T
    print(f"    After dedupe/transpose: {beataml_df.shape} (samples x genes)")
    print(f"    Sample ID examples: {list(beataml_df.index[:3])}")
    print(f"    Gene symbol examples: {list(beataml_df.columns[:10])}")

    # KAALCURA coverage check
    kaalcura_genes = set()
    for axis_name, axis_info in GENE_SETS.items():
        kaalcura_genes.update(axis_info['genes'])
    available = kaalcura_genes & set(beataml_df.columns)
    missing = kaalcura_genes - set(beataml_df.columns)
    coverage = len(available) / len(kaalcura_genes)
    print(f"    KAALCURA gene coverage: {len(available)}/{len(kaalcura_genes)} "
          f"({100*coverage:.1f}%)")
    if missing:
        print(f"    Missing KAALCURA genes: {sorted(missing)}")

    if coverage < 0.5:
        sys.exit(f"FATAL: gene coverage too low ({coverage:.1%})")

    # Fit KAALCURA
    print("  Fitting KAALCURA reference (residualization OFF, single-tissue)...")
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

    beataml_axes.to_csv(OUT_BEATAML_AXES)
    print(f"\n  Saved: {OUT_BEATAML_AXES}")

    print(f"\n  Pairwise Pearson correlations among axes (BeatAML):")
    axis_corr = beataml_axes.corr()
    print(axis_corr.round(3).to_string())

    # ---------------------------------------------------------
    # STEP 3: Train drug response models on BeatAML AUC
    # ---------------------------------------------------------
    banner("Step 3: Train drug response models on BeatAML AUC")
    print("  Loading BeatAML curve fits...")
    t0 = time.time()
    fits = pd.read_csv(BEATAML_FITS, sep='\t', low_memory=False)
    print(f"    Raw rows: {len(fits):,}  ({time.time()-t0:.1f}s)")
    fits_ok = fits[fits['paper_inclusion'] & fits['converged'] &
                   (fits['curve_type'] == 'decreasing') & (~fits['all_gt_50']) &
                   (fits['type'] == 'single-agent')].copy()
    print(f"    After QC filters: {len(fits_ok):,}")

    print(f"    curve_fits sample examples: "
          f"{fits_ok['dbgap_sample_id'].dropna().astype(str).head(3).tolist()}")
    print(f"    expression index examples:  {list(beataml_df.index[:3])}")

    fits_ok['_sid'] = fits_ok['dbgap_sample_id'].astype(str)
    beataml_df.index = beataml_df.index.astype(str)
    overlap = set(fits_ok['_sid']) & set(beataml_df.index)
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
    print(f"    Final training set: {axes_final.shape[0]} samples, "
          f"{drug_matrix_overlap.shape[1]} drugs")

    print("  Training drug models (CV=5, binarize at median per drug)...")
    t0 = time.time()
    drug_models = kaalcura.train_drug_models(
        axes_final, drug_matrix_overlap,
        ic50_threshold='median', n_cv_folds=5
    )
    print(f"  Trained {len(drug_models)} drug models in {time.time()-t0:.1f}s")

    auroc_values = [info['auroc'] for info in drug_models.values()]
    mean_auroc = float(np.mean(auroc_values)) if auroc_values else 0.0
    median_auroc = float(np.median(auroc_values)) if auroc_values else 0.0
    print(f"\n  Mean CV-AUROC:   {mean_auroc:.3f}")
    print(f"  Median CV-AUROC: {median_auroc:.3f}")
    print(f"  Drugs with AUROC >= 0.60: "
          f"{sum(1 for a in auroc_values if a >= 0.60)}/{len(auroc_values)}")

    # ---------------------------------------------------------
    # STEP 4: Van Galen pseudobulk + axes + drug prediction
    # ---------------------------------------------------------
    banner("Step 4: Van Galen pseudobulk + KAALCURA + drug prediction")
    print("  Loading Van Galen AnnData...")
    t0 = time.time()
    adata = ad.read_h5ad(str(ANNDATA_PATH))
    print(f"    {adata.n_obs:,} cells x {adata.n_vars:,} genes  ({time.time()-t0:.1f}s)")

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
    ).T
    print(f"    Pseudobulk matrix: {pseudobulk_df.shape}")

    vg_coverage = len(set(pseudobulk_df.columns) & kaalcura_genes) / len(kaalcura_genes)
    print(f"    KAALCURA gene coverage in Van Galen: {vg_coverage:.1%}")

    print("  Computing KAALCURA axes per cell type...")
    t0 = time.time()
    vangalen_axes = kaalcura.compute_axes(pseudobulk_df, residualize=False)
    print(f"  Computed in {time.time()-t0:.1f}s")
    print(f"\n  Van Galen cell-type axes:")
    print(vangalen_axes.round(3).to_string())
    vangalen_axes.to_csv(OUT_VANGALEN_AXES)

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

    # Q_A
    print("\n  Query A: HSC-like R_prolif < Mono-like R_prolif (LSC quiescence)")
    hsc_rprolif = vangalen_axes.loc['HSC-like', 'R_prolif']
    mono_rprolif = vangalen_axes.loc['Mono-like', 'R_prolif']
    print(f"    HSC-like R_prolif:  {hsc_rprolif:.3f}")
    print(f"    Mono-like R_prolif: {mono_rprolif:.3f}")
    Q_A_pass = hsc_rprolif < mono_rprolif
    print(f"    Q_A: {'PASS' if Q_A_pass else 'FAIL'}")

    # Q_B
    print(f"\n  Query B: Axis independence (|r| < {AXIS_INDEPENDENCE_MAX_ABS_R})")
    ct_axis_corr = vangalen_axes.corr()
    print(ct_axis_corr.round(3).to_string())
    max_abs_r = float(ct_axis_corr.abs().values[np.triu_indices(3, k=1)].max())
    print(f"    Max pairwise |r|: {max_abs_r:.3f}")
    Q_B_pass = max_abs_r < AXIS_INDEPENDENCE_MAX_ABS_R
    print(f"    Q_B: {'PASS' if Q_B_pass else 'FAIL'}")

    # Q_C
    print(f"\n  Query C: Mean CV-AUROC >= {MIN_CV_AUROC_PASS}")
    print(f"    Mean:   {mean_auroc:.3f}")
    print(f"    Median: {median_auroc:.3f}")
    Q_C_pass = mean_auroc >= MIN_CV_AUROC_PASS
    print(f"    Q_C: {'PASS' if Q_C_pass else 'FAIL'}")

    # Q_D
    print(f"\n  Query D: Prog-like predictions correlate with FLT3-ITD+ differential")
    clin = pd.read_excel(BEATAML_CLIN, sheet_name='summary')
    clin_per_patient_flt3 = (
        clin.dropna(subset=['FLT3-ITD'])
            .groupby('dbgap_subject_id')['FLT3-ITD']
            .apply(lambda s: 'positive' if (s == 'positive').any() else 'negative')
    )
    sample_patient = clin[['dbgap_subject_id', 'dbgap_sample_id']].dropna()
    sample_patient['dbgap_sample_id'] = sample_patient['dbgap_sample_id'].astype(str)
    sample_to_flt3 = {}
    for _, row in sample_patient.iterrows():
        pid = row['dbgap_subject_id']
        if pid in clin_per_patient_flt3.index:
            sample_to_flt3[row['dbgap_sample_id']] = clin_per_patient_flt3[pid]
    print(f"    Samples with FLT3-ITD status: {len(sample_to_flt3)}")

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
        observed_diff[drug] = float(np.median(itd_plus) - np.median(itd_minus))

    progLike_pred = celltype_drug_pred.loc['Prog-like']
    common_drugs = [d for d in observed_diff if d in progLike_pred.index]
    if len(common_drugs) < 30:
        print(f"    WARNING: only {len(common_drugs)} aligned drugs")
    obs_vals = [observed_diff[d] for d in common_drugs]
    pred_vals = [float(progLike_pred[d]) for d in common_drugs]
    if len(common_drugs) >= 10:
        rho, p = stats.spearmanr(pred_vals, obs_vals)
        print(f"    {len(common_drugs)} drugs aligned")
        print(f"    Spearman rho: {rho:.3f}, p: {p:.3e}")
        Q_D_pass = p < 0.05 and rho < 0
    else:
        rho, p = float('nan'), float('nan')
        Q_D_pass = False
    print(f"    Q_D: {'PASS' if Q_D_pass else 'FAIL'}")

    # Q_E
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
    print(f"    Jaccard: {jaccard:.3f}")
    Q_E_pass = jaccard < JACCARD_MAX
    print(f"    Q_E: {'PASS' if Q_E_pass else 'FAIL'}")

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

    summary = {
        'verdict': verdict,
        'mechanism': 'KAALCURA per cell-type pseudobulk, trained on BeatAML AUC',
        'version': 'v5.1',
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
        sys.exit(3)

    # ---------------------------------------------------------
    banner("Step 7: Integrate Layer 2 and save net")
    with open(SKELETON_PATH, 'rb') as f:
        G = pickle.load(f)
    print(f"  Loaded skeleton: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

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
    print(f"\n  Round 2.1d v5.1 complete — Layer 2 integrated via KAALCURA.")


if __name__ == '__main__':
    main()
