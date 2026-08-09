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


# ---- CONFORMAL abstention (productionizes CONFORMAL1) ------------------------------------------------------
# CONFORMAL1 finding, baked in here so the engine's confidence is trustworthy AND honestly OOD-bounded:
#   (1) MARGINAL split-conformal is VACUOUS for an imbalanced target class -- its coverage collapses onto the
#       majority (essential-class coverage 0.0). So we calibrate a SEPARATE threshold per class (Mondrian).
#   (2) Even class-conditional coverage does NOT transfer to a novel organism (essential-class coverage
#       dropped 0.94 in-distribution -> 0.55 OOD). So a novel-organism call must be flagged coverage-NOT-
#       guaranteed and made MORE conservative (wider sets = more abstention), never claim nominal coverage.
# Pure functions; scope = a statistical governance primitive, not a biology claim.
def conformal_class_thresholds(cal_probs, cal_labels, alpha=0.10):
    """Mondrian (class-conditional) split-conformal thresholds q_y for target coverage 1-alpha PER CLASS.
    cal_probs: (n,K) predicted class probabilities on a CALIBRATION set; cal_labels: (n,) true class ids.
    Nonconformity s_i = 1 - p_i[true]; q_y = the ceil((n_y+1)(1-alpha))/n_y quantile of s over class-y points.
    Guarantee holds IN-DISTRIBUTION only (exchangeability) -- use ood_adjusted_confidence on novel inputs."""
    cal_probs = np.asarray(cal_probs, float); cal_labels = np.asarray(cal_labels, int)
    K = cal_probs.shape[1]; q = {}
    for y in range(K):
        m = cal_labels == y
        if not m.any():
            q[y] = 1.0; continue
        s = 1.0 - cal_probs[m, y]; n = int(m.sum())
        ql = min(1.0, np.ceil((n + 1) * (1 - alpha)) / n)
        q[y] = float(np.quantile(s, ql, method="higher"))
    return q


def conformal_prediction_set(probs, thresholds):
    """Prediction set {y : p[y] >= 1 - q_y} for one point (probs: (K,)). size 1 = confident single label;
    size >=2 = uncertain (abstain); size 0 = confidently-wrong region (also treat as abstain)."""
    probs = np.asarray(probs, float)
    st = [int(y) for y in range(len(probs)) if probs[y] >= 1.0 - float(thresholds.get(y, 1.0))]
    return {"set": st, "size": len(st), "confident_label": (st[0] if len(st) == 1 else None),
            "abstain": len(st) != 1}


def ood_adjusted_confidence(probs, thresholds, ood=False, ood_widen=0.0):
    """Governance wrapper enforcing CONFORMAL1's OOD honesty rule. In-distribution: returns the class-
    conditional conformal set with coverage_guaranteed=True. On a NOVEL/OOD organism (ood=True): the nominal
    1-alpha coverage is NOT guaranteed (measured 0.94->0.55 drop), so it flags coverage_guaranteed=False and,
    with ood_widen>0, raises each q_y (widening sets => more conservative abstention). It NEVER claims nominal
    coverage OOD -- the honest deployment rule for a never-seen organism."""
    thr = ({y: min(1.0, float(q) + float(ood_widen)) for y, q in thresholds.items()}
           if (ood and ood_widen > 0) else dict(thresholds))
    r = conformal_prediction_set(probs, thr)
    r["ood"] = bool(ood)
    r["coverage_guaranteed"] = (not ood)
    r["note"] = ("in-distribution class-conditional 1-alpha coverage" if not ood else
                 "OOD: coverage NOT guaranteed (CONFORMAL1: essential-class coverage 0.94->0.55 on a novel "
                 "organism); flagged + widened for conservative abstention")
    return r
