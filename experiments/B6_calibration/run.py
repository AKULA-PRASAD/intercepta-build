"""B6 — is the engine's confidence signal calibrated? Implements prereg/B6_calibration.md.
H1: per-drug cell-line CV reliability predicts patient transfer accuracy. H2: per-sample OOD predicts accuracy.
Ships a confidence axis ONLY if validated; else engine confidence stays LOW (honest). Reproduce x2.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
import sklearn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.engine import InterceptaEngine

SEED, K = 42, 2000
HERE = os.path.dirname(os.path.abspath(__file__))
print("B6 calibration validation | sklearn", sklearn.__version__, flush=True)

eng = InterceptaEngine().fit(compute_calibration=True)          # all drugs + reliability + OOD
bx = D.load_beataml_expression()
auc = D.load_beataml_auc()
pred = eng.predict_transfer(bx)                                 # samples x drugs
ood = eng.ood_score(bx)                                         # per sample

# per-drug patient accuracy + cv reliability
recs = []
for dk in eng.fitted_drugs_:
    if dk not in pred.columns:
        continue
    a = auc[auc["drug"] == dk].groupby("sample")["auc"].mean()
    cells = [s for s in a.index if s in pred.index]
    if len(cells) < 30:
        continue
    prho = stats.spearmanr(pred.loc[cells, dk].values, a[cells].values)[0]
    recs.append({"drug": dk, "n": len(cells), "patient_rho": prho,
                 "cv_rho": eng.drug_cv_rho_.get(dk, np.nan)})
df = pd.DataFrame(recs).dropna(subset=["patient_rho", "cv_rho"])
rng = np.random.default_rng(SEED)

# H1: cv reliability vs patient accuracy across drugs
h1_rho = stats.spearmanr(df["cv_rho"], df["patient_rho"])[0]
null1 = np.array([stats.spearmanr(df["cv_rho"], rng.permutation(df["patient_rho"].values))[0] for _ in range(K)])
h1_p = (np.sum(null1 >= h1_rho) + 1) / (K + 1)
H1 = bool(h1_rho > 0 and h1_p < 0.05)

# H2: per-sample OOD split -> transfer accuracy low-OOD vs high-OOD
med = ood.median()
lo = set(ood[ood <= med].index); hi = set(ood[ood > med].index)
d_lo, d_hi = [], []
for dk in df["drug"]:
    a = auc[auc["drug"] == dk].groupby("sample")["auc"].mean()
    cl = [s for s in a.index if s in pred.index and s in lo]
    ch = [s for s in a.index if s in pred.index and s in hi]
    if len(cl) >= 15 and len(ch) >= 15:
        d_lo.append(stats.spearmanr(pred.loc[cl, dk].values, a[cl].values)[0])
        d_hi.append(stats.spearmanr(pred.loc[ch, dk].values, a[ch].values)[0])
d_lo, d_hi = np.array(d_lo), np.array(d_hi)
obs2 = float(d_lo.mean() - d_hi.mean()) if len(d_lo) else np.nan
if len(d_lo) >= 10:
    do = np.column_stack([d_lo, d_hi]); null2 = np.empty(K)
    for i in range(K):
        f = rng.integers(0, 2, len(d_lo)).astype(bool)
        null2[i] = np.where(f, do[:, 1], do[:, 0]).mean() - np.where(f, do[:, 0], do[:, 1]).mean()
    h2_p = (np.sum(null2 >= obs2) + 1) / (K + 1)
else:
    h2_p = np.nan
H2 = bool(np.isfinite(obs2) and obs2 > 0 and np.isfinite(h2_p) and h2_p < 0.05)

verdict = ("CALIBRATED: " + ("drug-reliability " if H1 else "") + ("OOD " if H2 else "") + "axis validated"
           if (H1 or H2) else
           "NOT CALIBRATED (both null) — engine confidence stays LOW for all; calibration deferred to a 2nd cohort. Consistent with B3e.")
print(f"\nH1 per-drug reliability vs patient accuracy: n_drugs={len(df)} Spearman={h1_rho:+.4f} perm p={h1_p:.4g} -> {H1}")
print(f"H2 OOD low vs high accuracy: n_drugs={len(d_lo)} diff(lo-hi)={obs2:+.4f} perm p={h2_p if np.isfinite(h2_p) else float('nan'):.4g} -> {H2}")
print(f"VERDICT: {verdict}")

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "sklearn": sklearn.__version__, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "seed": SEED, "K": K, "n_drugs_H1": len(df),
       "H1_spearman_cvrho_vs_patientrho": round(float(h1_rho), 4), "H1_perm_p": float(h1_p), "H1_pass": H1,
       "H2_n_drugs": int(len(d_lo)), "H2_diff_lowOOD_minus_highOOD": (round(obs2, 4) if np.isfinite(obs2) else None),
       "H2_perm_p": (float(h2_p) if np.isfinite(h2_p) else None), "H2_pass": H2,
       "confidence_calibrated": bool(H1 or H2), "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B6_metrics.json"), "w"), indent=2)
print("wrote results/B6_metrics.json")
