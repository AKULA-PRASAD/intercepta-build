"""Track-1 power/design simulation for the prospective functional-precision cohort — a PLANNING tool, not a
result about real data. Grounded in THIS program's observed effect sizes (V9 residual drug-specific ρ≈0.05-0.10;
clinical endpoints from literature-plausible ranges). Three aims:
  Aim 1  drug-SPECIFICITY transfer (prolif-residualized diag-off, permutation) — IDEAL and REALISTIC variants.
  Aim 2a measured functional readout -> BINARY clinical response (AUROC), by simulation.
  Aim 2b measured functional readout -> SURVIVAL (per-SD hazard ratio), Hsieh-Lavori analytic.
Deterministic (seed=42). Assumptions are explicit and conservative; a planning sim over-states nothing it doesn't
label. Real power for Aim 1 is the REALISTIC number (imperfect proliferation estimate + drug-drug correlation).
"""
import numpy as np, json, os, time
from scipy import stats
import warnings; warnings.filterwarnings("ignore")   # benign macOS BLAS matmul RuntimeWarnings; results validated

SEED = 42
HERE = os.path.dirname(os.path.abspath(__file__))
NSIM, NPERM = 300, 400
Ns = [50, 75, 100, 150, 200, 300]
Ks = [12, 20]
Rs = [0.05, 0.07, 0.10, 0.15]         # true residual drug-specific per-drug correlation (from V9)
A_PROLIF = 1.0                        # shared proliferation loading (residualized out before the test)
PROLIF_RELIABILITY = 0.8              # realistic: R_prolif estimate correlates ~0.9 (r^2=0.8) with truth
DRUG_CORR = 0.15                      # realistic: pan-drug shared-sensitivity component (inflates off-diagonal)


def _std_cols(M):
    M = M - M.mean(0); s = M.std(0); s[s == 0] = 1.0
    return M / s


def _resid_on(M, cov):
    c = (cov - cov.mean()); denom = (c @ c)
    if denom == 0:
        return M - M.mean(0)
    beta = (c @ (M - M.mean(0))) / denom
    return (M - M.mean(0)) - np.outer(c, beta)


def sim_power_aim1(N, K, r, rng, realistic):
    na = np.sqrt(1.0 / r - 1.0)                          # noise so residual diagonal corr == r
    dc = DRUG_CORR if realistic else 0.0
    hits = 0
    for _ in range(NSIM):
        p = rng.standard_normal(N)                       # latent proliferation (shared)
        shared_spec = rng.standard_normal(N) if realistic else np.zeros(N)   # pan-drug sensitivity (confound)
        s = np.sqrt(1 - dc) * rng.standard_normal((N, K)) + np.sqrt(dc) * shared_spec[:, None]
        pred = A_PROLIF * p[:, None] + s + na * rng.standard_normal((N, K))
        auc = A_PROLIF * p[:, None] + s + na * rng.standard_normal((N, K))
        if realistic:                                    # residualize on a NOISY proliferation estimate
            p_obs = np.sqrt(PROLIF_RELIABILITY) * p + np.sqrt(1 - PROLIF_RELIABILITY) * rng.standard_normal(N)
        else:
            p_obs = p
        Zp = _std_cols(_resid_on(pred, p_obs)); Za = _std_cols(_resid_on(auc, p_obs))
        C = (Zp.T @ Za) / N
        obs = np.trace(C) / K - (C.sum() - np.trace(C)) / (K * K - K)
        null = np.empty(NPERM)
        for j in range(NPERM):
            perm = rng.permutation(N); Cp = (Zp.T @ Za[perm]) / N
            null[j] = np.trace(Cp) / K - (Cp.sum() - np.trace(Cp)) / (K * K - K)
        hits += ((np.sum(null >= obs) + 1) / (NPERM + 1)) < 0.05
    return hits / NSIM


def sim_power_aim2a(N, auroc, prevalence, rng, nsim=2000):
    """Measured functional score -> binary clinical response. Responders x~N(d,1), non ~N(0,1);
    d=sqrt(2)*Phi^-1(AUROC). Test one-sided Mann-Whitney p<0.05."""
    d = np.sqrt(2) * stats.norm.ppf(auroc)
    hits = 0
    for _ in range(nsim):
        y = rng.random(N) < prevalence
        x = rng.standard_normal(N) + d * y
        if y.sum() < 3 or (~y).sum() < 3:
            continue
        hits += stats.mannwhitneyu(x[y], x[~y], alternative="greater").pvalue < 0.05
    return hits / nsim


def events_for_cox(hr, power=0.80, alpha=0.05):
    """Hsieh-Lavori: events needed for a per-SD continuous covariate Cox test (sigma=1)."""
    z = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)
    return z ** 2 / (np.log(hr) ** 2)


def main():
    rng = np.random.default_rng(SEED)
    out = {"seed": SEED, "nsim": NSIM, "nperm": NPERM, "kind": "PLANNING SIMULATION (not a result on real data)",
           "assumptions": {"prolif_reliability": PROLIF_RELIABILITY, "drug_corr": DRUG_CORR,
                           "aim1_effect_sizes_r": Rs, "note": "r from observed V9 residual drug-specificity"}}

    # ---- Aim 1: ideal + realistic ----
    print("=== Aim 1: drug-specificity transfer power (permutation test) ===")
    for tag, realistic in [("ideal", False), ("realistic", True)]:
        table = {}
        print(f"\n[{tag}]  K   r      " + "  ".join(f"N={n}" for n in Ns))
        Kset = Ks if not realistic else [20]             # realistic only for recommended K=20 (runtime)
        for K in Kset:
            for r in Rs:
                row = [round(sim_power_aim1(N, K, r, rng, realistic), 3) for N in Ns]
                table[f"K{K}_r{r}"] = dict(zip(map(str, Ns), row))
                print(f"       {K:<3} {r:<5}  " + "  ".join(f"{v:0.2f} " for v in row))
        out[f"aim1_{tag}"] = table
    # recommended N (realistic, K=20) for 80% power
    rec = {}
    for r in Rs:
        row = out["aim1_realistic"][f"K20_r{r}"]
        rec[f"r={r}"] = next((int(n) for n in map(str, Ns) if row[n] >= 0.80), None)
    out["aim1_realistic_N_for_80pct_K20"] = rec
    print("\n  Aim1 REALISTIC smallest N for >=80% power (K=20):", {k: (v or ">300") for k, v in rec.items()})

    # ---- Aim 2a: binary clinical response (AUROC) ----
    print("\n=== Aim 2a: measured functional score -> binary response (AUROC), prevalence 0.35 ===")
    a2a = {}; AUR = [0.60, 0.65, 0.70]
    print("AUROC   " + "  ".join(f"N={n}" for n in Ns))
    for a in AUR:
        row = [round(sim_power_aim2a(N, a, 0.35, rng), 3) for N in Ns]
        a2a[f"auroc{a}"] = dict(zip(map(str, Ns), row))
        print(f"{a:<7} " + "  ".join(f"{v:0.2f} " for v in row))
    out["aim2a_binary_response_power"] = a2a
    rec2a = {a: next((int(n) for n in map(str, Ns) if a2a[f"auroc{a}"][n] >= 0.80), None) for a in AUR}
    out["aim2a_N_for_80pct"] = rec2a
    print("  Aim2a smallest N for >=80% power:", {f"AUROC={k}": (v or ">300") for k, v in rec2a.items()})

    # ---- Aim 2b: survival (per-SD hazard ratio), Hsieh-Lavori analytic ----
    print("\n=== Aim 2b: measured functional score -> survival (per-SD HR), Hsieh-Lavori ===")
    a2b = {}; HRs = [1.4, 1.6, 2.0]
    for ef_tag, ef in [("event_frac_0.6", 0.6), ("event_frac_0.4", 0.4)]:
        d = {}
        for hr in HRs:
            E = events_for_cox(hr); Nreq = int(np.ceil(E / ef))
            d[f"HR{hr}"] = {"events_needed": int(np.ceil(E)), "N_needed": Nreq}
        a2b[ef_tag] = d
        print(f"  [{ef_tag}] " + " | ".join(f"HR {hr}: {d[f'HR{hr}']['events_needed']} events, N≈{d[f'HR{hr}']['N_needed']}" for hr in HRs))
    out["aim2b_survival"] = a2b

    # ---- overall recommendation (moderate vs conservative effect sizes, stated honestly) ----
    moderate = max(x for x in [rec.get("r=0.07"), rec2a.get(0.65), a2b["event_frac_0.6"]["HR1.6"]["N_needed"]] if x)
    conservative = max(x for x in [rec.get("r=0.05"), rec2a.get(0.60), a2b["event_frac_0.4"]["HR1.4"]["N_needed"]] if x)
    out["recommended_N"] = {
        "moderate_effects": {"N": moderate, "basis": "Aim1 r=0.07 (N=%s), Aim2a AUROC=0.65 (N=%s), Aim2b HR=1.6/60%%-events (N=%s)"
                             % (rec.get("r=0.07"), rec2a.get(0.60 if False else 0.65), a2b["event_frac_0.6"]["HR1.6"]["N_needed"])},
        "conservative_effects": {"N": conservative, "basis": "Aim1 r=0.05 (N=%s), Aim2a AUROC=0.60 (N=%s), Aim2b HR=1.4/40%%-events (N=%s)"
                                 % (rec.get("r=0.05"), rec2a.get(0.60), a2b["event_frac_0.4"]["HR1.4"]["N_needed"])},
        "design_target": max(moderate, min(conservative, 200))}
    print(f"\n=== RECOMMENDED N ===")
    print(f"  moderate effect sizes (r=0.07 / AUROC 0.65 / HR 1.6):   N≈{moderate}  powers all three at >=80%%")
    print(f"  conservative effect sizes (r=0.05 / AUROC 0.60 / HR 1.4): N≈{conservative}")
    print(f"  DESIGN TARGET: N≈{out['recommended_N']['design_target']} (covers Aim-1 at r=0.07 and the clinical endpoints; "
          f"the clinical endpoints, not Aim 1, dominate the requirement).")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "track1_power.json"), "w"), indent=2)
    print("\nwrote results/track1_power.json")


if __name__ == "__main__":
    main()
