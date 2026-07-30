"""
INTERCEPTA Net Architecture v2.0 — Step 5
Download pathway memberships from KEGG + Reactome for all mCRPC genes.
Maps escape routes and pathway crosstalk.

Author: Prasad Akula
"""
import json, urllib.request, urllib.parse, pandas as pd, numpy as np, time, os

start = time.time()
print("=" * 70)
print("INTERCEPTA Step 5: KEGG + Reactome Pathway Mapping")
print("  Pathways, escape routes, crosstalk for mCRPC genes")
print("=" * 70)

RESULTS = '/Users/kalki/INTERCEPTA/results'

# Load key mCRPC genes — use the top mutated + key drivers
print("\n[1/5] Loading mCRPC gene list...")
mut_freq = pd.read_csv(f'{RESULTS}/step2_mutation_frequencies.csv', index_col=0, header=0)
mut_freq.columns = ['frequency']

# Focus on biologically relevant genes (top mutated + known drivers)
top_mutated = mut_freq[mut_freq['frequency'] > 2.0].index.tolist()
known_drivers = ['AR','TP53','PTEN','RB1','BRCA2','BRCA1','ATM','SPOP','FOXA1',
                 'MYC','PIK3CA','CDK12','ERG','TMPRSS2','APC','CTNNB1','NKX3-1',
                 'NCOR1','NCOR2','MDM2','CDK4','CDK6','CCND1','AURKA','EZH2',
                 'PIK3CB','AKT1','MTOR','FGFR1','MET','BRAF','KRAS','RAF1',
                 'MAP2K1','PARP1','PARP2','CHEK1','CHEK2','RAD51','PALB2',
                 'SYP','CHGA','ENO2','SOX2','ASCL1','NEUROD1',
                 'GR','NR3C1','STAT3','JAK1','JAK2']
all_genes = sorted(set(top_mutated + known_drivers))
print(f"  Total genes to map: {len(all_genes)}")

# [2/5] KEGG pathway query
print("\n[2/5] Querying KEGG for pathway memberships...")

# Get human gene-to-pathway mapping from KEGG
kegg_gene_pathway = []
try:
    url = "https://rest.kegg.jp/link/pathway/hsa"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=60) as resp:
        kegg_data = resp.read().decode()
    
    # Parse: each line is "hsa:GENEID\thsa:PATHWAYID"
    for line in kegg_data.strip().split('\n'):
        parts = line.strip().split('\t')
        if len(parts) == 2:
            kegg_gene_pathway.append({
                'kegg_gene': parts[0],
                'kegg_pathway': parts[1]
            })
    print(f"  Total KEGG gene-pathway links: {len(kegg_gene_pathway)}")
except Exception as e:
    print(f"  KEGG link error: {e}")

# Get pathway names
print("  Loading KEGG pathway names...")
kegg_pathways = {}
try:
    url = "https://rest.kegg.jp/list/pathway/hsa"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=60) as resp:
        for line in resp.read().decode().strip().split('\n'):
            parts = line.strip().split('\t')
            if len(parts) == 2:
                pid = parts[0].replace('path:', '')
                pname = parts[1].replace(' - Homo sapiens (human)', '')
                kegg_pathways[pid] = pname
    print(f"  KEGG pathways: {len(kegg_pathways)}")
except Exception as e:
    print(f"  KEGG pathway names error: {e}")

# Map KEGG gene IDs to symbols using KEGG conv
print("  Converting KEGG gene IDs to symbols...")
kegg_id_to_symbol = {}
try:
    url = "https://rest.kegg.jp/conv/hsa/ncbi-geneid"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=120) as resp:
        for line in resp.read().decode().strip().split('\n'):
            parts = line.strip().split('\t')
            if len(parts) == 2:
                kegg_id_to_symbol[parts[1]] = parts[0].replace('ncbi-geneid:', '')
except Exception as e:
    print(f"  KEGG conv error: {e}")

# Now use KEGG symbol lookup
print("  Mapping gene symbols to KEGG IDs...")
symbol_to_kegg = {}
try:
    url = "https://rest.kegg.jp/list/hsa"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=120) as resp:
        for line in resp.read().decode().strip().split('\n'):
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                kid = parts[0]  # hsa:XXXXX
                # Gene symbols are in the description, first semicolon-separated field
                desc = parts[1]
                symbols = desc.split(';')[0].split(',')
                for s in symbols:
                    s = s.strip()
                    if s:
                        symbol_to_kegg[s] = kid
    print(f"  Mapped {len(symbol_to_kegg)} gene symbols to KEGG IDs")
except Exception as e:
    print(f"  Symbol mapping error: {e}")

# Build gene-pathway table for our genes
gene_pathways = []
for gene in all_genes:
    kid = symbol_to_kegg.get(gene, '')
    if not kid:
        continue
    for gp in kegg_gene_pathway:
        if gp['kegg_gene'] == kid:
            pid = gp['kegg_pathway'].replace('path:', '')
            pname = kegg_pathways.get(pid, pid)
            gene_pathways.append({
                'gene': gene, 'pathway_id': pid,
                'pathway_name': pname, 'source': 'KEGG'
            })

kegg_df = pd.DataFrame(gene_pathways)
if len(kegg_df) > 0:
    print(f"  mCRPC genes in KEGG pathways: {kegg_df['gene'].nunique()}")
    print(f"  Pathways containing mCRPC genes: {kegg_df['pathway_id'].nunique()}")
else:
    print(f"  No KEGG mappings found")

# [3/5] Reactome pathway query
print("\n[3/5] Querying Reactome for pathway memberships...")
reactome_results = []

# Query Reactome in batches
for i in range(0, len(all_genes), 20):
    batch = all_genes[i:i+20]
    for gene in batch:
        try:
            url = f"https://reactome.org/ContentService/data/mapping/UniProt/{gene}/pathways"
            req = urllib.request.Request(url, headers={'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                pathways = json.loads(resp.read().decode())
            for pw in pathways:
                reactome_results.append({
                    'gene': gene,
                    'pathway_id': pw.get('stId', ''),
                    'pathway_name': pw.get('displayName', ''),
                    'source': 'Reactome'
                })
        except:
            pass  # Gene not found in Reactome
    if (i+20) % 100 == 0:
        print(f"  Queried {min(i+20, len(all_genes))}/{len(all_genes)} genes...")
    time.sleep(0.5)

reactome_df = pd.DataFrame(reactome_results)
if len(reactome_df) > 0:
    print(f"  mCRPC genes in Reactome: {reactome_df['gene'].nunique()}")
    print(f"  Reactome pathways: {reactome_df['pathway_id'].nunique()}")

# [4/5] Combine and analyze
print("\n[4/5] Combining KEGG + Reactome...")
combined = pd.concat([kegg_df, reactome_df], ignore_index=True)
print(f"  Total gene-pathway edges: {len(combined)}")
print(f"  Unique genes: {combined['gene'].nunique()}")
print(f"  Unique pathways: {combined['pathway_id'].nunique()}")

# Key cancer pathways
print(f"\n  Key mCRPC-relevant pathways:")
cancer_keywords = ['prostate', 'androgen', 'p53', 'PI3K', 'AKT', 'mTOR',
                   'Wnt', 'cell cycle', 'apoptosis', 'DNA repair',
                   'MAPK', 'JAK', 'STAT', 'notch', 'hedgehog',
                   'homologous recombination', 'checkpoint', 'PARP',
                   'BRCA', 'hormone', 'steroid', 'neuroendocrine']

for kw in cancer_keywords:
    matches = combined[combined['pathway_name'].str.contains(kw, case=False, na=False)]
    if len(matches) > 0:
        genes_in = sorted(matches['gene'].unique())
        pw_name = matches.iloc[0]['pathway_name'][:60]
        print(f"  [{kw}] {len(genes_in)} genes: {genes_in[:6]}")

# [5/5] Identify escape routes
print(f"\n[5/5] Identifying potential escape routes...")
# Escape route = when a pathway is blocked, which other pathways
# share genes that could compensate?

# For each key driver, find all its pathways, then find other genes
# in those pathways that could activate alternative signaling
key_targets = ['AR', 'PTEN', 'TP53', 'BRCA2', 'ATM']
for target in key_targets:
    target_pws = combined[combined['gene'] == target]['pathway_id'].unique()
    if len(target_pws) == 0:
        print(f"  {target}: no pathway data")
        continue
    # Find all other genes in the same pathways
    shared = combined[combined['pathway_id'].isin(target_pws)]
    other_genes = sorted(set(shared['gene'].unique()) - {target})
    print(f"  {target} shares pathways with {len(other_genes)} genes")
    print(f"    Top co-pathway genes: {other_genes[:10]}")

# Save
combined.to_csv(f'{RESULTS}/step5_gene_pathway_map.csv', index=False)

elapsed = time.time() - start
print(f"\n{'='*70}")
print(f"STEP 5 COMPLETE")
print(f"  {len(combined)} gene-pathway edges")
print(f"  {combined['gene'].nunique()} genes in {combined['pathway_id'].nunique()} pathways")
print(f"  Runtime: {elapsed:.0f}s ({elapsed/60:.1f} min)")
print(f"  Saved to ~/INTERCEPTA/results/step5_gene_pathway_map.csv")
print(f"{'='*70}")
