"""STRUCTREPURPOSE1 — structural drug repurposing vs the INTERVENE1 sequence baseline, with a
mandatory organism-matched NULL / promiscuity guard. See PREREG.md (frozen gates).

Stages (all cached on disk so reproduce-x2 scores identical inputs):
  1. Fetch AlphaFold (v6) structures for the 2148 ChEMBL drug-target accessions -> drug-target Foldseek ref.
  2. Fetch AF structures for E. coli canonical antibacterial targets (VALIDATION) + N. gonorrhoeae's
     32 FBA-essential targets (COVERAGE).
  3. Build an organism-composition-matched RANDOM NON-drug-target reference of the same size (NULL).
  4. Foldseek TMalign: queries vs drug-target ref, and N. gonorrhoeae queries vs random ref.
  5. Score G1 (MoA recovery), G2 (expansion beyond 1/32), and the null guard. Print sha over payload.

Env: bioinfo (foldseek). CPU-only, open data. Deterministic. NEVER commits.
"""
import os, re, sys, json, time, random, hashlib, subprocess, shutil, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results")
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
INT = os.path.join(DATA, "intervene")
SR = os.path.join(DATA, "structrepurpose1")
DT_PDB = os.path.join(SR, "dt_pdb"); QEC = os.path.join(SR, "q_ecoli_pdb")
QNG = os.path.join(SR, "q_ngono_pdb"); RAND_PDB = os.path.join(SR, "rand_pdb")
CACHE = os.path.join(SR, "cache"); FS = os.path.join(SR, "fs")
for d in (DT_PDB, QEC, QNG, RAND_PDB, CACHE, FS, RES): os.makedirs(d, exist_ok=True)
FOLDSEEK = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/foldseek")
DT_FASTA = os.path.join(INT, "drug_targets.fasta"); DT_TSV = os.path.join(INT, "drug_targets.tsv")
NGONO_FASTA = os.path.join(DATA, "blind1", "ngono.fasta")
ECOLI_FASTA = os.path.join(DATA, "tid1", "proteomes", "ecoli.fasta")
LOCKED = os.path.join(HERE, "..", "BLIND1_ngonorrhoeae", "results", "LOCKED_predictions.tsv")
# The 32 BLIND1 essential accessions (A0ACH0F*, proteome UP001163151) are NOT in AlphaFold DB (too recent).
# They are mapped (mmseqs, pident>=90 & qcov>=0.8; achieved 98.7-100%) to their AF-covered orthologs in the
# N. gonorrhoeae FA 1090 reference proteome (UP000000535, taxid 242231). Structures = those orthologs.
FA1090_FASTA = os.path.join(SR, "fa1090.fasta")
ESS_MAP = os.path.join(SR, "ess_to_fa1090.json")  # orig_acc -> fa1090_acc

TM_THRESH = 0.50; TM_SENS = [0.40, 0.50, 0.60]; SEED = 1234
AF_URL = "https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v6.pdb"

# E. coli canonical antibacterial targets: gene -> (UniProt acc, expected MoA keyword) [keywords per INTERVENE1 CANON]
ECOLI_CANON = {
    "folA": ("P0ABQ4", "dihydrofolate"), "folP": ("P0AC13", "dihydropteroate"),
    "murA": ("P0A749", "carboxyvinyltransferase"), "gyrA": ("P0AES4", "gyrase"),
    "gyrB": ("P0AES6", "gyrase"), "parC": ("P0AFI2", "topoisomerase"),
    "parE": ("P20083", "topoisomerase"), "rpoB": ("P0A8V2", "rna polymerase"),
    "alr": ("P0A6B4", "alanine racemase"), "ddlB": ("P07862", "d-ala"),
    "dxr": ("P45568", "reductoisomerase"),
}
STOP = set("protein subunit chain type putative uncharacterized family domain factor alpha beta gamma "
           "delta small large 1 2 3 4 i ii iii iv a b c d and of the".split())


# ---------------- fetching ----------------
def af_fetch(acc, dst_dir):
    dst = os.path.join(dst_dir, f"{acc}.pdb")
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        return (acc, True)
    for _ in range(3):
        try:
            req = urllib.request.Request(AF_URL.format(acc=acc), headers={"User-Agent": "structrepurpose1"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            if data and data[:4] != b"<?xm" and len(data) > 200:
                open(dst, "wb").write(data); return (acc, True)
            return (acc, False)
        except urllib.error.HTTPError as e:
            if e.code == 404: return (acc, False)
            time.sleep(0.5)
        except Exception:
            time.sleep(0.5)
    return (acc, False)


def fetch_many(accs, dst_dir, tag, workers=24):
    ok = set()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for i, (acc, good) in enumerate(ex.map(lambda a: af_fetch(a, dst_dir), accs)):
            if good: ok.add(acc)
            if (i + 1) % 200 == 0: print(f"  [{tag}] {i+1}/{len(accs)} fetched, ok={len(ok)}", flush=True)
    print(f"  [{tag}] DONE {len(ok)}/{len(accs)} structures present", flush=True)
    return ok


# ---------------- fasta / drug parsing ----------------
def parse_fasta_headers(path):
    """acc -> {'taxid':..., 'gene':..., 'desc':...}"""
    out = {}
    for ln in open(path):
        if not ln.startswith(">"): continue
        acc = ln[1:].split()[0].split("|")[1] if "|" in ln else ln[1:].split()[0]
        tax = re.search(r"OX=(\d+)", ln); gene = re.search(r"GN=(\S+)", ln)
        desc = ln.split(None, 1)[1] if " " in ln else ""
        desc = re.sub(r"\s+(OS=|OX=|GN=|PE=|SV=).*$", "", desc).strip()
        out[acc] = {"taxid": tax.group(1) if tax else None,
                    "gene": gene.group(1) if gene else None, "desc": desc}
    return out


def acc2druginfo():
    d = {}
    for ln in open(DT_TSV).read().splitlines()[1:]:
        p = ln.split("\t")
        if len(p) < 6: continue
        d.setdefault(p[0], []).append({"organism": p[1], "action": p[3], "moa": p[4], "drug": p[5]})
    return d


def informative_tokens(desc):
    toks = re.split(r"[^a-zA-Z0-9]+", (desc or "").lower())
    return set(t for t in toks if t and t not in STOP and len(t) > 2)


# ---------------- foldseek ----------------
def run_foldseek(qdir, rdir, tag):
    out = os.path.join(FS, f"aln_{tag}.m8"); tmp = os.path.join(FS, f"tmp_{tag}")
    shutil.rmtree(tmp, ignore_errors=True)
    if os.path.exists(out): os.remove(out)
    r = subprocess.run([FOLDSEEK, "easy-search", qdir, rdir, out, tmp, "--alignment-type", "1",
                        "-e", "10", "-s", "9.5", "--max-seqs", "6000", "--threads", "4",
                        "--format-output", "query,target,qtmscore,ttmscore,alntmscore,fident,evalue,alnlen",
                        "-v", "1"], capture_output=True, text=True)
    if not os.path.exists(out):
        print("STDERR:", r.stderr[-3000:]); raise SystemExit(f"foldseek produced no output ({tag})")
    shutil.rmtree(tmp, ignore_errors=True)
    return out


def acc_of(name):
    return re.sub(r"\.pdb.*$", "", os.path.basename(name))


def best_hits(m8):
    """query_acc -> list of (tm, target_acc, ttm, fident) sorted desc by tm."""
    per = {}
    for ln in open(m8):
        p = ln.rstrip("\n").split("\t")
        if len(p) < 8: continue
        q = acc_of(p[0]); t = acc_of(p[1]); tm = float(p[2]); ttm = float(p[3]); fid = float(p[5])
        per.setdefault(q, {})
        if t not in per[q] or tm > per[q][t][0]:
            per[q][t] = (tm, ttm, fid)
    return {q: sorted(([tm, t, ttm, fid] for t, (tm, ttm, fid) in d.items()), key=lambda x: -x[0])
            for q, d in per.items()}


# ---------------- random reference (organism-matched null) ----------------
def uniprot_candidates(taxid, want, exclude):
    """Return a list of candidate accessions for taxid (cached), excluding `exclude`."""
    cf = os.path.join(CACHE, f"cand_{taxid}.txt")
    if os.path.exists(cf):
        cands = [x for x in open(cf).read().split() if x]
    else:
        if taxid == "9606":
            url = "https://rest.uniprot.org/uniprotkb/stream?query=organism_id:9606+AND+reviewed:true&format=list"
        else:
            url = f"https://rest.uniprot.org/uniprotkb/search?query=organism_id:{taxid}&format=list&size=500"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "structrepurpose1"})
            with urllib.request.urlopen(req, timeout=90) as r:
                cands = [x.strip() for x in r.read().decode().split() if x.strip()]
        except Exception as e:
            print(f"  [cand {taxid}] FAILED {e}"); cands = []
        open(cf, "w").write("\n".join(cands) + "\n")
    return [c for c in cands if c not in exclude]


def build_random_ref(dt_ok_per_taxid, exclude):
    """For each taxid, fetch dt_ok_per_taxid[t] random NON-drug structures of that taxid. Cached acc list."""
    chosen_cf = os.path.join(CACHE, "rand_chosen.json")
    if os.path.exists(chosen_cf):
        chosen = json.load(open(chosen_cf))
        # ensure structures present
        fetch_many([a for lst in chosen.values() for a in lst], RAND_PDB, "rand-cached")
        return chosen
    rng = random.Random(SEED)
    chosen = {}
    for taxid in sorted(dt_ok_per_taxid, key=lambda t: -dt_ok_per_taxid[t]):
        need = dt_ok_per_taxid[taxid]
        if need <= 0: continue
        cands = uniprot_candidates(taxid, need, exclude)
        rng.shuffle(cands)
        got = []
        i = 0
        # fetch in blocks until `need` succeed or candidates exhausted
        while len(got) < need and i < len(cands):
            block = cands[i:i + max(need * 2, 40)]; i += len(block)
            ok = fetch_many(block, RAND_PDB, f"rand-tax{taxid}")
            for a in block:
                if a in ok and a not in got:
                    got.append(a)
                    if len(got) >= need: break
        chosen[taxid] = got[:need]
        print(f"  [rand {taxid}] need {need} got {len(chosen[taxid])}", flush=True)
    json.dump(chosen, open(chosen_cf, "w"), indent=1, sort_keys=True)
    return chosen


# ---------------- main ----------------
def main():
    t0 = time.time()
    dt_hdr = parse_fasta_headers(DT_FASTA)
    dt_accs = sorted(dt_hdr.keys())
    druginfo = acc2druginfo()
    print(f"[1] drug-target reference: {len(dt_accs)} accessions", flush=True)
    dt_ok = fetch_many(dt_accs, DT_PDB, "drugtarget")
    dt_ok_per_taxid = {}
    for a in dt_ok:
        tx = dt_hdr[a]["taxid"]
        if tx: dt_ok_per_taxid[tx] = dt_ok_per_taxid.get(tx, 0) + 1

    # queries
    print("[2] fetching query structures", flush=True)
    ec_want = {g: acc for g, (acc, kw) in ECOLI_CANON.items()}
    ec_ok = fetch_many(sorted(set(ec_want.values())), QEC, "ecoli-canon")
    ess_map = json.load(open(ESS_MAP))  # orig_acc -> fa1090_acc (AF-covered ortholog)
    ng_meta = {}  # fa1090_acc -> {orig, gene}
    for ln in open(LOCKED).read().splitlines()[1:]:
        p = ln.split("\t")
        if len(p) >= 3 and p[2] == "1":
            fa = ess_map.get(p[0])
            if fa: ng_meta[fa] = {"orig": p[0], "gene": p[1]}
    ng_ess = sorted((fa, m["gene"]) for fa, m in ng_meta.items())  # (fa1090_acc, gene)
    ng_hdr = parse_fasta_headers(FA1090_FASTA)
    ng_ok = fetch_many([fa for fa, g in ng_ess], QNG, "ngono-ess")

    # random null reference (organism-matched, same successful-count per taxid as drug targets)
    print("[3] building organism-matched random NULL reference", flush=True)
    exclude = set(dt_accs) | {a for a, g in ng_ess} | set(ess_map.keys()) | set(ec_want.values())
    rand_chosen = build_random_ref(dt_ok_per_taxid, exclude)
    rand_ok = set()
    for lst in rand_chosen.values():
        for a in lst:
            if os.path.exists(os.path.join(RAND_PDB, f"{a}.pdb")): rand_ok.add(a)
    # prune any stray pdbs not in chosen list so DB == chosen set exactly
    keep = {f"{a}.pdb" for a in rand_ok}
    for f in os.listdir(RAND_PDB):
        if f.endswith(".pdb") and f not in keep:
            os.remove(os.path.join(RAND_PDB, f))
    n_dt, n_rand = len(dt_ok), len(rand_ok)
    print(f"    drug-target ref n={n_dt} ; random ref n={n_rand}", flush=True)

    # foldseek
    print("[4] foldseek TMalign searches", flush=True)
    # combine ecoli+ngono queries into one dir for the vs-drugtarget search
    QALL = os.path.join(SR, "q_all"); shutil.rmtree(QALL, ignore_errors=True); os.makedirs(QALL)
    for f in os.listdir(QEC):
        if f.endswith(".pdb"): shutil.copy(os.path.join(QEC, f), os.path.join(QALL, f))
    for f in os.listdir(QNG):
        if f.endswith(".pdb"): shutil.copy(os.path.join(QNG, f), os.path.join(QALL, f))
    m8_dt = run_foldseek(QALL, DT_PDB, "vs_dt")
    m8_rand = run_foldseek(QNG, RAND_PDB, "vs_rand")
    hits_dt = best_hits(m8_dt); hits_rand = best_hits(m8_rand)

    # ---------------- G1: E. coli canonical MoA recovery via structure ----------------
    print("[5] scoring", flush=True)
    g1_detail = []
    for gene, (acc, kw) in sorted(ECOLI_CANON.items()):
        if acc not in ec_ok:
            g1_detail.append({"gene": gene, "acc": acc, "structure": False}); continue
        hlist = hits_dt.get(acc, [])
        top = hlist[0] if hlist else None
        best_tm = round(top[0], 3) if top else 0.0
        tgt = top[1] if top else None
        moas = sorted({x["moa"] for x in druginfo.get(tgt, []) if x["moa"]}) if tgt else []
        moa_str = " | ".join(moas)[:140]
        correct = bool(top and best_tm >= TM_THRESH and kw.lower() in moa_str.lower())
        g1_detail.append({"gene": gene, "acc": acc, "structure": True, "expected_moa_kw": kw,
                          "best_struct_homolog": tgt, "best_tm": best_tm,
                          "homolog_desc": (dt_hdr.get(tgt, {}) or {}).get("desc", "")[:80],
                          "retrieved_moa": moa_str, "n_drugs": len(druginfo.get(tgt, [])),
                          "correct": correct})
    g1_tested = [r for r in g1_detail if r.get("structure") and r["best_tm"] >= TM_THRESH]
    g1_correct = [r for r in g1_tested if r["correct"]]
    g1_rate = round(len(g1_correct) / len(g1_tested), 3) if g1_tested else 0.0
    G1 = bool(len(g1_tested) >= 8 and g1_rate >= 0.80)

    # ---------------- G2: N. gonorrhoeae coverage + null guard ----------------
    def covered(hits, accs, T):
        return set(a for a in accs if hits.get(a) and hits[a][0][0] >= T)

    ng_cov_detail = []
    for acc, gene in sorted(ng_ess):
        dt_top = hits_dt.get(acc, [[0.0, None, 0, 0]])[0]
        rd_top = hits_rand.get(acc, [[0.0, None, 0, 0]])[0]
        dt_tm = round(dt_top[0], 3); rd_tm = round(rd_top[0], 3); tgt = dt_top[1]
        moas = sorted({x["moa"] for x in druginfo.get(tgt, []) if x["moa"]}) if tgt else []
        drugs = sorted({x["drug"] for x in druginfo.get(tgt, [])}) if tgt else []
        orgs = sorted({x["organism"] for x in druginfo.get(tgt, [])}) if tgt else []
        qtok = informative_tokens(ng_hdr.get(acc, {}).get("desc", ""))
        ttok = informative_tokens((dt_hdr.get(tgt, {}) or {}).get("desc", "")) if tgt else set()
        shared = sorted(qtok & ttok)
        ng_cov_detail.append({
            "acc": acc, "orig_acc": ng_meta[acc]["orig"], "gene": gene, "structure": acc in ng_ok,
            "query_desc": ng_hdr.get(acc, {}).get("desc", "")[:80],
            "best_dt_homolog": tgt, "best_dt_tm": dt_tm,
            "dt_homolog_desc": (dt_hdr.get(tgt, {}) or {}).get("desc", "")[:80],
            "dt_homolog_organisms": orgs[:3], "moa": (moas[0] if moas else "")[:90],
            "n_existing_drugs": len(drugs),
            "best_random_tm": rd_tm, "dt_minus_rand": round(dt_tm - rd_tm, 3),
            "shared_family_tokens": shared, "family_plausible": bool(shared),
            "covered_dt": bool(dt_tm >= TM_THRESH), "specific_vs_null": bool(dt_tm >= TM_THRESH and dt_tm > rd_tm),
        })
    ng_cov_detail.sort(key=lambda x: -x["best_dt_tm"])

    n_total = len(ng_ess)
    cov = {}
    for T in TM_SENS:
        cov[f"{T:.2f}"] = {
            "n_dt": len(covered(hits_dt, [a for a, g in ng_ess], T)),
            "n_rand": len(covered(hits_rand, [a for a, g in ng_ess], T)),
        }
    n_dt_cov = cov[f"{TM_THRESH:.2f}"]["n_dt"]
    n_rand_cov = cov[f"{TM_THRESH:.2f}"]["n_rand"]
    n_specific = sum(1 for r in ng_cov_detail if r["specific_vs_null"])
    n_plausible = sum(1 for r in ng_cov_detail if r["covered_dt"] and r["family_plausible"])

    G2a = bool(n_dt_cov > 1)  # beats sequence baseline 1/32
    G2b = bool(n_dt_cov >= 2 * n_rand_cov and (n_dt_cov - n_rand_cov) >= 3)  # NULL guard
    G2 = bool(G2a and G2b)

    verdict_gate = "PASS" if (G1 and G2) else ("PARTIAL" if G1 else "NEGATIVE")
    if G1 and G2a and not G2b:
        verdict_gate = "NEGATIVE"  # expansion is promiscuity

    payload = {
        "knowledge_base": {
            "drug_target_accessions_requested": len(dt_accs),
            "drug_target_structures_fetched": n_dt,
            "drug_target_af_404": len(dt_accs) - n_dt,
            "source": "ChEMBL drug-mechanism -> AlphaFold DB v6 structures",
        },
        "tm_threshold_primary": TM_THRESH,
        "null_reference": {
            "design": "organism-composition-matched random NON-drug-target AF proteins (per-taxid same "
                      "successful-count as drug targets); seeded RNG=1234; cached accession list",
            "n_random_structures": n_rand,
        },
        "G1_validation_ecoli": {
            "canonical_targets_with_structure": sum(1 for r in g1_detail if r.get("structure")),
            "tested_at_TM>=%.2f" % TM_THRESH: len(g1_tested),
            "correct_moa_recovered": len(g1_correct),
            "recovery_rate": g1_rate,
            "intervene1_sequence_baseline": "9/9 correct MoA",
            "detail": sorted(g1_detail, key=lambda x: x["gene"]),
            "G1_pass": G1,
        },
        "G2_coverage_ngonorrhoeae": {
            "n_essential_targets": n_total,
            "query_structure_source": "BLIND1 essential accs (UP001163151, not in AF-DB) mapped by mmseqs "
                                      "(pident>=90,qcov>=0.8; 98.7-100%) to AF-covered FA1090 orthologs (UP000000535)",
            "n_query_structures_available": len(ng_ok),
            "intervene1_sequence_coverage": 1,
            "structural_coverage_at_TM>=%.2f" % TM_THRESH: n_dt_cov,
            "null_random_coverage_at_TM>=%.2f" % TM_THRESH: n_rand_cov,
            "n_specific_vs_null_paired": n_specific,
            "n_covered_and_family_plausible": n_plausible,
            "coverage_by_threshold": cov,
            "G2a_beats_sequence_baseline": G2a,
            "G2b_survives_null_guard": G2b,
            "G2_pass": G2,
            "detail": ng_cov_detail,
        },
        "GATE": verdict_gate,
    }

    # deterministic sha over payload (exclude verdict/provenance)
    payload_json = json.dumps(payload, sort_keys=True)
    sha = hashlib.sha256(payload_json.encode()).hexdigest()

    verdict = (
        f"STRUCTURAL REPURPOSING vs INTERVENE1 sequence baseline ({verdict_gate}). "
        f"Drug-target STRUCTURE reference: {n_dt}/{len(dt_accs)} AlphaFold(v6) structures fetched "
        f"({len(dt_accs)-n_dt} 404). "
        f"G1 VALIDATION (E. coli canonical antibacterial targets): structural best-homolog recovered the "
        f"correct drug-class MoA in {len(g1_correct)}/{len(g1_tested)} (rate {g1_rate}) at TM>={TM_THRESH} "
        f"[{'PASS' if G1 else 'FAIL'}] vs INTERVENE1 sequence 9/9. "
        f"G2 EXPANSION (novel N. gonorrhoeae, 32 FBA-essential): STRUCTURAL coverage = {n_dt_cov}/32 vs "
        f"INTERVENE1 SEQUENCE 1/32. NULL/promiscuity guard: organism-matched RANDOM non-drug reference "
        f"(n={n_rand}) gives {n_rand_cov}/32 at the same TM>={TM_THRESH}; per-query paired, {n_specific}/32 "
        f"queries score strictly higher vs drug targets than vs random. "
        + ({"PASS": f"The gain ({n_dt_cov} vs 1) SURVIVES the null (drug-target hit rate clearly exceeds the "
                    f"random-structure hit rate) -> structure adds REAL, specific repurposing coverage.",
            "PARTIAL": "Structure VALIDATES (G1) but does not expand coverage beyond sequence in a way that "
                       "survives the null guard.",
            "NEGATIVE": (f"COVERAGE GAIN IS PROMISCUITY: random non-drug structures are matched at TM>={TM_THRESH} "
                         f"nearly as often ({n_rand_cov}/32) as drug targets ({n_dt_cov}/32) -> the apparent "
                         f"expansion is generic fold-matching, NOT drug-target signal. Honest negative."
                         if (G1 and G2a and not G2b) else
                         "Structure does not validate the canonical drug-class MoA recovery (G1 fails); "
                         "structural repurposing is not established here.")}[verdict_gate])
        + " SCOPE: in-silico repurposing HYPOTHESES via drug-target fold homology; does NOT establish whole-cell "
          "activity, penetration, or selectivity (experiment-gated); AF-DB coverage bounds the reference; not wet-lab."
    )

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = {"summary": {**payload, "verdict": verdict}, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(RES, "STRUCTREPURPOSE1_metrics.json"), "w"), indent=2, sort_keys=True)
    open(os.path.join(RES, "STRUCTREPURPOSE1_payload.sha256"), "w").write(sha + "\n")

    # console panel
    print("\n=== G1 E. coli canonical MoA recovery (structural) ===")
    for r in sorted(g1_detail, key=lambda x: x["gene"]):
        if not r.get("structure"): print(f"  {r['gene']:6s} NO STRUCTURE"); continue
        print(f"  {r['gene']:6s} TM={r['best_tm']:.2f} correct={int(r['correct'])}  homolog={r['best_dt_homolog'] if 'best_dt_homolog' in r else r.get('best_struct_homolog')}  MoA:{r['retrieved_moa'][:55]}")
    print(f"\nG1 recovery: {len(g1_correct)}/{len(g1_tested)} (rate {g1_rate}) -> {'PASS' if G1 else 'FAIL'}")
    print("\n=== G2 N. gonorrhoeae structural coverage (top by TM) ===")
    for r in ng_cov_detail[:12]:
        flag = "COV" if r["covered_dt"] else "   "
        print(f"  {flag} {r['gene']:14s} dtTM={r['best_dt_tm']:.2f} randTM={r['best_random_tm']:.2f} "
              f"spec={int(r['specific_vs_null'])} plaus={int(r['family_plausible'])}  {r['moa'][:40]}")
    print(f"\nStructural coverage {n_dt_cov}/32  vs sequence 1/32  |  NULL random {n_rand_cov}/32  |  "
          f"specific-vs-null {n_specific}/32  |  plausible {n_plausible}")
    print(f"coverage by TM threshold: {json.dumps(cov)}")
    print(f"G1={G1}  G2a(beats seq)={G2a}  G2b(survives null)={G2b}  G2={G2}")
    print("GATE:", verdict_gate)
    print("\nVERDICT:", verdict)
    print("\npayload sha256:", sha, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
