"""
INTERCEPTA Net Architecture v2.0 — Step 7
Query ChEMBL for all compounds with measured activity against mCRPC drug targets.
Expands Layer 7 beyond the 286 GDSC drugs.

Author: Prasad Akula
"""
import json, urllib.request, urllib.parse, pandas as pd, numpy as np, time, os

start = time.time()
print("=" * 70)
print("INTERCEPTA Step 7: ChEMBL Compound Database Query")
print("  Every compound ever tested against mCRPC targets")
print("=" * 70)

RESULTS = '/Users/kalki/INTERCEPTA/results'
CHEMBL_API = "https://www.ebi.ac.uk/chembl/api/data"

# [1/5] Define targets — use selective + druggable targets from our net
print("\n[1/5] Defining mCRPC drug targets from our net...")

# From selectivity map (Step 6) + pathway analysis (Step 5) + clinical relevance
targets = {
    # Prostate-selective (safe)
    'AR': {'type': 'prostate-selective', 'rationale': 'Primary driver, amplified in 58%'},
    'KLK3': {'type': 'prostate-selective', 'rationale': 'PSA, 37.9x selective'},
    'FOLH1': {'type': 'prostate-selective', 'rationale': 'PSMA, 10.2x selective, radioligand target'},
    'TMPRSS2': {'type': 'prostate-selective', 'rationale': '4.6x selective, fusion partner'},
    
    # Mutation-specific vulnerabilities
    'PARP1': {'type': 'synthetic-lethality', 'rationale': 'PARPi target for BRCA-mutant (13%)'},
    'PARP2': {'type': 'synthetic-lethality', 'rationale': 'PARPi target'},
    
    # Pathway targets (with escape route context)
    'PIK3CA': {'type': 'escape-route', 'rationale': 'PI3K activates when PTEN lost (31%)'},
    'AKT1': {'type': 'escape-route', 'rationale': 'PI3K/AKT/mTOR escape pathway'},
    'MTOR': {'type': 'escape-route', 'rationale': 'mTOR downstream of PI3K'},
    'CDK4': {'type': 'cell-cycle', 'rationale': 'Cell cycle, connected to RB1 (12%)'},
    'CDK6': {'type': 'cell-cycle', 'rationale': 'Cell cycle'},
    'AURKA': {'type': 'cell-cycle', 'rationale': 'Aurora kinase, mitotic'},
    'EZH2': {'type': 'epigenetic', 'rationale': 'Polycomb, NE differentiation'},
    'BRAF': {'type': 'MAPK', 'rationale': 'MAPK escape route'},
    'MDM2': {'type': 'p53-pathway', 'rationale': 'p53 regulator, targetable'},
    'CHEK1': {'type': 'DDR', 'rationale': 'DNA damage checkpoint'},
    'CHEK2': {'type': 'DDR', 'rationale': 'DNA damage checkpoint'},
    'NR3C1': {'type': 'escape-route', 'rationale': 'Glucocorticoid receptor substitutes AR'},
    'BCL2': {'type': 'apoptosis', 'rationale': 'Anti-apoptotic, venetoclax target'},
    'MCL1': {'type': 'apoptosis', 'rationale': 'BCL2 family resistance mechanism'},
}

print(f"  {len(targets)} druggable targets defined")
for ttype in set(v['type'] for v in targets.values()):
    genes = [k for k,v in targets.items() if v['type']==ttype]
    print(f"    {ttype}: {genes}")

# [2/5] Query ChEMBL for target IDs
print("\n[2/5] Mapping targets to ChEMBL target IDs...")

target_chembl_ids = {}
for gene in targets:
    try:
        url = f"{CHEMBL_API}/target/search.json?q={gene}&limit=5"
        req = urllib.request.Request(url, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        
        # Find human single protein target
        for t in data.get('targets', []):
            if (t.get('organism', '') == 'Homo sapiens' and 
                t.get('target_type', '') == 'SINGLE PROTEIN'):
                pref_name = t.get('pref_name', '')
                # Verify it's the right gene
                for comp in t.get('target_components', []):
                    for syn in comp.get('target_component_synonyms', []):
                        if syn.get('component_synonym', '').upper() == gene.upper():
                            target_chembl_ids[gene] = {
                                'chembl_id': t['target_chembl_id'],
                                'pref_name': pref_name
                            }
                            break
                if gene in target_chembl_ids:
                    break
                # Fallback: accept if gene name in preferred name
                if gene.upper() in pref_name.upper() or gene in str(t.get('target_components','')):
                    target_chembl_ids[gene] = {
                        'chembl_id': t['target_chembl_id'],
                        'pref_name': pref_name
                    }
                    break
    except Exception as e:
        pass
    time.sleep(0.3)

print(f"  Mapped {len(target_chembl_ids)}/{len(targets)} targets to ChEMBL")
for gene, info in sorted(target_chembl_ids.items()):
    print(f"    {gene:<10} -> {info['chembl_id']} ({info['pref_name'][:40]})")

# [3/5] Query compounds with activity against each target
print("\n[3/5] Querying compounds per target (IC50/Ki/EC50 data)...")

all_activities = []
for gene, info in target_chembl_ids.items():
    tid = info['chembl_id']
    try:
        # Get activities with IC50 or Ki measurements
        url = (f"{CHEMBL_API}/activity.json?"
               f"target_chembl_id={tid}"
               f"&standard_type__in=IC50,Ki,EC50"
               f"&standard_relation==&limit=1000")
        req = urllib.request.Request(url, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        
        activities = data.get('activities', [])
        for act in activities:
            all_activities.append({
                'target_gene': gene,
                'target_chembl_id': tid,
                'molecule_chembl_id': act.get('molecule_chembl_id', ''),
                'molecule_name': act.get('canonical_smiles', '')[:80] if act.get('canonical_smiles') else '',
                'pchembl_value': act.get('pchembl_value', None),
                'standard_type': act.get('standard_type', ''),
                'standard_value': act.get('standard_value', None),
                'standard_units': act.get('standard_units', ''),
            })
        
        n_compounds = len(set(a['molecule_chembl_id'] for a in activities))
        print(f"  {gene:<10} {tid}: {len(activities)} measurements, {n_compounds} compounds")
    except Exception as e:
        print(f"  {gene:<10} error: {str(e)[:60]}")
    time.sleep(0.5)

act_df = pd.DataFrame(all_activities)
print(f"\n  Total activity measurements: {len(act_df):,}")
print(f"  Unique compounds: {act_df['molecule_chembl_id'].nunique():,}")
print(f"  Targets with data: {act_df['target_gene'].nunique()}")

# [4/5] Analyze potency distribution
print("\n[4/5] Analyzing compound potency...")
if len(act_df) > 0 and 'pchembl_value' in act_df.columns:
    act_df['pchembl_value'] = pd.to_numeric(act_df['pchembl_value'], errors='coerce')
    potent = act_df[act_df['pchembl_value'] >= 6.0]  # IC50 < 1uM
    very_potent = act_df[act_df['pchembl_value'] >= 7.0]  # IC50 < 100nM
    
    print(f"  Potent (IC50 < 1uM, pChEMBL >= 6): {potent['molecule_chembl_id'].nunique()} compounds")
    print(f"  Very potent (IC50 < 100nM, pChEMBL >= 7): {very_potent['molecule_chembl_id'].nunique()} compounds")
    
    print(f"\n  Compounds per target (potent, IC50 < 1uM):")
    print(f"  {'Target':<10} {'All':>6} {'<1uM':>6} {'<100nM':>7} {'Best pChEMBL':>13}")
    print(f"  {'-'*10} {'-'*6} {'-'*6} {'-'*7} {'-'*13}")
    
    for gene in sorted(act_df['target_gene'].unique()):
        g_data = act_df[act_df['target_gene']==gene]
        g_potent = g_data[g_data['pchembl_value']>=6.0]
        g_vpotent = g_data[g_data['pchembl_value']>=7.0]
        best = g_data['pchembl_value'].max()
        best_str = f"{best:.1f}" if not np.isnan(best) else "N/A"
        print(f"  {gene:<10} {g_data['molecule_chembl_id'].nunique():>6} "
              f"{g_potent['molecule_chembl_id'].nunique():>6} "
              f"{g_vpotent['molecule_chembl_id'].nunique():>7} {best_str:>13}")

# [5/5] Save and summarize
print("\n[5/5] Saving...")
act_df.to_csv(f'{RESULTS}/step7_chembl_activities.csv', index=False)

# Save target summary
target_summary = []
for gene, info in targets.items():
    chembl = target_chembl_ids.get(gene, {})
    g_data = act_df[act_df['target_gene']==gene] if len(act_df) > 0 else pd.DataFrame()
    target_summary.append({
        'gene': gene,
        'type': info['type'],
        'rationale': info['rationale'],
        'chembl_id': chembl.get('chembl_id', ''),
        'n_compounds': g_data['molecule_chembl_id'].nunique() if len(g_data)>0 else 0,
        'n_potent': len(g_data[g_data['pchembl_value']>=6.0]) if 'pchembl_value' in g_data.columns else 0,
    })
pd.DataFrame(target_summary).to_csv(f'{RESULTS}/step7_target_summary.csv', index=False)

elapsed = time.time() - start
print(f"\n{'='*70}")
print(f"STEP 7 COMPLETE")
print(f"  {len(act_df):,} activity measurements from ChEMBL")
print(f"  {act_df['molecule_chembl_id'].nunique() if len(act_df)>0 else 0:,} unique compounds")
print(f"  {act_df['target_gene'].nunique() if len(act_df)>0 else 0} targets with compound data")
print(f"  Runtime: {elapsed:.0f}s ({elapsed/60:.1f} min)")
print(f"  Saved to ~/INTERCEPTA/results/step7_*.csv")
print(f"{'='*70}")
