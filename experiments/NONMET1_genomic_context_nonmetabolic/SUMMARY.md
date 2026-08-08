# NONMET1 — SUMMARY: Does CONSERVED GENOMIC CONTEXT crack the non-metabolic essential half?

**Verdict: FAIL — a rigorous, reproduced FIRST-CLASS NEGATIVE.** (A negative that closes a door is a success here.)
Reproduced x3 byte-identical. Payload SHA-256 (sorted-key JSON, excl. verdict/provenance):
`30c2afc11ef68d5c0a60b5954fcc821554e76d11d67949212ec9cb2492690edd`

## Gap and hypothesis (pre-registered in PREREG.md BEFORE any outcome)
FBA-essentiality (MET1-3, VALIDATED) is metabolic-scoped and blind to ~half of drug targets (proteases,
polymerases, ribosomal/structural/translational essentials); raw sequence-conservation breadth is the established
baseline that partly recovers those non-metabolic essentials. MET4 tried PPI-network centrality for this half and it
collapsed under **study bias**. NONMET1 hypothesis (novel, study-bias-resistant): **essentiality of non-metabolic
genes is encoded in CONSERVED GENOMIC CONTEXT** -- genes in synteny-conserved neighborhoods (same neighbors
co-located across many genomes) are enriched for essentiality and **add beyond** the gene's own conservation.
Genomic coordinates are not subject to research-attention bias, so unlike MET4 this signal is study-bias-free by
construction.

## Method (all locked before scoring)
- Fixed 12-genome bacterial panel (RefSeq main chromosomes; accessions + SHA-256 in
  $INTERCEPTA_DATA/nonmet1/genome_manifest.tsv). Two focal organisms scored vs the other 11.
- Orthology = mmseqs reciprocal-best-hit (--threads 1, min-seq-id 0.30, cov 0.5, e<=1e-5); deterministic, cached.
- Neighborhood k=4 (2 up + 2 down by genomic rank); synteny window W=5 gene-ranks.
- own_conservation = fraction of panel genomes with an ortholog (BASELINE); context_conservation = fraction where
  the ortholog KEEPS >=1 same-neighbor ortholog within W (synteny breadth); conditional_synteny = context/own.
- Non-metabolic subproteome = protein-coding genes NOT in the organism's MET2 GEM gene set.
- Truth: E. coli PEC (Class 1 essential, whole-genome single-gene-KO); M. tuberculosis DeJesus 2017 Tn-seq (ES).
- Decisive test: 5-fold CV (StratifiedKFold shuffle=False, no RNG) logistic regression delta-AUROC of adding
  context BEYOND own-conservation. Gate PASS = delta-AUROC >= +0.03 AND enrichment OR>2 (Fisher p<0.01); else FAIL.

## Results
### E. coli (PRIMARY) -- non-metabolic subproteome, n=2547 genes, 179 experimentally essential (7.0%)
| model | AUROC |
|---|---|
| M1: own-conservation only (null baseline) | 0.908 |
| M2: own + context_conservation | 0.924 |
| M2b: own + conditional_synteny | 0.929 |
- delta-AUROC (context beyond own) = +0.016 -- BELOW the +0.03 gate. Conditional-synteny +0.021, also below gate.
- Enrichment median-split OR = 147 (Fisher p ~ 0) -- passes the enrichment sub-gate, BUT context is strongly
  COLLINEAR with own-conservation (Pearson r=0.84, Spearman 0.88): the enrichment is not independent of raw
  conservation. Decisive add-on gate is delta-AUROC, which FAILS.
- Standardized M2 coefficients: own 0.93, context 0.78 (shared variance).
- Study-bias control (the MET4 lesson): context correlates only r=0.26 with the PEC PMID study proxy and still adds
  delta-AUROC +0.012 beyond own+study. So -- unlike MET4's PPI -- genomic context is NOT a study-bias artifact; it
  is simply too collinear with raw conservation to clear the independent-signal bar.

### M. tuberculosis (GENERALITY) -- n=2916, 241 ES (8.3%)
- own-only AUROC 0.699; delta-AUROC (context) = +0.0007 ~ zero; conditional +0.001. Context adds nothing.
- Median context = 0 (Mtb phylogenetically distant from panel -> sparse synteny), so median-split enrichment is
  degenerate (OR undefined). Clean negative; generality organism agrees.

## Honest one-line LEDGER verdict
NONMET1 (reproduced x3, byte-identical SHA 30c2afc1): NEGATIVE -- conserved genomic-context / synteny is
study-bias-FREE (unlike MET4's PPI) but is largely COLLINEAR with raw sequence-conservation breadth (r=0.84) and
adds only delta-AUROC +0.016 (E. coli) / +0.001 (Mtb) beyond the conservation null -- below the pre-registered
+0.03 bar. The "genomic context cracks the non-metabolic half" door is CLOSED: synteny re-encodes conservation
rather than providing an independent mechanistic signal. Raw conservation breadth (AUROC 0.91 on the E. coli
non-metabolic subproteome) remains the strong baseline and is not beaten. FBA remains the only validated
confound-honest mechanistic essentiality signal, and it stays metabolic-scoped.

Scope: in-silico, enrichment-only, non-metabolic subproteome, 12-genome bacterial panel, two focal organisms.
Data/caches in $INTERCEPTA_DATA/nonmet1/ (never committed). Not git-committed.
