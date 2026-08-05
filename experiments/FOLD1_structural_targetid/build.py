"""FOLD1 build — does STRUCTURAL homology (Foldseek) recover isolated-pathogen drug targets that SEQUENCE homology (mmseqs)
MISSES (the TID3 silent-failure ceiling)? For the phylogenetically-isolated pathogens (C. albicans fungus + parasites
P. falciparum/T. brucei/L. major), fetch AlphaFold structures for their targets + sampled non-targets and for the pooled
reference targets (other panel organisms), then compute best SEQUENCE (mmseqs) and best STRUCTURE (Foldseek) homology of
each pathogen protein to the reference targets. Caches per-protein scores. Deterministic (seeded sampling). Env: bioinfo
(mmseqs + foldseek). Output: $INTERCEPTA_DATA/fold1/scores.tsv.
"""
import os, sys, time, random, subprocess, shutil
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
TID1 = os.path.join(DATA, "tid1")
OUT = os.path.join(DATA, "fold1"); STR = os.path.join(OUT, "struct"); os.makedirs(STR, exist_ok=True)
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
FOLDSEEK = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/foldseek")
PATHOGENS = ["calbicans", "pfalciparum", "tbrucei", "lmajor"]
PANEL = ["ecoli", "mtb", "paeruginosa", "bsubtilis", "hpylori", "salmonella", "efaecalis", "pfalciparum", "tbrucei", "lmajor", "calbicans"]
N_NONTARGET = 120
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
    # eval sets: each pathogen's targets + sampled non-targets
    evalset = {}
    for X in PATHOGENS:
        tg = sorted(a for a in targets[X] if a in prot[X])
        non = sorted(a for a in prot[X] if a not in targets[X]); random.shuffle(non)
        evalset[X] = [(a, 1) for a in tg] + [(a, 0) for a in non[:N_NONTARGET]]
    # reference targets = pooled panel targets EXCLUDING each pathogen (leave-pathogen-out) -> use union excl. pathogens
    ref = set()
    for o in PANEL:
        if o in PATHOGENS: continue
        for a in targets[o]:
            if a in prot[o]: ref.add(a)
    ref = sorted(ref)
    print(f"eval: {sum(len(v) for v in evalset.values())} pathogen proteins; reference targets {len(ref)}", flush=True)
    # fetch AF structures for reference + all eval proteins
    ref_ok, seqs_ref = [], {}
    for i, a in enumerate(ref):
        if fetch_af(a): ref_ok.append(a); seqs_ref[a] = None
        if (i + 1) % 50 == 0: print(f"  ref AF {i+1}/{len(ref)} ({len(ref_ok)} ok) [{time.time()-t0:.0f}s]", flush=True)
    # reference sequences (for mmseqs)
    refseq = {}
    for o in PANEL:
        if o in PATHOGENS: continue
        for a in ref_ok:
            if a in prot[o]: refseq[a] = prot[o][a]
    # write reference structure dir (already in STR) + reference seq fasta
    refdir = os.path.join(OUT, "refstruct"); shutil.rmtree(refdir, ignore_errors=True); os.makedirs(refdir)
    for a in ref_ok: shutil.copy(os.path.join(STR, f"{a}.pdb"), os.path.join(refdir, f"{a}.pdb"))
    with open(os.path.join(OUT, "ref.fasta"), "w") as f:
        for a in ref_ok:
            if a in refseq: f.write(f">{a}\n{refseq[a]}\n")

    rows = []
    for X in PATHOGENS:
        qdir = os.path.join(OUT, f"q_{X}"); shutil.rmtree(qdir, ignore_errors=True); os.makedirs(qdir)
        qseq = {}
        got = []
        for a, y in evalset[X]:
            if fetch_af(a):
                shutil.copy(os.path.join(STR, f"{a}.pdb"), os.path.join(qdir, f"{a}.pdb"))
                qseq[a] = prot[X][a]; got.append((a, y))
        with open(os.path.join(OUT, f"q_{X}.fasta"), "w") as f:
            for a, y in got: f.write(f">{a}\n{qseq[a]}\n")
        # STRUCTURE: foldseek easy-search query structures vs reference structures
        fout = os.path.join(OUT, f"fs_{X}.m8"); ftmp = os.path.join(OUT, f"fstmp_{X}"); shutil.rmtree(ftmp, ignore_errors=True)
        subprocess.run([FOLDSEEK, "easy-search", qdir, refdir, fout, ftmp, "--threads", "4",
                        "--format-output", "query,target,bits,evalue,alntmscore", "-e", "10"], capture_output=True, text=True)
        sbest = {}
        if os.path.exists(fout):
            for ln in open(fout):
                p = ln.rstrip("\n").split("\t")
                if len(p) < 5: continue
                q = p[0].replace(".pdb", ""); q = q.split("_")[0] if False else q
                q = q.split(".pdb")[0]
                b = float(p[2]); tm = float(p[4])
                key = q
                if key not in sbest or b > sbest[key][0]: sbest[key] = (b, tm)
        # SEQUENCE: mmseqs query seqs vs reference seqs
        mout = os.path.join(OUT, f"mm_{X}.m8"); mtmp = os.path.join(OUT, f"mmtmp_{X}"); shutil.rmtree(mtmp, ignore_errors=True)
        subprocess.run([MMSEQS, "easy-search", os.path.join(OUT, f"q_{X}.fasta"), os.path.join(OUT, "ref.fasta"), mout, mtmp,
                        "--threads", "4", "-e", "1e-3", "-s", "5.7", "--format-output", "query,target,bits", "-v", "1"], capture_output=True, text=True)
        mbest = {}
        if os.path.exists(mout):
            for ln in open(mout):
                p = ln.rstrip("\n").split("\t")
                if len(p) < 3: continue
                q = p[0].split("|")[1] if "|" in p[0] else p[0]; b = float(p[2])
                if q not in mbest or b > mbest[q]: mbest[q] = b
        for a, y in got:
            qk = a  # foldseek query id is the pdb filename stem = accession
            sb, tm = sbest.get(qk, (0.0, 0.0))
            rows.append((X, a, y, mbest.get(a, 0.0), sb, tm))
        print(f"  [{X}] {len(got)} proteins ({sum(y for _,y in got)} targets); foldseek+mmseqs done [{time.time()-t0:.0f}s]", flush=True)
        shutil.rmtree(ftmp, ignore_errors=True); shutil.rmtree(mtmp, ignore_errors=True)

    with open(os.path.join(OUT, "scores.tsv"), "w") as f:
        f.write("pathogen\tuniprot\tis_target\tseq_bits\tstruct_bits\tstruct_tmscore\n")
        for r in rows: f.write("\t".join(str(x) for x in r) + "\n")
    print(f"DONE {len(rows)} rows -> {os.path.join(OUT,'scores.tsv')} [{time.time()-t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
