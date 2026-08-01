"""TID2 cache builder — for the evaluation set (all ChEMBL targets + seeded non-target sample per organism), fetch the
AlphaFold DB v6 structure and run fpocket, caching the max per-protein Druggability Score. Deterministic feature
extraction; output cached as data (`$INTERCEPTA_DATA/tid2/druggability.tsv`, MANIFEST'd) so the TID2 analysis (run.py)
reproduces fast. Resumable. Env: bioinfo (fpocket). Run: bioinfo python.
"""
import os, sys, subprocess, shutil, time, urllib.request
import numpy as np

DATA = os.path.join(os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data"))
TID1, TID2 = os.path.join(DATA, "tid1"), os.path.join(DATA, "tid2")
STRUCT = os.path.join(TID2, "structures"); os.makedirs(STRUCT, exist_ok=True)
FPOCKET = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/fpocket")
PANEL = ["mtb", "ecoli", "paeruginosa", "pfalciparum"]
N_NONTARGET, SEED = 400, 42
TSV = os.path.join(TID2, "druggability.tsv")


def proteome_accs(org):
    accs = []
    for ln in open(os.path.join(TID1, "proteomes", f"{org}.fasta")):
        if ln.startswith(">"):
            h = ln[1:].split()[0]; accs.append(h.split("|")[1] if "|" in h else h)
    return accs


def eval_set():
    sel = {}
    for org in PANEL:
        allp = proteome_accs(org)
        tgt = [a.strip() for a in open(os.path.join(TID1, "targets", f"{org}_chembl.txt")) if a.strip()]
        tgt = [a for a in tgt if a in set(allp)]
        non = [a for a in allp if a not in set(tgt)]
        rng = np.random.default_rng(SEED)
        nsamp = list(np.array(non)[rng.permutation(len(non))[:N_NONTARGET]])
        for a in tgt:
            sel[a] = (org, 1)
        for a in nsamp:
            sel.setdefault(a, (org, 0))
    return sel


def fetch(acc):
    p = os.path.join(STRUCT, f"{acc}.pdb")
    if os.path.exists(p) and os.path.getsize(p) > 0:
        return p
    url = f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v6.pdb"
    try:
        urllib.request.urlretrieve(url, p)
        return p if os.path.getsize(p) > 0 else None
    except Exception:
        if os.path.exists(p):
            os.remove(p)
        return None


def fpocket_max_drug(pdb, acc):
    work = os.path.join(STRUCT, f"_w_{acc}"); os.makedirs(work, exist_ok=True)
    wp = os.path.join(work, f"{acc}.pdb"); shutil.copy(pdb, wp)
    subprocess.run([FPOCKET, "-f", wp], capture_output=True, text=True)
    info = os.path.join(work, f"{acc}_out", f"{acc}_info.txt")
    best, npock = 0.0, 0
    if os.path.exists(info):
        for ln in open(info):
            if "Druggability Score" in ln:
                try:
                    v = float(ln.split(":")[1].strip()); npock += 1; best = max(best, v)
                except Exception:
                    pass
    shutil.rmtree(work, ignore_errors=True)
    return best, npock


def main():
    t0 = time.time()
    sel = eval_set()
    done = {}
    if os.path.exists(TSV):
        for ln in open(TSV):
            p = ln.rstrip("\n").split("\t")
            if len(p) >= 5 and p[0] != "accession":
                done[p[0]] = ln
    print(f"eval set: {len(sel)} proteins; already cached: {len(done)}")
    fh = open(TSV, "w")
    fh.write("accession\torganism\tis_target\tmax_druggability\tn_pockets\thas_structure\n")
    for ln in done.values():
        fh.write(ln if ln.endswith("\n") else ln + "\n")
    fh.flush()
    todo = [a for a in sel if a not in done]
    for i, acc in enumerate(todo):
        org, y = sel[acc]
        pdb = fetch(acc)
        if pdb is None:
            fh.write(f"{acc}\t{org}\t{y}\t0.0\t0\t0\n"); fh.flush(); continue
        drug, npock = fpocket_max_drug(pdb, acc)
        fh.write(f"{acc}\t{org}\t{y}\t{drug:.4f}\t{npock}\t1\n"); fh.flush()
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(todo)}  [{time.time()-t0:.0f}s]")
    fh.close()
    print(f"done: {len(sel)} proteins cached to {TSV} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
