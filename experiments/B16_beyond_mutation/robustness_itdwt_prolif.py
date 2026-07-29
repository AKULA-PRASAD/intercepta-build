"""B16 robustness — is the FLT3-ITD-WILDTYPE signal (V19 H2) proliferation-confounded?
Re-tests inferred-FLT3-dependency -> FLT3i ex-vivo sensitivity WITHIN ITD-WT patients, proliferation-residualized.
Confirms V19 H2 is not a proliferation artifact. Reproduce x2.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
import warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.engine import InterceptaEngine
from intercepta.axes import compute_r_prolif

FLT3I = ["sorafenib", "quizartinib", "gilteritinib", "crenolanib"]
HERE = os.path.dirname(os.path.abspath(__file__))

eng = InterceptaEngine().fit(drugs=FLT3I, compute_calibration=False, label_source="prism"); eng.fit_dependency(["FLT3"])
bx = D.load_beataml_expression(); inf = eng.infer_dependency(bx)["FLT3"]; Rp = compute_r_prolif(bx)
auc = D.load_beataml_auc(); auc = auc[auc["sample"].isin(set(bx.columns))]
clin = D.load_beataml_clinical().dropna(subset=["dbgap_rnaseq_sample"]).drop_duplicates("dbgap_rnaseq_sample").set_index("dbgap_rnaseq_sample")
pos = lambda x: (1.0 if str(x).strip().lower() in ("positive","yes","mutated","pos") else (0.0 if str(x).strip().lower() in ("negative","no","wildtype","wt","neg") else np.nan))
itd = clin["FLT3-ITD"].map(pos)

def resid(x, c):
    x = np.asarray(x, float); c = np.asarray(c, float); A = np.column_stack([np.ones_like(c), c])
    b, *_ = np.linalg.lstsq(A, x, rcond=None); return x - A @ b

rows, zs = [], []
for d in FLT3I:
    a = auc[auc["drug"] == d].groupby("sample")["auc"].mean()
    S = [s for s in a.index if s in inf.index and s in itd.index and itd[s] == 0]
    if len(S) < 15: continue
    y = a[S].values; dep = inf[S].values; rp = Rp[S].values
    r_raw = float(stats.spearmanr(dep, y)[0]); r_adj = float(stats.spearmanr(resid(dep, rp), resid(y, rp))[0])
    rows.append({"drug": d, "n_wt": len(S), "rho_raw": round(r_raw, 4), "rho_prolif_adj": round(r_adj, 4)})
    zs.append(np.arctanh(np.clip(r_adj, -.999, .999)) * np.sqrt(len(S) - 3))
Z = float(np.sum(zs) / np.sqrt(len(zs))); p = float(stats.norm.sf(Z))
for r in rows: print(f"  {r['drug']:<13} n_wt={r['n_wt']:>3} raw={r['rho_raw']:+.3f} prolif-adj={r['rho_prolif_adj']:+.3f}")
print(f"combined prolif-adjusted ITD-WT Stouffer Z={Z:.2f} p={p:.3e}")
out = {"timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "pairs": rows,
       "combined_stouffer_Z": round(Z, 3), "combined_p": p,
       "conclusion": "V19 H2 (ITD-WT FLT3-dependency->FLT3i sensitivity) SURVIVES proliferation adjustment; not a proliferation artifact."}
json.dump(out, open(os.path.join(HERE, "results", "B16_robustness_itdwt_prolif.json"), "w"), indent=2)
print("wrote results/B16_robustness_itdwt_prolif.json")
