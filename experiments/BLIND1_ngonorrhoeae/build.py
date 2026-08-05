"""BLIND1 Stage 1 (LOCK) — produce and freeze the FBA-essentiality predictions for N. gonorrhoeae from the de-novo GEM ALONE.
NO experimental essentiality is read here (blindness). Output: results/LOCKED_predictions.tsv (+ .sha256). Env: metabolic.
"""
import os, hashlib, logging, cobra
from cobra.flux_analysis import single_gene_deletion
logging.getLogger("cobra").setLevel(logging.ERROR)
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)
GEM = os.path.join(DATA, "blind1", "ngono.xml"); FASTA = os.path.join(DATA, "blind1", "ngono.fasta")


def gid2acc(g):
    p = g.split("_"); return p[1] if len(p) > 1 else g


def main():
    acc2sym = {}
    for ln in open(FASTA):
        if not ln.startswith(">"): continue
        acc = ln[1:].split()[0].split("|")[1] if "|" in ln else ln[1:].split()[0]
        for tok in ln.split():
            if tok.startswith("GN="): acc2sym[acc] = tok[3:]
    m = cobra.io.read_sbml_model(GEM); wt = m.slim_optimize(); thr = 0.01 * wt
    sg = single_gene_deletion(m, m.genes, processes=4); sg["gid"] = sg["ids"].apply(lambda s: list(s)[0])
    rows = []
    for r in sg.itertuples():
        acc = gid2acc(r.gid); ess = 1 if r.growth < thr else 0
        rows.append((acc, acc2sym.get(acc, ""), ess, round(float(r.growth), 4)))
    rows.sort()
    with open(os.path.join(RES, "LOCKED_predictions.tsv"), "w") as f:
        f.write("uniprot\tsymbol\tfba_essential\tgrowth_ratio\n")
        for a, s, e, g in rows: f.write(f"{a}\t{s}\t{e}\t{g}\n")
    ess_accs = sorted(a for a, s, e, g in rows if e == 1)
    payload = "\n".join(ess_accs)
    open(os.path.join(RES, "LOCKED_predictions.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    print(f"LOCKED: {len(m.genes)} GEM genes, WT {wt:.3f}, {len(ess_accs)} FBA-ESSENTIAL predicted (frozen). "
          f"sha256(essential-set)={hashlib.sha256(payload.encode()).hexdigest()[:16]}... NO experimental data consulted.")


if __name__ == "__main__":
    main()
