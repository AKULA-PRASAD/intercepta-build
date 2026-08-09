# DYNAMICS2 — FEASIBILITY (resolved BEFORE any ESM scoring of the expanded set)

The FROZEN DYNAMICS1 contact-extraction (`extract_contacts`, ≤4.5 Å heavy-atom, most-contacted
`label_asym_id`) was run on each NEW target's drug-bound PDB to confirm: (i) the named drug ligand
CCD has atoms in the file; (ii) a protein scoring chain is assignable; (iii) drug-contact residues
are found; and (iv) the documented resistance residue(s) appear among the contacts (a mechanistic
sanity check, NOT part of the scoring). **All 11 new targets are FEASIBLE.** The 15 DYNAMICS1
targets were already feasible (their structures are reused verbatim). Total scored set = 26.

Ligand identity of every new PDB was verified from the mmCIF `_struct.title` + the RCSB
chemical-component name for the frozen CCD (not assumed):

| target | PDB | title (verbatim, abbreviated) | frozen ligand CCD → chem name | chain | n_lig atoms | n_contacts | resistance residue present as contact |
|---|---|---|---|---|---|---|---|
| HIV-1 RT | 1VRT | "HIGH RESOLUTION STRUCTURES OF HIV-1 RT … RT-INHIBITOR COMPLEXES" | NVP → nevirapine | A | 20 | 16 | K103,Y181,Y188,L100,G190 ✓ |
| HIV-1 protease | 1OHR | "VIRACEPT (NELFINAVIR) … INHIBITOR OF HIV-1 PROTEASE" | 1UN → nelfinavir | A | 40 | 15 | D30,V82,I84 ✓ |
| Influenza N1 NA | 2HU4 | "N1 neuraminidase in complex with oseltamivir" | G39 → oseltamivir carboxylate | A | 160 | 18 | R292,N294 ✓ |
| HCV NS3/4A | 3SV6 | "NS3/4A protease in complex with Telaprevir" | SV6 → telaprevir | A | 49 | 19 | R155,A156,D168 ✓ (exact triad) |
| Candida CYP51/Erg11 | 5FSA | "CYP51 from Candida albicans … posaconazole" | X2N → posaconazole | A | 102 | 29 | Y132,F126 ✓ |
| Influenza PA endonuclease | 6FS6 | "Influenza A/California/04/2009 endonuclease … baloxavir acid" | E4Z → baloxavir acid | E | 204 | 17 | I38 ✓ (exact baloxavir I38T residue) |
| HSV-1 thymidine kinase | 1KI2 | "THYMIDINE KINASE FROM HSV-1 COMPLEXED WITH GANCICLOVIR" | GA2 → ganciclovir | A | 36 | 14 | Q125,R163,A168 ✓ |
| HCV NS5B polymerase | 4WTG | "HCV NS5B … IN COMPLEX WITH SOFOSBUVIR DIPHOSPHATE GS-607596, MN2+ …" | 6GS → 2'-F-2'-Me-uridine-5'-diphosphate | C | 26 | 14 | S282 ✓ (S282T durability residue) + GDD D318/D319/D220 |
| MurD | 3UAG | "UDP-N-ACETYLMURAMOYL-L-ALANINE:D-GLUTAMATE LIGASE" | UMA → UDP-MurNAc-Ala substrate | A | 49 | 25 | — (undrugged durable core) |
| MurE | 1E8C | "Structure of MurE … UDP-N-acetylmuramyl tripeptide synthetase from E. coli" | UAG → UDP-MurNAc-tripeptide | A | 114 | 23 | — (undrugged durable core) |
| GlmU | 1HV9 | "STRUCTURE OF E. COLI GLMU …" | UD1 → UDP-GlcNAc substrate | B | 78 | 30 | — (undrugged durable core) |

Notes:
- **1VRT** contains a modified cysteine (CSD) that is NOT in DYNAMICS1's frozen residue map; per the
  frozen behavior it is omitted as a gap. CSD is NOT among the NVP contacts, so the contact set is
  unaffected. No code change was made to accommodate it (the metric stays frozen).
- **4WTG** is a crystallization construct with engineered thermostabilizing mutations
  (S15G/E86Q/E87Q/C223H/V321I) and a Δ8 β-hairpin deletion; contact residue 223 is therefore an
  engineered His, but the durability residue S282 and catalytic GDD are wild-type and present.
  It is the only NS5B structure with the sofosbuvir-derived nucleotide in the active site
  (documented caveat, pre-declared in PREREG.md).
- Structures fetched from RCSB (`files.rcsb.org`, browser UA) to
  `$INTERCEPTA_DATA/dynamics2/structures/` (computational, not wet-lab; never committed).
- The 15 DYNAMICS1 CIFs were copied into the same directory so the run is self-contained and
  independently reproduces DYNAMICS1's per-target features (a frozen-metric cross-check).
