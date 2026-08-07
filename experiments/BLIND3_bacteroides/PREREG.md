# BLIND3 — pre-registered PROSPECTIVE-blind essentiality test on *Bacteroides thetaiotaomicron* VPI-5482

**Registered (Stage 1) BEFORE the experimental essential-gene SET was fetched, parsed, or used to build any prediction.**
This is the THIRD, independent prospective-blind essentiality validation, run under the identical protocol as BLIND1
(*N. gonorrhoeae*, beta/gamma-proteobacterium) and BLIND2 (*C. jejuni*, epsilon-proteobacterium). BLIND3 adds a **new
PHYLUM — Bacteroidetes (Bacteroidota)** — for maximum clade diversity in the blind suite. Predictions are locked (hashed)
first; the experimental answer is scored only in Stage 2 (a separate later commit). The lock sha recorded below is the
pre-reveal blindness commitment (the orchestrator commits the lock file; this module cannot and does not git commit).

## Organism & rationale (Stage 0)
*Bacteroides thetaiotaomicron* VPI-5482 (= ATCC 29148 / DSM 2079 / NCTC 10582), genome NC_004663, taxon 226186.
- **Genuinely never used** in ANY prior INTERCEPTA experiment. Verified: `bacteroides` / `thetaiotaomicron` / `fragilis`
  appear in **0** files under `experiments/` (`grep -ri` → 0 hits). Distinct from every prior essentiality organism.
- **NEW PHYLUM — Bacteroidetes (Bacteroidota).** Every prior blind/dev essentiality organism is a Proteobacterium
  (gamma / beta / epsilon), a Firmicute, or an Actinobacterium. *B. thetaiotaomicron* is the first Bacteroidetes member,
  a phylogenetically deep addition (a distinct anaerobic gut-symbiont clade) — the reason it was the a-priori priority pick.
- **Clinical / biological priority.** A dominant human-gut-microbiome symbiont and opportunistic pathobiont (bacteremia,
  abscesses in dysbiosis / barrier breach); a keystone Bacteroidetes model organism. It also has **open, published
  genome-wide essentiality** (Goodman 2009 INSeq → DEG1023), which is the enabling requirement for a blind score.
- **Choice between the two candidate Bacteroidetes organisms:** *B. thetaiotaomicron* VPI-5482 (DEG1023, Goodman 2009
  INSeq, 325 essential genes) was chosen over *B. fragilis* 638R (DEG1034, Yaligara 2014 Tn-seq) because it is the
  task-preferred organism, the more widely used reference gut-symbiont model, and its strain matches an available UniProt
  reference proteome exactly (UP000001414, VPI-5482). Both are new-phylum and never-used; B. theta is the stronger pick.

## Deployment scenario (deliberate, honest hard path)
No curated BiGG genome-scale model exists for *B. thetaiotaomicron* → we use a **de-novo CarveMe reconstruction from the
UniProt reference proteome** (UP000001414, 4782 proteins, default universe / complete-medium carve, `--fbc2`, SCIP MILP
solver). This is the real "new pathogen, no curated model" deployment case — the same honest, weaker path used in
BLIND1/BLIND2 (not a curated best case). The GEM is built from the proteome ALONE; no essentiality information enters the
reconstruction or the FBA. (Note: the higher WT growth and larger network here vs BLIND1/2 reflect a well-annotated,
metabolically rich anaerobe — reported as-is, not tuned.)

## Locked prediction (Stage 1 output)
COBRApy single-gene-deletion FBA on the CarveMe GEM; a gene is **FBA-essential if its knockout growth < 1% of WT**
(identical rule to BLIND1/BLIND2/CROSSVAL). The full per-gene call (UniProt accession + symbol + fba 0/1 + KO growth
ratio) is written to `results/LOCKED_predictions.tsv`; the sorted essential-accession set is hashed to
`results/LOCKED_predictions.sha256` (payload = `"\n".join(sorted(acc for fba==1))`, BLIND1 convention). This computation is
a deterministic function of the metabolic network only and is provably independent of which genes are experimentally
essential. **Determinism verified:** `build.py` was run twice; the LOCKED_predictions.tsv is byte-identical and the
essential-set sha256 is identical across runs (signed-zero GLPK jitter in the growth-ratio column is collapsed to `0.0`
so the artifact is fully canonical; it never affected any 0/1 essentiality call or the hashed payload).

## Pre-registered experimental source (fixed now, fetched only in Stage 2)
**I WILL score against DEG accession `DEG1023`** — *Bacteroides thetaiotaomicron* VPI-5482 essential genes, **Goodman AL,
et al. (2009)** "Identifying Genetic Determinants Needed to Establish a Human Gut Symbiont in Its Habitat", *Cell Host &
Microbe* 6:279–289 (PMID 19748469), **INSeq** transposon-insertion sequencing, same strain VPI-5482, genome NC_004663.
DEG lists this entry with **325 essential genes** in rich (TYG) medium. Database of Essential Genes (DEG), Tianjin
University: `http://tubic.tju.edu.cn/deg/` (accession `DEG1023`; also mirrored at `http://origin.tubic.org/deg/`).
- **Alternative rejected (pre-reveal):** DEG1034 (*B. fragilis* 638R, Yaligara 2014 Tn-seq) — a different strain/species,
  which would introduce a strain gap against our VPI-5482 GEM. DEG1023 is the exact-strain match.
- **Blindness note (transparent):** to confirm the dataset EXISTS and to plan the Stage-2 adjudication I read ONLY the DEG
  organism-index row (organism name, reference, method, medium, genome accession, essential-gene COUNT, and the DEG
  identifier format). I did NOT fetch, open, or parse the essential-gene SET (which genes / sequences are essential), and
  the FBA lock is by construction answer-independent. Full essential-set retrieval and parsing happen only in Stage 2.

## Adjudication (fixed now)
Primary/robust: **sequence-homology bridge** — map DEG1023's essential PROTEIN sequences (from the DEG protein file
`DEG10.aa.gz` / DEG download, selected by the `DEG1023` accession) onto our CarveMe proteome by **mmseqs easy-search,
pident ≥ 90** (same-species ortholog cutoff, set once, not swept), defining the experimental-essential set in our UniProt
accession space, then score the SAME LOCKED predictions (sha-verified unchanged). This is the identical,
namespace-independent method that adjudicated BLIND1 and BLIND2 (robust to the locus-tag/GI namespace mismatches that made
naive symbol matching fail in BLIND1).

## Pre-registered hypothesis & decision rule (fixed now — IDENTICAL to BLIND1/BLIND2)
**H1:** the locked FBA-essential set is enriched for the experimental essential set (DEG1023), 2×2 Fisher
**odds ratio > 3 AND p < 0.01** over the GEM (metabolic-subproteome) genes.
- **PASS** ⇒ prospective-blind evidence that the FBA-essentiality mechanism signal predicts experimental essentiality on a
  third, genuinely novel, pre-registered organism from a NEW PHYLUM (Bacteroidetes) → the flagship becomes n = 3 across
  four phyla.
- **FAIL** ⇒ reported first-class as an honest negative (e.g., the signal does not transfer to an anaerobic gut
  Bacteroidetes symbiont, or a de-novo-GEM artifact) — recorded, not hidden or re-run to a better number.

## Scope (what a PASS does and does not show)
Essentiality-enrichment only; in-silico FBA vs a published INSeq screen (not a wet-lab experiment we ran);
prospective-BLIND in the lock/held-out sense; de-novo model; species/strain-level; NOT drug-target / selectivity /
clinical. Precision/recall are bounded by the metabolic subproteome.

## Sources & hashes (provenance)
- GEM proteome: UniProt reference proteome UP000001414 (B. theta VPI-5482, 4782 proteins),
  `https://rest.uniprot.org/uniprotkb/stream?query=proteome:UP000001414&format=fasta`
  → `$INTERCEPTA_DATA/blind3/btheta.fasta`  sha256 `7fea34eddeb654c1d41d14eb7c6de3d457665c078ef32cef7986062976384eea`
- GEM: CarveMe de-novo `$INTERCEPTA_DATA/blind3/btheta.xml` sha256
  `3905ee50826668f3f89d8e6db0083b13392b0f3ce27e1df7bf5f3d148c6ea2b7`
  (830 genes, 2267 reactions, 1484 metabolites, WT growth 71.928; `carve --fbc2 --solver scip`, default universe/medium).
- Essentiality: DEG `DEG1023` (Goodman 2009 INSeq), protein sequences from `$INTERCEPTA_DATA/expval_deg/DEG10.aa.gz`
  (local, pre-existing) / DEG download — **named now, fetched/parsed only in Stage 2.**

## LOCKED-predictions commitment (blindness audit trail)
- `results/LOCKED_predictions.sha256` (essential-accession payload sha256):
  **`e743e599ad7e08701f3fd95396cb302e9e4df1f6d44b1e247eb994b415176442`**
- GEM: 830 genes, WT growth 71.928, **25 FBA-essential** genes predicted (frozen).
- Stage-1 locked BEFORE Stage-2 reveal. Recorded here as the pre-reveal blindness commitment. This module did NOT git commit.

---
## REVEAL OUTCOME (Stage 2, to be filled after the lock is committed)
*(empty — Stage 2 not run. No score.py, no reveal, no experimental essential-gene set consulted in Stage 1.)*
