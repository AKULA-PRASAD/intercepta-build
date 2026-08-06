"""HARDENV1 — CROSS-VIRUS blind structural target-class recovery (hardens GENERALIZE2/3 from n=1 to n=4 viruses).

Panel + per-virus leakage exclusions + gate FROZEN in PREREG.md before scoring. Reuses GENERALIZE3's cleaning
(longest/target protein chain; standard AAs + MSE->MET; drop ligands/ions/waters/nucleic acids) and Foldseek
TMalign (--alignment-type 1, query-normalized qtmscore). Deterministic; reproduced x2 (sha over sorted-key JSON
payload excluding verdict/provenance). Env: bioinfo (foldseek). CPU-only, open data (RCSB legacy .pdb).
"""
import os, re, json, time, hashlib, subprocess, shutil, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results")
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
H1 = os.path.join(DATA, "hardenv1")
RAW = os.path.join(H1, "raw"); QDIR = os.path.join(H1, "query_clean"); RDIR = os.path.join(H1, "ref_clean")
G3RAW = os.path.join(DATA, "generalize3", "raw")  # base-panel PDBs already cached here
FOLDSEEK = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/foldseek")

# ---------------- FROZEN query set: viral drug target -> (PDB id, correct class, virus family) ----------------
QUERY = {
    "HIV_RT":   ("1rt1", "polymerase",  "retrovirus"),
    "HIV_PR":   ("1hxw", "protease",    "retrovirus"),
    "HIV_IN":   ("1itg", "nuclease",    "retrovirus"),
    "FLU_NA":   ("2hu4", "glycosidase", "orthomyxovirus"),
    "FLU_PA":   ("4awm", "nuclease",    "orthomyxovirus"),
    "HCV_NS3":  ("1a1r", "protease",    "flavivirus"),
    "HCV_NS5B": ("4wtg", "polymerase",  "flavivirus"),
    "HSV_TK":   ("2ki5", "kinase",      "herpesvirus"),
    "HSV_POL":  ("2gv9", "polymerase",  "herpesvirus"),
}
VIRUS_OF = {"HIV_RT": "HIV-1", "HIV_PR": "HIV-1", "HIV_IN": "HIV-1", "FLU_NA": "InfluenzaA",
            "FLU_PA": "InfluenzaA", "HCV_NS3": "HCV", "HCV_NS5B": "HCV", "HSV_TK": "HSV-1", "HSV_POL": "HSV-1"}

# ---------------- FROZEN reference panel: PDB -> (class, label, viral_family_or_nonviral) ----------------
REF = {
    # base 31 (GENERALIZE3, unchanged)
    "4cha": ("protease", "chymotrypsin", "nonviral"), "1ppb": ("protease", "thrombin", "nonviral"),
    "1cqq": ("protease", "rhinovirus-3C-protease", "picornavirus"), "9pap": ("protease", "papain", "nonviral"),
    "1hxw": ("protease", "HIV-protease", "retrovirus"), "1tlp": ("protease", "thermolysin", "nonviral"),
    "4wtg": ("polymerase", "HCV-NS5B-RdRp", "flavivirus"), "3hvt": ("polymerase", "HIV-RT", "retrovirus"),
    "1kln": ("polymerase", "DNApol-Klenow", "nonviral"),
    "1m17": ("kinase", "EGFR-kinase", "nonviral"), "1hck": ("kinase", "CDK2-kinase", "nonviral"),
    "1atp": ("kinase", "PKA-kinase", "nonviral"), "2src": ("kinase", "Src-kinase", "nonviral"),
    "2rh1": ("gpcr", "beta2-GPCR", "nonviral"), "1f88": ("gpcr", "rhodopsin-GPCR", "nonviral"),
    "3eml": ("gpcr", "A2A-GPCR", "nonviral"), "1rx2": ("reductase", "DHFR", "nonviral"),
    "1hw9": ("reductase", "HMG-CoA-reductase", "nonviral"), "1vid": ("methyltransferase", "COMT-MTase", "nonviral"),
    "2adm": ("methyltransferase", "DNA-adenine-MTase", "nonviral"), "1err": ("nuclear_receptor", "estrogen-receptor", "nonviral"),
    "2prg": ("nuclear_receptor", "PPARg", "nonviral"), "1e3g": ("nuclear_receptor", "androgen-receptor", "nonviral"),
    "1bl8": ("ion_channel", "KcsA-Kchannel", "nonviral"), "7rsa": ("nuclease", "RNaseA", "nonviral"),
    "1rnb": ("nuclease", "barnase", "nonviral"), "1pjr": ("helicase", "PcrA-helicase", "nonviral"),
    "3pjr": ("helicase", "PcrA-helicase-DNA", "nonviral"), "2cba": ("lyase", "carbonic-anhydrase-II", "nonviral"),
    "1acj": ("esterase", "acetylcholinesterase", "nonviral"), "2hnp": ("phosphatase", "PTP1B-phosphatase", "nonviral"),
    # 6 additions (same-fold cross-family correct-class analogs; see PREREG)
    "2sil": ("glycosidase", "bacterial-sialidase", "nonviral"),
    "4pep": ("protease", "pepsin-aspartic", "nonviral"),
    "2ren": ("protease", "renin-aspartic", "nonviral"),
    "1rve": ("nuclease", "EcoRV-endonuclease", "nonviral"),
    "2rn2": ("nuclease", "E.coli-RNaseH", "nonviral"),
    "4ake": ("kinase", "adenylate-kinase", "nonviral"),
}

AA3 = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
       "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F",
       "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V", "MSE": "M"}


def fetch(pid):
    os.makedirs(RAW, exist_ok=True)
    dst = os.path.join(RAW, f"{pid.lower()}.pdb")
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        return dst
    cached = os.path.join(G3RAW, f"{pid.lower()}.pdb")   # reuse GENERALIZE3 cache when present
    if os.path.exists(cached) and os.path.getsize(cached) > 0:
        shutil.copy(cached, dst); return dst
    urllib.request.urlretrieve(f"https://files.rcsb.org/download/{pid.upper()}.pdb", dst)
    return dst


def parse_chains(pdb_path):
    chains = {}
    for ln in open(pdb_path, errors="replace"):
        if ln[:6] not in ("ATOM  ", "HETATM"):
            continue
        resname = ln[17:20].strip()
        if resname not in AA3:
            continue  # drops ligands, ions, waters, nucleic acids
        chain = ln[21]; resid = ln[22:27]
        chains.setdefault(chain, [])
        if not chains[chain] or chains[chain][-1][0] != resid:
            chains[chain].append([resid, resname, []])
        chains[chain][-1][2].append(ln)
    return chains


def write_longest_chain(pdb_path, out_path):
    chains = parse_chains(pdb_path)
    scored = sorted(((len(res), ch, res) for ch, res in chains.items()), key=lambda x: (-x[0], x[1]))
    nres, ch, residues = scored[0]
    with open(out_path, "w") as f:
        aserial = 1
        for resid, resname, lines in residues:
            out_resname = "MET" if resname == "MSE" else resname
            for ln in lines:
                f.write("ATOM  " + f"{aserial:5d}" + ln[11:17] + f"{out_resname:>3s}" + " A" + ln[22:])
                aserial += 1
        f.write("END\n")
    return {"chosen_chain": ch, "chain_residues": nres, "n_chains_in_file": len(chains)}


def build():
    shutil.rmtree(QDIR, ignore_errors=True); os.makedirs(QDIR)
    shutil.rmtree(RDIR, ignore_errors=True); os.makedirs(RDIR)
    qrep, rrep = {}, {}
    for name, (pid, cls, fam) in QUERY.items():
        qrep[name] = write_longest_chain(fetch(pid), os.path.join(QDIR, f"{name}.pdb"))
        qrep[name].update({"pdb": pid, "correct_class": cls, "virus_family": fam})
    for pid, (cls, lab, fam) in REF.items():
        rrep[pid] = write_longest_chain(fetch(pid), os.path.join(RDIR, f"{pid}.pdb"))
        rrep[pid].update({"class": cls, "label": lab, "family": fam})
    return qrep, rrep


def run_foldseek():
    out = os.path.join(H1, "aln.m8"); tmp = os.path.join(H1, "tmp")
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


def base(name):
    return re.sub(r"\.pdb.*$", "", os.path.basename(name))


def main():
    t0 = time.time()
    qrep, rrep = build()
    out = run_foldseek()

    # best qtmscore per (query, ref); also keep alntmscore for diagnostics
    best = {}
    for ln in open(out):
        p = ln.rstrip("\n").split("\t")
        if len(p) < 8:
            continue
        qp, rp = base(p[0]), base(p[1])
        tm, alntm, fid = float(p[2]), float(p[4]), float(p[5])
        k = (qp, rp)
        if k not in best or tm > best[k][0]:
            best[k] = (tm, alntm, fid)

    TM_BAR = 0.40
    n_classes = len(set(c for c, _, _ in REF.values()))
    per_target = {}
    n_recover = 0
    viruses_with_recovery = set()
    for name, (pid, correct_cls, fam) in QUERY.items():
        # LEAKAGE CONTROL: drop refs whose family == this virus's family
        excluded = sorted([rp for rp, (c, l, rfam) in REF.items() if rfam == fam])
        rows = [{"ref": rp, "label": REF[rp][1], "class": REF[rp][0],
                 "tm": round(best[(name, rp)][0], 3), "alntm": round(best[(name, rp)][1], 3),
                 "seq_ident": round(best[(name, rp)][2], 3)}
                for (q, rp) in best if q == name and rp not in excluded]
        rows.sort(key=lambda x: (-x["tm"], x["ref"]))
        top = rows[0] if rows else None
        correct_rows = [r for r in rows if r["class"] == correct_cls]
        offclass_rows = [r for r in rows if r["class"] != correct_cls]
        best_correct = correct_rows[0]["tm"] if correct_rows else 0.0
        best_offclass = offclass_rows[0]["tm"] if offclass_rows else 0.0
        recover = bool(top and top["class"] == correct_cls and top["tm"] >= TM_BAR)
        if recover:
            n_recover += 1; viruses_with_recovery.add(VIRUS_OF[name])
        per_target[name] = {
            "virus": VIRUS_OF[name], "query_pdb": pid, "correct_class": correct_cls,
            "predicted_class": top["class"] if top else None, "best_hit": top["label"] if top else None,
            "best_tm": top["tm"] if top else 0.0, "best_alntm": top["alntm"] if top else 0.0,
            "best_seq_ident": top["seq_ident"] if top else None,
            "best_correct_class_tm": round(best_correct, 3), "best_offclass_tm": round(best_offclass, 3),
            "offclass_win_margin": round(best_correct - best_offclass, 3),
            "RECOVER": recover, "leakage_excluded_refs": excluded, "top3": rows[:3],
        }

    n = len(QUERY)
    recovery_fraction = round(n_recover / n, 3)
    n_viruses = len(set(VIRUS_OF.values()))
    gate_pass = bool(recovery_fraction > 0.5 and len(viruses_with_recovery) >= 3)
    gate_negative = bool(n_recover <= 1)
    gate = "PASS" if gate_pass else ("NEGATIVE" if gate_negative else "PARTIAL")

    per_virus = {}
    for v in sorted(set(VIRUS_OF.values())):
        ts = [t for t in QUERY if VIRUS_OF[t] == v]
        rec = [t for t in ts if per_target[t]["RECOVER"]]
        per_virus[v] = {"targets": sorted(ts), "n_targets": len(ts), "n_recover": len(rec),
                        "recovered": sorted(rec)}

    summary = {
        "test": "HARDENV1 cross-virus blind structural target-class recovery (Foldseek TMalign, query-normalized qtmscore)",
        "method": "reuse GENERALIZE3 cleaning (longest target chain, MSE->MET, drop ligands/ions/waters/NA) + "
                  "Foldseek --alignment-type 1; per-virus family leakage exclusion applied at scoring.",
        "tm_bar": TM_BAR, "n_targets": n, "n_viruses": n_viruses,
        "reference_panel_size": len(REF), "reference_n_classes": n_classes,
        "reference_classes": sorted(set(c for c, _, _ in REF.values())),
        "random_baseline_recovery_prob": round(1.0 / n_classes, 3),
        "query_clean_report": qrep, "ref_clean_report": rrep,
        "per_target": per_target, "per_virus": per_virus,
        "n_recover": n_recover, "recovery_fraction": recovery_fraction,
        "n_viruses_with_recovery": len(viruses_with_recovery),
        "viruses_with_recovery": sorted(viruses_with_recovery),
        "n_targets_correct_class_wins_offclass": sum(1 for t in per_target.values() if t["offclass_win_margin"] > 0),
        "GATE": gate,
        "confounds": "qtmscore query-length-normalized -> very large multidomain queries (HSV_POL ~1035 res) can "
                     "score <0.40 despite a real domain match (same effect as SARS-CoV-2 spike in G3). In-silico "
                     "structural class-ID on experimental structures; not wet-lab. Coarse functional classes.",
    }
    summary["verdict"] = (
        f"CROSS-VIRUS STRUCTURAL RECOVERY ({gate}). Across {n} clinically drugged targets on {n_viruses} viruses "
        f"(HIV-1, Influenza A, HCV, HSV-1), blind Foldseek-TM vs a FROZEN {len(REF)}-structure {n_classes}-class panel "
        f"(per-virus same-family refs leakage-excluded) recovered the CORRECT drugged-enzyme class for "
        f"{n_recover}/{n} targets (fraction {recovery_fraction}) across {len(viruses_with_recovery)} viruses, "
        f"vs a ~{round(1.0/n_classes,3)} random-class baseline. "
        + {"PASS": "A MAJORITY of known viral drug targets across >=3 additional viruses recover their correct class "
                   "by structure alone, above a broad multi-class off-class baseline, with same-family analogs "
                   "excluded -> GENERALIZE3's SARS-CoV-2 result is NOT a one-off; the structural bridge is a "
                   "cross-virus property (n>1 established).",
           "PARTIAL": "Some viral targets recover correct class but not a clean majority across >=3 viruses; the "
                      "cross-virus signal is real but partial. Reported as-is, not upgraded.",
           "NEGATIVE": "Blind structural class-ID does not generalize beyond SARS-CoV-2 here (recovery at/near "
                       "random). Honest boundary of cross-virus generality."}[gate]
        + " SCOPE: in-silico structural class-ID on experimental PDB structures; not wet-lab; establishes (or bounds) "
          "cross-virus generality of the structural signal, not a deployed pipeline.")

    os.makedirs(RES, exist_ok=True)
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    payload_obj = {k: v for k, v in summary.items() if k != "verdict"}
    payload = json.dumps(payload_obj, sort_keys=True, default=str)
    sha = hashlib.sha256(payload.encode()).hexdigest()
    json.dump({"summary": summary, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)},
              open(os.path.join(RES, "HARDENV1_metrics.json"), "w"), indent=2, sort_keys=True, default=str)
    open(os.path.join(RES, "HARDENV1_payload.sha256"), "w").write(sha + "\n")

    print("=== PER-TARGET RECOVERY (best retained hit; same-family refs excluded) ===")
    for name in QUERY:
        t = per_target[name]
        flag = "RECOVER" if t["RECOVER"] else "  miss "
        print(f"  [{flag}] {name:9s} {t['virus']:11s} correct={t['correct_class']:14s} -> "
              f"best={str(t['best_hit']):22s} ({t['predicted_class']:14s}) TM={t['best_tm']:.3f} "
              f"margin(correct-off)={t['offclass_win_margin']:+.3f}")
    print(f"\nRecovery: {n_recover}/{n} targets (fraction {recovery_fraction}); "
          f"viruses with >=1 recovery: {sorted(viruses_with_recovery)}; random baseline ~{round(1.0/n_classes,3)}")
    print(f"GATE: {gate}")
    print("VERDICT:", summary["verdict"])
    print("payload sha256:", sha, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
