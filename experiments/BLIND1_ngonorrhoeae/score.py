"""BLIND1 Stage 2 (REVEAL) — score the LOCKED N. gonorrhoeae FBA-essentiality predictions (Stage 1, committed 986f0ce)
against the EXPERIMENTAL essential set (DEG N. gonorrhoeae), now consulted for the FIRST time. Pre-registered gate: OR>3,
p<0.01. Reports pass or fail honestly. Env: metabolic (or any with cobra not needed here — pure parsing + Fisher)."""
import os, re, csv, json, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results")
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
DEG_BAC = os.path.join(DATA, "expval_deg", "deg_bacteria.csv"); DEG_ANN = os.path.join(DATA, "expval_deg", "deg_annotation_p.csv")


def deg_accession():
    """DEG accession(s) for N. gonorrhoeae (revealed now)."""
    accs = []
    for ln in open(DEG_BAC, encoding="utf-8", errors="ignore"):
        if "gonorrhoeae" in ln.lower():
            m = re.findall(r"DEG\d{4}", ln)
            if m: accs.append((m[-1], ln))
    return accs


def deg_essential_ids(acc):
    s = set()
    for row in csv.reader(open(DEG_ANN, encoding="utf-8", errors="ignore"), delimiter=";"):
        if len(row) >= 11 and row[0].strip() == acc:
            g = row[2].strip()
            if g and g != "-": s.add(g.lower())
            lt = row[10].strip()
            if lt.startswith("locus_tag:"): s.add(lt.split(":", 1)[1].strip().lower())
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
    # locked predictions
    locked = []
    for ln in open(os.path.join(RES, "LOCKED_predictions.tsv")).read().splitlines()[1:]:
        p = ln.split("\t")
        if len(p) >= 3: locked.append({"acc": p[0], "sym": p[1].lower(), "fba": int(p[2])})
    lock_sha = open(os.path.join(RES, "LOCKED_predictions.sha256")).read().strip()
    # verify the lock is intact (predictions unchanged since Stage 1)
    payload = "\n".join(sorted(x["acc"] for x in locked if x["fba"] == 1))
    assert hashlib.sha256(payload.encode()).hexdigest() == lock_sha, "LOCK TAMPERED — predictions changed since Stage 1!"

    # REVEAL: experimental essential set
    accs = deg_accession()
    # prefer MS11; else the accession with the most essential ids
    chosen, exp = None, set()
    for acc, line in accs:
        e = deg_essential_ids(acc)
        if "ms11" in line.lower() and len(e) >= 50:
            chosen, exp = acc, e; break
        if len(e) > len(exp): chosen, exp = acc, e

    # adjudicable = locked genes that HAVE a symbol (matchable); exp-essential if symbol OR acc in DEG set
    adj = [x for x in locked if x["sym"]]
    exp_hit = set(x["acc"] for x in adj if x["sym"] in exp or x["acc"].lower() in exp)
    a = sum(1 for x in adj if x["fba"] == 1 and x["acc"] in exp_hit)
    b = sum(1 for x in adj if x["fba"] == 1 and x["acc"] not in exp_hit)
    c = sum(1 for x in adj if x["fba"] == 0 and x["acc"] in exp_hit)
    d = sum(1 for x in adj if x["fba"] == 0 and x["acc"] not in exp_hit)
    orr, pval = fisher_greater(a, b, c, d)
    prec = a / (a + b) if (a + b) else float("nan"); rec = a / (a + c) if (a + c) else float("nan")
    gate = bool(orr > 3 and (pval < 0.01 if pval == pval else False))
    summary = {"organism": "N_gonorrhoeae", "deg_accession": chosen, "locked_sha_verified": True,
               "n_locked_genes": len(locked), "n_adjudicable": len(adj), "n_experimental_essential_mapped": len(exp_hit),
               "contingency": {"both": a, "FBA_only": b, "exp_only": c, "neither": d},
               "precision": round(prec, 3) if prec == prec else None, "recall": round(rec, 3) if rec == rec else None,
               "odds_ratio": round(float(orr), 2), "fisher_p": (float(f"{pval:.3e}") if pval == pval else None),
               "PREREG_GATE_OR_gt3_p_lt0.01": gate}
    summary["verdict"] = (
        f"PROSPECTIVE-BLIND RESULT ({'PASS' if gate else 'FAIL'}): the pre-registered, LOCKED FBA-essentiality predictions for "
        f"the genuinely novel WHO pathogen N. gonorrhoeae (committed before any experimental data; lock sha verified intact) are "
        f"{'ENRICHED' if gate else 'NOT sufficiently enriched'} for EXPERIMENTAL essentiality (DEG {chosen}): odds ratio "
        f"{summary['odds_ratio']} (Fisher p={summary['fisher_p']}), precision {summary['precision']}, recall {summary['recall']} "
        f"over {len(adj)} adjudicable genes ({a} both / {b} FBA-only / {c} exp-only / {d} neither). "
        + ("This is prospective-blind evidence that the mechanism signal predicts experimental essentiality on a pre-registered, "
           "never-seen pathogen — the strongest such evidence obtainable without a wet lab."
           if gate else
           "Honest NEGATIVE, reported as pre-registered: the locked predictions did not clear the gate on this fastidious "
           "organism's sparse de-novo GEM — a real deployment limitation, not re-run to a better number.") +
        " SCOPE: essentiality-enrichment only; species-level proteome vs MS11 experimental set; de-novo GEM; in-silico vs "
        "published data; hypotheses; not wet-lab.")
    print("PANEL:", json.dumps({k: v for k, v in summary.items() if k != "verdict"}, indent=1))
    print("VERDICT:", summary["verdict"])
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    json.dump({"summary": summary, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)},
              open(os.path.join(RES, "BLIND1_reveal.json"), "w"), indent=2, sort_keys=True)
    pl = json.dumps({k: v for k, v in summary.items() if k != "verdict"}, sort_keys=True)
    open(os.path.join(RES, "BLIND1_reveal.sha256"), "w").write(hashlib.sha256(pl.encode()).hexdigest() + "\n")
    print("payload sha256:", hashlib.sha256(pl.encode()).hexdigest(), f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
