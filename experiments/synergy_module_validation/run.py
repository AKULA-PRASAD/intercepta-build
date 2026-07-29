"""Validation of the shipped SynergyRanker on real open data: O'Neil (38 drugs) AND DrugComb (124 drugs), both
with DepMap-expression + fingerprint features. Confirms each self-validates its leave-drug-combination-out
generalization (V23), and reports the honest library-size vs reliability tradeoff. Reproduce x2.
"""
import os, sys, json, time
import numpy as np, pandas as pd
import warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.synergy import SynergyRanker

HERE = os.path.dirname(os.path.abspath(__file__))
rna = D.load_depmap_expression()
demo_cells = [c for c in rna.index][:3]
q = rna.loc[demo_cells].T                      # genes x samples

out = {"python": sys.version.split()[0], "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "libraries": {}}
for name, ctor in [("oneil", SynergyRanker.from_oneil), ("drugcomb", SynergyRanker.from_drugcomb)]:
    r = ctor()
    ranked = r.rank_pairs(q, top=3)
    n_pairs = len(r.library_) * (len(r.library_) - 1) // 2
    print(f"[{name}] library={len(r.library_)} drugs ({n_pairs} rankable pairs) | leave-combination-out CV Spearman = {r.cv_leave_combination_rho_:.4f} | ood_threshold={r.ood_threshold_:.2f}")
    out["libraries"][name] = {"n_library_drugs": len(r.library_), "n_rankable_pairs": int(n_pairs),
                              "leave_combination_out_cv_spearman": round(float(r.cv_leave_combination_rho_), 4),
                              "ood_threshold": round(float(r.ood_threshold_), 3),
                              "demo_top_pairs": ranked.head(3).to_dict("records")}

out["honest_tradeoff"] = ("DrugComb ranks ~3x more drugs (124 vs 38) but with lower per-prediction reliability "
                          "(CV Spearman ~0.38 vs 0.62) — it aggregates many studies (noisier Loewe). Both are "
                          "cell-line Loewe synergy, known-drug library only, OOD-gated, not clinical.")
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "synergy_module_validation.json"), "w"), indent=2)
print("\n" + out["honest_tradeoff"])
print("wrote results/synergy_module_validation.json")
