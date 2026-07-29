"""B3 (L1) — cell-line -> PATIENT drug-response transfer. Implements prereg/B3_patient_transfer.md.

Train per-drug RidgeCV on GDSC cell-line z-expression -> LN_IC50; predict on BeatAML PATIENT z-expression;
score per-drug Spearman vs BeatAML ex-vivo AUC. Tests (1) transfer (diagonal mean rho>0, permutation),
(2) drug-specificity (diagonal > off-diagonal), (3) vs frozen R_prolif bar. Deterministic; reproduce x2.
"""
import os, sys, json, time
import numpy as np
from scipy import stats
from sklearn.linear_model import RidgeCV
import sklearn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.metrics import per_drug_spearman, paired_wilcoxon
from intercepta.axes import compute_r_prolif

TOPN, SEED, K = 2000, 42, 2000
MIN_TEST, MIN_TRAIN = 15, 30
HERE = os.path.dirname(os.path.abspath(__file__))
print("B3 patient transfer (GDSC cell lines -> BeatAML patients) | sklearn", sklearn.__version__, flush=True)

gdsc = D.load_gdsc_response()
gx = D.load_gdsc_expression()                    # genes x cells (COSMIC)
bx = D.load_beataml_expression()                 # genes(symbol) x patient samples
auc = D.load_beataml_auc()                       # sample, drug, auc

# shared genes (GDSC symbols ∩ BeatAML symbols), top-variance on GDSC
shared_genes = [g for g in gx.index if g in set(bx.index)]
v = gx.loc[shared_genes].var(1).sort_values(ascending=False)
genes = list(v.head(TOPN).index)
gxz = D.z_rows(gx.loc[genes]).fillna(0.0)        # genes x cells
bxz = D.z_rows(bx.loc[genes]).fillna(0.0)        # genes x patient samples
Rp_pat = compute_r_prolif(bx)                    # frozen R_prolif per patient (genes x samples)

gl = {d.lower(): d for d in gdsc["DRUG_NAME"].unique()}
auc = auc[auc["sample"].isin(set(bxz.columns))]
shared_drugs = sorted(set(gl) & set(auc["drug"].unique()))

# per-drug patient AUC vectors
pat_auc = {dk: auc[auc["drug"] == dk].groupby("sample")["auc"].mean() for dk in shared_drugs}

# train a GDSC ridge per drug, store predictions on ALL patient samples (for off-diagonal reuse)
gdsc_cos = set(gx.columns)
models_pred = {}   # dk -> pd.Series(pred indexed by patient sample)
import pandas as pd
for dk in shared_drugs:
    tr = gdsc[(gdsc["DRUG_NAME"] == gl[dk]) & (gdsc["COSMIC_ID"].isin(gdsc_cos))]
    if len(tr) < MIN_TRAIN:
        continue
    m = RidgeCV(alphas=[10.0, 100.0, 1000.0]).fit(gxz[tr["COSMIC_ID"].values].T.values, tr["LN_IC50"].values)
    models_pred[dk] = pd.Series(m.predict(bxz.T.values), index=bxz.columns)

usable = [dk for dk in shared_drugs if dk in models_pred and pat_auc[dk].index.isin(bxz.columns).sum() >= MIN_TEST]
diag, rprolif, offdiag = [], [], []
for dk in usable:
    y = pat_auc[dk]; cells = [c for c in y.index if c in bxz.columns]
    yv = y[cells].values
    diag.append(per_drug_spearman(models_pred[dk][cells].values, yv))
    rprolif.append(per_drug_spearman(Rp_pat[cells].values, yv))   # higher prolif ~ ? (report raw)
    # off-diagonal: this drug's AUC vs OTHER drugs' GDSC maps
    od = [per_drug_spearman(models_pred[dj][cells].values, yv) for dj in usable if dj != dk]
    offdiag.append(np.mean(od))

diag = np.array(diag); rprolif = np.array(rprolif); offdiag = np.array(offdiag)
n = len(usable)

# permutation null for diagonal mean rho: permute patient labels within each drug
rng = np.random.default_rng(SEED)
null_diag = np.empty(K)
preds = {dk: models_pred[dk] for dk in usable}
ys = {dk: pat_auc[dk] for dk in usable}
for i in range(K):
    vals = []
    for dk in usable:
        cells = [c for c in ys[dk].index if c in bxz.columns]
        yv = ys[dk][cells].values
        pv = preds[dk][cells].values
        vals.append(per_drug_spearman(pv, rng.permutation(yv)))
    null_diag[i] = np.mean(vals)
perm_p_transfer = (np.sum(null_diag >= diag.mean()) + 1) / (K + 1)

# specificity: diagonal vs off-diagonal, paired + permutation (sign flips)
spec_stat, spec_p_wil = paired_wilcoxon(diag, offdiag)
obs_spec = diag.mean() - offdiag.mean()
null_spec = np.empty(K)
d_o = np.column_stack([diag, offdiag])
for i in range(K):
    flip = rng.integers(0, 2, size=n).astype(bool)
    a = np.where(flip, d_o[:, 1], d_o[:, 0]); b = np.where(flip, d_o[:, 0], d_o[:, 1])
    null_spec[i] = a.mean() - b.mean()
perm_p_spec = (np.sum(null_spec >= obs_spec) + 1) / (K + 1)

w_rp_stat, w_rp_p = paired_wilcoxon(diag, rprolif)
transfer_pass = bool(diag.mean() > 0 and perm_p_transfer < 0.05)
specific_pass = bool(obs_spec > 0 and perm_p_spec < 0.05)
beats_prolif = bool(diag.mean() > rprolif.mean() and w_rp_p < 0.05)

print(f"\ndrugs usable: {n}  (patients with matched RNA+AUC per drug >= {MIN_TEST})")
print(f"DIAGONAL (matched) mean per-drug rho = {diag.mean():+.4f}  median={np.median(diag):+.4f}  frac>0={np.mean(diag>0):.2f}")
print(f"  transfer permutation p = {perm_p_transfer:.4g}  -> transfer? {transfer_pass}")
print(f"OFF-DIAGONAL (mismatched) mean rho   = {offdiag.mean():+.4f}   diag-off={obs_spec:+.4f}  spec perm p={perm_p_spec:.4g}  -> drug-specific? {specific_pass}")
print(f"R_prolif transfer mean rho           = {rprolif.mean():+.4f}   diag vs R_prolif Wilcoxon p={w_rp_p:.4g}  -> beats prolif? {beats_prolif}")
if transfer_pass and specific_pass and beats_prolif:
    verdict = "L1 PASS: cell-line->patient transfer is real AND drug-specific AND beyond proliferation"
elif transfer_pass and not specific_pass:
    verdict = "PARTIAL: transfers to patients but NOT drug-specific -> a generic chemosensitivity/proliferation axis, not drug-level patient prediction"
elif transfer_pass:
    verdict = "PARTIAL: significant transfer; specificity/proliferation checks mixed (see flags)"
else:
    verdict = "NULL: no significant cell-line->patient transfer at drug level (bounds L1; specifies need for matched-platform / larger-n data)"
print(f"VERDICT: {verdict}")

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "sklearn": sklearn.__version__, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "topN_genes": TOPN, "seed": SEED, "K_perm": K, "n_drugs": n,
       "diag_mean_rho": round(float(diag.mean()), 4), "diag_median_rho": round(float(np.median(diag)), 4),
       "diag_frac_pos": round(float(np.mean(diag > 0)), 4),
       "offdiag_mean_rho": round(float(offdiag.mean()), 4), "diag_minus_offdiag": round(float(obs_spec), 4),
       "rprolif_transfer_mean_rho": round(float(rprolif.mean()), 4),
       "perm_p_transfer": float(perm_p_transfer), "perm_p_specificity": float(perm_p_spec),
       "wilcoxon_p_diag_vs_rprolif": float(w_rp_p),
       "transfer_pass": transfer_pass, "specificity_pass": specific_pass, "beats_prolif": beats_prolif,
       "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B3_metrics.json"), "w"), indent=2)
print("wrote results/B3_metrics.json")
