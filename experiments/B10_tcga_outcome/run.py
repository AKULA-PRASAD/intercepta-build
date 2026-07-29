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

# TCGA expression: header -> matched -01 tumor samples for response patients
# (Xena pancan geneExp is gene-SYMBOL-keyed: 20502 symbols + 29 numeric IDs -> use symbols directly)
h = gzip.open(os.path.join(TCGA, "pancan_geneExp.gz"), "rt").readline().rstrip("\n").split("\t")
pat2samp = {s[:12]: s for s in h[1:] if s.endswith("-01")}
pats = [p for p in d["patient.arr"].unique() if p in pat2samp]
samps = [pat2samp[p] for p in pats]
ex = pd.read_csv(os.path.join(TCGA, "pancan_geneExp.gz"), sep="\t", usecols=[h[0]] + samps)
ex = ex.rename(columns={h[0]: "sym"}); ex["sym"] = ex["sym"].astype(str)
ex = ex[~ex["sym"].str.fullmatch(r"\d+")].drop_duplicates("sym").set_index("sym")   # keep symbol rows
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

dd = d[d["patient.arr"].isin(pats)]

# per-drug raw diagonal/off-diagonal AUROC (H1 transfer, H3 specificity) + within-(drug,cancer) strata (H2)
diag_auc, off_auc, rp_auc = [], [], []
Pd, Yd = {}, {}
strata = []   # (drug, cancer, patients, nonresp) for cancer-confound-free test
for dk in drugs:
    sub = dd[dd["drug"] == dk].drop_duplicates("patient.arr")
    sub = sub[sub["patient.arr"].isin(pred.index)].set_index("patient.arr")
    P = list(sub.index); y = sub["resp01"].values.astype(int); nr = 1 - y
    if y.sum() < MIN_CLASS or (len(y) - y.sum()) < MIN_CLASS:
        continue
    tr = pred.loc[P, dk].values
    diag_auc.append(roc_auc_score(nr, tr)); Pd[dk] = P; Yd[dk] = nr
    off_auc.append(np.mean([roc_auc_score(nr, pred.loc[P, dj].values) for dj in drugs if dj != dk]))
    rp_auc.append(roc_auc_score(nr, Rp[P].values))          # proliferation-only comparator
    canc = sub["cancers"].values
    for c in set(canc):
        ix = [i for i in range(len(P)) if canc[i] == c]
        if len(ix) >= 12 and nr[ix].sum() >= 4 and (len(ix) - nr[ix].sum()) >= 4:
            strata.append((dk, c, [P[i] for i in ix], nr[ix]))
diag_auc, off_auc, rp_auc = map(np.array, (diag_auc, off_auc, rp_auc)); n = len(diag_auc)
rng = np.random.default_rng(SEED)

# H1: raw pooled diagonal AUROC (cancer-CONFOUNDED)
null1 = np.array([np.mean([roc_auc_score(rng.permutation(Yd[dk]), pred.loc[Pd[dk], dk].values) for dk in Pd]) for _ in range(K)])
p_h1 = (np.sum(null1 >= diag_auc.mean()) + 1) / (K + 1); H1 = bool(diag_auc.mean() > 0.5 and p_h1 < 0.05)

# H2: WITHIN-CANCER stratified AUROC (cancer-confound CONTROLLED) — the decisive test
sa = np.array([roc_auc_score(nr, pred.loc[P, dk].values) for dk, c, P, nr in strata])
sw = np.array([len(P) for dk, c, P, nr in strata])
h2_mean = float(np.sum(sa * sw) / np.sum(sw)) if len(sa) else float("nan")
null2 = np.empty(K)
for i in range(K):
    v = [roc_auc_score(rng.permutation(nr), pred.loc[P, dk].values) for dk, c, P, nr in strata]
    null2[i] = np.sum(np.array(v) * sw) / np.sum(sw)
p_h2 = (np.sum(null2 >= h2_mean) + 1) / (K + 1) if len(sa) else np.nan
H2 = bool(len(sa) >= 5 and h2_mean > 0.5 and p_h2 < 0.05)

# H3: drug-specificity (raw)
obs3 = diag_auc.mean() - off_auc.mean(); do = np.column_stack([diag_auc, off_auc]); null3 = np.empty(K)
for i in range(K):
    f = rng.integers(0, 2, n).astype(bool); null3[i] = np.where(f, do[:,1], do[:,0]).mean() - np.where(f, do[:,0], do[:,1]).mean()
p_h3 = (np.sum(null3 >= obs3) + 1) / (K + 1); H3 = bool(obs3 > 0 and p_h3 < 0.05)

rows = [{"drug": dk, "n": len(Pd[dk]), "diag_auroc_nonresp": round(float(a), 4)} for dk, a in zip(Pd, diag_auc)]
print(f"\nusable drugs: {n} | within-cancer strata: {len(strata)}")
for r in sorted(rows, key=lambda x: -x["diag_auroc_nonresp"]):
    print(f"  {r['drug']:<16} n={r['n']:>3} raw AUROC(nonresp)={r['diag_auroc_nonresp']:.3f}")
print(f"\nH1 RAW pooled AUROC={diag_auc.mean():.4f} perm p={p_h1:.4g} -> {H1}  (cancer-CONFOUNDED)")
print(f"    proliferation-only AUROC={rp_auc.mean():.4f}  (comparator)")
print(f"H2 WITHIN-CANCER stratified AUROC={h2_mean:.4f} ({len(strata)} strata) perm p={p_h2 if np.isfinite(p_h2) else float('nan'):.4g} -> {H2}  (cancer-CONTROLLED, DECISIVE)")
print(f"H3 drug-specific: diag {diag_auc.mean():.3f} vs off {off_auc.mean():.3f} diff={obs3:+.4f} perm p={p_h3:.4g} -> {H3}")
if H2:
    verdict = f"TCGA HUMAN SIGNAL survives cancer-type control: within-cancer AUROC={h2_mean:.3f} (p={p_h2:.3f}). Real (weak) human drug-response signal."
elif H1:
    verdict = f"CONFOUNDED: raw AUROC={diag_auc.mean():.3f} (p={p_h1:.3f}) but within-cancer control AUROC={h2_mean:.3f} (p={p_h2:.3g}) does NOT hold -> the raw signal is CANCER-TYPE confounding, not drug-level human prediction."
else:
    verdict = "NULL: no transfer->human-response signal even raw."
print("VERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0], "sklearn": sklearn.__version__,
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": SEED, "K": K,
       "cohort": "TCGA (public: lifeome response + Xena pancan expr, symbol-keyed); engine PRISM-trained",
       "n_drugs": n, "n_within_cancer_strata": len(strata), "drugs": rows,
       "H1_raw_pooled_auroc": round(float(diag_auc.mean()), 4), "H1_perm_p": float(p_h1), "H1_pass_confounded": H1,
       "proliferation_only_auroc": round(float(rp_auc.mean()), 4),
       "H2_within_cancer_auroc": round(h2_mean, 4) if np.isfinite(h2_mean) else None, "H2_perm_p": (float(p_h2) if np.isfinite(p_h2) else None), "H2_pass_cancer_controlled": H2,
       "H3_diag_minus_off": round(float(obs3), 4), "H3_perm_p": float(p_h3), "H3_pass": H3, "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B10_metrics.json"), "w"), indent=2)
print("wrote results/B10_metrics.json")
