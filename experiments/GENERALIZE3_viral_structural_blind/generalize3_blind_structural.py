"""GENERALIZE3 — BLIND structural generalization test (unbiased version GENERALIZE2 left gated).

Reference panel + gate are FROZEN in PREREG.md before this runs. See PREREG for rationale.
Deterministic; reproduced x2 (sha over sorted-key JSON of the metrics payload, excluding verdict/provenance).
Env: bioinfo (foldseek). CPU-only, open data (RCSB legacy .pdb).
"""
import os, re, json, time, math, hashlib, subprocess, shutil, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results")
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
G3 = os.path.join(DATA, "generalize3")
RAW = os.path.join(G3, "raw"); QDIR = os.path.join(G3, "query_clean"); RDIR = os.path.join(G3, "ref_clean")
FOLDSEEK = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/foldseek")
FASTA = os.path.join(DATA, "generalize1", "mature_proteins.fasta")

# --- FROZEN query source PDBs (protein -> PDB id) ---
QUERY_PDB = {
    "nsp1": "7K3N", "nsp2": "7MSW", "nsp3_PLpro": "6W9C", "nsp5_Mpro": "6LU7",
    "nsp7": "7BV2", "nsp8": "7BV2", "nsp9": "6W4B", "nsp10": "6ZCT", "nsp12_RdRp": "7BV2",
    "nsp13": "6ZSL", "nsp14": "7N0B", "nsp15": "6VWW", "nsp16": "6W4H",
    "spike": "6VXX", "E": "7K3G", "M": "8CTK", "N": "6M3M", "ORF3a": "6XDC",
    "ORF7a": "6W37", "ORF8": "7JTL", "ORF9b": "6Z4U",
}
# map protein -> unique substring in its FASTA header (to fetch its known sequence)
QUERY_HDR = {
    "nsp1": "Host-translation-inhibitor-nsp1", "nsp2": "Non-structural-protein-2",
    "nsp3_PLpro": "Papain-like-protease", "nsp5_Mpro": "3C-like-proteinase",
    "nsp7": "Non-structural-protein-7", "nsp8": "Non-structural-protein-8",
    "nsp9": "RNA-capping-enzyme", "nsp10": "Non-structural-protein-10",
    "nsp12_RdRp": "RNA-directed-RNA-polymerase", "nsp13": "Helicase",
    "nsp14": "Guanine-N7-methyltransferase", "nsp15": "endoribonuclease",
    "nsp16": "2'-O-methyltransferase", "spike": "Spike-glycoprotein",
    "E": "Envelope-small-membrane", "M": "Membrane-protein", "N": "Nucleoprotein",
    "ORF3a": "ORF3a", "ORF7a": "ORF7a", "ORF8": "ORF8-protein", "ORF9b": "ORF9b",
}
# proteins in the 30-proteome with NO experimental structure sought (documented excluded)
NO_STRUCTURE = ["nsp4", "nsp6", "ORF3b", "ORF6", "ORF7b", "ORF9c", "ORF10", "ORF3c", "ORF3d"]

# --- FROZEN reference panel (PDB id -> class) ---
REF_CLASS = {
    "4cha": "protease", "1ppb": "protease", "1cqq": "protease", "9pap": "protease",
    "1hxw": "protease", "1tlp": "protease",
    "4wtg": "polymerase", "3hvt": "polymerase", "1kln": "polymerase",
    "1m17": "kinase", "1hck": "kinase", "1atp": "kinase", "2src": "kinase",
    "2rh1": "gpcr", "1f88": "gpcr", "3eml": "gpcr",
    "1rx2": "reductase", "1hw9": "reductase",
    "1vid": "methyltransferase", "2adm": "methyltransferase",
    "1err": "nuclear_receptor", "2prg": "nuclear_receptor", "1e3g": "nuclear_receptor",
    "1bl8": "ion_channel",
    "7rsa": "nuclease", "1rnb": "nuclease",
    "1pjr": "helicase", "3pjr": "helicase",
    "2cba": "lyase", "1acj": "esterase", "2hnp": "phosphatase",
}
REF_LABEL = {
    "4cha": "chymotrypsin", "1ppb": "thrombin", "1cqq": "rhinovirus-3C-protease", "9pap": "papain",
    "1hxw": "HIV-protease", "1tlp": "thermolysin", "4wtg": "HCV-NS5B-RdRp", "3hvt": "HIV-RT",
    "1kln": "DNApol-Klenow", "1m17": "EGFR-kinase", "1hck": "CDK2-kinase", "1atp": "PKA-kinase",
    "2src": "Src-kinase", "2rh1": "beta2-GPCR", "1f88": "rhodopsin-GPCR", "3eml": "A2A-GPCR",
    "1rx2": "DHFR", "1hw9": "HMG-CoA-reductase", "1vid": "COMT-MTase", "2adm": "DNA-adenine-MTase",
    "1err": "estrogen-receptor", "2prg": "PPARg", "1e3g": "androgen-receptor", "1bl8": "KcsA-Kchannel",
    "7rsa": "RNaseA", "1rnb": "barnase", "1pjr": "PcrA-helicase", "3pjr": "PcrA-helicase-DNA",
    "2cba": "carbonic-anhydrase-II", "1acj": "acetylcholinesterase", "2hnp": "PTP1B-phosphatase",
}

AA3 = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
       "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F",
       "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V", "MSE": "M"}


def fetch(pid):
    os.makedirs(RAW, exist_ok=True)
    dst = os.path.join(RAW, f"{pid.lower()}.pdb")
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        return dst
    url = f"https://files.rcsb.org/download/{pid}.pdb"
    urllib.request.urlretrieve(url, dst)
    return dst


def parse_chains(pdb_path):
    """Return {chain: [(resseq_icode, resname, [lines])]} preserving order, protein residues only."""
    chains = {}
    for ln in open(pdb_path):
        rec = ln[:6]
        if rec not in ("ATOM  ", "HETATM"):
            continue
        resname = ln[17:20].strip()
        if resname not in AA3:
            continue  # drops ligands, ions, waters, nucleic acids
        chain = ln[21]
        resid = (ln[22:27])  # resseq + icode
        chains.setdefault(chain, [])
        if not chains[chain] or chains[chain][-1][0] != resid:
            chains[chain].append([resid, resname, []])
        chains[chain][-1][2].append(ln)
    return chains


def chain_seq(residues):
    return "".join(AA3.get(r[1], "X") for r in residues)


def kmer_overlap(a, b, k=5):
    if len(a) < k or len(b) < k:
        return 0.0
    sa = set(a[i:i + k] for i in range(len(a) - k + 1))
    sb = set(b[i:i + k] for i in range(len(b) - k + 1))
    if not sa:
        return 0.0
    return len(sa & sb) / len(sa)


def write_chain(residues, out_path, newchain="A"):
    with open(out_path, "w") as f:
        aserial = 1
        for resid, resname, lines in residues:
            for ln in lines:
                out_resname = "MET" if resname == "MSE" else resname
                rec = "ATOM  "  # normalize MSE HETATM -> ATOM
                # rebuild columns: keep original but force ATOM record + chain A + resname
                newln = rec + f"{aserial:5d}" + ln[11:17] + f"{out_resname:>3s}" + " " + newchain + ln[22:]
                f.write(newln)
                aserial += 1
        f.write("END\n")


def load_query_seqs():
    seqs = {}
    hdr = None
    buf = []
    recs = {}
    for ln in open(FASTA):
        if ln.startswith(">"):
            if hdr is not None:
                recs[hdr] = "".join(buf)
            hdr = ln[1:].strip(); buf = []
        else:
            buf.append(ln.strip())
    if hdr is not None:
        recs[hdr] = "".join(buf)
    for prot, sub in QUERY_HDR.items():
        match = [v for h, v in recs.items() if sub in h]
        if not match:
            raise SystemExit(f"FASTA header not found for {prot} (substr {sub})")
        seqs[prot] = match[0]
    return seqs


def build_queries(qseqs):
    shutil.rmtree(QDIR, ignore_errors=True); os.makedirs(QDIR)
    report = {}
    for prot, pid in QUERY_PDB.items():
        pdb = fetch(pid)
        chains = parse_chains(pdb)
        target = qseqs[prot]
        scored = []
        for ch, residues in chains.items():
            cs = chain_seq(residues)
            ov = kmer_overlap(target, cs)
            scored.append((ov, len(residues), ch, residues))
        scored.sort(key=lambda x: (-x[0], -x[1], x[2]))
        best = scored[0]
        write_chain(best[3], os.path.join(QDIR, f"{prot}.pdb"))
        report[prot] = {"pdb": pid, "chosen_chain": best[2], "chain_residues": best[1],
                        "kmer_overlap": round(best[0], 3), "n_chains_in_file": len(chains)}
    return report


def build_refs():
    shutil.rmtree(RDIR, ignore_errors=True); os.makedirs(RDIR)
    report = {}
    for pid in REF_CLASS:
        pdb = fetch(pid)
        chains = parse_chains(pdb)
        scored = sorted(((len(res), ch, res) for ch, res in chains.items()), key=lambda x: (-x[0], x[1]))
        best = scored[0]
        write_chain(best[2], os.path.join(RDIR, f"{pid}.pdb"))
        report[pid] = {"class": REF_CLASS[pid], "label": REF_LABEL[pid],
                       "chosen_chain": best[1], "chain_residues": best[0]}
    return report


def run_foldseek():
    out = os.path.join(G3, "aln.m8"); tmp = os.path.join(G3, "tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    if os.path.exists(out):
        os.remove(out)
    r = subprocess.run([FOLDSEEK, "easy-search", QDIR, RDIR, out, tmp, "--alignment-type", "1",
                        "-e", "10", "-s", "9.5", "--max-seqs", "2000", "--threads", "4",
                        "--format-output", "query,target,qtmscore,ttmscore,alntmscore,fident,evalue,alnlen",
                        "-v", "1"], capture_output=True, text=True)
    if not os.path.exists(out):
        print("STDERR:", r.stderr[-3000:]); raise SystemExit("foldseek produced no output")
    shutil.rmtree(tmp, ignore_errors=True)
    return out


def pid_of(name):
    b = os.path.basename(name)
    return re.sub(r"\.pdb.*$", "", b)


def main():
    t0 = time.time()
    qseqs = load_query_seqs()
    qrep = build_queries(qseqs)
    rrep = build_refs()
    out = run_foldseek()

    # best (max qtmscore) per (viral_protein, ref_pdb)
    best = {}
    for ln in open(out):
        p = ln.rstrip("\n").split("\t")
        if len(p) < 8:
            continue
        qp = pid_of(p[0]); rp = pid_of(p[1]); tm = float(p[2]); fid = float(p[5]); ev = float(p[6])
        k = (qp, rp)
        if k not in best or tm > best[k][0]:
            best[k] = (tm, fid, ev)

    structured = list(QUERY_PDB.keys())
    per_prot = {}
    for qp in structured:
        rows = [{"ref": rp, "label": REF_LABEL[rp], "class": REF_CLASS[rp],
                 "tm": round(best[(qp, rp)][0], 3), "seq_ident": round(best[(qp, rp)][1], 3),
                 "evalue": best[(qp, rp)][2]} for (q, rp) in best if q == qp]
        rows.sort(key=lambda x: (-x["tm"], x["ref"]))
        top = rows[0] if rows else None
        per_prot[qp] = {"best_tm": top["tm"] if top else 0.0,
                        "best_class": top["class"] if top else None,
                        "best_label": top["label"] if top else None,
                        "best_seq_ident": top["seq_ident"] if top else None,
                        "top3": rows[:3]}

    # ranking by best_tm
    ranking = sorted(structured, key=lambda q: (-per_prot[q]["best_tm"], q))
    n = len(structured)
    topk = math.ceil(n / 2)
    rank_pos = {q: i + 1 for i, q in enumerate(ranking)}

    mp = per_prot["nsp5_Mpro"]; rd = per_prot["nsp12_RdRp"]
    G1 = bool(mp["best_class"] == "protease" and mp["best_tm"] >= 0.40)
    G2 = bool(rd["best_class"] == "polymerase" and rd["best_tm"] >= 0.40)
    G3g = bool(rank_pos["nsp5_Mpro"] <= topk and rank_pos["nsp12_RdRp"] <= topk)
    gate = "PASS" if (G1 and G2 and G3g) else ("PARTIAL" if (G1 or G2) else "FAIL")

    ranked_table = [{"rank": rank_pos[q], "protein": q, "source_pdb": QUERY_PDB[q],
                     "best_tm": per_prot[q]["best_tm"], "best_class": per_prot[q]["best_class"],
                     "best_label": per_prot[q]["best_label"], "best_seq_ident": per_prot[q]["best_seq_ident"]}
                    for q in ranking]

    summary = {
        "test": "GENERALIZE3 BLIND structural target-prioritization (Foldseek TMalign, query-normalized qtmscore)",
        "coverage_n_structured": n, "coverage_total_proteome": 30,
        "proteins_no_structure_excluded": NO_STRUCTURE,
        "reference_panel_size": len(REF_CLASS),
        "reference_classes": sorted(set(REF_CLASS.values())),
        "query_clean_report": qrep,
        "ref_clean_report": rrep,
        "ranked_table_by_best_tm": ranked_table,
        "nsp5_Mpro": {"rank": rank_pos["nsp5_Mpro"], "best": mp["best_label"], "class": mp["best_class"],
                      "tm": mp["best_tm"], "seq_ident": mp["best_seq_ident"], "top3": mp["top3"]},
        "nsp12_RdRp": {"rank": rank_pos["nsp12_RdRp"], "best": rd["best_label"], "class": rd["best_class"],
                       "tm": rd["best_tm"], "seq_ident": rd["best_seq_ident"], "top3": rd["top3"]},
        "secondary_nsp3_PLpro": {"rank": rank_pos["nsp3_PLpro"], "best": per_prot["nsp3_PLpro"]["best_label"],
                                 "class": per_prot["nsp3_PLpro"]["best_class"], "tm": per_prot["nsp3_PLpro"]["best_tm"]},
        "secondary_nsp13_helicase": {"rank": rank_pos["nsp13"], "best": per_prot["nsp13"]["best_label"],
                                     "class": per_prot["nsp13"]["best_class"], "tm": per_prot["nsp13"]["best_tm"]},
        "topk_halfway": topk,
        "G1_nsp5_protease_TM>=0.4": G1,
        "G2_nsp12_polymerase_TM>=0.4": G2,
        "G3_both_in_top_half": G3g,
        "GATE": gate,
        "confound": "Only structured subset ranked; proteins without experimental PDB are excluded. "
                    "qtmscore is query-normalized (large multidomain queries can score low). n=1 virus.",
    }
    summary["verdict"] = (
        f"BLIND STRUCTURAL TEST ({gate}). Coverage {n}/30 SARS-CoV-2 mature proteins had a usable cleaned "
        f"experimental structure. Against an UNBIASED {len(REF_CLASS)}-structure corona-free panel spanning "
        f"{len(set(REF_CLASS.values()))} drug-target classes, nsp5/Mpro's best drugged-analog was "
        f"{mp['best_label']} (class {mp['best_class']}, TM {mp['best_tm']}, rank {rank_pos['nsp5_Mpro']}/{n}); "
        f"nsp12/RdRp's was {rd['best_label']} (class {rd['best_class']}, TM {rd['best_tm']}, "
        f"rank {rank_pos['nsp12_RdRp']}/{n}). "
        + {"PASS": "Structure BLINDLY recovers the correct drugged fold+class for BOTH approved targets from a "
                   "broad unbiased panel, exactly where sequence gave zero (GENERALIZE1) and without hand-picked "
                   "controls (unlike GENERALIZE2). The viral-generalization failure is a sequence-tool limitation.",
           "PARTIAL": "Exactly one approved target blindly recovers its correct class at TM>=0.4 (or both do but "
                      "one falls below the top-half rank gate). Reported as-is, not upgraded.",
           "FAIL": "Neither approved target blindly recovers its correct drugged class at TM>=0.4 from the "
                   "unbiased panel. Honest negative: blind structural prioritization does not point at the right "
                   "viral intervention targets here."}[gate]
        + " SCOPE: in-silico target prioritization on structured subset only; not wet-lab; n=1 virus; "
          "establishes the principle, not a deployed pipeline.")

    os.makedirs(RES, exist_ok=True)
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    payload_obj = {k: v for k, v in summary.items() if k != "verdict"}
    payload = json.dumps(payload_obj, sort_keys=True, default=str)
    sha = hashlib.sha256(payload.encode()).hexdigest()
    json.dump({"summary": summary, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)},
              open(os.path.join(RES, "GENERALIZE3_metrics.json"), "w"), indent=2, sort_keys=True, default=str)
    open(os.path.join(RES, "GENERALIZE3_payload.sha256"), "w").write(sha + "\n")

    print("=== RANKED TABLE (by best drugged-analog TM) ===")
    for r in ranked_table:
        star = " <== APPROVED TARGET" if r["protein"] in ("nsp5_Mpro", "nsp12_RdRp") else ""
        print(f"  #{r['rank']:2d} {r['protein']:12s} ({r['source_pdb']}) best={str(r['best_label']):24s} "
              f"class={str(r['best_class']):16s} TM={r['best_tm']}{star}")
    print(f"\nCoverage: {n}/30 structured. topK(half)={topk}")
    print(f"G1 nsp5->protease TM>=0.4: {G1} | G2 nsp12->polymerase TM>=0.4: {G2} | G3 both top-half: {G3g}")
    print(f"GATE: {gate}")
    print("VERDICT:", summary["verdict"])
    print("payload sha256:", sha, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
