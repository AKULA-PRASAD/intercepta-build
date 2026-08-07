# BLIND5 — pre-registered PROSPECTIVE-blind essentiality test on the EUKARYOTE *Komagataella phaffii* GS115 (= *Pichia pastoris*)

**Registered (Stage 1) BEFORE the experimental essential-gene SET was fetched, parsed, opened, or used to build any
prediction.** This is the FIFTH prospective-blind essentiality validation in the INTERCEPTA blind suite, and the **FIRST
that crosses the prokaryote/eukaryote divide** — every prior blind organism (BLIND1 *N. gonorrhoeae*, BLIND2 *C. jejuni*,
BLIND3 *B. thetaiotaomicron*, BLIND4 *S. pneumoniae*) is a bacterium. Predictions are locked (hashed) first; the
experimental answer is fetched and scored only in Stage 2 (a separate later commit). The lock sha recorded below is the
pre-reveal blindness commitment. This module did NOT and cannot git commit; the orchestrator commits the lock file BEFORE
the reveal — the git history is the audit trail of blindness.

## Organism & rationale (Stage 0)
***Komagataella phaffii* strain GS115 / ATCC 20864** (the yeast formerly and widely known as *Pichia pastoris*), NCBI
taxon 644223, UniProt reference proteome UP000000314.
- **First EUKARYOTE in the prospective-blind suite.** BLIND1–4 are all bacteria. Extending the locked-before-reveal
  protocol to a eukaryote is the qualitative jump the suite was missing — the "predicts across kingdoms" claim, now under
  the *same* prospective-blind discipline (not a retrospective eukaryote test as HARDENF1/GENERALIZE4 were).
- **Genuinely never used in ANY prior INTERCEPTA experiment.** Verified: `Komagataella` / `phaffii` / `Pichia` /
  `pastoris` appear in **0** files under `experiments/` (`grep -rli` → 0 hits each). Its essentiality has NEVER been
  fetched, parsed, or inspected by this pipeline (blindness intact; see the honest note below on what index-level metadata
  was read).
- **Distinct clade, and never-inspected — unlike the two eukaryotes already touched.** *S. cerevisiae* (GENERALIZE4) and
  *C. albicans* (HARDENF1) are excluded by directive. *S. pombe* was also excluded: it is NOT 0-hits (it appears in the
  HARDENF1 files, where it was ATTEMPTED and reported as an honest boundary — no usable curated GEM with machine-readable
  GPR was found — and its DEG essential-gene COUNT was noted), so it is neither never-used nor a clean GEM path.
  *K. phaffii* is a different genus (Saccharomycetales, family Pichiaceae — a methylotrophic yeast), never used here, with
  a genuinely never-inspected essentiality resource AND a loadable curated GEM.
- **Why a model/industrial eukaryote and not a WHO fungal PATHOGEN.** The directive prefers a real fungal pathogen IF it
  has an open, published, GENOME-WIDE essentiality resource obtainable CPU-only, else a clean model eukaryote (S. pombe is
  named as "an excellent rigorous choice — the prokaryote/eukaryote-divide claim is the point"). I checked the three
  suggested WHO fungal-priority pathogens: **none of *Cryptococcus neoformans*, *Candida glabrata* (*Nakaseomyces
  glabratus*), or *Candida auris* has a genome-wide essentiality entry in the Database of Essential Genes (DEG)**, and with
  the session's web-search budget exhausted I could not confirm — CPU-only, without fabricating — an OPEN, published,
  genome-wide essentiality screen with a clean identifier namespace for any of them (Schwarzmüller-2014 *C. glabrata* is a
  ~619-gene targeted deletion set, not genome-wide; *Cryptococcus* deletion collections are not a saturation essentiality
  screen; a clean open *C. auris* genome-wide screen could not be confirmed). Rather than guess or fabricate a
  fungal-pathogen essentiality source, I chose the best-supported, fully-verifiable eukaryote that satisfies EVERY hard
  requirement: *K. phaffii* has (a) a **gold-standard genome-wide essentiality screen** in DEG (DEG2027, transposon
  mutagenesis, 753 essential genes) and (b) an **openly downloadable, cobra-loadable CURATED GEM** (iMT1026 v3). This is
  strictly stronger than the sanctioned S. pombe fallback (which had a genome-wide label but NO usable GEM). Honest caveat:
  *K. phaffii* is a biotechnology workhorse, not a clinical pathogen — the prokaryote/eukaryote-divide claim is the point,
  exactly as the directive frames the S. pombe option.

## Deployment scenario (deliberate — curated GEM, honest note)
Unlike BLIND1–4 (de-novo CarveMe carves from the proteome), BLIND5 uses a **published, curated genome-scale model**,
because CarveMe's default reaction universe is **bacterial** and a de-novo carve of a eukaryote against a bacterial
universe would be low-quality and non-representative (the exact caveat the directive flags). A curated fungal GEM is the
higher-quality, honest path for a eukaryote. (pyscipopt 6.2.1 is present, so a de-novo carve was *possible* — it was
rejected on quality grounds, not availability.) The GEM is used exactly as published, in its own default medium; no
essentiality information enters the model or the FBA. This is the same "use the curated model as-is" path as HARDENF1
(*C. albicans*) and GENERALIZE4 (*S. cerevisiae*).

- **GEM:** *P. pastoris* / *K. phaffii* model **iMT1026 v3** (Tomàs-Gamisans, Ferrer, Albiol; BioModels
  **MODEL1612130000**, file `MODEL1612130000_url.xml`, SBML L2). Publication lineage: Tomàs-Gamisans et al. 2016
  *Microbial Biotechnology* 9(6):787 (iMT1026) and the 2018 v3 update. Loads in cobra 0.31 with **1026 genes / 2237
  reactions / 1706 metabolites**; WT growth in the model's default medium = **0.057750** (positive; leaner than the
  C. albicans model, so a non-trivial FBA-essential set is expected). Gene IDs are GS115 systematic locus tags
  (`PAS_chrX-Y_NNNN`, a few contig `PAS_cNNN_NNNN` and standard-name genes).
  Local: `$INTERCEPTA_DATA/blind5/kphaffii_iMT1026v3.xml`
  sha256 `55b0e634d25ee0970103ae905e8c33ccb23377f464461181411930c9c998ad01`.
- **Proteome (for ID mapping only):** UniProt reference proteome **UP000000314** (*K. phaffii* GS115, 5038 proteins),
  `https://rest.uniprot.org/uniprotkb/stream?query=proteome:UP000000314&format=fasta`
  → `$INTERCEPTA_DATA/blind5/kphaffii.fasta`
  sha256 `9d56862fa4a6c880bebc023dcff297a5ec3f7e30ef7a9421666eea2f4e1fde09`.
  Used only to map GEM locus tags → UniProt accessions (971/1026 map by gene name); it does NOT enter the FBA.

## Locked prediction (Stage 1 output)
COBRApy `single_gene_deletion` on the curated GEM in its default medium (`processes=1`, deterministic); a gene is
**FBA-essential iff its knockout growth < 1% of WT** (identical rule to BLIND1–4 / HARDENF1 / GENERALIZE4). The full
per-gene call (GS115 locus tag + mapped UniProt accession + fba 0/1 + KO/WT growth ratio) is written to
`results/LOCKED_predictions.tsv`; the **sorted set of FBA-essential locus tags** is hashed to
`results/LOCKED_predictions.sha256` (payload = `"\n".join(sorted(locus for fba==1))`). This computation is a deterministic
function of the metabolic network only and is provably independent of which genes are experimentally essential.
- **Hashed key = GS115 locus tag** (the GEM's native identifier), a deviation from the BLIND1–3 convention of hashing
  UniProt accessions — because this is a curated GEM whose gene IDs are locus tags, not CarveMe UniProt IDs. Honest,
  disclosed, and namespace-consistent; the UniProt accession is carried as a convenience column for Stage-2 adjudication.
- **Determinism:** signed-zero GLPK jitter in the growth-ratio column is collapsed to `0.0` and KO growth is rounded 6 dp
  before the WT-ratio (4 dp), so the tsv artifact is fully canonical. `build.py` is run twice and the LOCKED_predictions.tsv
  is byte-identical with an identical essential-set sha256 (recorded below).

## Pre-registered experimental source (NAMED now, fetched only in Stage 2 — NOT read)
**I WILL score against DEG accession `DEG2027`** — *Komagataella phaffii* GS115 essential genes, **genome-wide transposon
mutagenesis**, **753 essential genes** (per the DEG organism index). Database of Essential Genes (DEG), Tianjin University:
`http://tubic.org/deg/` (browse eukaryotes → accession `DEG2027`; historical host `http://tubic.tju.edu.cn/deg/`). The
essential PROTEIN sequences will be taken from the DEG eukaryote protein download (the DEG-provided `.aa`/FASTA for
DEG2027), fetched and parsed ONLY in Stage 2.
- **Blindness note (transparent — mirrors BLIND3).** To confirm the dataset EXISTS and to plan the Stage-2 adjudication I
  read ONLY organism-index-level metadata: the DEG eukaryote browse table (organism name, DEG accession, essential-gene
  COUNT = 753, method = transposon mutagenesis) and, from the DEG2027 record header, the strain (GS115) and the fact that
  DEG assigns internal per-gene IDs of the FORMAT `DEG20270NNN`. I did NOT fetch, open, or parse the essential-gene SET —
  I did not record which genes, which locus tags, or which sequences are essential. The FBA lock is by construction
  answer-independent. Full essential-set retrieval and parsing happen only in Stage 2.

## Adjudication (fixed now — identical, namespace-independent method to BLIND1–3)
Primary/robust: **sequence-homology bridge** — map DEG2027's essential PROTEIN sequences onto our GS115 proteome / GEM
gene set by **mmseqs easy-search, pident ≥ 90** (same-species ortholog cutoff, set once, not swept), defining the
experimental-essential set in our identifier space, then score the SAME LOCKED predictions (sha-verified unchanged). A
symbol/locus-tag match (both sides are GS115 `PAS_` systematic names) will be reported as a secondary cross-check. This is
the identical method that adjudicated BLIND1–3 and is robust to namespace mismatch (our declared #1 failure mode).

## Pre-registered hypothesis & decision rule (fixed now — IDENTICAL to BLIND1–4)
**H1:** the locked FBA-essential set is enriched for the experimental essential set (DEG2027), 2×2 Fisher
**odds ratio > 3 AND p < 0.01** over the GEM (metabolic-subproteome) genes.
- **PASS** ⇒ prospective-blind evidence that the FBA-essentiality mechanism signal predicts experimental essentiality on a
  genuinely novel, pre-registered EUKARYOTE — the FIRST cross-kingdom (prokaryote→eukaryote) confirmation in the blind
  suite, under the same locked-before-reveal discipline.
- **FAIL** ⇒ reported first-class as an honest negative (e.g., the signal does not transfer to a eukaryote under blind
  lock, or a curated-GEM/medium artifact) — recorded, not hidden or re-run to a better number.

## Scope (what a PASS does and does not show)
Essentiality-enrichment only; in-silico FBA vs a published genome-wide transposon screen (not a wet-lab experiment we ran);
prospective-BLIND in the lock/held-out sense; curated model is still a model (medium/gap-fill assumptions); species/strain
level (GS115 GEM vs GS115 screen — exact-strain match); NOT drug-target / selectivity / clinical. *K. phaffii* is a model/
industrial eukaryote, not a clinical pathogen — the value here is the prokaryote/eukaryote-divide crossing under blind lock.
Precision/recall are bounded by the metabolic subproteome.

## Solver note (deterministic reproducibility — disclosed)
The curated iMT1026 v3 network has a KO LP (gene **PAS_chr3_0036**, gating reaction `AMETtm`, S-adenosyl-methionine
mitochondrial transport) on which the **default float GLPK simplex CYCLES indefinitely** (single-gene deletion hangs).
The lock therefore pins the **exact-rational simplex `glpk_exact`**, which cannot cycle and is fully deterministic; it
solves that KO cleanly (growth 0.0 = essential) and completes the full 1026-gene deletion in ~33 s single-process
(`processes=1`), run in 50-gene batches (a single monolithic all-genes call was avoided). This is a *more* rigorous
(exact) essentiality call, not a workaround that changes the answer. Disclosed for full reproducibility.

## LOCKED-predictions commitment (blindness audit trail)
- `results/LOCKED_predictions.sha256` (essential-locus-tag payload sha256):
  **`e68760b40e57443a0772b1734e6bf6efd93f3b7ec1e292328ad4a1a03ff6e551`**
- GEM: 1026 genes, WT growth 0.057750, **167 FBA-essential** genes predicted (frozen); 971/1026 GEM genes mapped to a
  UniProt accession (convenience column; the hashed key is the GS115 locus tag).
- Determinism: reproduced ×2 — LOCKED_predictions.tsv byte-identical, essential-set sha256 identical (glpk_exact).
- Stage-1 locked BEFORE Stage-2 reveal. Recorded here as the pre-reveal blindness commitment. This module did NOT git commit.
