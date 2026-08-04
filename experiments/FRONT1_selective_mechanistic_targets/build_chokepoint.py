"""FRONT1 Step A — metabolic CHOKEPOINT genes per pathogen from the MET2 CarveMe GEMs (UniProt-keyed).
A reaction is a chokepoint if it is the UNIQUE producer OR unique consumer of some non-currency metabolite
(Rahman/Schomburg 2006); a gene is a chokepoint gene if any of its reactions is a chokepoint. Exchange/demand/sink/
biomass reactions and currency metabolites excluded. Deterministic stoichiometry pass. Env: `metabolic` (cobra).
Output: $INTERCEPTA_DATA/front1/chokepoints.tsv (organism, uniprot, chokepoint).
"""
import os, time, warnings; warnings.filterwarnings("ignore")
from collections import defaultdict
from cobra.io import read_sbml_model

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
GEMS = os.path.join(DATA, "met2", "gems")
OUT = os.path.join(DATA, "front1"); os.makedirs(OUT, exist_ok=True)
ORGS = ["ecoli", "mtb", "paeruginosa", "bsubtilis", "hpylori", "salmonella", "efaecalis"]
# currency metabolites (BiGG base ids) excluded from chokepoint counting
CURRENCY = {"h", "h2o", "atp", "adp", "amp", "pi", "ppi", "nad", "nadh", "nadp", "nadph", "co2", "o2",
            "nh4", "coa", "h2o2", "fad", "fadh2", "gtp", "gdp", "gmp", "utp", "udp", "ump", "ctp", "cdp",
            "cmp", "so4", "hco3", "na1", "k", "cl", "mg2", "fe2", "fe3", "ca2", "mn2", "zn2", "cu2",
            "cobalt2", "mobd", "ni2", "h2s", "so3", "acp", "thf", "amet", "ahcys", "q8", "q8h2", "mqn8",
            "mql8", "2dmmql8", "2dmmq8", "fmn", "fmnh2", "pydx5p", "trdrd", "trdox", "nadph"}
EXCL_PREFIX = ("EX_", "DM_", "SK_", "sink_", "demand_")


def base(mid):  # strip compartment suffix: atp_c -> atp
    return mid.rsplit("_", 1)[0]


def main():
    t0 = time.time()
    with open(os.path.join(OUT, "chokepoints.tsv"), "w") as fh:
        fh.write("organism\tuniprot\tchokepoint\n")
        for org in ORGS:
            gem = os.path.join(GEMS, f"{org}.xml")
            if not os.path.exists(gem):
                print(f"{org}: GEM missing, skip", flush=True); continue
            m = read_sbml_model(gem)
            producers, consumers = defaultdict(set), defaultdict(set)
            for r in m.reactions:
                if r.id.startswith(EXCL_PREFIX) or "biomass" in r.id.lower():
                    continue
                rev = r.reversibility
                for met, coeff in r.metabolites.items():
                    if base(met.id) in CURRENCY:
                        continue
                    if coeff > 0 or rev:
                        producers[met.id].add(r.id)
                    if coeff < 0 or rev:
                        consumers[met.id].add(r.id)
            choke_rxn = set()
            for mid, prods in producers.items():
                if len(prods) == 1:
                    choke_rxn |= prods
            for mid, cons in consumers.items():
                if len(cons) == 1:
                    choke_rxn |= cons
            choke_genes = set()
            for g in m.genes:
                if any(r.id in choke_rxn for r in g.reactions):
                    choke_genes.add(g.id)
            for g in m.genes:
                fh.write(f"{org}\t{g.id}\t{1 if g.id in choke_genes else 0}\n")
            fh.flush()
            print(f"{org}: {len(m.genes)} genes, {len(choke_genes)} chokepoint ({100*len(choke_genes)/max(len(m.genes),1):.0f}%), "
                  f"{len(choke_rxn)} chokepoint reactions [{time.time()-t0:.0f}s]", flush=True)
    print(f"wrote {os.path.join(OUT,'chokepoints.tsv')} [{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
