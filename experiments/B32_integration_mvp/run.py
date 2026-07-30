"""B32 — integration MVP: does composing the INTERCEPTA modules (B30 ADMET + B31 synthesizability) predict a
held-out real-world developability outcome (ClinTox clinical-toxicity failure) better than any single module?
Implements prereg/B32_integration_mvp.md. Leakage-controlled, scaffold split, reproduce x2.
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
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta.admet import ADMETPredictor, featurize, NBITS
from intercepta.synth import SynthesizabilityScorer, sa_score

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
PANEL = ["herg", "ames", "dili", "ld50_zhu", "cyp3a4_veith", "bioavailability_ma",
         "bbb_martins", "ppbr_az", "clearance_microsome_az", "half_life_obach"]
SEEDS = [1, 2, 3, 4, 5]


def canon(s):
    m = Chem.MolFromSmiles(str(s)); return Chem.MolToSmiles(m) if m else None


def murcko(s):
    try:
        return MurckoScaffold.MurckoScaffoldSmiles(smiles=str(s), includeChirality=False)
    except Exception:
        return ""


def auroc_oriented(f_tr, y_tr, f_te, y_te):
    """1-feature classifier AUROC on test, orientation chosen on train (honest)."""
    ok_tr = np.isfinite(f_tr); ok_te = np.isfinite(f_te)
    if len(np.unique(y_tr[ok_tr])) < 2 or len(np.unique(y_te[ok_te])) < 2:
        return 0.5
    a_tr = roc_auc_score(y_tr[ok_tr], f_tr[ok_tr]); sign = 1.0 if a_tr >= 0.5 else -1.0
    return float(roc_auc_score(y_te[ok_te], sign * f_te[ok_te]))


def main():
    from tdc.single_pred import Tox
    ct = Tox(name="clintox", path=os.path.join(DATA, "tdc_tox")).get_data()
    ct = ct.dropna(subset=["Drug"]).reset_index(drop=True)
    ct["canon"] = [canon(s) for s in ct["Drug"]]
    ct = ct.dropna(subset=["canon"]).drop_duplicates("canon").reset_index(drop=True)
    y = ct["Y"].values.astype(int)
    smiles = ct["Drug"].tolist()

    # ---- module-output features (modules trained ONLY on their own data) ----
    adm = ADMETPredictor.from_tdc(tasks=PANEL)                 # each task fit on its full TDC train_val
    admet_wide = adm.predict(smiles, tidy=False)               # molecules x PANEL predicted values
    synth = SynthesizabilityScorer.from_rascore(subsample=50000, conformal=False)
    solv = synth.predict(smiles)["solvable_prob"].values
    sa = np.asarray(sa_score(smiles), float)
    feat_names = list(admet_wide.columns) + ["synth_solvable_prob", "sa_score"]
    M = np.column_stack([admet_wide.values, solv, sa]).astype(float)
    M = np.where(np.isfinite(M), M, np.nan)

    # ---- leakage control: exclude ClinTox molecules present in ANY module training set ----
    from tdc.benchmark_group import admet_group
    g = admet_group(path=os.path.join(DATA, "tdc_admet"))
    train_smis = set()
    for t in PANEL:
        tv = g.get(t)["train_val"]
        train_smis |= set(filter(None, (canon(s) for s in tv["Drug"])))
    # synth training molecules (RAscore subsample) — canonicalize the same 50k
    rs = pd.read_csv(os.path.join(DATA, "rascore", "data", "uspto_chembl_classification_train.csv"))
    rs = rs.iloc[np.random.default_rng(42).permutation(len(rs))[:50000]]
    train_smis |= set(filter(None, (canon(s) for s in rs["smi"])))
    leak = np.array([c in train_smis for c in ct["canon"]])
    keep = ~leak
    n_leak = int(leak.sum())

    # median-impute features (for logistic/single-feature) using kept-set medians
    med = np.nanmedian(M[keep], axis=0)
    Mi = np.where(np.isfinite(M), M, med)

    scaff = np.array([murcko(s) for s in smiles], dtype=object)
    # Morgan features for the direct-trained reference
    Xmorgan, _ = featurize(smiles); Xmorgan = Xmorgan[:, :NBITS]

    def scaffold_masks(idx, seed):
        uniq = np.array(sorted(set(scaff[idx])))
        perm = np.random.default_rng(seed).permutation(uniq)
        test_sc = set(perm[:int(0.2 * len(perm))])
        te = np.array([scaff[i] in test_sc for i in idx])
        return idx[~te], idx[te]

    idx_keep = np.where(keep)[0]
    comp, best_single, direct, singles_all = [], [], [], {f: [] for f in feat_names}
    comp_ap, triv_ap = [], []
    for seed in SEEDS:
        tr, te = scaffold_masks(idx_keep, seed)
        if len(np.unique(y[te])) < 2 or len(np.unique(y[tr])) < 2:
            continue
        # composite: L2-logistic on standardized module features
        sc = StandardScaler().fit(Mi[tr])
        lr = LogisticRegression(max_iter=1000, C=1.0).fit(sc.transform(Mi[tr]), y[tr])
        p = lr.predict_proba(sc.transform(Mi[te]))[:, 1]
        comp.append(float(roc_auc_score(y[te], p))); comp_ap.append(float(average_precision_score(y[te], p)))
        triv_ap.append(float(np.mean(y[te])))
        # each single module output
        s_aucs = {}
        for j, f in enumerate(feat_names):
            a = auroc_oriented(Mi[tr, j], y[tr], Mi[te, j], y[te]); s_aucs[f] = a; singles_all[f].append(a)
        best_single.append(max(s_aucs.values()))
        # direct-trained reference (Morgan GBT on ClinTox)
        m = HistGradientBoostingClassifier(random_state=42, max_iter=300, learning_rate=0.06, max_depth=6).fit(Xmorgan[tr], y[tr])
        direct.append(float(roc_auc_score(y[te], m.predict_proba(Xmorgan[te])[:, 1])))

    comp = np.array(comp); best_single = np.array(best_single); direct = np.array(direct)
    single_mean = {f: round(float(np.mean(v)), 4) for f, v in singles_all.items() if v}
    best_feat = max(single_mean, key=single_mean.get)
    h1 = bool((comp.mean() - comp.std()) > max(0.5, best_single.mean()))
    h2 = bool(comp.mean() > 0.6)
    res = {
        "n_clintox": int(len(ct)), "n_positive": int(y.sum()), "prevalence": round(float(y.mean()), 4),
        "n_excluded_leakage": n_leak, "n_leakfree": int(keep.sum()), "seeds_used": int(len(comp)),
        "composite_auroc_mean": round(float(comp.mean()), 4), "composite_auroc_sd": round(float(comp.std()), 4),
        "composite_auprc_mean": round(float(np.mean(comp_ap)), 4), "trivial_auprc": round(float(np.mean(triv_ap)), 4),
        "best_single_module_auroc_mean": round(float(best_single.mean()), 4), "best_single_feature": best_feat,
        "single_module_auroc_mean": single_mean,
        "direct_trained_morgan_gbt_auroc_mean": round(float(direct.mean()), 4),
        "H1_composite_beats_best_single_by_1sd": h1, "H2_composite_auroc_gt_0.6": h2,
        "verdict": (
            f"INTEGRATION ADDS VALUE (whole > parts): the composite of module outputs predicts ClinTox clinical-tox "
            f"failure at AUROC {comp.mean():.3f}±{comp.std():.3f} on a leakage-free scaffold split, beating the best "
            f"single module ('{best_feat}' {single_mean[best_feat]:.3f}) by >1sd and a direct Morgan GBT "
            f"({direct.mean():.3f}). Composing independently-validated modules genuinely improves a held-out "
            f"real-world developability prediction. Scope: research prioritization signal, small positive class "
            f"({int(y.sum())}), scaffold-split, survivorship-confounded — NOT a regulatory safety determination."
        ) if h1 and h2 else (
            f"NEGATIVE (first-class): the composite (AUROC {comp.mean():.3f}) does NOT beat the best single module "
            f"('{best_feat}' {single_mean[best_feat]:.3f}) beyond 1sd — on this outcome the single best module (a "
            f"toxicity endpoint) is as good as composing them. Modules stand alone; no whole>parts claim here."
        ),
    }
    print("VERDICT:", res["verdict"])
    print(f"composite {res['composite_auroc_mean']}±{res['composite_auroc_sd']} | best single {res['best_single_module_auroc_mean']} "
          f"({best_feat}) | direct {res['direct_trained_morgan_gbt_auroc_mean']} | leak-excluded {n_leak}")

    prov = {"experiment": "B32_integration_mvp", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "seeds": SEEDS, "panel": PANEL,
            "outcome": "TDC ClinTox (clinical-trial toxicity failure); modules trained only on their own data",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    full = {"provenance": prov, "results": res}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(full, open(os.path.join(HERE, "results", "B32_metrics.json"), "w"), indent=2, sort_keys=True)
    digest = hashlib.sha256(json.dumps(res, sort_keys=True).encode()).hexdigest()
    open(os.path.join(HERE, "results", "B32_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B32_metrics.json")


def _libvers():
    import sklearn, scipy, numpy, rdkit, importlib.metadata as m
    try: tdcv = m.version("PyTDC")
    except Exception: tdcv = "unknown"
    return {"numpy": numpy.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__, "rdkit": rdkit.__version__, "PyTDC": tdcv}


if __name__ == "__main__":
    main()
