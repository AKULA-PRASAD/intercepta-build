"""B13 — can EXPRESSION-inferred dependency recover the functional signal (and beat baseline expression)?
Implements prereg/B13_inferred_dependency.md. Follows B12/V15. Public DepMap. Reproduce x2. Aggregate outputs only.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold
import sklearn, warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.metrics import bh_fdr

SEED, K, TOPN, MIN_CELLS = 42, 2000, 2000, 40
HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = [("idasanutlin","MDM2"),("nutlin-3","MDM2"),("afatinib","EGFR"),("gefitinib","EGFR"),("erlotinib","EGFR"),
         ("alpelisib","PIK3CA"),("buparlisib","PIK3CA"),("trametinib","MAP2K1"),("selumetinib","MAP2K1"),
         ("pd0325901","MAP2K1"),("palbociclib","CDK6"),("ribociclib","CDK6"),("vemurafenib","BRAF"),
         ("dabrafenib","BRAF"),("gilteritinib","FLT3")]
print("B13 inferred-dependency | sklearn", sklearn.__version__, flush=True)

ce = D.load_depmap_crispr()                    # cells x genes (dependency; neg = dependent)
dx = D.load_depmap_expression()                # cells x genes (expression)
prism = D.load_prism(); prism["k"] = prism["name"].str.lower().str.strip()
cos2dep,_ = D.load_cosmic_depmap_map()
gdsc = D.load_gdsc_response(); gdsc = gdsc[gdsc["COSMIC_ID"].isin(cos2dep)].copy(); gdsc["dep"]=gdsc["COSMIC_ID"].map(cos2dep); gdsc["k"]=gdsc["DRUG_NAME"].str.lower().str.strip()

# shared feature genes + z-scored expression (cells x genes)
genes = list(dx.columns[dx.var(0).values.argsort()[::-1]][:TOPN])
Xexpr = D.z_rows(dx[genes].T).T                # cells x topN (z per gene)
targets = sorted(set(g for _, g in PAIRS))
# Step 1: expr -> dependency, out-of-fold predicted dep̂ per target gene
dep_hat = {}; dep_cv_rho = {}
for g in targets:
    if g not in ce.columns: continue
    cells = [c for c in Xexpr.index if c in ce.index and np.isfinite(ce.loc[c, g])]
    if len(cells) < 100: continue
    Xg = Xexpr.loc[cells].values; yg = ce.loc[cells, g].values.astype(float)
    kf = KFold(5, shuffle=True, random_state=SEED); pr = np.empty(len(yg))
    for tri, tei in kf.split(Xg):
        pr[tei] = RidgeCV(alphas=[10.,100.,1000.]).fit(Xg[tri], yg[tri]).predict(Xg[tei])
    dep_hat[g] = pd.Series(pr, index=cells); dep_cv_rho[g] = float(stats.spearmanr(pr, yg)[0])
print("expr->dependency CV rho:", {g: round(dep_cv_rho[g],3) for g in dep_cv_rho})

def response(drug):
    p = prism[prism["k"]==drug]
    if p["depmap_id"].nunique()>=30: return p.groupby("depmap_id")["auc"].mean()
    gg = gdsc[gdsc["k"]==drug]
    if gg["dep"].nunique()>=30: return gg.groupby("dep")["LN_IC50"].mean()
    return None

rows=[]
for drug,g in PAIRS:
    if g not in dep_hat or g not in ce.columns: continue
    resp = response(drug)
    if resp is None: continue
    cells=[c for c in resp.index if c in dep_hat[g].index and c in ce.index and c in dx.index and np.isfinite(dx.loc[c,g])]
    if len(cells)<MIN_CELLS: continue
    y=resp[cells].values.astype(float)
    r_inf = stats.spearmanr(dep_hat[g][cells].values, y)[0]         # inferred dependency -> drug
    r_expr= stats.spearmanr(dx.loc[cells,g].values, y)[0]           # baseline target expression -> drug
    r_true= stats.spearmanr(ce.loc[cells,g].values, y)[0]           # true dependency -> drug (upper bound)
    rows.append({"drug":drug,"gene":g,"n":len(cells),"cv_expr_to_dep":round(dep_cv_rho[g],3),
                 "rho_inferred":round(float(r_inf),4),"rho_expr":round(float(r_expr),4),"rho_true":round(float(r_true),4)})

n=len(rows); rng=np.random.default_rng(SEED)
inf_abs=np.array([abs(r["rho_inferred"]) for r in rows]); expr_abs=np.array([abs(r["rho_expr"]) for r in rows]); true_abs=np.array([abs(r["rho_true"]) for r in rows])
obs=float(np.median(inf_abs)-np.median(expr_abs)); do=np.column_stack([inf_abs,expr_abs])
null=np.array([(lambda f: np.median(np.where(f,do[:,1],do[:,0]))-np.median(np.where(f,do[:,0],do[:,1])))(rng.integers(0,2,n).astype(bool)) for _ in range(K)])
p_h1=(np.sum(null>=obs)+1)/(K+1); H1=bool(obs>0 and p_h1<0.05)
recov=float(np.mean([r["rho_inferred"]/r["rho_true"] for r in rows if r["rho_true"]>0.1 and r["rho_inferred"]>0])) if any(r["rho_true"]>0.1 for r in rows) else np.nan

print(f"\npairs: {n}")
for r in sorted(rows,key=lambda x:-abs(x["rho_inferred"])):
    print(f"  {r['drug']:<13}->{r['gene']:<7} n={r['n']:>3} inferred={r['rho_inferred']:+.3f} expr={r['rho_expr']:+.3f} true={r['rho_true']:+.3f} (expr->dep CV={r['cv_expr_to_dep']:+.2f})")
print(f"\nH1 inferred-dep beats baseline expression: median|inf|={np.median(inf_abs):.3f} vs median|expr|={np.median(expr_abs):.3f} diff={obs:+.3f} perm p={p_h1:.4g} -> {H1}")
print(f"recovery of true-dependency signal: {recov:.2f}" if np.isfinite(recov) else "recovery: n/a")
verdict=("INFERRED-DEPENDENCY LAYER works: expression->inferred-dependency beats baseline expression (patient-translatable functional layer)" if H1
         else "Inferred dependency does NOT beat baseline expression here (dependency not learnable enough / no gain) — honest bound")
print("VERDICT:",verdict)

out={"git_sha":os.popen("git rev-parse HEAD").read().strip(),"python":sys.version.split()[0],"sklearn":sklearn.__version__,
     "timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"seed":SEED,"K":K,"n_pairs":n,
     "expr_to_dep_cv_rho":{g:round(dep_cv_rho[g],4) for g in dep_cv_rho},"pairs":rows,
     "H1_median_inferred":round(float(np.median(inf_abs)),4),"H1_median_expr":round(float(np.median(expr_abs)),4),
     "H1_diff":round(obs,4),"H1_perm_p":float(p_h1),"H1_pass":H1,
     "recovery_fraction":(round(recov,3) if np.isfinite(recov) else None),"verdict":verdict}
os.makedirs(os.path.join(HERE,"results"),exist_ok=True)
json.dump(out,open(os.path.join(HERE,"results","B13_metrics.json"),"w"),indent=2)
print("wrote results/B13_metrics.json")
