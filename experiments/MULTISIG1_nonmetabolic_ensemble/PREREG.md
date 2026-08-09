# MULTISIG1 — PRE-REGISTRATION (LOCKED BEFORE SCORING)

## Context / prior closures
Four INDIVIDUAL homology-independent signals each FAILED to beat the conservation-breadth
baseline (`own`, AUROC ~0.908) on the FBA-blind **non-metabolic** E. coli essential half:

| Exp | Signal class | ΔAUROC beyond conservation | Verdict |
|-----|--------------|----------------------------|---------|
| MET4 | PPI-network centrality | +0.128 → **collapses to −0.004** under study-bias control | NEGATIVE (study-bias artifact) |
| NONMET1 | genomic context / synteny | **+0.0158** | NEGATIVE (collinear r=0.84 w/ conservation) |
| REGNET1 | curated regulatory GRN degree | **−0.006** | NEGATIVE (clean null) |
| PLMESS1 | ESM-2 learned PLM embedding | **+0.008** | NEGATIVE (re-encodes conservation) |

## THE QUESTION (ceiling test, NOT a new signal)
Individually each signal fails. **Does their COMBINATION (ensemble) beat conservation-alone
by a decisive margin?** This is the definitive ensemble UPPER-BOUND: if even ALL non-metabolic
signals combined cannot crack the non-metabolic half, conservation-breadth is the closed ceiling.

## Scope
E. coli, non-metabolic subproteome (UniProt NOT in the MET2 GEM), enrichment/prediction-only,
in-silico, CPU, cached-data-only. NO external fetch. NO wet-lab.

## Pool (reused EXACTLY from NONMET1 / PLMESS1)
- NONMET1 E. coli non-metabolic pool: non-metabolic ∧ has PEC essentiality call.
- Confirmed n = 2547, essential = 179, prevalence 7.03% (byte-consistent with NONMET1 & PLMESS1).
- Target y = PEC class-1 essential.

## Feature sources & alignment (aligned to the SAME NONMET1 pool, by locus_tag / gene-symbol)
1. **Conservation-breadth** `own` — fraction of 11 panel bacteria with an RBH ortholog (NONMET1). Coverage 2547/2547 (100%). THE BASELINE.
2. **Genomic-context** `ctx`,`cond` — synteny-neighborhood conservation breadth + conditional synteny (NONMET1). Coverage 100% (0 for genes with no conserved neighborhood, already the natural value).
3. **Regulatory** `outdeg`,`indeg` — Abasy 2005 curated GRN out/in-degree, mapped by gene-symbol (REGNET1). Coverage **412/2547 (16.2%)**. Genes not in the GRN get the DOCUMENTED DEFAULT **0** (absence-of-regulatory-edge == degree 0), matching REGNET1's handling. No imputation flag (0 is the meaningful value, not "missing").
4. **PLM embedding** `EMB` — ESM-2 esm2_t30_150M mean-pooled 640-d, cached per locus_tag by PLMESS1. Coverage **2547/2547 (100%)** — reused EXACTLY from cache, NOT re-embedded. PCA-reduced (k=50, LOCKED, fit TRAIN-FOLDS-ONLY).

## Models (both reported)
- **Logistic (L2)**: `LogisticRegression(C=1.0, solver=lbfgs, max_iter=2000)`.
- **Gradient boosting**: `GradientBoostingClassifier(random_state=0)` sklearn defaults (deterministic, subsample=1.0).

## CV protocol (LOCKED, identical to NONMET1/PLMESS1)
- `StratifiedKFold(n_splits=5, shuffle=False)` — deterministic, no RNG.
- Pooled out-of-fold AUROC.
- **Leakage guard**: within each fold, StandardScaler (scalar features) AND the embedding
  StandardScaler + PCA(k=50, svd_solver='full') are fit on the TRAIN folds ONLY, then applied to test.
  No feature scaling, PCA, or selection uses any test-fold information.

## Feature groups
- C = conservation (`own`)                 [baseline]
- G = genomic context (`ctx`,`cond`)
- R = regulatory (`outdeg`,`indeg`)
- E = PLM embedding (PCA-50)
- FULL ENSEMBLE = C + G + R + E

## PRE-REGISTERED GATE (locked before any scoring)
Primary metric = ΔAUROC = AUROC(FULL ENSEMBLE) − AUROC(conservation C alone), under the SAME
no-leakage CV, for EACH model (logistic and GBM).

- **PASS** iff ΔAUROC(ensemble − conservation) **≥ +0.03** for the logistic model (primary),
  AND the GBM directionally agrees (ΔAUROC_GBM ≥ +0.03). (Report both; the decisive claim
  requires the primary logistic gate; GBM is the corroborating model.)
- **NEGATIVE** iff the ensemble does NOT beat conservation by ≥ +0.03 → the definitive
  ensemble-ceiling closure: conservation-breadth is unbeatable even by all signals combined.

## Ablation (drop-one marginal contribution) — reported regardless of verdict
For each signal S ∈ {C, G, R, E}: marginal = AUROC(FULL) − AUROC(FULL minus S).
Positive marginal ⇒ S adds signal in combination. Reported for both models.

## Leakage triple-check (mandatory if ensemble "passes" via the embedding)
- Report ensemble AUROC WITH and WITHOUT the embedding (C+G+R vs C+G+R+E).
- If the ensemble passes ONLY because of E, triple-check it is not a high-dim/PCA leakage
  artifact (PCA fit train-only already; additionally report standalone-E AUROC and the
  C+G+R-without-E result) BEFORE any ceiling-break claim.

## Reproducibility
Deterministic (fixed seeds, no shuffle). SHA-256 over sorted-key JSON payload EXCLUDING
`verdict` and `provenance`. Must reproduce x2 byte-identical.

## Expectation (honest prior)
Given the four individual closures each RE-ENCODE conservation (NONMET1 r=0.84; PLMESS1
standalone AUROC 0.878 < 0.908; REGNET1 clean null), I EXPECT the ensemble does NOT beat
conservation by +0.03 → the DECISIVE ensemble-ceiling closure. If it DOES add, report the
genuine integration gain + which signal(s) drive it (with the leakage triple-check). NO tuning to pass.
