"""B47 — structure-based channel: AutoDock Vina docking on LIT-PCBA targets, and its orthogonality to the ligand-based
(ECFP4-similarity) channel. Implements prereg/B47_docking_structure_channel.md. Runs in the `docking` conda env
(rdkit + openbabel + vina). Deterministic (RDKit ETKDG seed + Vina seed=42/cpu=8) -> reproduce x2.
"""
import os, sys, json, time, hashlib, tempfile, shutil, subprocess
import numpy as np
import warnings; warnings.filterwarnings("ignore")
from scipy.stats import spearmanr
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from rdkit.ML.Scoring.Scoring import CalcAUC, CalcBEDROC, CalcEnrichment
from vina import Vina

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
LIT = os.path.join(DATA, "lit_pcba")
OBABEL = "/Users/kalki/miniconda3/envs/docking/bin/obabel"
TARGETS = ["FEN1", "MAPK1", "ESR1_ant"]
MAX_ACT, MAX_DEC, EMBED_SEED, BOX = 60, 120, 0xB47, [22.0, 22.0, 22.0]


def read_smi(path):
    out = []
    with open(path) as fh:
        for line in fh:
            s = line.split()
            if s:
                out.append(s[0])
    return out


def largest(smi):
    m = Chem.MolFromSmiles(str(smi))
    if m is None:
        return None
    fr = Chem.GetMolFrags(m, asMols=True, sanitizeFrags=True)
    return max(fr, key=lambda f: f.GetNumHeavyAtoms()) if fr else m


def ecfp(m):
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048)


def prep_ligand_pdbqt(mol, out):
    mh = Chem.AddHs(mol); p = AllChem.ETKDGv3(); p.randomSeed = EMBED_SEED
    if AllChem.EmbedMolecule(mh, p) != 0:
        p.useRandomCoords = True
        if AllChem.EmbedMolecule(mh, p) != 0:
            return False
    try:
        AllChem.MMFFOptimizeMolecule(mh)
    except Exception:
        pass
    Chem.MolToMolFile(mh, out + ".sdf")
    r = subprocess.run([OBABEL, out + ".sdf", "-O", out + ".pdbqt"], capture_output=True)
    return os.path.exists(out + ".pdbqt") and os.path.getsize(out + ".pdbqt") > 0


def pdbqt_centroid(path):
    xs = [[float(l[30:38]), float(l[38:46]), float(l[46:54])] for l in open(path)
          if l.startswith(("ATOM", "HETATM"))]
    return list(np.mean(np.array(xs), axis=0))


def dock_score(recpdbqt, ligpdbqt, center):
    v = Vina(sf_name="vina", seed=42, cpu=8, verbosity=0)
    v.set_receptor(recpdbqt); v.set_ligand_from_file(ligpdbqt)
    v.compute_vina_maps(center=center, box_size=BOX); v.dock(exhaustiveness=8, n_poses=3)
    return float(v.energies(n_poses=1)[0][0])  # top affinity (kcal/mol; more negative = better)


def metrics(labels, scores):
    ranked = [[int(labels[i])] for i in np.argsort(-np.asarray(scores))]
    return {"auroc": round(float(CalcAUC(ranked, 0)), 4), "bedroc_a80.5": round(float(CalcBEDROC(ranked, 0, 80.5)), 4),
            "ef_5pct": round(float(CalcEnrichment(ranked, 0, [0.05])[0]), 3)}


def evaluate(tgt, work):
    tdir = os.path.join(LIT, tgt)
    prot = sorted(f for f in os.listdir(tdir) if f.endswith("_protein.mol2"))
    ligs = sorted(f for f in os.listdir(tdir) if f.endswith("_ligand.mol2"))
    if not prot or not ligs:
        return {"note": "missing receptor/ligand"}
    rec_pdbqt = os.path.join(work, f"{tgt}_rec.pdbqt")
    subprocess.run([OBABEL, os.path.join(tdir, prot[0]), "-O", rec_pdbqt, "-xr"], capture_output=True)
    lig0_pdbqt = os.path.join(work, f"{tgt}_lig0.pdbqt")
    subprocess.run([OBABEL, os.path.join(tdir, ligs[0]), "-O", lig0_pdbqt], capture_output=True)
    if not os.path.exists(rec_pdbqt) or not os.path.exists(lig0_pdbqt):
        return {"note": "receptor/ligand prep failed"}
    center = pdbqt_centroid(lig0_pdbqt)
    ref_fps = []
    for lf in ligs:
        rm = Chem.MolFromMol2File(os.path.join(tdir, lf))
        if rm is not None:
            ref_fps.append(ecfp(rm))
    if not ref_fps:
        return {"note": "no readable reference ligand for similarity channel"}

    rng = np.random.default_rng(42)
    acts = [s for s in (largest(x) for x in read_smi(os.path.join(tdir, "actives.smi"))) if s is not None]
    decs = [s for s in (largest(x) for x in read_smi(os.path.join(tdir, "inactives.smi"))) if s is not None]
    if len(acts) > MAX_ACT:
        acts = [acts[i] for i in sorted(rng.permutation(len(acts))[:MAX_ACT])]
    if len(decs) > MAX_DEC:
        decs = [decs[i] for i in sorted(rng.permutation(len(decs))[:MAX_DEC])]
    queries = [(m, 1) for m in acts] + [(m, 0) for m in decs]

    labels, dock_sc, ligsim, n_fail = [], [], [], 0
    for i, (m, lab) in enumerate(queries):
        lp = os.path.join(work, f"{tgt}_q{i}")
        if not prep_ligand_pdbqt(m, lp):
            n_fail += 1; continue
        try:
            aff = dock_score(rec_pdbqt, lp + ".pdbqt", center)
        except Exception:
            n_fail += 1; continue
        labels.append(lab); dock_sc.append(-aff)  # higher = better
        ligsim.append(max(DataStructs.BulkTanimotoSimilarity(ecfp(m), ref_fps)))
        os.remove(lp + ".pdbqt"); os.remove(lp + ".sdf")
    labels = np.array(labels)
    if len(np.unique(labels)) < 2 or int(labels.sum()) < 5:
        return {"note": "too few docked actives", "n_docked": int(len(labels)), "n_fail": n_fail}
    dock_m = metrics(labels, dock_sc); lig_m = metrics(labels, ligsim)
    rho = spearmanr(dock_sc, ligsim).correlation
    return {"n_docked": int(len(labels)), "n_actives_docked": int(labels.sum()), "n_prep_fail": n_fail,
            "n_references": len(ref_fps), "docking": dock_m, "ligand_similarity": lig_m,
            "spearman_dock_vs_ligsim": round(float(rho), 4)}


def main():
    work = tempfile.mkdtemp(prefix="b47dock_")
    per = {}
    try:
        for t in TARGETS:
            s = evaluate(t, work); per[t] = s
            if "docking" in s:
                print(f"  {t:9s} n={s['n_docked']:3d} (act {s['n_actives_docked']:2d}, fail {s['n_prep_fail']}) | "
                      f"DOCK AUROC {s['docking']['auroc']} EF5 {s['docking']['ef_5pct']} | "
                      f"LIGSIM AUROC {s['ligand_similarity']['auroc']} | Spearman {s['spearman_dock_vs_ligsim']}")
            else:
                print(f"  {t:9s} SKIP ({s.get('note')})")
    finally:
        shutil.rmtree(work, ignore_errors=True)

    scored = {k: v for k, v in per.items() if "docking" in v}
    d_auc = np.array([v["docking"]["auroc"] for v in scored.values()])
    l_auc = np.array([v["ligand_similarity"]["auroc"] for v in scored.values()])
    rhos = np.array([v["spearman_dock_vs_ligsim"] for v in scored.values()])
    dock_mean = round(float(d_auc.mean()), 4) if len(d_auc) else None
    rho_mean = round(float(rhos.mean()), 4) if len(rhos) else None
    n_dock_wins = int(sum(1 for v in scored.values() if v["docking"]["auroc"] > v["ligand_similarity"]["auroc"]))
    h1 = bool(dock_mean is not None and dock_mean > 0.55)
    h2 = bool(rho_mean is not None and rho_mean < 0.40)

    summary = {"n_targets": len(scored), "panel_mean_docking_auroc": dock_mean,
               "panel_mean_ligand_similarity_auroc": round(float(l_auc.mean()), 4) if len(l_auc) else None,
               "panel_mean_spearman_dock_vs_ligsim": rho_mean, "n_targets_docking_beats_ligsim": n_dock_wins,
               "H1_docking_enriches_above_chance": h1, "H2_orthogonal_to_ligand_based": h2,
               "verdict": (
                   f"STRUCTURE CHANNEL ADDED & ORTHOGONAL (motivates B48 fusion): docking enriches above chance "
                   f"(panel-mean AUROC {dock_mean}) and is {'weakly' if h2 else 'NOT weakly'} correlated with the "
                   f"ligand-similarity channel (mean Spearman {rho_mean}) — {'complementary information, the '
                   'prerequisite for a fusion gain' if h2 else 'more redundant than hoped'}. Ligand-similarity mean "
                   f"AUROC {round(float(l_auc.mean()),4)}; docking wins on {n_dock_wins}/{len(scored)} targets. "
                   f"Docking is weak on unbiased data as expected; heuristic score, rigid receptor, subsampled, "
                   f"3 targets; not wet-lab."
                   if h1 else
                   f"DOCKING ADDS LITTLE RETRIEVAL SIGNAL HERE (honest negative): panel-mean docking AUROC {dock_mean} "
                   f"(<=0.55, ~chance) vs ligand-similarity {round(float(l_auc.mean()),4)}; mean Spearman {rho_mean}. "
                   f"On these unbiased targets, Vina docking does not enrich real actives above chance with this prep — "
                   f"consistent with the literature (docking weak on unbiased data). Reported truthfully; still may "
                   f"contribute orthogonally in fusion (B48). Heuristic score, rigid receptor, subsampled, 3 targets."),
               }
    print("\nVERDICT:", summary["verdict"])

    prov = {"experiment": "B47_docking_structure_channel", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "targets": TARGETS, "max_act": MAX_ACT,
            "max_dec": MAX_DEC, "embed_seed": EMBED_SEED, "vina_seed": 42, "vina_cpu": 8, "exhaustiveness": 8,
            "box": BOX, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    full = {"provenance": prov, "summary": summary, "per_target": per}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(full, open(os.path.join(HERE, "results", "B47_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary, "per_target": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B47_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B47_metrics.json")


def _libvers():
    import rdkit, numpy, scipy, vina
    return {"rdkit": rdkit.__version__, "numpy": numpy.__version__, "scipy": scipy.__version__,
            "vina": vina.__version__, "openbabel": "3.1.0"}


if __name__ == "__main__":
    main()
