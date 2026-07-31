# Pre-registration — B49: proteochemometric pan-target model — can we predict activity for UNSEEN targets? (FINALIZED 2026-07-30, PRE-RESULT)

## Why (the "any drug for any disease" generalization axis)
Every QSAR so far is single-target (needs that target's own ligand data). The universal-platform vision requires
predicting activity for targets with **little or no** ligand data. Proteochemometrics (PCM) attempts this by learning
from **ligand features ⊕ protein features** jointly, so knowledge transfers across the proteome. B49 asks the honest
question: does a PCM model using **ESM-2 protein embeddings** generalize to **held-out proteins** (leave-protein-out) —
i.e. can it rank actives for a target it never saw ligands for — and do the protein features add anything over a
pooled ligand-only model? Literature caution (pre-registered expectation): protein-language-model embeddings alone
capture **limited** target-specific bioactivity signal, so a strong result is NOT expected — this is an honest probe of
the generalization axis, first-class either way.

## Data (OPEN; already local + UniProt sequences)
15 LIT-PCBA target-sets (actives/inactives SMILES; `$INTERCEPTA_DATA/lit_pcba`), mapped to **14 UniProt proteins**
(ESR1_ago & ESR1_ant share P03372). Protein sequences fetched once from UniProt REST (`{acc}.fasta`), cached +
sha-logged. PCM uses ALL targets **including the low-active ones B46 had to skip** (pooling makes few-active targets
usable). Per target: all actives (≤300) + seeded inactive sample (≤600, random_state=42).

## Method (env: intercepta-build; torch 2.13 + transformers 4.50; deterministic)
- **Protein features:** ESM-2 `facebook/esm2_t30_150M_UR50D`, sequence truncated to 1022 residues, **CPU inference
  (deterministic), mean-pooled last hidden state** → one 640-d vector per protein. Cached.
- **Ligand features:** Morgan r2, 1024-bit.
- **PCM feature vector:** ligand(1024) ⊕ protein(640). Model: HistGradientBoostingClassifier (seed=42).
- **Evaluation — leave-PROTEIN-out CV** (14 folds): hold out ALL target-sets of one protein; train PCM on the other
  13 proteins' pooled data; predict each held-out target-set's actives-vs-decoys → AUROC (rdkit.ML.Scoring). (Grouping
  by protein prevents the ESR1 ago/antag leakage of identical embeddings.)
- **Baseline (does protein help?):** identical leave-protein-out with a **ligand-only** model (no protein features) —
  isolates whether ESM embeddings add target-specificity beyond pooled ligand structure.

## Metrics & aggregate
Per held-out target-set: PCM AUROC and ligand-only AUROC. Panel: mean AUROC (PCM vs ligand-only), number of held-out
targets with PCM AUROC>0.60, and Δ(PCM − ligand-only).

## Hypotheses (pre-registered; honest, modest)
- **H1 (PCM generalizes to unseen proteins):** leave-protein-out **mean PCM AUROC > 0.55** (above chance for targets
  whose ligands were never seen). If FALSE → no cross-target generalization here (first-class negative).
- **H2 (protein features add target-specificity):** **mean PCM AUROC ≥ ligand-only + 0.02**. If FALSE → the ESM
  embedding adds no usable target-specific signal over pooled ligand structure (the honest, literature-consistent
  outcome); reported plainly, NOT hidden.
- **Reported regardless:** per-target AUROC (PCM vs ligand-only), Δ, and how many unseen targets clear 0.60.

## Honesty / scope
Retrospective, in-silico, real-actives-vs-decoys. Sequence truncation (1022) loses info for large proteins (e.g. MTOR
2549 aa) — a documented approximation. Decoys not property-matched. Leave-protein-out is a genuine unseen-target test
but 14 proteins is small. Enrichment ≠ proven activity; not wet-lab; no SOTA claim. A NULL H2 (protein adds nothing) is
expected-allowed and reported as first-class.

## Reproducibility
Deterministic: UniProt sequences cached (sha-logged); ESM-2 CPU inference (deterministic); Morgan deterministic; HGB
seed=42; folds fixed by protein. Reproduce ×2 byte-identical (payload sha256 over summary+per-target). Output:
`experiments/B49_proteochemometric_pantarget/results/B49_metrics.json`. Env: intercepta-build; INTERCEPTA_DATA owned path.
