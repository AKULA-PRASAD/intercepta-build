# CRISPRIDESIGN1 — SUMMARY

**What this is:** a TURNKEY, collaborator-ready **in-silico DESIGN** of a CRISPRi (dCas9) essentiality-validation experiment
for INTERCEPTA flagship antibacterial targets in *E. coli* K-12 MG1655 — the first wet-lab rung of docs/EXPERIMENTAL_VALIDATION.md
Tier 1. **NOT a performed experiment; guides are predicted, not validated; predicted efficiency is a heuristic, not measured.**

## Result
- **Real sequences.** Genome + all-CDS nucleotide fetched from NCBI RefSeq **NC_000913.3** (genome = 4,641,652 bp, asserted).
  SHA-256: genome `6b195fed…`, CDS `e0a1f542…`. Each target CDS is asserted to match its genome slice (valid ATG/stop) before design.
- **Integrity correction (truth over vision):** the brief's `dxr = b0420` is **wrong — b0420 is `dxs`** (a different MEP enzyme).
  The real fosmidomycin target dxr/ispC is **b0173** (P45568), used here so the fosmidomycin chemical control is valid.
- **12 specificity-passing sgRNAs** (3 per target × 4 targets) + 1 verified non-targeting control. Every guide: base-pairs with
  the **non-template/coding strand** (Qi 2013 orientation, verified independently), within the **first ~30% of the ORF**,
  GC 30–70%, no poly-T, and **0 perfect AND 0 ≤2-mismatch off-targets** genome-wide (both strands, PAM-adjacent).
- Ready-to-order **cloning oligos** provided (example BsaI CACC/AAAC Golden-Gate scar; collaborator must confirm for their vector).
- **PROTOCOL.md** is the clean, ~2-page collaborator-facing document (targets, sequences, strain/plasmids, procedure, gate,
  fosmidomycin cross-check, ~$200–400, ~2–3 weeks, honest caveats).

## Top guides (guide 1 per target; full set in results JSON)
| Target | Protospacer 5'→3' | PAM | ORF pos | GC | off-targets |
|---|---|---|---|---|---|
| dxr/ispC (b0173) | `ATCGTCCATTACGGCATAGC` | GGG | 12.9% | 50% | 0 perfect / 0 ≤2mm |
| murA (b3189) | `CTTTCAGTTTCGGGACGTTC` | TGG | 9.9% | 50% | 0 perfect / 0 ≤2mm |
| ftsZ (b0095, +ctrl) | `GCGTCATTGGTAAGTTCCAT` | TGG | 1.0% | 45% | 0 perfect / 0 ≤2mm |
| lacZ (b0344, −ctrl) | `GGCCAGTGAATCCGTAATCA` | TGG | 0.2% | 50% | 0 perfect / 0 ≤2mm |
| non-targeting | `ACGGAGGCTAAGCGTCGCAA` | — | — | 60% | 0 perfect / 0 ≤2mm |

## Pre-registered gate (restated from Tier 1)
- **SUCCESS:** targeting sgRNA reduces final OD600/CFU **≥5× vs non-targeting** (p<0.01, n≥3), matching ftsZ; ftsZ MUST show a
  defect, lacZ MUST NOT.
- **FAILURE = first-class negative:** no defect ⇒ the essentiality prediction is wrong under these conditions; report honestly.
- **Orthogonal chemical cross-check (dxr):** fosmidomycin MIC vs MG1655.

## Reproducibility
Deterministic (regex scan + numpy mismatch count; no RNG; fixed tie-breaks). Payload SHA-256 (sorted-key JSON, excluding
provenance) = **`a0a5186e4cd5c67d08a6e54c1760581bc620a58af6bf8ad67f15e812c55ad310`**, reproduced ×2 byte-identical.

## Scope / caveats
IN-SILICO DESIGN for a wet-lab collaborator. Guide efficiency is a stated heuristic (early-ORF + GC), NOT measured. Essentiality
is a computational prediction — this experiment IS its test. CRISPRi is partial knockdown; essentiality is condition-dependent;
the vectors/overhangs are one example system. The guides REQUIRE experimental validation.

## Files
`PREREG.md` (locked rules + gate) · `run.py` (deterministic design) · `PROTOCOL.md` (collaborator-facing) ·
`results/CRISPRIDESIGN1_metrics.json` (sorted keys, full guide set + provenance) · `results/CRISPRIDESIGN1_payload.sha256`.
Data cache: `$INTERCEPTA_DATA/crispridesign1/` (fetched genome + CDS, not committed).
