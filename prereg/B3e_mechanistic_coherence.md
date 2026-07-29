# Pre-registration — B3e (L1b mechanistic coherence): does transfer strength track AML mechanism? (FINALIZED 2026-07-29, pre-run)

## Motivation
B3d's exploratory ranking suggested the best-transferring drugs are AML-relevant. That was NOT a hypothesis
test (drug-class curation = researcher DOF). B3e converts it into a real, pre-registered test using an
**external, pre-existing annotation** (GDSC's own `PATHWAY_NAME`) and a hypothesis frozen from textbook AML
genetics BEFORE any transfer-vs-pathway number is computed.

## Frozen definitions (declared before running)
- Transfer strength per drug = proliferation-residualized diagonal Spearman ρ from the B3b setup (DepMap
  RNA-seq + GDSC2 labels → BeatAML patients), exactly as in B3b/B3d.
- **AML driver-signaling group** = drugs whose GDSC `PATHWAY_NAME` ∈ {"RTK signaling", "ERK MAPK signaling"}.
  Rationale (a priori, not from results): the recurrently-mutated AML signaling drivers are FLT3/KIT (RTK) and
  NRAS/KRAS→MEK/ERK (ERK MAPK). This is the single pre-declared AML-relevant axis. All other GDSC-annotated
  pathways = the comparison group. (PI3K/MTOR, EGFR, ABL, IGF1R deliberately EXCLUDED from the AML group —
  declared now, not tuned.)

## Hypotheses (assumed FALSE)
- **H1 (primary):** residual transfer ρ is higher for AML driver-signaling drugs than for other drugs.
  One-sided Mann–Whitney U across drugs; permutation confirmation (shuffle group labels, k=2000, seed=42).
- **H2 (secondary, DOF-free, no annotation):** residual transfer ρ correlates positively across drugs with
  each drug's *within-cell-line* predictability (5-fold CV Spearman of expression→GDSC2 LN_IC50 on DepMap,
  computed WITHOUT patient data) — i.e., the engine transfers to patients the drugs it can actually model.
  Spearman across drugs; permutation p.
- **H0:** no association between transfer strength and AML mechanism / cell-line predictability.

## Decision rule (fixed)
- H1 PASS iff one-sided MWU p<0.05 AND permutation p<0.05, AML group median > other median.
- H2 PASS iff Spearman ρ>0 with permutation p<0.05.
- Coherence CONFIRMED if H1 passes (primary). H2 is corroborating. Report both regardless; a null is reported
  honestly and downgrades the "mechanistically coherent" language in V9+.

## Data
Residual transfer ρ (B3b pipeline, GDSC2 labels). Pathway annotation: GDSC1 xlsx `PATHWAY_NAME` per DRUG_NAME
(external table; drugs without an annotation are dropped from H1, n reported). Cell-line CV: DepMap RNA-seq +
GDSC2 LN_IC50. All held, sha256 in MANIFEST.

## Honest prior
B3d hinted at coherence but it was exploratory and effects are weak. Prior H1 passes ~40–55%. A null is fully
possible and would mean "the weak transfer signal is real and robust but not cleanly organized by the one
pre-declared AML pathway axis" — still honest, still useful.

## Reproducibility
Deterministic; CV fold assignment seeded (seed=42); permutation seed=42, k=2000. Reproduce ×2.
Output: `experiments/B3e_mechanistic_coherence/results/B3e_metrics.json`.
