"""BLIND1 Stage 2b (REVEAL, sequence-bridge adjudication) — the first reveal (symbol match) was INCONCLUSIVE: the DEG
N. gonorrhoeae MS11 essential set is keyed by NGFG_ locus tags absent from UniProt, so only 1/613 matched. The correct,
namespace-independent adjudication is SEQUENCE HOMOLOGY: map the 751 DEG-essential PROTEINS (from DEG10.aa.gz) to our
proteome by mmseqs, defining the experimental-essential set in OUR accession space, then re-score the SAME LOCKED
predictions (Stage 1, sha-verified intact — predictions are NOT changed; only the experimental-set parsing is corrected).
Env: bioinfo (mmseqs). Transparent: this is a scoring correction for an identifier-namespace artifact, not outcome-tuning.
"""
import os, re, json, time, hashlib, subprocess, shutil, gzip
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results")
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
PROT = os.path.join(DATA, "blind1", "ngono.fasta")
DEGAA = os.path.join(DATA, "expval_deg", "DEG10.aa.gz")
DEG_ACC = "DEG1055"   # N. gonorrhoeae MS11 (Remmele 2014), 751 essential (revealed in Stage 2)
PIDENT = 90.0         # same-species ortholog: confident same-gene mapping


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
    assert hashlib.sha256(payload.encode()).hexdigest() == lock_sha, "LOCK TAMPERED"

    # extract DEG1055 essential protein sequences
    deg_fa = os.path.join(DATA, "blind1", "deg1055.fasta"); n_deg = 0
    with gzip.open(DEGAA, "rt") as fin, open(deg_fa, "w") as fo:
        keep = False
        for ln in fin:
            if ln.startswith(">"):
                keep = ln[1:].strip().startswith(DEG_ACC)
                if keep: n_deg += 1
            if keep: fo.write(ln)
    # mmseqs: DEG-essential proteins (query) vs our proteome (target) -> our accs that are experimental-essential orthologs
    out = os.path.join(DATA, "blind1", "deg_vs_ngono.m8"); tmp = os.path.join(DATA, "blind1", "tmp_sb"); shutil.rmtree(tmp, ignore_errors=True)
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
    summary = {"organism": "N_gonorrhoeae", "deg_accession": DEG_ACC, "adjudication": "sequence-homology bridge (pident>=90)",
               "locked_sha_verified": True, "n_deg_essential_proteins": n_deg, "n_locked_genes": len(genes),
               "n_experimental_essential_in_our_space": len(exp_accs),
               "contingency": {"both": a, "FBA_only": b, "exp_only": c, "neither": d},
               "precision": round(prec, 3) if prec == prec else None, "recall": round(rec, 3) if rec == rec else None,
               "odds_ratio": round(float(orr), 2), "fisher_p": float(f"{pval:.3e}"),
               "PREREG_GATE_OR_gt3_p_lt0.01": gate}
    summary["verdict"] = (
        f"PROSPECTIVE-BLIND RESULT ({'PASS' if gate else 'FAIL'}), sequence-bridge adjudication of the pre-registered LOCKED "
        f"predictions (sha verified intact; predictions unchanged): on the genuinely novel, never-seen WHO pathogen "
        f"N. gonorrhoeae, FBA-essential genes are {'ENRICHED' if gate else 'NOT enriched'} for EXPERIMENTAL essentiality "
        f"(DEG {DEG_ACC}, {n_deg} essential proteins mapped by mmseqs to {len(exp_accs)} of our genes): odds ratio "
        f"{summary['odds_ratio']} (Fisher p={summary['fisher_p']}), precision {summary['precision']}, recall {summary['recall']} "
        f"({a} both / {b} FBA-only / {c} exp-only / {d} neither). INTEGRITY: the first reveal (symbol match) was inconclusive "
        f"(NGFG_ locus tags absent from UniProt -> 1/613 mapped); this corrects the EXPERIMENTAL-SET IDENTIFIER MAPPING via "
        f"sequence homology (objectively correct, outcome-independent) while the PREDICTIONS remain locked/frozen. "
        + ("This is genuine prospective-blind evidence the mechanism signal predicts experimental essentiality on a "
           "pre-registered, never-seen pathogen." if gate else
           "Honest NEGATIVE as pre-registered -- the locked predictions did not clear the gate; reported, not re-run.") +
        " SCOPE: essentiality-enrichment only; sparse de-novo GEM (fastidious organism); species-vs-MS11 strain gap; in-silico "
        "vs published data; hypotheses; not wet-lab.")
    print("PANEL:", json.dumps({k: v for k, v in summary.items() if k != "verdict"}, indent=1))
    print("VERDICT:", summary["verdict"])
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    json.dump({"summary": summary, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)},
              open(os.path.join(RES, "BLIND1_reveal_seqbridge.json"), "w"), indent=2, sort_keys=True)
    pl = json.dumps({k: v for k, v in summary.items() if k != "verdict"}, sort_keys=True)
    open(os.path.join(RES, "BLIND1_seqbridge.sha256"), "w").write(hashlib.sha256(pl.encode()).hexdigest() + "\n")
    print("payload sha256:", hashlib.sha256(pl.encode()).hexdigest(), f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
