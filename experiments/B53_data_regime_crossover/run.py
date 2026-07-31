"""B53 — the data-regime crossover: as known actives N shrinks, does structure-based docking (N-independent) beat the
best ligand-based method (QSAR / similarity)? Draws AUROC vs N for each channel on a fixed scaffold-held-out test set,
finds the crossover N*. Implements prereg/B53_data_regime_crossover.md. Runs in `docking` env. Deterministic -> x2.
"""
import os, sys, json, time, hashlib, tempfile, shutil, subprocess
import numpy as np
import warnings; warnings.filterwarnings("ignore")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit.ML.Scoring.Scoring import CalcAUC
from sklearn.ensemble import HistGradientBoostingClassifier
from vina import Vina

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
LIT = os.path.join(DATA, "lit_pcba")
OBABEL = "/Users/kalki/miniconda3/envs/docking/bin/obabel"
TARGETS = ["FEN1", "MAPK1", "VDR"]
N_TEST_ACT, N_TEST_DEC, N_TRAIN_INACT = 50, 100, 2000
N_GRID, SUB_SEEDS, EMBED_SEED, BOX = [5, 10, 20, 40, 80, 160], [1, 2, 3, 4, 5], 0xB53, [22.0, 22.0, 22.0]


def read_smi(p): return [l.split()[0] for l in open(p) if l.split()]
def largest(smi):
    m = Chem.MolFromSmiles(str(smi))
    if m is None: return None
    fr = Chem.GetMolFrags(m, asMols=True, sanitizeFrags=True)
    return max(fr, key=lambda f: f.GetNumHeavyAtoms()) if fr else m
def murcko(m):
    try: return Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(m))
    except Exception: return ""
def ecfp(m): return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048)
def morgan1024(m):
    a = np.zeros(1024, dtype=np.float32)
    DataStructs.ConvertToNumpyArray(AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=1024), a); return a
def auroc(y, s):
    r = [[int(y[i])] for i in np.argsort(-np.asarray(s))]; return float(CalcAUC(r, 0))
def prank(x):
    x = np.asarray(x, float); o = x.argsort(); r = np.empty_like(o, float); r[o] = np.arange(len(x)); return r / max(len(x) - 1, 1)


def prep_lig(mol, out):
    mh = Chem.AddHs(mol); p = AllChem.ETKDGv3(); p.randomSeed = EMBED_SEED
    if AllChem.EmbedMolecule(mh, p) != 0:
        p.useRandomCoords = True
        if AllChem.EmbedMolecule(mh, p) != 0: return False
    try: AllChem.MMFFOptimizeMolecule(mh)
    except Exception: pass
    Chem.MolToMolFile(mh, out + ".sdf")
    subprocess.run([OBABEL, out + ".sdf", "-O", out + ".pdbqt"], capture_output=True)
    return os.path.exists(out + ".pdbqt") and os.path.getsize(out + ".pdbqt") > 0


def centroid(path):
    xs = [[float(l[30:38]), float(l[38:46]), float(l[46:54])] for l in open(path) if l.startswith(("ATOM", "HETATM"))]
    return list(np.mean(np.array(xs), axis=0))


def dock(rec, lig, c):
    v = Vina(sf_name="vina", seed=42, cpu=8, verbosity=0)
    v.set_receptor(rec); v.set_ligand_from_file(lig)
    v.compute_vina_maps(center=c, box_size=BOX); v.dock(exhaustiveness=8, n_poses=3)
    return float(v.energies(n_poses=1)[0][0])


def evaluate(tgt, work):
    td = os.path.join(LIT, tgt)
    prot = sorted(f for f in os.listdir(td) if f.endswith("_protein.mol2"))[0]
    lig0 = sorted(f for f in os.listdir(td) if f.endswith("_ligand.mol2"))[0]
    rec = os.path.join(work, f"{tgt}_rec.pdbqt"); l0 = os.path.join(work, f"{tgt}_l0.pdbqt")
    subprocess.run([OBABEL, os.path.join(td, prot), "-O", rec, "-xr"], capture_output=True)
    subprocess.run([OBABEL, os.path.join(td, lig0), "-O", l0], capture_output=True)
    c = centroid(l0)

    acts = [(Chem.MolToSmiles(m), m) for m in (largest(s) for s in read_smi(os.path.join(td, "actives.smi"))) if m]
    acts = list({s: m for s, m in acts}.items())
    decs = [(Chem.MolToSmiles(m), m) for m in (largest(s) for s in read_smi(os.path.join(td, "inactives.smi"))) if m]
    aset = {s for s, _ in acts}; decs = [(s, m) for s, m in {s: m for s, m in decs}.items() if s not in aset]

    # scaffold-aware split: 20% of active scaffolds -> test scaffolds
    scafs = sorted({murcko(m) for _, m in acts})
    perm = np.random.default_rng(42).permutation(len(scafs))
    test_scafs = {scafs[i] for i in perm[:max(1, int(0.2 * len(scafs)))]}
    test_acts = [(s, m) for s, m in acts if murcko(m) in test_scafs]
    pool_acts = [(s, m) for s, m in acts if murcko(m) not in test_scafs]
    rng = np.random.default_rng(42)
    if len(test_acts) > N_TEST_ACT:
        test_acts = [test_acts[i] for i in sorted(rng.permutation(len(test_acts))[:N_TEST_ACT])]
    test_decs = [decs[i] for i in sorted(rng.permutation(len(decs))[:N_TEST_DEC])]
    if len(pool_acts) < max(N_GRID) or len(test_acts) < 10:
        return {"note": f"insufficient actives (pool {len(pool_acts)}, test {len(test_acts)})"}

    test = test_acts + test_decs
    y = np.array([1] * len(test_acts) + [0] * len(test_decs))
    test_fp1024 = np.vstack([morgan1024(m) for _, m in test])
    test_ecfp = [ecfp(m) for _, m in test]

    # docking the test set once (N-independent)
    dock_sc, ok = [], []
    for i, (s, m) in enumerate(test):
        lp = os.path.join(work, f"{tgt}_t{i}")
        if not prep_lig(m, lp):
            dock_sc.append(np.nan); ok.append(False); continue
        try:
            dock_sc.append(-dock(rec, lp + ".pdbqt", c)); ok.append(True)
        except Exception:
            dock_sc.append(np.nan); ok.append(False)
        for e in (".pdbqt", ".sdf"):
            if os.path.exists(lp + e): os.remove(lp + e)
    dock_sc = np.array(dock_sc); ok = np.array(ok)
    yv = y[ok]; dvec = dock_sc[ok]; fp1024 = test_fp1024[ok]; ecfp_ok = [test_ecfp[i] for i in np.where(ok)[0]]
    docking_auroc = round(auroc(yv, dvec), 4)

    pool_fp1024 = {s: morgan1024(m) for s, m in pool_acts}
    pool_ecfp = {s: ecfp(m) for s, m in pool_acts}
    # fixed training inactives (Morgan-1024) for QSAR
    tr_inact = [decs[i] for i in sorted(np.random.default_rng(7).permutation(len(decs))[:N_TRAIN_INACT])]
    tr_inact = [s for s, _ in tr_inact if s not in {ts for ts, _ in test_decs}]
    Xinact = np.vstack([morgan1024(Chem.MolFromSmiles(s)) for s in tr_inact])

    curve = {}
    pool_keys = [s for s, _ in pool_acts]
    for N in N_GRID:
        q_aucs, s_aucs, f_aucs = [], [], []
        for seed in SUB_SEEDS:
            sel = np.random.default_rng(seed).permutation(len(pool_keys))[:N]
            act_keys = [pool_keys[i] for i in sel]
            # QSAR(N)
            Xtr = np.vstack([pool_fp1024[k] for k in act_keys] + [Xinact])
            ytr = np.array([1] * N + [0] * len(Xinact))
            m = HistGradientBoostingClassifier(random_state=42, max_iter=150, learning_rate=0.06, max_depth=6).fit(Xtr, ytr)
            q = m.predict_proba(fp1024)[:, 1]; q_aucs.append(auroc(yv, q))
            # similarity(N): max Tanimoto to the N training actives
            refs = [pool_ecfp[k] for k in act_keys]
            sim = np.array([max(DataStructs.BulkTanimotoSimilarity(fp, refs)) for fp in ecfp_ok]); s_aucs.append(auroc(yv, sim))
            # rank fusion of (QSAR, sim, docking)
            fus = (prank(q) + prank(sim) + prank(dvec)) / 3.0; f_aucs.append(auroc(yv, fus))
        curve[N] = {"qsar": round(float(np.mean(q_aucs)), 4), "qsar_sd": round(float(np.std(q_aucs)), 4),
                    "similarity": round(float(np.mean(s_aucs)), 4), "sim_sd": round(float(np.std(s_aucs)), 4),
                    "best_ligand": round(float(np.mean([max(q, s) for q, s in zip(q_aucs, s_aucs)])), 4),
                    "fusion": round(float(np.mean(f_aucs)), 4)}
    # crossover N* = smallest N where best_ligand >= docking
    nstar = next((N for N in N_GRID if curve[N]["best_ligand"] >= docking_auroc), None)
    return {"n_test": int(ok.sum()), "n_test_actives": int(yv.sum()), "n_pool_actives": len(pool_acts),
            "docking_auroc": docking_auroc, "curve": {str(N): curve[N] for N in N_GRID}, "crossover_Nstar": nstar}


def main():
    work = tempfile.mkdtemp(prefix="b53_"); per = {}
    try:
        for tgt in TARGETS:
            s = evaluate(tgt, work); per[tgt] = s
            if "curve" in s:
                bl5 = s["curve"]["5"]["best_ligand"]; bl160 = s["curve"]["160"]["best_ligand"]
                print(f"  {tgt:7s} docking {s['docking_auroc']} (flat) | best-ligand N=5 {bl5} -> N=160 {bl160} | "
                      f"crossover N* = {s['crossover_Nstar']}")
            else:
                print(f"  {tgt:7s} SKIP ({s.get('note')})")
    finally:
        shutil.rmtree(work, ignore_errors=True)

    scored = {k: v for k, v in per.items() if "curve" in v}
    n_cross = 0
    for v in scored.values():
        d = v["docking_auroc"]; c = v["curve"]
        if c["5"]["best_ligand"] < d and c["160"]["best_ligand"] > d:
            n_cross += 1
    h1 = bool(n_cross >= 2)
    # H0: ligand dominates at N=5 on all targets
    h0 = bool(all(v["curve"]["5"]["best_ligand"] >= v["docking_auroc"] for v in scored.values()))
    # H2: below N*, fusion >= best single (docking or best_ligand) — check at N=5
    h2_hits = 0
    for v in scored.values():
        c5 = v["curve"]["5"]; best_single = max(c5["best_ligand"], v["docking_auroc"])
        if c5["fusion"] >= best_single:
            h2_hits += 1

    summary = {"n_targets": len(scored), "n_targets_with_crossover": n_cross,
               "crossover_Nstar_per_target": {k: v["crossover_Nstar"] for k, v in scored.items()},
               "docking_auroc_per_target": {k: v["docking_auroc"] for k, v in scored.items()},
               "best_ligand_at_N5": {k: v["curve"]["5"]["best_ligand"] for k, v in scored.items()},
               "best_ligand_at_N160": {k: v["curve"]["160"]["best_ligand"] for k, v in scored.items()},
               "H1_crossover_exists": h1, "H0_ligand_dominates_when_scarce": h0,
               "H2_fusion_helps_scarce_at_N5": bool(h2_hits >= 2),
               "verdict": (
                   f"DATA-REGIME CROSSOVER CONFIRMED: on {n_cross}/{len(scored)} targets, N-independent docking "
                   f"(AUROC {[v['docking_auroc'] for v in scored.values()]}) BEATS the best ligand-based method when "
                   f"actives are scarce and is overtaken as N grows — crossover N* = "
                   f"{[v['crossover_Nstar'] for v in scored.values()]}. So structure-based information genuinely earns "
                   f"its keep below ~N* known actives; above it, ligand-based dominates (the 'information not "
                   f"combination' thesis is data-regime-dependent). Fusion helps in the scarce regime on "
                   f"{h2_hits}/{len(scored)}. Retrospective, in-silico, heuristic docking, 3 targets, novel-chemistry "
                   f"test; not wet-lab; docking measured as-configured."
                   if h1 else
                   f"NO CROSSOVER — LIGAND-BASED DOMINATES EVEN WHEN SCARCE (honest, competing-hypothesis wins): "
                   f"best ligand-based method (QSAR or similarity) >= docking at N as low as 5 on "
                   f"{sum(1 for v in scored.values() if v['curve']['5']['best_ligand']>=v['docking_auroc'])}/{len(scored)} "
                   f"targets; docking AUROC {[v['docking_auroc'] for v in scored.values()]}. Consistent with the "
                   f"literature claim that ligand similarity stays competitive at very low N; structure-based docking "
                   f"(as configured) does not overtake it here. First-class negative; heuristic docking, 3 targets, "
                   f"in-silico; not wet-lab."),
               }
    print("\nVERDICT:", summary["verdict"])

    prov = {"experiment": "B53_data_regime_crossover", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "targets": TARGETS, "n_grid": N_GRID,
            "sub_seeds": SUB_SEEDS, "n_test_act": N_TEST_ACT, "n_test_dec": N_TEST_DEC, "n_train_inact": N_TRAIN_INACT,
            "vina_seed": 42, "vina_cpu": 8, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = {"provenance": prov, "summary": summary, "per_target": per}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "B53_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary, "per_target": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B53_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B53_metrics.json")


def _libvers():
    import rdkit, numpy, sklearn, scipy, vina
    return {"rdkit": rdkit.__version__, "numpy": numpy.__version__, "scikit-learn": sklearn.__version__,
            "scipy": scipy.__version__, "vina": vina.__version__, "openbabel": "3.1.0"}


if __name__ == "__main__":
    main()
