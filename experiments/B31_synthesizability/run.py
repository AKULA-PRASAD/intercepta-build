"""B31 — synthesizability module: predict AiZynthFinder retrosynthetic SOLVABILITY from structure. Implements
prereg/B31_synthesizability.md. Unified featurizer with ADMET (Morgan2048+physchem), HGB classifier, vs trivial +
oriented-SAscore baselines, on RAscore's original random split AND a Bemis-Murcko scaffold split. Deterministic ->
reproduce x2 byte-identical (payload; provenance timestamp/git_sha aside).
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
import warnings; warnings.filterwarnings("ignore")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta.admet import featurize

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
RASCORE = os.path.join(DATA, "rascore", "data")
SUBSAMPLE_TRAIN = 50000
SCAFFOLD_SEEDS = [1, 2, 3]
GBT = dict(random_state=42, max_iter=300, learning_rate=0.06, max_depth=6)


def load():
    tr = pd.read_csv(os.path.join(RASCORE, "uspto_chembl_classification_train.csv"))
    te = pd.read_csv(os.path.join(RASCORE, "uspto_chembl_classification_test.csv"))
    tr = tr.iloc[np.random.default_rng(42).permutation(len(tr))[:SUBSAMPLE_TRAIN]].reset_index(drop=True)
    return tr[["smi", "activity"]], te[["smi", "activity"]]


_FCACHE = {}
def feat(smiles):
    todo = [s for s in smiles if s not in _FCACHE]
    if todo:
        X, _ = featurize(todo)
        for s, r in zip(todo, X):
            _FCACHE[s] = r
    return np.vstack([_FCACHE[s] for s in smiles]).astype(np.float32)


def sa_scores(smiles):
    """RDKit Contrib SAscore (Ertl & Schuffenhauer; higher = harder to make). No download; deterministic.
    Oriented classifier score = -SA (higher = more solvable)."""
    import os
    from rdkit.Chem import RDConfig
    sys.path.append(os.path.join(RDConfig.RDContribDir, "SA_Score"))
    import sascorer
    from rdkit import Chem
    out = []
    for s in smiles:
        try:
            m = Chem.MolFromSmiles(str(s))
            out.append(float(sascorer.calculateScore(m)) if m is not None else np.nan)
        except Exception:
            out.append(np.nan)
    return np.array(out)


def murcko(smiles):
    from rdkit import Chem
    from rdkit.Chem.Scaffolds import MurckoScaffold
    scs = []
    for s in smiles:
        try:
            scs.append(MurckoScaffold.MurckoScaffoldSmiles(smiles=str(s), includeChirality=False))
        except Exception:
            scs.append("")
    return np.array(scs, dtype=object)


def evaluate(Xtr, ytr, Xte, yte, sate):
    """Fit HGB; return model + baseline metrics on the test fold."""
    m = HistGradientBoostingClassifier(**GBT).fit(Xtr, ytr)
    p = m.predict_proba(Xte)[:, 1]
    res = {"model_auroc": float(roc_auc_score(yte, p)), "model_auprc": float(average_precision_score(yte, p)),
           "trivial_auroc": 0.5, "trivial_auprc": float(np.mean(yte))}
    ok = np.isfinite(sate)
    if ok.sum() > 10 and len(np.unique(yte[ok])) == 2:
        res["sa_auroc"] = float(roc_auc_score(yte[ok], -sate[ok]))          # oriented: higher -SA = more solvable
        res["sa_auprc"] = float(average_precision_score(yte[ok], -sate[ok]))
    else:
        res["sa_auroc"] = res["sa_auprc"] = None
    return res


def main():
    tr, te = load()
    pool = pd.concat([tr, te], ignore_index=True)
    Xpool = feat(pool["smi"].tolist())
    sapool = sa_scores(pool["smi"].tolist())
    ntr = len(tr)
    Xtr, ytr = Xpool[:ntr], tr["activity"].values.astype(int)
    Xte, yte = Xpool[ntr:], te["activity"].values.astype(int)
    sate = sapool[ntr:]

    # ---- Arm 1: original random split (comparable to published RAscore) ----
    random_arm = evaluate(Xtr, ytr, Xte, yte, sate)
    print(f"[random ]  model AUROC {random_arm['model_auroc']:.3f} AUPRC {random_arm['model_auprc']:.3f} | "
          f"SA AUROC {random_arm['sa_auroc']:.3f} | base rate {random_arm['trivial_auprc']:.3f}")

    # ---- Arm 2: Bemis-Murcko scaffold split (novel-chemistry generalization) ----
    scaff = murcko(pool["smi"].tolist())
    y_all = pool["activity"].values.astype(int)
    uniq = np.array(sorted(set(scaff)))
    sc_auroc, sc_auprc, sc_sa = [], [], []
    for seed in SCAFFOLD_SEEDS:
        perm = np.random.default_rng(seed).permutation(uniq)
        n_test_sc = int(0.2 * len(perm))
        test_scaffolds = set(perm[:n_test_sc])
        te_mask = np.array([s in test_scaffolds for s in scaff])
        r = evaluate(Xpool[~te_mask], y_all[~te_mask], Xpool[te_mask], y_all[te_mask], sapool[te_mask])
        sc_auroc.append(r["model_auroc"]); sc_auprc.append(r["model_auprc"]); sc_sa.append(r["sa_auroc"])
    scaffold_arm = {"model_auroc_mean": float(np.mean(sc_auroc)), "model_auroc_sd": float(np.std(sc_auroc)),
                    "model_auprc_mean": float(np.mean(sc_auprc)), "model_auprc_sd": float(np.std(sc_auprc)),
                    "sa_auroc_mean": float(np.mean([x for x in sc_sa if x is not None])),
                    "n_unique_scaffolds": int(len(uniq)), "seeds": SCAFFOLD_SEEDS}
    print(f"[scaffold] model AUROC {scaffold_arm['model_auroc_mean']:.3f}±{scaffold_arm['model_auroc_sd']:.3f} "
          f"AUPRC {scaffold_arm['model_auprc_mean']:.3f} | SA AUROC {scaffold_arm['sa_auroc_mean']:.3f}")

    # ---- honest verdict ----
    sota = {"RAscore_XGB_auroc": 0.95, "RAscore_DNN_auroc": 0.93, "SAscore_oriented_auroc_ref": 0.85,
            "note": "published RAscore ChEMBL test (Thakkar et al. Chem Sci 2021), random split; retrieved 2026-07-29"}
    h1_random = random_arm["model_auroc"] > max(0.5, random_arm["sa_auroc"] or 0)
    h1_scaffold = scaffold_arm["model_auroc_mean"] - scaffold_arm["model_auroc_sd"] > max(0.5, scaffold_arm["sa_auroc_mean"])
    gap = random_arm["model_auroc"] - scaffold_arm["model_auroc_mean"]
    summary = {
        "H1_random_beats_trivial_and_SA": bool(h1_random),
        "H1_scaffold_beats_trivial_and_SA_by_1sd": bool(h1_scaffold),
        "H2_generalization_gap_auroc": round(float(gap), 4),
        "H3_random_vs_published_RAscore_gap": round(float(0.95 - random_arm["model_auroc"]), 4),
        "verdict": (
            f"VALIDATED synthesizability screening filter: structure-only GBT predicts AiZynthFinder solvability at "
            f"AUROC {random_arm['model_auroc']:.3f} (random split; published RAscore 0.93-0.95, same model family) and "
            f"{scaffold_arm['model_auroc_mean']:.3f} on a scaffold split (novel chemistry) — beating trivial (0.5) and "
            f"the oriented-SAscore heuristic on both. Honest generalization gap random->scaffold = {gap:.3f}. Scope: "
            "algorithmic retrosynthetic solvability (USPTO templates), a computational proxy, NOT a lab guarantee."
        ) if (h1_random and h1_scaffold) else
        ("NEGATIVE: learned solvability does not beat the SAscore heuristic beyond noise — structure adds little here. "
         "See per-arm numbers."),
    }
    print("\nVERDICT:", summary["verdict"])

    prov = {"experiment": "B31_synthesizability", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(),
            "data": "RAscore uspto_chembl_classification (179413 train / 19935 test; subsample_train=%d)" % SUBSAMPLE_TRAIN,
            "features": "Morgan/ECFP4 2048-bit + 17 RDKit physchem (unified with admet)",
            "model": "HistGradientBoostingClassifier seed=42 max_iter=300 lr=0.06 max_depth=6",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    full = {"provenance": prov, "summary": summary, "sota_reference": sota,
            "random_split": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in random_arm.items()},
            "scaffold_split": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in scaffold_arm.items()}}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(full, open(os.path.join(HERE, "results", "B31_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({k: full[k] for k in ("summary", "sota_reference", "random_split", "scaffold_split")}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B31_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B31_metrics.json")


def _libvers():
    import sklearn, scipy, numpy, rdkit, importlib.metadata as m
    try: tdcv = m.version("PyTDC")
    except Exception: tdcv = "unknown"
    return {"numpy": numpy.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__, "rdkit": rdkit.__version__, "PyTDC": tdcv}


if __name__ == "__main__":
    main()
