"""
INTERCEPTA Net Architecture v2.0 — Step 3
Process scRNA-seq: cluster cells, identify populations, compute KAALCURA per cluster.
36,424 cells from 13 prostate tumors (Chen et al. 2021, GSE141445).

Author: Prasad Akula
"""
import pandas as pd, numpy as np, time, warnings, os, sys, gc
from scipy import sparse
from scipy.stats import zscore
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

start = time.time()
print("=" * 70)
print("INTERCEPTA Step 3: scRNA-seq Cell Population Analysis")
print("  36,424 cells x 25,044 genes from 13 prostate tumors")
print("=" * 70)

DATADIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'scrna', 'GSE141445')
RESULTS = os.path.join(os.path.dirname(__file__), '..', 'results')

# [1] Load as sparse to save memory
print("\n[1/6] Loading count matrix as sparse (~600MB instead of 7GB)...")
t0 = time.time()
# Read in chunks to manage memory
chunk_iter = pd.read_csv(
    os.path.join(DATADIR, 'GSM4203181_data.matrix.txt.gz'),
    sep='\t', index_col=0, compression='gzip',
    chunksize=5000
)

chunks_data = []
gene_names = None
cell_names = None

for i, chunk in enumerate(chunk_iter):
    if cell_names is None:
        cell_names = chunk.columns.tolist()
    chunks_data.append(sparse.csr_matrix(chunk.values.astype(np.float32)))
    if gene_names is None:
        gene_names = chunk.index.tolist()
    else:
        gene_names.extend(chunk.index.tolist())
    if (i+1) % 2 == 0:
        print(f"  Loaded {(i+1)*5000} genes...")

data = sparse.vstack(chunks_data)
del chunks_data
gc.collect()
print(f"  Sparse matrix: {data.shape[0]} genes x {data.shape[1]} cells")
print(f"  Memory: {data.data.nbytes/1024/1024:.0f} MB (vs ~7000 MB dense)")
print(f"  Time: {time.time()-t0:.0f}s")

n_genes, n_cells = data.shape

# [2] QC filtering
print("\n[2/6] Quality control filtering...")
genes_per_cell = np.array((data > 0).sum(axis=0)).flatten()
counts_per_cell = np.array(data.sum(axis=0)).flatten()

# Filter cells: >500 genes, <5000 genes
cell_mask = (genes_per_cell > 500) & (genes_per_cell < 5000)
print(f"  Cells before QC: {n_cells}")
print(f"  Cells after QC (500<genes<5000): {cell_mask.sum()}")

data_qc = data[:, cell_mask]
cell_names_qc = [cell_names[i] for i in range(n_cells) if cell_mask[i]]

# Filter genes: expressed in >10 cells
genes_in_cells = np.array((data_qc > 0).sum(axis=1)).flatten()
gene_mask = genes_in_cells > 10
data_qc = data_qc[gene_mask, :]
gene_names_qc = [gene_names[i] for i in range(n_genes) if gene_mask[i]]
print(f"  Genes after QC (>10 cells): {len(gene_names_qc)}")

n_g, n_c = data_qc.shape
print(f"  Final: {n_g} genes x {n_c} cells")

# [3] Normalize + log transform
print("\n[3/6] Normalizing (CPM + log1p)...")
cell_totals = np.array(data_qc.sum(axis=0)).flatten()
# Normalize to 10,000 counts per cell
scale_factors = 10000.0 / cell_totals
# Multiply each column by its scale factor
data_norm = data_qc.multiply(sparse.diags(scale_factors))
# Log transform
data_log = data_norm.copy()
data_log.data = np.log1p(data_log.data)
print(f"  Normalized and log-transformed")

# [4] Identify cell types using marker genes
print("\n[4/6] Cell type identification using marker genes...")

markers = {
    'Epithelial': ['EPCAM','KRT8','KRT18','CDH1'],
    'Luminal': ['KLK3','AR','NKX3-1','TMPRSS2'],
    'Basal': ['KRT5','KRT14','TP63'],
    'T_cell': ['CD3D','CD3E','CD8A','CD4','IL7R'],
    'Macrophage': ['CD68','CD163','CSF1R','SPP1'],
    'Fibroblast': ['COL1A1','DCN','LUM','ACTA2'],
    'Endothelial': ['PECAM1','VWF','CDH5'],
    'NK_cell': ['NKG7','GNLY'],
    'B_cell': ['CD79A','MS4A1'],
    'Mast_cell': ['TPSAB1','TPSB2'],
    'NE_like': ['SYP','CHGA','ENO2','NCAM1'],
}

# Build gene index
gene_idx = {g: i for i, g in enumerate(gene_names_qc)}

# Score each cell for each cell type
print("  Computing marker scores per cell...")
cell_scores = {}
for ct, genes in markers.items():
    present = [g for g in genes if g in gene_idx]
    if not present:
        continue
    indices = [gene_idx[g] for g in present]
    # Mean expression of marker genes
    marker_expr = np.array(data_log[indices, :].mean(axis=0)).flatten()
    cell_scores[ct] = marker_expr

scores_df = pd.DataFrame(cell_scores, index=cell_names_qc)

# Assign each cell to highest-scoring type
cell_types = scores_df.idxmax(axis=1)
cell_type_counts = cell_types.value_counts()

print(f"\n  Cell type distribution:")
print(f"  {'Type':<15} {'Count':>7} {'Percent':>8}")
print(f"  {'-'*15} {'-'*7} {'-'*8}")
for ct, count in cell_type_counts.items():
    pct = count / len(cell_types) * 100
    print(f"  {ct:<15} {count:>7} {pct:>7.1f}%")

# [5] Compute KAALCURA axes per cell type
print("\n[5/6] Computing KAALCURA axes per cell population...")

prolif_genes = ['MKI67','TOP2A','PCNA','CDK1','CCNB1','AURKA','BUB1','PLK1',
                'MCM2','MCM6','FOXM1','BIRC5','NUSAP1','TPX2','CDC20','CENPF']
emt_genes_pos = ['VIM','CDH2','SNAI1','SNAI2','ZEB1','ZEB2','TWIST1','FN1']
emt_genes_neg = ['CDH1','CLDN1','TJP1']
ddr_genes = ['BRCA1','BRCA2','RAD51','ATM','ATR','CHEK1','CHEK2','PARP1',
             'PARP2','XRCC1','MLH1','MSH2','FANCA','FANCD2','RPA1']

def compute_axis(gene_list, data_log, gene_idx, cell_indices, invert=False):
    """Compute mean z-scored expression for a gene set."""
    present = [g for g in gene_list if g in gene_idx]
    if not present:
        return np.zeros(len(cell_indices))
    indices = [gene_idx[g] for g in present]
    vals = np.array(data_log[indices, :][:, cell_indices].todense())
    # Z-score per gene across cells
    z = np.zeros_like(vals, dtype=np.float64)
    for i in range(vals.shape[0]):
        row = vals[i, :]
        std = row.std()
        if std > 0:
            z[i, :] = (row - row.mean()) / std
    axis = z.mean(axis=0).flatten()
    if invert:
        axis = -axis
    return np.array(axis).flatten()

# Map cell names to indices
cell_idx_map = {name: i for i, name in enumerate(cell_names_qc)}

print(f"\n  {'Population':<15} {'N cells':>8} {'R_prolif':>9} {'R_emt':>9} {'R_ddr':>9}")
print(f"  {'-'*15} {'-'*8} {'-'*9} {'-'*9} {'-'*9}")

kaalcura_results = []
for ct in cell_type_counts.index:
    ct_cells = cell_types[cell_types == ct].index.tolist()
    ct_indices = [cell_idx_map[c] for c in ct_cells if c in cell_idx_map]
    
    if len(ct_indices) < 20:
        continue
    
    r_prolif = compute_axis(prolif_genes, data_log, gene_idx, ct_indices)
    r_emt_pos = compute_axis(emt_genes_pos, data_log, gene_idx, ct_indices)
    r_emt_neg = compute_axis(emt_genes_neg, data_log, gene_idx, ct_indices, invert=True)
    r_emt = (r_emt_pos + r_emt_neg) / 2
    r_ddr = compute_axis(ddr_genes, data_log, gene_idx, ct_indices)
    
    kaalcura_results.append({
        'cell_type': ct,
        'n_cells': len(ct_indices),
        'R_prolif_mean': float(np.mean(r_prolif)),
        'R_prolif_std': float(np.std(r_prolif)),
        'R_emt_mean': float(np.mean(r_emt)),
        'R_emt_std': float(np.std(r_emt)),
        'R_ddr_mean': float(np.mean(r_ddr)),
        'R_ddr_std': float(np.std(r_ddr)),
    })
    
    print(f"  {ct:<15} {len(ct_indices):>8} {np.mean(r_prolif):>+9.3f} "
          f"{np.mean(r_emt):>+9.3f} {np.mean(r_ddr):>+9.3f}")

# [6] Key biological insights
print("\n[6/6] Biological insights for INTERCEPTA...")
kdf = pd.DataFrame(kaalcura_results)

# Which populations are most proliferative (sensitive to chemo)?
most_prolif = kdf.loc[kdf['R_prolif_mean'].idxmax()]
print(f"  Most proliferative (chemo-sensitive): {most_prolif['cell_type']} "
      f"(R_prolif={most_prolif['R_prolif_mean']:+.3f})")

# Which have highest DDR (sensitive to PARP inhibitors)?
most_ddr = kdf.loc[kdf['R_ddr_mean'].idxmax()]
print(f"  Highest DNA repair (PARPi-sensitive): {most_ddr['cell_type']} "
      f"(R_ddr={most_ddr['R_ddr_mean']:+.3f})")

# Which are most mesenchymal (resistant)?
most_emt = kdf.loc[kdf['R_emt_mean'].idxmax()]
print(f"  Most mesenchymal (drug-resistant): {most_emt['cell_type']} "
      f"(R_emt={most_emt['R_emt_mean']:+.3f})")

# Save
kdf.to_csv(os.path.join(RESULTS, 'step3_kaalcura_per_population.csv'), index=False)
cell_types.to_csv(os.path.join(RESULTS, 'step3_cell_type_assignments.csv'))

elapsed = time.time() - start
print(f"\n{'='*70}")
print(f"STEP 3 COMPLETE")
print(f"  {n_c:,} cells clustered into {len(cell_type_counts)} populations")
print(f"  KAALCURA axes computed per population")
print(f"  Runtime: {elapsed:.0f}s ({elapsed/60:.1f} min)")
print(f"  Saved to ~/INTERCEPTA/results/step3_*.csv")
print(f"{'='*70}")
