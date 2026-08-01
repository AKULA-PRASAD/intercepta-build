"""E2E1 — zero-data END-TO-END discovery on M. tuberculosis. Composes the validated capabilities into one pipeline
from PROTEOME to a ranked candidate shortlist, using ZERO TB activity data:
  target-ID (conservation x fpocket druggability x host-nonhomology, leave-Mtb-out)  -> pick top druggable known target
  -> its fpocket pocket becomes the Vina box  -> dock a ChEMBL screening library (C1-style)  -> + ADMET + synth
  -> ranked, provenance/confidence-tiered shortlist.
Capability-COMPOSITION demonstration (NOT a discovery claim; output = hypotheses, not validated hits).
Implements prereg/E2E1_pathogen_endtoend.md. Orchestrator env: intercepta-build (calls mmseqs/fpocket/obabel/vina bins).
"""
import os, sys, json, time, hashlib, subprocess, shutil, glob
import numpy as np
import pandas as pd
import warnings; warnings.filterwarnings("ignore")
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem
RDLogger.DisableLog("rdApp.*")
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.abspath(os.path.join(HERE, "..", "..")), "src"))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
TID1, TID2 = os.path.join(DATA, "tid1"), os.path.join(DATA, "tid2")
BIO = os.path.expanduser("~/miniconda3/envs/bioinfo/bin"); MMSEQS, FPOCKET = f"{BIO}/mmseqs", f"{BIO}/fpocket"
DOCK = os.path.expanduser("~/miniconda3/envs/docking/bin"); OBABEL, VINA = f"{DOCK}/obabel", f"{DOCK}/vina"
SCR = os.path.join(HERE, "scratch")
OTHERS = ["ecoli", "paeruginosa", "pfalciparum"]        # leave-Mtb-out reference organisms
LIB_N, SEED, EXHAUST = 120, 42, 8


def read_fasta(p):
    seqs, a, b = {}, None, []
    for ln in open(p):
        if ln.startswith(">"):
            if a: seqs[a] = "".join(b)
            h = ln[1:].split()[0]; a = h.split("|")[1] if "|" in h else h; b = []
        else: b.append(ln.strip())
    if a: seqs[a] = "".join(b)
    return seqs


def write_fasta(seqs, accs, path):
    with open(path, "w") as f:
        for a in accs:
            if seqs.get(a): f.write(f">{a}\n{seqs[a]}\n")


def best_bits(qf, tf, tag):
    out = os.path.join(SCR, f"{tag}.m8"); tmp = os.path.join(SCR, f"tmp_{tag}"); shutil.rmtree(tmp, ignore_errors=True)
    subprocess.run([MMSEQS, "easy-search", qf, tf, out, tmp, "--threads", "4", "-e", "1e-3", "-s", "5.7",
                    "--format-output", "query,target,bits", "-v", "1"], capture_output=True, text=True)
    best = {}
    if os.path.exists(out):
        for ln in open(out):
            p = ln.rstrip("\n").split("\t")
            if len(p) < 3: continue
            q = p[0].split("|")[1] if "|" in p[0] else p[0]; v = float(p[2])
            if q not in best or v > best[q]: best[q] = v
    shutil.rmtree(tmp, ignore_errors=True)
    return best


def zscore(x):
    x = np.asarray(x, float); s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0.0


def fpocket_box(pdb, acc):
    work = os.path.join(SCR, f"fp_{acc}"); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    wp = os.path.join(work, f"{acc}.pdb"); shutil.copy(pdb, wp)
    subprocess.run([FPOCKET, "-f", wp], capture_output=True, text=True)
    info = os.path.join(work, f"{acc}_out", f"{acc}_info.txt")
    best_n, best_d, cur = None, -1.0, None
    if os.path.exists(info):
        for ln in open(info):
            s = ln.strip()
            if s.lower().startswith("pocket"):
                cur = int(s.split()[1])
            elif "Druggability Score" in s and cur is not None:
                d = float(s.split(":")[1]);
                if d > best_d: best_d, best_n = d, cur
    if best_n is None:
        shutil.rmtree(work, ignore_errors=True); return None
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
    t0 = time.time()
    shutil.rmtree(SCR, ignore_errors=True); os.makedirs(SCR, exist_ok=True)
    from intercepta.discover import DiscoveryPipeline
    print("=== E2E1: zero-data end-to-end on M. tuberculosis ===")

    # ---------- STAGE 1: target-ID (conservation x druggability x host-nonhomology, leave-Mtb-out) ----------
    dtab = pd.read_csv(os.path.join(TID2, "druggability.tsv"), sep="\t")
    dm = dtab[dtab.organism == "mtb"].copy()
    mtb_seqs = read_fasta(os.path.join(TID1, "proteomes", "mtb.fasta"))
    eval_acc = [a for a in dm.accession if a in mtb_seqs]
    write_fasta(mtb_seqs, eval_acc, os.path.join(SCR, "mtb_eval.fasta"))
    # reference: OTHER organisms' known targets (leave-Mtb-out) + human proteome (selectivity)
    ot_seqs, ot_acc = {}, []
    for o in OTHERS:
        op = read_fasta(os.path.join(TID1, "proteomes", f"{o}.fasta"))
        for a in (x.strip() for x in open(os.path.join(TID1, "targets", f"{o}_chembl.txt")) if x.strip()):
            if a in op: ot_seqs[a] = op[a]; ot_acc.append(a)
    write_fasta(ot_seqs, ot_acc, os.path.join(SCR, "othertgt.fasta"))
    human = read_fasta(os.path.join(TID1, "proteomes", "human.fasta")); write_fasta(human, list(human), os.path.join(SCR, "human.fasta"))
    cons = best_bits(os.path.join(SCR, "mtb_eval.fasta"), os.path.join(SCR, "othertgt.fasta"), "cons")
    hum = best_bits(os.path.join(SCR, "mtb_eval.fasta"), os.path.join(SCR, "human.fasta"), "hum")
    dm = dm.set_index("accession").loc[eval_acc].reset_index()
    dm["cons"] = [cons.get(a, 0.0) for a in dm.accession]
    dm["hum"] = [hum.get(a, 0.0) for a in dm.accession]
    dm["composite"] = zscore(dm["cons"]) + zscore(dm["max_druggability"]) - zscore(dm["hum"])   # selectivity penalty
    y = dm["is_target"].values
    k = int(y.sum())
    order = np.argsort(-dm["composite"].values)
    prec_at_k = float(y[order][:k].sum() / k)
    prec_cons = float(y[np.argsort(-dm["cons"].values)][:k].sum() / k)
    auroc_comp = float(roc_auc_score(y, dm["composite"])) if 0 < y.sum() < len(y) else float("nan")
    # PICK target: top composite among known druggable targets with structure
    cand = dm[(dm.is_target == 1) & (dm.has_structure == 1)].sort_values("composite", ascending=False)
    chosen = cand.iloc[0]["accession"]
    print(f"target-ID: {len(dm)} Mtb proteins, {k} known targets; precision@k composite {prec_at_k:.3f} vs "
          f"conservation {prec_cons:.3f}; AUROC {auroc_comp:.3f}. CHOSEN target: {chosen} "
          f"(druggability {cand.iloc[0]['max_druggability']}) [{time.time()-t0:.0f}s]")

    # ---------- STAGE 2: pocket -> box (front->back bridge) ----------
    struct = os.path.join(TID2, "structures", f"{chosen}.pdb")
    box = fpocket_box(struct, chosen)
    print(f"pocket: {box}")
    # receptor pdbqt
    prot_only = os.path.join(SCR, "prot.pdb")
    with open(prot_only, "w") as f:
        for ln in open(struct):
            if ln.startswith("ATOM"): f.write(ln)
        f.write("TER\n")
    rec = os.path.join(SCR, "receptor.pdbqt")
    subprocess.run([OBABEL, prot_only, "-O", rec, "-xr", "-p", "7.4"], capture_output=True, text=True)

    # ---------- STAGE 3: dock a ChEMBL screening library ----------
    lib = pd.read_csv(os.path.join(DATA, "tdc_gen", "chembl.tab"), sep="\t")
    col = "smiles" if "smiles" in lib.columns else lib.columns[-1]
    smis = lib[col].dropna().sample(LIB_N, random_state=SEED).tolist()
    smis = [Chem.MolToSmiles(m) for m in (Chem.MolFromSmiles(s) for s in smis) if m is not None]
    print(f"docking {len(smis)} library compounds into {chosen} pocket ...")
    vina = {}
    for i, s in enumerate(smis):
        tag = f"L{i:03d}"; pq = prep_ligand(s, tag)
        vina[s] = dock(pq, tag, rec, box) if pq else None
        for f in glob.glob(os.path.join(SCR, f"{tag}*")):
            try: os.remove(f)
            except OSError: pass
        if (i + 1) % 40 == 0: print(f"  docked {i+1}/{len(smis)} [{time.time()-t0:.0f}s]")

    # ---------- STAGE 4: multi-channel (ADMET safety + synth) ----------
    print("fitting ADMET(hERG/AMES/DILI) + synthesizability ...")
    pipe = DiscoveryPipeline.from_default(seed=SEED)
    prof = pipe.profile(smis)                                   # QED, synth, per-tox, safety, AD, developability_F
    prof = prof.set_index("smiles")

    # ---------- STAGE 5: ranked, tiered candidate shortlist ----------
    rows = []
    for s in smis:
        if s not in prof.index or vina.get(s) is None: continue
        r = prof.loc[s]
        v = float(vina[s])
        rows.append({"smiles": s, "vina_kcal_mol": round(v, 2),
                     "predicted_safety": float(r["predicted_safety"]), "qed": float(r["qed"]),
                     "synth_solvable_prob": float(r["synth_solvable_prob"]),
                     "applicability_domain": r["applicability_domain"]})
    df = pd.DataFrame(rows)
    # candidate score: docking (more negative better) gated by safety*synth; rank ascending vina among developable
    df["cand_score"] = (-df["vina_kcal_mol"]) * df["predicted_safety"] * df["synth_solvable_prob"]
    df = df.sort_values("cand_score", ascending=False).reset_index(drop=True)
    df["confidence_tier"] = np.where(df["applicability_domain"].astype(str).str.startswith("in-domain"),
                                     "reliable-ADMET (docking pose-plausible hypothesis)", "LOW (out-of-domain)")
    df.to_csv(os.path.join(HERE, "results", "E2E1_shortlist.csv"), index=False) if os.path.isdir(os.path.join(HERE, "results")) else None
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    df.to_csv(os.path.join(HERE, "results", "E2E1_shortlist.csv"), index=False)

    shortlist = [{k2: (round(v2, 4) if isinstance(v2, float) else v2) for k2, v2 in rec.items()}
                 for rec in df.head(20).to_dict("records")]
    summary = {
        "kind": "capability-composition demonstration (NOT a discovery claim)",
        "pathogen": "Mycobacterium tuberculosis", "zero_tb_activity_data": True,
        "targetID_n_proteins": len(dm), "targetID_n_known_targets": k,
        "targetID_precAtk_composite": round(prec_at_k, 4), "targetID_precAtk_conservation": round(prec_cons, 4),
        "targetID_auroc_composite": round(auroc_comp, 4),
        "chosen_target": chosen, "chosen_target_druggability": round(float(cand.iloc[0]["max_druggability"]), 3),
        "pocket_box": box, "library_size": len(smis), "n_docked": int(df.shape[0]),
        "shortlist_top": shortlist,
        "scope": ("Composition demo; output = ranked COMPUTATIONAL HYPOTHESES, not validated hits. Target-ID is "
                  "conservation-dominated (TID1/TID2). Docking weak at the top (C1). ADMET/synth are disease-agnostic "
                  "transfers. Generic screening library (not curated TB actives). Zero TB activity data. No wet-lab.")}
    print("\nPANEL:", json.dumps({k2: v for k2, v in summary.items() if k2 != "shortlist_top"}, indent=1))
    print(f"top candidate: {shortlist[0]['smiles'] if shortlist else 'none'} "
          f"(vina {shortlist[0]['vina_kcal_mol'] if shortlist else '-'})")

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = {"summary": summary, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "E2E1_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({k2: v for k2, v in summary.items() if k2 != "scope"}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "E2E1_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/E2E1_metrics.json (%.1fs)" % (time.time() - t0))


if __name__ == "__main__":
    main()
