"""HIT2 Step A — dock the MoleculeACE CHEMBL204 (thrombin) TEST set into the thrombin pocket with ZERO activity data.
RDKit ETKDG 3D + MMFF -> obabel pdbqt -> AutoDock Vina 1.2.7 (seed 42, exhaustiveness 16). Deterministic. Writes a
regenerable cache: $INTERCEPTA_DATA/hit2/thrombin_vina.tsv (idx, active, pact, vina, smiles). Run in the `docking` env.
"""
import os, csv, sys, time, subprocess
from rdkit import Chem
from rdkit.Chem import AllChem

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
HIT2 = os.path.join(DATA, "hit2")
MACE = os.path.join(DATA, "hit1", "moleculeace", "CHEMBL204_Ki.csv")
DOCK = os.path.expanduser("~/miniconda3/envs/docking/bin")
OBABEL, VINA = os.path.join(DOCK, "obabel"), os.path.join(DOCK, "vina")
REC, CONF = os.path.join(HIT2, "receptor.pdbqt"), os.path.join(HIT2, "vina.conf")
SCR = os.path.join(HIT2, "scratch"); os.makedirs(SCR, exist_ok=True)
OUT = os.path.join(HIT2, "thrombin_vina.tsv")
SEED, EXHAUST, ACT_CUT = 42, 16, 6.5


def prep(smi, tag):
    m = Chem.MolFromSmiles(smi)
    if m is None: return None
    m = Chem.AddHs(m)
    p = AllChem.ETKDGv3(); p.randomSeed = SEED
    if AllChem.EmbedMolecule(m, p) != 0: return None
    try: AllChem.MMFFOptimizeMolecule(m)
    except Exception: pass
    molf = os.path.join(SCR, f"{tag}.mol"); pq = os.path.join(SCR, f"{tag}.pdbqt")
    Chem.MolToMolFile(m, molf)
    subprocess.run([OBABEL, molf, "-O", pq, "-p", "7.4"], capture_output=True, text=True)
    return pq if os.path.exists(pq) and os.path.getsize(pq) > 0 else None


def dock(pq, tag):
    out = os.path.join(SCR, f"{tag}_out.pdbqt")
    r = subprocess.run([VINA, "--receptor", REC, "--ligand", pq, "--config", CONF, "--out", out,
                        "--seed", str(SEED), "--exhaustiveness", str(EXHAUST), "--cpu", "4"],
                       capture_output=True, text=True)
    for ln in r.stdout.splitlines():
        s = ln.split()
        if len(s) == 4 and s[0] == "1":
            try: return float(s[1])
            except ValueError: return None
    return None


def main():
    t0 = time.time()
    rows = [r for r in csv.DictReader(open(MACE)) if r["split"] == "test"]
    done = {}
    if os.path.exists(OUT):
        for ln in open(OUT):
            p = ln.rstrip("\n").split("\t")
            if p[0] != "idx" and len(p) >= 4: done[int(p[0])] = True
    mode = "a" if done else "w"
    fh = open(OUT, mode)
    if not done: fh.write("idx\tactive\tpact\tvina\tsmiles\n")
    print(f"docking {len(rows)} thrombin test compounds ({len(done)} already cached)", flush=True)
    for i, r in enumerate(rows):
        if i in done: continue
        smi = r["smiles"]; pact = float(r["y [pEC50/pKi]"]); act = int(pact >= ACT_CUT)
        pq = prep(smi, f"lig{i}")
        v = dock(pq, f"lig{i}") if pq else None
        fh.write(f"{i}\t{act}\t{pact:.4f}\t{'' if v is None else round(v,3)}\t{smi}\n"); fh.flush()
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{len(rows)}  [{time.time()-t0:.0f}s]", flush=True)
    fh.close()
    print(f"DONE {len(rows)} compounds [{time.time()-t0:.0f}s] -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
