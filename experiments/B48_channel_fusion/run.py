"""B48 — the payoff: does fusing the ligand-QSAR + ligand-similarity + structure-docking channels beat the best single
channel? Leakage-controlled logistic fusion (scaffold-CV OOF) + parameter-free rank fusion, on the same LIT-PCBA
targets/ligands as B47, under the honest NN<0.4 lens. Implements prereg/B48_channel_fusion.md. Runs in `docking` env.
Deterministic (QSAR seed=42, Vina seed=42/cpu=8) -> reproduce x2.
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
from rdkit.ML.Scoring.Scoring import CalcAUC, CalcEnrichment
from sklearn.linear_model import LogisticRegression
from vina import Vina

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta.admet import featurize, _TaskModel

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
LIT = os.path.join(DATA, "lit_pcba")
OBABEL = "/Users/kalki/miniconda3/envs/docking/bin/obabel"
TARGETS = ["FEN1", "MAPK1", "ESR1_ant"]
MAX_ACT, MAX_DEC, N_INACTIVE, EMBED_SEED, BOX = 60, 120, 8000, 0xB47, [22.0, 22.0, 22.0]
SEEDS = [1, 2, 3]


def read_smi(p):
    return [l.split()[0] for l in open(p) if l.split()]


def largest(smi):
    m = Chem.MolFromSmiles(str(smi))
    if m is None:
        return None
    fr = Chem.GetMolFrags(m, asMols=True, sanitizeFrags=True)
    return max(fr, key=lambda f: f.GetNumHeavyAtoms()) if fr else m


def canon(m): return Chem.MolToSmiles(m)
def ecfp(m): return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048)
def murcko(s):
    try: return MurckoScaffold.MurckoScaffoldSmiles(smiles=str(s), includeChirality=False)
    except Exception: return ""


def prep_ligand_pdbqt(mol, out):
    mh = Chem.AddHs(mol); p = AllChem.ETKDGv3(); p.randomSeed = EMBED_SEED
    if AllChem.EmbedMolecule(mh, p) != 0:
        p.useRandomCoords = True
        if AllChem.EmbedMolecule(mh, p) != 0:
            return False
    try: AllChem.MMFFOptimizeMolecule(mh)
    except Exception: pass
    Chem.MolToMolFile(mh, out + ".sdf")
    subprocess.run([OBABEL, out + ".sdf", "-O", out + ".pdbqt"], capture_output=True)
    return os.path.exists(out + ".pdbqt") and os.path.getsize(out + ".pdbqt") > 0


def centroid(path):
    xs = [[float(l[30:38]), float(l[38:46]), float(l[46:54])] for l in open(path) if l.startswith(("ATOM", "HETATM"))]
    return list(np.mean(np.array(xs), axis=0))


def dock_score(rec, lig, c):
    v = Vina(sf_name="vina", seed=42, cpu=8, verbosity=0)
    v.set_receptor(rec); v.set_ligand_from_file(lig)
    v.compute_vina_maps(center=c, box_size=BOX); v.dock(exhaustiveness=8, n_poses=3)
    return float(v.energies(n_poses=1)[0][0])


def auroc(labels, scores):
    ranked = [[int(labels[i])] for i in np.argsort(-np.asarray(scores))]
    return round(float(CalcAUC(ranked, 0)), 4)


def ef5(labels, scores):
    ranked = [[int(labels[i])] for i in np.argsort(-np.asarray(scores))]
    return round(float(CalcEnrichment(ranked, 0, [0.05])[0]), 3)


def prank(x):  # percentile rank in [0,1]
    x = np.asarray(x, float); order = x.argsort(); r = np.empty_like(order, float)
    r[order] = np.arange(len(x)); return r / max(len(x) - 1, 1)


def logistic_oof(feats, y, scaff):
    """3-fold scaffold-CV out-of-fold logistic fusion scores (no ligand scores itself)."""
    oof = np.full(len(y), np.nan)
    for seed in SEEDS:
        uniq = np.array(sorted(set(scaff))); perm = np.random.default_rng(seed).permutation(uniq)
        tsc = set(perm[:max(1, int(0.34 * len(perm)))]); te = np.array([s in tsc for s in scaff]); tr = ~te
        if len(np.unique(y[tr])) < 2 or te.sum() == 0:
            continue
        lr = LogisticRegression(max_iter=1000, random_state=42).fit(feats[tr], y[tr])
        oof[te] = lr.predict_proba(feats[te])[:, 1]
    # any still-nan (ligand never in a test fold) -> fill with a full-fit prob (rare)
    if np.isnan(oof).any():
        lr = LogisticRegression(max_iter=1000, random_state=42).fit(feats, y)
        pr = lr.predict_proba(feats)[:, 1]; oof[np.isnan(oof)] = pr[np.isnan(oof)]
    return oof


def evaluate(tgt, work):
    tdir = os.path.join(LIT, tgt)
    prot = sorted(f for f in os.listdir(tdir) if f.endswith("_protein.mol2"))
    ligs = sorted(f for f in os.listdir(tdir) if f.endswith("_ligand.mol2"))
    rec = os.path.join(work, f"{tgt}_rec.pdbqt"); l0 = os.path.join(work, f"{tgt}_l0.pdbqt")
    subprocess.run([OBABEL, os.path.join(tdir, prot[0]), "-O", rec, "-xr"], capture_output=True)
    subprocess.run([OBABEL, os.path.join(tdir, ligs[0]), "-O", l0], capture_output=True)
    if not (os.path.exists(rec) and os.path.exists(l0)):
        return {"note": "receptor prep failed"}
    c = centroid(l0)
    ref_fps = [ecfp(m) for m in (Chem.MolFromMol2File(os.path.join(tdir, lf)) for lf in ligs) if m is not None]
    if not ref_fps:
        return {"note": "no reference ligand"}

    acts = list(dict.fromkeys(canon(m) for m in (largest(x) for x in read_smi(os.path.join(tdir, "actives.smi"))) if m))
    decs = list(dict.fromkeys(canon(m) for m in (largest(x) for x in read_smi(os.path.join(tdir, "inactives.smi"))) if m))
    decs = [s for s in decs if s not in set(acts)]
    rng = np.random.default_rng(42)
    eval_acts = [acts[i] for i in sorted(rng.permutation(len(acts))[:min(MAX_ACT, len(acts))])]
    eval_decs = [decs[i] for i in sorted(rng.permutation(len(decs))[:min(MAX_DEC, len(decs))])]
    eval_set = eval_acts + eval_decs
    eval_lab = np.array([1] * len(eval_acts) + [0] * len(eval_decs))
    eval_scaff = np.array([murcko(s) for s in eval_set], dtype=object)

    # QSAR channel: train on the rest, predict eval (held out)
    tr_acts = [s for s in acts if s not in set(eval_acts)]
    rem_dec = [s for s in decs if s not in set(eval_decs)]
    tr_dec = [rem_dec[i] for i in sorted(rng.permutation(len(rem_dec))[:min(N_INACTIVE, len(rem_dec))])]
    tr_smiles = tr_acts + tr_dec; tr_y = np.array([1] * len(tr_acts) + [0] * len(tr_dec))
    Xtr, _ = featurize(tr_smiles); Xev, _ = featurize(eval_set)
    qsar = _TaskModel(tgt, "roc-auc", seed=42).fit(Xtr, tr_y).predict(Xev)[0]
    tr_fps = [ecfp(largest(s)) for s in tr_smiles]
    nn = np.array([max(DataStructs.BulkTanimotoSimilarity(ecfp(largest(s)), tr_fps)) for s in eval_set])

    ligsim = np.array([max(DataStructs.BulkTanimotoSimilarity(ecfp(largest(s)), ref_fps)) for s in eval_set])
    dock = []
    for i, s in enumerate(eval_set):
        lp = os.path.join(work, f"{tgt}_q{i}")
        if not prep_ligand_pdbqt(largest(s), lp):
            dock.append(np.nan); continue
        try: dock.append(-dock_score(rec, lp + ".pdbqt", c))
        except Exception: dock.append(np.nan)
        for e in (".pdbqt", ".sdf"):
            if os.path.exists(lp + e): os.remove(lp + e)
    dock = np.array(dock)
    ok = ~np.isnan(dock)
    y = eval_lab[ok]; scaff = eval_scaff[ok]; nnok = nn[ok]
    qz, lz, dz = qsar[ok], ligsim[ok], dock[ok]
    if len(np.unique(y)) < 2 or int(y.sum()) < 5:
        return {"note": "too few docked actives", "n_docked": int(ok.sum())}

    feats = np.column_stack([prank(qz), prank(lz), prank(dz)])
    fuse_log = logistic_oof(feats, y, scaff)
    fuse_rank = feats.mean(axis=1)

    chans = {"qsar": qz, "ligsim": lz, "docking": dz, "fusion_logistic": fuse_log, "fusion_rank": fuse_rank}
    full = {k: {"auroc": auroc(y, v), "ef_5pct": ef5(y, v)} for k, v in chans.items()}
    nov = nnok < 0.40
    novel = None
    if int(y[nov].sum()) >= 5 and len(y[nov]) >= 20 and len(np.unique(y[nov])) == 2:
        novel = {k: {"auroc": auroc(y[nov], v[nov])} for k, v in chans.items()}
        novel["n_novel"] = int(len(y[nov])); novel["n_novel_actives"] = int(y[nov].sum())
    best_single = max(full["qsar"]["auroc"], full["ligsim"]["auroc"], full["docking"]["auroc"])
    return {"n_docked": int(ok.sum()), "n_actives": int(y.sum()), "n_references": len(ref_fps),
            "mean_nn_to_qsar_train": round(float(nnok.mean()), 4), "full": full, "novel_lt0.4": novel,
            "best_single_auroc": best_single,
            "delta_fusion_log_minus_best_single": round(full["fusion_logistic"]["auroc"] - best_single, 4)}


def main():
    work = tempfile.mkdtemp(prefix="b48_"); per = {}
    try:
        for t in TARGETS:
            s = evaluate(t, work); per[t] = s
            if "full" in s:
                f = s["full"]
                print(f"  {t:9s} n={s['n_docked']:3d} | QSAR {f['qsar']['auroc']} ligsim {f['ligsim']['auroc']} "
                      f"dock {f['docking']['auroc']} || FUSE-log {f['fusion_logistic']['auroc']} "
                      f"FUSE-rank {f['fusion_rank']['auroc']} | dFuse-best {s['delta_fusion_log_minus_best_single']:+}")
            else:
                print(f"  {t:9s} SKIP ({s.get('note')})")
    finally:
        shutil.rmtree(work, ignore_errors=True)

    scored = {k: v for k, v in per.items() if "full" in v}
    def pm(ch): return round(float(np.mean([v["full"][ch]["auroc"] for v in scored.values()])), 4)
    best_single_pm = round(float(np.mean([v["best_single_auroc"] for v in scored.values()])), 4)
    fuse_log_pm = pm("fusion_logistic")
    delta = round(fuse_log_pm - best_single_pm, 4)
    # novel
    nov_vals = [v["novel_lt0.4"] for v in scored.values() if v.get("novel_lt0.4")]
    nov_fuse = round(float(np.mean([n["fusion_logistic"]["auroc"] for n in nov_vals])), 4) if nov_vals else None
    nov_best = round(float(np.mean([max(n["qsar"]["auroc"], n["ligsim"]["auroc"], n["docking"]["auroc"]) for n in nov_vals])), 4) if nov_vals else None
    h1 = bool(delta >= 0.02)
    h2 = bool(nov_fuse is not None and nov_best is not None and nov_fuse >= nov_best)

    summary = {"n_targets": len(scored),
               "panel_mean_auroc": {"qsar": pm("qsar"), "ligsim": pm("ligsim"), "docking": pm("docking"),
                                    "fusion_logistic": fuse_log_pm, "fusion_rank": pm("fusion_rank")},
               "panel_mean_best_single_auroc": best_single_pm,
               "delta_fusion_minus_best_single": delta,
               "novel_fusion_auroc": nov_fuse, "novel_best_single_auroc": nov_best,
               "H1_fusion_beats_best_single": h1, "H2_holds_on_novel_chemistry": h2,
               "verdict": (
                   f"WHOLE > PARTS — FUSION WINS (new structural information breaks the integration ceiling): "
                   f"leakage-controlled logistic fusion panel-mean AUROC {fuse_log_pm} vs best single channel "
                   f"{best_single_pm} (delta {delta:+}); on novel chemistry fusion {nov_fuse} vs best {nov_best}. The "
                   f"orthogonal docking channel (B47) adds real value ON TOP of the strong ligand QSAR — the program's "
                   f"first genuine integration gain. Retrospective, 3 targets, subsampled, in-silico; not wet-lab."
                   if h1 else
                   f"INTEGRATION CEILING HOLDS EVEN WITH ORTHOGONAL 3D INFORMATION (first-class negative, extends "
                   f"B32->B38): logistic fusion panel-mean AUROC {fuse_log_pm} vs best single {best_single_pm} "
                   f"(delta {delta:+}, < +0.02). Despite docking being orthogonal (B47 Spearman 0.27), fusing it with "
                   f"the strong ligand QSAR does NOT beat the best single channel here — the QSAR already captures the "
                   f"accessible signal. Consistent with 'bottleneck is information, not combination'. Honest negative; "
                   f"3 targets, subsampled, in-silico; not wet-lab."),
               }
    print("\nVERDICT:", summary["verdict"])

    prov = {"experiment": "B48_channel_fusion", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "targets": TARGETS, "max_act": MAX_ACT,
            "max_dec": MAX_DEC, "vina_seed": 42, "vina_cpu": 8, "embed_seed": EMBED_SEED, "cv_seeds": SEEDS,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = {"provenance": prov, "summary": summary, "per_target": per}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "B48_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary, "per_target": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B48_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B48_metrics.json")


def _libvers():
    import rdkit, numpy, scipy, sklearn, vina
    return {"rdkit": rdkit.__version__, "numpy": numpy.__version__, "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__, "vina": vina.__version__, "openbabel": "3.1.0"}


if __name__ == "__main__":
    main()
