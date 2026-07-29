"""
kaalcura_step1_build_mapping.py
================================
Step 1 of 2: Extract SIDG→gene_symbol mapping from GDSC all_data file.
Saves: data/gdsc/sidg_to_symbol.csv
Runtime: 2-5 minutes (reads 5.3GB file in chunks)

Run: python3 code/kaalcura_step1_build_mapping.py
"""
import os, sys, zipfile, time
import pandas as pd

BASE = os.path.expanduser('~/INTERCEPTA/')
DATA = BASE + 'data/gdsc/'

print("="*60)
print("STEP 1: BUILD SIDG → GENE SYMBOL MAPPING")
print("="*60)

zip_path = DATA + 'sanger_model_gene_expression.csv.gz'
out_path  = DATA + 'sidg_to_symbol.csv'

if not os.path.exists(zip_path):
    print(f"ERROR: ZIP not found at {zip_path}")
    sys.exit(1)

print(f"\nReading gene_id + gene_symbol columns from all_data ZIP...")
print("(This reads 5.3GB in chunks — expect 2-5 minutes)\n")

t0 = time.time()
chunks = []
n_genes_seen = 0

with zipfile.ZipFile(zip_path) as z:
    reader = pd.read_csv(
        z.open('rnaseq_all_data_20220624.csv'),
        usecols=['gene_id', 'gene_symbol'],
        chunksize=1_000_000
    )
    for i, chunk in enumerate(reader):
        chunk_unique = chunk.drop_duplicates('gene_id')
        chunks.append(chunk_unique)
        combined = pd.concat(chunks).drop_duplicates('gene_id')
        n_genes_seen = len(combined)
        elapsed = time.time() - t0
        print(f"  Chunk {i+1}: {n_genes_seen} unique genes found "
              f"({elapsed:.0f}s elapsed)", end='\r')
        if n_genes_seen >= 37000:
            print(f"\n  Found all ~37602 genes after chunk {i+1}. Stopping early.")
            break

print()
mapping = pd.concat(chunks).drop_duplicates('gene_id').reset_index(drop=True)
print(f"\nTotal mapping entries: {len(mapping)}")

# Verify key KAALCURA genes are present
key_genes = ['BRCA1','BRCA2','MKI67','ATM','PARP1','TP53',
             'CDH1','VIM','AR','MTOR','TOP2A','CDK1','PCNA']
found     = [g for g in key_genes if g in mapping['gene_symbol'].values]
missing   = [g for g in key_genes if g not in mapping['gene_symbol'].values]

print(f"\nKey KAALCURA genes found: {found}")
if missing:
    print(f"Missing: {missing}")
else:
    print("All key genes present ✓")

# Save
mapping.to_csv(out_path, index=False)
print(f"\nSaved: {out_path}")
print(f"Total time: {time.time()-t0:.0f}s")
print("\nNow run: python3 code/kaalcura_step2_validate.py")
