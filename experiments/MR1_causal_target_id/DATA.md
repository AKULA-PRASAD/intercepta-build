# MR1 — data panel (LOCKED 2026-08-10, before any H1/H2 statistic)

## Instruments
- **eQTLGen 2019 cis-eQTL** (FDR<0.05, blood, N≈31,684): `$INTERCEPTA_DATA/mr1/eqtlgen_cis.txt.gz`
  (10,507,664 rows). Instrument table = strongest cis SNP per gene (max|Z|):
  **16,987 genes / 16,290 unique SNPs** (`instruments.parquet`, `build_instruments.py`).

## Outcome GWAS — 6 GENETICS1-panel diseases with OPEN GWAS Catalog harmonized full sumstats
Chosen for disease-class diversity (so grouped-CV folds = whole diseases test cross-disease transfer)
and confirmed harmonized `.h.tsv.gz` availability on the open EBI FTP (no token). Panel locked before scoring.

| disease (GENETICS1 id) | class | accession | harmonized file |
|---|---|---|---|
| coronary artery disorder (MONDO_0005010) | cardiovascular | GCST90132314 | GCST90132314.h.tsv.gz |
| type 2 diabetes (MONDO_0005148) | metabolic | GCST006867 | 30054458-GCST006867-EFO_0001360.h.tsv.gz |
| inflammatory bowel disease (MONDO_0005265) | GI/immune | GCST004131 | 28067908-GCST004131-EFO_0003767.h.tsv.gz |
| Parkinson disease (MONDO_0005180) | neurodegenerative | GCST009325 | GCST009325.h.tsv.gz |
| rheumatoid arthritis (MONDO_0008383) | autoimmune | GCST90132223 | GCST90132223.h.tsv.gz |

### CORRECTION 2026-08-10 (pre-scoring, data-availability only — NOT outcome-driven)
Panel reduced from 6 → **5 diseases**: **asthma (GCST90014325) dropped**. Reason: its harmonized file
is 2.2 GB with **no tabix index**, and the EBI summary-statistics endpoint is throttled per-connection
(~130 KB/s), making a 2.2 GB non-indexed download infeasible in a reasonable window. Diversity is retained
(cardiovascular, metabolic, GI-immune, neurodegenerative, autoimmune). This decision was made **before any
MR estimate or H1/H2 statistic was computed** (no outcome data seen), so it cannot bias the result; it only
reduces power (grouped-CV folds 6→5). Matching is by **rsID** (genome-build-independent), so the eQTLGen
GRCh37 vs GWAS-Catalog GRCh38 coordinate difference does not require liftover.

FTP base: `https://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/<range>/<accession>/harmonised/<file>`.
All raw sumstats live only in `$INTERCEPTA_DATA/mr1/gwas/` — never committed.

## Labels (from GENETICS1 dataset, already cached)
`OT_genetic_association` (baseline predictor) and `clinical` (ChEMBL clinical-precedence, the ground truth)
per (gene, disease), restricted to these 6 diseases. Genes without a cis instrument → MR_score=0 (untested).
