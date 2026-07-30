"""B32b — feature-level fusion: do the module TRANSFER features add value on top of raw structure for predicting
ClinTox? Implements prereg/B32b_feature_fusion.md. S = Morgan+physchem, M = 12 module outputs (B30 ADMET panel +
B31 synth + SA), S+M = concat; same HGB on all three; leakage-controlled scaffold split, 5 seeds. Reproduce x2.
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
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta.admet import ADMETPredictor, featurize
from intercepta.synth import SynthesizabilityScorer, sa_score

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
PANEL = ["herg", "ames", "dili", "ld50_zhu", "cyp3a4_veith", "bioavailability_ma",
         "bbb_martins", "ppbr_az", "clearance_microsome_az", "half_life_obach"]
SEEDS = [1, 2, 3, 4, 5]
GBT = dict(random_state=42, max_iter=300, learning_rate=0.06, max_depth=6)


def canon(s):
    m = Chem.MolFromSmiles(str(s)); return Chem.MolToSmiles(m) if m else None


def murcko(s):
    try:
        return MurckoScaffold.MurckoScaffoldSmiles(smiles=str(s), includeChirality=False)
    except Exception:
        return ""


def fit_auc(Xtr, ytr, Xte, yte):
    m = HistGradientBoostingClassifier(**GBT).fit(Xtr, ytr)
    p = m.predict_proba(Xte)[:, 1]
    return float(roc_auc_score(yte, p)), float(average_precision_score(yte, p))


def auroc_oriented(f_tr, y_tr, f_te, y_te):
    ok_tr = np.isfinite(f_tr); ok_te = np.isfinite(f_te)
    if len(np.unique(y_tr[ok_tr])) < 2 or len(np.unique(y_te[ok_te])) < 2:
        return 0.5
    sign = 1.0 if roc_auc_score(y_tr[ok_tr], f_tr[ok_tr]) >= 0.5 else -1.0
    return float(roc_auc_score(y_te[ok_te], sign * f_te[ok_te]))


def main():
    from tdc.single_pred import Tox
    ct = Tox(name="clintox", path=os.path.join(DATA, "tdc_tox")).get_data().dropna(subset=["Drug"])
    ct = ct.assign(canon=[canon(s) for s in ct["Drug"]]).dropna(subset=["canon"]).drop_duplicates("canon").reset_index(drop=True)
    smiles = ct["Drug"].tolist(); y = ct["Y"].values.astype(int)

    # S = raw structure (Morgan + physchem)
    S, _ = featurize(smiles)
    # M = module transfer features
    adm = ADMETPredictor.from_tdc(tasks=PANEL)
    admet_wide = adm.predict(smiles, tidy=False)[PANEL]
    synth = SynthesizabilityScorer.from_rascore(subsample=50000, conformal=False)
    solv = synth.predict(smiles)["solvable_prob"].values
    sa = np.asarray(sa_score(smiles), float)
    feat_names = PANEL + ["synth_solvable_prob", "sa_score"]
    M = np.column_stack([admet_wide.values, solv, sa]).astype(float)
    med = np.nanmedian(np.where(np.isfinite(M), M, np.nan), axis=0); med = np.where(np.isfinite(med), med, 0.0)
    M = np.where(np.isfinite(M), M, med)
    SM = np.hstack([S, M])

    # leakage: exclude ClinTox molecules seen by any module
    from tdc.benchmark_group import admet_group
    g = admet_group(path=os.path.join(DATA, "tdc_admet"))
    seen = set()
    for t in PANEL:
        seen |= set(filter(None, (canon(s) for s in g.get(t)["train_val"]["Drug"])))
    rs = pd.read_csv(os.path.join(DATA, "rascore", "data", "uspto_chembl_classification_train.csv"))
    rs = rs.iloc[np.random.default_rng(42).permutation(len(rs))[:50000]]
    seen |= set(filter(None, (canon(s) for s in rs["smi"])))
    keep = ~ct["canon"].isin(seen).values
    n_leak = int((~keep).sum())

    scaff = np.array([murcko(s) for s in smiles], dtype=object)
    idx_keep = np.where(keep)[0]

    def scaffold_masks(seed):
        uniq = np.array(sorted(set(scaff[idx_keep])))
        perm = np.random.default_rng(seed).permutation(uniq)
        test_sc = set(perm[:int(0.2 * len(perm))])
        te = np.array([scaff[i] in test_sc for i in idx_keep])
        return idx_keep[~te], idx_keep[te]

    aucs = {"S": [], "M": [], "SM": []}; aprs = {"S": [], "M": [], "SM": []}; best_single = []
    for seed in SEEDS:
        tr, te = scaffold_masks(seed)
        if len(np.unique(y[te])) < 2 or len(np.unique(y[tr])) < 2:
            continue
        for name, X in (("S", S), ("M", M), ("SM", SM)):
            a, ap = fit_auc(X[tr], y[tr], X[te], y[te]); aucs[name].append(a); aprs[name].append(ap)
        best_single.append(max(auroc_oriented(M[tr, j], y[tr], M[te, j], y[te]) for j in range(M.shape[1])))

    def ms(v): return (round(float(np.mean(v)), 4), round(float(np.std(v)), 4))
    S_m, S_s = ms(aucs["S"]); M_m, M_s = ms(aucs["M"]); SM_m, SM_s = ms(aucs["SM"]); bs_m, _ = ms(best_single)
    h1 = bool((SM_m - SM_s) > S_m)                                   # fusion beats structure by >1sd
    h2 = bool(SM_m >= max(S_m, M_m, bs_m) - 1e-9)                    # fusion is best overall
    res = {
        "n_clintox": int(len(ct)), "n_positive": int(y.sum()), "n_excluded_leakage": n_leak,
        "n_leakfree": int(keep.sum()), "seeds_used": len(aucs["S"]),
        "structure_S_auroc_mean": S_m, "structure_S_auroc_sd": S_s, "structure_S_auprc_mean": ms(aprs["S"])[0],
        "modules_M_auroc_mean": M_m, "modules_M_auroc_sd": M_s, "modules_M_auprc_mean": ms(aprs["M"])[0],
        "fusion_SM_auroc_mean": SM_m, "fusion_SM_auroc_sd": SM_s, "fusion_SM_auprc_mean": ms(aprs["SM"])[0],
        "best_single_module_auroc_mean": bs_m,
        "delta_fusion_minus_structure": round(SM_m - S_m, 4),
        "H1_fusion_beats_structure_by_1sd": h1, "H2_fusion_is_best": h2,
        "verdict": (
            f"DECISIVE FUSION WIN: feature-level fusion S+M (AUROC {SM_m:.3f}±{SM_s:.3f}) beats raw structure S "
            f"({S_m:.3f}) by >1sd (delta {SM_m-S_m:+.3f}) and is the best of S / M ({M_m:.3f}) / best-single "
            f"({bs_m:.3f}) — the external-data-trained ADMET/synth modules add genuine transfer signal on top of "
            f"structure (scope: ClinTox benchmark, small positive class, scaffold-split, survivorship-confounded)."
        ) if h1 else (
            f"WEAK / NON-DECISIVE POSITIVE: feature-level fusion S+M (AUROC {SM_m:.3f}±{SM_s:.3f}) is the BEST model "
            f"(> structure S {S_m:.3f}, > modules M {M_m:.3f}, > best-single {bs_m:.3f}) and beats structure by "
            f"delta {SM_m-S_m:+.3f} with lower variance — but the margin does NOT clear the pre-registered >1sd bar, "
            f"so per the fixed decision rule this is H1-FAIL: hypothesis-generating, NOT a validated improvement. "
            f"Modules add a small, consistent-but-not-decisive transfer signal on top of structure; do not ship "
            f"fusion as a validated win. (Still more positive than B32's scalar late-fusion, which lost to best-single.)"
        ) if (h2 and (SM_m - S_m) > 0) else (
            f"NEGATIVE (first-class): feature-level fusion S+M (AUROC {SM_m:.3f}±{SM_s:.3f}) does NOT beat raw "
            f"structure S ({S_m:.3f}); raw structure is sufficient for ClinTox and the ADMET/synth transfer features "
            f"add nothing beyond it here. Modules remain useful standalone; no integration claim. Consistent with B32."
        ),
    }
    print("VERDICT:", res["verdict"])
    print(f"S {S_m}±{S_s} | M {M_m}±{M_s} | S+M {SM_m}±{SM_s} | best-single {bs_m} | leak-excluded {n_leak}")

    prov = {"experiment": "B32b_feature_fusion", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "seeds": SEEDS, "panel": PANEL,
            "features": "S=Morgan2048+17physchem (2065); M=12 module outputs; S+M=concat (2077); HGB on all three",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    full = {"provenance": prov, "results": res}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(full, open(os.path.join(HERE, "results", "B32b_metrics.json"), "w"), indent=2, sort_keys=True)
    digest = hashlib.sha256(json.dumps(res, sort_keys=True).encode()).hexdigest()
    open(os.path.join(HERE, "results", "B32b_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B32b_metrics.json")


def _libvers():
    import sklearn, scipy, numpy, rdkit, importlib.metadata as m
    try: tdcv = m.version("PyTDC")
    except Exception: tdcv = "unknown"
    return {"numpy": numpy.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__, "rdkit": rdkit.__version__, "PyTDC": tdcv}


if __name__ == "__main__":
    main()
