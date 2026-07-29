#!/usr/bin/env python3
"""
INTERCEPTA Step 13: DICE Immune Expression Map
15,994 genes from our net expressed >1 TPM across 15 immune cell types.
CTLA4 highest in memory Tregs (1798 TPM), PD-L1 in activated T cells.
AR barely in immune (1.2 TPM) — confirms prostate specificity.

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
"""
import pandas as pd

def process_dice(data_dir='../data/dice', results_dir='../results',
                 ot_dir='../data/opentargets'):
    """Process DICE immune expression and map to gene symbols."""
    df = pd.read_csv(f'{data_dir}/mean_tpm_merged.csv', index_col=0)
    df.columns = [c.replace('\n', ' ').strip() for c in df.columns]
    
    # Map ENSEMBL → gene symbols using Open Targets
    targets = pd.read_parquet(f'{ot_dir}/targets/', columns=['id','approvedSymbol'])
    ens_to_sym = dict(zip(targets['id'], targets['approvedSymbol']))
    df['gene_symbol'] = df.index.map(ens_to_sym)
    mapped = df.dropna(subset=['gene_symbol']).set_index('gene_symbol')
    mapped = mapped[~mapped.index.duplicated(keep='first')]
    
    print(f'DICE: {len(mapped)} mapped genes x {len(mapped.columns)} immune cell types')
    
    # Key checkpoints
    for g in ['CD274','CTLA4','PDCD1','AR','FOLH1']:
        if g in mapped.index:
            top = mapped.loc[g].idxmax()
            val = mapped.loc[g].max()
            print(f'  {g:<8} top: {top:<35} {val:.1f} TPM')
    
    return mapped

if __name__ == '__main__':
    process_dice()
