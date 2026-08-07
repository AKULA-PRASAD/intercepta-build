"""BLIND2 Stage 2 (REVEAL) — score the LOCKED C. jejuni NCTC 11168 FBA-essentiality predictions (Stage 1) against the
EXPERIMENTAL essential set DEG1049 (Mandal, Jiang & Kwon 2017, Tn-seq, NCTC 11168), consulted here for the FIRST time.
Adjudication = sequence-homology bridge (mmseqs, pident>=90) — the identical, namespace-independent method that adjudicated
BLIND1 (pre-registered in PREREG.md). The PREDICTIONS stay locked/sha-verified unchanged; only the experimental-set is
mapped now. Pre-registered gate: OR>3 AND p<0.01 (identical to BLIND1). Reports PASS/FAIL honestly. Env: bioinfo (mmseqs).
Deterministic; Fisher via math.comb (one-sided, greater) for comparability with BLIND1/CROSSVAL. Reproduce x2 byte-identical.
"""
import os, json, time, hashlib, subprocess, shutil, gzip
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results")
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
PROT = os.path.join(DATA, "blind2", "cjejuni.fasta")
DEGAA = os.path.join(DATA, "expval_deg", "DEG10.aa.gz")
DEG_ACC = "DEG1049"   # C. jejuni NCTC 11168 (Mandal 2017), Tn-seq essential set (pre-registered)
PIDENT = 90.0         # same-species ortholog: confident same-gene mapping (set once, not swept)


def fisher_greater(a, b, c, d):
    from math import comb
    n = a + b + c + d; r = a + b; col = a + c
    p = sum(comb(col, k) * comb(n - col, r - k) for k in range(a, min(r, col) + 1)) / comb(n, r)
    return (a * d) / max(b * c, 1), p


def main():
    t0 = time.time()
    # locked predictions (verify integrity)
    locked = []
    for ln in open(os.path.join(RES, "LOCKED_predictions.tsv")).read().splitlines()[1:]:
        p = ln.split("\t")
        if len(p) >= 3: locked.append({"acc": p[0], "fba": int(p[2])})
    lock_sha = open(os.path.join(RES, "LOCKED_predictions.sha256")).read().strip()
    payload = "\n".join(sorted(x["acc"] for x in locked if x["fba"] == 1))
    assert hashlib.sha256(payload.encode()).hexdigest() == lock_sha, "LOCK TAMPERED — predictions changed since Stage 1!"

    # REVEAL: extract DEG1049 essential protein sequences
    deg_fa = os.path.join(DATA, "blind2", "deg1049.fasta"); n_deg = 0
    with gzip.open(DEGAA, "rt") as fin, open(deg_fa, "w") as fo:
        keep = False
        for ln in fin:
            if ln.startswith(">"):
                keep = ln[1:].strip().startswith(DEG_ACC)
                if keep: n_deg += 1
            if keep: fo.write(ln)
    # mmseqs: DEG-essential proteins (query) vs our proteome (target) -> our accs that are experimental-essential orthologs
    out = os.path.join(DATA, "blind2", "deg_vs_cjejuni.m8"); tmp = os.path.join(DATA, "blind2", "tmp_sb")
    shutil.rmtree(tmp, ignore_errors=True)
    subprocess.run([MMSEQS, "easy-search", deg_fa, PROT, out, tmp, "--threads", "4", "-e", "1e-5",
                    "--format-output", "query,target,pident,bits", "-v", "1"], capture_output=True, text=True)
    exp_accs = set()
    if os.path.exists(out):
        for ln in open(out):
            p = ln.rstrip("\n").split("\t")
            if len(p) < 4: continue
            tgt = p[1].split("|")[1] if "|" in p[1] else p[1]
            if float(p[2]) >= PIDENT: exp_accs.add(tgt)
    shutil.rmtree(tmp, ignore_errors=True)

    genes = locked  # sequence bridge adjudicates ALL locked genes (no symbol requirement)
    a = sum(1 for x in genes if x["fba"] == 1 and x["acc"] in exp_accs)
    b = sum(1 for x in genes if x["fba"] == 1 and x["acc"] not in exp_accs)
    c = sum(1 for x in genes if x["fba"] == 0 and x["acc"] in exp_accs)
    d = sum(1 for x in genes if x["fba"] == 0 and x["acc"] not in exp_accs)
    orr, pval = fisher_greater(a, b, c, d)
    prec = a / (a + b) if (a + b) else float("nan"); rec = a / (a + c) if (a + c) else float("nan")
    gate = bool(orr > 3 and pval < 0.01)
    summary = {"organism": "C_jejuni_NCTC11168", "clade": "epsilon-proteobacteria", "deg_accession": DEG_ACC,
               "adjudication": "sequence-homology bridge (mmseqs pident>=90)", "locked_sha_verified": True,
               "n_deg_essential_proteins": n_deg, "n_locked_genes": len(genes),
               "n_experimental_essential_in_our_space": len(exp_accs),
               "contingency": {"both": a, "FBA_only": b, "exp_only": c, "neither": d},
               "precision": round(prec, 3) if prec == prec else None, "recall": round(rec, 3) if rec == rec else None,
               "odds_ratio": round(float(orr), 2), "fisher_p": float(f"{pval:.3e}"),
               "PREREG_GATE_OR_gt3_p_lt0.01": gate}
    summary["verdict"] = (
        f"PROSPECTIVE-BLIND RESULT ({'PASS' if gate else 'FAIL'}), sequence-bridge adjudication of the pre-registered LOCKED "
        f"predictions (sha {lock_sha[:16]}... verified intact; predictions unchanged): on the genuinely novel, never-seen WHO "
        f"priority pathogen C. jejuni NCTC 11168 (NEW clade: epsilon-proteobacteria), de-novo CarveMe FBA-essential genes are "
        f"{'ENRICHED' if gate else 'NOT enriched'} for EXPERIMENTAL essentiality (DEG {DEG_ACC}, Mandal 2017 Tn-seq, "
        f"{n_deg} essential proteins mapped by mmseqs to {len(exp_accs)} of our genes): odds ratio {summary['odds_ratio']} "
        f"(Fisher p={summary['fisher_p']}), precision {summary['precision']}, recall {summary['recall']} "
        f"({a} both / {b} FBA-only / {c} exp-only / {d} neither). "
        + ("This is a SECOND independent prospective-blind confirmation (n=2 with BLIND1) that the FBA-essentiality mechanism "
           "signal predicts experimental essentiality on a pre-registered, never-seen pathogen — now extended to a new "
           "phylogenetic clade." if gate else
           "Honest NEGATIVE as pre-registered — the locked predictions did not clear the gate on this microaerophilic "
           "organism's sparse de-novo GEM; reported, not re-run to a better number.") +
        " SCOPE: essentiality-enrichment only; sparse de-novo GEM; in-silico FBA vs published Tn-seq; hypotheses; not wet-lab.")
    print("PANEL:", json.dumps({k: v for k, v in summary.items() if k != "verdict"}, indent=1))
    print("VERDICT:", summary["verdict"])
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    json.dump({"summary": summary, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)},
              open(os.path.join(RES, "BLIND2_reveal.json"), "w"), indent=2, sort_keys=True)
    pl = json.dumps({k: v for k, v in summary.items() if k != "verdict"}, sort_keys=True)
    open(os.path.join(RES, "BLIND2_reveal.sha256"), "w").write(hashlib.sha256(pl.encode()).hexdigest() + "\n")
    print("payload sha256:", hashlib.sha256(pl.encode()).hexdigest(), f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
