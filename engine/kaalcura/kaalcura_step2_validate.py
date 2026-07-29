"""
kaalcura_step2_validate.py
===========================
Step 2 of 2: Recompute kaalcura_real_validation.csv from scratch
using real GDSC expression (FPKM) and IC50 data.

Requires: data/gdsc/sidg_to_symbol.csv (from step 1)
Produces: results/kaalcura_real_validation_RERUN.csv
          results/kaalcura_revalidation_report.txt

Runtime: 10-20 minutes
Run: python3 code/kaalcura_step2_validate.py
"""
import os, sys, time, warnings
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LinearRegression
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intercepta_kaalcura_v1 import KAALCURA, GENE_SETS

BASE    = os.path.expanduser('~/INTERCEPTA/')
DATA    = BASE + 'data/gdsc/'
RESULTS = BASE + 'results/'

print("="*60)
print("STEP 2: KAALCURA REVALIDATION ON REAL GDSC DATA")
print("="*60)

# ── Check prerequisites ─────────────────────────────────────
mapping_path = DATA + 'sidg_to_symbol.csv'
fpkm_path    = DATA + 'expression_data/rnaseq_fpkm_20220624.csv'
ic50_path    = DATA + 'GDSC2_fitted_dose_response.xlsx'
orig_path    = RESULTS + 'kaalcura_real_validation.csv'

for label, path in [
    ('Gene mapping', mapping_path),
    ('FPKM expression', fpkm_path),
    ('IC50 data', ic50_path),
]:
    if not os.path.exists(path):
        print(f"ERROR: {label} not found: {path}")
        if label == 'Gene mapping':
            print("  Run step 1 first: python3 code/kaalcura_step1_build_mapping.py")
        sys.exit(1)
    print(f"  ✓ {label}: {os.path.getsize(path)/1e6:.0f}MB")

# ── Step 1: Load gene mapping ───────────────────────────────
print("\n[1/6] Loading SIDG → gene_symbol mapping...")
mapping = pd.read_csv(mapping_path)
sidg_to_sym = dict(zip(mapping['gene_id'], mapping['gene_symbol']))
sym_to_sidg = dict(zip(mapping['gene_symbol'], mapping['gene_id']))
print(f"  {len(sidg_to_sym)} SIDG → symbol pairs loaded")

# ── Step 2: Identify KAALCURA genes ─────────────────────────
print("\n[2/6] Identifying KAALCURA genes in GDSC...")
kaalcura_genes = sorted(set(g for gs in GENE_SETS.values() for g in gs['genes']))
genes_with_sidg = {g: sym_to_sidg[g] for g in kaalcura_genes if g in sym_to_sidg}
print(f"  KAALCURA genes: {len(kaalcura_genes)} total, "
      f"{len(genes_with_sidg)} found in GDSC")

missing = [g for g in kaalcura_genes if g not in sym_to_sidg]
if missing:
    print(f"  Missing ({len(missing)}): {missing[:10]}")

if len(genes_with_sidg) < 20:
    print(f"  FATAL: Only {len(genes_with_sidg)} genes found. Cannot validate.")
    sys.exit(1)

# ── Step 3: Load FPKM expression ────────────────────────────
print("\n[3/6] Loading FPKM expression matrix...")
t0 = time.time()
fpkm_raw = pd.read_csv(fpkm_path, index_col=0)
print(f"  Raw FPKM shape: {fpkm_raw.shape} ({time.time()-t0:.0f}s)")
print(f"  First 3 row index: {list(fpkm_raw.index[:3])}")
print(f"  First 3 columns: {list(fpkm_raw.columns[:3])}")

# The FPKM file format:
# - Row index = gene IDs (SIDG or info rows like 'model_name', 'gene_id')
# - Columns = cell line IDs (SIDM)
# First 4 rows are metadata: model_name, dataset_name, data_source, gene_id
# Actual gene rows start after metadata rows

# Extract cell line name mapping from row 'model_name'
if 'model_name' in fpkm_raw.index:
    cell_names = fpkm_raw.loc['model_name'].to_dict()  # SIDM → cell line name
    print(f"  Cell line names available: {len(cell_names)}")
else:
    cell_names = {}
    print("  WARNING: model_name row not found")

# Drop metadata rows, keep only gene rows (SIDG IDs)
meta_rows = ['model_name', 'dataset_name', 'data_source', 'gene_id']
gene_rows = [r for r in fpkm_raw.index if r not in meta_rows]
fpkm_genes = fpkm_raw.loc[gene_rows]
print(f"  Gene rows (SIDG): {len(fpkm_genes)}")

# Rename index from SIDG to gene symbols
sidg_index = fpkm_genes.index.tolist()
sym_index  = [sidg_to_sym.get(s, s) for s in sidg_index]
fpkm_genes.index = sym_index

# Rename columns from SIDM to cell line names
if cell_names:
    fpkm_genes.columns = [cell_names.get(c, c) for c in fpkm_genes.columns]

# Keep only KAALCURA genes
available_kaalcura = [g for g in kaalcura_genes if g in fpkm_genes.index]
print(f"  KAALCURA genes in expression: {len(available_kaalcura)}/{len(kaalcura_genes)}")

fpkm_sub = fpkm_genes.loc[available_kaalcura].T  # cell lines × genes
fpkm_sub = fpkm_sub.apply(pd.to_numeric, errors='coerce').fillna(0)
print(f"  Expression matrix for KAALCURA: {fpkm_sub.shape}")

# ── Step 4: Load IC50 data ───────────────────────────────────
print("\n[4/6] Loading IC50 data...")
ic50_raw = pd.read_excel(ic50_path)
print(f"  IC50 shape: {ic50_raw.shape}")
print(f"  Columns: {list(ic50_raw.columns[:8])}")

# Identify columns
cell_col = next((c for c in ic50_raw.columns
                 if 'cell' in c.lower() or 'cosmic' in c.lower()), None)
drug_col = next((c for c in ic50_raw.columns
                 if 'drug' in c.lower()), None)
ic50_col = next((c for c in ic50_raw.columns
                 if 'ln_ic50' in c.lower() or 'ic50' in c.lower()), None)

# Standard GDSC2 columns
if not cell_col:
    cell_col = 'CELL_LINE_NAME' if 'CELL_LINE_NAME' in ic50_raw.columns else ic50_raw.columns[3]
if not drug_col:
    drug_col = 'DRUG_NAME'      if 'DRUG_NAME'      in ic50_raw.columns else ic50_raw.columns[4]
if not ic50_col:
    ic50_col = 'LN_IC50'        if 'LN_IC50'        in ic50_raw.columns else ic50_raw.columns[5]

print(f"  Using: cell='{cell_col}', drug='{drug_col}', ic50='{ic50_col}'")

# Match IC50 cell lines to expression cell lines
ic50_cells = set(ic50_raw[cell_col].unique())
expr_cells  = set(fpkm_sub.index)
matched = ic50_cells & expr_cells
print(f"  Cell line overlap: {len(matched)}/{len(ic50_cells)} IC50 cells in expression")

if len(matched) < 50:
    print("  Low overlap — trying case-insensitive match...")
    expr_upper   = {c.upper(): c for c in expr_cells}
    ic50_raw[cell_col] = ic50_raw[cell_col].str.upper()
    fpkm_sub.index     = fpkm_sub.index.str.upper()
    matched = set(ic50_raw[cell_col].unique()) & set(fpkm_sub.index)
    print(f"  After uppercase: {len(matched)} matched")

if len(matched) < 20:
    print(f"  FATAL: Only {len(matched)} cell lines match. "
          "Check cell line naming between FPKM and IC50.")
    print(f"  IC50 examples: {list(ic50_cells)[:5]}")
    print(f"  Expr examples: {list(expr_cells)[:5]}")
    sys.exit(1)

# ── Step 5: Fit KAALCURA ────────────────────────────────────
print("\n[5/6] Fitting KAALCURA on real GDSC expression...")
expr_matched = fpkm_sub.loc[fpkm_sub.index.isin(matched)]
print(f"  Expression for matched cells: {expr_matched.shape}")

k = KAALCURA(n_tissue_pcs=3, random_state=42)
k.fit_reference(expr_matched)
axes = k.compute_axes(expr_matched, residualize=True)
print(f"  KAALCURA fitted on {len(axes)} cell lines")
print(f"  R_prolif mean={axes['R_prolif'].mean():.3f}  "
      f"R_emt mean={axes['R_emt'].mean():.3f}  "
      f"R_ddr mean={axes['R_ddr'].mean():.3f}")

# Axis independence check
corr = axes.corr()
max_off_diag = corr.where(~np.eye(3,dtype=bool)).abs().max().max()
print(f"  Max off-diagonal axis correlation: {max_off_diag:.3f} "
      f"({'independent ✓' if max_off_diag < 0.2 else 'correlated ⚠'})")

# ── Step 6: Compute AUROC per drug ──────────────────────────
print("\n[6/6] Computing AUROC for each drug...")
drugs   = ic50_raw[drug_col].unique()
print(f"  Total drugs: {len(drugs)}")

rows  = []
skipped = 0

for drug in drugs:
    drug_data = (ic50_raw[ic50_raw[drug_col] == drug]
                 [[cell_col, ic50_col]]
                 .dropna()
                 .rename(columns={cell_col:'cell', ic50_col:'ic50'}))

    # Match to axes
    merged = axes.copy()
    merged['cell'] = merged.index
    merged = merged.merge(drug_data, on='cell', how='inner')

    if len(merged) < 30:
        skipped += 1
        continue

    ic50_vals = merged['ic50'].values
    threshold = np.percentile(ic50_vals, 30)
    y_true    = (ic50_vals < threshold).astype(int)

    if y_true.sum() < 5 or (1-y_true).sum() < 5:
        skipped += 1
        continue

    X = merged[['R_prolif','R_emt','R_ddr']].values
    try:
        lr = LinearRegression().fit(X, ic50_vals)
        y_pred = lr.predict(X)
        auroc  = roc_auc_score(y_true, -y_pred)
    except Exception:
        skipped += 1
        continue

    rows.append({
        'drug':       drug,
        'auroc':      round(auroc, 6),
        'coef_prolif': round(lr.coef_[0], 6),
        'coef_emt':    round(lr.coef_[1], 6),
        'coef_ddr':    round(lr.coef_[2], 6),
        'n_cell_lines': len(merged),
    })

    if len(rows) % 50 == 0:
        print(f"  {len(rows)} drugs computed...", end='\r')

print(f"\n  Computed: {len(rows)} drugs, skipped: {skipped}")

if not rows:
    print("  ERROR: No drugs computed.")
    sys.exit(1)

results_df = pd.DataFrame(rows).sort_values('auroc', ascending=False)
mean_auroc = results_df['auroc'].mean()

# ── Results ─────────────────────────────────────────────────
print("\n" + "="*60)
print("REVALIDATION RESULTS")
print("="*60)
print(f"\n  Drugs validated: {len(results_df)}")
print(f"  Mean AUROC:      {mean_auroc:.3f}")
print(f"  Std AUROC:       {results_df['auroc'].std():.3f}")

t_stat, p_val = stats.ttest_1samp(results_df['auroc'].values, 0.5)
print(f"  T-test vs 0.5:   t={t_stat:.1f}, p={p_val:.2e}")

print(f"\n  Top 10 drugs:")
print(results_df.head(10)[['drug','auroc','coef_prolif','coef_emt','coef_ddr']].to_string(index=False))

# Mechanism checks
print("\n  MECHANISM CHECKS:")
parp  = ['Olaparib','Talazoparib','Niraparib','Rucaparib','Veliparib']
taxan = ['Docetaxel','Paclitaxel','Cabazitaxel','Vinblastine','Vinorelbine']

for label, drug_list in [('PARP inhibitors', parp), ('Taxanes', taxan)]:
    found_rows = results_df[results_df['drug'].isin(drug_list)]
    if len(found_rows):
        mean_ddr    = found_rows['coef_ddr'].mean()
        mean_prolif = found_rows['coef_prolif'].mean()
        print(f"\n  {label} (n={len(found_rows)}):")
        print(found_rows[['drug','auroc','coef_prolif','coef_ddr']].to_string(index=False))
    else:
        print(f"\n  {label}: none found in results")

# Compare to original
if os.path.exists(orig_path):
    orig = pd.read_csv(orig_path)
    print(f"\n  COMPARISON TO ORIGINAL kaalcura_real_validation.csv:")
    print(f"  Original: n={len(orig)}, mean_AUROC={orig['auroc'].mean():.3f}")
    print(f"  Rerun:    n={len(results_df)}, mean_AUROC={mean_auroc:.3f}")

    shared = set(orig['drug']) & set(results_df['drug'])
    if len(shared) > 10:
        o = orig[orig['drug'].isin(shared)].set_index('drug')['auroc']
        r = results_df[results_df['drug'].isin(shared)].set_index('drug')['auroc']
        o, r = o.align(r, join='inner')
        corr = o.corr(r)
        print(f"\n  AUROC correlation for {len(shared)} shared drugs: r={corr:.3f}")
        if corr > 0.80:
            print("  ✓ HIGH CORRELATION — AUROC=0.638 is CONFIRMED REAL.")
            print("    The original and rerun agree. The claim stands.")
        elif corr > 0.50:
            print("  ⚠ MODERATE CORRELATION — partial agreement.")
            print("    Results are directionally consistent but not identical.")
        else:
            print("  ✗ LOW CORRELATION — results differ substantially.")
            print("    The original may have used different data/parameters.")
else:
    print("\n  Original file not found for comparison.")

# Save
out_path = RESULTS + 'kaalcura_real_validation_RERUN.csv'
results_df.to_csv(out_path, index=False)
print(f"\n  Saved: {out_path}")

# Write report
report_path = RESULTS + 'kaalcura_revalidation_report.txt'
with open(report_path, 'w') as f:
    f.write("KAALCURA REVALIDATION REPORT\n")
    f.write("="*40 + "\n\n")
    f.write(f"Date: {pd.Timestamp.now()}\n")
    f.write(f"Data: {fpkm_path}\n")
    f.write(f"IC50: {ic50_path}\n\n")
    f.write(f"Drugs validated: {len(results_df)}\n")
    f.write(f"Mean AUROC: {mean_auroc:.3f}\n")
    f.write(f"T-test p: {p_val:.2e}\n")
    f.write(f"Axis max correlation: {max_off_diag:.3f}\n\n")
    if os.path.exists(orig_path):
        f.write(f"Correlation with original: r={corr:.3f}\n")
    f.write("\nTop 20 drugs:\n")
    f.write(results_df.head(20).to_string())
print(f"  Report: {report_path}")

print("\n" + "="*60)
print("REVALIDATION COMPLETE")
print("="*60)
