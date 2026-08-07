# BLIND7 — pre-registered PROSPECTIVE-blind essentiality test on *Trypanosoma brucei brucei* TREU927

**Registered (Stage 1) BEFORE the experimental essential-gene SET was fetched, parsed, or used to build any prediction.**
This is the first **KINETOPLASTID** entry in the prospective-blind essentiality suite (BLIND1–4 bacteria across four
phyla; BLIND5 eukaryote/fungus *K. phaffii*; BLIND6 archaeon). Predictions are locked (hashed) first; the experimental
answer is scored only in Stage 2 (a separate later commit). The lock sha recorded below is the pre-reveal blindness
commitment (the orchestrator commits the lock file; this module cannot and does not git commit).

## Organism & rationale (Stage 0)
*Trypanosoma brucei brucei* strain **TREU927 / 927-4 GUTat10.1** (UniProt reference proteome UP000008524, taxon 185431,
genome assembly GCA_000002445.1). Causative-genus agent of **human African trypanosomiasis (sleeping sickness)** and
nagana — a **kinetoplastid protozoan**, a distinct and phylogenetically deep eukaryotic-pathogen class from the
apicomplexans (*Plasmodium*/*Toxoplasma*, done non-blind in GENERALIZE5) and from fungi (BLIND5).
- **New pathogen class + real vision relevance.** Kinetoplastids (Trypanosoma, Leishmania) are the agents of major
  **neglected tropical diseases (NTDs)** — sleeping sickness, Chagas, leishmaniasis. Adding one is genuine
  disease-discovery breadth, not generality-only value.
- **Enabling data exists (essentiality never inspected).** *T. brucei* has a genome-wide loss-of-fitness screen —
  **Alsford et al. 2011, *Genome Research*, RIT-seq** (RNAi target sequencing; bloodstream + insect life-cycle stages;
  ~7,435 protein-coding genes assayed). This is the requirement for a blind score. Its EXISTENCE and identifier FORMAT
  were confirmed (below); its gene MEMBERSHIP (which genes lose fitness) was NOT fetched, opened, or parsed.

### Blindness / novelty audit (HONEST DEVIATION — read this)
The task expected `grep experiments/` → **0 hits** for `trypanosoma|brucei|cruzi|leishmania|kinetoplast`. That is
**not** literally true and is disclosed here rather than glossed:
- `tbrucei`, `lmajor`, `tcruzi` appear as **drug-target reference-panel keys** in the *target-ID* line —
  `MET1`, `MET2`, `TID3`, `TID4`, `FOLD1` — i.e. small lists of *known validated drug targets* (and, in FOLD1,
  AlphaFold structures of those targets) used as homology/conservation reference organisms.
- They were **never** used in the FBA-essentiality blind/dev suite; **no kinetoplastid GEM was ever built**; and
  **no kinetoplastid genome-wide essentiality screen was ever fetched or parsed** (searched `$INTERCEPTA_DATA` — the
  only kinetoplastid files are FOLD1's known-target FASTAs/structures, not essentiality). The word-level grep for
  `trypanosoma`/`leishmania`/`kinetoplast` is 0; the hits are the `tbrucei`/`lmajor`/`tcruzi` short keys only.
- **Substantive conclusion:** the two conditions this suite actually cares about hold — (1) *T. brucei* has never been a
  subject of an essentiality prediction/GEM here, and (2) its experimental essentiality has never been inspected. A
  handful of its *known drug targets* being in a conservation panel cannot leak the *genome-wide RIT-seq essentiality
  answer* into a metabolic-network FBA computation. Recorded as an honest deviation, not hidden.

## Deployment scenario (deliberate, honest hard path)
No open, ready-to-run **genome-scale** *T. brucei* metabolic model was found: BioModels holds only `BIOMD0000000428`
(Achcar 2012 — a glycolysis-only ODE kinetic model, not a genome-scale FBA reconstruction). The curated
kinetoplastid GEM iAC560 is *Leishmania major*, a different species that would inject a species gap against a
*T. brucei* essentiality screen. So we use a **de-novo CarveMe reconstruction from the UniProt reference proteome**
(UP000008524, 8,588 proteins; `carve --fbc2 --solver scip`, default bacterial universe / complete medium). The GEM is
built from the proteome ALONE; no essentiality information enters the reconstruction or the FBA.

- **DOMAIN-MISMATCH CAVEAT (prominent, first-class).** CarveMe's reference universe is **bacterial**. *T. brucei* is a
  divergent eukaryote, so only genes with bacterial homologs carve in: the model has **337 genes** — just **3.9 %** of
  the 8,588-protein proteome (contrast BLIND3 *B. theta*: 830 GEM genes ≈ 17 % of a bacterial proteome). This sparse
  carve is itself an **honest finding** about the reach of a bacterial-universe tool on a kinetoplastid. The model does
  **grow** (WT objective 53.43 > 0), so single-gene-deletion FBA essentiality is well-defined over these 337 genes.

## Locked prediction (Stage 1 output)
COBRApy `single_gene_deletion` FBA on the CarveMe GEM; a gene is **FBA-essential if its knockout growth < 1 % of WT**
(identical rule to BLIND1–6 / CROSSVAL). The per-gene call (UniProt accession + TriTrypDB symbol + fba 0/1 + KO growth
ratio) is in `results/LOCKED_predictions.tsv`; the sorted essential-**accession** set is hashed to
`results/LOCKED_predictions.sha256` (payload = `"\n".join(sorted(acc for fba==1))`, BLIND1 convention). This computation
is a deterministic function of the metabolic network only and is provably independent of which genes are experimentally
essential. **Determinism verified:** `build.py` run twice → `LOCKED_predictions.tsv` byte-identical and the essential-set
sha256 identical (`processes=1`; KO-growth rounded 6dp then WT-ratio 4dp; signed-zero collapsed to `0.0` — never affected
any 0/1 call or the hashed payload).

## Pre-registered experimental source (fixed now, fetched only in Stage 2)
**I WILL score against the *T. brucei* RIT-seq genome-wide loss-of-fitness screen:** **Alsford S, Turner DJ, Obado SO,
Sanchez-Flores A, Glover L, Berriman M, Hertz-Fowler C, Horn D (2011)** "High-throughput phenotyping using parallel
sequencing of RNA interference targets in the African trypanosome", *Genome Research* **21(6):915–924**,
DOI 10.1101/gr.115089.110, **PMID 21363968, PMCID PMC3106324**. Per-gene RIT-seq loss-of-fitness (bloodstream and/or
procyclic/insect stages), keyed by **TriTrypDB / GeneDB systematic gene IDs** (`Tb927.X.XXXX`, older `Tb0N.…` form —
the same namespace visible in our TSV `symbol` column). Source (NOT yet fetched): NCBI PMC supplementary of PMC3106324
(`https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3106324/`), the *Genome Research* article page, and/or the phenotype as
redistributed by TriTrypDB (`https://tritrypdb.org/`).
- **Blindness note (transparent):** to confirm the dataset EXISTS and to name the Stage-2 source I read ONLY the PubMed
  citation metadata (authors, title, journal, method, organism, life-cycle stages, gene-COUNT ~7,435, gene-ID format).
  I did NOT fetch, open, or parse the per-gene fitness SET (which genes lose fitness). The FBA lock is answer-independent
  by construction.

## Adjudication (fixed now)
Primary/robust: **sequence-homology bridge** — take the RIT-seq essential gene set (in Tb927 systematic-ID / protein
space) and map it onto our CarveMe proteome by **mmseqs easy-search, pident ≥ 90** (same-species ortholog cutoff, set
once, not swept), defining the experimental-essential set in our UniProt-accession space, then score the SAME LOCKED
predictions (sha-verified unchanged). This is the identical, namespace-independent method that adjudicated BLIND1–3
(robust to the Tb927↔UniProt namespace mismatch). Threshold for "RIT-seq essential" (the loss-of-fitness cutoff the
authors report) is fixed at reveal to the authors' own categorical/threshold call — NOT swept to a favorable number.

## Pre-registered hypothesis & decision rule (fixed now — IDENTICAL to BLIND1–6)
**H1:** the locked FBA-essential set is enriched for the experimental essential set (Alsford 2011 RIT-seq), 2×2 Fisher
**odds ratio > 3 AND p < 0.01** over the GEM (metabolic-subproteome) genes.
- **PASS** ⇒ prospective-blind evidence that the FBA-essentiality mechanism signal predicts experimental essentiality on
  a genuinely novel pre-registered organism from a NEW pathogen class (kinetoplastid, a major NTD) — extends the suite
  beyond bacteria/fungus/archaeon.
- **FAIL** ⇒ reported first-class as an honest negative. Two distinct failure modes are pre-named and equally publishable:
  (a) the FBA-essentiality signal genuinely does not transfer to a host-adapted kinetoplastid, or (b) the
  **bacterial-universe de-novo carve is too sparse/mismatched** (337/8588 genes) to carry signal — an honest
  **reach-limit** result for the tool on a divergent eukaryote. Recorded, never re-run to a nicer number.

## Honest caveats (fixed now)
- **Modality gap:** RIT-seq measures **RNAi-knockdown loss-of-fitness**, a slightly different modality than the
  transposon-insertion (Tn/INSeq) essentiality used in the bacterial BLINDs — knockdown ≠ knockout, and coverage is
  RNAi-library-dependent. Reported as a real cross-modality comparison.
- **Sparse de-novo GEM / domain mismatch** (above) — the dominant risk; a FAIL via mode (b) is a first-class finding.
- **Host-adapted metabolism:** bloodstream-form *T. brucei* is glucose-rich-host-adapted; a default-complete-medium GEM
  may be over-permissive. Reported either way.
- **Scope:** essentiality-enrichment only; in-silico FBA vs a published RNAi screen (not wet-lab we ran);
  prospective-BLIND in the lock/held-out sense; de-novo model; species/strain-level; NOT drug-target/selectivity/clinical.
  Precision/recall bounded by the (small) metabolic subproteome.

## Sources & hashes (provenance)
- GEM proteome: UniProt reference proteome **UP000008524** (*T. brucei brucei* TREU927, 8,588 proteins),
  `https://rest.uniprot.org/uniprotkb/stream?query=proteome:UP000008524&format=fasta`
  → `$INTERCEPTA_DATA/blind7/tbrucei.fasta`  sha256 `316f1286886cbf4df2ed614e8d69333cf68599db95b340d1ccff43816be92d73`
- GEM: CarveMe de-novo `$INTERCEPTA_DATA/blind7/tbrucei.xml` sha256
  `1b8daed8839ff4760382c935adcdd4b6e819764e7341ea54d60bc85e041b79fc`
  (337 genes, 1299 reactions, 1007 metabolites, WT growth 53.43; `carve --fbc2 --solver scip`, default universe/medium).
- Essentiality: Alsford 2011 RIT-seq (PMID 21363968 / PMC3106324) — **named now, fetched/parsed only in Stage 2.**

## LOCKED-predictions commitment (blindness audit trail)
- `results/LOCKED_predictions.sha256` (essential-accession payload sha256):
  **`31e8cc0047ba7643e40a82ab1b78a18cc92c0af0149f7a5a44bb404e6e6e6b0f`**
- `results/LOCKED_predictions.tsv` file sha256:
  `3d59ead633d260c209e2d61f1cdfee8a1fce971f853c1b2c883504c60c808a2f`
- GEM: 337 genes, WT growth 53.43, **21 FBA-essential** genes predicted (frozen).
- Stage-1 locked BEFORE any Stage-2 reveal. Recorded as the pre-reveal blindness commitment. This module did NOT git commit.

---
## REVEAL OUTCOME (Stage 2, filled AFTER the lock was committed to git — commit 1e77a7d, pushed)
**FAIL — a first-class, honest reach-limit NEGATIVE (exactly the outcome pre-named for the sparse-carve / domain-mismatch case).**
Lock verified intact FIRST: the sorted essential-UniProt payload of `results/LOCKED_predictions.tsv` re-hashes to
`31e8cc00…` (equal to the committed lock); predictions were NOT modified.

**Experimental essentiality actually used (Stage 2 fetch).** The paper's own call (Z-score > 3.3, Supplemental File 1A)
is behind the *Genome Research* paywall (genome.cshlp.org OIDC-gated; PMC not open-access; EuropePMC "not open access";
DEG has **no** *T. brucei* entry — only *Plasmodium* among parasites). So I used the **pre-registered open TriTrypDB /
VEuPathDB mirror** of the same Alsford/Horn RIT-seq reads: `GenesByHighThroughputPhenotyping` (Horn profile, release 68),
**bloodstream-form BFD6** (6 d / 20 doublings) vs uninduced `No_Tet`, **down-regulated** coverage (= loss of fitness),
protein-coding. VEuPathDB re-quantitates the reads as htseq/tpm **fold-change**, not the paper's DEGseq Z-score — a
documented DEVIATION; the verdict is shown robust across three fold-change thresholds. Old→new gene IDs bridged via the
release-68 GeneAliases crosswalk; essential PROTEIN sequences (TREU927 release-68) mapped onto our locked CarveMe proteome
by the pre-registered **mmseqs pident ≥ 90** homology bridge (same-strain orthologs hit at ~100 % identity).

**Result over the 337 locked GEM genes** (2×2 = both / FBA-only / exp-only / neither):
- **PRIMARY (fc ≥ 2): 5 / 16 / 104 / 212 → odds ratio 0.637, Fisher p = 0.867, precision 0.238, recall 0.046** — gate NOT met.
- Sensitivity fc ≥ 1.5 (VEuPathDB default): 5 / 16 / 129 / 187 → OR 0.453, p 0.966.
- Sensitivity fc ≥ 3: 3 / 18 / 70 / 246 → OR 0.586, p 0.872.

**All three ORs are < 1** (FBA-essentiality is, if anything, slightly *anti*-correlated with RIT-seq loss-of-fitness) —
nowhere near the pre-registered gate (OR > 3 AND p < 0.01). The FAIL is **robust to threshold choice**, so it is not a
cutoff artifact. This is the honest **reach-limit** result: a bacterial-universe de-novo carve of a divergent kinetoplastid
yields only 337/8588 genes (3.9 %), and over that small, biased metabolic subproteome the FBA-essentiality mechanism signal
that transferred to bacteria (BLIND1 6.13 / BLIND2 3.92 / BLIND3 8.03 PASS) and failed once before (BLIND4 2.96 FAIL) does
**not** transfer to *T. brucei*. Plausible, non-exclusive drivers (reported, not used to explain away): (a) the RIT-seq
loss-of-fitness set is very large (~⅓ of the GEM genes, 109/337, are experimentally essential), diluting enrichment;
(b) default-complete-medium FBA under-calls essentiality for a host-adapted bloodstream parasite; (c) RNAi-knockdown
fitness ≠ knockout essentiality (modality gap); (d) sparse/mismatched bacterial-universe carve.

**Honest caveat on the 2×2 denominator:** RIT-seq assayed ~7,435 of ~9,660 genes; GEM genes whose ortholog was not
assayed are counted here as non-essential (unknown→negative). This cannot rescue the verdict — OR is 0.45–0.64 vs a
required > 3 — but is disclosed. **Reproduced ×2 byte-identical**; reveal payload sha256
`b112943e8163bb0166474eca0a0ceed22bb4a65acd197385ca203a571bc6b014`.

**Provenance (Stage-2 fetches, $INTERCEPTA_DATA/blind7):** `ritseq_bfd6_fc2.ids` sha256
`a9578380b053186f030b457f56aa0cf2bb15ab3c963f27395ecf5dca8f92c279` (3542 old-ID bloodstream loss-of-fitness genes at
fc≥2); `ritseq_bfd6_fc1p5.ids` `7bda4325…`; `ritseq_bfd6_fc3.ids` `bb4de50b…`; GeneAliases r68
`3f5ddf2e…`; essential-protein superset FASTA `44776281…`. Source: TriTrypDB `https://tritrypdb.org/` (Alsford et al.
2011, *Genome Res* 21:915–924, PMID 21363968). This module did NOT git commit the reveal (orchestrator commits).

**Meaning:** a genuine prospective-blind NEGATIVE on a new pathogen class — recorded first-class, not hidden or re-run to a
nicer number. The blind suite now stands at n = 3 PASS (bacteria, across 3 phyla) + FAILs on *S. pneumoniae* (BLIND4) and
*T. brucei* (BLIND7); the transfer of FBA-essentiality signal is real but bounded — it does not reach a divergent,
host-adapted kinetoplastid via a bacterial-universe carve.
