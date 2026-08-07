"""DARK1 build — construct the DARK set (genuinely un-analyzable proteins) and the CONTROL set (known drugged
targets), fetch all real inputs (UniProt sequences, AlphaFold structures), and run the composite's two target-ID
signals (sequence mmseqs vs drug targets; structural foldseek vs a drugged-fold reference). Everything is cached
under $INTERCEPTA_DATA/dark1/ so run.py can score deterministically and reproduce byte-identically.

DARK operationalization (two objective hard gates; PREREG.md): (1) ZERO mmseqs hits (e<=1e-3, -s 5.7) vs the
2148-protein ChEMBL drug-target reference; (2) mean AlphaFold pLDDT (mean CA B-factor) < 50 OR no model. Candidate
pool = UniProt reviewed disordered-region proteins len 50-300, sorted by accession (deterministic), hard-filtered.
CONTROL = human ChEMBL drug targets sampled deterministically, each with a usable (pLDDT>=50) AlphaFold model.

Env: bioinfo (mmseqs+foldseek). Network: UniProt REST + AlphaFold API/files. Reuses FOLD1 refstruct/ as the
drugged-fold structural reference (cached ChEMBL drug-target AlphaFold structures).
"""
import os, json, subprocess, shutil, time, urllib.request, urllib.parse

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
D = os.path.join(DATA, "dark1"); os.makedirs(D, exist_ok=True)
INT = os.path.join(DATA, "intervene")
DT_FASTA = os.path.join(INT, "drug_targets.fasta"); DT_TSV = os.path.join(INT, "drug_targets.tsv")
REFSTRUCT = os.path.join(DATA, "fold1", "refstruct")           # 403 cached drugged-target AlphaFold structures
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
FOLDSEEK = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/foldseek")
PDBDIR = os.path.join(D, "pdb"); os.makedirs(PDBDIR, exist_ok=True)

# ---- FROZEN config (PREREG.md) ----
E_SEQ = 1e-3
PLDDT_USABLE = 50.0
POOL_QUERY = ("(reviewed:true) AND (ft_region:disordered) AND (length:[50 TO 300])")
POOL_SIZE = 300           # deterministic pool, sorted by accession
N_DARK_MAX = 40
N_CONTROL = 20
N_LOWPLDDT_CANDIDATES = 55  # collect this many pLDDT<50 candidates before mmseqs-filtering to the dark set


def http_get(url, timeout=40):
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return r.read()
        except Exception:
            time.sleep(1.0)
    return None


def af_meta(acc):
    """Return (pdbUrl, mean_plddt_api) from the AlphaFold API, or (None, None) if no model."""
    b = http_get(f"https://alphafold.ebi.ac.uk/api/prediction/{acc}", timeout=30)
    if not b:
        return None, None
    try:
        d = json.loads(b)[0]
        return d.get("pdbUrl"), d.get("globalMetricValue")
    except Exception:
        return None, None


def fetch_pdb(acc):
    """Download the AlphaFold PDB (via API-resolved pdbUrl, version-agnostic). Return path or None."""
    pdb = os.path.join(PDBDIR, f"{acc}.pdb")
    if os.path.exists(pdb) and os.path.getsize(pdb) > 1000:
        return pdb
    url, _ = af_meta(acc)
    if not url:
        return None
    b = http_get(url, timeout=60)
    if not b:
        return None
    if b[:2] == b"\x1f\x8b":            # gzip magic -> decompress
        import gzip
        try:
            b = gzip.decompress(b)
        except Exception:
            return None
    if len(b) < 1000:
        return None
    open(pdb, "wb").write(b)
    return pdb


def mean_ca_plddt(pdb):
    """Mean pLDDT = mean over CA-atom B-factor column (AlphaFold stores per-residue pLDDT there)."""
    bs = [float(l[60:66]) for l in open(pdb) if l.startswith("ATOM") and l[12:16].strip() == "CA"]
    return round(sum(bs) / len(bs), 2) if bs else None


def fetch_seq(acc):
    b = http_get(f"https://rest.uniprot.org/uniprotkb/{acc}.fasta", timeout=30)
    if not b:
        return None
    lines = b.decode().splitlines()
    if not lines or not lines[0].startswith(">"):
        return None
    return "".join(lines[1:])


def build_pool():
    """Deterministic UniProt candidate pool (accession, length), sorted by accession."""
    cache = os.path.join(D, "pool.tsv")
    if os.path.exists(cache):
        return [ln.split("\t") for ln in open(cache).read().splitlines() if ln]
    q = urllib.parse.quote(POOL_QUERY)
    url = (f"https://rest.uniprot.org/uniprotkb/search?query={q}"
           f"&fields=accession,length&format=tsv&sort=accession+asc&size={POOL_SIZE}")
    b = http_get(url, timeout=60)
    rows = [ln.split("\t") for ln in b.decode().splitlines()[1:] if ln]
    open(cache, "w").write("\n".join("\t".join(r) for r in rows) + "\n")
    return rows


def sample_controls():
    """Deterministic sample of human SINGLE PROTEIN drug-target accessions (sorted-unique, fixed stride)."""
    accs = []
    seen = set()
    for ln in open(DT_TSV).read().splitlines()[1:]:
        p = ln.split("\t")
        if len(p) >= 3 and p[1] == "Homo sapiens" and p[2] == "SINGLE PROTEIN" and p[0] not in seen:
            seen.add(p[0]); accs.append(p[0])
    accs = sorted(accs)
    stride = max(1, len(accs) // 40)
    return [accs[i] for i in range(0, len(accs), stride)]  # ~40 candidates -> keep first N_CONTROL with models


def write_fasta(path, seqs):
    with open(path, "w") as f:
        for acc, s in seqs:
            f.write(f">{acc}\n{s}\n")


def run_mmseqs(query_fasta, out_m8):
    tmp = os.path.join(D, "mmtmp"); shutil.rmtree(tmp, ignore_errors=True)
    subprocess.run([MMSEQS, "easy-search", query_fasta, DT_FASTA, out_m8, tmp, "--threads", "4",
                    "-e", str(E_SEQ), "-s", "5.7", "--format-output", "query,target,pident,bits,evalue",
                    "-v", "1"], capture_output=True, text=True)
    shutil.rmtree(tmp, ignore_errors=True)


def run_foldseek(query_pdb_dir, out_m8):
    tmp = os.path.join(D, "fstmp"); shutil.rmtree(tmp, ignore_errors=True)
    r = subprocess.run([FOLDSEEK, "easy-search", query_pdb_dir, REFSTRUCT, out_m8, tmp, "--threads", "4",
                        "-e", "10", "--format-output", "query,target,bits,evalue,alntmscore"],
                       capture_output=True, text=True)
    shutil.rmtree(tmp, ignore_errors=True)
    if not os.path.exists(out_m8):
        open(out_m8, "w").write("")  # foldseek may find nothing -> empty table (all abstain), still valid
    return r


def main():
    t0 = time.time()
    print("[build] pool ...", flush=True)
    pool = build_pool()
    print(f"[build] pool size {len(pool)}", flush=True)

    # ---- collect low-pLDDT dark CANDIDATES (both gates applied after mmseqs) ----
    dark_cand = {}   # acc -> {plddt, len, seq}
    dropped_confident = []   # candidates dropped: had a CONFIDENT structure (pLDDT>=50) -> not structurally dark
    n_no_model = 0
    for acc, length in pool:
        if len(dark_cand) >= N_LOWPLDDT_CANDIDATES:
            break
        pdb = fetch_pdb(acc)
        if pdb is None:
            # no AlphaFold model at all -> structurally dark by criterion; still need a sequence for mmseqs
            seq = fetch_seq(acc)
            if seq:
                dark_cand[acc] = {"plddt": None, "len": len(seq), "seq": seq, "no_model": True}
                n_no_model += 1
            continue
        pl = mean_ca_plddt(pdb)
        if pl is None:
            continue
        if pl >= PLDDT_USABLE:
            dropped_confident.append([acc, pl]); continue
        seq = fetch_seq(acc)
        if not seq:
            continue
        dark_cand[acc] = {"plddt": pl, "len": len(seq), "seq": seq, "no_model": False}
    print(f"[build] low-pLDDT/no-model dark candidates: {len(dark_cand)} "
          f"(no_model={n_no_model}); dropped_confident_structure={len(dropped_confident)} "
          f"[{time.time()-t0:.0f}s]", flush=True)

    # mmseqs the candidates vs drug targets; DARK = candidates with ZERO hits
    cand_fasta = os.path.join(D, "dark_candidates.fasta")
    write_fasta(cand_fasta, [(a, dark_cand[a]["seq"]) for a in sorted(dark_cand)])
    cand_m8 = os.path.join(D, "dark_candidates_seqhits.m8")
    run_mmseqs(cand_fasta, cand_m8)
    hit_accs = set()
    if os.path.exists(cand_m8):
        for ln in open(cand_m8):
            p = ln.split("\t")
            if len(p) >= 5 and float(p[4]) <= E_SEQ and float(p[3]) > 0:
                hit_accs.add(p[0])
    dropped_homolog = sorted(hit_accs)  # candidates that turned out to HAVE a drugged homolog -> not dark
    dark = sorted([a for a in dark_cand if a not in hit_accs])[:N_DARK_MAX]
    print(f"[build] candidates with a drugged homolog (dropped): {len(dropped_homolog)}; "
          f"final DARK set: {len(dark)} [{time.time()-t0:.0f}s]", flush=True)

    # ---- CONTROL set ----
    ctrl = {}
    for acc in sample_controls():
        if len(ctrl) >= N_CONTROL:
            break
        pdb = fetch_pdb(acc)
        if pdb is None:
            continue
        pl = mean_ca_plddt(pdb)
        if pl is None or pl < PLDDT_USABLE:   # controls need a USABLE structure (fair structural channel)
            continue
        seq = fetch_seq(acc)
        if not seq:
            continue
        ctrl[acc] = {"plddt": pl, "len": len(seq), "seq": seq, "no_model": False}
    ctrl_accs = sorted(ctrl)
    print(f"[build] CONTROL set: {len(ctrl_accs)} [{time.time()-t0:.0f}s]", flush=True)

    # mmseqs controls vs drug targets
    ctrl_fasta = os.path.join(D, "control.fasta")
    write_fasta(ctrl_fasta, [(a, ctrl[a]["seq"]) for a in ctrl_accs])
    ctrl_m8 = os.path.join(D, "control_seqhits.m8")
    run_mmseqs(ctrl_fasta, ctrl_m8)

    # ---- structural signal: foldseek dark & control query PDBs vs drugged-fold reference ----
    for label, accs in (("dark", dark), ("control", ctrl_accs)):
        qdir = os.path.join(D, f"q_{label}"); shutil.rmtree(qdir, ignore_errors=True); os.makedirs(qdir)
        for a in accs:
            src = os.path.join(PDBDIR, f"{a}.pdb")
            if os.path.exists(src):
                shutil.copy(src, os.path.join(qdir, f"{a}.pdb"))
        run_foldseek(qdir, os.path.join(D, f"{label}_fs.m8"))
    print(f"[build] foldseek done [{time.time()-t0:.0f}s]", flush=True)

    # ---- freeze set membership + metadata ----
    sets = {
        "config": {"E_SEQ": E_SEQ, "PLDDT_USABLE": PLDDT_USABLE, "TM_HIT": 0.5,
                   "pool_query": POOL_QUERY, "pool_size": len(pool),
                   "structural_reference": "FOLD1 refstruct/ (403 cached ChEMBL drug-target AlphaFold structures)"},
        "dark": {a: {"plddt": dark_cand[a]["plddt"], "len": dark_cand[a]["len"],
                     "no_model": dark_cand[a]["no_model"]} for a in dark},
        "control": {a: {"plddt": ctrl[a]["plddt"], "len": ctrl[a]["len"], "no_model": False} for a in ctrl_accs},
        "verification": {
            "n_candidates_lowplddt_or_nomodel": len(dark_cand),
            "n_candidates_no_model": n_no_model,
            "n_dropped_confident_structure": len(dropped_confident),
            "n_dropped_has_drugged_homolog": len(dropped_homolog),
            "dropped_has_drugged_homolog": dropped_homolog,
        },
    }
    json.dump(sets, open(os.path.join(D, "sets.json"), "w"), indent=2, sort_keys=True)
    print(f"[build] DONE dark={len(dark)} control={len(ctrl_accs)} [{time.time()-t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
