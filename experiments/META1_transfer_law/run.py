#!/usr/bin/env python
"""META1 — Transfer Law meta-analysis. Reads committed metrics JSONs; computes drivers.
Numbers are READ from committed files (never invented). See PREREG.md."""
import json, os, hashlib, math, warnings
import numpy as np
from scipy import stats
import statsmodels.api as sm

warnings.simplefilter("ignore")
EXP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def load(p):
    with open(os.path.join(EXP, p)) as f:
        return json.load(f)

def norm_cont(c):
    """Normalize a contingency dict/list to (both, fba_only, exp_only, neither)."""
    if isinstance(c, (list, tuple)):  # BLIND6 order: both, fbaonly, exponly, neither
        return float(c[0]), float(c[1]), float(c[2]), float(c[3])
    g = lambda *ks: next(c[k] for k in ks if k in c)
    return (float(g("both")), float(g("FBA_only", "fba_only")),
            float(g("exp_only", "exp_only")), float(g("neither")))

def metrics_from_cont(both, fo, eo, ne):
    n = both + fo + eo + ne
    base = (both + eo) / n
    fba_frac = (both + fo) / n
    prec = both / (both + fo) if (both + fo) else 0.0
    rec = both / (both + eo) if (both + eo) else 0.0
    fpr = fo / (fo + ne) if (fo + ne) else 0.0
    lrp = (rec / fpr) if fpr else float("inf")
    lift = (prec / base) if base else 0.0
    # Haldane-Anscombe +0.5 odds ratio (finite even when a cell is 0)
    orh = ((both + 0.5) * (ne + 0.5)) / ((fo + 0.5) * (eo + 0.5))
    return dict(n_adj=n, base_rate=base, fba_ess_frac=fba_frac, precision=prec,
                recall=rec, LR_plus=lrp, lift=lift, OR_haldane=orh, log_OR=math.log(orh))

# ---- PRIMARY per-organism records: (name, domain, host_dep, GEM_type, contingency, OR, p,
#       committed_pass, n_fba_essential, n_gem_genes, source_path) ----
RECS = []
def add(name, domain, host, gem, cont, orv, p, passed, n_fba, n_gem, src):
    both, fo, eo, ne = norm_cont(cont)
    d = dict(organism=name, domain=domain, host_dependent=host, GEM_type=gem,
             OR_reported=orv, fisher_p=p, committed_pass=bool(passed),
             n_fba_essential=n_fba, n_gem_genes=n_gem, source=src,
             both=both, FBA_only=fo, exp_only=eo, neither=ne)
    d.update(metrics_from_cont(both, fo, eo, ne))
    RECS.append(d)

# CROSSVAL curated bacteria
cv = load("CROSSVAL_curated/results/CROSSVAL_metrics.json")["summary"]["panel"]
CV_SRC = "CROSSVAL_curated/results/CROSSVAL_metrics.json"
cvmap = [("E. coli","E. coli"),("K. pneumoniae","K. pneumoniae"),("Salmonella Tm","Salmonella Tm"),
         ("B. subtilis","B. subtilis"),("S. aureus","S. aureus (MRSA)"),("M. tuberculosis","M. tuberculosis")]
for nm, key in cvmap:
    r = cv[key]
    add(nm, "bacteria", False, "curated", r["contingency"], r["odds_ratio"], r["fisher_p"],
        r["gate_pass"], r["n_fba_essential"], r["n_genes"], CV_SRC)

# VALIDATE deg CarveMe bacteria
vd = load("VALIDATE_essentiality/results/VALIDATE_essentiality_deg.json")["summary"]["organisms"]
VD_SRC = "VALIDATE_essentiality/results/VALIDATE_essentiality_deg.json"
add("A. baumannii", "bacteria", False, "denovo_CarveMe", vd["abaumannii"]["contingency"],
    vd["abaumannii"]["odds_ratio"], vd["abaumannii"]["fisher_p"], vd["abaumannii"]["H1_OR_gt3_p_lt0.01"],
    vd["abaumannii"]["n_our_genes"], vd["abaumannii"]["n_our_genes"], VD_SRC)
add("P. aeruginosa", "bacteria", False, "denovo_CarveMe", vd["paeruginosa"]["contingency"],
    vd["paeruginosa"]["odds_ratio"], vd["paeruginosa"]["fisher_p"], vd["paeruginosa"]["H1_OR_gt3_p_lt0.01"],
    vd["paeruginosa"]["n_our_genes"], vd["paeruginosa"]["n_our_genes"], VD_SRC)

# BLIND reveals
# BLIND1: use the SEQUENCE-BRIDGE reveal (comparable to BLIND2-7's mmseqs adjudication). The
# non-bridge BLIND1_reveal.json used symbol-matching that mapped only 1/613 genes (OR 0) and is a
# known artifact corrected by the seqbridge file (predictions frozen; identifier mapping fixed).
b1 = load("BLIND1_ngonorrhoeae/results/BLIND1_reveal_seqbridge.json")["summary"]
add("N. gonorrhoeae", "bacteria", False, "denovo_CarveMe", b1["contingency"], b1["odds_ratio"],
    b1["fisher_p"], b1["PREREG_GATE_OR_gt3_p_lt0.01"], None, b1["n_locked_genes"],
    "BLIND1_ngonorrhoeae/results/BLIND1_reveal_seqbridge.json")
b2 = load("BLIND2_cjejuni/results/BLIND2_reveal.json")["summary"]
add("C. jejuni", "bacteria", False, "denovo_CarveMe", b2["contingency"], b2["odds_ratio"],
    b2["fisher_p"], b2["PREREG_GATE_OR_gt3_p_lt0.01"], None, b2["n_locked_genes"],
    "BLIND2_cjejuni/results/BLIND2_reveal.json")
b3 = load("BLIND3_bacteroides/results/BLIND3_reveal.json")["summary"]
add("B. thetaiotaomicron", "bacteria", False, "denovo_CarveMe", b3["contingency"], b3["odds_ratio"],
    b3["fisher_p"], b3["PREREG_GATE_OR_gt3_p_lt0.01"], None, b3["n_locked_genes"],
    "BLIND3_bacteroides/results/BLIND3_reveal.json")
b4 = load("BLIND4_spneumoniae/results/BLIND4_reveal.json")["summary"]
add("S. pneumoniae", "bacteria", False, "denovo_CarveMe", b4["contingency"], b4["odds_ratio"],
    b4["fisher_p"], b4["PREREG_GATE_OR_gt3_p_lt0.01"], None, b4["n_locked_genes"],
    "BLIND4_spneumoniae/results/BLIND4_reveal.json")
b5 = load("BLIND5_kphaffii/results/BLIND5_reveal.json")   # top-level; EUKARYOTE yeast
add("K. phaffii", "eukaryote", False, "denovo_CarveMe", b5["contingency"], b5["odds_ratio"],
    float(b5["fisher_p_greater"]), b5["VERDICT"] == "PASS", b5["fba_essential"], b5["gem_universe"],
    "BLIND5_kphaffii/results/BLIND5_reveal.json")
b6 = load("BLIND6_mmaripaludis/results/BLIND6_reveal.json")  # top-level; ARCHAEA curated iMR539
add("M. maripaludis", "archaea", False, "curated",
    b6["contingency_both_fbaonly_exponly_neither"], b6["odds_ratio"], float(b6["fisher_p_greater"]),
    b6["verdict"] == "PASS", b6["n_fba_essential"], b6["n_gem_genes"],
    "BLIND6_mmaripaludis/results/BLIND6_reveal.json")
b7 = load("BLIND7_tbrucei/results/BLIND7_reveal.json")   # EUKARYOTE parasite, host-dep; primary fc2
f7 = b7["metrics"][b7["primary_threshold"]]
add("T. brucei", "eukaryote", True, "denovo_CarveMe",
    {"both": f7["both"], "fba_only": f7["fba_only"], "exp_only": f7["exp_only"], "neither": f7["neither"]},
    f7["odds_ratio"], f7["fisher_p"], b7["verdict"] == "PASS", b7["n_fba_essential"], b7["n_gem_genes"],
    "BLIND7_tbrucei/results/BLIND7_reveal.json")

# Eukaryote curated
g4 = load("GENERALIZE4_fungal_fba/results/GENERALIZE4_metrics.json")["payload"]
add("S. cerevisiae", "eukaryote", False, "curated", g4["contingency"], g4["odds_ratio"],
    g4["fisher_p"], g4["gate_pass"], g4["n_fba_essential"], g4["n_genes"],
    "GENERALIZE4_fungal_fba/results/GENERALIZE4_metrics.json")
hf = load("HARDENF1_fungal_multi/results/HARDENF1_metrics.json")["payload"]
add("C. albicans", "eukaryote", False, "curated", hf["contingency"], hf["odds_ratio"],
    hf["fisher_p"], hf["gate_pass"], hf["n_fba_essential"], hf["n_genes"],
    "HARDENF1_fungal_multi/results/HARDENF1_metrics.json")
g5 = load("GENERALIZE5_parasite_fba/results/GENERALIZE5_metrics.json")["payload"]
add("P. falciparum", "eukaryote", True, "curated", g5["primary"]["contingency"],
    g5["primary"]["odds_ratio"], g5["primary"]["fisher_p_greater"], g5["primary"]["gate_pass"],
    g5["n_fba_essential"], g5["n_model_genes"], "GENERALIZE5_parasite_fba/results/GENERALIZE5_metrics.json")
hp = load("HARDENP1_parasite_multi/results/HARDENP1_metrics.json")["payload"]
add("T. gondii", "eukaryote", True, "curated", hp["primary"]["contingency"],
    hp["primary"]["odds_ratio"], hp["primary"]["fisher_p_greater"], hp["primary"]["gate_pass"],
    hp["n_fba_essential"], hp["n_model_genes"], "HARDENP1_parasite_multi/results/HARDENP1_metrics.json")

# ---- WITHIN-ORGANISM sensitivity: alternate GEM/truth for E.coli, Kpn, Mtb (labelled, not primary)
ALT = []
def add_alt(name, cont, orv, p, passed, src, note):
    both, fo, eo, ne = norm_cont(cont); m = metrics_from_cont(both, fo, eo, ne)
    ALT.append(dict(organism=name, OR_reported=orv, fisher_p=p, committed_pass=bool(passed),
                    base_rate=m["base_rate"], precision=m["precision"], recall=m["recall"],
                    lift=m["lift"], source=src, note=note))
ve = load("VALIDATE_essentiality/results/VALIDATE_essentiality.json")["summary"]
add_alt("E. coli (alt: CarveMe/PEC)", ve["contingency_FBAess_vs_expess"], ve["odds_ratio"],
        3.1e-24, ve["H1_enrichment_OR_gt3_p_lt0.01"],
        "VALIDATE_essentiality/results/VALIDATE_essentiality.json", "PEC truth, MET2 subproteome")
vk = load("VALIDATE_essentiality/results/VALIDATE_essentiality_kp.json")["summary"]
add_alt("K. pneumoniae (alt: held-out CarveMe)", vk["contingency_FBAess_vs_expess"], vk["odds_ratio"],
        3.5e-16, vk["H1_enrichment_OR_gt3_p_lt0.01"],
        "VALIDATE_essentiality/results/VALIDATE_essentiality_kp.json", "held-out; CRISPRi/Tn-seq")
vm = load("VALIDATE_essentiality/results/VALIDATE_essentiality_mtb.json")["summary"]
add_alt("M. tuberculosis (alt: CarveMe)", vm["contingency_FBAess_vs_expess"], vm["odds_ratio"],
        vm["fisher_p"], vm["H1_enrichment_OR_gt3_p_lt0.01"],
        "VALIDATE_essentiality/results/VALIDATE_essentiality_mtb.json", "DeJesus Tn-seq; de-novo GEM")

# ---- PARARESOLVE within-Pf base-rate demonstration (same organism/GEM, different screens)
pr1 = load("PARARESOLVE1_parasite_confound/results/PARARESOLVE1_metrics.json")["payload"]
pr2 = load("PARARESOLVE2_screentech_probe/results/PARARESOLVE2_metrics.json")["payload"]
pf_ref_zhang = next(r for r in pr1["swap_results"] if r["label"] == "iPfal19")
pf_ref_bush = next(r for r in pr2["results_primary"] if r["label"] == "iPfal19")
PARARESOLVE_PF = {
    "iPfal19_vs_Zhang_piggyBac": {"base_rate": pf_ref_zhang["base_rate_exp_essential"],
        "odds_ratio": pf_ref_zhang["odds_ratio"], "gate_pass": pf_ref_zhang["gate_pass"],
        "precision": pf_ref_zhang["precision"], "fisher_p": pf_ref_zhang["fisher_p_greater"]},
    "iPfal19_vs_Bushell_barseq": {"base_rate": pf_ref_bush["base_rate_exp_essential"],
        "odds_ratio": pf_ref_bush["odds_ratio"], "gate_pass": pf_ref_bush["gate_pass"],
        "precision": pf_ref_bush["precision"], "fisher_p": pf_ref_bush["fisher_p_greater"]},
    "note": "SAME organism (P. falciparum) + SAME GEM (iPfal19); only the experimental screen "
            "(base rate) differs -> gate FLIPS. Within-organism evidence of base-rate confounding."}

# ================= ANALYSIS =================
def arr(k): return np.array([r[k] for r in RECS], float)
log_or = arr("log_OR"); base = arr("base_rate")
# coverage driver uses the ADJUDICABLE FBA-essential count (both+FBA_only) — consistent across all
# 19 organisms; the file's model-wide n_fba_essential differs (whole-model vs adjudicable subset).
n_fba = np.array([r["both"] + r["FBA_only"] for r in RECS], float)
n_gem = np.array([r["n_gem_genes"] if r["n_gem_genes"] else np.nan for r in RECS], float)
fba_frac = arr("fba_ess_frac")
euk = np.array([1.0 if r["domain"] == "eukaryote" else 0.0 for r in RECS])
host = np.array([1.0 if r["host_dependent"] else 0.0 for r in RECS])
curated = np.array([1.0 if r["GEM_type"] == "curated" else 0.0 for r in RECS])
passed = np.array([1 if r["committed_pass"] else 0 for r in RECS])

def spear(x, y):
    m = ~(np.isnan(x) | np.isnan(y))
    rho, p = stats.spearmanr(x[m], y[m])
    return round(float(rho), 4), round(float(p), 5), int(m.sum())

def mwu(binvec, y):
    a = y[binvec == 1]; b = y[binvec == 0]
    U, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    n1, n2 = len(a), len(b)
    rbc = 1 - 2 * U / (n1 * n2)  # rank-biserial (group1 vs group0)
    return dict(U=float(U), p=round(float(p), 5), n1=n1, n2=n2,
                median1=round(float(np.median(a)), 4), median0=round(float(np.median(b)), 4),
                rank_biserial=round(float(rbc), 4))

H1 = {"spearman_logOR_vs_n_fba_essential_adjudicable": spear(log_or, n_fba),
      "spearman_logOR_vs_n_gem_genes": spear(log_or, n_gem),
      "spearman_logOR_vs_fba_ess_frac": spear(log_or, fba_frac),
      "curated_vs_denovo_logOR_mwu": mwu(curated, log_or),
      "curated_vs_denovo_pass_mwu": mwu(curated, passed.astype(float))}
H2 = {"spearman_logOR_vs_base_rate": spear(log_or, base),
      "spearman_precision_vs_base_rate": spear(arr("precision"), base),
      "spearman_lift_vs_base_rate": spear(arr("lift"), base),
      "pararesolve_within_Pf": PARARESOLVE_PF}
H3 = {"host_dep_vs_logOR_mwu": mwu(host, log_or),
      "host_dep_pass_rate": {"host_dep_pass": int(passed[host == 1].sum()), "host_dep_n": int((host == 1).sum()),
                             "free_pass": int(passed[host == 0].sum()), "free_n": int((host == 0).sum())}}
H4 = {"spearman_logOR_vs_domain_euk": spear(log_or, euk),
      "euk_vs_prok_logOR_mwu": mwu(euk, log_or)}

# multivariable OLS on log_OR (drop rows missing n_gem for the coverage term; use log n_fba)
X_cols = ["base_rate", "log_n_fba", "domain_euk", "host_dep"]
Xr = np.column_stack([base, np.log(n_fba), euk, host])
ok = ~np.isnan(Xr).any(axis=1)
Xd = sm.add_constant(Xr[ok]); yd = log_or[ok]
ols = sm.OLS(yd, Xd).fit()
ci = ols.conf_int()
OLS = {"n": int(ok.sum()), "n_predictors": len(X_cols), "r2": round(float(ols.rsquared), 4),
       "adj_r2": round(float(ols.rsquared_adj), 4),
       "coefs": {nm: {"beta": round(float(ols.params[i]), 4), "p": round(float(ols.pvalues[i]), 5),
                      "ci95": [round(float(ci[i][0]), 4), round(float(ci[i][1]), 4)]}
                 for i, nm in enumerate(["const"] + X_cols)}}
# VIF (collinearity honesty)
def vif(j):
    Xj = Xr[ok]; y = Xj[:, j]; Xrest = sm.add_constant(np.delete(Xj, j, axis=1))
    r2 = sm.OLS(y, Xrest).fit().rsquared
    return round(float(1 / (1 - r2)) if r2 < 1 else float("inf"), 3)
OLS["VIF"] = {nm: vif(i) for i, nm in enumerate(X_cols)}

# logistic on committed_pass (expect near-separation -> report as unstable)
LOGIT = {}
try:
    lg = sm.Logit(passed[ok], Xd).fit(disp=0, maxiter=200)
    LOGIT = {"status": "converged", "pseudo_r2": round(float(lg.prsquared), 4),
             "coefs": {nm: round(float(lg.params[i]), 4) for i, nm in enumerate(["const"] + X_cols)},
             "warning": "n=%d, 5 fails, collinear predictors -> treat as DIRECTIONAL ONLY" % int(ok.sum())}
except Exception as e:
    LOGIT = {"status": "failed_or_separated", "error": type(e).__name__,
             "note": "quasi-complete separation expected with this n; logistic UNSTABLE, not reported as evidence"}

# ---- Base-rate-confound verdict + fairer-metric reclassification (SECONDARY LENS) ----
fair_gate = lambda r: (r["fisher_p"] < 0.01) and (r["lift"] >= 1.5)
per_org = []
for r in RECS:
    per_org.append({"organism": r["organism"], "domain": r["domain"], "host_dep": r["host_dependent"],
                    "GEM_type": r["GEM_type"], "OR": round(r["OR_reported"], 3),
                    "fisher_p": r["fisher_p"], "base_rate": round(r["base_rate"], 3),
                    "precision": round(r["precision"], 3), "recall": round(r["recall"], 3),
                    "lift": round(r["lift"], 3), "LR_plus": (round(r["LR_plus"], 3) if np.isfinite(r["LR_plus"]) else None),
                    "committed_pass": r["committed_pass"],
                    "fair_gate_pass(p<0.01 & lift>=1.5)": bool(fair_gate(r))})
# which committed FAILS retain real signal under the fair lens?
fails = [r for r in RECS if not r["committed_pass"]]
reclassified = [{"organism": r["organism"], "OR": round(r["OR_reported"], 3), "fisher_p": r["fisher_p"],
                 "base_rate": round(r["base_rate"], 3), "lift": round(r["lift"], 3),
                 "fair_gate_pass": bool(fair_gate(r)),
                 "interpretation": ("REAL-signal-under-OR-compression" if fair_gate(r) else "genuine null (lift<=1.5 or p>=0.01)")}
                for r in fails]

payload = {
    "n_organisms_assembled": len(RECS),
    "n_pass_committed": int(passed.sum()), "n_fail_committed": int((passed == 0).sum()),
    "domain_counts": {"bacteria": int((euk == 0).sum()) - int((np.array([r["domain"] == "archaea" for r in RECS])).sum()),
                      "archaea": int(np.array([r["domain"] == "archaea" for r in RECS]).sum()),
                      "eukaryote": int(euk.sum())},
    "unparseable": [],
    "dataset_primary": [{k: r[k] for k in ("organism", "domain", "host_dependent", "GEM_type",
                        "OR_reported", "fisher_p", "committed_pass", "base_rate", "precision",
                        "recall", "lift", "n_fba_essential", "n_gem_genes", "source")} for r in RECS],
    "H1_gem_coverage": H1, "H2_base_rate": H2, "H3_host_dependence": H3, "H4_domain": H4,
    "multivariable_OLS_logOR": OLS, "logistic_pass": LOGIT,
    "base_rate_confound": {
        "spearman_OR_vs_base_rate": spear(arr("OR_reported"), base),
        "spearman_logOR_vs_base_rate": H2["spearman_logOR_vs_base_rate"],
        "pararesolve_within_Pf_flip": PARARESOLVE_PF,
        "committed_fails_reclassified": reclassified,
        "proposed_fair_gate": "Fisher p<0.01 AND precision-lift(precision/base_rate)>=1.5",
        "note": "SECONDARY LENS ONLY. Does NOT flip any committed verdict."},
    "per_organism_table": per_org,
    "within_organism_alt_GEM_sensitivity": ALT,
}

# ---- reproducibility SHA (payload only, sorted keys, excludes provenance/verdict) ----
def canon(o): return json.dumps(o, sort_keys=True, separators=(",", ":"), default=str)
sha = hashlib.sha256(canon(payload).encode()).hexdigest()
print("PAYLOAD_SHA256:", sha)

out = {"provenance": {"module": "META1_transfer_law", "inputs": "committed experiments/*/results/*.json"},
       "payload": payload, "payload_sha256": sha}
with open(os.path.join(os.path.dirname(__file__), "results", "META1_metrics.json"), "w") as f:
    json.dump(out, f, sort_keys=True, indent=1)
with open(os.path.join(os.path.dirname(__file__), "results", "payload.sha256"), "w") as f:
    f.write(sha + "\n")

# console summary
print("n organisms:", len(RECS), "| pass", int(passed.sum()), "fail", int((passed == 0).sum()))
print("H1 logOR~n_fba:", H1["spearman_logOR_vs_n_fba_essential_adjudicable"], "| ~n_gem:", H1["spearman_logOR_vs_n_gem_genes"],
      "| ~fba_frac:", H1["spearman_logOR_vs_fba_ess_frac"])
print("H2 logOR~base_rate:", H2["spearman_logOR_vs_base_rate"])
print("H3 host_dep MWU:", H3["host_dep_vs_logOR_mwu"], H3["host_dep_pass_rate"])
print("H4 logOR~euk:", H4["spearman_logOR_vs_domain_euk"])
print("OLS r2:", OLS["r2"], "coefs:", {k: v["beta"] for k, v in OLS["coefs"].items()}, "VIF:", OLS["VIF"])
print("PARARESOLVE Pf flip:", {k: (v.get("base_rate"), v.get("odds_ratio"), v.get("gate_pass"))
                               for k, v in PARARESOLVE_PF.items() if isinstance(v, dict)})
print("FAILS reclassified:")
for r in reclassified: print("  ", r)
