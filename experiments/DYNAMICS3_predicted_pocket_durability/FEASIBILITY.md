# DYNAMICS3 — FEASIBILITY (resolved BEFORE gate scoring)

**Gate (frozen in PREREG):** a target yields a *usable top pocket* iff (i) an AlphaFold-DB F1 model
exists for its SIFTS-resolved accession AND covers ≥ 50% of the crystal domain span, AND (ii) fpocket
returns pocket 1 with ≥ 5 distinct protein residues. **PROCEED iff ≥ 18 / 26.**

## RESULT: FEASIBLE — 20 / 26 usable (≥ 18) → PROCEED

### UniProt resolution (largest-span-on-scoring-chain rule, from PDBe SIFTS)
Accessions frozen in `run.py` `ACC`. Notable: 2XCT (gyrA) is a GyrB–GyrA fusion chain → GyrA
dominates → **GYRA_STAAN (Q99XG5)**; 3RAE scoring chain D → **PARE_STRPN (Q59961)**; the viral
crystal chains map to polyprotein / strain-specific entries (see failures below).

### Feasible (20): AF F1 obtained, ≥50% domain coverage, pocket1 ≥5 residues
embB, folP, gyrA, inhA, parC, rpoB, rpsL (7 HIGH abx) · alr, ddlB, dxr, glmU, mraY, murA, murB, murD,
murE, murF, murG (11 LOW abx) · CYP51_Ca (HIGH antifungal) · HSV1_TK (HIGH antiviral).
→ **9 HIGH / 11 LOW.** (embB: 4 of 11 pocket residues fell outside the frozen 1022-residue ESM window
on the 1098-aa protein and were dropped, per the pre-registered windowing rule; 7 scored.)

### Infeasible (6) — reported honestly, NOT worked around
| gene | accession | reason |
|---|---|---|
| FLU_NA | Q6DPL2 | no AF-DB model (HTTP 404) — strain-specific influenza neuraminidase absent |
| FLU_PA | C3W5S0 | no AF-DB model (404) — strain-specific influenza PA absent |
| HCV_NS3 | A8DG50 | no AF-DB model (404) — HCV polyprotein entry absent |
| HCV_NS5B | Q99IB8 | no AF-DB model (404) — HCV polyprotein entry absent |
| HIV1_PR | Q9Q288 | no AF-DB model (404) — HIV-1 protease-only viral entry absent |
| HIV1_RT | P04585 | AF F1 model (155 aa) covers **0%** of the RT domain (UniProt 588–1147 of Pol) |

**Honest applicability bound established at feasibility time:** DYNAMICS3 is de-facto restricted to
bacterial/eukaryotic single-chain cores. Strain-specific viral proteins are largely missing from
AlphaFold-DB, and multi-domain viral **polyprotein** entries' F1 fragment does not cover the mature
drug-target domain. This does NOT affect the core use case (undrugged bacterial cores such as ispE),
which is fully covered.
