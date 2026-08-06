# HARDENF1 — FBA essentiality on a REAL FUNGAL PATHOGEN (*Candida albicans*) — SUMMARY

**GATE: PASS** (same OR>3 AND p<0.01 gate as every bacterium and as GENERALIZE4; frozen in PREREG.md before
scoring). Reproduced x2 byte-identical.
**payload sha256:** `e6162793a7ab3eb9fdacdcd67dcadbba93ae28526cc1fff0a41bf9fb3985c6ff`
**Evidence tier:** VERIFIED (in-silico FBA vs a curated external experimental essentiality resource). Real
human fungal pathogen — this is the *C. albicans* goal that GENERALIZE4 could only approximate with model yeast.

## What this hardens
GENERALIZE4 showed FBA single-gene-deletion essentiality transfers to a eukaryote, but on n=1 — the *model*
yeast *S. cerevisiae*, not a pathogen. HARDENF1 repeats the identical pipeline on *Candida albicans* SC5314, a
genuine human fungal pathogen, taking the eukaryote->FBA entry to n>1 with a clinically relevant organism.

## Organism, data, mapping
- **GEM:** Mirhakkak & Schaeuble 2021 curated *C. albicans* GEM (BioModels **MODEL2110210002**), 771 genes /
  3316 reactions, sha256 `b92fe385...`. Publication doi:10.1038/s41396-020-00848-z.
- **Essentiality:** CGD curated phenotype annotations (`C_albicans_SC5314_phenotype_data.tab`, sha256
  `7a05dd66...`): a gene is essential iff it has >=1 `inviable` phenotype from a loss-of-function mutant
  (null/repressible/conditional). Includes the GRACE conditional-knockout essentiality (Roemer 2003) + later
  deletion studies. 1666 essential genes total.
- **ID bridge (namespace = #1 failure mode):** deterministic `CAALFM_C{chr}{coord}{W|C}{hap}` ->
  `C{chr}_{coord}{W|C}_{hap}` (CGD A22 systematic). **768/771** GEM genes resolve to the authoritative CGD A22
  ID universe; the 3 misses are mtDNA-encoded `CM_*` genes (no nuclear feature / no essentiality annotation) —
  clean, no namespace artifact.

## Result (gate frozen before scoring)
COBRApy single-gene-deletion on the curated GEM in its default medium (WT growth 130.632484; essential if KO
growth <1% WT, rounded 6 dp for GLPK jitter) vs the CGD essential set.
**OR 13.93, Fisher one-sided p 0.00409, precision 0.857, recall 0.025, AUROC 0.5355.**
Universe 771 metabolic genes; 236 experimental essentials mapped in-model.
Contingency: **both 6 / FBA-only 1 / exp-only 230 / neither 534.**

## Meaning + honest caveats (first-class)
The FBA-essentiality signal — validated in bacteria and in model-yeast — **holds on a real fungal pathogen**:
the enrichment is highly precise (6 of 7 FBA-essential genes are experimentally essential; OR 13.93) and clears
the pre-registered gate (p 0.00409 < 0.01). But the honest picture is **very-high-precision / very-low-recall**:
- The model's rich default medium (WT growth 130) makes almost nothing in-silico essential — only **7** of 771
  genes are FBA-essential. So the enrichment rests on a small FBA-essential set, and the p-value clears 0.01 but
  not by a huge margin. Same medium-asymmetry caveat as the bacterial pipeline and GENERALIZE4 (nutrient-rich
  media rescue biosynthetic essentials), only more extreme because the GEM default medium is very permissive.
- Recall is tiny (0.025): the 230 experimentally-essential metabolic genes the FBA misses are largely
  biosynthetic genes rescued by the rich medium, plus essential genes outside metabolism.
- **Not re-tuned:** the gate was frozen before scoring; the sparse-essential outcome is reported as-is, not
  re-run under a leaner medium to inflate recall.
- Scope: essentiality-ENRICHMENT only; in-silico FBA vs a curated published essentiality resource (not wet-lab);
  curated model is still a model; recall bounded by the metabolic subproteome; non-annotated genes treated as
  non-essential (absence of evidence).

## Secondary organism (*S. pombe*) — honest boundary, NOT run
A clean *S. pombe* essentiality label is local (DEG2009, 1260 genes), but no openly-downloadable curated
*S. pombe* GEM usable for gene-deletion FBA CPU-only was found: SpoMBEL1693 (MODEL1507180061) carries no
machine-readable GPRs (cobra parses 0 genes); Pitkanen-2014 CoReCo (MODEL1302010035) parses 0 genes / no
objective; Lu-2021 (MODEL2109240001) has 874 genes but opaque `...@Seq_N` IDs with no clean bridge to the
DEG2009 namespace. Rather than fabricate a mapping, this is reported as the boundary; the higher-value
real-pathogen result (*C. albicans*) is delivered instead.

## Bottom line
FBA gene-essentiality enrichment now holds across bacteria (6-organism cross-Gram/phylum panel + blind
*N. gonorrhoeae*), a model eukaryote (*S. cerevisiae*, GENERALIZE4), **and a real fungal pathogen
(*C. albicans*, HARDENF1)** — eukaryote->FBA is n>1 and includes a clinical pathogen. The signal is genuine and
highly precise, but low-recall under the model's rich default medium; honest and disclosed.
