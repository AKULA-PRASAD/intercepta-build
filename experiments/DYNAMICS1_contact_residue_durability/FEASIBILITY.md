# DYNAMICS1 — FEASIBILITY GATE (resolved BEFORE ESM scoring)

**Question:** can DRUG-CONTACT residues (protein heavy atom ≤ 4.5 Å from a bound ligand) be
assigned from an experimental PDB structure for ≥ 10 of the 17 AMR1 targets, balanced across
HIGH/LOW (≥ 4 each)?

**Verdict: FEASIBLE — 15/17 assigned (7 HIGH, 8 LOW).** Exceeds the ≥10 / ≥4-each threshold.

## Method
mmCIF fetched from RCSB `files.rcsb.org` (browser UA; all HTTP 200). Ligand identity for every
structure verified against the RCSB chemcomp API (name + formula). Contact residues extracted
by a deterministic self-contained `_atom_site` parser (heavy atoms only, first altloc):
protein residue with min heavy-atom distance ≤ 4.5 Å to any atom of the frozen ligand CCD.
Scoring chain = the `label_asym_id` with the most contacts.

## Assigned targets (FROZEN table)
| gene | label | PDB | ligand (verified) | ligand type | chain | n_contacts | key contact(s) |
|---|---|---|---|---|---|---|---|
| rpoB | HIGH | 1I6V | RFP rifampicin | drug | C | 18 | RRDR (Ser389–Arg409) |
| gyrA | HIGH | 2XCT | CPF ciprofloxacin | drug | A | 6 | QRDR region |
| parC | HIGH | 3RAE | LFX levofloxacin | drug | D | 4 | Arg456/Glu474 (topo IV) |
| rpsL | HIGH | 1FJG | SRY streptomycin | drug | M | 4 | **Lys46/Lys47/Lys91 (S12; K43-equiv)** |
| inhA | HIGH | 1ZID | ZID INH-NAD adduct | drug | A | 30 | NAD/acyl pocket |
| embB | HIGH | 7BVF | 95E ethambutol | drug | A | 12 | **Met306** (resistance hot-spot) |
| folP | HIGH | 1AJ0 | SAN sulfanilamide | drug | A | 8 | pterin/sulfa site |
| murA | LOW | 1UAE | FFQ fosfomycin | drug | A | 13 | **Cys115** (fosfomycin target) |
| dxr | LOW | 1ONP | FOM fosmidomycin | drug | A | 14 | MEP/metal site |
| alr | LOW | 1EPV | DCS D-cycloserine–PLP | drug | A | 20 | PLP/catalytic site |
| ddlB | LOW | 2DLN | PHY phosphinate TS-analog | inhibitor | A | 19 | ATP/D-Ala site |
| mraY | LOW | 5CKR | 57M muraymycin D2 | inhibitor | A | 23 | translocase active site |
| murF | LOW | 2AM1 | 1LG benzamide inhibitor | inhibitor | A | 22 | inhibitor pocket |
| murG | LOW | 1NLM | UD1 UDP-GlcNAc | substrate | A | 20 | substrate site |
| murB | LOW | 2MBR | EPU EP-UDP-GlcNAc | substrate | A | 26 | FAD/substrate site |

## INFEASIBLE (2/17) — honestly declared
- **katG** (HIGH, isoniazid): no isoniazid-bound deposit exists; KatG structures (e.g. 2CCA,
  4C50) carry only the **heme** cofactor. isoniazid has no free-ligand CCD in the used deposits.
- **pncA** (HIGH, pyrazinamide): Mtb PncA deposits are apo (e.g. 3PL1); the pyrazinamide CCD
  **PZA** appears only in unrelated proteins (bovine/goat lactoperoxidase, human HSP70), not in
  a pyrazinamidase.

Both dropped targets are prodrug-**ACTIVATORS** whose HIGH liability is driven by loss-of-
function of a dispensable activator, NOT by drug-contact-residue escape — so a "drug-contact
residue" is the least well-defined for exactly these two, making their exclusion
mechanistically coherent rather than a cherry-pick.

## Honest confound (pre-declared, carried into the scoring sensitivities)
Ligand type is heterogeneous: all 7 HIGH are clinical drugs; the 8 LOW mix clinical drugs
(murA fosfomycin, dxr fosmidomycin, alr D-cycloserine), research inhibitors (mraY, murF, ddlB),
and pure substrates (murG, murB). Substrate/cofactor contacts are catalytically constrained by
construction. Two sensitivity subsets isolate this: drop-substrates (13) and clinical-drug-only
(10; 7 HIGH / 3 LOW).

## Data provenance
Structures cached at `$INTERCEPTA_DATA/dynamics1/structures/` (never committed). Ligand names
verified via `https://data.rcsb.org/rest/v1/core/chemcomp/{CCD}`.
