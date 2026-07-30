"""B30b — validate the ADMET applicability-domain flag + calibrated conformal uncertainty. Implements
prereg/B30b_admet_uncertainty.md. Same features/model as B30 (Morgan+physchem GBT). Official TDC 5-seed protocol:
train on `train`, calibrate inductive conformal on `valid`, evaluate on the scaffold `test`. Deterministic ->
reproduce x2 byte-identical (payload; provenance timestamp/git_sha aside).
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
import warnings; warnings.filterwarnings("ignore")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from scipy import stats

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta.admet import featurize, _TaskModel, TASK_METRIC, CLASSIFICATION_METRICS, NBITS
from intercepta.metrics import bh_fdr

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
TDC_DIR = os.path.join(DATA, "tdc_admet")
SEEDS = [1, 2, 3, 4, 5]
LEVELS = {"90": 0.10, "80": 0.20}

from tdc.benchmark_group import admet_group
group = admet_group(path=TDC_DIR)
TASKS = list(group.dataset_names)

_CACHE = {}
def feat(smiles):
    todo = [s for s in smiles if s not in _CACHE]
    if todo:
        X, _ = featurize(todo)
        for s, row in zip(todo, X):
            _CACHE[s] = row
    return np.vstack([_CACHE[s] for s in smiles]).astype(np.float32)


def conf_quantile(scores, alpha):
    """Inductive-conformal (1-alpha) quantile with finite-sample correction. inf if calibration too small."""
    n = len(scores)
    k = int(np.ceil((n + 1) * (1 - alpha)))
    if k > n:
        return np.inf
    return float(np.sort(scores)[k - 1])


def run_task(task):
    metric = TASK_METRIC[task]
    is_clf = metric in CLASSIFICATION_METRICS
    b = group.get(task)
    test = b["test"]; Xte = feat(test["Drug"].tolist()); yte = test["Y"].values.astype(float)
    # accumulators
    a1_ood, a1_ind = [], []                                   # Aim1 per-seed OOD/in-domain mean error
    err_all, ad_all = [], []                                  # Aim1 pooled (err, AD-distance) for per-task Spearman
    cov = {lv: [] for lv in LEVELS}; wid = {lv: [] for lv in LEVELS}          # plain conformal
    covM = {lv: [] for lv in LEVELS}; widhi = {lv: [] for lv in LEVELS}       # Mondrian (AD-binned)
    setsz = {lv: [] for lv in LEVELS}
    for seed in SEEDS:
        tr, va = group.get_train_valid_split(benchmark=task, split_type="default", seed=seed)
        Xtr = feat(tr["Drug"].tolist()); ytr = tr["Y"].values.astype(float)
        tm = _TaskModel(task, metric, seed=42).fit(Xtr, ytr)
        # predictions + AD distance (1 - max Tanimoto to train) for valid (calibration) and test
        pv, adv, _ = tm.predict(feat(va["Drug"].tolist())); yv = va["Y"].values.astype(float)
        pt, adt, indom = tm.predict(Xte)

        # ---- Aim 1: does test error rise with AD distance? ----
        err_t = np.abs(yte - pt)
        err_all.append(err_t); ad_all.append(adt)
        a1_ood.append(float(np.mean(err_t[~indom])) if (~indom).any() else np.nan)
        a1_ind.append(float(np.mean(err_t[indom])) if indom.any() else np.nan)

        # nonconformity scores on calibration (valid)
        if is_clf:
            proba = tm.model_.predict_proba(tm._split_impute(feat(va["Drug"].tolist())))  # (nv,2)
            yv_int = yv.astype(int)
            s_cal = 1.0 - proba[np.arange(len(yv_int)), yv_int]
            proba_t = tm.model_.predict_proba(tm._split_impute(Xte))
        else:
            s_cal = np.abs(yv - pv)

        # AD tertile edges from calibration (for Mondrian)
        edges = np.quantile(adv, [1/3, 2/3])
        def adbin(a): return np.digitize(a, edges)     # 0,1,2
        cbin = adbin(adv); tbin = adbin(adt)

        for lv, alpha in LEVELS.items():
            q = conf_quantile(s_cal, alpha)
            # Mondrian per-bin quantiles
            qbin = {}
            for bnum in (0, 1, 2):
                sc = s_cal[cbin == bnum]
                qbin[bnum] = conf_quantile(sc, alpha) if len(sc) >= 10 else q
            qt_m = np.array([qbin[bb] for bb in tbin])
            if is_clf:
                # LAC prediction set coverage: true label in set iff (1 - p_true) <= q
                s_true_t = 1.0 - proba_t[np.arange(len(yte)), yte.astype(int)]
                cov[lv].append(float(np.mean(s_true_t <= q)))
                covM[lv].append(float(np.mean(s_true_t <= qt_m)))
                # mean set size (plain)
                sz = (1.0 - proba_t <= q).sum(1)
                setsz[lv].append(float(np.mean(sz)))
            else:
                cov[lv].append(float(np.mean(err_t <= q)))
                wid[lv].append(2.0 * q if np.isfinite(q) else np.nan)
                covM[lv].append(float(np.mean(err_t <= qt_m)))
                # width in high-AD bin vs low-AD bin (Mondrian): report high-bin width
                widhi[lv].append(2.0 * qbin[2] if np.isfinite(qbin[2]) else np.nan)

    # pre-registered H1a test: per-task Spearman(error, AD-distance), pooled over the 5 seeds' test predictions.
    # (pooling repeats the fixed test set 5x -> the p-value is anti-conservative; adjudication also uses effect
    #  size (rho) and BH-FDR across the 22 tasks, per prereg.)
    ea = np.concatenate(err_all); aa = np.concatenate(ad_all)
    rho, pval = stats.spearmanr(ea, aa)
    out = {"metric": metric, "kind": "classification" if is_clf else "regression",
           "aim1_spearman_err_vs_ad": round(float(rho) if np.isfinite(rho) else 0.0, 4),
           "aim1_spearman_p_pooled": float(pval) if np.isfinite(pval) else 1.0,
           "aim1_mean_err_ood": round(float(np.nanmean(a1_ood)), 4),
           "aim1_mean_err_in_domain": round(float(np.nanmean(a1_ind)), 4)}
    for lv in LEVELS:
        out[f"cov{lv}"] = round(float(np.mean(cov[lv])), 4)
        out[f"cov{lv}_mondrian"] = round(float(np.mean(covM[lv])), 4)
        if is_clf:
            out[f"setsize{lv}"] = round(float(np.mean(setsz[lv])), 3)
        else:
            out[f"width{lv}"] = round(float(np.nanmean(wid[lv])), 4)
            out[f"width{lv}_mondrian_highADbin"] = round(float(np.nanmean(widhi[lv])), 4)
    return out


def main():
    res = {t: run_task(t) for t in TASKS}
    for i, (t, r) in enumerate(res.items(), 1):
        print(f"[{i:2d}/22] {t:34s} {r['kind'][:4]:4s} AD-rho {r['aim1_spearman_err_vs_ad']:+.3f} "
              f"(err ood {r['aim1_mean_err_ood']:.3f} vs in {r['aim1_mean_err_in_domain']:.3f}) | "
              f"cov90 {r['cov90']:.3f} (mondrian {r['cov90_mondrian']:.3f})")

    reg = [r for r in res.values() if r["kind"] == "regression"]
    clf = [r for r in res.values() if r["kind"] == "classification"]

    # ---- Aim 1 verdict (pre-registered test: per-task Spearman(error, AD-distance) -> BH-FDR across tasks) ----
    rhos = np.array([r["aim1_spearman_err_vs_ad"] for r in res.values()])
    pvals = np.array([r["aim1_spearman_p_pooled"] for r in res.values()])
    bhq = bh_fdr(pvals)
    for (t, r), q in zip(res.items(), bhq):
        r["aim1_spearman_bh_q"] = round(float(q), 5)
    n_pos = int(np.sum(rhos > 0))                                   # H1a direction
    n_pos_sig = int(np.sum((rhos > 0) & (bhq < 0.05)))              # H1a: positive AND BH-FDR significant
    ood = np.array([r["aim1_mean_err_ood"] for r in res.values()])
    ind = np.array([r["aim1_mean_err_in_domain"] for r in res.values()])
    n_ood_worse = int(np.sum(ood > ind))                           # H1b binary-flag separation
    try:
        w_p = float(stats.wilcoxon(ood, ind, alternative="greater")[1])   # one-sided: OOD error > in-domain
    except Exception:
        w_p = float("nan")
    h1a = (n_pos >= 16 and n_pos_sig >= 12)                         # continuous AD signal (majority, BH-significant)
    h1b = (n_ood_worse >= 16 and np.isfinite(w_p) and w_p < 0.05)   # binary 95th-pct flag separates error
    if h1a and h1b:
        verdict = ("AD VALIDATED — error rises with AD distance across the majority of tasks (BH-FDR<0.05) AND the "
                   "binary OOD flag separates high- from low-error molecules. Applicability domain is an informative "
                   "reliability signal; usable as a gate.")
    elif h1a:
        verdict = ("AD is a REAL but WEAK/soft reliability signal — per-molecule error rises with AD distance in the "
                   f"majority of tasks ({n_pos}/22 positive, {n_pos_sig}/22 BH-FDR<0.05, mean Spearman "
                   f"{float(np.mean(rhos)):+.3f}), so AD DISTANCE is a validated continuous reliability weight. The "
                   f"specific binary 95th-percentile OOD flag is a WEAKER separator ({n_ood_worse}/22 tasks OOD-worse, "
                   f"one-sided Wilcoxon p={w_p:.3f}) — kept as a soft confidence weight, NOT a hard gate. Honest "
                   "effect-size call: informative but weak.")
    else:
        verdict = ("AD NULL — error does not rise with AD distance after BH-FDR; the flag is demoted to descriptive "
                   "only (cf. B6/V13 reliability).")
    aim1 = {"n_tasks_error_rises_with_AD": n_pos, "n_tasks_AD_rho_BH_significant": n_pos_sig,
            "n_tasks_OOD_error_worse": n_ood_worse, "mean_AD_rho": round(float(np.mean(rhos)), 4),
            "wilcoxon_OOD_gt_indomain_p_onesided": round(w_p, 5),
            "H1a_continuous_AD_signal": bool(h1a), "H1b_binary_flag_separates": bool(h1b), "verdict": verdict}

    def agg_cov(group_list, lv):
        c = np.array([r[f"cov{lv}"] for r in group_list]); cm = np.array([r[f"cov{lv}_mondrian"] for r in group_list])
        return round(float(np.mean(c)), 4), round(float(np.mean(cm)), 4)
    conformal = {"regression": {}, "classification": {}}
    for lv in LEVELS:
        nominal = round(1 - LEVELS[lv], 2)
        rc, rcm = agg_cov(reg, lv); cc, ccm = agg_cov(clf, lv)
        conformal["regression"][f"nominal_{lv}"] = {"nominal": nominal, "mean_coverage_plain": rc,
            "mean_coverage_mondrian": rcm, "mean_width_plain": round(float(np.nanmean([r[f"width{lv}"] for r in reg])), 4)}
        conformal["classification"][f"nominal_{lv}"] = {"nominal": nominal, "mean_coverage_plain": cc,
            "mean_coverage_mondrian": ccm, "mean_set_size_plain": round(float(np.mean([r[f"setsize{lv}"] for r in clf])), 3)}

    def cov_ok(section):
        return all(abs(section[f"nominal_{lv}"]["mean_coverage_plain"] - (1 - LEVELS[lv])) <= 0.05 for lv in LEVELS)
    def cov_ok_m(section):
        return all(abs(section[f"nominal_{lv}"]["mean_coverage_mondrian"] - (1 - LEVELS[lv])) <= 0.05 for lv in LEVELS)
    summary = {
        "aim1_applicability_domain": aim1,
        "aim2_3_conformal_coverage": {
            "regression_plain_calibrated_within_0.05": bool(cov_ok(conformal["regression"])),
            "regression_mondrian_within_0.05": bool(cov_ok_m(conformal["regression"])),
            "classification_plain_within_0.05": bool(cov_ok(conformal["classification"])),
            "classification_mondrian_within_0.05": bool(cov_ok_m(conformal["classification"])),
        },
        "honest_note": ("Scaffold test is OOD vs the in-distribution valid calibration set (exchangeability violated), "
                        "so plain conformal can under-cover; AD-conditioned (Mondrian) conformal widens intervals for "
                        "out-of-domain molecules to recover coverage. Coverage reported as measured, either way."),
    }

    prov = {"experiment": "B30b_admet_uncertainty", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "seeds": SEEDS,
            "protocol": "train on train, calibrate inductive conformal on valid, coverage on scaffold test; 5 seeds mean",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    full = {"provenance": prov, "summary": summary, "conformal": conformal, "tasks": res}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(full, open(os.path.join(HERE, "results", "B30b_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary, "conformal": conformal, "tasks": res}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B30b_payload.sha256"), "w").write(digest + "\n")

    print("\n== Aim 1 (AD validity) ==", json.dumps(aim1, indent=1))
    print("== Aim 2/3 (conformal coverage) =="); print(json.dumps(conformal, indent=1))
    print("== summary flags ==", json.dumps(summary["aim2_3_conformal_coverage"]))
    print("payload sha256:", digest); print("wrote results/B30b_metrics.json")


def _libvers():
    import sklearn, scipy, numpy, rdkit, importlib.metadata as m
    try: tdcv = m.version("PyTDC")
    except Exception: tdcv = "unknown"
    return {"numpy": numpy.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__, "rdkit": rdkit.__version__, "PyTDC": tdcv}


if __name__ == "__main__":
    main()
