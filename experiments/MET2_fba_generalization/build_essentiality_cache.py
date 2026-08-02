"""MET2 Step A — FBA gene-essentiality on DE-NOVO CarveMe GEMs (UniProt-keyed genes by construction) under a consistent
glucose-aerobic MINIMAL medium, for 3 bacteria. Tests whether MET1's essentiality-breaks-conservation result GENERALIZES.
Output: $INTERCEPTA_DATA/met2/essentiality.tsv. Env: `metabolic`. Run: metabolic python.
"""
import os, time, warnings; warnings.filterwarnings("ignore")
from cobra.io import read_sbml_model
from cobra.flux_analysis import single_gene_deletion

DATA = os.path.join(os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data"), "met2")
ORGS = ["ecoli", "mtb", "paeruginosa"]
TSV = os.path.join(DATA, "essentiality.tsv")
# glucose aerobic minimal medium (standard BiGG exchange ids) — consistent across CarveMe models
MINIMAL = {"EX_glc__D_e": 10, "EX_o2_e": 20, "EX_nh4_e": 1000, "EX_pi_e": 1000, "EX_so4_e": 1000,
           "EX_h2o_e": 1000, "EX_h_e": 1000, "EX_co2_e": 1000, "EX_k_e": 1000, "EX_na1_e": 1000,
           "EX_cl_e": 1000, "EX_mg2_e": 1000, "EX_fe2_e": 1000, "EX_fe3_e": 1000, "EX_ca2_e": 1000,
           "EX_mn2_e": 1000, "EX_zn2_e": 1000, "EX_cu2_e": 1000, "EX_cobalt2_e": 1000, "EX_mobd_e": 1000, "EX_ni2_e": 1000}


def main():
    t0 = time.time()
    with open(TSV, "w") as fh:
        fh.write("organism\tuniprot\tessential\tgrowth_ratio\n")
        for org in ORGS:
            gem = os.path.join(DATA, "gems", f"{org}.xml")
            if not os.path.exists(gem):
                print(f"{org}: GEM missing, skip", flush=True); continue
            m = read_sbml_model(gem)
            # consistent CORE-essentiality: use the model's DEFAULT (complete) medium so ALL organisms grow (glucose-
            # minimal fails for lipid-metabolisers like M. tuberculosis). Genes essential here are essential regardless
            # of nutrients -> the most drug-relevant. (Minimal-medium recipe kept below for reference / E. coli robustness.)
            wt = m.optimize().objective_value
            if not wt or wt < 1e-6:
                exset = {r.id for r in m.exchanges}
                m.medium = {r: v for r, v in MINIMAL.items() if r in exset}
                wt = m.optimize().objective_value
            if not wt or wt < 1e-6:
                print(f"{org}: NO growth (default or minimal); skipping", flush=True); continue
            d = single_gene_deletion(m, processes=1)
            gmap = {g.id: g for g in m.genes}
            n = 0
            for _, row in d.iterrows():
                ids = list(row["ids"]) if "ids" in row else list(row.name)
                if len(ids) != 1:
                    continue
                g = gmap.get(ids[0])
                if g is None:
                    continue
                gr = (row["growth"] / wt) if row["growth"] == row["growth"] else 0.0
                fh.write(f"{org}\t{g.id}\t{1 if gr < 0.01 else 0}\t{gr:.4f}\n"); n += 1
            fh.flush()
            print(f"{org}: WT {wt:.3f}, {n} genes, {sum(1 for _ in [0])} ... [{time.time()-t0:.0f}s]", flush=True)
    import collections
    c, e = collections.Counter(), collections.Counter()
    for ln in open(TSV):
        p = ln.rstrip().split("\t")
        if p[0] == "organism": continue
        c[p[0]] += 1; e[p[0]] += int(p[2])
    for o in ORGS:
        print(f"  {o}: {c[o]} genes, {e[o]} essential ({100*e[o]/max(c[o],1):.0f}%)")
    print(f"wrote {TSV} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
