# GENERALIZE5 — pre-registered test: does FBA gene-essentiality generalize to a PARASITE (*Plasmodium falciparum*, malaria)?

**Registered (Stage 1) BEFORE computing the 2x2 contingency table, odds ratio, Fisher p, or precision/recall.**
Data sources (GEM + experimental essentiality) were fetched and their FORMAT inspected (gene-ID namespaces, phenotype
categories, mapping overlap counts) to design the mapping — this is method design, not outcome. The ENRICHMENT ANSWER
(OR / p / contingency / precision / recall) has not been looked at when this file is written.

## Hypothesis
FBA single-gene-deletion essentiality computed on a CURATED *P. falciparum* genome-scale metabolic model is enriched
for the parasite's EXPERIMENTALLY essential genes (genome-wide piggyBac saturation-mutagenesis screen, Zhang et al.
2018 *Science*), over the model's metabolic-gene subproteome. Mirrors the bacterial CROSSVAL / BLIND1 method exactly.

## Materials (fixed now)
- **GEM:** `iPfal19` — curated *P. falciparum* 3D7 genome-scale model, from the PARADIGM database
  (Carey/Untaroiu/Papin; GitHub `maureencarey/paradigm`, bioRxiv 10.1101/772467; file `models/iPfal19.xml`).
  475 genes, 1233 reactions, 983 metabolites. Gene IDs are PlasmoDB `PF3D7_` locus tags. Objective `biomass`;
  default-medium WT growth = 31.40 (grows). SHA-256 of the model file recorded in results.
- **Experimental essentiality:** Zhang et al. 2018 *Science* (piggyBac saturation mutagenesis) per-gene
  Mutagenesis Index Score (MIS), Mutagenesis Fitness Score (MFS), and mutability phenotype, as ingested by PlasmoDB
  and redistributed in the Pf Target Browser `Pf3D7_gene_annotations.csv` (Figshare dataset 27190545). Columns
  `Zhang MIS`, `Zhang MFS`, `Zhang Phenotype`, keyed by `Gene ID` (PF3D7_). 5318 genes with a phenotype call.
- **Gene-ID mapping:** iPfal19 gene IDs are already PF3D7_ (471/475). Exact case-insensitive PF3D7_ match to Zhang.
  Old-style IDs (e.g. `PFF0530w`) bridged to canonical PF3D7_ via `Pfalciparum3D7_GeneAliases.csv` (PlasmoDB alias
  history). Mitochondrial-genome genes (`mal_mito_*`) are outside Zhang's NUCLEAR screen and cannot map — reported as
  legitimately unmappable, NOT forced.

## Essentiality definitions (fixed now)
- **FBA-essential (predicted):** COBRApy `single_gene_deletion`; a gene is essential if KO growth < 1% of WT
  (`< 0.01 * WT`), identical to the bacterial pipeline.
- **Experimentally essential (ground truth), PRIMARY:** Zhang `Phenotype == "Non - Mutable in CDS"` (the coding
  sequence could not tolerate transposon insertion = essential). `"Mutable in CDS"` = dispensable. This is PlasmoDB's
  authoritative categorical call — a threshold I do NOT choose. Genes with no Zhang call are excluded from the 2x2.
- **SENSITIVITY (secondary, reported, not the gate):** MIS threshold essential = `MIS <= 0.2` (low-MIS = intolerant of
  insertion). Reported to show the verdict is not an artifact of the categorical definition.

## Pre-registered decision gate (fixed now)
2x2 Fisher exact (one-sided, `alternative="greater"`) over the mapped metabolic genes:
FBA-essential vs experimentally-essential. **PASS iff odds ratio > 3 AND Fisher p < 0.01.** Same gate as every prior
organism. Also report precision, recall, AUROC (growth-ratio vs experimental label), full contingency, n mapped.

- **PASS** ⇒ FBA-essentiality generalizes from bacteria to a parasitic eukaryote (malaria) — enrichment evidence.
- **FAIL** ⇒ reported first-class as an honest negative (e.g., host-dependent parasite metabolism makes the
  default-medium GEM a poor essentiality predictor). Recorded, never re-run to a nicer number.
- **INCONCLUSIVE** ⇒ if gene-ID mapping collapses (like BLIND1's first reveal), reported as an honest namespace
  boundary, NOT a fabricated number.

## Scope (fixed now)
Essentiality-enrichment only; in-silico FBA vs a published experimental screen (not wet-lab we ran); a curated model
is still a model (medium/gap-fill assumptions); *P. falciparum* is host-dependent (intra-erythrocytic) — the
default-medium GEM may be sparse/over-permissive, an honest deployment risk reported either way. Not
drug-target/selectivity/clinical. Deterministic; reproduced x2 byte-identical (SHA-256 over sorted-key metrics payload
excluding verdict/provenance).
