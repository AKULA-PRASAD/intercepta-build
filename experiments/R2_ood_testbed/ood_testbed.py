#!/usr/bin/env python3
"""R2 — leakage-controlled OOD-generalization testbed (a reusable instrument).

Measures whether a method predicts bioactivity for genuinely NOVEL chemotypes (held out of training by
ECFP4 Tanimoto), scored separately on SEEN(analog) vs NOVEL splits, with a pre-registered WALL_BREAKING
alarm. See PREREG.md (locked). Deterministic scoring -> reproduce x2 byte-identical.

Usage:
  python ood_testbed.py [target_csv] [smiles_col] [potency_col] [split_col] [external_scores_csv]
Defaults instantiate on MoleculeACE CHEMBL204 thrombin shipped in AFFINITY1/benchmark_data.
`external_scores_csv` (optional): columns `smiles,score` (higher=more active) for a drop-in method.
"""
import os, sys, json, hashlib
import numpy as np, pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)
ACT_CUT, NN_NOVEL, B, SEED, NBITS, RADIUS, EF_FRAC, ALARM = 6.5, 0.40, 2000, 42, 2048, 2, 0.10, 0.60

def fp(smi):
    m = Chem.MolFromSmiles(str(smi))
    return None if m is None else AllChem.GetMorganFingerprintAsBitVect(m, RADIUS, nBits=NBITS)

def to_np(bvs):
    X = np.zeros((len(bvs), NBITS), dtype=np.int8)
    for i, b in enumerate(bvs): DataStructs.ConvertToNumpyArray(b, X[i])
    return X

def scaffold(smi):
    m = Chem.MolFromSmiles(str(smi))
    if m is None: return None
    try: return MurckoScaffold.MurckoScaffoldSmiles(mol=m)
    except Exception: return None

def boot_auroc(score, y, seed=SEED, B=B):
    s = np.asarray(score, float); y = np.asarray(y, int); m = ~np.isnan(s); s, y = s[m], y[m]
    if len(set(y.tolist())) < 2: return {"auroc": None, "ci95": [None, None], "n": int(len(y)), "n_pos": int(y.sum())}
    obs = float(roc_auc_score(y, s)); rng = np.random.default_rng(seed); n = len(y); out = []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        if len(set(y[idx].tolist())) < 2: continue
        out.append(roc_auc_score(y[idx], s[idx]))
    out = np.array(out)
    return {"auroc": round(obs, 6), "ci95": [round(float(np.percentile(out, 2.5)), 6), round(float(np.percentile(out, 97.5)), 6)],
            "n": int(len(y)), "n_pos": int(y.sum())}

def ef(score, y, frac=EF_FRAC):
    s = np.asarray(score, float); y = np.asarray(y, int); m = ~np.isnan(s); s, y = s[m], y[m]
    npos = int(y.sum())
    if npos == 0 or len(y) == 0: return None
    k = max(1, int(round(frac * len(y)))); top = np.argsort(-s, kind="mergesort")[:k]
    return round(float((y[top].sum() / k) / (npos / len(y))), 4)

def load(target_csv, smi_c, pot_c, split_c):
    d = pd.read_csv(target_csv)
    d = d.rename(columns={smi_c: "smiles", pot_c: "pot", split_c: "split"})
    d = d[["smiles", "pot", "split"]].dropna(subset=["smiles", "pot", "split"]).copy()
    d["active"] = (d["pot"].astype(float) >= ACT_CUT).astype(int)
    d["fp"] = [fp(s) for s in d["smiles"]]; d = d[d["fp"].notna()].reset_index(drop=True)
    return d

def main():
    a = sys.argv
    target_csv = a[1] if len(a) > 1 else os.path.join(HERE, "..", "AFFINITY1_cofolding_zeroshot", "benchmark_data", "CHEMBL204_Ki.csv")
    smi_c = a[2] if len(a) > 2 else "smiles"; pot_c = a[3] if len(a) > 3 else "y [pEC50/pKi]"; split_c = a[4] if len(a) > 4 else "split"
    ext_csv = a[5] if len(a) > 5 else None
    d = load(target_csv, smi_c, pot_c, split_c)
    tr, te = d[d.split == "train"].reset_index(drop=True), d[d.split == "test"].reset_index(drop=True)
    tr_act = tr[tr.active == 1]
    # novelty = max Tanimoto of each TEST cpd to TRAIN ACTIVES
    tr_act_fps = list(tr_act.fp)
    nn = np.array([max(DataStructs.BulkTanimotoSimilarity(f, tr_act_fps)) if tr_act_fps else 0.0 for f in te.fp])
    te = te.assign(nn_tan=nn, novelty=np.where(nn < NN_NOVEL, "novel", "analog"))
    # scaffold-disjoint sensitivity: test scaffolds not present among train scaffolds
    tr_scaf = set(s for s in (scaffold(x) for x in tr.smiles) if s)
    te = te.assign(scaf_novel=[1 if (scaffold(x) not in tr_scaf) else 0 for x in te.smiles])

    # ---- methods ----
    scores = {}
    scores["similarity"] = nn  # interpolation control
    rf = RandomForestClassifier(n_estimators=300, random_state=SEED, n_jobs=1)
    rf.fit(to_np(list(tr.fp)), tr.active.values)
    scores["qsar_rf"] = rf.predict_proba(to_np(list(te.fp)))[:, 1]
    if ext_csv and os.path.exists(ext_csv):
        e = pd.read_csv(ext_csv).rename(columns={smi_c: "smiles"})
        emap = dict(zip(e["smiles"].astype(str), e["score"].astype(float)))
        scores["external"] = np.array([emap.get(str(s), np.nan) for s in te.smiles])

    y = te.active.values
    masks = {"ALL": np.ones(len(te), bool),
             "SEEN_analog": (te.novelty == "analog").values,
             "NOVEL": (te.novelty == "novel").values,
             "NOVEL_scaffold": (te.scaf_novel == 1).values}
    report = {}
    for meth, sc in scores.items():
        report[meth] = {}
        for split, mk in masks.items():
            report[meth][split] = {**boot_auroc(sc[mk], y[mk]), "ef10": ef(sc[mk], y[mk])}

    # ---- pre-registered ALARM gate ----
    alarms = {}
    for meth in scores:
        if meth == "similarity":  # excluded (interpolation by construction)
            alarms[meth] = "EXCLUDED_interpolation_control"; continue
        nov = report[meth]["NOVEL"]; lo = nov["ci95"][0]
        alarms[meth] = ("WALL_BREAKING" if (lo is not None and lo > ALARM) else "WALL_HOLDS")
    verdict = "WALL_BREAKING" if any(v == "WALL_BREAKING" for v in alarms.values()) else "WALL_HOLDS"

    payload = {
        "instrument": "R2 OOD-generalization testbed",
        "config": {"act_cut": ACT_CUT, "nn_novel_threshold": NN_NOVEL, "bootstrap_B": B, "seed": SEED,
                   "ecfp": [RADIUS, NBITS], "ef_frac": EF_FRAC, "alarm_novel_ci_lower_gt": ALARM},
        "target_csv": os.path.basename(os.path.abspath(target_csv)),
        "counts": {"train": int(len(tr)), "train_active": int(tr.active.sum()),
                   "test": int(len(te)), "test_active": int(y.sum()),
                   "test_novel": int((te.novelty == "novel").sum()), "test_novel_active": int(((te.novelty == "novel") & (te.active == 1)).sum()),
                   "test_scaffold_novel": int((te.scaf_novel == 1).sum())},
        "leakage_audit_test_to_train_maxTanimoto": {"min": round(float(nn.min()), 4), "median": round(float(np.median(nn)), 4),
                                                    "frac_lt_0.4": round(float((nn < 0.4).mean()), 4), "frac_ge_0.8": round(float((nn >= 0.8).mean()), 4)},
        "results": report, "alarm_per_method": alarms, "verdict": verdict,
    }
    payload = json.loads(json.dumps(payload, sort_keys=True))
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(); sha = hashlib.sha256(blob).hexdigest()
    json.dump({"payload": payload, "payload_sha256": sha}, open(os.path.join(RES, "R2_metrics.json"), "w"), sort_keys=True, indent=2)
    open(os.path.join(RES, "payload.sha256"), "w").write(sha + "\n")
    print("VERDICT:", verdict, "| sha", sha)
    for meth in scores:
        r = report[meth]
        def fmt(x): return "NA" if x["auroc"] is None else f'{x["auroc"]:.3f} CI[{x["ci95"][0]:.3f},{x["ci95"][1]:.3f}] n_pos={x["n_pos"]}'
        print(f'  {meth:11s} ALL {fmt(r["ALL"])} | SEEN {fmt(r["SEEN_analog"])} | NOVEL {fmt(r["NOVEL"])} -> {alarms[meth]}')

if __name__ == "__main__":
    main()
