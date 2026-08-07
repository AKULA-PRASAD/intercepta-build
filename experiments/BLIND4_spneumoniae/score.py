"""BLIND4 Stage 2 (REVEAL) — score the LOCKED S. pneumoniae TIGR4 FBA-essentiality predictions (Stage 1) against the
EXPERIMENTAL essential set, consulted here for the FIRST time. Adjudication = sequence-homology bridge (mmseqs, pident>=90) —
the identical, namespace-independent method that adjudicated BLIND1/BLIND2 — plus an SP_ locus-tag cross-check.

EXPERIMENTAL SOURCE (per PREREG decision rule): the pre-registered PRIMARY gold-standard van Opijnen 2009 Tn-seq (TIGR4) is
NOT cleanly fetchable CPU-only in this environment (Nature article behind idp.nature.com auth wall; OGEE v3 unreachable /
legacy host blocked by safe-browse redirect; web-search budget exhausted). Per the pre-registered decision rule this invokes
the STRAIN-MATCHED FALLBACK: DEG accession DEG1007 (S. pneumoniae TIGR4, genome NC_003028 — the SAME strain/genome van
Opijnen assayed), protein sequences local in $INTERCEPTA_DATA/expval_deg/DEG10.aa.gz. HONEST CAVEAT: DEG1007 is
insertion-duplication + allelic-replacement mutagenesis (Thanassi 2002 / Song 2005), NOT Tn-seq, and is smaller/older than
the van Opijnen Tn-seq set — a weaker but strain-matched experimental truth.

PREDICTIONS stay locked/sha-verified unchanged; only the experimental set is mapped now. Pre-registered gate: OR>3 AND
p<0.01 (identical to BLIND1/BLIND2). Reports PASS/FAIL honestly. Env: bioinfo (mmseqs). Fisher via math.comb (one-sided,
greater) for comparability with BLIND1/BLIND2/CROSSVAL. Reproduce x2 byte-identical (payload sha excludes verdict/provenance).
"""
import os, json, time, hashlib, subprocess, shutil, gzip
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results")
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
PROT = os.path.join(DATA, "blind4", "spneumo.fasta")
DEGAA = os.path.join(DATA, "expval_deg", "DEG10.aa.gz")
DEGANN = os.path.join(DATA, "expval_deg", "deg_annotation_p.csv")
DEG_ACC = "DEG1007"   # S. pneumoniae TIGR4 (Thanassi 2002 / Song 2005), essential set, strain-matched fallback (pre-registered)
PIDENT = 90.0         # same-species/strain ortholog: confident same-gene mapping (set once, not swept)
LOCK_EXPECTED = "f86a02a4e7107ec2c12e3a231942449a01dc24f1be78fbbae42b6db1b8b5651d"  # committed Stage-1 lock (git b89fd42)


def fisher_greater(a, b, c, d):
    from math import comb
    n = a + b + c + d; r = a + b; col = a + c
    p = sum(comb(col, k) * comb(n - col, r - k) for k in range(a, min(r, col) + 1)) / comb(n, r)
    return (a * d) / max(b * c, 1), p


def main():
    t0 = time.time()
    # locked predictions (verify integrity FIRST — abort if tampered)
    locked = []
    for ln in open(os.path.join(RES, "LOCKED_predictions.tsv")).read().splitlines()[1:]:
        p = ln.split("\t")
        if len(p) >= 3: locked.append({"acc": p[0], "sym": p[1], "fba": int(p[2])})
    lock_sha = open(os.path.join(RES, "LOCKED_predictions.sha256")).read().strip()
    payload = "\n".join(sorted(x["acc"] for x in locked if x["fba"] == 1))
    assert hashlib.sha256(payload.encode()).hexdigest() == lock_sha, "LOCK TAMPERED — predictions changed since Stage 1!"
    assert lock_sha == LOCK_EXPECTED, f"LOCK MISMATCH vs committed {LOCK_EXPECTED} — ABORT"

    # REVEAL: extract DEG1007 essential protein sequences (first consultation of experimental membership)
    deg_fa = os.path.join(DATA, "blind4", "deg1007.fasta"); n_deg = 0
    with gzip.open(DEGAA, "rt") as fin, open(deg_fa, "w") as fo:
        keep = False
        for ln in fin:
            if ln.startswith(">"):
                keep = ln[1:].strip().startswith(DEG_ACC)
                if keep: n_deg += 1
            if keep: fo.write(ln)
    # mmseqs: DEG-essential proteins (query) vs our proteome (target) -> our accs that are experimental-essential orthologs
    out = os.path.join(DATA, "blind4", "deg_vs_spneumo.m8"); tmp = os.path.join(DATA, "blind4", "tmp_sb")
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

    genes = locked  # sequence bridge adjudicates ALL locked genes (metabolic subproteome; no symbol requirement)
    a = sum(1 for x in genes if x["fba"] == 1 and x["acc"] in exp_accs)
    b = sum(1 for x in genes if x["fba"] == 1 and x["acc"] not in exp_accs)
    c = sum(1 for x in genes if x["fba"] == 0 and x["acc"] in exp_accs)
    d = sum(1 for x in genes if x["fba"] == 0 and x["acc"] not in exp_accs)
    orr, pval = fisher_greater(a, b, c, d)
    prec = a / (a + b) if (a + b) else float("nan"); rec = a / (a + c) if (a + c) else float("nan")
    gate = bool(orr > 3 and pval < 0.01)

    # SP_ locus-tag cross-check (corroboration, namespace-native, partial coverage): DEG1007 SP_ tags vs our locked SP_ symbols
    deg_sp = set()
    for ln in open(DEGANN, encoding="latin-1"):
        f = [t.strip().strip('"') for t in ln.rstrip("\n").split('";"')]
        f = [t.strip('"') for t in f]
        if f and f[0] == DEG_ACC and len(f) > 2 and f[2].startswith("SP_"):
            deg_sp.add(f[2])
    locked_sp = {x["sym"] for x in genes if x["sym"].startswith("SP_")}
    ess_sp = {x["sym"] for x in genes if x["fba"] == 1 and x["sym"].startswith("SP_")}
    sp_cross = {"deg1007_SP_tags": len(deg_sp), "locked_genes_with_SP_symbol": len(locked_sp),
                "FBA_essential_with_SP_symbol": len(ess_sp),
                "FBA_essential_SP_in_DEG1007": sorted(ess_sp & deg_sp),
                "note": "partial coverage: only locked genes whose UniProt gene name IS the SP_ ordered-locus tag are "
                        "checkable this way; the mmseqs homology bridge is the complete pre-registered adjudication."}

    summary = {"organism": "S_pneumoniae_TIGR4", "clade": "Firmicutes (Bacilli, Gram-positive)",
               "experimental_source": DEG_ACC,
               "experimental_source_detail": "DEG1007 S. pneumoniae TIGR4 (NC_003028), insertion-duplication/allelic-"
                   "replacement (Thanassi 2002 / Song 2005); STRAIN-MATCHED FALLBACK invoked per PREREG decision rule "
                   "because van Opijnen 2009 Tn-seq (primary) was not cleanly fetchable CPU-only (Nature auth wall; OGEE "
                   "unreachable).",
               "adjudication": "sequence-homology bridge (mmseqs pident>=90)", "locked_sha_verified": True,
               "locked_sha": lock_sha,
               "n_deg_essential_proteins": n_deg, "n_locked_genes": len(genes),
               "n_experimental_essential_in_our_space": len(exp_accs),
               "contingency": {"both": a, "FBA_only": b, "exp_only": c, "neither": d},
               "precision": round(prec, 3) if prec == prec else None, "recall": round(rec, 3) if rec == rec else None,
               "odds_ratio": round(float(orr), 2), "fisher_p": float(f"{pval:.3e}"),
               "PREREG_GATE_OR_gt3_p_lt0.01": gate, "SP_locus_tag_cross_check": sp_cross}
    summary["verdict"] = (
        f"PROSPECTIVE-BLIND RESULT ({'PASS' if gate else 'FAIL'}), sequence-bridge adjudication of the pre-registered LOCKED "
        f"predictions (sha {lock_sha[:16]}... verified intact and equal to committed lock; predictions unchanged): on the "
        f"genuinely novel, never-seen WHO priority pathogen S. pneumoniae TIGR4 (NEW clade: Gram-positive Firmicute), de-novo "
        f"CarveMe FBA-essential genes are {'ENRICHED' if gate else 'NOT enriched'} for EXPERIMENTAL essentiality "
        f"({DEG_ACC}, {n_deg} essential proteins mapped by mmseqs to {len(exp_accs)} of our genes): odds ratio "
        f"{summary['odds_ratio']} (Fisher p={summary['fisher_p']}), precision {summary['precision']}, recall "
        f"{summary['recall']} ({a} both / {b} FBA-only / {c} exp-only / {d} neither). "
        + ("This is a THIRD independent prospective-blind confirmation (n=3 with BLIND1/BLIND2, now spanning three phyla incl. "
           "a Gram-positive Firmicute) that the FBA-essentiality mechanism signal predicts experimental essentiality on a "
           "pre-registered, never-seen pathogen." if gate else
           "Honest NEGATIVE as pre-registered — the locked predictions did not clear the gate; reported, not re-run to a "
           "better number.") +
        " HONEST CAVEAT: experimental truth is the strain-matched DEG1007 (allelic-replacement), NOT the pre-registered "
        "van Opijnen Tn-seq (unfetchable CPU-only here). SCOPE: essentiality-enrichment only; sparse de-novo GEM; in-silico "
        "FBA vs a published experimental set; hypotheses; not wet-lab.")
    print("PANEL:", json.dumps({k: v for k, v in summary.items() if k != "verdict"}, indent=1))
    print("VERDICT:", summary["verdict"])
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "deg_aa_sha256": hashlib.sha256(open(DEGAA, "rb").read()).hexdigest(),
            "experimental_source_decision": "van Opijnen 2009 Tn-seq (primary) UNFETCHABLE CPU-only -> DEG1007 fallback"}
    json.dump({"summary": summary, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)},
              open(os.path.join(RES, "BLIND4_reveal.json"), "w"), indent=2, sort_keys=True)
    pl = json.dumps({k: v for k, v in summary.items() if k != "verdict"}, sort_keys=True)
    open(os.path.join(RES, "BLIND4_reveal.sha256"), "w").write(hashlib.sha256(pl.encode()).hexdigest() + "\n")
    print("payload sha256:", hashlib.sha256(pl.encode()).hexdigest(), f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
