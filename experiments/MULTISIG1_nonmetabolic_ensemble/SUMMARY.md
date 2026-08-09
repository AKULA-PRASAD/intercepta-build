# MULTISIG1 — SUMMARY

**The definitive ENSEMBLE ceiling test on the FBA-blind non-metabolic essential half.**
NOT a new signal — the ensemble UPPER-BOUND of the four signals that each individually failed
(MET4 PPI / NONMET1 synteny / REGNET1 regulatory / PLMESS1 ESM-2).

## Verdict: NEGATIVE (first-class) — the definitive ensemble-ceiling closure
Even the COMBINATION of ALL four homology-independent non-metabolic signals does NOT beat
conservation-breadth alone by the pre-registered +0.03 margin. Conservation-breadth is the
unbeaten ceiling for the FBA-blind non-metabolic essential half, even by all signals combined.

Reproduced x2 BYTE-IDENTICAL — payload SHA-256
`e6badcb77c23860d874bd6a1c4b32ddeb23361b218f8c8a77e73ce18325aa481`.

## Pool (reused EXACTLY from NONMET1/PLMESS1)
E. coli non-metabolic subproteome, n = 2547, essential = 179, prevalence 7.03%. Truth = PEC class-1.
Baseline conservation AUROC = **0.9078**, reproducing NONMET1 exactly (independent consistency check).

## Mapping coverage per source (honest)
| Source | Feature | Coverage | Default for missing |
|--------|---------|----------|---------------------|
| Conservation (NONMET1) | own | 2547/2547 (100%) | none (computed for all) |
| Genomic context (NONMET1) | ctx, cond | 2547/2547 (100%) | 0 (no conserved neighborhood) |
| Regulatory (REGNET1 Abasy GRN, 1202 nodes/3148 edges) | outdeg, indeg | **412/2547 (16.2%)** | 0 (absence of edge == degree 0) |
| PLM embedding (PLMESS1 ESM-2, cached) | 640-d -> PCA-50 | 2547/2547 (100%) | none; PCA fit train-fold-only |

## Pre-registered gate
ΔAUROC = AUROC(FULL ENSEMBLE C+G+R+E) - AUROC(conservation C alone), same no-leakage 5-fold CV.
PASS iff ΔAUROC >= +0.03 for logistic (primary) AND GBM corroborates. NEGATIVE otherwise.

## Ensemble vs conservation ΔAUROC (both models)
| Model | Conservation alone | Full ensemble | ΔAUROC | Gate +0.03 |
|-------|--------------------|---------------|--------|------------|
| Logistic (L2) | 0.9078 | 0.9267 | **+0.0189** | FAIL |
| Gradient boosting | 0.9037 | 0.9132 | **+0.0095** | FAIL |

Both below the +0.03 bar -> NEGATIVE.

## Drop-one ablation (marginal contribution to the FULL ensemble)
Logistic: genomic-context **+0.0131** (largest), conservation +0.0069, embedding +0.0037,
regulatory **-0.0021** (slightly hurts). GBM: same ordering, all small. No single signal — nor
their union — clears the gate. The signals are collinear with conservation (NONMET1's r=0.84
synteny finding), so combining them yields no independent lift.

## Leakage checks (triple-check trigger did NOT fire)
- PCA + all scalers fit on TRAIN FOLDS ONLY (no test-fold information).
- Ensemble WITHOUT the embedding (C+G+R): logistic AUROC 0.9230 (Δ +0.0152), GBM 0.9082 (Δ +0.0045).
- Adding the embedding on top of C+G+R lifts logistic only +0.0037 -> the embedding is NOT the driver.
- The ensemble does NOT pass "only via the embedding" (it does not pass at all), so there is no
  high-dim/PCA inflation artifact to defend. ensemble_passes_only_via_embedding = false for both models.
- Standalone embedding AUROC 0.878 (logit) < conservation 0.908 — consistent with PLMESS1.

## LEDGER verdict (one line)
**MULTISIG1 (reproduced x2, sha e6badcb7): NEGATIVE = the definitive ensemble-ceiling closure —
the COMBINATION of all four homology-independent non-metabolic signals (conservation + genomic
context + regulatory degree + ESM-2 PLM) does NOT beat conservation-breadth alone (logistic
ΔAUROC +0.019, GBM +0.009; gate +0.03); the signals re-encode conservation so their union adds
no independent lift; conservation-breadth (AUROC 0.908) is unbeatable even by all signals combined.**

## Scope
E. coli, non-metabolic subproteome, enrichment/prediction-only, in-silico, CPU, cached-data-only.
Caveats inherited from sources: small CPU ESM-2 (150M); Abasy 2005 GRN coverage (16.2%);
single-organism truth (PEC).
