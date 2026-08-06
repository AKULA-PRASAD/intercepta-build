"""GENERALIZE4 — does FBA gene-essentiality generalize from BACTERIA to a EUKARYOTE?

Mirrors experiments/CROSSVAL_curated/run.py exactly, on Saccharomyces cerevisiae (model eukaryote):
  GEM  = iMM904 (BiGG); gene IDs = systematic ORF names, .name = standard symbol.
  Truth = DEG2001 (Giaever 2002 genome-wide deletion collection essential ORFs).
  Bridge= SGD_features.tab (standard name + aliases -> systematic ORF name).

Single-gene FBA deletion (essential if KO growth < 1% WT) -> 2x2 Fisher over the model's metabolic genes.
PRE-REGISTERED GATE (see PREREG.md): odds ratio > 3 AND Fisher p < 0.01. Deterministic; reproduce x2.
Env: metabolic (cobra). No scipy -> env-independent hypergeometric Fisher 'greater'. NO git commit.
"""
import os, sys, csv, json, time, hashlib, logging
import cobra
from cobra.flux_analysis import single_gene_deletion
logging.getLogger("cobra").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
G = os.path.join(DATA, "generalize4")
MODEL = os.path.join(G, "iMM904.xml")
DEG_E = os.path.join(G, "deg_euk", "deg_annotation_e.csv")
SGD = os.path.join(G, "SGD_features.tab")
DEG_ACC = "DEG2001"  # S. cerevisiae, Giaever 2002


def build_name2sys():
    """Map upper-cased standard name / alias / systematic name -> systematic ORF name, from SGD_features.tab ORFs."""
    m = {}
    with open(SGD, encoding="utf-8", errors="ignore") as fh:
        for row in csv.reader(fh, delimiter="\t"):
            if len(row) < 6 or row[1] != "ORF":
                continue
            sysname = row[3].strip()
            if not sysname:
                continue
            keys = {sysname}
            if row[4].strip():
                keys.add(row[4].strip())
            for a in row[5].split("|"):
                if a.strip():
                    keys.add(a.strip())
            for k in keys:
                m[k.upper()] = sysname.upper()
    return m


def deg_essential_standard():
    """Standard gene names of DEG2001 (S. cerevisiae) essential ORFs."""
    s = set()
    with open(DEG_E, encoding="utf-8", errors="ignore") as fh:
        for row in csv.reader(fh, delimiter=";"):
            if len(row) >= 3 and row[0].strip() == DEG_ACC:
                g = row[2].strip()
                if g and g != "-":
                    s.add(g)
    return s


def fisher_greater(a, b, c, d):
    try:
        from scipy.stats import fisher_exact
        return fisher_exact([[a, b], [c, d]], alternative="greater")
    except Exception:
        from math import comb
        n = a + b + c + d; r = a + b; col = a + c
        p = sum(comb(col, k) * comb(n - col, r - k) for k in range(a, min(r, col) + 1)) / comb(n, r)
        return (a * d) / max(b * c, 1), p


def main():
    t0 = time.time()
    name2sys = build_name2sys()
    deg_std = deg_essential_standard()
    # essential genes in systematic space
    essential_sys = set()
    n_deg_resolved = 0
    for g in deg_std:
        s = name2sys.get(g.upper())
        if s:
            essential_sys.add(s); n_deg_resolved += 1
    print(f"  SGD name2sys keys: {len(name2sys)} | DEG2001 essential standard names: {len(deg_std)} "
          f"| resolved to systematic: {n_deg_resolved} ({len(essential_sys)} unique sys)", flush=True)

    m = cobra.io.read_sbml_model(MODEL)
    wt = m.slim_optimize(); thr = 0.01 * wt
    print(f"  iMM904: {len(m.genes)} genes, {len(m.reactions)} rxns, WT growth {wt:.6f}, threshold {thr:.6f}", flush=True)
    sg = single_gene_deletion(m, m.genes, processes=1)
    sg["gid"] = sg["ids"].apply(lambda s: list(s)[0])
    # round to 6 dp to absorb GLPK degenerate-LP alternate-optima jitter -> byte-identical reproduction
    gr = {r.gid: round((r.growth if r.growth == r.growth else 0.0), 6) for r in sg.itertuples()}
    ess = set(g for g, v in gr.items() if v < thr)

    genes = list(m.genes)

    def is_exp(g):
        gid = g.id.upper()
        if gid in essential_sys:
            return True
        # backstop: resolve the model's own id/name through SGD then test
        s = name2sys.get(gid) or (name2sys.get(g.name.upper()) if g.name else None)
        return bool(s and s in essential_sys)

    expset = set(g.id for g in genes if is_exp(g))
    a = sum(1 for g in genes if g.id in ess and g.id in expset)
    b = sum(1 for g in genes if g.id in ess and g.id not in expset)
    c = sum(1 for g in genes if g.id not in ess and g.id in expset)
    d = sum(1 for g in genes if g.id not in ess and g.id not in expset)
    orr, pval = fisher_greater(a, b, c, d)
    y = [1 if g.id in expset else 0 for g in genes]
    sc = [-gr.get(g.id, wt) for g in genes]  # higher score = more essential (lower KO growth)
    try:
        from sklearn.metrics import roc_auc_score
        auroc = float(roc_auc_score(y, sc)) if 0 < sum(y) < len(y) else float("nan")
    except Exception:
        # tie-aware Mann-Whitney AUROC (rank-based), env-independent
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
        "organism": "Saccharomyces cerevisiae (model eukaryote)",
        "model": "iMM904",
        "deg_accession": DEG_ACC,
        "n_genes": len(genes),
        "n_fba_essential": len(ess),
        "n_deg_essential_total": len(deg_std),
        "n_deg_resolved_to_systematic": n_deg_resolved,
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
          f"AUROC {payload['auroc']} | FBA-ess {len(ess)} exp-mapped {len(expset)} | "
          f"contingency {payload['contingency']} -> {'PASS' if payload['gate_pass'] else 'FAIL'} [{time.time()-t0:.0f}s]",
          flush=True)

    verdict = (
        f"GENERALIZATION TEST (bacteria -> eukaryote): on S. cerevisiae (iMM904 GEM vs Giaever-2002 DEG2001 essential set), "
        f"FBA single-gene-deletion essentiality is {'ENRICHED' if payload['gate_pass'] else 'NOT sufficiently enriched'} "
        f"for experimental essentiality among the model's metabolic genes: OR {payload['odds_ratio']} "
        f"(Fisher one-sided p {payload['fisher_p']}), precision {payload['precision']}, recall {payload['recall']}, "
        f"AUROC {payload['auroc']}. Contingency {payload['contingency']}. "
        f"Gate (OR>3 AND p<0.01): {'PASS' if payload['gate_pass'] else 'FAIL'}. "
        f"SCOPE: essentiality-enrichment only; in-silico FBA vs a published deletion set (not wet-lab); curated model is still "
        f"a model; recall bounded by metabolic subproteome; MODEL EUKARYOTE (S. cerevisiae), not a direct C. albicans claim — "
        f"but the essential metabolic machinery is shared with fungal pathogens.")
    print("\nVERDICT:", verdict, flush=True)

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model_md5": hashlib.md5(open(MODEL, "rb").read()).hexdigest()}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump({"payload": payload, "verdict": verdict, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)},
              open(os.path.join(HERE, "results", "GENERALIZE4_metrics.json"), "w"), indent=2, sort_keys=True)
    ser = json.dumps(payload, sort_keys=True)
    sha = hashlib.sha256(ser.encode()).hexdigest()
    open(os.path.join(HERE, "results", "GENERALIZE4_payload.sha256"), "w").write(sha + "\n")
    print("payload sha256:", sha, f"[{time.time()-t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
