# REGNET1 — pre-registration (frozen before results)

**The #1 gap in INTERCEPTA's core (Phase-1 audit):** no validated, homology-independent MECHANISTIC signal for the
**non-metabolic** essential half. MET4 (STRING PPI centrality) died of STUDY BIAS; NONMET1 (synteny) was study-bias-free
but merely re-encoded conservation. This is the principled third attempt, addressing MET4's exact flaw.

## Hypothesis
Non-metabolic essentiality is predicted by position in a **curated, experimentally-derived transcriptional regulatory
network** — specifically **master-regulator influence (regulatory out-degree)**: a TF regulating many genes is essential
because its loss dysregulates the cell. Because the edges are experimentally curated (RegulonDB-derived, via Abasy Atlas
`511145_v2005_sRDB04`, sha c1f625e5; 1202 genes / 3148 TF→gene edges), the signal is **study-bias-resistant by source**
(unlike MET4's literature co-mention PPI) and — being about the regulatory neighborhood, not the gene's own conservation —
is **not a restatement of sequence conservation** (unlike NONMET1).

## Method (identical rigor to NONMET1, for direct comparability)
- Directed regulatory graph from the curated edges (source=regulator → target). Per gene: **out-degree** (master-regulator
  influence), in-degree, betweenness, is_TF.
- Restrict to the **NON-METABOLIC subproteome** (E. coli genes NOT in the MET2 GEM). Truth = PEC experimental essentiality.
  Map Abasy gene names → NONMET1 E. coli genes by gene symbol.
- Tests: (a) enrichment of high regulatory out-degree for PEC essentiality (2×2 Fisher OR, p); (b) DECISIVE — 5-fold-CV
  logistic **ΔAUROC of regulatory features BEYOND conservation breadth** (own); (c) **MET4 control** — regress out the PEC
  publication count (study proxy); the regulatory lift must SURVIVE.

## Pre-registered gate
- **PASS** ⇔ ΔAUROC(regulatory beyond conservation) ≥ **+0.03** AND enrichment OR > **2** (Fisher p<0.01) AND the lift
  **survives the study-bias (publication-count) control**. ⇒ the first validated non-metabolic mechanistic signal.
- **FAIL (first-class NEGATIVE)** ⇔ otherwise — the **third principled closure** of the non-metabolic-mechanism door
  (MET4 PPI / NONMET1 synteny / REGNET1 regulatory), a strong publishable bound.

## Honesty / scope
Abasy `v2005_sRDB04` is the **2005 curated** RegulonDB-derived network — smaller than current RegulonDB (coverage
limitation; curation, the load-bearing property, is preserved). RegulonDB itself is incomplete (well-studied TFs have more
curated targets) → a POSITIVE could be residual study bias, which is EXACTLY why the publication-count control (c) is
mandatory and decisive. E. coli only, non-metabolic subproteome, enrichment-only, in-silico. Deterministic; reproduce ×2.
Frozen before running.
