"""B3d (L1b robustness) — try to break the weak drug-specific patient signal. Implements prereg/B3d_robustness.md.
Training identical to B3b (DepMap RNA-seq + GDSC2 labels -> BeatAML). Tests: R1 drug jackknife, R2 drug
bootstrap CI, R3 internal patient split-half. Deterministic; reproduce x2.
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
from sklearn.linear_model import RidgeCV
import sklearn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.metrics import per_drug_spearman
from intercepta.axes import compute_r_prolif

TOPN, SEED, B, MIN_TEST, MIN_TRAIN, MIN_HALF = 2000, 42, 2000, 15, 30, 8
HERE = os.path.dirname(os.path.abspath(__file__))
print("B3d robustness of L1b (DepMap RNA-seq + GDSC2 -> BeatAML) | sklearn", sklearn.__version__, flush=True)

cos2dep, dep2cos = D.load_cosmic_depmap_map()
gdsc = D.load_gdsc_response()
dx = D.load_depmap_expression()
bx = D.load_beataml_expression()
auc = D.load_beataml_auc()
gdsc = gdsc[gdsc["COSMIC_ID"].isin(cos2dep.keys())].copy()
gdsc["DepMap_ID"] = gdsc["COSMIC_ID"].map(cos2dep)
gdsc = gdsc[gdsc["DepMap_ID"].isin(dx.index)]

shared_genes = [g for g in dx.columns if g in set(bx.index)]
genes = list(dx[shared_genes].var(0).sort_values(ascending=False).head(TOPN).index)
dxz = D.z_rows(dx[genes].T).fillna(0.0)
bxz = D.z_rows(bx.loc[genes]).fillna(0.0)
Rp_pat = compute_r_prolif(bx)

gl = {d.lower(): d for d in gdsc["DRUG_NAME"].unique()}
auc = auc[auc["sample"].isin(set(bxz.columns))]
shared_drugs = sorted(set(gl) & set(auc["drug"].unique()))
pat_auc = {dk: auc[auc["drug"] == dk].groupby("sample")["auc"].mean() for dk in shared_drugs}

models_pred = {}
for dk in shared_drugs:
    tr = gdsc[gdsc["DRUG_NAME"] == gl[dk]].dropna(subset=["LN_IC50"]).drop_duplicates("DepMap_ID")
    tr = tr[tr["DepMap_ID"].isin(dxz.columns)]
    if len(tr) < MIN_TRAIN:
        continue
    m = RidgeCV(alphas=[10.0, 100.0, 1000.0]).fit(dxz[tr["DepMap_ID"].values].T.values, tr["LN_IC50"].values)
    models_pred[dk] = pd.Series(m.predict(bxz.T.values), index=bxz.columns)
usable = [dk for dk in shared_drugs if dk in models_pred and pat_auc[dk].index.isin(bxz.columns).sum() >= MIN_TEST]


def resid_on(x, cov):
    x = np.asarray(x, float); cov = np.asarray(cov, float)
    A = np.column_stack([np.ones_like(cov), cov]); beta, *_ = np.linalg.lstsq(A, x, rcond=None)
    return x - A @ beta


def residual_specificity(drug_list, patient_filter=None, min_test=MIN_TEST):
    """Return per-drug (diag_r, off_r) arrays over drug_list, restricting patients by patient_filter set."""
    cells_by = {}
    for dk in drug_list:
        c = [s for s in pat_auc[dk].index if s in bxz.columns and (patient_filter is None or s in patient_filter)]
        cells_by[dk] = c
    dl = [dk for dk in drug_list if len(cells_by[dk]) >= min_test]
    diag_r, off_r = [], []
    for dk in dl:
        cells = cells_by[dk]; yv = pat_auc[dk][cells].values; rp = Rp_pat[cells].values
        yr = resid_on(yv, rp)
        diag_r.append(per_drug_spearman(resid_on(models_pred[dk][cells].values, rp), yr))
        off_r.append(np.mean([per_drug_spearman(resid_on(models_pred[dj][cells].values, rp), yr)
                              for dj in dl if dj != dk]))
    return np.array(diag_r), np.array(off_r), dl


diag_r, off_r, dl = residual_specificity(usable)
per_drug_diff = diag_r - off_r
full_diff = float(diag_r.mean() - off_r.mean())
n = len(dl)

# R1 jackknife over drugs
jack = np.array([ (np.delete(diag_r, i).mean() - np.delete(off_r, i).mean()) for i in range(n) ])
R1_pass = bool(np.all(jack > 0))

# R2 bootstrap over drugs
rng = np.random.default_rng(SEED)
boot = np.array([ (lambda idx: diag_r[idx].mean() - off_r[idx].mean())(rng.integers(0, n, n)) for _ in range(B) ])
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
R2_pass = bool(ci_lo > 0)

# R3 patient split-half (disjoint patients; training is patient-independent -> clean)
allpat = sorted(set(bxz.columns))
half = {s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 2 for s in allpat}
h0 = {s for s in allpat if half[s] == 0}; h1 = {s for s in allpat if half[s] == 1}
d0, o0, dl0 = residual_specificity(usable, h0, min_test=MIN_HALF)
d1, o1, dl1 = residual_specificity(usable, h1, min_test=MIN_HALF)
diff0 = float(d0.mean() - o0.mean()) if len(d0) else float("nan")
diff1 = float(d1.mean() - o1.mean()) if len(d1) else float("nan")
R3_pass = bool(np.isfinite(diff0) and np.isfinite(diff1) and diff0 > 0 and diff1 > 0)

robust = R1_pass and R2_pass and R3_pass

# exploratory: top/bottom drugs by residual diagonal rho
order = np.argsort(-diag_r)
top = [(dl[i], round(float(diag_r[i]), 3)) for i in order[:8]]
bot = [(dl[i], round(float(diag_r[i]), 3)) for i in order[-5:]]

print(f"\nn drugs = {n} | full residual diag-off = {full_diff:+.4f}")
print(f"R1 jackknife: min leave-one-out = {jack.min():+.4f}  max = {jack.max():+.4f}  -> all>0? {R1_pass}")
print(f"R2 bootstrap(B={B}) 95% CI of diag-off = [{ci_lo:+.4f}, {ci_hi:+.4f}]  -> CI>0? {R2_pass}")
print(f"R3 patient split-half: halfA diff={diff0:+.4f} (n={len(d0)}), halfB diff={diff1:+.4f} (n={len(d1)})  -> both>0? {R3_pass}")
print(f"ROBUST (R1&R2&R3)? {robust}")
print(f"exploratory top drugs by resid diagonal rho: {top}")
print(f"exploratory bottom: {bot}")
verdict = ("L1b ROBUST to drug- and patient-subsetting (still one cohort/cancer; still needs 2nd patient cohort)"
           if robust else "L1b FRAGILE — see which test failed; downgrade V9 accordingly")
print(f"VERDICT: {verdict}")

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "sklearn": sklearn.__version__, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "topN_genes": TOPN, "seed": SEED, "B_boot": B, "n_drugs": n,
       "full_resid_diag_minus_off": round(full_diff, 4),
       "R1_jackknife_min": round(float(jack.min()), 4), "R1_jackknife_max": round(float(jack.max()), 4), "R1_pass": R1_pass,
       "R2_boot_ci_lo": round(float(ci_lo), 4), "R2_boot_ci_hi": round(float(ci_hi), 4), "R2_pass": R2_pass,
       "R3_halfA_diff": round(diff0, 4), "R3_halfA_n": len(d0), "R3_halfB_diff": round(diff1, 4), "R3_halfB_n": len(d1), "R3_pass": R3_pass,
       "robust": robust, "exploratory_top_drugs": top, "exploratory_bottom_drugs": bot, "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B3d_metrics.json"), "w"), indent=2)
print("wrote results/B3d_metrics.json")
