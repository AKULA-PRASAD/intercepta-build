# FRONT2 — Structural selectivity: can a binding-site pathogen-vs-host difference RESCUE the host-homologous targets E2E2 over-excludes? (finalized 2026-08-04, PRE-RESULT)

## Why
E2E2 exposed the tension: a sequence-level host-non-homology hard filter is SAFE but PERMANENTLY EXCLUDES 35–52% of real
drug targets (those with a human homolog) — many of which are drugged SELECTIVELY in reality by exploiting binding-site
differences a sequence filter cannot see. FRONT2 tests whether STRUCTURE recovers what sequence loses: among the
host-homologous targets, does the pathogen protein's own pocket druggability — and, crucially, its DIFFERENCE from the human
homolog's pocket — distinguish the genuinely druggable/selective targets from non-targets? If yes, structure RESCUES the
over-excluded real targets (a real front-half capability gain); if no, the information ceiling extends to structural
selectivity.

## Data (feasibility-verified 2026-08-04; cache building, b0ksxm5yx)
Host-homologous pathogen metabolic genes (Mtb + E. coli): all host-homologous known targets + a seeded sample of ~100
host-homologous non-targets per organism. Per gene: pathogen fpocket max Druggability Score (reuse TID2 cache where present,
else fetch AlphaFold v6 + fpocket) + its best human homolog's fpocket druggability (fetch AF + fpocket). fpocket + AF verified
(thrombin human P00734 druggability 0.617).

## Hypotheses (pre-registered)
- **H1 (structure rescues):** among host-homologous genes, pathogen pocket druggability distinguishes known targets from
  non-targets (AUROC > 0.60, permutation p<0.05) → structure identifies the druggable targets the sequence filter excluded.
- **H2 (selective-difference):** the pathogen-vs-human druggability DIFFERENCE (path_drug − human_drug) distinguishes targets
  additionally/better (AUROC > 0.60 AND partial signal beyond pathogen druggability alone) → the rescuable targets have
  pathogen-SELECTIVE pockets (more druggable in pathogen than host).
- **H0 (first-class):** neither pathogen druggability nor the pathogen-vs-host difference distinguishes targets among the
  host-homologous set (AUROC ≈ 0.5) → structure cannot rescue the over-excluded targets zero-data; the information ceiling
  extends from sequence to structural selectivity (consistent with TID2, where pocket druggability ≈ conservation, weak).

## Honesty / scope
fpocket Druggability Score is a HEURISTIC (TID2 found it ≈ conservation and weak on the full proteome); AlphaFold PREDICTED
structures (apo, no ligand/induced-fit); metabolic subproteome; 2 bacteria; sampled non-targets; ChEMBL target ground-truth
selection-biased; a structural difference ≠ proven selective druggability (needs the actual inhibitor); not wet-lab. A
positive here is an existence signal that structure adds selectivity information sequence lacks, not a validated selective-
target predictor.

## Reproducibility
Deterministic (fpocket/AF cached as a data artifact; fixed non-target sample seed; permutation seed fixed). Reproduce ×2
byte-identical (payload over per-organism + pooled AUROC/enrichment). Output:
`experiments/FRONT2_structural_selectivity/results/FRONT2_metrics.json`. Envs: bioinfo (mmseqs/fpocket) + intercepta-build.
Data: TID2 structures + AlphaFold human homologs (MANIFEST).
