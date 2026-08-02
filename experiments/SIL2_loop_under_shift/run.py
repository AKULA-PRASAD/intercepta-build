"""SIL2 — does the conformal-gated self-improving loop (SIL1) survive DISTRIBUTION SHIFT? Re-runs SIL1's 4-arm ablation
on MoleculeACE (binarised potency) and evaluates on BOTH an IN-DOMAIN test and a NOVEL-chemistry test (scaffold-disjoint
+ NN-Tanimoto<0.40 to train). Maps whether the living-net loop's benefit (SIL1) is a near-domain phenomenon or crosses
the B62 information ceiling. Implements prereg/SIL2_loop_under_shift.md. Deterministic -> reproduce x2.
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
from rdkit.Chem import AllChem
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.metrics import roc_auc_score
from intercepta.admet import featurize, _TaskModel

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
MACE = os.path.join(DATA, "moleculeace")
SEEDS, TRAIN_CAP, NN_NOVEL, MIN_NOVEL, MIN_INDOM = [1, 2, 3], 250, 0.40, 30, 40
PCOL = "y [pEC50/pKi]"


def bit(m): return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=1024)
def auroc(y, s): return float(roc_auc_score(y, s)) if 0 < np.sum(y) < len(y) else float("nan")
def scaf(m):
    try: return MurckoScaffold.MurckoScaffoldSmiles(mol=m)
    except Exception: return ""


def singleton_pseudolabels(model, Xpool):
    _, _, _, _, _, sets, size = model.predict_conformal(Xpool)
    keep, lab = [], []
    for i, (st, sz) in enumerate(zip(sets, size)):
        if sz == 1:
            keep.append(i); lab.append(int(st.strip("{}").split(",")[0]))
    return np.array(keep, int), np.array(lab, int)


def carve(mols, y, X, seed):
    """novel-test (scaffold-disjoint + NN<0.4) ; then random split of the rest into train(<=cap)/indomain-test/pool."""
    FP = [bit(m) for m in mols]
    sc = np.array([scaf(m) for m in mols], dtype=object)
    uniq = np.array(sorted(set(sc) - {""}))
    if len(uniq) < 6: return None
    perm = np.random.default_rng(seed).permutation(len(uniq)); uniq = uniq[perm]
    held_sc = set(uniq[:max(1, int(0.30 * len(uniq)))])
    held = np.array([s in held_sc for s in sc]); rest = np.where(~held)[0]
    rest_fp = [FP[i] for i in rest]
    novel = [i for i in np.where(held)[0]
             if max(DataStructs.BulkTanimotoSimilarity(FP[i], rest_fp)) < NN_NOVEL]
    if len(novel) < MIN_NOVEL: return None
    rng = np.random.default_rng(1000 + seed); rp = rng.permutation(rest)
    n_ind = max(MIN_INDOM, int(0.20 * len(rest)))
    indom = rp[:n_ind]; after = rp[n_ind:]
    train = after[:TRAIN_CAP]; pool = after[TRAIN_CAP:]
    if len(train) < 60 or len(pool) < 60: return None
    return train, pool, indom, np.array(novel, int)


def loop_aucs(X, y, tr, po, tests):
    """returns dict test_name -> (A,B,C,D auroc), plus gold_acc."""
    mA = _TaskModel("t", "roc-auc", seed=42).fit(X[tr], y[tr])
    mConf = _TaskModel("t", "roc-auc", seed=42, conformal=True).fit(X[tr], y[tr])
    keep, gl = singleton_pseudolabels(mConf, X[po])
    gold_acc = float(np.mean(gl == y[po][keep])) if len(keep) else float("nan")
    mB = mA
    if len(keep) >= 5 and len(set(np.concatenate([y[tr], gl]))) == 2:
        mB = _TaskModel("t", "roc-auc", seed=42).fit(np.vstack([X[tr], X[po][keep]]), np.concatenate([y[tr], gl]))
    pall = (mConf.predict(X[po])[0] >= 0.5).astype(int)
    mC = mA
    if len(set(np.concatenate([y[tr], pall]))) == 2:
        mC = _TaskModel("t", "roc-auc", seed=42).fit(np.vstack([X[tr], X[po]]), np.concatenate([y[tr], pall]))
    mD = mA
    if len(keep) >= 5:
        sh = np.random.default_rng(1).permutation(gl)
        if len(set(np.concatenate([y[tr], sh]))) == 2:
            mD = _TaskModel("t", "roc-auc", seed=42).fit(np.vstack([X[tr], X[po][keep]]), np.concatenate([y[tr], sh]))
    out = {}
    for nm, te in tests.items():
        if len(set(y[te])) < 2:
            out[nm] = None; continue
        out[nm] = {"A": auroc(y[te], mA.predict(X[te])[0]), "B": auroc(y[te], mB.predict(X[te])[0]),
                   "C": auroc(y[te], mC.predict(X[te])[0]), "D": auroc(y[te], mD.predict(X[te])[0])}
    return out, gold_acc


def process(path):
    df = pd.read_csv(path)
    mols, ys = [], []
    for _, r in df.iterrows():
        m = Chem.MolFromSmiles(str(r["smiles"]))
        if m is not None and np.isfinite(r[PCOL]):
            mols.append(m); ys.append(float(r[PCOL]))
    if len(mols) < 150: return None
    yv = np.array(ys); y = (yv >= np.median(yv)).astype(int)
    X, v = featurize([Chem.MolToSmiles(m) for m in mols])
    mols = [m for m, k in zip(mols, v) if k]; X, y = X[v], y[v]
    accs = {"indomain": {"A": [], "B": [], "C": [], "D": []}, "novel": {"A": [], "B": [], "C": [], "D": []}, "gold": []}
    for seed in SEEDS:
        c = carve(mols, y, X, seed)
        if c is None: continue
        tr, po, indom, novel = c
        res, gacc = loop_aucs(X, y, tr, po, {"indomain": indom, "novel": novel})
        if res["indomain"] and res["novel"]:
            for k in "ABCD":
                accs["indomain"][k].append(res["indomain"][k]); accs["novel"][k].append(res["novel"][k])
            accs["gold"].append(gacc)
    if not accs["gold"]: return None
    def mean(d, k): return float(np.mean(d[k]))
    r = {"gold_acc": round(float(np.nanmean(accs["gold"])), 4)}
    for reg in ("indomain", "novel"):
        a, b = mean(accs[reg], "A"), mean(accs[reg], "B")
        r[f"{reg}_A"] = round(a, 4); r[f"{reg}_B"] = round(b, 4)
        r[f"{reg}_dBA"] = round(b - a, 4)
        r[f"{reg}_dBC"] = round(b - mean(accs[reg], "C"), 4)
        r[f"{reg}_dBD"] = round(b - mean(accs[reg], "D"), 4)
    return r


def main():
    t0 = time.time()
    print("=== SIL2: self-improving loop under distribution shift ===")
    per = {}
    for path in sorted(glob.glob(os.path.join(MACE, "CHEMBL*.csv"))):
        name = os.path.basename(path).replace(".csv", "")
        try:
            r = process(path)
        except Exception as ex:
            print(f"  {name:16s} ERR {repr(ex)[:50]}"); continue
        if r is None:
            print(f"  {name:16s} SKIP"); continue
        per[name] = r
        print(f"  {name:16s} in-dom dB-A {r['indomain_dBA']:+.3f} | NOVEL dB-A {r['novel_dBA']:+.3f} "
              f"(in-dom B {r['indomain_B']} novel B {r['novel_B']}) | gold_acc {r['gold_acc']} [{time.time()-t0:.0f}s]")

    def med(k): return round(float(np.median([per[t][k] for t in per])), 4)
    def fpos(k): return round(float(np.mean([per[t][k] > 0 for t in per])), 3)
    summary = {"n_targets": len(per),
               "median_indomain_dBA": med("indomain_dBA"), "median_novel_dBA": med("novel_dBA"),
               "median_indomain_dBD": med("indomain_dBD"), "median_novel_dBD": med("novel_dBD"),
               "frac_indomain_dBA_pos": fpos("indomain_dBA"), "frac_novel_dBA_pos": fpos("novel_dBA"),
               "median_gold_acc": med("gold_acc")}
    idom, nov = summary["median_indomain_dBA"], summary["median_novel_dBA"]
    fi, fn = summary["frac_indomain_dBA_pos"], summary["frac_novel_dBA_pos"]
    EFF, MAJ = 0.005, 0.60
    # an effect is credited ONLY if median>EFF AND a target-majority is positive (guards the coin-flip over-read, B65 lesson)
    H1 = idom > EFF and fi >= MAJ
    survives = nov > EFF and fn >= MAJ
    collapses = H1 and not survives
    summary["H1_indomain_replicates"] = bool(H1)
    summary["H2a_loop_survives_shift"] = bool(survives)
    summary["H2b_loop_near_domain_only"] = bool(collapses)
    if H1 and survives:
        summary["verdict"] = (f"H2a: the self-improving loop SURVIVES distribution shift — helps on NOVEL chemistry "
                              f"(ΔB−A novel {nov:+.3f}, {summary['frac_novel_dBA_pos']} of targets) comparably to "
                              f"in-domain ({idom:+.3f}). Conformal-gated self-knowledge transfers to novel chemistry.")
    elif H1 and collapses:
        summary["verdict"] = (f"H2b (first-class, expected): the loop's benefit is a NEAR-DOMAIN phenomenon — in-domain "
                              f"ΔB−A {idom:+.3f} ({summary['frac_indomain_dBA_pos']}) but NOVEL ΔB−A {nov:+.3f} "
                              f"({summary['frac_novel_dBA_pos']}) collapses. Self-accumulated IN-DOMAIN knowledge does "
                              f"NOT cross the novel-chemistry ceiling (consistent with B62) — the living-net loop is "
                              f"bounded to the near-domain regime. Guardrail note: novel ΔB−D {summary['median_novel_dBD']:+.3f}.")
    else:
        summary["verdict"] = (f"MIXED: in-domain ΔB−A {idom:+.3f} (H1 {'held' if H1 else 'failed'}), novel {nov:+.3f} — "
                              f"see per-target; report as-is.")
    print("\nPANEL:", json.dumps(summary, indent=1)); print("VERDICT:", summary["verdict"])

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "per_target": per, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "SIL2_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k: v for k, v in summary.items() if k != "verdict"}, "per_target": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "SIL2_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/SIL2_metrics.json (%.1fs)" % (time.time() - t0))


if __name__ == "__main__":
    main()
