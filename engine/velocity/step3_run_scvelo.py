"""
INTERCEPTA Step 3: Run scVelo on STARsolo velocity output.
"""
import scvelo as scv
import scanpy as sc
import anndata as ad
import numpy as np
import pandas as pd
import os, glob
from scipy.io import mmread
from scipy import sparse

WORKDIR = os.path.expanduser("~/INTERCEPTA/data/velocity")
RESULTS = os.path.expanduser("~/INTERCEPTA/results")

print("INTERCEPTA: Running scVelo on velocity data")
print("=" * 60)

# Find velocity matrices
velo_dir = os.path.join(WORKDIR, "velocity_out")
spliced_files = sorted(glob.glob(f"{velo_dir}/*_spliced.mtx"))

if not spliced_files:
    print("ERROR: No velocity matrices found.")
    print(f"  Looked in: {velo_dir}")
    exit(1)

print(f"Found {len(spliced_files)} samples with velocity data")

adatas = []
for sf in spliced_files:
    sample = os.path.basename(sf).replace("_spliced.mtx", "")
    base = os.path.join(velo_dir, sample)
    
    try:
        spliced = mmread(f"{base}_spliced.mtx").T.tocsr()
        unspliced = mmread(f"{base}_unspliced.mtx").T.tocsr()
        
        # Load barcodes and features
        barcodes = pd.read_csv(f"{base}_barcodes.tsv", header=None)[0].values
        features = pd.read_csv(f"{base}_features.tsv", header=None, sep='\t')
        gene_names = features[1].values if features.shape[1] > 1 else features[0].values
        
        adata = ad.AnnData(X=spliced)
        adata.layers["spliced"] = spliced
        adata.layers["unspliced"] = unspliced
        adata.obs_names = [f"{sample}_{bc}" for bc in barcodes]
        adata.var_names = gene_names
        adata.obs["sample"] = sample
        
        adatas.append(adata)
        print(f"  {sample}: {adata.n_obs} cells x {adata.n_vars} genes")
    except Exception as e:
        print(f"  {sample}: Error - {e}")

if not adatas:
    print("ERROR: No data loaded.")
    exit(1)

# Merge
adata = ad.concat(adatas)
adata.var_names_make_unique()
print(f"\nMerged: {adata.n_obs} cells x {adata.n_vars} genes")

# QC
sc.pp.filter_cells(adata, min_genes=500)
sc.pp.filter_genes(adata, min_cells=10)
print(f"After QC: {adata.n_obs} cells x {adata.n_vars} genes")

# Preprocessing for velocity
scv.pp.filter_and_normalize(adata, min_shared_counts=20, n_top_genes=2000)
scv.pp.moments(adata, n_pcs=30, n_neighbors=30)

# Dynamical mode - the full RNA velocity
print("\nRunning dynamical model (this may take 30-60 min)...")
scv.tl.recover_dynamics(adata, n_jobs=4)
scv.tl.velocity(adata, mode="dynamical")
scv.tl.velocity_graph(adata)
scv.tl.latent_time(adata)

# Clustering
sc.tl.leiden(adata, resolution=0.5)

print("\nRNA Velocity COMPLETE")
print(f"  Cells: {adata.n_obs}")
print(f"  Latent time: {adata.obs['latent_time'].min():.3f} to {adata.obs['latent_time'].max():.3f}")

# Save
adata.write(f"{RESULTS}/step3_velocity_adata.h5ad")
adata.obs[['sample','leiden','latent_time']].to_csv(f"{RESULTS}/step3_velocity_results.csv")

# Identify cells transitioning toward resistance
print("\nAnalyzing transition trajectories...")
# Cells with high latent time are further along the trajectory
late_cells = adata.obs[adata.obs['latent_time'] > 0.8]
early_cells = adata.obs[adata.obs['latent_time'] < 0.2]
print(f"  Early state cells (latent_time < 0.2): {len(early_cells)}")
print(f"  Late state cells (latent_time > 0.8): {len(late_cells)}")
print(f"  Late-state = high scVelo latent_time (pseudotime/magnitude only).")
print(f"  NOTE (LEDGER/README): latent_time is NOT a drug-response/resistance readout — there is no per-cell")
print(f"  resistance ground truth here, so any 'pre-resistance / time-machine' interpretation is NOT TESTABLE.")

print(f"\nSaved to {RESULTS}/step3_velocity_adata.h5ad")
