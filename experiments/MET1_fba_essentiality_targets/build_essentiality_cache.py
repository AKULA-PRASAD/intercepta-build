"""MET1 Step A — FBA gene-essentiality cache. For each organism's BiGG genome-scale metabolic model, run COBRApy
single-gene-deletion and record, per gene, its UniProt accession + essentiality (KO growth < 1% of WT). Deterministic
data artifact -> $INTERCEPTA_DATA/met1/essentiality.tsv. Env: `metabolic` (cobra). Run: metabolic python.
"""
import os, time, warnings; warnings.filterwarnings("ignore")
from cobra.io import load_model
from cobra.flux_analysis import single_gene_deletion

DATA = os.path.join(os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data"), "met1")
os.makedirs(DATA, exist_ok=True)
GEMS = {"ecoli": "iML1515", "saureus": "iYS854", "kpneumoniae": "iYL1228"}
TSV = os.path.join(DATA, "essentiality.tsv")


def main():
    t0 = time.time()
    with open(TSV, "w") as fh:
        fh.write("organism\tuniprot\tgene_id\tessential\tgrowth_ratio\n")
        for org, gid in GEMS.items():
            m = load_model(gid)
            wt = m.optimize().objective_value
            d = single_gene_deletion(m, processes=1)
            # map deletion index (frozenset of gene ids) -> gene
            gmap = {g.id: g for g in m.genes}
            n = 0
            for _, row in d.iterrows():
                ids = list(row["ids"]) if "ids" in row else list(row.name)
                if len(ids) != 1:
                    continue
                g = gmap.get(ids[0])
                if g is None:
                    continue
                up = g.annotation.get("uniprot")
                if isinstance(up, list):
                    up = up[0]
                if not up:
                    continue
                gr = (row["growth"] / wt) if (wt and row["growth"] == row["growth"]) else 0.0
                ess = 1 if gr < 0.01 else 0
                fh.write(f"{org}\t{up}\t{g.id}\t{ess}\t{gr:.4f}\n"); n += 1
            print(f"{org} ({gid}): WT growth {wt:.3f}, {n} genes w/ uniprot, "
                  f"essential {sum(1 for _ in [0])}... [{time.time()-t0:.0f}s]", flush=True)
    # summary
    import collections
    cnt = collections.Counter(); ess = collections.Counter()
    for ln in open(TSV):
        p = ln.rstrip().split("\t")
        if p[0] == "organism": continue
        cnt[p[0]] += 1; ess[p[0]] += int(p[3])
    for o in GEMS:
        print(f"  {o}: {cnt[o]} genes, {ess[o]} FBA-essential ({100*ess[o]/max(cnt[o],1):.0f}%)")
    print(f"wrote {TSV} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
