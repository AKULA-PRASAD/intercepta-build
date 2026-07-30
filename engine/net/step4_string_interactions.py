"""
INTERCEPTA Net Architecture v2.0 — Step 4
Download protein-protein interactions from STRING v12.5
For all recurrently mutated mCRPC genes from Step 2.

Author: Prasad Akula
"""
import json, urllib.request, urllib.parse, pandas as pd, numpy as np, time, os

start = time.time()
print("=" * 70)
print("INTERCEPTA Step 4: STRING Protein-Protein Interactions")
print("  For all mCRPC genes from Step 2 (SU2C mutation data)")
print("=" * 70)

RESULTS = '/Users/kalki/INTERCEPTA/results'
STRING_API = "https://string-db.org/api"
SPECIES = 9606  # Homo sapiens

# Load mutation frequencies from Step 2
print("\n[1/4] Loading mCRPC genes from Step 2...")
mut_freq = pd.read_csv(f'{RESULTS}/step2_mutation_frequencies.csv', index_col=0, header=0)
mut_freq.columns = ['frequency']

# Take genes mutated in >1% of patients (recurrent mutations)
recurrent = mut_freq[mut_freq['frequency'] > 1.0]
all_genes = recurrent.index.tolist()

# Filter out TTN, MUC16, etc (large genes with passenger mutations)
passenger_genes = ['TTN','MUC16','MUC4','OBSCN','SYNE1','RYR1','RYR2','RYR3',
                   'CSMD3','LRP1B','HMCN1','PLEC','MACF1','DCHS2','FAT3',
                   'ABCA13','USH2A','AHNAK2','CACNA1E','FLG','DNAH5','DNAH11']
driver_genes = [g for g in all_genes if g not in passenger_genes]

print(f"  Recurrently mutated genes (>1%): {len(all_genes)}")
print(f"  After removing likely passengers: {len(driver_genes)}")
print(f"  Top 20: {driver_genes[:20]}")

# [2/4] Map gene names to STRING IDs
print("\n[2/4] Mapping genes to STRING identifiers...")

# Query in batches of 200
string_ids = {}
batch_size = 200
for i in range(0, len(driver_genes), batch_size):
    batch = driver_genes[i:i+batch_size]
    params = urllib.parse.urlencode({
        'identifiers': '%0d'.join(batch),
        'species': SPECIES,
        'limit': 1,
        'caller_identity': 'INTERCEPTA'
    })
    url = f"{STRING_API}/json/get_string_ids?{params}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        for item in data:
            query = item.get('queryItem', '')
            sid = item.get('stringId', '')
            pname = item.get('preferredName', '')
            if query and sid:
                string_ids[query] = {'stringId': sid, 'name': pname}
        print(f"  Batch {i//batch_size+1}: mapped {len(data)} genes")
    except Exception as e:
        print(f"  Batch {i//batch_size+1} error: {e}")
    time.sleep(1)  # Rate limiting

print(f"  Total mapped: {len(string_ids)} / {len(driver_genes)}")

# [3/4] Get interactions for all mapped genes
print("\n[3/4] Downloading protein-protein interactions...")
mapped_sids = [v['stringId'] for v in string_ids.values()]

all_interactions = []
# Query in batches
for i in range(0, len(mapped_sids), 200):
    batch = mapped_sids[i:i+200]
    params = urllib.parse.urlencode({
        'identifiers': '%0d'.join(batch),
        'species': SPECIES,
        'required_score': 700,  # High confidence only
        'caller_identity': 'INTERCEPTA'
    })
    url = f"{STRING_API}/json/network?{params}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
        all_interactions.extend(data)
        print(f"  Batch {i//200+1}: {len(data)} interactions (total: {len(all_interactions)})")
    except Exception as e:
        print(f"  Batch {i//200+1} error: {e}")
    time.sleep(1)

# Parse interactions
print("\n[4/4] Parsing interaction network...")
edges = []
for inter in all_interactions:
    edges.append({
        'protein_A': inter.get('preferredName_A', ''),
        'protein_B': inter.get('preferredName_B', ''),
        'combined_score': inter.get('score', 0),
        'string_A': inter.get('stringId_A', ''),
        'string_B': inter.get('stringId_B', ''),
    })

edges_df = pd.DataFrame(edges).drop_duplicates(subset=['protein_A','protein_B'])

print(f"  Total interactions (score>700): {len(edges_df)}")
print(f"  Unique proteins: {len(set(edges_df['protein_A']) | set(edges_df['protein_B']))}")

# Network statistics
if len(edges_df) > 0:
    # Hub proteins
    all_proteins = list(edges_df['protein_A']) + list(edges_df['protein_B'])
    hub_counts = pd.Series(all_proteins).value_counts()

    print(f"\n  Top 20 hub proteins (most interactions):")
    print(f"  {'Protein':<15} {'Interactions':>13} {'Mutated in mCRPC':>17}")
    print(f"  {'-'*15} {'-'*13} {'-'*17}")
    for prot, count in hub_counts.head(20).items():
        mut_pct = mut_freq.get(prot, pd.Series([0])).values[0] if prot in mut_freq.index else 0
        mut_str = f"{mut_pct:.1f}%" if mut_pct > 0 else "no"
        print(f"  {prot:<15} {count:>13} {mut_str:>17}")

    # Key mCRPC driver interactions
    print(f"\n  Key mCRPC driver interactions:")
    key_drivers = ['TP53','AR','PTEN','RB1','BRCA2','BRCA1','ATM','MYC','FOXA1','SPOP']
    for driver in key_drivers:
        driver_edges = edges_df[(edges_df['protein_A']==driver) | (edges_df['protein_B']==driver)]
        if len(driver_edges) > 0:
            partners = []
            for _, row in driver_edges.iterrows():
                partner = row['protein_B'] if row['protein_A']==driver else row['protein_A']
                partners.append(partner)
            print(f"  {driver:<10} interacts with {len(partners)} proteins: {partners[:8]}...")

# Save
edges_df.to_csv(f'{RESULTS}/step4_string_interactions.csv', index=False)
hub_counts.to_csv(f'{RESULTS}/step4_hub_proteins.csv')

elapsed = time.time() - start
print(f"\n{'='*70}")
print(f"STEP 4 COMPLETE")
print(f"  {len(edges_df)} high-confidence interactions (STRING score>700)")
print(f"  {len(set(edges_df['protein_A']) | set(edges_df['protein_B']))} proteins in network")
print(f"  Runtime: {elapsed:.0f}s")
print(f"  Saved to ~/INTERCEPTA/results/step4_*.csv")
print(f"{'='*70}")
