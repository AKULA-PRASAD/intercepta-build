# CANCERCLASS1 — cancer-LINEAGE deployment envelope for zero-data functional-dependency target-ID (PRE-REGISTRATION)

*Locked 2026-08-11, before computing any per-lineage statistic. Completes the deployment-envelope picture for
the human arms: GENETICCLASS1 gave the DISEASE-CLASS envelope for the genetic arm; this gives the CANCER-LINEAGE
envelope for the functional-dependency arm (DEPEND1). Extends the transfer-condition principle to cancer
lineages — for which cancer contexts does zero-data dependency target-ID transfer, and where should the router
cap/abstain? DEPEND1 validated the signal pooled + split-by-lineage-for-CV, but never reported the PER-LINEAGE
recovery envelope. Validated on cached data (DepMap CRISPR + IntOGen); falsify-first (a no-signal lineage is a
first-class ABSTAIN).*

## Data (open; figshare-mirrored DepMap, IntOGen cached)
- **Observable:** DepMap 22Q2 `CRISPR_gene_effect.csv` (Chronos gene-effect, cell lines × genes; more negative =
  more essential) + `sample_info.csv` (cell line → lineage), from figshare article 19700056 (public mirror of
  the DepMap portal). `$INTERCEPTA_DATA/depmap_cancer_envelope/`.
- **Ground truth (independent of the observable):** IntOGen `Compendium_Cancer_Genes.tsv` cancer-driver symbols
  (`$INTERCEPTA_DATA/f3clin1/2024-06-18_IntOGen-Drivers/`), cached. Non-circular: drivers are curated from
  patient mutation data, NOT from DepMap dependency.

## Method (deterministic; DEPEND1's confound guards)
1. **Pan-essential guard (mandatory):** exclude genes essential (gene-effect < −0.5) in ≥ 90% of lines — these
   are trivially pan-essential, NOT selective; a lineage envelope must be about SELECTIVE dependency.
2. **Per lineage** with ≥ **MIN_LINES = 15** cell lines: lineage-selective-essentiality score per (non-pan)
   gene = (overall mean gene-effect) − (lineage mean gene-effect) [positive = more essential in THIS lineage
   than overall]. Rank genes desc.
3. **Recovery:** recovery@K (K=20) = fraction of the lineage's top-K selective dependencies that are IntOGen
   drivers.
4. **Null + significance:** permutation null — shuffle lineage labels across lines, recompute recovery@K,
   B = 1000 perms (seed 42); enrichment = recovery / mean(null recovery); one-sided permutation p.

## Pre-registered per-lineage GATE (the deployment envelope → router transfer-condition table)
- **FULL** iff recovery-enrichment ≥ 3.0 **AND** permutation p < 0.05.
- **CAPPED** iff enrichment ≥ 1.5 (or p < 0.05 but enrichment < 3.0) — signal present but weaker.
- **ABSTAIN** iff enrichment < 1.5 AND p ≥ 0.05 — no robust lineage-level driver recovery.

## Hypothesis (falsifiable)
The functional-dependency signal is **non-uniform across cancer lineages** — stronger in oncogene-addicted/
driver-dependency-rich lineages, weaker where selective dependencies are not driver-linked. PASS = the envelope
discriminates (≥1 FULL AND ≥1 non-FULL by the locked gate). A uniform result (all FULL or all ABSTAIN) is
reported honestly as-is.

## Integration
Emit `cancer_lineage_transfer_table.json` (lineage → grade + evidence) — the cancer-arm analog of GENETICCLASS1's
disease-class table and the FBA organism-class table; a candidate refinement for the router's human_cancer arm.

## Rigor / scope
Reproduce ×2 byte-identical (deterministic; permutation seed 42). Honest scope: characterizes the DEPLOYMENT
ENVELOPE of a validated arm across cancer lineages (coverage, not a new method); cell-line dependency (not
patient/clinical); IntOGen driver recovery is target-RELEVANCE, not a validated drug target. `results/
CANCERCLASS1_metrics.json` (sorted keys) + `payload.sha256`; DepMap data NEVER committed.
