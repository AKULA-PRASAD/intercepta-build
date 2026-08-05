"""A. baumannii-NATIVE condition-robustness (CONDROB axis) on the held-out AB CarveMe GEM. Multi-medium single-gene
deletion -> per-gene condition-robustness class, keyed by UniProt accession (gid2acc) so it plugs straight into the engine.
Env: metabolic (cobra). HONEST: de-novo CarveMe default-medium GEM is sparse -> lower-confidence than iML1515 (as CONDROB1
caveated); AB is not Enterobacteriaceae so E. coli transfer would be inappropriate -> native is the honest choice here.
"""
import os, logging, cobra
from cobra.flux_analysis import single_gene_deletion
logging.getLogger("cobra").setLevel(logging.ERROR)
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
GEM = os.path.join(DATA, "newbug2", "abaumannii.xml")
CARBON = {"glc": "EX_glc__D_e", "glyc": "EX_glyc_e", "ac": "EX_ac_e", "succ": "EX_succ_e"}


def gid2acc(g):
    p = g.split("_"); return p[1] if len(p) > 1 else g


def ess_under(m, base, carbon=None, anaerobic=False):
    exchanges = {r.id for r in m.exchanges}
    with m:
        med = dict(base)
        if carbon and carbon in exchanges:
            for ex in CARBON.values(): med.pop(ex, None)
            med[carbon] = 10.0
        if anaerobic: med.pop("EX_o2_e", None)
        try: m.medium = {k: v for k, v in med.items() if k in exchanges}
        except Exception: return None
        wt = m.slim_optimize()
        if not wt or wt < 1e-6: return None
        sg = single_gene_deletion(m, m.genes, processes=4); sg["gid"] = sg["ids"].apply(lambda s: list(s)[0])
        return set(sg[sg.growth < 0.01 * wt]["gid"])


def main():
    m = cobra.io.read_sbml_model(GEM); base = dict(m.medium)
    conds = {"glc_aer": dict(carbon="EX_glc__D_e"), "glyc_aer": dict(carbon="EX_glyc_e"),
             "ac_aer": dict(carbon="EX_ac_e"), "succ_aer": dict(carbon="EX_succ_e"),
             "glc_anaer": dict(carbon="EX_glc__D_e", anaerobic=True)}
    per = {}
    for name, kw in conds.items():
        e = ess_under(m, base, **kw)
        if e is not None: per[name] = e; print(f"  [{name}] essential {len(e)}", flush=True)
    N = len(per); allg = set().union(*per.values()) if per else set()
    rob = {g: sum(1 for c in per if g in per[c]) for g in allg}
    with open(os.path.join(DATA, "synleth", "abaumannii_condition_robust.tsv"), "w") as f:
        f.write("gene\tclass\n"); seen = set()
        for g in m.genes:
            acc = gid2acc(g.id)
            if acc in seen: continue
            seen.add(acc); k = rob.get(g.id, 0)
            cls = "condition_robust" if k == N else "condition_partial" if k >= 1 else "non_essential"
            f.write(f"{acc}\t{cls}\n")
    nrob = sum(1 for g in allg if rob[g] == N)
    print(f"AB-native condition-robustness over {N} media: {len(allg)} ever-essential, {nrob} condition-robust (all media)")


if __name__ == "__main__":
    main()
