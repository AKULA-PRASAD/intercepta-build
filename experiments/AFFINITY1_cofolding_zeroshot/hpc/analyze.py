#!/usr/bin/env python3
"""AFFINITY1 statistical analysis (Phase 6). Publication-grade, self-contained (numpy+pandas).

Reads  $INTERCEPTA_DATA/affinity1/scored.csv  (written by `run.py score`)
Emits  results/AFFINITY1_stats.json  with, for each score (Boltz affval, Boltz probbin, docking):
  - observed AUROC + paired bootstrap 95% CI (B=10000, seed 42)
  - Delta AUROC (Boltz - docking) with paired bootstrap CI + one-sided p(Boltz>docking)
  - per split: overall / analog-actives-vs-inactives / novel-actives-vs-inactives (n flagged)
Honest guard: any split with < 10 positives is tagged UNDERPOWERED (the n=5 novel split).
"""
import os, json, hashlib
import numpy as np, pandas as pd

WORK = os.path.join(os.environ["INTERCEPTA_DATA"], "affinity1")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)
DOCK_BASE = 0.4285   # HIT2 full-set docking overall AUROC (fixed baseline of record)
B, SEED = 10000, 42

def auroc(score, y):
    s = np.asarray(score, float); y = np.asarray(y, int)
    m = ~np.isnan(s); s, y = s[m], y[m]
    npos, nneg = int(y.sum()), int((y == 0).sum())
    if npos == 0 or nneg == 0: return np.nan
    order = np.argsort(s, kind="mergesort"); ranks = np.empty(len(s)); ranks[order] = np.arange(1, len(s)+1)
    df = pd.DataFrame({"s": s, "r": ranks}); ranks = df.groupby("s")["r"].transform("mean").values
    return float((ranks[y == 1].sum() - npos*(npos+1)/2.0) / (npos*nneg))

def boot_ci(score, y, B=B, seed=SEED):
    s = np.asarray(score, float); y = np.asarray(y, int); n = len(y)
    rng = np.random.default_rng(seed); out = []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        a = auroc(s[idx], y[idx])
        if not np.isnan(a): out.append(a)
    out = np.array(out)
    return float(np.nanmean(out)), [float(np.percentile(out,2.5)), float(np.percentile(out,97.5))]

def delta_vs_docking(model_score, dock_score, y, B=B, seed=SEED):
    s1 = np.asarray(model_score,float); s0 = np.asarray(dock_score,float); y = np.asarray(y,int); n=len(y)
    rng = np.random.default_rng(seed); d = []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        a1, a0 = auroc(s1[idx], y[idx]), auroc(s0[idx], y[idx])
        if not (np.isnan(a1) or np.isnan(a0)): d.append(a1 - a0)
    d = np.array(d)
    return {"delta_mean": float(np.mean(d)),
            "delta_ci95": [float(np.percentile(d,2.5)), float(np.percentile(d,97.5))],
            "p_one_sided_boltz_gt_docking": float(np.mean(d <= 0))}

def split_block(df, name):
    y = df.active.values
    aff = -df.aff_pred_value.values          # higher = stronger binder
    prob = df.aff_prob_binary.values
    dock = -df.vina.values
    npos, nneg = int(y.sum()), int((y==0).sum())
    blk = {"n": int(len(df)), "n_pos": npos, "n_neg": nneg,
           "UNDERPOWERED": bool(npos < 10),
           "auroc_boltz_affval":  dict(zip(["auroc","ci95"], boot_ci(aff, y))),
           "auroc_boltz_probbin": dict(zip(["auroc","ci95"], boot_ci(prob, y))),
           "auroc_docking":       dict(zip(["auroc","ci95"], boot_ci(dock, y))),
           "delta_affval_vs_docking":  delta_vs_docking(aff, dock, y),
           "delta_probbin_vs_docking": delta_vs_docking(prob, dock, y)}
    return blk

def main():
    d = pd.read_csv(os.path.join(WORK, "scored.csv"))
    d = d[~d.aff_pred_value.isna()].copy()
    ina = d[d.active == 0]
    res = {
        "n_scored": int(len(d)),
        "docking_baseline_of_record": DOCK_BASE,
        "bootstrap": {"B": B, "seed": SEED},
        "overall": split_block(d, "overall"),
        "analog_actives_vs_inactives": split_block(pd.concat([d[(d.active==1)&(d.novelty=='analog')], ina]), "analog"),
        "novel_actives_vs_inactives":  split_block(pd.concat([d[(d.active==1)&(d.novelty=='novel')],  ina]), "novel"),
        "note": ("Decisive number = OVERALL AUROC vs docking (well powered). Novel split is reported "
                 "with CI but is UNDERPOWERED (n_pos flagged) and must NOT drive the verdict alone."),
    }
    blob = json.dumps(res, sort_keys=True, separators=(",",":")).encode()
    res["sha256"] = hashlib.sha256(blob).hexdigest()
    with open(os.path.join(RES, "AFFINITY1_stats.json"), "w") as f:
        json.dump(res, f, sort_keys=True, indent=2)
    o = res["overall"]
    print("OVERALL n=%d  Boltz(affval)=%.3f CI%s  Boltz(prob)=%.3f  docking=%.3f  base=%.4f" % (
        o["n"], o["auroc_boltz_affval"]["auroc"], o["auroc_boltz_affval"]["ci95"],
        o["auroc_boltz_probbin"]["auroc"], o["auroc_docking"]["auroc"], DOCK_BASE))
    print("Delta(affval-docking)=%s  p(boltz>docking)=%.4f" % (
        o["delta_affval_vs_docking"]["delta_ci95"], o["delta_affval_vs_docking"]["p_one_sided_boltz_gt_docking"]))
    print("wrote results/AFFINITY1_stats.json sha=%s" % res["sha256"])

if __name__ == "__main__":
    main()
