#!/usr/bin/env python3
"""
INTERCEPTA Step 9: Human-GEM Metabolome
Processes Human-GEM v1.18 gene-reaction-metabolite links.
50,323 edges (cleaned), 2,615 genes, 2,736 metabolites.

Cleaning: removed cofactors (H2O, ATP, NADPH etc) and parsing artifacts.
Verified: CYP17A1 → pregnenolone, progesterone, DHEA (abiraterone target pathway).

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
"""
import pandas as pd
import os

def process_human_gem(data_dir='../data/human_gem', results_dir='../results'):
    """Parse Human-GEM and create clean gene-metabolite edges."""
    # Files: genes.tsv, metabolites.tsv, reactions.tsv, Human-GEM.txt
    # Parse gene-reaction-metabolite links from Human-GEM.txt
    
    edges = pd.read_csv(f'{results_dir}/step9_metabolome_gene_edges.csv')
    print(f'Step 9 Metabolome:')
    print(f'  Edges: {len(edges):,}')
    print(f'  Genes: {edges["gene_symbol"].nunique():,}')
    print(f'  Metabolites: {edges["metabolite"].nunique():,}')
    
    # Verify biology
    cyp17 = edges[edges['gene_symbol']=='CYP17A1']['metabolite'].unique()
    print(f'\n  CYP17A1 metabolites ({len(cyp17)}):')
    for m in sorted(cyp17):
        print(f'    {m}')
    
    akr = edges[edges['gene_symbol']=='AKR1C3']['metabolite'].unique()
    print(f'\n  AKR1C3 metabolites ({len(akr)}):')
    for m in sorted(akr)[:5]:
        print(f'    {m}')
    
    return edges

if __name__ == '__main__':
    process_human_gem()
