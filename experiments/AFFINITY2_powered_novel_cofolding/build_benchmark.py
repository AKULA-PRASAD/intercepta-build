#!/usr/bin/env python
"""AFFINITY2 step 1 — build the POWERED, leakage-controlled novel-chemotype benchmark (compound side).
Per target: ECFP4 novel split (max-Tanimoto to TRAIN actives < 0.40), select ALL novel actives (cap 125) +
an equal random sample of novel inactives (seed 42), <=250/target. Identify the LIT-PCBA receptor PDB(s).
Deterministic. Writes compounds.csv per target + benchmark_manifest.json. Implements PREREG.md.
"""
import os, json, glob, hashlib
import numpy as np, pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs

D = os.environ.get("INTERCEPTA_DATA", os.path.expanduser("~/intercepta_data"))
HERE = os.path.dirname(os.path.abspath(__file__))
R3 = os.path.join(HERE, "..", "R3_data_ingestion", "results")
LITP = os.path.join(D, "lit_pcba")
OUT = os.path.join(HERE, "benchmark"); os.makedirs(OUT, exist_ok=True)
ACT_CUT, NN_NOVEL, NBITS, RADIUS, SEED, CAP_ACT = 6.5, 0.40, 2048, 2, 42, 125
PANEL = ["ALDH1", "PKM2", "FEN1"]  # most novel actives; GBA/MAPK1 addable if GPU budget allows (see PREREG)

def ecfp(s):
    m = Chem.MolFromSmiles(s)
    return None if m is None else AllChem.GetMorganFingerprintAsBitVect(m, RADIUS, nBits=NBITS)

def build_target(tgt):
    df = pd.read_csv(os.path.join(R3, tgt, "r2input.csv"))
    df["active"] = (df["y [pEC50/pKi]"] >= ACT_CUT).astype(int)
    df["fp"] = [ecfp(s) for s in df.smiles]
    df = df[df.fp.notna()].reset_index(drop=True)
    tr = df[df.split == "train"]; te = df[df.split == "test"]
    train_actives = list(tr[tr.active == 1].fp)
    nn = np.array([max(DataStructs.BulkTanimotoSimilarity(f, train_actives)) for f in te.fp])
    te = te.assign(nn_to_train_active=nn, novel=(nn < NN_NOVEL))
    novel = te[te.novel]
    nov_act = novel[novel.active == 1]; nov_ina = novel[novel.active == 0]
    rng = np.random.default_rng(SEED)
    n_act = min(len(nov_act), CAP_ACT)
    sel_act = nov_act.sample(n=n_act, random_state=SEED) if len(nov_act) > n_act else nov_act
    n_ina = min(len(nov_ina), n_act)  # class-balanced
    sel_ina = nov_ina.sample(n=n_ina, random_state=SEED) if len(nov_ina) > n_ina else nov_ina
    sel = pd.concat([sel_act, sel_ina]).sort_values("smiles").reset_index(drop=True)
    sel_out = sel[["smiles", "active", "nn_to_train_active"]].copy()
    sel_out.insert(0, "cmpd_id", [f"{tgt}_{i:04d}" for i in range(len(sel_out))])
    sel_out.to_csv(os.path.join(OUT, f"{tgt}_compounds.csv"), index=False)
    pdbs = sorted({os.path.basename(p).split("_")[0] for p in glob.glob(os.path.join(LITP, tgt, "*_protein.mol2"))})
    return {"target": tgt, "n_train_actives": int((tr.active == 1).sum()), "n_test": int(len(te)),
            "n_novel_test": int(len(novel)), "n_novel_actives_total": int(len(nov_act)),
            "n_novel_inactives_total": int(len(nov_ina)), "scored_actives": int(len(sel_act)),
            "scored_inactives": int(len(sel_ina)), "scored_total": int(len(sel_out)),
            "receptor_pdbs_available": pdbs, "receptor_pdb_chosen": pdbs[0] if pdbs else None}

def main():
    man = {"config": {"ACT_CUT": ACT_CUT, "NN_NOVEL": NN_NOVEL, "NBITS": NBITS, "RADIUS": RADIUS,
                      "SEED": SEED, "CAP_ACT": CAP_ACT}, "panel": PANEL, "targets": []}
    for t in PANEL:
        r = build_target(t); man["targets"].append(r)
        print(f"{t}: novel_test={r['n_novel_test']} novel_act(total)={r['n_novel_actives_total']} "
              f"-> scored {r['scored_actives']}a/{r['scored_inactives']}i (total {r['scored_total']}); "
              f"receptor {r['receptor_pdb_chosen']} of {r['receptor_pdbs_available']}")
    payload = json.dumps(man, indent=2, sort_keys=True)
    open(os.path.join(OUT, "benchmark_manifest.json"), "w").write(payload + "\n")
    print("\ntotal complexes to co-fold:", sum(t["scored_total"] for t in man["targets"]))
    print("manifest sha256:", hashlib.sha256(payload.encode()).hexdigest())

if __name__ == "__main__":
    main()
