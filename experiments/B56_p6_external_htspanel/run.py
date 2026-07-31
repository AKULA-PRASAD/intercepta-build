"""B56 — external replication of P6 (bias independence/additivity, B54) on the TDC/Butkiewicz PubChem-HTS panel — a
different curation + target set than LIT-PCBA. Runs the B54 2x2 factorial VERBATIM (only the data loader differs). If
interaction ~0 replicates, P6 graduates toward a scientific principle; if not, P6 is demoted. Implements
prereg/B56_p6_external_htspanel.md. Deterministic -> reproduce x2. No docking.
"""
import os, sys, json, time, hashlib
import numpy as np
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
TARGETS = ["hiv", "m1_muscarinic_receptor_antagonists_butkiewicz", "orexin1_receptor_butkiewicz",
           "potassium_ion_channel_kir2.1_butkiewicz", "serine_threonine_kinase_33_butkiewicz", "sarscov2_3clpro_diamond"]
MAX_ACT, POOL_CAP, RATIO, SEEDS, NN_NOVEL, MIN_NOVEL_TEST = 400, 8000, 3, [1, 2, 3, 4, 5], 0.40, 15


def largest(smi):
    m = Chem.MolFromSmiles(str(smi))
    if m is None: return None
    fr = Chem.GetMolFrags(m, asMols=True, sanitizeFrags=True)
    return max(fr, key=lambda f: f.GetNumHeavyAtoms()) if fr else m
def murcko(m):
    try: return Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(m))
    except Exception: return ""
def bit(m): return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=1024)
def arr(fp):
    a = np.zeros(1024, dtype=np.float32); DataStructs.ConvertToNumpyArray(fp, a); return a
def physchem6(m):
    return np.array([Descriptors.MolWt(m), Crippen.MolLogP(m), Descriptors.NumHDonors(m),
                     Descriptors.NumHAcceptors(m), Descriptors.TPSA(m), Descriptors.NumRotatableBonds(m)], float)
def auroc(y, s):
    r = [[int(y[i])] for i in np.argsort(-np.asarray(s))]; return float(CalcAUC(r, 0))


def match_decoys(a_desc, i_desc, mu, sd, k, forbidden):
    A = (a_desc - mu) / sd; I = (i_desc - mu) / sd
    used = np.zeros(len(I), bool); used[list(forbidden)] = True; picks = []
    for _ in range(k):
        for a in A:
            d = np.sum((I - a) ** 2, axis=1); d[used] = np.inf
            j = int(np.argmin(d))
            if np.isfinite(d[j]): used[j] = True; picks.append(j)
    return picks


def fit_auroc(tr_fp, tr_y, te_fp, te_y):
    m = HistGradientBoostingClassifier(random_state=42, max_iter=150, learning_rate=0.06, max_depth=6).fit(tr_fp, tr_y)
    return auroc(te_y, m.predict_proba(te_fp)[:, 1])


def load(tgt):
    from tdc.single_pred import HTS
    d = HTS(name=tgt, path=os.path.join(DATA, "tdc_bio")).get_data().dropna(subset=["Y", "Drug"])
    acts = [m for m in (largest(s) for s in d[d["Y"] == 1]["Drug"].tolist()) if m is not None]
    decs = [m for m in (largest(s) for s in d[d["Y"] == 0]["Drug"].tolist()) if m is not None]
    # dedup by canonical smiles; drop cross-label
    ac = {Chem.MolToSmiles(m): m for m in acts}; aset = set(ac)
    dc = {Chem.MolToSmiles(m): m for m in decs if Chem.MolToSmiles(m) not in aset}
    return list(ac.values()), list(dc.values())


def evaluate(tgt):
    acts, decs = load(tgt)
    rng = np.random.default_rng(42)
    if len(acts) > MAX_ACT:
        acts = [acts[i] for i in sorted(rng.permutation(len(acts))[:MAX_ACT])]
    if len(decs) > POOL_CAP:
        decs = [decs[i] for i in sorted(rng.permutation(len(decs))[:POOL_CAP])]
    if len(decs) < RATIO * len(acts) + 20:
        return {"note": f"insufficient decoys ({len(decs)})"}

    aX = np.vstack([arr(bit(m)) for m in acts]); aFP = [bit(m) for m in acts]
    aScaf = np.array([murcko(m) for m in acts], dtype=object)
    aDesc = np.vstack([physchem6(m) for m in acts]); iDesc = np.vstack([physchem6(m) for m in decs])
    dX = np.vstack([arr(bit(m)) for m in decs])
    alld = np.vstack([aDesc, iDesc]); mu = alld.mean(0); sd = alld.std(0); sd[sd == 0] = 1.0
    nA = len(acts)

    def split_indices(seed, novel):
        if not novel:
            perm = np.random.default_rng(seed).permutation(nA); nte = max(10, int(0.2 * nA))
            return perm[nte:], perm[:nte]
        uniq = np.array(sorted(set(aScaf))); perm = np.random.default_rng(seed).permutation(uniq)
        tsc = set(perm[:max(1, int(0.3 * len(uniq)))]); te = np.array([s in tsc for s in aScaf])
        tr_idx = np.where(~te)[0]; te_cand = np.where(te)[0]; tr_fps = [aFP[i] for i in tr_idx]
        novel_te = [i for i in te_cand if max(DataStructs.BulkTanimotoSimilarity(aFP[i], tr_fps)) < NN_NOVEL]
        return tr_idx, np.array(novel_te, int)

    cells = {c: [] for c in ("A0B0", "A1B0", "A0B1", "A1B1")}; ok = True
    for seed in SEEDS:
        for novel, Bt in ((False, "B0"), (True, "B1")):
            tr_a, te_a = split_indices(seed, novel)
            if novel and len(te_a) < MIN_NOVEL_TEST:
                ok = False; continue
            if len(te_a) < 5 or len(tr_a) < 5: continue
            drng = np.random.default_rng(1000 + seed)
            n_trd, n_ted = RATIO * len(tr_a), RATIO * len(te_a)
            perm = drng.permutation(len(decs)); trd0, ted0 = perm[:n_trd], perm[n_trd:n_trd + n_ted]
            trd1 = match_decoys(aDesc[tr_a], iDesc, mu, sd, RATIO, set())[:n_trd]
            ted1 = match_decoys(aDesc[te_a], iDesc, mu, sd, RATIO, set(trd1))[:n_ted]
            for At, trd, ted in (("A0", trd0, ted0), ("A1", trd1, ted1)):
                tr_fp = np.vstack([aX[tr_a], dX[trd]]); tr_y = np.array([1] * len(tr_a) + [0] * len(trd))
                te_fp = np.vstack([aX[te_a], dX[ted]]); te_y = np.array([1] * len(te_a) + [0] * len(ted))
                if len(np.unique(tr_y)) < 2: continue
                cells[At + Bt].append(fit_auroc(tr_fp, tr_y, te_fp, te_y))
    if not ok or not all(cells[c] for c in cells):
        return {"note": "insufficient novel-chemistry test actives", "n_actives": nA}
    m = {c: round(float(np.mean(v)), 4) for c, v in cells.items()}
    return {"n_actives": nA, "cells": m,
            "decoy_effect": round(((m["A0B0"] - m["A1B0"]) + (m["A0B1"] - m["A1B1"])) / 2, 4),
            "analog_effect": round(((m["A0B0"] - m["A0B1"]) + (m["A1B0"] - m["A1B1"])) / 2, 4),
            "interaction": round((m["A0B0"] - m["A1B0"]) - (m["A0B1"] - m["A1B1"]), 4),
            "irreducible_A1B1": m["A1B1"]}


def main():
    per = {}
    for t in TARGETS:
        s = evaluate(t); per[t] = s
        if "cells" in s:
            c = s["cells"]
            print(f"  {t[:26]:26s} A0B0 {c['A0B0']} A1B0 {c['A1B0']} A0B1 {c['A0B1']} A1B1 {c['A1B1']} | "
                  f"decoy {s['decoy_effect']:+} analog {s['analog_effect']:+} interaction {s['interaction']:+}")
        else:
            print(f"  {t[:26]:26s} SKIP ({s.get('note')})")

    sc = {k: v for k, v in per.items() if "cells" in v}
    if len(sc) < 2:
        summary = {"n_targets": len(sc), "verdict": f"INCONCLUSIVE: only {len(sc)} target(s) supported the novel arm."}
    else:
        def pm(key): return round(float(np.mean([v[key] for v in sc.values()])), 4)
        def pc(cell): return round(float(np.mean([v["cells"][cell] for v in sc.values()])), 4)
        decoy, analog, inter, irr = pm("decoy_effect"), pm("analog_effect"), pm("interaction"), pm("irreducible_A1B1")
        h1 = bool(abs(inter) < 0.03); h2 = bool(abs(inter) >= 0.03)
        summary = {"n_targets": len(sc), "panel_cells": {c: pc(c) for c in ("A0B0", "A1B0", "A0B1", "A1B1")},
                   "decoy_bias_effect": decoy, "analog_bias_effect": analog, "interaction": inter,
                   "irreducible_A1B1": irr,
                   "B54_reference": {"interaction": -0.019, "decoy": 0.075, "analog": 0.087, "irreducible": 0.628},
                   "H1_P6_replicates_independent": h1, "H2_P6_fails": h2,
                   "verdict": (
                       f"P6 REPLICATES on a different HTS curation/target set — biases INDEPENDENT/ADDITIVE: interaction "
                       f"{inter:+} (|.|<0.03; B54 -0.019). Decoy-effect {decoy:+} (B54 +0.075), analog-effect {analog:+} "
                       f"(B54 +0.087). Panel standard {pc('A0B0')} -> doubly-controlled {irr}. P6 graduates toward a "
                       f"SCIENTIFIC PRINCIPLE: analog and physicochemical/decoy biases are separate additive inflation "
                       f"sources across LIT-PCBA AND the TDC/Butkiewicz HTS panel; honest evaluation needs BOTH controls. "
                       f"PARTIAL external replication (different curation/targets, both PubChem-HTS); {len(sc)} targets, "
                       f"in-silico; not wet-lab."
                       if h1 else
                       f"P6 DOES NOT REPLICATE on the HTS panel (P6 demoted to benchmark-specific): interaction {inter:+} "
                       f"(|.|>=0.03; B54 -0.019). On this curation the two biases are NOT cleanly independent -> the "
                       f"additivity law does not transfer; P6 is not general. First-class negative; {len(sc)} targets, "
                       f"in-silico; not wet-lab."),
                   }
    print("\nVERDICT:", summary["verdict"])

    prov = {"experiment": "B56_p6_external_htspanel", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "targets": TARGETS, "max_act": MAX_ACT,
            "pool_cap": POOL_CAP, "ratio": RATIO, "seeds": SEEDS, "nn_novel": NN_NOVEL,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = {"provenance": prov, "summary": summary, "per_target": per}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "B56_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary, "per_target": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B56_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B56_metrics.json")


def _libvers():
    import rdkit, numpy, sklearn
    return {"rdkit": rdkit.__version__, "numpy": numpy.__version__, "scikit-learn": sklearn.__version__}


if __name__ == "__main__":
    main()
