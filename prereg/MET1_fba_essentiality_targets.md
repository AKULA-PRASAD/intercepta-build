# MET1 — Does mechanistic FBA gene-essentiality enrich for drug targets BEYOND the conservation ceiling? (finalized 2026-08-02, PRE-RESULT)

(MET1 = first MECHANISTIC target-ID chapter — an orthogonal, non-homology signal, to test whether it breaks the conservation ceiling the whole TID1–TID4 arc hit.)

## Why (the highest-stakes target-ID test yet)
TID1–TID4 established that every sequence-based target-ID signal (homology, structure) ≈ generic CONSERVATION — a robust
ceiling. FBA gene-essentiality is fundamentally different: from an organism's own genome-scale metabolic model it asks
"is this gene's deletion LETHAL given the reaction network + growth medium?" — a mechanistic, non-homology signal,
computable per-organism from sequence alone (works for a novel pathogen, zero activity data). MET1 tests whether this
orthogonal signal **enriches for known drug targets BEYOND conservation** — i.e. whether it breaks the ceiling. Chosen
autonomously after a Phase-0 that ranked it top by (value × CPU-feasibility × honest-validatability).

## Feasibility (verified 2026-08-02)
COBRApy 0.31.1 + GLPK solver install/run on arm64 (no GPU); iML1515 loads in 3s, genome-wide single-gene-deletion ≈ 13s;
**1515/1516 BiGG genes carry a UniProt xref** → FBA-essentiality links directly to the UniProt ChEMBL-xref drug targets
we already have. GEMs available: E. coli iML1515, S. aureus iYS854, K. pneumoniae iYL1228 (Mtb/P. aeruginosa GEMs not in
the BiGG loader — noted).

## Data (OPEN; on hand + BiGG)
Per organism (E. coli primary + S. aureus, K. pneumoniae robustness): BiGG GEM (COBRApy); drug-target positives =
UniProt ChEMBL-xref accessions (TID1/TID4 data); gene protein sequences (UniProt reference proteomes) for the
conservation signal. Analysis restricted to the METABOLIC subproteome (genes in the GEM) — FBA cannot speak to
non-metabolic genes (a stated scope limit; ~1500 of ~4500 proteins).

## Design (gene-level; is a mechanistic signal orthogonal to + additive over conservation?)
For each organism's GEM genes (mapped to UniProt): (1) **FBA essentiality** = COBRApy single_gene_deletion, essential if
KO growth < 1% of WT (deterministic; default medium); (2) **is_drug_target** = gene ∈ organism's ChEMBL-xref targets;
(3) **conservation** = mmseqs2 best-homology-bits of the gene to the OTHER organisms' known targets (leave-organism-out,
the TID1 signal). Pool genes across organisms + per-organism.

## Metrics / tests
- **H1 (enrichment):** drug-target rate among FBA-essential genes vs non-essential (Fisher odds-ratio + rates); AUROC of
  essentiality (binary) vs is_target.
- **H2 (DECISIVE — beyond conservation):** gene-level held-out logistic `is_target ~ conservation + essentiality`
  (standardized) — is the essentiality coefficient significant AND does nested ΔAUROC (conservation+essentiality vs
  conservation-only) > 0? Only additive lift over conservation counts (the TID2/TID1 discipline).
- **Optional validation of FBA-essentiality itself:** if an experimental essential-gene set is reachable (e.g. E. coli
  Keio), report FBA precision/recall/MCC vs it; else report the FBA-essential set + its known modest-precision caveat.

## Hypotheses (pre-registered)
- **H1 TRUE:** FBA-essential metabolic genes are enriched for drug targets (odds-ratio > 1, significant) — essentiality
  carries target signal.
- **H2 TRUE (breaks the ceiling):** essentiality retains a **significant positive coefficient after partialling out
  conservation**, AND conservation+essentiality beats conservation-only (nested ΔAUROC > 0.02 with a gene-majority) →
  the FIRST orthogonal signal that adds target-ID information beyond conservation. A genuine capability gain.
- **H0 (first-class, expected-allowed):** essentiality adds nothing beyond conservation (H2 fails) → even a mechanistic,
  non-homology signal is largely captured by conservation (essential genes are conserved) → the ceiling is DEEPER than
  homology; the honest boundary tightens.

## Honesty / scope
Retrospective; METABOLIC subproteome only (FBA blind to non-metabolic targets — the majority; stated); default growth
medium (essentiality is medium-dependent — a caveat); FBA essentiality has known modest precision (many false positives);
3 organisms (E. coli powered, S. aureus/K. pneumoniae smaller); essential genes ARE conserved so the residual-after-
conservation (H2) is the honest test (guards circularity); not wet-lab.

## Reproducibility
Deterministic (FBA/LP deterministic given model+medium; mmseqs fixed; model seed n/a). FBA-essentiality cached as a data
artifact (regenerable). Reproduce ×2 byte-identical (payload over per-organism + pooled metrics). Output:
`experiments/MET1_fba_essentiality_targets/results/MET1_metrics.json`. Envs: `metabolic` (cobra), `bioinfo` (mmseqs2),
`intercepta-build` (analysis). Feasibility-gated: build FBA-essentiality cache (metabolic env) → smoke-test the analysis
on E. coli before the full run.
