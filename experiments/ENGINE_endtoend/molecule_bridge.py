"""ENGINE molecule bridge — closes the pipeline SHAPE to end-to-end: genome -> (validated) TARGET -> candidate MOLECULES.
Takes a top VALIDATED target from the DiscoveryEngine's held-out K. pneumoniae shortlist (dxs, A6T5F3 — the engine's
#1-ranked EXPERIMENTALLY-essential target), detects its pocket (fpocket on the AlphaFold structure), docks a ChEMBL
screening library (AutoDock Vina), and annotates each candidate with ADMET/synthesizability + applicability-domain
(the shipped, validated modules). Ranks by a developability-gated docking score. Reuses the E2E1 pipeline verbatim.

HONEST SCOPE (loud, per C1/HIT2/B44): docking is a heuristic score, NOT binding free energy; early-enrichment is weak
(C1 AUROC 0.63; HIT2 shows docking is useless for within-series potency); zero target activity data is used; the library
is a generic ChEMBL sample, not curated actives; outputs are POSE-PLAUSIBLE candidate HYPOTHESES, not validated actives,
not drugs. This demonstrates the pipeline's end-to-end SHAPE with the molecule half's real ceiling stated, not hidden.
Deterministic (seeded). Envs: rdkit/admet (intercepta-build) + fpocket (bioinfo) + obabel/vina (docking).
"""
import os, sys, time, json, hashlib, shutil, subprocess
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
SCR = os.path.join(DATA, "engine", "scratch_mol");
BIO = os.path.expanduser("~/miniconda3/envs/bioinfo/bin"); FPOCKET = f"{BIO}/fpocket"
DOCK = os.path.expanduser("~/miniconda3/envs/docking/bin"); OBABEL, VINA = f"{DOCK}/obabel", f"{DOCK}/vina"
SEED, EXHAUST, LIB_N = 42, 8, 60
TARGET_ACC, TARGET_GENE = "A6T5F3", "dxs"   # engine top-ranked experimentally-essential K. pneumoniae target


def fpocket_box(pdb, acc):
    work = os.path.join(SCR, f"fp_{acc}"); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    wp = os.path.join(work, f"{acc}.pdb"); shutil.copy(pdb, wp)
    subprocess.run([FPOCKET, "-f", wp], capture_output=True, text=True)
    info = os.path.join(work, f"{acc}_out", f"{acc}_info.txt")
    best_n, best_d, cur = None, -1.0, None
    if os.path.exists(info):
        for ln in open(info):
            s = ln.strip()
            if s.lower().startswith("pocket"): cur = int(s.split()[1])
            elif "Druggability Score" in s and cur is not None:
                d = float(s.split(":")[1])
                if d > best_d: best_d, best_n = d, cur
    if best_n is None: shutil.rmtree(work, ignore_errors=True); return None
    vert = os.path.join(work, f"{acc}_out", "pockets", f"pocket{best_n}_vert.pqr")
    pts = [(float(l[30:38]), float(l[38:46]), float(l[46:54])) for l in open(vert) if l.startswith(("ATOM", "HETATM"))]
    P = np.array(pts); c = P.mean(0); size = np.clip(P.max(0) - P.min(0) + 8.0, 16, 26)
    shutil.rmtree(work, ignore_errors=True)
    return {"center": [round(float(x), 3) for x in c], "size": [round(float(x), 3) for x in size],
            "druggability": round(best_d, 3), "pocket": best_n}


def prep_ligand(smi, tag):
    m = Chem.MolFromSmiles(smi)
    if m is None: return None
    m = Chem.AddHs(m); p = AllChem.ETKDGv3(); p.randomSeed = SEED
    if AllChem.EmbedMolecule(m, p) != 0: return None
    try: AllChem.MMFFOptimizeMolecule(m)
    except Exception: pass
    molf = os.path.join(SCR, f"{tag}.mol"); pq = os.path.join(SCR, f"{tag}.pdbqt")
    Chem.MolToMolFile(m, molf); subprocess.run([OBABEL, molf, "-O", pq], capture_output=True, text=True)
    return pq if (os.path.exists(pq) and os.path.getsize(pq) > 0) else None


def dock(pq, tag, rec, box):
    out = os.path.join(SCR, f"{tag}_out.pdbqt"); c, s = box["center"], box["size"]
    subprocess.run([VINA, "--receptor", rec, "--ligand", pq, "--out", out,
                    "--center_x", f"{c[0]}", "--center_y", f"{c[1]}", "--center_z", f"{c[2]}",
                    "--size_x", f"{s[0]}", "--size_y", f"{s[1]}", "--size_z", f"{s[2]}",
                    "--seed", f"{SEED}", "--exhaustiveness", f"{EXHAUST}", "--cpu", "4"], capture_output=True, text=True)
    if os.path.exists(out):
        for ln in open(out):
            if ln.startswith("REMARK VINA RESULT"): return float(ln.split()[3])
    return None


def main():
    t0 = time.time(); shutil.rmtree(SCR, ignore_errors=True); os.makedirs(SCR, exist_ok=True)
    import pandas as pd
    from intercepta.discover import DiscoveryPipeline
    struct = os.path.join(DATA, "engine", "struct", f"{TARGET_ACC}.pdb")
    print(f"=== ENGINE molecule bridge: K. pneumoniae {TARGET_GENE} ({TARGET_ACC}) ===")
    box = fpocket_box(struct, TARGET_ACC); print("pocket box:", box)
    prot_only = os.path.join(SCR, "prot.pdb")
    with open(prot_only, "w") as f:
        for ln in open(struct):
            if ln.startswith("ATOM"): f.write(ln)
        f.write("TER\n")
    rec = os.path.join(SCR, "receptor.pdbqt")
    subprocess.run([OBABEL, prot_only, "-O", rec, "-xr", "-p", "7.4"], capture_output=True, text=True)
    # library
    lib = pd.read_csv(os.path.join(DATA, "tdc_gen", "chembl.tab"), sep="\t")
    col = "smiles" if "smiles" in lib.columns else lib.columns[-1]
    smis = lib[col].dropna().sample(LIB_N, random_state=SEED).tolist()
    smis = [Chem.MolToSmiles(m) for m in (Chem.MolFromSmiles(s) for s in smis) if m is not None]
    print(f"docking {len(smis)} compounds into {TARGET_GENE} pocket ...")
    vina = {}
    for i, s in enumerate(smis):
        pq = prep_ligand(s, f"lig{i}")
        vina[s] = dock(pq, f"lig{i}", rec, box) if pq else None
        if (i + 1) % 20 == 0: print(f"  docked {i+1}/{len(smis)} [{time.time()-t0:.0f}s]", flush=True)
    # ADMET/synth annotation via the shipped validated pipeline
    pipe = DiscoveryPipeline.from_default()
    prof = pipe.profile(smis).set_index("smiles")
    rows = []
    for s in smis:
        if vina.get(s) is None: continue
        row = {"smiles": s, "vina_kcal_mol": round(float(vina[s]), 2)}
        if s in prof.index:
            for c2 in ("predicted_safety", "synth_solvable_prob", "qed", "in_domain"):
                if c2 in prof.columns:
                    row[c2] = bool(prof.loc[s, c2]) if c2 == "in_domain" else float(prof.loc[s, c2])
        rows.append(row)
    df = pd.DataFrame(rows)
    if "predicted_safety" in df and "synth_solvable_prob" in df:
        df["cand_score"] = (-df["vina_kcal_mol"]) * df["predicted_safety"].fillna(0.5) * df["synth_solvable_prob"].fillna(0.5)
    else:
        df["cand_score"] = -df["vina_kcal_mol"]
    df = df.sort_values("cand_score", ascending=False).reset_index(drop=True)
    top = df.head(10).to_dict("records")
    summary = {"target_gene": TARGET_GENE, "target_acc": TARGET_ACC, "pocket_box": box,
               "library_size": len(smis), "n_docked": int(df.shape[0]),
               "best_vina_kcal_mol": float(df["vina_kcal_mol"].min()) if len(df) else None,
               "top_candidates": top,
               "honest_scope": ("Docking is a heuristic score, NOT binding free energy; early-enrichment is weak (C1 AUROC "
                                "0.63; HIT2: useless for within-series potency); ZERO target activity data used; generic ChEMBL "
                                "library, not curated actives; outputs are POSE-PLAUSIBLE candidate HYPOTHESES, not validated "
                                "actives, not drugs. Demonstrates the end-to-end SHAPE (genome->target->molecule) with the "
                                "molecule-half ceiling stated. Not wet-lab.")}
    print("\nTOP CANDIDATES (vina | safety | synth | cand_score):")
    for r in top[:5]:
        print(f"  vina {r['vina_kcal_mol']:+.2f}  safety {r.get('predicted_safety','-')}  "
              f"synth {r.get('synth_solvable_prob','-')}  score {r['cand_score']:.3f}")
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump({"summary": summary, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)},
              open(os.path.join(HERE, "results", "ENGINE_molecule_bridge.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({k: v for k, v in summary.items() if k != "honest_scope"}, sort_keys=True)
    open(os.path.join(HERE, "results", "ENGINE_molbridge_payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    print("\npayload sha256:", hashlib.sha256(payload.encode()).hexdigest(), f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
