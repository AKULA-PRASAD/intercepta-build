"""REACH1 build — per-gene CONSERVATION BREADTH for the E. coli proteome: across how many of the 6 other (diverse) panel
bacteria does each E. coli gene have a homolog? Core machinery (ribosome, tRNA synthetases, DNA/RNA polymerase) is
universally conserved -> high breadth; accessory genes -> low. This is a SEQUENCE-derived signal (mmseqs), so it is NOT
study-biased (the confound that killed MET4's PPI centrality). Output: $INTERCEPTA_DATA/reach1/breadth.tsv (acc, breadth 0-6).
Deterministic (fixed threads/params, cached). Env: bioinfo (mmseqs2).
"""
import os, subprocess, shutil
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
PROT = os.path.join(DATA, "tid1", "proteomes")
OUT = os.path.join(DATA, "reach1"); os.makedirs(OUT, exist_ok=True)
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
QUERY = "ecoli"
OTHERS = ["mtb", "paeruginosa", "bsubtilis", "hpylori", "salmonella", "efaecalis"]


def acc_of(header_id):
    return header_id.split("|")[1] if "|" in header_id else header_id


def main():
    # build one combined target DB with headers tagged by organism: >{org}__{acc}
    combined = os.path.join(OUT, "others_tagged.fasta")
    with open(combined, "w") as out:
        for o in OTHERS:
            for ln in open(os.path.join(PROT, f"{o}.fasta")):
                if ln.startswith(">"):
                    acc = acc_of(ln[1:].split()[0])
                    out.write(f">{o}__{acc}\n")
                else:
                    out.write(ln)
    m8 = os.path.join(OUT, "ecoli_vs_others.m8"); tmp = os.path.join(OUT, "tmp"); shutil.rmtree(tmp, ignore_errors=True)
    subprocess.run([MMSEQS, "easy-search", os.path.join(PROT, f"{QUERY}.fasta"), combined, m8, tmp,
                    "--threads", "4", "-e", "1e-5", "-s", "5.7", "--format-output", "query,target", "-v", "1"],
                   capture_output=True, text=True)
    # per E. coli query: distinct organisms among its hits
    breadth = {}
    if os.path.exists(m8):
        for ln in open(m8):
            p = ln.rstrip("\n").split("\t")
            if len(p) < 2: continue
            q = acc_of(p[0]); org = p[1].split("__")[0]
            breadth.setdefault(q, set()).add(org)
    # write breadth for ALL E. coli proteins (0 if no hit)
    all_acc = [acc_of(ln[1:].split()[0]) for ln in open(os.path.join(PROT, f"{QUERY}.fasta")) if ln.startswith(">")]
    with open(os.path.join(OUT, "breadth.tsv"), "w") as f:
        f.write("uniprot\tbreadth\n")
        for a in all_acc:
            f.write(f"{a}\t{len(breadth.get(a, set()))}\n")
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"DONE breadth for {len(all_acc)} E. coli proteins -> {os.path.join(OUT,'breadth.tsv')}; "
          f"with>=1 homolog: {sum(1 for a in all_acc if breadth.get(a))}")


if __name__ == "__main__":
    main()
