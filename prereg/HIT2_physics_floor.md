# HIT2 — The structure-only PHYSICS floor: does docking recover the NOVEL-chemotype actives that ligand-transfer cannot? (finalized 2026-08-04, PRE-RESULT)

## Why (the crux the molecule half turns on)
HIT1 found ligand-based hit-finding is ANALOG-DRIVEN with only a soft, partial signal for scaffold-novel chemotypes. But
ligand methods are fundamentally analogy-bound — they rank by resemblance to known binders. The ONE zero-data signal that
does NOT depend on chemical analogy is structure-based PHYSICS: docking a molecule into the target pocket scores its fit
regardless of whether it resembles any known ligand. So physics is the natural candidate to recover NOVEL-chemotype actives
where ligand-transfer provably fails. HIT2 tests this head-to-head on the SAME compounds as HIT1. (C1 already showed docking
carries a real-but-weak zero-data signal on Mpro; HIT2 asks the sharper question: is that weak signal ANALOGY-INDEPENDENT,
i.e. does it hold on novel chemotypes?)

## Target + library
- Target: **thrombin** (human coagulation factor II; MoleculeACE CHEMBL204) — a clean, well-pocketed classic docking target
  (deep S1 specificity pocket; many high-res holo structures). Structure: a high-resolution thrombin–small-molecule-inhibitor
  complex (PDB, to be fixed at prep); box defined from the co-crystallised ligand centroid (± padding). Cognate ligand
  removed before docking (zero-data: no thrombin activity labels used to place the box beyond the known pocket location).
- Library: the MoleculeACE **CHEMBL204 test set** — SAME 553 compounds as HIT1 (292 actives pAct≥6.5 / 261 inactives) →
  clean head-to-head of PHYSICS vs ligand-TRANSFER on identical compounds and the identical novelty split.

## Method (reuse C1's validated pipeline)
Per compound: RDKit ETKDG 3D + MMFF → obabel → pdbqt → **AutoDock Vina 1.2.7** (`--seed 42 --exhaustiveness 16 --cpu 4`),
best-pose affinity = physics score (lower kcal/mol = better). Dock ONCE → cache scores as a regenerable data artifact
(`$INTERCEPTA_DATA/hit2/thrombin_vina.tsv`); the analysis is reproduced ×2 on the cache (Vina is deterministic given seed).

## Design / metrics (on the SAME novelty split as HIT1)
Novelty of a test active = nearest-HIT1-seed-active (CHEMBL204 train actives) ECFP4 Tanimoto; NOVEL < 0.4, ANALOG ≥ 0.4.
Rankers: PHYSICS (−Vina), SIMILARITY (max Tanimoto to seeds), QSAR (HIT1 RF). Report AUROC overall, analog-vs-inactive,
novel-vs-inactive for each; correlation of physics score with novelty (≈0 expected if physics is analogy-independent);
and a rank-sum CONSENSUS (physics+ligand) overall and on novel actives.

## Hypotheses (pre-registered)
- **H1 (physics floor exists):** docking recovers actives above random zero-data (overall AUROC > 0.55).
- **H2 (THE CRUX — analogy-independence):** docking's NOVEL-chemotype recovery ≈ its ANALOG recovery (|AUROC_novel −
  AUROC_analog| small) AND novel-vs-inactive AUROC > 0.55 — i.e. physics recovers novel chemotypes about as well as analogs,
  so on NOVEL actives PHYSICS ≥ SIMILARITY. This would make physics the signal that survives where analogy fails.
- **H0 (first-class):** docking ≈ random even overall (AUROC ≤ 0.55) → no usable physics floor on this target (consistent
  with docking's known weak prospective enrichment; C1). Reported plainly — then the molecule half's novel-chemotype
  problem is genuinely hard for BOTH families, a hard ceiling.

## Honesty / scope
Single target (thrombin — a FAVOURABLE, well-pocketed docking case → generous to physics; a positive here is an existence
proof, not generalization); Vina scoring has known modest accuracy; one structure/pocket/protonation; rigid receptor;
potency data (measured binders, not needle-in-haystack); retrospective, in-silico, open data; not wet-lab. Generalization
across targets = later. A weak/positive physics floor is judged against RANDOM and against the HIT1 ligand signal on the
identical compounds.

## Reproducibility
Vina deterministic (`--seed 42`); dock once → cache; analysis reproduced ×2 byte-identical (payload over ranker AUROCs +
consensus on the fixed split). Output: `experiments/HIT2_physics_floor/results/HIT2_metrics.json`. Envs: `docking`
(vina/obabel), `intercepta-build` (rdkit/sklearn analysis). Data: thrombin PDB + MoleculeACE CHEMBL204 (MANIFEST).
