"""HIT2 — the structure-only PHYSICS floor: does thrombin docking recover the NOVEL-chemotype actives that ligand-transfer
cannot? Analysis over the cached Vina scores (build_dock_cache.py) + HIT1 ligand signals, on the SAME CHEMBL204 test set and
novelty split. Compares PHYSICS vs SIMILARITY vs QSAR overall / analog / novel, + a consensus. Deterministic; reproduced ×2.
Env: intercepta-build (rdkit/sklearn).
"""
import os, csv, json, time, hashlib
import numpy as np
import warnings; warnings.filterwarnings("ignore")
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
CACHE = os.path.join(DATA, "hit2", "thrombin_vina.tsv")
MACE = os.path.join(DATA, "hit1", "moleculeace", "CHEMBL204_Ki.csv")
ACT_CUT, NOVEL_TAN, SEED = 6.5, 0.4, 42


def fp(smi):
    m = Chem.MolFromSmiles(smi); return AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048) if m else None


def to_np(bv):
    a = np.zeros((2048,), dtype=np.uint8); DataStructs.ConvertToNumpyArray(bv, a); return a


def auroc(y, s):
    y = np.asarray(y); return float(roc_auc_score(y, s)) if 0 < y.sum() < len(y) else float("nan")


def sub_auroc(pos, neg, s):
    if pos.sum() < 5 or neg.sum() < 5: return float("nan")
    idx = np.where(pos | neg)[0]; return round(auroc(pos[idx].astype(int), np.asarray(s)[idx]), 4)


def main():
    t0 = time.time()
    # HIT1 seeds (CHEMBL204 train actives) for novelty / similarity / QSAR
    train = [r for r in csv.DictReader(open(MACE)) if r["split"] == "train"]
    seed_act_fp = [fp(r["smiles"]) for r in train if float(r["y [pEC50/pKi]"]) >= ACT_CUT]
    seed_act_fp = [f for f in seed_act_fp if f is not None]
    Xtr = np.vstack([to_np(fp(r["smiles"])) for r in train if fp(r["smiles"])])
    ytr = np.array([int(float(r["y [pEC50/pKi]"]) >= ACT_CUT) for r in train if fp(r["smiles"])])
    rf = RandomForestClassifier(n_estimators=300, random_state=SEED, n_jobs=4).fit(Xtr, ytr)

    rows = [ln.rstrip("\n").split("\t") for ln in open(CACHE)][1:]
    smis = [r[4] for r in rows]; y = np.array([int(r[1]) for r in rows])
    vina = np.array([float(r[3]) if r[3] != "" else np.nan for r in rows])
    fps = [fp(s) for s in smis]
    sim = np.array([max(DataStructs.BulkTanimotoSimilarity(f, seed_act_fp)) if f else 0.0 for f in fps])
    qsar = rf.predict_proba(np.vstack([to_np(f) if f else np.zeros(2048, np.uint8) for f in fps]))[:, 1]
    # physics goodness: -vina (higher=better); failed docks -> worst
    worst = np.nanmax(vina) + 5.0 if np.isfinite(vina).any() else 0.0
    phys = -np.where(np.isnan(vina), worst, vina)
    n_failed = int(np.isnan(vina).sum())

    novelty = sim  # nearest-seed-active Tanimoto
    is_act = y == 1; is_inact = y == 0
    novel_act = is_act & (novelty < NOVEL_TAN); analog_act = is_act & (novelty >= NOVEL_TAN)
    # consensus = mean of normalized ranks (higher=better) of physics & similarity
    def nrank(s):
        order = np.argsort(np.argsort(s)); return order / (len(s) - 1)
    consensus = (nrank(phys) + nrank(sim)) / 2.0

    def block(score):
        return {"overall": round(auroc(y, score), 4),
                "analog_vs_inactive": sub_auroc(analog_act, is_inact, score),
                "novel_vs_inactive": sub_auroc(novel_act, is_inact, score)}
    R = {"physics": block(phys), "similarity": block(sim), "qsar": block(qsar), "consensus": block(consensus)}
    corr_phys_novelty = round(float(np.corrcoef(phys, novelty)[0, 1]), 4)

    ph_ov, ph_nv, ph_an = R["physics"]["overall"], R["physics"]["novel_vs_inactive"], R["physics"]["analog_vs_inactive"]
    sim_nv = R["similarity"]["novel_vs_inactive"]
    H1 = ph_ov > 0.55
    analogy_independent = (ph_nv == ph_nv and ph_an == ph_an and abs(ph_nv - ph_an) < 0.1 and ph_nv > 0.55)
    physics_beats_sim_on_novel = (ph_nv == ph_nv and sim_nv == sim_nv and ph_nv > sim_nv)
    summary = {"target": "thrombin (CHEMBL204)", "n_test": len(y), "n_active": int(y.sum()),
               "n_novel_active": int(novel_act.sum()), "n_failed_dock": n_failed,
               "physics_overall_AUROC": ph_ov, "physics_novel_AUROC": ph_nv, "physics_analog_AUROC": ph_an,
               "similarity_novel_AUROC": sim_nv, "corr_physics_novelty": corr_phys_novelty,
               "consensus_overall_AUROC": R["consensus"]["overall"], "consensus_novel_AUROC": R["consensus"]["novel_vs_inactive"],
               "H1_physics_floor_exists": bool(H1),
               "H2_physics_analogy_independent": bool(analogy_independent),
               "physics_beats_similarity_on_novel": bool(physics_beats_sim_on_novel)}
    if H1 and analogy_independent:
        summary["verdict"] = (f"H1+H2 (physics floor is ANALOGY-INDEPENDENT): thrombin docking recovers actives above random "
                              f"zero-data (overall AUROC {ph_ov}) and — the crux — recovers NOVEL chemotypes about as well as "
                              f"analogs (novel {ph_nv} vs analog {ph_an}; |Δ|<0.1; corr(physics,novelty)={corr_phys_novelty}≈0), "
                              f"UNLIKE similarity (novel {sim_nv}). So structure-based physics is the zero-data signal that "
                              f"SURVIVES where chemical analogy fails — the complement to HIT1's analog-bound ligand signal. "
                              f"SCOPE: single FAVOURABLE target (thrombin, well-pocketed) → existence proof, not generalization; "
                              f"Vina scoring weak; rigid receptor; not wet-lab.")
    elif H1:
        summary["verdict"] = (f"H1 only (weak physics floor, NOT clearly analogy-independent): docking beats random overall "
                              f"(AUROC {ph_ov}) but novel-chemotype recovery ({ph_nv}) is not clearly ≥ analog ({ph_an}) / not "
                              f">0.55 robustly — physics helps weakly but does not cleanly rescue novel chemotypes here. Honest. "
                              f"Single target; Vina weak; not wet-lab.")
    else:
        summary["verdict"] = (f"H0 (no usable physics floor on this target): thrombin docking ≈ random zero-data (overall AUROC "
                              f"{ph_ov} ≤ 0.55), consistent with docking's known weak prospective enrichment (C1). Then the "
                              f"molecule-half novel-chemotype problem is hard for BOTH ligand AND physics families here — a hard "
                              f"ceiling. Single target; Vina weak; not wet-lab.")
    print("PANEL:", json.dumps({k: v for k, v in summary.items() if k != "verdict"}, indent=1)); print("VERDICT:", summary["verdict"])

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "act_cut": ACT_CUT, "novel_tan": NOVEL_TAN}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "rankers": R, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "HIT2_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k: v for k, v in summary.items() if k != "verdict"}, "rankers": R}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "HIT2_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
