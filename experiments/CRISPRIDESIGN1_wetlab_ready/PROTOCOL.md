# CRISPRi essentiality-validation experiment — *E. coli* K-12 MG1655
### Collaborator-facing, ready-to-execute protocol (~$200–400, ~2–3 weeks)

> **HONEST SCOPE — read first.** This is an **in-silico experiment DESIGN** produced computationally by the INTERCEPTA
> pipeline. It has **NOT been performed**. The sgRNAs are **predicted, not validated**; the "predicted efficiency" is a
> **heuristic** (early-ORF position + GC), **not a measurement**. Target essentiality is a **computational prediction**
> (FBA + chokepoint + cross-organism breadth, corroborated against published knockout data) — **this experiment is exactly
> the test of whether that prediction is true in a real cell.** All DNA below is REAL, taken from NCBI RefSeq **NC_000913.3**
> (not invented). Please sanity-check every sequence against your strain/vector before ordering.

---

## 1. Rationale (one paragraph)
INTERCEPTA nominates, from genome + zero drug data, a small set of essential, host-non-homologous antibacterial targets. The
top broad-spectrum picks are **dxr/ispC** (MEP isoprenoid pathway; the fosmidomycin target) and **murA** (cell-wall; the
fosfomycin target). This experiment prospectively tests whether knocking these genes down halts *E. coli* growth — the first
wet-lab confirmation that a computationally-nominated target is really essential.

## 2. Targets and controls
| Role | Gene | Locus tag | Enzyme / function | Expectation |
|---|---|---|---|---|
| **Primary** | **dxr / ispC** | b0173 | 1-deoxy-D-xylulose-5-P reductoisomerase (MEP) | growth defect on knockdown |
| **Secondary** | **murA** | b3189 | UDP-GlcNAc enolpyruvyl transferase (cell wall) | growth defect on knockdown |
| **Positive control** | **ftsZ** | b0095 | cell-division GTPase (known essential) | **MUST** show growth defect |
| **Negative control** | **lacZ** | b0344 | β-galactosidase (dispensable on glucose) | **MUST NOT** show defect |
| **Non-targeting control** | scrambled | — | no genome match (verified) | baseline (dCas9 burden only) |

> Note: the original target brief listed "dxr = b0420"; **b0420 is `dxs`** (a different MEP enzyme). The true fosmidomycin
> target dxr/ispC is **b0173** — used here so the fosmidomycin chemical cross-check is valid.

## 3. sgRNAs to order (20-nt protospacers, 5'→3')
All target the **non-template (coding) strand within the first ~30% of the ORF** (dCas9 CRISPRi strong-repression orientation,
Qi et al. 2013), have GC 30–70%, no poly-T terminator, and **0 perfect and 0 ≤2-mismatch off-targets** genome-wide against
NC_000913.3 (both strands, PAM-adjacent). Ranked by a predicted-efficiency **heuristic** (use guide 1 first; order ≥2/target
to hedge). Cloning oligos use an **EXAMPLE** BsaI Golden-Gate scar (CACC/AAAC overhangs) — **confirm the overhangs for YOUR
vector** before ordering.

### dxr / ispC (b0173) — PRIMARY
| # | Protospacer (5'→3') | PAM | ORF pos | GC | Top oligo (5'→3') | Bottom oligo (5'→3') |
|---|---|---|---|---|---|---|
| 1 | `ATCGTCCATTACGGCATAGC` | GGG | 12.9% | 50% | `CACCATCGTCCATTACGGCATAGC` | `AAACGCTATGCCGTAATGGACGAT` |
| 2 | `CATCGTCCATTACGGCATAG` | CGG | 13.0% | 50% | `CACCCATCGTCCATTACGGCATAG` | `AAACCTATGCCGTAATGGACGATG` |
| 3 | `CGCGGAAGTGTTCGGGATTA` | TGG | 5.7%  | 55% | `CACCCGCGGAAGTGTTCGGGATTA` | `AAACTAATCCCGAACACTTCCGCG` |

### murA (b3189) — SECONDARY
| # | Protospacer (5'→3') | PAM | ORF pos | GC | Top oligo (5'→3') | Bottom oligo (5'→3') |
|---|---|---|---|---|---|---|
| 1 | `CTTTCAGTTTCGGGACGTTC` | TGG | 9.9% | 50% | `CACCCTTTCAGTTTCGGGACGTTC` | `AAACGAACGTCCCGAAACTGAAAG` |
| 2 | `CGGAAATTGTGACTTCGCCC` | TGG | 3.0% | 55% | `CACCCGGAAATTGTGACTTCGCCC` | `AAACGGGCGAAGTCACAATTTCCG` |
| 3 | `AGTAGTGCGGCAAAAAGGAT` | AGG | 6.4% | 45% | `CACCAGTAGTGCGGCAAAAAGGAT` | `AAACATCCTTTTTGCCGCACTACT` |

### ftsZ (b0095) — POSITIVE control (must show defect)
| # | Protospacer (5'→3') | PAM | ORF pos | GC | Top oligo (5'→3') | Bottom oligo (5'→3') |
|---|---|---|---|---|---|---|
| 1 | `GCGTCATTGGTAAGTTCCAT` | TGG | 1.0% | 45% | `CACCGCGTCATTGGTAAGTTCCAT` | `AAACATGGAACTTACCAATGACGC` |
| 2 | `GACTTTAATCACCGCGTCAT` | TGG | 2.2% | 45% | `CACCGACTTTAATCACCGCGTCAT` | `AAACATGACGCGGTGATTAAAGTC` |

### lacZ (b0344) — NEGATIVE control (must NOT show defect)
| # | Protospacer (5'→3') | PAM | ORF pos | GC | Top oligo (5'→3') | Bottom oligo (5'→3') |
|---|---|---|---|---|---|---|
| 1 | `GGCCAGTGAATCCGTAATCA` | TGG | 0.2% | 50% | `CACCGGCCAGTGAATCCGTAATCA` | `AAACTGATTACGGATTCACTGGCC` |
| 2 | `CGATTAAGTTGGGTAACGCC` | AGG | 2.0% | 50% | `CACCCGATTAAGTTGGGTAACGCC` | `AAACGGCGTTACCCAACTTAATCG` |

### NON-TARGETING control (no genome match)
| Protospacer (5'→3') | GC | Top oligo (5'→3') | Bottom oligo (5'→3') |
|---|---|---|---|
| `ACGGAGGCTAAGCGTCGCAA` | 60% | `CACCACGGAGGCTAAGCGTCGCAA` | `AAACTTGCGACGCTTAGCCTCCGT` |

> A full 3-guide-per-target set (incl. ftsZ g3, lacZ g3) is in `results/CRISPRIDESIGN1_metrics.json`.
> If your sgRNA promoter needs a +1 guanine and a spacer does not start with G, prepend a G (making it 21-nt).

## 4. Strain and plasmids (example system — substitute your lab's standard)
- **Strain:** *E. coli* K-12 MG1655 (or BW25113/MG1655-derived CRISPRi host).
- **dCas9:** an inducible dCas9 plasmid — e.g. Addgene **#44249 (pdCas9-bacteria)**, aTc-inducible.
- **sgRNA:** a compatible pgRNA backbone — e.g. Addgene **#44251 (pgRNA-bacteria)**. **NB:** the original Qi/Bikard
  pgRNA-bacteria is cloned by inverse-PCR/Gibson, *not* BsaI. The CACC/AAAC oligos above are for a **BsaI Golden-Gate** vector;
  use them only if your backbone has the matching BsaI cassette, otherwise adapt the spacer to your backbone's cloning scheme.
- Plasmid cost ≈ $65–130; oligos ≈ $20–40; media/consumables the rest. **Total ≈ $200–400.**

## 5. Procedure
1. **Clone** each spacer into the sgRNA backbone (anneal top+bottom oligos → ligate into cut backbone; or Gibson/inverse-PCR per
   your vector). Sequence-verify each insert.
2. **Co-transform** each sgRNA plasmid + the dCas9 plasmid into MG1655; select on the appropriate antibiotics.
3. **Grow** overnight, dilute 1:100 into fresh medium (defined glucose minimal or LB), split into **+inducer** (dCas9 ON) and
   **−inducer** wells, in **triplicate** per guide + all controls.
4. **Read out** growth: OD600 every 30–60 min for 8–24 h (plate reader) **and** endpoint **CFU** (serial dilution plating).
5. Compare each targeting guide to the **non-targeting** control on the same plate/day.

## 6. Pre-registered success / failure gate (locked before the run)
- **SUCCESS (target confirmed essential):** targeting sgRNA reduces final OD600 **or** CFU **≥ 5-fold vs non-targeting control**,
  **p < 0.01, n ≥ 3**, in the same direction as ftsZ.
- **Assay validity:** **ftsZ MUST** show the defect and **lacZ MUST NOT** — otherwise the assay is uninterpretable, not the gene.
- **FAILURE = a first-class negative:** no growth defect ⇒ the gene is not essential under these conditions ⇒ the computational
  prediction is **wrong** here. Report it as such — a real falsification is a valuable result, not a failed experiment.

## 7. Orthogonal chemical cross-check (dxr only)
Run a **fosmidomycin MIC / growth-inhibition** assay against MG1655 (broth microdilution). Fosmidomycin inhibits DXR, so a clear
MIC gives an **independent, drug-based** confirmation that inhibiting the predicted target impairs growth — corroborating (or
contradicting) the CRISPRi result by a completely different mechanism.

## 8. Honest caveats
- Guide **efficiency is predicted, not measured** — actual knockdown varies; ordering ≥2 guides/target hedges this.
- Essentiality is **condition-dependent** (medium, aeration). dxr/murA/ftsZ are core on standard media; lacZ is dispensable on
  glucose. Choose a medium where the pathway is required.
- CRISPRi gives **partial knockdown** (not a clean knockout); a weak-but-real defect can still be a positive if it clears the gate.
- The vectors/overhangs above are **one example system**; adapt to your lab's validated CRISPRi setup.
- Provenance: sgRNAs derived from NCBI RefSeq **NC_000913.3** (E. coli K-12 MG1655), fetched and SHA-256-logged in
  `results/CRISPRIDESIGN1_metrics.json`. Design is deterministic and reproduced ×2 byte-identical.
