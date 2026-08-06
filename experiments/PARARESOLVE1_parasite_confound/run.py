"""PARARESOLVE1 — isolate the GEM axis of the parasite FBA-essentiality confound.

CONTROLLED SWAP: hold organism (P. falciparum), screen (Zhang 2018 piggyBac), gate (OR>3 & p<0.01), and
ID-map FIXED; vary ONLY the genome-scale reconstruction. PRIMARY = >=1 genuinely INDEPENDENT Pf GEM
(different team from iPfal19): Chiappino-Pepe 2017 (EPFL) + Abdel-Haleem 2018 iAM-Pf480 (UCSD). SAME-LINEAGE
sensitivity (PARADIGM): iPfal17 precursor, gf_Pfalciparum3D7, gf_no_ortho_Pfalciparum3D7. Plus mechanistic
salvage-bypass test on iPfal19 (FAIL) vs iTgo2020 (PASS).

Method IDENTICAL to GENERALIZE5/HARDENP1: COBRApy single_gene_deletion, KO growth rounded 6dp, essential if
KO<1% WT; 2x2 Fisher enrichment; estimator FROZEN to sample OR (a*d)/(b*c) + math.comb one-sided
hypergeometric (scipy deliberately unused, for byte-comparability with iPfal19 OR 2.469). See PREREG.md.
Env: metabolic (cobra 0.31.1, GLPK). Deterministic; reproduced x2.
"""
import os, csv, json, time, hashlib, logging, warnings
import cobra
from cobra.flux_analysis import single_gene_deletion
logging.getLogger("cobra").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
G = os.path.join(DATA, "generalize5")
P = os.path.join(DATA, "pararesolve1")
HP = os.path.join(DATA, "hardenp1")

ZHANG = os.path.join(G, "zhang2018_essentiality.csv")
ALIAS = os.path.join(G, "Pfalciparum3D7_GeneAliases.csv")
IPFAL19_OR = 2.469     # GENERALIZE5 anchor (FAIL)
TOXO_OR = 14.10        # HARDENP1 anchor (PASS)

# (label, path, kind, loader) — kind in {"reference","independent","same_lineage"}
PF_MODELS = [
    ("iPfal19", os.path.join(G, "iPfal19.xml"), "reference",
     "PARADIGM (Carey/Untaroiu/Papin, U.Virginia); anchor to reproduce GENERALIZE5"),
    ("Chiappino-Pepe_2017", os.path.join(P, "ipfa2017_chiappino_pepe.xml"), "independent",
     "Chiappino-Pepe et al. 2017 PLoS Comput Biol 13(4):e1005397 (Hatzimanikatis lab, EPFL)"),
    ("AbdelHaleem_2018_iAM-Pf480", os.path.join(P, "pfal2018_abdel_haleem.xml"), "independent",
     "Abdel-Haleem et al. 2018 Cell Reports 24(9):2337, iAM-Pf480 (Palsson lab, UCSD)"),
    ("iPfal17_precursor", os.path.join(P, "iPfal17.xml"), "same_lineage",
     "PARADIGM precursor to iPfal19 (SBML model id 'plata_orig_xml')"),
    ("gf_Pfalciparum3D7", os.path.join(G, "gf_Pfalciparum3D7.xml"), "same_lineage",
     "PARADIGM gap-filled variant"),
    ("gf_no_ortho_Pfalciparum3D7", os.path.join(G, "gf_no_ortho_Pfalciparum3D7.xml"), "same_lineage",
     "PARADIGM gap-filled (no-ortholog) variant"),
]


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fisher_greater_sampleOR(a, b, c, d):
    """One-sided Fisher (greater) via math.comb hypergeometric; SAMPLE OR (a*d)/(b*c).
    FROZEN to GENERALIZE5/HARDENP1 (scipy deliberately not used)."""
    from math import comb
    n = a + b + c + d
    r = a + b
    col = a + c
    p = sum(comb(col, k) * comb(n - col, r - k) for k in range(a, min(r, col) + 1)) / comb(n, r)
    orr = (a * d) / max(b * c, 1)
    return float(orr), float(p)


def load_aliases():
    amap = {}
    for row in csv.reader(open(ALIAS, encoding="utf-8", errors="ignore")):
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
        if gid:
            z[gid] = row["Zhang Phenotype"].strip()
    return z


ALIASES = load_aliases()
ZHANG_PH = load_zhang()


def canon_pf(gid):
    """model gene id -> canonical PF3D7 id present in Zhang (strip .N-pN suffix; alias fallback)."""
    base = gid.split(".")[0].strip()
    for cand in (base.upper(), gid.strip().upper()):
        if cand in ZHANG_PH:
            return cand
    for key in (base.lower(), gid.strip().lower()):
        a = ALIASES.get(key)
        if a and a.upper() in ZHANG_PH:
            return a.upper()
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


def score_pf(label, path, kind, source):
    m = cobra.io.read_sbml_model(path)
    genes = list(m.genes)
    wt, gr, fba_ess = fba_essential_set(m)

    mapped = {}
    for g in genes:
        c = canon_pf(g.id)
        if c:
            mapped[g.id] = c
    exp_ess = set(cid for cid in mapped.values() if ZHANG_PH.get(cid) == "Non - Mutable in CDS")

    a = b = c = d = 0
    for gid, cid in mapped.items():
        pe = gid in fba_ess
        ee = cid in exp_ess
        if pe and ee: a += 1
        elif pe and not ee: b += 1
        elif not pe and ee: c += 1
        else: d += 1
    orr, p = fisher_greater_sampleOR(a, b, c, d)
    y = [1 if cid in exp_ess else 0 for gid, cid in mapped.items()]
    sc = [-gr.get(gid, wt) for gid in mapped]
    auroc = rank_auroc(y, sc)
    return {
        "label": label, "kind": kind, "source": source,
        "model_sha256": sha256_file(path),
        "wt_growth": round(float(wt), 4),
        "n_model_genes": len(genes),
        "n_fba_essential": len(fba_ess),
        "n_genes_mapped_to_zhang": len(mapped),
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


# ---------------- Mechanistic salvage-bypass test ----------------
def importable_bases(m):
    """base species ids that can be IMPORTED (boundary rxn, lower_bound<0) under default medium."""
    bases = set()
    for r in m.reactions:
        if r.boundary and r.lower_bound < 0:
            for met in r.metabolites:
                bases.add(base_species(met))
    return bases


def base_species(met):
    """metabolite id minus compartment suffix; fallback to rsplit on '_'."""
    mid = met.id
    comp = getattr(met, "compartment", None)
    if comp and mid.endswith("_" + comp):
        return mid[: -(len(comp) + 1)]
    if "_" in mid:
        return mid.rsplit("_", 1)[0]
    return mid


def salvage_test(m, fba_ess, mapped, exp_ess):
    """For each FN (exp-essential & FBA-dispensable, mapped): categorize the bypass.
    GPR_redundant (no reaction disabled by g alone) / salvage_import (blocked-rxn metabolite importable) /
    internal_reroute (blocked but not importable)."""
    imp = importable_bases(m)
    gene_by_id = {g.id: g for g in m.genes}
    cats = {"GPR_redundant": 0, "salvage_import": 0, "internal_reroute": 0}
    fn_ids = []
    for gid, cid in mapped.items():
        if (cid in exp_ess) and (gid not in fba_ess):
            fn_ids.append(gid)
    for gid in fn_ids:
        g = gene_by_id[gid]
        blocked = [r for r in g.reactions if r.gpr.eval({gid}) is False]
        if not blocked:
            cats["GPR_redundant"] += 1
            continue
        mets = set()
        for r in blocked:
            for met in r.metabolites:
                mets.add(base_species(met))
        if mets & imp:
            cats["salvage_import"] += 1
        else:
            cats["internal_reroute"] += 1
    n_fn = len(fn_ids)
    n_nonempty = cats["salvage_import"] + cats["internal_reroute"]
    return {
        "n_false_negatives": n_fn,
        "categories": cats,
        "salvage_explained_frac_of_nonredundant": round(cats["salvage_import"] / n_nonempty, 3) if n_nonempty else None,
        "salvage_explained_frac_of_all_FN": round(cats["salvage_import"] / n_fn, 3) if n_fn else None,
        "n_importable_species": len(imp),
    }


def salvage_ipfal19():
    m = cobra.io.read_sbml_model(os.path.join(G, "iPfal19.xml"))
    _, _, fba_ess = fba_essential_set(m)
    mapped = {g.id: canon_pf(g.id) for g in m.genes if canon_pf(g.id)}
    exp_ess = set(cid for cid in mapped.values() if ZHANG_PH.get(cid) == "Non - Mutable in CDS")
    r = salvage_test(m, fba_ess, mapped, exp_ess)
    r["model"] = "iPfal19"; r["screen"] = "Zhang2018_piggyBac"
    return r


def salvage_itgo2020():
    import re
    MODEL = os.path.join(HP, "iTgo2020_krishnan.mat")
    SIDIK = os.path.join(HP, "sidik2016_phenotype.csv")
    m = cobra.io.load_matlab_model(MODEL)
    _, _, fba_ess = fba_essential_set(m)
    sidik = {}
    for row in csv.DictReader(open(SIDIK, encoding="utf-8", errors="ignore")):
        mm = re.match(r"TGGT1_(\d+)", row["gene_id_TGGT1"].strip())
        v = row["mean_phenotype"].strip()
        if mm and v != "":
            try:
                sidik[mm.group(1)] = float(v)
            except ValueError:
                pass
    mapped = {}
    for g in m.genes:
        mm = re.match(r"TGME49_(\d+)", g.id.strip())
        if mm and mm.group(1) in sidik:
            mapped[g.id] = mm.group(1)
    exp_ess = set(k for k in mapped.values() if sidik[k] < -2.0)
    r = salvage_test(m, fba_ess, mapped, exp_ess)
    r["model"] = "iTgo2020"; r["screen"] = "Sidik2016_CRISPR"
    return r


def run():
    swap = [score_pf(lbl, path, kind, src) for (lbl, path, kind, src) in PF_MODELS]
    independent = [s for s in swap if s["kind"] == "independent"]
    any_indep_pass = any(s["gate_pass"] for s in independent)
    all_indep_fail = all(not s["gate_pass"] for s in independent)

    salv_pf = salvage_ipfal19()
    salv_tg = salvage_itgo2020()

    payload = {
        "experiment": "PARARESOLVE1",
        "question": "Is the P. falciparum FBA-essentiality FAILURE iPfal19-GEM-specific, or robust across "
                    "independent Pf GEMs? (isolate the GEM axis of the GENERALIZE5-vs-HARDENP1 confound)",
        "design": "controlled swap: organism (P. falciparum), screen (Zhang 2018 piggyBac), gate (OR>3 & "
                  "p<0.01), ID-map FIXED; vary ONLY the genome-scale reconstruction",
        "experimental_source": "Zhang et al. 2018 Science piggyBac saturation mutagenesis; essential = "
                               "phenotype 'Non - Mutable in CDS'",
        "estimator": "sample OR (a*d)/(b*c) + one-sided hypergeometric via math.comb (FROZEN to GENERALIZE5)",
        "anchors": {"iPfal19_GENERALIZE5_OR": IPFAL19_OR, "iTgo2020_HARDENP1_OR": TOXO_OR},
        "swap_results": swap,
        "independent_gems_any_pass": any_indep_pass,
        "independent_gems_all_fail": all_indep_fail,
        "salvage_bypass_test": {
            "definition": "FN=exp-essential & FBA-dispensable; per FN gene: GPR_redundant (no rxn disabled by "
                          "g alone) / salvage_import (a blocked-rxn metabolite is importable, lower_bound<0) / "
                          "internal_reroute (blocked but no import). salvage_explained_frac over non-redundant FN.",
            "iPfal19_FAIL": salv_pf,
            "iTgo2020_PASS": salv_tg,
        },
        "residual_confounds_unresolved": [
            "screen technology (Zhang piggyBac vs Sidik CRISPR): NOT controllable here — no genome-wide "
            "Plasmodium CRISPR essentiality screen was obtainable CPU-only; the P. falciparum CRISPR-KO "
            "literature is gene-by-gene, not genome-scale saturating. This axis remains a standing limitation.",
            "organism biology (Plasmodium vs Toxoplasma): the swap controls it WITHIN Plasmodium but the "
            "Plasmodium-vs-Toxoplasma comparison still crosses organisms.",
            "base rate differs by organism (Pf ~0.64 vs Tg ~0.42) — reported per model, not eliminated.",
            "knowledgebase non-independence: all Pf GEMs share upstream biochemistry (KEGG/PlasmoDB) and "
            "earlier reconstructions (Plata 2010); 'independent' = independent team/reconstruction only.",
        ],
    }
    return payload


def interpret(payload):
    ind = [s for s in payload["swap_results"] if s["kind"] == "independent"]
    parts = []
    for s in ind:
        parts.append(f"{s['label']} OR {s['odds_ratio']} p {s['fisher_p_greater']} "
                     f"(rec {s['recall']}, prec {s['precision']}, base {s['base_rate_exp_essential']}) "
                     f"-> {'PASS' if s['gate_pass'] else 'FAIL'}")
    if payload["independent_gems_all_fail"]:
        axis = ("The malaria FBA failure is ROBUST across independent Pf reconstructions (all independent GEMs "
                "FAIL the same OR>3 bar on the same Zhang screen). => the 'just a bad iPfal19 GEM' attribution "
                "is WEAKENED: the failure is NOT specific to iPfal19's curation. Evidence shifts toward "
                "Plasmodium biology / screen-technology / base-rate rather than GEM idiosyncrasy.")
    elif payload["independent_gems_any_pass"]:
        axis = ("At least one INDEPENDENT Pf GEM PASSES (OR>3) on the same Zhang screen => the failure was "
                "iPfal19-GEM-SPECIFIC, not Plasmodium biology. Confound resolves TOWARD the GEM axis.")
    else:
        axis = "No independent GEM evaluable."
    sp = payload["salvage_bypass_test"]["iPfal19_FAIL"]
    st = payload["salvage_bypass_test"]["iTgo2020_PASS"]
    salv = (f"Salvage-explained FN fraction (of non-redundant FN): iPfal19 {sp['salvage_explained_frac_of_nonredundant']} "
            f"(FN={sp['n_false_negatives']}, cats={sp['categories']}) vs iTgo2020 "
            f"{st['salvage_explained_frac_of_nonredundant']} (FN={st['n_false_negatives']}, cats={st['categories']}).")
    return " | ".join(parts) + " || " + axis + " || " + salv


def main():
    t0 = time.time()
    payload = run()
    verdict = interpret(payload)
    out = {"payload": payload, "verdict": verdict,
           "provenance": {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                          "git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
                          "cobra_version": cobra.__version__,
                          "zhang_sha256": sha256_file(ZHANG),
                          "runtime_sec": round(time.time() - t0, 1)}}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "PARARESOLVE1_metrics.json"), "w"),
              indent=2, sort_keys=True)
    payload_json = json.dumps(payload, sort_keys=True)
    sha = hashlib.sha256(payload_json.encode()).hexdigest()
    open(os.path.join(HERE, "results", "PARARESOLVE1_payload.sha256"), "w").write(sha + "\n")
    print("=== SWAP (Zhang 2018, gate OR>3 & p<0.01) ===")
    for s in payload["swap_results"]:
        print(f"  [{s['kind']:11s}] {s['label']:28s} OR {s['odds_ratio']:6.3f} p {s['fisher_p_greater']:9} "
              f"prec {s['precision']} rec {s['recall']} base {s['base_rate_exp_essential']} "
              f"n_map {s['n_genes_mapped_to_zhang']} cont {s['contingency']} -> "
              f"{'PASS' if s['gate_pass'] else 'FAIL'}")
    print("=== SALVAGE ===")
    print("  iPfal19:", json.dumps(payload["salvage_bypass_test"]["iPfal19_FAIL"], sort_keys=True))
    print("  iTgo2020:", json.dumps(payload["salvage_bypass_test"]["iTgo2020_PASS"], sort_keys=True))
    print("VERDICT:", verdict)
    print("payload sha256:", sha, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
