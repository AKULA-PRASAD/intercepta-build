# CRISPRIDESIGN1 — PRE-REGISTRATION (design rules + success/failure gate, locked BEFORE designing)

**Scope binding (read first, applies to every line below):** this is an **IN-SILICO EXPERIMENT DESIGN / proposal** to hand a
wet-lab collaborator. It is **NOT a performed experiment, NOT validated guides**. Predicted knockdown efficiency is a stated
**heuristic**, not a measurement. The guides **REQUIRE experimental validation**. Nothing here claims the experiment has been run.

## Goal
Produce a TURNKEY, collaborator-ready CRISPRi (dCas9) essentiality-validation experiment for INTERCEPTA flagship antibacterial
targets in *E. coli* K-12 MG1655 (RefSeq **NC_000913.3**) — the first wet-lab rung of docs/EXPERIMENTAL_VALIDATION.md Tier 1.
Deterministic design (no RNG); reproduced ×2 byte-identical (SHA-256 over sorted-key JSON payload, excluding provenance).

## Targets (PRE-REGISTERED)
| role | gene | locus tag (VERIFIED against NC_000913.3) | rationale |
|---|---|---|---|
| PRIMARY | **dxr / ispC** | **b0173** (NP_414715.1, UniProt P45568) | MEP pathway; BESTINT1 multi-axis top (0.88); exp-essential ≥2/3 (PREDVAL); fosmidomycin = orthogonal chemical positive control (DXR reductoisomerase inhibitor; INTERVENE1 dxr→fosmidomycin; the 1/32 N. gonorrhoeae repurposing hit) |
| SECONDARY | **murA** | **b3189** (NP_417656.1, UniProt P0A749) | cell-wall core; fosfomycin target (INTERVENE1 recovered); exp-essential 3/3 orgs (PREDVAL) |
| CONTROL: POSITIVE-essential | **ftsZ** | **b0095** (NP_414637.1, UniProt P0A9A6) | canonical essential cell-division gene; MUST show a growth defect (assay-direction anchor) |
| CONTROL: NEGATIVE-dispensable | **lacZ** | **b0344** (NP_414878.1, UniProt P00722) | β-galactosidase; dispensable on glucose; SHOULD show NO defect |
| CONTROL: NON-TARGETING | scrambled | none (0 genome match, verified) | baseline for dCas9-burden-only effect |

**INTEGRITY CORRECTION (truth over vision):** the task brief listed `dxr = b0420`. **b0420 is `dxs`** (1-deoxy-D-xylulose-5-
phosphate *synthase*, P77488) — a DIFFERENT MEP-pathway enzyme. The real fosmidomycin target `dxr/ispC` (1-deoxy-D-xylulose-5-
phosphate *reductoisomerase*) is **b0173** (P45568), confirmed by gene name + protein annotation in the fetched NC_000913.3 CDS
set. We use the biologically correct **b0173** and flag the discrepancy. (dxs/b0420 is also a validated MEP target but is NOT the
fosmidomycin target, so using it would break the orthogonal chemical control.)

## Sequence provenance (REAL — fetched, not invented)
- Source: NCBI RefSeq, `efetch nuccore NC_000913.3` — full genome FASTA + all-CDS nucleotide (`fasta_cds_na`).
- Files (in `$INTERCEPTA_DATA/crispridesign1/`) with SHA-256 recorded in results at run time. Genome length asserted = 4,641,652 bp.
- Target CDS coordinates/strands are PARSED from the fetched CDS headers at run time (not hardcoded) and each CDS is asserted to
  match the corresponding genome slice (start=ATG, valid stop) before any guide is designed. If the assertion fails → abort.

## sgRNA DESIGN RULES (deterministic; LOCKED before designing)
1. **Strand (CRISPRi ORF rule, Qi et al. Cell 2013):** the sgRNA must **base-pair with the NON-TEMPLATE (coding) strand** for
   strong repression → operationally, scan the **template strand** (5'→3') of the CDS for a 20-nt protospacer immediately 5' of an
   **NGG PAM** on the template strand. (Protospacer + PAM on template strand ⟺ sgRNA anneals to the non-template strand.) Every
   emitted guide is asserted to satisfy this by construction.
2. **Position:** the protospacer's 5'-most coding base must fall within the **first 30% of the ORF** (early-ORF / promoter-proximal;
   earlier = predicted-stronger). Protospacer must lie fully within the CDS.
3. **Length / PAM:** exactly **20-nt protospacer**, PAM = **NGG** immediately 3' on the template strand.
4. **GC content:** **30–70%** inclusive.
5. **No terminator:** reject any protospacer containing a run of **≥4 T (TTTT)** (RNA-Pol terminator / synthesis risk).
6. **SPECIFICITY (hard gate):** genome-wide search of BOTH strands of NC_000913.3 for the 20-nt protospacer adjacent to an NGG PAM,
   allowing ≤2 mismatches. **Require exactly one 0-mismatch PAM-adjacent site (the intended on-target) ⇒ 0 perfect off-targets.**
   Report the count of ≤2-mismatch PAM-adjacent sites. A guide with ANY perfect genomic off-target is rejected.
7. **Predicted-efficiency HEURISTIC (stated, NOT measured):** `eff = mean(pos_score, gc_score)` where
   `pos_score = 1 − frac5prime/0.30` (start of ORF → 1.0) and `gc_score = clip(1 − |GC−0.50|/0.20, 0, 1)` (peak at 50% GC).
   No poly-T (hard filter). Deterministic tie-break: higher eff, then earlier frac5prime, then lexicographic spacer.
8. **Output:** top **2–3** passing guides per target (0 perfect off-targets), ranked by the heuristic, + one **non-targeting**
   control (deterministic scrambled 20-nt, GC 30–70%, no TTTT, verified 0 perfect and reporting its ≤2-mismatch genomic count).
9. **Cloning oligos (EXAMPLE vector — clearly labeled):** BsaI Golden-Gate scar with the common **CACC / AAAC** 4-nt overhangs:
   `top = 5'-CACC-[spacer]-3'`, `bottom = 5'-AAAC-[revcomp(spacer)]-3'`. Noted: if the sgRNA promoter requires a +1 G and the
   spacer does not begin with G, prepend a G. **The collaborator MUST confirm the exact overhangs for their chosen vector** (e.g.
   Addgene pdCas9 #44249 + pgRNA-bacteria #44251 use Gibson/inverse-PCR, not BsaI) — the BsaI/CACC-AAAC scar is one common example.

## READOUT + PRE-REGISTERED GATE (restated from docs/EXPERIMENTAL_VALIDATION.md Tier 1)
- System: *E. coli* K-12 MG1655 + inducible **dCas9** (CRISPRi) + one sgRNA plasmid per condition; targeting sgRNA vs
  non-targeting control sgRNA; positive control ftsZ; negative control lacZ. Induce dCas9; measure **OD600 growth curve + CFU**;
  **n ≥ 3 (triplicate)**.
- **SUCCESS (per targeting guide):** targeting sgRNA reduces final OD600 (or CFU) **≥ 5-fold vs non-targeting control**
  (**p < 0.01, n ≥ 3**), matching ftsZ's direction (ftsZ MUST show the defect; lacZ MUST NOT).
- **FAILURE / first-class negative:** no growth defect (dispensable-like) ⇒ the essentiality prediction is WRONG under these
  conditions → report honestly as a negative (this is a genuine, valuable falsification, not a discarded result).
- **Orthogonal chemical cross-check (dxr only):** fosmidomycin **MIC / growth-inhibition** assay vs *E. coli* MG1655
  (fosmidomycin inhibits DXR) — an independent, drug-based confirmation that inhibiting the predicted target impairs growth.
- Est. cost **~$200–400**, ~**2–3 weeks**, standard molecular-microbiology bench.

## Reproducibility
Deterministic (regex scan + numpy mismatch count; no RNG; fixed tie-breaks). `run.py` run twice → payload SHA-256 must match
byte-identical. Payload = sorted-key JSON of {design rules, targets+provenance, guides, controls, gate}, EXCLUDING provenance
(git sha / timestamp / runtime).
