import json, numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
D="data/beataml/"
fits=pd.read_csv(D+"beataml_probit_curve_fits_v4_dbgap.txt", sep="\t")
clin=pd.read_excel(D+"beataml_wv1to4_clinical.xlsx")
cabo=fits[fits["inhibitor"].str.lower()=="cabozantinib"][["dbgap_subject_id","auc"]].dropna()
cabo=cabo.groupby("dbgap_subject_id")["auc"].median().reset_index()   # one AUC/subject
c=clin[["dbgap_subject_id","FLT3-ITD","NPM1"]].copy()
def pos(x):
    s=str(x).strip().lower()
    return 1 if s in ("positive","yes","mutated","mutation","present","pos","1","true") else (0 if s in ("negative","no","wildtype","wt","absent","neg","0","false") else np.nan)
c["ITD"]=c["FLT3-ITD"].map(pos); c["NPM1m"]=c["NPM1"].map(pos)
df=cabo.merge(c, on="dbgap_subject_id").dropna(subset=["auc","NPM1m"])
def mw(a,b): 
    u,p=stats.mannwhitneyu(a,b,alternative="two-sided"); return p
mut=df[df.NPM1m==1]["auc"]; wt=df[df.NPM1m==0]["auc"]
p_repro=mw(mut,wt)
print(f"REPRODUCE NPM1-mut vs wt Cabozantinib: n_mut={len(mut)} n_wt={len(wt)} "
      f"median_mut={mut.median():.1f} median_wt={wt.median():.1f} diff={wt.median()-mut.median():.1f} p={p_repro:.3e}")
# confound 1: FLT3-ITD
di=df.dropna(subset=["ITD"]); im=di[di.ITD==1]["auc"]; iw=di[di.ITD==0]["auc"]
print(f"FLT3-ITD pos vs neg Cabozantinib: n_pos={len(im)} n_neg={len(iw)} median_pos={im.median():.1f} median_neg={iw.median():.1f} p={mw(im,iw):.3e}")
# confound 2: within ITD-negative
neg=di[di.ITD==0]; nm=neg[neg.NPM1m==1]["auc"]; nw=neg[neg.NPM1m==0]["auc"]
p_itdneg=mw(nm,nw) if (len(nm)>3 and len(nw)>3) else float("nan")
print(f"WITHIN ITD-negative, NPM1-mut vs wt: n_mut={len(nm)} n_wt={len(nw)} median_mut={nm.median():.1f} median_wt={nw.median():.1f} p={p_itdneg:.3e}")
# confound 3: OLS auc ~ NPM1 + ITD
d3=di.dropna(subset=["NPM1m","ITD"])
m=sm.OLS(d3["auc"], sm.add_constant(d3[["NPM1m","ITD"]].astype(float))).fit()
npm1_beta=float(m.params["NPM1m"]); npm1_p=float(m.pvalues["NPM1m"]); itd_beta=float(m.params["ITD"]); itd_p=float(m.pvalues["ITD"])
print(f"OLS auc ~ NPM1 + FLT3-ITD (n={len(d3)}): NPM1 beta={npm1_beta:+.1f} p={npm1_p:.3e} | ITD beta={itd_beta:+.1f} p={itd_p:.3e}")
# co-occurrence
ct=pd.crosstab(d3.NPM1m, d3.ITD)
print("NPM1 x ITD co-occurrence:\n", ct.to_string())
reproduced = p_repro<1e-6 and mut.median()<wt.median() and len(mut)>=100
independent = (p_itdneg<0.05 and nm.median()<nw.median()) and (npm1_p<0.05 and npm1_beta<0)
verdict = "NPM1 INDEPENDENT of FLT3-ITD (survives)" if independent else "NPM1 (partly) FLT3-ITD-CONFOUNDED"
print(f"\nVERDICT: reproduced={reproduced} | {verdict}")
out={"reproduce_p":float(p_repro),"n_mut":int(len(mut)),"n_wt":int(len(wt)),
     "median_mut":float(mut.median()),"median_wt":float(wt.median()),
     "flt3itd_p":float(mw(im,iw)),"within_itdneg_npm1_p":float(p_itdneg),
     "ols_npm1_beta":npm1_beta,"ols_npm1_p":npm1_p,"ols_itd_beta":itd_beta,"ols_itd_p":itd_p,
     "cooccurrence":ct.to_dict(),"reproduced":bool(reproduced),"npm1_independent":bool(independent),"verdict":verdict}
json.dump(out, open("verification/beataml_npm1_cabo_metrics.json","w"), indent=2)
print("wrote verification/beataml_npm1_cabo_metrics.json")
