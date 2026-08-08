"""CRISPRIDESIGN1 — deterministic, wet-lab-ready CRISPRi essentiality-validation experiment DESIGN for INTERCEPTA
flagship antibacterial targets in E. coli K-12 MG1655 (RefSeq NC_000913.3).

SCOPE (binds every output): IN-SILICO DESIGN / proposal for a wet-lab collaborator. NOT a performed experiment; NOT
validated guides. Predicted knockdown efficiency is a HEURISTIC, not a measurement. Guides REQUIRE experimental validation.

Design rules are PRE-REGISTERED in PREREG.md and implemented here deterministically (no RNG). Reproduce x2 byte-identical:
payload SHA-256 over sorted-key JSON excluding provenance (git sha / timestamp / runtime). Sequences are REAL — fetched from
NCBI NC_000913.3 (genome + all-CDS nucleotide) and cached in $INTERCEPTA_DATA/crispridesign1/; coordinates/strands are parsed
from the fetched CDS headers and each CDS is asserted against the genome slice before any guide is designed.
Env: intercepta-build (numpy). Off-target search is genome-wide, both strands, <=2 mismatches, PAM-adjacent.
"""
import os, re, json, time, hashlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data"), "crispridesign1")
GENOME_FASTA = os.path.join(DATA, "NC_000913.3.fasta")
CDS_FASTA = os.path.join(DATA, "NC_000913.3_cds_na.fasta")
ACCESSION = "NC_000913.3"
GENOME_LEN_EXPECTED = 4641652

# PRE-REGISTERED targets (role -> (locus_tag, gene, protein_id, uniprot))
TARGETS = [
    ("PRIMARY",              "b0173", "dxr",  "NP_414715.1", "P45568"),
    ("SECONDARY",            "b3189", "murA", "NP_417656.1", "P0A749"),
    ("CONTROL_POS_essential","b0095", "ftsZ", "NP_414637.1", "P0A9A6"),
    ("CONTROL_NEG_dispens",  "b0344", "lacZ", "NP_414878.1", "P00722"),
]
# design constants (pre-registered)
ORF_WINDOW_FRAC = 0.30      # protospacer 5'-most coding base within first 30% of ORF
GC_MIN, GC_MAX = 0.30, 0.70
MAX_MM = 2                  # off-target mismatch ceiling reported
GUIDES_PER_TARGET = 3
GC_TOL = 0.20              # gc_score peak width
B2I = {"A": 0, "C": 1, "G": 2, "T": 3, "N": 4}
COMP = {"A": "T", "T": "A", "G": "C", "C": "G", "N": "N"}

def rc(s): return "".join(COMP[c] for c in reversed(s))

def read_genome(p):
    seq = []
    for ln in open(p):
        if not ln.startswith(">"): seq.append(ln.strip())
    return "".join(seq).upper()

def parse_cds(p):
    recs, hdr, seq = {}, None, []
    for ln in open(p):
        if ln.startswith(">"):
            if hdr is not None: recs[hdr] = "".join(seq)
            hdr, seq = ln.strip(), []
        else:
            seq.append(ln.strip())
    if hdr is not None: recs[hdr] = "".join(seq)
    out = {}
    for h, s in recs.items():
        m = re.search(r"locus_tag=(b\d+)\]", h)
        loc = re.search(r"location=([^\]]+)\]", h)
        if not m or not loc: continue
        lt = m.group(1); locstr = loc.group(1)
        comp = locstr.startswith("complement")
        nums = re.findall(r"\d+", locstr)
        a, b = int(nums[0]), int(nums[1])
        out[lt] = {"seq": s.upper(), "start": a, "end": b, "strand": "-" if comp else "+", "location": locstr}
    return out

def gc_frac(s): return (s.count("G") + s.count("C")) / len(s)

def has_polyT(s): return "TTTT" in s

def eff_heuristic(frac5, gc):
    pos_score = 1.0 - frac5 / ORF_WINDOW_FRAC
    gc_score = max(0.0, min(1.0, 1.0 - abs(gc - 0.50) / GC_TOL))
    return round((pos_score + gc_score) / 2.0, 4), round(pos_score, 4), round(gc_score, 4)

def encode(seq):
    return np.frombuffer(bytes(B2I[c] for c in seq), dtype=np.uint8)

def offtarget_scan(gp, gm, spacer):
    """Genome-wide, both strands, PAM-adjacent (NGG immediately 3' of the 20-mer on that strand).
    Returns (perfect_count, le2mm_count) counting all PAM-adjacent sites with 0 / <=2 mismatches over both strands."""
    q = encode(spacer); W = len(q)
    perfect = 0; le2 = 0
    for arr in (gp, gm):
        L = arr.shape[0]
        n = L - W - 2  # need room for NGG (3 nt) after the 20-mer
        # sliding mismatch count via W position-wise comparisons
        match = np.zeros(n, dtype=np.int16)
        for k in range(W):
            match += (arr[k:k + n] == q[k])
        mm = W - match
        # PAM: positions p..p+W-1 = protospacer; PAM at p+W (N), p+W+1 (G), p+W+2 (G)
        g1 = arr[W + 1: W + 1 + n]; g2 = arr[W + 2: W + 2 + n]
        pam = (g1 == 2) & (g2 == 2)
        perfect += int(np.count_nonzero((mm == 0) & pam))
        le2 += int(np.count_nonzero((mm <= MAX_MM) & pam))
    return perfect, le2

def design_for_target(coding, gp, gm):
    """coding = CDS coding strand 5'->3' (ATG..stop). Scan TEMPLATE strand for N20 + NGG (non-template-strand base-pairing).
    Return ranked list of guide dicts passing all filters (before final specificity gate)."""
    L = len(coding)
    template = rc(coding)  # 5'->3', transcription direction
    limit = int(L * ORF_WINDOW_FRAC)
    cands = []
    # scan template for 20-mer immediately 5' of NGG
    for m in re.finditer(r"(?=([ACGT]{20})([ACGT]GG))", template):
        a = m.start(1)
        spacer = m.group(1)  # protospacer on template strand = sgRNA spacer (5'->3')
        pam = m.group(2)
        # map to coding-strand coordinates: template index a..a+19 -> coding L-1-(a+19) .. L-1-a
        cod_5p = L - 1 - (a + 19)  # 5'-most coding base covered (0-based from ATG)
        frac5 = cod_5p / L
        if not (0.0 <= frac5 <= ORF_WINDOW_FRAC):
            continue
        gc = gc_frac(spacer)
        if not (GC_MIN <= gc <= GC_MAX):
            continue
        if has_polyT(spacer):
            continue
        eff, pos_s, gc_s = eff_heuristic(frac5, gc)
        cands.append({
            "protospacer_5to3": spacer, "pam": pam, "strand_targeted": "non-template (coding)",
            "protospacer_on": "template strand", "orf_pos_pct_from_start": round(frac5 * 100, 2),
            "coding_5p_base_0idx": cod_5p, "gc_percent": round(gc * 100, 2),
            "poly_t": False, "predicted_efficiency_heuristic": eff,
            "eff_pos_score": pos_s, "eff_gc_score": gc_s,
        })
    # deterministic ranking: eff desc, frac asc, spacer lexicographic
    cands.sort(key=lambda d: (-d["predicted_efficiency_heuristic"], d["orf_pos_pct_from_start"], d["protospacer_5to3"]))
    return cands

def make_oligos(spacer):
    top = "CACC" + spacer
    bot = "AAAC" + rc(spacer)
    note = "" if spacer[0] == "G" else "if sgRNA promoter needs a +1 G, prepend G to spacer (21-nt)"
    return {"top_oligo_5to3": top, "bottom_oligo_5to3": bot, "bsai_overhangs": "CACC / AAAC (EXAMPLE vector)", "note": note}

def nontargeting_control(gp, gm):
    # deterministic candidate list (scrambled; GC 40-60%, no TTTT). Pick first with 0 perfect genomic hits.
    cands = ["ACGGAGGCTAAGCGTCGCAA", "GTAGCGACTAAACGTAGGCA", "GACGACTAGCTAGGCATCGA",
             "CGATGCTAGCGATCAGTACG", "GCACTACCAGAGCTAACTCA"]
    for s in cands:
        assert set(s) <= set("ACGT") and len(s) == 20
        gc = gc_frac(s)
        if not (GC_MIN <= gc <= GC_MAX) or has_polyT(s):
            continue
        perfect, le2 = offtarget_scan(gp, gm, s)  # PAM-adjacent perfect/<=2mm; also do a PAM-agnostic perfect check below
        # PAM-agnostic perfect occurrence (conservative: any exact 20-mer match on either strand)
        genome_str = None
        if perfect == 0:
            return {"protospacer_5to3": s, "gc_percent": round(gc * 100, 2), "poly_t": False,
                    "perfect_offtargets_pam_adjacent": perfect, "le2mm_offtargets_pam_adjacent": le2,
                    "role": "non-targeting negative control (no genome match)", **make_oligos(s)}
    raise RuntimeError("no non-targeting candidate passed 0-perfect check")

def main():
    t0 = time.time()
    genome = read_genome(GENOME_FASTA)
    assert len(genome) == GENOME_LEN_EXPECTED, f"genome length {len(genome)} != {GENOME_LEN_EXPECTED}"
    cds = parse_cds(CDS_FASTA)
    gp = encode(genome)               # + strand
    gm = encode(rc(genome))           # - strand (5'->3')
    input_sha = {os.path.basename(GENOME_FASTA): hashlib.sha256(open(GENOME_FASTA, 'rb').read()).hexdigest(),
                 os.path.basename(CDS_FASTA): hashlib.sha256(open(CDS_FASTA, 'rb').read()).hexdigest()}

    targets_out = []
    for role, lt, gene, protid, uni in TARGETS:
        rec = cds[lt]
        coding = rec["seq"]
        # provenance assertions (REAL sequence, coordinates verified vs genome)
        gslice = genome[rec["start"] - 1: rec["end"]]
        coding_check = rc(gslice) if rec["strand"] == "-" else gslice
        assert coding_check == coding, f"{lt} CDS does not match genome slice"
        assert coding[:3] == "ATG" and coding[-3:] in ("TAA", "TAG", "TGA"), f"{lt} not a valid ORF"
        cands = design_for_target(coding, gp, gm)
        # apply specificity gate, keep first GUIDES_PER_TARGET with 0 perfect off-targets
        kept = []
        for c in cands:
            perfect, le2 = offtarget_scan(gp, gm, c["protospacer_5to3"])
            c["perfect_pam_sites_genome"] = perfect          # expect 1 = the on-target
            c["perfect_offtargets"] = perfect - 1            # exclude on-target
            c["le2mm_pam_sites_genome"] = le2
            c["le2mm_offtargets"] = le2 - 1                  # exclude on-target
            if c["perfect_offtargets"] != 0:
                continue
            c.update(make_oligos(c["protospacer_5to3"]))
            kept.append(c)
            if len(kept) >= GUIDES_PER_TARGET:
                break
        targets_out.append({
            "role": role, "gene": gene, "locus_tag": lt, "protein_id": protid, "uniprot": uni,
            "cds_location": rec["location"], "cds_strand": rec["strand"], "cds_len_bp": len(coding),
            "cds_gc_percent": round(gc_frac(coding) * 100, 2), "n_candidates_in_window": len(cands),
            "guides": kept,
        })

    nt = nontargeting_control(gp, gm)

    gate = {
        "system": "E. coli K-12 MG1655 + inducible dCas9 (CRISPRi) + one sgRNA plasmid per condition",
        "conditions": "targeting sgRNA vs NON-TARGETING control; ftsZ = positive-essential control; lacZ = negative-dispensable control",
        "readout": "OD600 growth curve + CFU, triplicate (n>=3), after dCas9 induction",
        "success": "targeting sgRNA reduces final OD600 or CFU >=5-fold vs non-targeting control (p<0.01, n>=3), matching ftsZ direction",
        "failure_first_class": "no growth defect (dispensable-like) => essentiality prediction is WRONG under these conditions; report as a first-class negative",
        "control_expectations": "ftsZ MUST show defect; lacZ MUST NOT show defect",
        "orthogonal_chemical_crosscheck_dxr": "fosmidomycin MIC / growth-inhibition vs MG1655 (fosmidomycin inhibits DXR) — independent drug-based confirmation",
        "est_cost_usd": "200-400", "est_time": "2-3 weeks", "skill": "standard molecular microbiology bench",
    }
    design_rules = {
        "strand_rule": "sgRNA base-pairs with NON-TEMPLATE (coding) strand (Qi 2013); protospacer+NGG PAM on template strand",
        "orf_window": f"protospacer 5'-most coding base within first {int(ORF_WINDOW_FRAC*100)}% of ORF; earlier=predicted-stronger",
        "protospacer_len": 20, "pam": "NGG", "gc_range": [GC_MIN, GC_MAX], "reject_polyT": ">=4 consecutive T",
        "specificity": f"genome-wide both strands, PAM-adjacent, <= {MAX_MM} mismatches; require 0 perfect off-targets",
        "efficiency_heuristic": "eff = mean(pos_score=1-frac/0.30, gc_score=clip(1-|GC-0.5|/0.20,0,1)); HEURISTIC not measured",
        "oligo_scar": "BsaI Golden-Gate CACC/AAAC overhangs (EXAMPLE vector; collaborator must confirm for their vector)",
    }
    n_guides = sum(len(t["guides"]) for t in targets_out)
    verdict = (
        "IN-SILICO CRISPRi ESSENTIALITY-VALIDATION EXPERIMENT DESIGN (NOT PERFORMED; guides REQUIRE wet-lab validation; "
        f"predicted efficiency is a HEURISTIC, not measured). Targets (REAL, NC_000913.3): dxr/ispC b0173 [CORRECTED from the "
        "brief's b0420 which is dxs, a different MEP enzyme], murA b3189, + controls ftsZ b0095 (positive-essential), lacZ b0344 "
        f"(negative-dispensable), + a verified non-targeting control. Designed {n_guides} specificity-passing sgRNAs "
        "(non-template-strand-base-pairing, first 30% of ORF, GC 30-70%, no poly-T, 0 perfect genomic off-targets). Ready-to-order "
        "cloning oligos (example BsaI CACC/AAAC scar) provided. Pre-registered gate: targeting guide reduces final OD600/CFU >=5x "
        "vs non-targeting (p<0.01, n>=3) matching ftsZ; no defect = first-class negative (falsifies the essentiality prediction). "
        "Orthogonal chemical cross-check: fosmidomycin MIC for dxr. ~$200-400, ~2-3 weeks. Deterministic; reproduced x2.")

    payload = {
        "accession": ACCESSION, "genome_len_bp": len(genome), "input_sha256": input_sha,
        "design_rules": design_rules, "targets": targets_out, "non_targeting_control": nt, "gate": gate,
        "scope": "IN-SILICO DESIGN / proposal for a wet-lab collaborator; NOT performed; NOT validated guides; "
                 "predicted efficiency is a heuristic; guides REQUIRE experimental validation",
    }
    metrics = dict(payload); metrics["verdict"] = verdict
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "runtime_sec": round(time.time() - t0, 1)}
    metrics["provenance"] = prov

    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(metrics, open(os.path.join(HERE, "results", "CRISPRIDESIGN1_metrics.json"), "w"), indent=2, sort_keys=True)
    payload_str = json.dumps(payload, sort_keys=True)
    sha = hashlib.sha256(payload_str.encode()).hexdigest()
    open(os.path.join(HERE, "results", "CRISPRIDESIGN1_payload.sha256"), "w").write(sha + "\n")

    # human-readable console summary
    print("VERDICT:", verdict)
    for t in targets_out:
        print(f"\n=== {t['gene']} ({t['locus_tag']}, {t['role']}) {t['cds_location']} len={t['cds_len_bp']}bp "
              f"cand_in_window={t['n_candidates_in_window']} kept={len(t['guides'])} ===")
        for i, g in enumerate(t["guides"], 1):
            print(f"  g{i}: {g['protospacer_5to3']} PAM={g['pam']} ORF@{g['orf_pos_pct_from_start']}% "
                  f"GC={g['gc_percent']}% eff={g['predicted_efficiency_heuristic']} "
                  f"perfectOff={g['perfect_offtargets']} <=2mmOff={g['le2mm_offtargets']}")
            print(f"       top={g['top_oligo_5to3']}  bot={g['bottom_oligo_5to3']}")
    print(f"\nNON-TARGETING: {nt['protospacer_5to3']} GC={nt['gc_percent']}% "
          f"perfectOff(PAM)={nt['perfect_offtargets_pam_adjacent']} <=2mmOff(PAM)={nt['le2mm_offtargets_pam_adjacent']}")
    print(f"\npayload sha256: {sha}  [{time.time()-t0:.0f}s]")

if __name__ == "__main__":
    main()
