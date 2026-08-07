# BLIND6 — pre-registered PROSPECTIVE-blind essentiality test on the ARCHAEON *Methanococcus maripaludis* S2

**Registered (Stage 1) BEFORE the experimental essential-gene SET was fetched, parsed, or used to build any prediction.**
BLIND6 extends the prospective-blind essentiality suite to **ARCHAEA — the THIRD and final domain of life**, so the suite
can claim prospective-blind validation across ALL THREE DOMAINS (BLIND1–4 bacteria, multiple phyla; BLIND5 a eukaryote;
BLIND6 an archaeon). Predictions are locked (hashed) first; the experimental answer is fetched and scored only in Stage 2
(a separate later commit). The lock sha recorded below is the pre-reveal blindness commitment. This module did NOT git
commit (the orchestrator commits the lock file before any reveal).

## Honest framing up front (vision-relevance)
Archaea cause **essentially no human infectious disease** (no validated archaeal human pathogen). So BLIND6's value is
**generality/breadth — third-domain coverage of the method — NOT direct clinical priority.** Stated plainly: this is a
"does the FBA-essentiality signal reach the third domain of life?" test, not a therapeutic-target claim. *M. maripaludis*
is a hydrogenotrophic methanogen (an environmental/biotech organism), not a pathogen.

## Organism & rationale (Stage 0)
*Methanococcus maripaludis* strain **S2** (DSM 14266 / JCM 13030 / NBRC 101832 / LL), NCBI taxon **267377**, a member of
the **Euryarchaeota** (domain Archaea).
- **Genuinely never used** in ANY prior INTERCEPTA experiment. Verified: `maripaludis` / `methanococcus` / `haloferax` /
  `sulfolobus` / `saccharolobus` / `methanosarcina` / `archae*` appear in **0** files under `experiments/`
  (`grep -rli` → 0 hits). It is also the first organism from the domain Archaea in the entire program.
- **Enabling requirement met — open, published, GENOME-WIDE essentiality:** Sarmiento, Mrázek & Whitman (2013) PNAS
  whole-genome transposon-mutagenesis screen (see Stage-2 source below). This is the strongest open genome-wide archaeal
  essentiality resource among the candidates.
- **A CURATED archaeal GEM exists for the exact strain** (Richards et al. 2016, iMR539; BioModels curated branch), which
  lets BLIND6 avoid the known failure mode of running CarveMe (whose default reconstruction universe is **bacterial**) on
  an archaeon — a mismatch that would risk a sparse/low-quality de-novo carve. Choosing the curated model is the honest
  *best-supported* path for a divergent domain; the domain-mismatch caveat that BLIND1/3's de-novo carves carry therefore
  does **not** apply here (this is a strength, and it is why the curated model was preferred).

## Deployment scenario (deliberate — curated best case, not the de-novo hard path)
Unlike BLIND1/BLIND2/BLIND3 (de-novo CarveMe, "new pathogen, no curated model" hard path), BLIND6 uses a **curated,
peer-reviewed, manually reconstructed archaeal GEM**: **iMR539** — Richards MR, et al. (2016) "Exploring hydrogenotrophic
methanogenesis: a genome scale metabolic reconstruction of *Methanococcus maripaludis*", *J. Bacteriol.* — BioModels
**BIOMD0000001099** (curated branch). 539 of the 1,722 protein-coding genes, 688 reactions, 710 metabolites. The GEM is
loaded as-is; **no essentiality information enters the reconstruction or the FBA on our side.**
- **Curated-model circularity caveat (disclosed):** a curated GEM encodes prior biological knowledge and the authors report
  ~93% agreement with *experimental phenotype* data (growth on substrates, not the Sarmiento gene-essentiality set). A
  reviewer may note that a manually curated network can implicitly reflect known biology, so BLIND6 is a slightly *weaker*
  independence test than BLIND1/3's fully de-novo carves. It remains genuinely prospective-blind in the operative sense:
  the FBA-essentiality prediction is a deterministic function of the network topology and is computed and hashed **before**
  the Sarmiento essential-gene SET is ever fetched or read.

## Locked prediction (Stage 1 output, committed before reveal)
COBRApy single-gene-deletion FBA on iMR539; a gene is **FBA-essential if its knockout growth < 1% of WT**
(identical rule to BLIND1/2/3/4/CROSSVAL). The full per-gene call is written to `results/LOCKED_predictions.tsv`
(columns: `mmp_locus`, `symbol`, `uniprot`, `fba_essential`, `growth_ratio`); the sorted essential-identifier set is hashed
to `results/LOCKED_predictions.sha256` (payload = `"\n".join(sorted(mmp_locus for fba==1))`, BLIND1 hashing convention).
**Identifier note:** the curated GEM's gene ids ARE **MMP#### locus tags** — the SAME namespace the Stage-2 essentiality
resource uses — so the primary/hashed identifier is the MMP locus tag (UniProt accession + gene symbol are attached from the
reference proteome for readability). This is the only deviation from the BLIND1/3 lock format and it makes Stage-2
adjudication a **direct locus-tag match** with no cross-namespace bridge required.
- **Determinism verified:** `build.py` was run twice; `LOCKED_predictions.tsv` is byte-identical and the essential-set
  sha256 is identical across runs (GLPK signed-zero jitter in the growth-ratio column is collapsed to `0.0`; it never
  affected any 0/1 call or the hashed payload).

## Pre-registered experimental source (fixed now, fetched only in Stage 2 — NOT read yet)
**I WILL score against:** Sarmiento F, Mrázek J, Whitman WB (2013) **"Genome-scale analysis of gene function in the
hydrogenotrophic methanogenic archaeon *Methanococcus maripaludis*"**, *PNAS* 110(12):4726–4731. **PMID 23487778 /
PMC3607031.** Method: whole-genome **transposon (in vitro Tn5) mutagenesis** essentiality screen, same strain S2.
- The per-gene essentiality-index (EI) classification for all genes is in the paper's **supplementary Dataset S4**.
  URL: `https://pmc.ncbi.nlm.nih.gov/articles/PMC3607031/` (PNAS SI, Dataset S4).
- **Identifier FORMAT (confirmed) = `MMP####` locus tags** (e.g. `MMP0001`) — the same namespace as the iMR539 gene ids,
  so no homology bridge is needed for adjudication.
- **Blindness note (transparent):** to confirm the dataset EXISTS and to plan Stage 2 I read ONLY aggregate metadata from
  the paper's abstract/methods (organism, strain, method, the identifier FORMAT, the total gene count 1,779, and the
  aggregate "~526 possibly essential" figure) and the name of the supplementary table. I did **NOT** fetch, open, or parse
  Dataset S4 or any per-gene essential/non-essential membership. The FBA lock is by construction answer-independent.

## Adjudication (fixed now)
Primary: **direct MMP-locus-tag match** — parse Dataset S4, take the set of genes classified essential (by the paper's own
EI threshold), intersect with the 539 locked GEM genes on the MMP locus tag, and score the SAME LOCKED predictions
(sha-verified unchanged). If Dataset S4's identifiers or thresholds require interpretation, the fallback is the same
namespace-independent **sequence-homology bridge** (mmseqs easy-search, pident ≥ 90 same-species cutoff, set once) used in
BLIND1–3 — but it is expected to be unnecessary here since both sides are MMP-keyed.

## Pre-registered hypothesis & decision rule (fixed now — IDENTICAL to BLIND1–5)
**H1:** the locked FBA-essential set is enriched for the experimental essential set (Sarmiento 2013), 2×2 Fisher
**odds ratio > 3 AND p < 0.01** over the GEM (metabolic-subproteome) genes.
- **PASS** ⇒ prospective-blind evidence that the FBA-essentiality mechanism signal predicts experimental essentiality on a
  genuinely novel, pre-registered organism from the **third domain of life (Archaea)** → the suite spans all three domains.
- **FAIL** ⇒ reported first-class as an honest negative (e.g., the signal does not transfer to a hydrogenotrophic
  methanogen, or the curated archaeal network's essentiality structure diverges from the transposon screen) — recorded,
  not hidden or re-run to a better number. An honest negative here is itself a finding about the method's reach to a
  deeply divergent domain.

## Scope (what a PASS does and does not show)
Essentiality-enrichment only; in-silico FBA vs a published transposon screen (not a wet-lab experiment we ran);
prospective-BLIND in the lock/held-out sense; curated (not de-novo) model, with the circularity caveat above;
species/strain-level; **NOT drug-target / selectivity / clinical** (and archaea are not human pathogens). Precision/recall
are bounded by the metabolic subproteome (~539 of 1,722 genes).

## Sources & hashes (provenance)
- GEM: curated iMR539, BioModels **BIOMD0000001099** (file `MODEL1607200000_url.xml`), SBML L2V1.
  `$INTERCEPTA_DATA/blind6/mmp_iMR539.xml`
  sha256 `57e3885fc243521a466fdafa553417b9473a49327c5945e7467023e0917a3a97`
  (539 genes, 688 reactions, 710 metabolites, WT biomass growth 0.0973; objective `biomass0`).
- Proteome (for symbol/accession mapping only): UniProt reference proteome **UP000000590** (M. maripaludis S2, 1,722
  proteins), `https://rest.uniprot.org/uniprotkb/stream?query=proteome:UP000000590&format=fasta`
  → `$INTERCEPTA_DATA/blind6/mmp_proteome.fasta`
  sha256 `0d97916fd32bc3ea5bb6fa2a34bddb2fb5245b77c1dfd9620162f3ca341445bc`.
- MMP→UniProt map: `$INTERCEPTA_DATA/blind6/mmp_map.tsv` (accession, gene_primary, gene_oln)
  sha256 `5eaab97ec3fc5657c8704fb9c15b77200eef449229a48ace3b56485dc320fa58`.
- Essentiality (named now, fetched/parsed only in Stage 2): Sarmiento 2013 PNAS PMC3607031, Dataset S4 (MMP locus tags).

## LOCKED-predictions commitment (blindness audit trail)
- `results/LOCKED_predictions.sha256` (essential MMP-locus payload sha256):
  **`e41877bfb22556c3032c69165c4254c3f0a90d9d05b707b1ac002f1ae7f5d111`**
- GEM: 539 genes, WT growth 0.0973, **231 FBA-essential** genes predicted (frozen).
- Stage-1 locked BEFORE Stage-2 reveal. Recorded here as the pre-reveal blindness commitment. This module did NOT git commit.

---
## REVEAL OUTCOME (Stage 2, to be filled after the lock is committed to git)
*(empty — Stage 2 not run; no score.py written; no essentiality membership read.)*
