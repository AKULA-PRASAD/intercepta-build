"""GENERALIZE2 — confirmatory STRUCTURAL-bridge test (the mechanism behind GENERALIZE1's negative).

GENERALIZE1 established (reproduced x2, sha d58f9e7e): at e<=1e-5 SARS-CoV-2 proteins have ZERO non-coronaviral
drugged-SEQUENCE homolog (Mpro and RdRp included), because cross-family viral sequence identity is below
detection. This asks the direct follow-up: does STRUCTURE bridge the gap? Foldseek TM-score of the two SARS-CoV-2
drug targets (Mpro=6lu7, RdRp=7bv2) vs a small NON-CORONAVIRAL reference of drugged enzymes + negative controls.

CONFIRMATORY (not blind): the reference analogs are chosen by hypothesis (positive/negative controls), so this
tests CAPABILITY ("can structure recover the fold sequence missed?"), NOT a blind discovery ranking. The full
unbiased blind structural screen is currently GATED by a real resource boundary: AlphaFold DB EXCLUDES viral
proteins -- the query SARS-CoV-2 proteins AND the bridging drugged-viral references (HCV NS5B, HIV RT, rhinovirus
3C) are ALL 404 in AF DB (verified) -- so an unbiased 2000-structure reference cannot be built from AF DB and
would require hand-building a viral PDB set. Documented as a boundary, not faked.

PRE-STATED PREDICTIONS (fixed before running; the honest gate):
  P1: Mpro (cysteine/chymotrypsin-like 3C fold) best-matches a PROTEASE of that clan (rhinovirus 3C 1cqq or
      chymotrypsin 4cha), TM >= 0.4, and OUTSCORES the polymerases, HIV aspartic protease, kinase, and GPCR.
  P2: RdRp best-matches a POLYMERASE (HCV NS5B 4wtg or HIV RT 3hvt), TM >= 0.4, and OUTSCORES protease/kinase/GPCR.
  P3: both matches occur despite ~0 detectable sequence homology (already established in GENERALIZE1 -- the full
      2145-seq reference INCLUDED rhinovirus 3C / HCV / HIV and still gave 0 hits at e<=1e-5).
PASS iff P1 AND P2 hold. Env: bioinfo (foldseek). Deterministic; reproduced x2.
"""
import os, json, time, hashlib, subprocess, shutil, re
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results")
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
G2 = os.path.join(DATA, "generalize2"); FOLDSEEK = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/foldseek")
QDIR = os.path.join(G2, "query_clean"); RDIR = os.path.join(G2, "ref")

CLASS = {"1cqq": "protease", "4cha": "protease", "4wtg": "polymerase", "3hvt": "polymerase",
         "1hxw": "protease(aspartic-diff-fold)", "1m17": "kinase(NEGCTRL)", "2rh1": "GPCR(NEGCTRL)"}
LABEL = {"1cqq": "rhinovirus-3C-protease", "4cha": "chymotrypsin", "4wtg": "HCV-NS5B-polymerase",
         "3hvt": "HIV-RT-polymerase", "1hxw": "HIV-protease(aspartic)", "1m17": "EGFR-kinase", "2rh1": "beta2-GPCR"}


def pdbid(name):
    m = re.match(r"([0-9a-zA-Z]{4})", os.path.basename(name))
    return m.group(1).lower() if m else os.path.basename(name)


def main():
    t0 = time.time()
    out = os.path.join(G2, "aln.m8"); tmp = os.path.join(G2, "tmp"); shutil.rmtree(tmp, ignore_errors=True)
    # TMalign-based alignment (--alignment-type 1) for accurate TM-score; qtmscore normalized by query length
    r = subprocess.run([FOLDSEEK, "easy-search", QDIR, RDIR, out, tmp, "--alignment-type", "1",
                        "-e", "10", "-s", "9.5", "--max-seqs", "1000", "--threads", "4",
                        "--format-output", "query,target,qtmscore,ttmscore,alntmscore,fident,evalue,alnlen", "-v", "1"],
                       capture_output=True, text=True)
    if not os.path.exists(out):
        print("STDERR:", r.stderr[-2000:]); raise SystemExit("foldseek produced no output")
    # best TM per (query_protein, reference_pdb) grouping chains
    best = {}   # (qprot, rpdb) -> (tm, fident, evalue)
    for ln in open(out):
        p = ln.rstrip("\n").split("\t")
        if len(p) < 8:
            continue
        qp = "Mpro" if "6lu7" in p[0] else ("RdRp" if "7bv2" in p[0] else pdbid(p[0]))
        rp = pdbid(p[1]); tm = float(p[2]); fid = float(p[5]); ev = float(p[6])
        k = (qp, rp)
        if k not in best or tm > best[k][0]:
            best[k] = (tm, fid, ev)
    shutil.rmtree(tmp, ignore_errors=True)

    def ranked(qp):
        rows = [{"ref": rp, "label": LABEL.get(rp, rp), "class": CLASS.get(rp, "?"),
                 "tm": round(best[(qp, rp)][0], 3), "seq_ident": round(best[(qp, rp)][1], 3),
                 "evalue": best[(qp, rp)][2]} for (q, rp) in best if q == qp]
        rows.sort(key=lambda x: -x["tm"])
        return rows
    mpro = ranked("Mpro"); rdrp = ranked("RdRp")

    def top(rows): return rows[0] if rows else None
    m_top = top(mpro); r_top = top(rdrp)
    # P1: Mpro top is a protease-clan (not aspartic) with TM>=0.4
    p1 = bool(m_top and m_top["class"] == "protease" and m_top["tm"] >= 0.4)
    # P2: RdRp top is a polymerase with TM>=0.4
    p2 = bool(r_top and r_top["class"] == "polymerase" and r_top["tm"] >= 0.4)
    gate = "PASS" if (p1 and p2) else ("PARTIAL" if (p1 or p2) else "FAIL")

    summary = {
        "test": "GENERALIZE2 confirmatory structural-bridge (Foldseek TM) — CAPABILITY not blind screen",
        "resource_boundary": "AlphaFold DB excludes viral proteins (query + HCV/HIV/rhinovirus refs all 404) -> "
                             "full unbiased blind structural screen needs a hand-built viral PDB reference; documented.",
        "Mpro_ranking": mpro, "RdRp_ranking": rdrp,
        "Mpro_top": m_top, "RdRp_top": r_top,
        "P1_Mpro_matches_protease_clan_TM>=0.4": p1,
        "P2_RdRp_matches_polymerase_TM>=0.4": p2,
        "sequence_baseline": "GENERALIZE1: 0 sequence hits at e<=1e-5 vs a 2145-seq reference that INCLUDED "
                             "rhinovirus 3C / HCV / HIV -> any structural match here is recovered where sequence gave nothing.",
        "GATE": gate,
    }
    summary["verdict"] = (
        f"STRUCTURAL-BRIDGE CONFIRMATORY TEST ({gate}). Foldseek TM of the two SARS-CoV-2 drug targets vs a "
        f"non-coronaviral drugged-enzyme reference + negative controls. Mpro top hit: {m_top['label'] if m_top else '-'} "
        f"(class {m_top['class'] if m_top else '-'}, TM {m_top['tm'] if m_top else '-'}, seq_ident {m_top['seq_ident'] if m_top else '-'}). "
        f"RdRp top hit: {r_top['label'] if r_top else '-'} (class {r_top['class'] if r_top else '-'}, TM {r_top['tm'] if r_top else '-'}, "
        f"seq_ident {r_top['seq_ident'] if r_top else '-'}). "
        + ({"PASS": "BOTH viral drug-target folds are correctly recovered by STRUCTURE (protease->protease-clan, "
                    "polymerase->polymerase) with meaningful TM despite ~0 sequence homology -> structure bridges exactly the "
                    "gap sequence could not (GENERALIZE1). CONCLUSION: the viral-generalization failure is a SEQUENCE-TOOL "
                    "limitation, not fundamental; the structural path is viable and is blocked only by AlphaFold DB's exclusion "
                    "of viral structures (a fetch/tooling boundary, solvable by a PDB-based reference), NOT by the method.",
            "PARTIAL": "Exactly one of the two folds was correctly recovered by structure; reported as-is.",
            "FAIL": "Structure did NOT recover the folds either -> even structural homology does not bridge here; viral "
                    "intervention-target prioritization is out of reach for this homology-based approach. Honest negative."}[gate])
        + " SCOPE: confirmatory capability test on 2 targets w/ chosen controls (NOT a blind discovery ranking); TM on "
          "experimental PDB structures; establishes the PRINCIPLE, not a deployed viral pipeline; not wet-lab; n=1 virus.")
    print("PANEL:", json.dumps({k: v for k, v in summary.items() if k != "verdict"}, indent=1, default=str))
    print("\nVERDICT:", summary["verdict"])
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(RES, exist_ok=True)
    json.dump({"summary": summary, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)},
              open(os.path.join(RES, "GENERALIZE2_metrics.json"), "w"), indent=2, sort_keys=True, default=str)
    payload = json.dumps({k: v for k, v in summary.items() if k != "verdict"}, sort_keys=True, default=str)
    open(os.path.join(RES, "GENERALIZE2_payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    print("payload sha256:", hashlib.sha256(payload.encode()).hexdigest(), f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
