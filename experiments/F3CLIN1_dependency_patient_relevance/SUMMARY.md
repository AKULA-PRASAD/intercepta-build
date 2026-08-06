# F3CLIN1 — Do DEPEND1 selective cell-line dependencies bridge to PATIENT-tumor driver biology? — SUMMARY

**Verdict: PASS** (all pre-registered conditions met, incl. both study-bias controls). Reproduced x2
byte-identical. Payload SHA-256: `a7d00ee7392d1904ab58e4a08289f7ee9fbf012f526b3a4cdaa9dbec62a79060`.

DEPEND1's SELECTIVE cancer cell-line CRISPR dependencies are ENRICHED for genes recurrently altered as DRIVERS
in PATIENT tumors — a cell-line->patient TARGET-RELEVANCE bridge. This is DISTINCT from, and does NOT rescue,
the failed human drug-RESPONSE line (B20 FIMM FAILS, B10 TCGA confounded, B17 BeatAML null).

## Inputs (open; sha in PREREG section 1)
- SELECTIVE set: re-derived from DepMap Chronos gene-effect with DEPEND1's EXACT frozen definition
  (dep_frac 0.01-0.50; pan-essential >0.90 excluded). Re-derivation reproduced DEPEND1's **3664** selective
  genes exactly (assert in code); pan-essential = 1020, both excluded from the target claim.
- Universe = **17931** DepMap-screened genes.
- Patient driver ground truth: IntOGen Compendium of Cancer Genes, release **2024-06-18** (CC0 / public
  domain), 633 driver genes across 260 cohorts / 86 cancer types with patient RECURRENCE; **622** are screened
  in DepMap (11 not screened, recorded, excluded from the 2x2).
- Study-bias proxy: CancerMine `NUM_PAPERS` per gene (IntOGen Unfiltered file), covering 7339 universe genes.

## Primary enrichment (2x2 Fisher, over the 17931-gene universe)
Selective-intersect-driver = 240; driver rate among selective = **6.55%** vs **2.68%** among non-selective.
**Fisher OR = 2.55, p = 3.4e-26.**

## Mandatory study-bias / confound guards
- **(a) Random-gene null** (K=10000): observed overlap 240 vs expected 127 (95th pct 143); empirical
  p = 1e-4. Enrichment is far above a random-gene draw.
- **(b) Publication-matched null** (K=10000, matched on NUM_PAPERS deciles): observed 240 vs matched-null
  mean 133 (95th pct 149); empirical p = 1e-4. Enrichment survives matching on a publication-count background.
- **(c) Mantel-Haenszel** OR stratified by NUM_PAPERS decile: **MH OR = 2.72, CMH p = 3.8e-29.** Enrichment
  survives adjusting for how well-studied genes are. (Honest caveat: CancerMine driver-citation counts are
  partially circular with driver status, so this control is CONSERVATIVE / possibly over-correcting; the OR
  actually rose slightly under stratification, consistent with the signal not being a fame artifact.)
- **Pan-essential** genes (housekeeping) were excluded a priori from the selective set — cannot inflate.

## Supporting
- **Recurrence dose-response:** enrichment is STRONGER for more-recurrent drivers — recurrent drivers
  (n_cohorts >= 5) OR = **3.69** (p = 6.7e-20) vs focal/rare drivers OR = **2.00** (p = 4.8e-10). The signal
  tracks patient recurrence, as expected if it reflects real driver biology.
- **Reverse-direction sanity:** ranking selective genes by selectivity strength, the top-50 are **32%** patient
  drivers, top-100 30%, top-200 21% — vs a universe base rate of **3.5%** (~9x enrichment at the top).
  Top selectively-essential examples (drivers starred): KRAS*, TYMS, CFLAR, HNF1B, NXT1, IRF4*, SOX10,
  SEPHS2, MDM2*, CTNNB1*, NMNAT1, FERMT2, CBFB*, UMPS, NRAS*. (Non-driver top hits like TYMS/UMPS/SEPHS2 are
  known selective metabolic dependencies, not mutational drivers — a correct, informative distinction.)

## What this DOES and does NOT establish (scope honesty)
- **DOES:** cancer CELL-LINE selective CRISPR dependencies are enriched (OR~2.5, ~9x at the top, dose-response
  with recurrence) for genes that are recurrent DRIVERS in PATIENT tumors, and this survives a random-gene
  null AND two study/annotation-bias controls. The DEPEND1 target-ID layer surfaces patient-relevant driver
  biology — the honest F3 reframe is validated for TARGET RELEVANCE.
- **Does NOT:** rescue patient drug-RESPONSE prediction (B20 FIMM external replication FAILS, B10 TCGA is
  cancer-type confounded, B17 BeatAML survival is an honest null); it is NOT clinical outcome, NOT wet-lab,
  NOT a novel-pathogen result. A residual study/annotation-bias caveat remains even after the controls. This
  must never be read as "clinical validation."

## Reproducibility
run.py -> results/F3CLIN1_metrics.json (sorted keys) + results/payload.sha256. Payload SHA-256 over sorted-key
JSON of numeric results (excludes verdict/provenance); run twice, identical
(`a7d00ee7392d1904ab58e4a08289f7ee9fbf012f526b3a4cdaa9dbec62a79060`). Seed 42, K=10000. No git commit/push;
no data committed.
