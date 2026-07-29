"""B7 — EXTERNAL validation on PDXE (public patient-derived xenografts). Implements prereg/B7_pdxe_external.md.
Train engine on GDSC/DepMap; predict on PDXE RNA-seq; test transfer (H1) + proliferation-residualized
drug-specificity (H2) vs BestAvgResponse. Independent of BeatAML AND cell lines. Reproduce x2.
PDXE files (public, Gao 2015 nm.3954 MOESM10) read from INTERCEPTA_PDXE (default scratchpad); NOT committed.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
import sklearn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.engine import InterceptaEngine
from intercepta.axes import compute_r_prolif

SEED, K, MIN_MODELS = 42, 2000, 15
PDXE = os.environ.get("INTERCEPTA_PDXE", "/private/tmp/claude-501/-Users-kalki-kaalcura/285c6fb0-5803-4a7d-ba7b-c59f3e2d16c5/scratchpad")
SYN = {"byl719":"alpelisib","bkm120":"buparlisib","lee011":"ribociclib","lde225":"sonidegib","bgj398":"infigratinib",
       "ldk378":"ceritinib","lgx818":"encorafenib","mek162":"binimetinib","gemcitabine-50mpk":"gemcitabine",
       "binimetinib-3.5mpk":"binimetinib","5fu":"fluorouracil","inc280":"capmatinib"}
HERE = os.path.dirname(os.path.abspath(__file__))
print("B7 PDXE external validation | sklearn", sklearn.__version__, flush=True)

expr = pd.read_parquet(os.path.join(PDXE, "pdxe_rnaseq.parquet"))    # genes x PDX models
resp = pd.read_csv(os.path.join(PDXE, "pdxe_response.csv"))
resp["tx"] = resp["Treatment"].astype(str).str.strip().str.lower()
resp = resp[~resp["tx"].str.contains(r"\+", regex=True)].copy()
resp["drug"] = resp["tx"].map(lambda x: SYN.get(x, x))
resp = resp[resp["Model"].astype(str).isin(expr.columns)]
bar = resp.groupby(["Model", "drug"])["BestAvgResponse"].mean()

drugs = sorted(d for d in resp["drug"].unique() if resp[resp["drug"] == d]["Model"].nunique() >= MIN_MODELS)
eng = InterceptaEngine().fit(drugs=drugs, compute_calibration=False)
drugs = [d for d in drugs if d in eng.fitted_drugs_]
print("fitted+testable drugs:", drugs, flush=True)

pred = eng.predict_transfer(expr)                                    # models x drugs (z LN_IC50)
Rp = compute_r_prolif(expr)                                          # per model

def resid(x, c):
    x = np.asarray(x, float); c = np.asarray(c, float)
    A = np.column_stack([np.ones_like(c), c]); b, *_ = np.linalg.lstsq(A, x, rcond=None); return x - A @ b

cells_by = {}
for dk in drugs:
    m = [x for x in bar.xs(dk, level=1).index if x in pred.index]
    cells_by[dk] = m
usable = [d for d in drugs if len(cells_by[d]) >= MIN_MODELS]
diag, off, diag_r, off_r, rp_only = [], [], [], [], []
for dk in usable:
    cells = cells_by[dk]; y = bar.xs(dk, level=1)[cells].values; rp = Rp[cells].values
    p = pred.loc[cells, dk].values
    diag.append(stats.spearmanr(p, y)[0]); rp_only.append(stats.spearmanr(rp, y)[0])
    off.append(np.mean([stats.spearmanr(pred.loc[cells, dj].values, y)[0] for dj in usable if dj != dk]))
    yr = resid(y, rp)
    diag_r.append(stats.spearmanr(resid(p, rp), yr)[0])
    off_r.append(np.mean([stats.spearmanr(resid(pred.loc[cells, dj].values, rp), yr)[0] for dj in usable if dj != dk]))
diag, off, diag_r, off_r, rp_only = map(np.array, (diag, off, diag_r, off_r, rp_only))
n = len(usable); rng = np.random.default_rng(SEED)

# H1 transfer permutation
null1 = np.empty(K)
for i in range(K):
    null1[i] = np.mean([stats.spearmanr(pred.loc[cells_by[dk], dk].values, rng.permutation(bar.xs(dk, level=1)[cells_by[dk]].values))[0] for dk in usable])
p_h1 = (np.sum(null1 >= diag.mean()) + 1) / (K + 1)
H1 = bool(diag.mean() > 0 and p_h1 < 0.05)
# H2 specificity (residualized) sign-flip permutation
obs = diag_r.mean() - off_r.mean(); do = np.column_stack([diag_r, off_r]); null2 = np.empty(K)
for i in range(K):
    f = rng.integers(0, 2, n).astype(bool)
    null2[i] = np.where(f, do[:,1], do[:,0]).mean() - np.where(f, do[:,0], do[:,1]).mean()
p_h2 = (np.sum(null2 >= obs) + 1) / (K + 1)
H2 = bool(obs > 0 and diag_r.mean() > 0 and p_h2 < 0.05)

print(f"\nusable drugs: {n} {usable}")
print(f"H1 transfer: diagonal mean ρ={diag.mean():+.4f} (off={off.mean():+.4f}) perm p={p_h1:.4g} -> {H1}")
print(f"    R_prolif-only transfer ρ={rp_only.mean():+.4f}")
print(f"H2 drug-specific (prolif-residualized): diag_r={diag_r.mean():+.4f} off_r={off_r.mean():+.4f} diff={obs:+.4f} perm p={p_h2:.4g} -> {H2}")
verdict = ("EXTERNAL VALIDATION: transfer generalizes to PDXE" + (" AND is drug-specific beyond proliferation (V9 replicates externally!)" if H2 else " but drug-specificity does NOT externally replicate (generic proliferation transfer)")) if H1 else "NULL: transfer does not generalize to PDXE"
print(f"VERDICT: {verdict}")

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "sklearn": sklearn.__version__, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "seed": SEED, "K": K, "cohort": "PDXE (Gao 2015 nm.3954; public PDX)", "n_drugs": n, "drugs": usable,
       "H1_diag_mean_rho": round(float(diag.mean()), 4), "offdiag_mean_rho": round(float(off.mean()), 4),
       "rprolif_only_rho": round(float(rp_only.mean()), 4), "H1_perm_p": float(p_h1), "H1_transfer_pass": H1,
       "H2_resid_diag": round(float(diag_r.mean()), 4), "H2_resid_off": round(float(off_r.mean()), 4),
       "H2_resid_diff": round(float(obs), 4), "H2_perm_p": float(p_h2), "H2_drugspecific_pass": H2,
       "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B7_metrics.json"), "w"), indent=2)
print("wrote results/B7_metrics.json")
