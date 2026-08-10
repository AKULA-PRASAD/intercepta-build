#!/usr/bin/env python3
"""R5-gate adjudication: does the PKM2/ALDH1 residual survive a STRICTER novelty threshold (Tanimoto<0.3)
and a STRONGER 15-descriptor property control? Decides whether R5 (molecule-half heavy compute) opens.
Reproducible; reuses the R3-harmonized r2input.csv for each target. See DECISION.md for the verdict (CLOSED)."""
import numpy as np, pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, AllChem, DataStructs
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
import os

DESC = [Descriptors.MolWt, Descriptors.MolLogP, Descriptors.NumHDonors, Descriptors.NumHAcceptors, Descriptors.TPSA,
        Descriptors.NumRotatableBonds, lambda m: m.GetNumHeavyAtoms(), Descriptors.RingCount, Descriptors.FractionCSP3,
        Descriptors.NumAromaticRings, Descriptors.NumAliphaticRings, Descriptors.NHOHCount, Descriptors.NOCount,
        Descriptors.qed, Descriptors.HeavyAtomMolWt]
def ecfp(s):
    m = Chem.MolFromSmiles(s); return None if m is None else AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048)
def to_np(bvs):
    X = np.zeros((len(bvs), 2048), np.int8)
    for i, b in enumerate(bvs): DataStructs.ConvertToNumpyArray(b, X[i])
    return X
def props(s):
    m = Chem.MolFromSmiles(s); return [f(m) for f in DESC] if m else None
def boot_ci(sc, y, B=2000, seed=42):
    sc = np.asarray(sc, float); y = np.asarray(y, int); rng = np.random.default_rng(seed); n = len(y); o = []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        if len(set(y[idx])) < 2: continue
        o.append(roc_auc_score(y[idx], sc[idx]))
    return float(np.mean(o)), float(np.percentile(o, 2.5)), float(np.percentile(o, 97.5))

def main(base="../R3_data_ingestion/results"):
    here = os.path.dirname(os.path.abspath(__file__))
    print(f'{"target":7s} {"nn<":>4s} {"n_nov_act":>9s} {"ECFP":>6s} {"ECFP_CIlo":>9s} {"PROP15":>7s} {"ECFP-PROP":>9s} {"R5?":>7s}')
    for tgt in ["PKM2", "ALDH1"]:
        d = pd.read_csv(os.path.join(here, base, tgt, "r2input.csv")); d["active"] = (d["y [pEC50/pKi]"] >= 6.5).astype(int)
        d["fp"] = [ecfp(s) for s in d.smiles]; d["P"] = [props(s) for s in d.smiles]
        d = d[d.fp.notna() & d.P.notna()].reset_index(drop=True); tr, te = d[d.split == "train"], d[d.split == "test"]
        tra = list(tr[tr.active == 1].fp)
        ecm = RandomForestClassifier(300, random_state=42, n_jobs=1).fit(to_np(list(tr.fp)), tr.active.values)
        prm = RandomForestClassifier(300, random_state=42, n_jobs=1).fit(np.array(list(tr.P), float), tr.active.values)
        ecs = ecm.predict_proba(to_np(list(te.fp)))[:, 1]; prs = prm.predict_proba(np.array(list(te.P), float))[:, 1]
        nn = np.array([max(DataStructs.BulkTanimotoSimilarity(f, tra)) for f in te.fp])
        for thr in [0.4, 0.3]:
            mk = nn < thr; y = te.active.values[mk]
            if y.sum() < 5 or (y == 0).sum() < 5: print(f'{tgt:7s} {thr:>4} {int(y.sum()):>9d}  too few'); continue
            em, elo, _ = boot_ci(ecs[mk], y); pm, _, _ = boot_ci(prs[mk], y); gap = em - pm
            print(f'{tgt:7s} {thr:>4} {int(y.sum()):>9d} {em:>6.3f} {elo:>9.3f} {pm:>7.3f} {gap:>9.3f} '
                  f'{"OPEN" if (elo>0.60 and gap>0.10) else "CLOSED":>7s}')

if __name__ == "__main__":
    main()
