import pandas as pd, numpy as np, time, warnings, gc
from scipy import sparse
warnings.filterwarnings('ignore')

start = time.time()
print('INTERCEPTA Step 3b: Fix KAALCURA — z-score GLOBALLY, then average per population')

DATADIR = '/Users/kalki/INTERCEPTA/data/scrna/GSE141445'
RESULTS = '/Users/kalki/INTERCEPTA/results'

# Reload
print('\nLoading...')
chunk_iter = pd.read_csv(f'{DATADIR}/GSM4203181_data.matrix.txt.gz',
    sep='\t', index_col=0, compression='gzip', chunksize=5000)
chunks = []; gn = []; cn = None
for i, chunk in enumerate(chunk_iter):
    if cn is None: cn = chunk.columns.tolist()
    chunks.append(sparse.csr_matrix(chunk.values.astype(np.float32)))
    gn.extend(chunk.index.tolist())
data = sparse.vstack(chunks); del chunks; gc.collect()

# QC
ng0, nc0 = data.shape
gpc = np.array((data>0).sum(axis=0)).flatten()
cmask = (gpc>500)&(gpc<5000)
data = data[:,cmask]
cn = [cn[i] for i in range(nc0) if cmask[i]]
gic = np.array((data>0).sum(axis=1)).flatten()
gmask = gic>10
data = data[gmask,:]
gn = [gn[i] for i in range(ng0) if gmask[i]]

# Normalize
dt = data.T.tocsr()
totals = np.array(dt.sum(axis=1)).flatten()
dt = dt.multiply((10000.0/totals).reshape(-1,1))
dt.data = np.log1p(dt.data)
data_log = dt.T.tocsr()
del dt; gc.collect()
ng, nc = data_log.shape
print(f'  {ng} genes x {nc} cells ({time.time()-start:.0f}s)')

# Load cell types from previous run
ctypes = pd.read_csv(f'{RESULTS}/step3_cell_type_assignments.csv', index_col=0, header=0)
ctypes.columns = ['cell_type']
ctypes = ctypes['cell_type']

gi = {g:i for i,g in enumerate(gn)}
ci = {n:i for i,n in enumerate(cn)}

# Gene sets
prolif = ['MKI67','TOP2A','PCNA','CDK1','CCNB1','AURKA','BUB1','PLK1','MCM2','MCM6','FOXM1','BIRC5','NUSAP1','TPX2','CDC20','CENPF']
emt_pos = ['VIM','CDH2','SNAI1','SNAI2','ZEB1','ZEB2','TWIST1','FN1']
emt_neg = ['CDH1','CLDN1','TJP1']
ddr = ['BRCA1','BRCA2','RAD51','ATM','ATR','CHEK1','CHEK2','PARP1','PARP2','XRCC1','MLH1','MSH2','FANCA','FANCD2','RPA1']

def compute_global_axis(genes, data_log, gi, all_cell_indices):
    """Z-score GLOBALLY across all cells, return per-cell scores."""
    present = [g for g in genes if g in gi]
    if not present: return np.zeros(len(all_cell_indices))
    idx = [gi[g] for g in present]
    # Extract expression for these genes across ALL cells
    vals = np.array(data_log[idx, :].todense())  # genes x all_cells
    # Z-score each gene across ALL cells
    z = np.zeros_like(vals, dtype=np.float64)
    for r in range(vals.shape[0]):
        mu = vals[r,:].mean()
        s = vals[r,:].std()
        if s > 0:
            z[r,:] = (vals[r,:] - mu) / s
    # Mean z-score across genes = axis score per cell
    return z.mean(axis=0).flatten()

print('\nComputing GLOBAL z-scored axes for ALL cells...')
all_idx = list(range(nc))

rp_all = compute_global_axis(prolif, data_log, gi, all_idx)
print(f'  R_prolif: global mean={rp_all.mean():.4f} std={rp_all.std():.3f}')

re_pos_all = compute_global_axis(emt_pos, data_log, gi, all_idx)
re_neg_all = compute_global_axis(emt_neg, data_log, gi, all_idx)
re_all = (re_pos_all - re_neg_all) / 2
print(f'  R_emt:    global mean={re_all.mean():.4f} std={re_all.std():.3f}')

rd_all = compute_global_axis(ddr, data_log, gi, all_idx)
print(f'  R_ddr:    global mean={rd_all.mean():.4f} std={rd_all.std():.3f}')

# Now compute mean per population
print(f'\nKAALCURA per population (globally z-scored):')
print(f'  {"Pop":<15} {"N":>7} {"R_prolif":>9} {"R_emt":>9} {"R_ddr":>9}')
print(f'  {"-"*15} {"-"*7} {"-"*9} {"-"*9} {"-"*9}')

results = []
for ct in ctypes.value_counts().index:
    ct_cells = ctypes[ctypes==ct].index.tolist()
    idx = [ci[c] for c in ct_cells if c in ci]
    if len(idx) < 20: continue
    
    rp = rp_all[idx].mean()
    re = re_all[idx].mean()
    rd = rd_all[idx].mean()
    
    results.append({'cell_type':ct, 'n_cells':len(idx),
                    'R_prolif':round(rp,4), 'R_emt':round(re,4), 'R_ddr':round(rd,4)})
    print(f'  {ct:<15} {len(idx):>7} {rp:>+9.4f} {re:>+9.4f} {rd:>+9.4f}')

kdf = pd.DataFrame(results)

print(f'\nBiological insights:')
mp = kdf.loc[kdf['R_prolif'].idxmax()]
md = kdf.loc[kdf['R_ddr'].idxmax()]
me = kdf.loc[kdf['R_emt'].idxmax()]
ml = kdf.loc[kdf['R_prolif'].idxmin()]
print(f'  MOST proliferative (chemo-sensitive): {mp["cell_type"]} (R_prolif={mp["R_prolif"]:+.4f})')
print(f'  LEAST proliferative (chemo-resistant): {ml["cell_type"]} (R_prolif={ml["R_prolif"]:+.4f})')
print(f'  Highest DDR (PARPi-sensitive): {md["cell_type"]} (R_ddr={md["R_ddr"]:+.4f})')
print(f'  Most mesenchymal (drug-resistant): {me["cell_type"]} (R_emt={me["R_emt"]:+.4f})')

# Drug sensitivity predictions per population
print(f'\nDrug sensitivity predictions:')
for _, row in kdf.iterrows():
    ct = row['cell_type']
    chemo = 'SENSITIVE' if row['R_prolif'] > 0 else 'RESISTANT'
    parpi = 'SENSITIVE' if row['R_ddr'] > 0 else 'RESISTANT'
    tki = 'RESISTANT' if row['R_emt'] > 0 else 'SENSITIVE'
    print(f'  {ct:<15} Chemo:{chemo:<10} PARPi:{parpi:<10} TKI:{tki:<10}')

kdf.to_csv(f'{RESULTS}/step3_kaalcura_per_population.csv', index=False)
print(f'\nRuntime: {time.time()-start:.0f}s')
print(f'Saved to ~/INTERCEPTA/results/step3_kaalcura_per_population.csv')
