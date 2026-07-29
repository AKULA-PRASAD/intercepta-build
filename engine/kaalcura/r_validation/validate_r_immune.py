"""
validate_r_immune.py
====================
Validates R_immune axis — immune engagement axis.

Gene sets already defined in axis_definitions.py:
  CYTOTOXIC:       CD8A, CD8B, GZMA, GZMB, PRF1, NKG7, GNLY, IFNG
  IFN_RESPONSE:    STAT1, IRF1, CXCL9, CXCL10, IDO1, HLA-DRA
  ANTIGEN_PRESENT: HLA-A, HLA-B, HLA-C, B2M, TAP1, TAP2
  IMMUNE_EXCLUSION: TGFB1, VEGFA, IL10  (subtracted)

Formula (from axis_definitions.py):
  S = Z_cytotoxic + Z_ifn + Z_antigen - Z_exclusion
  R_immune = sigmoid(S)

Tests:
  1. Gene correlations in TCGA-PRAD (molecular validation)
  2. Independence from R_prolif and R_emt (all datasets)
  3. Anti-PD1 response prediction in GSE91061 (melanoma)
  4. Domain specificity: R_immune should NOT predict chemotherapy
  5. Pan-cancer state space

Run from: ~/kaalcura/KAALCURA_SUBMISSION/code/
"""

import sys, os, zipfile, gzip
sys.path.insert(0, '.')
sys.path.insert(0, '/Users/kalki/kaalcura')
os.chdir('/Users/kalki/kaalcura/KAALCURA_SUBMISSION/code')

import numpy as np
import pandas as pd
from scipy import stats

from axis_definitions import (compute_r_prolif, compute_r_emt,
                               compute_r_immune, load_geo_matrix,
                               map_probes_to_genes, PROBE_MAP,
                               CYTOTOXIC, IFN_RESPONSE,
                               ANTIGEN_PRESENT, IMMUNE_EXCLUSION, zscore)

DATA = '/Users/kalki/kaalcura/data/'

print("=" * 65)
print("R_immune AXIS VALIDATION")
print("=" * 65)
print(f"CYTOTOXIC:        {CYTOTOXIC}")
print(f"IFN_RESPONSE:     {IFN_RESPONSE}")
print(f"ANTIGEN_PRESENT:  {ANTIGEN_PRESENT}")
print(f"IMMUNE_EXCLUSION: {IMMUNE_EXCLUSION}")

# ═══════════════════════════════════════════════════════════
# 1. TCGA-PRAD — molecular validation + independence
# ═══════════════════════════════════════════════════════════
print("\n[1] TCGA-PRAD molecular validation...")
with gzip.open(DATA + 'tcga_prad_expression.gz', 'rt') as f:
    prad = pd.read_csv(f, sep='\t', index_col=0)
print(f"    Shape: {prad.shape}")

Rp_prad = compute_r_prolif(prad)
Re_prad = compute_r_emt(prad)
Ri_prad = compute_r_immune(prad)

print(f"    R_immune range: {Ri_prad.min():.3f} - {Ri_prad.max():.3f}, mean: {Ri_prad.mean():.3f}")

r_rp, _ = stats.spearmanr(Ri_prad, Rp_prad)
r_re, _ = stats.spearmanr(Ri_prad, Re_prad)
print(f"\n    Independence (TCGA-PRAD):")
print(f"      R_immune vs R_prolif: r={r_rp:.3f}  {'✓' if abs(r_rp)<0.3 else '✗'}")
print(f"      R_immune vs R_emt:    r={r_re:.3f}  {'✓' if abs(r_re)<0.3 else '✗'}")

# Gene-level correlations
print(f"\n    Gene correlations with R_immune:")
all_immune = CYTOTOXIC + IFN_RESPONSE + ANTIGEN_PRESENT + IMMUNE_EXCLUSION
expected = {g: '+' for g in CYTOTOXIC + IFN_RESPONSE + ANTIGEN_PRESENT}
expected.update({g: '-' for g in IMMUNE_EXCLUSION})
expected['MKI67'] = '~'  # should be near zero

check_genes = all_immune + ['MKI67', 'CD8A', 'PD1', 'CD274', 'PDCD1LG2']
print(f"    {'Gene':12s} {'r':>8s}  exp  check")
print(f"    {'-'*40}")
for g in check_genes:
    if g in prad.index:
        r, _ = stats.spearmanr(Ri_prad, prad.loc[g])
        exp = expected.get(g, '?')
        if   exp == '+': chk = '✓' if r > 0.1 else ('~' if r > 0 else '✗')
        elif exp == '-': chk = '✓' if r < -0.1 else ('~' if r < 0 else '✗')
        else:            chk = f'({r:.3f})'
        print(f"    {g:12s} {r:>8.3f}   {exp}    {chk}")
    else:
        print(f"    {g:12s}  NOT FOUND")

# ═══════════════════════════════════════════════════════════
# 2. PAN-CANCER independence
# ═══════════════════════════════════════════════════════════
print("\n[2] PAN-CANCER independence...")
with gzip.open(DATA + 'pancan_expression.gz', 'rt') as f:
    pc = pd.read_csv(f, sep='\t', index_col=0)

Rp_pc = compute_r_prolif(pc)
Re_pc = compute_r_emt(pc)
Ri_pc = compute_r_immune(pc)

r_rp_pc, _ = stats.spearmanr(Ri_pc, Rp_pc)
r_re_pc, _ = stats.spearmanr(Ri_pc, Re_pc)
print(f"    Pan-cancer (n={len(Ri_pc)}):")
print(f"      R_immune vs R_prolif: r={r_rp_pc:.3f}  {'✓ INDEPENDENT' if abs(r_rp_pc)<0.3 else '✗ CORRELATED'}")
print(f"      R_immune vs R_emt:    r={r_re_pc:.3f}  {'✓ INDEPENDENT' if abs(r_re_pc)<0.3 else '✗ CORRELATED'}")

print(f"\n    Key gene correlations (pan-cancer):")
for g in ['CD8A', 'GZMB', 'IFNG', 'CXCL9', 'CXCL10', 'MKI67', 'TGFB1', 'CD274']:
    if g in pc.index:
        r, _ = stats.spearmanr(Ri_pc, pc.loc[g])
        flag = '← KEY: should be near 0' if g == 'MKI67' else ''
        print(f"      {g:10s}: r={r:>7.3f}  {flag}")

# ═══════════════════════════════════════════════════════════
# 3. GSE91061 — anti-PD1 response in melanoma
# ═══════════════════════════════════════════════════════════
print("\n[3] GSE91061 — anti-PD1 melanoma response...")
gse91061_path = DATA + 'scrna/GSE91061_melanoma.txt.gz'

try:
    # Load using load_geo_matrix if it's a series matrix,
    # otherwise load raw expression
    if 'series_matrix' in gse91061_path or not os.path.exists(gse91061_path):
        # Try alternate path
        alt_paths = [
            DATA + 'treatment/GSE91061_series_matrix.txt.gz',
            DATA + 'GSE91061_series_matrix.txt.gz',
        ]
        found_path = None
        for p in alt_paths:
            if os.path.exists(p):
                found_path = p
                break
        if found_path:
            gsm_ids, clinical, expr = load_geo_matrix(found_path)
            gdf = map_probes_to_genes(expr, PROBE_MAP)
            Ri = compute_r_immune(gdf)
            print(f"    Loaded via GEO matrix: {gdf.shape}")
        else:
            raise FileNotFoundError("GSE91061 series matrix not found")
    else:
        # Raw expression file
        with gzip.open(gse91061_path, 'rt') as f:
            first_line = f.readline()
        print(f"    First line: {first_line[:100]}")

        with gzip.open(gse91061_path, 'rt') as f:
            expr91 = pd.read_csv(f, sep='\t', index_col=0)
        print(f"    GSE91061 shape: {expr91.shape}")

        # Determine orientation (genes as rows or columns)
        if expr91.shape[0] > expr91.shape[1]:
            # genes as rows (normal)
            Ri = compute_r_immune(expr91)
        else:
            # genes as columns — transpose
            Ri = compute_r_immune(expr91.T)

        print(f"    R_immune computed for {len(Ri)} samples")

    # Load clinical data for response annotation
    # Try to find response column
    if 'clinical' in dir():
        records = []
        for gsm in gsm_ids:
            if gsm not in Ri.index: continue
            resp = ''
            for k, v in clinical[gsm].items():
                if any(w in k.lower() for w in ['response','respons','benefit','outcome']):
                    resp = v; break
            records.append({'gsm': gsm, 'ri': float(Ri[gsm]), 'response': resp})
        df91 = pd.DataFrame(records)
        print(f"    Clinical records: {len(df91)}")
        print(f"    Response values: {df91['response'].value_counts().to_dict()}")

        # Try to separate responders from non-responders
        resp_vals = df91['response'].str.lower()
        r_mask = resp_vals.str.contains('respond|complete|partial|benefit|yes|cr|pr', na=False)
        nr_mask = resp_vals.str.contains('progress|non.respond|no.benefit|no|pd|sd', na=False)

        responders    = df91[r_mask]['ri']
        nonresponders = df91[nr_mask]['ri']

        print(f"    Responders: {len(responders)}, Non-responders: {len(nonresponders)}")
        if len(responders) >= 5 and len(nonresponders) >= 5:
            u, p = stats.mannwhitneyu(responders, nonresponders, alternative='greater')
            auroc = u / (len(responders) * len(nonresponders))
            print(f"    R_immune AUROC = {auroc:.3f} (p={p:.4f})")
            print(f"    Responder median:     {responders.median():.3f}")
            print(f"    Non-responder median: {nonresponders.median():.3f}")
            if auroc > 0.55:
                print(f"    ✓ R_immune predicts anti-PD1 response direction")
            else:
                print(f"    ✗ R_immune does not predict anti-PD1 response")
        else:
            print(f"    Insufficient response annotations — check field names")
            print(f"    All response values: {df91['response'].unique()[:20]}")
    else:
        print(f"    Clinical data not loaded this way — check file format")

except FileNotFoundError as e:
    print(f"    GSE91061 not found: {e}")
    print(f"    Checking available treatment files...")
    trt_dir = DATA + 'treatment/'
    if os.path.exists(trt_dir):
        files = os.listdir(trt_dir)
        immuno_files = [f for f in files if '91061' in f or 'immun' in f.lower() or 'melanom' in f.lower()]
        print(f"    Available: {files}")
        print(f"    Immuno-related: {immuno_files}")
    else:
        print(f"    Treatment directory not found")

except Exception as e:
    print(f"    Error: {e}")
    import traceback; traceback.print_exc()

# ═══════════════════════════════════════════════════════════
# 4. DOMAIN SPECIFICITY — R_immune should NOT predict chemo
# ═══════════════════════════════════════════════════════════
print("\n[4] GDSC domain specificity test...")
print("    R_immune should NOT predict chemotherapy IC50")
print("    (if it does, it may be confounded with proliferation)")
try:
    with zipfile.ZipFile(f'{DATA}/gdsc_expression.zip', 'r') as z:
        with z.open(z.namelist()[0]) as f:
            gexpr = pd.read_csv(f, sep='\t', index_col=0)
    gexpr = gexpr.drop(columns=['GENE_title'], errors='ignore')

    Ri_gdsc = compute_r_immune(gexpr)
    Rp_gdsc = compute_r_prolif(gexpr)

    r_ri_rp, _ = stats.spearmanr(Ri_gdsc, Rp_gdsc)
    print(f"    R_immune vs R_prolif (GDSC): r={r_ri_rp:.3f}  {'✓ INDEPENDENT' if abs(r_ri_rp)<0.3 else '✗'}")

    resp = pd.read_csv(f'{DATA}/gdsc_response.csv')
    cosmic_to_ri = {}
    for col in gexpr.columns:
        try: cosmic_to_ri[int(col.replace('DATA.',''))] = float(Ri_gdsc[col])
        except: pass
    cosmic_to_rp = {}
    for col in gexpr.columns:
        try: cosmic_to_rp[int(col.replace('DATA.',''))] = float(Rp_gdsc[col])
        except: pass

    chemo_kws = ['paclitaxel','docetaxel','gemcitabine','cisplatin',
                 '5-fluorouracil','oxaliplatin','doxorubicin']

    print(f"\n    {'Drug':25s} {'r(Ri)':>8s} {'r(Rp)':>8s}  specificity")
    print(f"    {'-'*60}")
    for drug in sorted(resp['DRUG_NAME'].unique()):
        if not any(k in str(drug).lower() for k in chemo_kws): continue
        sub = resp[resp['DRUG_NAME']==drug][['COSMIC_ID','LN_IC50']].dropna()
        sub['COSMIC_ID'] = sub['COSMIC_ID'].astype(int)
        sub_ri = sub[sub['COSMIC_ID'].isin(cosmic_to_ri)]
        if len(sub_ri) < 50: continue

        ri_vals = np.array([cosmic_to_ri[c] for c in sub_ri['COSMIC_ID']])
        rp_vals = np.array([cosmic_to_rp[c] for c in sub_ri['COSMIC_ID']])
        ic_vals = sub_ri['LN_IC50'].values

        r_ri, _ = stats.spearmanr(ri_vals, ic_vals)
        r_rp, _ = stats.spearmanr(rp_vals, ic_vals)
        # R_prolif should predict chemo (r<0, high prolif=sensitive=low IC50)
        # R_immune should NOT predict chemo (r~0)
        spec = '✓ specific' if abs(r_ri) < 0.10 else ('~ weak' if abs(r_ri) < 0.20 else '✗ not specific')
        print(f"    {str(drug):25s} {r_ri:>8.3f} {r_rp:>8.3f}  {spec}")

except Exception as e:
    print(f"    Error: {e}")
    import traceback; traceback.print_exc()

# ═══════════════════════════════════════════════════════════
# 5. THREE-AXIS STATE SPACE
# ═══════════════════════════════════════════════════════════
print("\n[5] Three-axis state space (TCGA-PRAD):")
print(f"    R_prolif vs R_immune: r={stats.spearmanr(Rp_prad, Ri_prad)[0]:.3f}")
print(f"    R_prolif vs R_emt:    r={stats.spearmanr(Rp_prad, Re_prad)[0]:.3f}")
print(f"    R_immune vs R_emt:    r={stats.spearmanr(Ri_prad, Re_prad)[0]:.3f}")
print(f"\n    Pan-cancer:")
print(f"    R_prolif vs R_immune: r={stats.spearmanr(Rp_pc, Ri_pc)[0]:.3f}")
print(f"    R_prolif vs R_emt:    r={stats.spearmanr(Rp_pc, Re_pc)[0]:.3f}")
print(f"    R_immune vs R_emt:    r={stats.spearmanr(Ri_pc, Re_pc)[0]:.3f}")

print("\n" + "=" * 65)
print("VERDICT CRITERIA")
print("=" * 65)
print("""
GREEN LIGHT:
  ✓ R_immune vs R_prolif pan-cancer |r| < 0.30
  ✓ CD8A, GZMB, IFNG: positive correlation
  ✓ TGFB1, VEGFA: negative correlation
  ✓ MKI67: near-zero correlation
  ✓ anti-PD1 AUROC > 0.55 in GSE91061
  ✓ Chemo domain specificity: R_immune r~0 for chemo in GDSC
""")
