#!/usr/bin/env python
"""TRANSFERLAW1 step 1 — compute the a-priori, outcome-INDEPENDENT metabolic-autonomy features per GEM.
Uses ONLY model topology (COBRApy): NO experimental essentiality, NO OR outcome (non-circularity, PREREG).
Features per GEM: log10_reactions, blocked_fraction (FVA), exchange_fraction, biomass_synth_fraction, gpr_coverage.
Deterministic; caches to $INTERCEPTA_DATA/transferlaw1/features.json so re-runs are fast + byte-identical."""
import os, json, math, sys
import cobra
from cobra.flux_analysis import find_blocked_reactions

D = os.environ.get("INTERCEPTA_DATA", os.path.expanduser("~/intercepta_data"))
CACHE = os.path.join(D, "transferlaw1"); os.makedirs(CACHE, exist_ok=True)
cobra_cfg = cobra.Configuration(); cobra_cfg.solver = "glpk"

def load_model(path):
    if path.endswith(".mat"):
        return cobra.io.load_matlab_model(path)
    return cobra.io.read_sbml_model(path)

def biomass_reaction(model):
    # objective first; else name/id containing 'biomass'
    try:
        objs = [r for r in model.reactions if r.objective_coefficient != 0]
        if objs: return objs[0]
    except Exception: pass
    for r in model.reactions:
        if "biomass" in (r.id + r.name).lower(): return r
    return None

def biomass_synth_fraction(model, bio):
    """Fraction of biomass PRECURSORS (reactants) the model can each produce de novo on its own medium."""
    if bio is None: return float("nan")
    reactants = [m for m, c in bio.metabolites.items() if c < 0]
    if not reactants: return float("nan")
    ok = 0
    for met in reactants:
        with model:
            try:
                dm = model.add_boundary(met, type="demand")
                model.objective = dm
                v = model.slim_optimize()
                if v is not None and v > 1e-6: ok += 1
            except Exception:
                pass
    return ok / len(reactants)

def compute(path, fmt=None):
    m = load_model(path)
    nrxn = len(m.reactions)
    try:
        blocked = len(find_blocked_reactions(m))
    except Exception:
        blocked = float("nan")
    exch = len(m.exchanges) if hasattr(m, "exchanges") else sum(1 for r in m.reactions if r.boundary)
    gpr = sum(1 for r in m.reactions if r.gene_reaction_rule and r.gene_reaction_rule.strip())
    bio = biomass_reaction(m)
    feats = {
        "n_reactions": int(nrxn), "n_genes": int(len(m.genes)), "n_metabolites": int(len(m.metabolites)),
        "log10_reactions": round(math.log10(nrxn), 4) if nrxn > 0 else float("nan"),
        "blocked_fraction": round(blocked / nrxn, 4) if isinstance(blocked, int) and nrxn else float("nan"),
        "exchange_fraction": round(exch / nrxn, 4) if nrxn else float("nan"),
        "biomass_synth_fraction": round(biomass_synth_fraction(m, bio), 4),
        "gpr_coverage": round(gpr / nrxn, 4) if nrxn else float("nan"),
        "biomass_rxn": bio.id if bio else None,
    }
    return feats

def get_features(key, path):
    cf = os.path.join(CACHE, "features.json")
    cache = json.load(open(cf)) if os.path.exists(cf) else {}
    if key in cache:
        return cache[key]
    feats = compute(path)
    cache[key] = feats
    json.dump(cache, open(cf, "w"), indent=2, sort_keys=True)
    return feats

if __name__ == "__main__":
    # quick validation on 3 GEMs: E. coli (high autonomy) vs Plasmodium (low) vs Toxoplasma
    tests = [("E.coli_iML1515", f"{D}/synleth/iML1515.xml"),
             ("Pf_iPfal19", f"{D}/generalize5/iPfal19.xml"),
             ("Toxo_iTgo2020", f"{D}/hardenp1/iTgo2020_krishnan.mat")]
    for key, path in tests:
        if not os.path.exists(path):
            print(f"{key}: MISSING {path}"); continue
        f = compute(path)
        print(f"{key}: rxn={f['n_reactions']} exch_frac={f['exchange_fraction']} "
              f"biomass_synth={f['biomass_synth_fraction']} blocked={f['blocked_fraction']} gpr={f['gpr_coverage']}")
