"""BLIND5 Stage 2 (REVEAL + SCORE) — Komagataella phaffii GS115 (EUKARYOTE), FIRST eukaryote in the blind suite.
The EXPERIMENTAL essential set DEG2027 (Zhu et al. 2018 Sci Rep, PMID 29976927; genome-wide Tn-seq; GS115; 753 essential
genes) is consulted HERE for the first time. The Stage-1 predictions were locked and git-committed BEFORE this reveal
(commit 1067834). This script (a) re-verifies the lock is byte-intact, then (b) scores the LOCKED predictions.

Adjudication = DIRECT GS115 systematic-locus-tag match. Both sides use the identical GS115 `PAS_...` locus-tag
namespace (the GEM iMT1026 v3 gene IDs AND the DEG2027 annotation's `locus_tag:` field), an EXACT same-strain match,
so no sequence-homology bridge is needed (the mmseqs bridge in BLIND1-3 existed only to defeat namespace mismatch,
which does not occur here). Fisher one-sided 'greater' via env-independent math.comb hypergeometric (OR = a*d/(b*c),
matching BLIND1-3 / HARDENF1). Deterministic; reproduce x2 byte-identical (sha over sorted-key JSON, excl verdict/prov).
Gate (pre-registered, identical to BLIND1-4): odds ratio > 3 AND p < 0.01. NO git commit.
"""
import os, csv, json, math, hashlib

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results")
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
LOCK_TSV = os.path.join(RES, "LOCKED_predictions.tsv")
LOCK_SHA = os.path.join(RES, "LOCKED_predictions.sha256")
DEG_ANN = os.path.join(DATA, "blind5", "deg_ann", "deg_annotation_e.csv")   # DEG eukaryote annotation (semicolon CSV)
DEG_AA = os.path.join(DATA, "blind5", "DEG20.aa.gz")                        # DEG eukaryote protein seqs (753 for DEG2027)
DEG_ACC = "DEG2027"
COMMITTED_LOCK_SHA = "8d0822054d41ae86174305982106a355b800208f83048a445309be2de8dfe521"


def fisher_greater(a, b, c, d):
    """One-sided (greater) Fisher exact p on 2x2 [[a,b],[c,d]] via exact hypergeometric tail; env-independent."""
    n = a + b + c + d; row1 = a + b; col1 = a + c
    kmin = max(0, col1 - (n - row1)); kmax = min(row1, col1)
    def logC(nn, kk): return math.lgamma(nn + 1) - math.lgamma(kk + 1) - math.lgamma(nn - kk + 1)
    logdenom = logC(n, col1)
    p = 0.0
    for k in range(a, kmax + 1):
        lp = logC(row1, k) + logC(n - row1, col1 - k) - logdenom
        p += math.exp(lp)
    return min(1.0, p)


def main():
    # ---- (a) LOCK INTEGRITY: recompute payload sha from the tsv; MUST equal the committed lock. Abort otherwise. ----
    rows = []
    with open(LOCK_TSV) as f:
        rd = csv.reader(f, delimiter="\t"); header = next(rd)
        for r in rd: rows.append(r)                                  # locus_tag, uniprot, fba_essential, growth_ratio
    fba_ess = sorted(r[0] for r in rows if r[2] == "1")
    payload_sha = hashlib.sha256("\n".join(fba_ess).encode()).hexdigest()
    file_sha = open(LOCK_SHA).read().strip()
    assert payload_sha == file_sha == COMMITTED_LOCK_SHA, \
        f"LOCK TAMPERED: payload {payload_sha} vs file {file_sha} vs committed {COMMITTED_LOCK_SHA}"
    gem_loci = [r[0] for r in rows]                                  # the 1026 GEM-gene universe (GS115 locus tags)
    gem_set = set(gem_loci); fba_set = set(fba_ess)
    assert len(gem_loci) == len(gem_set) == 1026 and len(fba_set) == 147

    # ---- REVEAL: parse DEG2027 experimental essential genes -> GS115 locus tags (namespace = our locus_tag column) ----
    exp_loci = set(); deg2027_rows = 0; no_locus = 0
    with open(DEG_ANN, encoding="utf-8", errors="replace") as f:
        for fld in csv.reader(f, delimiter=";", quotechar='"'):
            if not fld or fld[0] != DEG_ACC: continue
            deg2027_rows += 1
            lt = next((x.split("locus_tag:", 1)[1].strip() for x in fld if x.strip().startswith("locus_tag:")), None)
            if lt: exp_loci.add(lt)
            else: no_locus += 1
    # experimental-essential genes that fall inside our GEM universe (the scoreable overlap)
    exp_in_gem = exp_loci & gem_set

    # ---- 2x2 over the 1026 GEM genes ----
    a = len(fba_set & exp_in_gem)                 # both: FBA-essential AND experimentally-essential
    b = len(fba_set - exp_in_gem)                 # FBA-only
    c = len(exp_in_gem - fba_set)                 # exp-only
    d = len(gem_set) - a - b - c                  # neither
    OR = (a * d) / (b * c) if b * c else float("inf")
    p = fisher_greater(a, b, c, d)
    precision = a / (a + b) if (a + b) else 0.0
    recall = a / (a + c) if (a + c) else 0.0
    verdict = "PASS" if (OR > 3 and p < 0.01) else "FAIL"

    payload = {                                    # hashed reproducibility payload (excludes verdict/provenance)
        "deg_accession": DEG_ACC, "gem_universe": len(gem_set), "fba_essential": len(fba_set),
        "deg2027_rows": deg2027_rows, "deg2027_loci": len(exp_loci), "deg2027_no_locus": no_locus,
        "exp_essential_in_gem": len(exp_in_gem),
        "contingency": {"both": a, "fba_only": b, "exp_only": c, "neither": d},
        "odds_ratio": round(OR, 6), "fisher_p_greater": f"{p:.6e}",
        "precision": round(precision, 6), "recall": round(recall, 6),
        "gate": "OR>3 AND p<0.01",
    }
    reveal_sha = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    out = dict(payload)
    out.update({
        "VERDICT": verdict, "reveal_payload_sha256": reveal_sha,
        "lock_intact": True, "locked_sha_verified": COMMITTED_LOCK_SHA,
        "adjudication": "direct GS115 systematic locus-tag match (exact same-strain namespace; no homology bridge needed)",
        "experimental_source": ("DEG2027 — Zhu et al. 2018 Sci Rep (PMID 29976927), genome-wide Tn-seq, "
                                "K. phaffii GS115, 753 essential; DEG20.aa.gz + deg_annotation_e.csv"),
        "deg_aa_sha256": hashlib.sha256(open(DEG_AA, "rb").read()).hexdigest(),
        "deg_ann_sha256": hashlib.sha256(open(DEG_ANN, "rb").read()).hexdigest(),
    })
    with open(os.path.join(RES, "BLIND5_reveal.json"), "w") as f:
        json.dump(out, f, indent=2, sort_keys=True); f.write("\n")
    open(os.path.join(RES, "BLIND5_reveal.sha256"), "w").write(reveal_sha + "\n")
    print(f"LOCK INTACT sha={COMMITTED_LOCK_SHA[:16]}...  DEG2027 rows={deg2027_rows} loci={len(exp_loci)} "
          f"(no_locus={no_locus}), in-GEM={len(exp_in_gem)}")
    print(f"2x2 [both {a} / fba_only {b} / exp_only {c} / neither {d}]  OR={OR:.4f}  p={p:.4e}  "
          f"prec={precision:.4f}  rec={recall:.4f}  -> {verdict}")
    print(f"reveal_payload_sha256={reveal_sha}")


if __name__ == "__main__":
    main()
