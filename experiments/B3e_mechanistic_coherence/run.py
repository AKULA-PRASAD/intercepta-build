"""B3e (L1b mechanistic coherence) — does patient-transfer strength track AML mechanism?
Implements prereg/B3e_mechanistic_coherence.md. Frozen: AML group = GDSC PATHWAY_NAME in {RTK signaling,
ERK MAPK signaling}. H1: AML-group drugs transfer better (MWU + permutation). H2: transfer rho correlates with
within-cell-line CV predictability. Deterministic; reproduce x2.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold
import sklearn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.metrics import per_drug_spearman
from intercepta.axes import compute_r_prolif

TOPN, SEED, K, MIN_TEST, MIN_TRAIN = 2000, 42, 2000, 15, 30
AML_PATHWAYS = {"rtk signaling", "erk mapk signaling"}   # FROZEN a priori (AML driver signaling axis)
HERE = os.path.dirname(os.path.abspath(__file__))
print("B3e mechanistic coherence | sklearn", sklearn.__version__, flush=True)

cos2dep, dep2cos = D.load_cosmic_depmap_map()
gdsc = D.load_gdsc_response()
dx = D.load_depmap_expression()
bx = D.load_beataml_expression()
auc = D.load_beataml_auc()
gdsc = gdsc[gdsc["COSMIC_ID"].isin(cos2dep.keys())].copy()
gdsc["DepMap_ID"] = gdsc["COSMIC_ID"].map(cos2dep); gdsc = gdsc[gdsc["DepMap_ID"].isin(dx.index)]

shared_genes = [g for g in dx.columns if g in set(bx.index)]
genes = list(dx[shared_genes].var(0).sort_values(ascending=False).head(TOPN).index)
dxz = D.z_rows(dx[genes].T).fillna(0.0)
bxz = D.z_rows(bx.loc[genes]).fillna(0.0)
Rp_pat = compute_r_prolif(bx)

gl = {d.lower(): d for d in gdsc["DRUG_NAME"].unique()}
auc = auc[auc["sample"].isin(set(bxz.columns))]
shared_drugs = sorted(set(gl) & set(auc["drug"].unique()))
pat_auc = {dk: auc[auc["drug"] == dk].groupby("sample")["auc"].mean() for dk in shared_drugs}

# per-drug: model, residual diagonal rho, AND within-cell-line 5-fold CV predictability
def resid_on(x, cov):
    x = np.asarray(x, float); cov = np.asarray(cov, float)
    A = np.column_stack([np.ones_like(cov), cov]); beta, *_ = np.linalg.lstsq(A, x, rcond=None)
    return x - A @ beta

models_pred, cv_pred = {}, {}
for dk in shared_drugs:
    tr = gdsc[gdsc["DRUG_NAME"] == gl[dk]].dropna(subset=["LN_IC50"]).drop_duplicates("DepMap_ID")
    tr = tr[tr["DepMap_ID"].isin(dxz.columns)]
    if len(tr) < MIN_TRAIN:
        continue
    Xtr = dxz[tr["DepMap_ID"].values].T.values; ytr = tr["LN_IC50"].values
    m = RidgeCV(alphas=[10.0, 100.0, 1000.0]).fit(Xtr, ytr)
    models_pred[dk] = pd.Series(m.predict(bxz.T.values), index=bxz.columns)
    # within-cell-line 5-fold CV predictability (no patient data)
    kf = KFold(n_splits=5, shuffle=True, random_state=SEED); preds = np.empty(len(ytr))
    for tri, tei in kf.split(Xtr):
        mm = RidgeCV(alphas=[10.0, 100.0, 1000.0]).fit(Xtr[tri], ytr[tri]); preds[tei] = mm.predict(Xtr[tei])
    cv_pred[dk] = stats.spearmanr(preds, ytr)[0]

usable = [dk for dk in shared_drugs if dk in models_pred and pat_auc[dk].index.isin(bxz.columns).sum() >= MIN_TEST]
cells_by = {dk: [c for c in pat_auc[dk].index if c in bxz.columns] for dk in usable}
resid_rho = {}
for dk in usable:
    cells = cells_by[dk]; yv = pat_auc[dk][cells].values; rp = Rp_pat[cells].values
    resid_rho[dk] = per_drug_spearman(resid_on(models_pred[dk][cells].values, rp), resid_on(yv, rp))

# external pathway annotation (GDSC1 xlsx)
ann = pd.read_excel(os.path.join(D.DATA, "independent/gdsc1/GDSC1_fitted_dose_response.xlsx"),
                    usecols=["DRUG_NAME", "PATHWAY_NAME"]).dropna().drop_duplicates("DRUG_NAME")
ann["d"] = ann["DRUG_NAME"].str.lower(); path = dict(zip(ann["d"], ann["PATHWAY_NAME"].str.lower()))

# H1: AML driver-signaling vs other
annotated = [dk for dk in usable if dk in path]
aml = [dk for dk in annotated if path[dk] in AML_PATHWAYS]
oth = [dk for dk in annotated if path[dk] not in AML_PATHWAYS]
aml_r = np.array([resid_rho[dk] for dk in aml]); oth_r = np.array([resid_rho[dk] for dk in oth])
mwu_p = stats.mannwhitneyu(aml_r, oth_r, alternative="greater")[1] if len(aml) and len(oth) else np.nan
obs_gap = float(np.median(aml_r) - np.median(oth_r)) if len(aml) and len(oth) else np.nan
rng = np.random.default_rng(SEED); allr = np.array([resid_rho[dk] for dk in annotated]); na = len(aml)
null = np.array([(lambda p: np.median(allr[p[:na]]) - np.median(allr[p[na:]]))(rng.permutation(len(allr))) for _ in range(K)])
perm_p_h1 = (np.sum(null >= obs_gap) + 1) / (K + 1)
H1_pass = bool(len(aml) and len(oth) and mwu_p < 0.05 and perm_p_h1 < 0.05 and np.median(aml_r) > np.median(oth_r))

# H2: transfer rho vs within-cell-line CV predictability
cd = [dk for dk in usable if dk in cv_pred and np.isfinite(cv_pred[dk])]
tr_r = np.array([resid_rho[dk] for dk in cd]); cvv = np.array([cv_pred[dk] for dk in cd])
h2_rho, _ = stats.spearmanr(tr_r, cvv)
null2 = np.array([stats.spearmanr(tr_r, rng.permutation(cvv))[0] for _ in range(K)])
perm_p_h2 = (np.sum(null2 >= h2_rho) + 1) / (K + 1)
H2_pass = bool(h2_rho > 0 and perm_p_h2 < 0.05)

print(f"\nusable drugs={len(usable)}  annotated={len(annotated)}  AML-signaling={len(aml)}  other={len(oth)}")
print(f"H1: AML-signaling median resid rho={np.median(aml_r):+.4f} vs other={np.median(oth_r):+.4f}  gap={obs_gap:+.4f}")
print(f"    one-sided MWU p={mwu_p:.4g}  permutation p={perm_p_h1:.4g}  -> H1 PASS? {H1_pass}")
print(f"    AML drugs: {sorted(aml)}")
print(f"H2: Spearman(transfer rho, cell-line CV predictability)={h2_rho:+.4f}  perm p={perm_p_h2:.4g}  -> H2 PASS? {H2_pass}")
verdict = ("Mechanistic coherence CONFIRMED (H1): patient-transfer strength is higher for AML driver-signaling drugs"
           if H1_pass else
           ("Mechanistic coherence NOT confirmed by the pre-declared AML-pathway test (H1 null); "
            + ("H2 corroborates engine-consistency" if H2_pass else "H2 also null") + " — downgrade coherence language honestly"))
print(f"VERDICT: {verdict}")

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "sklearn": sklearn.__version__, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "AML_pathways": sorted(AML_PATHWAYS), "n_usable": len(usable), "n_annotated": len(annotated),
       "n_aml": len(aml), "n_other": len(oth),
       "aml_median_resid_rho": round(float(np.median(aml_r)), 4) if len(aml) else None,
       "other_median_resid_rho": round(float(np.median(oth_r)), 4) if len(oth) else None,
       "H1_gap": round(obs_gap, 4) if np.isfinite(obs_gap) else None,
       "H1_mwu_p": float(mwu_p) if np.isfinite(mwu_p) else None, "H1_perm_p": float(perm_p_h1), "H1_pass": H1_pass,
       "aml_drugs": sorted(aml),
       "H2_spearman": round(float(h2_rho), 4), "H2_perm_p": float(perm_p_h2), "H2_pass": H2_pass,
       "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B3e_metrics.json"), "w"), indent=2)
print("wrote results/B3e_metrics.json")
