"""Validation of the shipped SynergyRanker module on real open O'Neil data + DepMap expression.
Confirms the module reproduces the V23 leave-drug-combination-out generalization (~0.6) with the reproducible
DepMap-expression + fingerprint pipeline it ships with, and demonstrates rank_pairs. Reproduce x2.
"""
import os, sys, json, time
import numpy as np, pandas as pd
import warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.synergy import SynergyRanker

HERE = os.path.dirname(os.path.abspath(__file__))
r = SynergyRanker.from_oneil()          # fits + computes leave-combination-out CV rho
print(f"SynergyRanker fitted | library={len(r.library_)} drugs | genes={len(r.genes_)}")
print(f"leave-drug-combination-out CV Spearman = {r.cv_leave_combination_rho_:.4f}  (V23/B24 O'Neil ~0.61)")

# demo: rank pairs for a few held-in cell lines' own expression (as query)
rna = D.load_depmap_expression()
demo_cells = [c for c in rna.index][:3]
q = rna.loc[demo_cells].T                # genes x samples
ranked = r.rank_pairs(q, top=3)
print("\nrank_pairs demo (top-3 synergistic pairs per query cell):")
print(ranked.to_string(index=False))

out = {"python": sys.version.split()[0], "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "n_library_drugs": len(r.library_), "n_genes": len(r.genes_),
       "leave_combination_out_cv_spearman": round(float(r.cv_leave_combination_rho_), 4),
       "note": "Module ships the reproducible DepMap-expression + Morgan-fingerprint pipeline validated in B24/B26. "
               "Scope: cell-line Loewe synergy, KNOWN-drug library only, OOD-gated, not clinical.",
       "demo_top_pairs": ranked.to_dict("records")}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "synergy_module_validation.json"), "w"), indent=2)
print("\nwrote results/synergy_module_validation.json")
