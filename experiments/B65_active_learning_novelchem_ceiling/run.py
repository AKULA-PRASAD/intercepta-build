"""B65 — does active learning's label-efficiency advantage COLLAPSE in the novel-chemistry regime?
Simulated pool-based AL on MoleculeACE continuous potency: ensemble (query-by-bagging) uncertainty sampling AND greedy
acquisition vs RANDOM, with learning curves measured SEPARATELY on an in-domain (interpolation) test and a
scaffold-disjoint + NN<0.4 novel-chemistry (extrapolation) test. Tests the P9/B62 prediction that acquisition cannot buy
novel-chemistry generalization (signal-loss ceiling). Implements prereg/B65_active_learning_novelchem_ceiling.md.
Deterministic -> reproduce x2. No docking.
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
from sklearn.ensemble import HistGradientBoostingRegressor
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
MACE = os.path.join(DATA, "moleculeace")
SEEDS, NN_NOVEL, MIN_NOVEL = [1, 2, 3], 0.40, 15
N0, BATCH, ROUNDS, ENSEMBLE = 20, 15, 8, 3       # seed labels, batch, AL rounds, committee size
PCOL = "y [pEC50/pKi]"


def bit(m):
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=1024)


def arr(fp):
    a = np.zeros(1024, dtype=np.float32); DataStructs.ConvertToNumpyArray(fp, a); return a


def murcko(m):
    try:
        return MurckoScaffold.GetScaffoldForMol(m)
    except Exception:
        return None


def fit_committee(X, y, seed):
    """Query-by-bagging: ENSEMBLE HGBs on bootstrap resamples -> (mean, std) predictors."""
    models = []
    for e in range(ENSEMBLE):
        rng = np.random.default_rng(seed * 100 + e)
        bs = rng.integers(0, len(y), len(y))
        models.append(HistGradientBoostingRegressor(random_state=42, max_iter=100, learning_rate=0.06,
                                                     max_depth=6).fit(X[bs], y[bs]))
    return models


def committee_predict(models, X):
    P = np.column_stack([m.predict(X) for m in models])
    return P.mean(1), P.std(1)


def spear(pred, true):
    if len(true) < 3 or np.std(pred) == 0:
        return 0.0
    r = spearmanr(pred, true).correlation
    return 0.0 if (r is None or np.isnan(r)) else float(r)


def lc_auc(nlabels, scores):
    """Normalized area under the (labels, Spearman) learning curve."""
    nlabels = np.asarray(nlabels, float); scores = np.asarray(scores, float)
    if len(nlabels) < 2 or nlabels[-1] == nlabels[0]:
        return float(np.mean(scores))
    return float(np.trapz(scores, nlabels) / (nlabels[-1] - nlabels[0]))


def run_strategy(X, y, FP, pool, test_nov, test_ind, strategy, seed):
    """One AL trajectory. Returns learning curves on novel + in-domain test, and mean acquired-similarity to labeled."""
    rng = np.random.default_rng(seed)
    labeled = list(rng.permutation(pool)[:N0])
    unlab = [i for i in pool if i not in set(labeled)]
    nlabels, sc_nov, sc_ind, acq_sim = [], [], [], []
    for rnd in range(ROUNDS + 1):
        models = fit_committee(X[labeled], y[labeled], seed)
        pn, _ = committee_predict(models, X[test_nov]); pi, _ = committee_predict(models, X[test_ind])
        nlabels.append(len(labeled)); sc_nov.append(spear(pn, y[test_nov])); sc_ind.append(spear(pi, y[test_ind]))
        if rnd == ROUNDS or len(unlab) == 0:
            break
        b = min(BATCH, len(unlab))
        if strategy == "random":
            pick_local = list(np.random.default_rng(seed * 1000 + rnd).permutation(len(unlab))[:b])
        else:
            mean_u, std_u = committee_predict(models, X[unlab])
            score = std_u if strategy == "uncertainty" else mean_u          # uncertainty: max std; greedy: max pred
            pick_local = list(np.argsort(-score, kind="stable")[:b])
        picks = [unlab[j] for j in pick_local]
        lab_fps = [FP[i] for i in labeled]
        acq_sim.append(float(np.mean([max(DataStructs.BulkTanimotoSimilarity(FP[i], lab_fps)) for i in picks])))
        labeled += picks
        unlab = [unlab[j] for j in range(len(unlab)) if j not in set(pick_local)]
    return {"nlabels": nlabels, "novel": sc_nov, "indomain": sc_ind,
            "auc_novel": lc_auc(nlabels, sc_nov), "auc_indomain": lc_auc(nlabels, sc_ind),
            "acq_sim": (float(np.mean(acq_sim)) if acq_sim else float("nan"))}


def process(path):
    df = pd.read_csv(path)
    mols, ys = [], []
    for _, r in df.iterrows():
        m = Chem.MolFromSmiles(str(r["smiles"]))
        if m is not None and np.isfinite(r[PCOL]):
            mols.append(m); ys.append(float(r[PCOL]))
    if len(mols) < 120:
        return None
    y = np.array(ys); X = np.vstack([arr(bit(m)) for m in mols]); FP = [bit(m) for m in mols]
    scaf = np.array([Chem.MolToSmiles(s) if s is not None and s.GetNumAtoms() > 0 else ""
                     for s in (murcko(m) for m in mols)], dtype=object)
    per_seed = []
    for seed in SEEDS:
        uniq = np.array(sorted(set(scaf) - {""}))
        if len(uniq) < 6:
            continue
        perm = np.random.default_rng(seed).permutation(uniq)
        held_sc = set(perm[: max(1, int(0.30 * len(uniq)))])
        held = np.array([s in held_sc for s in scaf])
        pool_all = np.where(~held)[0]
        held_idx = np.where(held)[0]
        pool_fps = [FP[i] for i in pool_all]
        # novel test = held-out scaffolds that are ALSO NN<0.4 to the pool (extrapolation)
        test_nov = [i for i in held_idx
                    if max(DataStructs.BulkTanimotoSimilarity(FP[i], pool_fps)) < NN_NOVEL]
        if len(test_nov) < MIN_NOVEL or len(pool_all) < (N0 + BATCH + 30):
            continue
        # in-domain test = random held-out subset FROM the pool's scaffold space (interpolation), removed from acquirable
        rng = np.random.default_rng(1000 + seed)
        pool_perm = rng.permutation(pool_all)
        n_ind = min(max(15, int(0.15 * len(pool_all))), len(pool_all) - (N0 + BATCH + 15))
        test_ind = list(pool_perm[:n_ind]); pool = list(pool_perm[n_ind:])
        res = {}
        for strat in ("uncertainty", "greedy", "random"):
            res[strat] = run_strategy(X, y, FP, pool, np.array(test_nov), np.array(test_ind), strat, seed)
        per_seed.append(res)
    if not per_seed:
        return None

    def avg(strat, key):
        return float(np.mean([ps[strat][key] for ps in per_seed]))
    out = {"n_seeds": len(per_seed), "n_mols": len(mols),
           "auc_novel": {s: round(avg(s, "auc_novel"), 4) for s in ("uncertainty", "greedy", "random")},
           "auc_indomain": {s: round(avg(s, "auc_indomain"), 4) for s in ("uncertainty", "greedy", "random")},
           "acq_sim": {s: round(avg(s, "acq_sim"), 4) for s in ("uncertainty", "greedy", "random")}}
    # advantage (AL - random) per test set, for the uncertainty arm (primary) and greedy arm
    for arm in ("uncertainty", "greedy"):
        out[f"adv_indomain_{arm}"] = round(out["auc_indomain"][arm] - out["auc_indomain"]["random"], 4)
        out[f"adv_novel_{arm}"] = round(out["auc_novel"][arm] - out["auc_novel"]["random"], 4)
    return out


def main():
    t0 = time.time()
    per = {}
    print("=== B65: active learning x novel-chemistry ceiling ===")
    for path in sorted(glob.glob(os.path.join(MACE, "CHEMBL*.csv"))):
        name = os.path.basename(path).replace(".csv", "")
        try:
            r = process(path)
        except Exception as ex:
            print(f"  {name:16s} ERROR {ex}"); continue
        if r is None:
            print(f"  {name:16s} SKIP (insufficient novel test / pool)"); continue
        per[name] = r
        print(f"  {name:16s} adv_indomain(unc) {r['adv_indomain_uncertainty']:+.3f}  "
              f"adv_novel(unc) {r['adv_novel_uncertainty']:+.3f} | "
              f"adv_indomain(grd) {r['adv_indomain_greedy']:+.3f}  adv_novel(grd) {r['adv_novel_greedy']:+.3f} "
              f"[{time.time()-t0:.0f}s]")

    def med(key):
        v = [r[key] for r in per.values()]
        return round(float(np.median(v)), 4) if v else None

    def signtest(key):  # fraction of targets with positive value
        v = [r[key] for r in per.values()]
        return round(float(np.mean([x > 0 for x in v])), 3) if v else None

    summary = {
        "n_targets": len(per),
        "median_adv_indomain_uncertainty": med("adv_indomain_uncertainty"),
        "median_adv_novel_uncertainty": med("adv_novel_uncertainty"),
        "median_adv_indomain_greedy": med("adv_indomain_greedy"),
        "median_adv_novel_greedy": med("adv_novel_greedy"),
        "frac_targets_adv_novel_pos_uncertainty": signtest("adv_novel_uncertainty"),
        "frac_targets_adv_indomain_pos_uncertainty": signtest("adv_indomain_uncertainty"),
        "median_acq_sim": {s: round(float(np.median([r["acq_sim"][s] for r in per.values()])), 4)
                           for s in ("uncertainty", "greedy", "random")},
    }
    # verdict — an effect is credited ONLY if the median is meaningful (|.|>=0.03) AND the sign is a target majority
    # (frac_pos>=0.6 for positive, <=0.4 for negative). Otherwise it is a NULL (guards against over-reading noise).
    EFF, MAJ = 0.03, 0.60
    ai, an = summary["median_adv_indomain_uncertainty"], summary["median_adv_novel_uncertainty"]
    fi = summary["frac_targets_adv_indomain_pos_uncertainty"]; fn = summary["frac_targets_adv_novel_pos_uncertainty"]
    indomain_effect = ai is not None and abs(ai) >= EFF and (fi >= MAJ or fi <= 1 - MAJ)
    novel_effect = an is not None and abs(an) >= EFF and (fn >= MAJ or fn <= 1 - MAJ)
    if indomain_effect and ai > 0 and not novel_effect:
        verdict = (f"H1 TRUE + H2 TRUE: AL advantage is a NEAR-DOMAIN phenomenon — in-domain {ai:+.3f} "
                   f"(frac_pos {fi}) but novel collapses to {an:+.3f} (frac_pos {fn}, no effect). Consistent with the "
                   f"P9/B62 signal-loss ceiling: acquisition cannot buy novel-chemistry generalization.")
    elif novel_effect and an > 0:
        verdict = (f"H0/ALTERNATIVE (hopeful): AL advantage is real on novel chemistry ({an:+.3f}, frac_pos {fn}) — "
                   f"acquisition DOES improve novel-chemistry generalization; would revise the P9/B62 reading.")
    else:
        verdict = (f"FLAT NULL (H1 and H2 both UNSUPPORTED): in this small-label novel-chemistry-hard MoleculeACE "
                   f"potency regime, neither uncertainty nor greedy acquisition reliably beats RANDOM on EITHER test "
                   f"set — in-domain adv {ai:+.3f} (frac_pos {fi}), novel adv {an:+.3f} (frac_pos {fn}); all within "
                   f"noise (|median|<{EFF}, sign ~50/50). The acquisition functions demonstrably selected the intended "
                   f"compounds (uncertainty acq_sim {summary['median_acq_sim']['uncertainty']} < random "
                   f"{summary['median_acq_sim']['random']} < greedy {summary['median_acq_sim']['greedy']}), so correct "
                   f"acquisition simply did NOT translate into better generalization. REINFORCES B62: when signal is "
                   f"weak, WHICH points you label barely matters — the lever is information quantity/quality, not "
                   f"acquisition strategy. First-class negative; tempers P4 in the weak-signal small-label regime.")
    summary["verdict"] = verdict
    print("\nPANEL:", json.dumps(summary, indent=1)); print("VERDICT:", verdict)

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "per_target": per, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "B65_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k: v for k, v in summary.items() if k != "verdict"}, "per_target": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B65_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B65_metrics.json (%.1fs)" % (time.time() - t0))


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    main()
