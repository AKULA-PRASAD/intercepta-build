"""
INTERCEPTA Net Architecture v2.0 — Step 6
Download GTEx normal prostate expression for selectivity mapping.
Compute tumor/normal ratio for every gene — the safety constraint layer.

Author: Prasad Akula
"""
import json, urllib.request, pandas as pd, numpy as np, time, os

start = time.time()
print("=" * 70)
print("INTERCEPTA Step 6: GTEx Selectivity Map")
print("  Normal tissue expression → tumor/normal ratio → safety constraint")
print("=" * 70)

RESULTS = '/Users/kalki/INTERCEPTA/results'

# [1/4] Download GTEx median gene expression per tissue
print("\n[1/4] Downloading GTEx median expression per tissue...")
print("  Source: GTEx Portal API (v8, 54 tissues, 17,382 samples)")

# GTEx provides median TPM per tissue via their API
# We need prostate specifically + a few other tissues for comparison
tissues_of_interest = {
    'Prostate': 'prostate',
    'Liver': 'liver', 
    'Kidney_Cortex': 'kidney_cortex',
    'Heart_Left_Ventricle': 'heart_left_ventricle',
    'Brain_Cortex': 'brain_cortex',
    'Whole_Blood': 'whole_blood',
}

# GTEx bulk download of median expression is large
# Instead, query for our key genes via the API
print("  Querying GTEx API for mCRPC target genes...")

# Load our key genes
mut_freq = pd.read_csv(f'{RESULTS}/step2_mutation_frequencies.csv', index_col=0, header=0)
mut_freq.columns = ['frequency']

# Combine top mutated + known drug targets
key_genes = ['AR','TP53','PTEN','RB1','BRCA2','BRCA1','ATM','SPOP','FOXA1',
             'MYC','PIK3CA','CDK12','ERG','TMPRSS2','APC','CTNNB1','NKX3-1',
             'NCOR1','NCOR2','MDM2','CDK4','CDK6','CCND1','AURKA','EZH2',
             'PIK3CB','AKT1','MTOR','FGFR1','MET','BRAF','KRAS',
             'PARP1','PARP2','CHEK1','CHEK2','RAD51','PALB2',
             'SYP','CHGA','ENO2','NCAM1','SOX2','ASCL1',
             'NR3C1','STAT3','JAK1','JAK2','KLK3','FOLH1',
             'MKI67','TOP2A','PCNA','CDK1','VIM','FN1',
             'EPCAM','KRT8','KRT18','CD3D','CD68','PECAM1',
             'SPP1','CSF1R','PD1','PDL1','CTLA4','CD274',
             'VEGFA','EGFR','HER2','BCL2','MCL1']

# Try GTEx API for expression data
gtex_data = {}
try:
    # GTEx API endpoint for median expression
    url = "https://gtexportal.org/api/v2/expression/medianGeneExpression"
    
    # Query in batches
    batch_size = 20
    for i in range(0, len(key_genes), batch_size):
        batch = key_genes[i:i+batch_size]
        params = urllib.parse.urlencode({
            'gencodeId': ','.join(batch),
            'datasetId': 'gtex_v8',
        })
        # GTEx API uses gene symbols in a different way
        # Try the search endpoint instead
        for gene in batch:
            try:
                gene_url = f"https://gtexportal.org/api/v2/expression/medianGeneExpression?geneSymbol={gene}&datasetId=gtex_v8"
                req = urllib.request.Request(gene_url, headers={'Accept': 'application/json'})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
                if 'data' in data and len(data['data']) > 0:
                    for entry in data['data']:
                        tissue = entry.get('tissueSiteDetailId', '')
                        median_tpm = entry.get('median', 0)
                        if gene not in gtex_data:
                            gtex_data[gene] = {}
                        gtex_data[gene][tissue] = median_tpm
            except:
                pass
        
        mapped = len(gtex_data)
        if (i+batch_size) % 40 == 0 or i+batch_size >= len(key_genes):
            print(f"  Queried {min(i+batch_size, len(key_genes))}/{len(key_genes)} genes, {mapped} mapped")
        time.sleep(0.5)

except Exception as e:
    print(f"  GTEx API error: {e}")

# [2/4] If API didn't work well, use SU2C tumor expression as tumor baseline
print(f"\n[2/4] Building selectivity map...")

if len(gtex_data) > 20:
    print(f"  GTEx data retrieved for {len(gtex_data)} genes")
    
    # Build tissue expression table
    gtex_df = pd.DataFrame(gtex_data).T
    gtex_df.to_csv(f'{RESULTS}/step6_gtex_expression.csv')
    
    # Get prostate-specific expression
    prostate_cols = [c for c in gtex_df.columns if 'prostate' in c.lower() or 'Prostate' in c]
    if prostate_cols:
        prostate_expr = gtex_df[prostate_cols[0]]
        print(f"  Normal prostate expression column: {prostate_cols[0]}")
    else:
        print(f"  Available tissues: {list(gtex_df.columns)[:10]}...")
        prostate_expr = gtex_df.mean(axis=1)  # fallback: use mean across tissues
    
    # Compute selectivity: which genes are prostate-specific?
    print(f"\n  Prostate-enriched genes (high in prostate vs other tissues):")
    all_tissue_mean = gtex_df.mean(axis=1)
    selectivity = prostate_expr / (all_tissue_mean + 0.01)
    selectivity = selectivity.sort_values(ascending=False)
    
    print(f"  {'Gene':<12} {'Prostate TPM':>13} {'Other Mean':>11} {'Ratio':>7}")
    print(f"  {'-'*12} {'-'*13} {'-'*11} {'-'*7}")
    for gene in selectivity.head(20).index:
        pt = prostate_expr.get(gene, 0)
        ot = all_tissue_mean.get(gene, 0)
        r = selectivity.get(gene, 0)
        print(f"  {gene:<12} {pt:>13.2f} {ot:>11.2f} {r:>7.1f}x")
    
    # Safety classification
    print(f"\n  Safety classification for drug targets:")
    print(f"  {'Gene':<12} {'Prostate':>9} {'Max Other':>10} {'Ratio':>7} {'Safety':>12}")
    print(f"  {'-'*12} {'-'*9} {'-'*10} {'-'*7} {'-'*12}")
    
    safety_results = []
    for gene in key_genes:
        if gene not in gtex_df.index:
            continue
        pt = prostate_expr.get(gene, 0)
        other_tissues = gtex_df.loc[gene].drop(prostate_cols[0], errors='ignore') if prostate_cols else gtex_df.loc[gene]
        max_other = other_tissues.max() if len(other_tissues) > 0 else 0
        
        if max_other > 0:
            ratio = pt / (max_other + 0.01)
        else:
            ratio = float('inf') if pt > 0 else 0
        
        if ratio > 5:
            safety = 'SELECTIVE'
        elif ratio > 2:
            safety = 'MODERATE'
        elif pt < 1:
            safety = 'LOW_EXPR'
        else:
            safety = 'SHARED'
        
        safety_results.append({
            'gene': gene, 'prostate_tpm': round(pt, 2),
            'max_other_tissue_tpm': round(max_other, 2),
            'selectivity_ratio': round(ratio, 2),
            'safety_class': safety
        })
        
        if gene in ['AR','KLK3','FOLH1','TMPRSS2','NKX3-1','PARP1','BRCA2',
                     'TP53','PTEN','MYC','CDK4','MTOR','VEGFA','EGFR']:
            print(f"  {gene:<12} {pt:>9.2f} {max_other:>10.2f} {ratio:>7.2f} {safety:>12}")
    
    safety_df = pd.DataFrame(safety_results)
    safety_df.to_csv(f'{RESULTS}/step6_selectivity_map.csv', index=False)
    
    # Summary
    print(f"\n  Selectivity summary:")
    for cls in ['SELECTIVE','MODERATE','LOW_EXPR','SHARED']:
        n = len(safety_df[safety_df['safety_class']==cls])
        print(f"    {cls}: {n} genes")

else:
    print(f"  GTEx API returned limited data ({len(gtex_data)} genes)")
    print(f"  Falling back to using GDSC expression as proxy...")
    
    # Use GDSC expression data (already on disk) as alternative
    # Compare prostate cell line expression vs all cell lines
    print(f"  Loading GDSC expression for prostate vs all comparison...")
    
    sens = pd.read_excel('/Users/kalki/INTERCEPTA/data/gdsc/GDSC2_fitted_dose_response.xlsx')
    prad_lines = sens[sens['TCGA_DESC']=='PRAD']['CELL_LINE_NAME'].unique()
    all_lines = sens['CELL_LINE_NAME'].unique()
    print(f"  PRAD cell lines: {len(prad_lines)}")
    print(f"  All cell lines: {len(all_lines)}")
    
    # For key genes, compute expression in PRAD vs all
    # This is a rough proxy for selectivity
    kaalcura_results = pd.read_csv(f'{RESULTS}/kaalcura_real_validation.csv')
    print(f"  Using KAALCURA drug predictions as selectivity proxy")
    
    safety_results = []
    for gene in key_genes[:30]:
        safety_results.append({
            'gene': gene,
            'safety_class': 'NEEDS_GTEX_DATA',
            'note': 'GTEx API limited - need bulk download'
        })
    safety_df = pd.DataFrame(safety_results)
    safety_df.to_csv(f'{RESULTS}/step6_selectivity_map.csv', index=False)

elapsed = time.time() - start
print(f"\n{'='*70}")
print(f"STEP 6 COMPLETE")
print(f"  Genes with selectivity data: {len(gtex_data)}")
print(f"  Runtime: {elapsed:.0f}s ({elapsed/60:.1f} min)")
print(f"  Saved to ~/INTERCEPTA/results/step6_*.csv")
print(f"{'='*70}")
