"""B24 — can we predict drug-combination SYNERGY for UNSEEN combinations (leave-drug-combination-out), beyond an
informed drug-identity baseline? Open O'Neil/OncoPolyPharmacology data (TDC). Implements
prereg/B24_synergy_generalization.md. Reproduce x2. Aggregate outputs only.
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

SEED, KF, NBITS = 42, 5, 1024
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
rng = np.random.default_rng(SEED)

syn = pd.read_parquet(os.path.join(DATA, "oneil_synergy.parquet"))
cellfeat = pd.read_parquet(os.path.join(DATA, "oneil_cellfeat.parquet"))
smi = pd.read_parquet(os.path.join(DATA, "oneil_smiles.parquet")).set_index("id")["smiles"].to_dict()

def morgan(s):
    m = Chem.MolFromSmiles(s)
    if m is None: return np.zeros(NBITS, np.int8)
    return np.frombuffer(AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=NBITS).ToBitString().encode(), "u1").astype(np.int8) - ord("0")
FP = {d: morgan(s) for d, s in smi.items()}

# cell PCA (unsupervised, 39 distinct cells) -> <=30 comps
cpca = PCA(n_components=min(30, cellfeat.shape[0] - 1), random_state=SEED).fit(cellfeat.values)
CELLPC = pd.DataFrame(cpca.transform(cellfeat.values), index=cellfeat.index)

# assemble features (order-invariant drug encoding: sum + bitwise-AND)
syn = syn[syn["Cell_Line_ID"].isin(CELLPC.index) & syn["Drug1_ID"].isin(FP) & syn["Drug2_ID"].isin(FP)].reset_index(drop=True)
y = syn["Y"].values.astype(float)
pair_key = (syn["Drug1_ID"].astype(str) + "|" + syn["Drug2_ID"].astype(str)).apply(lambda s: "|".join(sorted(s.split("|")))).values
X_cell = CELLPC.loc[syn["Cell_Line_ID"]].values
fp1 = np.vstack([FP[d] for d in syn["Drug1_ID"]]); fp2 = np.vstack([FP[d] for d in syn["Drug2_ID"]])
X = np.hstack([X_cell, (fp1 + fp2).astype(np.int8), (fp1 & fp2).astype(np.int8)])
print(f"B24 synergy | n={len(y)} pairs={len(set(pair_key))} cells={syn['Cell_Line_ID'].nunique()} features={X.shape[1]}", flush=True)

def model(): return HistGradientBoostingRegressor(random_state=SEED, max_iter=300, learning_rate=0.06, max_depth=6)
def perf(pred, yy, thr=10.0):
    r = float(stats.pearsonr(pred, yy)[0]); rho = float(stats.spearmanr(pred, yy)[0])
    lab = (yy > thr).astype(int)
    if lab.min() != lab.max():
        order = np.argsort(pred); ranks = np.empty_like(order, float); ranks[order] = np.arange(len(pred))
        n1 = lab.sum(); n0 = len(lab) - n1; auroc = float((ranks[lab == 1].sum() - n1 * (n1 - 1) / 2) / (n1 * n0))
    else: auroc = float("nan")
    return {"pearson": round(r, 4), "spearman": round(rho, 4), "auroc_syn": round(auroc, 4)}

def run_split(splitter, groups, tag):
    oof = np.full(len(y), np.nan); base = np.full(len(y), np.nan)
    it = splitter.split(X, y, groups) if groups is not None else splitter.split(X)
    for tr, te in it:
        oof[te] = model().fit(X[tr], y[tr]).predict(X[te])
        if tag == "random":                                   # baseline = training pair-mean (fallback global)
            pm = pd.Series(y[tr]).groupby(pair_key[tr]).mean(); gm = y[tr].mean()
            base[te] = [pm.get(pair_key[i], gm) for i in te]
        else:                                                 # LOCO/LOCELL baseline = drug-marginal mean (fallback global)
            gm = y[tr].mean()
            dm = {}
            tr_df = pd.DataFrame({"d1": syn["Drug1_ID"].values[tr], "d2": syn["Drug2_ID"].values[tr], "y": y[tr]})
            drug_mean = pd.concat([tr_df[["d1", "y"]].rename(columns={"d1": "d"}), tr_df[["d2", "y"]].rename(columns={"d2": "d"})]).groupby("d")["y"].mean()
            for i in te:
                v = [drug_mean.get(syn["Drug1_ID"].values[i]), drug_mean.get(syn["Drug2_ID"].values[i])]
                v = [x for x in v if x is not None and np.isfinite(x)]
                base[i] = np.mean(v) if v else gm
    return oof, base

results = {}
# 1. random 5-fold
oof, base = run_split(KFold(KF, shuffle=True, random_state=SEED), None, "random")
results["random_split"] = {"model": perf(oof, y), "pair_mean_baseline": perf(base, y),
                           "delta_spearman_vs_baseline": round(perf(oof, y)["spearman"] - perf(base, y)["spearman"], 4)}
# 2. leave-drug-combination-out
oofL, baseL = run_split(GroupKFold(KF), pair_key, "loco")
mL, bL = perf(oofL, y), perf(baseL, y)
# bootstrap p for delta-spearman (model vs baseline) under LOCO
def spear(a): return stats.spearmanr(a, y)[0]
obs = mL["spearman"] - bL["spearman"]; boot = []
idx = np.arange(len(y))
for _ in range(2000):
    b = rng.choice(idx, len(idx), replace=True)
    boot.append(stats.spearmanr(oofL[b], y[b])[0] - stats.spearmanr(baseL[b], y[b])[0])
boot = np.array(boot); p_delta = float(2 * min((boot <= 0).mean(), (boot >= 0).mean()))
ci = (round(float(np.percentile(boot, 2.5)), 4), round(float(np.percentile(boot, 97.5)), 4))
results["leave_combination_out"] = {"model": mL, "drug_marginal_baseline": bL,
                                    "delta_spearman_vs_baseline": round(obs, 4), "delta_ci95": ci, "delta_p": p_delta}
# 3. leave-cell-line-out
oofC, baseC = run_split(GroupKFold(min(KF, syn["Cell_Line_ID"].nunique())), syn["Cell_Line_ID"].values, "locell")
results["leave_cell_out"] = {"model": perf(oofC, y), "drug_marginal_baseline": perf(baseC, y),
                             "delta_spearman_vs_baseline": round(perf(oofC, y)["spearman"] - perf(baseC, y)["spearman"], 4)}

# 4. LEAVE-DRUG-OUT (strongest skeptical check: truly novel chemistry; both drugs of a test pair held out) ----
drugs_all = sorted(set(syn["Drug1_ID"]) | set(syn["Drug2_ID"]))
drug_fold = {d: i % KF for i, d in enumerate(rng.permutation(drugs_all))}
d1f = syn["Drug1_ID"].map(drug_fold).values; d2f = syn["Drug2_ID"].map(drug_fold).values
predD = np.full(len(y), np.nan)
for k in range(KF):
    te = np.where((d1f == k) & (d2f == k))[0]                 # both drugs in held-out fold
    tr = np.where((d1f != k) & (d2f != k))[0]                 # both drugs in train folds (drop cross pairs)
    if len(te) < 20 or len(tr) < 200: continue
    predD[te] = model().fit(X[tr], y[tr]).predict(X[te])
mask = np.isfinite(predD)
gm_all = y.mean()
mD = perf(predD[mask], y[mask]); bD = perf(np.full(mask.sum(), gm_all), y[mask])  # baseline: global mean (drug unseen)
results["leave_drug_out"] = {"n_test": int(mask.sum()), "model": mD, "global_mean_baseline_spearman": bD["spearman"],
                             "note": "both drugs of each test pair are held out (novel chemistry); baseline collapses to global mean"}
H3 = bool(mask.sum() > 100 and mD["spearman"] > 0.1 and (np.isnan(mD["auroc_syn"]) or mD["auroc_syn"] > 0.55))

H1 = bool(results["random_split"]["model"]["pearson"] > 0 and results["random_split"]["delta_spearman_vs_baseline"] > 0)
H2 = bool(mL["spearman"] > 0 and obs > 0 and p_delta < 0.05 and (np.isnan(mL["auroc_syn"]) or mL["auroc_syn"] > bL["auroc_syn"]))

print("\n=== random split (leaky reference) ===")
print("  model:", results["random_split"]["model"], "| pair-mean baseline:", results["random_split"]["pair_mean_baseline"])
print("=== LEAVE-DRUG-COMBINATION-OUT (the real generalization test) ===")
print("  model:", mL, "| drug-marginal baseline:", bL)
print(f"  delta Spearman vs baseline = {obs:+.4f}  CI95 {ci}  p={p_delta:.4g}")
print("=== leave-cell-line-out ===")
print("  model:", results["leave_cell_out"]["model"], "| baseline:", results["leave_cell_out"]["drug_marginal_baseline"])
print(f"=== LEAVE-DRUG-OUT (novel chemistry; n_test={results['leave_drug_out']['n_test']}) ===")
print("  model:", mD, "| global-mean baseline spearman:", bD["spearman"])
print(f"\nH1 (random sanity): {H1} | H2 (unseen combinations of seen drugs): {H2} | H3 (novel-drug chemistry generalizes): {H3}")

if H2 and H3:
    verdict = (f"GENERALIZES (incl. novel chemistry): synergy predictable for UNSEEN combinations beyond drug-identity "
               f"(LOCO Spearman {mL['spearman']:+.3f} vs baseline {bL['spearman']:+.3f}, delta {obs:+.3f} p={p_delta:.1e}) "
               f"AND survives LEAVE-DRUG-OUT (novel drugs, Spearman {mD['spearman']:+.3f}) — a genuine, useful, "
               f"chemistry-generalizing signal. First clearly-positive generalizing predictor in the program.")
elif H2:
    verdict = (f"GENERALIZES to unseen COMBINATIONS OF KNOWN DRUGS (LOCO Spearman {mL['spearman']:+.3f} vs baseline "
               f"{bL['spearman']:+.3f}, delta {obs:+.3f} p={p_delta:.1e}) — real and useful — BUT does NOT clearly "
               f"survive leave-drug-out (novel chemistry, Spearman {mD['spearman']:+.3f}); claim bounded to new "
               f"pairings of seen drugs. Honest scope.")
elif H1:
    verdict = (f"CEILING (honest negative): strong on random split (Pearson {results['random_split']['model']['pearson']}) "
               f"but does NOT beat the drug-identity baseline for UNSEEN combinations (LOCO delta {obs:+.3f}, p={p_delta:.2g}) "
               f"-> synergy prediction here is largely drug-identity memorization, not generalizable. Consistent with "
               f"the program theme: generalization is the wall.")
else:
    verdict = "Model fails even the random-split sanity check — investigate features/pipeline before interpreting."
print("\nVERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0], "sklearn": sklearn.__version__,
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": SEED,
       "data": {"source": "O'Neil 2016 / OncoPolyPharmacology via TDC (open)", "n": int(len(y)),
                "n_pairs": int(len(set(pair_key))), "n_cells": int(syn["Cell_Line_ID"].nunique()), "n_features": int(X.shape[1])},
       "results": results, "H1_random_sanity": H1, "H2_generalizes_to_unseen_combos": H2,
       "H3_generalizes_to_novel_drugs": H3, "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B24_metrics.json"), "w"), indent=2)
print("wrote results/B24_metrics.json")
