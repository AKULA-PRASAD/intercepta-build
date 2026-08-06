# GENERALIZE4 — does FBA gene-essentiality generalize from BACTERIA to a EUKARYOTE?

**Pre-registered (Stage 1) BEFORE computing the 2x2 Fisher / any gate score.** Method, data, ID-mapping
strategy and the decision rule are fixed here first. The metrics are produced by `run.py` in a later step and
reported (PASS/FAIL) exactly as written below — negatives are first-class and will not be hidden or re-run to a
nicer number.

## Organism & rationale
**Saccharomyces cerevisiae** (model eukaryote). INTERCEPTA has validated that COBRApy single-gene-deletion FBA on
genome-scale metabolic models (GEMs) is enriched for EXPERIMENTAL essential genes across a 6-organism, cross-
Gram / cross-phylum BACTERIAL panel (E. coli, K. pneumoniae, Salmonella, B. subtilis, S. aureus/MRSA, M. tuberculosis)
plus a prospective-blind test on N. gonorrhoeae. Every organism so far is a **bacterium**. This experiment tests
whether the same in-silico signal transfers to a **eukaryote** — a distinct disease class.

*Candida albicans* is the true fungal-pathogen goal (curated GEM + GRACE/transposon essentiality). We use
S. cerevisiae instead because it provides the single cleanest eukaryotic essentiality label in existence — the
systematic genome-wide deletion collection (Giaever et al. 2002) — and a curated, widely-benchmarked BiGG GEM
(iMM904). The essential metabolic machinery (glycolysis, amino-acid / nucleotide / lipid / cofactor biosynthesis,
etc.) is shared with fungal pathogens, so S. cerevisiae is a legitimate model-eukaryote generalization test. This is
a deliberate, disclosed scope choice, NOT a claim about C. albicans specifically.

## Data (open, CPU-only, already downloaded)
- **GEM:** iMM904 (BiGG, `http://bigg.ucsd.edu/static/models/iMM904.xml`). Gene IDs = systematic ORF names
  (e.g. `YHR104W`); gene `.name` = standard symbol (e.g. `GRE3`). 905 genes, 1577 reactions.
- **Experimental essentiality:** DEG accession **DEG2001** = *S. cerevisiae* essential ORFs from Giaever 2002
  (`deg_annotation_e.csv`, 1110 essential genes, standard gene names).
- **ID bridge:** `SGD_features.tab` (SGD, R64) — maps standard name + aliases -> systematic ORF name.

## ID-mapping strategy (the #1 declared failure mode: namespace mismatch)
Everything is normalized to **systematic ORF-name space** (stable), because the model gene IDs are already
systematic:
1. From `SGD_features.tab` build `name2sys`: for every ORF, map its standard name (col5) and each alias (col6, `|`-
   split) and its own systematic name (col4), all upper-cased, -> systematic name (col4).
2. `essential_sys` = { name2sys[g] for g in DEG2001 standard names that resolve }. Report how many of 1110 resolve.
3. A model gene is EXPERIMENTALLY-ESSENTIAL iff its systematic ID (upper-cased) is in `essential_sys`
   (backstop: its standard `.name` maps to a systematic name in `essential_sys`). Report n mapped.

## Method (mirrors the bacterial pipeline exactly)
COBRApy `single_gene_deletion` on iMM904 in its default (curated) medium; WT growth = `slim_optimize()`;
a gene is **FBA-essential** iff KO growth `< 0.01 * WT`. Universe = the model's metabolic genes (metabolic
subproteome), identical to `experiments/CROSSVAL_curated/run.py`.

## Pre-registered hypothesis & decision gate (FIXED before scoring)
**H1:** the FBA-essential set is enriched for the experimental (Giaever) essential set among iMM904's metabolic
genes. 2x2 Fisher (one-sided 'greater') over model genes: FBA-essential vs experimental-essential.
**GATE: odds ratio > 3 AND Fisher p < 0.01.** (Identical to every bacterial organism.) Also report precision,
recall, the full contingency table (both / FBA-only / exp-only / neither), and growth-ratio AUROC.
- **PASS** => the FBA-essentiality mechanism signal generalizes from bacteria to a eukaryote (essentiality-
  enrichment, in-silico vs published lab data).
- **FAIL** => reported first-class as an honest negative (signal does not transfer to eukaryotic metabolism, or the
  GEM/medium assumptions break the enrichment). Recorded, not hidden.

## Scope (true regardless of outcome)
Essentiality-ENRICHMENT only; in-silico FBA vs a published experimental deletion set (not a wet-lab experiment we
ran); curated model is still a model (medium/gap-fill assumptions); recall is bounded by the metabolic subproteome;
model eukaryote (S. cerevisiae), NOT a direct C. albicans pathogen claim. Deterministic; reproduced x2 (SHA-256 over
sorted-key JSON of the metrics payload, excluding verdict/provenance).
