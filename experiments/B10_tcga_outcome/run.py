"""B10 — TCGA human clinical drug-response validation. Implements prereg/B10_tcga_human_outcome.md.
Real human patients, public data, no gate. Engine (PRISM-trained) transfer prediction vs TCGA clinical response
(responder CR/PR vs non-responder SD/PD), with cancer-type + proliferation adjustment. Most-confounded test —
honest by design. Reproduce x2. Aggregate outputs only (no patient-level data committed).
"""
import os, sys, json, time, gzip
import numpy as np, pandas as pd
from scipy import stats
from sklearn.metrics import roc_auc_score
import statsmodels.api as sm
import sklearn, warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.engine import InterceptaEngine
from intercepta.metrics import bh_fdr
from intercepta.axes import compute_r_prolif

SEED, K, MIN_N, MIN_CLASS = 42, 2000, 20, 8
TCGA = os.environ.get("INTERCEPTA_TCGA", "/private/tmp/claude-501/-Users-kalki-kaalcura/285c6fb0-5803-4a7d-ba7b-c59f3e2d16c5/scratchpad/tcga_dr")
HERE = os.path.dirname(os.path.abspath(__file__))
RESP = {"Complete Response": 1, "Partial Response": 1, "Stable Disease": 0, "Clinical Progressive Disease": 0}
print("B10 TCGA human outcome | sklearn", sklearn.__version__, flush=True)

# response table
d = pd.read_csv(os.path.join(TCGA, "response/drug_response.txt"), sep="\t", encoding="latin-1")
d["resp01"] = d["response"].map(RESP); d = d.dropna(subset=["resp01"])
d["drug"] = d["drug.name"].astype(str).str.lower().str.strip()

# entrez->symbol from DepMap raw header
hdr = pd.read_csv(D._p("depmap_expression.csv"), nrows=0).columns
e2s = {}
for c in hdr:
    if " (" in c and c.endswith(")"):
        sym, ent = c.split(" (")[0], c.split(" (")[1][:-1]
        if ent.isdigit(): e2s[ent] = sym

# TCGA expression: header -> matched -01 tumor samples for response patients
h = gzip.open(os.path.join(TCGA, "pancan_geneExp.gz"), "rt").readline().rstrip("\n").split("\t")
pat2samp = {s[:12]: s for s in h[1:] if s.endswith("-01")}
pats = [p for p in d["patient.arr"].unique() if p in pat2samp]
samps = [pat2samp[p] for p in pats]
ex = pd.read_csv(os.path.join(TCGA, "pancan_geneExp.gz"), sep="\t", usecols=[h[0]] + samps)
ex = ex.rename(columns={h[0]: "gid"}); ex["gid"] = ex["gid"].astype(str)
ex["sym"] = ex["gid"].map(e2s); ex = ex.dropna(subset=["sym"]).drop_duplicates("sym").set_index("sym").drop(columns=["gid"])
ex.columns = [c[:12] for c in ex.columns]                 # sample -> patient barcode
print(f"TCGA expr: {ex.shape[0]} symbol-genes x {ex.shape[1]} patients", flush=True)

# usable drugs: in response (>=20, >=MIN_CLASS each) AND engine can train (PRISM)
cand = [dk for dk, sub in d[d["patient.arr"].isin(pats)].groupby("drug")
        if len(sub) >= MIN_N and sub["resp01"].sum() >= MIN_CLASS and (sub["resp01"] == 0).sum() >= MIN_CLASS]
eng = InterceptaEngine().fit(drugs=cand, compute_calibration=False, label_source="prism")
drugs = [dk for dk in cand if dk in eng.fitted_drugs_]
print("usable drugs (response + PRISM-trainable):", drugs, flush=True)

pred = eng.predict_transfer(ex)                            # patients x drugs (z; higher=resistant)
Rp = compute_r_prolif(ex)

def logit_coef(y, tr, canc, rp):
    X = pd.DataFrame({"tr": stats.zscore(tr), "rp": stats.zscore(rp)})
    du = pd.get_dummies(canc, drop_first=True, dtype=float)
    if du.shape[1] and du.shape[1] < len(y) - 3: X = pd.concat([X, du.reset_index(drop=True)], axis=1)
    X = sm.add_constant(X, has_constant="add")
    try:
        m = sm.Logit(np.asarray(y, float), X.values.astype(float)).fit(disp=0, maxiter=200)
        return float(m.params[1]), float(m.pvalues[1]), float(m.bse[1])   # tr coef
    except Exception:
        return np.nan, np.nan, np.nan

rows = []; dd = d[d["patient.arr"].isin(pats)]
diag_auc, off_auc = [], []
for dk in drugs:
    sub = dd[dd["drug"] == dk].drop_duplicates("patient.arr")
    P = [p for p in sub["patient.arr"] if p in pred.index]
    sub = sub[sub["patient.arr"].isin(P)].set_index("patient.arr").loc[P]
    y = sub["resp01"].values.astype(int); nonresp = 1 - y
    tr = pred.loc[P, dk].values
    if y.sum() < MIN_CLASS or (len(y) - y.sum()) < MIN_CLASS: continue
    auc = roc_auc_score(nonresp, tr)                       # resistant score predicts non-response
    b, p, se = logit_coef(y, tr, sub["cancers"].values, Rp[P].values)
    diag_auc.append(auc)
    off_auc.append(np.mean([roc_auc_score(nonresp, pred.loc[P, dj].values) for dj in drugs if dj != dk]))
    rows.append({"drug": dk, "n": len(P), "n_resp": int(y.sum()), "auroc_nonresp": round(float(auc), 4),
                 "adj_logit_coef": (round(b, 4) if np.isfinite(b) else None), "adj_p": (float(p) if np.isfinite(p) else None),
                 "adj_se": (round(se, 4) if np.isfinite(se) else None)})

df = pd.DataFrame(rows); diag_auc = np.array(diag_auc); off_auc = np.array(off_auc); n = len(df)
rng = np.random.default_rng(SEED)
# H1: mean AUROC>0.5, permutation (per drug, shuffle labels)
null1 = np.empty(K)
Pd = {r["drug"]: [p for p in dd[dd["drug"]==r["drug"]].drop_duplicates("patient.arr")["patient.arr"] if p in pred.index] for _,r in df.iterrows()}
yd = {dk: (1 - dd[dd["drug"]==dk].drop_duplicates("patient.arr").set_index("patient.arr").loc[Pd[dk],"resp01"].values.astype(int)) for dk in df["drug"]}
for i in range(K):
    null1[i] = np.mean([roc_auc_score(rng.permutation(yd[dk]), pred.loc[Pd[dk], dk].values) for dk in df["drug"]])
p_h1 = (np.sum(null1 >= diag_auc.mean()) + 1) / (K + 1)
H1 = bool(diag_auc.mean() > 0.5 and p_h1 < 0.05)
# H2: DL meta of adjusted logit coef (expect <0)
m = df.dropna(subset=["adj_logit_coef", "adj_se"])
if len(m) >= 3:
    b = m["adj_logit_coef"].values; se = m["adj_se"].values; w = 1/se**2
    mu_f = np.sum(w*b)/np.sum(w); Q = np.sum(w*(b-mu_f)**2); k = len(b)
    tau2 = max(0, (Q-(k-1))/(np.sum(w)-np.sum(w**2)/np.sum(w))) if k>1 else 0
    wr = 1/(se**2+tau2); mu = float(np.sum(wr*b)/np.sum(wr)); se_mu = float(np.sqrt(1/np.sum(wr))); p_h2 = float(2*stats.norm.sf(abs(mu/se_mu)))
    H2 = bool(mu < 0 and p_h2 < 0.05)
else:
    mu, se_mu, p_h2, H2 = np.nan, np.nan, np.nan, False
# H3 specificity
obs3 = diag_auc.mean() - off_auc.mean(); do = np.column_stack([diag_auc, off_auc]); null3 = np.empty(K)
for i in range(K):
    f = rng.integers(0,2,n).astype(bool); null3[i] = np.where(f,do[:,1],do[:,0]).mean()-np.where(f,do[:,0],do[:,1]).mean()
p_h3 = (np.sum(null3 >= obs3)+1)/(K+1); H3 = bool(obs3>0 and p_h3<0.05)

df["adj_BHq"] = bh_fdr(df["adj_p"].values)
print(f"\nusable drugs: {n}")
for _,r in df.sort_values("auroc_nonresp",ascending=False).iterrows():
    print(f"  {r['drug']:<16} n={r['n']:>3} resp={r['n_resp']:>3} AUROC(nonresp)={r['auroc_nonresp']:.3f} adj_coef={r['adj_logit_coef']} adj_p={r['adj_p'] and round(r['adj_p'],3)} BHq={round(r['adj_BHq'],3) if pd.notna(r['adj_BHq']) else None}")
print(f"\nH1 transfer→response: mean AUROC(nonresp)={diag_auc.mean():.4f} perm p={p_h1:.4g} -> {H1}")
print(f"H2 cancer+prolif-ADJUSTED meta coef={mu if np.isfinite(mu) else float('nan'):+.4f} (SE {se_mu if np.isfinite(se_mu) else float('nan'):.4f}) p={p_h2 if np.isfinite(p_h2) else float('nan'):.4g} -> {H2}")
print(f"H3 drug-specific: diag AUROC {diag_auc.mean():.3f} vs off {off_auc.mean():.3f} diff={obs3:+.4f} perm p={p_h3:.4g} -> {H3}")
if H2:
    verdict = "TCGA HUMAN SIGNAL (adjusted): transfer predicts real patient response beyond cancer-type+proliferation"
elif H1:
    verdict = "CONFOUNDED: raw transfer→response signal (AUROC>0.5) but it does NOT survive cancer-type+proliferation adjustment (H2 null) — not drug-level human validation"
else:
    verdict = "NULL: transfer does not predict TCGA human clinical response"
print("VERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0], "sklearn": sklearn.__version__,
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": SEED, "K": K,
       "cohort": "TCGA (public: lifeome response + Xena pancan expr); engine PRISM-trained", "n_drugs": n, "drugs": rows,
       "H1_mean_auroc_nonresp": round(float(diag_auc.mean()),4), "H1_perm_p": float(p_h1), "H1_pass": H1,
       "H2_adj_meta_coef": (round(mu,4) if np.isfinite(mu) else None), "H2_p": (float(p_h2) if np.isfinite(p_h2) else None), "H2_pass": H2,
       "H3_diag_minus_off_auroc": round(float(obs3),4), "H3_perm_p": float(p_h3), "H3_pass": H3, "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B10_metrics.json"), "w"), indent=2)
print("wrote results/B10_metrics.json")
