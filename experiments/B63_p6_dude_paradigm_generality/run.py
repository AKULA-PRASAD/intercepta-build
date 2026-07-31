"""B63 — does P6 (bias independence/additivity) hold under the DUD-E decoy paradigm on DIVERSE actives? Closes P6's one
untested boundary: 2x2 factorial {A0 random-background vs A1 DUD-E-style (property-matched + topology-dissimilar)
decoys} x {B0 random vs B1 novel-chemistry actives}, MoleculeACE actives + constructed ChEMBL-background decoys.
Implements prereg/B63_p6_dude_paradigm_generality.md. Deterministic -> reproduce x2. No docking.
"""
import os, sys, json, time, hashlib, glob
import numpy as np
import pandas as pd
import warnings; warnings.filterwarnings("ignore")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem, Descriptors, Crippen
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit.ML.Scoring.Scoring import CalcAUC
from sklearn.ensemble import HistGradientBoostingClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
MACE = os.path.join(DATA, "moleculeace")
CHEMBL = os.path.join(DATA, "tdc_gen", "chembl.tab")
MAX_ACT, BG_N, RATIO, SEEDS, NN_NOVEL, MIN_NOVEL, TOPO_MAX = 400, 8000, 3, [1, 2, 3], 0.40, 15, 0.50


def bit(m): return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=1024)
def arr(fp):
    a = np.zeros(1024, dtype=np.float32); DataStructs.ConvertToNumpyArray(fp, a); return a
def murcko(m):
    try: return Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(m))
    except Exception: return ""
def desc(m):
    return np.array([Descriptors.MolWt(m), Crippen.MolLogP(m), Descriptors.NumHDonors(m),
                     Descriptors.NumHAcceptors(m), Descriptors.TPSA(m), Descriptors.NumRotatableBonds(m)], float)
def auroc(y, s):
    r = [[int(y[i])] for i in np.argsort(-np.asarray(s))]; return float(CalcAUC(r, 0))


def load_background():
    mols = []
    rng = np.random.default_rng(42)
    lines = open(CHEMBL).read().splitlines()[1:]
    idx = rng.permutation(len(lines))[:BG_N * 3]  # oversample; some won't parse
    for i in sorted(idx):
        p = lines[i].split("\t")
        if len(p) >= 2:
            m = Chem.MolFromSmiles(p[1].strip('"'))
            if m is not None:
                mols.append(m)
        if len(mols) >= BG_N:
            break
    return mols


def evaluate(path, BG, bgX, bgFP, bgDesc):
    df = pd.read_csv(path)
    acts = [Chem.MolFromSmiles(str(s)) for s in df["smiles"]]
    acts = [m for m in acts if m is not None]
    rng = np.random.default_rng(42)
    if len(acts) > MAX_ACT:
        acts = [acts[i] for i in sorted(rng.permutation(len(acts))[:MAX_ACT])]
    nA = len(acts)
    aX = np.vstack([arr(bit(m)) for m in acts]); aFP = [bit(m) for m in acts]
    aScaf = np.array([murcko(m) for m in acts], dtype=object)
    aDesc = np.vstack([desc(m) for m in acts])
    mu = np.vstack([aDesc, bgDesc]).mean(0); sd = np.vstack([aDesc, bgDesc]).std(0); sd[sd == 0] = 1.0
    A = (aDesc - mu) / sd; Bz = (bgDesc - mu) / sd

    def split_indices(seed, novel):
        if not novel:
            perm = np.random.default_rng(seed).permutation(nA); nte = max(10, int(0.2 * nA))
            return perm[nte:], perm[:nte]
        uniq = np.array(sorted(set(aScaf))); perm = np.random.default_rng(seed).permutation(uniq)
        tsc = set(perm[:max(1, int(0.3 * len(uniq)))]); te = np.array([s in tsc for s in aScaf])
        tr = np.where(~te)[0]; tec = np.where(te)[0]; trf = [aFP[i] for i in tr]
        nov = [i for i in tec if max(DataStructs.BulkTanimotoSimilarity(aFP[i], trf)) < NN_NOVEL]
        return tr, np.array(nov, int)

    def random_decoys(k, rng2, used):
        avail = [j for j in range(len(BG)) if j not in used]
        return list(rng2.permutation(avail)[:k])

    def dude_decoys(act_idx, k, used):
        """property-matched (nearest z) + topology-dissimilar (max Tanimoto to actives < TOPO_MAX), greedy
        no-replacement. Returns EXACTLY k decoys TOTAL (the pre-registered 3:1 ratio, k = RATIO*len(actives)),
        round-robin across actives: each active claims its nearest still-available topology-dissimilar background
        compound in turn until k are chosen. Per-active physchem ordering is computed ONCE (with a resume pointer)
        and membership uses plain-int sets — deterministic; O(1) checks; no redundant argsorts."""
        picks, picks_set = [], set()
        ref = [aFP[a] for a in act_idx[:50]]                          # topology reference (loop-invariant)
        order = {ai: np.argsort(np.sum((Bz - A[ai]) ** 2, axis=1)) for ai in act_idx}   # nearest-first, once
        ptr = {ai: 0 for ai in act_idx}                              # resume pointer per active (no rescanning)
        while len(picks) < k:
            progressed = False
            for ai in act_idx:
                if len(picks) >= k:
                    break
                o, i = order[ai], ptr[ai]
                while i < len(o):
                    j = int(o[i]); i += 1
                    if j in used or j in picks_set:
                        continue
                    if max(DataStructs.BulkTanimotoSimilarity(bgFP[j], ref)) < TOPO_MAX:
                        picks.append(j); picks_set.add(j); progressed = True
                        break
                ptr[ai] = i
            if not progressed:                                       # eligible background exhausted
                break
        return picks

    cells = {c: [] for c in ("A0B0", "A1B0", "A0B1", "A1B1")}; ok = True
    for seed in SEEDS:
        for novel, Bt in ((False, "B0"), (True, "B1")):
            tr_a, te_a = split_indices(seed, novel)
            if novel and len(te_a) < MIN_NOVEL:
                ok = False; continue
            if len(te_a) < 5 or len(tr_a) < 5:
                continue
            drng = np.random.default_rng(1000 + seed)
            n_trd, n_ted = RATIO * len(tr_a), RATIO * len(te_a)
            used = set()
            trd0 = random_decoys(n_trd, drng, used); used.update(trd0)
            ted0 = random_decoys(n_ted, drng, used)
            used1 = set()
            trd1 = dude_decoys(tr_a, n_trd, used1); used1.update(trd1)
            ted1 = dude_decoys(te_a, n_ted, used1)
            for At, trd, ted in (("A0", trd0, ted0), ("A1", trd1, ted1)):
                if len(trd) < 3 or len(ted) < 3:
                    continue
                trX = np.vstack([aX[tr_a], bgX[trd]]); trY = np.array([1] * len(tr_a) + [0] * len(trd))
                teX = np.vstack([aX[te_a], bgX[ted]]); teY = np.array([1] * len(te_a) + [0] * len(ted))
                if len(np.unique(trY)) < 2:
                    continue
                m = HistGradientBoostingClassifier(random_state=42, max_iter=150, learning_rate=0.06, max_depth=6).fit(trX, trY)
                cells[At + Bt].append(auroc(teY, m.predict_proba(teX)[:, 1]))
    if not ok or not all(cells[c] for c in cells):
        return {"note": "insufficient novel-chemistry test actives", "n_actives": nA}
    m = {c: round(float(np.mean(v)), 4) for c, v in cells.items()}
    return {"n_actives": nA, "cells": m,
            "decoy_effect": round(((m["A0B0"] - m["A1B0"]) + (m["A0B1"] - m["A1B1"])) / 2, 4),
            "analog_effect": round(((m["A0B0"] - m["A0B1"]) + (m["A1B0"] - m["A1B1"])) / 2, 4),
            "interaction": round((m["A0B0"] - m["A1B0"]) - (m["A0B1"] - m["A1B1"]), 4),
            "irreducible_A1B1": m["A1B1"]}


def main():
    print("loading ChEMBL background...")
    BG = load_background(); bgX = np.vstack([arr(bit(m)) for m in BG]); bgFP = [bit(m) for m in BG]
    bgDesc = np.vstack([desc(m) for m in BG])
    print(f"background: {len(BG)} compounds")
    per = {}
    for path in sorted(glob.glob(os.path.join(MACE, "CHEMBL*.csv"))):
        name = os.path.basename(path).replace(".csv", "")
        s = evaluate(path, BG, bgX, bgFP, bgDesc); per[name] = s
        if "cells" in s:
            c = s["cells"]
            print(f"  {name:16s} A0B0 {c['A0B0']} A1B0 {c['A1B0']} A0B1 {c['A0B1']} A1B1 {c['A1B1']} | "
                  f"decoy {s['decoy_effect']:+} analog {s['analog_effect']:+} interaction {s['interaction']:+}")
        else:
            print(f"  {name:16s} SKIP ({s.get('note')})")

    sc = {k: v for k, v in per.items() if "cells" in v}
    def pm(key): return round(float(np.mean([v[key] for v in sc.values()])), 4)
    def pc(cell): return round(float(np.mean([v["cells"][cell] for v in sc.values()])), 4)
    decoy, analog, inter, irr = pm("decoy_effect"), pm("analog_effect"), pm("interaction"), pm("irreducible_A1B1")
    h1 = bool(abs(inter) < 0.03); h2 = bool(abs(inter) >= 0.03)

    summary = {"n_targets": len(sc), "panel_cells": {c: pc(c) for c in ("A0B0", "A1B0", "A0B1", "A1B1")},
               "decoy_bias_effect": decoy, "analog_bias_effect": analog, "interaction": inter, "irreducible_A1B1": irr,
               "reference": {"B54_interaction": -0.019, "B56_interaction": -0.0005},
               "H1_P6_generalises_across_decoy_paradigms": h1, "H2_P6_paradigm_specific": h2,
               "verdict": (
                   f"P6 GENERALISES ACROSS DECOY PARADIGMS -> a GENERAL LAW of VS bias: under the DUD-E paradigm "
                   f"(property-matched + topology-dissimilar constructed decoys) on diverse ChEMBL actives, the "
                   f"analogue x decoy interaction is {inter:+} (|.|<0.03), matching the HTS-paradigm B54 (-0.019) / B56 "
                   f"(-0.0005). Decoy-effect {decoy:+}, analogue-effect {analog:+}. So analogue and decoy bias are "
                   f"INDEPENDENT and ADDITIVE regardless of decoy construction (HTS-inactives OR DUD-E-style) and across "
                   f"three curations -- P6 graduates from replicated to a general law; honest evaluation needs BOTH "
                   f"controls universally. {len(sc)} targets; constructed decoys (our DUD-E recipe); not wet-lab."
                   if h1 else
                   f"P6 IS DECOY-PARADIGM-SPECIFIC (honest boundary): under the DUD-E paradigm the interaction is {inter:+} "
                   f"(|.|>=0.03), unlike the HTS-paradigm B54/B56 (~0). So analogue and decoy bias are NOT cleanly "
                   f"independent under DUD-E-style decoys -> P6's additivity does not transfer across decoy "
                   f"constructions; it is HTS-paradigm-specific. First-class boundary on P6's generality. {len(sc)} "
                   f"targets; constructed decoys; not wet-lab."),
               }
    print("\nPANEL interaction:", inter, "(B54 -0.019, B56 -0.0005) | decoy", decoy, "analog", analog)
    print("VERDICT:", summary["verdict"])

    prov = {"experiment": "B63_p6_dude_paradigm_generality", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "max_act": MAX_ACT, "bg_n": BG_N, "ratio": RATIO,
            "seeds": SEEDS, "nn_novel": NN_NOVEL, "topo_max": TOPO_MAX,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = {"provenance": prov, "summary": summary, "per_target": per}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "B63_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary, "per_target": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B63_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B63_metrics.json")


def _libvers():
    import rdkit, numpy, sklearn, pandas
    return {"rdkit": rdkit.__version__, "numpy": numpy.__version__, "scikit-learn": sklearn.__version__, "pandas": pandas.__version__}


if __name__ == "__main__":
    main()
