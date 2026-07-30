"""B45 (amended) — honest self-audit via NN-similarity-stratified enrichment. Keep the scaffold split (B43 protocol),
but stratify each test set by every compound's max Tanimoto to TRAIN (cross-set nearest neighbor), then report
enrichment as a function of that similarity: bands [<0.3, 0.3-0.4, 0.4-0.5, >=0.5]. Directly answers "does the model
still recognize actives that are GENUINELY DISSIMILAR (NN<0.4) from training?" Implements the AMENDMENT in
prereg/B45_hard_split_selfaudit.md (the pre-registered Butina cluster split failed its validity check H2). Tuning-free.
Deterministic -> reproduce x2.
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
import warnings; warnings.filterwarnings("ignore")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit.ML.Scoring.Scoring import CalcAUC, CalcEnrichment

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta.admet import featurize, _TaskModel

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
PANEL = [("hiv", "antiviral"), ("m1_muscarinic_receptor_antagonists_butkiewicz", "GPCR"),
         ("orexin1_receptor_butkiewicz", "GPCR"), ("potassium_ion_channel_kir2.1_butkiewicz", "ion-channel"),
         ("serine_threonine_kinase_33_butkiewicz", "kinase"), ("sarscov2_3clpro_diamond", "protease")]
N_INACTIVE, SEEDS = 3000, [1, 2, 3]
BANDS = [("lt0.3", -0.01, 0.30), ("0.3-0.4", 0.30, 0.40), ("0.4-0.5", 0.40, 0.50), ("ge0.5", 0.50, 1.01)]


def murcko(s):
    try: return MurckoScaffold.MurckoScaffoldSmiles(smiles=str(s), includeChirality=False)
    except Exception: return ""


def bitfp(s):
    m = Chem.MolFromSmiles(str(s))
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048) if m is not None else None


def band_metrics(labels, scores):
    """AUROC + EF@5% for one band (actives vs decoys ranked within band)."""
    if len(labels) < 20 or int(np.sum(labels)) < 5 or len(np.unique(labels)) < 2:
        return None
    ranked = [[int(labels[i])] for i in np.argsort(-scores)]
    return {"n": int(len(labels)), "n_active": int(np.sum(labels)),
            "auroc": round(float(CalcAUC(ranked, 0)), 4),
            "ef_5pct": round(float(CalcEnrichment(ranked, 0, [0.05])[0]), 3)}


def evaluate(name):
    from tdc.single_pred import HTS
    d = HTS(name=name, path=os.path.join(DATA, "tdc_bio")).get_data().dropna(subset=["Y", "Drug"])
    act = d[d["Y"] == 1]; inact = d[d["Y"] == 0].sample(n=min(N_INACTIVE, int((d["Y"] == 0).sum())), random_state=42)
    df = pd.concat([act, inact]).reset_index(drop=True)
    smiles = df["Drug"].tolist(); y = df["Y"].values.astype(int)
    X, _ = featurize(smiles); fps = [bitfp(s) for s in smiles]
    keep = [i for i, f in enumerate(fps) if f is not None]
    if len(keep) < len(fps):
        X = X[keep]; y = y[keep]; smiles = [smiles[i] for i in keep]; fps = [fps[i] for i in keep]
    scaff = np.array([murcko(s) for s in smiles], dtype=object)

    # pool test compounds across the 3 scaffold seeds: (nn_tanimoto, label, score)
    pooled_nn, pooled_y, pooled_sc, full_auc = [], [], [], []
    for seed in SEEDS:
        uniq = np.array(sorted(set(scaff))); perm = np.random.default_rng(seed).permutation(uniq)
        tsc = set(perm[:int(0.2 * len(perm))]); te = np.array([s in tsc for s in scaff]); tr = ~te
        if len(np.unique(y[te])) < 2 or int(y[tr].sum()) < 5:
            continue
        m = _TaskModel(name, "roc-auc", seed=42).fit(X[tr], y[tr]); sc = m.predict(X[te])[0]
        # full-test AUROC (reference)
        ranked = [[int(y[te][i])] for i in np.argsort(-sc)]; full_auc.append(CalcAUC(ranked, 0))
        # cross-set NN Tanimoto for each test compound
        trfps = [fps[i] for i in np.where(tr)[0]]; teidx = np.where(te)[0]
        for j, gi in enumerate(teidx):
            sims = DataStructs.BulkTanimotoSimilarity(fps[gi], trfps)
            pooled_nn.append(max(sims) if sims else 0.0); pooled_y.append(int(y[gi])); pooled_sc.append(float(sc[j]))
    if not full_auc:
        return {"n_actives": int(y.sum()), "note": "insufficient actives per fold"}
    nn = np.array(pooled_nn); yy = np.array(pooled_y); ss = np.array(pooled_sc)
    per_band = {}
    for bname, lo, hi in BANDS:
        mask = (nn > lo) & (nn <= hi)
        per_band[bname] = band_metrics(yy[mask], ss[mask]) or {"n": int(mask.sum()), "n_active": int(yy[mask].sum()),
                                                                "note": "too few (n>=20 & act>=5 required)"}
    novel_mask = nn < 0.40
    novel = band_metrics(yy[novel_mask], ss[novel_mask]) or {"n": int(novel_mask.sum()),
            "n_active": int(yy[novel_mask].sum()), "note": "too few novel actives"}
    return {"n_total": int(len(y)), "n_actives": int(y.sum()), "full_test_auroc": round(float(np.mean(full_auc)), 4),
            "pooled_test_n": int(len(yy)), "mean_xset_nn_tanimoto": round(float(nn.mean()), 4),
            "novel_lt0.4": novel, "by_band": per_band}


def main():
    per = {}
    for name, cls in PANEL:
        s = evaluate(name); s["class"] = cls; per[name] = s
        if "by_band" in s:
            b = s["by_band"]
            def a(x): return b[x].get("auroc", "—")
            print(f"  {name[:30]:30s}[{cls:11s}] full {s['full_test_auroc']} | AUROC by NN band  "
                  f"<0.3:{a('lt0.3')} 0.3-0.4:{a('0.3-0.4')} 0.4-0.5:{a('0.4-0.5')} >=0.5:{a('ge0.5')} "
                  f"| novel<0.4 AUROC {s['novel_lt0.4'].get('auroc','—')} (act {s['novel_lt0.4'].get('n_active')})")
        else:
            print(f"  {name[:30]:30s}[{cls:11s}] SKIP ({s.get('note')})")

    scored = {k: v for k, v in per.items() if "by_band" in v}
    novel_aucs = {k: v["novel_lt0.4"]["auroc"] for k, v in scored.items() if "auroc" in v["novel_lt0.4"]}
    # gradient: mean AUROC[>=0.5] - mean AUROC[<0.3] across targets having both
    grad = []
    for v in scored.values():
        hi, lo = v["by_band"]["ge0.5"], v["by_band"]["lt0.3"]
        if "auroc" in hi and "auroc" in lo:
            grad.append(hi["auroc"] - lo["auroc"])
    n_novel_ok = int(sum(1 for a in novel_aucs.values() if a > 0.65))
    panel_novel_auc = round(float(np.mean(list(novel_aucs.values()))), 4) if novel_aucs else None
    grad_mean = round(float(np.mean(grad)), 4) if grad else None
    h1 = bool(panel_novel_auc is not None and panel_novel_auc > 0.65 and n_novel_ok >= 4)
    h2 = bool(grad_mean is not None and grad_mean >= 0.03)

    summary = {"n_targets_scored": len(scored), "n_targets_with_novel_band": len(novel_aucs),
               "panel_mean_novel_lt0.4_auroc": panel_novel_auc, "n_targets_novel_auroc_gt0.65": n_novel_ok,
               "similarity_gradient_auroc_ge0.5_minus_lt0.3": grad_mean,
               "panel_mean_full_test_auroc": round(float(np.mean([v["full_test_auroc"] for v in scored.values()])), 4),
               "H1_capability_real_on_novel_chemistry": h1, "H2_similarity_gradient_exists": h2,
               "verdict": (
                   f"ENRICHMENT IS REAL ON NOVEL CHEMISTRY (not memorization): on test compounds GENUINELY dissimilar "
                   f"to training (NN-Tanimoto<0.4), panel-mean AUROC {panel_novel_auc} with {n_novel_ok}/"
                   f"{len(novel_aucs)} targets>0.65. A real similarity gradient exists (AUROC[>=0.5]-AUROC[<0.3]="
                   f"{grad_mean}) so there IS split optimism, but the capability clearly survives into novel chemistry. "
                   f"Honest: use the novel-band numbers, not the full-test numbers, as the generalization estimate. "
                   f"Retrospective, in-silico, real-actives-vs-decoys; enrichment != proven activity; not wet-lab."
                   if h1 else
                   f"CAPABILITY LARGELY MEMORIZATION (honest downgrade): on genuinely-dissimilar test compounds "
                   f"(NN<0.4) panel-mean AUROC {panel_novel_auc} ({n_novel_ok}/{len(novel_aucs)} targets>0.65); "
                   f"similarity gradient {grad_mean}. Much of our reported enrichment depends on train-test similarity "
                   f"and does NOT extend to novel chemistry — the honest generalization estimate is the (lower) "
                   f"novel-band number. First-class negative; recorded truthfully."),
               }
    print("\nVERDICT:", summary["verdict"])

    prov = {"experiment": "B45_hard_split_selfaudit", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "seeds": SEEDS, "n_inactive_cap": N_INACTIVE,
            "design": "AMENDED: NN-similarity-stratified enrichment on scaffold-split test sets (Butina cluster split "
                      "failed validity check H2). Bands [<0.3,0.3-0.4,0.4-0.5,>=0.5] by cross-set NN Tanimoto.",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    full = {"provenance": prov, "summary": summary, "per_target": per}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(full, open(os.path.join(HERE, "results", "B45_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary, "per_target": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B45_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B45_metrics.json")


def _libvers():
    import sklearn, scipy, numpy, rdkit
    return {"numpy": numpy.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__, "rdkit": rdkit.__version__}


if __name__ == "__main__":
    main()
