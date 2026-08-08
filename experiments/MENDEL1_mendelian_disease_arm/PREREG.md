# MENDEL1 — Pre-registration (FROZEN before scoring)

**Arm:** Wave-B new-disease-class coverage — human **germline monogenic (Mendelian)** disease.
**Capability under test:** intervention-**MODE** classification + small-molecule **feasibility/druggability triage** with **fail-safe abstention**, from the *causal gene + its established molecular consequence alone*.

## Why this is a DIFFERENT zero-data shape (and not a repeat of DEPEND1/F3CLIN1/INTERVENE1-2)
For Mendelian disease the causal gene is genetically ESTABLISHED (OMIM/ClinVar/UniProt). So the task is NOT "find the target from nothing" — that was popularity-confounded and near-random for human single-disease target-ID (DEPEND1/F3CLIN1 line). The task is: *given the proven causal gene, reason to a credible INTERVENTION MODE and honestly triage whether a small molecule can even work* — routing the cases that require replacement/gene-therapy/ASO to ABSTAIN. The validatable deliverable is **mode reasoning + feasibility triage + honest abstention**, NOT a lead compound (the zero-shot affinity wall from HIT2/B49/B65 stands and is out of scope).

## Ground truth (committed as `ground_truth.json`, cited, n=28, no fabricated triple)
Modes (mutually exclusive prediction target): `INHIBIT_SM`, `RESTORE_SM`, `NOT_SM` (definitions in `ground_truth.json`).
Ground-truth class counts (a property of the dataset, not of any prediction): **RESTORE_SM = 11, INHIBIT_SM = 7, NOT_SM = 10** (total 28).
=> **Majority-class baseline accuracy = 11/28 = 0.393** (predict RESTORE_SM for all).
The `NOT_SM` set (the fail-safe class, n=10) = {DMD, F8, F9, GAA, IDUA, ADA, HEXA, HTT, SOD1, COL1A1}.

## Predictor features (all zero-data / cited annotations; NO "is-there-a-known-drug" feature -> no label leakage)
- `consequence` ∈ {LoF, GoF, DN, TOXIC_AGG} — from ClinVar/OMIM/UniProt disease annotation.
- `mut_class` ∈ {null, missense_misfold, missense_activating, mixed, expansion, missense_point, missense_glycine} — predominant severe-allele class.
- `protein_class` ∈ {enzyme, kinase, receptor, ion_channel, transporter, nuclear_receptor, transport_carrier, globin, secreted, structural, other} — from UniProt.
- `fpocket_drug_score` — best-pocket **Druggability Score** from fpocket run on the AlphaFold DB model (computed in `prep_structures.py`, cached). Used ONLY in the G3 arm.

## Decision logic (FROZEN — the "invention": a mechanism-first intervention-mode triage)
Constants: `DRUG_THRESH = 0.5` (fpocket standard druggability cutoff — Le Guilloux 2009; Schmidtke & Barril 2010; NOT tuned to this data).
`DRUGGABLE_CLASSES = {enzyme, kinase, receptor, ion_channel, transporter, nuclear_receptor}`.

**PRIMARY system (mechanism-only, no fpocket):** `predict(gene)`:
1. `if consequence == TOXIC_AGG:` — toxic conformer/aggregate.
   - `if protein_class in {transport_carrier, globin}: return RESTORE_SM` — a ligand-carrier protein with a native binding cavity is amenable to a **kinetic stabilizer** (Kelly-type amyloid-stabilization principle). *(Least-generalizable branch; supported by n=2 — flagged.)*
   - `else: return NOT_SM` — disordered/aggregated or repeat-expansion toxic species has no ligandable functional handle -> **silence** (ASO/siRNA), not a small molecule.
2. `elif consequence in {GoF, DN}:` — over-active / poison product.
   - `if protein_class in DRUGGABLE_CLASSES: return INHIBIT_SM`
   - `else: return NOT_SM`
3. `else (LoF):`
   - `if protein_class not in DRUGGABLE_CLASSES: return NOT_SM` — structural/secreted/scaffold LoF has no small-molecule handle -> replace/gene.
   - `elif mut_class == 'null': return NOT_SM` — a ligandable fold but **no residual protein** to potentiate/chaperone -> enzyme/factor replacement.
   - `else: return RESTORE_SM` — residual/misfolded protein -> chaperone / potentiator / cofactor / bypass.

**Known, pre-declared blind spots (predicted misses, stated BEFORE scoring so they cannot be spun later):**
- Downstream-node druggability (LoF gene, druggable node in its pathway): TSC2→mTOR, NF1→MEK, VHL→HIF2α — the gene-level triage predicts `NOT_SM` where truth is `INHIBIT_SM`. These are **safe/conservative** errors (abstain, never a false SM promise).
- Splice/paralog bypass of a null gene: SMN1→risdiplam — predicted `NOT_SM` where truth is `RESTORE_SM`. Also **safe/conservative**.
These are expected; they are the honest boundary, not a defect to hide.

## Pre-registered gates (numbers stated BEFORE scoring)
- **G1 — mode accuracy:** PRIMARY 3-class accuracy must beat majority baseline (0.393) by ≥ 0.20, i.e. **accuracy ≥ 0.60**.
- **G2 — FAIL-SAFE (HARD, decisive integrity requirement):** of the 10 true `NOT_SM` genes, the number given a confident small-molecule call (`INHIBIT_SM` or `RESTORE_SM`) must be **exactly 0** (100% correctly abstained). ANY unsafe call = G2 FAIL, regardless of G1.
- **G3 — druggability-triage value (does fpocket ADD anything?):** compute (a) AUROC of `fpocket_drug_score` alone for SM-feasible (INHIBIT_SM∪RESTORE_SM, n=18) vs NOT_SM (n=10); (b) a fpocket-augmented "Variant A" that grants a druggable handle whenever `fpocket_drug_score ≥ DRUG_THRESH` (letting the pocket override protein_class in the LoF and GoF/DN branches). **G3 PASS** iff Variant A improves balanced accuracy over PRIMARY by ≥ 0.05 **AND** introduces **no** new G2 fail-safe violations. Otherwise **G3 = NEGATIVE** (structural druggability does not add / actively harms the triage).

## Overall verdict rule (frozen)
- **PASS (new validated Mendelian coverage arm)** = G1 PASS **AND** G2 PASS (fail-safe holds). G3 reported separately (PASS = triage adds value; NEGATIVE = honest bound on structural druggability).
- **NEGATIVE (first-class, honest bound)** = G1 fail (mode not classifiable beyond baseline) **OR** G2 fail (a false small-molecule promise slips through — the triage is not fail-safe).

## Scope / honesty (frozen)
In-silico; n=28 hand-curated cited cases (small — a coverage *seed*, not a census); mode + feasibility TRIAGE only, NOT a molecule and NOT a potency claim; "sm_feasible" = a credible target-directed small-molecule mechanism is documented, NOT that it is efficacious/safe for every allele; several interventions are allele-dependent (e.g. migalastat only for amenable GLA missense) — noted per row. Reproduce ×2 byte-identical over sorted-key JSON payload (excludes verdict/provenance).
