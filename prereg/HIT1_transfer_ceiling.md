# HIT1 — The novel-chemotype ceiling of zero/low-data ligand-based hit-finding (finalized 2026-08-04, PRE-RESULT)

## Why (opening the molecule half, mirroring the target-ID arc)
The target-ID arc opened by mapping the CONSERVATION ceiling (TID1) before anything else. The molecule half has the same
spine — an information ceiling — and the field systematically HIDES it: the 2025 audit *Data Leakage and Redundancy in the
LIT-PCBA Benchmark* (arXiv 2507.21404) shows "zero-shot" virtual-screening numbers are inflated by ANALOG LEAKAGE (models
recover analogs of known actives) and do NOT measure novel-chemotype recovery. HIT1 measures that ceiling honestly: given a
few known binders, can any ligand-based ranker recover NOVEL-chemotype potent compounds, or does enrichment collapse to the
analog neighborhood? This is the molecule-half analog of the conservation ceiling, and the floor every later chapter (a
physics/structure signal, generation) must be measured against.

## Data (fetched, verified 2026-08-04)
MoleculeACE (github.com/molML/MoleculeACE): 30 curated ChEMBL targets, 48,714 compounds. Per compound: SMILES, pActivity
(y[pKi/pEC50]), `cliff_mol` (activity-cliff flag), `split` (train/test, scaffold/cliff-aware). Purpose-built to test
whether molecular similarity predicts activity → exactly the ceiling question. HONEST SCOPE: all compounds are MEASURED
binders, so HIT1 tests the POTENCY-transfer ceiling (recover potent binders incl. scaffold-novel/cliff ones) — the
fine-grained, lead-opt-relevant version — NOT full active-vs-decoy hit-finding (that + the physics floor = HIT2, with
docking we run and control ourselves; the LIT-PCBA strain-study subset we found is compound-selection-biased and unsafe
for a headline enrichment claim).

## Design (per target, then aggregated across the 30)
- ACTIVE = pActivity ≥ 6.5 (potent, ~≤316 nM; standard hit cutoff). Include a target iff its `split==test` set has ≥20
  actives and ≥20 inactives (report inclusions).
- SEEDS = the target's `split==train` actives (the "known binders"). LIBRARY = its `split==test` compounds.
- Fingerprints: ECFP4 (Morgan radius 2, 2048 bits, RDKit).
- **Two rankers of the library:**
  1. **Similarity-transfer:** score = max Tanimoto to any seed active.
  2. **Learned QSAR:** RandomForest (seeded) on ECFP4, trained on ALL train compounds (active/inactive labels).
- **Novelty split of test actives:** ANALOG = nearest-seed-active Tanimoto ≥ 0.4; NOVEL = < 0.4 (scaffold-disjoint).
  Also report the independent `cliff_mol` axis.
- **Metrics:** BEDROC(α=20), EF@1%, EF@5%, AUROC per ranker — OVERALL and for recovery of NOVEL actives specifically.
- **NULL:** label-shuffled ranker → confirm BEDROC/EF ≈ random.

## Hypotheses (pre-registered)
- **H1 (aggregate works):** both rankers achieve strong OVERALL enrichment (median BEDROC ≫ random across targets) — hit
  recovery works in aggregate.
- **H2 (THE CEILING — the crux, non-tautological part):** overall enrichment is ANALOG-driven; NOVEL-chemotype recovery
  is near-random for similarity AND learned QSAR does NOT rescue it (median Δ[QSAR−sim] novel-recovery small, and QSAR
  novel-recovery near random) — i.e. LEARNING does not generalize beyond chemical analogy → the novel-chemotype ceiling.
- **H0/ALT (first-class):** learned QSAR recovers NOVEL chemotypes substantially better than similarity (median ΔBEDROC_novel
  > 0.1 in majority of targets) → learning DOES generalize beyond analogy — a genuine positive, reported plainly.

## Honesty / scope
Potency-transfer among measured binders (not active-vs-decoy hit-finding); MoleculeACE's own train/test split; ECFP4/RF
(standard, not SOTA — the point is the CEILING, which SOTA also hits per the audit); novelty threshold 0.4 (report
sensitivity implicitly via cliff axis); retrospective, in-silico, open data; not wet-lab. The similarity-ranker's failure
on low-similarity actives is partly definitional — the DECISIVE, non-tautological test is whether LEARNED QSAR beats it on
novel recovery.

## Reproducibility
Deterministic (RDKit ECFP deterministic; RF random_state fixed; fixed thresholds/splits). Reproduce ×2 byte-identical
(payload over per-target + aggregate metrics). Output: `experiments/HIT1_transfer_ceiling/results/HIT1_metrics.json`. Env:
intercepta-build (rdkit/sklearn). Data: MoleculeACE 30 CSVs (MANIFEST).
