"""BLIND4 Stage 1 (LOCK) — produce and freeze the FBA-essentiality predictions for S. pneumoniae TIGR4 from the de-novo
CarveMe GEM ALONE. NO experimental essentiality is read here (blindness). Output: results/LOCKED_predictions.tsv (+ .sha256).
Env: metabolic (cobra + GLPK). Identical protocol to BLIND1/BLIND2/build.py (gid->accession parsing adapts to CarveMe gene ids).
"""
import os, hashlib, logging, cobra
from cobra.flux_analysis import single_gene_deletion
logging.getLogger("cobra").setLevel(logging.ERROR)
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)
GEM = os.path.join(DATA, "blind4", "spneumo.xml"); FASTA = os.path.join(DATA, "blind4", "spneumo.fasta")


def gid2acc(g):
    """CarveMe gene id like 'G_sp_Q97QS2_...' / 'sp_A0A0H2UNG0_PULA_STRPN' -> UniProt accession (2nd token)."""
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
        # round KO growth to 6dp for solver-jitter reproducibility, then normalize to WT ratio at 4dp (as BLIND2).
        # +0.0 collapses IEEE signed-zero (-0.0 -> 0.0) so the full TSV is byte-identical run-to-run (essential-set sha
        # is already invariant to this; the payload is accessions only).
        rows.append((acc, acc2sym.get(acc, ""), ess, round(round(float(r.growth), 6) / wt, 4) + 0.0))
    rows.sort()
    with open(os.path.join(RES, "LOCKED_predictions.tsv"), "w") as f:
        f.write("uniprot\tsymbol\tfba_essential\tgrowth_ratio\n")
        for a, s, e, g in rows: f.write(f"{a}\t{s}\t{e}\t{g}\n")
    ess_accs = sorted(a for a, s, e, g in rows if e == 1)
    payload = "\n".join(ess_accs)
    open(os.path.join(RES, "LOCKED_predictions.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    print(f"LOCKED: {len(m.genes)} GEM genes, WT {wt:.3f}, {len(ess_accs)} FBA-ESSENTIAL predicted (frozen). "
          f"sha256(essential-set)={hashlib.sha256(payload.encode()).hexdigest()} NO experimental data consulted.")


if __name__ == "__main__":
    main()
