"""Scoring + the guilty-until-proven-innocent battery (Constitution rule 3)."""
import numpy as np
from scipy import stats


def per_drug_spearman(pred, obs):
    return stats.spearmanr(pred, obs)[0]


def paired_wilcoxon(a, b):
    """Paired Wilcoxon signed-rank of per-drug metric arrays a vs b."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    w, p = stats.wilcoxon(a, b)
    return float(w), float(p)


def bh_fdr(pvals):
    """Benjamini-Hochberg adjusted p-values (nan-safe)."""
    p = np.asarray(pvals, float)
    ok = np.isfinite(p)
    out = np.full_like(p, np.nan)
    q = p[ok]
    n = q.size
    if n == 0:
        return out
    order = np.argsort(q)
    ranked = q[order] * n / (np.arange(n) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adj = np.empty(n)
    adj[order] = np.clip(ranked, 0, 1)
    out[ok] = adj
    return out


def permutation_p(observed, permute_fn, k=2000, seed=42):
    """Fraction of k label-permuted statistics >= observed (one-sided), +1 smoothed."""
    rng = np.random.default_rng(seed)
    null = np.array([permute_fn(rng) for _ in range(k)])
    return float((np.sum(null >= observed) + 1) / (k + 1))
