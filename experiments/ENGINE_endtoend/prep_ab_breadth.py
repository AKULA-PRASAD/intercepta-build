"""A. baumannii conservation-breadth (REACH1 signal) for the multi-axis engine run. mmseqs the AB proteome vs the 7-panel
tagged DB (reused from the K. pneumoniae prep) -> per-AB-protein breadth (0-7 diverse bacteria with a homolog). Env: bioinfo.
"""
import os, subprocess, shutil
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
OUT = os.path.join(DATA, "engine"); MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
QF = os.path.join(DATA, "newbug2", "abaumannii.fasta"); PANEL = os.path.join(OUT, "panel_tagged.fasta")


def acc_of(h): return h.split("|")[1] if "|" in h else h


def main():
    m8 = os.path.join(OUT, "abaumannii_breadth.m8"); tmp = os.path.join(OUT, "tmpb_ab"); shutil.rmtree(tmp, ignore_errors=True)
    subprocess.run([MMSEQS, "easy-search", QF, PANEL, m8, tmp, "--threads", "4", "-e", "1e-5", "-s", "5.7",
                    "--format-output", "query,target", "-v", "1"], capture_output=True, text=True)
    breadth = {}
    if os.path.exists(m8):
        for ln in open(m8):
            p = ln.rstrip("\n").split("\t")
            if len(p) < 2: continue
            breadth.setdefault(acc_of(p[0]), set()).add(p[1].split("__")[0])
    allacc = [acc_of(ln[1:].split()[0]) for ln in open(QF) if ln.startswith(">")]
    with open(os.path.join(OUT, "abaumannii_breadth.tsv"), "w") as f:
        f.write("uniprot\tbreadth\n")
        for a in allacc: f.write(f"{a}\t{len(breadth.get(a, set()))}\n")
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"AB breadth: {len(allacc)} proteins, with>=1 homolog {sum(1 for a in allacc if breadth.get(a))}")


if __name__ == "__main__":
    main()
