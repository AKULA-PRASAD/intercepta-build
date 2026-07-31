"""B64 — END-TO-END DISCOVERY DEMONSTRATION on FEN1 (flap endonuclease 1; DNA-repair / synthetic-lethality oncology
target). Composes every validated INTERCEPTA module into ONE closed pipeline and runs it end-to-end:
  activity QSAR (calibrated + applicability domain, LIT-PCBA FEN1)  ->  target-conditioned BRICS-GA generation  ->
  multi-channel scoring (activity x developability(QED x synth) x safety(hERG/AMES/DILI))  ->  ranked, AD-annotated
  candidate shortlist.  Output = ranked COMPUTATIONAL HYPOTHESES (NOT validated actives, NOT drugs, no wet-lab).
Implements prereg/B64_endtoend_fen1_demonstration.md. Deterministic -> reproduce x2 (payload sha256).
"""
import os, sys, json, time, hashlib
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
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
sys.path.insert(0, os.path.join(ROOT, "src"))
from intercepta.admet import featurize, _TaskModel                       # noqa: E402
from intercepta.discover import DiscoveryPipeline                        # noqa: E402

SEED, N_INACT, NN_NOVEL, POP, GEN, TOP = 42, 10000, 0.40, 60, 8, 20
FEN1 = os.path.join(DATA, "lit_pcba", "FEN1")


def load_smi(path, cap=None, seed=SEED):
    smis = []
    for line in open(path):
        p = line.split()
        if p:
            m = Chem.MolFromSmiles(p[0])
            if m is not None:
                smis.append(Chem.MolToSmiles(m))
    smis = sorted(set(smis))
    if cap is not None and len(smis) > cap:
        smis = list(np.array(smis)[np.random.RandomState(seed).permutation(len(smis))[:cap]])
    return smis


def morgan(smis):
    fps = []
    for s in smis:
        m = Chem.MolFromSmiles(s)
        fps.append(AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048) if m else None)
    return fps


def max_tanimoto(query_fp, ref_fps):
    if query_fp is None or not ref_fps:
        return 0.0
    return float(max(DataStructs.BulkTanimotoSimilarity(query_fp, ref_fps)))


def scaffold_of(s):
    m = Chem.MolFromSmiles(s)
    if m is None:
        return ""
    try:
        return MurckoScaffold.MurckoScaffoldSmiles(mol=m)
    except Exception:
        return ""


def auroc_split(Xa, ya, idx_tr, idx_te):
    mdl = _TaskModel("FEN1", "roc-auc", seed=SEED).fit(Xa[idx_tr], ya[idx_tr])
    val = mdl.predict(Xa[idx_te])[0]
    return float(roc_auc_score(ya[idx_te], val))


def main():
    t0 = time.time()
    print("=== B64: end-to-end discovery demonstration on FEN1 ===")

    # ---- 1. load FEN1 (LIT-PCBA): all actives + seeded inactive subsample --------------------------------
    actives = load_smi(os.path.join(FEN1, "actives.smi"))
    inactives = load_smi(os.path.join(FEN1, "inactives.smi"), cap=N_INACT)
    print(f"FEN1 actives={len(actives)}  inactive-subsample={len(inactives)}")
    smis = actives + inactives
    y = np.array([1] * len(actives) + [0] * len(inactives), dtype=int)
    X, valid = featurize(smis)
    X, y = X[valid], y[valid]
    smis = [s for s, v in zip(smis, valid) if v]

    # ---- 2. QSAR validation (honest, up front): random + scaffold-disjoint held-out AUROC ----------------
    rng = np.random.RandomState(SEED)
    perm = rng.permutation(len(y)); cut = int(0.8 * len(y))
    tr, te = perm[:cut], perm[cut:]
    auc_random = auroc_split(X, y, tr, te)

    scaffs = np.array([scaffold_of(s) for s in smis])
    uniq = sorted(set(scaffs) - {""})
    su = np.array(uniq)[np.random.RandomState(SEED).permutation(len(uniq))]
    test_sc = set(su[: int(0.2 * len(su))])
    is_te = np.array([s in test_sc for s in scaffs])
    auc_scaffold = float("nan")
    if is_te.sum() > 5 and y[is_te].sum() > 0 and y[~is_te].sum() > 0 and len(set(y[is_te])) == 2:
        auc_scaffold = auroc_split(X, y, np.where(~is_te)[0], np.where(is_te)[0])
    print(f"QSAR held-out AUROC: random={auc_random:.3f}  scaffold-disjoint={auc_scaffold:.3f}")
    print("  (novel-chemistry doubly-controlled residual AUROC ~0.80 established in B45, the strongest of the panel)")

    # ---- 3. final FEN1 QSAR on ALL data (conformal + AD) for scoring/generation --------------------------
    fen1 = _TaskModel("FEN1", "roc-auc", seed=SEED, conformal=True).fit(X, y)

    # ---- 4. compose the full pipeline: ADMET safety + synth + FEN1 activity, then generate ---------------
    print("fitting ADMET(hERG/AMES/DILI) + synthesizability + composing pipeline ...")
    pipe = DiscoveryPipeline.from_default(seed=SEED)          # herg/ames/dili + synth (validated B30/B31)
    pipe.target_model, pipe.target_name = fen1, "FEN1"        # attach the validated FEN1 activity QSAR (B40 pattern)
    print("target-conditioned generation (BRICS-GA) ...")
    shortlist, history = pipe.discover(seed_smiles=None, pop_size=POP, generations=GEN, top=TOP)

    # ---- 5. honest annotation: nearest-known-active Tanimoto + conformal set on P(active) ----------------
    active_fps = [fp for fp in morgan(actives) if fp is not None]
    cand_smis = shortlist["smiles"].tolist()
    cand_fps = morgan(cand_smis)
    Xc, _ = featurize(cand_smis)
    _, _, _, _, _, csets, csize = fen1.predict_conformal(Xc)
    shortlist = shortlist.copy()
    shortlist["nn_tanimoto_to_known_active"] = [round(max_tanimoto(fp, active_fps), 4) for fp in cand_fps]
    shortlist["is_novel_chemistry"] = shortlist["nn_tanimoto_to_known_active"] < NN_NOVEL
    shortlist["activity_conformal_set"] = list(csets) if csets is not None else ["n/a"] * len(cand_smis)
    shortlist["honest_confidence"] = np.where(
        shortlist["applicability_domain"].str.startswith("in-domain"), "reliable (in-domain)",
        "LOW — out-of-domain, do not trust the activity call")

    cols = ["smiles", "developability_F", "p_target_active", "activity_conformal_set", "applicability_domain",
            "nn_tanimoto_to_known_active", "is_novel_chemistry", "qed", "sa_score", "synth_solvable_prob",
            "p_herg", "p_ames", "p_dili", "predicted_safety", "honest_confidence"]
    shortlist = shortlist[[c for c in cols if c in shortlist.columns]]
    shortlist.to_csv(os.path.join(HERE, "results", "B64_shortlist.csv"), index=False)

    n_indom = int(shortlist["applicability_domain"].str.startswith("in-domain").sum())
    print(f"shortlist: {len(shortlist)} candidates, {n_indom} in-domain (reliable), "
          f"{int(shortlist['is_novel_chemistry'].sum())} novel-chemistry")

    # ---- 6. assemble deterministic payload ---------------------------------------------------------------
    def r(v, n=4):
        return None if (isinstance(v, float) and (np.isnan(v))) else (round(float(v), n) if isinstance(v, (int, float, np.floating)) else v)

    records = [{k: r(rec[k]) for k in shortlist.columns} for rec in shortlist.to_dict("records")]
    validation = {"target": "FEN1", "n_actives": len(actives), "n_inactive_subsample": len(inactives),
                  "auroc_random_heldout": round(auc_random, 4),
                  "auroc_scaffold_disjoint_heldout": (round(auc_scaffold, 4) if auc_scaffold == auc_scaffold else None),
                  "b45_novel_chemistry_residual_auroc_ref": 0.80}
    summary = {"experiment": "B64", "kind": "end-to-end capability demonstration (NOT a hypothesis test)",
               "target": "FEN1 (flap endonuclease 1; DNA-repair / synthetic-lethality oncology)",
               "pipeline": "activity-QSAR -> target-conditioned BRICS-GA -> multi-channel(activity x developability x safety) -> ranked shortlist",
               "n_shortlist": len(shortlist), "n_in_domain_reliable": n_indom,
               "n_novel_chemistry": int(shortlist["is_novel_chemistry"].sum()),
               "gen_pop": POP, "gen_generations": GEN, "seed": SEED,
               "scope": ("Ranked COMPUTATIONAL HYPOTHESES, not validated actives / not drugs; retrospective in-silico, "
                         "open data; enrichment != measured activity (P2); out-of-domain candidates untrustworthy (P9); "
                         "no wet-lab, no prospective confirmation.")}
    out = {"summary": summary, "validation": validation, "shortlist": records,
           "generation_history": history if history is not None else [],
           "runtime_sec": round(time.time() - t0, 1)}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "B64_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"validation": validation, "shortlist": records}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B64_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest)
    print("wrote results/B64_metrics.json + results/B64_shortlist.csv  (%.1fs)" % (time.time() - t0))


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    main()
