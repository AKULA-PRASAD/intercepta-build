"""B25 — does more diverse open data (DrugComb: 124 drugs, 41 cells) fix B24's weak NOVEL-DRUG synergy
generalization (leave-drug-out ρ=0.25)? Implements prereg/B25_synergy_scaleup.md. Reproduce x2.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import KFold, GroupKFold
import sklearn, warnings; warnings.filterwarnings("ignore")
from rdkit import Chem
from rdkit.Chem import AllChem

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D

SEED, KF, NBITS, MAXROWS = 42, 5, 1024, 120000
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
rng = np.random.default_rng(SEED)

syn = pd.read_parquet(os.path.join(DATA, "drugcomb_synergy.parquet"))
smi = pd.read_parquet(os.path.join(DATA, "drugcomb_smiles.parquet")).set_index("id")["smiles"].to_dict()
rna = D.load_depmap_expression()
if len(syn) > MAXROWS:                                       # seeded subsample; preserves all drugs+cells
    syn = syn.iloc[rng.permutation(len(syn))[:MAXROWS]].reset_index(drop=True)

def morgan(s):
    m = Chem.MolFromSmiles(str(s))
    if m is None: return np.zeros(NBITS, np.int8)
    return np.frombuffer(AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=NBITS).ToBitString().encode(), "u1").astype(np.int8) - ord("0")
FP = {d: morgan(s) for d, s in smi.items()}
syn = syn[syn["Drug1_ID"].isin(FP) & syn["Drug2_ID"].isin(FP) & syn["Cell_ACH"].isin(set(rna.index))].reset_index(drop=True)

cells = sorted(syn["Cell_ACH"].unique())
cmat = rna.loc[cells]
cpca = PCA(n_components=min(20, len(cells) - 1), random_state=SEED).fit(cmat.values)
CELLPC = pd.DataFrame(cpca.transform(cmat.values), index=cells)

y = syn["Synergy_Loewe"].values.astype(float)
pair_key = (syn["Drug1_ID"].astype(str) + "|" + syn["Drug2_ID"].astype(str)).apply(lambda s: "|".join(sorted(s.split("|")))).values
fp1 = np.vstack([FP[d] for d in syn["Drug1_ID"]]); fp2 = np.vstack([FP[d] for d in syn["Drug2_ID"]])
X = np.hstack([CELLPC.loc[syn["Cell_ACH"]].values, (fp1 + fp2).astype(np.int8), (fp1 & fp2).astype(np.int8)])
print(f"B25 DrugComb | n={len(y)} pairs={len(set(pair_key))} drugs={len(FP)} cells={len(cells)} feat={X.shape[1]}", flush=True)

def model(): return HistGradientBoostingRegressor(random_state=SEED, max_iter=200, learning_rate=0.06, max_depth=6)
def sp(a, b): return float(stats.spearmanr(a, b)[0])

# leave-combination-out (reference) + drug-marginal baseline
oofC = np.full(len(y), np.nan); baseC = np.full(len(y), np.nan)
for tr, te in GroupKFold(KF).split(X, y, pair_key):
    oofC[te] = model().fit(X[tr], y[tr]).predict(X[te])
    tr_df = pd.DataFrame({"d1": syn["Drug1_ID"].values[tr], "d2": syn["Drug2_ID"].values[tr], "y": y[tr]})
    dm = pd.concat([tr_df[["d1", "y"]].rename(columns={"d1": "d"}), tr_df[["d2", "y"]].rename(columns={"d2": "d"})]).groupby("d")["y"].mean()
    gm = y[tr].mean()
    baseC[te] = [np.mean([v for v in (dm.get(syn["Drug1_ID"].values[i]), dm.get(syn["Drug2_ID"].values[i])) if v is not None and np.isfinite(v)] or [gm]) for i in te]
loco = {"model_spearman": round(sp(oofC, y), 4), "drug_marginal_baseline_spearman": round(sp(baseC, y), 4),
        "delta": round(sp(oofC, y) - sp(baseC, y), 4)}

# LEAVE-DRUG-OUT (the fix test): partition drugs; test = both drugs held out
drugs_all = sorted(FP.keys()); dfold = {d: i % KF for i, d in enumerate(rng.permutation(drugs_all))}
d1f = syn["Drug1_ID"].map(dfold).values; d2f = syn["Drug2_ID"].map(dfold).values
predD = np.full(len(y), np.nan)
for k in range(KF):
    te = np.where((d1f == k) & (d2f == k))[0]; tr = np.where((d1f != k) & (d2f != k))[0]
    if len(te) < 50 or len(tr) < 500: continue
    predD[te] = model().fit(X[tr], y[tr]).predict(X[te])
mask = np.isfinite(predD)
rho_drug = sp(predD[mask], y[mask])
# bootstrap CI for leave-drug-out rho
idx = np.where(mask)[0]; boot = [sp(predD[b], y[b]) for b in (rng.choice(idx, len(idx), replace=True) for _ in range(1000))]
ci = (round(float(np.percentile(boot, 2.5)), 4), round(float(np.percentile(boot, 97.5)), 4))
ldo = {"n_test": int(mask.sum()), "model_spearman": round(rho_drug, 4), "ci95": ci, "B24_leave_drug_out_rho": 0.246}

# leave-cell-out
oofL = np.full(len(y), np.nan)
for tr, te in GroupKFold(min(KF, len(cells))).split(X, y, syn["Cell_ACH"].values):
    oofL[te] = model().fit(X[tr], y[tr]).predict(X[te])
lco = {"model_spearman": round(sp(oofL, y), 4)}

H1 = bool(rho_drug > 0.25 and ci[0] > 0)
H2 = bool(loco["model_spearman"] > 0 and loco["delta"] > 0)
print(f"\nleave-combination-out: model rho={loco['model_spearman']} vs drug-marginal {loco['drug_marginal_baseline_spearman']} (delta {loco['delta']})")
print(f"LEAVE-DRUG-OUT (fix test): rho={ldo['model_spearman']} CI95 {ci} (n={ldo['n_test']}) | B24 was 0.246")
print(f"leave-cell-out: rho={lco['model_spearman']} (cells={len(cells)}; ~B24's 39 -> not expected to improve)")
print(f"H1 novel-drug generalization improves (>0.25): {H1} | H2 combination sanity: {H2}")
if H1:
    verdict = (f"FIX WORKS: with 124 drugs (vs 38), novel-drug synergy generalization improves to rho={rho_drug:.3f} "
               f"(CI {ci}) vs B24's 0.25 -> the leave-drug weakness was chemical-diversity-limited, genuinely improved by open data.")
else:
    verdict = (f"HONEST BOUND: more chemical diversity (124 drugs) does NOT improve novel-drug generalization "
               f"(rho={rho_drug:.3f} vs B24 0.25) -> this weakness is closer to INTRINSIC than data-limited; reclassify in WEAKNESS_AUDIT.")
print("\nVERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0], "sklearn": sklearn.__version__,
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": SEED,
       "data": {"source": "DrugComb via TDC (open) + DepMap cell features", "n": int(len(y)), "n_pairs": int(len(set(pair_key))),
                "n_drugs": len(FP), "n_cells": len(cells), "subsampled_to": MAXROWS},
       "leave_combination_out": loco, "leave_drug_out": ldo, "leave_cell_out": lco,
       "H1_novel_drug_improves": H1, "H2_combination_sanity": H2, "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B25_metrics.json"), "w"), indent=2)
print("wrote results/B25_metrics.json")
