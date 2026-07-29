import pandas as pd, numpy as np, time, warnings, gc
from scipy import sparse
warnings.filterwarnings('ignore')

start = time.time()
print('=' * 70)
print('INTERCEPTA Step 3: scRNA-seq Cell Population + KAALCURA')
print('=' * 70)

DATADIR = '/Users/kalki/INTERCEPTA/data/scrna/GSE141445'
RESULTS = '/Users/kalki/INTERCEPTA/results'

print('\n[1/5] Loading sparse matrix...')
chunk_iter = pd.read_csv(
    f'{DATADIR}/GSM4203181_data.matrix.txt.gz',
    sep='\t', index_col=0, compression='gzip', chunksize=5000)

chunks = []; gene_names = []; cell_names = None
for i, chunk in enumerate(chunk_iter):
    if cell_names is None: cell_names = chunk.columns.tolist()
    chunks.append(sparse.csr_matrix(chunk.values.astype(np.float32)))
    gene_names.extend(chunk.index.tolist())
    if (i+1)%2==0: print(f'  {(i+1)*5000} genes...')

data = sparse.vstack(chunks); del chunks; gc.collect()
print(f'  {data.shape[0]} genes x {data.shape[1]} cells ({time.time()-start:.0f}s)')

print('\n[2/5] QC + Normalize...')
n_genes, n_cells = data.shape
gpc = np.array((data>0).sum(axis=0)).flatten()
cmask = (gpc>500)&(gpc<5000)
data = data[:,cmask]
cn = [cell_names[i] for i in range(n_cells) if cmask[i]]
gic = np.array((data>0).sum(axis=1)).flatten()
gmask = gic>10
data = data[gmask,:]
gn = [gene_names[i] for i in range(n_genes) if gmask[i]]
ng, nc = data.shape
print(f'  {ng} genes x {nc} cells after QC')

# Normalize: transpose, scale, log
dt = data.T.tocsr()
totals = np.array(dt.sum(axis=1)).flatten()
dt = dt.multiply((10000.0/totals).reshape(-1,1))
dt.data = np.log1p(dt.data)
data_log = dt.T.tocsr()
del dt; gc.collect()
print(f'  Normalized + log1p ({time.time()-start:.0f}s)')

print('\n[3/5] Identifying cell types...')
markers = {
    'Epithelial':['EPCAM','KRT8','KRT18','CDH1'],
    'Luminal':['KLK3','AR','NKX3-1','TMPRSS2'],
    'T_cell':['CD3D','CD3E','CD8A','CD4','IL7R'],
    'Macrophage':['CD68','CD163','CSF1R','SPP1'],
    'Fibroblast':['COL1A1','DCN','LUM','ACTA2'],
    'Endothelial':['PECAM1','VWF','CDH5'],
    'NK_cell':['NKG7','GNLY'],
    'NE_like':['SYP','CHGA','ENO2','NCAM1'],
}
gi = {g:i for i,g in enumerate(gn)}

scores = {}
for ct, genes in markers.items():
    p = [g for g in genes if g in gi]
    if not p: continue
    idx = [gi[g] for g in p]
    scores[ct] = np.array(data_log[idx,:].mean(axis=0)).flatten()

sdf = pd.DataFrame(scores, index=cn)
ctypes = sdf.idxmax(axis=1)

print(f'\n  Cell type distribution:')
for ct, count in ctypes.value_counts().items():
    print(f'    {ct:<15} {count:>7} ({count/len(ctypes)*100:.1f}%)')

print('\n[4/5] KAALCURA axes per population...')
prolif = ['MKI67','TOP2A','PCNA','CDK1','CCNB1','AURKA','BUB1','PLK1','MCM2','MCM6','FOXM1','BIRC5','NUSAP1','TPX2','CDC20','CENPF']
emt_pos = ['VIM','CDH2','SNAI1','SNAI2','ZEB1','ZEB2','TWIST1','FN1']
emt_neg = ['CDH1','CLDN1','TJP1']
ddr = ['BRCA1','BRCA2','RAD51','ATM','ATR','CHEK1','CHEK2','PARP1','PARP2','XRCC1','MLH1','MSH2','FANCA','FANCD2','RPA1']

def ax(genes, cidx):
    p = [g for g in genes if g in gi]
    if not p: return np.zeros(len(cidx))
    ix = [gi[g] for g in p]
    v = np.array(data_log[ix,:][:,cidx].todense())
    z = np.zeros_like(v, dtype=np.float64)
    for r in range(v.shape[0]):
        s = v[r,:].std()
        if s>0: z[r,:] = (v[r,:]-v[r,:].mean())/s
    return z.mean(axis=0).flatten()

ci = {n:i for i,n in enumerate(cn)}
res = []

print(f'\n  {"Pop":<15} {"N":>7} {"R_prolif":>9} {"R_emt":>9} {"R_ddr":>9}')
print(f'  {"-"*15} {"-"*7} {"-"*9} {"-"*9} {"-"*9}')

for ct in ctypes.value_counts().index:
    cells = ctypes[ctypes==ct].index.tolist()
    idx = [ci[c] for c in cells if c in ci]
    if len(idx)<20: continue
    rp = ax(prolif, idx)
    rep = ax(emt_pos, idx)
    ren = ax(emt_neg, idx)
    re = (np.array(rep) - np.array(ren)) / 2
    rd = ax(ddr, idx)
    res.append({'cell_type':ct, 'n_cells':len(idx),
                'R_prolif':float(np.mean(rp)), 'R_emt':float(np.mean(re)),
                'R_ddr':float(np.mean(rd))})
    print(f'  {ct:<15} {len(idx):>7} {np.mean(rp):>+9.3f} {np.mean(re):>+9.3f} {np.mean(rd):>+9.3f}')

print('\n[5/5] Biological insights...')
kdf = pd.DataFrame(res)
mp = kdf.loc[kdf['R_prolif'].idxmax()]
md = kdf.loc[kdf['R_ddr'].idxmax()]
me = kdf.loc[kdf['R_emt'].idxmax()]
print(f'  Most proliferative (chemo-sensitive): {mp["cell_type"]} (R_prolif={mp["R_prolif"]:+.3f})')
print(f'  Highest DDR (PARPi-sensitive): {md["cell_type"]} (R_ddr={md["R_ddr"]:+.3f})')
print(f'  Most mesenchymal (resistant): {me["cell_type"]} (R_emt={me["R_emt"]:+.3f})')

kdf.to_csv(f'{RESULTS}/step3_kaalcura_per_population.csv', index=False)
ctypes.to_csv(f'{RESULTS}/step3_cell_type_assignments.csv')

print(f'\n{"="*70}')
print(f'STEP 3 COMPLETE: {nc:,} cells, {len(ctypes.value_counts())} populations')
print(f'Runtime: {time.time()-start:.0f}s ({(time.time()-start)/60:.1f} min)')
print(f'Saved to ~/INTERCEPTA/results/step3_*.csv')
print(f'{"="*70}')
