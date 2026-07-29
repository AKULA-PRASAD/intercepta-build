"""B16 — does inferred-FLT3-dependency predict FLT3-inhibitor ex-vivo response BEYOND FLT3-ITD status?
The decisive test of whether the functional-inference layer adds over the standard clinical biomarker.
Implements prereg/B16_beyond_mutation.md. Reproduce x2. Aggregate outputs only.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
import sklearn, warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.engine import InterceptaEngine
from intercepta.metrics import bh_fdr
from intercepta.axes import compute_r_prolif

SEED, MIN_N, MIN_WT = 42, 25, 15
HERE = os.path.dirname(os.path.abspath(__file__))
FLT3I = ["sorafenib", "quizartinib", "gilteritinib", "crenolanib"]
print("B16 beyond-mutation | sklearn", sklearn.__version__, flush=True)

# engine + inferred FLT3 dependency on BeatAML
eng = InterceptaEngine().fit(drugs=FLT3I, compute_calibration=False, label_source="prism")
eng.fit_dependency(["FLT3"])
bx = D.load_beataml_expression()
inf_flt3 = eng.infer_dependency(bx)["FLT3"]                 # per sample (more negative = more dependent)
Rp = compute_r_prolif(bx)
auc = D.load_beataml_auc(); auc = auc[auc["sample"].isin(set(bx.columns))]

# FLT3-ITD per rnaseq_sample (clinical)
clin = D.load_beataml_clinical().dropna(subset=["dbgap_rnaseq_sample"]).drop_duplicates("dbgap_rnaseq_sample").set_index("dbgap_rnaseq_sample")
def pos(x):
    s=str(x).strip().lower(); return 1.0 if s in ("positive","yes","mutated","pos") else (0.0 if s in ("negative","no","wildtype","wt","neg") else np.nan)
itd = clin["FLT3-ITD"].map(pos)

def z(a): a=np.asarray(a,float); s=a.std(); return (a-a.mean())/s if s>0 else a-a.mean()
rows=[]; itdwt_rho=[]
for drug in FLT3I:
    a = auc[auc["drug"]==drug].groupby("sample")["auc"].mean()
    samp=[s for s in a.index if s in inf_flt3.index and s in itd.index and np.isfinite(itd[s])]
    if len(samp)<MIN_N: continue
    y=a[samp].values.astype(float); dep=inf_flt3[samp].values.astype(float); it=itd[samp].values.astype(float); rp=Rp[samp].values.astype(float)
    # OLS AUC ~ inferred_dep + FLT3_ITD + prolif  (does dep add beyond ITD?)
    X=np.column_stack([z(dep), it, z(rp)])
    res=sm.OLS(y, sm.add_constant(X, has_constant="add")).fit()
    b_dep=float(res.params[1]); p_dep=float(res.pvalues[1]); se_dep=float(res.bse[1]); p_itd=float(res.pvalues[2])
    # within ITD-WT: does inferred dep predict sensitivity?
    wt=[i for i in range(len(samp)) if it[i]==0]
    r_wt=stats.spearmanr(dep[wt], y[wt])[0] if len(wt)>=MIN_WT else np.nan
    rows.append({"drug":drug,"n":len(samp),"n_itd":int(it.sum()),"n_itdwt":len(wt),
                 "dep_beyond_itd_beta":round(b_dep,3),"dep_beyond_itd_p":p_dep,"dep_se":round(se_dep,4),
                 "dep_sensitizing":bool(b_dep>0),  # positive: less-dependent(higher dep val)->higher AUC(resistant)
                 "itd_p":round(p_itd,4),
                 "itdwt_rho":(round(float(r_wt),4) if np.isfinite(r_wt) else None)})
    if np.isfinite(r_wt): itdwt_rho.append((len(wt), r_wt))

bh=bh_fdr([r["dep_beyond_itd_p"] for r in rows])
for r,q in zip(rows,bh): r["dep_BHq"]=float(q)
# H1: DL meta of standardized inferred_dep coef (expect >0 = sensitizing beyond ITD)
b=np.array([r["dep_beyond_itd_beta"] for r in rows]); se=np.array([r["dep_se"] for r in rows]); w=1/se**2
mu_f=np.sum(w*b)/np.sum(w); Q=np.sum(w*(b-mu_f)**2); k=len(b); tau2=max(0,(Q-(k-1))/(np.sum(w)-np.sum(w**2)/np.sum(w))) if k>1 else 0
wr=1/(se**2+tau2); mu=float(np.sum(wr*b)/np.sum(wr)); se_mu=float(np.sqrt(1/np.sum(wr))); p_h1=float(2*stats.norm.sf(abs(mu/se_mu)))
H1=bool(mu>0 and p_h1<0.05)
# H2: pooled ITD-WT (sample-size-weighted mean rho + combined)
if itdwt_rho:
    ns=np.array([x[0] for x in itdwt_rho]); rs=np.array([x[1] for x in itdwt_rho]); h2_rho=float(np.sum(ns*rs)/np.sum(ns))
    zc=np.arctanh(np.clip(rs,-0.999,0.999)); zse=1/np.sqrt(ns-3); zmu=np.sum(zc/zse**2)/np.sum(1/zse**2); zsem=np.sqrt(1/np.sum(1/zse**2)); p_h2=float(stats.norm.sf(zmu/zsem))
    H2=bool(h2_rho>0 and p_h2<0.05)
else: h2_rho,p_h2,H2=np.nan,np.nan,False

print(f"\nFLT3 inhibitors tested: {len(rows)}")
for r in rows:
    print(f"  {r['drug']:<13} n={r['n']:>3} ITD={r['n_itd']:>3} | dep-beyond-ITD beta={r['dep_beyond_itd_beta']:+.2f} p={r['dep_beyond_itd_p']:.3g} BHq={r['dep_BHq']:.3g} | ITD-WT rho={r['itdwt_rho']} (n_wt={r['n_itdwt']})")
print(f"\nH1 inferred-dep adds BEYOND FLT3-ITD: meta beta={mu:+.3f} (SE {se_mu:.3f}) p={p_h1:.4g} -> {H1}")
print(f"H2 predicts within FLT3-ITD-WT: pooled rho={h2_rho if np.isfinite(h2_rho) else float('nan'):+.4f} p={p_h2 if np.isfinite(p_h2) else float('nan'):.4g} -> {H2}")
if H1 and H2: verdict="GENUINE ADVANCE: inferred-FLT3-dependency predicts FLT3i response BEYOND FLT3-ITD, including in ITD-WT patients (adds over standard biomarker)"
elif H1: verdict="inferred-dep adds beyond FLT3-ITD overall, but not clearly in ITD-WT subset"
elif H2: verdict="inferred-dep predicts within ITD-WT but does not robustly add beyond ITD overall"
else: verdict="REDUNDANT: inferred-FLT3-dep does not add beyond FLT3-ITD (re-detects the known biomarker) — honest bound"
print("VERDICT:",verdict)

out={"git_sha":os.popen("git rev-parse HEAD").read().strip(),"python":sys.version.split()[0],"sklearn":sklearn.__version__,
     "timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"seed":SEED,"n_drugs":len(rows),"pairs":rows,
     "H1_meta_beta":round(mu,4),"H1_p":float(p_h1),"H1_pass":H1,
     "H2_itdwt_pooled_rho":(round(h2_rho,4) if np.isfinite(h2_rho) else None),"H2_p":(float(p_h2) if np.isfinite(p_h2) else None),"H2_pass":H2,"verdict":verdict}
os.makedirs(os.path.join(HERE,"results"),exist_ok=True)
json.dump(out,open(os.path.join(HERE,"results","B16_metrics.json"),"w"),indent=2)
print("wrote results/B16_metrics.json")
