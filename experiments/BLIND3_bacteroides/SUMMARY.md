# BLIND3 — Bacteroides thetaiotaomicron VPI-5482 — prospective-blind essentiality test (Stage 1 + Stage 2)

**VERDICT: PASS.** n=3 prospective-blind confirmation, extended to a NEW PHYLUM (Bacteroidetes).

## Design (identical protocol to BLIND1/BLIND2)
- **Stage 1 (LOCK)** de-novo CarveMe GEM from the UniProt reference proteome ALONE -> COBRApy single-gene-deletion FBA
  (essential if KO growth < 1% WT); predictions frozen + hashed, then git-committed BEFORE any reveal (commit 24e409a).
- **Stage 2 (REVEAL)** map the pre-registered experimental essential set onto the LOCKED predictions via mmseqs
  sequence-homology bridge (pident>=90); 2x2 Fisher (one-sided greater) over the GEM subproteome; gate OR>3 AND p<0.01.

## Organism
B. thetaiotaomicron VPI-5482 (NC_004663, taxon 226186). Never used before (0 grep hits). First **Bacteroidetes** in the
suite (all prior essentiality organisms: Proteobacteria / Firmicutes / Actinobacteria) -> maximum clade diversity.

## Artifacts / provenance
| item | value |
|---|---|
| Proteome | UniProt UP000001414, 4782 proteins; btheta.fasta sha256 7fea34eddeb654c1d41d14eb7c6de3d457665c078ef32cef7986062976384eea |
| GEM | de-novo CarveMe btheta.xml sha256 3905ee50826668f3f89d8e6db0083b13392b0f3ce27e1df7bf5f3d148c6ea2b7; 830 genes, 2267 rxns, 1484 mets, WT growth 71.928 |
| LOCK (Stage 1) | 25 FBA-essential; payload sha256 **e743e599ad7e08701f3fd95396cb302e9e4df1f6d44b1e247eb994b415176442** (committed, verified intact at reveal) |
| Experimental set | DEG **DEG1023** (Goodman 2009 INSeq, 325 essential); seqs DEG10.aa.gz sha256 5b906f5fae0f002406b5aa490fb620c9b396ae20166b80bf77cb6e4a7f58d34d |
| REVEAL sha (Stage 2) | **1437a830691bdb6dabe52e66bb204c15aaa24f2d3631c64bbf7c18bb1eb9e98d** (reproduced x2 byte-identical) |

## Result
- Contingency (over 830 locked genes): **12 both / 13 FBA-only / 83 exp-only / 722 neither**
- **odds ratio 8.03, Fisher p = 3.83e-06, precision 0.48, recall 0.126** -> **PASS** (gate OR>3 AND p<0.01)
- 325 DEG1023 essential proteins mapped by mmseqs to 327 experimental-essential genes in our accession space.

## Suite comparison (identical protocol + gate)
| exp | organism | clade | GEM | OR | p | prec | rec | verdict |
|---|---|---|---|---|---|---|---|---|
| BLIND1 | N. gonorrhoeae MS11 | beta/gamma-proteo | de-novo | 6.13 | 4.2e-06 | 0.78 | 0.10 | PASS |
| BLIND2 | C. jejuni NCTC 11168 | epsilon-proteo | de-novo | 3.92 | 6.5e-04 | 0.27 | 0.22 | PASS |
| **BLIND3** | **B. thetaiotaomicron VPI-5482** | **Bacteroidetes** | **de-novo** | **8.03** | **3.8e-06** | **0.48** | **0.13** | **PASS** |
| BLIND4 | (see BLIND4) | — | de-novo | 2.96 | — | — | — | FAIL |

BLIND3 is the strongest OR in the suite so far. n=3 PASS across three phyla; the one FAIL (BLIND4) is reported first-class.

## Scope / honesty
Essentiality-enrichment only; de-novo (uncurated) GEM; in-silico FBA vs a published INSeq screen (not a wet-lab experiment
we ran); prospective-BLIND in the git-committed-lock sense; species/strain-level; NOT drug-target / selectivity / clinical.
Precision/recall bounded by the metabolic subproteome. Predictions were locked+committed before the experimental set was
fetched; nothing was tuned to the outcome; the lock sha was re-verified intact at reveal. This module did NOT git commit.
