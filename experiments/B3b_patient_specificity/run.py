"""B3b (L1b) — matched-platform + proliferation-residualized drug-specificity in patient transfer.
Implements prereg/B3b_matched_specificity.md. Train per-drug Ridge on DepMap RNA-seq (labels=GDSC LN_IC50 via
COSMIC<->DepMap) -> predict on BeatAML patient RNA-seq. Tests (1) matched-platform transfer, (2) whether any
DRUG-SPECIFIC signal survives removing R_prolif. Deterministic; reproduce x2.
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
print("B3b matched-platform patient specificity (DepMap RNA-seq -> BeatAML patients) | sklearn", sklearn.__version__, flush=True)

cos2dep, dep2cos = D.load_cosmic_depmap_map()
gdsc = D.load_gdsc_response()
dx = D.load_depmap_expression()                  # cells(ACH) x genes(symbol) — RNA-seq
bx = D.load_beataml_expression()                 # genes(symbol) x patient samples
auc = D.load_beataml_auc()

# map GDSC LN_IC50 onto DepMap cells (via COSMIC->DepMap)
gdsc = gdsc[gdsc["COSMIC_ID"].isin(cos2dep.keys())].copy()
gdsc["DepMap_ID"] = gdsc["COSMIC_ID"].map(cos2dep)
gdsc = gdsc[gdsc["DepMap_ID"].isin(dx.index)]

shared_genes = [g for g in dx.columns if g in set(bx.index)]
v = dx[shared_genes].var(0).sort_values(ascending=False)
genes = list(v.head(TOPN).index)
dxz = D.z_rows(dx[genes].T).fillna(0.0)          # genes x cells(ACH)
bxz = D.z_rows(bx.loc[genes]).fillna(0.0)        # genes x patient samples
Rp_pat = compute_r_prolif(bx)                    # frozen R_prolif per patient

gl = {d.lower(): d for d in gdsc["DRUG_NAME"].unique()}
auc = auc[auc["sample"].isin(set(bxz.columns))]
shared_drugs = sorted(set(gl) & set(auc["drug"].unique()))
pat_auc = {dk: auc[auc["drug"] == dk].groupby("sample")["auc"].mean() for dk in shared_drugs}

models_pred = {}
for dk in shared_drugs:
    tr = gdsc[gdsc["DRUG_NAME"] == gl[dk]].dropna(subset=["LN_IC50"])
    tr = tr[tr["DepMap_ID"].isin(dxz.columns)].drop_duplicates("DepMap_ID")
    if len(tr) < MIN_TRAIN:
        continue
    m = RidgeCV(alphas=[10.0, 100.0, 1000.0]).fit(dxz[tr["DepMap_ID"].values].T.values, tr["LN_IC50"].values)
    models_pred[dk] = pd.Series(m.predict(bxz.T.values), index=bxz.columns)

usable = [dk for dk in shared_drugs if dk in models_pred and pat_auc[dk].index.isin(bxz.columns).sum() >= MIN_TEST]


def resid_on(x, cov):
    """OLS residual of x on [1, cov]."""
    x = np.asarray(x, float); cov = np.asarray(cov, float)
    A = np.column_stack([np.ones_like(cov), cov])
    beta, *_ = np.linalg.lstsq(A, x, rcond=None)
    return x - A @ beta


diag, offdiag, rprolif, diag_r, offdiag_r = [], [], [], [], []
cells_by = {dk: [c for c in pat_auc[dk].index if c in bxz.columns] for dk in usable}
for dk in usable:
    cells = cells_by[dk]; yv = pat_auc[dk][cells].values; rp = Rp_pat[cells].values
    pv = models_pred[dk][cells].values
    diag.append(per_drug_spearman(pv, yv))
    rprolif.append(per_drug_spearman(rp, yv))
    offdiag.append(np.mean([per_drug_spearman(models_pred[dj][cells].values, yv) for dj in usable if dj != dk]))
    # residualized (remove proliferation from BOTH prediction and AUC)
    yr = resid_on(yv, rp)
    diag_r.append(per_drug_spearman(resid_on(pv, rp), yr))
    offdiag_r.append(np.mean([per_drug_spearman(resid_on(models_pred[dj][cells].values, rp), yr) for dj in usable if dj != dk]))

diag = np.array(diag); offdiag = np.array(offdiag); rprolif = np.array(rprolif)
diag_r = np.array(diag_r); offdiag_r = np.array(offdiag_r); n = len(usable)

rng = np.random.default_rng(SEED)
# transfer permutation (matched platform, raw)
null_t = np.empty(K)
for i in range(K):
    null_t[i] = np.mean([per_drug_spearman(models_pred[dk][cells_by[dk]].values,
                         rng.permutation(pat_auc[dk][cells_by[dk]].values)) for dk in usable])
perm_p_transfer = (np.sum(null_t >= diag.mean()) + 1) / (K + 1)


def specperm(d, o):
    obs = d.mean() - o.mean(); do = np.column_stack([d, o]); null = np.empty(K)
    for i in range(K):
        f = rng.integers(0, 2, n).astype(bool)
        null[i] = np.where(f, do[:, 1], do[:, 0]).mean() - np.where(f, do[:, 0], do[:, 1]).mean()
    return obs, (np.sum(null >= obs) + 1) / (K + 1)


spec_obs, perm_p_spec = specperm(diag, offdiag)
spec_obs_r, perm_p_spec_r = specperm(diag_r, offdiag_r)
w_rp_stat, w_rp_p = paired_wilcoxon(diag, rprolif)

transfer_pass = bool(diag.mean() > 0 and perm_p_transfer < 0.05)
specific_resid_pass = bool(diag_r.mean() > offdiag_r.mean() and diag_r.mean() > 0 and perm_p_spec_r < 0.05)
beats_prolif = bool(diag.mean() > rprolif.mean() and w_rp_p < 0.05)

print(f"\ndrugs usable: {n}")
print(f"MATCHED-PLATFORM diagonal mean rho = {diag.mean():+.4f} median={np.median(diag):+.4f} frac>0={np.mean(diag>0):.2f}  (B3 array was +0.0541)")
print(f"  transfer perm p={perm_p_transfer:.4g} -> transfer? {transfer_pass}")
print(f"  off-diagonal={offdiag.mean():+.4f} diag-off={spec_obs:+.4f} spec perm p={perm_p_spec:.4g}")
print(f"  R_prolif transfer={rprolif.mean():+.4f}  diag vs prolif p={w_rp_p:.4g} -> beats prolif? {beats_prolif}")
print(f"PROLIF-RESIDUALIZED: diag_r={diag_r.mean():+.4f} off_r={offdiag_r.mean():+.4f} diff={spec_obs_r:+.4f} perm p={perm_p_spec_r:.4g}")
print(f"  -> drug-specific signal beyond proliferation? {specific_resid_pass}")
if specific_resid_pass:
    verdict = "L1b PASS: a drug-specific cell-line->patient signal SURVIVES proliferation removal (matched platform) — real drug-level patient signal exists, weak"
elif transfer_pass and not specific_resid_pass:
    verdict = "L1 BOUNDED (confirmed): patient transfer is generic proliferation/chemosensitivity only — no drug-specific signal survives; redirect to L2/prospective matched data"
else:
    verdict = "NULL: matched-platform transfer not significant either"
print(f"VERDICT: {verdict}")

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "sklearn": sklearn.__version__, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "topN_genes": TOPN, "seed": SEED, "K_perm": K, "n_drugs": n,
       "matched_diag_mean_rho": round(float(diag.mean()), 4), "matched_diag_median_rho": round(float(np.median(diag)), 4),
       "matched_diag_frac_pos": round(float(np.mean(diag > 0)), 4),
       "offdiag_mean_rho": round(float(offdiag.mean()), 4), "diag_minus_off": round(float(spec_obs), 4),
       "rprolif_transfer_mean_rho": round(float(rprolif.mean()), 4),
       "resid_diag_mean_rho": round(float(diag_r.mean()), 4), "resid_offdiag_mean_rho": round(float(offdiag_r.mean()), 4),
       "resid_diag_minus_off": round(float(spec_obs_r), 4),
       "perm_p_transfer": float(perm_p_transfer), "perm_p_specificity_raw": float(perm_p_spec),
       "perm_p_specificity_resid": float(perm_p_spec_r), "wilcoxon_p_diag_vs_rprolif": float(w_rp_p),
       "transfer_pass": transfer_pass, "beats_prolif": beats_prolif,
       "drug_specific_beyond_prolif_pass": specific_resid_pass, "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B3b_metrics.json"), "w"), indent=2)
print("wrote results/B3b_metrics.json")
