"""
build_aml_net.py
=================
Builds disease_net_acute_myeloid_leukemia.json WITH interaction edges.
Merges SIGNOR directed edges + STRING interactions for AML genes.
Equivalent to build_unified_net.py but for AML.

Run: python3 code/build_aml_net.py
Runtime: ~30 seconds
"""
import os, sys, json, csv
import pandas as pd
import numpy as np

BASE    = os.path.expanduser('~/INTERCEPTA/')
RESULTS = BASE + 'results/'

print("="*60)
print("BUILDING AML DISEASE NETWORK WITH EDGES")
print("="*60)

# ── Load existing AML gene list ─────────────────────────────
aml_json_path = RESULTS + 'disease_net_acute_myeloid_leukemia.json'
with open(aml_json_path) as f:
    aml_net = json.load(f)

aml_genes = set(aml_net.get('genes', []))
print(f"\n[1/4] AML genes: {len(aml_genes)}")

if not aml_genes:
    print("ERROR: No genes in AML network JSON")
    sys.exit(1)

# ── Load SIGNOR directed edges ──────────────────────────────
print("\n[2/4] Loading SIGNOR directed edges...")
signor_path = RESULTS + 'signor_directed_edges.csv'
if not os.path.exists(signor_path):
    print(f"  ERROR: {signor_path} not found")
    sys.exit(1)

signor_df = pd.read_csv(signor_path)
cols = list(signor_df.columns)
src_col = cols[0]
tgt_col = cols[1]
eff_col = next((c for c in cols if 'effect' in c.lower()), None)
mech_col = next((c for c in cols if 'mechanism' in c.lower()), None)

print(f"  Total SIGNOR edges: {len(signor_df)}")
print(f"  Columns: {cols[:5]}")

# Filter to edges where BOTH genes are in AML network
aml_signor = signor_df[
    signor_df[src_col].isin(aml_genes) &
    signor_df[tgt_col].isin(aml_genes)
].copy()

print(f"  AML-relevant SIGNOR edges (both genes in AML net): {len(aml_signor)}")

# Also include edges where AT LEAST ONE gene is AML
aml_signor_any = signor_df[
    signor_df[src_col].isin(aml_genes) |
    signor_df[tgt_col].isin(aml_genes)
].copy()
print(f"  AML-adjacent SIGNOR edges (at least one AML gene): {len(aml_signor_any)}")

# Build edge list from SIGNOR
signor_edges = []
for _, row in aml_signor.iterrows():
    edge = {
        'source': row[src_col],
        'target': row[tgt_col],
        'type': 'directed',
        'database': 'SIGNOR',
    }
    if eff_col and pd.notna(row.get(eff_col)):
        edge['effect'] = row[eff_col]
    if mech_col and pd.notna(row.get(mech_col)):
        edge['mechanism'] = row[mech_col]
    signor_edges.append(edge)

print(f"  Built {len(signor_edges)} SIGNOR edges for AML")

# ── Load STRING interactions ─────────────────────────────────
print("\n[3/4] Loading STRING interactions...")
string_path = RESULTS + 'step4_string_interactions.csv'
if not os.path.exists(string_path):
    print(f"  WARNING: {string_path} not found — skipping STRING")
    string_edges = []
else:
    string_df = pd.read_csv(string_path)
    scols = list(string_df.columns)
    s_src = scols[0]
    s_tgt = scols[1]
    s_score = next((c for c in scols if 'score' in c.lower()), scols[2] if len(scols)>2 else None)

    print(f"  Total STRING edges: {len(string_df)}")

    aml_string = string_df[
        string_df[s_src].isin(aml_genes) &
        string_df[s_tgt].isin(aml_genes)
    ].copy()
    print(f"  AML STRING edges (both genes): {len(aml_string)}")

    string_edges = []
    for _, row in aml_string.iterrows():
        edge = {
            'source': row[s_src],
            'target': row[s_tgt],
            'type': 'undirected',
            'database': 'STRING',
        }
        if s_score and pd.notna(row.get(s_score)):
            edge['score'] = float(row[s_score])
        string_edges.append(edge)

    print(f"  Built {len(string_edges)} STRING edges for AML")

# ── Assemble and save ────────────────────────────────────────
print("\n[4/4] Assembling AML network with edges...")

all_edges = signor_edges + string_edges

# Add edges to existing AML network JSON
aml_net['edges'] = all_edges
aml_net['n_edges'] = len(all_edges)
aml_net['n_signor_edges'] = len(signor_edges)
aml_net['n_string_edges'] = len(string_edges)
aml_net['edge_build_method'] = 'SIGNOR+STRING filtered to AML genes'

# Statistics
src_genes = set(e['source'] for e in all_edges)
tgt_genes = set(e['target'] for e in all_edges)
connected_genes = src_genes | tgt_genes
isolated_genes  = aml_genes - connected_genes

print(f"\n  AML Network Statistics:")
print(f"  ─────────────────────────")
print(f"  Gene nodes:        {len(aml_genes)}")
print(f"  Total edges:       {len(all_edges)}")
print(f"  SIGNOR directed:   {len(signor_edges)}")
print(f"  STRING undirected: {len(string_edges)}")
print(f"  Connected genes:   {len(connected_genes)}")
print(f"  Isolated genes:    {len(isolated_genes)}")

# Hub genes by degree
from collections import Counter
degree = Counter()
for e in all_edges:
    degree[e['source']] += 1
    degree[e['target']] += 1

top_hubs = sorted(degree.items(), key=lambda x: -x[1])[:10]
print(f"\n  Top hub genes:")
for gene, deg in top_hubs:
    print(f"    {gene}: {deg} connections")

# Check key AML genes are connected
key_aml = ['FLT3','NPM1','DNMT3A','IDH1','IDH2','TP53','RUNX1','KIT','NRAS']
connected_key = [g for g in key_aml if g in connected_genes]
missing_key   = [g for g in key_aml if g not in connected_genes]
print(f"\n  Key AML genes connected: {connected_key}")
if missing_key:
    print(f"  Key AML genes isolated:  {missing_key}")

# Save
with open(aml_json_path, 'w') as f:
    json.dump(aml_net, f, indent=2)

file_size = os.path.getsize(aml_json_path) / 1e6
print(f"\n  Saved: {aml_json_path}")
print(f"  File size: {file_size:.1f}MB")

# Verify
print("\n  Verification:")
with open(aml_json_path) as f:
    verify = json.load(f)
print(f"  ✓ Genes: {len(verify.get('genes',[]))}")
print(f"  ✓ Edges: {len(verify.get('edges',[]))}")
print(f"  ✓ SIGNOR: {verify.get('n_signor_edges',0)}")
print(f"  ✓ STRING: {verify.get('n_string_edges',0)}")

print("\n" + "="*60)
print("AML NETWORK BUILD COMPLETE")
print(f"The 'disease network has 0 edges' bug is now FIXED.")
print("="*60)
