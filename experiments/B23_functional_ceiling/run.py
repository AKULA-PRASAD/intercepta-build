"""B23 — does MEASURED functional dependency (DepMap CRISPR) break the +0.212 baseline ceiling, beyond the
trivial target? Fair head-to-head vs RNA on the SAME 498 matched cell lines / 272 drugs, identical CV, plus a
pre-specified target-leakage control. Implements prereg/B23_functional_ceiling.md. Fully local. Reproduce x2.
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
from scipy import stats
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
import sklearn, warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D

SEED, KF, MIN_LINES, TOPN, ALPHAS = 42, 5, 120, 2000, (10.0, 100.0, 1000.0)
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
# curated single-target drugs (target gene in DepMap) for the leakage control — GDSC name (lower) -> target genes
DRUG_TARGETS = {
    "nutlin-3a (-)": ["MDM2"], "nutlin-3": ["MDM2"], "plx-4720": ["BRAF"], "dabrafenib": ["BRAF"],
    "trametinib": ["MAP2K1", "MAP2K2"], "selumetinib": ["MAP2K1", "MAP2K2"], "pd0325901": ["MAP2K1", "MAP2K2"],
    "refametinib": ["MAP2K1", "MAP2K2"], "erlotinib": ["EGFR"], "gefitinib": ["EGFR"], "afatinib": ["EGFR", "ERBB2"],
    "lapatinib": ["EGFR", "ERBB2"], "sapitinib": ["EGFR"], "nilotinib": ["ABL1"], "axitinib": ["KDR"],
    "crizotinib": ["ALK", "MET"], "mk-2206": ["AKT1", "AKT2"], "alpelisib": ["PIK3CA"], "pictilisib": ["PIK3CA"],
    "palbociclib": ["CDK4", "CDK6"], "olaparib": ["PARP1"], "talazoparib": ["PARP1"], "bortezomib": ["PSMB5"],
    "navitoclax": ["BCL2", "BCL2L1"], "venetoclax": ["BCL2"], "dasatinib": ["ABL1"], "rucaparib": ["PARP1"],
}

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()[:16]

# ---- load + match ----
rna = D.load_depmap_expression(); cr = D.load_depmap_crispr(); gdsc = D.load_gdsc_response()
m = pd.read_csv(os.path.join(DATA, "depmap_meta.csv")).dropna(subset=["COSMICID", "DepMap_ID"])
cosmic2id = {int(k): str(v) for k, v in zip(m["COSMICID"], m["DepMap_ID"])}
gdsc = gdsc.copy(); gdsc["ach"] = pd.to_numeric(gdsc["COSMIC_ID"], errors="coerce").map(cosmic2id)
matched = sorted(set(rna.index) & set(cr.index) & set(gdsc["ach"].dropna()))
Xr_full = rna.loc[matched].astype(float); Xd_full = cr.loc[matched].astype(float)
r_top = Xr_full.var().sort_values(ascending=False).head(TOPN).index
d_top = Xd_full.var().sort_values(ascending=False).head(TOPN).index
Xr = Xr_full[r_top]; Xd = Xd_full[d_top]
Xrd = pd.concat([Xr.add_prefix("r_"), Xd.add_prefix("d_")], axis=1)
print(f"B23 functional ceiling | matched lines={len(matched)}  RNA/CRISPR top={TOPN}", flush=True)
g = gdsc[gdsc["ach"].isin(set(matched))]
drugs = sorted(g.groupby("DRUG_NAME")["ach"].nunique().pipe(lambda s: s[s >= MIN_LINES]).index)
print(f"drugs with >= {MIN_LINES} lines: {len(drugs)}", flush=True)

def cv_rho(X, y_ser):
    sub = [a for a in matched if a in y_ser.index]
    if len(sub) < MIN_LINES: return np.nan
    Xs = X.loc[sub].values; y = y_ser.loc[sub].values.astype(float)
    oof = np.full(len(sub), np.nan)
    for tr, te in KFold(KF, shuffle=True, random_state=SEED).split(Xs):
        sc = StandardScaler().fit(Xs[tr]); mdl = RidgeCV(alphas=ALPHAS).fit(np.nan_to_num(sc.transform(Xs[tr])), y[tr])
        oof[te] = mdl.predict(np.nan_to_num(sc.transform(Xs[te])))
    return float(stats.spearmanr(oof, y)[0])

rows = []
for d in drugs:
    y = g[g["DRUG_NAME"] == d].dropna(subset=["ach", "LN_IC50"]).groupby("ach")["LN_IC50"].mean()
    rR, rD, rRD = cv_rho(Xr, y), cv_rho(Xd, y), cv_rho(Xrd, y)
    if all(np.isfinite(v) for v in (rR, rD, rRD)):
        rows.append({"drug": d, "rho_RNA": round(rR, 4), "rho_dep": round(rD, 4), "rho_both": round(rRD, 4)})
df = pd.DataFrame(rows); rR, rD, rRD = df["rho_RNA"].values, df["rho_dep"].values, df["rho_both"].values

def paired(a, b):
    w = stats.wilcoxon(a, b)
    return {"mean_delta": round(float(np.mean(a - b)), 4), "median_delta": round(float(np.median(a - b)), 4),
            "wilcoxon_p": float(w.pvalue), "frac_a_gt_b": round(float(np.mean(a > b)), 3)}
D_vs_R, RD_vs_R = paired(rD, rR), paired(rRD, rR)
H1 = bool(np.mean(rD) >= np.mean(rR))
H2 = bool(np.mean(rRD) > np.mean(rR) and RD_vs_R["wilcoxon_p"] < 0.05 and RD_vs_R["mean_delta"] >= 0.02)

# ---- target-leakage control: rebuild dependency features EXCLUDING each drug's target ----
lc = []
gl = {d.lower(): d for d in drugs}
for dl, tgts in DRUG_TARGETS.items():
    if dl not in gl: continue
    dname = gl[dl]
    y = g[g["DRUG_NAME"] == dname].dropna(subset=["ach", "LN_IC50"]).groupby("ach")["LN_IC50"].mean()
    keep = [c for c in Xd_full.columns if c not in set(tgts)]
    dtop_ex = Xd_full[keep].var().sort_values(ascending=False).head(TOPN).index
    rD_ex = cv_rho(Xd_full[dtop_ex], y); rR = cv_rho(Xr, y)
    if np.isfinite(rD_ex) and np.isfinite(rR):
        lc.append({"drug": dname, "targets": tgts, "rho_dep_noTarget": round(rD_ex, 4), "rho_RNA": round(rR, 4),
                   "dep_still_wins": bool(rD_ex > rR)})
lc_df = pd.DataFrame(lc)
if len(lc_df):
    H3 = bool(np.mean(lc_df["rho_dep_noTarget"] - lc_df["rho_RNA"]) > 0 and
              stats.wilcoxon(lc_df["rho_dep_noTarget"].values, lc_df["rho_RNA"].values).pvalue < 0.05)
    lc_summary = {"n_drugs": len(lc_df), "mean_dep_noTarget": round(float(lc_df["rho_dep_noTarget"].mean()), 4),
                  "mean_RNA": round(float(lc_df["rho_RNA"].mean()), 4),
                  "frac_dep_wins": round(float(lc_df["dep_still_wins"].mean()), 3),
                  "wilcoxon_p": float(stats.wilcoxon(lc_df["rho_dep_noTarget"].values, lc_df["rho_RNA"].values).pvalue)}
else:
    H3, lc_summary = None, None

print(f"\nn drugs: {len(df)}")
print(f"  mean per-drug rho:  RNA={np.mean(rR):+.4f}  dependency={np.mean(rD):+.4f}  both={np.mean(rRD):+.4f}")
print(f"  dependency vs RNA: {D_vs_R}")
print(f"  both vs RNA:       {RD_vs_R}")
print(f"H1 dep>=RNA: {H1} | H2 integration beats RNA (ceiling broken): {H2}")
print(f"target-leakage control ({lc_summary['n_drugs'] if lc_summary else 0} curated drugs): {lc_summary}")
print(f"H3 not-target-leakage (dep-noTarget > RNA): {H3}")

if H2 and H3:
    verdict = ("MEASURED FUNCTIONAL DEPENDENCY BREAKS THE BASELINE CEILING, and NOT via target tautology "
               "(survives target exclusion) -> functional measurement is the informative modality; genuine advance.")
elif H2 and H3 is False:
    verdict = ("Dependency beats RNA but the advantage is TARGET-TAUTOLOGICAL (vanishes once the drug's target is "
               "excluded) -> no generalizable functional-state signal beyond the known target. Honest bound.")
else:
    verdict = (f"CEILING HOLDS for measured genome-wide dependency (dep {np.mean(rD):+.3f} vs RNA {np.mean(rR):+.3f}; "
               f"both {np.mean(rRD):+.3f}) -> even measured function does not beat baseline here. Deepens B22/V21.")
print("\nVERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0], "sklearn": sklearn.__version__,
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": SEED,
       "data": {"crispr_sha256": sha256(os.path.join(DATA, "depmap_crispr_gene_effect.csv")), "n_matched_lines": len(matched),
                "n_drugs": len(df)},
       "mean_rho": {"RNA": round(float(np.mean(rR)), 4), "dependency": round(float(np.mean(rD)), 4), "both": round(float(np.mean(rRD)), 4)},
       "median_rho": {"RNA": round(float(np.median(rR)), 4), "dependency": round(float(np.median(rD)), 4), "both": round(float(np.median(rRD)), 4)},
       "dependency_vs_RNA": D_vs_R, "both_vs_RNA": RD_vs_R, "H1_dep_ge_RNA": H1, "H2_integration_breaks_ceiling": H2,
       "target_leakage_control": lc_summary, "target_leakage_per_drug": lc, "H3_not_target_leakage": H3,
       "per_drug": rows, "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B23_metrics.json"), "w"), indent=2)
print("wrote results/B23_metrics.json")
