"""B54 — factorial decomposition of ligand-based VS enrichment. 2x2: {random vs property-matched decoys} x {analog-
present vs analog-controlled (novel-chemistry NN<0.4) actives}. Measures whether decoy-bias and analog-bias are
independent (interaction term) and the irreducible binding signal that survives BOTH controls (A1B1). Implements
prereg/B54_decoy_artifact_discriminator.md. Deterministic -> reproduce x2. No docking.
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
LIT = os.path.join(DATA, "lit_pcba")
TARGETS = ["ALDH1", "VDR", "PKM2", "FEN1", "MAPK1", "GBA", "KAT2A", "ESR1_ant"]
MAX_ACT, RATIO, SEEDS, NN_NOVEL, MIN_NOVEL_TEST = 300, 3, [1, 2, 3, 4, 5], 0.40, 15


def read_smi(p): return [l.split()[0] for l in open(p) if l.split()]
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
    """greedy NN property-matched inactive indices (no replacement), k per active."""
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


def evaluate(tgt):
    td = os.path.join(LIT, tgt)
    acts = list({Chem.MolToSmiles(m): m for m in (largest(s) for s in read_smi(os.path.join(td, "actives.smi"))) if m}.values())
    aset = {Chem.MolToSmiles(m) for m in acts}
    decs = [m for s, m in {Chem.MolToSmiles(m): m for m in (largest(s) for s in read_smi(os.path.join(td, "inactives.smi"))) if m}.items() if s not in aset]
    rng = np.random.default_rng(42)
    if len(acts) > MAX_ACT:
        acts = [acts[i] for i in sorted(rng.permutation(len(acts))[:MAX_ACT])]
    if len(decs) < RATIO * len(acts) + 20:
        return {"note": f"insufficient inactives ({len(decs)})"}

    aX = np.vstack([arr(bit(m)) for m in acts]); aFP = [bit(m) for m in acts]
    aScaf = np.array([murcko(m) for m in acts], dtype=object)
    aDesc = np.vstack([physchem6(m) for m in acts]); iDesc = np.vstack([physchem6(m) for m in decs])
    dX = np.vstack([arr(bit(m)) for m in decs])
    alld = np.vstack([aDesc, iDesc]); mu = alld.mean(0); sd = alld.std(0); sd[sd == 0] = 1.0
    nA = len(acts)

    def split_indices(seed, novel):
        if not novel:                                        # B0: random active split (analog present)
            perm = np.random.default_rng(seed).permutation(nA); nte = max(10, int(0.2 * nA))
            return perm[nte:], perm[:nte]
        uniq = np.array(sorted(set(aScaf))); perm = np.random.default_rng(seed).permutation(uniq)
        tsc = set(perm[:max(1, int(0.3 * len(uniq)))]); te = np.array([s in tsc for s in aScaf])
        tr_idx = np.where(~te)[0]; te_cand = np.where(te)[0]
        # restrict test actives to NN<0.4 vs train actives (analog controlled)
        tr_fps = [aFP[i] for i in tr_idx]
        novel_te = [i for i in te_cand if max(DataStructs.BulkTanimotoSimilarity(aFP[i], tr_fps)) < NN_NOVEL]
        return tr_idx, np.array(novel_te, int)

    cells = {c: [] for c in ("A0B0", "A1B0", "A0B1", "A1B1")}
    novel_ok = True
    for seed in SEEDS:
        for novel, Bt in ((False, "B0"), (True, "B1")):
            tr_a, te_a = split_indices(seed, novel)
            if novel and len(te_a) < MIN_NOVEL_TEST:
                novel_ok = False; continue
            if len(te_a) < 5 or len(tr_a) < 5:
                continue
            drng = np.random.default_rng(1000 + seed)
            # A0: random decoys
            perm = drng.permutation(len(decs))
            n_trd, n_ted = RATIO * len(tr_a), RATIO * len(te_a)
            trd0, ted0 = perm[:n_trd], perm[n_trd:n_trd + n_ted]
            # A1: matched decoys (train matched to train actives; test matched to test actives, disjoint)
            trd1 = match_decoys(aDesc[tr_a], iDesc, mu, sd, RATIO, set())[:n_trd]
            ted1 = match_decoys(aDesc[te_a], iDesc, mu, sd, RATIO, set(trd1))[:n_ted]
            for At, trd, ted in (("A0", trd0, ted0), ("A1", trd1, ted1)):
                tr_fp = np.vstack([aX[tr_a], dX[trd]]); tr_y = np.array([1] * len(tr_a) + [0] * len(trd))
                te_fp = np.vstack([aX[te_a], dX[ted]]); te_y = np.array([1] * len(te_a) + [0] * len(ted))
                if len(np.unique(tr_y)) < 2: continue
                cells[At + Bt].append(fit_auroc(tr_fp, tr_y, te_fp, te_y))
    if not novel_ok or not all(cells[c] for c in cells):
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
            print(f"  {t:9s} A0B0 {c['A0B0']} A1B0 {c['A1B0']} A0B1 {c['A0B1']} A1B1 {c['A1B1']} | "
                  f"decoy {s['decoy_effect']:+} analog {s['analog_effect']:+} interaction {s['interaction']:+} | irred {s['irreducible_A1B1']}")
        else:
            print(f"  {t:9s} SKIP ({s.get('note')})")

    sc = {k: v for k, v in per.items() if "cells" in v}
    def pm(key): return round(float(np.mean([v[key] for v in sc.values()])), 4)
    def pc(cell): return round(float(np.mean([v["cells"][cell] for v in sc.values()])), 4)
    decoy, analog, inter, irr = pm("decoy_effect"), pm("analog_effect"), pm("interaction"), pm("irreducible_A1B1")
    n_irr = int(sum(1 for v in sc.values() if v["irreducible_A1B1"] > 0.60))
    h1 = bool(abs(inter) < 0.03)          # independent/additive
    h2 = bool(inter <= -0.03)             # overlapping/subadditive
    h3 = bool(irr > 0.60)                 # irreducible signal exists

    summary = {"n_targets": len(sc),
               "panel_cells": {c: pc(c) for c in ("A0B0", "A1B0", "A0B1", "A1B1")},
               "decoy_bias_effect": decoy, "analog_bias_effect": analog, "interaction": inter,
               "irreducible_signal_A1B1": irr, "n_targets_irreducible_gt0.60": n_irr,
               "H1_biases_independent": h1, "H2_biases_overlap_subadditive": h2, "H3_irreducible_signal_exists": h3,
               "verdict": (
                   f"DECOMPOSITION: ligand-based VS enrichment falls from standard {pc('A0B0')} (analog+decoy bias "
                   f"present) to doubly-controlled {irr} (both removed). Decoy-bias effect {decoy:+}, analog-bias "
                   f"effect {analog:+}, INTERACTION {inter:+} -> the two biases are "
                   + ("INDEPENDENT/ADDITIVE (interaction~0): they are separate inflation sources; BOTH controls are "
                      "needed." if h1 else "OVERLAPPING/SUBADDITIVE: controlling one removes much of the other -> "
                      "they are largely the same phenomenon; one control ~ suffices." if h2 else
                      "SUPERADDITIVE (controls compound): removing one makes the other bite harder.")
                   + (f" AN IRREDUCIBLE BINDING SIGNAL SURVIVES BOTH (A1B1 {irr}>0.60, {n_irr}/{len(sc)} targets) -> "
                      f"ligand-based VS captures real generalizable signal beyond both biases; its honest ceiling is "
                      f"~{irr}, far below the biased {pc('A0B0')}."
                      if h3 else
                      f" NO IRREDUCIBLE SIGNAL: under BOTH controls AUROC collapses to {irr}~chance -> ligand-based VS "
                      f"enrichment on these sets is ESSENTIALLY BIAS-DRIVEN (theory-reframing).")
                   + " Retrospective, in-silico, 6-descriptor matching (lower bound), NN<0.4 analog control, 8 targets; not wet-lab."),
               }
    print("\nVERDICT:", summary["verdict"])

    prov = {"experiment": "B54_decoy_artifact_discriminator", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "targets": TARGETS, "max_act": MAX_ACT,
            "ratio": RATIO, "seeds": SEEDS, "nn_novel": NN_NOVEL, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = {"provenance": prov, "summary": summary, "per_target": per}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "B54_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary, "per_target": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B54_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B54_metrics.json")


def _libvers():
    import rdkit, numpy, sklearn
    return {"rdkit": rdkit.__version__, "numpy": numpy.__version__, "scikit-learn": sklearn.__version__}


if __name__ == "__main__":
    main()
