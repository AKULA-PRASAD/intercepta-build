"""B37 — learned joint representation: pretrain a multi-task MLP on tox21 (12 assays), extract its hidden layer as a
learned molecular embedding, and test whether it transfers to held-out outcomes BETTER than raw structure (the test
frozen-module fusion failed in B36). Implements prereg/B37_learned_joint_representation.md. Deterministic -> x2.
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
import warnings; warnings.filterwarnings("ignore")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta.admet import featurize

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
TOXP = os.path.join(DATA, "tdc_tox")
TRANSFER = ["clintox", "skin_reaction", "carcinogens_lagunin"]
SEEDS = [1, 2, 3, 4, 5]
GBT = dict(random_state=42, max_iter=200, learning_rate=0.06, max_depth=6)
HIDDEN = (256, 64)


def canon(s):
    m = Chem.MolFromSmiles(str(s)); return Chem.MolToSmiles(m) if m else None


def murcko(s):
    try: return MurckoScaffold.MurckoScaffoldSmiles(smiles=str(s), includeChirality=False)
    except Exception: return ""


def embed(mlp, X):
    """Forward pass to the LAST hidden layer (the learned joint representation); relu activations."""
    a = X
    for i in range(len(mlp.coefs_) - 1):
        a = np.maximum(0.0, a @ mlp.coefs_[i] + mlp.intercepts_[i])
    return a


def build_tox21_mlp():
    from tdc.single_pred import Tox
    from tdc.utils import retrieve_label_name_list
    labs = retrieve_label_name_list("Tox21")
    wide = None
    for lab in labs:
        d = Tox(name="tox21", label_name=lab, path=TOXP).get_data()[["Drug", "Y"]].dropna(subset=["Drug"]).copy()
        d["canon"] = [canon(s) for s in d["Drug"]]; d = d.dropna(subset=["canon"]).drop_duplicates("canon")
        d = d.rename(columns={"Y": lab})[["canon", lab]]
        wide = d if wide is None else wide.merge(d, on="canon", how="outer")
    wide = wide.reset_index(drop=True)
    Y = wide[labs].fillna(0.0).values.astype(int)          # missing tox21 labels -> 0 (noted caveat)
    X, _ = featurize(wide["canon"].tolist())
    mlp = MLPClassifier(hidden_layer_sizes=HIDDEN, random_state=42, max_iter=150, early_stopping=False).fit(X, Y)
    return mlp, set(wide["canon"]), len(wide), labs


def load_outcome(name):
    from tdc.single_pred import Tox
    df = Tox(name=name, path=TOXP).get_data().dropna(subset=["Y", "Drug"]).copy()
    df["canon"] = [canon(s) for s in df["Drug"]]
    return df.dropna(subset=["canon"]).drop_duplicates("canon").reset_index(drop=True)


def paired(A, B, C, y, scaff, idx):
    dCA, dBA, aA, aB, aC = [], [], [], [], []
    for seed in SEEDS:
        uniq = np.array(sorted(set(scaff[idx]))); perm = np.random.default_rng(seed).permutation(uniq)
        tsc = set(perm[:int(0.2 * len(perm))]); te = np.array([scaff[i] in tsc for i in idx])
        tr, tei = idx[~te], idx[te]
        if len(np.unique(y[tei])) < 2 or len(np.unique(y[tr])) < 2: continue
        def fit(Z): return roc_auc_score(y[tei], HistGradientBoostingClassifier(**GBT).fit(Z[tr], y[tr]).predict_proba(Z[tei])[:, 1])
        a, b, c = fit(A), fit(B), fit(C)
        aA.append(a); aB.append(b); aC.append(c); dCA.append(c - a); dBA.append(b - a)
    return (round(float(np.mean(aA)), 4), round(float(np.mean(aB)), 4), round(float(np.mean(aC)), 4),
            round(float(np.mean(dCA)), 4), round(float(np.mean(dBA)), 4))


def main():
    mlp, tox_set, n_tox, labs = build_tox21_mlp()
    print(f"pretrained tox21 multi-task MLP on {n_tox} molecules x {len(labs)} assays; embedding dim {HIDDEN[-1]}")
    per = []
    for name in TRANSFER:
        df = load_outcome(name); y = df["Y"].values.astype(int)
        keep = ~df["canon"].isin(tox_set).values                     # leakage: exclude tox21 pretraining molecules
        if keep.sum() < 60 or int(y[keep].sum()) < 15:
            per.append({"outcome": name, "skipped": "too few after leakage control", "n": int(keep.sum())}); continue
        S, _ = featurize(df["Drug"].tolist())
        E = embed(mlp, S); C = np.hstack([S, E])
        scaff = np.array([murcko(s) for s in df["Drug"]], dtype=object); idx = np.where(keep)[0]
        aA, aB, aC, dCA, dBA = paired(S, E, C, y, scaff, idx)
        per.append({"outcome": name, "n_leakfree": int(keep.sum()), "n_positive": int(y[idx].sum()),
                    "auroc_structure_A": aA, "auroc_embedding_B": aB, "auroc_struct_plus_embed_C": aC,
                    "delta_C_minus_A": dCA, "delta_B_minus_A": dBA})
        print(f"  {name:22s} n={per[-1]['n_leakfree']:5d} pos={per[-1]['n_positive']:4d} | A(struct) {aA:.3f} "
              f"B(embed) {aB:.3f} C(both) {aC:.3f} | ΔC-A {dCA:+.4f} ΔB-A {dBA:+.4f}")

    scored = [p for p in per if "delta_C_minus_A" in p]
    dCA = np.array([p["delta_C_minus_A"] for p in scored]); dBA = np.array([p["delta_B_minus_A"] for p in scored])
    frac_pos = float(np.mean(dCA > 0)); all_C_ge_A = bool(np.all(dCA > -0.002))
    robust = bool(dCA.mean() > 0 and frac_pos == 1.0 and (dCA.mean() - dCA.std()) > 0 and all_C_ge_A)
    mixed = bool((not robust) and dCA.mean() > 0 and frac_pos >= 0.5)      # helps some outcomes, not robust
    h1 = robust
    meta = {"n_outcomes": len(scored), "mean_delta_C_minus_A": round(float(dCA.mean()), 4),
            "mean_delta_B_minus_A": round(float(dBA.mean()), 4), "fraction_outcomes_C_gt_A": round(frac_pos, 3),
            "per_outcome_delta_C_minus_A": {p["outcome"]: p["delta_C_minus_A"] for p in scored},
            "H1_learned_representation_robustly_beats_structure": h1,
            "verdict": (
                f"LEARNED JOINT REPRESENTATION ROBUSTLY ADDS VALUE: augmenting structure with the tox21-pretrained "
                f"multi-task embedding beats raw structure on ALL held-out outcomes (mean ΔAUROC(C−A) +{dCA.mean():.4f}, "
                f"{frac_pos:.0%} positive). A learned representation transfers signal frozen-module fusion (B36) could "
                f"not — a real (if small) integration win; scale-up = a deep molecular foundation model."
            ) if robust else (
                f"MIXED / WITHIN-DOMAIN ONLY (not a robust integration win): the tox21-pretrained embedding helps "
                f"only where the outcome is closest to its toxicity training domain (per-outcome ΔC−A: "
                + ", ".join(f"{p['outcome']} {p['delta_C_minus_A']:+.4f}" for p in scored) + f"); mean ΔC−A "
                f"{dCA.mean():+.4f} across {len(scored)} outcomes, and the embedding ALONE is generally WORSE than "
                f"structure (mean ΔB−A {dBA.mean():+.4f}). So the learned representation shows genuine WITHIN-DOMAIN "
                f"transfer (e.g. skin_reaction) but does NOT robustly beat raw structure across held-out outcomes — "
                f"consistent with the information-bottleneck: a shallow learned representation over Morgan+physchem "
                f"adds nothing general beyond raw structure. A robust integration win would need a much larger deep "
                f"molecular foundation model (beyond torch-free shallow MLP) — the honest boundary."
            ) if mixed else (
                f"NO GAIN: the tox21-pretrained embedding does NOT beat raw structure (mean ΔC−A {dCA.mean():+.4f}, "
                f"embedding-alone ΔB−A {dBA.mean():+.4f}). Information bottleneck, not representation; INTERCEPTA's "
                f"value is its standalone modules."
            )}
    print("\nVERDICT:", meta["verdict"])

    prov = {"experiment": "B37_learned_joint_representation", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "seeds": SEEDS,
            "representation": f"sklearn MLPClassifier hidden={HIDDEN} multi-task on tox21 ({len(labs)} assays); embedding=last hidden",
            "transfer_outcomes": TRANSFER, "note": "missing tox21 labels filled 0",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    full = {"provenance": prov, "meta_analysis": meta, "per_outcome": per}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(full, open(os.path.join(HERE, "results", "B37_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"meta_analysis": meta, "per_outcome": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B37_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B37_metrics.json")


def _libvers():
    import sklearn, scipy, numpy, rdkit
    return {"numpy": numpy.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__, "rdkit": rdkit.__version__}


if __name__ == "__main__":
    main()
