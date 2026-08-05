"""FRONT2 — structural selectivity analysis. Among HOST-HOMOLOGOUS pathogen metabolic genes (the ones E2E2's sequence
filter over-excludes), does pathogen pocket druggability — and its DIFFERENCE from the human homolog's pocket — distinguish
known targets from non-targets? If yes, structure RESCUES the over-excluded targets. Reads the fpocket cache
(build_druggability.py). Deterministic; reproduced ×2. Env: intercepta-build.
"""
import os, json, time, hashlib
import numpy as np
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
CACHE = os.path.join(DATA, "front2", "druggability.tsv")
SEED = 42


def auroc(y, s):
    y = np.asarray(y)
    return float(roc_auc_score(y, s)) if 0 < y.sum() < len(y) else float("nan")


def perm_p(y, s, n=2000):
    y = np.asarray(y); obs = auroc(y, s)
    if obs != obs: return float("nan"), obs
    rng = np.random.RandomState(SEED); cnt = 0
    for _ in range(n):
        yp = rng.permutation(y)
        if auroc(yp, s) >= obs: cnt += 1
    return (cnt + 1) / (n + 1), obs


def odds_ratio(y, x):
    thr = np.quantile(x, 0.75); hi = x >= thr
    a = float(((hi) & (y == 1)).sum()) + .5; b = float(((hi) & (y == 0)).sum()) + .5
    c = float(((~hi) & (y == 1)).sum()) + .5; d = float(((~hi) & (y == 0)).sum()) + .5
    return round((a * d) / (b * c), 2)


def main():
    t0 = time.time()
    rows = [ln.rstrip("\n").split("\t") for ln in open(CACHE)][1:]
    # columns: organism uniprot is_target path_drug path_npk human_acc human_drug human_npk
    rec = {}
    for r in rows:
        if len(r) < 8 or r[3] == "" or r[6] == "": continue
        rec.setdefault(r[0], []).append((int(r[2]), float(r[3]), float(r[6])))
    per = {}; pooled_y, pooled_pd, pooled_diff = [], [], []
    for X, lst in rec.items():
        y = np.array([a for a, _, _ in lst]); pd = np.array([b for _, b, _ in lst]); hd = np.array([c for _, _, c in lst])
        diff = pd - hd
        p_pd, a_pd = perm_p(y, pd);
        per[X] = {"n": len(y), "n_target": int(y.sum()),
                  "AUROC_pathogen_druggability": round(a_pd, 4), "perm_p_pathogen": round(p_pd, 4),
                  "AUROC_human_druggability": round(auroc(y, hd), 4),
                  "AUROC_selectivity_diff": round(auroc(y, diff), 4),
                  "OR_topq_pathogen_druggability": odds_ratio(y, pd),
                  "mean_path_drug_target": round(float(pd[y == 1].mean()), 3), "mean_path_drug_nontarget": round(float(pd[y == 0].mean()), 3),
                  "mean_diff_target": round(float(diff[y == 1].mean()), 3), "mean_diff_nontarget": round(float(diff[y == 0].mean()), 3)}
        pooled_y += list(y); pooled_pd += list(pd); pooled_diff += list(diff)
        print(f"  [{X}] n={len(y)} tgt={int(y.sum())} | path-drug AUROC {a_pd:.3f} (p={p_pd:.3f}) | selectivity-diff AUROC {per[X]['AUROC_selectivity_diff']:.3f} [{time.time()-t0:.0f}s]")
    py = np.array(pooled_y); ppd = np.array(pooled_pd); pdiff = np.array(pooled_diff)
    pool_pd_p, pool_pd_a = perm_p(py, ppd)
    pool = {"n": len(py), "n_target": int(py.sum()),
            "AUROC_pathogen_druggability": round(pool_pd_a, 4), "perm_p_pathogen": round(pool_pd_p, 4),
            "AUROC_selectivity_diff": round(auroc(py, pdiff), 4)}
    H1 = pool_pd_a > 0.60 and pool_pd_p < 0.05
    H2 = auroc(py, pdiff) > 0.60 and auroc(py, pdiff) > pool_pd_a + 0.02
    summary = {"organisms": list(rec), "pooled": pool, "H1_structure_rescues": bool(H1),
               "H2_selectivity_diff_adds": bool(H2)}
    if H1:
        summary["verdict"] = (f"H1 TRUE (structure RESCUES over-excluded targets): among host-homologous genes, pathogen "
                              f"pocket druggability distinguishes known targets from non-targets (pooled AUROC {pool_pd_a:.3f}, "
                              f"perm p {pool_pd_p:.4f}) — so STRUCTURE recovers druggable targets the sequence filter excluded. "
                              + (f"The pathogen-vs-host DIFFERENCE adds further (selectivity-diff AUROC {auroc(py,pdiff):.3f}) → "
                                 f"rescuable targets have pathogen-SELECTIVE pockets." if H2 else
                                 f"But the pathogen-vs-host difference does NOT add beyond pathogen druggability (diff AUROC "
                                 f"{auroc(py,pdiff):.3f}) — the signal is 'is it druggable at all', not host-selectivity per se.")
                              + " SCOPE: fpocket heuristic, AF apo structures, metabolic subproteome, 2 bacteria, sampled non-targets; not wet-lab.")
    else:
        summary["verdict"] = (f"H0 (structure does NOT rescue zero-data): among host-homologous genes, neither pathogen pocket "
                              f"druggability (pooled AUROC {pool_pd_a:.3f}, perm p {pool_pd_p:.4f}) nor the pathogen-vs-host "
                              f"difference (AUROC {auroc(py,pdiff):.3f}) meaningfully distinguishes known targets from non-targets "
                              f"— the information ceiling extends from SEQUENCE to STRUCTURAL selectivity (consistent with TID2, "
                              f"pocket druggability ≈ conservation, weak). So the 35–52% host-homologous targets E2E2 over-excludes "
                              f"CANNOT be cheaply rescued by zero-data structural druggability; distinguishing selectively-druggable "
                              f"host-homologous targets needs more than an apo predicted pocket (real ligand / induced-fit / "
                              f"experimental data). SCOPE: fpocket heuristic, AF apo structures, metabolic subproteome, 2 bacteria; not wet-lab.")
    print("\nPANEL:", json.dumps({k: v for k, v in summary.items() if k != "verdict"}, indent=1)); print("VERDICT:", summary["verdict"])

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "per_organism": per, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "FRONT2_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k: v for k, v in summary.items() if k != "verdict"}, "per_organism": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "FRONT2_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
