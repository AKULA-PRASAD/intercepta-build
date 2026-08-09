# DYNAMICS1 — Drug-contact-residue mutational tolerance as a resistance-liability signal (PRE-REGISTRATION)

**Frozen BEFORE any ESM scoring.** Author: DYNAMICS1 module. Env: miniforge `intercepta`
(torch 2.10 + transformers 4.41, CPU-only, offline HF cache). Zero budget. Data →
`$INTERCEPTA_DATA/dynamics1/`; NEVER committed.

## Gap / motivation (the AMR1 follow-on)
AMR1 (LEDGER, reproduced x2, sha 7e5be558) tested whether **static WHOLE-PROTEIN biology**
(conservation / mutational tolerance + prodrug + paralog + bypass) separates documented
HIGH- vs LOW-resistance-liability antibacterial targets. **NEGATIVE: composite AUROC 0.556,
MWU p 0.74**; no feature beat chance (F1 whole-protein conservation-tolerance 0.569). The
honest bound named the follow-on verbatim: *"resistance-liability needs a DYNAMICS signal,
e.g. active-site mutational scanning / evolvability."* The failure mode was crystallised by
**rpsL**: it is the MOST whole-protein-conserved target in the set yet is HIGH-liability,
because its streptomycin-**contact** residue (K43-equivalent) mutates freely.

## Hypothesis (the residue-specific signal AMR1 missed)
Resistance liability is set NOT by whole-protein conservation but by the **mutational
tolerance of the specific DRUG-CONTACT residues**: can the pathogen mutate the residues that
touch the drug without losing protein function? **HIGH-liability** targets (rpoB, gyrA, rpsL…)
have drug-contact residues that are mutationally **TOLERANT** (escape mutations accessible);
**LOW/durable** targets have drug-contact residues that are catalytically **CONSTRAINED**
(can't mutate without losing function). This is residue-specific dynamics, distinct from
AMR1's failed whole-protein signal.

## Ground truth (REUSED verbatim from AMR1 `ground_truth.json`)
n = 17 cited targets, 9 HIGH / 8 LOW. HIGH = rpoB, gyrA, parC, rpsL, katG, inhA, embB, pncA,
folP. LOW = murA, alr, ddlB, dxr, murG, mraY, murB, murF. Labels are the held-out truth; the
model input is ONLY the structure + protein sequence (NO resistance rate/MIC/label used as input).

## FEASIBILITY GATE (see FEASIBILITY.md — resolved BEFORE this scoring section was run)
For each target, a DRUG-BOUND (or functionally-liganded) experimental PDB structure is
identified; DRUG-CONTACT residues = protein residues with any heavy atom within **4.5 Å** of
any heavy atom of the bound ligand. **PROCEED iff drug-contact residues can be assigned for
≥ 10 of 17 targets, balanced across HIGH/LOW (≥ 4 each).** Else declare DATA-INFEASIBLE.
**Resolved: FEASIBLE — 15/17 assigned (7 HIGH, 8 LOW).** katG and pncA are INFEASIBLE
(no drug-bound structure exists: KatG deposits carry heme only, PncA is apo / pyrazinamide
binds only unrelated proteins) — both are prodrug-ACTIVATORS, the case where a "drug-contact
residue" is least defined; their exclusion is mechanistically coherent and pre-declared here.

### FROZEN structure/ligand table (PDB ID + ligand CCD + ligand type)
| gene | label | PDB | ligand (CCD) | ligand type |
|---|---|---|---|---|
| rpoB | HIGH | 1I6V | RFP (rifampicin) | drug |
| gyrA | HIGH | 2XCT | CPF (ciprofloxacin) | drug |
| parC | HIGH | 3RAE | LFX (levofloxacin) | drug |
| rpsL | HIGH | 1FJG | SRY (streptomycin) | drug |
| inhA | HIGH | 1ZID | ZID (isonicotinyl-NAD adduct) | drug |
| embB | HIGH | 7BVF | 95E (ethambutol) | drug |
| folP | HIGH | 1AJ0 | SAN (sulfanilamide) | drug |
| murA | LOW | 1UAE | FFQ (fosfomycin) | drug |
| dxr | LOW | 1ONP | FOM (fosmidomycin) | drug |
| alr | LOW | 1EPV | DCS (D-cycloserine–PLP adduct) | drug |
| ddlB | LOW | 2DLN | PHY (phosphinate TS-analog) | inhibitor |
| mraY | LOW | 5CKR | 57M (muraymycin D2) | inhibitor |
| murF | LOW | 2AM1 | 1LG (benzamide inhibitor) | inhibitor |
| murG | LOW | 1NLM | UD1 (UDP-GlcNAc substrate) | substrate |
| murB | LOW | 2MBR | EPU (EP-UDP-GlcNAc substrate) | substrate |

## Contact assignment (deterministic geometry; frozen)
Parse `_atom_site` from the mmCIF. Heavy atoms only (drop H/D); first altloc only. Protein
residue = standard AA or a mapped modified residue (MSE→M, KCX→K, …) bearing a `label_seq_id`.
Contact = protein residue with min heavy-atom distance ≤ **4.5 Å** to any atom of the frozen
ligand CCD (any copy). **Scoring chain** = the single `label_asym_id` with the most contact
residues (ties → lexicographic). Contact set = that chain's contact residues. The chain's
ESM sequence = its modelled residues ordered by `label_seq_id` (unmodelled gaps omitted);
contacts mapped to indices in that sequence.

## ESM-2 mutational-tolerance metric (FROZEN, primary)
Model: `facebook/esm2_t30_150M_UR50D` (cached), CPU, eval, `torch.manual_seed(0)`, float32.
If chain length > 1022, take the contiguous 1022-residue window centred on the median contact
index (clipped to ends); all contacts fit within one drug pocket so remain in-window.

**Per-contact-residue tolerance = masked-marginal Shannon entropy.** For each contact residue:
mask that single position, run one forward pass, take the model logits at that position,
softmax over the **20 canonical amino-acid tokens only** → distribution p; tolerance = Shannon
entropy H = −Σ_a p_a ln p_a (nats). High H ⇒ position accepts many residues ⇒ mutationally
TOLERANT ⇒ more resistance-liable.

**Target-level durability feature = MEAN masked-marginal entropy over the target's contact
residues** (higher = MORE liability). This is the PRIMARY score.

Secondary (reported, not gated): (a) MAX contact entropy; (b) mean substitution-LLR
= mean over contacts of [mean over 19 non-WT AAs of (ln p_mut − ln p_wt)] (higher = more
tolerant); (c) rpsL K43-equivalent per-residue entropy (mechanistic check).

## Pre-registered hypothesis & gate (frozen BEFORE scoring)
**H1:** mean drug-contact-residue masked-marginal entropy separates HIGH- from LOW-liability
targets, in the direction higher-entropy→HIGH.
**Primary metric:** AUROC(mean-contact-entropy vs HIGH=1) over the feasible targets; two-sided
Mann-Whitney U p.
**PASS iff:** AUROC ≥ **0.75** AND MWU p < **0.05** AND AUROC > **0.556** (must beat AMR1's
whole-protein signal). All three required.
**NEGATIVE (first-class):** otherwise → even residue-specific dynamics (from a static
structure + a PLM) do NOT predict resistance liability → deeper bound: true evolvability needs
fitness/experimental data, not a static structure + PLM proxy.

## Mandatory analyses (reported regardless of verdict)
1. Primary AUROC + MWU p (all 15 feasible) + explicit contrast vs AMR1's 0.556 / p 0.74.
2. Per-target mean & max contact entropy; per-target n_contacts; rpsL K43-equiv entropy.
3. Ligand-type sensitivity: (A) drop pure substrates murG,murB → 13 targets; (B)
   clinical-drug-bound only (7 HIGH + murA,dxr,alr) → 10 targets (7 HIGH / 3 LOW).
   Reported to expose the drug-vs-substrate contact confound honestly.
4. Secondary metrics (max-entropy AUROC, substitution-LLR AUROC).

## Reproducibility
SHA-256 over sorted-key JSON of the `payload` (per-target features + all AUROC/p),
EXCLUDING verdict/provenance/runtime. Entropies rounded to 6 decimals in the payload.
Structures + ESM logits cached under `$INTERCEPTA_DATA/dynamics1/`. Run twice; require
BYTE-IDENTICAL. No git commit.

## Honest scope (binds the result BEFORE it is known)
Small n (≤15; 7H/8L) → a demonstration / bound, NOT a population estimate; wide AUROC CI.
ESM masked-marginal entropy is a PLM proxy for mutational tolerance, NOT measured fitness.
A single static structure's contacts may miss induced-fit / allosteric / efflux / target-
bypass resistance. Ligand-type is heterogeneous (clinical drugs for all HIGH; drugs +
research inhibitors + substrates for LOW) → a real drug-vs-substrate confound, quantified in
the sensitivity analyses. Not tuned to pass; if it fails the gate, the NEGATIVE is the result.
