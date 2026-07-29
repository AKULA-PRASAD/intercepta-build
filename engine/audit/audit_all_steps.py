#!/usr/bin/env python3
"""
INTERCEPTA Full Audit
======================
Verifies all 11 completed Universal Net steps.
Checks data integrity, biology correctness, and known gaps.

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
"""
import pandas as pd
import json
import os

def audit():
    print('INTERCEPTA FULL AUDIT — ALL STEPS')
    print('='*60)
    
    with open('../results/mcrpc_unified_net.json') as f:
        net = json.load(f)
    
    print(f'Net version: {net["metadata"]["version"]}')
    print(f'Total genes: {len(net["genes"])}')
    print(f'File size: {os.path.getsize("../results/mcrpc_unified_net.json")/1e6:.1f} MB')
    
    layers = {'disease_associations':0,'metabolites':0,'alphafold':0,
              'immune_expression':0,'drug_correlations':0,'interactions':0,
              'pathways':0,'selectivity':0,'compounds':0,'cna':0}
    for gene, data in net['genes'].items():
        for layer in layers:
            if layer in data and data[layer]: layers[layer] += 1
    
    print(f'\nGenes per layer:')
    for layer, count in sorted(layers.items(), key=lambda x:-x[1]):
        print(f'  {layer:<25} {count:>6}')
    
    # Biology checks
    print(f'\nBiology verification:')
    ar = net['genes']['AR']
    ar_mut = ar.get('mutation_frequency', 0)
    ar_cna = ar.get('cna', {}).get('amp', 0)
    print(f'  AR: mut={ar_mut:.1%} + amp={ar_cna}/427 = {ar_mut+ar_cna/427:.1%} (expected ~63%)')
    
    for gene, expected in [('BRCA2','breast'),('TP53','Li-Fraumeni'),('CYP17A1','adrenal')]:
        diseases = [d['disease_name'] for d in net['genes'].get(gene,{}).get('disease_associations',[])]
        match = any(expected.lower() in d.lower() for d in diseases)
        print(f'  {gene} → "{expected}": {match} ({diseases[:2]})')
    
    print(f'\nKNOWN GAPS:')
    print(f'  Step 4 (STRING): only 686 proteins (needs expansion)')
    print(f'  Step 10 (AlphaFold): only 20 targets (ATM failed)')
    print(f'  Step 12 (Epigenome): ENCODE API broken, skipped')
    print(f'  Steps 14-20: not started')

if __name__ == '__main__':
    audit()
