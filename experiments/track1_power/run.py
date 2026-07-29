"""Track-1 power calculation by Monte-Carlo simulation of the EXACT pre-registered test:
proliferation-residualized drug-SPECIFICITY (mean diagonal - mean off-diagonal per-drug correlation), permutation.
Grounded in observed effect sizes (V9 residual drug-specific rho ~ 0.05-0.10). Estimates power vs cohort size N
and panel size K. Deterministic (seed). This is a PLANNING simulation (gaussian, true-proliferation residualized;
real power is somewhat lower due to imperfect proliferation estimation + drug-drug correlation — stated in protocol).
"""
import numpy as np, json, os, time

SEED = 42
HERE = os.path.dirname(os.path.abspath(__file__))
NSIM, NPERM = 300, 400
Ns = [50, 75, 100, 150, 200, 300]
Ks = [12, 20]
Rs = [0.05, 0.07, 0.10, 0.15]     # true residual drug-specific per-drug correlation
A_PROLIF = 1.0                    # shared proliferation loading (residualized out before the test)


def _std_cols(M):
    M = M - M.mean(0)
    s = M.std(0); s[s == 0] = 1.0
    return M / s


def _resid_on(M, cov):
    # residualize each column of M on [1, cov] (cov = proliferation), vectorized
    c = (cov - cov.mean()); denom = (c @ c)
    if denom == 0:
        return M - M.mean(0)
    beta = (c @ (M - M.mean(0))) / denom
    return (M - M.mean(0)) - np.outer(c, beta)


def sim_power(N, K, r, rng):
    na = np.sqrt(1.0 / r - 1.0)        # noise so residual diagonal corr == r (b=g=1)
    hits = 0
    for _ in range(NSIM):
        p = rng.standard_normal(N)                       # latent proliferation (shared)
        s = rng.standard_normal((N, K))                  # drug-specific latent (independent across drugs)
        pred = A_PROLIF * p[:, None] + s + na * rng.standard_normal((N, K))
        auc = A_PROLIF * p[:, None] + s + na * rng.standard_normal((N, K))
        rp = _resid_on(pred, p); ra = _resid_on(auc, p)  # residualize on proliferation
        Zp = _std_cols(rp)
        Za = _std_cols(ra)
        C = (Zp.T @ Za) / N                              # KxK correlation matrix
        diag = np.trace(C) / K
        off = (C.sum() - np.trace(C)) / (K * K - K)
        obs = diag - off
        # permutation null: shuffle patients of auc, recompute diag-off
        null = np.empty(NPERM)
        for j in range(NPERM):
            perm = rng.permutation(N)
            Cp = (Zp.T @ Za[perm]) / N
            null[j] = np.trace(Cp) / K - (Cp.sum() - np.trace(Cp)) / (K * K - K)
        pval = (np.sum(null >= obs) + 1) / (NPERM + 1)
        hits += pval < 0.05
    return hits / NSIM


def main():
    rng = np.random.default_rng(SEED)
    table = {}
    print(f"Track-1 power (test: prolif-residualized diag-off specificity, permutation; NSIM={NSIM}, NPERM={NPERM})")
    print("K   r      " + "  ".join(f"N={n}" for n in Ns))
    for K in Ks:
        for r in Rs:
            row = [round(sim_power(N, K, r, rng), 3) for N in Ns]
            table[f"K{K}_r{r}"] = dict(zip([str(n) for n in Ns], row))
            print(f"{K:<3} {r:<5}  " + "  ".join(f"{v:0.2f} " for v in row))
    # smallest N reaching 0.80 power, per (K, r)
    rec = {}
    for K in Ks:
        for r in Rs:
            row = table[f"K{K}_r{r}"]
            n80 = next((int(n) for n in map(str, Ns) if row[n] >= 0.80), None)
            rec[f"K={K}, r={r}"] = n80
    print("\nsmallest N for >=80% power:")
    for k, v in rec.items():
        print(f"  {k}: N={v if v else '>300'}")
    out = {"seed": SEED, "nsim": NSIM, "nperm": NPERM, "Ns": Ns, "Ks": Ks, "Rs": Rs,
           "prolif_loading": A_PROLIF, "power_table": table, "N_for_80pct_power": rec,
           "note": "Planning sim (gaussian, true-proliferation residualized). Real power somewhat lower (imperfect "
                   "proliferation estimate + drug-drug correlation). Effect sizes r from observed V9 (~0.05-0.10)."}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "track1_power.json"), "w"), indent=2)
    print("\nwrote results/track1_power.json")


if __name__ == "__main__":
    main()
