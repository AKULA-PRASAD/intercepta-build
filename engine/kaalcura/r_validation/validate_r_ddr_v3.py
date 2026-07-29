"""
validate_r_ddr_v3.py
====================
Validates the proliferation-residualized R_ddr axis (v3).
Critical tests:
  1. R_ddr vs R_prolif must be near-zero (orthogonal by construction)
  2. HRR gene residuals must show correct gene-level directions
  3. GDSC PARP inhibitors must show correct sensitivity direction
  4. MKI67 must be near-zero correlation with R_ddr in pan-cancer
"""

import sys, os, zipfile, gzip
sys.path.insert(0, '.')
sys.path.insert(0, '/Users/kalki/kaalcura')
os.chdir('/Users/kalki/kaalcura/KAALCURA_SUBMISSION/code')

import numpy as np
import pandas as pd
from scipy import stats

from axis_definitions import compute_r_prolif, compute_r_emt, zscore
from r_ddr_v3 import compute_r_ddr, get_gene_counts, HRR_RESIDUAL_GENES

DATA = '/Users/kalki/kaalcura/data/'

print("=" * 65)
print("R_ddr v3 VALIDATION — Proliferation-Residualized")
print("=" * 65)
print(f"Method: sigmoid(mean residual of HRR genes after regressing on R_prolif)")
print(f"HRR genes: {HRR_RESIDUAL_GENES}")

# ═══════════════════════════════════════════════════════════
# 1. TCGA-PRAD
# ═══════════════════════════════════════════════════════════
print("\n[1] TCGA-PRAD...")
with gzip.open(DATA + 'tcga_prad_expression.gz', 'rt') as f:
    prad = pd.read_csv(f, sep='\t', index_col=0)

Rp_prad = compute_r_prolif(prad)
Re_prad = compute_r_emt(prad)
Rd_prad = compute_r_ddr(prad, r_prolif=Rp_prad)

found, missing = get_gene_counts(prad)
print(f"  Found: {found['HRR_RESIDUAL']}")
print(f"  Missing: {missing['HRR_RESIDUAL']}")
print(f"  R_ddr range: {Rd_prad.min():.3f} - {Rd_prad.max():.3f}, mean: {Rd_prad.mean():.3f}")

r_rp, _ = stats.spearmanr(Rd_prad, Rp_prad)
r_re, _ = stats.spearmanr(Rd_prad, Re_prad)
print(f"\n  Independence:")
print(f"    R_ddr vs R_prolif: r={r_rp:.4f}  {'✓ ORTHOGONAL' if abs(r_rp)<0.05 else ('✓ INDEPENDENT' if abs(r_rp)<0.15 else '✗ CORRELATED')}")
print(f"    R_ddr vs R_emt:    r={r_re:.4f}  {'✓' if abs(r_re)<0.3 else '✗'}")

# Gene-level validation: check individual HRR gene residual correlations
print(f"\n  Per-gene residual validation:")
rp_z = zscore(Rp_prad)
for gene in HRR_RESIDUAL_GENES:
    if gene in prad.index:
        gene_z = zscore(prad.loc[gene])
        slope, intercept, _, _, _ = stats.linregress(rp_z, gene_z)
        residual = gene_z - (slope * rp_z + intercept)
        r_raw, _  = stats.spearmanr(Rd_prad, gene_z)
        r_res, _  = stats.spearmanr(Rd_prad, residual)
        print(f"    {gene:10s}: raw_r={r_raw:>7.3f} → residual_r={r_res:>7.3f}  slope={slope:.3f}")
    else:
        print(f"    {gene:10s}: NOT FOUND")

# Also check non-HRR genes
print(f"\n  Reference gene checks:")
for g in ['MKI67', 'BRCA1', 'RAD51', 'ATM', 'CHEK1', 'PARP1']:
    if g in prad.index:
        r, _ = stats.spearmanr(Rd_prad, prad.loc[g])
        print(f"    {g:8s}: r={r:>7.3f}")

# ═══════════════════════════════════════════════════════════
# 2. PAN-CANCER — the critical test
# ═══════════════════════════════════════════════════════════
print("\n[2] PAN-CANCER — critical independence test...")
with gzip.open(DATA + 'pancan_expression.gz', 'rt') as f:
    pc = pd.read_csv(f, sep='\t', index_col=0)

Rp_pc = compute_r_prolif(pc)
Re_pc = compute_r_emt(pc)
Rd_pc = compute_r_ddr(pc, r_prolif=Rp_pc)

r_rp_pc, _ = stats.spearmanr(Rd_pc, Rp_pc)
r_re_pc, _ = stats.spearmanr(Rd_pc, Re_pc)
print(f"  Pan-cancer (n={len(Rd_pc)}):")
print(f"    R_ddr vs R_prolif: r={r_rp_pc:.4f}  {'✓ ORTHOGONAL' if abs(r_rp_pc)<0.05 else ('✓ NEAR-ZERO' if abs(r_rp_pc)<0.15 else '✗ STILL CORRELATED')}")
print(f"    R_ddr vs R_emt:    r={r_re_pc:.4f}  {'✓' if abs(r_re_pc)<0.3 else '✗'}")

print(f"\n  Key gene correlations (pan-cancer):")
for g in ['BRCA2', 'PALB2', 'BRIP1', 'FANCA', 'RAD51C', 'MKI67', 'RAD51', 'BRCA1', 'ATM', 'PARP1']:
    if g in pc.index:
        r, _ = stats.spearmanr(Rd_pc, pc.loc[g])
        flag = ''
        if g == 'MKI67':   flag = f'← KEY (v1={0.615:.3f}, v2={0.615:.3f}, want ~0)'
        if g in HRR_RESIDUAL_GENES and r < 0: flag = '← ✗ unexpected'
        if g in HRR_RESIDUAL_GENES and r > 0: flag = '← ✓'
        print(f"    {g:10s}: r={r:>7.3f}  {flag}")

# ═══════════════════════════════════════════════════════════
# 3. GDSC PARP inhibitor sensitivity
# ═══════════════════════════════════════════════════════════
print("\n[3] GDSC PARP inhibitor + platinum sensitivity...")
with zipfile.ZipFile(f'{DATA}/gdsc_expression.zip', 'r') as z:
    with z.open(z.namelist()[0]) as f:
        gexpr = pd.read_csv(f, sep='\t', index_col=0)
gexpr = gexpr.drop(columns=['GENE_title'], errors='ignore')

Rp_gdsc = compute_r_prolif(gexpr)
Rd_gdsc = compute_r_ddr(gexpr, r_prolif=Rp_gdsc)

r_ind_gdsc, _ = stats.spearmanr(Rd_gdsc, Rp_gdsc)
print(f"  GDSC R_ddr range: {Rd_gdsc.min():.3f} - {Rd_gdsc.max():.3f}")
print(f"  R_ddr vs R_prolif: r={r_ind_gdsc:.4f}  {'✓' if abs(r_ind_gdsc)<0.1 else '✗'}")

resp = pd.read_csv(f'{DATA}/gdsc_response.csv')
cosmic_to_rddr = {}
for col in gexpr.columns:
    try:
        cosmic_to_rddr[int(col.replace('DATA.', ''))] = float(Rd_gdsc[col])
    except: pass

parp_kws  = ['olaparib','rucaparib','talazoparib','niraparib','veliparib']
plat_kws  = ['cisplatin','carboplatin','oxaliplatin']
chemo_kws = ['paclitaxel','docetaxel','gemcitabine']

print(f"\n  {'Drug':30s} {'r':>8s} {'p':>10s} {'n':>6s}  type")
print("  " + "-" * 65)

results = []
for drug in sorted(resp['DRUG_NAME'].unique()):
    dl = str(drug).lower()
    is_parp  = any(k in dl for k in parp_kws)
    is_plat  = any(k in dl for k in plat_kws)
    is_chemo = any(k in dl for k in chemo_kws)
    if not (is_parp or is_plat or is_chemo): continue

    sub = resp[resp['DRUG_NAME']==drug][['COSMIC_ID','LN_IC50']].dropna()
    sub['COSMIC_ID'] = sub['COSMIC_ID'].astype(int)
    sub = sub[sub['COSMIC_ID'].isin(cosmic_to_rddr)]
    if len(sub) < 30: continue

    rd_v  = np.array([cosmic_to_rddr[c] for c in sub['COSMIC_ID']])
    ic_v  = sub['LN_IC50'].values
    r, p  = stats.spearmanr(rd_v, ic_v)
    dtype = 'PARP' if is_parp else ('Plat' if is_plat else 'Chemo')
    # Expected: high R_ddr (HRR intact) = high IC50 (resistant) → r > 0
    correct = '✓' if (dtype in ('PARP','Plat') and r > 0) else ('✗' if dtype in ('PARP','Plat') else '~')
    results.append({'drug': drug, 'r': r, 'p': p, 'n': len(sub), 'type': dtype, 'correct': correct})
    print(f"  {str(drug):30s} {r:>8.3f} {p:>10.4f} {len(sub):>6d}  [{dtype}] {correct}")

if results:
    rdf = pd.DataFrame(results)
    for dtype in ['PARP', 'Plat']:
        sub = rdf[rdf['type']==dtype]
        if len(sub):
            correct_pct = (sub['r']>0).mean()*100
            sig_n = ((sub['r']>0)&(sub['p']<0.05)).sum()
            print(f"\n  {dtype}: {correct_pct:.0f}% correct direction, {sig_n}/{len(sub)} significant+correct")

# ═══════════════════════════════════════════════════════════
# 4. SUMMARY
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("SUMMARY")
print("=" * 65)
print(f"  R_ddr vs R_prolif (PRAD):       r={r_rp:.4f}")
print(f"  R_ddr vs R_prolif (pan-cancer): r={r_rp_pc:.4f}")
print(f"  R_ddr vs R_emt    (pan-cancer): r={r_re_pc:.4f}")
print(f"  R_ddr vs R_prolif (GDSC):       r={r_ind_gdsc:.4f}")

print("""
GREEN LIGHT:
  |r| < 0.10 with R_prolif in pan-cancer (orthogonal by construction)
  PARP inhibitors in GDSC: ≥ 60% correct direction
  HRR genes: positive correlation with R_ddr
  MKI67: near-zero correlation with R_ddr
""")
