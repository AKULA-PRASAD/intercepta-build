"""B35 — rigorous PAIRED re-adjudication of feature-level integration (S+M vs S) on ClinTox. Fixes B32b's unpaired
">1sd" bar with per-seed paired deltas (Wilcoxon + bootstrap CI) and a pooled out-of-fold paired bootstrap on the
same data. Implements prereg/B35_integration_paired.md. Deterministic -> reproduce x2.
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
from scipy import stats
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta.admet import ADMETPredictor, featurize
from intercepta.synth import SynthesizabilityScorer, sa_score

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
PANEL = ["herg", "ames", "dili", "ld50_zhu", "cyp3a4_veith", "bioavailability_ma",
         "bbb_martins", "ppbr_az", "clearance_microsome_az", "half_life_obach"]
SEEDS = list(range(1, 11))                       # 10 scaffold-split seeds (higher power)
GBT = dict(random_state=42, max_iter=300, learning_rate=0.06, max_depth=6)


def canon(s):
    m = Chem.MolFromSmiles(str(s)); return Chem.MolToSmiles(m) if m else None


def murcko(s):
    try: return MurckoScaffold.MurckoScaffoldSmiles(smiles=str(s), includeChirality=False)
    except Exception: return ""


def build_features():
    from tdc.single_pred import Tox
    ct = Tox(name="clintox", path=os.path.join(DATA, "tdc_tox")).get_data().dropna(subset=["Drug"])
    ct = ct.assign(canon=[canon(s) for s in ct["Drug"]]).dropna(subset=["canon"]).drop_duplicates("canon").reset_index(drop=True)
    smiles = ct["Drug"].tolist(); y = ct["Y"].values.astype(int)
    S, _ = featurize(smiles)
    adm = ADMETPredictor.from_tdc(tasks=PANEL); admet_wide = adm.predict(smiles, tidy=False)[PANEL]
    synth = SynthesizabilityScorer.from_rascore(subsample=50000, conformal=False)
    solv = synth.predict(smiles)["solvable_prob"].values
    sa = np.asarray(sa_score(smiles), float)
    M = np.column_stack([admet_wide.values, solv, sa]).astype(float)
    med = np.nanmedian(np.where(np.isfinite(M), M, np.nan), axis=0); med = np.where(np.isfinite(med), med, 0.0)
    M = np.where(np.isfinite(M), M, med)
    # leakage exclusion
    from tdc.benchmark_group import admet_group
    g = admet_group(path=os.path.join(DATA, "tdc_admet")); seen = set()
    for t in PANEL:
        seen |= set(filter(None, (canon(s) for s in g.get(t)["train_val"]["Drug"])))
    rs = pd.read_csv(os.path.join(DATA, "rascore", "data", "uspto_chembl_classification_train.csv"))
    rs = rs.iloc[np.random.default_rng(42).permutation(len(rs))[:50000]]
    seen |= set(filter(None, (canon(s) for s in rs["smi"])))
    keep = ~ct["canon"].isin(seen).values
    scaff = np.array([murcko(s) for s in smiles], dtype=object)
    return S, M, np.hstack([S, M]), y, scaff, keep


def scaffold_split(scaff, idx, seed):
    uniq = np.array(sorted(set(scaff[idx])))
    perm = np.random.default_rng(seed).permutation(uniq)
    test_sc = set(perm[:int(0.2 * len(perm))])
    te = np.array([scaff[i] in test_sc for i in idx])
    return idx[~te], idx[te]


def auroc_fit(Xtr, ytr, Xte, yte):
    m = HistGradientBoostingClassifier(**GBT).fit(Xtr, ytr)
    return m.predict_proba(Xte)[:, 1]


def main():
    S, M, SM, y, scaff, keep = build_features()
    idx = np.where(keep)[0]

    # ---- Part A: per-seed paired deltas (S+M vs S) ----
    auc_S, auc_SM, deltas = [], [], []
    for seed in SEEDS:
        tr, te = scaffold_split(scaff, idx, seed)
        if len(np.unique(y[te])) < 2 or len(np.unique(y[tr])) < 2:
            continue
        pS = auroc_fit(S[tr], y[tr], S[te], y[te]); aS = roc_auc_score(y[te], pS)
        pSM = auroc_fit(SM[tr], y[tr], SM[te], y[te]); aSM = roc_auc_score(y[te], pSM)
        auc_S.append(aS); auc_SM.append(aSM); deltas.append(aSM - aS)
    deltas = np.array(deltas)
    wilcox_p = float(stats.wilcoxon(deltas, alternative="greater")[1]) if len(deltas) >= 6 and np.any(deltas != 0) else float("nan")
    rng = np.random.default_rng(42)
    boot = np.array([rng.choice(deltas, len(deltas), replace=True).mean() for _ in range(5000)])
    ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])

    # ---- Part B: pooled out-of-fold paired bootstrap (same data), fixed 5-fold scaffold partition (seed 0) ----
    uniq = np.array(sorted(set(scaff[idx]))); perm = np.random.default_rng(0).permutation(uniq)
    folds = {s: i % 5 for i, s in enumerate(perm)}
    oof_S = np.full(len(idx), np.nan); oof_SM = np.full(len(idx), np.nan)
    fold_of = np.array([folds[scaff[i]] for i in idx])
    for f in range(5):
        te = fold_of == f; tr = ~te
        if len(np.unique(y[idx[tr]])) < 2:
            continue
        oof_S[te] = auroc_fit(S[idx[tr]], y[idx[tr]], S[idx[te]], y[idx[te]])
        oof_SM[te] = auroc_fit(SM[idx[tr]], y[idx[tr]], SM[idx[te]], y[idx[te]])
    yv = y[idx]; ok = np.isfinite(oof_S) & np.isfinite(oof_SM)
    aS_oof = float(roc_auc_score(yv[ok], oof_S[ok])); aSM_oof = float(roc_auc_score(yv[ok], oof_SM[ok]))
    rng2 = np.random.default_rng(7); n = int(ok.sum()); yv_ok = yv[ok]; s_ok = oof_S[ok]; sm_ok = oof_SM[ok]
    bdelta = []
    for _ in range(5000):
        b = rng2.integers(0, n, n)
        if len(np.unique(yv_ok[b])) < 2:
            continue
        bdelta.append(roc_auc_score(yv_ok[b], sm_ok[b]) - roc_auc_score(yv_ok[b], s_ok[b]))
    bdelta = np.array(bdelta)
    oof_ci_lo, oof_ci_hi = np.percentile(bdelta, [2.5, 97.5])
    oof_p = float((bdelta <= 0).mean())                    # one-sided bootstrap p (delta <= 0)

    frac_pos = float(np.mean(deltas > 0))
    h1 = bool(frac_pos >= 0.8 and np.isfinite(wilcox_p) and wilcox_p < 0.05 and ci_lo > 0 and oof_ci_lo > 0 and oof_p < 0.05)
    res = {
        "n_leakfree": int(keep.sum()), "n_positive": int(y[idx].sum()), "seeds": len(deltas),
        "auroc_S_mean": round(float(np.mean(auc_S)), 4), "auroc_SM_mean": round(float(np.mean(auc_SM)), 4),
        "paired_delta_mean": round(float(deltas.mean()), 4), "paired_delta_all": [round(float(d), 4) for d in deltas],
        "fraction_seeds_delta_positive": round(frac_pos, 3),
        "wilcoxon_onesided_p": round(wilcox_p, 5),
        "bootstrap_delta_CI95": [round(float(ci_lo), 4), round(float(ci_hi), 4)],
        "pooled_oof_auroc_S": round(aS_oof, 4), "pooled_oof_auroc_SM": round(aSM_oof, 4),
        "pooled_oof_delta": round(aSM_oof - aS_oof, 4),
        "pooled_oof_bootstrap_delta_CI95": [round(float(oof_ci_lo), 4), round(float(oof_ci_hi), 4)],
        "pooled_oof_onesided_p": round(oof_p, 5),
        "H1_feature_fusion_beats_structure_paired": h1,
        "verdict": (
            f"VALIDATED (SMALL) INTEGRATION WIN: under the correct PAIRED test, feature-level fusion S+M beats raw "
            f"structure S — mean paired ΔAUROC +{deltas.mean():.4f} ({frac_pos:.0%} of {len(deltas)} seeds positive, "
            f"Wilcoxon p={wilcox_p:.4f}, bootstrap 95% CI [{ci_lo:.4f},{ci_hi:.4f}]); pooled out-of-fold AUROC "
            f"{aSM_oof:.3f} vs {aS_oof:.3f} (Δ+{aSM_oof-aS_oof:.4f}, bootstrap CI [{oof_ci_lo:.4f},{oof_ci_hi:.4f}], "
            f"p={oof_p:.4f}). The external-data-trained ADMET/synth modules add a REAL but SMALL orthogonal signal on "
            f"top of structure. HONEST: effect size is small (~+0.01 AUROC), single outcome (ClinTox), survivorship-"
            f"confounded — a statistically-real modest platform benefit, NOT a large advantage."
        ) if h1 else (
            f"STRUCTURE SUFFICIENT (integration not established): paired ΔAUROC +{deltas.mean():.4f} ({frac_pos:.0%} "
            f"seeds positive, Wilcoxon p={wilcox_p:.4f}, CI [{ci_lo:.4f},{ci_hi:.4f}]; pooled-OOF Δ {aSM_oof-aS_oof:+.4f}, "
            f"CI [{oof_ci_lo:.4f},{oof_ci_hi:.4f}], p={oof_p:.4f}). Feature-level integration does not reliably beat raw "
            f"structure on ClinTox even under the paired test — the B32/B32b 'not established' bound stands."
        ),
    }
    print("VERDICT:", res["verdict"])
    print(f"per-seed Δ mean {res['paired_delta_mean']} ({frac_pos:.0%} pos) Wilcoxon p {res['wilcoxon_onesided_p']} "
          f"CI {res['bootstrap_delta_CI95']} | OOF S {aS_oof:.3f} S+M {aSM_oof:.3f} p {oof_p:.4f}")

    prov = {"experiment": "B35_integration_paired", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "seeds": SEEDS,
            "note": "paired re-adjudication of B32b feature-level fusion on ClinTox; same features/data",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    full = {"provenance": prov, "results": res}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(full, open(os.path.join(HERE, "results", "B35_metrics.json"), "w"), indent=2, sort_keys=True)
    digest = hashlib.sha256(json.dumps(res, sort_keys=True).encode()).hexdigest()
    open(os.path.join(HERE, "results", "B35_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B35_metrics.json")


def _libvers():
    import sklearn, scipy, numpy, rdkit
    return {"numpy": numpy.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__, "rdkit": rdkit.__version__}


if __name__ == "__main__":
    main()
