# DYNAMICS3 — Does durability extend to PREDICTED pockets? (PRE-REGISTRATION)

**Frozen BEFORE any predicted-pocket ESM scoring.** Author: DYNAMICS3 module. Env: fpocket
(miniconda `bioinfo`) + ESM-2 (miniforge `intercepta`, torch+transformers, CPU-only, offline HF
cache). Zero budget. Data → `$INTERCEPTA_DATA/dynamics3/`; NEVER committed. NEVER git commit.

## The gap DYNAMICS3 attacks
DYNAMICS1 (PASS, sha fb6984c0) and DYNAMICS2 (FIRMED_UP, AUROC 0.827 / MWU p 0.0051, n=26) showed
that **mean ESM-2 masked-marginal Shannon entropy over DRUG-CONTACT residues** separates HIGH- from
LOW-resistance-liability targets. BUT the contact residues are defined from a **drug-BOUND crystal**.
So the signal is only computable for targets that already have a drug-bound structure — it CANNOT
score an undrugged / novel target (the actual use case), which is exactly why DURABLETARGETS1 had to
mark cores like **ispE** durability = **NA**. DYNAMICS3 asks: can we replace the crystal-defined
contact set with an fpocket-**PREDICTED** pocket on the **apo AlphaFold** structure, so durability
becomes computable for ANY target that has (or can get) a structure?

## Hypothesis (frozen)
Mean ESM-2 masked-marginal entropy over the **top fpocket pocket-lining residues of the AlphaFold
model** (a) **RECOVERS** the DYNAMICS crystal-drug-contact durability signal (agreement on the
overlap set), and (b) still **SEPARATES** HIGH vs LOW resistance-liability — so durability can be
computed for novel/undrugged targets and can fill the DURABLETARGETS1 NAs.

## FROZEN METHOD
### Target set
The DYNAMICS2 n=26 set, VERBATIM (genes, PDB, scoring chain, HIGH/LOW label, and the per-target
**crystal-drug-contact durability = mean_entropy**) are READ AT RUNTIME from
`experiments/DYNAMICS2_durability_scaleup/results/DYNAMICS2_metrics.json` (no re-scoring of the
crystal signal; it is the committed reference).

### UniProt resolution (deterministic, frozen; derived from PDBe SIFTS)
For each target, the UniProt accession = the SIFTS-mapped UniProt that maps to the DYNAMICS2 scoring
chain (`label_asym_id`) with the **largest residue span on that chain** (ties → lexicographically
smallest accession). This handles fusion/complex chains (e.g. 2XCT GyrB–GyrA fusion → GyrA dominates
→ GYRA_STAAN) and multi-protein assemblies. The resolved accessions are frozen in `run.py` (the
`ACC` dict) and documented in FEASIBILITY.md; SIFTS is NOT re-queried at run time.

### AlphaFold structure
Fetch `AF-<acc>-F1` (latest AlphaFold-DB version) from the AF-DB API and CACHE it under
`$INTERCEPTA_DATA/dynamics3/af/`; record accession + sha256. Fetching is permitted (computational).
Runs reuse the cache → byte-identical reproduction.

### fpocket predicted pocket (default parameters)
Run `fpocket -f AF-<acc>-F1.pdb` (default params). The **PRIMARY predicted pocket = pocket 1**
(fpocket's own top-ranked pocket, by pocket Score). Pocket-lining residues = the distinct protein
residues appearing in `pocket1_atm.pdb`. This is the honest choice: for a NOVEL target you do not
know which pocket is the drug site, so you must take fpocket's blind top-ranked pocket.

### Predicted-pocket durability (FROZEN metric — identical to DYNAMICS1/2)
`predicted_pocket_durability` = MEAN masked-marginal Shannon entropy (`facebook/esm2_t30_150M_UR50D`,
CPU, eval, torch.manual_seed(0), float32, window 1022 centred on median pocket index if len>1022)
over the pocket-1 lining residues, using the AlphaFold model's own sequence + numbering. The
`masked_marginal` function is copied **VERBATIM** from DYNAMICS1/2/run.py. The metric is NOT changed;
the ONLY change is that the residue set is the predicted pocket instead of crystal drug contacts.
ESM logits cached under `$INTERCEPTA_DATA/dynamics3/esm_logits/`.

## FEASIBILITY GATE (resolved in FEASIBILITY.md BEFORE the gates below are scored)
A target yields a **usable top pocket** iff: (i) an AF-DB F1 model exists for its accession AND the
F1 model covers ≥ 50% of the crystal domain span [min_unp_start, max_unp_end]; AND (ii) fpocket
returns ≥ 1 pocket whose pocket 1 has ≥ 5 distinct protein residues. **PROCEED to the gates iff
≥ 18 / 26 targets yield a usable top pocket.** Failures reported honestly (accession 404 in AF-DB,
or AF model does not cover the crystal domain).

## PRE-REGISTERED GATES (frozen BEFORE scoring predicted pockets)
Both computed over the **overlap = feasible targets** (every feasible target has a committed crystal
durability, so overlap = feasible set).
- **G1 (agreement / recovery):** Spearman ρ between `predicted_pocket_durability` and the DYNAMICS2
  `crystal-drug-contact durability` (`mean_entropy`) across feasible targets. **Require ρ ≥ 0.50 AND
  p < 0.05** (higher-entropy predicted pocket ↔ higher-entropy crystal contacts). Does the cheap
  predicted version recover the crystal signal?
- **G2 (discrimination):** AUROC(`predicted_pocket_durability` vs HIGH=1) over feasible targets, in
  the direction higher-entropy → HIGH. **Require AUROC ≥ 0.70.** Two-sided Mann-Whitney U p reported.

### VERDICT LADDER
- **PASS** = G1 AND G2 → durability extends to predicted pockets → usable for novel/undrugged targets
  → fills the DURABLETARGETS1 NAs.
- **PARTIAL** = exactly one of G1/G2 met.
- **NEGATIVE (first-class)** = neither → durability needs a real/drug-bound binding-site definition;
  fpocket's blind apo top-pocket is too noisy / not the drug site → durability stays drugged-target-only.

## SECONDARY (reported, NOT gated — to diagnose, not to rescue)
1. Pocket-vs-crystal site overlap: fraction of the crystal drug-contact residues (by AF numbering,
   where numbering is shared) recovered by pocket 1 — descriptive.
2. G1/G2 on the antibacterial-only feasible subset (the clean single-domain cores).
3. Exploratory: durability using the **highest-fpocket-druggability-score** pocket instead of the
   Score-ranked pocket 1 (reported only to show whether the top-pocket choice, not the metric, is the
   failure mode; the GATE stays on the frozen pocket-1 primary — this is a diagnostic, not a re-gate).

## APPLICATION (regardless of verdict, reported): fill the DURABLETARGETS1 NA
Compute `predicted_pocket_durability` for **ispE** (the DURABLETARGETS1 NA core; E. coli IspE,
UniProt P62615) via the identical AF+fpocket+ESM pipeline, to demonstrate the NA is now fillable
(value carries the verdict's confidence: a PASS makes it usable, a NEGATIVE makes it advisory-only).

## Reproducibility
SHA-256 over sorted-key JSON of `payload` (per-target predicted durability + pocket residues + G1/G2
+ ispE), EXCLUDING provenance/runtime. Entropies rounded to 6 decimals. AF structures, fpocket
outputs, ESM logits cached under `$INTERCEPTA_DATA/dynamics3/`. Run twice → require BYTE-IDENTICAL.
No git commit; no data committed.

## HONEST SCOPE (binds the result BEFORE it is known — carries DYNAMICS's caveats + new ones)
- ESM masked-marginal entropy is a **PLM proxy** for mutational tolerance, NOT measured fitness.
- **apo AlphaFold + fpocket** predicted pockets are NOISIER than drug-bound crystals: fpocket's
  top-ranked pocket may not be the functional/drug site (confirmed pre-freeze on murA, where the
  top pocket did not overlap the fosfomycin site). If G1 fails, that is the genuine bound.
- **AF-DB coverage is itself a limit:** strain-specific viral proteins (influenza NA/PA, HCV NS3/NS5B,
  HIV protease) are absent from AF-DB, and the HIV-1 Pol polyprotein AF model does not cover the RT
  domain — so DYNAMICS3 is de facto bacterial/eukaryotic-core-only, reported openly.
- A **positive G1 could be partly a whole-protein confound** (globally conserved proteins have low
  entropy in ANY pocket): flagged, not corrected, and discussed against the verdict.
- Not tuned to pass. If G1/G2 fail, the NEGATIVE / applicability-bound is the result.
