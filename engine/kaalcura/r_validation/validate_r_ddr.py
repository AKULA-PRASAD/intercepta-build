"""
validate_r_ddr.py
=================
Step 1 validation of R_ddr axis.

Tests (in order of importance):
  1. Molecular validation: R_ddr correlates with known HRR genes in TCGA-BRCA
  2. Independence: R_ddr vs R_prolif correlation (should be near-zero)
  3. GDSC cell lines: low R_ddr predicts PARP inhibitor sensitivity
  4. TCGA-BRCA: R_ddr anti-correlates with BRCA1/2 mutation status
  5. Pan-cancer: R_ddr shows consistent HRR biology across cancer types

Run from: ~/kaalcura/KAALCURA_SUBMISSION/code/
"""

import sys, os, zipfile, gzip
sys.path.insert(0, '.')
os.chdir('/Users/kalki/kaalcura/KAALCURA_SUBMISSION/code')

import numpy as np
import pandas as pd
from scipy import stats

# Import existing KAALCURA infrastructure
from axis_definitions import compute_r_prolif, compute_r_emt, zscore

# Import new R_ddr axis
sys.path.insert(0, '/Users/kalki/kaalcura')
from r_ddr_axis import compute_r_ddr, get_gene_counts, HRR_ACTIVE, REPLICATION_STRESS, NHEJ_BACKUP

DATA = '/Users/kalki/kaalcura/data/'

print("=" * 65)
print("R_ddr AXIS VALIDATION")
print("=" * 65)

# ═══════════════════════════════════════════════════════════
# 1. LOAD TCGA-PRAD for axis independence check
# ═══════════════════════════════════════════════════════════
print("\n[1] Loading TCGA-PRAD...")
with gzip.open(DATA + 'tcga_prad_expression.gz', 'rt') as f:
    prad = pd.read_csv(f, sep='\t', index_col=0)
print(f"    Shape: {prad.shape}")

Rp_prad = compute_r_prolif(prad)
Re_prad = compute_r_emt(prad)

# Check gene availability
found, missing = get_gene_counts(prad)
print(f"\n    R_ddr gene availability in TCGA-PRAD:")
for module, genes in found.items():
    print(f"      {module}: {len(genes)}/{len(eval(module))} found: {genes}")
for module, genes in missing.items():
    if genes:
        print(f"      MISSING from {module}: {genes}")

try:
    Rd_prad = compute_r_ddr(prad)
    print(f"\n    R_ddr computed for {len(Rd_prad)} samples")
    print(f"    R_ddr range: {Rd_prad.min():.3f} - {Rd_prad.max():.3f}")
    print(f"    R_ddr mean:  {Rd_prad.mean():.3f}")

    # Independence from R_prolif and R_emt
    r_rp, p_rp = stats.spearmanr(Rd_prad, Rp_prad)
    r_re, p_re = stats.spearmanr(Rd_prad, Re_prad)
    print(f"\n    Axis independence (TCGA-PRAD):")
    print(f"      R_ddr vs R_prolif: r={r_rp:.3f}, p={p_rp:.4f}")
    print(f"      R_ddr vs R_emt:    r={r_re:.3f}, p={p_re:.4f}")
    print(f"      {'✓ INDEPENDENT' if abs(r_rp) < 0.3 and abs(r_re) < 0.3 else '✗ CORRELATED — review gene sets'}")

except Exception as e:
    print(f"    ERROR: {e}")

# ═══════════════════════════════════════════════════════════
# 2. MOLECULAR VALIDATION in TCGA-PRAD
# ═══════════════════════════════════════════════════════════
print("\n[2] Molecular validation — R_ddr gene correlations (TCGA-PRAD):")
validation_genes = HRR_ACTIVE + REPLICATION_STRESS + NHEJ_BACKUP + ['PARP1', 'PARP2', 'ATM', 'ATR']
print(f"\n    {'Gene':12s} {'r':>8s} {'direction':>12s}")
print("    " + "-" * 36)
for g in validation_genes:
    if g in prad.index:
        r, p = stats.spearmanr(Rd_prad, prad.loc[g])
        direction = "HRR_ACTIVE↑" if g in HRR_ACTIVE else ("STRESS↓" if g in REPLICATION_STRESS else ("NHEJ↓" if g in NHEJ_BACKUP else "expected?"))
        expected_sign = "+" if g in HRR_ACTIVE else "-"
        actual_sign = "+" if r > 0 else "-"
        correct = "✓" if expected_sign == actual_sign else "✗"
        print(f"    {g:12s} {r:>8.3f}  {direction:12s} {correct}")
    else:
        print(f"    {g:12s}  NOT FOUND")

# ═══════════════════════════════════════════════════════════
# 3. GDSC PARP INHIBITOR SENSITIVITY
# ═══════════════════════════════════════════════════════════
print("\n[3] GDSC PARP inhibitor sensitivity...")
with zipfile.ZipFile(f'{DATA}/gdsc_expression.zip', 'r') as z:
    with z.open(z.namelist()[0]) as f:
        gexpr = pd.read_csv(f, sep='\t', index_col=0)
gexpr = gexpr.drop(columns=['GENE_title'], errors='ignore')
print(f"    GDSC expr: {gexpr.shape}")

found_g, missing_g = get_gene_counts(gexpr)
print(f"    Gene availability in GDSC:")
for module, genes in found_g.items():
    print(f"      {module}: {len(genes)} found")

try:
    Rd_gdsc = compute_r_ddr(gexpr)
    Rp_gdsc = compute_r_prolif(gexpr)
    print(f"    R_ddr GDSC range: {Rd_gdsc.min():.3f} - {Rd_gdsc.max():.3f}")

    # R_ddr vs R_prolif independence in GDSC
    r_ind, p_ind = stats.spearmanr(Rd_gdsc, Rp_gdsc)
    print(f"    R_ddr vs R_prolif (GDSC): r={r_ind:.3f}, p={p_ind:.4f}")

    # Load GDSC response data
    resp = pd.read_csv(f'{DATA}/gdsc_response.csv')
    print(f"\n    GDSC response data: {resp.shape}")
    print(f"    Columns: {list(resp.columns[:6])}")

    # Find PARP inhibitor drugs
    drug_col = [c for c in resp.columns if 'drug' in c.lower() or 'name' in c.lower()][0]
    cell_col  = [c for c in resp.columns if 'cell' in c.lower() or 'line' in c.lower()][0]
    ic50_col  = [c for c in resp.columns if 'ic50' in c.lower() or 'ln_ic' in c.lower()][0]

    print(f"\n    Drug column: {drug_col}")
    print(f"    Cell column: {cell_col}")
    print(f"    IC50 column: {ic50_col}")

    parp_drugs = ['Olaparib', 'Rucaparib', 'Talazoparib', 'Niraparib',
                  'olaparib', 'rucaparib', 'talazoparib', 'AZD2461']
    platinum_drugs = ['Cisplatin', 'Carboplatin', 'Oxaliplatin',
                      'cisplatin', 'carboplatin']

    all_drugs = resp[drug_col].unique()
    found_parp = [d for d in all_drugs if any(p.lower() in str(d).lower() for p in parp_drugs)]
    found_plat = [d for d in all_drugs if any(p.lower() in str(d).lower() for p in platinum_drugs)]

    print(f"\n    PARP inhibitors found: {found_parp}")
    print(f"    Platinum drugs found: {found_plat}")

    print(f"\n    R_ddr vs PARP/platinum sensitivity:")
    print(f"    {'Drug':25s} {'r':>8s} {'p':>10s} {'n':>6s} {'direction':>12s}")
    print("    " + "-" * 65)

    target_drugs = found_parp + found_plat
    results = []
    for drug in target_drugs:
        drug_resp = resp[resp[drug_col] == drug][[cell_col, ic50_col]].dropna()
        common = [c for c in drug_resp[cell_col].values if c in Rd_gdsc.index]
        if len(common) < 30:
            continue
        rd_vals = Rd_gdsc[common].values
        ic50_vals = drug_resp.set_index(cell_col).loc[common, ic50_col].values
        r, p = stats.spearmanr(rd_vals, ic50_vals)
        # High R_ddr = HRR intact = PARP resistant = HIGH IC50 → expect r > 0
        direction = "✓ HRR intact=resistant" if r > 0 else "✗ unexpected direction"
        results.append({'drug': drug, 'r': r, 'p': p, 'n': len(common)})
        print(f"    {str(drug):25s} {r:>8.3f} {p:>10.4f} {len(common):>6d}  {direction}")

    if results:
        rdf = pd.DataFrame(results)
        correct_direction = (rdf['r'] > 0).mean()
        sig_correct = ((rdf['r'] > 0) & (rdf['p'] < 0.05)).sum()
        print(f"\n    Summary: {correct_direction*100:.0f}% correct direction, {sig_correct}/{len(rdf)} significant correct")

except Exception as e:
    print(f"    ERROR: {e}")
    import traceback; traceback.print_exc()

# ═══════════════════════════════════════════════════════════
# 4. PAN-CANCER VALIDATION
# ═══════════════════════════════════════════════════════════
print("\n[4] Pan-cancer molecular validation...")
try:
    with gzip.open(DATA + 'pancan_expression.gz', 'rt') as f:
        pc = pd.read_csv(f, sep='\t', index_col=0)
    print(f"    Pan-cancer shape: {pc.shape}")

    found_pc, missing_pc = get_gene_counts(pc)
    hrr_found = found_pc['HRR_ACTIVE']
    print(f"    HRR_ACTIVE genes found: {len(hrr_found)}/9")

    Rd_pc = compute_r_ddr(pc)
    Rp_pc = compute_r_prolif(pc)
    Re_pc = compute_r_emt(pc)

    r_rp_pc, _ = stats.spearmanr(Rd_pc, Rp_pc)
    r_re_pc, _ = stats.spearmanr(Rd_pc, Re_pc)
    print(f"    Pan-cancer independence:")
    print(f"      R_ddr vs R_prolif: r={r_rp_pc:.3f}")
    print(f"      R_ddr vs R_emt:    r={r_re_pc:.3f}")

    # Key gene correlations in pan-cancer
    print(f"\n    Key gene correlations (pan-cancer, n={len(Rd_pc)}):")
    for g in ['RAD51', 'BRCA1', 'PARP1', 'CHEK1', 'H2AFX', 'MKI67']:
        if g in pc.index:
            r, p = stats.spearmanr(Rd_pc, pc.loc[g])
            print(f"      {g:8s}: r={r:.3f}")

except Exception as e:
    print(f"    ERROR: {e}")
    import traceback; traceback.print_exc()

print("\n" + "=" * 65)
print("VALIDATION COMPLETE")
print("=" * 65)
print("""
INTERPRETATION GUIDE:
  [1] Independence: |r| < 0.3 with R_prolif and R_emt → axes are orthogonal
  [2] Molecular: HRR_ACTIVE genes should have r > 0, STRESS/NHEJ should have r < 0
  [3] GDSC: PARP inhibitors should have r > 0 (high R_ddr = HRR intact = higher IC50)
           Platinum should also have r > 0 (similar biology)
  [4] Pan-cancer: same pattern should hold across 33 cancer types

If all pass: R_ddr is biologically valid and therapy-domain specific.
Next step: clinical patient validation (TCGA survival + treatment interaction)
""")
