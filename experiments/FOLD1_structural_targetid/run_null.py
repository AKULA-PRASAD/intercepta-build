"""FOLD1 structural-conservation NULL analysis — the specificity test for the FOLD1 modest positive.

Joins scores.tsv (best structural TM to reference TARGETS) with scores_null.tsv (best structural TM to a matched
random NON-target reference) on (pathogen, uniprot). Decisive question: is the FOLD1 structural signal SPECIFIC to
target-homology, or just generic "target-like fold" similarity that any protein-vs-many-references would produce?

Metrics per pathogen + pooled:
  - AUROC(TM-to-targets) vs AUROC(TM-to-nontargets) for target discrimination. If target-ref discriminates targets
    BETTER than a same-size non-target ref, the signal is target-SPECIFIC (survives the null). If ~equal, it is
    generic fold similarity (the TID1 critique applies -> the FOLD1 positive is an artifact, keep provider quarantined).
  - Paired margin on isolated-pathogen TARGETS: mean(TM-to-targets - TM-to-nontargets). Positive => targets are more
    structurally similar to OTHER targets than to random proteins (specific).
Deterministic; reproduced x2. Env: intercepta-build.
"""
import os, json, time, hashlib
import numpy as np
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
SCORES = os.path.join(DATA, "fold1", "scores.tsv")
NULLSC = os.path.join(DATA, "fold1", "scores_null.tsv")
DELTA = 0.02   # minimum AUROC advantage of target-ref over non-target-ref to call the signal target-specific


def auroc(y, s):
    y = np.asarray(y)
    return round(float(roc_auc_score(y, s)), 4) if 0 < y.sum() < len(y) else float("nan")


def main():
    t0 = time.time()
    tgt_tm = {}
    for ln in open(SCORES).read().splitlines()[1:]:
        r = ln.split("\t")
        if len(r) < 6: continue
        tgt_tm[(r[0], r[1])] = (int(r[2]), float(r[5]))            # (is_target, TM-to-targets)
    null_tm = {}
    for ln in open(NULLSC).read().splitlines()[1:]:
        r = ln.split("\t")
        if len(r) < 5: continue
        null_tm[(r[0], r[1])] = float(r[4])                        # TM-to-nontargets

    per = {}; pooled = []
    for (X, a), (y, tmt) in tgt_tm.items():
        if (X, a) not in null_tm: continue
        per.setdefault(X, []).append((y, tmt, null_tm[(X, a)]))
        pooled.append((y, tmt, null_tm[(X, a)]))

    def block(rows):
        y = np.array([r[0] for r in rows]); tmt = np.array([r[1] for r in rows]); tmn = np.array([r[2] for r in rows])
        tgt_margin = [r[1] - r[2] for r in rows if r[0] == 1]      # per-target (TM-to-targets - TM-to-nontargets)
        return {"n": len(rows), "n_targets": int(y.sum()),
                "AUROC_TM_to_targets": auroc(y, tmt), "AUROC_TM_to_nontargets": auroc(y, tmn),
                "mean_target_margin": round(float(np.mean(tgt_margin)), 4) if tgt_margin else float("nan")}

    for X in per: per[X] = block(per[X])
    pool = block(pooled)
    d_auroc = round(pool["AUROC_TM_to_targets"] - pool["AUROC_TM_to_nontargets"], 4)
    # consistency: target-ref AUROC exceeds non-target-ref AUROC in every pathogen
    consistent = all(per[X]["AUROC_TM_to_targets"] > per[X]["AUROC_TM_to_nontargets"] for X in per)
    specific = (d_auroc > DELTA) and consistent and pool["mean_target_margin"] > 0

    summary = {"pathogens": list(per), "pooled": pool, "delta_AUROC_targets_minus_nontargets": d_auroc,
               "consistent_across_pathogens": bool(consistent),
               "structural_signal_is_target_specific": bool(specific)}
    if specific:
        summary["verdict"] = (f"NULL SURVIVED — the FOLD1 structural signal is TARGET-SPECIFIC, not generic fold similarity: "
                              f"structure-to-reference-TARGETS discriminates isolated-pathogen targets better than a matched "
                              f"random NON-target reference (pooled AUROC {pool['AUROC_TM_to_targets']} vs "
                              f"{pool['AUROC_TM_to_nontargets']}, delta +{d_auroc}, consistent across all pathogens={consistent}), "
                              f"and targets are on average structurally closer to OTHER targets than to random proteins "
                              f"(mean per-target margin +{pool['mean_target_margin']}). So structural homology to known targets "
                              f"is a genuine specific signal for isolated-pathogen target-ID -> PROMOTE StructuralHomologyProvider "
                              f"to OWN_REPRODUCED. Caveats unchanged: modest effect; Foldseek TM; AlphaFold predicted structures; "
                              f"hypotheses, not validated targets; not wet-lab.")
    else:
        summary["verdict"] = (f"NULL NOT SURVIVED — the FOLD1 structural signal is largely GENERIC fold similarity, not specific "
                              f"target-homology: a matched random NON-target reference discriminates targets about as well as the "
                              f"target reference (pooled AUROC targets {pool['AUROC_TM_to_targets']} vs non-targets "
                              f"{pool['AUROC_TM_to_nontargets']}, delta {d_auroc}, consistent={consistent}, mean target margin "
                              f"{pool['mean_target_margin']}). This is the TID1 critique realized in structure space: 'targets have "
                              f"target-like generic folds'. The FOLD1 AUROC gain over sequence is real but is NOT specific homology "
                              f"-> KEEP StructuralHomologyProvider QUARANTINED (do NOT promote). Honest boundary recorded.")
    print("PANEL:", json.dumps({k: v for k, v in summary.items() if k != "verdict"}, indent=1))
    print("VERDICT:", summary["verdict"])
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "per_pathogen": per, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "FOLD1_null_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k: v for k, v in summary.items() if k != "verdict"}, "per_pathogen": per}, sort_keys=True)
    open(os.path.join(HERE, "results", "FOLD1_null_payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    print("payload sha256:", hashlib.sha256(payload.encode()).hexdigest(), f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
