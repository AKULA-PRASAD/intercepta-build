"""GENERALIZE5 — does FBA gene-essentiality generalize to a PARASITE (P. falciparum, malaria)?

Mirrors the bacterial CROSSVAL/BLIND1 method: COBRApy single-gene-deletion FBA on a CURATED GEM (iPfal19), essential
if KO growth < 1% WT; 2x2 Fisher enrichment vs EXPERIMENTAL essentiality (Zhang et al. 2018 Science piggyBac
saturation mutagenesis, PlasmoDB phenotype call); pre-registered gate OR>3 AND p<0.01. Deterministic; reproduced x2.
Env: metabolic (cobra 0.31; NO scipy -> math.comb hypergeometric Fisher fallback). See PREREG.md.
"""
import os, sys, csv, json, time, hashlib, logging
import cobra
from cobra.flux_analysis import single_gene_deletion
logging.getLogger("cobra").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
D = os.path.join(DATA, "generalize5")
MODEL = os.path.join(D, "iPfal19.xml")
ZHANG = os.path.join(D, "zhang2018_essentiality.csv")
ALIAS = os.path.join(D, "Pfalciparum3D7_GeneAliases.csv")

MIS_ESSENTIAL_THRESHOLD = 0.2  # sensitivity (secondary) definition, pre-registered


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fisher_greater(a, b, c, d):
    """One-sided Fisher (greater). scipy if available, else math.comb hypergeometric (metabolic env has no scipy)."""
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
    """any lowercased alias -> canonical PF3D7_ id."""
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
    """PF3D7 id (upper) -> dict(mis, mfs, phenotype)."""
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


def run():
    t0 = time.time()
    m = cobra.io.read_sbml_model(MODEL)
    # round to 6 decimals to remove GLPK degenerate-optimum jitter -> byte-identical reproduction
    wt = round(float(m.slim_optimize()), 6)
    thr = 0.01 * wt
    genes = list(m.genes)

    # FBA single-gene deletion
    sg = single_gene_deletion(m, genes, processes=1)
    sg["gid"] = sg["ids"].apply(lambda s: list(s)[0])
    gr = {r.gid: round(float(r.growth), 6) for r in sg.itertuples()}
    fba_ess = set(g.id for g in genes if gr.get(g.id, wt) < thr)

    # map model gene -> canonical PF3D7 id -> zhang
    aliases = load_aliases()
    zhang = load_zhang()

    def canon(gid):
        u = gid.strip().upper()
        if u in zhang:
            return u
        a = aliases.get(gid.strip().lower())
        if a and a.upper() in zhang:
            return a.upper()
        return None

    mapped = {}       # model gene id -> canonical PF3D7 id present in Zhang
    unmapped = []
    for g in genes:
        c = canon(g.id)
        if c:
            mapped[g.id] = c
        else:
            unmapped.append(g.id)

    def contingency(ess_pred, exp_ess_ids):
        a = b = c = d = 0
        for gid, cid in mapped.items():
            pe = gid in ess_pred
            ee = cid in exp_ess_ids
            if pe and ee: a += 1
            elif pe and not ee: b += 1
            elif not pe and ee: c += 1
            else: d += 1
        return a, b, c, d

    def score(exp_ess_ids, label):
        a, b, c, d = contingency(fba_ess, exp_ess_ids)
        orr, p = fisher_greater(a, b, c, d)
        prec = a / (a + b) if (a + b) else None
        rec = a / (a + c) if (a + c) else None
        # AUROC: score = -growth (lower growth -> more essential) vs experimental label over mapped genes
        y = [1 if cid in exp_ess_ids else 0 for gid, cid in mapped.items()]
        sc = [-gr.get(gid, wt) for gid in mapped]  # lower growth -> higher essentiality score
        auroc = None
        try:
            from sklearn.metrics import roc_auc_score
            auroc = float(roc_auc_score(y, sc)) if 0 < sum(y) < len(y) else None
        except Exception:
            # manual rank-based AUROC (Mann-Whitney U) with tie handling; metabolic env lacks sklearn
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
                "n_exp_essential_mapped": sum(1 for cid in mapped.values() if cid in exp_ess_ids),
                "contingency": {"both": a, "FBA_only": b, "exp_only": c, "neither": d},
                "odds_ratio": round(orr, 3),
                "fisher_p_greater": float(f"{p:.3e}"),
                "precision": round(prec, 3) if prec is not None else None,
                "recall": round(rec, 3) if rec is not None else None,
                "auroc": round(auroc, 4) if auroc is not None else None,
                "gate_pass": bool(orr > 3 and p < 0.01)}

    # PRIMARY: phenotype == "Non - Mutable in CDS"
    exp_primary = set(cid for cid in mapped.values()
                      if zhang[cid]["phenotype"] == "Non - Mutable in CDS")
    # SENSITIVITY: MIS <= threshold
    exp_mis = set(cid for cid in mapped.values()
                  if zhang[cid]["mis"] is not None and zhang[cid]["mis"] <= MIS_ESSENTIAL_THRESHOLD)

    primary = score(exp_primary, "phenotype:Non-Mutable-in-CDS")
    sensitivity = score(exp_mis, f"MIS<={MIS_ESSENTIAL_THRESHOLD}")

    payload = {
        "organism": "Plasmodium falciparum 3D7 (malaria)",
        "model": "iPfal19",
        "model_source": "PARADIGM database (Carey et al.; github.com/maureencarey/paradigm; bioRxiv 10.1101/772467); models/iPfal19.xml",
        "experimental_source": "Zhang et al. 2018 Science (piggyBac saturation mutagenesis), via PlasmoDB / Pf Target Browser Figshare 27190545",
        "wt_growth": round(float(wt), 4),
        "essential_threshold_frac_WT": 0.01,
        "n_model_genes": len(genes),
        "n_fba_essential": len(fba_ess),
        "n_genes_mapped_to_zhang": len(mapped),
        "n_genes_unmapped": len(unmapped),
        "unmapped_gene_ids": sorted(unmapped),
        "primary": primary,
        "sensitivity_MIS": sensitivity,
    }
    return payload, {"model_sha256": sha256_file(MODEL), "zhang_sha256": sha256_file(ZHANG)}


def main():
    t0 = time.time()
    payload, filehashes = run()
    p = payload["primary"]
    verdict = (
        f"FBA gene-essentiality (iPfal19, curated P. falciparum GEM) vs EXPERIMENTAL essentiality "
        f"(Zhang 2018 piggyBac saturation mutagenesis): over {payload['n_genes_mapped_to_zhang']} mapped metabolic "
        f"genes, OR {p['odds_ratio']} (Fisher one-sided p {p['fisher_p_greater']}), precision {p['precision']}, "
        f"recall {p['recall']}, AUROC {p['auroc']}. Pre-registered gate (OR>3 AND p<0.01): "
        f"{'PASS' if p['gate_pass'] else 'FAIL'}. "
        f"Contingency {p['contingency']}. SCOPE: essentiality-enrichment only; in-silico vs published screen; "
        f"curated model still a model; P. falciparum is host-dependent so the default-medium GEM may be "
        f"over-permissive (honest deployment risk)."
    )
    out = {"payload": payload, "verdict": verdict,
           "provenance": {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                          "git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
                          "cobra_version": cobra.__version__,
                          "file_hashes": filehashes,
                          "runtime_sec": round(time.time() - t0, 1)}}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "GENERALIZE5_metrics.json"), "w"),
              indent=2, sort_keys=True)
    payload_json = json.dumps(payload, sort_keys=True)
    sha = hashlib.sha256(payload_json.encode()).hexdigest()
    open(os.path.join(HERE, "results", "GENERALIZE5_payload.sha256"), "w").write(sha + "\n")
    print("VERDICT:", verdict)
    print("\nPRIMARY:", json.dumps(p, sort_keys=True))
    print("SENSITIVITY (MIS):", json.dumps(payload["sensitivity_MIS"], sort_keys=True))
    print("n_mapped", payload["n_genes_mapped_to_zhang"], "n_unmapped", payload["n_genes_unmapped"],
          "unmapped:", payload["unmapped_gene_ids"])
    print("payload sha256:", sha, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
