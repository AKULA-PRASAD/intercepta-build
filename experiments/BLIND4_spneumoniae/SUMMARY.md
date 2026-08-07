# BLIND4 — *Streptococcus pneumoniae* TIGR4 — prospective-blind essentiality test (Stage 1 + Stage 2)

**Verdict: FAIL (honest negative), reported first-class.** Third organism in the prospective-blind suite; first FAIL.

## Blindness trail
- **Stage 1 (LOCK)** committed to git (b89fd42, pushed) BEFORE any experimental essential-gene set was fetched.
  Locked essential-accession payload sha256 **f86a02a4e7107ec2c12e3a231942449a01dc24f1be78fbbae42b6db1b8b5651d**.
- **Stage 2 (REVEAL)** verified the lock intact (recomputed payload == committed sha) BEFORE scoring; predictions unchanged.

## Organism & model
- *S. pneumoniae* serotype 4 TIGR4 (taxid 170187, NC_003028). New clade for the suite: Gram-positive Firmicute
  (BLIND1/BLIND2 are proteobacteria). Major WHO/AMR pathogen. Genuinely never used in any prior INTERCEPTA experiment.
- De-novo CarveMe GEM from UniProt UP000000585 (2109 proteins; proteome sha 4d321cf1…; GEM sha 77ffc13a…):
  634 genes, 1511 reactions, WT growth 54.994, **14 FBA-essential rows** (13 real genes + `spontaneous` pseudo-gene).

## Experimental truth used (with honest caveat)
- Pre-registered PRIMARY = van Opijnen 2009 Tn-seq TIGR4 (gold standard) — **not cleanly fetchable CPU-only** (Nature auth
  wall; OGEE unreachable; web-search budget exhausted).
- Per the pre-registered decision rule, fell back to strain-matched **DEG1007** (TIGR4, NC_003028; DEG10.aa.gz sha 5b906f5f…),
  244 essential proteins. CAVEAT: DEG1007 is insertion-duplication/allelic-replacement (Thanassi 2002 / Song 2005), NOT
  Tn-seq — weaker/older/smaller than the intended gold standard.

## Result (mmseqs pident>=90 homology bridge over 634 GEM genes)
- DEG1007's 244 essential proteins mapped (same strain) to 239 of our accession space.
- Contingency: **5 both / 9 FBA-only / 98 exp-only / 522 neither**.
- **OR 2.96, Fisher p 0.0607, precision 0.357, recall 0.049** → **does NOT clear the gate (OR>3 AND p<0.01)** → **FAIL**.
- SP_ locus-tag cross-check: partial coverage only (81/244 DEG1007 rows carry SP_ tags); no additional signal.

## Interpretation & suite comparison
- Direction is positive (~3x enrichment) but sub-threshold on both OR and p.
- BLIND1 *N. gonorrhoeae* OR 6.13 (PASS) | BLIND2 *C. jejuni* OR 3.92 (PASS) | **BLIND4 *S. pneumoniae* OR 2.96 (FAIL)**.
- Likely drivers: very sparse de-novo GEM (13 real FBA-essential of 634) for a fastidious/fermentative Gram-positive
  Firmicute; and a weaker fallback truth (DEG1007 allelic-replacement vs the intended van Opijnen Tn-seq). Suite = 2 PASS / 1
  FAIL. The FAIL is genuine and first-class — reported, not tuned. A future re-score against van Opijnen Tn-seq (if fetched)
  could be run against the SAME locked predictions without changing the lock.
- **Reproduced x2 byte-identical** — Stage-2 payload sha256 f5b818ee0269bc511884edacd9f6175a6c4089b60b2b73ee8efcedb16224cefd.

## Scope
Essentiality-enrichment only; sparse de-novo GEM; in-silico FBA vs a published experimental set (fallback, not the intended
Tn-seq); species/strain-level; NOT drug-target/selectivity/clinical; NOT a wet-lab experiment. Awaiting orchestrator commit
of the reveal (I do not git commit).
