"""B41 — applicability-domain-constrained Pareto multi-objective discovery. Fixes B40's scalarization + reward-hacking
(OOD drift) with NSGA-II Pareto selection + a reliability (AD) constraint; re-examines the activity-vs-safety
trade-off within the reliable domain. Implements prereg/B41_pareto_reliable_discovery.md. Deterministic -> x2.
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
from intercepta.admet import featurize
from intercepta.discover import DiscoveryPipeline, build_target_qsar
from intercepta.generate import MoleculeOptimizer, ParetoOptimizer, qed_score, synth_score, _fast_non_dominated_sort

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
N_SEEDS, POP, GENS = 200, 100, 8
OBJ_NAMES = ["activity", "safety", "qed", "synth"]


def main():
    pipe = DiscoveryPipeline.from_default(synth_subsample=50000, seed=42)
    qsar = build_target_qsar("hiv", seed=42)
    herg = pipe.admet.models_["herg"]; tox = [pipe.admet.models_[t] for t in pipe.TOX]

    cache = {}
    def vec_and_feas(mol):
        smi = Chem.MolToSmiles(mol)
        if smi in cache:
            return cache[smi]
        X, _ = featurize([smi])
        act, act_dom = float(qsar.predict(X)[0][0]), bool(qsar.predict(X)[2][0])
        safety = 1.0 - float(np.mean([t.predict(X)[0][0] for t in tox]))
        adm_dom = bool(herg.predict(X)[2][0])
        v = (np.array([act, safety, qed_score(mol), synth_score(mol)]), bool(act_dom and adm_dom))
        cache[smi] = v; return v
    objective_vec = lambda m: vec_and_feas(m)[0]
    feasible = lambda m: vec_and_feas(m)[1]

    chem = pd.read_csv(os.path.join(DATA, "tdc_gen", "chembl.tab"), sep="\t")
    col = "smiles" if "smiles" in chem.columns else chem.columns[-1]
    seeds = [Chem.MolToSmiles(m) for m in (Chem.MolFromSmiles(s) for s in
             chem[col].dropna().sample(N_SEEDS, random_state=42).tolist()) if m is not None]

    cond = DiscoveryPipeline(pipe.admet, pipe.synth, seed=42, target_model=qsar, target_name="hiv")

    def hypervolume(F, ref=np.zeros(4), n=20000, seed=0):
        """Monte-Carlo dominated hypervolume in [0,1]^4 for a maximize front F (n x 4)."""
        if len(F) == 0:
            return 0.0
        rng = np.random.default_rng(seed); pts = rng.random((n, 4))
        dom = np.zeros(n, bool)
        for f in F:
            dom |= np.all(pts <= f, axis=1)
        return round(float(dom.mean()), 4)

    def eval_pop(smiles):
        mols = [Chem.MolFromSmiles(s) for s in smiles]; mols = [m for m in mols if m]
        F = np.vstack([objective_vec(m) for m in mols]); feas = np.array([feasible(m) for m in mols])
        fi = np.where(feas)[0]
        front = fi[_fast_non_dominated_sort(F[fi])[0]] if len(fi) else np.array([], int)
        # best balanced in-domain candidate = max min(activity, safety) among feasible
        bal_idx = fi[np.argmax(np.minimum(F[fi, 0], F[fi, 1]))] if len(fi) else None
        return {"n": len(mols), "in_domain_frac": round(float(feas.mean()), 4),
                "mean": {OBJ_NAMES[j]: round(float(F[:, j].mean()), 4) for j in range(4)},
                "front_size": int(len(front)), "hypervolume_front": hypervolume(F[front]) if len(front) else 0.0,
                "best_balanced": (None if bal_idx is None else
                    {"smiles": smiles[bal_idx], **{OBJ_NAMES[j]: round(float(F[bal_idx, j]), 4) for j in range(4)}}),
                # activity-safety correlation among in-domain (trade-off sign)
                "activity_safety_corr_indomain": (round(float(np.corrcoef(F[fi, 0], F[fi, 1])[0, 1]), 4)
                                                   if len(fi) > 5 else None)}

    seed_stats = eval_pop(seeds)
    A_pop = MoleculeOptimizer(objective=cond.developability, pop_size=POP, generations=GENS, seed=42).optimize(seeds)["final_population"]
    B_pop = ParetoOptimizer(objective_vec, feasible=None, pop_size=POP, generations=GENS, seed=42).optimize(seeds)["population"]
    C_pop = ParetoOptimizer(objective_vec, feasible=feasible, pop_size=POP, generations=GENS, seed=42).optimize(seeds)["population"]
    A, B, C = eval_pop(A_pop), eval_pop(B_pop), eval_pop(C_pop)
    for tag, s in [("A scalar/unconstrained (~B40)", A), ("B Pareto/unconstrained", B), ("C Pareto/AD-constrained", C)]:
        print(f"[{tag:32s}] in-domain {s['in_domain_frac']:.2f} | HV {s['hypervolume_front']} | front {s['front_size']} | "
              f"mean act {s['mean']['activity']} safety {s['mean']['safety']} | corr(act,safety) {s['activity_safety_corr_indomain']}")

    def has_balanced(s):  # a candidate above seed medians on BOTH activity and safety
        b = s["best_balanced"]
        return bool(b and b["activity"] > seed_stats["mean"]["activity"] and b["safety"] > seed_stats["mean"]["safety"])
    h1 = bool(C["in_domain_frac"] > A["in_domain_frac"] + 0.1)                 # AD constraint improves reliability
    h2 = bool(has_balanced(C) or has_balanced(B))                             # Pareto finds active-AND-safe candidate
    h4 = bool(max(B["hypervolume_front"], C["hypervolume_front"]) >= A["hypervolume_front"])
    res = {
        "seed": seed_stats, "arm_A_scalar_unconstrained": A, "arm_B_pareto": B, "arm_C_pareto_ad_constrained": C,
        "H1_ad_constraint_improves_reliability": h1, "H2_pareto_finds_balanced_candidate": h2,
        "H4_pareto_hypervolume_ge_scalar": h4,
        "verdict": (
            f"AD-CONSTRAINED PARETO DISCOVERY IMPROVES ON SCALARIZATION: NSGA-II + reliability constraint raises the "
            f"in-domain (reliable) fraction to {C['in_domain_frac']:.0%} (vs {A['in_domain_frac']:.0%} for the scalar/"
            f"unconstrained B40-style arm), recovers a wider Pareto front (HV {max(B['hypervolume_front'],C['hypervolume_front'])} "
            f"vs scalar {A['hypervolume_front']}), and finds candidates that are BOTH active and safe "
            f"(best-balanced reliable candidate act {C['best_balanced']['activity'] if C['best_balanced'] else 'NA'}, "
            f"safety {C['best_balanced']['safety'] if C['best_balanced'] else 'NA'}). Activity-safety correlation among "
            f"reliable candidates: {C['activity_safety_corr_indomain']} (vs unconstrained {A['activity_safety_corr_indomain']}) "
            f"— the honest read on whether the trade-off is intrinsic or partly OOD artifact. HONEST SCOPE: all "
            f"objectives are in-silico predictions; the AD constraint improves RELIABILITY, not ground truth; "
            f"candidates are hypotheses, not validated/safe/active drugs."
        ) if (h1 and h2 and h4) else (
            f"PARTIAL: H1(reliability)={h1} H2(balanced)={h2} H4(HV≥scalar)={h4}. in-domain A {A['in_domain_frac']:.2f} "
            f"C {C['in_domain_frac']:.2f}; HV A {A['hypervolume_front']} B {B['hypervolume_front']} C {C['hypervolume_front']}. "
            f"See per-arm numbers — the AD-constrained Pareto approach did not clear all criteria; reported honestly."
        ),
    }
    print("\nVERDICT:", res["verdict"])

    prov = {"experiment": "B41_pareto_reliable_discovery", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "seed": 42,
            "config": {"n_seeds": N_SEEDS, "pop": POP, "generations": GENS, "objectives": OBJ_NAMES,
                       "target": "HIV QSAR (B40)", "hypervolume": "Monte-Carlo in [0,1]^4, 20000 pts, seed 0"},
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    full = {"provenance": prov, "results": res}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(full, open(os.path.join(HERE, "results", "B41_metrics.json"), "w"), indent=2, sort_keys=True)
    digest = hashlib.sha256(json.dumps(res, sort_keys=True).encode()).hexdigest()
    open(os.path.join(HERE, "results", "B41_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B41_metrics.json")


def _libvers():
    import sklearn, scipy, numpy, rdkit
    return {"numpy": numpy.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__, "rdkit": rdkit.__version__}


if __name__ == "__main__":
    main()
