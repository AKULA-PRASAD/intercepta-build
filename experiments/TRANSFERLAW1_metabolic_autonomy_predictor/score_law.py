#!/usr/bin/env python
"""TRANSFERLAW1 step 2 — score the a-priori metabolic-autonomy transfer law. Deterministic (seed 42).
S = z(log10_reactions) - z(blocked_fraction) - z(exchange_fraction) + z(gpr_coverage)  [biomass dropped, see PREREG].
H1 Spearman(S, log OR) + bootstrap CI; H2 AUROC(S, gate_pass); H3 Spearman(S, OR) within the 6 P. falciparum recons.
Features from compute_features.get_features (GEM topology ONLY; non-circular). Reproduces byte-identical."""
import os, json, math, hashlib
import numpy as np
from scipy import stats
from compute_features import get_features

def roc_auc_score(y, score):
    """Rank-based AUROC (Mann-Whitney), tie-aware; no sklearn dependency."""
    y = np.asarray(y, int); score = np.asarray(score, float)
    pos = score[y == 1]; neg = score[y == 0]
    if len(pos) == 0 or len(neg) == 0: return float("nan")
    ranks = stats.rankdata(score)
    return float((ranks[y == 1].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))

D = os.environ.get("INTERCEPTA_DATA", os.path.expanduser("~/intercepta_data"))
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)
SEED = 42
FEATS = ["log10_reactions", "blocked_fraction", "exchange_fraction", "gpr_coverage"]
SIGNS = {"log10_reactions": +1, "blocked_fraction": -1, "exchange_fraction": -1, "gpr_coverage": +1}

# organism -> (gem relpath, committed OR, gate_pass)   [one representative per organism]
PANEL = {
    "E.coli":         ("synleth/iML1515.xml", 44.94, True),
    "Salmonella":     ("crossval/gems/STM_v1_0.xml", 4.33, True),
    "B.subtilis":     ("crossval/gems/iYO844.xml", 12.48, True),
    "S.aureus":       ("crossval/gems/iYS854.xml", 15.91, True),
    "M.tuberculosis": ("crossval/gems/iEK1008.xml", 26.11, True),
    "K.pneumoniae":   ("crossval/gems/iYL1228.xml", 5.92, True),
    "A.baumannii":    ("crossval/gems/iCN718.xml", 12.75, True),
    "N.gonorrhoeae":  ("blind1/ngono.xml", 6.13, True),
    "C.jejuni":       ("blind2/cjejuni.xml", 3.92, True),
    "B.theta":        ("blind3/btheta.xml", 8.03, True),
    "S.pneumoniae":   ("blind4/spneumo.xml", 2.96, False),
    "K.phaffii":      ("blind5/kphaffii_iMT1026v3.xml", 2.36, False),
    "M.maripaludis":  ("blind6/mmp_iMR539.xml", 4.23, True),
    "T.brucei":       ("blind7/tbrucei.xml", 0.64, False),
    "S.cerevisiae":   ("generalize4/iMM904.xml", 4.65, True),
    "C.albicans":     ("hardenf1/calb_gem_Mirhakkak2021.xml", 13.93, True),
    "Toxoplasma":     ("hardenp1/iTgo2020_krishnan.mat", 14.10, True),
    "P.falciparum":   ("generalize5/iPfal19.xml", 2.469, False),
}
# the 6 P. falciparum reconstructions (H3 within-organism natural experiment)
PF_SWAP = {
    "iPfal19":            ("generalize5/iPfal19.xml", 2.469),
    "iPfal17":            ("pararesolve1/iPfal17.xml", 2.461),
    "Chiappino-Pepe2017": ("pararesolve1/ipfa2017_chiappino_pepe.xml", 1.034),
    "AbdelHaleem_iAM480": ("pararesolve1/pfal2018_abdel_haleem.xml", 3.074),
    "gf_Pf3D7":           ("generalize5/gf_Pfalciparum3D7.xml", 1.03),
    "gf_no_ortho":        ("generalize5/gf_no_ortho_Pfalciparum3D7.xml", 0.859),
}

def zscore(v):
    v = np.asarray(v, float); s = v.std()
    return (v - v.mean()) / (s if s > 0 else 1.0)

def compute_S(feat_rows):
    """feat_rows: list of dicts. Returns S array (z-scored composite over this set)."""
    cols = {f: zscore([r[f] for r in feat_rows]) for f in FEATS}
    return sum(SIGNS[f] * cols[f] for f in FEATS)

def get(relpath):
    p = os.path.join(D, relpath)
    if not os.path.exists(p): return None
    return get_features(relpath, p)

def main():
    # ---- main panel ----
    rows, missing = [], []
    for org, (rp, orr, gp) in PANEL.items():
        f = get(rp)
        if f is None or any(f.get(k) is None or (isinstance(f.get(k), float) and math.isnan(f[k])) for k in FEATS):
            missing.append(org); continue
        rows.append({"organism": org, "OR": orr, "gate_pass": gp, **{k: f[k] for k in FEATS},
                     "biomass_synth_fraction_dropped": f.get("biomass_synth_fraction")})
    S = compute_S(rows)
    for r, s in zip(rows, S): r["S"] = round(float(s), 4)
    logOR = np.array([math.log(r["OR"]) for r in rows]); Sarr = np.array([r["S"] for r in rows])
    gp = np.array([1 if r["gate_pass"] else 0 for r in rows])

    rho, p_rho = stats.spearmanr(Sarr, logOR)
    rng = np.random.default_rng(SEED); n = len(rows); boot = []
    for _ in range(2000):
        idx = rng.integers(0, n, n)
        if len(set(logOR[idx])) < 3: continue
        boot.append(stats.spearmanr(Sarr[idx], logOR[idx]).correlation)
    boot = [b for b in boot if b == b]
    ci = [round(float(np.percentile(boot, 2.5)), 4), round(float(np.percentile(boot, 97.5)), 4)]
    auroc = float(roc_auc_score(gp, Sarr)) if len(set(gp)) > 1 else float("nan")
    h1_pass = bool(ci[0] > 0)
    h2_pass = bool(auroc >= 0.75)

    # ---- H3: within-organism P. falciparum swap ----
    pf_rows = []
    for lab, (rp, orr) in PF_SWAP.items():
        f = get(rp)
        if f is None or any(math.isnan(f[k]) if isinstance(f[k], float) else f[k] is None for k in FEATS): continue
        pf_rows.append({"recon": lab, "OR": orr, **{k: f[k] for k in FEATS}})
    pf_S = compute_S(pf_rows)
    for r, s in zip(pf_rows, pf_S): r["S"] = round(float(s), 4)
    pf_rho, pf_p = stats.spearmanr([r["S"] for r in pf_rows], [r["OR"] for r in pf_rows])
    h3_pass = bool(pf_rho > 0)

    verdict = ("LAW ESTABLISHED: a-priori metabolic-autonomy predicts FBA-transfer" if (h1_pass and (h2_pass or h3_pass))
               else "HONEST NEGATIVE: transfer-condition NOT quantifiable from GEM topology alone (stays qualitative)")

    out = {"panel_n": len(rows), "missing": missing, "features_used": FEATS, "signs": SIGNS,
           "H1_spearman_S_vs_logOR": {"rho": round(float(rho), 4), "p": float(p_rho), "boot95CI": ci, "PASS": h1_pass},
           "H2_AUROC_S_for_gatepass": {"auroc": round(auroc, 4), "PASS": h2_pass},
           "H3_within_Pfalciparum_swap": {"n_recon": len(pf_rows), "spearman_S_vs_OR": round(float(pf_rho), 4),
                                          "p": float(pf_p), "PASS": h3_pass,
                                          "recons": sorted([(r["recon"], r["OR"], r["S"]) for r in pf_rows], key=lambda x: x[2])},
           "VERDICT": verdict,
           "per_organism": sorted([(r["organism"], r["OR"], r["gate_pass"], r["S"]) for r in rows], key=lambda x: x[3]),
           "relationship_to_META1": "a-priori/non-circular (GEM topology only) predictor; META1 used outcome-entangled features post-hoc",
           "seed": SEED}
    payload = json.dumps(out, indent=2, sort_keys=True)
    open(os.path.join(RES, "TRANSFERLAW1_metrics.json"), "w").write(payload + "\n")
    open(os.path.join(RES, "payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    print(f"H1 rho(S,logOR)={rho:.3f} CI{ci} PASS={h1_pass} | H2 AUROC={auroc:.3f} PASS={h2_pass} | "
          f"H3 Pf-swap rho={pf_rho:.3f} PASS={h3_pass}")
    print("VERDICT:", verdict)
    print("per-organism (sorted by S):")
    for org, orr, gpv, s in sorted([(r["organism"], r["OR"], r["gate_pass"], r["S"]) for r in rows], key=lambda x: x[3]):
        print(f"  S={s:+.2f}  OR={orr:<7} pass={gpv}  {org}")
    print("sha256:", hashlib.sha256(payload.encode()).hexdigest())

if __name__ == "__main__":
    main()
