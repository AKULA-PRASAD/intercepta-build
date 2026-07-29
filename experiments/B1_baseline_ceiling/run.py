"""B1 — the honest baseline ceiling, re-established inside the clean build repo.

Implements prereg/B1_baseline_ceiling.md. Per-drug RidgeCV trained on GDSC z-expression -> LN_IC50, applied
to CCLE z-expression, scored by per-drug Spearman vs PRISM AUC. Two designs are reported:
  * LEAKY   — GDSC training includes the same cell lines used in CCLE test (inflated; NOT valid).
  * STRICT  — every test cell line's COSMIC removed from training -> disjoint cell lines (the valid ceiling).
Bar: parameter-free frozen R_prolif. Ported faithfully from the verified ~/kaalcura V1B run; must reproduce
mean STRICT per-drug rho = +0.212. Deterministic (Ridge closed-form); reproduce x2.
"""
import os, sys, json, time
import numpy as np
from scipy import stats
from sklearn.linear_model import RidgeCV
import sklearn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.splits import disjoint_train_cosmics
from intercepta.metrics import per_drug_spearman, paired_wilcoxon
from intercepta.axes import compute_r_prolif

TOPN = 2000
HERE = os.path.dirname(os.path.abspath(__file__))

print("B1 baseline ceiling (per-drug RidgeCV, GDSC->CCLE) | sklearn", sklearn.__version__, flush=True)

cos2dep, dep2cos = D.load_cosmic_depmap_map()
gdsc = D.load_gdsc_response()
prism = D.load_prism()
gx = D.load_gdsc_expression()                       # genes x cells (COSMIC)
dx = D.load_depmap_expression()                     # cells x genes (symbol)
Rp_ccle = compute_r_prolif(dx.T)                    # frozen R_prolif per CCLE cell

shared_genes = [g for g in gx.index if g in set(dx.columns)]
v = gx.loc[shared_genes].var(1).sort_values(ascending=False)
genes = list(v.head(TOPN).index)
gxz = D.z_rows(gx.loc[genes]).fillna(0.0)           # genes x cells (COSMIC)
dxz = D.z_rows(dx[genes].T).fillna(0.0)             # genes x cells (DepMap)

gl = {d.lower(): d for d in gdsc["DRUG_NAME"].unique()}
pl = {d.lower(): d for d in prism["name"].unique()}
shared = sorted(set(gl) & set(pl))
gdsc_cos = set(gx.columns)
shared_cells = (set(cos2dep.get(c) for c in gdsc["COSMIC_ID"].unique() if c in cos2dep)
                & set(dx.index) & set(Rp_ccle.index) & set(prism["depmap_id"].unique()))
prism_g = prism[prism["depmap_id"].isin(shared_cells)].copy()
prism_g["k"] = prism_g["name"].str.lower()
obs = prism_g[prism_g["k"].isin(shared)].groupby(["depmap_id", "k"])["auc"].mean()

leaky_rho, strict_rho, rprolif_rho, drugs_used = [], [], [], []
for dk in shared:
    tr_all = gdsc[(gdsc["DRUG_NAME"] == gl[dk]) & (gdsc["COSMIC_ID"].isin(gdsc_cos))]
    if len(tr_all) < 30:
        continue
    cells = [c for c in shared_cells if (c, dk) in obs.index]
    if len(cells) < 20:
        continue
    yte = np.array([obs[(c, dk)] for c in cells])
    Xte = dxz[cells].T.values
    tr_strict = disjoint_train_cosmics(tr_all, cells, dep2cos)   # leakage correction
    if len(tr_strict) < 30:
        continue

    def fit_pred(tr):
        m = RidgeCV(alphas=[10.0, 100.0, 1000.0]).fit(gxz[tr["COSMIC_ID"].values].T.values, tr["LN_IC50"].values)
        return m.predict(Xte)

    lr_leaky = per_drug_spearman(fit_pred(tr_all), yte)
    lr_strict = per_drug_spearman(fit_pred(tr_strict), yte)
    rp = per_drug_spearman([-float(Rp_ccle[c]) for c in cells], yte)
    if np.isfinite(lr_leaky) and np.isfinite(lr_strict) and np.isfinite(rp):
        leaky_rho.append(lr_leaky); strict_rho.append(lr_strict); rprolif_rho.append(rp); drugs_used.append(dk)

leaky_rho = np.array(leaky_rho); strict_rho = np.array(strict_rho); rprolif_rho = np.array(rprolif_rho)
w_stat, w_p = paired_wilcoxon(strict_rho, rprolif_rho)
beats = bool((strict_rho.mean() > rprolif_rho.mean()) and (w_p < 0.05))

print(f"\ndrugs evaluated: {len(drugs_used)}  (features: top-{TOPN} shared genes)")
print(f"LEAKY  mean rho={leaky_rho.mean():+.4f} median={np.median(leaky_rho):+.4f}  [inflated — not valid]")
print(f"STRICT mean rho={strict_rho.mean():+.4f} median={np.median(strict_rho):+.4f} frac>0={np.mean(strict_rho>0):.2f}  <-- the ceiling")
print(f"R_prolif bar: mean={rprolif_rho.mean():+.4f} median={np.median(rprolif_rho):+.4f}")
print(f"paired Wilcoxon (STRICT vs bar): W={w_stat:.1f} p={w_p:.4g}")
print(f"PRE-REGISTERED verdict: STRICT beats bar? {'YES' if beats else 'NO'}")

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "sklearn": sklearn.__version__, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "topN_genes": TOPN, "n_drugs": len(drugs_used),
       "leaky_mean_rho": round(float(leaky_rho.mean()), 4), "leaky_median_rho": round(float(np.median(leaky_rho)), 4),
       "strict_mean_rho": round(float(strict_rho.mean()), 4), "strict_median_rho": round(float(np.median(strict_rho)), 4),
       "strict_frac_pos": round(float(np.mean(strict_rho > 0)), 4),
       "rprolif_mean_rho": round(float(rprolif_rho.mean()), 4), "rprolif_median_rho": round(float(np.median(rprolif_rho)), 4),
       "wilcoxon_p_strict_vs_rprolif": float(w_p), "beats_bar_strict": beats,
       "expected_strict_mean_rho_from_kaalcura_V1B": 0.2124}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B1_metrics.json"), "w"), indent=2)
print("wrote results/B1_metrics.json")
