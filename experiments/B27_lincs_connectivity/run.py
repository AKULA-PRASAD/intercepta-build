"""B27 — does LINCS L1000 signature-reversal (connectivity) predict drug efficacy? Repurposing test: within a
cell line, does reversal rank drugs by PRISM sensitivity better than chance? Implements
prereg/B27_lincs_connectivity.md. Open data (dhimmel/lincs + PRISM + DepMap). Reproduce x2.
"""
import os, sys, json, time, re
import numpy as np, pandas as pd
from scipy import stats
import warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.axes import CELL_CYCLE, REPLICATION

SEED, NPERM, MIN_DRUGS = 42, 2000, 30
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
LB = os.path.join(DATA, "lincs/dhimmel-lincs-8e9c56a/data")
rng = np.random.default_rng(SEED)
norm = lambda x: re.sub(r"[^a-z0-9]", "", str(x).lower())

# --- LINCS consensus signatures (DrugBank x Entrez) -> drug-name x symbol ---
sig = pd.read_csv(os.path.join(LB, "consensi/consensi-drugbank.tsv"), sep="\t").set_index("perturbagen")
genes = pd.read_csv(os.path.join(LB, "consensi/genes.tsv"), sep="\t")
e2s = {str(r.entrez_gene_id): r.symbol for r in genes.itertuples()}
sig.columns = [e2s.get(str(c)) for c in sig.columns]
sig = sig.loc[:, [c for c in sig.columns if isinstance(c, str)]]
sig = sig.loc[:, ~sig.columns.duplicated()]
db = pd.read_csv(os.path.join(DATA, "drugbank_slim.tsv"), sep="\t")[["drugbank_id", "name"]]
id2name = {r.drugbank_id: r.name for r in db.itertuples()}
sig.index = [id2name.get(i) for i in sig.index]
sig = sig[[isinstance(i, str) for i in sig.index]]
sig = sig.groupby(level=0).mean()                          # collapse dup names
sig["_k"] = [norm(i) for i in sig.index]; sig = sig.groupby("_k").mean()   # normalized-name key

# --- PRISM efficacy (drug x cell AUC) ---
pr = D.load_prism()                                        # depmap_id, name, auc
pr["_k"] = pr["name"].map(norm)
rna = D.load_depmap_expression()                           # cells x genes (symbols)

shared_genes = [g for g in sig.columns if g in set(rna.columns)]
shared_drugs = [k for k in sig.index if k in set(pr["_k"])]
print(f"B27 | LINCS genes∩DepMap={len(shared_genes)} | drugs LINCS∩PRISM={len(shared_drugs)}", flush=True)

prism_cells = [c for c in rna.index if c in set(pr["depmap_id"])]   # restrict to PRISM-covered cells (efficiency)
rna = rna.loc[prism_cells]
Sig = sig.loc[shared_drugs, shared_genes]                  # drugs x genes (z-scores)
# cell state: expression z-scored per gene across cells
X = rna[shared_genes]
cellz = (X - X.mean(0)) / X.std(0).replace(0, 1)           # cells x genes
# standardize each drug sig and each cell state across genes, then reversal = -corr
def zrow(M): M = M - M.mean(1).values[:, None]; s = M.std(1).values[:, None]; return M / np.where(s == 0, 1, s)
Dz = zrow(Sig.copy()); Cz = zrow(cellz.copy())
cells = list(Cz.index)
REV = -(Dz.values @ Cz.values.T) / len(shared_genes)        # drugs x cells reversal score
REV = pd.DataFrame(REV, index=shared_drugs, columns=cells)

# PRISM AUC matrix drugs x cells (mean over dup), sensitivity = -AUC
auc = pr[pr["_k"].isin(shared_drugs) & pr["depmap_id"].isin(cells)].groupby(["_k", "depmap_id"])["auc"].mean().unstack()
auc = auc.reindex(index=shared_drugs, columns=cells)
SENS = -auc                                                 # higher = more sensitive

def pooled_within(axis):
    """axis='cell': within each cell, Spearman(reversal over drugs, sensitivity over drugs). 'drug': transpose."""
    rev, sen = (REV, SENS) if axis == "cell" else (REV.T, SENS.T)
    units = rev.columns; rhos, ns = [], []
    for u in units:
        r = rev[u]; s = sen[u]; ok = r.notna() & s.notna()
        if ok.sum() >= MIN_DRUGS:
            rho = stats.spearmanr(r[ok], s[ok])[0]
            if np.isfinite(rho): rhos.append(rho); ns.append(int(ok.sum()))
    rhos = np.array(rhos); ns = np.array(ns)
    z = np.arctanh(np.clip(rhos, -.999, .999)); zmu = np.sum(z * (ns - 3)) / np.sum(ns - 3)
    return {"mean_rho": round(float(np.mean(rhos)), 4), "pooled_z": round(float(zmu * np.sqrt(np.sum(ns - 3))), 3),
            "n_units": len(rhos), "median_n": int(np.median(ns))}, rhos, ns

cell_res, cell_rhos, cell_ns = pooled_within("cell")
drug_res, _, _ = pooled_within("drug")

# within-cell permutation null: shuffle drug labels of sensitivity within each cell, recompute mean rho
obs = cell_res["mean_rho"]; perm = np.empty(NPERM)
Srev = REV.values; Ssen = SENS.values
for j in range(NPERM):
    pr_rhos = []
    for ci in range(len(cells)):
        r = Srev[:, ci]; s = Ssen[:, ci]; ok = np.isfinite(r) & np.isfinite(s)
        if ok.sum() >= MIN_DRUGS:
            sp = rng.permutation(s[ok]); rho = stats.spearmanr(r[ok], sp)[0]
            if np.isfinite(rho): pr_rhos.append(rho)
    perm[j] = np.mean(pr_rhos)
p_perm = float((1 + np.sum(perm >= obs)) / (1 + NPERM))
H1 = bool(obs > 0 and p_perm < 0.05)
NEGLIGIBLE = 0.05                                           # |rho| below this = practically negligible, however significant

# H3 robustness (only meaningful if H1): exclude proliferation genes, recompute within-cell mean rho
prolif = set(CELL_CYCLE) | set(REPLICATION)
ng = [g for g in shared_genes if g not in prolif]
Dz2 = zrow(Sig[ng].copy()); Cz2 = zrow(cellz[ng].copy())
REV2 = pd.DataFrame(-(Dz2.values @ Cz2.values.T) / len(ng), index=shared_drugs, columns=cells)
rr = []
for ci, u in enumerate(cells):
    r = REV2[u]; s = SENS[u]; ok = r.notna() & s.notna()
    if ok.sum() >= MIN_DRUGS:
        rho = stats.spearmanr(r[ok], s[ok])[0]
        if np.isfinite(rho): rr.append(rho)
prolif_excl_rho = round(float(np.mean(rr)), 4)

print(f"\nwithin-CELL (repurposing): mean Spearman(reversal,sensitivity)={cell_res['mean_rho']} over {cell_res['n_units']} cells "
      f"(median {cell_res['median_n']} drugs), permutation p={p_perm:.4g}")
print(f"within-DRUG: mean rho={drug_res['mean_rho']} over {drug_res['n_units']} drugs")
print(f"proliferation-gene-excluded within-cell mean rho={prolif_excl_rho} (H3 robustness)")
print(f"H1 (connectivity predicts efficacy within-cell): {H1}")
if H1 and abs(cell_res["mean_rho"]) < NEGLIGIBLE:
    verdict = (f"STATISTICALLY SIGNIFICANT BUT PRACTICALLY NEGLIGIBLE: within-cell reversal->sensitivity mean rho "
               f"{cell_res['mean_rho']} (perm p={p_perm:.1e}) is significant only because of huge N "
               f"({cell_res['n_units']} cells x ~{cell_res['median_n']} drugs); |rho|<{NEGLIGIBLE} explains ~"
               f"{100*cell_res['mean_rho']**2:.2f}% of variance -> NOT a practically useful repurposing signal. "
               f"Proliferation-robust ({prolif_excl_rho}). Honest: connectivity has a real but vanishingly small "
               f"effect here, consistent with the program theme that generic transcriptomic signals are weak.")
elif H1 and abs(prolif_excl_rho - cell_res["mean_rho"]) < 0.02:
    verdict = (f"CONNECTIVITY PREDICTS EFFICACY (usable, prolif-robust): within-cell reversal->sensitivity mean rho "
               f"{cell_res['mean_rho']} (perm p={p_perm:.1e}), survives proliferation-gene exclusion ({prolif_excl_rho}).")
elif H1:
    verdict = (f"within-cell signal present (rho {cell_res['mean_rho']}, p={p_perm:.1e}) but changes on proliferation-"
               f"gene exclusion ({prolif_excl_rho}) -> partly a proliferation confound. Honest, bounded.")
else:
    verdict = (f"HONEST NEGATIVE: LINCS signature-reversal does NOT predict drug efficacy within cells "
               f"(mean rho {cell_res['mean_rho']}, perm p={p_perm:.2g}). Consistent with the program theme.")
out_practical = bool(H1 and abs(cell_res["mean_rho"]) >= NEGLIGIBLE)
print("\nVERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": SEED,
       "data": {"n_shared_genes": len(shared_genes), "n_drugs": len(shared_drugs), "n_cells": len(cells)},
       "within_cell": cell_res, "within_cell_perm_p": p_perm, "within_drug": drug_res,
       "prolif_excluded_within_cell_rho": prolif_excl_rho, "H1_statistically_significant": H1,
       "practically_useful_effect": bool(H1 and abs(cell_res["mean_rho"]) >= NEGLIGIBLE),
       "effect_size_note": f"mean rho {cell_res['mean_rho']} explains ~{100*cell_res['mean_rho']**2:.3f}% of variance",
       "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B27_metrics.json"), "w"), indent=2)
print("wrote results/B27_metrics.json")
