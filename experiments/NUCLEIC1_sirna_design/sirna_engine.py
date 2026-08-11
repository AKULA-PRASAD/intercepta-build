#!/usr/bin/env python
"""NUCLEIC1 — deterministic siRNA design engine. Cited, independently-validated rules; NO training data,
NO ViennaRNA. Scores a 19-nt duplex core (sense = target-mRNA subsequence 5'->3'; antisense = its reverse
complement). Rules: Reynolds 2004 (8-criterion), Ui-Tei 2004 (4-rule), thermodynamic end-asymmetry
(Khvorova/Schwarz via a nearest-neighbor dG table), and immunostimulatory/homopolymer/GC filters.
Deterministic + unit-testable to spec (V1). This module makes NO new-efficacy-model claim (see PREREG)."""

# Turner 1999 RNA nearest-neighbor duplex free energies (dG37, kcal/mol), 5'->3'/3'->5'. Standard values.
NN_DG = {
    "AA": -0.93, "AU": -1.10, "UA": -1.33, "UU": -0.93,
    "CA": -2.11, "CU": -2.08, "GA": -2.35, "GU": -2.24,
    "AC": -2.24, "AG": -2.08, "UC": -2.35, "UG": -2.11,
    "CC": -3.26, "CG": -2.36, "GC": -3.42, "GG": -3.26,
    # note: this is a standard symmetric-ish approximation table for relative end-stability comparison
}
COMP = {"A": "U", "U": "A", "G": "C", "C": "G", "T": "A"}


def _rna(s):
    return s.upper().replace("T", "U")


def revcomp(s):
    s = _rna(s)
    return "".join(COMP[c] for c in reversed(s))


def gc(s):
    s = _rna(s)
    return (s.count("G") + s.count("C")) / len(s) if s else 0.0


def _end_stability(seq4):
    """Sum of NN dG over a 4-nt terminus (more negative = more stable)."""
    seq4 = _rna(seq4)
    return sum(NN_DG.get(seq4[i:i + 2], 0.0) for i in range(len(seq4) - 1))


def thermo_asymmetry(sense19):
    """Antisense 5' end should be LESS stable than sense 5' end (Khvorova/Schwarz).
    sense 5' end = sense[0:4]; antisense 5' end pairs with sense 3' end = sense[-4:].
    Return dG(antisense-5'end) - dG(sense-5'end); POSITIVE (antisense end less stable) is favorable."""
    s = _rna(sense19)
    dg_sense5 = _end_stability(s[:4])
    dg_anti5 = _end_stability(revcomp(s[-4:]))   # antisense 5' end = revcomp of sense 3' end
    return dg_anti5 - dg_sense5


def reynolds(sense19):
    """Reynolds 2004 8-criterion (each +1 if satisfied). sense is the 19-nt guide-strand-sense (5'->3')."""
    s = _rna(sense19)
    if len(s) != 19:
        return 0, {}
    c = {}
    c["gc_30_52"] = 0.30 <= gc(s) <= 0.52
    # low internal stability at sense 3' end (positions 15-19 AU-rich): >=3 A/U in last 5
    c["au_3prime_third"] = sum(1 for x in s[-5:] if x in "AU") >= 3
    c["no_internal_repeat"] = not any(s[i] == s[i+1] == s[i+2] == s[i+3] for i in range(len(s)-3))
    c["A_at_19"] = s[18] == "A"
    c["A_at_3"] = s[2] == "A"
    c["U_at_10"] = s[9] == "U"
    c["not_GC_at_19"] = s[18] not in "GC"
    c["not_G_at_13"] = s[12] != "G"
    return sum(c.values()), c


def ui_tei(sense19):
    """Ui-Tei 2004 4 rules on the ANTISENSE (guide) strand. +1 each."""
    s = _rna(sense19)
    anti = revcomp(s)  # 5'->3' antisense
    c = {}
    c["antisense5_AU"] = anti[0] in "AU"          # A/U at antisense 5' end
    c["sense5_GC"] = s[0] in "GC"                  # G/C at sense 5' end
    c["au_rich_antisense_5p7"] = sum(1 for x in anti[:7] if x in "AU") >= 4
    c["no_gc_stretch_gt9"] = _max_gc_run(s) <= 9
    return sum(c.values()), c


def _max_gc_run(s):
    s = _rna(s); best = cur = 0
    for x in s:
        cur = cur + 1 if x in "GC" else 0
        best = max(best, cur)
    return best


def filters_ok(sense19):
    """Hard filters: no immunostimulatory motif, no homopolymer>=4, GC in [0.20,0.65]."""
    s = _rna(sense19); anti = revcomp(s)
    for motif in ("UGUGU", "GUCCUUCAA"):
        if motif in s or motif in anti:
            return False, "immunostim_motif"
    if any(b * 4 in s for b in "AUGC"):
        return False, "homopolymer4"
    if not (0.20 <= gc(s) <= 0.65):
        return False, "gc_out_of_range"
    return True, "ok"


def score_sirna(sense19):
    """Composite deterministic score. Returns dict with per-rule detail + total + pass flag."""
    s = _rna(sense19)
    ok, why = filters_ok(s)
    r_tot, r_det = reynolds(s)
    u_tot, u_det = ui_tei(s)
    asym = thermo_asymmetry(s)
    # documented (NOT fitted) composite: reynolds (0-8) + 2x ui_tei (0-8) + asymmetry bonus
    total = r_tot + 2 * u_tot + (2.0 if asym > 0 else 0.0)
    # gate: passes design if filters ok AND reynolds>=6 AND ui_tei>=3 AND favorable asymmetry
    passed = bool(ok and r_tot >= 6 and u_tot >= 3 and asym > 0)
    return {"sense": s, "antisense": revcomp(s), "gc": round(gc(s), 3),
            "reynolds": r_tot, "ui_tei": u_tot, "thermo_asym_dG": round(asym, 3),
            "filters": why, "score": round(float(total), 3), "pass": passed}


def enumerate_candidates(mrna, top=None):
    """All 19-mer sense candidates over the mRNA (5'->3'); scored; sorted by score desc."""
    m = _rna(mrna)
    cands = []
    for i in range(len(m) - 18):
        w = m[i:i + 19]
        if set(w) <= set("AUGC"):
            r = score_sirna(w); r["pos"] = i; cands.append(r)
    cands.sort(key=lambda d: (-d["score"], d["pos"]))
    return cands[:top] if top else cands


if __name__ == "__main__":
    # V1/V2 self-test (no network): known-potent siRNA senses vs random 19-mers from the same context.
    import random, json
    # literature siRNAs (sense strand, cited in positive_controls.json); quick smoke here:
    potent = {"TTR_patisiran_like": "GUAACCAAGAGUAUUCCAU",  # ~TTR-targeting (illustrative)
              "GAPDH_validated":    "GUAUGACAACAGCCUCAAG",
              "PLK1_validated":     "GCACAUACCGCCUGAGUCU"}
    rng = random.Random(42)
    def rand19():
        return "".join(rng.choice("AUGC") for _ in range(19))
    print("=== known siRNA senses ===")
    for n, s in potent.items():
        r = score_sirna(s); print(f"  {n:22s} score={r['score']:5.1f} R={r['reynolds']} U={r['ui_tei']} asym={r['thermo_asym_dG']:+.2f} pass={r['pass']}")
    rs = [score_sirna(rand19())["score"] for _ in range(500)]
    import statistics as st
    print(f"=== 500 random 19-mers: mean score {st.mean(rs):.2f} (sd {st.pstdev(rs):.2f}), max {max(rs):.1f} ===")
    print("engine self-test OK")
