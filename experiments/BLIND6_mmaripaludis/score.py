"""BLIND6 Stage 2 (REVEAL + SCORE) — adjudicate the LOCKED FBA-essentiality predictions for the archaeon
Methanococcus maripaludis S2 against the pre-registered experimental essentiality (Sarmiento et al. 2013 PNAS,
via DEG accession DEG3001, Tn-seq, 519 essential genes). Predictions are NOT changed; the lock sha is verified first.

Adjudication: the pre-registered PRIMARY was a direct MMP#### locus-tag match against PNAS Dataset S4. That SI file is
paywalled behind a Cloudflare bot-challenge (not fetchable CPU-only), so we use the pre-registered FALLBACK: DEG3001, the
Database of Essential Genes entry for the IDENTICAL source (same PMID 23487778, same strain S2, same Tn-seq screen, 519
essential genes). DEG3001 carries NCBI GI numbers + symbols, NOT MMP locus tags, so we bridge by the pre-registered
namespace-independent method (identical to BLIND1/2/3): mmseqs easy-search of DEG3001's 519 essential PROTEIN sequences
against our organism's UniProt proteome relabeled by MMP locus tag, pident >= 90 (same-species ortholog cutoff, set once).
2x2 Fisher over the 539 GEM metabolic-subproteome genes; pre-registered gate OR>3 AND p<0.01.
"""
import os, json, hashlib, gzip
from scipy.stats import fisher_exact

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results")
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data"); B6 = os.path.join(DATA, "blind6")
LOCK_SHA = "e41877bfb22556c3032c69165c4254c3f0a90d9d05b707b1ac002f1ae7f5d111"
PIDENT = 90.0

def verify_lock():
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(RES, "LOCKED_predictions.tsv"))][1:]
    ess = sorted(r[0] for r in rows if r[3] == "1")
    sha = hashlib.sha256("\n".join(ess).encode()).hexdigest()
    assert sha == LOCK_SHA, f"LOCK BROKEN: {sha} != {LOCK_SHA}"
    return rows

def exp_essential_mmp():
    """MMP locus tags whose protein is hit by a DEG3001 essential protein at pident>=PIDENT."""
    s = set()
    for ln in open(os.path.join(B6, "deg_vs_gem.m8")):
        q, t, pid, *_ = ln.rstrip("\n").split("\t")
        if float(pid) >= PIDENT:
            s.add(t)
    return s

def main():
    rows = verify_lock()
    gem = {r[0]: int(r[3]) for r in rows}          # MMP -> FBA-essential 0/1
    exp = exp_essential_mmp()
    both = fba_only = exp_only = neither = 0
    for mmp, fba in gem.items():
        e = 1 if mmp in exp else 0
        if fba and e: both += 1
        elif fba and not e: fba_only += 1
        elif e and not fba: exp_only += 1
        else: neither += 1
    table = [[both, fba_only], [exp_only, neither]]
    orr, p = fisher_exact(table, alternative="greater")
    precision = both / (both + fba_only) if (both + fba_only) else 0.0
    recall = both / (both + exp_only) if (both + exp_only) else 0.0
    n_gem = len(gem)
    exp_in_gem = both + exp_only
    base_rate_fba = (both + fba_only) / n_gem
    verdict = "PASS" if (orr > 3 and p < 0.01) else "FAIL"

    # deterministic scored payload (EXCLUDES verdict/provenance) for byte-identical reproduction
    scored = {
        "n_gem_genes": n_gem,
        "contingency_both_fbaonly_exponly_neither": [both, fba_only, exp_only, neither],
        "odds_ratio": round(float(orr), 4),
        "fisher_p_greater": float(f"{p:.6e}"),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "n_exp_essential_in_gem": exp_in_gem,
        "n_fba_essential": both + fba_only,
        "fba_essential_base_rate": round(base_rate_fba, 4),
        "pident_cutoff": PIDENT,
        "gate": "OR>3 AND p<0.01",
    }
    payload = json.dumps(scored, sort_keys=True, separators=(",", ":"))
    reveal_sha = hashlib.sha256(payload.encode()).hexdigest()

    full = dict(scored)
    full["verdict"] = verdict
    full["reveal_payload_sha256"] = reveal_sha
    full["provenance"] = {
        "organism": "Methanococcus maripaludis S2 (taxon 267377, Archaea/Euryarchaeota)",
        "domain": "Archaea (third domain of life)",
        "lock_sha256_verified": LOCK_SHA,
        "gem": "curated iMR539 (Richards et al. 2016, BioModels BIOMD0000001099)",
        "experimental_source_prereg_primary": "Sarmiento, Mrazek & Whitman 2013 PNAS 110:4726-4731 (PMID 23487778), Dataset S4 (MMP locus tags) -- PAYWALLED/Cloudflare, not CPU-fetchable",
        "experimental_source_used": "DEG3001 (Database of Essential Genes; SAME Sarmiento 2013 source, strain S2, Tn-seq, 519 essential genes, genome NC_005791)",
        "adjudication": f"pre-registered sequence-homology bridge: mmseqs easy-search DEG3001 essential proteins -> UniProt proteome relabeled by MMP locus tag, pident>={PIDENT}",
        "deg30_aa_gz_sha256": "93b7fe2108265d2dcb059faa47f4dba0cf17af97cf53df56b6975b72e1fd10e6",
        "deg_annotation_a_csv_sha256": "89f53cb50040c61a600a2f6d41c184a540e5192ec901ee211ed7e7872b7716ab",
    }
    with open(os.path.join(RES, "BLIND6_reveal.json"), "w") as f:
        json.dump(full, f, indent=2, sort_keys=True); f.write("\n")
    open(os.path.join(RES, "BLIND6_reveal.sha256"), "w").write(reveal_sha + "\n")
    print(f"VERDICT {verdict} | OR={orr:.4f} p={p:.3e} | precision={precision:.3f} recall={recall:.3f}")
    print(f"contingency both/fbaOnly/expOnly/neither = {both}/{fba_only}/{exp_only}/{neither} over {n_gem} GEM genes")
    print(f"exp-essential in GEM={exp_in_gem}, FBA-essential={both+fba_only} (base rate {base_rate_fba:.3f})")
    print(f"reveal_payload_sha256={reveal_sha}")

if __name__ == "__main__":
    main()
