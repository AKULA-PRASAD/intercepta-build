"""B29 — are the SynergyRanker conformal prediction intervals CALIBRATED? Split-conformal empirical coverage,
disjoint by drug combination (valid for unseen combinations). Implements prereg/B29_synergy_conformal_coverage.md.
Reproduce x2.
"""
import os, sys, json, time, re
import numpy as np, pandas as pd
import warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.synergy import SynergyRanker

SEEDS, NLEVELS = [0, 1, 2, 3, 4], {"90pct": 0.10, "80pct": 0.20}
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
norm = lambda x: re.sub(r"[^a-z0-9]", "", str(x).lower())

rna = D.load_depmap_expression()
meta = pd.read_csv(os.path.join(DATA, "depmap_meta.csv")); n2a = {}
for _, r in meta.iterrows():
    for c in ["stripped_cell_line_name", "CCLE_Name", "cell_line_name"]:
        v = r.get(c)
        if pd.notna(v): n2a[norm(str(v).split("_")[0] if c == "CCLE_Name" else v)] = r["DepMap_ID"]

def load(corpus):
    if corpus == "oneil":
        s = pd.read_parquet(os.path.join(DATA, "oneil_synergy.parquet")).rename(columns={"Drug1_ID": "d1", "Drug2_ID": "d2", "Cell_Line_ID": "c", "Y": "Y"})
        s["Cell"] = s["c"].map(lambda c: n2a.get(norm(c)))
        smi = pd.read_parquet(os.path.join(DATA, "oneil_smiles.parquet")).set_index("id")["smiles"].to_dict()
    else:
        s = pd.read_parquet(os.path.join(DATA, "drugcomb_synergy.parquet")).rename(columns={"Drug1_ID": "d1", "Drug2_ID": "d2", "Cell_ACH": "Cell", "Synergy_Loewe": "Y"})
        smi = pd.read_parquet(os.path.join(DATA, "drugcomb_smiles.parquet")).set_index("id")["smiles"].to_dict()
        if len(s) > 60000: s = s.iloc[np.random.default_rng(0).permutation(len(s))[:60000]]
    s = s.dropna(subset=["Cell", "Y"]); s = s[s["Cell"].isin(set(rna.index))].reset_index(drop=True)
    s["pair"] = (s["d1"].astype(str) + "|" + s["d2"].astype(str)).map(lambda x: "|".join(sorted(x.split("|"))))
    return s, smi

def coverage_for(corpus):
    s, smi = load(corpus)
    cells = sorted(s["Cell"].unique()); cell_expr = rna.loc[cells]
    pairs = np.array(sorted(s["pair"].unique()))
    res = {lv: [] for lv in NLEVELS}; widths = {lv: [] for lv in NLEVELS}
    for seed in SEEDS:
        rng = np.random.default_rng(seed); perm = rng.permutation(pairs)
        n = len(perm); tr = set(perm[:int(.6 * n)]); ca = set(perm[int(.6 * n):int(.8 * n)]); te = set(perm[int(.8 * n):])
        strain = s[s["pair"].isin(tr)]
        r = SynergyRanker(n_pca=20).fit(strain.rename(columns={"d1": "Drug1_ID", "d2": "Drug2_ID"}), cell_expr, smi, compute_cv=False)
        def predy(sub):
            p = r.predict(rna.loc[sorted(sub["Cell"].unique())].T,
                          sub[["Cell", "d1", "d2"]].rename(columns={"Cell": "sample", "d1": "drug1", "d2": "drug2"}), smiles=smi)
            ok = p["predicted_synergy"].notna().values
            return p["predicted_synergy"].values[ok], sub["Y"].values[ok]
        pc, yc = predy(s[s["pair"].isin(ca)]); pt, yt = predy(s[s["pair"].isin(te)])
        for lv, a in NLEVELS.items():
            q = float(np.quantile(np.abs(pc - yc), 1 - a))
            res[lv].append(float(np.mean(np.abs(pt - yt) <= q))); widths[lv].append(2 * q)
    return {lv: {"nominal": round(1 - NLEVELS[lv], 2), "empirical_coverage": round(float(np.mean(res[lv])), 4),
                 "mean_interval_width": round(float(np.mean(widths[lv])), 2)} for lv in NLEVELS}

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seeds": SEEDS, "corpora": {}}
for corpus in ["oneil", "drugcomb"]:
    cov = coverage_for(corpus); out["corpora"][corpus] = cov
    print(f"[{corpus}]")
    for lv, d in cov.items():
        print(f"  nominal {d['nominal']:.0%} -> empirical coverage {d['empirical_coverage']:.1%} | mean interval width {d['mean_interval_width']}")

def cal(corpus): return all(abs(d["empirical_coverage"] - d["nominal"]) <= 0.05 for d in out["corpora"][corpus].values())
H1 = bool(cal("oneil"))
out["H1_oneil_calibrated_within_0.05"] = H1
out["verdict"] = ("CALIBRATED: conformal intervals achieve ~nominal coverage on unseen combinations (O'Neil within +-0.05); "
                  "uncertainty is validated. NOTE intervals are WIDE — the honest message that point synergy predictions carry "
                  "substantial uncertainty.") if H1 else \
    ("MISCALIBRATED beyond +-0.05 on O'Neil — report honestly; intervals approximate, not guaranteed. " + json.dumps(out["corpora"]["oneil"]))
print("\nH1 (O'Neil calibrated within +-0.05):", H1)
print("VERDICT:", out["verdict"])
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B29_metrics.json"), "w"), indent=2)
print("wrote results/B29_metrics.json")
