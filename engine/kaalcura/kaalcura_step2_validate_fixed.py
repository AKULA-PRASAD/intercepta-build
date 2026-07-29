"""
kaalcura_step2_validate.py  (FIXED)
=====================================
Fixed: IC50 uses CELL_LINE_NAME, not COSMIC_ID for matching.
       Expression uses model_name row for cell line names.

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
print("KAALCURA REVALIDATION ON REAL GDSC DATA (FIXED)")
print("="*60)

mapping_path = DATA + 'sidg_to_symbol.csv'
fpkm_path    = DATA + 'expression_data/rnaseq_fpkm_20220624.csv'
ic50_path    = DATA + 'GDSC2_fitted_dose_response.xlsx'
orig_path    = RESULTS + 'kaalcura_real_validation.csv'

for label, path in [('Gene mapping',mapping_path),
                    ('FPKM expression',fpkm_path),
                    ('IC50 data',ic50_path)]:
    if not os.path.exists(path):
        print(f"ERROR: {label} not found: {path}")
        sys.exit(1)
    print(f"  ✓ {label}: {os.path.getsize(path)/1e6:.0f}MB")

# ── Load gene mapping ───────────────────────────────────────
print("\n[1/6] Loading SIDG → gene_symbol mapping...")
mapping = pd.read_csv(mapping_path)
sidg_to_sym = dict(zip(mapping['gene_id'], mapping['gene_symbol']))
sym_to_sidg = dict(zip(mapping['gene_symbol'], mapping['gene_id']))
print(f"  {len(sidg_to_sym)} pairs loaded")

# ── Identify KAALCURA genes ─────────────────────────────────
print("\n[2/6] Identifying KAALCURA genes in GDSC...")
kaalcura_genes = sorted(set(g for gs in GENE_SETS.values() for g in gs['genes']))
found_genes = [g for g in kaalcura_genes if g in sym_to_sidg]
print(f"  {len(found_genes)}/{len(kaalcura_genes)} KAALCURA genes found")

# ── Load FPKM expression ────────────────────────────────────
print("\n[3/6] Loading FPKM expression matrix...")
t0 = time.time()
fpkm_raw = pd.read_csv(fpkm_path, index_col=0)
print(f"  Raw shape: {fpkm_raw.shape}  ({time.time()-t0:.0f}s)")

# Row 'model_name' contains cell line names for each SIDM column
cell_name_row = fpkm_raw.loc['model_name'] if 'model_name' in fpkm_raw.index else None
if cell_name_row is not None:
    # Map: SIDM_ID → cell_line_name
    sidm_to_name = {sidm: str(name) for sidm, name in cell_name_row.items()
                    if pd.notna(name)}
    print(f"  Cell line names: {len(sidm_to_name)}")

# Drop metadata rows, keep SIDG gene rows
meta_rows = ['model_name','dataset_name','data_source','gene_id']
fpkm_genes = fpkm_raw.drop(index=[r for r in meta_rows if r in fpkm_raw.index])

# Rename row index: SIDG → gene symbol
fpkm_genes.index = [sidg_to_sym.get(s, s) for s in fpkm_genes.index]

# Rename columns: SIDM → cell line name
if cell_name_row is not None:
    fpkm_genes.columns = [sidm_to_name.get(c, c) for c in fpkm_genes.columns]

# Keep KAALCURA genes only
avail = [g for g in kaalcura_genes if g in fpkm_genes.index]
print(f"  KAALCURA genes in matrix: {len(avail)}/{len(kaalcura_genes)}")

# Transpose: cell lines × genes
expr = fpkm_genes.loc[avail].T
expr = expr.apply(pd.to_numeric, errors='coerce').fillna(0)
print(f"  Final expression matrix: {expr.shape}")  # (n_cell_lines, n_genes)
print(f"  Cell line name examples: {list(expr.index[:4])}")

# ── Load IC50 data ──────────────────────────────────────────
print("\n[4/6] Loading IC50 data...")
ic50_raw = pd.read_excel(ic50_path)
print(f"  Shape: {ic50_raw.shape}")
print(f"  Columns: {list(ic50_raw.columns[:10])}")

# Use CELL_LINE_NAME and DRUG_NAME (string columns)
cell_col = 'CELL_LINE_NAME'
drug_col = 'DRUG_NAME'
ic50_col = 'LN_IC50'

# Fallback column detection
if cell_col not in ic50_raw.columns:
    cell_col = next((c for c in ic50_raw.columns if 'cell' in c.lower()), None)
if drug_col not in ic50_raw.columns:
    drug_col = next((c for c in ic50_raw.columns if 'drug' in c.lower()), None)
if ic50_col not in ic50_raw.columns:
    ic50_col = next((c for c in ic50_raw.columns if 'ic50' in c.lower()), None)

print(f"  Using: cell='{cell_col}', drug='{drug_col}', ic50='{ic50_col}'")

# Convert to string for matching
ic50_raw[cell_col] = ic50_raw[cell_col].astype(str).str.strip()
expr.index = expr.index.astype(str).str.strip()

# Check overlap
ic50_cells = set(ic50_raw[cell_col].unique())
expr_cells  = set(expr.index)
matched = ic50_cells & expr_cells
print(f"  Direct match: {len(matched)}/{len(ic50_cells)} IC50 cells in expression")

# Case-insensitive fallback
if len(matched) < 50:
    print("  Trying case-insensitive match...")
    ic50_upper  = {c.upper():c for c in ic50_cells}
    expr_upper  = {c.upper():c for c in expr_cells}
    common_upper = set(ic50_upper) & set(expr_upper)
    # Rebuild ic50 and expr with normalised names
    ic50_raw[cell_col] = ic50_raw[cell_col].str.upper()
    expr.index = expr.index.str.upper()
    matched = set(ic50_raw[cell_col].unique()) & set(expr.index)
    print(f"  After uppercase: {len(matched)} matched")

# Strip/replace common differences (dash vs space etc.)
if len(matched) < 50:
    print("  Trying normalised match (strip dashes/spaces)...")
    def norm(s):
        return str(s).upper().replace('-','').replace(' ','').replace('_','')
    ic50_norm = {norm(c):c for c in set(ic50_raw[cell_col])}
    expr_norm = {norm(c):c for c in expr.index}
    ic50_raw[cell_col] = ic50_raw[cell_col].map(
        lambda x: ic50_norm.get(norm(x), x))
    expr.index = pd.Index([expr_norm.get(norm(c), c) for c in expr.index])
    matched = set(ic50_raw[cell_col].unique()) & set(expr.index)
    print(f"  After normalisation: {len(matched)} matched")

if len(matched) < 20:
    print(f"\n  Too few matches ({len(matched)}).")
    print(f"  IC50 cell examples:  {list(ic50_cells)[:6]}")
    print(f"  Expr cell examples:  {list(expr_cells)[:6]}")
    print("\n  Try matching via SANGER_MODEL_ID (SIDM) if available...")
    if 'SANGER_MODEL_ID' in ic50_raw.columns:
        # Match SIDM IDs directly
        sidm_col = 'SANGER_MODEL_ID'
        # We need to rebuild expr with SIDM index
        # Reload FPKM with SIDM column names
        print("  Rebuilding expression with SIDM cell line IDs...")
        fpkm_raw2 = pd.read_csv(fpkm_path, index_col=0)
        fpkm_sidm = fpkm_raw2.drop(
            index=[r for r in meta_rows if r in fpkm_raw2.index])
        fpkm_sidm.index = [sidg_to_sym.get(s,s) for s in fpkm_sidm.index]
        avail2 = [g for g in kaalcura_genes if g in fpkm_sidm.index]
        expr2 = fpkm_sidm.loc[avail2].T
        expr2 = expr2.apply(pd.to_numeric, errors='coerce').fillna(0)
        ic50_raw[sidm_col] = ic50_raw[sidm_col].astype(str).str.strip()
        expr2.index = expr2.index.astype(str).str.strip()
        matched2 = set(ic50_raw[sidm_col].unique()) & set(expr2.index)
        print(f"  SIDM match: {len(matched2)}")
        if len(matched2) > len(matched):
            expr = expr2
            cell_col = sidm_col
            matched = matched2
            print(f"  Using SIDM matching: {len(matched)} cells")

if len(matched) < 20:
    print(f"FATAL: Only {len(matched)} cell lines matched. Cannot validate.")
    sys.exit(1)

print(f"\n  Final matched cell lines: {len(matched)}")

# ── Fit KAALCURA ────────────────────────────────────────────
print("\n[5/6] Fitting KAALCURA on real GDSC expression...")
expr_matched = expr.loc[expr.index.isin(matched)]
print(f"  Expression for matched cells: {expr_matched.shape}")

k = KAALCURA(n_tissue_pcs=3, random_state=42)
k.fit_reference(expr_matched)
axes = k.compute_axes(expr_matched, residualize=True)
axes['cell'] = axes.index
print(f"  KAALCURA fitted on {len(axes)} cell lines")
print(f"  R_prolif={axes['R_prolif'].mean():.3f}  "
      f"R_emt={axes['R_emt'].mean():.3f}  "
      f"R_ddr={axes['R_ddr'].mean():.3f}")

corr_mat = axes[['R_prolif','R_emt','R_ddr']].corr()
max_corr = corr_mat.where(~np.eye(3,dtype=bool)).abs().max().max()
print(f"  Max axis correlation: {max_corr:.3f} "
      f"({'✓ independent' if max_corr<0.2 else '⚠ correlated'})")

# ── Compute AUROC per drug ──────────────────────────────────
print("\n[6/6] Computing AUROC for each drug...")
drugs   = ic50_raw[drug_col].dropna().unique()
print(f"  Total drugs: {len(drugs)}")

rows, skipped = [], 0
for drug in drugs:
    drug_data = (ic50_raw[ic50_raw[drug_col]==drug]
                 [[cell_col, ic50_col]]
                 .dropna()
                 .rename(columns={cell_col:'cell', ic50_col:'ic50'}))
    merged = axes.merge(drug_data, on='cell', how='inner')
    if len(merged) < 30:
        skipped += 1; continue

    ic50_vals = merged['ic50'].values
    y_true = (ic50_vals < np.percentile(ic50_vals, 30)).astype(int)
    if y_true.sum() < 5 or (1-y_true).sum() < 5:
        skipped += 1; continue

    X = merged[['R_prolif','R_emt','R_ddr']].values
    try:
        lr    = LinearRegression().fit(X, ic50_vals)
        auroc = roc_auc_score(y_true, -lr.predict(X))
    except Exception:
        skipped += 1; continue

    rows.append({'drug':drug, 'auroc':round(auroc,6),
                 'coef_prolif':round(lr.coef_[0],6),
                 'coef_emt':   round(lr.coef_[1],6),
                 'coef_ddr':   round(lr.coef_[2],6),
                 'n_cell_lines':len(merged)})
    if len(rows) % 50 == 0:
        print(f"  {len(rows)} drugs...", end='\r')

print(f"\n  Computed {len(rows)}, skipped {skipped}")
if not rows:
    print("ERROR: No drugs computed."); sys.exit(1)

res = pd.DataFrame(rows).sort_values('auroc', ascending=False)
mean_auroc = res['auroc'].mean()
t_stat, p_val = stats.ttest_1samp(res['auroc'].values, 0.5)

# ── Print results ───────────────────────────────────────────
print("\n" + "="*60)
print("RESULTS")
print("="*60)
print(f"  n_drugs:    {len(res)}")
print(f"  mean_AUROC: {mean_auroc:.3f}")
print(f"  std:        {res['auroc'].std():.3f}")
print(f"  t-test p:   {p_val:.2e}  (vs random 0.5)")
print(f"\n  Top 10:")
print(res.head(10)[['drug','auroc','coef_prolif','coef_emt','coef_ddr']].to_string(index=False))

for label, drug_list in [('PARP inhibitors',
                          ['Olaparib','Talazoparib','Niraparib','Rucaparib','Veliparib']),
                         ('Taxanes',
                          ['Docetaxel','Paclitaxel','Cabazitaxel','Vinblastine','Vinorelbine'])]:
    sub = res[res['drug'].isin(drug_list)]
    if len(sub):
        print(f"\n  {label}:")
        print(sub[['drug','auroc','coef_prolif','coef_ddr']].to_string(index=False))

# Compare to original
if os.path.exists(orig_path):
    orig = pd.read_csv(orig_path)
    shared = set(orig['drug']) & set(res['drug'])
    print(f"\n  COMPARISON TO ORIGINAL:")
    print(f"  Original: n={len(orig)}, mean={orig['auroc'].mean():.3f}")
    print(f"  Rerun:    n={len(res)},  mean={mean_auroc:.3f}")
    if len(shared) > 10:
        o = orig[orig['drug'].isin(shared)].set_index('drug')['auroc']
        r = res[res['drug'].isin(shared)].set_index('drug')['auroc']
        o, r = o.align(r, join='inner')
        corr = o.corr(r)
        print(f"  Shared drugs: {len(shared)}, AUROC correlation r={corr:.3f}")
        if corr > 0.80:
            print("  ✓ HIGH CORRELATION — AUROC=0.638 CONFIRMED REAL.")
        elif corr > 0.50:
            print("  ⚠ MODERATE CORRELATION — directionally consistent.")
        else:
            print("  ✗ LOW CORRELATION — results differ substantially.")

# Save
out = RESULTS + 'kaalcura_real_validation_RERUN.csv'
res.to_csv(out, index=False)
print(f"\n  Saved: {out}")
print("\n" + "="*60)
print("REVALIDATION COMPLETE")
print("="*60)
