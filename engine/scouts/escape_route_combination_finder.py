#!/usr/bin/env python3
"""
INTERCEPTA Escape Route Combination Finder
===========================================
Uses the disease net's escape routes to design rational combinations:
  Drug A blocks primary target
  Drug B blocks the escape gene
  
This is the NET approach — not random screening.

Author: Prasad Akula
"""
import json
import pandas as pd
import urllib.request

def find_combinations(net_path='../results/mcrpc_unified_net.json',
                     scout1_path='../results/scout1_all_drugs_ranked.csv'):
    
    with open(net_path) as f:
        net = json.load(f)
    scout1 = pd.read_csv(scout1_path)
    gdsc = pd.read_excel('../data/gdsc/GDSC2_fitted_dose_response.xlsx')
    
    # Build drug-target map from GDSC
    drug_targets = gdsc[['DRUG_NAME','PUTATIVE_TARGET']].drop_duplicates()
    target_to_drugs = {}
    for _, r in drug_targets.iterrows():
        for t in str(r['PUTATIVE_TARGET']).split(','):
            t = t.strip()
            if t not in target_to_drugs: target_to_drugs[t] = []
            target_to_drugs[t].append(r['DRUG_NAME'])
    
    escape = net.get('escape_routes', {})
    
    combos = []
    for route_target, data in escape.items():
        if not isinstance(data, dict): continue
        escape_genes = data.get('connected_genes', [])
        
        for eg in escape_genes[:20]:
            drugs = target_to_drugs.get(eg, [])
            for drug in drugs:
                row = scout1[scout1['drug']==drug]
                if len(row):
                    combos.append({
                        'primary_target': route_target,
                        'escape_gene': eg,
                        'blocking_drug': drug,
                        'hr': row.iloc[0]['hr'],
                        'tail_kill': row.iloc[0]['tail_kill'],
                    })
    
    return pd.DataFrame(combos).sort_values('hr')

def check_novelty(drug1, drug2, condition='prostate cancer'):
    query = f'{drug1} {drug2} {condition}'.replace(' ', '+')
    url = f'https://clinicaltrials.gov/api/v2/studies?query.term={query}&pageSize=5'
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get('totalCount', 0)
    except:
        return -1

if __name__ == '__main__':
    combos = find_combinations()
    print(f'Found {len(combos)} escape route combinations')
    print(f'\nTop 10 by HR:')
    for _, r in combos.head(10).iterrows():
        print(f'  {r["primary_target"]}→{r["escape_gene"]}→{r["blocking_drug"]} HR={r["hr"]:.3f}')
    
    combos.to_csv('../results/escape_route_combinations.csv', index=False)
    print(f'\nSaved: results/escape_route_combinations.csv')

