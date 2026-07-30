# Pre-registration — B44: ligand-based 3D shape/pharmacophore for scaffold hopping (FINALIZED 2026-07-30, PRE-RESULT)

## Why (the last feasible computational rung; a capability 2D structurally lacks)
Every validated retrieval so far (B42/B43) rests on 2D Morgan fingerprints. 2D fingerprints are a famously strong VS
baseline, but they are structurally **blind to scaffold hops**: an active built on a chemotype unlike the reference
has low 2D Tanimoto by construction, regardless of whether it presents the same 3D shape/pharmacophore. 3D
ligand-based similarity (shape + pharmacophore overlay) is the standard tool for exactly this case. B44 asks the
honest, sharply-scoped question: **does 3D O3A shape/pharmacophore similarity to known actives retrieve NOVEL-SCAFFOLD
actives (2D-dissimilar to the references) better than 2D fingerprint similarity does?** This is the one retrieval task
where 3D can beat 2D in principle; if it does not, that is a first-class negative that honestly bounds the capability.
No receptor docking engine is installed (vina/smina/gnina absent; only Open Babel) — receptor-based binding stays the
computational ceiling. This is ligand-based 3D only (rdkit O3A), which IS available.

## Data (OPEN; TDC HTS single-target; real actives vs decoys)
`hiv` (antiviral phenotypic; 1443 actives — chosen for scaffold diversity, enough novel-scaffold actives to test).
All actives + a seeded decoy subsample (see Method). Same source as B42/B43 (MANIFEST HIV row).

## Method
1. **Featurize/scaffold**: Morgan-2048 (2D); Bemis–Murcko scaffold per molecule.
2. **References**: cluster actives by Murcko scaffold; pick K=8 references = one representative (first by canonical
   SMILES) from each of the 8 largest scaffold clusters. Fixed, deterministic.
3. **Query set**: all non-reference actives + a seeded decoy subsample (random_state=42; cap decoys at 2500 to bound
   3D runtime → query set ≈ actives + 2500). Split queries into **novel-scaffold actives** (Murcko scaffold shares
   with NO reference) vs same-scaffold actives.
4. **3D**: for every reference and query, embed ONE conformer (ETKDG v3, randomSeed=0xB44 fixed) + MMFF94 optimize;
   drop molecules that fail embedding (recorded). O3A-align each query to each reference
   (`rdMolAlign.GetO3A`, MMFF properties); **3D score = max O3A alignment score over the 8 references** (best-matching
   pharmacophore/shape overlay).
5. **2D baseline**: 2D score = max Morgan Tanimoto over the same 8 references.
6. **Rank & score** two retrieval sets, each = {novel-scaffold actives} ∪ {decoys}, once ranked by 3D score and once
   by 2D score. Metrics (rdkit.ML.Scoring): AUROC, BEDROC(α=80.5), EF@1%, EF@5%. Also report the same on the full
   {all actives} ∪ {decoys} set for context (where 2D is expected to win — the honest full picture).

## Hypotheses (assumed FALSE)
- **H1 (scaffold hopping — the positive claim):** on the NOVEL-SCAFFOLD actives vs decoys, 3D O3A enrichment exceeds
  2D fingerprint enrichment: AUROC_3D − AUROC_2D > +0.03 AND EF@1%_3D > EF@1%_2D. (3D retrieves chemotype-hopped
  actives that 2D misses.)
- **H2 (3D still meaningful):** 3D novel-scaffold AUROC > 0.60 (above chance on the hardest set) AND EF@1%_3D > 2.
- **H0 (first-class negative):** 3D does NOT beat 2D even on novel-scaffold actives → ligand-based 3D adds no retrieval
  capability over the 2D spine on this target; honestly reported, bounds the rung.

## Honesty / scope
Retrospective, in-silico, real-actives-vs-decoys — NOT prospective, NOT wet-lab. Single low-energy conformer (speed
bound) is an approximation to the true conformational ensemble; O3A is a heuristic overlay, not a binding free energy.
Single target (HIV); enrichment ≠ proven activity; this tests a LIGAND-based 3D retrieval capability, not de novo
discovery and not receptor docking. Decoys are assay-inactives (property-matching not applied — reported as a caveat).

## Reproducibility
Deterministic: seed=42 (decoy subsample), ETKDG randomSeed=0xB44 fixed, reference selection deterministic, O3A
deterministic given conformers. Reproduce ×2 byte-identical (payload sha256 over summary+per-set metrics).
Output: `experiments/B44_ligand_3d_scaffold_hop/results/B44_metrics.json`.
