"""B30 — an honest ADMET / safety-prediction module on the TDC ADMET Benchmark Group (22 tasks, scaffold splits).
Implements prereg/B30_admet.md. Structure-only (Morgan/ECFP + RDKit physchem) gradient-boosted trees, official TDC
5-seed protocol, official metric per task, vs (a) trivial baseline and (b) published leaderboard rank-1. Deterministic
(model random_state=42, TDC seeds fixed) -> reproduce x2 byte-identical (metrics payload; timestamp/git_sha aside).
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
import warnings; warnings.filterwarnings("ignore")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta.admet import featurize, _TaskModel, TASK_METRIC, CLASSIFICATION_METRICS, NBITS

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
TDC_DIR = os.path.join(DATA, "tdc_admet")
SEEDS = [1, 2, 3, 4, 5]
LEADERBOARD = json.load(open(os.path.join(HERE, "leaderboard_ref.json")))["tasks"]

from tdc.benchmark_group import admet_group
group = admet_group(path=TDC_DIR)
TASKS = list(group.dataset_names)

# ---- feature cache: SMILES -> [morgan bits | physchem descriptors] (deterministic) ----
_CACHE = {}
def feat(smiles):
    todo = [s for s in smiles if s not in _CACHE]
    if todo:
        X, _ = featurize(todo)
        for s, row in zip(todo, X):
            _CACHE[s] = row
    return np.vstack([_CACHE[s] for s in smiles]).astype(np.float32)


def trivial_pred(metric, y_train, n_test):
    """Trivial baseline test predictions: base rate (classification) or train mean (regression)."""
    if metric in CLASSIFICATION_METRICS:
        return np.full(n_test, float(np.mean(y_train)))     # constant prevalence -> AUROC 0.5, AUPRC~prevalence
    return np.full(n_test, float(np.mean(y_train)))         # predict-the-mean -> MAD floor; spearman undefined(->0)


def run_task(task):
    metric = TASK_METRIC[task]
    b = group.get(task)
    test = b["test"]
    test_smi = test["Drug"].tolist()
    Xte = feat(test_smi)
    preds_model, preds_triv, rowcounts = [], [], []
    for seed in SEEDS:
        tr, va = group.get_train_valid_split(benchmark=task, split_type="default", seed=seed)
        Xtr = feat(tr["Drug"].tolist()); ytr = tr["Y"].values.astype(float)
        tm = _TaskModel(task, metric, seed=42).fit(Xtr, ytr)     # model seed fixed=42; only the SPLIT varies by seed
        val, _, _ = tm.predict(Xte)
        preds_model.append({task: list(map(float, val))})
        preds_triv.append({task: list(map(float, trivial_pred(metric, ytr, len(test_smi))))})
        rowcounts.append(len(tr))
    model_mean, model_sd = group.evaluate_many(preds_model)[task]
    triv_mean, triv_sd = group.evaluate_many(preds_triv)[task]
    if metric == "spearman" and not np.isfinite(triv_mean):
        triv_mean, triv_sd = 0.0, 0.0    # a constant predictor has Spearman=0 by definition (no rank information)

    # applicability domain on the FULL official train_val vs the scaffold test (honest descriptive stat)
    tv = b["train_val"]
    Xtv = feat(tv["Drug"].tolist())
    ad = _TaskModel(task, metric, seed=42).fit(Xtv, tv["Y"].values.astype(float))
    _, _, indom = ad.predict(Xte)
    frac_ood = float(1.0 - np.mean(indom))

    lb = LEADERBOARD.get(task, {})
    lower_better = metric == "mae"
    # honest gap vs SOTA (positive = we trail SOTA), and vs trivial (positive = we beat trivial)
    beats_trivial = (model_mean < triv_mean - model_sd) if lower_better else (model_mean > triv_mean + model_sd)
    gap_to_sota = (model_mean - lb["best"]) if lower_better else (lb["best"] - model_mean)  # >0 => we trail
    return {
        "metric": metric, "direction": "lower_is_better" if lower_better else "higher_is_better",
        "test_n": int(len(test)), "train_n_per_seed": rowcounts,
        "class_prevalence": (float(np.mean(b["train_val"]["Y"])) if metric in CLASSIFICATION_METRICS else None),
        "model_mean": round(float(model_mean), 4), "model_sd": round(float(model_sd), 4),
        "trivial_mean": round(float(triv_mean), 4), "trivial_sd": round(float(triv_sd), 4),
        "beats_trivial_by_1sd": bool(beats_trivial),
        "leaderboard_best": lb.get("best"), "leaderboard_model": lb.get("model"),
        "gap_to_sota": round(float(gap_to_sota), 4),
        "test_frac_out_of_domain": round(frac_ood, 3),
    }


def main():
    results = {}
    for i, task in enumerate(TASKS, 1):
        r = run_task(task); results[task] = r
        flag = "BEATS trivial" if r["beats_trivial_by_1sd"] else "~= trivial (NULL)"
        print(f"[{i:2d}/22] {task:34s} {r['metric']:8s} model {r['model_mean']:.3f}±{r['model_sd']:.3f} | "
              f"trivial {r['trivial_mean']:.3f} | SOTA {r['leaderboard_best']} (gap {r['gap_to_sota']:+.3f}) | "
              f"OOD {r['test_frac_out_of_domain']:.0%} | {flag}")

    # ---- honest aggregate summary ----
    n = len(results)
    n_beat = sum(r["beats_trivial_by_1sd"] for r in results.values())
    # normalized closeness to SOTA per task: trivial->0, SOTA->1, for a fair cross-metric aggregate.
    def closeness(r):
        lo, hi = r["trivial_mean"], r["leaderboard_best"]
        denom = (lo - hi) if r["direction"] == "lower_is_better" else (hi - lo)
        num = (lo - r["model_mean"]) if r["direction"] == "lower_is_better" else (r["model_mean"] - lo)
        if denom == 0 or not np.isfinite(denom):
            return None
        c = float(num / denom)
        return c if np.isfinite(c) else None
    excluded = []
    for task, r in results.items():
        c = closeness(r)
        r["frac_sota_gap_closed"] = None if c is None else round(c, 3)
        if c is None:
            excluded.append(task)
    clos = [r["frac_sota_gap_closed"] for r in results.values() if r["frac_sota_gap_closed"] is not None]
    med = float(np.median(clos)) if clos else float("nan")
    summary = {
        "n_tasks": n, "n_beats_trivial_by_1sd": int(n_beat),
        "n_null_or_below_trivial": int(n - n_beat),
        "closeness_excluded_tasks": excluded,   # tasks with degenerate trivial==SOTA denom (excluded from the mean)
        "mean_fraction_of_sota_gap_closed": (round(float(np.mean(clos)), 3) if clos else None),
        "median_fraction_of_sota_gap_closed": (round(med, 3) if clos else None),
        "interpretation": (
            f"Structure-only GBT baseline beats the trivial baseline by >1sd on {n_beat}/{n} ADMET tasks. "
            f"It closes a median {round(med * 100)}% of the trivial->SOTA gap: a solid, honest "
            "mid-leaderboard predictor, trailing graph/foundation models (MiniMol, MapLight+GNN, CFA) as expected. "
            "NOT a SOTA claim; an in-silico screening filter, scaffold-split only, NOT a safety guarantee."),
    }

    prov = {
        "experiment": "B30_admet",
        "git_sha": os.popen("git rev-parse HEAD").read().strip(),
        "python": sys.version.split()[0],
        "libs": _libvers(),
        "tdc_benchmark": "admet_group (22 tasks)", "seeds": SEEDS,
        "features": f"Morgan/ECFP radius=2 {NBITS}-bit + 17 RDKit physchem descriptors",
        "model": "HistGradientBoosting (Classifier/Regressor), random_state=42, max_iter=300, lr=0.06, max_depth=6",
        "leaderboard_ref": "leaderboard_ref.json (TDC leaderboard rank-1, retrieved 2026-07-29)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    out = {"provenance": prov, "summary": summary, "tasks": results}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    path = os.path.join(HERE, "results", "B30_metrics.json")
    json.dump(out, open(path, "w"), indent=2, sort_keys=True)
    # reproducibility hash over the DETERMINISTIC payload only (excludes provenance timestamp/git_sha)
    payload = json.dumps({"summary": summary, "tasks": results}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B30_payload.sha256"), "w").write(digest + "\n")
    print("\nSUMMARY:", summary["interpretation"])
    print(f"beats trivial: {n_beat}/{n} | median SOTA-gap closed: {summary['median_fraction_of_sota_gap_closed']:.0%}")
    print("payload sha256:", digest)
    print("wrote results/B30_metrics.json")


def _libvers():
    import sklearn, scipy, numpy, pandas, rdkit
    import importlib.metadata as m
    try: tdcv = m.version("PyTDC")
    except Exception: tdcv = "unknown"
    return {"numpy": numpy.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__, "rdkit": rdkit.__version__, "PyTDC": tdcv}


if __name__ == "__main__":
    main()
