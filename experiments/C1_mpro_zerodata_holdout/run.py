"""C1 — Zero-data holdout on SARS-CoV-2 Mpro. Label-free structure-based screen: RDKit 3D -> obabel pdbqt ->
AutoDock Vina docking into the Mpro (6LU7) active site, using ZERO Mpro activity data. Evaluate whether Vina enrichment
recovers the 78 HELD-OUT crystallographic actives above random (Arm A), and whether a physical-validity (protein-clash)
gate improves it (Arm B). Implements prereg/C1_mpro_zerodata_holdout.md. Runs in the `docking` env.
"""
import os, sys, json, time, hashlib, subprocess, glob, math
import numpy as np
import pandas as pd
import warnings; warnings.filterwarnings("ignore")
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem
from sklearn.metrics import roc_auc_score
from scipy.stats import mannwhitneyu
RDLogger.DisableLog("rdApp.*")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
DOCK = os.path.expanduser("~/miniconda3/envs/docking/bin")
OBABEL, VINA = os.path.join(DOCK, "obabel"), os.path.join(DOCK, "vina")
REC = os.path.join(HERE, "receptor", "receptor.pdbqt")
SCR = os.path.join(HERE, "scratch"); os.makedirs(SCR, exist_ok=True)
N_INACT, SEED, EXHAUST, CLASH = 312, 42, 8, 2.0


def box():
    d = {}
    for ln in open(os.path.join(HERE, "receptor", "box.txt")):
        p = ln.split(); d[p[0]] = [float(x) for x in p[1:]]
    return d["center"], d["size"]


def receptor_heavy():
    xs = []
    for ln in open(REC):
        if ln.startswith(("ATOM", "HETATM")):
            elem = ln[76:78].strip() or ln[12:16].strip()[0]
            if not elem.startswith("H"):
                xs.append((float(ln[30:38]), float(ln[38:46]), float(ln[46:54])))
    return np.array(xs)


def prep_ligand(smi, tag):
    m = Chem.MolFromSmiles(smi)
    if m is None:
        return None
    m = Chem.AddHs(m)
    p = AllChem.ETKDGv3(); p.randomSeed = SEED
    if AllChem.EmbedMolecule(m, p) != 0:
        return None
    try:
        AllChem.MMFFOptimizeMolecule(m)
    except Exception:
        pass
    molf = os.path.join(SCR, f"{tag}.mol"); pdbqt = os.path.join(SCR, f"{tag}.pdbqt")
    Chem.MolToMolFile(m, molf)
    r = subprocess.run([OBABEL, molf, "-O", pdbqt], capture_output=True, text=True)
    return pdbqt if (os.path.exists(pdbqt) and os.path.getsize(pdbqt) > 0) else None


def dock(pdbqt, tag, c, s):
    out = os.path.join(SCR, f"{tag}_out.pdbqt")
    cmd = [VINA, "--receptor", REC, "--ligand", pdbqt, "--out", out,
           "--center_x", f"{c[0]}", "--center_y", f"{c[1]}", "--center_z", f"{c[2]}",
           "--size_x", f"{s[0]}", "--size_y", f"{s[1]}", "--size_z", f"{s[2]}",
           "--seed", f"{SEED}", "--exhaustiveness", f"{EXHAUST}", "--cpu", "4"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not os.path.exists(out):
        return None, None
    score, pose = None, []
    for ln in open(out):
        if ln.startswith("REMARK VINA RESULT") and score is None:
            score = float(ln.split()[3])
        elif ln.startswith(("ATOM", "HETATM")):
            elem = ln[76:78].strip() or ln[12:16].strip()[0]
            if not elem.startswith("H"):
                pose.append((float(ln[30:38]), float(ln[38:46]), float(ln[46:54])))
        elif ln.startswith("ENDMDL"):
            break                                                   # best pose only (model 1)
    return score, (np.array(pose) if pose else None)


def min_dist_to_receptor(pose, rec):
    if pose is None or len(pose) == 0:
        return 0.0
    d = np.sqrt(((pose[:, None, :] - rec[None, :, :]) ** 2).sum(-1))
    return float(d.min())


def bedroc(labels, scores, alpha=20.0):
    order = np.argsort(-np.asarray(scores, float)); y = np.asarray(labels)[order]
    N = len(y); n = int(y.sum())
    if n == 0 or n == N:
        return float("nan")
    ra = n / N
    ranks = np.where(y == 1)[0] + 1
    rie = (np.sum(np.exp(-alpha * ranks / N)) / n) / ((1 - math.exp(-alpha)) / (N * (math.exp(alpha / N) - 1)))
    return float(rie * (ra * math.sinh(alpha / 2)) / (math.cosh(alpha / 2) - math.cosh(alpha / 2 - alpha * ra))
                 + 1.0 / (1 - math.exp(alpha * (1 - ra))))


def ef(labels, scores, frac):
    order = np.argsort(-np.asarray(scores, float)); y = np.asarray(labels)[order]
    N = len(y); ntop = max(1, int(round(frac * N))); n = y.sum()
    return float((y[:ntop].sum() / ntop) / (n / N)) if n else float("nan")


def enrich(labels, good, tag):
    labels = np.asarray(labels)
    return {"auroc": round(float(roc_auc_score(labels, good)), 4),
            "ef1": round(ef(labels, good, 0.01), 3), "ef5": round(ef(labels, good, 0.05), 3),
            "bedroc20": round(bedroc(labels, good), 4),
            "n": int(len(labels)), "n_active": int(labels.sum())}


def main():
    t0 = time.time()
    print("=== C1: Mpro zero-data structure-based screen ===")
    df = pd.read_csv(os.path.join(DATA, "tdc_bio", "sarscov2_3clpro_diamond.tab"), sep="\t")
    df["Drug"] = df["Drug"].astype(str).str.strip('"')
    act = df[df.Y == 1]; inact = df[df.Y == 0].sample(n=N_INACT, random_state=SEED)
    cap = int(os.environ.get("C1_CAP", "0"))            # smoke-test hook: cap actives+inactives (0 = full run)
    if cap > 0:
        act = act.head(cap); inact = inact.head(cap)
    lib = pd.concat([act, inact]).reset_index(drop=True)
    print(f"library: {len(lib)} ({int(lib.Y.sum())} held-out actives + {len(inact)} inactives)")
    c, s = box(); rec = receptor_heavy()
    print(f"box center {c} size {s}; receptor heavy atoms {len(rec)}")

    rows = []
    for i, r in lib.iterrows():
        tag = f"L{i:04d}"; smi = r["Drug"]
        score, valid = None, False
        pq = prep_ligand(smi, tag)
        if pq is not None:
            score, pose = dock(pq, tag, c, s)
            if score is not None:
                valid = min_dist_to_receptor(pose, rec) >= CLASH
        rows.append({"id": int(r["Drug_ID"]), "y": int(r["Y"]),
                     "vina": (round(float(score), 3) if score is not None else None), "valid": bool(valid)})
        for f in glob.glob(os.path.join(SCR, f"{tag}*")):
            try: os.remove(f)
            except OSError: pass
        if (i + 1) % 50 == 0:
            print(f"  docked {i+1}/{len(lib)}  [{time.time()-t0:.0f}s]")

    res = pd.DataFrame(rows)
    docked = res["vina"].notna().sum()
    worst = (res["vina"].max() if docked else 0.0) + 10.0
    # goodness = -vina (higher=better); failures -> worst
    res["goodA"] = res["vina"].fillna(worst).astype(float).mul(-1.0)
    # Arm B: invalid poses pushed to the bottom
    res["goodB"] = np.where(res["valid"], res["goodA"], -(abs(worst) + 10.0))
    labels = res["y"].values
    armA = enrich(labels, res["goodA"].values, "A")
    armB = enrich(labels, res["goodB"].values, "B")
    prev = float(labels.mean())
    # score separation actives vs inactives (Arm A, docked only)
    dk = res[res["vina"].notna()]
    u = mannwhitneyu(dk[dk.y == 1]["vina"], dk[dk.y == 0]["vina"], alternative="less") if dk.y.nunique() == 2 else None
    summary = {
        "target": "SARS-CoV-2 Mpro (6LU7)", "n_library": len(res), "n_actives": int(labels.sum()),
        "n_docked": int(docked), "n_valid_pose": int(res["valid"].sum()), "active_prevalence": round(prev, 4),
        "armA_pure_vina": armA, "armB_validity_gated": armB, "random_reference_auroc": 0.5,
        "actives_vs_inactives_vina_MWU_p": (round(float(u.pvalue), 4) if u else None),
        "median_vina_active": round(float(dk[dk.y == 1]["vina"].median()), 3) if docked else None,
        "median_vina_inactive": round(float(dk[dk.y == 0]["vina"].median()), 3) if docked else None,
    }
    H1 = armA["auroc"] > 0.55 and armA["ef1"] > 1.0
    H2 = (armB["ef1"] > armA["ef1"]) or (armB["auroc"] > armA["auroc"])
    summary["H1_zero_data_recovery"] = bool(H1)
    summary["H2_validity_gate_helps"] = bool(H2)
    if H1:
        summary["verdict"] = (f"H1 TRUE: zero-data structure-based docking RECOVERS Mpro binders above random "
                              f"(AUROC {armA['auroc']}, EF1% {armA['ef1']}). "
                              + ("Validity gate helps (H2)." if H2 else "Validity gate does not add (H2 false)."))
    else:
        summary["verdict"] = (f"H0 (first-class, expected per Thread A): pure docking is ~random on this zero-data "
                              f"Mpro fragment screen (AUROC {armA['auroc']}, EF1% {armA['ef1']}); "
                              + (f"validity gating lifts it to AUROC {armB['auroc']}/EF1% {armB['ef1']} (H2)." if H2
                                 else "validity gating does not rescue it (H2 false).")
                              + " Confirms the affinity-ranking weak link; motivates homology-transfer (C2/C3).")
    print("\nPANEL:", json.dumps(summary, indent=1)); print("VERDICT:", summary["verdict"])

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "vina": EXHAUST, "receptor": "6LU7 chain A"}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "per_compound": rows, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "C1_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k: v for k, v in summary.items() if k != "verdict"}, "per_compound": rows}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "C1_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/C1_metrics.json (%.1fs)" % (time.time() - t0))


if __name__ == "__main__":
    main()
