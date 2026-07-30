#!/usr/bin/env python3
"""
INTERCEPTA Step 8: Open Targets Disease Map
Downloads and processes Open Targets v26.03 disease-gene associations.
4,508,002 associations, 30,548 genes, 26,288 diseases.

Author: Prasad Akula
"""
import pandas as pd
import os

def download_opentargets(data_dir='../data/opentargets'):
    """Download Open Targets data if not present."""
    os.makedirs(data_dir, exist_ok=True)
    # Data downloaded from: https://platform.opentargets.org/downloads
    # associationByOverallDirect parquet files
    # targets parquet files  
    # diseases parquet files
    print("Open Targets requires manual download from platform.opentargets.org")
    print(f"Place parquet files in {data_dir}/")

def process_opentargets(data_dir='../data/opentargets', results_dir='../results'):
    """Process Open Targets into gene-disease associations."""
    assoc = pd.read_parquet(f'{data_dir}/')
    # Filter columns
    assoc = assoc.rename(columns={'targetId':'gene','diseaseId':'diseaseId',
                                   'score':'associationScore'})
    
    # Load gene symbols from targets
    targets = pd.read_parquet(f'{data_dir}/targets/', columns=['id','approvedSymbol'])
    id_to_sym = dict(zip(targets['id'], targets['approvedSymbol']))
    assoc['gene'] = assoc['gene'].map(id_to_sym)
    assoc = assoc.dropna(subset=['gene'])
    
    # Load disease names
    diseases = pd.read_parquet(f'{data_dir}/diseases/', columns=['id','name'])
    diseases = diseases.drop_duplicates('id')
    diseases.to_csv(f'{results_dir}/step8_disease_names.csv', index=False)
    
    assoc.to_parquet(f'{results_dir}/step8_gene_disease_associations.parquet', index=False)
    
    print(f'Step 8 COMPLETE:')
    print(f'  Associations: {len(assoc):,}')
    print(f'  Genes: {assoc["gene"].nunique():,}')
    print(f'  Diseases: {assoc["diseaseId"].nunique():,}')
    return assoc

def verify_biology(results_dir='../results'):
    """Verify key disease-gene associations."""
    assoc = pd.read_parquet(f'{results_dir}/step8_gene_disease_associations.parquet')
    names = pd.read_csv(f'{results_dir}/step8_disease_names.csv')
    name_map = dict(zip(names['id'], names['name']))
    
    checks = {
        'prostate': ['AR','BRCA2','PTEN'],
        'leukemia': ['FLT3','DNMT3A','IDH1'],
        'alzheimer': ['APP','APOE'],
    }
    for disease_kw, expected_genes in checks.items():
        matches = assoc[assoc['diseaseId'].map(lambda x: disease_kw in name_map.get(x,'').lower())]
        if len(matches):
            top = matches.nlargest(5,'associationScore')['gene'].values
            found = [g for g in expected_genes if g in top]
            print(f'  {disease_kw}: top={list(top)}, expected={expected_genes}, found={found}')

if __name__ == '__main__':
    verify_biology()
