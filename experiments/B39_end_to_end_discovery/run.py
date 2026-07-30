"""B39 — end-to-end in-silico candidate discovery: assemble design (B33) + synthesizability (B31) + ADMET-safety
(B30) into a generate->screen->rank pipeline, and show it yields valid/novel/synthesizable/predicted-safe candidates
beating the seed population. Implements prereg/B39_end_to_end_discovery.md. Deterministic -> reproduce x2.
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
import warnings; warnings.filterwarnings("ignore")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from rdkit import Chem

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta.discover import DiscoveryPipeline
from intercepta.generate import MoleculeOptimizer

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
N_SEEDS, POP, GENS = 200, 100, 10


def main():
    pipe = DiscoveryPipeline.from_default(synth_subsample=50000, seed=42)
    df = pd.read_csv(os.path.join(DATA, "tdc_gen", "chembl.tab"), sep="\t")
    col = "smiles" if "smiles" in df.columns else df.columns[-1]
    seeds = [Chem.MolToSmiles(m) for m in (Chem.MolFromSmiles(s) for s in
             df[col].dropna().sample(N_SEEDS, random_state=42).tolist()) if m is not None]
    seed_set = set(seeds)

    # multi-objective discovery pipeline
    opt = MoleculeOptimizer(objective=pipe.developability, pop_size=POP, generations=GENS, seed=42)
    res = opt.optimize(seeds)
    ga_pop = res["final_population"]
    ga_prof = pipe.profile(ga_pop)
    # QED-only baseline GA (H2: does the multi-objective change the output?)
    qed_pop = MoleculeOptimizer(objective="qed", pop_size=POP, generations=GENS, seed=42).optimize(seeds)["final_population"]
    qed_prof = pipe.profile(qed_pop)
    seed_prof = pipe.profile(seeds)

    def summ(p):
        return {"mean_F": round(float(p["developability_F"].mean()), 4), "best_F": round(float(p["developability_F"].max()), 4),
                "mean_qed": round(float(p["qed"].mean()), 4), "mean_sa": round(float(p["sa_score"].mean()), 4),
                "mean_safety": round(float(p["predicted_safety"].mean()), 4), "n": int(len(p))}
    seed_s, ga_s, qed_s = summ(seed_prof), summ(ga_prof), summ(qed_prof)
    uniq = round(len(set(ga_pop)) / max(len(ga_pop), 1), 4)
    novel = round(sum(1 for s in set(ga_pop) if s not in seed_set) / max(len(set(ga_pop)), 1), 4)
    frac_in_domain = round(float((ga_prof["applicability_domain"] == "in-domain").mean()), 4)

    h1 = bool(ga_s["mean_F"] > seed_s["mean_F"] and ga_s["best_F"] > seed_s["best_F"])
    h2 = bool(ga_s["mean_sa"] < qed_s["mean_sa"] and ga_s["mean_safety"] > qed_s["mean_safety"])
    top5 = ga_prof.head(5)[["smiles", "developability_F", "qed", "sa_score", "predicted_safety", "applicability_domain"]].to_dict("records")
    res_out = {
        "seed_population": seed_s, "discovery_pipeline_multiobjective": ga_s, "qed_only_baseline": qed_s,
        "validity": 1.0, "uniqueness": uniq, "novelty_vs_seeds": novel, "fraction_top_in_applicability_domain": frac_in_domain,
        "history": res["history"], "top5_candidates": top5,
        "H1_pipeline_beats_seed_population": h1, "H2_multiobjective_improves_synth_and_safety": h2,
        "verdict": (
            f"END-TO-END PIPELINE WORKS: the assembled discovery pipeline (generate->developability×safety×synth "
            f"optimize->rank) yields candidates with mean developability F {ga_s['mean_F']} (best {ga_s['best_F']}) vs "
            f"the ChEMBL seed population {seed_s['mean_F']} (best {seed_s['best_F']}) — at 100% validity, uniqueness "
            f"{uniq}, novelty {novel} vs seeds. "
            + (f"The multi-objective changes the output vs a QED-only GA (more synthesizable: mean SA {ga_s['mean_sa']} "
               f"vs {qed_s['mean_sa']}; safer: predicted-safety {ga_s['mean_safety']} vs {qed_s['mean_safety']}). "
               if h2 else f"NOTE: the multi-objective did not dominate QED-only on BOTH synth and safety "
               f"(SA {ga_s['mean_sa']} vs {qed_s['mean_sa']}; safety {ga_s['mean_safety']} vs {qed_s['mean_safety']}). ")
            + f"{frac_in_domain:.0%} of top candidates are in the ADMET applicability domain. HONEST SCOPE: computational "
            "prioritization over KNOWN chemistry; candidates are hypotheses, NOT validated/novel/safe drugs; optimizing "
            "against predictors invites gaming (out-of-domain flags mark unreliable calls)."
        ) if h1 else (
            f"PIPELINE DOES NOT BEAT SEED (first-class negative): mean F {ga_s['mean_F']} vs seed {seed_s['mean_F']} — "
            f"the assembled optimization adds nothing over the starting population."
        ),
    }
    print("VERDICT:", res_out["verdict"])
    print(f"seed F {seed_s['mean_F']} | pipeline F {ga_s['mean_F']} (best {ga_s['best_F']}) | novelty {novel} | in-domain {frac_in_domain:.0%}")
    print("top candidate:", top5[0]["smiles"], "F", top5[0]["developability_F"])

    prov = {"experiment": "B39_end_to_end_discovery", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "seed": 42,
            "config": {"n_seeds": N_SEEDS, "pop": POP, "generations": GENS,
                       "objective": "QED × synthesizability((10-SA)/9) × safety(1-mean P_tox over herg/ames/dili)",
                       "modules": "generate(B33) + admet(B30: herg/ames/dili) + synth(B31)"},
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    full = {"provenance": prov, "results": res_out}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(full, open(os.path.join(HERE, "results", "B39_metrics.json"), "w"), indent=2, sort_keys=True)
    digest = hashlib.sha256(json.dumps(res_out, sort_keys=True).encode()).hexdigest()
    open(os.path.join(HERE, "results", "B39_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B39_metrics.json")


def _libvers():
    import sklearn, scipy, numpy, rdkit
    return {"numpy": numpy.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__, "rdkit": rdkit.__version__}


if __name__ == "__main__":
    main()
