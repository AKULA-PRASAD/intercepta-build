# Pre-registration — B47: structure-based channel (AutoDock Vina docking) + orthogonality to ligand-based (FINALIZED 2026-07-30, PRE-RESULT)

## Why (add the missing information channel; set up the fusion test)
Every INTERCEPTA retrieval so far is LIGAND-based (2D/3D of the molecule). B47 adds the **structure-based** channel —
physics-based docking of molecules into the target's 3D pocket (AutoDock Vina) — the first genuinely NEW information
source (the receptor) in the program. Two honest questions: (1) does docking enrich real actives on unbiased LIT-PCBA
targets, and (2) is the docking signal **orthogonal** to our ligand-based signal (different information)? The literature
says docking is WEAK on unbiased data (Vina median EF1% ~0.9; arXiv:2605.01681) but complementary — so the real payoff
is B48 (fusing orthogonal channels). B47 establishes the channel + the orthogonality that motivates B48.

## Data (OPEN; LIT-PCBA, cached; MANIFEST sha 93467a5b)
3 targets spanning classes, each with a LIT-PCBA co-crystal receptor + ligand: **FEN1** (nuclease, 5fv7), **MAPK1**
(kinase), **ESR1_ant** (nuclear receptor). Per target: receptor = the first `*_protein.mol2` (sorted); reference
ligand(s) = the `*_ligand.mol2` co-crystal(s); query set = **≤60 seeded actives + ≤120 seeded decoys** (random_state=42)
from that target's `actives.smi`/`inactives.smi` (subsampled — docking throughput bound).

## Method (deterministic; docking-env: rdkit 2025.09.5 + openbabel 3.1 + AutoDock Vina 1.2.7)
- **Receptor prep:** `obabel mol2 -> pdbqt -xr` (rigid). **Box:** centre = centroid of the co-crystal ligand heavy
  atoms; size 22×22×22 Å.
- **Ligand prep:** SMILES -> RDKit ETKDGv3 (randomSeed=0xB47) 3D + MMFF94 optimise -> SDF -> `obabel -> pdbqt`
  (Gasteiger). Failures recorded/skipped.
- **Docking:** AutoDock Vina, `sf_name='vina'`, **seed=42, cpu=8** (verified byte-deterministic), exhaustiveness=8,
  n_poses=3; **docking score = −(top binding affinity)** (higher = better). [Determinism pre-verified on FEN1: identical
  −6.8010 across two cpu=8 runs.]
- **Ligand-similarity channel (for orthogonality):** max ECFP4 (Morgan r2, 2048) Tanimoto of each query to the
  reference co-crystal ligand(s) — the canonical ligand-based VS baseline.
- **Metrics (rdkit.ML.Scoring):** per target, rank queries by docking score AND by ligand-similarity; compute AUROC,
  BEDROC(80.5), EF@5% for each channel; and **Spearman correlation between the two score vectors** (orthogonality).

## Hypotheses (pre-registered; honest, docking expected weak)
- **H1 (docking enriches above chance):** panel-mean **docking AUROC > 0.55** (better than random; honest low bar,
  since unbiased-data docking is known weak). If FALSE → docking adds no retrieval signal here (first-class negative).
- **H2 (orthogonality — motivates B48):** panel-mean **Spearman(docking, ligand-similarity) < 0.4** — the channels
  carry substantially different information (complementary), the prerequisite for a fusion gain in B48.
- **Reported regardless:** per-target docking AUROC vs ligand-similarity AUROC (does docking ever win?), EF, and the
  correlation.

## Honesty / scope
Retrospective, in-silico. Rigid single-conformation receptor; one input ligand conformer (Vina searches flexibly from
it); Open Babel Gasteiger prep (not AD4/meeko typing — a known approximation); 3 targets; heavily subsampled queries
(docking is slow) → AUROC is the fair metric, EF is at the subsampled ratio. Docking affinity is a heuristic score,
NOT a binding free energy; enrichment ≠ proven activity; not wet-lab. No SOTA claim.

## Reproducibility
Deterministic: RDKit ETKDG seed=0xB47, Vina seed=42 cpu=8 (pre-verified), seeded query subsample (42). Reproduce ×2
byte-identical (payload sha256 over summary+per-target). Output:
`experiments/B47_docking_structure_channel/results/B47_metrics.json`. Env: `docking` (rdkit 2025.09.5 / openbabel 3.1 /
vina 1.2.7); INTERCEPTA_DATA owned path.
