"""B28 — cross-corpus external validation of the synergy ranker: train on one corpus, predict MEASURED synergy in
an independent one (O'Neil <-> DrugComb). Rank (Spearman) + retrieval (precision@10%) + novel-combination subset.
Implements prereg/B28_synergy_crosscorpus.md. Reproduce x2.
"""
import os, sys, json, time, re
import numpy as np, pandas as pd
from scipy import stats
import warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.synergy import SynergyRanker

SEED = 42
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
rng = np.random.default_rng(SEED)
norm = lambda x: re.sub(r"[^a-z0-9]", "", str(x).lower())

rna = D.load_depmap_expression()
meta = pd.read_csv(os.path.join(DATA, "depmap_meta.csv"))
n2a = {}
for _, r in meta.iterrows():
    for c in ["stripped_cell_line_name", "CCLE_Name", "cell_line_name"]:
        v = r.get(c)
        if pd.notna(v):
            n2a[norm(str(v).split("_")[0] if c == "CCLE_Name" else v)] = r["DepMap_ID"]

def load_oneil():
    syn = pd.read_parquet(os.path.join(DATA, "oneil_synergy.parquet")).rename(columns={"Cell_Line_ID": "cellname", "Y": "Y"})
    syn["sample"] = syn["cellname"].map(lambda c: n2a.get(norm(c)))
    smi = pd.read_parquet(os.path.join(DATA, "oneil_smiles.parquet")).set_index("id")["smiles"].to_dict()
    syn = syn.rename(columns={"Drug1_ID": "drug1", "Drug2_ID": "drug2"})
    return syn.dropna(subset=["sample"])[["drug1", "drug2", "sample", "Y"]], smi

def load_drugcomb():
    syn = pd.read_parquet(os.path.join(DATA, "drugcomb_synergy.parquet")).rename(
        columns={"Cell_ACH": "sample", "Synergy_Loewe": "Y", "Drug1_ID": "drug1", "Drug2_ID": "drug2"})
    smi = pd.read_parquet(os.path.join(DATA, "drugcomb_smiles.parquet")).set_index("id")["smiles"].to_dict()
    return syn[["drug1", "drug2", "sample", "Y"]], smi

def fit_ranker(name):
    return SynergyRanker.from_oneil() if name == "oneil" else SynergyRanker.from_drugcomb()

def pair_key(df): return (df["drug1"].astype(str) + "|" + df["drug2"].astype(str)).map(lambda s: "|".join(sorted(s.split("|"))))

def evaluate(train_name, test_syn, test_smi, train_pairs):
    r = fit_ranker(train_name)
    test = test_syn[test_syn["sample"].isin(set(rna.index))].dropna(subset=["Y"]).reset_index(drop=True)
    # subsample for runtime (seeded); preserves diversity
    if len(test) > 60000:
        test = test.iloc[rng.permutation(len(test))[:60000]].reset_index(drop=True)
    expr = rna.loc[sorted(test["sample"].unique())].T
    pred = r.predict(expr, test[["sample", "drug1", "drug2"]], smiles=test_smi)
    ok = pred["predicted_synergy"].notna() & test["Y"].notna()
    p = pred.loc[ok, "predicted_synergy"].values; y = test.loc[ok, "Y"].values
    rho = float(stats.spearmanr(p, y)[0]); n = int(ok.sum())
    # bootstrap CI
    idx = np.arange(n); boot = [stats.spearmanr(p[b], y[b])[0] for b in (rng.choice(idx, n, replace=True) for _ in range(1000))]
    ci = (round(float(np.percentile(boot, 2.5)), 4), round(float(np.percentile(boot, 97.5)), 4))
    # retrieval: precision@10% -- of top-10% predicted, fraction with measured Y in top quartile of test corpus
    thr_y = np.quantile(y, 0.75); base = float((y >= thr_y).mean())
    k = max(1, int(0.10 * n)); topk = np.argsort(-p)[:k]; prec = float((y[topk] >= thr_y).mean())
    # novel-combination subset (test pairs whose combination not in training corpus)
    tp = pair_key(test.loc[ok].reset_index(drop=True)); novel = ~tp.isin(set(train_pairs))
    rho_novel = float(stats.spearmanr(p[novel.values], y[novel.values])[0]) if novel.sum() > 200 else None
    return {"train": train_name, "n_eval": n, "spearman": round(rho, 4), "ci95": ci,
            "precision_at_10pct": round(prec, 4), "base_rate": round(base, 4), "enrichment": round(prec / base, 3) if base > 0 else None,
            "n_novel_combos": int(novel.sum()), "spearman_novel_combos": (round(rho_novel, 4) if rho_novel is not None else None)}

oneil, oneil_smi = load_oneil(); dc, dc_smi = load_drugcomb()
oneil_pairs = set(pair_key(oneil)); dc_pairs = set(pair_key(dc))
print("evaluating O'Neil -> DrugComb ...", flush=True)
o2d = evaluate("oneil", dc, dc_smi, oneil_pairs)
print("  ", o2d, flush=True)
print("evaluating DrugComb -> O'Neil ...", flush=True)
d2o = evaluate("drugcomb", oneil, oneil_smi, dc_pairs)
print("  ", d2o, flush=True)

both_pos = o2d["spearman"] > 0 and o2d["ci95"][0] > 0 and d2o["spearman"] > 0 and d2o["ci95"][0] > 0
strong = both_pos and o2d["spearman"] >= 0.1 and d2o["spearman"] >= 0.1
H3 = (o2d["spearman_novel_combos"] or 0) > 0 and (d2o["spearman_novel_combos"] or 0) > 0
if strong and H3:
    verdict = (f"EXTERNALLY VALIDATED across independent corpora: O'Neil->DrugComb rho={o2d['spearman']} (CI {o2d['ci95']}), "
               f"DrugComb->O'Neil rho={d2o['spearman']} (CI {d2o['ci95']}); holds on novel combinations; retrieval enrichment "
               f"{o2d['enrichment']}/{d2o['enrichment']}x. The synergy ranker transfers across labs/assays.")
elif both_pos:
    verdict = (f"TRANSFERS WEAKLY across corpora (O'Neil->DrugComb rho={o2d['spearman']}, DrugComb->O'Neil rho={d2o['spearman']}; "
               f"both CI>0 but small) -> real but modest external transfer; honestly bounded.")
else:
    verdict = (f"DOES NOT robustly transfer across corpora (O'Neil->DrugComb rho={o2d['spearman']}, DrugComb->O'Neil "
               f"rho={d2o['spearman']}) -> the ranker is within-corpus; honest ceiling on the shipped tool.")
print("\nVERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": SEED,
       "oneil_to_drugcomb": o2d, "drugcomb_to_oneil": d2o,
       "H1_both_positive_ci_excludes_0": bool(both_pos), "externally_validated_nonneg": bool(strong),
       "H3_novel_combos_positive": bool(H3), "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B28_metrics.json"), "w"), indent=2)
print("wrote results/B28_metrics.json")
