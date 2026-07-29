"""B3c (L1b external replication) — repeat B3b with INDEPENDENT GDSC1 labels.
Implements prereg/B3c_external_replication.md. Identical to B3b except drug-response labels come from GDSC1
(independent screen). Tests whether the proliferation-residualized drug-specific patient signal replicates.
Deterministic; reproduce x2.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from sklearn.linear_model import RidgeCV
import sklearn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.metrics import per_drug_spearman, paired_wilcoxon
from intercepta.axes import compute_r_prolif

TOPN, SEED, K, MIN_TEST, MIN_TRAIN = 2000, 42, 2000, 15, 30
HERE = os.path.dirname(os.path.abspath(__file__))
print("B3c external replication (DepMap RNA-seq + GDSC1 labels -> BeatAML patients) | sklearn", sklearn.__version__, flush=True)

cos2dep, dep2cos = D.load_cosmic_depmap_map()
gdsc = D.load_gdsc1_response()                    # <-- INDEPENDENT labels (GDSC1)
dx = D.load_depmap_expression()
bx = D.load_beataml_expression()
auc = D.load_beataml_auc()

gdsc = gdsc[gdsc["COSMIC_ID"].isin(cos2dep.keys())].copy()
gdsc["DepMap_ID"] = gdsc["COSMIC_ID"].map(cos2dep)
gdsc = gdsc[gdsc["DepMap_ID"].isin(dx.index)]

shared_genes = [g for g in dx.columns if g in set(bx.index)]
v = dx[shared_genes].var(0).sort_values(ascending=False)
genes = list(v.head(TOPN).index)
dxz = D.z_rows(dx[genes].T).fillna(0.0)
bxz = D.z_rows(bx.loc[genes]).fillna(0.0)
Rp_pat = compute_r_prolif(bx)

gl = {d.lower(): d for d in gdsc["DRUG_NAME"].unique()}
auc = auc[auc["sample"].isin(set(bxz.columns))]
shared_drugs = sorted(set(gl) & set(auc["drug"].unique()))
pat_auc = {dk: auc[auc["drug"] == dk].groupby("sample")["auc"].mean() for dk in shared_drugs}

models_pred = {}
for dk in shared_drugs:
    tr = gdsc[gdsc["DRUG_NAME"] == gl[dk]].dropna(subset=["LN_IC50"])
    tr = tr.groupby("DepMap_ID", as_index=False)["LN_IC50"].mean()   # avg replicate curves per cell
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


cells_by = {dk: [c for c in pat_auc[dk].index if c in bxz.columns] for dk in usable}
diag, offdiag, diag_r, offdiag_r, rprolif = [], [], [], [], []
for dk in usable:
    cells = cells_by[dk]; yv = pat_auc[dk][cells].values; rp = Rp_pat[cells].values; pv = models_pred[dk][cells].values
    diag.append(per_drug_spearman(pv, yv)); rprolif.append(per_drug_spearman(rp, yv))
    offdiag.append(np.mean([per_drug_spearman(models_pred[dj][cells].values, yv) for dj in usable if dj != dk]))
    yr = resid_on(yv, rp)
    diag_r.append(per_drug_spearman(resid_on(pv, rp), yr))
    offdiag_r.append(np.mean([per_drug_spearman(resid_on(models_pred[dj][cells].values, rp), yr) for dj in usable if dj != dk]))

diag = np.array(diag); offdiag = np.array(offdiag); diag_r = np.array(diag_r); offdiag_r = np.array(offdiag_r); rprolif = np.array(rprolif)
n = len(usable); rng = np.random.default_rng(SEED)

null_t = np.empty(K)
for i in range(K):
    null_t[i] = np.mean([per_drug_spearman(models_pred[dk][cells_by[dk]].values, rng.permutation(pat_auc[dk][cells_by[dk]].values)) for dk in usable])
perm_p_transfer = (np.sum(null_t >= diag.mean()) + 1) / (K + 1)


def specperm(d, o):
    obs = d.mean() - o.mean(); do = np.column_stack([d, o]); null = np.empty(K)
    for i in range(K):
        f = rng.integers(0, 2, n).astype(bool)
        null[i] = np.where(f, do[:, 1], do[:, 0]).mean() - np.where(f, do[:, 0], do[:, 1]).mean()
    return obs, (np.sum(null >= obs) + 1) / (K + 1)


spec_obs, perm_p_spec = specperm(diag, offdiag)
spec_obs_r, perm_p_spec_r = specperm(diag_r, offdiag_r)
replicates = bool(spec_obs_r > 0 and perm_p_spec_r < 0.05)

print(f"\ndrugs usable (GDSC1 overlap): {n}")
print(f"diagonal mean rho = {diag.mean():+.4f}  off = {offdiag.mean():+.4f}  transfer perm p={perm_p_transfer:.4g}")
print(f"RESIDUALIZED diag_r={diag_r.mean():+.4f} off_r={offdiag_r.mean():+.4f} diff={spec_obs_r:+.4f} perm p={perm_p_spec_r:.4g}")
print(f"REPLICATION (drug-specific beyond prolif, independent GDSC1 labels): {'PASS' if replicates else 'FAIL'}")
verdict = ("L1b REPLICATES with independent GDSC1 labels: drug-specific patient signal holds across two screens (weak, needs 2nd patient cohort)"
           if replicates else
           "L1b does NOT replicate with independent labels -> downgrade B3b to PROVISIONAL / single-screen")
print(f"VERDICT: {verdict}")

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "sklearn": sklearn.__version__, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "label_source": "GDSC1", "topN_genes": TOPN, "seed": SEED, "K_perm": K, "n_drugs": n,
       "diag_mean_rho": round(float(diag.mean()), 4), "offdiag_mean_rho": round(float(offdiag.mean()), 4),
       "perm_p_transfer": float(perm_p_transfer),
       "resid_diag_mean_rho": round(float(diag_r.mean()), 4), "resid_offdiag_mean_rho": round(float(offdiag_r.mean()), 4),
       "resid_diag_minus_off": round(float(spec_obs_r), 4), "perm_p_specificity_resid": float(perm_p_spec_r),
       "rprolif_transfer_mean_rho": round(float(rprolif.mean()), 4),
       "replicates_drug_specific_beyond_prolif": replicates, "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B3c_metrics.json"), "w"), indent=2)
print("wrote results/B3c_metrics.json")
