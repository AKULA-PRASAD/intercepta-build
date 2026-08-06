"""DEPEND1 — Functional-dependency (DepMap CRISPR/Chronos) target-ID for host-embedded (cancer) biology.

The host-embedded analog of the bacterial FBA-essentiality module. Implements prereg/PREREG.md.
- SELECTIVE vs PAN-ESSENTIAL separation (mandatory confound guard).
- G1: SELECTIVE-dependency recovers known actionable targets vs null.
- G2: out-of-sample generalization (split BY CELL LINE, stratified by lineage; TEST lines only).
- G3: label-free expr->dependency (Ridge CV split by cell line) vs own-expression baseline.
Public DepMap. CPU-only. Reproduce x2 byte-identical. Aggregate outputs only. NEVER commit data/push.
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
from scipy import stats
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold
import sklearn, warnings; warnings.filterwarnings("ignore")

SEED, K, TOPN = 42, 2000, 2000
DEP_THRESH = -0.5           # Chronos: effect < -0.5 => dependent
PAN_FRAC   = 0.90           # dependent in >90% lines => pan-essential
SEL_LO, SEL_HI = 0.01, 0.50 # selective dependency band
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("DEPEND1_DATA", "/Users/kalki/kaalcura/data")

# frozen input sha256 (PREREG §1)
SHAS = {
 "depmap_crispr_gene_effect.csv":"d1633bfa0bf4719e72e564f15d9bcda7fddbbd3dac2a8a3aebf4898ac9f56f00",
 "depmap_meta.csv":"382c0c26cf57a2fb82449f797c58cb0dfc2313949908d8f83560ebcf3e5bcbaa",
 "depmap_mut_try1.csv":"e99e43789c1c4821ccb737a45cd6f4fbbeac709c5a8cca326846d6d9a16cf5c8",
 "depmap_expression.csv":"6b8d5f3c00ce73a5e025922d52b74929e19359e323786a0314410762b0c08a16"}

def sha256(path):
    h = hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""): h.update(chunk)
    return h.hexdigest()

def verify(name):
    p = os.path.join(DATA, name); got = sha256(p)
    if got != SHAS[name]:
        raise RuntimeError(f"sha256 mismatch {name}: expected {SHAS[name]} got {got}")
    return p

NONSIL = {"Missense_Mutation","Nonsense_Mutation","Frame_Shift_Del","Frame_Shift_Ins",
          "Splice_Site","In_Frame_Del","In_Frame_Ins","Nonstop_Mutation","Start_Codon_SNP"}

# ---- pre-registered known-actionable target <-> context pairs (PREREG §3) ----
# kind: 'mut_hotspot' = hotspot-mutant lines; 'tp53wt' = no non-silent TP53; 'lineage'
PAIRS = [
 ("BRAF","BRAF-hotspot","mut_hotspot","BRAF"),
 ("KRAS","KRAS-hotspot","mut_hotspot","KRAS"),
 ("NRAS","NRAS-hotspot","mut_hotspot","NRAS"),
 ("PIK3CA","PIK3CA-hotspot","mut_hotspot","PIK3CA"),
 ("CTNNB1","CTNNB1-hotspot","mut_hotspot","CTNNB1"),
 ("EGFR","EGFR-hotspot","mut_hotspot","EGFR"),
 ("MDM2","TP53-wildtype","tp53wt",None),
 ("SOX10","skin","lineage","skin"),
 ("PAX8","ovary","lineage","ovary"),
 ("FLT3","blood","lineage","blood"),
]
print("DEPEND1 | sklearn", sklearn.__version__, "| seed", SEED, flush=True)

# ---------------- load ----------------
ce = pd.read_csv(verify("depmap_crispr_gene_effect.csv"), index_col=0)
ce = ce.rename(columns={c: c.split(" (")[0] for c in ce.columns if " (" in c})
ce = ce.loc[:, ~ce.columns.duplicated()]
lines = list(ce.index)                                  # DepMap_ID (ACH-*)
genes = list(ce.columns)
E = ce.values.astype(float)                             # n_lines x n_genes
gidx = {g:i for i,g in enumerate(genes)}
print(f"CRISPR gene-effect: {E.shape[0]} lines x {E.shape[1]} genes", flush=True)

meta = pd.read_csv(verify("depmap_meta.csv"), low_memory=False)
lin = dict(zip(meta["DepMap_ID"], meta["lineage"].astype(str)))
lineage = np.array([lin.get(l, "nan") for l in lines])

maf = pd.read_csv(verify("depmap_mut_try1.csv"),
                  usecols=["Hugo_Symbol","DepMap_ID","isTCGAhotspot","isCOSMIChotspot","Variant_Classification"],
                  low_memory=False)
maf = maf[maf["DepMap_ID"].isin(set(lines))]
hot = maf[(maf["isTCGAhotspot"]==True)|(maf["isCOSMIChotspot"]==True)]
def hotspot_lines(g): return set(hot[hot["Hugo_Symbol"]==g]["DepMap_ID"])
tp53_mut = set(maf[(maf["Hugo_Symbol"]=="TP53") & (maf["Variant_Classification"].isin(NONSIL))]["DepMap_ID"])

def context_mask(kind, key, line_list):
    la = np.array(line_list)
    if kind=="mut_hotspot":
        s = hotspot_lines(key); return np.array([l in s for l in la])
    if kind=="tp53wt":
        return np.array([l not in tp53_mut for l in la])
    if kind=="lineage":
        return np.array([lin.get(l,"nan")==key for l in la])
    raise ValueError(kind)

# ---------------- pan-essential vs selective (mandatory guard) ----------------
dep = (E < DEP_THRESH)
dep_frac = dep.mean(0)                                   # per gene
n_pan  = int(np.sum(dep_frac > PAN_FRAC))
n_sel  = int(np.sum((dep_frac >= SEL_LO) & (dep_frac <= SEL_HI)))
n_inter= int(np.sum((dep_frac > SEL_HI) & (dep_frac <= PAN_FRAC)))
n_rare = int(np.sum(dep_frac < SEL_LO))
pan_set = set(np.array(genes)[dep_frac > PAN_FRAC])
print(f"\nPAN-ESSENTIAL (>{PAN_FRAC:.0%}): {n_pan} | SELECTIVE [{SEL_LO},{SEL_HI}]: {n_sel} | "
      f"intermediate: {n_inter} | rare(<{SEL_LO}): {n_rare}", flush=True)

# ---------------- context-selectivity helper ----------------
def selectivity(Emat, mask):
    """sel(g)=mean(effect|~mask)-mean(effect|mask); positive => more dependent in context."""
    inn = Emat[mask]; out = Emat[~mask]
    return np.nanmean(out,0) - np.nanmean(inn,0)

def target_rank(sel_all, ti):
    s_t = sel_all[ti]
    if not np.isfinite(s_t): return len(sel_all)
    return int(1 + np.sum(sel_all > s_t))

def perm_p_target(Emat, mask, ti, rng):
    """one-sided permutation p for the KNOWN target's selectivity under shuffled context labels."""
    e = Emat[:, ti]; ok = np.isfinite(e); e = e[ok]; n = e.size; m = int(mask[ok].sum())
    if m==0 or m==n: return 1.0
    obs = e[~mask[ok]].mean() - e[mask[ok]].mean()
    tot = e.sum()
    null = np.empty(K)
    for k in range(K):
        idx = rng.choice(n, m, replace=False)
        inmean = e[idx].mean()
        null[k] = (tot - e[idx].sum())/(n-m) - inmean
    return float((np.sum(null >= obs)+1)/(K+1))

n_genes = len(genes)
K1 = max(1, round(0.01*n_genes))

def run_recovery(Emat, line_list, tag):
    rng = np.random.default_rng(SEED)
    rows=[]; rec10=0; rec1pct=0; pvals=[]
    for tgt, cname, kind, key in PAIRS:
        mask = context_mask(kind, key, line_list)
        ti = gidx[tgt]
        n_ctx = int(mask.sum())
        if n_ctx < 5 or n_ctx > len(mask)-5:
            rows.append({"target":tgt,"context":cname,"n_ctx":n_ctx,"skipped":"context too small on this split"})
            continue
        sel = selectivity(Emat, mask)
        rk = target_rank(sel, ti)
        p  = perm_p_target(Emat, mask, ti, rng)
        in10 = rk<=10; in1 = rk<=K1
        rec10 += in10; rec1pct += in1; pvals.append(p)
        # lineage confound diagnostic for mutation contexts
        lin_frac=None
        if kind=="mut_hotspot":
            la = np.array(line_list)[mask]; ll=[lin.get(l,"nan") for l in la]
            if ll:
                vc = pd.Series(ll).value_counts(normalize=True); lin_frac=f"{vc.index[0]}={vc.iloc[0]:.2f}"
        rows.append({"target":tgt,"context":cname,"n_ctx":n_ctx,
                     "target_dep_frac":round(float(dep_frac[ti]),4),
                     "is_pan_essential":bool(dep_frac[ti]>PAN_FRAC),
                     "sel_score":round(float(sel[ti]),4),
                     "rank":rk,"in_top10":bool(in10),"in_top1pct":bool(in1),
                     "perm_p":round(p,5),"top_lineage_in_ctx":lin_frac})
    nt = len([r for r in rows if "rank" in r])
    r10 = rec10/nt if nt else 0.0; r1 = rec1pct/nt if nt else 0.0
    # pooled permutation p (Fisher combine of per-pair one-sided p)
    if pvals:
        chi = -2*np.sum(np.log(np.clip(pvals,1e-12,1))); pooled = float(stats.chi2.sf(chi, 2*len(pvals)))
    else: pooled=1.0
    print(f"\n[{tag}] recovery@top10={r10:.2f} ({rec10}/{nt})  recovery@top1%(<= {K1})={r1:.2f}  pooled_perm_p={pooled:.3g}")
    for r in rows:
        if "rank" in r:
            print(f"    {r['target']:7s} {r['context']:14s} n_ctx={r['n_ctx']:4d} rank={r['rank']:5d} "
                  f"dep_frac={r['target_dep_frac']:.3f} pan={r['is_pan_essential']} perm_p={r['perm_p']:.4f}")
        else:
            print(f"    {r['target']:7s} {r['context']:14s} SKIP ({r['skipped']})")
    return {"recovery_top10":round(r10,4),"recovery_top1pct":round(r1,4),
            "n_recovered_top10":int(rec10),"n_tested":nt,"pooled_perm_p":pooled,"k_top1pct":int(K1),
            "pairs":rows}

# ---------------- G1: recovery on ALL lines ----------------
print("\n================ G1: known-actionable recovery vs null (ALL lines) ================")
g1 = run_recovery(E, lines, "G1 ALL")
null_top10 = 10.0/n_genes

# ---------------- G2: held-out generalization (split BY CELL LINE, stratified by lineage) ----------------
print("\n================ G2: out-of-sample generalization (TEST lines only) ================")
rng = np.random.default_rng(SEED)
test_mask = np.zeros(len(lines), dtype=bool)
for lg in np.unique(lineage):
    idx = np.where(lineage==lg)[0]; rng.shuffle(idx)
    ntest = int(round(0.30*len(idx)))
    test_mask[idx[:ntest]] = True
train_idx = np.where(~test_mask)[0]; test_idx = np.where(test_mask)[0]
train_lines = [lines[i] for i in train_idx]; test_lines = [lines[i] for i in test_idx]
E_train = E[train_idx]; E_test = E[test_idx]
print(f"split: train={len(train_lines)} test={len(test_lines)} (disjoint cell lines, lineage-stratified)")
g2_train = run_recovery(E_train, train_lines, "G2 TRAIN")
g2_test  = run_recovery(E_test,  test_lines,  "G2 TEST")

# ---------------- G3: label-free expr->dependency (CV split by cell line) ----------------
print("\n================ G3: label-free expr->dependency (5-fold CV, split by cell line) ================")
dx = pd.read_csv(verify("depmap_expression.csv"), index_col=0)
dx = dx.rename(columns={c: c.split(" (")[0] for c in dx.columns if " (" in c})
dx = dx.loc[:, ~dx.columns.duplicated()]
common = [l for l in lines if l in dx.index]            # CRISPR ∩ expression lines
dxc = dx.loc[common]
# top-N most-variable feature genes; z-score per gene
var = dxc.var(0); feat = list(var.sort_values(ascending=False).index[:TOPN])
Xf = dxc[feat].copy()
Xz = (Xf - Xf.mean(0)) / Xf.std(0).replace(0, np.nan)
Xz = Xz.fillna(0.0).values
ce_common = ce.loc[common]
actionable = sorted(set(t for t,_,_,_ in PAIRS))
g3_rows=[]
for g in actionable:
    y = ce_common[g].values.astype(float)
    ok = np.isfinite(y)
    if ok.sum() < 100:
        g3_rows.append({"gene":g,"skipped":"n<100"}); continue
    Xg = Xz[ok]; yg = y[ok]
    kf = KFold(5, shuffle=True, random_state=SEED); pr = np.empty(len(yg))
    for tri, tei in kf.split(Xg):
        pr[tei] = RidgeCV(alphas=[10.,100.,1000.]).fit(Xg[tri], yg[tri]).predict(Xg[tei])
    rho_model = float(stats.spearmanr(pr, yg)[0])
    # own-expression baseline: target gene's OWN expression -> its dependency
    if g in dxc.columns:
        own = dxc.loc[np.array(common)[ok], g].values.astype(float)
        rho_own = float(stats.spearmanr(own, yg)[0])
    else:
        rho_own = float("nan")
    g3_rows.append({"gene":g,"n":int(ok.sum()),"cv_rho_model":round(rho_model,4),
                    "rho_own_expr_baseline":(round(rho_own,4) if np.isfinite(rho_own) else None),
                    "target_dep_frac":round(float(dep_frac[gidx[g]]),4)})
tested3=[r for r in g3_rows if "cv_rho_model" in r]
med_model = float(np.median([r["cv_rho_model"] for r in tested3]))
# paired: model beats own-expression baseline on PREDICTIVE STRENGTH = |rho| (own-expr rho is
# negative-but-informative: high expr -> more dependent; comparing |rho| is the fair test, matches B13).
paired=[r for r in tested3 if r["rho_own_expr_baseline"] is not None]
mdl=np.array([abs(r["cv_rho_model"]) for r in paired]); own=np.array([abs(r["rho_own_expr_baseline"]) for r in paired])
diff = mdl - own; obs3=float(np.median(diff)); rng3=np.random.default_rng(SEED); m=len(diff)
null3=np.array([(diff*(rng3.integers(0,2,m)*2-1)).mean() for _ in range(K)])  # mean sign-flip null (H0 sym about 0)
p_h3=float((np.sum(null3 >= diff.mean())+1)/(K+1))
med_own_abs=float(np.median(own)); med_model_abs=float(np.median(mdl))
print(f"median CV rho(model)={med_model:.3f}  median |rho|(model)={med_model_abs:.3f}  "
      f"median |rho|(own-expr baseline)={med_own_abs:.3f}  "
      f"median(|model|-|own|)={obs3:+.3f}  perm p(model>own)={p_h3:.3g}")
for r in sorted(tested3,key=lambda x:-x["cv_rho_model"]):
    print(f"    {r['gene']:7s} n={r['n']:4d} cv_rho_model={r['cv_rho_model']:+.3f} own_expr={r['rho_own_expr_baseline']} dep_frac={r['target_dep_frac']:.3f}")

# ---------------- gate verdicts ----------------
G1 = "PASS" if (g1["recovery_top10"]>=0.60 and g1["pooled_perm_p"]<0.01) else \
     ("PARTIAL" if g1["recovery_top1pct"]>=0.60 else "NEGATIVE")
G2 = "PASS" if (g2_test["recovery_top10"]>=0.50 and g2_test["pooled_perm_p"]<0.01) else \
     ("PARTIAL" if g2_test["recovery_top1pct"]>=0.50 else "NEGATIVE")
model_beats_own = bool(obs3>0 and p_h3<0.05)
G3 = "PASS" if (med_model>=0.20 and model_beats_own) else \
     ("PARTIAL" if med_model>=0.20 else "NEGATIVE")
verdict = (f"G1 selective-dependency recovery={G1} (top10={g1['recovery_top10']:.2f} vs null {null_top10:.4f}); "
           f"G2 held-out generalization={G2} (TEST top10={g2_test['recovery_top10']:.2f}); "
           f"G3 label-free expr->dependency={G3} (median CV rho={med_model:.2f}, beats own-expr={model_beats_own}). "
           f"Scope: cancer cell-line Chronos dependency; NOT patient/clinical, NOT wet-lab.")
print("\n================ VERDICT ================\n"+verdict)
print(f"G1={G1}  G2={G2}  G3={G3}")

# ---------------- payload (numeric only; EXCLUDES verdict/provenance) ----------------
payload = {
 "seed":SEED,"K":K,"dep_thresh":DEP_THRESH,"pan_frac":PAN_FRAC,"sel_band":[SEL_LO,SEL_HI],"topN":TOPN,
 "n_lines":int(E.shape[0]),"n_genes":int(E.shape[1]),
 "pan_essential_n":n_pan,"selective_n":n_sel,"intermediate_n":n_inter,"rare_n":n_rare,
 "null_recovery_top10":round(null_top10,6),
 "G1":g1,
 "G2_split":{"n_train":len(train_lines),"n_test":len(test_lines)},
 "G2_train":g2_train,"G2_test":g2_test,
 "G3":{"n_common_lines":len(common),"median_cv_rho_model":round(med_model,4),
       "median_abs_rho_model":round(med_model_abs,4),"median_abs_rho_own_expr":round(med_own_abs,4),
       "median_absmodel_minus_absown":round(obs3,4),
       "perm_p_model_gt_own":round(p_h3,5),"per_target":g3_rows},
 "gates":{"G1":G1,"G2":G2,"G3":G3},
}
payload_json = json.dumps(payload, sort_keys=True)
sha = hashlib.sha256(payload_json.encode()).hexdigest()

out = dict(payload)
out["verdict"]=verdict
out["input_sha256"]=SHAS
out["git_sha"]=os.popen("git rev-parse HEAD").read().strip()
out["python"]=sys.version.split()[0]; out["sklearn"]=sklearn.__version__
out["timestamp_utc"]=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
out["payload_sha256"]=sha

os.makedirs(os.path.join(HERE,"results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE,"results","DEPEND1_metrics.json"),"w"), indent=2, sort_keys=True)
open(os.path.join(HERE,"results","payload.sha256"),"w").write(sha+"\n")
print("\npayload_sha256:", sha)
print("wrote results/DEPEND1_metrics.json + results/payload.sha256")
