"""ENGINE demo prep — builds the two on-the-fly inputs the unified DiscoveryEngine needs for the held-out K. pneumoniae
demonstration: (1) conservation-BREADTH across the 7 diverse panel bacteria (REACH1 signal), (2) a reference-target FASTA
= the known ChEMBL drug-target sequences of the OTHER panel organisms (for the ConservationProvider, leave-pathogen-out).
Deterministic. Env: bioinfo (mmseqs). Reuses existing proteomes/targets; nothing committed.
"""
import os, subprocess, shutil
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
PROT = os.path.join(DATA, "tid1", "proteomes"); TGT = os.path.join(DATA, "tid1", "targets")
OUT = os.path.join(DATA, "engine"); os.makedirs(OUT, exist_ok=True)
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
PATHOGEN = "kpneumoniae"
PATHOGEN_FASTA = os.path.join(DATA, "newbug", "kpneumoniae.fasta")
PANEL = ["ecoli", "mtb", "paeruginosa", "bsubtilis", "hpylori", "salmonella", "efaecalis"]


def acc_of(h): return h.split("|")[1] if "|" in h else h


def build_breadth():
    combined = os.path.join(OUT, "panel_tagged.fasta")
    with open(combined, "w") as out:
        for o in PANEL:
            for ln in open(os.path.join(PROT, f"{o}.fasta")):
                if ln.startswith(">"): out.write(f">{o}__{acc_of(ln[1:].split()[0])}\n")
                else: out.write(ln)
    m8 = os.path.join(OUT, f"{PATHOGEN}_breadth.m8"); tmp = os.path.join(OUT, "tmpb"); shutil.rmtree(tmp, ignore_errors=True)
    subprocess.run([MMSEQS, "easy-search", PATHOGEN_FASTA, combined, m8, tmp, "--threads", "4", "-e", "1e-5",
                    "-s", "5.7", "--format-output", "query,target", "-v", "1"], capture_output=True, text=True)
    breadth = {}
    if os.path.exists(m8):
        for ln in open(m8):
            p = ln.rstrip("\n").split("\t")
            if len(p) < 2: continue
            breadth.setdefault(acc_of(p[0]), set()).add(p[1].split("__")[0])
    allacc = [acc_of(ln[1:].split()[0]) for ln in open(PATHOGEN_FASTA) if ln.startswith(">")]
    with open(os.path.join(OUT, f"{PATHOGEN}_breadth.tsv"), "w") as f:
        f.write("uniprot\tbreadth\n")
        for a in allacc: f.write(f"{a}\t{len(breadth.get(a, set()))}\n")
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"breadth: {len(allacc)} proteins, with>=1 homolog {sum(1 for a in allacc if breadth.get(a))}")


def build_reference_targets():
    ref = os.path.join(OUT, "reference_targets.fasta"); n = 0
    with open(ref, "w") as out:
        for o in PANEL:                                            # leave-pathogen-out: PATHOGEN not in PANEL anyway
            tf = os.path.join(TGT, f"{o}_chembl.txt")
            if not os.path.exists(tf): continue
            tgt_accs = set(x.strip() for x in open(tf) if x.strip())
            seqs, acc, buf = {}, None, []
            for ln in open(os.path.join(PROT, f"{o}.fasta")):
                if ln.startswith(">"):
                    if acc and acc in tgt_accs: seqs[acc] = "".join(buf)
                    acc = acc_of(ln[1:].split()[0]); buf = []
                else: buf.append(ln.strip())
            if acc and acc in tgt_accs: seqs[acc] = "".join(buf)
            for a, s in seqs.items():
                out.write(f">{o}__{a}\n{s}\n"); n += 1
    print(f"reference targets: {n} sequences -> {ref}")


if __name__ == "__main__":
    build_breadth(); build_reference_targets()
