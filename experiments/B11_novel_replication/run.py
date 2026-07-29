"""B11 — cross-system replication of NOVEL BeatAML markers in pan-cancer DepMap cell lines.
Implements prereg/B11_novel_marker_replication.md. Public data. Reproduce x2. Aggregate outputs only.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
import sklearn, warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.metrics import bh_fdr

MIN_MUT, MIN_WT = 8, 8
HERE = os.path.dirname(os.path.abspath(__file__))
# BeatAML drug -> GDSC/PRISM name
SYN = {"flavopiridol": "alvocidib"}
PAIRS = [("DNMT3A", "saracatinib"), ("NRAS", "mk-2206"), ("NRAS", "bortezomib"), ("NRAS", "flavopiridol"),
         ("IDH2", "saracatinib"), ("IDH2", "vandetanib"), ("IDH2", "afatinib"), ("IDH2", "nvp-tae684"),
         ("IDH2", "doramapimod"), ("IDH2", "tozasertib"), ("U2AF1", "cediranib"), ("U2AF1", "pelitinib"),
         ("WT1", "raf265"), ("BCOR", "raf265")]
print("B11 novel-marker cross-system replication | sklearn", sklearn.__version__, flush=True)

# mutations: gene -> set(DepMap_ID) non-silent
NS = {"Missense_Mutation", "Nonsense_Mutation", "Frame_Shift_Del", "Frame_Shift_Ins", "Splice_Site",
      "In_Frame_Del", "In_Frame_Ins", "Nonstop_Mutation"}
maf = pd.read_csv(D._p("depmap_mut_try1.csv"), usecols=["Hugo_Symbol", "DepMap_ID", "Variant_Classification"], low_memory=False)
maf = maf[maf["Variant_Classification"].isin(NS)]
genes = set(g for g, _ in PAIRS)
gene_cells = {g: set(maf[maf["Hugo_Symbol"] == g]["DepMap_ID"].unique()) for g in genes}
all_mut_tested = set(maf["DepMap_ID"].unique())          # cells with a MAF (so wt = tested-but-no-variant)

# drug response: PRISM (depmap_id, name, auc) primary; GDSC (LN_IC50 via COSMIC->DepMap) fallback
prism = D.load_prism(); prism["k"] = prism["name"].str.lower().str.strip()
cos2dep, _ = D.load_cosmic_depmap_map()
gdsc = D.load_gdsc_response(); gdsc = gdsc[gdsc["COSMIC_ID"].isin(cos2dep)].copy(); gdsc["dep"] = gdsc["COSMIC_ID"].map(cos2dep); gdsc["k"] = gdsc["DRUG_NAME"].str.lower().str.strip()

def response(drug):
    dk = SYN.get(drug, drug)
    p = prism[prism["k"] == dk]
    if p["depmap_id"].nunique() >= 30:
        return p.groupby("depmap_id")["auc"].mean(), "PRISM_AUC"
    g = gdsc[gdsc["k"] == dk]
    if g["dep"].nunique() >= 30:
        return g.groupby("dep")["LN_IC50"].mean(), "GDSC_LN_IC50"
    return None, None

rows = []
for gene, drug in PAIRS:
    resp, src = response(drug)
    if resp is None:
        rows.append({"gene": gene, "drug": drug, "skipped": "drug<30 cells"}); continue
    cells = [c for c in resp.index if c in all_mut_tested]
    mut = np.array([1.0 if c in gene_cells[gene] else 0.0 for c in cells])
    y = resp[cells].values.astype(float)
    nm, nw = int(mut.sum()), int((mut == 0).sum())
    if nm < MIN_MUT or nw < MIN_WT:
        rows.append({"gene": gene, "drug": drug, "n_mut": nm, "n_wt": nw, "skipped": "n<8"}); continue
    ym, yw = y[mut == 1], y[mut == 0]
    p = stats.mannwhitneyu(ym, yw, alternative="two-sided")[1]
    sensitizing = bool(np.median(ym) < np.median(yw))     # mut more sensitive (lower AUC/IC50)
    rows.append({"gene": gene, "drug": drug, "src": src, "n_mut": nm, "n_wt": nw,
                 "median_mut": round(float(np.median(ym)), 3), "median_wt": round(float(np.median(yw)), 3),
                 "mwu_p": float(p), "sensitizing_in_celllines": sensitizing,
                 "matches_beataml_direction": sensitizing})

tested = [r for r in rows if "mwu_p" in r]
if tested:
    bh = bh_fdr([r["mwu_p"] for r in tested])
    for r, q in zip(tested, bh):
        r["BHq"] = float(q); r["replicated"] = bool(q < 0.05 and r["sensitizing_in_celllines"])
n_rep = sum(r.get("replicated", False) for r in tested)

print(f"\ntested pairs: {len(tested)} / {len(PAIRS)}")
for r in sorted(tested, key=lambda x: x["mwu_p"]):
    print(f"  {r['gene']:<7}->{r['drug']:<14} [{r['src']}] mut={r['n_mut']:>3} wt={r['n_wt']:>3} "
          f"med {r['median_mut']:.2f}v{r['median_wt']:.2f} MWUp={r['mwu_p']:.3g} BHq={r['BHq']:.3g} "
          f"sensitizing={r['sensitizing_in_celllines']} REPLICATED={r.get('replicated')}")
for r in rows:
    if "skipped" in r: print(f"  {r['gene']:<7}->{r['drug']:<14} SKIPPED ({r['skipped']})")
verdict = (f"{n_rep} of {len(tested)} novel BeatAML markers REPLICATE cross-system (BH<0.05 + same direction) in "
           f"pan-cancer DepMap cell lines" if n_rep else
           "NO novel BeatAML marker replicates cross-system in pan-cancer cell lines (AML-specific or spurious; honest null)")
print("VERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0], "sklearn": sklearn.__version__,
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "n_pairs_tested": len(tested), "n_replicated": n_rep, "pairs": rows, "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B11_metrics.json"), "w"), indent=2)
print("wrote results/B11_metrics.json")
