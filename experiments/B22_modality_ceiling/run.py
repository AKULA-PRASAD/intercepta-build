"""B22 — is the drug-response ceiling RNA-specific or modality-general? Fair head-to-head of transcriptomics vs
proteomics (CCLE, Nusinow 2020) predicting GDSC2 response on the SAME 291 matched cell lines, identical CV.
Implements prereg/B22_modality_ceiling.md. Reproduce x2. Aggregate outputs only.
"""
import os, sys, json, time, re, hashlib
import numpy as np, pandas as pd
from scipy import stats
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
import sklearn, warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.metrics import bh_fdr

SEED, KFOLDS, MIN_LINES, TOPN, MIN_PROT_FRAC, ALPHAS = 42, 5, 120, 2000, 0.7, (10.0, 100.0, 1000.0)
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
PROT = os.path.join(DATA, "ccle_proteomics.csv.gz")
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()[:16]

# ---- load + match (proteomics ∩ RNA ∩ GDSC), keyed to DepMap_ID ----
rna = D.load_depmap_expression()                       # ACH rows x genes
gdsc = D.load_gdsc_response()                          # COSMIC_ID, DRUG_NAME, LN_IC50
m = pd.read_csv(os.path.join(DATA, "depmap_meta.csv"))
name2id = {str(k): str(v) for k, v in zip(m["CCLE_Name"], m["DepMap_ID"]) if pd.notna(k) and pd.notna(v)}
cm = m.dropna(subset=["COSMICID", "DepMap_ID"]); cosmic2id = {int(k): str(v) for k, v in zip(cm["COSMICID"], cm["DepMap_ID"])}
pr = pd.read_csv(PROT); cols = pr.columns.tolist(); mc = cols[:6]
cell = [c for c in cols if not c.endswith("_Peptides") and c not in mc]
P = pr[["Gene_Symbol"] + cell].copy(); P.columns = ["gene"] + [name2id.get(re.sub(r"_TenPx\d+$", "", c), "") for c in cell]
P = P.dropna(subset=["gene"]).groupby("gene").mean(numeric_only=True)
P = P.loc[:, [c for c in P.columns if c.startswith("ACH-")]]; P = P.T.groupby(level=0).mean().T   # gene x ACH, unique
gdsc = gdsc.copy(); gdsc["ach"] = pd.to_numeric(gdsc["COSMIC_ID"], errors="coerce").map(cosmic2id)

matched = sorted(set(P.columns) & set(rna.index) & set(gdsc["ach"].dropna()))
# protein features present in >=70% of matched lines; RNA all genes
Pm = P[matched]; prot_keep = Pm.index[(Pm.notna().mean(axis=1) >= MIN_PROT_FRAC)]
Xp_full = Pm.loc[prot_keep].T                                  # lines x proteins
Xr_full = rna.loc[matched]                                     # lines x genes
# top-2000-variance (label-free) per modality
p_top = Xp_full.var().sort_values(ascending=False).head(TOPN).index
r_top = Xr_full.var().sort_values(ascending=False).head(TOPN).index
Xp = Xp_full[p_top].astype(float); Xr = Xr_full[r_top].astype(float)
lines = np.array(matched)
print(f"B22 modality ceiling | matched lines={len(lines)}  proteins(top)={len(p_top)}  genes(top)={len(r_top)}", flush=True)

g = gdsc[gdsc["ach"].isin(set(matched))]
drug_counts = g.groupby("DRUG_NAME")["ach"].nunique()
drugs = sorted(drug_counts[drug_counts >= MIN_LINES].index)
print(f"drugs with >= {MIN_LINES} matched lines: {len(drugs)}", flush=True)

def cv_rho(X, y_ser, idx):
    """out-of-fold Spearman for RidgeCV on feature matrix X (DataFrame lines x feats) restricted to idx (ACH)."""
    sub = [a for a in idx if a in y_ser.index]
    if len(sub) < MIN_LINES: return np.nan, len(sub)
    Xs = X.loc[sub].values; y = y_ser.loc[sub].values.astype(float)
    oof = np.full(len(sub), np.nan); kf = KFold(KFOLDS, shuffle=True, random_state=SEED)
    for tr, te in kf.split(Xs):
        sc = StandardScaler().fit(Xs[tr]); Xtr = np.nan_to_num(sc.transform(Xs[tr])); Xte = np.nan_to_num(sc.transform(Xs[te]))
        mdl = RidgeCV(alphas=ALPHAS).fit(Xtr, y[tr]); oof[te] = mdl.predict(Xte)
    return float(stats.spearmanr(oof, y)[0]), len(sub)

Xrp = pd.concat([Xr.add_prefix("r_"), Xp.add_prefix("p_")], axis=1)
rows = []
for d in drugs:
    gd = g[g["DRUG_NAME"] == d].dropna(subset=["ach", "LN_IC50"]).groupby("ach")["LN_IC50"].mean()
    idx = [a for a in lines if a in gd.index]
    rR, n = cv_rho(Xr, gd, idx); rP, _ = cv_rho(Xp, gd, idx); rRP, _ = cv_rho(Xrp, gd, idx)
    if np.isfinite(rR) and np.isfinite(rP) and np.isfinite(rRP):
        rows.append({"drug": d, "n": n, "rho_RNA": round(rR, 4), "rho_protein": round(rP, 4), "rho_both": round(rRP, 4)})
df = pd.DataFrame(rows)
rR, rP, rRP = df["rho_RNA"].values, df["rho_protein"].values, df["rho_both"].values

def paired(a, b):
    w = stats.wilcoxon(a, b); return {"mean_delta": round(float(np.mean(a - b)), 4), "median_delta": round(float(np.median(a - b)), 4),
                                      "wilcoxon_p": float(w.pvalue), "frac_a_gt_b": round(float(np.mean(a > b)), 3)}
P_vs_R = paired(rP, rR); RP_vs_R = paired(rRP, rR)
H1 = bool(abs(np.mean(rP) - np.mean(rR)) <= 0.02)                       # comparable modality
H2 = bool(np.mean(rP) > np.mean(rR) and np.mean(rRP) > np.mean(rR)
          and P_vs_R["wilcoxon_p"] < 0.05 and RP_vs_R["wilcoxon_p"] < 0.05
          and P_vs_R["mean_delta"] >= 0.02 and RP_vs_R["mean_delta"] >= 0.02)

print(f"\nn drugs evaluated: {len(df)}")
print(f"  mean per-drug rho:  RNA={np.mean(rR):+.4f}  protein={np.mean(rP):+.4f}  both={np.mean(rRP):+.4f}")
print(f"  median per-drug rho: RNA={np.median(rR):+.4f}  protein={np.median(rP):+.4f}  both={np.median(rRP):+.4f}")
print(f"  protein vs RNA: {P_vs_R}")
print(f"  both vs RNA:    {RP_vs_R}")
print(f"H1 comparable modality: {H1} | H2 proteomics beats RNA (ceiling RNA-specific): {H2}")
if H2:
    verdict = ("CEILING IS RNA-SPECIFIC: proteomics carries drug-specific signal RNA lacks (protein and protein+RNA "
               "beat RNA alone) -> a genuine new direction; shift the baseline-omics layer to proteomics and pursue "
               "matched patient proteomics.")
else:
    verdict = (f"CEILING IS MODALITY-GENERAL: baseline proteomics does NOT beat baseline RNA for drug-specific "
               f"response (protein {np.mean(rP):+.3f} vs RNA {np.mean(rR):+.3f}; both {np.mean(rRP):+.3f}). No baseline "
               f"molecular profile resolves within-lineage drug specificity here -> functional/perturbation data "
               f"(Track-1), not another baseline omic, is required. First-class negative.")
print("\nVERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0], "sklearn": sklearn.__version__,
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": SEED,
       "data": {"ccle_proteomics_sha256": sha256(PROT), "n_matched_lines": len(lines),
                "n_proteins_top": int(len(p_top)), "n_genes_top": int(len(r_top))},
       "n_drugs": len(df),
       "mean_rho": {"RNA": round(float(np.mean(rR)), 4), "protein": round(float(np.mean(rP)), 4), "both": round(float(np.mean(rRP)), 4)},
       "median_rho": {"RNA": round(float(np.median(rR)), 4), "protein": round(float(np.median(rP)), 4), "both": round(float(np.median(rRP)), 4)},
       "protein_vs_RNA": P_vs_R, "both_vs_RNA": RP_vs_R, "H1_comparable": H1, "H2_proteomics_beats_RNA": H2,
       "per_drug": rows, "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B22_metrics.json"), "w"), indent=2)
print("wrote results/B22_metrics.json")
