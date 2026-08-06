"""HARDENP1 — does FBA gene-essentiality ALSO FAIL on a SECOND host-dependent parasite (Toxoplasma gondii)?

Mirrors GENERALIZE5 exactly: COBRApy single-gene-deletion FBA on a CURATED T. gondii GEM (iTgo2020, Krishnan 2020),
essential if KO growth < 1% WT; 2x2 Fisher enrichment vs the genome-wide CRISPR fitness screen (Sidik et al. 2016
Cell, mean phenotype score < -2 = fitness-conferring/essential); pre-registered gate OR>3 AND p<0.01.
Deterministic; reproduced x2. See PREREG.md.

ID map: GEM TGME49_NNNNNN <-> screen TGGT1_NNNNNN by shared ToxoDB numeric locus suffix.
OR/p estimator frozen to GENERALIZE5's: sample OR (a*d)/(b*c) + one-sided hypergeometric via math.comb (NOT scipy),
for apples-to-apples comparison with Plasmodium's OR 2.469.
Env: metabolic (cobra 0.31; scipy present but deliberately unused for OR/p — see PREREG).
"""
import os, sys, csv, json, time, hashlib, logging, re
import cobra
from cobra.flux_analysis import single_gene_deletion
logging.getLogger("cobra").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
D = os.path.join(DATA, "hardenp1")
MODEL = os.path.join(D, "iTgo2020_krishnan.mat")
SIDIK = os.path.join(D, "sidik2016_phenotype.csv")

PRIMARY_CUTOFF = -2.0        # Sidik mean phenotype < -2 = essential (field standard; validated on Sidik controls)
SENS_STRICT = -3.0
SENS_LOOSE = -1.5
PLASMODIUM_OR = 2.469        # GENERALIZE5 anchor for comparison


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fisher_greater_sampleOR(a, b, c, d):
    """One-sided Fisher (greater) via math.comb hypergeometric; SAMPLE odds ratio (a*d)/(b*c).
    Frozen to match GENERALIZE5 exactly (scipy deliberately not used). See PREREG."""
    from math import comb
    n = a + b + c + d
    r = a + b
    col = a + c
    p = sum(comb(col, k) * comb(n - col, r - k) for k in range(a, min(r, col) + 1)) / comb(n, r)
    orr = (a * d) / max(b * c, 1)
    return float(orr), float(p)


def load_sidik():
    """TGGT1 numeric suffix -> mean phenotype score (float)."""
    s = {}
    for row in csv.DictReader(open(SIDIK, encoding="utf-8", errors="ignore")):
        m = re.match(r"TGGT1_(\d+)", row["gene_id_TGGT1"].strip())
        v = row["mean_phenotype"].strip()
        if not m or v == "":
            continue
        try:
            s[m.group(1)] = float(v)
        except ValueError:
            pass
    return s


def run():
    m = cobra.io.load_matlab_model(MODEL)
    wt = round(float(m.slim_optimize()), 6)
    thr = 0.01 * wt
    genes = list(m.genes)

    sg = single_gene_deletion(m, genes, processes=1)
    sg["gid"] = sg["ids"].apply(lambda s: list(s)[0])
    gr = {r.gid: round(float(r.growth), 6) for r in sg.itertuples()}
    fba_ess = set(g.id for g in genes if gr.get(g.id, wt) < thr)

    sidik = load_sidik()

    def numeric(gid):
        mm = re.match(r"TGME49_(\d+)", gid.strip())
        return mm.group(1) if mm else None

    mapped = {}          # model gene id -> sidik numeric key (scored)
    unmapped = []
    for g in genes:
        num = numeric(g.id)
        if num is not None and num in sidik:
            mapped[g.id] = num
        else:
            unmapped.append(g.id)

    def contingency(ess_pred, exp_ess_ids):
        a = b = c = d = 0
        for gid, key in mapped.items():
            pe = gid in ess_pred
            ee = key in exp_ess_ids
            if pe and ee:
                a += 1
            elif pe and not ee:
                b += 1
            elif not pe and ee:
                c += 1
            else:
                d += 1
        return a, b, c, d

    def score(exp_ess_ids, label):
        a, b, c, d = contingency(fba_ess, exp_ess_ids)
        orr, p = fisher_greater_sampleOR(a, b, c, d)
        prec = a / (a + b) if (a + b) else None
        rec = a / (a + c) if (a + c) else None
        y = [1 if key in exp_ess_ids else 0 for gid, key in mapped.items()]
        sc = [-gr.get(gid, wt) for gid in mapped]   # lower growth -> higher essentiality score
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
                "n_exp_essential_mapped": sum(1 for key in mapped.values() if key in exp_ess_ids),
                "contingency": {"both": a, "FBA_only": b, "exp_only": c, "neither": d},
                "odds_ratio": round(orr, 3),
                "fisher_p_greater": float(f"{p:.3e}"),
                "precision": round(prec, 3) if prec is not None else None,
                "recall": round(rec, 3) if rec is not None else None,
                "auroc": round(auroc, 4) if auroc is not None else None,
                "gate_pass": bool(orr > 3 and p < 0.01)}

    exp_primary = set(k for k in mapped.values() if sidik[k] < PRIMARY_CUTOFF)
    exp_strict = set(k for k in mapped.values() if sidik[k] < SENS_STRICT)
    exp_loose = set(k for k in mapped.values() if sidik[k] < SENS_LOOSE)

    primary = score(exp_primary, f"Sidik_mean_phenotype<{PRIMARY_CUTOFF}")
    sens_strict = score(exp_strict, f"Sidik_mean_phenotype<{SENS_STRICT}")
    sens_loose = score(exp_loose, f"Sidik_mean_phenotype<{SENS_LOOSE}")

    payload = {
        "organism": "Toxoplasma gondii (ME49 model gene IDs; screen in type I RH/GT1)",
        "model": "iTgo2020 (Krishnan et al. 2020)",
        "model_source": "Krishnan et al. 2020 Cell Host & Microbe 27:290 (DOI 10.1016/j.chom.2020.01.002); "
                        "via PARADIGM github.com/maureencarey/paradigm models/published/iTgo2020_krishnan.mat",
        "experimental_source": "Sidik et al. 2016 Cell 167:1423 (DOI 10.1016/j.cell.2016.08.019) genome-wide CRISPR "
                               "fitness screen; mean phenotype score, Suppl. mmc3.xlsx sheet 'Phenotype'; "
                               "open Elsevier CDN 1-s2.0-S0092867416310704-mmc3.xlsx",
        "essential_definition_experimental": f"Sidik mean phenotype score < {PRIMARY_CUTOFF} "
                                              "(field-standard cutoff; validated on Sidik's own controls: "
                                              "40/40 dispensable score>=-2, 36/40 essential score<-2)",
        "id_mapping": "GEM TGME49_NNNNNN <-> screen TGGT1_NNNNNN by shared ToxoDB numeric locus suffix",
        "wt_growth": round(float(wt), 4),
        "essential_threshold_frac_WT": 0.01,
        "n_model_genes": len(genes),
        "n_fba_essential": len(fba_ess),
        "n_genes_mapped_to_sidik": len(mapped),
        "n_genes_unmapped": len(unmapped),
        "unmapped_gene_ids": sorted(unmapped),
        "primary": primary,
        "sensitivity_strict_minus3": sens_strict,
        "sensitivity_loose_minus1p5": sens_loose,
        "comparison_plasmodium_OR": PLASMODIUM_OR,
    }
    return payload, {"model_sha256": sha256_file(MODEL), "sidik_sha256": sha256_file(SIDIK)}


def main():
    t0 = time.time()
    payload, filehashes = run()
    p = payload["primary"]
    cmp_txt = ("HARDENS the boundary to n=2 host-dependent parasites (both FAIL OR>3)"
               if not p["gate_pass"] else
               "COMPLICATES the parasite conclusion (this parasite PASSES where Plasmodium failed)")
    verdict = (
        f"FBA gene-essentiality (iTgo2020, curated T. gondii GEM) vs EXPERIMENTAL essentiality "
        f"(Sidik 2016 genome-wide CRISPR screen, mean phenotype < {PRIMARY_CUTOFF}): over "
        f"{payload['n_genes_mapped_to_sidik']} mapped metabolic genes, OR {p['odds_ratio']} "
        f"(one-sided hypergeometric p {p['fisher_p_greater']}), precision {p['precision']}, recall {p['recall']}, "
        f"AUROC {p['auroc']}. Pre-registered gate (OR>3 AND p<0.01): {'PASS' if p['gate_pass'] else 'FAIL'}. "
        f"Contingency {p['contingency']}. vs Plasmodium OR {payload['comparison_plasmodium_OR']} (GENERALIZE5, FAIL): "
        f"{cmp_txt}. SCOPE: essentiality-enrichment only; in-silico vs published screen; curated model still a model; "
        f"T. gondii is host-embedded so the default-medium GEM may be over-permissive (honest deployment risk)."
    )
    out = {"payload": payload, "verdict": verdict,
           "provenance": {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                          "git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
                          "cobra_version": cobra.__version__,
                          "file_hashes": filehashes,
                          "runtime_sec": round(time.time() - t0, 1)}}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "HARDENP1_metrics.json"), "w"),
              indent=2, sort_keys=True)
    payload_json = json.dumps(payload, sort_keys=True)
    sha = hashlib.sha256(payload_json.encode()).hexdigest()
    open(os.path.join(HERE, "results", "HARDENP1_payload.sha256"), "w").write(sha + "\n")
    print("VERDICT:", verdict)
    print("\nPRIMARY:", json.dumps(p, sort_keys=True))
    print("SENS strict(-3):", json.dumps(payload["sensitivity_strict_minus3"], sort_keys=True))
    print("SENS loose(-1.5):", json.dumps(payload["sensitivity_loose_minus1p5"], sort_keys=True))
    print("n_mapped", payload["n_genes_mapped_to_sidik"], "n_unmapped", payload["n_genes_unmapped"],
          "unmapped:", payload["unmapped_gene_ids"])
    print("payload sha256:", sha, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
