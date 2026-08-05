"""FOLD1 structural-conservation NULL build — the decisive specificity test for the FOLD1 modest positive.

FOLD1 showed structure-to-reference-TARGETS discriminates isolated-pathogen targets better than sequence (AUROC
0.69 vs 0.64) and rescues 44% of sequence-blind targets. But is that SPECIFIC structural homology, or just "targets
have target-like generic folds"? (The exact critique TID1 raised for sequence conservation.) NULL: build a MATCHED
NON-TARGET structural reference (random non-target proteins from the same non-pathogen panel organisms, same size,
seeded), Foldseek each isolated-pathogen eval protein against it -> best TM to a NON-target. Then compare (run_null.py)
AUROC(TM-to-targets) vs AUROC(TM-to-nontargets). If TM-to-targets discriminates targets BETTER than TM-to-nontargets,
the structural signal is target-SPECIFIC (real). If equal, it is generic fold similarity (artifact).

Reuses the already-fetched query structures in $INTERCEPTA_DATA/fold1/q_{X}. Deterministic (seeded, disjoint from the
target reference). Env: bioinfo (foldseek). Output: $INTERCEPTA_DATA/fold1/scores_null.tsv.
"""
import os, time, random, subprocess, shutil
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
TID1 = os.path.join(DATA, "tid1")
OUT = os.path.join(DATA, "fold1"); STR = os.path.join(OUT, "struct"); os.makedirs(STR, exist_ok=True)
FOLDSEEK = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/foldseek")
PATHOGENS = ["calbicans", "pfalciparum", "tbrucei", "lmajor"]
PANEL = ["ecoli", "mtb", "paeruginosa", "bsubtilis", "hpylori", "salmonella", "efaecalis", "pfalciparum", "tbrucei", "lmajor", "calbicans"]
SEED = 42


def read_fasta(p):
    s, a, b = {}, None, []
    for ln in open(p):
        if ln.startswith(">"):
            if a: s[a] = "".join(b)
            h = ln[1:].split()[0]; a = h.split("|")[1] if "|" in h else h; b = []
        else: b.append(ln.strip())
    if a: s[a] = "".join(b)
    return s


def fetch_af(acc):
    pdb = os.path.join(STR, f"{acc}.pdb")
    if os.path.exists(pdb):
        return pdb if os.path.getsize(pdb) > 1000 else None
    subprocess.run(["curl", "-sL", "-m", "40", "-o", pdb, f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v6.pdb"], capture_output=True)
    if os.path.exists(pdb) and os.path.getsize(pdb) > 1000:
        return pdb
    if os.path.exists(pdb): os.remove(pdb)
    return None


def main():
    t0 = time.time(); random.seed(SEED)
    prot = {o: read_fasta(os.path.join(TID1, "proteomes", f"{o}.fasta")) for o in PANEL}
    targets = {o: set(x.strip() for x in open(os.path.join(TID1, "targets", f"{o}_chembl.txt")) if x.strip()) for o in PANEL}
    # size of the TARGET reference (leave-pathogen-out union) -> match the null size to it
    tref = set()
    for o in PANEL:
        if o in PATHOGENS: continue
        for a in targets[o]:
            if a in prot[o]: tref.add(a)
    n_ref = len(tref)
    # NULL reference = random NON-target proteins from the same non-pathogen panel organisms, matched size, seeded, disjoint from targets
    pool = []
    for o in PANEL:
        if o in PATHOGENS: continue
        for a in prot[o]:
            if a not in targets[o]: pool.append(a)
    random.shuffle(pool)
    # de-dup preserving order (same accession can appear across organisms rarely); take matched size
    seen = set(); nref = []
    for a in pool:
        if a in seen: continue
        seen.add(a); nref.append(a)
        if len(nref) >= n_ref: break
    print(f"target-ref size {n_ref}; null non-target-ref candidates {len(pool)} -> take {len(nref)}", flush=True)
    # fetch AF structures for the null reference
    nref_ok = []
    for i, a in enumerate(nref):
        if fetch_af(a): nref_ok.append(a)
        if (i + 1) % 50 == 0: print(f"  null-ref AF {i+1}/{len(nref)} ({len(nref_ok)} ok) [{time.time()-t0:.0f}s]", flush=True)
    nrefdir = os.path.join(OUT, "nullrefstruct"); shutil.rmtree(nrefdir, ignore_errors=True); os.makedirs(nrefdir)
    for a in nref_ok: shutil.copy(os.path.join(STR, f"{a}.pdb"), os.path.join(nrefdir, f"{a}.pdb"))
    print(f"null reference structures ready: {len(nref_ok)} [{time.time()-t0:.0f}s]", flush=True)

    # Foldseek each pathogen's already-fetched query structures vs the NULL non-target reference
    rows = []
    for X in PATHOGENS:
        qdir = os.path.join(OUT, f"q_{X}")
        if not os.path.isdir(qdir):
            print(f"  [{X}] MISSING query dir {qdir} -- rerun build.py first", flush=True); continue
        fout = os.path.join(OUT, f"fsnull_{X}.m8"); ftmp = os.path.join(OUT, f"fsnulltmp_{X}"); shutil.rmtree(ftmp, ignore_errors=True)
        subprocess.run([FOLDSEEK, "easy-search", qdir, nrefdir, fout, ftmp, "--threads", "4",
                        "--format-output", "query,target,bits,evalue,alntmscore", "-e", "10"], capture_output=True, text=True)
        sbest = {}
        if os.path.exists(fout):
            for ln in open(fout):
                p = ln.rstrip("\n").split("\t")
                if len(p) < 5: continue
                q = p[0].split(".pdb")[0]; b = float(p[2]); tm = float(p[4])
                if q not in sbest or b > sbest[q][0]: sbest[q] = (b, tm)
        # is_target label from the pdbs present in qdir (matched against the pathogen's target set)
        for fn in sorted(os.listdir(qdir)):
            if not fn.endswith(".pdb"): continue
            a = fn[:-4]; y = 1 if a in targets[X] else 0
            sb, tm = sbest.get(a, (0.0, 0.0))
            rows.append((X, a, y, sb, tm))
        print(f"  [{X}] {sum(1 for fn in os.listdir(qdir) if fn.endswith('.pdb'))} proteins; foldseek-vs-null done [{time.time()-t0:.0f}s]", flush=True)
        shutil.rmtree(ftmp, ignore_errors=True)

    with open(os.path.join(OUT, "scores_null.tsv"), "w") as f:
        f.write("pathogen\tuniprot\tis_target\tnull_struct_bits\tnull_struct_tmscore\n")
        for r in rows: f.write("\t".join(str(x) for x in r) + "\n")
    print(f"DONE {len(rows)} rows -> {os.path.join(OUT,'scores_null.tsv')} [{time.time()-t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
