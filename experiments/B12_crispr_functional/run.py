"""B12 — does FUNCTIONAL gene-dependency (DepMap CRISPR) predict drug response, and beat baseline expression?
Implements prereg/B12_crispr_functional.md. Public cell-line data. Reproduce x2. Aggregate outputs only.
Requires depmap_crispr_gene_effect.csv under INTERCEPTA_DATA (see README / download instructions).
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
import sklearn, warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.metrics import bh_fdr

SEED, K, MIN_CELLS = 42, 2000, 25
HERE = os.path.dirname(os.path.abspath(__file__))
# drug -> target gene (established pharmacology), frozen in prereg
PAIRS = [("sorafenib","FLT3"),("quizartinib","FLT3"),("gilteritinib","FLT3"),("crenolanib","FLT3"),
         ("trametinib","MAP2K1"),("selumetinib","MAP2K1"),("pd0325901","MAP2K1"),
         ("venetoclax","BCL2"),("erlotinib","EGFR"),("gefitinib","EGFR"),("afatinib","EGFR"),
         ("alpelisib","PIK3CA"),("buparlisib","PIK3CA"),("ribociclib","CDK6"),("palbociclib","CDK6"),
         ("dabrafenib","BRAF"),("vemurafenib","BRAF"),("encorafenib","BRAF"),("alisertib","AURKA"),
         ("everolimus","MTOR"),("idasanutlin","MDM2"),("nutlin-3","MDM2")]
print("B12 CRISPR functional | sklearn", sklearn.__version__, flush=True)

ce = D.load_depmap_crispr()                    # cells x genes (gene effect; negative = dependency)
dx = D.load_depmap_expression()                # cells x genes (expression)
prism = D.load_prism(); prism["k"] = prism["name"].str.lower().str.strip()
cos2dep, _ = D.load_cosmic_depmap_map()
gdsc = D.load_gdsc_response(); gdsc = gdsc[gdsc["COSMIC_ID"].isin(cos2dep)].copy(); gdsc["dep"] = gdsc["COSMIC_ID"].map(cos2dep); gdsc["k"] = gdsc["DRUG_NAME"].str.lower().str.strip()

def response(drug):
    p = prism[prism["k"] == drug]
    if p["depmap_id"].nunique() >= 30:
        return p.groupby("depmap_id")["auc"].mean(), "PRISM_AUC"
    g = gdsc[gdsc["k"] == drug]
    if g["dep"].nunique() >= 30:
        return g.groupby("dep")["LN_IC50"].mean(), "GDSC_LN_IC50"
    return None, None

rows = []
for drug, gene in PAIRS:
    if gene not in ce.columns:
        rows.append({"drug": drug, "gene": gene, "skipped": "gene not in CRISPR"}); continue
    resp, src = response(drug)
    if resp is None:
        rows.append({"drug": drug, "gene": gene, "skipped": "drug<30 cells"}); continue
    cells = [c for c in resp.index if c in ce.index]
    if len(cells) < MIN_CELLS:
        rows.append({"drug": drug, "gene": gene, "skipped": f"n={len(cells)}<{MIN_CELLS}"}); continue
    y = resp[cells].values.astype(float)
    dep = ce.loc[cells, gene].values.astype(float)          # gene effect (neg = dependent)
    # Spearman(dependency, response): positive = more dependent (more neg effect) -> more sensitive (lower AUC/IC50)
    rho_dep = stats.spearmanr(dep, y)[0]
    rho_expr = np.nan
    if gene in dx.columns:
        ex = dx.loc[[c for c in cells if c in dx.index], gene]
        common = [c for c in cells if c in dx.index]
        if len(common) >= MIN_CELLS:
            rho_expr = stats.spearmanr(dx.loc[common, gene].values, resp[common].values)[0]
    rows.append({"drug": drug, "gene": gene, "src": src, "n": len(cells),
                 "rho_dependency": round(float(rho_dep), 4),
                 "rho_expression": (round(float(rho_expr), 4) if np.isfinite(rho_expr) else None)})

tested = [r for r in rows if "rho_dependency" in r]
rho_dep = np.array([r["rho_dependency"] for r in tested])
n = len(tested); rng = np.random.default_rng(SEED)
# H1: pooled dependency->response (permutation: sign-flip of per-pair rho under H0 mean 0)
obs1 = rho_dep.mean()
null1 = np.array([(rho_dep * (rng.integers(0, 2, n) * 2 - 1)).mean() for _ in range(K)])  # sign-flip null (mean 0)
p_h1 = (np.sum(null1 >= obs1) + 1) / (K + 1)
H1 = bool(obs1 > 0 and p_h1 < 0.05)
# per-pair BH on one-sided p from Fisher-z (dependency>0)
def one_sided_p(r, nn):
    if not np.isfinite(r) or nn < 6: return np.nan
    z = np.arctanh(np.clip(r,-0.999,0.999))*np.sqrt(nn-3); return float(stats.norm.sf(z))
for r in tested: r["dep_one_sided_p"] = one_sided_p(r["rho_dependency"], r["n"])
bh = bh_fdr([r["dep_one_sided_p"] for r in tested])
for r,q in zip(tested,bh): r["dep_BHq"]=float(q)
# H2: functional vs baseline (|rho_dep| vs |rho_expr|), paired where both exist
both = [r for r in tested if r["rho_expression"] is not None]
if len(both) >= 4:
    dabs = np.array([abs(r["rho_dependency"]) for r in both]); eabs = np.array([abs(r["rho_expression"]) for r in both])
    obs2 = float(np.median(dabs) - np.median(eabs)); m = len(both); do = np.column_stack([dabs,eabs])
    null2 = np.array([(lambda f: np.median(np.where(f,do[:,1],do[:,0]))-np.median(np.where(f,do[:,0],do[:,1])))(rng.integers(0,2,m).astype(bool)) for _ in range(K)])
    p_h2 = (np.sum(null2 >= obs2)+1)/(K+1); H2 = bool(obs2>0 and p_h2<0.05)
else:
    obs2, p_h2, H2 = np.nan, np.nan, False

print(f"\ntested pairs: {n}")
for r in sorted(tested, key=lambda x:-x["rho_dependency"]):
    print(f"  {r['drug']:<13}->{r['gene']:<7} [{r['src']}] n={r['n']:>3} rho_dep={r['rho_dependency']:+.3f} (BHq={r['dep_BHq']:.3g}) rho_expr={r['rho_expression']}")
print(f"\nH1 dependency->response pooled rho={obs1:+.4f} perm p={p_h1:.4g} -> {H1}")
print(f"H2 functional>baseline: median|rho_dep|={np.median([abs(r['rho_dependency']) for r in both]) if both else float('nan'):.3f} vs median|rho_expr|={np.median([abs(r['rho_expression']) for r in both]) if both else float('nan'):.3f} diff={obs2 if np.isfinite(obs2) else float('nan'):+.3f} perm p={p_h2 if np.isfinite(p_h2) else float('nan'):.4g} -> {H2}")
verdict = ("FUNCTIONAL MECHANISM: target dependency predicts drug sensitivity" + (" AND beats baseline expression (thesis supported)" if H2 else "; not better than expression for these targets") ) if H1 else "NULL: gene-dependency does not predict drug response here"
print("VERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0], "sklearn": sklearn.__version__,
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": SEED, "K": K,
       "n_pairs": n, "pairs": rows, "H1_pooled_rho": round(float(obs1),4), "H1_perm_p": float(p_h1), "H1_pass": H1,
       "H2_diff_medabs": (round(obs2,4) if np.isfinite(obs2) else None), "H2_perm_p": (float(p_h2) if np.isfinite(p_h2) else None), "H2_pass": H2, "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B12_metrics.json"), "w"), indent=2)
print("wrote results/B12_metrics.json")
