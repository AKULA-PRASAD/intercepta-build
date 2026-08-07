"""BLIND6 Stage 1 (LOCK) — freeze the FBA-essentiality predictions for the ARCHAEON Methanococcus maripaludis S2
from the CURATED genome-scale model iMR539 (Richards et al. 2016, BioModels BIOMD0000001099) ALONE.
NO experimental essentiality is read here (blindness). Output: results/LOCKED_predictions.tsv (+ .sha256). Env: metabolic.

Protocol identical to BLIND1/BLIND2/BLIND3: COBRApy single-gene-deletion FBA, gene FBA-essential if KO growth < 1% WT,
signed-zero collapse + rounding for byte-identical determinism, payload = sorted essential-identifier set hashed to sha256.
Only difference vs BLIND1/3: the GEM is a CURATED archaeal reconstruction whose gene ids are MMP#### locus tags (NOT
CarveMe UniProt ids), which is ALSO the identifier namespace of the Stage-2 essentiality resource (Sarmiento 2013) --
so the primary/hashed identifier here is the MMP locus tag (UniProt accession + gene symbol are attached for readability).
"""
import os, hashlib, logging, cobra
from cobra.flux_analysis import single_gene_deletion
logging.getLogger("cobra").setLevel(logging.ERROR)
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)
GEM = os.path.join(DATA, "blind6", "mmp_iMR539.xml")
MAP = os.path.join(DATA, "blind6", "mmp_map.tsv")  # UniProt: accession \t gene_primary \t gene_oln(MMP locus tag)


def load_map():
    """MMP locus tag -> (uniprot_accession, gene_symbol) from the UniProt reference-proteome mapping."""
    oln2 = {}
    with open(MAP) as f:
        next(f)  # header
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 3:
                continue
            acc, sym, oln = p[0], p[1], p[2]
            for tag in oln.replace(";", " ").split():  # gene_oln may list >1 locus tag
                oln2[tag] = (acc, sym)
    return oln2


def main():
    oln2 = load_map()
    m = cobra.io.read_sbml_model(GEM)
    wt = m.slim_optimize(); thr = 0.01 * wt
    sg = single_gene_deletion(m, m.genes, processes=4)
    sg["gid"] = sg["ids"].apply(lambda s: list(s)[0])
    rows = []
    for r in sg.itertuples():
        gid = r.gid                       # curated-GEM gene id IS the MMP locus tag
        ess = 1 if r.growth < thr else 0
        # round KO growth to 6dp (GLPK jitter), normalize to WT ratio at 4dp, collapse signed-zero -> canonical tsv
        gr = round(round(float(r.growth), 6) / wt, 4); gr = 0.0 if gr == 0 else gr
        acc, sym = oln2.get(gid, ("", ""))
        rows.append((gid, sym, acc, ess, gr))
    rows.sort()
    with open(os.path.join(RES, "LOCKED_predictions.tsv"), "w") as f:
        f.write("mmp_locus\tsymbol\tuniprot\tfba_essential\tgrowth_ratio\n")
        for gid, sym, acc, e, gr in rows:
            f.write(f"{gid}\t{sym}\t{acc}\t{e}\t{gr}\n")
    ess_ids = sorted(gid for gid, sym, acc, e, gr in rows if e == 1)
    payload = "\n".join(ess_ids)
    sha = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(RES, "LOCKED_predictions.sha256"), "w").write(sha + "\n")
    print(f"LOCKED: {len(m.genes)} GEM genes, WT {wt:.4f}, {len(ess_ids)} FBA-ESSENTIAL predicted (frozen). "
          f"sha256(essential MMP-locus set)={sha} NO experimental data consulted.")


if __name__ == "__main__":
    main()
