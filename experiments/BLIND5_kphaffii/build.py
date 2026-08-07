"""BLIND5 Stage 1 (LOCK) — freeze the FBA-essentiality predictions for the EUKARYOTE Komagataella phaffii GS115
(= Pichia pastoris) from the CURATED genome-scale model iMT1026 v3 ALONE. NO experimental essentiality is read
here (blindness). Output: results/LOCKED_predictions.tsv (+ .sha256). Env: metabolic (cobra 0.31 + GLPK).

Protocol identical in spirit to BLIND1/BLIND2/BLIND3 (same 1%-of-WT essentiality rule, same signed-zero-collapsed
canonical tsv, same 'hash the sorted essential-key set' lock convention). The ONLY difference vs BLIND1-3 is that
this is a CURATED model (not a de-novo CarveMe carve), so the gene identifiers are the model's native GS115
systematic locus tags (PAS_chrX_XXXX / PAS_cNNN_XXXX / a few standard-name genes). The lock payload is therefore
the sorted set of FBA-ESSENTIAL locus tags (fully determined by the metabolic network + FBA, provably independent
of which genes are experimentally essential). The UniProt accession (mapped from the GS115 reference proteome by
gene name) is carried as a convenience column for the Stage-2 sequence/symbol adjudication, but is NOT the hashed key.
"""
import os, hashlib, logging, cobra
from cobra.flux_analysis import single_gene_deletion
logging.getLogger("cobra").setLevel(logging.ERROR)
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)
GEM = os.path.join(DATA, "blind5", "kphaffii_iMT1026v3.xml"); FASTA = os.path.join(DATA, "blind5", "kphaffii.fasta")


def main():
    # gene-name (GS115 locus tag / standard name) -> UniProt accession, from the GS115 reference proteome
    gn2acc = {}
    for ln in open(FASTA):
        if not ln.startswith(">"): continue
        acc = ln[1:].split()[0].split("|")[1] if "|" in ln else ln[1:].split()[0]
        for tok in ln.split():
            if tok.startswith("GN="): gn2acc[tok[3:]] = acc
    # Solver: EXACT-rational simplex (glpk_exact) WITH PRESOLVE ON.
    #  * glpk_exact gives the mathematically EXACT LP optimum -> the authoritative, solver-independent essentiality call
    #    (float GLPK gives numerically DIFFERENT borderline calls near the 1%-WT threshold; exact is ground truth).
    #  * The default GLPK float simplex CYCLES indefinitely on a degenerate KO LP (gene PAS_chr3_0036 / rxn AMETtm,
    #    S-adenosyl-methionine mito transport); glpk_exact WARMSTARTS with that same float simplex, so it too can hang.
    #    Enabling GLPK presolve removes the degeneracy that triggers the cycle -> every KO LP terminates reliably.
    #  * processes=1 + exact arithmetic -> fully deterministic; reproduced x2 byte-identical (see PREREG).
    # Run in 50-gene batches (robust; a single monolithic all-genes call is avoided) with a progress log to stderr.
    import sys, time as _t; _t0 = _t.time()
    m = cobra.io.read_sbml_model(GEM); m.solver = "glpk_exact"; m.solver.configuration.presolve = True
    wt = m.slim_optimize(); thr = 0.01 * wt
    genes = list(m.genes); growth = {}
    for i in range(0, len(genes), 50):
        sg = single_gene_deletion(m, genes[i:i + 50], processes=1)
        for r in sg.itertuples():
            growth[list(r.ids)[0]] = float(r.growth)
        print(f"  chunk {i}-{i+len(genes[i:i+50])} cum {round(_t.time()-_t0,1)}s", file=sys.stderr, flush=True)
    rows = []
    for locus, gr_raw in growth.items():
        acc = gn2acc.get(locus, ""); ess = 1 if gr_raw < thr else 0
        # round KO growth to 6dp to absorb GLPK alternate-optima jitter, then normalize to WT ratio at 4dp;
        # collapse signed-zero (-0.0) to 0.0 so the tsv artifact is fully canonical/deterministic (BLIND3 convention)
        gr = round(round(gr_raw, 6) / wt, 4); gr = 0.0 if gr == 0 else gr
        rows.append((locus, acc, ess, gr))
    rows.sort()
    with open(os.path.join(RES, "LOCKED_predictions.tsv"), "w") as f:
        f.write("locus_tag\tuniprot\tfba_essential\tgrowth_ratio\n")
        for l, a, e, g in rows: f.write(f"{l}\t{a}\t{e}\t{g}\n")
    ess_keys = sorted(l for l, a, e, g in rows if e == 1)      # HASHED KEY = essential GS115 locus tags
    payload = "\n".join(ess_keys)
    sha = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(RES, "LOCKED_predictions.sha256"), "w").write(sha + "\n")
    print(f"LOCKED: {len(m.genes)} GEM genes, WT {wt:.6f}, {len(ess_keys)} FBA-ESSENTIAL predicted (frozen). "
          f"mapped-to-UniProt {sum(1 for l,a,e,g in rows if a)}/{len(rows)}. "
          f"sha256(essential-locus-set)={sha}  NO experimental data consulted.")


if __name__ == "__main__":
    main()
