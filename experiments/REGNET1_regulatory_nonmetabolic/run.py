"""REGNET1 — does a CURATED transcriptional regulatory network (master-regulator influence) predict NON-METABOLIC
essentiality BEYOND conservation, and SURVIVE a study-bias control? The principled third attack (after MET4 PPI /
NONMET1 synteny). Reuses NONMET1 cached E. coli pool + Abasy curated GRN. Deterministic. Env: intercepta-build.
Pre-registered in PREREG.md (frozen before results)."""
import os, re, json, hashlib
import numpy as np
import networkx as nx
from scipy.stats import fisher_exact
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
ND = os.path.join(DATA, "nonmet1"); PROT = os.path.join(ND, "prot"); RBH = os.path.join(ND, "rbh")
MET2 = os.path.join(DATA, "met2", "essentiality.tsv"); PEC = os.path.join(DATA, "expval", "PECData.dat")
GRN = os.path.join(DATA, "regnet1", "eco_2005.json")
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)
PANEL = ["ecoli","mtb","salmonella","paeruginosa","bsubtilis","saureus","hpylori",
         "vcholerae","nmeningitidis","spneumoniae","kpneumoniae","ccrescentus"]
W_SYNT = 5

def load_genes(lab):
    rows=[]
    with open(os.path.join(PROT,f"{lab}.genes.tsv")) as f:
        next(f)
        for ln in f:
            r=ln.rstrip("\n").split("\t"); rows.append((r[1],float(r[2]),r[3],r[4] if len(r)>4 else ""))
    return rows
def load_rbh(foc,lab):
    o={}; p=os.path.join(RBH,f"{foc}__{lab}.m8")
    if not os.path.exists(p): return o
    for ln in open(p):
        c=ln.rstrip("\n").split("\t")
        if len(c)>=2: o.setdefault(c[0],c[1])
    return o
def context_scores(foc):
    genes=load_genes(foc); N=len(genes); panels=[l for l in PANEL if l!=foc]; P=len(panels)
    omap={}; prank={}
    for lab in panels:
        omap[lab]=load_rbh(foc,lab); prank[lab]={g[0]:i for i,g in enumerate(load_genes(lab))}
    own=np.zeros(N)
    for i in range(N):
        gi=genes[i][0]
        for lab in panels:
            if gi in omap[lab]: own[i]+=1
    own/=P
    return genes,own
def metabolic_set_ecoli():
    s=set()
    for ln in open(MET2):
        p=ln.rstrip().split("\t")
        if p[0]=="ecoli": s.add(p[1])
    return s
def pec_truth():
    ess={}; pmid={}
    with open(PEC) as f:
        next(f)
        for ln in f:
            c=ln.rstrip("\n").split("\t")
            if len(c)<10: continue
            bs=re.findall(r"\bb\d{4}\b",c[3]); e=1 if c[9].strip()=="1" else 0
            npm=len([x for x in re.split(r"[,\s]+",c[12].strip()) if x]) if len(c)>12 else 0
            for b in bs: ess[b]=e; pmid[b]=npm
    return ess,pmid

# ---- curated regulatory graph ---------------------------------------------------------------------------
gj=json.load(open(GRN))["elements"]
G=nx.DiGraph()
for e in gj["edges"]:
    d=e["data"]; G.add_edge(d["source"], d["target"])
outdeg=dict(G.out_degree()); indeg=dict(G.in_degree())
btw=nx.betweenness_centrality(G) if G.number_of_nodes()<=5000 else {n:0.0 for n in G}
def name_key(s): return s.strip().lower()
OUT={name_key(k):v for k,v in outdeg.items()}; IN={name_key(k):v for k,v in indeg.items()}; BTW={name_key(k):v for k,v in btw.items()}

# ---- build the non-metabolic pool with regulatory + conservation features + PEC label + pmid -----------
genes,own=context_scores("ecoli"); met=metabolic_set_ecoli(); ess,pmid=pec_truth()
rows=[]; mapped=0
for i,g in enumerate(genes):
    b=g[0]; uni=g[2]; nm=name_key(g[3])
    if b not in ess: continue
    if uni in met: continue                      # NON-METABOLIC subproteome only
    od=OUT.get(nm,0); ind=IN.get(nm,0); bt=BTW.get(nm,0.0)
    if nm in OUT or nm in IN: mapped+=1
    rows.append({"b":b,"name":nm,"own":own[i],"outdeg":od,"indeg":ind,"btw":bt,
                 "y":ess[b],"pmid":pmid.get(b,0)})
own_a=np.array([r["own"] for r in rows]); out_a=np.array([float(r["outdeg"]) for r in rows])
ind_a=np.array([float(r["indeg"]) for r in rows]); btw_a=np.array([r["btw"] for r in rows])
pmid_a=np.array([float(r["pmid"]) for r in rows]); y=np.array([r["y"] for r in rows])
N=len(y); K=int(y.sum()); base=K/N

# ---- (a) enrichment: high regulatory out-degree vs essentiality (Fisher) --------------------------------
# "high out-degree" = a regulator (out-degree > 0), the master-regulator hypothesis
hi=out_a>0
a=int(np.sum(hi&(y==1))); b_=int(np.sum(hi&(y==0))); c=int(np.sum(~hi&(y==1))); d=int(np.sum(~hi&(y==0)))
orr,p=fisher_exact([[a,b_],[c,d]],alternative="greater"); orr=float(orr); p=float(p)

# ---- (b) CV logistic: ΔAUROC of regulatory features BEYOND conservation --------------------------------
def cv_auroc(X):
    X=np.asarray(X,float); oof=np.zeros(N); skf=StratifiedKFold(5,shuffle=False)
    for tr,te in skf.split(X,y):
        sc=StandardScaler().fit(X[tr]); clf=LogisticRegression(max_iter=1000).fit(sc.transform(X[tr]),y[tr])
        oof[te]=clf.predict_proba(sc.transform(X[te]))[:,1]
    return float(roc_auc_score(y,oof))
au_own=cv_auroc(own_a.reshape(-1,1))
reg_feats=np.column_stack([out_a,ind_a,btw_a])
au_own_reg=cv_auroc(np.column_stack([own_a,reg_feats]))
delta=au_own_reg-au_own

# ---- (c) study-bias control: does regulatory lift survive regressing out publication count? -------------
au_own_pmid=cv_auroc(np.column_stack([own_a,pmid_a]))
au_own_pmid_reg=cv_auroc(np.column_stack([own_a,pmid_a,reg_feats]))
delta_beyond_pmid=au_own_pmid_reg-au_own_pmid
# correlation of out-degree with study proxy (is the regulatory signal just 'well-studied TF'?)
from numpy import corrcoef
r_out_pmid=float(corrcoef(out_a,pmid_a)[0,1]) if np.std(out_a)>0 and np.std(pmid_a)>0 else float("nan")

G1_delta = delta>=0.03
G1_enrich = (orr>2.0) and (p<0.01)
G1_survives = delta_beyond_pmid>=0.03
PASS = G1_delta and G1_enrich and G1_survives

metrics={
 "experiment":"REGNET1_regulatory_nonmetabolic",
 "grn":{"source":"Abasy Atlas 511145_v2005_sRDB04 (RegulonDB-derived, curated)","sha16":"c1f625e5",
        "n_nodes":G.number_of_nodes(),"n_edges":G.number_of_edges()},
 "pool":{"n_nonmetabolic":N,"n_essential":K,"base_rate":round(base,4),"mapped_to_grn":mapped},
 "a_enrichment":{"contingency_regulator":{"both":a,"reg_noness":b_,"nonreg_ess":c,"neither":d},
                 "odds_ratio":round(orr,3),"fisher_p":p,"pass":bool(G1_enrich)},
 "b_delta_auroc":{"auroc_conservation":round(au_own,4),"auroc_conservation_plus_regulatory":round(au_own_reg,4),
                  "delta_auroc":round(delta,4),"gate":0.03,"pass":bool(G1_delta)},
 "c_studybias_control":{"auroc_own_pmid":round(au_own_pmid,4),"auroc_own_pmid_regulatory":round(au_own_pmid_reg,4),
    "delta_beyond_pmid":round(delta_beyond_pmid,4),"outdeg_vs_pmid_pearson":round(r_out_pmid,3),
    "survives":bool(G1_survives)},
 "overall_PASS":bool(PASS),
 "scope":("E. coli only, NON-METABOLIC subproteome, enrichment-only, in-silico; Abasy 2005 curated GRN (smaller than "
          "current RegulonDB -- coverage limit, curation preserved); a POSITIVE could be residual study bias, hence the "
          "mandatory publication-count control (c)."),
}
payload=json.dumps({k:v for k,v in metrics.items() if k!="scope"},sort_keys=True,separators=(",",":"))
sha=hashlib.sha256(payload.encode()).hexdigest()
if PASS:
    verdict=(f"PASS — curated regulatory master-regulator influence is the FIRST validated non-metabolic mechanistic "
             f"signal: regulators enriched for essentiality (OR {orr:.2f}, p {p:.1e}), adds ΔAUROC {delta:+.3f} beyond "
             f"conservation AND survives the study-bias control (ΔAUROC-beyond-pubcount {delta_beyond_pmid:+.3f}).")
else:
    reasons=[]
    if not G1_enrich: reasons.append(f"enrichment OR {orr:.2f} p {p:.1e}")
    if not G1_delta: reasons.append(f"ΔAUROC beyond conservation only {delta:+.3f} (<0.03)")
    if not G1_survives: reasons.append(f"does not survive study-bias control (ΔAUROC-beyond-pubcount {delta_beyond_pmid:+.3f})")
    verdict=("FAIL (first-class NEGATIVE) — curated regulatory-network master-regulator influence does NOT crack the "
             f"non-metabolic half: {'; '.join(reasons)}. THIRD principled closure of the door (after MET4 PPI/study-bias "
             f"and NONMET1 synteny/conservation-collinear); conservation breadth (AUROC {au_own:.3f}) remains the unbeaten "
             f"baseline. Honest bound: no homology-independent mechanistic signal for the non-metabolic essential half has "
             f"survived three independent principled attempts.")
metrics["verdict"]=verdict
json.dump(metrics,open(os.path.join(RES,"REGNET1_metrics.json"),"w"),indent=2,sort_keys=True)
open(os.path.join(RES,"payload.sha256"),"w").write(sha+"\n")
print("REGNET1:",("PASS" if PASS else "NEGATIVE"))
print(f"  GRN nodes={G.number_of_nodes()} edges={G.number_of_edges()} | pool N={N} ess={K} base={base:.3f} mapped_to_grn={mapped}")
print(f"  (a) regulator enrichment OR={orr:.2f} p={p:.2e}")
print(f"  (b) AUROC conservation={au_own:.4f} +regulatory={au_own_reg:.4f} ΔAUROC={delta:+.4f} (gate +0.03)")
print(f"  (c) study-bias control: ΔAUROC-beyond-pubcount={delta_beyond_pmid:+.4f} | out-deg~pmid r={r_out_pmid:.3f}")
print("  VERDICT:",verdict)
print("  payload_sha256=",sha)
