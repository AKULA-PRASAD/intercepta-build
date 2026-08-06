"""HOSTCTX1 — does EXPRESSION-CONSTRAINED context-specific FBA (E-Flux) RESCUE the malaria essentiality signal?

Clean controlled A/B vs GENERALIZE5: SAME iPfal19 GEM, SAME Zhang 2018 experimental truth, SAME alias map, SAME
gene-ID canonicalization, SAME 2x2 Fisher gate (OR>3 AND p<0.01), SAME essential-if-KO-growth<1%WT rule, SAME 6-dp
rounding. The ONLY difference is the E-Flux flux-capacity layer (Colijn et al. 2009). Blood-stage expression =
Malaria Cell Atlas (Howick 2019) asexual mean expression per PF3D7_ gene. Deterministic; reproduced x2. See PREREG.md.
Env: metabolic (cobra 0.31; NO scipy -> math.comb hypergeometric Fisher fallback).
"""
import os, sys, csv, json, time, hashlib, logging, ast, statistics
import cobra
from cobra.flux_analysis import single_gene_deletion
logging.getLogger("cobra").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
G5 = os.path.join(DATA, "generalize5")
H1 = os.path.join(DATA, "hostctx1")
MODEL = os.path.join(G5, "iPfal19.xml")
ZHANG = os.path.join(G5, "zhang2018_essentiality.csv")
ALIAS = os.path.join(G5, "Pfalciparum3D7_GeneAliases.csv")
EXPR = os.path.join(H1, "malariacellatlas_bloodstage_expression.csv")

DEFAULT_BOUND = 1000.0
EPS_BOUND = 1e-3


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---- reused VERBATIM from GENERALIZE5 (mapping + gate) ----
def fisher_greater(a, b, c, d):
    try:
        from scipy.stats import fisher_exact
        orr, p = fisher_exact([[a, b], [c, d]], alternative="greater")
        return float(orr), float(p)
    except Exception:
        from math import comb
        n = a + b + c + d; r = a + b; col = a + c
        p = sum(comb(col, k) * comb(n - col, r - k) for k in range(a, min(r, col) + 1)) / comb(n, r)
        orr = (a * d) / max(b * c, 1)
        return float(orr), float(p)


def load_aliases():
    amap = {}
    with open(ALIAS, encoding="utf-8", errors="ignore") as f:
        for row in csv.reader(f):
            if not row or not row[0].strip() or row[0].strip() == "name1":
                continue
            canon = row[0].strip()
            for cell in row:
                c = cell.strip()
                if c and c.upper() != "NA":
                    amap[c.lower()] = canon
    return amap


def load_zhang():
    z = {}
    for row in csv.DictReader(open(ZHANG, encoding="utf-8", errors="ignore")):
        gid = row["Gene ID"].strip().upper()
        if not gid:
            continue
        try:
            mis = float(row["Zhang MIS"]) if row["Zhang MIS"] not in ("", "NA") else None
        except ValueError:
            mis = None
        z[gid] = {"mis": mis, "phenotype": row["Zhang Phenotype"].strip()}
    return z


# ---- NEW: E-Flux layer ----
def load_expression(stage_col, aliases):
    """PF3D7 (upper) -> float expression for the chosen blood stage."""
    e = {}
    for row in csv.DictReader(open(EXPR, encoding="utf-8", errors="ignore")):
        gid = row["Gene ID"].strip().upper()
        v = row.get(stage_col, "")
        try:
            e[gid] = float(v)
        except (ValueError, TypeError):
            pass
    return e


def gpr_score(rule, gene_expr):
    """Reaction expression score from GPR: AND->min, OR->sum. Parse via Python AST (handles parentheses)."""
    if not rule.strip():
        return None
    tree = ast.parse(rule, mode="eval").body

    def walk(node):
        if isinstance(node, ast.BoolOp):
            vals = [walk(v) for v in node.values]
            if isinstance(node.op, ast.And):
                return min(vals)
            else:  # Or
                return sum(vals)
        if isinstance(node, ast.Name):
            return gene_expr[node.id]
        raise ValueError("unexpected GPR node: %r" % node)
    return walk(tree)


def apply_eflux(m, gene_expr, cap_at_default=False, normalization="median", eps_bound=EPS_BOUND):
    """Set gene-associated reaction bounds proportional to GPR expression score (Colijn 2009).
    Non-gene reactions (exchanges/uptake/spontaneous) keep ORIGINAL bounds. Returns diagnostics."""
    scores = {}
    for r in m.reactions:
        s = gpr_score(r.gene_reaction_rule, gene_expr)
        if s is not None:
            scores[r.id] = s
    pos = [v for v in scores.values() if v > 0]
    if normalization == "median":
        ref = statistics.median(pos)
    elif normalization == "max":
        ref = max(pos)
    else:
        raise ValueError(normalization)
    scale = DEFAULT_BOUND / ref
    for r in m.reactions:
        if r.id not in scores:
            continue  # non-gene reaction: keep original bounds (medium held identical to baseline)
        s = scores[r.id]
        bound = scale * s if s > 0 else eps_bound
        if cap_at_default:
            bound = min(bound, DEFAULT_BOUND)
        orig_lb, orig_ub = r.lower_bound, r.upper_bound
        if orig_lb < 0 and orig_ub > 0:      # reversible
            r.lower_bound, r.upper_bound = -bound, bound
        elif orig_ub > 0:                     # irreversible forward
            r.lower_bound, r.upper_bound = 0.0, bound
        elif orig_lb < 0:                     # irreversible reverse
            r.lower_bound, r.upper_bound = -bound, 0.0
        # (orig 0,0 reactions untouched)
    return {"n_scored_reactions": len(scores), "scale": scale, "reference_score": ref,
            "n_zero_score_reactions": sum(1 for v in scores.values() if v <= 0)}


def essential_set(m):
    """single_gene_deletion essentiality on model m (as bounded). Returns (fba_ess set, growth dict, wt)."""
    wt = round(float(m.slim_optimize()), 6)
    thr = 0.01 * wt
    genes = list(m.genes)
    sg = single_gene_deletion(m, genes, processes=1)
    sg["gid"] = sg["ids"].apply(lambda s: list(s)[0])
    gr = {r.gid: round(float(r.growth), 6) for r in sg.itertuples()}
    fba_ess = set(g.id for g in genes if gr.get(g.id, wt) < thr)
    return fba_ess, gr, wt


def build_mapping(m, aliases, zhang):
    def canon(gid):
        u = gid.strip().upper()
        if u in zhang:
            return u
        a = aliases.get(gid.strip().lower())
        if a and a.upper() in zhang:
            return a.upper()
        return None
    mapped, unmapped = {}, []
    for g in m.genes:
        c = canon(g.id)
        if c:
            mapped[g.id] = c
        else:
            unmapped.append(g.id)
    return mapped, unmapped


def score(fba_ess, gr, wt, mapped, exp_ess_ids, label):
    a = b = c = d = 0
    for gid, cid in mapped.items():
        pe = gid in fba_ess
        ee = cid in exp_ess_ids
        if pe and ee: a += 1
        elif pe and not ee: b += 1
        elif not pe and ee: c += 1
        else: d += 1
    orr, p = fisher_greater(a, b, c, d)
    prec = a / (a + b) if (a + b) else None
    rec = a / (a + c) if (a + c) else None
    y = [1 if cid in exp_ess_ids else 0 for gid, cid in mapped.items()]
    sc = [-gr.get(gid, wt) for gid in mapped]
    auroc = None
    npos = sum(y); nneg = len(y) - npos
    if 0 < npos < len(y):
        order = sorted(range(len(sc)), key=lambda i: sc[i])
        ranks = [0.0] * len(sc); i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and sc[order[j + 1]] == sc[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[order[k]] = avg
            i = j + 1
        sum_pos = sum(ranks[i] for i in range(len(y)) if y[i] == 1)
        auroc = (sum_pos - npos * (npos + 1) / 2.0) / (npos * nneg)
    return {"definition": label,
            "wt_growth": round(float(wt), 6),
            "n_fba_essential": len(fba_ess),
            "n_exp_essential_mapped": sum(1 for cid in mapped.values() if cid in exp_ess_ids),
            "contingency": {"both": a, "FBA_only": b, "exp_only": c, "neither": d},
            "odds_ratio": round(orr, 3),
            "fisher_p_greater": float(f"{p:.3e}"),
            "precision": round(prec, 3) if prec is not None else None,
            "recall": round(rec, 3) if rec is not None else None,
            "auroc": round(auroc, 4) if auroc is not None else None,
            "gate_pass": bool(orr > 3 and p < 0.01)}


def eflux_arm(aliases, zhang, exp_primary, mapped, stage_col, cap_at_default, normalization, eps_bound, label):
    m = cobra.io.read_sbml_model(MODEL)
    expr_raw = load_expression(stage_col, aliases)
    covered = [expr_raw[g.id.strip().upper()] for g in m.genes if g.id.strip().upper() in expr_raw]
    default_expr = statistics.median(covered)
    # gene -> expression (direct, else alias, else median default)
    gene_expr = {}
    n_direct = n_alias = n_default = 0
    for g in m.genes:
        u = g.id.strip().upper()
        if u in expr_raw:
            gene_expr[g.id] = expr_raw[u]; n_direct += 1
        else:
            a = aliases.get(g.id.strip().lower())
            if a and a.upper() in expr_raw:
                gene_expr[g.id] = expr_raw[a.upper()]; n_alias += 1
            else:
                gene_expr[g.id] = default_expr; n_default += 1
    diag = apply_eflux(m, gene_expr, cap_at_default=cap_at_default, normalization=normalization, eps_bound=eps_bound)
    fba_ess, gr, wt = essential_set(m)
    s = score(fba_ess, gr, wt, mapped, exp_primary, label)
    s["expr_coverage"] = {"direct": n_direct, "alias": n_alias, "default_median": n_default,
                          "default_expr_value": round(default_expr, 6)}
    s["eflux_diag"] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in diag.items()}
    s["config"] = {"stage_col": stage_col, "cap_at_default": cap_at_default,
                   "normalization": normalization, "eps_bound": eps_bound}
    return s


def run():
    aliases = load_aliases()
    zhang = load_zhang()

    # ---- BASELINE ANCHOR: plain FBA (must reproduce GENERALIZE5) ----
    m0 = cobra.io.read_sbml_model(MODEL)
    mapped, unmapped = build_mapping(m0, aliases, zhang)
    exp_primary = set(cid for cid in mapped.values() if zhang[cid]["phenotype"] == "Non - Mutable in CDS")
    fba0, gr0, wt0 = essential_set(m0)
    plain = score(fba0, gr0, wt0, mapped, exp_primary, "PLAIN_FBA:phenotype:Non-Mutable-in-CDS")
    baseline_reproduced = (plain["contingency"] == {"both": 55, "FBA_only": 14, "exp_only": 218, "neither": 137}
                           and plain["odds_ratio"] == 2.469)

    TROPH = "MalariaCellAtlas Trophozoite Mean Expression"
    SCHIZ = "MalariaCellAtlas Schizont Mean Expression"
    RING = "MalariaCellAtlas Ring Mean Expression"

    # ---- PRIMARY E-Flux arm: trophozoite, median-norm, uncapped, eps 1e-3 ----
    eflux_primary = eflux_arm(aliases, zhang, exp_primary, mapped, TROPH, False, "median", 1e-3,
                              "EFLUX_TROPH:phenotype:Non-Mutable-in-CDS")

    # ---- SENSITIVITY: stage + scaling variants ----
    sens = {}
    sens["schizont"] = eflux_arm(aliases, zhang, exp_primary, mapped, SCHIZ, False, "median", 1e-3, "EFLUX_SCHIZONT")
    sens["ring"] = eflux_arm(aliases, zhang, exp_primary, mapped, RING, False, "median", 1e-3, "EFLUX_RING")
    sens["troph_capped"] = eflux_arm(aliases, zhang, exp_primary, mapped, TROPH, True, "median", 1e-3, "EFLUX_TROPH_CAPPED")
    sens["troph_maxnorm"] = eflux_arm(aliases, zhang, exp_primary, mapped, TROPH, False, "max", 1e-3, "EFLUX_TROPH_MAXNORM")
    sens["troph_eps0"] = eflux_arm(aliases, zhang, exp_primary, mapped, TROPH, False, "median", 0.0, "EFLUX_TROPH_EPS0")

    # IDC-average stage: build an averaged expression file on the fly is heavy; instead average via helper
    idc = idc_average_arm(aliases, zhang, exp_primary, mapped)
    sens["idc_average"] = idc

    def deltas(ef):
        return {"d_odds_ratio": round(ef["odds_ratio"] - plain["odds_ratio"], 3),
                "d_precision": round((ef["precision"] or 0) - (plain["precision"] or 0), 3),
                "d_recall": round((ef["recall"] or 0) - (plain["recall"] or 0), 3),
                "d_auroc": round((ef["auroc"] or 0) - (plain["auroc"] or 0), 4)}

    payload = {
        "organism": "Plasmodium falciparum 3D7 (malaria)",
        "model": "iPfal19",
        "experimental_source": "Zhang et al. 2018 Science (piggyBac saturation mutagenesis), phenotype 'Non - Mutable in CDS'",
        "expression_source": "Malaria Cell Atlas (Howick et al. 2019 Science 365:eaaw2619), asexual blood-stage mean expression per PF3D7_ gene, via PlasmoDB/Pf Target Browser Figshare 27190545",
        "essential_threshold_frac_WT": 0.01,
        "n_model_genes": len(m0.genes),
        "n_genes_mapped_to_zhang": len(mapped),
        "n_genes_unmapped": len(unmapped),
        "baseline_reproduced_vs_GENERALIZE5": bool(baseline_reproduced),
        "plain_FBA": plain,
        "eflux_primary": eflux_primary,
        "deltas_primary": deltas(eflux_primary),
        "sensitivity": {k: {"odds_ratio": v["odds_ratio"], "fisher_p_greater": v["fisher_p_greater"],
                            "precision": v["precision"], "recall": v["recall"], "auroc": v["auroc"],
                            "contingency": v["contingency"], "gate_pass": v["gate_pass"],
                            "n_fba_essential": v["n_fba_essential"], "wt_growth": v["wt_growth"],
                            "config": v["config"], "deltas": deltas(v)}
                        for k, v in sens.items()},
    }
    return payload, {"model_sha256": sha256_file(MODEL), "zhang_sha256": sha256_file(ZHANG),
                     "expr_sha256": sha256_file(EXPR)}


def idc_average_arm(aliases, zhang, exp_primary, mapped):
    """E-Flux with expression = mean of Ring/Troph/Schizont (IDC asexual average)."""
    m = cobra.io.read_sbml_model(MODEL)
    cols = ["MalariaCellAtlas Ring Mean Expression", "MalariaCellAtlas Trophozoite Mean Expression",
            "MalariaCellAtlas Schizont Mean Expression"]
    avg = {}
    for row in csv.DictReader(open(EXPR, encoding="utf-8", errors="ignore")):
        gid = row["Gene ID"].strip().upper()
        vals = []
        for c in cols:
            try:
                vals.append(float(row[c]))
            except (ValueError, TypeError, KeyError):
                pass
        if len(vals) == 3:
            avg[gid] = sum(vals) / 3.0
    covered = [avg[g.id.strip().upper()] for g in m.genes if g.id.strip().upper() in avg]
    default_expr = statistics.median(covered)
    gene_expr = {}
    for g in m.genes:
        u = g.id.strip().upper()
        if u in avg:
            gene_expr[g.id] = avg[u]
        else:
            a = aliases.get(g.id.strip().lower())
            gene_expr[g.id] = avg[a.upper()] if (a and a.upper() in avg) else default_expr
    diag = apply_eflux(m, gene_expr, cap_at_default=False, normalization="median", eps_bound=1e-3)
    fba_ess, gr, wt = essential_set(m)
    s = score(fba_ess, gr, wt, mapped, exp_primary, "EFLUX_IDC_AVERAGE")
    s["config"] = {"stage_col": "IDC_average(Ring,Troph,Schizont)", "cap_at_default": False,
                   "normalization": "median", "eps_bound": 1e-3}
    return s


def main():
    t0 = time.time()
    payload, filehashes = run()
    pl = payload["plain_FBA"]; ef = payload["eflux_primary"]; dl = payload["deltas_primary"]
    # verdict
    rescue = ef["gate_pass"] and ef["odds_ratio"] > pl["odds_ratio"]
    improved = ef["odds_ratio"] > pl["odds_ratio"] and ef["fisher_p_greater"] < 0.01
    if rescue:
        gate = "RESCUE"
    elif improved:
        gate = "PARTIAL"
    else:
        gate = "NEGATIVE"
    # robustness: does any sensitivity variant clear the gate?
    any_pass = any(v["gate_pass"] for v in payload["sensitivity"].values()) or ef["gate_pass"]
    any_improve = any(v["deltas"]["d_odds_ratio"] > 0 for v in payload["sensitivity"].values())
    verdict = (
        f"E-Flux context-specific FBA (Malaria Cell Atlas trophozoite expression) vs plain default-medium FBA on "
        f"iPfal19, essentiality-enrichment vs Zhang 2018. Baseline reproduced vs GENERALIZE5: "
        f"{payload['baseline_reproduced_vs_GENERALIZE5']}. PLAIN: OR {pl['odds_ratio']} p {pl['fisher_p_greater']} "
        f"prec {pl['precision']} rec {pl['recall']} AUROC {pl['auroc']} contingency {pl['contingency']}. "
        f"E-FLUX: OR {ef['odds_ratio']} p {ef['fisher_p_greater']} prec {ef['precision']} rec {ef['recall']} "
        f"AUROC {ef['auroc']} contingency {ef['contingency']}. Deltas {dl}. GATE (RESCUE iff OR>3 AND p<0.01 AND "
        f"OR>baseline): {gate}. Robustness: any variant clears gate = {any_pass}; any variant improves OR over "
        f"baseline = {any_improve}. SCOPE: enrichment only; in-silico; one stage/atlas/model; n=1 parasite; "
        f"E-Flux scaling somewhat arbitrary (sensitivity swept)."
    )
    out = {"payload": payload, "verdict": verdict, "gate": gate,
           "provenance": {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                          "git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
                          "cobra_version": cobra.__version__,
                          "file_hashes": filehashes,
                          "runtime_sec": round(time.time() - t0, 1)}}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "HOSTCTX1_metrics.json"), "w"), indent=2, sort_keys=True)
    payload_json = json.dumps(payload, sort_keys=True)
    sha = hashlib.sha256(payload_json.encode()).hexdigest()
    open(os.path.join(HERE, "results", "HOSTCTX1_payload.sha256"), "w").write(sha + "\n")
    print("VERDICT:", verdict)
    print("\nPLAIN :", json.dumps(pl, sort_keys=True))
    print("EFLUX :", json.dumps(ef, sort_keys=True))
    print("DELTAS:", json.dumps(dl, sort_keys=True))
    print("\nSENSITIVITY:")
    for k, v in payload["sensitivity"].items():
        print(f"  {k:16s} OR {v['odds_ratio']:.3f} p {v['fisher_p_greater']:.2e} prec {v['precision']} "
              f"rec {v['recall']} pass {v['gate_pass']} dOR {v['deltas']['d_odds_ratio']:+.3f} cont {v['contingency']}")
    print("\nGATE:", gate)
    print("payload sha256:", sha, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
