# C1 — Zero-data holdout on SARS-CoV-2 Mpro: can label-free structure-based screening recover real binders with ZERO target data? (finalized 2026-07-31, PRE-RESULT)

## Vision alignment (the filter, answered)
This is Chapter 1 of the reoriented north star (VISION.md governing section; memory `north-star-zero-data-disease`).
It directly instantiates the stress test: *"a new pathogen appears with no activity data, no known inhibitors, no
labels — can INTERCEPTA produce scientifically credible candidates from sequence/structure alone?"* Would this
capability matter for a disease that never existed before? **Yes — it is the capability.** We test it on the canonical
pandemic protein (SARS-CoV-2 main protease, Mpro / 3CLpro) precisely because it has a HELD-OUT ground-truth answer key
we can score against, while the pipeline itself uses **zero Mpro activity data**.

## Phase-0 provenance (three fundamentally different solution families → this design)
Deep research across (A) physics/structure, (B) homology/target-ID, (C) structure-based generation converged:
label-free discovery yields *pose-plausible candidate hypotheses, not potency-ranked leads*; the reliable stages are
structure + pocket + pose + physical-validity/synthesizability gating; the **weak link is affinity ranking** (Thread A:
docking is near-random prospectively on LIT-PCBA; Thread C: co-folding/generative affinity is overconfident and
uncorrelated in the top-100). C1 measures our OWN pipeline against that literature on the pandemic target, honestly —
a NULL (docking ≈ random) is an expected, first-class outcome that would motivate the physics-gating / homology-transfer
chapters (C2/C3), not a failure to hide.

## The zero-data contract (binding)
The pipeline may use ONLY: (1) the Mpro sequence/structure, (2) general, disease-agnostic chemistry/physics. It may NOT
use: any Mpro activity label, any Mpro-derived QSAR, any known Mpro inhibitor. The 78 actives in the TDC set are the
HELD-OUT answer key — read ONLY at the final evaluation step to compute enrichment; never to fit, filter, or rank.

## Data (OPEN, cached / free)
- **Library + ground truth:** TDC `sarscov2_3clpro_diamond` (880 compounds, 78 crystallographic-fragment actives / 802
  inactives). To bound docking compute: dock ALL 78 actives + a seeded 312-inactive sample (4:1), n=390. (Fragment
  hits are a HARD, honest case — small ligands dock poorly; this is stated up front, not a rigged easy set.)
- **Receptor:** an SARS-CoV-2 Mpro structure fetched from RCSB PDB (free). Ligand/waters removed; active site defined
  around the catalytic dyad (His41/Cys145). For a truly novel pathogen this structure would be predicted (AF2/ESMFold,
  near-experimental for a protease homolog) — C1 uses the experimental structure; ESMFold-equivalence is a C2 robustness check.

## Design (label-free structure-based screen; two arms)
Prepare receptor (PDB → pdbqt, obabel) + a deterministic docking box around His41/Cys145. Each ligand: SMILES → 3D
(RDKit ETKDG, seeded) → pdbqt → **AutoDock Vina 1.2.7** (seed=42, deterministic). Two rankings:
- **Arm A (pure physics):** rank by Vina docking score (best pose ΔG). This is the zero-knowledge baseline.
- **Arm B (physics + validity gate):** discard poses failing a physical-validity/strain check (heavy-atom clash /
  implausible geometry — a lightweight PoseBusters-style gate, Thread C's load-bearing filter), then rank the survivors;
  ungated/failed compounds ranked last.

## Metrics (enrichment of the 78 held-out actives; both arms + random reference)
- **AUROC** (−Vina score vs active label), **EF1%**, **EF5%**, **BEDROC (α=20)**. Random reference = active prevalence.
- Docking sanity: mean/median Vina score, pose-validity pass rate, actives-vs-inactives score separation (Mann–Whitney).

## Hypotheses (pre-registered)
- **H1 (zero-data structure-based recovery):** Arm A **AUROC > 0.55** AND EF1% > 1× (docking recovers real Mpro binders
  above random with zero target data). **H0 (expected-allowed, first-class):** AUROC ≈ 0.5 / EF1% ≈ 1 → pure docking is
  near-random here (consistent with Thread A's prospective-docking finding), establishing the honest baseline the weak
  link predicts.
- **H2 (physics/validity gating helps):** Arm B enrichment (EF1%/AUROC) **> Arm A** → the physical-validity gate is a
  real lever for label-free structure-based screening (Thread C). Reported regardless of sign.
- **Reported regardless:** full enrichment table (both arms vs random), score separation, pose-validity rate, and the
  honest read (candidates are pose-plausible HYPOTHESES, not validated actives).

## Honesty / scope
Retrospective evaluation with a held-out answer key (not prospective wet-lab). Crystallographic FRAGMENT ground truth
(a deliberately hard case; drug-like Mpro ground truth is not in local data — a noted limitation). Single receptor
conformation; Vina only (no FEP/ensemble); no induced fit. Output = pose-plausible candidate hypotheses requiring assay
confirmation — NOT potency predictions (the affinity-ranking weak link is the point). Zero Mpro activity data used. Not
wet-lab; not a clinical/safety claim.

## Reproducibility
Deterministic target: RDKit ETKDG seed=42, Vina seed=42/exhaustiveness fixed, inactive-sample seed=42, box from fixed
residues. Reproduce ×2 byte-identical where docking permits (payload sha256 over per-compound Vina scores + enrichment
summary); if Vina exhibits platform nondeterminism it will be documented and the enrichment summary reproduced instead.
Output: `experiments/C1_mpro_zerodata_holdout/results/C1_metrics.json`. Envs: `docking` (Vina/obabel), `intercepta-build`
(RDKit/eval). INTERCEPTA_DATA owned.
