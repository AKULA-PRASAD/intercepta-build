# DYNAMICS4 FEASIBILITY — UniProt functional-site annotation availability (resolved BEFORE gate scoring)

Source: UniProt REST `.json` per accession (frozen DYNAMICS3 SIFTS `ACC` map), features of type
{Active site, Binding site, Site}, residue ranges enumerated, restricted to the crystal domain span.
Fetched + cached under `$INTERCEPTA_DATA/dynamics4/uniprot/`. NO residues fabricated.

## Per-target functional-site residue count (within crystal domain span)

| gene | acc | span | n_func | annotated residues (UniProt numbering) | feasible (>=3)? |
|---|---|---|---|---|---|
| embB | P9WNL7 | 1–1098 | 0 | — | NO (no annotation) |
| rpoB | Q9KWU7 | 1–1119 | 0 | — | NO (no annotation) |
| rpsL | Q5SHN3 | 1–132 | 0 | — | NO (no annotation) |
| HIV1_PR | Q9Q288 | 1–99 | 0 | — | NO (no annotation) |
| gyrA | Q99XG5 | 2–491 | 1 | 123 (active-site Tyr, DNA cleavage) | NO (<3) |
| alr | P10724 | 2–388 | 4 | 39,136,265,312 | yes |
| murB | P08373 | 3–342 | 4 | 159,190,229,325 | yes |
| HCV_NS3 | A8DG50 | 1013–1208 | 4 | 1123,1125,1171,1175 | yes |
| HCV_NS5B | Q99IB8 | 2443–3012 | 4 | 2443,2662,2760,2761 | yes |
| CYP51_Ca | P10613 | 49–528 | 5 | 64,118,307,377,470 | yes |
| FLU_PA | C3W5S0 | 1–198 | 6 | 41,80,108,119,120,134 | yes |
| parC | Q59961 | 404–647 | 7 | 433,458,461,506,508,513,629 | yes |
| murD | P14900 | 2–438 | 7 | 112–118 | yes |
| murF | Q8DNV6 | 1–454 | 7 | 107–113 | yes |
| mraY | O66465 | 1–359 | 9 | 70,75,190,193,196,264,268,305,321 | yes |
| inhA | P9WGR1 | 2–269 | 10 | 20,21,64,65,95,96,149,158,165,194 | yes |
| FLU_NA | Q6DPL2 | 63–449 | 13 | 98,131,132,257,258,273,274,278,304,322,324,348,382 | yes |
| HIV1_RT | P04585 | 588–1147 | 13 | 588,697,772,773,988,1001,1027,1028,1030,1065,1085,1136,1147 | yes |
| HSV1_TK | P0DTH5 | 46–376 | 13 | 56–63,83,101,125,216,222 | yes |
| folP | P0AC13 | 1–282 | 14 | 22,28,61,62,96,115,185,190,221,222,223,255,256,257 | yes |
| murA | P0A749 | 1–419 | 15 | 22,23,91,115,120–124,160–163,305,327 | yes |
| murG | P17443 | 2–355 | 15 | 15,16,17,127,163,191,244,263–268,287,288 | yes |
| dxr | P45568 | 1–398 | 20 | 10–13,36,37,38,124–126,150–152,186,209,215,222,227,228,231 | yes |
| murE | P22188 | 2–495 | 25 | 27,29,44,45,46,116–122,157,158,159,185,191,193,390,414–417,465,469 | yes |
| glmU | P0ACC7 | 1–456 | 26 | 11–14,25,76,81,82,103–105,140,154,169,227,333,351,363,366,377,380,386,387,405,423,440 | yes |
| ddlB | P07862 | 1–306 | 61 | 15,134–189,257,270,272,281 (ATP-grasp region) | yes |

## Feasibility verdict
**FEASIBLE: 21 / 26 (>= 15 required → PROCEED to gates).**
**INFEASIBLE: 5** — embB, rpoB, rpsL, HIV1_PR (zero UniProt functional-site annotation), gyrA (1 < 3).

## Honest interpretation of the 5 infeasible (a real applicability bound, not hidden)
The annotation method cannot score targets UniProt does not annotate with a classic Active/Binding/
catalytic Site: **rpoB** (RNA-polymerase β; rifampicin binds the RNA exit channel, not an annotated
enzymatic site), **rpsL** (ribosomal protein S12; streptomycin binds the 16S rRNA decoding site),
**embB** (arabinosyltransferase; large integral-membrane transferase, unannotated), **HIV1_PR**
(this SIFTS-resolved accession Q9Q288 carries no site features), **gyrA** (only the DNA-cleavage
active-site Tyr123 is annotated — the fluoroquinolone QRDR is not a UniProt binding site). These are
exactly the "drug binds a non-catalytic interface" cases flagged in PREREG scope. Note 4 of the 5
excluded are HIGH-liability targets whose crystal durability was high — dropping them makes the G2
discrimination test HARDER, not easier (reported as-is, not tuned).

## Head-to-head crystal-site-overlap set (numbering-aligned bacterial/eukaryotic)
Overlap is compared to fpocket only where crystal auth_seq == UniProt numbering (DYNAMICS3-feasible,
cov=1.0). Intersection = 16 targets: folP, inhA, parC, CYP51_Ca, HSV1_TK, alr, ddlB, dxr, glmU, mraY,
murA, murB, murD, murE, murF, murG. The 5 viral feasible targets (FLU_NA, FLU_PA, HCV_NS3, HCV_NS5B,
HIV1_RT) are scored for G1/G2 but excluded from the overlap head-to-head (polyprotein/mature
numbering offset makes residue-number overlap non-comparable — not fabricated).
</content>
