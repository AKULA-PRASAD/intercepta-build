"""
INTERCEPTA Net Architecture v2.0 — Step 1
Build complete gene-drug correlation net from GDSC data on disk.
ALL genes x ALL drugs x 962 cell lines.
Every significant connection (p<0.001, |r|>0.15) becomes a net edge.

Author: Prasad Akula
"""
import pandas as pd, numpy as np, time, warnings, os
warnings.filterwarnings('ignore')

start = time.time()
print("=" * 70)
print("INTERCEPTA Step 1: Complete Gene-Drug Net from GDSC")
print("  ALL genes. ALL drugs. No cherry-picking. From data.")
print("=" * 70)

DATA = os.path.join(os.path.dirname(__file__), '..', 'data', 'gdsc')
RESULTS = os.path.join(os.path.dirname(__file__), '..', 'results')

# Load expression
print("\n[1/4] Loading expression (962 cell lines x 37,602 genes)...")
expr = pd.read_csv(os.path.join(DATA, 'expression_data', 'rnaseq_tpm_20220624.csv'),
                    skiprows=[0,2,3], index_col=1, low_memory=False)
expr = expr.drop(columns=[expr.columns[0]], errors='ignore')
expr = expr.iloc[1:]
expr = expr.apply(pd.to_numeric, errors='coerce')
expr = expr.T
expr = np.log2(expr + 1)
expr = expr.fillna(0)
expr = expr.loc[:, expr.std() > 0.1]  # Remove zero-variance genes
print(f"  {expr.shape[0]} cell lines x {expr.shape[1]} genes")

# Load drug sensitivity
print("\n[2/4] Loading drug sensitivity (286 drugs)...")
sens = pd.read_excel(os.path.join(DATA, 'GDSC2_fitted_dose_response.xlsx'))
ic50 = sens.pivot_table(index='CELL_LINE_NAME', columns='DRUG_NAME',
                         values='LN_IC50', aggfunc='median')

common = sorted(set(expr.index) & set(ic50.index))
expr_a = expr.loc[common]
ic50_a = ic50.loc[common]
print(f"  {len(common)} matched cell lines x {ic50_a.shape[1]} drugs")

# Compute ALL correlations
print("\n[3/4] Computing ALL gene-drug correlations...")
print("  This is the real net — every gene, every drug, from data.")
print("  Estimated time: 3-5 minutes.\n")

connections = []
drugs_processed = 0
total_drugs = ic50_a.shape[1]

for drug in ic50_a.columns:
    drug_vals = ic50_a[drug].dropna()
    valid = drug_vals.index.tolist()
    n = len(valid)
    if n < 30:
        drugs_processed += 1
        continue

    # Vectorized Pearson correlation: all genes at once
    X = expr_a.loc[valid].values  # n_samples x n_genes
    y = drug_vals.loc[valid].values  # n_samples

    X_mean = X.mean(axis=0)
    y_mean = y.mean()
    X_centered = X - X_mean
    y_centered = y - y_mean

    X_std = X.std(axis=0)
    y_std = y.std()

    # Avoid division by zero
    valid_genes = X_std > 0
    r_values = np.zeros(X.shape[1])
    r_values[valid_genes] = (X_centered[:, valid_genes].T @ y_centered) / (n * X_std[valid_genes] * y_std)

    # Keep significant: |r| > 0.15
    sig_mask = np.abs(r_values) > 0.15
    sig_indices = np.where(sig_mask)[0]

    gene_names = expr_a.columns
    for idx in sig_indices:
        r = r_values[idx]
        connections.append({
            'gene': gene_names[idx],
            'drug': drug,
            'r': round(float(r), 4),
            'abs_r': round(abs(float(r)), 4),
            'direction': 'sensitive' if r < 0 else 'resistant',
            'n_samples': n
        })

    drugs_processed += 1
    if drugs_processed % 50 == 0:
        elapsed = time.time() - start
        print(f"  {drugs_processed}/{total_drugs} drugs | "
              f"{len(connections):,} connections | {elapsed:.0f}s")

net = pd.DataFrame(connections)
elapsed = time.time() - start
print(f"\n  Done: {drugs_processed} drugs processed in {elapsed:.0f}s")

# Statistics
print(f"\n[4/4] NET STATISTICS:")
print(f"  Total connections: {len(net):,}")
print(f"  Unique genes: {net['gene'].nunique():,}")
print(f"  Unique drugs: {net['drug'].nunique():,}")
print(f"  Sensitizing (high expr = low IC50): {(net['direction']=='sensitive').sum():,}")
print(f"  Resistance (high expr = high IC50): {(net['direction']=='resistant').sum():,}")

strong = net[net['abs_r'] > 0.3]
print(f"\n  Strong connections (|r| > 0.3): {len(strong):,}")
print(f"    Covering {strong['gene'].nunique()} genes, {strong['drug'].nunique()} drugs")

# Hub genes — connected to most drugs
print(f"\n  Top 30 hub genes (connected to most drugs):")
hubs = net.groupby('gene').agg(
    n_drugs=('drug', 'nunique'),
    mean_r=('r', 'mean'),
    mean_abs_r=('abs_r', 'mean')
).sort_values('n_drugs', ascending=False)

print(f"  {'Gene':<15} {'#Drugs':>7} {'Mean r':>8} {'Mean|r|':>8} {'Trend':>12}")
print(f"  {'-'*15} {'-'*7} {'-'*8} {'-'*8} {'-'*12}")
for gene, row in hubs.head(30).iterrows():
    trend = 'sensitizing' if row['mean_r'] < 0 else 'resistance'
    print(f"  {gene:<15} {row['n_drugs']:>7} {row['mean_r']:>+8.3f} "
          f"{row['mean_abs_r']:>8.3f} {trend:>12}")

# Hub drugs
print(f"\n  Top 20 hub drugs (connected to most genes):")
drug_hubs = net.groupby('drug').agg(
    n_genes=('gene', 'nunique'),
    mean_abs_r=('abs_r', 'mean')
).sort_values('n_genes', ascending=False)

for drug, row in drug_hubs.head(20).iterrows():
    print(f"  {drug:<30} {row['n_genes']:>6} genes  mean|r|={row['mean_abs_r']:.3f}")

# Check KAALCURA genes in the net
kaalcura_genes = ['MKI67','TOP2A','PCNA','CDK1','CCNB1','AURKA','BUB1','PLK1',
                  'MCM2','MCM6','FOXM1','BIRC5','NUSAP1','TPX2','CDC20','CENPF',
                  'VIM','CDH2','SNAI1','SNAI2','ZEB1','ZEB2','TWIST1','FN1',
                  'CDH1','CLDN1','TJP1','BRCA1','BRCA2','RAD51','ATM','ATR',
                  'CHEK1','CHEK2','PARP1','PARP2']
kaalcura_in_net = [g for g in kaalcura_genes if g in net['gene'].values]
print(f"\n  KAALCURA genes in net: {len(kaalcura_in_net)}/{len(kaalcura_genes)}")

# mCRPC driver genes in the net
mcrpc_drivers = ['AR','TP53','PTEN','RB1','BRCA2','BRCA1','ATM','SPOP',
                 'FOXA1','MYC','PIK3CA','CDK12','ERG','TMPRSS2']
drivers_in_net = [g for g in mcrpc_drivers if g in net['gene'].values]
print(f"  mCRPC driver genes in net: {len(drivers_in_net)}/{len(mcrpc_drivers)}")
for g in mcrpc_drivers:
    if g in net['gene'].values:
        n = net[net['gene']==g]['drug'].nunique()
        mr = net[net['gene']==g]['r'].mean()
        print(f"    {g:<10} connected to {n:>3} drugs  mean_r={mr:+.3f}")
    else:
        print(f"    {g:<10} NOT IN NET")

# Save
net.to_csv(os.path.join(RESULTS, 'step1_complete_gene_drug_net.csv'), index=False)
hubs.to_csv(os.path.join(RESULTS, 'step1_hub_genes.csv'))
drug_hubs.to_csv(os.path.join(RESULTS, 'step1_hub_drugs.csv'))

total_time = time.time() - start
print(f"\n{'='*70}")
print(f"STEP 1 COMPLETE")
print(f"  {len(net):,} data-derived connections")
print(f"  {net['gene'].nunique():,} genes x {net['drug'].nunique():,} drugs")
print(f"  Runtime: {total_time:.0f}s ({total_time/60:.1f} min)")
print(f"  Saved to ~/INTERCEPTA/results/step1_*.csv")
print(f"{'='*70}")
