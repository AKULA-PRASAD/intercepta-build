# BLIND3 — Stage 1 (LOCK) summary

**Status: STAGE 1 LOCKED. No reveal. No score.py. No experimental essential-gene set consulted. No git commit by this module.**

## What was done
De-novo genome-scale metabolic model built for a never-used **new-phylum (Bacteroidetes)** organism, FBA-essentiality
predictions computed and frozen, and the essential-set hashed as the pre-reveal blindness commitment — under the identical
protocol as BLIND1 (N. gonorrhoeae) and BLIND2 (C. jejuni).

## Organism
*Bacteroides thetaiotaomicron* VPI-5482 (NC_004663, taxon 226186). Never used in any prior INTERCEPTA experiment
(`grep -ri bacteroides|thetaiotaomicron|fragilis experiments/` -> 0 hits). First **Bacteroidetes** in the suite (all prior
essentiality organisms are Proteobacteria / Firmicutes / Actinobacteria) -> maximum clade diversity. Task-preferred pick;
chosen over B. fragilis 638R (DEG1034) because it is the exact-strain match to the UniProt reference proteome and the
canonical gut-symbiont model, with open genome-wide INSeq essentiality (Goodman 2009 -> DEG1023).

## Artifacts (all in experiments/BLIND3_bacteroides/ ; data in $INTERCEPTA_DATA/blind3/)
| item | value |
|---|---|
| Proteome | UniProt UP000001414, 4782 proteins; btheta.fasta sha256 7fea34eddeb654c1d41d14eb7c6de3d457665c078ef32cef7986062976384eea |
| GEM | de-novo CarveMe btheta.xml sha256 3905ee50826668f3f89d8e6db0083b13392b0f3ce27e1df7bf5f3d148c6ea2b7; 830 genes, 2267 reactions, 1484 metabolites, WT growth 71.928 |
| FBA-essential | **25** genes (KO growth < 1% WT) |
| LOCK sha256 | **e743e599ad7e08701f3fd95396cb302e9e4df1f6d44b1e247eb994b415176442** (sorted essential-accession payload) |
| Determinism | build.py run twice -> LOCKED_predictions.tsv byte-identical, LOCK sha256 identical |

## Stage-2 essentiality source (named, NOT fetched)
DEG **DEG1023** — Goodman AL et al. 2009 *Cell Host & Microbe* 6:279-289 (PMID 19748469), INSeq, B. theta VPI-5482,
325 essential genes; Database of Essential Genes http://tubic.tju.edu.cn/deg/ . Adjudication (pre-registered): mmseqs
sequence-homology bridge, pident >= 90, against the LOCKED predictions. Gate (identical to BLIND1/2): Fisher OR > 3 AND
p < 0.01.

## Sanity note (not a reveal)
The 25 FBA-essential genes are biologically sensible core-metabolism genes (peptidoglycan: murB/murF/murG/mraY/ddl;
CoA biosynthesis: coaBC/coaD/coaE/coaX; menaquinone: menB/menD/menG; MEP/isoprenoid: dxr/ispE/ispF; gmk/nadK/pdxH) —
a plausibility check on the model, produced with zero knowledge of the experimental set.

STAGE 1 LOCKED, sha=e743e599ad7e08701f3fd95396cb302e9e4df1f6d44b1e247eb994b415176442, ready for orchestrator to commit before reveal.
