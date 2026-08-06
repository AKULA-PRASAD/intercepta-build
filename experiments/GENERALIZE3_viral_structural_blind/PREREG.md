# GENERALIZE3 — pre-registered BLIND structural generalization test (the unbiased version GENERALIZE2 left gated)

**Registered (Stage 1) BEFORE any scoring against the known-drug-target answer.** Reference list and numeric
gate below are FROZEN before Foldseek is run.

## Background (from committed GENERALIZE1 & GENERALIZE2)
- **GENERALIZE1 (FAIL, honest negative, sha d58f9e7e):** at e<=1e-5, 0/30 SARS-CoV-2 mature proteins have ANY
  non-coronaviral drugged-*sequence* homolog. Cross-family viral sequence identity is below detection.
- **GENERALIZE2 (PASS, confirmatory, sha f8f7d1be):** Foldseek TM shows Mpro->rhinovirus-3C and RdRp->HCV-NS5B,
  but only as a HAND-PICKED 2-target capability test with hypothesis-chosen controls, because AlphaFold DB
  excludes viral proteins. NOT a blind discovery ranking.

## What GENERALIZE3 does differently (the blind version)
1. **Query set:** acquire an EXPERIMENTAL RCSB PDB structure for as many of the 30 SARS-CoV-2 mature proteins
   as exist. Clean each to the SINGLE chain that is the protein of interest (see cleaning rule) — strip all
   other chains, ligands, ions, waters, nucleic acids. This is critical: in GENERALIZE2, leaving cofactor
   chains in produced a false GPCR match.
2. **Reference set:** a corona-free, broad, multi-class drugged/enzyme panel (below), chosen to span MANY
   drug-target classes so each viral protein has a plausible correct-class analog to find. This is NOT rigged
   to Mpro/RdRp: proteases, polymerases, kinases, GPCRs, reductases, methyltransferases, nuclear receptors,
   ion channel, nucleases, helicases, lyase, esterase, phosphatase are all represented. Crucially, viral
   enzymes OTHER than Mpro/RdRp are given their correct-class options too (methyltransferases for nsp14/nsp16,
   nuclease for nsp15, helicase for nsp13, papain-clan + 3C-clan cysteine proteases for nsp3/nsp5), so a
   correct hit is a genuine multi-class discrimination, not a 2-way default.
3. Foldseek-rank each viral protein by best drugged-analog TM-score (TMalign mode, query-normalized qtmscore,
   same as GENERALIZE2).

## Cleaning rules (fixed)
- **Query:** for each viral protein, among all chains of its source PDB, select the chain whose CA sequence has
  the highest 5-mer overlap fraction with that protein's known SARS-CoV-2 sequence (from
  `generalize1/mature_proteins.fasta`). Write ONLY that chain (standard AAs + MSE-as-MET); drop everything
  else. This deterministically picks the protein-of-interest chain and avoids the cofactor trap.
- **Reference:** keep the single LONGEST protein chain (most CA residues; standard AAs + MSE); drop everything
  else. Reference crystal structures are dominated by their drug-target protein, so longest-chain = the target.

## FROZEN reference panel (31 corona-free structures, 12 classes) — PDB id : class
proteases: 4cha (chymotrypsin, serine), 1ppb (thrombin, serine), 1cqq (rhinovirus 3C, cysteine/picornaviral),
9pap (papain, cysteine/papain-clan), 1hxw (HIV protease, aspartic), 1tlp (thermolysin, metallo);
polymerases: 4wtg (HCV NS5B RdRp), 3hvt (HIV reverse transcriptase), 1kln (DNA pol I Klenow);
kinases: 1m17 (EGFR), 1hck (CDK2), 1atp (PKA), 2src (Src);
gpcrs: 2rh1 (beta2-adrenergic), 1f88 (rhodopsin), 3eml (A2A adenosine);
reductases: 1rx2 (DHFR), 1hw9 (HMG-CoA reductase);
methyltransferases: 1vid (COMT, SAM-dep), 2adm (DNA adenine MTase, SAM-dep);
nuclear_receptors: 1err (estrogen receptor LBD), 2prg (PPARgamma LBD), 1e3g (androgen receptor LBD);
ion_channel: 1bl8 (KcsA K+ channel);
nucleases: 7rsa (RNase A), 1rnb (barnase);
helicases: 1pjr (PcrA helicase), 3pjr (PcrA helicase-DNA);
lyase: 2cba (carbonic anhydrase II);
esterase: 1acj (acetylcholinesterase);
phosphatase: 2hnp (PTP1B).

## Ground truth (fixed now; used ONLY in Stage 2 scoring)
Clinically approved SARS-CoV-2 antiviral targets: **nsp5/Mpro** (protease) and **nsp12/RdRp** (polymerase).
Secondary diagnostics (NOT gated): nsp3/PLpro -> protease (papain clan); nsp13/helicase -> helicase.

## PRE-REGISTERED GATE (frozen before scoring)
Let n = number of the 30 proteins with a usable cleaned structure. For each structured viral protein, its
"best drugged-analog" = the reference with max qtmscore; that reference's class = predicted class.
- **G1:** nsp5/Mpro's best-analog class == `protease` AND its best qtmscore >= 0.40.
- **G2:** nsp12/RdRp's best-analog class == `polymerase` AND its best qtmscore >= 0.40.
- **G3 (ranking):** among the n structured proteins ranked by best qtmscore (descending), BOTH nsp5 and nsp12
  fall in the top ceil(n/2) (top half).
- **PASS** <=> G1 AND G2 AND G3.
- **PARTIAL** <=> (G1 or G2) but not PASS.
- **FAIL** <=> NOT G1 and NOT G2 (neither approved target recovers its correct drugged fold) — reported
  first-class as an honest negative, not re-run to a better number.

I pre-commit to reporting the FULL ranked table (all n structured proteins, best hit + class + TM), coverage
(n/30), and where nsp5 & nsp12 land.

## Disclosed confound (fixed)
Proteins with NO experimental PDB structure are EXCLUDED; this ranks only the structured subset. TM is
query-normalized, so very large multidomain queries (e.g. spike) can score low even with a real domain match.
n=1 virus. This establishes the PRINCIPLE of blind structural target prioritization on one emerging pathogen;
it is not wet-lab, not a deployed pipeline, and not a claim about all viruses.

## What PASS / FAIL would mean
PASS = structure blindly recovers the correct drugged fold+class for both approved viral targets from a broad
unbiased panel, exactly where sequence homology gave zero (GENERALIZE1) — the viral-generalization failure is
a sequence-tool limitation, not fundamental, now shown WITHOUT hand-picking the controls. FAIL = even an
unbiased structural screen does not point at the right intervention targets — honest boundary of the approach.
