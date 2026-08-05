"""FRONT2 Step A — structural druggability of HOST-HOMOLOGOUS pathogen metabolic targets AND their human homologs, to test
whether a binding-site-level pathogen-vs-host difference can RESCUE the host-homologous targets E2E2's sequence filter
over-excludes. Reuses TID2's cached AF structures + druggability for the pathogen side; fetches AF + runs fpocket for the
human homologs. Scope (feasibility): all host-homologous known targets + a seeded sample of host-homologous non-targets,
Mtb + E. coli. Deterministic. Envs: bioinfo (mmseqs + fpocket). Output: $INTERCEPTA_DATA/front2/druggability.tsv.
"""
import os, time, subprocess, shutil, random
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
TID1, MET2, TID2 = os.path.join(DATA, "tid1"), os.path.join(DATA, "met2"), os.path.join(DATA, "tid2")
OUT = os.path.join(DATA, "front2"); os.makedirs(OUT, exist_ok=True)
SCR = os.path.join(OUT, "scratch"); os.makedirs(SCR, exist_ok=True)
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
FPOCKET = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/fpocket")
HUMAN = os.path.join(TID1, "proteomes", "human.fasta")
ORGS = ["mtb", "ecoli"]
N_NONTARGET_SAMPLE = 100
HOST_EVALUE = "1e-4"
SEED = 42


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
        for x in accs:
            if seqs.get(x): f.write(f">{x}\n{seqs[x]}\n")


def host_homolog(genes_fasta, tag):
    """best human homolog accession per pathogen gene (mmseqs)."""
    out = os.path.join(SCR, f"{tag}.m8"); tmp = os.path.join(SCR, f"tmp_{tag}"); shutil.rmtree(tmp, ignore_errors=True)
    subprocess.run([MMSEQS, "easy-search", genes_fasta, HUMAN, out, tmp, "--threads", "4", "-e", HOST_EVALUE,
                    "-s", "5.7", "--format-output", "query,target,bits", "-v", "1"], capture_output=True, text=True)
    best = {}
    if os.path.exists(out):
        for ln in open(out):
            p = ln.rstrip("\n").split("\t")
            if len(p) < 3: continue
            q = p[0].split("|")[1] if "|" in p[0] else p[0]
            tgt = p[1].split("|")[1] if "|" in p[1] else p[1]; b = float(p[2])
            if q not in best or b > best[q][1]: best[q] = (tgt, b)
    shutil.rmtree(tmp, ignore_errors=True)
    return {k: v[0] for k, v in best.items()}


def fetch_af(acc):
    pdb = os.path.join(SCR, f"{acc}.pdb")
    if os.path.exists(pdb) and os.path.getsize(pdb) > 1000: return pdb
    url = f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v6.pdb"
    subprocess.run(["curl", "-sL", "-m", "60", "-o", pdb, url], capture_output=True)
    return pdb if os.path.exists(pdb) and os.path.getsize(pdb) > 1000 else None


def fpocket_drug(pdb):
    """max fpocket Druggability Score over pockets (0 if none/failure)."""
    stem = os.path.splitext(os.path.basename(pdb))[0]
    outdir = os.path.join(os.path.dirname(pdb), f"{stem}_out")
    shutil.rmtree(outdir, ignore_errors=True)
    subprocess.run([FPOCKET, "-f", pdb], capture_output=True, cwd=os.path.dirname(pdb))
    info = os.path.join(outdir, f"{stem}_info.txt")
    best, npk = 0.0, 0
    if os.path.exists(info):
        for ln in open(info):
            if "Druggability Score" in ln:
                try:
                    v = float(ln.split(":")[1].strip()); npk += 1; best = max(best, v)
                except Exception: pass
    shutil.rmtree(outdir, ignore_errors=True)
    return best, npk


def main():
    t0 = time.time(); random.seed(SEED)
    # reuse TID2 pathogen druggability
    tid2 = {}
    for ln in open(os.path.join(TID2, "druggability.tsv")):
        p = ln.rstrip().split("\t")
        if p[0] == "accession": continue
        tid2[p[0]] = (float(p[3]), int(p[4]))
    ess = {}
    for ln in open(os.path.join(MET2, "essentiality.tsv")):
        p = ln.rstrip().split("\t")
        if p[0] in ORGS: ess.setdefault(p[0], {})[p[1]] = int(p[2])
    prot = {o: read_fasta(os.path.join(TID1, "proteomes", f"{o}.fasta")) for o in ORGS}
    targets = {o: set(x.strip() for x in open(os.path.join(TID1, "targets", f"{o}_chembl.txt")) if x.strip()) for o in ORGS}

    fh = open(os.path.join(OUT, "druggability.tsv"), "w")
    fh.write("organism\tuniprot\tis_target\tpath_drug\tpath_npk\thuman_acc\thuman_drug\thuman_npk\n")
    hcache = {}  # human acc -> (drug, npk)
    for X in ORGS:
        genes = [a for a in ess.get(X, {}) if a in prot[X]]
        write_fasta(prot[X], genes, os.path.join(SCR, f"{X}.fasta"))
        hh = host_homolog(os.path.join(SCR, f"{X}.fasta"), X)      # host-homologous genes only (have a human hit)
        homologous = [a for a in genes if a in hh]
        tgt = [a for a in homologous if a in targets[X]]
        non = [a for a in homologous if a not in targets[X]]
        random.shuffle(non); sample = tgt + non[:N_NONTARGET_SAMPLE]
        print(f"[{X}] {len(homologous)} host-homologous genes; scoped {len(sample)} ({len(tgt)} targets + {min(len(non),N_NONTARGET_SAMPLE)} non) [{time.time()-t0:.0f}s]", flush=True)
        for i, a in enumerate(sample):
            # pathogen druggability: reuse TID2 else fetch+fpocket
            if a in tid2:
                pd, pn = tid2[a]
            else:
                pdb = fetch_af(a); (pd, pn) = fpocket_drug(pdb) if pdb else (float("nan"), 0)
            hacc = hh[a]
            if hacc in hcache:
                hd, hn = hcache[hacc]
            else:
                hpdb = fetch_af(hacc); (hd, hn) = fpocket_drug(hpdb) if hpdb else (float("nan"), 0)
                hcache[hacc] = (hd, hn)
            ist = 1 if a in targets[X] else 0
            pd_s = "" if pd != pd else f"{pd:.4f}"; hd_s = "" if hd != hd else f"{hd:.4f}"
            fh.write(f"{X}\t{a}\t{ist}\t{pd_s}\t{pn}\t{hacc}\t{hd_s}\t{hn}\n"); fh.flush()
            if (i + 1) % 25 == 0:
                print(f"  [{X}] {i+1}/{len(sample)} [{time.time()-t0:.0f}s]", flush=True)
    fh.close()
    print(f"DONE -> {os.path.join(OUT,'druggability.tsv')} [{time.time()-t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
