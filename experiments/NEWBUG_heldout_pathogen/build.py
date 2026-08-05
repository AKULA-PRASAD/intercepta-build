"""NEWBUG build — FBA essentiality + metabolic chokepoint for a HELD-OUT WHO priority pathogen (K. pneumoniae, NOT in the
7-panel), from its de-novo CarveMe GEM. Mirrors MET2 (essentiality) + FRONT1 (chokepoint) for one organism. Env: metabolic.
Output: $INTERCEPTA_DATA/newbug/{essentiality.tsv,chokepoints.tsv} keyed by UniProt accession.
"""
import os, time, warnings; warnings.filterwarnings("ignore")
from collections import defaultdict
from cobra.io import read_sbml_model
from cobra.flux_analysis import single_gene_deletion

DATA = os.path.join(os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data"), "newbug")
GEM = os.path.join(DATA, "kpneumoniae.xml")
ORG = "kpneumoniae"
CURRENCY = {"h", "h2o", "atp", "adp", "amp", "pi", "ppi", "nad", "nadh", "nadp", "nadph", "co2", "o2", "nh4", "coa",
            "h2o2", "fad", "fadh2", "gtp", "gdp", "gmp", "utp", "udp", "ump", "ctp", "cdp", "cmp", "so4", "hco3", "na1",
            "k", "cl", "mg2", "fe2", "fe3", "ca2", "mn2", "zn2", "cu2", "cobalt2", "mobd", "ni2", "h2s", "so3", "acp",
            "thf", "amet", "ahcys", "q8", "q8h2", "mqn8", "mql8", "fmn", "fmnh2", "pydx5p", "trdrd", "trdox"}
EXCL = ("EX_", "DM_", "SK_", "sink_", "demand_")
MINIMAL = {"EX_glc__D_e": 10, "EX_o2_e": 20, "EX_nh4_e": 1000, "EX_pi_e": 1000, "EX_so4_e": 1000, "EX_h2o_e": 1000,
           "EX_h_e": 1000, "EX_co2_e": 1000, "EX_k_e": 1000, "EX_na1_e": 1000, "EX_cl_e": 1000, "EX_mg2_e": 1000,
           "EX_fe2_e": 1000, "EX_fe3_e": 1000, "EX_ca2_e": 1000, "EX_mn2_e": 1000, "EX_zn2_e": 1000, "EX_cu2_e": 1000}


def base(mid): return mid.rsplit("_", 1)[0]


def gid2acc(gid):
    """CarveMe encodes the UniProt FASTA header 'tr|A6T680|A6T680_KLEP7' as gene id 'tr_A6T680_A6T680_KLEP7'
    (| -> _). Recover the UniProt accession = the 2nd field."""
    p = gid.split("_")
    return p[1] if len(p) >= 2 and p[0] in ("sp", "tr") else gid


def main():
    t0 = time.time()
    m = read_sbml_model(GEM)
    wt = m.optimize().objective_value
    if not wt or wt < 1e-6:
        exset = {r.id for r in m.exchanges}; m.medium = {r: v for r, v in MINIMAL.items() if r in exset}
        wt = m.optimize().objective_value
    print(f"{ORG}: WT growth {wt:.3f}; {len(m.genes)} genes, {len(m.reactions)} rxns [{time.time()-t0:.0f}s]", flush=True)
    # essentiality
    d = single_gene_deletion(m, processes=1)
    gmap = {g.id: g for g in m.genes}
    with open(os.path.join(DATA, "essentiality.tsv"), "w") as fh:
        fh.write("organism\tuniprot\tessential\tgrowth_ratio\n")
        n = 0
        for _, row in d.iterrows():
            ids = list(row["ids"]) if "ids" in row else list(row.name)
            if len(ids) != 1 or gmap.get(ids[0]) is None: continue
            gr = (row["growth"] / wt) if row["growth"] == row["growth"] else 0.0
            fh.write(f"{ORG}\t{gid2acc(ids[0])}\t{1 if gr < 0.01 else 0}\t{gr:.4f}\n"); n += 1
    # chokepoint
    producers, consumers = defaultdict(set), defaultdict(set)
    for r in m.reactions:
        if r.id.startswith(EXCL) or "biomass" in r.id.lower(): continue
        rev = r.reversibility
        for met, coeff in r.metabolites.items():
            if base(met.id) in CURRENCY: continue
            if coeff > 0 or rev: producers[met.id].add(r.id)
            if coeff < 0 or rev: consumers[met.id].add(r.id)
    choke_rxn = set()
    for mid, s in producers.items():
        if len(s) == 1: choke_rxn |= s
    for mid, s in consumers.items():
        if len(s) == 1: choke_rxn |= s
    with open(os.path.join(DATA, "chokepoints.tsv"), "w") as fh:
        fh.write("organism\tuniprot\tchokepoint\n")
        for g in m.genes:
            fh.write(f"{ORG}\t{gid2acc(g.id)}\t{1 if any(r.id in choke_rxn for r in g.reactions) else 0}\n")
    ne = sum(1 for ln in open(os.path.join(DATA, 'essentiality.tsv')) if ln.rstrip().endswith('\t1') is False and '\t1\t' in ln)
    print(f"{ORG}: essentiality + chokepoints written [{time.time()-t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
