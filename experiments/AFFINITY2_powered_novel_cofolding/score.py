#!/usr/bin/env python
"""AFFINITY2 step 3 — score the powered novel-chemotype benchmark + apply the pre-registered WALL_BREAKING gate.
Baselines (property RF, ligand QSAR RF) are computed locally (no GPU). Co-folding scores are read from the
Explorer Boltz outputs (benchmark/boltz_out/<target>/predictions/<cmpd_id>/affinity_<cmpd_id>.json ->
affinity_pred_value) once the relay run returns them; if absent, baselines are reported and co-folding is
marked PENDING. Deterministic (seed 42); reproduces byte-identical. Implements PREREG.md."""
import os, json, glob, hashlib
import numpy as np, pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, AllChem, DataStructs
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__)); BM = os.path.join(HERE, "benchmark")
R3 = os.path.join(HERE, "..", "R3_data_ingestion", "results")
RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)
SEED, NBITS, RADIUS, ACT_CUT = 42, 2048, 2, 6.5
PANEL = ["ALDH1", "PKM2", "FEN1"]
DESC = [Descriptors.MolWt, Descriptors.MolLogP, Descriptors.NumHDonors, Descriptors.NumHAcceptors, Descriptors.TPSA,
        Descriptors.NumRotatableBonds, lambda m: m.GetNumHeavyAtoms(), Descriptors.RingCount, Descriptors.FractionCSP3,
        Descriptors.NumAromaticRings, Descriptors.NumAliphaticRings, Descriptors.NHOHCount, Descriptors.NOCount,
        Descriptors.qed, Descriptors.HeavyAtomMolWt]

def ecfp(s):
    m = Chem.MolFromSmiles(s); return None if m is None else AllChem.GetMorganFingerprintAsBitVect(m, RADIUS, nBits=NBITS)
def to_np(bvs):
    X = np.zeros((len(bvs), NBITS), np.int8)
    for i, b in enumerate(bvs): DataStructs.ConvertToNumpyArray(b, X[i])
    return X
def props(s):
    m = Chem.MolFromSmiles(s); return [f(m) for f in DESC] if m else None
def boot_ci(sc, y, B=2000, seed=SEED):
    sc = np.asarray(sc, float); y = np.asarray(y, int); rng = np.random.default_rng(seed); o = []
    for _ in range(B):
        idx = rng.integers(0, len(y), len(y))
        if len(set(y[idx])) < 2: continue
        o.append(roc_auc_score(y[idx], sc[idx]))
    return float(np.mean(o)), float(np.percentile(o, 2.5)), float(np.percentile(o, 97.5))

def cofold_scores(tgt, ids):
    """read Boltz affinity_pred_value per compound; score = -affinity_pred_value. None if outputs absent.
    cmpd_ids are globally unique (target-prefixed) so we search all of boltz_out/ regardless of chunk layout."""
    base = os.path.join(BM, "boltz_out")
    if not os.path.isdir(base): return None
    out = {}
    for cid in ids:
        hits = glob.glob(os.path.join(base, "**", f"affinity_{cid}.json"), recursive=True)
        if not hits: continue
        try:
            j = json.load(open(hits[0])); out[cid] = -float(j["affinity_pred_value"])
        except Exception: pass
    return out if out else None

def main():
    per_target, tier1_targets, tier2_targets = {}, 0, 0
    for tgt in PANEL:
        comp = pd.read_csv(os.path.join(BM, f"{tgt}_compounds.csv"))
        # train set for the baselines (same target, R3 train split)
        tr = pd.read_csv(os.path.join(R3, tgt, "r2input.csv"))
        tr["active"] = (tr["y [pEC50/pKi]"] >= ACT_CUT).astype(int); tr = tr[tr.split == "train"]
        tr_fp = [ecfp(s) for s in tr.smiles]; tr_ok = [i for i, f in enumerate(tr_fp) if f is not None]
        Xtr_e = to_np([tr_fp[i] for i in tr_ok]); ytr = tr.active.values[tr_ok]
        Xtr_p = np.array([props(s) for s in tr.smiles.values[tr_ok]], float)
        y = comp.active.values
        te_fp = [ecfp(s) for s in comp.smiles]; te_p = np.array([props(s) for s in comp.smiles], float)
        qsar = RandomForestClassifier(300, random_state=SEED, n_jobs=1).fit(Xtr_e, ytr).predict_proba(to_np(te_fp))[:, 1]
        prop = RandomForestClassifier(300, random_state=SEED, n_jobs=1).fit(Xtr_p, ytr).predict_proba(te_p)[:, 1]
        qa = boot_ci(qsar, y); pa = boot_ci(prop, y)
        rec = {"n": int(len(y)), "n_active": int(y.sum()),
               "QSAR_AUROC": round(qa[0], 4), "QSAR_CI": [round(qa[1], 4), round(qa[2], 4)],
               "property_AUROC": round(pa[0], 4), "property_CI": [round(pa[1], 4), round(pa[2], 4)]}
        cf = cofold_scores(tgt, list(comp.cmpd_id))
        if cf:
            mask = comp.cmpd_id.isin(cf).values
            cfs = np.array([cf[c] for c in comp.cmpd_id[mask]]); yc = y[mask]
            ca = boot_ci(cfs, yc)
            best_base = max(qa[0], pa[0]); gap = ca[0] - best_base
            tier1 = bool(ca[1] > 0.60)                 # ZERO_DATA_SIGNAL (standalone)
            tier2 = bool(tier1 and gap > 0.10)          # BEATS_LIGAND_ML
            rec.update({"cofold_AUROC": round(ca[0], 4), "cofold_CI": [round(ca[1], 4), round(ca[2], 4)],
                        "cofold_n_scored": int(mask.sum()), "cofold_minus_best_baseline": round(gap, 4),
                        "TIER1_zero_data_signal": tier1, "TIER2_beats_ligand_ml": tier2})
            tier1_targets += int(tier1); tier2_targets += int(tier2)
        else:
            rec.update({"cofold_AUROC": None, "TIER1_zero_data_signal": None,
                        "TIER2_beats_ligand_ml": None, "status": "PENDING_GPU_RUN"})
        per_target[tgt] = rec
        print(f"{tgt}: QSAR {rec['QSAR_AUROC']} | property {rec['property_AUROC']} | "
              f"cofold {rec.get('cofold_AUROC')} | TIER1 {rec.get('TIER1_zero_data_signal')} "
              f"TIER2 {rec.get('TIER2_beats_ligand_ml')}")

    if any(v.get("cofold_AUROC") is None for v in per_target.values()):
        verdict = "PENDING_GPU_RUN"
    elif tier1_targets >= 2:
        verdict = ("TIER1+TIER2: co-folding breaks the wall, beats ligand-ML (R5 OPENS, strong)"
                   if tier2_targets >= 2 else "TIER1: zero-data co-folding signal (R5 OPENS)")
    else:
        verdict = "WALL HOLDS -> D2 CLOSED DEFINITIVELY AT POWER (co-folding, last untried method, fails zero-data)"
    out = {"panel": PANEL,
           "gate": "TIER1 cofold standalone novel-AUROC CI-lo>0.60 on >=2 targets; TIER2 also cofold-max(QSAR,property)>0.10",
           "per_target": per_target, "n_targets_tier1": tier1_targets, "n_targets_tier2": tier2_targets,
           "VERDICT": verdict, "seed": SEED}
    payload = json.dumps(out, indent=2, sort_keys=True)
    open(os.path.join(RES, "AFFINITY2_metrics.json"), "w").write(payload + "\n")
    open(os.path.join(RES, "payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    print("\nVERDICT:", verdict); print("sha256:", hashlib.sha256(payload.encode()).hexdigest())

if __name__ == "__main__":
    main()
