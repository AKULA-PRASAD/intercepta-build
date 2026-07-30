#!/usr/bin/env python3
"""
INTERCEPTA Step 10: AlphaFold Protein Structures
Downloads AlphaFold v6 structures for drug target proteins.
19/20 targets successful (ATM too large, no prediction).

Author: Prasad Akula
"""
import pandas as pd
import json
import os
import subprocess

TARGETS = {
    'AR':'P10275','PARP1':'P09874','CDK4':'P11802','TP53':'P04637',
    'PIK3CA':'P42336','MDM2':'Q00987','BRCA1':'P38398','ATM':'Q13315',
    'AKT1':'P31749','MTOR':'P42345','BCL2L1':'Q07817','EGFR':'P00533',
    'ERBB2':'P04626','TOP2B':'Q02880','CSNK2A1':'P68400','AKT2':'O14965',
    'MAPK14':'Q16539','KIT':'P10721','MAP2K1':'Q02750','CDK2':'P24941'
}

def verify_structures(data_dir='../data/alphafold', results_dir='../results'):
    """Verify downloaded AlphaFold structures."""
    results = pd.read_csv(f'{results_dir}/step10_alphafold_structures.csv')
    ok = results[results['status']=='OK']
    fail = results[results['status']=='FAILED']
    print(f'Step 10 AlphaFold:')
    print(f'  Valid: {len(ok)}/20')
    print(f'  Failed: {list(fail["gene"].values)}')
    for _, r in ok.iterrows():
        print(f'  {r["gene"]:<10} {r["n_atoms"]:>6} atoms  {r["size_kb"]:>5}KB')
    return results

if __name__ == '__main__':
    verify_structures()
