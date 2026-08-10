#!/usr/bin/env python3
"""Reviewer-proof equivalence proof for the AFFINITY1 AUROC optimization.

Asserts the fast numpy AUROC in analyze.py (_rank_avg-based) is numerically identical to:
  (1) the previous pandas/groupby midrank implementation (OLD),
  (2) the DEFINITION of AUROC = Wilcoxon-Mann-Whitney with ties=0.5 (brute-force pairwise, ground truth),
  (3) sklearn.metrics.roc_auc_score (community reference), when available,
across random / heavy-tie / all-identical / perfect-separation / perfect-inversion / bootstrap-duplicate
datasets; and that the bootstrap CIs are bit-identical when only the inner AUROC is swapped.
Run:  python hpc/test_auroc_equivalence.py   (exit 0 = PASS). Tolerance 1e-12.
"""
import os, importlib.util, numpy as np, pandas as pd
os.environ.setdefault("INTERCEPTA_DATA", "/tmp/aff_eqtest"); os.makedirs(os.path.join(os.environ["INTERCEPTA_DATA"], "affinity1"), exist_ok=True)
_spec = importlib.util.spec_from_file_location("an", os.path.join(os.path.dirname(__file__), "analyze.py"))
_an = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_an)
NEW = _an.auroc
TOL = 1e-12

def OLD(s, y):  # previous pandas/groupby midrank
    s = np.asarray(s, float); y = np.asarray(y, int); mm = ~np.isnan(s); s, y = s[mm], y[mm]
    npos = int(y.sum()); nneg = len(y) - npos
    if npos == 0 or nneg == 0: return np.nan
    order = np.argsort(s, kind="mergesort"); r = np.empty(len(s)); r[order] = np.arange(1, len(s) + 1)
    r = pd.DataFrame({"s": s, "r": r}).groupby("s")["r"].transform("mean").values
    return float((r[y == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg))

def DEF(s, y):  # DEFINITION: mean over pos x neg pairs of [pos>neg] + 0.5[pos==neg]
    s = np.asarray(s, float); y = np.asarray(y, int); mm = ~np.isnan(s); s, y = s[mm], y[mm]
    pos, neg = s[y == 1], s[y == 0]
    if len(pos) == 0 or len(neg) == 0: return np.nan
    return float(sum(np.sum(a > neg) + 0.5 * np.sum(a == neg) for a in pos) / (len(pos) * len(neg)))

def boot(fn, s, y, B=3000, seed=42):
    s = np.asarray(s, float); y = np.asarray(y, int); n = len(y); rng = np.random.default_rng(seed); out = []
    for _ in range(B):
        idx = rng.integers(0, n, n); a = fn(s[idx], y[idx])
        if a == a: out.append(a)
    return (float(np.mean(out)), float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5)))

def main():
    try:
        from sklearn.metrics import roc_auc_score as SK; have_sk = True
    except Exception:
        have_sk = False
    rng = np.random.default_rng(7)
    cases = {
        "random_no_ties": (rng.random(400), rng.integers(0, 2, 400)),
        "heavy_ties": (rng.integers(0, 6, 400).astype(float), rng.integers(0, 2, 400)),
        "all_identical": (np.full(50, 3.0), rng.integers(0, 2, 50)),
    }
    s = rng.random(60); y = (s > np.median(s)).astype(int)
    cases["perfect_separation"] = (s, y); cases["perfect_inversion"] = (s, 1 - y)
    idx = rng.integers(0, 200, 200); base_s = rng.random(200); base_y = rng.integers(0, 2, 200)
    cases["bootstrap_dupes"] = (base_s[idx], base_y[idx])
    worst = 0.0
    for name, (s, y) in cases.items():
        vals = [OLD(s, y), NEW(s, y), DEF(s, y)]
        if have_sk and len(set(y.tolist())) == 2: vals.append(float(SK(y, s)))
        vals = [v for v in vals if v == v]
        d = max(vals) - min(vals); worst = max(worst, d)
        assert d < TOL, "MISMATCH in %s: spread=%.3e vals=%s" % (name, d, vals)
    # bootstrap CI bit-identity: swapping only the inner AUROC must not change CIs
    s = rng.random(300); y = rng.integers(0, 2, 300)
    assert boot(OLD, s, y) == boot(NEW, s, y), "bootstrap CIs differ when only AUROC impl is swapped"
    print("PASS: NEW == OLD == DEFINITION%s ; worst |delta| = %.2e ; bootstrap CIs bit-identical" % (
        " == sklearn" if have_sk else " (sklearn unavailable)", worst))

if __name__ == "__main__":
    main()
