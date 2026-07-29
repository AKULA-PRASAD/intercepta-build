#!/usr/bin/env python3
"""
Derive phenotypic diffusion rate (beta) from RNA velocity magnitudes.
"""
import scanpy as sc
import numpy as np
import pandas as pd
import json
import os

OUTDIR = f"/scratch/{os.environ['USER']}/INTERCEPTA/results"
H5AD = f"{OUTDIR}/velocity_star_full.h5ad"

print("Loading velocity h5ad...")
adata = sc.read_h5ad(H5AD)
print(f"  {adata.n_obs} cells x {adata.n_vars} genes")

lt = adata.obs['latent_time'].values
print(f"  latent_time range: {lt.min():.3f} to {lt.max():.3f}")

vel = adata.layers['velocity']
if hasattr(vel, 'toarray'):
    vel = vel.toarray()

vel_mag = np.sqrt(np.nansum(vel**2, axis=1))
print(f"  Velocity magnitudes: mean={np.nanmean(vel_mag):.4f}, median={np.nanmedian(vel_mag):.4f}")

clusters = adata.obs['leiden'].values
results = []
for cid in sorted(np.unique(clusters), key=int):
    mask = clusters == cid
    n = mask.sum()
    mean_lt = lt[mask].mean()
    std_lt = lt[mask].std()
    mean_vel = np.nanmean(vel_mag[mask])
    results.append({
        'cluster': int(cid), 'n_cells': int(n),
        'mean_latent_time': float(mean_lt), 'std_latent_time': float(std_lt),
        'mean_velocity_magnitude': float(mean_vel),
    })
    print(f"  Cluster {cid:>2}: n={n:>5} lt={mean_lt:.3f}+/-{std_lt:.3f} vel={mean_vel:.4f}")

df = pd.DataFrame(results)
df.to_csv(f"{OUTDIR}/velocity_magnitudes_per_cluster.csv", index=False)

cell_cycle_days = 3.0
overall_var = np.var(lt)
within_cluster_var = np.mean([r['std_latent_time']**2 for r in results])

beta_estimate = within_cluster_var / (2 * cell_cycle_days)
print(f"\nBeta estimate: {beta_estimate:.6e} /day")
print(f"  Current model value: 5e-5")
print(f"  Ratio: {beta_estimate / 5e-5:.1f}x")

derivation = {
    'beta_estimate': float(beta_estimate),
    'method': 'within_cluster_variance / (2 * cell_cycle_days)',
    'within_cluster_var': float(within_cluster_var),
    'cell_cycle_days': cell_cycle_days,
    'current_model_value': 5e-5,
    'n_cells': int(adata.n_obs),
}
with open(f"{OUTDIR}/beta_derivation.json", 'w') as f:
    json.dump(derivation, f, indent=2)
print("DONE")
