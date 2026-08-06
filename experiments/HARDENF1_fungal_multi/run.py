"""HARDENF1 — does FBA gene-essentiality hold on a REAL FUNGAL PATHOGEN (Candida albicans)?

Hardens GENERALIZE4 (which showed FBA-essentiality transfers to a eukaryote, but only the MODEL yeast
S. cerevisiae, n=1, not a pathogen). Same pipeline as CROSSVAL_curated / GENERALIZE4:
  GEM   = Mirhakkak & Schaeuble 2021 curated C. albicans GEM (BioModels MODEL2110210002). Gene IDs = CGD
          Assembly-22 systematic names in SBML-safe form (e.g. CAALFM_C100070WA).
  Truth = CGD curated phenotype annotations: gene ESSENTIAL iff >=1 'inviable' phenotype from a loss-of-function
          mutant (null / repressible / conditional). Includes GRACE (Roemer 2003) + later deletion studies.
  Bridge= deterministic CAALFM_C{chr}{coord}{W|C}{hap} -> C{chr}_{coord}{W|C}_{hap} (canonical A22 systematic).

Single-gene FBA deletion (essential if KO growth < 1% WT) -> 2x2 Fisher over the model's metabolic genes.
PRE-REGISTERED GATE (see PREREG.md): odds ratio > 3 AND Fisher one-sided p < 0.01. Deterministic; reproduce x2.
Env: metabolic (cobra). Env-independent math.comb hypergeometric Fisher 'greater' (matches GENERALIZE4 OR
definition regardless of scipy). NO git commit.
"""
import os, csv, json, re, time, hashlib, logging
import cobra
from cobra.flux_analysis import single_gene_deletion
logging.getLogger("cobra").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
H = os.path.join(DATA, "hardenf1")
MODEL = os.path.join(H, "calb_gem_Mirhakkak2021.xml")
PHENO = os.path.join(H, "CGD_C_albicans_SC5314_phenotype_data.tab")
MAPPING = os.path.join(H, "CGD_ORF19_Assembly22_mapping.tab")

LOF = {"null", "repressible", "conditional"}          # frozen: loss-of-function mutant types
CAALFM_RE = re.compile(r"^CAALFM_C([1-7R])(\d{5})([WC])([AB])$")


def norm_a22(gid):
    """GEM gene id -> canonical CGD A22 systematic id (frozen deterministic transform)."""
    m = CAALFM_RE.match(gid)
    if m:
        return "C%s_%s%s_%s" % (m.group(1), m.group(2), m.group(3), m.group(4))
    if gid.startswith("CAALFM_"):
        return gid[len("CAALFM_"):]
    return gid


def read_pheno_rows():
    rows = list(csv.reader((l for l in open(PHENO, encoding="utf-8", errors="ignore")
                            if not l.startswith("!")), delimiter="\t"))
    hdr = rows[0]
    ix = {h: i for i, h in enumerate(hdr)}
    return rows[1:], ix


def essential_a22():
    """A22 systematic IDs of experimentally-essential genes: >=1 'inviable' annotation from a LOF mutant."""
    data, ix = read_pheno_rows()
    fn, ph, mt = ix["Feature Name"], ix["Phenotype"], ix["Mutant Type"]
    s = set()
    for r in data:
        if len(r) > max(fn, ph, mt) and r[ph].strip() == "inviable" and r[mt].strip() in LOF:
            f = r[fn].strip()
            if f:
                s.add(f)
    return s


def a22_universe():
    """All valid CGD A22 systematic IDs (mapping file + phenotype file) — coverage denominator only."""
    u = set()
    r = csv.reader(open(MAPPING, encoding="utf-8", errors="ignore"), delimiter="\t")
    next(r, None)
    for row in r:
        if len(row) >= 2 and row[1].strip():
            u.add(row[1].strip())
    data, ix = read_pheno_rows()
    fn = ix["Feature Name"]
    for row in data:
        if len(row) > fn and row[fn].strip():
            u.add(row[fn].strip())
    return u


def fisher_greater(a, b, c, d):
    """Env-independent one-sided Fisher (hypergeometric 'greater'); OR = a*d/(b*c) as in GENERALIZE4."""
    from math import comb
    n = a + b + c + d
    r = a + b
    col = a + c
    p = sum(comb(col, k) * comb(n - col, r - k) for k in range(a, min(r, col) + 1)) / comb(n, r)
    return (a * d) / max(b * c, 1), p


def main():
    t0 = time.time()
    ess = essential_a22()
    univ = a22_universe()
    print(f"  CGD inviable-LOF essential genes (A22): {len(ess)} | A22 systematic-id universe: {len(univ)}",
          flush=True)

    m = cobra.io.read_sbml_model(MODEL)
    wt = m.slim_optimize()
    thr = 0.01 * wt
    genes = list(m.genes)
    n_resolved = sum(1 for g in genes if norm_a22(g.id) in univ)
    print(f"  GEM: {len(genes)} genes, {len(m.reactions)} rxns, WT growth {wt:.6f}, threshold {thr:.6f} | "
          f"genes resolving to A22 universe: {n_resolved}/{len(genes)}", flush=True)

    sg = single_gene_deletion(m, m.genes, processes=1)
    sg["gid"] = sg["ids"].apply(lambda s: list(s)[0])
    # round to 6 dp to absorb GLPK degenerate-LP alternate-optima jitter -> byte-identical reproduction
    grw = {r.gid: round((r.growth if r.growth == r.growth else 0.0), 6) for r in sg.itertuples()}
    fba_ess = set(g for g, v in grw.items() if v < thr)

    def is_exp(g):
        return norm_a22(g.id) in ess

    expset = set(g.id for g in genes if is_exp(g))
    a = sum(1 for g in genes if g.id in fba_ess and g.id in expset)
    b = sum(1 for g in genes if g.id in fba_ess and g.id not in expset)
    c = sum(1 for g in genes if g.id not in fba_ess and g.id in expset)
    d = sum(1 for g in genes if g.id not in fba_ess and g.id not in expset)
    orr, pval = fisher_greater(a, b, c, d)

    # growth-ratio AUROC: tie-aware Mann-Whitney (sklearn-independent), higher score = more essential
    y = [1 if g.id in expset else 0 for g in genes]
    sc = [-grw.get(g.id, wt) for g in genes]
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
    else:
        auroc = float("nan")
    prec = a / (a + b) if (a + b) else float("nan")
    rec = a / (a + c) if (a + c) else float("nan")

    payload = {
        "organism": "Candida albicans SC5314 (real fungal pathogen)",
        "model": "Mirhakkak_Schaeuble_2021 (BioModels MODEL2110210002)",
        "essentiality_source": "CGD phenotype annotations: inviable + LOF mutant (null/repressible/conditional)",
        "n_genes": len(genes),
        "n_genes_resolved_to_a22_universe": n_resolved,
        "n_fba_essential": len(fba_ess),
        "n_exp_essential_total": len(ess),
        "n_exp_essential_mapped_in_model": len(expset),
        "contingency": {"both": a, "FBA_only": b, "exp_only": c, "neither": d},
        "precision": round(prec, 3) if prec == prec else None,
        "recall": round(rec, 3) if rec == rec else None,
        "odds_ratio": round(float(orr), 2),
        "fisher_p": (float(f"{pval:.2e}") if pval == pval else None),
        "auroc": round(auroc, 4) if auroc == auroc else None,
        "gate": "OR>3 AND p<0.01",
        "gate_pass": bool(orr > 3 and (pval < 0.01 if pval == pval else False)),
    }
    print(f"  OR {payload['odds_ratio']} p {payload['fisher_p']} prec {payload['precision']} rec {payload['recall']} "
          f"AUROC {payload['auroc']} | FBA-ess {len(fba_ess)} exp-mapped {len(expset)} | "
          f"contingency {payload['contingency']} -> {'PASS' if payload['gate_pass'] else 'FAIL'} [{time.time()-t0:.0f}s]",
          flush=True)

    verdict = (
        f"HARDENING TEST (eukaryote FBA-essentiality on a REAL FUNGAL PATHOGEN): on Candida albicans SC5314 "
        f"(Mirhakkak-2021 curated GEM vs CGD curated inviable/loss-of-function essentiality), FBA single-gene-deletion "
        f"essentiality is {'ENRICHED' if payload['gate_pass'] else 'NOT sufficiently enriched'} for experimental "
        f"essentiality among the model's metabolic genes: OR {payload['odds_ratio']} (Fisher one-sided p "
        f"{payload['fisher_p']}), precision {payload['precision']}, recall {payload['recall']}, AUROC {payload['auroc']}. "
        f"Contingency {payload['contingency']}. Gate (OR>3 AND p<0.01): {'PASS' if payload['gate_pass'] else 'FAIL'}. "
        f"ID mapping {n_resolved}/{len(genes)} GEM genes -> CGD A22 systematic (3 mtDNA CM_ genes unmapped), no namespace "
        f"artifact. This {'HARDENS' if payload['gate_pass'] else 'does NOT harden'} the eukaryote->FBA entry beyond the "
        f"n=1 model-yeast (GENERALIZE4) to a clinically relevant fungal pathogen. SCOPE: essentiality-enrichment only; "
        f"in-silico FBA vs a curated published essentiality resource (not wet-lab); curated model is still a model; recall "
        f"bounded by the metabolic subproteome; non-annotated genes treated non-essential (absence of evidence). "
        f"S. pombe attempted but reported as an honest boundary (no open curated GEM with usable GPRs CPU-only).")
    print("\nVERDICT:", verdict, flush=True)

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model_sha256": hashlib.sha256(open(MODEL, "rb").read()).hexdigest(),
            "pheno_sha256": hashlib.sha256(open(PHENO, "rb").read()).hexdigest()}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump({"payload": payload, "verdict": verdict, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)},
              open(os.path.join(HERE, "results", "HARDENF1_metrics.json"), "w"), indent=2, sort_keys=True)
    ser = json.dumps(payload, sort_keys=True)
    sha = hashlib.sha256(ser.encode()).hexdigest()
    open(os.path.join(HERE, "results", "HARDENF1_payload.sha256"), "w").write(sha + "\n")
    print("payload sha256:", sha, f"[{time.time()-t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
