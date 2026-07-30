#!/usr/bin/env python3
"""
INTERCEPTA: Integrate Steps 8-10,13 into Unified Net v2.0
Adds disease associations, metabolites, AlphaFold structures,
and immune expression to the unified net.
Final: 49.1 MB, 27,431 genes, 11 layers.

Author: Prasad Akula
"""
import json
import pandas as pd

def integrate(net_path='../results/mcrpc_unified_net.json',
              results_dir='../results'):
    with open(net_path) as f:
        net = json.load(f)
    
    # Step 8: Disease associations (optimized with groupby)
    print('Step 8: Disease associations...')
    assoc = pd.read_parquet(f'{results_dir}/step8_gene_disease_associations.parquet')
    names = pd.read_csv(f'{results_dir}/step8_disease_names.csv')
    name_map = dict(zip(names['id'], names['name']))
    top_per_gene = assoc.sort_values('associationScore', ascending=False).groupby('gene').head(10)
    grouped = top_per_gene.groupby('gene')
    count8 = 0
    for gene, group in grouped:
        if gene in net['genes']:
            net['genes'][gene]['disease_associations'] = [
                {'disease_id': r['diseaseId'], 'disease_name': name_map.get(r['diseaseId'],''),
                 'score': round(r['associationScore'],4)}
                for _, r in group.iterrows()
            ]
            count8 += 1
    print(f'  Added to {count8} genes')
    
    # Step 9: Metabolites
    print('Step 9: Metabolites...')
    met = pd.read_csv(f'{results_dir}/step9_metabolome_gene_edges.csv')
    met_grouped = met.groupby('gene_symbol')['metabolite'].apply(lambda x: list(x.unique()[:20]))
    count9 = 0
    for gene, mets in met_grouped.items():
        if gene in net['genes']:
            net['genes'][gene]['metabolites'] = mets
            count9 += 1
    print(f'  Added to {count9} genes')
    
    # Step 10: AlphaFold
    print('Step 10: AlphaFold...')
    af = pd.read_csv(f'{results_dir}/step10_alphafold_structures.csv')
    count10 = 0
    for _, r in af[af['status']=='OK'].iterrows():
        if r['gene'] in net['genes']:
            net['genes'][r['gene']]['alphafold'] = {
                'uniprot': r['uniprot'], 'n_atoms': int(r['n_atoms'])}
            count10 += 1
    print(f'  Added to {count10} genes')
    
    # Step 13: Immune
    print('Step 13: Immune...')
    immune = pd.read_csv(f'{results_dir}/step13_immune_expression.csv', index_col=0)
    immune = immune[~immune.index.duplicated(keep='first')]
    count13 = 0
    for gene in net['genes']:
        if gene in immune.index:
            row = immune.loc[gene]
            top_val = float(row.max())
            if top_val > 1.0:
                net['genes'][gene]['immune_expression'] = {
                    'top_cell_type': row.idxmax(),
                    'top_tpm': round(top_val, 1),
                    'mean_tpm': round(float(row.mean()), 1)}
                count13 += 1
    print(f'  Added to {count13} genes')
    
    net['metadata']['version'] = '2.0'
    net['metadata']['date'] = '2026-04-08'
    
    with open(net_path, 'w') as f:
        json.dump(net, f)
    print(f'\nSaved: {len(json.dumps(net))/1e6:.1f} MB')
    return net

if __name__ == '__main__':
    integrate()
