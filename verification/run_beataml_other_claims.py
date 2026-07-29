import json, numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
D="data/beataml/"
fits=pd.read_csv(D+"beataml_probit_curve_fits_v4_dbgap.txt",sep="\t")
clin=pd.read_excel(D+"beataml_wv1to4_clinical.xlsx")
mut=pd.read_csv(D+"beataml_wes_wv1to4_mutations_dbgap.txt",sep="\t")
def pos(x):
    s=str(x).strip().lower(); return 1 if s in ("positive","yes","mutated","pos","present") else (0 if s in ("negative","no","wildtype","wt","neg","absent") else np.nan)
base=clin[["dbgap_subject_id","dbgap_dnaseq_sample","FLT3-ITD","NPM1"]].copy()
base["ITD"]=base["FLT3-ITD"].map(pos); base["NPM1m"]=base["NPM1"].map(pos)
def wes_status(gene):
    s=set(mut[mut.symbol==gene]["dbgap_sample_id"].unique()); return base["dbgap_dnaseq_sample"].isin(s).astype(float)
for g in ["NRAS","DNMT3A"]: base[g]=wes_status(g)
def drug_auc(name):
    d=fits[fits.inhibitor.str.lower()==name.lower()].groupby("dbgap_subject_id")["auc"].median().reset_index(); return d
def mw(a,b): return stats.mannwhitneyu(a,b,alternative="two-sided")[1]

print("=== NRAS -> MEK inhibitors (expected KNOWN RAS/MAPK biology; check 3-drug consistency) ===")
res={"nras_mek":{}}
for drug in ["Selumetinib (AZD6244)","Trametinib (GSK1120212)","Selumetinib","Trametinib","CI-1040 (PD184352)","CI-1040"]:
    da=drug_auc(drug)
    if len(da)<20: continue
    df=da.merge(base,on="dbgap_subject_id").dropna(subset=["auc","NRAS"])
    m=df[df.NRAS==1]["auc"]; w=df[df.NRAS==0]["auc"]
    if len(m)>3 and len(w)>3:
        p=mw(m,w); res["nras_mek"][drug]={"n_mut":int(len(m)),"n_wt":int(len(w)),"med_mut":round(float(m.median()),1),"med_wt":round(float(w.median()),1),"p":float(p)}
        print(f"  {drug:28.28s} NRASmut={m.median():.1f} wt={w.median():.1f} (mut {'MORE' if m.median()<w.median() else 'LESS'} sensitive) p={p:.3e} n={len(m)}/{len(w)}")

print("\n=== DNMT3A -> Dasatinib (deconfound vs NPM1 + FLT3-ITD) ===")
da=drug_auc("Dasatinib")
df=da.merge(base,on="dbgap_subject_id").dropna(subset=["auc","DNMT3A"])
m=df[df.DNMT3A==1]["auc"]; w=df[df.DNMT3A==0]["auc"]
p=mw(m,w)
print(f"  reproduce: DNMT3Amut={m.median():.1f} wt={w.median():.1f} diff={w.median()-m.median():.1f} p={p:.3e} n={len(m)}/{len(w)}")
d2=df.dropna(subset=["DNMT3A","NPM1m","ITD"])
ols=sm.OLS(d2["auc"], sm.add_constant(d2[["DNMT3A","NPM1m","ITD"]].astype(float))).fit()
print(f"  OLS auc ~ DNMT3A + NPM1 + FLT3-ITD (n={len(d2)}): DNMT3A beta={ols.params['DNMT3A']:+.1f} p={ols.pvalues['DNMT3A']:.3e} | NPM1 p={ols.pvalues['NPM1m']:.3e} | ITD p={ols.pvalues['ITD']:.3e}")
dnmt_indep = ols.pvalues["DNMT3A"]<0.05 and ols.params["DNMT3A"]<0
res["dnmt3a_dasatinib"]={"reproduce_p":float(p),"n_mut":int(len(m)),"n_wt":int(len(w)),"ols_dnmt_beta":float(ols.params["DNMT3A"]),"ols_dnmt_p":float(ols.pvalues["DNMT3A"]),"independent":bool(dnmt_indep)}
res["nras_mek_consistent"]=all(v["p"]<0.05 and v["med_mut"]<v["med_wt"] for v in res["nras_mek"].values()) if res["nras_mek"] else False
print(f"\nNRAS->MEK consistent across drugs (all sig, correct dir)? {res['nras_mek_consistent']}")
print(f"DNMT3A->Dasatinib independent of NPM1/FLT3-ITD? {dnmt_indep}")
json.dump(res, open("verification/beataml_other_claims_metrics.json","w"), indent=2)
print("wrote verification/beataml_other_claims_metrics.json")
