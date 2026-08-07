"""PARARESOLVE2 — screen-technology ROBUSTNESS probe.

Score P. falciparum FBA single-gene-deletion essentiality vs the Bushell et al. 2017 (Cell 170:260)
*P. berghei* PlasmoGEM double-crossover-KO + barseq relative-growth-rate essentiality set — a THIRD screen
technology (distinct from Zhang 2018 piggyBac and from Sidik 2016 CRISPR). Truth = Bushell Table S1 authors'
own "Phenotype" label (PRIMARY essential == "Essential"; SENSITIVITY == "Essential"|"Slow"). Map Bushell
P. berghei genes onto the Pf GEMs via Bushell's authoritative PlasmoDB "P. falciparum ID" ortholog column.

HARD SCOPE: this is NOT a closure of the CRISPR-specific axis (no genome-wide Pf CRISPR screen exists) and it
carries a P. berghei -> P. falciparum SPECIES confound. Robustness evidence only. See PREREG.md.

Method IDENTICAL to GENERALIZE5/PARARESOLVE1/HARDENP1: COBRApy single_gene_deletion, KO growth rounded 6dp,
essential if KO<1% WT; 2x2 Fisher; estimator FROZEN to sample OR (a*d)/(b*c) + math.comb one-sided
hypergeometric. Env: metabolic (cobra 0.31.1, GLPK). Deterministic; reproduced x2 byte-identical.
"""
import os, csv, json, time, hashlib, logging, warnings
import cobra
from cobra.flux_analysis import single_gene_deletion
logging.getLogger("cobra").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
G = os.path.join(DATA, "generalize5")
P1 = os.path.join(DATA, "pararesolve1")
P2 = os.path.join(DATA, "pararesolve2")

BUSHELL = os.path.join(P2, "bushell2017_tableS1.csv")
BUSHELL_ZIP = os.path.join(P2, "bushell2017_europepmc_supplementaryFiles.zip")
BUSHELL_MMC1 = os.path.join(P2, "bushell_mmc", "mmc1.xlsx")

ZHANG_IPFAL19_OR = 2.469   # GENERALIZE5 anchor (FAIL, iPfal19 vs Zhang piggyBac)
TOXO_OR = 14.10            # HARDENP1 anchor (PASS, iTgo2020 vs Sidik CRISPR)

# (label, path, kind, source)
GEMS = [
    ("iPfal19", os.path.join(G, "iPfal19.xml"), "reference",
     "PARADIGM (Carey/Untaroiu/Papin, U.Virginia); Zhang-2018 anchor GEM (OR 2.47 FAIL)"),
    ("AbdelHaleem_2018_iAM-Pf480", os.path.join(P1, "pfal2018_abdel_haleem.xml"), "independent",
     "Abdel-Haleem et al. 2018 Cell Reports 24(9):2337, iAM-Pf480 (Palsson lab, UCSD); INDEPENDENT team"),
]

DEFINITIVE = {"Essential", "Slow", "Dispensable", "Fast"}  # exclude 'Insufficient data'
ESS_PRIMARY = {"Essential"}
ESS_SENSITIVITY = {"Essential", "Slow"}


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fisher_greater_sampleOR(a, b, c, d):
    """One-sided Fisher (greater) via math.comb hypergeometric; SAMPLE OR (a*d)/(b*c).
    FROZEN to GENERALIZE5/PARARESOLVE1/HARDENP1 (scipy deliberately not used)."""
    from math import comb
    n = a + b + c + d
    r = a + b
    col = a + c
    p = sum(comb(col, k) * comb(n - col, r - k) for k in range(a, min(r, col) + 1)) / comb(n, r)
    orr = (a * d) / max(b * c, 1)
    return float(orr), float(p)


def load_bushell():
    """Pf_ID (uppercase) -> phenotype label, for rows with a definitive Pf ortholog id."""
    pf2phen = {}
    for row in csv.DictReader(open(BUSHELL, encoding="utf-8", errors="ignore")):
        pf = (row["Pf_ID"] or "").strip().upper()
        phen = (row["Phenotype"] or "").strip()
        if pf and pf not in ("NA", "NONE", ""):
            pf2phen[pf] = phen
    return pf2phen


BUSHELL_PHEN = load_bushell()


def canon_pf(gid):
    """GEM gene id -> Bushell Pf ortholog id (strip .N/-pN suffix, uppercase)."""
    base = gid.split(".")[0].strip().upper()
    for cand in (base, gid.strip().upper()):
        if cand in BUSHELL_PHEN:
            return cand
    return None


def rank_auroc(y, sc):
    npos = sum(y); nneg = len(y) - npos
    if not (0 < npos < len(y)):
        return None
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
    return (sum_pos - npos * (npos + 1) / 2.0) / (npos * nneg)


def fba_essential_set(m):
    wt = round(float(m.slim_optimize()), 6)
    thr = 0.01 * wt
    genes = list(m.genes)
    sg = single_gene_deletion(m, genes, processes=1)
    sg["gid"] = sg["ids"].apply(lambda s: list(s)[0])
    gr = {r.gid: round(float(r.growth), 6) for r in sg.itertuples()}
    fba_ess = set(g.id for g in genes if gr.get(g.id, wt) < thr)
    return wt, gr, fba_ess


def score_one(label, path, kind, source, ess_labels):
    m = cobra.io.read_sbml_model(path)
    genes = list(m.genes)
    wt, gr, fba_ess = fba_essential_set(m)

    # map GEM genes to Bushell rows with a DEFINITIVE phenotype
    mapped = {}          # gid -> pf_id
    for g in genes:
        pf = canon_pf(g.id)
        if pf and BUSHELL_PHEN.get(pf) in DEFINITIVE:
            mapped[g.id] = pf
    exp_ess = set(pf for pf in mapped.values() if BUSHELL_PHEN.get(pf) in ess_labels)

    a = b = c = d = 0
    for gid, pf in mapped.items():
        pe = gid in fba_ess
        ee = pf in exp_ess
        if pe and ee: a += 1
        elif pe and not ee: b += 1
        elif not pe and ee: c += 1
        else: d += 1
    orr, p = fisher_greater_sampleOR(a, b, c, d)
    y = [1 if pf in exp_ess else 0 for gid, pf in mapped.items()]
    sc = [-gr.get(gid, wt) for gid in mapped]
    auroc = rank_auroc(y, sc)
    return {
        "label": label, "kind": kind, "source": source,
        "essential_definition": "|".join(sorted(ess_labels)),
        "model_sha256": sha256_file(path),
        "wt_growth": round(float(wt), 4),
        "n_model_genes": len(genes),
        "n_fba_essential": len(fba_ess),
        "n_genes_mapped_definitive": len(mapped),
        "map_frac": round(len(mapped) / len(genes), 3),
        "n_exp_essential_mapped": len(exp_ess),
        "base_rate_exp_essential": round(len(exp_ess) / len(mapped), 3) if mapped else None,
        "contingency": {"both": a, "FBA_only": b, "exp_only": c, "neither": d},
        "odds_ratio": round(orr, 3),
        "fisher_p_greater": float(f"{p:.3e}"),
        "precision": round(a / (a + b), 3) if (a + b) else None,
        "recall": round(a / (a + c), 3) if (a + c) else None,
        "auroc": round(auroc, 4) if auroc is not None else None,
        "gate_pass": bool(orr > 3 and p < 0.01),
    }


def run():
    primary = [score_one(l, p, k, s, ESS_PRIMARY) for (l, p, k, s) in GEMS]
    sensitivity = [score_one(l, p, k, s, ESS_SENSITIVITY) for (l, p, k, s) in GEMS]

    # phenotype distribution of the Bushell truth (over Pf-mapped definitive genes) for transparency
    from collections import Counter
    phen_counts = Counter(v for v in BUSHELL_PHEN.values())

    ref_primary = next(s for s in primary if s["kind"] == "reference")
    all_fail = all(not s["gate_pass"] for s in primary)
    any_pass = any(s["gate_pass"] for s in primary)

    payload = {
        "experiment": "PARARESOLVE2",
        "question": "Does P. falciparum FBA-essentiality ALSO FAIL against a THIRD screen technology "
                    "(Bushell 2017 P. berghei PlasmoGEM double-crossover-KO + barseq relative growth rate), "
                    "as it did vs Zhang 2018 piggyBac? Screen-technology ROBUSTNESS probe.",
        "hard_scope": "NOT a closure of the CRISPR-specific axis (no genome-wide Pf CRISPR screen exists). "
                      "Bushell is P. berghei -> scored on P. falciparum GEMs via PlasmoDB ortholog = a "
                      "cross-species confound. Partial-genome screen; robustness evidence only.",
        "experimental_source": "Bushell et al. 2017 Cell 170(2):260 (PMID 28708996, PMC5509546, open access); "
                               "Table S1 = mmc1.xlsx; essential = authors' 'Phenotype' label (barseq RGR).",
        "essential_definitions": {"primary": "Phenotype=='Essential'",
                                   "sensitivity": "Phenotype in {'Essential','Slow'}",
                                   "excluded": "Phenotype=='Insufficient data'"},
        "estimator": "sample OR (a*d)/(b*c) + one-sided hypergeometric via math.comb (FROZEN to GENERALIZE5)",
        "gate": "OR>3 AND p<0.01 (taken on PRIMARY definition)",
        "anchors": {"iPfal19_vs_Zhang_piggyBac_OR": ZHANG_IPFAL19_OR,
                    "iTgo2020_vs_Sidik_CRISPR_OR": TOXO_OR},
        "bushell_phenotype_counts_over_pf_mapped": dict(sorted(phen_counts.items())),
        "bushell_sha256": {
            "supplementary_zip": sha256_file(BUSHELL_ZIP) if os.path.exists(BUSHELL_ZIP) else None,
            "mmc1_xlsx": sha256_file(BUSHELL_MMC1) if os.path.exists(BUSHELL_MMC1) else None,
            "tableS1_csv": sha256_file(BUSHELL),
        },
        "results_primary": primary,
        "results_sensitivity": sensitivity,
        "reference_gem_gate_pass": ref_primary["gate_pass"],
        "all_gems_fail_primary": all_fail,
        "any_gem_pass_primary": any_pass,
        "residual_confounds_unresolved": [
            "CRISPR-specific axis NOT closed: no genome-wide saturating P. falciparum CRISPR essentiality "
            "screen exists (Pf CRISPR is gene-by-gene). This probe uses barseq-KO, a THIRD technology.",
            "SPECIES confound: Bushell screened P. berghei; scored on P. falciparum GEMs via Bushell's "
            "PlasmoDB Pf-ortholog column (authoritative but cross-species).",
            "Partial-genome screen (2578 genes) + ~56-62% GEM coverage (vs Zhang ~89%): lower power / "
            "possible mapping selection effect.",
            "Base-rate/biology residual (PARARESOLVE1) not eliminated by a screen-technology swap.",
        ],
    }
    return payload


def interpret(payload):
    def fmt(s):
        return (f"{s['label']} OR {s['odds_ratio']} p {s['fisher_p_greater']} "
                f"(rec {s['recall']}, prec {s['precision']}, base {s['base_rate_exp_essential']}, "
                f"n {s['n_genes_mapped_definitive']}, cov {s['map_frac']}) "
                f"-> {'PASS' if s['gate_pass'] else 'FAIL'}")
    prim = " | ".join(fmt(s) for s in payload["results_primary"])
    if payload["all_gems_fail_primary"]:
        axis = ("Plasmodium FBA ALSO FAILS vs Bushell barseq-KO (a THIRD screen technology) just as it failed "
                "vs Zhang piggyBac (2.47) -> the malaria FBA failure is SCREEN-TECHNOLOGY-ROBUST, NOT a "
                "piggyBac artifact -> the screen-technology axis is largely EXONERATED as the cause of the "
                "Pf-vs-Toxo (14.10) gap; the driver points back to GEM topology + base-rate/biology "
                "(consistent with PARARESOLVE1). NOTE: this does NOT close the CRISPR-specific axis and "
                "carries a P. berghei->P. falciparum species confound.")
    elif payload["any_gem_pass_primary"]:
        axis = ("At least one Pf GEM PASSES vs Bushell where it failed vs Zhang -> screen/dataset specifics "
                "matter; the piggyBac-specificity of Zhang is IMPLICATED. Report the split; species confound "
                "and no-CRISPR caveats still stand.")
    else:
        axis = "No GEM evaluable."
    sens = " | ".join(f"{s['label']} OR {s['odds_ratio']} ({'PASS' if s['gate_pass'] else 'FAIL'})"
                      for s in payload["results_sensitivity"])
    return (f"PRIMARY(Essential): {prim} || {axis} || SENSITIVITY(Essential+Slow): {sens} || "
            f"anchors: Zhang/iPfal19 2.47 FAIL, Toxo/Sidik 14.10 PASS.")


def main():
    t0 = time.time()
    payload = run()
    verdict = interpret(payload)
    out = {"payload": payload, "verdict": verdict,
           "provenance": {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                          "git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
                          "cobra_version": cobra.__version__,
                          "runtime_sec": round(time.time() - t0, 1)}}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "PARARESOLVE2_metrics.json"), "w"),
              indent=2, sort_keys=True)
    payload_json = json.dumps(payload, sort_keys=True)
    sha = hashlib.sha256(payload_json.encode()).hexdigest()
    open(os.path.join(HERE, "results", "PARARESOLVE2_payload.sha256"), "w").write(sha + "\n")
    print("=== PARARESOLVE2 vs Bushell 2017 barseq-KO (gate OR>3 & p<0.01) ===")
    print("Bushell phenotype counts (Pf-mapped):", payload["bushell_phenotype_counts_over_pf_mapped"])
    print("-- PRIMARY (essential == 'Essential') --")
    for s in payload["results_primary"]:
        print(f"  [{s['kind']:11s}] {s['label']:28s} OR {s['odds_ratio']:6.3f} p {s['fisher_p_greater']:9} "
              f"prec {s['precision']} rec {s['recall']} base {s['base_rate_exp_essential']} "
              f"n {s['n_genes_mapped_definitive']} cov {s['map_frac']} cont {s['contingency']} -> "
              f"{'PASS' if s['gate_pass'] else 'FAIL'}")
    print("-- SENSITIVITY (essential == 'Essential'|'Slow') --")
    for s in payload["results_sensitivity"]:
        print(f"  [{s['kind']:11s}] {s['label']:28s} OR {s['odds_ratio']:6.3f} p {s['fisher_p_greater']:9} "
              f"prec {s['precision']} rec {s['recall']} base {s['base_rate_exp_essential']} -> "
              f"{'PASS' if s['gate_pass'] else 'FAIL'}")
    print("VERDICT:", verdict)
    print("payload sha256:", sha, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
