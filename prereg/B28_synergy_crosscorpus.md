# Pre-registration — B28: cross-corpus external validation of the synergy ranker (harden V23) (FINALIZED 2026-07-29, PRE-RESULT)

## The question (hardening the one robust positive)
V23/the shipped SynergyRanker generalizes to unseen combinations WITHIN a corpus (leave-combination-out CV
Spearman 0.62 O'Neil / 0.39 DrugComb). The decisive rigor test — the standard we hold everything to — is
**external replication across independent corpora**: does a model trained on ONE synergy dataset predict MEASURED
synergy in a SECOND, independently-generated one (different institution, different Loewe computation)? Plus a
practical retrieval metric: are the top-predicted pairs actually synergistic?

## Data (OPEN; already cached)
O'Neil/OncoPolyPharmacology (583 pairs × 39 cells) and DrugComb (5,618 pairs × 41 cells), both Loewe synergy, both
with DepMap-expression cell features + Morgan-fingerprint drug features (the shipped SynergyRanker pipeline). Note
the corpora use different Loewe scales/definitions (O'Neil mean ≈ +5, DrugComb mean ≈ −9), so absolute values are
NOT comparable — we evaluate **rank** (Spearman) and **retrieval**, which are scale-invariant.

## Design (train on A, evaluate on B, and vice versa)
Fit the SynergyRanker pipeline on corpus A (all of it). For every (drug1, drug2, cell) instance in corpus B that is
featurizable (both drugs have SMILES → fingerprints; cell has DepMap expression), predict synergy and compare to
B's MEASURED Loewe. Cell PCA fit on A's cells, projected onto B's cells; fingerprints computable for any drug.
Both directions: O'Neil→DrugComb and DrugComb→O'Neil.

## Metrics & hypotheses (assumed FALSE)
- **H1 (cross-corpus rank transfer):** Spearman(predicted, measured) on the held-out corpus > 0, bootstrap CI
  excludes 0, in BOTH directions. (Primary.)
- **H2 (retrieval usefulness):** precision@top-10% — among the instances the model ranks most synergistic, the
  fraction that are actually synergistic (measured Loewe in the corpus's top quartile) exceeds the base rate
  (enrichment > 1).
- **H3 (novel-combination subset):** H1 restricted to test pairs whose drug COMBINATION is not in the training
  corpus (true cross-corpus new combinations) — the effect is not just shared-pair memorization.
- H0: cross-corpus Spearman ≈ 0 → the tool does not transfer across independent corpora (within-corpus only).

## Decision rule & interpretation (fixed)
- **H1 (+H3) PASS** with a non-negligible effect (Spearman ≥ 0.1 and CI>0) → the synergy ranker is EXTERNALLY
  VALIDATED across independent labs/assays — a materially stronger claim than within-corpus CV. Report H2
  enrichment as the practical usefulness.
- **H1 PASS but small (0 < ρ < 0.1)** → transfers but weakly; honestly bounded.
- **H1 FAIL** → does NOT transfer across corpora → the tool is within-corpus only (honest ceiling on V23);
  first-class negative that bounds the shipped tool's claims.
- Effect size, not just p-value, governs the verdict (per B27 discipline).

## Honesty / scope
Cell-line Loewe synergy (not clinical). Corpora share many common oncology drugs, so H1 partly reflects shared-drug
transfer; H3 isolates the harder new-combination case. Different Loewe definitions cap achievable cross-corpus ρ.
A null is first-class. Deterministic (seed=42); reproduce ×2. Output:
experiments/B28_synergy_crosscorpus/results/B28_metrics.json.
