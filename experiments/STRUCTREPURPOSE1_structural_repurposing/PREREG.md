# STRUCTREPURPOSE1 — PRE-REGISTRATION (frozen before scoring)

## Question
INTERVENE1 (sequence homology, mmseqs, e<=1e-5, pident>=35) maps a pathogen's validated-essential
targets to EXISTING drugs via ChEMBL drug-target proteins. It VALIDATED (E. coli canonical
antibacterial targets: 9/9 correct drug-class MoA recovered) but was NARROW: for novel
*N. gonorrhoeae*, only **1/32** FBA-validated-essential targets had a repurposing candidate.

Does STRUCTURAL homology (Foldseek TMalign) EXPAND the addressable target fraction beyond
sequence's 1/32 **for real** — i.e. via genuine drugged-fold recovery, NOT via structural
promiscuity (the fact that Foldseek finds SOME neighbor for almost any protein)?

## The specific false claim we guard against
"Structure expands repurposing coverage" when the extra hits are just structural promiscuity.
A bogus coverage gain is worse than an honest small one. The NULL comparison below is the
decisive, mandatory guard.

## Data / methods (frozen)
- Knowledge base (drug-target STRUCTURE reference): AlphaFold DB structures (AF-{acc}-F1-model_v6.pdb,
  current latest version; directive said v4 but AF-DB has re-versioned to v6 — verified via AF API)
  for the 2148 ChEMBL drug-target accessions in `$INTERCEPTA_DATA/intervene/drug_targets.fasta`.
  Report n fetched vs 404. Foldseek DB built from the fetched set.
- Query set A (VALIDATION, E. coli canonical antibacterial targets — same class INTERVENE1 used):
  UniProt AF structures for folA, folP, murA, gyrA, gyrB, parC, parE, rpoB, alr, ddlB, dxr.
  Expected MoA keyword per gene taken verbatim from INTERVENE1's CANON dict.
- Query set B (COVERAGE, novel N. gonorrhoeae): the 32 FBA-essential (fba_essential==1) accessions in
  `experiments/BLIND1_ngonorrhoeae/results/LOCKED_predictions.tsv`. These accessions (proteome
  UP001163151) are too recent to be in AlphaFold DB (all 404). Each is therefore mapped by mmseqs
  (pident>=90 AND qcov>=0.8; achieved 98.7-100% identity — same protein, different strain accession) to
  its ortholog in the AF-covered N. gonorrhoeae FA 1090 reference proteome (UP000000535), and that
  ortholog's AF structure is used. Targets without a confident AF-covered ortholog are counted as
  "no structure" (conservative; cannot be a coverage hit).
- Foldseek (directive command): `easy-search Q R out tmp --alignment-type 1 -e 10 -s 9.5
  --format-output "query,target,qtmscore,ttmscore,alntmscore,fident,evalue,alnlen"`.
  TM metric = **qtmscore** (query-length-normalized), best (max) over all targets per query
  (consistent with GENERALIZE2/3). Deterministic.

## NULL / promiscuity reference (frozen, decisive)
Size-matched RANDOM NON-drug-target reference, **organism-composition-matched** to the drug-target
set: for each taxid t present in the drug-target reference, sample the SAME number of successfully
fetched random UniProt proteins of taxid t that are NOT drug targets and NOT query proteins
(seeded RNG=1234; chosen accession list cached for reproducibility). This controls for
"bacterial/human folds are generically matchable in any large structure set."

## TM threshold (frozen)
Primary **T = 0.50** (Xu & Zhang: TM<0.17 = random, TM>0.5 = same fold). A structural repurposing
hit requires best qtmscore >= 0.50 to a drug-target structure. Sensitivity also reported at 0.40 and 0.60.
For every counted coverage hit we additionally report the drug target's MoA/organism and an automated
enzyme-family plausibility flag (informative-token overlap between query and drug-target descriptions).

## PRE-REGISTERED GATES
- **G1 (validation)**: among the canonical E. coli antibacterial targets that get any structural
  drug-target hit at TM>=0.50, the best structural homolog independently recovers the correct
  drug-class MoA at rate **>= 0.80** (comparable to INTERVENE1's 9/9). [analogous to the sequence 9/9]
- **G2 (expansion, survives null)**: BOTH must hold —
  - G2a: n(N. gonorrhoeae essential with a structural drug-target hit at TM>=0.50) **> 1**
    (strictly beats INTERVENE1's sequence-only 1/32);
  - G2b (NULL GUARD): drug-target coverage clearly exceeds the random-reference coverage at the
    SAME threshold — require **n_dt >= 2 x n_rand AND (n_dt - n_rand) >= 3**. If the random-structure
    hit rate is comparable to the drug-target hit rate, the coverage is PROMISCUITY -> NEGATIVE.

## VERDICT rule
- **PASS** = G1 AND G2 (G2a AND G2b).
- **PARTIAL** = G1 only (structure validates but expansion fails or is promiscuity).
- **NEGATIVE** = structure does not validate (G1 fails), OR the coverage gain does not survive the
  null guard (G2a holds but G2b fails = promiscuity).

## Reproducibility
SHA-256 over sorted-key JSON of the metrics payload EXCLUDING verdict/provenance; run twice;
must match. CPU-only, open data. Structures + sampled random accession list cached on disk so
both runs score identical inputs; Foldseek TMalign is deterministic.
