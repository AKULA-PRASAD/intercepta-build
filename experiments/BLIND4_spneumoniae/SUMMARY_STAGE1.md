# BLIND4 — STAGE 1 (LOCK) SUMMARY — *Streptococcus pneumoniae* TIGR4

**Stage 1 only. No reveal, no scoring, no `score.py`, no git commit. Experimental essential-gene set NOT fetched/parsed/opened.**

## What was done
1. **Organism confirmed novel & justified.** *S. pneumoniae* serotype 4 TIGR4 (taxid 170187, genome NC_003028). grep over
   `experiments/` -> 0 hits for S. pneumoniae/TIGR4/D39 (only `streptococcus` hit = *S. pyogenes*; all `pneumoniae` hits =
   *Klebsiella*). New clade for the suite: Gram-positive Firmicute (BLIND1/2 are proteobacteria). Major WHO/AMR pathogen with
   the gold-standard Tn-seq essentiality dataset (van Opijnen 2009, the paper that pioneered Tn-seq in this organism).
2. **Proteome fetched** from UniProt reference proteome UP000000585 (2109 proteins), strain-matched to TIGR4.
   sha256 4d321cf1a9e06017d937cf7f5572dea11513a6a82df369184409a8f965a2a16a.
3. **De-novo CarveMe GEM built** (default `bacteria` universe, default complete medium, no gapfill, diamond + MILP consensus).
   634 genes, 1511 reactions, 1064 metabolites, WT growth 54.994.
   GEM sha256 77ffc13a331c1af4512ef7adf460deb78c361adb89ee983d01915ed31eef7f08.
4. **COBRApy single-gene-deletion FBA** (essential if KO growth < 1% WT) -> **14 FBA-essential rows** (13 real genes +
   `spontaneous` pseudo-gene). Written to `results/LOCKED_predictions.tsv` and hashed to `results/LOCKED_predictions.sha256`.
5. **Determinism verified** — FBA recomputed 3x; essential-accession sha identical each time and the full TSV byte-identical.

## Locked commitment
- essential-accession payload sha256: **f86a02a4e7107ec2c12e3a231942449a01dc24f1be78fbbae42b6db1b8b5651d**
- full LOCKED_predictions.tsv sha256: 372a0955c1854f62b682041e3d61f4700fb01012512b7ed828b2574fe246bef5

## Pre-registered Stage-2 experimental source (named, NOT fetched)
- PRIMARY (gold standard): **van Opijnen et al. 2009, Nat Methods 6:767-772, DOI 10.1038/nmeth.1377** — Tn-seq, TIGR4,
  `SP_XXXX` locus tags (also curated in OGEE v3, https://v3.ogee.info/).
- FALLBACK (guaranteed executable, strain-matched): **DEG `DEG1007`** (TIGR4, NC_003028; proteins local in
  `$INTERCEPTA_DATA/expval_deg/DEG10.aa.gz`) — insertion-duplication/allelic-replacement, not Tn-seq.
- Gate (fixed): Fisher **OR > 3 AND p < 0.01**; adjudication = mmseqs pident>=90 sequence-homology bridge (BLIND1/2 method),
  with direct `SP_XXXX` locus-tag match as corroborating cross-check.

## Files
- `PREREG.md`, `build.py`, `results/LOCKED_predictions.tsv`, `results/LOCKED_predictions.sha256`, this summary.
- Data (not committed): `$INTERCEPTA_DATA/blind4/{spneumo.fasta, spneumo.xml, spneumo.tsv, carve.log}`.

**STAGE 1 LOCKED — awaiting orchestrator git-commit before any reveal.**
