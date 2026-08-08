"""NONMET1 prep (data-generation, deterministic): fetch the fixed 12-genome panel CDS FASTAs (NCBI efetch
fasta_cds_na), translate to protein, and run mmseqs reciprocal-best-hit orthology for the two focal organisms
(E. coli, Mtb) vs the other 11 panel genomes. All outputs -> $INTERCEPTA_DATA/nonmet1/ (never committed).
run.py consumes these caches and is the unit reproduced x2. See PREREG.md for locked params.
Env: bioinfo (for mmseqs). Pure-stdlib fetch/translate."""
import os, sys, re, time, hashlib, subprocess, urllib.request

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
ND = os.path.join(DATA, "nonmet1")
GEN = os.path.join(ND, "genomes"); PROT = os.path.join(ND, "prot")
RBH = os.path.join(ND, "rbh"); TMP = os.path.join(ND, "mmseqs_tmp")
for d in (ND, GEN, PROT, RBH, TMP): os.makedirs(d, exist_ok=True)
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
LOCAL_ECOLI = os.path.join(DATA, "crispridesign1", "NC_000913.3_cds_na.fasta")

PANEL = [  # (accession, label). E. coli uses local file; others fetched.
    ("NC_000913.3", "ecoli"), ("NC_000962.3", "mtb"), ("NC_003197.2", "salmonella"),
    ("NC_002516.2", "paeruginosa"), ("NC_000964.3", "bsubtilis"), ("NC_007795.1", "saureus"),
    ("NC_000915.1", "hpylori"), ("NC_002505.1", "vcholerae"), ("NC_003112.2", "nmeningitidis"),
    ("NC_003028.3", "spneumoniae"), ("NC_016845.1", "kpneumoniae"), ("NC_011916.1", "ccrescentus"),
]
FOCALS = ["ecoli", "mtb"]

CODON = {  # standard genetic code
 'TTT':'F','TTC':'F','TTA':'L','TTG':'L','CTT':'L','CTC':'L','CTA':'L','CTG':'L','ATT':'I','ATC':'I','ATA':'I',
 'ATG':'M','GTT':'V','GTC':'V','GTA':'V','GTG':'V','TCT':'S','TCC':'S','TCA':'S','TCG':'S','CCT':'P','CCC':'P',
 'CCA':'P','CCG':'P','ACT':'T','ACC':'T','ACA':'T','ACG':'T','GCT':'A','GCC':'A','GCA':'A','GCG':'A','TAT':'Y',
 'TAC':'Y','TAA':'*','TAG':'*','CAT':'H','CAC':'H','CAA':'Q','CAG':'Q','AAT':'N','AAC':'N','AAA':'K','AAG':'K',
 'GAT':'D','GAC':'D','GAA':'E','GAG':'E','TGT':'C','TGC':'C','TGA':'*','TGG':'W','CGT':'R','CGC':'R','CGA':'R',
 'CGG':'R','AGT':'S','AGC':'S','AGA':'R','AGG':'R','GGT':'G','GGC':'G','GGA':'G','GGG':'G'}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def fetch(acc, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        return
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id="
           + acc + "&rettype=fasta_cds_na&retmode=text")
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "intercepta-nonmet1"})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            if len(data) > 1000 and data[:1] == b">":
                with open(dest, "wb") as f: f.write(data)
                return
        except Exception as e:
            sys.stderr.write(f"  fetch {acc} attempt {attempt} failed: {e}\n")
        time.sleep(3)
    raise RuntimeError(f"failed to fetch {acc}")


def translate(nt):
    nt = nt.upper().replace("\n", "")
    aa = []
    for i in range(0, len(nt) - 2, 3):
        c = nt[i:i+3]
        r = CODON.get(c, "X")
        if r == "*": break
        aa.append(r)
    return "".join(aa)


def parse_cds(path):
    """Yield (locus_tag, midpoint, protein_seq, uniprot, gene_sym) for each CDS, in file order."""
    hdr = None; seq = []
    def emit(h, s):
        lt = re.search(r"\[locus_tag=([^\]]+)\]", h)
        loc = re.search(r"\[location=([^\]]+)\]", h)
        pid = re.search(r"\[protein_id=([^\]]+)\]", h)
        gen = re.search(r"\[gene=([^\]]+)\]", h)
        up = re.search(r"UniProtKB[/A-Za-z-]*:([A-Z0-9]+)", h)
        nums = re.findall(r"\d+", loc.group(1)) if loc else []
        if not nums: return None
        mid = (int(nums[0]) + int(nums[-1])) / 2.0
        tag = lt.group(1) if lt else (pid.group(1) if pid else None)
        if tag is None: return None
        return (tag, mid, translate("".join(s)), up.group(1) if up else "", gen.group(1) if gen else "")
    with open(path, encoding="utf-8", errors="ignore") as f:
        for ln in f:
            if ln.startswith(">"):
                if hdr is not None:
                    r = emit(hdr, seq)
                    if r: yield r
                hdr = ln; seq = []
            else:
                seq.append(ln.strip())
    if hdr is not None:
        r = emit(hdr, seq)
        if r: yield r


def main():
    manifest = []
    genes = {}   # label -> list of (locus_tag, midpoint, aa, uniprot, sym) sorted by midpoint
    for acc, lab in PANEL:
        raw = LOCAL_ECOLI if lab == "ecoli" else os.path.join(GEN, f"{lab}_{acc}.fna")
        if lab != "ecoli":
            fetch(acc, raw)
        manifest.append((lab, acc, os.path.getsize(raw), sha256(raw)))
        recs = list(parse_cds(raw))
        # dedup locus_tags (keep first), sort by midpoint
        seen = set(); uniq = []
        for tag, mid, aa, up, sym in recs:
            if tag in seen:
                tag = f"{tag}__d{len(uniq)}"
            seen.add(tag)
            if len(aa) >= 20:  # drop tiny/broken translations
                uniq.append((tag, mid, aa, up, sym))
        uniq.sort(key=lambda x: x[1])
        genes[lab] = uniq
        # write protein fasta + gene table
        with open(os.path.join(PROT, f"{lab}.faa"), "w") as f:
            for tag, mid, aa, up, sym in uniq:
                f.write(f">{tag}\n{aa}\n")
        with open(os.path.join(PROT, f"{lab}.genes.tsv"), "w") as f:
            f.write("rank\tlocus_tag\tmidpoint\tuniprot\tgene\n")
            for rank, (tag, mid, aa, up, sym) in enumerate(uniq):
                f.write(f"{rank}\t{tag}\t{mid:.1f}\t{up}\t{sym}\n")
        print(f"  {lab} ({acc}): {len(uniq)} CDS proteins")
    with open(os.path.join(ND, "genome_manifest.tsv"), "w") as f:
        f.write("label\taccession\tbytes\tsha256\n")
        for lab, acc, sz, sh in manifest:
            f.write(f"{lab}\t{acc}\t{sz}\t{sh}\n")
    # mmseqs RBH: each focal vs each other panel genome
    for foc in FOCALS:
        for acc, lab in PANEL:
            if lab == foc: continue
            out = os.path.join(RBH, f"{foc}__{lab}.m8")
            if os.path.exists(out) and os.path.getsize(out) > 0:
                continue
            q = os.path.join(PROT, f"{foc}.faa"); t = os.path.join(PROT, f"{lab}.faa")
            tmp = os.path.join(TMP, f"{foc}__{lab}")
            os.makedirs(tmp, exist_ok=True)
            cmd = [MMSEQS, "easy-rbh", q, t, out, tmp, "--threads", "1",
                   "--min-seq-id", "0.30", "-c", "0.5", "--cov-mode", "0", "-e", "1e-5",
                   "--format-output", "query,target,pident,qcov,tcov,evalue,bits"]
            print("  RBH", foc, "vs", lab)
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                sys.stderr.write(r.stdout[-2000:] + "\n" + r.stderr[-2000:] + "\n")
                raise RuntimeError(f"mmseqs failed {foc} {lab}")
    print("PREP DONE")


if __name__ == "__main__":
    main()
