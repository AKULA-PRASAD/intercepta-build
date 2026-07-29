"""B4 — does the mechanism-anchored engine beat its parts? Implements prereg/B4_mechanism_integration.md.
Per verified drug-marker pair, OLS AUC ~ marker + R_prolif + transfer_pred [+ FLT3_ITD]; test whether the
expression-transfer prediction adds beyond the mutation marker (and vice versa). Deterministic; reproduce x2.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold
import statsmodels.api as sm
import sklearn, warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.metrics import bh_fdr
from intercepta.axes import compute_r_prolif

TOPN, SEED, MIN_TRAIN = 2000, 42, 30
HERE = os.path.dirname(os.path.abspath(__file__))
# (drug, marker_name, marker_source)  — source: 'wes' or clinical col
PAIRS = [("trametinib", "NRAS", "wes"), ("selumetinib", "NRAS", "wes"),
         ("cabozantinib", "NPM1", "clin"), ("dasatinib", "DNMT3A", "wes"),
         ("sorafenib", "FLT3_ITD", "clin")]
print("B4 mechanism-anchored integration | sklearn", sklearn.__version__, flush=True)

cos2dep, dep2cos = D.load_cosmic_depmap_map()
gdsc = D.load_gdsc_response(); gdsc = gdsc[gdsc["COSMIC_ID"].isin(cos2dep.keys())].copy()
gdsc["DepMap_ID"] = gdsc["COSMIC_ID"].map(cos2dep); gdsc = gdsc[gdsc["DepMap_ID"].isin(D.load_depmap_expression().index)]
dx = D.load_depmap_expression(); bx = D.load_beataml_expression(); auc = D.load_beataml_auc()
clin = D.load_beataml_clinical()

shared_genes = [g for g in dx.columns if g in set(bx.index)]
genes = list(dx[shared_genes].var(0).sort_values(ascending=False).head(TOPN).index)
dxz = D.z_rows(dx[genes].T).fillna(0.0); bxz = D.z_rows(bx.loc[genes]).fillna(0.0)
Rp_pat = compute_r_prolif(bx)
gl = {d.lower(): d for d in gdsc["DRUG_NAME"].unique()}

def pos(x):
    s = str(x).strip().lower()
    return 1 if s in ("positive", "yes", "mutated", "pos") else (0 if s in ("negative", "no", "wildtype", "wt", "neg") else np.nan)

# marker table per rnaseq_sample
wes_status = D.load_beataml_wes_gene_status(["NRAS", "DNMT3A"])
wes_tested = set()
_wraw = pd.read_csv(os.path.join(D.BEATAML, "beataml_wes_wv1to4_mutations_dbgap.txt"), sep="\t", usecols=["dbgap_sample_id"])
wes_tested = set(_wraw["dbgap_sample_id"].unique())
cl = clin.dropna(subset=["dbgap_rnaseq_sample"]).copy()
cl["NPM1_m"] = cl["NPM1"].map(pos); cl["FLT3_ITD"] = cl["FLT3-ITD"].map(pos)
def wes_call(dna, geneset):
    if pd.isna(dna) or dna not in wes_tested: return np.nan
    return 1.0 if dna in geneset else 0.0
cl["NRAS"] = cl["dbgap_dnaseq_sample"].map(lambda d: wes_call(d, wes_status["NRAS"]))
cl["DNMT3A"] = cl["dbgap_dnaseq_sample"].map(lambda d: wes_call(d, wes_status["DNMT3A"]))
cl["NPM1"] = cl["NPM1_m"]
mk = cl.set_index("dbgap_rnaseq_sample")

# transfer predictions per needed drug
pred = {}
for dk in set(p[0] for p in PAIRS):
    if dk not in gl: continue
    tr = gdsc[gdsc["DRUG_NAME"] == gl[dk]].dropna(subset=["LN_IC50"]).drop_duplicates("DepMap_ID")
    tr = tr[tr["DepMap_ID"].isin(dxz.columns)]
    if len(tr) < MIN_TRAIN: continue
    m = RidgeCV(alphas=[10.0, 100.0, 1000.0]).fit(dxz[tr["DepMap_ID"].values].T.values, tr["LN_IC50"].values)
    pred[dk] = pd.Series(m.predict(bxz.T.values), index=bxz.columns)

def z(a): a = np.asarray(a, float); s = a.std(); return (a - a.mean()) / s if s > 0 else a - a.mean()
def cvspear(X, y):
    kf = KFold(5, shuffle=True, random_state=SEED); pr = np.empty(len(y))
    for tri, tei in kf.split(X):
        pr[tei] = sm.OLS(y[tri], sm.add_constant(X[tri], has_constant="add")).fit().predict(sm.add_constant(X[tei], has_constant="add"))
    return float(stats.spearmanr(pr, y)[0])

rows = []
for dk, marker, src in PAIRS:
    if dk not in pred: continue
    a = auc[auc["drug"] == dk].groupby("sample")["auc"].mean()
    samples = [s for s in a.index if s in bxz.columns and s in mk.index]
    df = pd.DataFrame({"AUC": a[samples].values,
                       "marker": mk.loc[samples, marker].values,
                       "prolif": Rp_pat[samples].values,
                       "pred": pred[dk][samples].values,
                       "FLT3_ITD": mk.loc[samples, "FLT3_ITD"].values}, index=samples)
    if marker == "FLT3_ITD":
        df = df.drop(columns=["FLT3_ITD"]); cov = ["marker", "prolif", "pred"]
    else:
        cov = ["marker", "prolif", "pred", "FLT3_ITD"]
    df = df.dropna(subset=cov + ["AUC"])
    n = len(df); npos = int(df["marker"].sum())
    if n < 25 or npos < 5:
        rows.append({"drug": dk, "marker": marker, "n": n, "n_mut": npos, "skipped": "insufficient"}); continue
    X = df[cov].astype(float).copy()
    for c in ["prolif", "pred"]:
        X[c] = z(X[c].values)
    res = sm.OLS(df["AUC"].values, sm.add_constant(X.values, has_constant="add")).fit()
    idx = {c: i + 1 for i, c in enumerate(cov)}
    b_pred = float(res.params[idx["pred"]]); p_pred = float(res.pvalues[idx["pred"]]); se_pred = float(res.bse[idx["pred"]])
    b_mk = float(res.params[idx["marker"]]); p_mk = float(res.pvalues[idx["marker"]])
    # CV predictive Spearman: combined vs marker-only vs transfer-only
    y = df["AUC"].values
    cv_comb = cvspear(df[["marker", "pred"]].astype(float).values, y)
    cv_mk = cvspear(df[["marker"]].astype(float).values, y)
    cv_pr = cvspear(df[["pred"]].astype(float).values, y)
    rows.append({"drug": dk, "marker": marker, "n": n, "n_mut": npos,
                 "transfer_beta": round(b_pred, 6), "transfer_p": p_pred, "transfer_se": round(se_pred, 6),
                 "transfer_adds": bool(p_pred < 0.05 and b_pred > 0),
                 "marker_beta": round(b_mk, 6), "marker_p": p_mk, "marker_adds": bool(p_mk < 0.05 and b_mk < 0),
                 "cv_combined": round(cv_comb, 4), "cv_marker_only": round(cv_mk, 4), "cv_transfer_only": round(cv_pr, 4)})

valid = [r for r in rows if "transfer_p" in r]
# BH across transfer p-values
tp = [r["transfer_p"] for r in valid]; bh = bh_fdr(tp)
for r, q in zip(valid, bh): r["transfer_BHq"] = float(q)
n_add = sum(r["transfer_adds"] for r in valid)
n_comp = sum(r["transfer_adds"] and r["marker_adds"] for r in valid)
# DL random-effects meta of standardized transfer beta
betas = np.array([r["transfer_beta"] for r in valid]); ses = np.array([r["transfer_se"] for r in valid])
w = 1 / ses**2; mu_f = np.sum(w * betas) / np.sum(w)
Q = np.sum(w * (betas - mu_f)**2); k = len(betas)
tau2 = max(0, (Q - (k - 1)) / (np.sum(w) - np.sum(w**2) / np.sum(w))) if k > 1 else 0
wr = 1 / (ses**2 + tau2); mu = float(np.sum(wr * betas) / np.sum(wr)); se_mu = float(np.sqrt(1 / np.sum(wr)))
meta_p = float(2 * stats.norm.sf(abs(mu / se_mu)))
engine_beats_parts = bool(n_add >= 3)

print(f"\npairs evaluated: {len(valid)}")
for r in valid:
    print(f"  {r['drug']:<13} ~ {r['marker']:<7} n={r['n']:>3} mut={r['n_mut']:>3} | "
          f"transfer beta={r['transfer_beta']:+.3f} p={r['transfer_p']:.3g} BHq={r['transfer_BHq']:.3g} adds={r['transfer_adds']} | "
          f"marker p={r['marker_p']:.3g} adds={r['marker_adds']} | CV comb/mk/tr={r['cv_combined']:+.3f}/{r['cv_marker_only']:+.3f}/{r['cv_transfer_only']:+.3f}")
print(f"\ntransfer adds beyond marker in {n_add}/{len(valid)} pairs; complementary (both add) in {n_comp}/{len(valid)}")
print(f"DL meta standardized transfer effect = {mu:+.4f} (SE {se_mu:.4f}), p={meta_p:.4g}")
verdict = ("ENGINE > PARTS: expression transfer adds beyond the verified mutation marker in >=3/5 pairs — the two verified signals are complementary"
           if engine_beats_parts else
           "NOT confirmed: for these mutation-driven drugs the marker largely suffices; transfer and mutation markers cover different drug sets (honest bound on the engine)")
print(f"VERDICT: {verdict}")

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "sklearn": sklearn.__version__, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "topN_genes": TOPN, "seed": SEED, "pairs": rows, "n_valid_pairs": len(valid),
       "n_transfer_adds": n_add, "n_complementary": n_comp,
       "meta_transfer_effect": round(mu, 4), "meta_transfer_se": round(se_mu, 4), "meta_p": meta_p,
       "engine_beats_parts": engine_beats_parts, "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B4_metrics.json"), "w"), indent=2)
print("wrote results/B4_metrics.json")
