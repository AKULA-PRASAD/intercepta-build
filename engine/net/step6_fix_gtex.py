"""
INTERCEPTA Step 6 FIX: Real GTEx selectivity map.
54 normal tissues, 17,382 samples, median TPM per gene per tissue.
"""
import pandas as pd, numpy as np, time
start = time.time()
print("=" * 70)
print("INTERCEPTA Step 6 FIX: Real GTEx Selectivity Map")
print("  54 normal tissues from GTEx v8")
print("=" * 70)

RESULTS = '/Users/kalki/INTERCEPTA/results'

# Load GTEx median TPM (GCT format: skip first 2 header lines)
print("\n[1/4] Loading GTEx median TPM...")
gtex = pd.read_csv('/Users/kalki/INTERCEPTA/data/gtex_median_tpm.gct.gz',
                    sep='\t', skiprows=2, index_col=0, compression='gzip')

# Column 0 = Name (ENSG ID), Column 1 = Description (gene symbol)
# Remaining columns = tissue names
gene_symbols = gtex['Description']
gtex = gtex.drop(columns=['Description'])

# Use gene symbols as index
gtex.index = gene_symbols
# Handle duplicate symbols by taking the max
gtex = gtex.groupby(level=0).max()

print(f"  Genes: {gtex.shape[0]}")
print(f"  Tissues: {gtex.shape[1]}")
print(f"  Tissue names: {list(gtex.columns[:10])}...")

# Find prostate column
prostate_cols = [c for c in gtex.columns if 'prostate' in c.lower() or 'Prostate' in c]
print(f"  Prostate column: {prostate_cols}")

if not prostate_cols:
    print("  Looking for prostate...")
    for c in gtex.columns:
        if 'prost' in c.lower():
            prostate_cols = [c]
            break

prostate_col = prostate_cols[0] if prostate_cols else None

# [2/4] Compute selectivity ratios
print("\n[2/4] Computing selectivity ratios...")
if prostate_col:
    prostate_expr = gtex[prostate_col]
    other_tissues = gtex.drop(columns=[prostate_col])
    other_mean = other_tissues.mean(axis=1)
    other_max = other_tissues.max(axis=1)
    
    # Selectivity = prostate / mean(all other tissues)
    selectivity_vs_mean = (prostate_expr + 0.01) / (other_mean + 0.01)
    # Selectivity = prostate / max(all other tissues) -- stricter
    selectivity_vs_max = (prostate_expr + 0.01) / (other_max + 0.01)
    
    print(f"  Computed ratios for {len(selectivity_vs_mean)} genes")
    
    # Key mCRPC genes
    print("\n[3/4] Key mCRPC target selectivity (REAL GTEx data):")
    print(f"  {'Gene':<12} {'Prostate':>9} {'Other Mean':>11} {'Other Max':>10} {'vs Mean':>8} {'vs Max':>7} {'Safety':>14}")
    print(f"  {'-'*12} {'-'*9} {'-'*11} {'-'*10} {'-'*8} {'-'*7} {'-'*14}")
    
    key_genes = ['KLK3','FOLH1','AR','TMPRSS2','NKX3-1','FOXA1',
                 'TP53','PTEN','RB1','BRCA2','BRCA1','ATM','MYC',
                 'PARP1','PARP2','CDK4','CDK6','MTOR','PIK3CA',
                 'SPOP','CDK12','EZH2','AURKA','CCND1',
                 'VEGFA','EGFR','ERBB2','BCL2','MCL1',
                 'SYP','CHGA','ENO2','NR3C1','STAT3',
                 'KLK2','STEAP2','ACPP','SLC45A3']
    
    results = []
    for gene in key_genes:
        if gene not in prostate_expr.index:
            continue
        pe = prostate_expr[gene]
        om = other_mean[gene]
        ox = other_max[gene]
        r_mean = selectivity_vs_mean[gene]
        r_max = selectivity_vs_max[gene]
        
        if r_mean > 10:
            safety = 'HIGHLY-SELECT'
        elif r_mean > 3:
            safety = 'PROSTATE-SEL'
        elif r_mean > 1.5:
            safety = 'MODERATE'
        elif r_mean < 0.3:
            safety = 'LOW-IN-PROST'
        else:
            safety = 'UBIQUITOUS'
        
        # Which tissue has max expression?
        max_tissue = other_tissues.loc[gene].idxmax() if gene in other_tissues.index else ''
        
        results.append({
            'gene': gene,
            'prostate_tpm': round(pe, 2),
            'other_mean_tpm': round(om, 2),
            'other_max_tpm': round(ox, 2),
            'ratio_vs_mean': round(r_mean, 2),
            'ratio_vs_max': round(r_max, 2),
            'safety_class': safety,
            'max_other_tissue': max_tissue
        })
        
        print(f"  {gene:<12} {pe:>9.2f} {om:>11.2f} {ox:>10.2f} {r_mean:>8.1f}x {r_max:>6.2f}x {safety:>14}")
    
    # [4/4] Full genome selectivity
    print("\n[4/4] Genome-wide selectivity summary...")
    
    # Top prostate-selective genes
    sel_sorted = selectivity_vs_mean.sort_values(ascending=False)
    print(f"\n  Top 20 most prostate-selective genes (GTEx, real normal tissue):")
    print(f"  {'Gene':<15} {'Prostate TPM':>13} {'Other Mean':>11} {'Ratio':>7}")
    print(f"  {'-'*15} {'-'*13} {'-'*11} {'-'*7}")
    for gene in sel_sorted.head(20).index:
        pe = prostate_expr[gene]
        om = other_mean[gene]
        r = sel_sorted[gene]
        if pe > 0.5:  # Skip very low expression genes
            print(f"  {gene:<15} {pe:>13.2f} {om:>11.2f} {r:>7.1f}x")
    
    # Summary counts
    print(f"\n  Selectivity distribution (all {len(selectivity_vs_mean)} genes):")
    print(f"    Highly selective (>10x): {(selectivity_vs_mean > 10).sum()}")
    print(f"    Prostate-selective (3-10x): {((selectivity_vs_mean > 3) & (selectivity_vs_mean <= 10)).sum()}")
    print(f"    Moderate (1.5-3x): {((selectivity_vs_mean > 1.5) & (selectivity_vs_mean <= 3)).sum()}")
    print(f"    Ubiquitous (0.3-1.5x): {((selectivity_vs_mean > 0.3) & (selectivity_vs_mean <= 1.5)).sum()}")
    print(f"    Low in prostate (<0.3x): {(selectivity_vs_mean < 0.3).sum()}")
    
    # Save
    rdf = pd.DataFrame(results)
    rdf.to_csv(f'{RESULTS}/step6_selectivity_map.csv', index=False)
    
    full = pd.DataFrame({
        'prostate_tpm': prostate_expr,
        'other_mean_tpm': other_mean,
        'other_max_tpm': other_max,
        'ratio_vs_mean': selectivity_vs_mean,
        'ratio_vs_max': selectivity_vs_max
    })
    full.to_csv(f'{RESULTS}/step6_full_selectivity.csv')
    
    print(f"\n  Saved {len(rdf)} key targets + {len(full)} full genome selectivity")

elapsed = time.time() - start
print(f"\n{'='*70}")
print(f"STEP 6 FIXED - REAL GTEx DATA")
print(f"  {gtex.shape[0]} genes x {gtex.shape[1]} normal tissues")
print(f"  Runtime: {elapsed:.0f}s")
print(f"{'='*70}")
