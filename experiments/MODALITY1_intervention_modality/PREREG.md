# MODALITY1 — Pre-registration (FROZEN before scoring)

**Arm:** the INTERVENTION half — a mechanism-first, FAIL-SAFE **intervention-MODALITY recommender** across the FULL modality taxonomy and MANY disease classes. Generalizes MENDEL1 (germline-monogenic, 3 small-molecule-centric modes) to 6 modality classes + abstention over monogenic / cancer / autoimmune / cardiometabolic / neuro / ophthalmic / hematologic disease.

**Capability under test:** from OBJECTIVE target/disease features alone — subcellular **localization**, disease **mechanism**, **druggability** (protein-class), and causal-gene-vs-downstream-node — recommend a credible intervention MODALITY, with a HARD fail-safe: never confidently recommend an INFEASIBLE modality (route those to abstention).

## Why this is a real invention and not a restatement of known drug facts
The contribution is NOT new pharmacology (every row restates a known approved modality). The contribution is a **mechanism+localization-first FEASIBILITY TRIAGE with honest abstention** that (a) recovers the approved modality far above baseline from objective features only, and (b) is provably fail-safe — it never recommends a modality that molecular reality forbids (e.g. small-molecule inhibitor for a secreted deficiency, antibody for an intracellular target, enzyme replacement for a gain-of-function, gene-addition for a dominant/toxic product). This is the intervention-half analog of the composite router's fail-safe abstention.

## Ground truth (committed as `ground_truth.json`, cited, n=43, no fabricated triple)
Modalities (mutually exclusive prediction target): `SMALL_MOLECULE_INHIBITOR`, `SMALL_MOLECULE_ACTIVATOR`, `MONOCLONAL_ANTIBODY`, `ASO_siRNA`, `ENZYME_PROTEIN_REPLACEMENT`, `GENE_THERAPY`, `ABSTAIN`.
Class counts (a property of the dataset): SM_INHIBITOR 8, MONOCLONAL_ANTIBODY 7, ASO_siRNA 7, ENZYME_PROTEIN_REPLACEMENT 7, SM_ACTIVATOR 6, GENE_THERAPY 6, ABSTAIN 2 (total 43).
=> **Majority-class baseline accuracy = 8/43 = 0.186** (predict SM_INHIBITOR for all).
`true_modality` = the mechanism-canonical / landmark APPROVED modality; multi-modality targets (a real phenomenon) list alternatives in `also_feasible`.

## Predictor features (objective / declared, NO "is-there-an-approved-X" leakage feature)
- `mechanism` ∈ {GoF, overactivity, LoF_null, LoF, LoF_misfold, dominant_negative, toxic_aggregation} — from OMIM/ClinVar/UniProt/mechanism literature.
- `localization` ∈ {secreted, cell_surface, membrane, intracellular, lysosomal} — from UniProt subcellular location.
- `protein_class` — from UniProt; `druggable` is DERIVED deterministically: `druggable = protein_class ∈ DRUGGABLE_CLASSES` (below).
- `causal_node` ∈ {causal_gene, downstream_node} — uniform (`causal_gene`) in this seed (downstream-node reasoning is MENDEL1's; excluded here by design — a disclosed scope limit).
- `bbb_cns`, `splice_addressable` — objective disease/molecular properties used ONLY in the feasibility matrix (`bbb_cns` also gates enzyme-replacement feasibility). `splice_addressable` is NOT used by the predictor, so it cannot leak into predictions.

## Decision logic (FROZEN — the invention: a mechanism+localization-first modality recommender)
Constants: `DRUGGABLE_CLASSES = {enzyme, kinase, receptor, ion_channel, transporter, nuclear_receptor, transport_carrier, globin}`; `STABILIZABLE = {transport_carrier, globin}` (native-fold proteins with a ligand cavity amenable to a kinetic/allosteric stabilizer — Kelly-type; NOT tuned to this data).

**PRIMARY recommender `recommend(mechanism, localization, protein_class, druggable)`:**
1. `if mechanism in {GoF, overactivity}:`
   - `secreted | cell_surface → MONOCLONAL_ANTIBODY` (extracellular excess → neutralize/block)
   - `membrane | intracellular → SMALL_MOLECULE_INHIBITOR if druggable else ASO_siRNA` (druggable over-active target → SM; undruggable over-abundant → lower transcript)
   - else `ABSTAIN`
2. `elif mechanism in {dominant_negative, toxic_aggregation}:`
   - `protein_class ∈ STABILIZABLE → SMALL_MOLECULE_ACTIVATOR` (native-fold stabilizer: TTR/HbS)
   - `localization == intracellular → ASO_siRNA` (lower the toxic species: HTT/SOD1)
   - else `ABSTAIN` (secreted structural dominant-negative → no route: COL1A1)
3. `elif mechanism == LoF_misfold:`
   - `druggable and localization ∈ {membrane, intracellular, lysosomal} → SMALL_MOLECULE_ACTIVATOR` (chaperone/potentiator/cofactor of residual protein)
   - else `ABSTAIN`
4. `elif mechanism in {LoF_null, LoF}:`
   - `protein_class == enzyme and localization == lysosomal → (ABSTAIN if bbb_cns else ENZYME_PROTEIN_REPLACEMENT)` (M6P uptake works systemically; fails across the BBB)
   - `localization == secreted → ENZYME_PROTEIN_REPLACEMENT` (deliver the deficient secreted/circulating protein)
   - `localization ∈ {intracellular, membrane} → GENE_THERAPY` (can't deliver a functional protein into cells → add the gene)
   - else `ABSTAIN`
5. else `ABSTAIN`.

**Feasibility matrix (FROZEN, objective — used to score the fail-safe; a modality is INFEASIBLE when molecular reality forbids it):**
- MONOCLONAL_ANTIBODY infeasible if `localization ∈ {intracellular, lysosomal}` (no extracellular epitope).
- SMALL_MOLECULE_INHIBITOR infeasible unless `mechanism ∈ {GoF, overactivity}` AND `druggable` (nothing over-active to block at a LoF target; needs a pocket).
- SMALL_MOLECULE_ACTIVATOR infeasible unless `druggable` AND (`mechanism == LoF_misfold` OR (`mechanism == toxic_aggregation` AND `protein_class ∈ STABILIZABLE`)) — cannot chaperone a null (no residual protein) and cannot "activate" a gain.
- ENZYME_PROTEIN_REPLACEMENT infeasible unless `mechanism ∈ {LoF_null, LoF}` AND (`localization == secreted` OR (`localization == lysosomal` AND NOT `bbb_cns`)) — can't add-protein to fix a gain; can't deliver into cells except lysosomal (M6P) / secreted; can't cross the BBB.
- GENE_THERAPY (gene addition) infeasible if `mechanism ∈ {GoF, overactivity, dominant_negative, toxic_aggregation}` (adding wild-type does not remove a poison/gain).
- ASO_siRNA infeasible if `mechanism ∈ {LoF_null, LoF, LoF_misfold}` AND NOT `splice_addressable` (RNA-lowering cannot restore lost function; splice-switching is the exception).
- ABSTAIN is never a violation (the safe default).
- COHERENCE ASSERTION (checked in `run.py`): no row's approved `true_modality` (excluding ABSTAIN rows) is flagged infeasible by this matrix — the matrix is consistent with reality.

**Known, pre-declared blind spots (predicted misses stated BEFORE scoring so they cannot be spun later):**
- Multi-modality "co-feasible" cases where objective features cannot pick the historical choice — all SAFE (the predicted alternative is itself feasible): `ERBB2` (RTK → predicts SM_INHIBITOR; truth trastuzumab; lapatinib is real), `APOB`/`APOC3` (secreted overactive → predicts ANTIBODY; truth ASO), `ALAS1`/`HAO1` (druggable intracellular overactive → predicts SM_INHIBITOR; truth siRNA), `F9` (secreted LoF → predicts ENZYME_PROTEIN_REPLACEMENT; truth gene therapy; factor IX replacement is real), `DMD` (structural LoF → predicts GENE_THERAPY; truth exon-skip ASO; delandistrogene gene therapy is real).
- CNS-lysosomal boundary: `ARSA` (lysosomal + bbb_cns → predicts ABSTAIN; truth is ex-vivo gene therapy) — a SAFE abstention, exactly like MENDEL1's TSC2/NF1/VHL misses.
These are the honest boundary, not a defect to hide.

## Pre-registered gates (numbers stated BEFORE scoring)
- **G1 — top-modality accuracy:** PRIMARY top-1 accuracy must beat majority baseline (0.186) by ≥ **0.20**, i.e. **accuracy ≥ 0.386**.
- **G2 — FAIL-SAFE (HARD, decisive integrity requirement):** the number of rows whose PRIMARY top recommendation is INFEASIBLE (per the frozen matrix) must be **exactly 0**. ANY infeasible confident recommendation = G2 FAIL, regardless of G1.
- **G3 — localization is load-bearing for the fail-safe:** a mechanism-only (localization-blind) ablation `recommend_mechonly(mechanism, druggable)` must produce **≥ 1** infeasible recommendation while the localization-aware PRIMARY produces **0**. G3 PASS = localization strictly reduces fail-safe violations from >0 to 0 (proving the composed localization feature — not the mechanism restatement — is what makes the recommender safe). Otherwise G3 = NEGATIVE.

## Supplementary (NOT a gate) — structural druggability cross-check
Reuse MENDEL1's cached fpocket best-pocket Druggability Scores for the 21 overlapping targets; report AUROC of `fpocket_drug_score` for small-molecule-modality (SM_INHIBITOR ∪ SM_ACTIVATOR) vs non-small-molecule. Pre-registered expectation (from MENDEL1 G3): WEAK separation — structural pocket score does NOT cleanly determine modality; mechanism+localization do. Reported for cross-experiment consistency only.

## Overall verdict rule (frozen)
- **PASS (validated cross-class modality-recommender arm)** = G1 PASS **AND** G2 PASS (fail-safe holds). G3 reported separately.
- **NEGATIVE (first-class, honest bound)** = G1 fail (modality not recoverable beyond baseline) **OR** G2 fail (an infeasible modality is confidently recommended — the triage is not fail-safe).

## Scope / honesty (frozen)
In-silico; n=43 hand-curated cited cases (a coverage seed, not a census); recommends a MODALITY CLASS, not a molecule; the SMALL_MOLECULE branch still hits the affinity wall (AFFINITY1/HIT2/B49/B65); triage-not-therapy; `true_modality` = the landmark/mechanism-canonical approved modality (multi-modality is real, disclosed per row); localization/mechanism are objective inputs where available, declared inputs otherwise; `causal_node` uniform in this seed. Reproduce ×2 byte-identical over sorted-key JSON payload (excludes verdict/provenance).
