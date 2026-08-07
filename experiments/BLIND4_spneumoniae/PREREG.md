# BLIND4 — pre-registered PROSPECTIVE-blind essentiality test on *Streptococcus pneumoniae* TIGR4

**Registered (Stage 1) BEFORE the experimental essential-gene SET was fetched, parsed, opened, or used to build any
prediction.** This is the THIRD independent prospective-blind essentiality validation, run under the identical protocol as
BLIND1 (*N. gonorrhoeae* MS11) and BLIND2 (*C. jejuni* NCTC 11168). Predictions are locked (hashed) first and committed to
git by the orchestrator; the experimental answer is fetched and scored only in Stage 2 (a separate later commit). The git
history is the audit trail of blindness. The lock sha recorded below is the pre-reveal blindness commitment (I build + lock
only; I cannot git commit).

## Organism & rationale (Stage 0)
*Streptococcus pneumoniae* serotype 4 (strain **ATCC BAA-334 / TIGR4**), NCBI taxid **170187**, genome **NC_003028**.
- **Genuinely never used** in ANY prior INTERCEPTA experiment. Verified by grep over `experiments/`:
  `streptococcus|spneumo|s. pneumoniae|tigr4|d39` → the ONLY `streptococcus` hit is *Streptococcus pyogenes*
  (STRUCTREPURPOSE1); **zero** hits for *S. pneumoniae* / TIGR4 / D39. (The 148 `pneumoniae` substring hits elsewhere are
  all *Klebsiella pneumoniae* = `kpneumoniae`, a different genus already in the ever-used token set — not this organism.)
- **NEW CLADE for the essentiality suite — Firmicutes (Bacilli).** BLIND1 (β-proteobacterium) and BLIND2
  (ε-proteobacterium) are both Gram-negative proteobacteria. *S. pneumoniae* is a Gram-positive Firmicute, adding genuine
  phylogenetic and cell-envelope breadth to the prospective-blind panel.
- **Major WHO / global clinical priority.** Leading cause of community-acquired pneumonia, bacterial meningitis, otitis
  media, and sepsis; a top global cause of vaccine-preventable death in children. **Penicillin- and macrolide-resistant
  pneumococcus is a WHO priority AMR pathogen / CDC "serious threat."**
- **Gold-standard essentiality exists.** *S. pneumoniae* TIGR4 is the organism in which genome-wide **Tn-seq** was pioneered
  (van Opijnen, Bodi & Camilli, *Nat Methods* 2009) — a best-case experimental truth set for a prospective-blind test.

## Deployment scenario (deliberate, honest hard path)
No curated BiGG genome-scale model is used → we build a **de-novo CarveMe reconstruction from the UniProt reference
proteome** (UP000000585, 2109 proteins, TIGR4), default universe (`bacteria`), default complete medium, no gapfilling,
diamond homology + MILP consensus carve. This is the real "new pathogen, no curated model" deployment case — the same
honest, weaker path used in BLIND1/BLIND2 (not a curated best case). The GEM is a deterministic function of the
genome/proteome ALONE; **no essentiality information enters the reconstruction or the FBA.**

## Locked prediction (Stage 1 output, committed before reveal)
COBRApy single-gene-deletion FBA on the CarveMe GEM; a gene is **FBA-essential if its knockout growth < 1% of WT**
(identical rule to BLIND1, BLIND2, CROSSVAL). The full per-gene call (UniProt accession + symbol + fba 0/1 + KO growth
ratio) is written to `results/LOCKED_predictions.tsv`; the sorted essential-accession set is hashed to
`results/LOCKED_predictions.sha256`. This computation is provably independent of which genes are experimentally essential.

## Pre-registered experimental source (fixed now, fetched only in Stage 2 — NOT yet fetched/parsed/opened)
Strain-matched to our GEM/proteome (TIGR4) to avoid any strain gap.
- **PRIMARY (gold standard): van Opijnen, Bodi & Camilli (2009)**, *Tn-seq: high-throughput parallel sequencing for fitness
  and genetic interaction studies in microorganisms*, **Nature Methods 6(10):767–772**, DOI **10.1038/nmeth.1377**,
  `https://www.nature.com/articles/nmeth.1377` — genome-wide **Tn-seq** essentiality/fitness for *S. pneumoniae* TIGR4.
  Identifier FORMAT (noted, membership NOT read): **`SP_XXXX` ordered-locus tags** on genome NC_003028 (the same locus-tag
  namespace carried in our locked `symbol` column for the TIGR4 entries). Machine-readable essential-gene lists derived
  from this Tn-seq work are also curated in **OGEE v3** (`https://v3.ogee.info/`, *S. pneumoniae* TIGR4).
- **STRAIN-MATCHED FALLBACK (guaranteed executable): DEG accession `DEG1007`** — *S. pneumoniae* TIGR4, genome NC_003028,
  `https://tubic.org/deg/` — protein sequences already local in `$INTERCEPTA_DATA/expval_deg/DEG10.aa.gz`. Identifier FORMAT
  (from DEG catalog metadata only): TIGR4 locus tags / GI numbers. NOTE: DEG1007 is insertion-duplication + allelic-
  replacement mutagenesis (Thanassi 2002 / Song 2005), NOT Tn-seq — hence the *fallback*, used only if the van Opijnen
  Tn-seq list is not retrievable in a parseable form. Registered so Stage 2 can always proceed on a strain-matched set.
- **DECISION RULE (fixed now):** if the van Opijnen Tn-seq essential list is retrievable in machine-readable form, it is the
  PRIMARY experimental truth; otherwise DEG1007. Either way the LOCKED predictions and their sha are unchanged.
- **Blindness note (transparent):** to choose the source I inspected only the DEG *catalog metadata* (`deg_bacteria.csv`:
  organism, method, accession, genome, gene-count columns) and UniProt *proteome metadata* — never any essential-gene
  membership. The FBA lock is answer-independent and could not use it. Full essential-set fetch/parse happens only in Stage 2.

## Adjudication (fixed now)
Primary/robust: **sequence-homology bridge** — map the experimental essential PROTEIN sequences onto our CarveMe proteome by
**mmseqs easy-search, pident ≥ 90** (same-species ortholog cutoff, set once, not swept), defining the experimental-essential
set in our accession space, then score the SAME LOCKED predictions (sha-verified unchanged). Identical, namespace-independent
method that adjudicated BLIND1/BLIND2. Because van Opijnen (TIGR4, `SP_XXXX`) and our proteome (TIGR4, `SP_XXXX`
ordered-locus names) share the strain and annotation, a **direct `SP_XXXX` locus-tag match** is registered as a corroborating
cross-check.

## Pre-registered hypothesis & decision rule (fixed now — IDENTICAL to BLIND1/BLIND2)
**H1:** the locked FBA-essential set is enriched for the experimental essential set, 2×2 Fisher
**odds ratio > 3 AND p < 0.01** over the GEM (metabolic-subproteome) genes.
- **PASS** ⇒ prospective-blind evidence that the FBA-essentiality mechanism signal predicts experimental essentiality on a
  third, genuinely novel, pre-registered pathogen from a NEW clade (Gram-positive Firmicute) with a gold-standard Tn-seq
  truth set → the flagship becomes n = 3 across three phyla.
- **FAIL** ⇒ reported first-class as an honest negative (e.g., sparse de-novo GEM for this fastidious/fermentative organism,
  or the signal does not transfer to Firmicutes) — recorded, not hidden or re-run to a better number.

## Scope (what a PASS does and does not show)
Essentiality-enrichment only; in-silico FBA vs a published Tn-seq screen (not a wet-lab experiment we ran); prospective-BLIND
in the lock/held-out sense; de-novo model; species/strain-level; NOT drug-target / selectivity / clinical. Precision/recall
are bounded by the metabolic subproteome (a sparse de-novo GEM predicts few, core-metabolic essentials → expect low recall).

## Sources & hashes (provenance)
- GEM proteome: UniProt reference proteome **UP000000585** (TIGR4, taxid 170187, 2109 proteins),
  `https://rest.uniprot.org/uniprotkb/stream?query=proteome:UP000000585&format=fasta`
  → `$INTERCEPTA_DATA/blind4/spneumo.fasta`
  sha256 **`4d321cf1a9e06017d937cf7f5572dea11513a6a82df369184409a8f965a2a16a`**
- GEM: CarveMe de-novo `$INTERCEPTA_DATA/blind4/spneumo.xml`
  sha256 **`77ffc13a331c1af4512ef7adf460deb78c361adb89ee983d01915ed31eef7f08`**
  (**634 genes, 1511 reactions, 1064 metabolites, WT growth 54.994**; 878 annotated + 3934 non-annotated candidate
  reactions scored, 828 annotated / 460 non-annotated included).
- Essentiality (Stage 2, NOT fetched): van Opijnen 2009 Tn-seq (primary) / DEG1007 (fallback), as above.

## LOCKED-predictions commitment (blindness audit trail)
- `results/LOCKED_predictions.sha256` — sorted essential-accession payload sha256:
  **`f86a02a4e7107ec2c12e3a231942449a01dc24f1be78fbbae42b6db1b8b5651d`**
- `results/LOCKED_predictions.tsv` — full-file sha256:
  **`372a0955c1854f62b682041e3d61f4700fb01012512b7ed828b2574fe246bef5`**
- GEM: 634 genes, WT growth 54.994, **14 FBA-essential** rows predicted (13 real genes: murB, murG, gmk, tmk, pyrH, metK,
  ispA, pdxS, SP_0729, SP_1110, SP_1161, SP_1551, SP_1982; + CarveMe `spontaneous` pseudo-gene, kept for protocol
  consistency with BLIND2 — it maps to no UniProt accession and cannot be counted as experimentally essential in Stage 2).
- **Determinism verified:** FBA recomputed 3×; essential-accession sha identical every time and the full TSV byte-identical
  (signed-zero collapsed) → the locked commitment is reproducible.
- Stage-1 locked BEFORE Stage-2 reveal. Recorded here as the pre-reveal blindness commitment.

---
## REVEAL OUTCOME (Stage 2, filled after the lock was recorded)
_(empty — no reveal performed in Stage 1; to be filled only after the orchestrator commits this lock)_
