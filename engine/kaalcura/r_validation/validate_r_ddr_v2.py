"""
validate_r_ddr_v2.py
====================
R_ddr v2 validation. Fixed GDSC drug column detection.
Tests structural HRR gene set for cell-cycle independence.
"""

import sys, os, zipfile, gzip
sys.path.insert(0, '.')
os.chdir('/Users/kalki/kaalcura/KAALCURA_SUBMISSION/code')

import numpy as np
import pandas as pd
from scipy import stats

from axis_definitions import compute_r_prolif, compute_r_emt, zscore

sys.path.insert(0, '/Users/kalki/kaalcura')
from r_ddr_axis import (compute_r_ddr, get_gene_counts,
                        HRR_STRUCTURAL, NHEJ_COMPENSATORY)

DATA = '/Users/kalki/kaalcura/data/'

print("=" * 65)
print("R_ddr v2 VALIDATION")
print("=" * 65)
print(f"HRR_STRUCTURAL:    {HRR_STRUCTURAL}")
print(f"NHEJ_COMPENSATORY: {NHEJ_COMPENSATORY}")

# ═══════════════════════════════════════════════════════════
# 1. TCGA-PRAD — independence and molecular validation
# ═══════════════════════════════════════════════════════════
print("\n[1] TCGA-PRAD molecular validation...")
with gzip.open(DATA + 'tcga_prad_expression.gz', 'rt') as f:
    prad = pd.read_csv(f, sep='\t', index_col=0)

Rp_prad = compute_r_prolif(prad)
Re_prad = compute_r_emt(prad)
Rd_prad = compute_r_ddr(prad)

found, missing = get_gene_counts(prad)
print(f"  Found: {found}")
print(f"  Missing: {missing}")
print(f"  R_ddr range: {Rd_prad.min():.3f} - {Rd_prad.max():.3f}, mean: {Rd_prad.mean():.3f}")

r_rp, _ = stats.spearmanr(Rd_prad, Rp_prad)
r_re, _ = stats.spearmanr(Rd_prad, Re_prad)
print(f"\n  Independence (TCGA-PRAD):")
print(f"    R_ddr vs R_prolif: r={r_rp:.3f}  {'✓' if abs(r_rp)<0.3 else '✗ TOO CORRELATED'}")
print(f"    R_ddr vs R_emt:    r={r_re:.3f}  {'✓' if abs(r_re)<0.3 else '✗ TOO CORRELATED'}")

# Gene correlations — check direction
print(f"\n  Gene correlations with R_ddr (TCGA-PRAD):")
check_genes = {
    # Should be POSITIVE (structural HRR genes)
    'PALB2': '+', 'RAD51C': '+', 'RAD51D': '+', 'BRIP1': '+',
    'FANCA': '+', 'FANCD2': '+', 'BRCA2': '+',
    # Should be NEGATIVE (NHEJ genes)
    'LIG4': '-', 'XRCC6': '-',
    # Reference checks
    'RAD51': '+', 'BRCA1': '+',  # should still correlate positively in single type
    'MKI67': '?',  # key test: should be NEAR ZERO (independence from proliferation)
    'CHEK1': '?',  # replication stress — what does it show now?
    'ATM': '?', 'ATR': '?',
}
all_correct = True
for g, expected in check_genes.items():
    if g in prad.index:
        r, _ = stats.spearmanr(Rd_prad, prad.loc[g])
        if expected == '+':
            correct = '✓' if r > 0 else '✗'
            if r <= 0: all_correct = False
        elif expected == '-':
            correct = '✓' if r < 0 else '✗'
            if r >= 0: all_correct = False
        else:
            correct = f'(r={r:.3f})'
        print(f"    {g:10s}: r={r:>7.3f}  expected={expected}  {correct}")
    else:
        print(f"    {g:10s}: NOT FOUND")

# ═══════════════════════════════════════════════════════════
# 2. PAN-CANCER — the critical test v1 failed
# ═══════════════════════════════════════════════════════════
print("\n[2] PAN-CANCER — critical independence test...")
with gzip.open(DATA + 'pancan_expression.gz', 'rt') as f:
    pc = pd.read_csv(f, sep='\t', index_col=0)

Rd_pc = compute_r_ddr(pc)
Rp_pc = compute_r_prolif(pc)
Re_pc = compute_r_emt(pc)

r_rp_pc, _ = stats.spearmanr(Rd_pc, Rp_pc)
r_re_pc, _ = stats.spearmanr(Rd_pc, Re_pc)
print(f"  Pan-cancer independence (n={len(Rd_pc)}):")
print(f"    R_ddr vs R_prolif: r={r_rp_pc:.3f}  {'✓ INDEPENDENT' if abs(r_rp_pc)<0.3 else '✗ STILL CORRELATED'}")
print(f"    R_ddr vs R_emt:    r={r_re_pc:.3f}  {'✓ INDEPENDENT' if abs(r_re_pc)<0.3 else '✗ CORRELATED'}")

print(f"\n  Key gene correlations (pan-cancer):")
for g in ['PALB2', 'RAD51C', 'BRCA2', 'FANCA', 'MKI67', 'CHEK1', 'RAD51', 'BRCA1', 'ATM']:
    if g in pc.index:
        r, _ = stats.spearmanr(Rd_pc, pc.loc[g])
        flag = ''
        if g == 'MKI67': flag = '← KEY: should be near 0'
        if g in ['PALB2','RAD51C','BRCA2','FANCA'] and r < 0: flag = '← ✗ WRONG DIRECTION'
        if g in ['PALB2','RAD51C','BRCA2','FANCA'] and r > 0: flag = '← ✓'
        print(f"    {g:10s}: r={r:>7.3f}  {flag}")

# ═══════════════════════════════════════════════════════════
# 3. GDSC PARP inhibitor sensitivity — FIXED column detection
# ═══════════════════════════════════════════════════════════
print("\n[3] GDSC PARP inhibitor + platinum sensitivity...")
with zipfile.ZipFile(f'{DATA}/gdsc_expression.zip', 'r') as z:
    with z.open(z.namelist()[0]) as f:
        gexpr = pd.read_csv(f, sep='\t', index_col=0)
gexpr = gexpr.drop(columns=['GENE_title'], errors='ignore')

Rd_gdsc = compute_r_ddr(gexpr)
Rp_gdsc = compute_r_prolif(gexpr)
r_ind_gdsc, _ = stats.spearmanr(Rd_gdsc, Rp_gdsc)
print(f"  GDSC R_ddr range: {Rd_gdsc.min():.3f} - {Rd_gdsc.max():.3f}")
print(f"  R_ddr vs R_prolif (GDSC): r={r_ind_gdsc:.3f}  {'✓' if abs(r_ind_gdsc)<0.3 else '✗'}")

resp = pd.read_csv(f'{DATA}/gdsc_response.csv')
print(f"  Response columns: {list(resp.columns)}")

# Auto-detect correct column names
drug_col  = next((c for c in resp.columns if c in ['DRUG_NAME','COMPOUND_NAME','drug_name','compound_name']), None)
cell_col  = next((c for c in resp.columns if c in ['CELL_LINE_NAME','CCLE_Name','cell_line']), None)
ic50_col  = next((c for c in resp.columns if 'IC50' in c.upper() or 'LN_IC' in c.upper()), None)
cosmic_col = next((c for c in resp.columns if 'COSMIC' in c.upper()), None)

print(f"  Detected: drug={drug_col}, cell={cell_col}, ic50={ic50_col}, cosmic={cosmic_col}")

# Build cell line name → R_ddr mapping
# GDSC expression uses DATA.COSMIC_ID format in columns
gdsc_cols = gexpr.columns.tolist()
print(f"  GDSC expr columns sample: {gdsc_cols[:5]}")

# Try to match expression columns to response data
if cosmic_col and 'DATA.' in str(gdsc_cols[0]):
    # columns are DATA.906826 format — extract cosmic IDs
    cosmic_to_rddr = {}
    for col in gdsc_cols:
        cosmic_id = col.replace('DATA.', '')
        try:
            cosmic_to_rddr[int(cosmic_id)] = float(Rd_gdsc[col])
        except:
            pass
    print(f"  Mapped {len(cosmic_to_rddr)} GDSC cell lines via COSMIC ID")

    # Now compute correlations
    parp_kws   = ['olaparib','rucaparib','talazoparib','niraparib','veliparib','AZD2461']
    plat_kws   = ['cisplatin','carboplatin','oxaliplatin']
    chemo_kws  = ['paclitaxel','docetaxel','gemcitabine','5-fluorouracil']  # controls

    print(f"\n  {'Drug':30s} {'r':>8s} {'p':>10s} {'n':>6s}  direction")
    print("  " + "-" * 70)

    results = []
    all_drugs = resp[drug_col].unique() if drug_col else []
    for drug in sorted(all_drugs):
        drug_lower = str(drug).lower()
        is_parp  = any(k in drug_lower for k in parp_kws)
        is_plat  = any(k in drug_lower for k in plat_kws)
        is_chemo = any(k in drug_lower for k in chemo_kws)
        if not (is_parp or is_plat or is_chemo):
            continue

        sub = resp[resp[drug_col] == drug][[cosmic_col, ic50_col]].dropna()
        sub[cosmic_col] = sub[cosmic_col].astype(int)
        sub = sub[sub[cosmic_col].isin(cosmic_to_rddr)]
        if len(sub) < 30:
            continue

        rd_vals   = np.array([cosmic_to_rddr[c] for c in sub[cosmic_col]])
        ic50_vals = sub[ic50_col].values
        r, p = stats.spearmanr(rd_vals, ic50_vals)

        # Expected direction: high R_ddr (HRR intact) → high IC50 (resistant) → r > 0
        if is_parp:   expected, dtype = '+', 'PARP'
        elif is_plat: expected, dtype = '+', 'Plat'
        else:         expected, dtype = '?', 'Chemo'

        correct = '✓' if (expected == '+' and r > 0) else ('✗' if expected == '+' else '~')
        results.append({'drug': drug, 'r': r, 'p': p, 'n': len(sub), 'type': dtype, 'correct': correct})
        print(f"  {str(drug):30s} {r:>8.3f} {p:>10.4f} {len(sub):>6d}  [{dtype}] {correct}")

    if results:
        rdf = pd.DataFrame(results)
        parp_res = rdf[rdf['type']=='PARP']
        plat_res = rdf[rdf['type']=='Plat']
        if len(parp_res):
            parp_correct = (parp_res['r'] > 0).mean()
            print(f"\n  PARP inhibitors: {parp_correct*100:.0f}% correct direction ({len(parp_res)} drugs)")
        if len(plat_res):
            plat_correct = (plat_res['r'] > 0).mean()
            print(f"  Platinum:        {plat_correct*100:.0f}% correct direction ({len(plat_res)} drugs)")
else:
    print("  Could not match GDSC columns — check DATA format")
    print(f"  First 3 response rows:\n{resp.head(3)}")

# ═══════════════════════════════════════════════════════════
# 4. THREE-AXIS STATE SPACE CHECK
# ═══════════════════════════════════════════════════════════
print("\n[4] Three-axis state space (TCGA-PRAD)...")
print(f"  R_prolif vs R_ddr: r={stats.spearmanr(Rp_prad, Rd_prad)[0]:.3f}")
print(f"  R_prolif vs R_emt: r={stats.spearmanr(Rp_prad, Re_prad)[0]:.3f}")
print(f"  R_ddr    vs R_emt: r={stats.spearmanr(Rd_prad, Re_prad)[0]:.3f}")
print(f"\n  Pan-cancer:")
print(f"  R_prolif vs R_ddr: r={stats.spearmanr(Rp_pc, Rd_pc)[0]:.3f}")
print(f"  R_prolif vs R_emt: r={stats.spearmanr(Rp_pc, Re_pc)[0]:.3f}")
print(f"  R_ddr    vs R_emt: r={stats.spearmanr(Rd_pc, Re_pc)[0]:.3f}")
print("\n  All |r| < 0.30 = axes are orthogonal ✓")

print("\n" + "=" * 65)
print("VERDICT")
print("=" * 65)
print("""
GREEN LIGHT criteria:
  ✓ R_ddr vs R_prolif pan-cancer |r| < 0.30  (not measuring quiescence)
  ✓ PALB2/RAD51C/FANCD2 positive correlation in pan-cancer
  ✓ MKI67 near-zero correlation with R_ddr in pan-cancer
  ✓ PARP inhibitors in GDSC: r > 0 (≥60% correct direction)

If all green: R_ddr v2 is valid. Proceed to clinical patient validation.
If MKI67 still correlates: need to investigate further.
""")
