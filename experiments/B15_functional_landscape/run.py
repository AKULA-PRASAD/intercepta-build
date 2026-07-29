"""B15 — how broadly does the expression->inferred-dependency layer rescue BeatAML ex-vivo drug prediction?
Systematic map across pre-declared actionable drug->target pairs. Implements prereg/B15_functional_layer_landscape.md.
Generalizes B14/V17. Reproduce x2. Aggregate outputs only.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold
import sklearn, warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.engine import InterceptaEngine
from intercepta.metrics import bh_fdr
from intercepta.axes import compute_r_prolif

SEED, K, TOPN, MIN_PT, CV_MIN = 42, 2000, 2000, 15, 0.15
HERE = os.path.dirname(os.path.abspath(__file__))
# pre-declared drug -> primary target gene (established pharmacology)
D2T = {"sorafenib":"FLT3","quizartinib":"FLT3","gilteritinib":"FLT3","crenolanib":"FLT3","kw-2449":"FLT3",
       "dovitinib":"FLT3","tandutinib":"FLT3","midostaurin":"FLT3","venetoclax":"BCL2","ibrutinib":"BTK",
       "entospletinib":"SYK","prt062607":"SYK","ruxolitinib":"JAK2","tofacitinib":"JAK1","trametinib":"MAP2K1",
       "selumetinib":"MAP2K1","crizotinib":"MET","foretinib":"MET","erlotinib":"EGFR","gefitinib":"EGFR",
       "afatinib":"EGFR","nilotinib":"ABL1","dasatinib":"ABL1","ponatinib":"ABL1","imatinib":"ABL1",
       "sunitinib":"KIT","axitinib":"KDR","cediranib":"KDR","alisertib":"AURKA","selinexor":"XPO1",
       "sns-032":"CDK9","flavopiridol":"CDK9","lapatinib":"ERBB2"}
print("B15 functional-inference landscape | sklearn", sklearn.__version__, flush=True)

ce = D.load_depmap_crispr(); dx = D.load_depmap_expression()
bx = D.load_beataml_expression(); auc = D.load_beataml_auc()
auc = auc[auc["sample"].isin(set(bx.columns))]
genes = [g for g in dx.columns[dx.var(0).values.argsort()[::-1]] if g in set(bx.index)][:TOPN]
Xdep = D.z_rows(dx[genes].T).T.fillna(0.0); Xbea = D.z_rows(bx.loc[genes]).T.fillna(0.0)
Rp = compute_r_prolif(bx)

# train expr->dep for each needed target (learnable filter via 5-fold CV)
targets = sorted(set(D2T.values()))
inferred = {}; cvrho = {}
for g in targets:
    if g not in ce.columns: continue
    cells = [c for c in Xdep.index if c in ce.index and np.isfinite(ce.loc[c, g])]
    if len(cells) < 100: continue
    Xg = Xdep.loc[cells].values; yg = ce.loc[cells, g].values.astype(float)
    kf = KFold(5, shuffle=True, random_state=SEED); pr = np.empty(len(yg))
    for tri, tei in kf.split(Xg): pr[tei] = RidgeCV(alphas=[10.,100.,1000.]).fit(Xg[tri], yg[tri]).predict(Xg[tei])
    cvrho[g] = float(stats.spearmanr(pr, yg)[0])
    if cvrho[g] >= CV_MIN:
        inferred[g] = pd.Series(RidgeCV(alphas=[10.,100.,1000.]).fit(Xg, yg).predict(Xbea.values), index=Xbea.index)
print("targets learnable (CV>=%.2f):" % CV_MIN, {g: round(cvrho[g],2) for g in inferred})

drugs_avail = [d for d in D2T if D2T[d] in inferred and auc[auc["drug"]==d]["sample"].nunique() >= MIN_PT]
eng = InterceptaEngine().fit(drugs=list(set(drugs_avail)), compute_calibration=False, label_source="prism")
direct = eng.predict_transfer(bx) if eng.fitted_drugs_ else pd.DataFrame(index=bx.columns)

def resid(x, c):
    x=np.asarray(x,float); c=np.asarray(c,float); A=np.column_stack([np.ones_like(c),c]); b,*_=np.linalg.lstsq(A,x,rcond=None); return x-A@b
def one_sided_p(r,nn):
    if not np.isfinite(r) or nn<6: return np.nan
    return float(stats.norm.sf(np.arctanh(np.clip(r,-0.999,0.999))*np.sqrt(nn-3)))

rows=[]
for d in drugs_avail:
    g=D2T[d]; a=auc[auc["drug"]==d].groupby("sample")["auc"].mean(); cells=[s for s in a.index if s in inferred[g].index]
    if len(cells)<MIN_PT: continue
    y=a[cells].values; rp=Rp[cells].values; yr=resid(y,rp)
    r_inf=stats.spearmanr(resid(inferred[g][cells].values,rp),yr)[0]
    r_dir=stats.spearmanr(resid(direct.loc[cells,d].values,rp),yr)[0] if d in direct.columns else np.nan
    rows.append({"drug":d,"target":g,"n":len(cells),"rho_inferred":round(float(r_inf),4),
                 "rho_direct":(round(float(r_dir),4) if np.isfinite(r_dir) else None),"inf_p":one_sided_p(r_inf,len(cells))})
n=len(rows); rng=np.random.default_rng(SEED)
bh=bh_fdr([r["inf_p"] for r in rows])
for r,q in zip(rows,bh):
    r["inf_BHq"]=float(q); r["rescued"]=bool(q<0.05 and r["rho_inferred"]>0 and (r["rho_direct"] is None or abs(r["rho_inferred"])>abs(r["rho_direct"])))
both=[(abs(r["rho_inferred"]),abs(r["rho_direct"])) for r in rows if r["rho_direct"] is not None]
if len(both)>=4:
    da=np.array([x[0] for x in both]); ea=np.array([x[1] for x in both]); obs=float(np.median(da)-np.median(ea)); do=np.column_stack([da,ea]); m=len(both)
    null=np.array([(lambda f:np.median(np.where(f,do[:,1],do[:,0]))-np.median(np.where(f,do[:,0],do[:,1])))(rng.integers(0,2,m).astype(bool)) for _ in range(K)])
    p_h1=(np.sum(null>=obs)+1)/(K+1); H1=bool(obs>0 and p_h1<0.05)
else: obs,p_h1,H1=np.nan,np.nan,False
n_res=sum(r["rescued"] for r in rows)

print(f"\ntested drugs: {n}")
for r in sorted(rows,key=lambda x:-x["rho_inferred"]):
    print(f"  {r['drug']:<13}->{r['target']:<7} n={r['n']:>3} inferred={r['rho_inferred']:+.3f}(BHq={r['inf_BHq']:.3g}) direct={r['rho_direct']} rescued={r['rescued']}")
print(f"\nH1 broad: median|inferred|={np.median([abs(r['rho_inferred']) for r in rows]):.3f} vs median|direct|={np.median([x[1] for x in both]) if both else float('nan'):.3f} diff={obs if np.isfinite(obs) else float('nan'):+.3f} perm p={p_h1 if np.isfinite(p_h1) else float('nan'):.4g} -> {H1}")
print(f"drugs 'rescued' (inferred sig BH<0.05 & > direct): {n_res}/{n}")
rescued_targets=sorted(set(r["target"] for r in rows if r["rescued"]))
print("rescued target classes:", rescued_targets)
verdict=("BROAD: functional-inference layer beats direct transfer across actionable targets" if H1
         else f"SPECIFIC: functional layer rescues a coherent subset ({n_res}/{n} drugs; targets {rescued_targets}), not broadly — precise, actionable map")
if n_res==0: verdict="NULL: no drug rescued by the functional layer (bounds V17)"
print("VERDICT:",verdict)

out={"git_sha":os.popen("git rev-parse HEAD").read().strip(),"python":sys.version.split()[0],"sklearn":sklearn.__version__,
     "timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"seed":SEED,"K":K,"n_drugs":n,
     "learnable_targets_cvrho":{g:round(cvrho[g],3) for g in inferred},"pairs":rows,
     "H1_diff_medabs":(round(obs,4) if np.isfinite(obs) else None),"H1_perm_p":(float(p_h1) if np.isfinite(p_h1) else None),"H1_broad_pass":H1,
     "n_rescued":n_res,"rescued_targets":rescued_targets,"verdict":verdict}
os.makedirs(os.path.join(HERE,"results"),exist_ok=True)
json.dump(out,open(os.path.join(HERE,"results","B15_metrics.json"),"w"),indent=2)
print("wrote results/B15_metrics.json")
