# BLIND5 — FIRST EUKARYOTE in the prospective-blind suite (*Komagataella phaffii* GS115) — SUMMARY

**GATE: FAIL (honest negative).** Pre-registered gate (OR>3 AND p<0.01, identical to BLIND1-4) frozen and
git-committed (commit 1067834) BEFORE the experimental essential set was consulted. Reproduced x2 byte-identical.
Predictions unchanged (lock sha re-verified intact). Not re-tuned.

## What this tested
First crossing of the prokaryote/eukaryote divide UNDER THE LOCK-BEFORE-REVEAL protocol (BLIND1-4 are all bacteria;
HARDENF1/GENERALIZE4 tested eukaryotes but retrospectively, not blind). Organism: *Komagataella phaffii* strain
GS115 (= *Pichia pastoris*), a eukaryote genuinely never used here and whose essentiality was never inspected before
the lock. A model/industrial yeast, not a clinical pathogen (disclosed) -- the value is the blind kingdom crossing.
The three suggested WHO fungal pathogens (Cryptococcus neoformans, Candida glabrata, Candida auris) have NO
genome-wide essentiality entry in DEG and no open genome-wide screen could be confirmed CPU-only, so the
best-supported fully-verifiable eukaryote was chosen (per the directive's own S. pombe-style fallback).

## Data (open, CPU-only)
- **GEM (curated):** iMT1026 v3 (Tomas-Gamisans et al.), BioModels MODEL1612130000, 1026 genes / 2237 rxns /
  1706 mets, WT growth 0.057750, gene IDs = GS115 `PAS_` systematic locus tags.
  sha256 `55b0e634d25ee0970103ae905e8c33ccb23377f464461181411930c9c998ad01`. A curated GEM was used (not de-novo
  CarveMe) because CarveMe's universe is BACTERIAL -- a eukaryote carve would be low quality.
- **Proteome (ID map):** UniProt UP000000314 (GS115, 5038 proteins),
  sha256 `9d56862fa4a6c880bebc023dcff297a5ec3f7e30ef7a9421666eea2f4e1fde09`.
- **Experimental essentiality (revealed in Stage 2):** DEG2027 = Zhu et al. 2018 *Sci Rep* (PMID 29976927),
  genome-wide **Tn-seq**, GS115, **753 essential genes**, assembly GCF_000027005.1.
  DEG20.aa.gz sha256 `a9e7612dd38b9243b14fc71a9db81b651cbfce694cd731a524338c62f868413f`;
  deg_annotation_e.csv provides a GS115 `locus_tag:` for each gene -> direct namespace match to our GEM.

## Locked FBA predictions (Stage 1, committed before reveal)
COBRApy single_gene_deletion, essential iff KO growth < 1% WT, solver = GLPK float + **presolve** (presolve required:
the default float simplex CYCLES indefinitely on gene PAS_chr3_0036 / rxn AMETtm; presolve removes the degeneracy),
processes=1. **147 of 1026 genes FBA-essential.**
**LOCKED_predictions.sha256 = `8d0822054d41ae86174305982106a355b800208f83048a445309be2de8dfe521`** (re-verified intact).
Solver-sensitivity caveat: ~20 borderline genes at the threshold are solver-dependent (exact-rational would call 167);
the committed pre-registered set is the 147-gene float+presolve set and is what was scored (no post-hoc re-scoring).

## Result (gate frozen before scoring)
Adjudication = DIRECT GS115 locus-tag match (exact same-strain namespace; no mmseqs bridge needed -- unlike BLIND1-3).
174 of the 752 DEG2027 loci fall inside the 1026-gene GEM universe.
**2x2: both 43 / FBA-only 104 / exp-only 131 / neither 748.**
**OR 2.361, Fisher one-sided p 4.00e-05, precision 0.293, recall 0.247.** Reveal payload sha256
`138a6b17eb2155135b5be684568f7a26420d4292753452e1dbf0cd78d287683a` (reproduced x2 byte-identical).

## Meaning + honest caveats (first-class)
- **FAIL, but a directional POSITIVE that misses the effect-size bar.** The enrichment is highly significant
  (p = 4.0e-05 << 0.01): FBA-essential genes ARE over-represented among experimental essentials. But the odds
  ratio 2.36 does not clear the pre-registered OR>3 gate. So on the first blind eukaryote the signal transfers in
  direction but is weaker than on most bacteria.
- **Suite (identical protocol/gate):** BLIND1 6.13 / BLIND2 3.92 / BLIND3 8.03 / BLIND6 4.23 PASS;
  BLIND4 2.96 / **BLIND5 2.36** / BLIND7 0.64 FAIL. BLIND5 sits with BLIND4 as a just-below-gate honest negative --
  a bacterium-calibrated OR>3 bar is not automatically cleared by a healthy curated eukaryote GEM.
- **Scope:** essentiality-ENRICHMENT only; in-silico FBA vs a published Tn-seq screen (not wet-lab); curated model is
  still a model (rich default medium rescues biosynthetic essentials -> low recall 0.247); non-essential-by-absence
  convention; single organism. Not drug-target / selectivity / clinical.

## Bottom line
The prospective-blind protocol now spans the prokaryote/eukaryote divide. On the first blind eukaryote the FBA
essentiality signal is genuine and statistically significant but sub-threshold (OR 2.36 < 3) -> honest FAIL,
reported first-class and not re-tuned. This module did NOT git commit; the orchestrator commits the reveal.
