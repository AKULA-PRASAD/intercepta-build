#!/usr/bin/env python3
"""
Quick diagnostic: list all 85 drugs in Round 2.2c eval set + their R_prolif importance.
No model re-runs. Just inspects the existing per_drug_full.csv and feature_importance_full.csv.
"""
import pandas as pd
from pathlib import Path

HOME = Path.home()
ROUND2_2C = HOME / 'INTERCEPTA' / 'round2_aml' / 'results' / 'round2_2c'

per_drug = pd.read_csv(ROUND2_2C / 'per_drug_full.csv')
imp = pd.read_csv(ROUND2_2C / 'feature_importance_full.csv')

# R_prolif importance per drug
rprolif = imp[imp['feature'] == 'R_prolif'][['drug', 'gain_normalized']].set_index('drug')

# Merge
out = per_drug[['drug', 'auroc_test_mean']].copy()
out['rprolif_importance'] = out['drug'].map(rprolif['gain_normalized']).fillna(0)
out = out.sort_values('rprolif_importance', ascending=False)

print(f"All 85 drugs in eval set, sorted by R_prolif importance:\n")
print(out.to_string(index=False))
print(f"\nDrug count: {len(out)}")
print(f"R_prolif importance mean: {out['rprolif_importance'].mean():.4f}")
print(f"R_prolif importance > 0: {(out['rprolif_importance'] > 0).sum()}")
