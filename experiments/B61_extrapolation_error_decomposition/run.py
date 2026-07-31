"""B61 — per-compound decomposition of novel-chemistry extrapolation error. For every novel (scaffold+NN<0.4) test
compound across MoleculeACE targets, predict its |error| from competing per-compound mechanisms (AD-distance,
local-cliff, scaffold-novelty, potency-shift) simultaneously, and measure how predictable the error is at all.
Implements prereg/B61_extrapolation_error_decomposition.md. Deterministic -> reproduce x2. No docking.
"""
import os, sys, json, time, hashlib, glob
import numpy as np
import pandas as pd
import warnings; warnings.filterwarnings("ignore")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.ensemble import HistGradientBoostingRegressor
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
MACE = os.path.join(DATA, "moleculeace")
SEEDS, NN_NOVEL, MIN_NOVEL, KCLIFF = [1, 2, 3], 0.40, 15, 5
PREDICTORS = ["ad_distance", "local_cliff", "scaffold_novelty", "potency_shift"]


def bit(m): return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=1024)
def arr(fp):
    a = np.zeros(1024, dtype=np.float32); DataStructs.ConvertToNumpyArray(fp, a); return a
def murcko(m):
    try: return MurckoScaffold.GetScaffoldForMol(m)
    except Exception: return None


def process(path):
    df = pd.read_csv(path); pcol = "y [pEC50/pKi]"
    mols, ys = [], []
    for _, r in df.iterrows():
        m = Chem.MolFromSmiles(str(r["smiles"]))
        if m is not None and np.isfinite(r[pcol]):
            mols.append(m); ys.append(float(r[pcol]))
    if len(mols) < 60:
        return None
    ys = np.array(ys); X = np.vstack([arr(bit(m)) for m in mols]); FP = [bit(m) for m in mols]
    scafm = [murcko(m) for m in mols]
    scaf = np.array([Chem.MolToSmiles(s) if s is not None else "" for s in scafm], dtype=object)
    scafFP = [bit(s) if s is not None and s.GetNumAtoms() > 0 else None for s in scafm]
    n = len(mols); rows = []
    for seed in SEEDS:
        uniq = np.array(sorted(set(scaf))); perm = np.random.default_rng(seed).permutation(uniq)
        tsc = set(perm[:max(1, int(0.3 * len(uniq)))]); te = np.array([s in tsc for s in scaf])
        tr = np.where(~te)[0]; tec = np.where(te)[0]; trf = [FP[i] for i in tr]
        novel = [i for i in tec if max(DataStructs.BulkTanimotoSimilarity(FP[i], trf)) < NN_NOVEL]
        if len(novel) < MIN_NOVEL or len(tr) < 20:
            continue
        reg = HistGradientBoostingRegressor(random_state=42, max_iter=200, learning_rate=0.06, max_depth=6).fit(X[tr], ys[tr])
        tr_med = np.median(ys[tr]); tr_std = ys[tr].std() + 1e-9
        tr_scaf_fps = [f for f in (scafFP[i] for i in tr) if f is not None]
        for i in novel:
            pred = float(reg.predict(X[i:i + 1])[0]); errv = abs(pred - ys[i])
            sims = np.array(DataStructs.BulkTanimotoSimilarity(FP[i], trf))
            ad = 1.0 - float(sims.max())
            order = np.argsort(sims)[::-1][:KCLIFF]
            local_cliff = float(np.std(ys[tr][order]))
            sc_nov = 1.0 - (float(max(DataStructs.BulkTanimotoSimilarity(scafFP[i], tr_scaf_fps)))
                            if scafFP[i] is not None and tr_scaf_fps else 0.0)
            pot_shift = abs(ys[i] - tr_med) / tr_std
            rows.append({"error": errv, "ad_distance": ad, "local_cliff": local_cliff,
                         "scaffold_novelty": sc_nov, "potency_shift": pot_shift})
    return rows


def main():
    all_rows = []; per_target = {}
    for path in sorted(glob.glob(os.path.join(MACE, "CHEMBL*.csv"))):
        name = os.path.basename(path).replace(".csv", "")
        rows = process(path)
        nc = len(rows) if rows else 0; per_target[name] = nc
        if rows:
            for r in rows: r["target"] = name
            all_rows.extend(rows)
        print(f"  {name:18s} novel-test compounds pooled: {nc}")

    D = pd.DataFrame(all_rows)
    n_comp = len(D); n_tgt = int((pd.Series(per_target) > 0).sum())
    err = D["error"].values

    uni = {}
    for p in PREDICTORS:
        rho_pool, pv = spearmanr(D[p].values, err)
        wt = [spearmanr(g[p].values, g["error"].values).correlation for _, g in D.groupby("target") if len(g) >= 15]
        uni[p] = {"spearman_pooled": round(float(rho_pool), 4), "p_pooled": round(float(pv), 6),
                  "spearman_within_target_mean": round(float(np.nanmean(wt)), 4), "n_targets": len(wt)}
    ranked = sorted(uni.items(), key=lambda kv: -abs(kv[1]["spearman_pooled"]))

    Xp = D[PREDICTORS].values; tg = D["target"].values; oof = np.full(len(err), np.nan)
    for t in np.unique(tg):
        te = tg == t; trm = ~te
        if te.sum() < 5 or len(np.unique(err[trm])) < 5: continue
        m = HistGradientBoostingRegressor(random_state=42, max_iter=150, learning_rate=0.06, max_depth=4).fit(Xp[trm], err[trm])
        oof[te] = m.predict(Xp[te])
    ok = ~np.isnan(oof)
    multi_rho = round(float(spearmanr(oof[ok], err[ok]).correlation), 4) if ok.sum() > 20 else None

    top = ranked[0][0]; ad_rho = uni["ad_distance"]["spearman_pooled"]
    best_abs = max(abs(uni[p]["spearman_pooled"]) for p in PREDICTORS)
    h1 = bool(top == "ad_distance" and abs(ad_rho) >= best_abs - 1e-9 and ad_rho > 0)
    h2 = bool(multi_rho is not None and multi_rho >= 0.3)
    null = bool(best_abs < 0.2 and (multi_rho is None or multi_rho < 0.2))

    summary = {"n_compounds": n_comp, "n_targets": n_tgt, "univariate": uni,
               "ranked_by_abs_pooled_spearman": [k for k, _ in ranked], "strongest_predictor": top,
               "multivariate_error_predictability_oof_spearman": multi_rho,
               "H1_ad_distance_dominates": h1, "H2_error_meaningfully_predictable": h2, "H0_irreducible": null,
               "verdict": (
                   f"EXTRAPOLATION ERROR IS LARGELY IRREDUCIBLE (honest ceiling): across {n_comp} novel-chemistry "
                   f"compounds from {n_tgt} targets, NO per-compound feature meaningfully predicts the error (best "
                   f"|Spearman|={round(best_abs,3)}: {top}={uni[top]['spearman_pooled']}; AD-distance={ad_rho}) and a "
                   f"multivariate model of the error reaches OOF Spearman {multi_rho}. Novel-chemistry extrapolation "
                   f"error is dominated by irreducible/label-noise factors, NOT AD-distance, local roughness, "
                   f"scaffold-novelty, or potency-shift. Bounds P8: you cannot cheaply KNOW which novel predictions to "
                   f"trust from structure alone. Retrospective, in-silico, n={n_comp} compounds; not wet-lab."
                   if null else
                   f"EXTRAPOLATION ERROR IS PARTLY PREDICTABLE: strongest per-compound driver '{top}' (pooled Spearman "
                   f"{uni[top]['spearman_pooled']}, within-target {uni[top]['spearman_within_target_mean']}); AD-distance "
                   f"{ad_rho}; multivariate OOF Spearman {multi_rho}. "
                   + ("AD-distance dominates (H1) -> covariate/feature shift governs the extrapolation gap; a usable "
                      "trust rule for novel predictions exists." if h1 else
                      f"'{top}' (not AD-distance) dominates -> governing mechanism = "
                      f"{'local SAR ruggedness' if top=='local_cliff' else 'scaffold novelty' if top=='scaffold_novelty' else 'label/potency shift'}.")
                   + f" {n_comp} compounds, {n_tgt} targets; retrospective, in-silico; not wet-lab."),
               }
    print("\nUnivariate (pooled Spearman):", [(k, uni[k]['spearman_pooled']) for k in summary['ranked_by_abs_pooled_spearman']])
    print("Multivariate error predictability (OOF Spearman):", multi_rho)
    print("VERDICT:", summary["verdict"])

    prov = {"experiment": "B61_extrapolation_error_decomposition", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "seeds": SEEDS, "nn_novel": NN_NOVEL, "k_cliff": KCLIFF,
            "data": "MoleculeACE", "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = {"provenance": prov, "summary": summary, "per_target_novel_counts": per_target}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "B61_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary, "per_target_novel_counts": per_target}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B61_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B61_metrics.json")


def _libvers():
    import rdkit, numpy, scipy, sklearn, pandas
    return {"rdkit": rdkit.__version__, "numpy": numpy.__version__, "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__, "pandas": pandas.__version__}


if __name__ == "__main__":
    main()
