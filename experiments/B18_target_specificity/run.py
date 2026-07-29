"""B18 — is the inferred-dependency layer TARGET-SPECIFIC? Double dissociation FLT3 vs BCL2.
Implements prereg/B18_target_specificity.md. Proliferation-adjusted Spearman matrix + permutation test.
Diagonal (matched target->drug) should beat off-diagonal (mismatched) if the layer reads target-specific
vulnerability rather than generic sensitivity. Reproduce x2. Aggregate outputs only.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
import warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.engine import InterceptaEngine
from intercepta.axes import compute_r_prolif

SEED, MIN_N, NPERM = 42, 25, 10000
HERE = os.path.dirname(os.path.abspath(__file__))
FLT3I = ["sorafenib", "quizartinib", "gilteritinib", "crenolanib"]
BCL2I = ["venetoclax"]
DRUG2TARGET = {**{d: "FLT3" for d in FLT3I}, **{d: "BCL2" for d in BCL2I}}
TARGETS = ["FLT3", "BCL2"]
rng = np.random.default_rng(SEED)

def resid(x, c):
    x = np.asarray(x, float); c = np.asarray(c, float)
    A = np.column_stack([np.ones_like(c), c]); b, *_ = np.linalg.lstsq(A, x, rcond=None)
    return x - A @ b

# engine: learn FLT3 + BCL2 dependency from expression, infer on BeatAML patients
eng = InterceptaEngine().fit(drugs=FLT3I + BCL2I, compute_calibration=False, label_source="prism")
eng.fit_dependency(TARGETS)
learn = getattr(eng, "dep_cv_rho_dep_", {}) or {}      # learnability CV rho (established in B15/V16)
bx = D.load_beataml_expression()
inf = eng.infer_dependency(bx)                          # DataFrame samples x {FLT3,BCL2}, gene-effect
Rp = compute_r_prolif(bx)
auc = D.load_beataml_auc(); auc = auc[auc["sample"].isin(set(bx.columns))]
print(f"B18 target-specificity | BeatAML samples={bx.shape[1]}  targets learned={list(eng.dep_models_)}  (learnability CV rho: B15/V16)", flush=True)

# proliferation-adjusted Spearman for every (target, drug) cell
cells = []   # dict per cell
for drug in FLT3I + BCL2I:
    a = auc[auc["drug"] == drug].groupby("sample")["auc"].mean()
    for tgt in TARGETS:
        dep = inf[tgt]
        S = [s for s in a.index if s in dep.index and s in Rp.index]
        if len(S) < MIN_N:
            continue
        y = a[S].values; dvals = dep[S].values; rp = Rp[S].values
        rho = float(stats.spearmanr(resid(dvals, rp), resid(y, rp))[0])   # + = sensitizing (target-consistent)
        _, p = stats.spearmanr(resid(dvals, rp), resid(y, rp))
        cells.append({"drug": drug, "target": tgt, "matched": DRUG2TARGET[drug] == tgt,
                      "n": len(S), "rho_prolif_adj": round(rho, 4), "p": float(p)})

diag = [c["rho_prolif_adj"] for c in cells if c["matched"]]
offd = [c["rho_prolif_adj"] for c in cells if not c["matched"]]
gap_obs = float(np.mean(diag) - np.mean(offd))

# permutation: reshuffle target labels across the drug axis (break matched/mismatched structure)
# recompute gap = mean(rho where perm-matched) - mean(rho where perm-mismatched)
rho_by = {(c["drug"], c["target"]): c["rho_prolif_adj"] for c in cells}
drugs_present = sorted({c["drug"] for c in cells})
true_tgt = {d: DRUG2TARGET[d] for d in drugs_present}
perm_gaps = []
for _ in range(NPERM):
    perm = dict(zip(drugs_present, rng.permutation([true_tgt[d] for d in drugs_present])))
    dm = [rho_by[(d, perm[d])] for d in drugs_present if (d, perm[d]) in rho_by]
    om = [rho_by[(d, t)] for d in drugs_present for t in TARGETS if t != perm[d] and (d, t) in rho_by]
    if dm and om:
        perm_gaps.append(np.mean(dm) - np.mean(om))
perm_gaps = np.array(perm_gaps)
p_h1 = float((1 + np.sum(perm_gaps >= gap_obs)) / (1 + len(perm_gaps)))
H1 = bool(gap_obs > 0 and p_h1 < 0.05)

# H2: BCL2 pillar (venetoclax diagonal sensitizing & specific)
ven_diag = next((c for c in cells if c["drug"] == "venetoclax" and c["target"] == "BCL2"), None)
bcl2_on_flt3i = [c for c in cells if c["target"] == "BCL2" and c["drug"] in FLT3I]
def pooled(cs):  # sample-size-weighted mean rho + Stouffer one-sided (sensitizing) p
    if not cs: return None
    ns = np.array([c["n"] for c in cs]); rs = np.array([c["rho_prolif_adj"] for c in cs])
    zc = np.arctanh(np.clip(rs, -.999, .999)); zmu = np.sum(zc * (ns - 3)) / np.sum(ns - 3)
    Z = zmu * np.sqrt(np.sum(ns - 3)); return {"pooled_rho": round(float(np.sum(ns * rs) / np.sum(ns)), 4),
                                               "stouffer_Z": round(float(Z), 3), "one_sided_p": float(stats.norm.sf(Z))}
bcl2_flt3i_pool = pooled(bcl2_on_flt3i)
H2 = bool(ven_diag and ven_diag["rho_prolif_adj"] > 0 and ven_diag["p"] < 0.05
          and (bcl2_flt3i_pool is None or bcl2_flt3i_pool["one_sided_p"] > 0.05))

# H3: FLT3 pillar (FLT3i diagonal sensitizing & specific vs venetoclax)
flt3_on_flt3i = [c for c in cells if c["target"] == "FLT3" and c["drug"] in FLT3I]
flt3_on_ven = next((c for c in cells if c["target"] == "FLT3" and c["drug"] == "venetoclax"), None)
flt3_flt3i_pool = pooled(flt3_on_flt3i)
H3 = bool(flt3_flt3i_pool and flt3_flt3i_pool["pooled_rho"] > 0 and flt3_flt3i_pool["one_sided_p"] < 0.05
          and (flt3_on_ven is None or not (flt3_on_ven["rho_prolif_adj"] > 0 and flt3_on_ven["p"] < 0.05)))

print("\nProliferation-adjusted specificity matrix (rho; + = target-consistent sensitizing):")
print(f"  {'drug':<13} {'FLT3-dep':>10} {'BCL2-dep':>10}   (diagonal = matched target)")
for drug in FLT3I + BCL2I:
    r = {c["target"]: c for c in cells if c["drug"] == drug}
    f = r.get("FLT3"); b = r.get("BCL2")
    fs = f"{f['rho_prolif_adj']:+.3f}{'*' if f and DRUG2TARGET[drug]=='FLT3' else ' '}" if f else "   -  "
    bs = f"{b['rho_prolif_adj']:+.3f}{'*' if b and DRUG2TARGET[drug]=='BCL2' else ' '}" if b else "   -  "
    print(f"  {drug:<13} {fs:>10} {bs:>10}")
print(f"\nmean diagonal rho={np.mean(diag):+.3f}  mean off-diagonal rho={np.mean(offd):+.3f}  gap={gap_obs:+.3f}")
print(f"H1 specificity (diag>off, perm p): p={p_h1:.4g} -> {H1}")
print(f"H2 BCL2 pillar: venetoclax<-BCL2-dep rho={ven_diag['rho_prolif_adj'] if ven_diag else None} p={ven_diag['p'] if ven_diag else None:.3g} | BCL2-dep->FLT3i pooled={bcl2_flt3i_pool} -> {H2}")
print(f"H3 FLT3 pillar: FLT3i<-FLT3-dep pooled={flt3_flt3i_pool} | FLT3-dep->venetoclax rho={flt3_on_ven['rho_prolif_adj'] if flt3_on_ven else None} -> {H3}")

if H1 and H2 and H3:
    verdict = ("TARGET-SPECIFIC (double dissociation): inferred-dependency reads WHICH vulnerability (FLT3 vs BCL2) "
               "a tumor has, not generic sensitivity — V19 generalizes to a second independent AML pillar.")
elif H1:
    verdict = "Layer is target-specific overall (diag>off), but one pillar's double-dissociation is incomplete — partial, honest."
elif H3 and not H2:
    verdict = "FLT3 pillar specific (V19), but BCL2/venetoclax not cleanly dependency-encoded in RNA — venetoclax response is more complex; honest partial."
else:
    verdict = "NOT target-specific: off-diagonal ~ diagonal; layer reads generic sensitivity, not target vulnerability — V19 is FLT3-specific only (honest bound)."
print("VERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": SEED, "n_perm": int(len(perm_gaps)),
       "learnable_cv_rho": {k: round(float(v), 4) for k, v in learn.items()},
       "cells": cells, "mean_diagonal_rho": round(float(np.mean(diag)), 4), "mean_offdiagonal_rho": round(float(np.mean(offd)), 4),
       "gap": round(gap_obs, 4), "H1_perm_p": p_h1, "H1_pass": H1,
       "H2_venetoclax_diag": ven_diag, "H2_bcl2_on_flt3i_pooled": bcl2_flt3i_pool, "H2_pass": H2,
       "H3_flt3i_pooled": flt3_flt3i_pool, "H3_flt3_on_venetoclax": flt3_on_ven, "H3_pass": H3,
       "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B18_metrics.json"), "w"), indent=2)
print("wrote results/B18_metrics.json")
