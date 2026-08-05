"""S. aureus-NATIVE resistance-robustness (SYNLETH) + condition-robustness (CONDROB) on its de-novo GEM, keyed by UniProt
accession (gid2acc) for the engine. Env: metabolic. HONEST: sparse default-medium CarveMe GEM -> low-confidence, as caveated."""
import os, logging, cobra
from cobra.flux_analysis import single_gene_deletion, single_reaction_deletion
logging.getLogger("cobra").setLevel(logging.ERROR)
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
GEM = os.path.join(DATA, "newbug3", "saureus.xml")
CARBON = {"glc": "EX_glc__D_e", "glyc": "EX_glyc_e", "ac": "EX_ac_e", "succ": "EX_succ_e"}


def gid2acc(g):
    p = g.split("_"); return p[1] if len(p) > 1 else g


def ess(m, base, carbon=None, anaerobic=False):
    ex = {r.id for r in m.exchanges}
    with m:
        med = dict(base)
        if carbon and carbon in ex:
            for c in CARBON.values(): med.pop(c, None)
            med[carbon] = 10.0
        if anaerobic: med.pop("EX_o2_e", None)
        try: m.medium = {k: v for k, v in med.items() if k in ex}
        except Exception: return None
        wt = m.slim_optimize()
        if not wt or wt < 1e-6: return None
        sg = single_gene_deletion(m, m.genes, processes=4); sg["gid"] = sg["ids"].apply(lambda s: list(s)[0])
        return set(sg[sg.growth < 0.01 * wt]["gid"])


def main():
    m = cobra.io.read_sbml_model(GEM); base = dict(m.medium); wt = m.slim_optimize(); thr = 0.01 * wt
    # resistance (SYNLETH): essential reactions + isozyme-buffered classification
    egenes = ess(m, base)
    sr = single_reaction_deletion(m, m.reactions, processes=4); sr["rid"] = sr["ids"].apply(lambda s: list(s)[0])
    erxns = set(sr[sr.growth < thr]["rid"]); combo_genes = set()
    for rid in erxns:
        genes = [g.id for g in m.reactions.get_by_id(rid).genes]
        if genes and not any(g in egenes for g in genes): combo_genes.update(genes)
    with open(os.path.join(DATA, "synleth", "saureus_resistance_classes.tsv"), "w") as f:
        f.write("gene\tclass\n"); seen = set()
        for g in m.genes:
            a = gid2acc(g.id)
            if a in seen: continue
            seen.add(a)
            f.write(f"{a}\t{'monotherapy_robust' if g.id in egenes else 'combination_required' if g.id in combo_genes else 'non_essential'}\n")
    # condition (CONDROB): multi-medium
    conds = {"glc_aer": dict(carbon="EX_glc__D_e"), "glyc_aer": dict(carbon="EX_glyc_e"),
             "ac_aer": dict(carbon="EX_ac_e"), "succ_aer": dict(carbon="EX_succ_e"), "glc_anaer": dict(carbon="EX_glc__D_e", anaerobic=True)}
    per = {}
    for name, kw in conds.items():
        e = ess(m, base, **kw)
        if e is not None: per[name] = e
    N = len(per); allg = set().union(*per.values()) if per else set()
    rob = {g: sum(1 for c in per if g in per[c]) for g in allg}
    with open(os.path.join(DATA, "synleth", "saureus_condition_robust.tsv"), "w") as f:
        f.write("gene\tclass\n"); seen = set()
        for g in m.genes:
            a = gid2acc(g.id)
            if a in seen: continue
            seen.add(a); k = rob.get(g.id, 0)
            f.write(f"{a}\t{'condition_robust' if k == N else 'condition_partial' if k >= 1 else 'non_essential'}\n")
    print(f"S. aureus native: {len(egenes)} essential, {len(combo_genes)} combination-genes; "
          f"condition over {N} media, {sum(1 for g in allg if rob[g]==N)} condition-robust")


if __name__ == "__main__":
    main()
