"""B14 — does the expression->inferred-dependency functional layer improve PATIENT (BeatAML ex-vivo) drug
prediction over the direct transcriptomic transfer? Implements prereg/B14_functional_layer_patients.md.
Culmination of the functional-inference thesis (B12/B13). Reproduce x2. Aggregate outputs only.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
from sklearn.linear_model import RidgeCV
import sklearn, warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.engine import InterceptaEngine
from intercepta.metrics import bh_fdr
from intercepta.axes import compute_r_prolif

SEED, K, TOPN, MIN_PT = 42, 2000, 2000, 15
HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = [("trametinib","MAP2K1"),("selumetinib","MAP2K1"),("sorafenib","FLT3"),("quizartinib","FLT3"),
         ("gilteritinib","FLT3"),("crenolanib","FLT3"),("venetoclax","BCL2"),("erlotinib","EGFR"),
         ("gefitinib","EGFR"),("afatinib","EGFR")]
print("B14 functional layer on patients | sklearn", sklearn.__version__, flush=True)

ce = D.load_depmap_crispr(); dx = D.load_depmap_expression()
bx = D.load_beataml_expression()               # genes(symbol) x patient samples
auc = D.load_beataml_auc()
targets = sorted(set(g for _, g in PAIRS))

# shared feature genes across DepMap ∩ BeatAML; z per gene within each dataset
genes = [g for g in dx.columns[dx.var(0).values.argsort()[::-1]] if g in set(bx.index)][:TOPN]
Xdep = D.z_rows(dx[genes].T).T.fillna(0.0)                  # DepMap cells x genes (z)
Xbea = D.z_rows(bx.loc[genes]).T.fillna(0.0)               # BeatAML patients x genes (z)

# train expr->dependency per target on DepMap (full fit), apply to BeatAML
inferred = {}
for g in targets:
    if g not in ce.columns: continue
    cells = [c for c in Xdep.index if c in ce.index and np.isfinite(ce.loc[c, g])]
    if len(cells) < 100: continue
    m = RidgeCV(alphas=[10.,100.,1000.]).fit(Xdep.loc[cells].values, ce.loc[cells, g].values.astype(float))
    inferred[g] = pd.Series(m.predict(Xbea.values), index=Xbea.index)   # inferred dep per BeatAML patient
print("inferred-dependency targets:", list(inferred))

# direct transfer (engine, PRISM-trained) for the drugs
drugs = sorted(set(d for d, _ in PAIRS))
eng = InterceptaEngine().fit(drugs=drugs, compute_calibration=False, label_source="prism")
direct = eng.predict_transfer(bx) if eng.fitted_drugs_ else pd.DataFrame(index=bx.columns)
Rp = compute_r_prolif(bx)
auc = auc[auc["sample"].isin(set(bx.columns))]

def resid(x, c):
    x=np.asarray(x,float); c=np.asarray(c,float); A=np.column_stack([np.ones_like(c),c]); b,*_=np.linalg.lstsq(A,x,rcond=None); return x-A@b

rows=[]; rinf=[]; rdir=[]
for drug, g in PAIRS:
    if g not in inferred: continue
    a = auc[auc["drug"]==drug].groupby("sample")["auc"].mean()
    cells=[s for s in a.index if s in inferred[g].index]
    if len(cells)<MIN_PT: continue
    y=a[cells].values; rp=Rp[cells].values
    yr=resid(y,rp)
    r_inf = stats.spearmanr(resid(inferred[g][cells].values, rp), yr)[0]
    r_dir = stats.spearmanr(resid(direct.loc[cells,drug].values, rp), yr)[0] if drug in direct.columns else np.nan
    rows.append({"drug":drug,"target":g,"n":len(cells),"rho_inferred_dep":round(float(r_inf),4),
                 "rho_direct_transfer":(round(float(r_dir),4) if np.isfinite(r_dir) else None)})
    rinf.append(r_inf);  rdir.append(r_dir if np.isfinite(r_dir) else np.nan)

rinf=np.array(rinf); n=len(rows); rng=np.random.default_rng(SEED)
# H1: pooled inferred-dep -> AUC, permutation (patient labels per drug)
cells_by={r["drug"]+"|"+r["target"]:[s for s in auc[auc["drug"]==r["drug"]].groupby("sample")["auc"].mean().index if s in inferred[r["target"]].index] for r in rows}
def pooled_perm():
    vals=[]
    for r in rows:
        g=r["target"]; a=auc[auc["drug"]==r["drug"]].groupby("sample")["auc"].mean(); cells=[s for s in a.index if s in inferred[g].index]
        rp=Rp[cells].values; yr=resid(rng.permutation(a[cells].values),rp); vals.append(stats.spearmanr(resid(inferred[g][cells].values,rp),yr)[0])
    return np.mean(vals)
obs1=np.nanmean(rinf); null1=np.array([pooled_perm() for _ in range(K)]); p_h1=(np.sum(null1>=obs1)+1)/(K+1); H1=bool(obs1>0 and p_h1<0.05)
# H2: |inferred| vs |direct|, paired sign-flip
both=[(abs(r["rho_inferred_dep"]),abs(r["rho_direct_transfer"])) for r in rows if r["rho_direct_transfer"] is not None]
if len(both)>=4:
    da=np.array([x[0] for x in both]); ea=np.array([x[1] for x in both]); obs2=float(np.median(da)-np.median(ea)); do=np.column_stack([da,ea]); m=len(both)
    null2=np.array([(lambda f:np.median(np.where(f,do[:,1],do[:,0]))-np.median(np.where(f,do[:,0],do[:,1])))(rng.integers(0,2,m).astype(bool)) for _ in range(K)])
    p_h2=(np.sum(null2>=obs2)+1)/(K+1); H2=bool(obs2>0 and p_h2<0.05)
else: obs2,p_h2,H2=np.nan,np.nan,False

print(f"\npairs: {n}")
for r in sorted(rows,key=lambda x:-x["rho_inferred_dep"]):
    print(f"  {r['drug']:<13}->{r['target']:<7} n={r['n']:>3} inferred_dep_rho={r['rho_inferred_dep']:+.3f}  direct_transfer_rho={r['rho_direct_transfer']}")
print(f"\nH1 inferred-dep -> BeatAML ex-vivo (prolif-resid): pooled ρ={obs1:+.4f} perm p={p_h1:.4g} -> {H1}")
print(f"H2 inferred-dep vs direct transfer: median|inf|={np.median([abs(r['rho_inferred_dep']) for r in rows]):.3f} vs median|direct|={np.median([abs(x[1]) for x in both]) if both else float('nan'):.3f} diff={obs2 if np.isfinite(obs2) else float('nan'):+.3f} perm p={p_h2 if np.isfinite(p_h2) else float('nan'):.4g} -> {H2}")
if H1 and H2: verdict="FUNCTIONAL LAYER TRANSLATES: expression->inferred-dependency predicts BeatAML ex-vivo response AND beats the direct transfer (novel, patient-relevant advance; to confirm in Track-1)"
elif H1: verdict="inferred-dependency predicts BeatAML ex-vivo response but NOT better than direct transfer (real, not an improvement)"
else: verdict="NULL: inferred-dependency does not translate to BeatAML ex-vivo (bounds the functional-inference thesis; honest)"
print("VERDICT:",verdict)

out={"git_sha":os.popen("git rev-parse HEAD").read().strip(),"python":sys.version.split()[0],"sklearn":sklearn.__version__,
     "timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"seed":SEED,"K":K,"n_pairs":n,"pairs":rows,
     "H1_pooled_rho":round(float(obs1),4),"H1_perm_p":float(p_h1),"H1_pass":H1,
     "H2_diff_medabs":(round(obs2,4) if np.isfinite(obs2) else None),"H2_perm_p":(float(p_h2) if np.isfinite(p_h2) else None),"H2_pass":H2,"verdict":verdict}
os.makedirs(os.path.join(HERE,"results"),exist_ok=True)
json.dump(out,open(os.path.join(HERE,"results","B14_metrics.json"),"w"),indent=2)
print("wrote results/B14_metrics.json")
