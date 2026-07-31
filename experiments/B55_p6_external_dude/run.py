"""B55 — attempted external replication of P6 on DUD-E; result: DUD-E CANNOT support the test. This runner quantifies
why: DUD-E actives are so analog-clustered (and their distinct Murcko scaffolds do NOT reflect that clustering) that a
novel-chemistry (NN<0.4) analog-control arm is essentially empty, so the B54 factorial is not runnable on DUD-E. A
first-class methodological finding; P6's external replication is deferred to a chemically-diverse benchmark (MUV).
Deterministic -> reproduce x2. No docking.
"""
import os, sys, json, time, hashlib
import numpy as np
import warnings; warnings.filterwarnings("ignore")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from rdkit.Chem.Scaffolds import MurckoScaffold

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
DUDE = os.path.join(DATA, "dude")
TARGETS = ["egfr", "vgfr2", "akt1", "aa2ar", "fa10", "hivpr", "ppara", "gcr"]
MAX_ACT, NN_NOVEL, SEEDS, MIN_NOVEL_TEST = 400, 0.40, [1, 2, 3, 4, 5], 15


def read_ism(p): return [l.split()[0] for l in open(p) if l.split()]
def largest(smi):
    m = Chem.MolFromSmiles(str(smi))
    if m is None: return None
    fr = Chem.GetMolFrags(m, asMols=True, sanitizeFrags=True)
    return max(fr, key=lambda f: f.GetNumHeavyAtoms()) if fr else m
def bit(m): return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=1024)
def murcko(m):
    try: return Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(m))
    except Exception: return ""


def evaluate(tgt):
    smis = read_ism(os.path.join(DUDE, tgt, "actives.ism"))
    mols = [m for m in (largest(s) for s in smis) if m is not None]
    rng = np.random.default_rng(42)
    if len(mols) > MAX_ACT:
        mols = [mols[i] for i in sorted(rng.permutation(len(mols))[:MAX_ACT])]
    fps = [bit(m) for m in mols]; scaf = [murcko(m) for m in mols]
    n = len(mols)
    # leave-one-out nearest-neighbour Tanimoto among actives (analog clustering)
    nn = np.array([max(DataStructs.BulkTanimotoSimilarity(fps[i], fps[:i] + fps[i + 1:])) if n > 1 else 0.0 for i in range(n)])
    # max novel-chemistry test actives achievable under a 30% scaffold split (mirrors B54 B1), over seeds
    uniq = sorted(set(scaf)); novel_counts = []
    for seed in SEEDS:
        perm = np.random.default_rng(seed).permutation(np.array(uniq, dtype=object))
        tsc = set(perm[:max(1, int(0.3 * len(uniq)))]); te = np.array([s in tsc for s in scaf])
        tr_idx = np.where(~te)[0]; te_cand = np.where(te)[0]; tr_fps = [fps[i] for i in tr_idx]
        nv = sum(1 for i in te_cand if max(DataStructs.BulkTanimotoSimilarity(fps[i], tr_fps)) < NN_NOVEL)
        novel_counts.append(nv)
    return {"n_actives": n, "n_unique_murcko_scaffolds": len(set(scaf)),
            "loo_nn_tanimoto_mean": round(float(nn.mean()), 4), "loo_nn_tanimoto_median": round(float(np.median(nn)), 4),
            "frac_nn_lt_0.4": round(float(np.mean(nn < 0.4)), 4), "frac_nn_lt_0.5": round(float(np.mean(nn < 0.5)), 4),
            "mean_novel_test_actives_scaffold_split": round(float(np.mean(novel_counts)), 2),
            "supports_novel_arm": bool(np.mean(novel_counts) >= MIN_NOVEL_TEST)}


def main():
    per = {}
    for t in TARGETS:
        s = evaluate(t); per[t] = s
        print(f"  {t:7s} n={s['n_actives']:3d} uniqScaf={s['n_unique_murcko_scaffolds']:3d} | LOO-NN mean "
              f"{s['loo_nn_tanimoto_mean']} frac<0.4 {s['frac_nn_lt_0.4']} | novel-test-actives(scaffold split) "
              f"{s['mean_novel_test_actives_scaffold_split']} -> supports novel arm: {s['supports_novel_arm']}")

    n_support = int(sum(1 for v in per.values() if v["supports_novel_arm"]))
    mean_nn = round(float(np.mean([v["loo_nn_tanimoto_mean"] for v in per.values()])), 4)
    mean_frac = round(float(np.mean([v["frac_nn_lt_0.4"] for v in per.values()])), 4)
    # DUD-E paradox: unique scaffolds ~= n_actives, yet NN high -> scaffold split ineffective for analog control
    scaf_ratio = round(float(np.mean([v["n_unique_murcko_scaffolds"] / v["n_actives"] for v in per.values()])), 3)

    summary = {"n_targets": len(per), "n_targets_supporting_novel_arm": n_support,
               "panel_mean_loo_nn_tanimoto": mean_nn, "panel_mean_frac_nn_lt_0.4": mean_frac,
               "panel_mean_unique_scaffold_ratio": scaf_ratio,
               "p6_externally_tested": bool(n_support >= 2),
               "verdict": (
                   f"INCONCLUSIVE FOR P6 — DUD-E CANNOT SUPPORT THE TEST (a first-class methodological finding): DUD-E "
                   f"actives are extremely analog-clustered (panel mean leave-one-out NN-Tanimoto {mean_nn}; only "
                   f"{mean_frac*100:.1f}% of actives are NN<0.4), so a novel-chemistry analog-control arm is empty "
                   f"({n_support}/{len(per)} targets reach >={MIN_NOVEL_TEST} novel test actives) and the B54 2x2 "
                   f"factorial is not runnable on DUD-E. **Sharper:** DUD-E actives have distinct Murcko scaffolds "
                   f"(unique-scaffold ratio {scaf_ratio}~1.0) YET mean NN {mean_nn} -> SCAFFOLD-SPLITTING DOES NOT "
                   f"CONTROL ANALOG SIMILARITY ON DUD-E; 'scaffold-split novelty' is illusory here. Consequences: (1) "
                   f"P6 (bias independence/additivity, B54) remains externally UNTESTED — status unchanged, NOT "
                   f"replicated and NOT falsified; its replication is deferred to a chemically-diverse benchmark (MUV, "
                   f"built for spread). (2) A concrete warning: report analog control by explicit NN-distance, not by "
                   f"scaffold split, on clustered benchmarks like DUD-E. Retrospective, in-silico, 8 targets; not wet-lab."
                   if n_support < 2 else
                   f"DUD-E supports the novel arm on {n_support}/{len(per)} targets (panel NN {mean_nn}); the P6 "
                   f"factorial can be run — see a follow-up. (Unexpected given DUD-E's known analog bias.)"),
               }
    print("\nVERDICT:", summary["verdict"])

    prov = {"experiment": "B55_p6_external_dude", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "targets": TARGETS, "max_act": MAX_ACT,
            "nn_novel": NN_NOVEL, "seeds": SEEDS, "min_novel_test": MIN_NOVEL_TEST,
            "note": "P6 external-replication ATTEMPT; DUD-E found unable to support the novel-chemistry arm.",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = {"provenance": prov, "summary": summary, "per_target": per}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "B55_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary, "per_target": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B55_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B55_metrics.json")


def _libvers():
    import rdkit, numpy
    return {"rdkit": rdkit.__version__, "numpy": numpy.__version__}


if __name__ == "__main__":
    main()
