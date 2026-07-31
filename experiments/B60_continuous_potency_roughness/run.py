"""B60 — does continuous-potency landscape roughness (ROGI on real pKi/pIC50) predict NOVEL-CHEMISTRY generalization of
a ligand-based potency model? The honest instrument for P7 (B58 used binary labels). MoleculeACE 30 ChEMBL targets.
Implements prereg/B60_continuous_potency_roughness.md. Deterministic -> reproduce x2. No docking.
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
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
MACE = os.path.join(DATA, "moleculeace")
SEEDS, NN_NOVEL, MIN_NOVEL, ROGI_N = [1, 2, 3], 0.40, 15, 500


def bit(m): return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=1024)
def arr(fp):
    a = np.zeros(1024, dtype=np.float32); DataStructs.ConvertToNumpyArray(fp, a); return a
def murcko(m):
    try: return Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(m))
    except Exception: return ""


def rogi(y, fps):
    y = np.asarray(y, float); s = y.std()
    if s < 1e-9 or len(y) < 4: return float("nan")
    y = (y - y.mean()) / s; n = len(y)
    D = np.zeros((n, n))
    for i in range(n):
        D[i] = 1.0 - np.array(DataStructs.BulkTanimotoSimilarity(fps[i], fps))
    np.fill_diagonal(D, 0.0); Z = linkage(squareform(D, checks=False), method="complete")
    ts = np.linspace(0.0, 1.0, 101); sds = []
    for t in ts:
        lab = fcluster(Z, t, criterion="distance")
        means = {c: y[lab == c].mean() for c in np.unique(lab)}
        sds.append(np.array([means[c] for c in lab]).std())
    return float(1.0 - np.trapz(sds, ts) / (y.std() + 1e-12))


def evaluate(path):
    df = pd.read_csv(path)
    pcol = "y [pEC50/pKi]"
    mols, ys, cliffs = [], [], []
    for _, r in df.iterrows():
        m = Chem.MolFromSmiles(str(r["smiles"]))
        if m is not None and np.isfinite(r[pcol]):
            mols.append(m); ys.append(float(r[pcol])); cliffs.append(int(r.get("cliff_mol", 0)))
    if len(mols) < 60: return {"note": f"too few ({len(mols)})"}
    ys = np.array(ys); X = np.vstack([arr(bit(m)) for m in mols]); FP = [bit(m) for m in mols]
    scaf = np.array([murcko(m) for m in mols], dtype=object); n = len(mols)
    rng = np.random.default_rng(42)

    # ROGI on continuous potency (seeded sample)
    idx = rng.permutation(n)[:min(ROGI_N, n)]
    rg = rogi(ys[idx], [FP[i] for i in idx])

    def gen(novel):
        sp = []
        for seed in SEEDS:
            if novel:
                uniq = np.array(sorted(set(scaf))); perm = np.random.default_rng(seed).permutation(uniq)
                tsc = set(perm[:max(1, int(0.3 * len(uniq)))]); te = np.array([s in tsc for s in scaf])
                tr = np.where(~te)[0]; tec = np.where(te)[0]; trf = [FP[i] for i in tr]
                te_i = np.array([i for i in tec if max(DataStructs.BulkTanimotoSimilarity(FP[i], trf)) < NN_NOVEL], int)
                if len(te_i) < MIN_NOVEL or len(tr) < 20: return None
            else:
                perm = np.random.default_rng(seed).permutation(n); k = max(10, int(0.2 * n))
                tr = perm[k:]; te_i = perm[:k]
            m = HistGradientBoostingRegressor(random_state=42, max_iter=200, learning_rate=0.06, max_depth=6).fit(X[tr], ys[tr])
            pr = m.predict(X[te_i])
            if len(np.unique(ys[te_i])) < 3: continue
            sp.append(spearmanr(pr, ys[te_i]).correlation)
        return round(float(np.nanmean(sp)), 4) if sp else None

    novel_gen = gen(True); rand_gen = gen(False)
    if novel_gen is None:
        return {"note": "insufficient novel-chemistry test compounds", "n": n}
    return {"n": n, "rogi": round(rg, 4), "novel_generalization": novel_gen, "random_generalization": rand_gen,
            "cliff_fraction": round(float(np.mean(cliffs)), 4), "potency_std": round(float(ys.std()), 4)}


def main():
    per = {}
    for path in sorted(glob.glob(os.path.join(MACE, "CHEMBL*.csv"))):
        name = os.path.basename(path).replace(".csv", "")
        s = evaluate(path); per[name] = s
        if "rogi" in s:
            print(f"  {name:18s} n={s['n']:4d} ROGI {s['rogi']:.3f} | novel-gen {s['novel_generalization']} "
                  f"rand-gen {s['random_generalization']} cliff% {s['cliff_fraction']:.3f}")
        else:
            print(f"  {name:18s} SKIP ({s.get('note')})")

    sc = {k: v for k, v in per.items() if "rogi" in v and v.get("novel_generalization") is not None
          and not np.isnan(v["rogi"])}
    rogis = np.array([sc[t]["rogi"] for t in sc])
    novelg = np.array([sc[t]["novel_generalization"] for t in sc])
    randg = np.array([sc[t]["random_generalization"] for t in sc if sc[t]["random_generalization"] is not None])
    cliff = np.array([sc[t]["cliff_fraction"] for t in sc])
    rho_novel, p_novel = spearmanr(rogis, novelg)
    rho_rand, p_rand = spearmanr(np.array([sc[t]["rogi"] for t in sc if sc[t]["random_generalization"] is not None]), randg)
    rho_cliff, p_cliff = spearmanr(cliff, novelg)
    h1 = bool(rho_novel <= -0.5)
    h2 = bool(abs(rho_novel) > abs(rho_rand))

    summary = {"n_targets": len(sc),
               "spearman_rogi_vs_novel_generalization": round(float(rho_novel), 4), "p_novel": round(float(p_novel), 4),
               "spearman_rogi_vs_random_generalization": round(float(rho_rand), 4), "p_random": round(float(p_rand), 4),
               "spearman_cliff_fraction_vs_novel_gen": round(float(rho_cliff), 4),
               "mean_novel_generalization": round(float(novelg.mean()), 4),
               "mean_random_generalization": round(float(randg.mean()), 4),
               "B58_binary_reference_spearman": -0.42,
               "H1_rogi_predicts_novel_generalization": h1, "H2_roughness_matters_more_for_extrapolation": h2,
               "verdict": (
                   f"CONTINUOUS-POTENCY ROUGHNESS PREDICTS NOVEL-CHEMISTRY GENERALIZATION (P7 confirmed with the honest "
                   f"instrument): across {len(sc)} ChEMBL targets, ROGI (on real pKi/pIC50) vs novel-chemistry "
                   f"generalization Spearman {round(float(rho_novel),3)} (p={round(float(p_novel),4)}), "
                   f"{'STRONGER' if abs(rho_novel)>0.42 else 'comparable'} than B58's binary-label -0.42 and "
                   f"{'stronger for extrapolation than interpolation' if h2 else 'similar for random splits'} "
                   f"(random-split {round(float(rho_rand),3)}). So the SAR-roughness mechanism was real but ATTENUATED "
                   f"by binary labels; measured on continuous potency it clearly predicts when a ligand-based model "
                   f"generalizes to novel chemistry. n={len(sc)}; ROGI reimplemented; correlation != causation; not wet-lab."
                   if h1 else
                   f"ROUGHNESS ONLY WEAKLY PREDICTS NOVEL-CHEMISTRY GENERALIZATION even with continuous potency + n="
                   f"{len(sc)} (honest): ROGI vs novel-gen Spearman {round(float(rho_novel),3)} "
                   f"(p={round(float(p_novel),4)}; pre-registered <=-0.5 not met), vs random-split "
                   f"{round(float(rho_rand),3)}. So P7 is GENUINELY WEAK/MULTIFACTORIAL even with the proper instrument "
                   f"— binary labels (B58 -0.42) were not the main limitation. Landscape roughness is a real but "
                   f"partial driver of ligand-based model generalization; other factors dominate. Strong first-class "
                   f"null; n={len(sc)}; not wet-lab."),
               }
    print(f"\nROGI vs novel-gen: {round(float(rho_novel),4)} (p={round(float(p_novel),4)}) | vs random-gen: "
          f"{round(float(rho_rand),4)} | cliff% vs novel-gen: {round(float(rho_cliff),4)}")
    print("VERDICT:", summary["verdict"])

    prov = {"experiment": "B60_continuous_potency_roughness", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "seeds": SEEDS, "nn_novel": NN_NOVEL, "rogi_n": ROGI_N,
            "data": "MoleculeACE 30 ChEMBL targets", "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = {"provenance": prov, "summary": summary, "per_target": per}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "B60_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary, "per_target": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B60_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B60_metrics.json")


def _libvers():
    import rdkit, numpy, scipy, sklearn, pandas
    return {"rdkit": rdkit.__version__, "numpy": numpy.__version__, "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__, "pandas": pandas.__version__}


if __name__ == "__main__":
    main()
