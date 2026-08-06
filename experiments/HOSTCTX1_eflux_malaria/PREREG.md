# HOSTCTX1 — pre-registered test: does EXPRESSION-CONSTRAINED context-specific FBA (E-Flux) RESCUE the malaria essentiality signal?

**Registered (Stage 1) BEFORE computing any E-Flux contingency table, odds ratio, Fisher p, precision, recall, or AUROC.**
The plain-FBA baseline numbers are already known (they are GENERALIZE5's published result, reproduced here as an
anchor). The E-Flux context-specific enrichment answer has NOT been looked at when this file is written. Expression
source format (columns, coverage) was inspected to design the mapping — that is method design, not outcome.

## Motivation / the wall
GENERALIZE5 found FBA gene-essentiality FAILS the bacterial-standard gate on *P. falciparum* (iPfal19): OR 2.469,
Fisher p 0.00217, precision 0.797, recall **0.201** (contingency both 55 / FBA-only 14 / exp-only 218 / neither 137,
n=424 mapped). Diagnosis: the parasite salvages metabolites from the host RBC, so the default-medium GEM finds
metabolic "workarounds" → 218 experimentally essential genes read FBA-DISPENSABLE → low recall. This experiment tests
whether adding BIOLOGICAL/HOST CONTEXT via expression-constrained E-Flux FBA rescues the signal.

## Hypothesis
H1 (RESCUE): E-Flux context-specific single-gene-deletion essentiality on iPfal19 — constraining reaction flux
capacities by blood-stage (asexual intraerythrocytic) transcript abundance — is MORE enriched for the parasite's
experimentally essential genes (Zhang 2018 piggyBac) than plain default-medium FBA, and clears the bacterial gate.

## Clean controlled A/B (change ONLY the context constraint)
Everything is reused BYTE-for-BYTE from GENERALIZE5: same GEM `iPfal19.xml`, same experimental truth
`zhang2018_essentiality.csv` (essential = phenotype `"Non - Mutable in CDS"`), same alias map
`Pfalciparum3D7_GeneAliases.csv`, same gene-ID canonicalization, same 2x2 Fisher gate, same essential-if-KO-growth
`< 1% of WT` rule, same 6-dp rounding of KO growth (GLPK jitter control). The plain-FBA arm is recomputed in the same
script and MUST reproduce GENERALIZE5 (OR 2.469, contingency 55/14/218/137) or the comparison is declared invalid.
The ONLY difference between arms is the E-Flux flux-capacity layer.

## Expression source (fixed now)
**Malaria Cell Atlas** (Howick et al. 2019 *Science* 365:eaaw2619; single-cell RNA-seq across the *P. falciparum* life
cycle; open via PlasmoDB / malariacellatlas.org), asexual blood-stage mean expression per gene keyed by PF3D7_ locus
tag, as redistributed in the PlasmoDB / Pf Target Browser gene-annotation table (Figshare 27190545), columns
`MalariaCellAtlas {Ring,Trophozoite,Schizont} Mean Expression`. **PRIMARY stage = Trophozoite** (metabolically most
active asexual blood stage). 5176 genes carry MCA values; 412/475 model genes match directly (more via aliases).
Coverage + sha256 recorded in results. Values are normalized single-cell means (range 0–4.4, median 0.30).

## E-Flux implementation (Colijn et al. 2009 PLoS Comput Biol) (fixed now)
1. Reaction expression score via GPR on the gene→expression map: **AND → min**, **OR → sum** (canonical), parsed from
   `gene_reaction_rule` via the Python AST (handles nested parentheses).
2. Gene→expression: direct PF3D7_ match, else alias→canonical→MCA, else **default = median MCA value over covered
   model genes** (documented).
3. Bounds: gene-associated reactions get flux capacity proportional to score, **canonical median normalization**:
   `scale = 1000 / median(score over gene-associated reactions with score>0)`; `bound = scale * score`.
   Reversible → `[-bound, +bound]`; irreversible-forward → `[0, +bound]`; irreversible-reverse → `[-bound, 0]`.
   Gene-associated reactions with score 0 get a small epsilon bound (`1e-3`, near-shutdown).
   **Non-gene-associated reactions (exchanges/uptake/spontaneous) keep their ORIGINAL bounds** — the medium/uptake is
   held identical to baseline so the A/B isolates the expression layer.
4. Essentiality on the E-Flux-constrained model: COBRApy `single_gene_deletion` (KO zeroes a gene's reactions via
   GPR, on top of the E-Flux bounds); essential if KO growth `< 0.01 * constrained-WT`; KO growth rounded to 6 dp.

## Pre-registered decision gate (fixed now)
2x2 Fisher exact (one-sided, greater) over the SAME mapped metabolic genes; report OR, p, precision, recall, AUROC,
full contingency for BOTH plain-FBA and E-Flux side by side, plus deltas.
- **RESCUE (PASS)** iff E-Flux clears **OR > 3 AND p < 0.01 AND improves over the plain-FBA baseline** (higher OR).
- **PARTIAL** iff E-Flux significantly/materially improves over baseline (higher OR, still p<0.01) but OR still < 3.
- **NEGATIVE (FAIL)** iff E-Flux does not improve over baseline, or is worse — reported first-class, never re-run to a
  nicer number. The wall is then deeper than expression-context.

## Sensitivity / robustness (fixed now — conclusion must be robust to arbitrary E-Flux scaling)
Rerun the E-Flux arm under: (a) blood stage = Schizont, Ring, and IDC-average (mean of Ring/Troph/Schizont);
(b) scaling variants: bound capped at original 1000 vs uncapped; max-normalization instead of median; epsilon ∈ {0, 1e-3}.
Report whether the RESCUE/PARTIAL/NEGATIVE verdict flips under any variant.

## Scope / confounds (fixed now)
Essentiality-enrichment only; in-silico vs a published screen (not wet-lab); E-Flux scaling is somewhat arbitrary
(hence the sensitivity sweep); expression is one stage / one atlas; recall may rise while precision falls (both
reported); base-rate of experimental essentiality is high (~64%) which mechanically compresses OR; n=1 parasite, one
curated model. Deterministic; reproduced x2 byte-identical (SHA-256 over sorted-key metrics payload excluding
verdict/provenance).
