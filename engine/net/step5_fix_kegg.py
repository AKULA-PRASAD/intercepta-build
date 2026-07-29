"""
INTERCEPTA Step 5 FIX: KEGG mapping corrected + Reactome combined.
"""
import json, urllib.request, urllib.parse, pandas as pd, numpy as np, time, os

start = time.time()
print("=" * 70)
print("INTERCEPTA Step 5 FIX: KEGG (corrected) + Reactome Pathways")
print("=" * 70)

RESULTS = '/Users/kalki/INTERCEPTA/results'

# Load our gene list
mut_freq = pd.read_csv(f'{RESULTS}/step2_mutation_frequencies.csv', index_col=0, header=0)
mut_freq.columns = ['frequency']
top_mutated = mut_freq[mut_freq['frequency'] > 2.0].index.tolist()
known_drivers = ['AR','TP53','PTEN','RB1','BRCA2','BRCA1','ATM','SPOP','FOXA1',
                 'MYC','PIK3CA','CDK12','ERG','TMPRSS2','APC','CTNNB1','NKX3-1',
                 'NCOR1','NCOR2','MDM2','CDK4','CDK6','CCND1','AURKA','EZH2',
                 'PIK3CB','AKT1','MTOR','FGFR1','MET','BRAF','KRAS','RAF1',
                 'MAP2K1','PARP1','PARP2','CHEK1','CHEK2','RAD51','PALB2',
                 'SYP','CHGA','ENO2','NCAM1','SOX2','NR3C1','STAT3','JAK1','JAK2']
all_genes = sorted(set(top_mutated + known_drivers))
print(f"  Genes to map: {len(all_genes)}")

# [1/3] Fix KEGG: build symbol-to-KEGG-ID map
print("\n[1/3] Building KEGG gene symbol map (fixed)...")
url = 'https://rest.kegg.jp/list/hsa'
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=120) as resp:
    lines = resp.read().decode().strip().split('\n')

symbol_to_kegg = {}
for line in lines:
    fields = line.split('\t')
    kid = fields[0]
    last = fields[-1]
    if ';' in last:
        symbol_part = last.split(';')[0]
        symbols = [s.strip() for s in symbol_part.split(',')]
        for s in symbols:
            if s:
                symbol_to_kegg[s] = kid

print(f"  KEGG symbols mapped: {len(symbol_to_kegg)}")

# Download KEGG gene-pathway links
print("  Downloading KEGG gene-pathway links...")
url = 'https://rest.kegg.jp/link/pathway/hsa'
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=120) as resp:
    kegg_links = resp.read().decode().strip().split('\n')

gene_pathway_links = []
for line in kegg_links:
    parts = line.strip().split('\t')
    if len(parts) == 2:
        gene_pathway_links.append((parts[0], parts[1].replace('path:', '')))
print(f"  KEGG gene-pathway links: {len(gene_pathway_links)}")

# Download KEGG pathway names
print("  Downloading KEGG pathway names...")
url = 'https://rest.kegg.jp/list/pathway/hsa'
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=60) as resp:
    pw_lines = resp.read().decode().strip().split('\n')

kegg_pw_names = {}
for line in pw_lines:
    parts = line.strip().split('\t')
    if len(parts) == 2:
        pid = parts[0].replace('path:', '')
        pname = parts[1].replace(' - Homo sapiens (human)', '').strip()
        kegg_pw_names[pid] = pname
print(f"  KEGG pathways: {len(kegg_pw_names)}")

# Map our genes to KEGG pathways
kegg_results = []
mapped_kegg = 0
for gene in all_genes:
    kid = symbol_to_kegg.get(gene, '')
    if not kid:
        continue
    mapped_kegg += 1
    for glink, plink in gene_pathway_links:
        if glink == kid:
            pname = kegg_pw_names.get(plink, plink)
            kegg_results.append({
                'gene': gene, 'pathway_id': plink,
                'pathway_name': pname, 'source': 'KEGG'
            })

kegg_df = pd.DataFrame(kegg_results)
print(f"  Genes mapped to KEGG: {mapped_kegg}/{len(all_genes)}")
print(f"  KEGG gene-pathway edges: {len(kegg_df)}")
print(f"  Unique KEGG pathways: {kegg_df['pathway_id'].nunique() if len(kegg_df)>0 else 0}")

# [2/3] Load existing Reactome data from previous run
print("\n[2/3] Loading Reactome data from previous Step 5...")
prev = pd.read_csv(f'{RESULTS}/step5_gene_pathway_map.csv')
reactome_df = prev[prev['source'] == 'Reactome']
print(f"  Reactome edges (from previous run): {len(reactome_df)}")

# [3/3] Combine
print("\n[3/3] Combining KEGG + Reactome...")
combined = pd.concat([kegg_df, reactome_df], ignore_index=True)
print(f"  Total gene-pathway edges: {len(combined)}")
print(f"  Unique genes: {combined['gene'].nunique()}")
print(f"  Unique pathways: {combined['pathway_id'].nunique()}")
print(f"  From KEGG: {len(kegg_df)}")
print(f"  From Reactome: {len(reactome_df)}")

# Key cancer pathway analysis
print(f"\n  Key mCRPC-relevant KEGG pathways:")
cancer_kw = ['Prostate cancer', 'p53 signaling', 'PI3K-Akt', 'mTOR signaling',
             'Wnt signaling', 'Cell cycle', 'Apoptosis', 'MAPK signaling',
             'Homologous recombination', 'Platinum drug resistance',
             'EGFR tyrosine kinase', 'Endocrine resistance',
             'JAK-STAT', 'Notch', 'Hedgehog', 'DNA replication',
             'Base excision repair', 'Mismatch repair']

for kw in cancer_kw:
    matches = kegg_df[kegg_df['pathway_name'].str.contains(kw, case=False, na=False)]
    if len(matches) > 0:
        genes_in = sorted(matches['gene'].unique())
        print(f"  {kw}: {len(genes_in)} genes -> {genes_in}")

# Escape route analysis with KEGG data
print(f"\n  Escape routes (KEGG-derived):")
for target in ['AR', 'PTEN', 'TP53', 'BRCA2']:
    t_pws = combined[combined['gene'] == target]['pathway_id'].unique()
    if len(t_pws) == 0:
        continue
    shared = combined[combined['pathway_id'].isin(t_pws)]
    others = sorted(set(shared['gene'].unique()) - {target})
    print(f"  {target} shares {len(t_pws)} pathways with {len(others)} genes: {others[:8]}")

# Save
combined.to_csv(f'{RESULTS}/step5_gene_pathway_map.csv', index=False)

print(f"\n{'='*70}")
print(f"STEP 5 FIXED")
print(f"  KEGG: {len(kegg_df)} edges ({kegg_df['gene'].nunique()} genes)")
print(f"  Reactome: {len(reactome_df)} edges ({reactome_df['gene'].nunique()} genes)")
print(f"  Combined: {len(combined)} edges ({combined['gene'].nunique()} genes)")
print(f"  Runtime: {time.time()-start:.0f}s")
print(f"{'='*70}")
