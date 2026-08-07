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


# ---- base-rate-fair essentiality-transfer gate (FAIRGATE1, validated 2026-08-07) ----
# Replaces the base-rate-CONFOUNDED odds-ratio gate for judging zero-data FBA-essentiality transfer.
# Rationale: OR approximates the risk ratio only for RARE outcomes; essentiality base rates run 0.03-0.64
# (common), so OR distorts effect size AS A FUNCTION OF base rate (proven: the same P. falciparum model flips
# PASS<->FAIL on the OR>3 gate purely with the screen's base rate). The risk ratio RR=precision/base_rate is the
# base-rate-invariant fold-enrichment (validated by invariance + simulation; experiments/FAIRGATE1_*).
def fair_gate(both, fba_only, exp_only, neither, alpha=0.01, T=1.0, n_boot=20000, seed=42):
    """Base-rate-fair transfer gate over a 2x2 (FBA-essential vs experimentally-essential) contingency.
    Returns RR (=precision/base_rate, base-rate-invariant fold-enrichment), a bootstrap 95% CI, one-sided
    Fisher p, and the PASS verdict := (RR_lower_CI > 1) AND (RR >= T) AND (Fisher p < alpha). T=1 (the
    significance-anchored no-enrichment floor) is the only base-rate-invariant non-arbitrary threshold; a larger
    fixed fold-floor re-imports base-rate sensitivity (FAIRGATE1 crux). Recommended gate for FUTURE prospective
    essentiality-transfer tests (supersedes raw OR>3). Pure function; scope = statistical, not a biology claim."""
    a, b, c, d = float(both), float(fba_only), float(exp_only), float(neither)
    N = a + b + c + d
    precision = a / (a + b) if (a + b) else float("nan")
    base_rate = (a + c) / N if N else float("nan")
    rr = precision / base_rate if base_rate else float("nan")
    odds_ratio = (a * d) / (b * c) if (b * c) else float("inf")
    _, p = stats.fisher_exact([[a, b], [c, d]], alternative="greater")
    probs = np.array([a, b, c, d]) / N
    rng = np.random.default_rng(seed)
    draws = rng.multinomial(int(round(N)), probs, size=n_boot).astype(float)
    aa, bb, cc, dd = draws.T
    dp, ep = aa + bb, aa + cc
    valid = (dp > 0) & (ep > 0)
    rr_b = (aa / np.where(dp > 0, dp, 1)) / np.where(ep > 0, ep / N, np.nan)
    rr_b = rr_b[valid & np.isfinite(rr_b) & (rr_b > 0)]
    lo, hi = float(np.percentile(rr_b, 2.5)), float(np.percentile(rr_b, 97.5))
    verdict = bool((lo > 1.0) and (rr >= T) and (float(p) < alpha))
    return {"RR": rr, "RR_ci95": [lo, hi], "fisher_p_greater": float(p), "odds_ratio": odds_ratio,
            "precision": precision, "base_rate": base_rate, "PASS": verdict, "T": T, "alpha": alpha}
