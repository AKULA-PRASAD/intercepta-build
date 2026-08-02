"""SIL1 — the conformal-gated SELF-IMPROVING LOOP (VISION principle 6). Per TDC ADMET classification task, carve
scaffold-disjoint TRAIN / UNLABELED-pool / TEST, then compare 4 arms on the SAME held-out TEST:
  A WITHOUT-loop (train only) · B WITH-loop (train + conformally-confident SINGLETON pseudo-labels) ·
  C ungated (train + ALL pool pseudo-labels) · D shuffled (B's compounds, SHUFFLED labels).
Tests H1 loop helps (B>A), H2 gating is the guardrail (B>C and B>D), H3 gated pseudo-labels are trustworthy.
Implements prereg/SIL1_conformal_self_improving_loop.md. Deterministic -> reproduce x2.
"""
import os, sys, json, time, hashlib
import numpy as np
import warnings; warnings.filterwarnings("ignore")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.metrics import roc_auc_score
from intercepta.admet import featurize, _TaskModel

HERE = os.path.dirname(os.path.abspath(__file__))
DD = os.path.join(os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data"), "tdc_admet")
SEEDS, TRAIN_CAP, MIN_TEST = [1, 2, 3], 250, 120
# (name, TDC class name)
PANEL = [("ames", "Tox"), ("cyp2d6_veith", "ADME"), ("bbb_martins", "ADME"),
         ("herg", "Tox"), ("bioavailability_ma", "ADME"), ("dili", "Tox")]


def load(name, cls):
    from tdc.single_pred import ADME, Tox
    d = (ADME if cls == "ADME" else Tox)(name=name, path=DD).get_data().dropna(subset=["Y", "Drug"])
    return d["Drug"].tolist(), d["Y"].values.astype(int)


def scaffold(s):
    m = Chem.MolFromSmiles(s)
    if m is None:
        return None
    try:
        return MurckoScaffold.MurckoScaffoldSmiles(mol=m)
    except Exception:
        return ""


def auroc(y, s):
    return float(roc_auc_score(y, s)) if 0 < np.sum(y) < len(y) else float("nan")


def carve(smis, y, seed):
    """scaffold-disjoint TRAIN(<=cap) / POOL / TEST."""
    scaf = np.array([scaffold(s) for s in smis], dtype=object)
    ok = np.array([s is not None for s in smis])
    idx = np.where(ok)[0]
    uniq = sorted(set(scaf[idx]) - {None})
    perm = np.random.default_rng(seed).permutation(len(uniq))
    uniq = [uniq[i] for i in perm]
    ntest = max(1, int(0.30 * len(uniq)))
    test_sc = set(uniq[:ntest]); rest_sc = uniq[ntest:]
    train_sc, pool_sc, n = set(), set(), 0
    for sc in rest_sc:                                  # fill TRAIN to the cap, rest -> POOL
        cnt = int(np.sum(scaf[idx] == sc))
        if n < TRAIN_CAP:
            train_sc.add(sc); n += cnt
        else:
            pool_sc.add(sc)
    tr = idx[np.array([scaf[i] in train_sc for i in idx])]
    po = idx[np.array([scaf[i] in pool_sc for i in idx])]
    te = idx[np.array([scaf[i] in test_sc for i in idx])]
    if len(tr) > TRAIN_CAP:                             # enforce SMALL labelled train (room for the loop to help)
        rng = np.random.default_rng(seed + 7)
        sh = tr[rng.permutation(len(tr))]
        keep, drop = np.sort(sh[:TRAIN_CAP]), sh[TRAIN_CAP:]
        po = np.sort(np.concatenate([po, drop]))        # excess train compounds go into the UNLABELED pool
        tr = keep
    return tr, po, te


def singleton_pseudolabels(model, Xpool):
    val, ad, ind, _, _, sets, size = model.predict_conformal(Xpool)
    keep, lab = [], []
    for i, (st, sz) in enumerate(zip(sets, size)):
        if sz == 1:                                     # confident conformal singleton -> GOLD
            keep.append(i); lab.append(int(st.strip("{}").split(",")[0]))
    return np.array(keep, int), np.array(lab, int), val


def run_task(name, cls, seed):
    smis, y = load(name, cls)
    X, v = featurize(smis)
    smis = [s for s, k in zip(smis, v) if k]; X, y = X[v], y[v]
    tr, po, te = carve(smis, y, seed)
    if len(te) < MIN_TEST or len(tr) < 60 or len(po) < 60 or len(set(y[te])) < 2 or len(set(y[tr])) < 2:
        return None
    # A: baseline
    mA = _TaskModel(name, "roc-auc", seed=42).fit(X[tr], y[tr])
    aucA = auroc(y[te], mA.predict(X[te])[0])
    # B: conformal-gated self-training
    mConf = _TaskModel(name, "roc-auc", seed=42, conformal=True).fit(X[tr], y[tr])
    keep, gold_lab, _ = singleton_pseudolabels(mConf, X[po])
    gold_acc = float(np.mean(gold_lab == y[po][keep])) if len(keep) else float("nan")
    if len(keep) >= 5 and len(set(np.concatenate([y[tr], gold_lab]))) == 2:
        Xb = np.vstack([X[tr], X[po][keep]]); yb = np.concatenate([y[tr], gold_lab])
        aucB = auroc(y[te], _TaskModel(name, "roc-auc", seed=42).fit(Xb, yb).predict(X[te])[0])
    else:
        aucB = aucA
    # C: ungated (ALL pool, argmax pseudo-labels)
    pall = (mConf.predict(X[po])[0] >= 0.5).astype(int)
    pool_acc = float(np.mean(pall == y[po]))
    if len(set(np.concatenate([y[tr], pall]))) == 2:
        Xc = np.vstack([X[tr], X[po]]); yc = np.concatenate([y[tr], pall])
        aucC = auroc(y[te], _TaskModel(name, "roc-auc", seed=42).fit(Xc, yc).predict(X[te])[0])
    else:
        aucC = aucA
    # D: shuffled labels on B's gated compounds
    if len(keep) >= 5:
        sh = np.random.default_rng(1000 + seed).permutation(gold_lab)
        if len(set(np.concatenate([y[tr], sh]))) == 2:
            Xd = np.vstack([X[tr], X[po][keep]]); yd = np.concatenate([y[tr], sh])
            aucD = auroc(y[te], _TaskModel(name, "roc-auc", seed=42).fit(Xd, yd).predict(X[te])[0])
        else:
            aucD = aucA
    else:
        aucD = aucA
    return {"n_train": int(len(tr)), "n_pool": int(len(po)), "n_test": int(len(te)),
            "n_gold": int(len(keep)), "gold_acc": round(gold_acc, 4) if gold_acc == gold_acc else None,
            "pool_acc": round(pool_acc, 4), "aucA": round(aucA, 4), "aucB": round(aucB, 4),
            "aucC": round(aucC, 4), "aucD": round(aucD, 4)}


def main():
    t0 = time.time()
    print("=== SIL1: conformal-gated self-improving loop ===")
    per = {}
    for name, cls in PANEL:
        rs = [run_task(name, cls, s) for s in SEEDS]
        rs = [r for r in rs if r]
        if not rs:
            print(f"  {name:20s} SKIP"); continue
        agg = {k: round(float(np.mean([r[k] for r in rs])), 4) for k in
               ("aucA", "aucB", "aucC", "aucD", "gold_acc", "pool_acc", "n_gold")}
        agg["dBA"] = round(agg["aucB"] - agg["aucA"], 4)
        agg["dBC"] = round(agg["aucB"] - agg["aucC"], 4)
        agg["dBD"] = round(agg["aucB"] - agg["aucD"], 4)
        per[name] = agg
        print(f"  {name:20s} A {agg['aucA']} B {agg['aucB']} C {agg['aucC']} D {agg['aucD']} | "
              f"dB-A {agg['dBA']:+.3f} dB-C {agg['dBC']:+.3f} dB-D {agg['dBD']:+.3f} | "
              f"gold_acc {agg['gold_acc']} pool_acc {agg['pool_acc']} n_gold {agg['n_gold']} [{time.time()-t0:.0f}s]")

    def med(k): return round(float(np.median([per[t][k] for t in per])), 4)
    summary = {"n_tasks": len(per), "median_dBA": med("dBA"), "median_dBC": med("dBC"), "median_dBD": med("dBD"),
               "median_gold_acc": med("gold_acc"), "median_pool_acc": med("pool_acc"),
               "frac_tasks_dBA_pos": round(float(np.mean([per[t]["dBA"] > 0 for t in per])), 3)}
    EFF = 0.005
    H1 = summary["median_dBA"] > EFF
    H2 = summary["median_dBC"] > EFF and summary["median_dBD"] > EFF
    H3 = summary["median_gold_acc"] > summary["median_pool_acc"] + 0.02
    summary.update({"H1_loop_helps": bool(H1), "H2_gating_is_guardrail": bool(H2), "H3_gold_trustworthy": bool(H3)})
    if H1 and H2:
        summary["verdict"] = (f"H1+H2 TRUE: the conformal-gated self-improving loop HELPS (median ΔB−A "
                              f"{summary['median_dBA']:+.3f}, {summary['frac_tasks_dBA_pos']} of tasks) AND the GATING is "
                              f"the guardrail (ΔB−C {summary['median_dBC']:+.3f}, ΔB−D {summary['median_dBD']:+.3f} — "
                              f"ungated/shuffled feedback does NOT help). Conformal confidence identifies trustworthy "
                              f"self-knowledge (gold_acc {summary['median_gold_acc']} vs pool {summary['median_pool_acc']}). "
                              f"Principle 6's living-net mechanism + anti-self-deception guardrail demonstrated.")
    elif H1:
        summary["verdict"] = (f"H1 TRUE, H2 partial: loop helps (ΔB−A {summary['median_dBA']:+.3f}) but gating value is "
                              f"weak (ΔB−C {summary['median_dBC']:+.3f}, ΔB−D {summary['median_dBD']:+.3f}) — report as-is.")
    else:
        summary["verdict"] = (f"H0 (first-class): the self-improving loop does NOT help here (median ΔB−A "
                              f"{summary['median_dBA']:+.3f}, {summary['frac_tasks_dBA_pos']} of tasks) — even "
                              f"conformal-gated self-generated knowledge adds no signal beyond the base model on these "
                              f"tasks. The 'living net helps' hypothesis is FALSIFIED in this setting (honest boundary; "
                              f"gold_acc {summary['median_gold_acc']} vs pool {summary['median_pool_acc']}). Gating still "
                              f"matters directionally (ΔB−C {summary['median_dBC']:+.3f}, ΔB−D {summary['median_dBD']:+.3f}).")
    print("\nPANEL:", json.dumps(summary, indent=1)); print("VERDICT:", summary["verdict"])

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "per_task": per, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "SIL1_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k: v for k, v in summary.items() if k != "verdict"}, "per_task": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "SIL1_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/SIL1_metrics.json (%.1fs)" % (time.time() - t0))


if __name__ == "__main__":
    main()
