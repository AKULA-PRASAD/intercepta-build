# HARDENP1 — pre-registered test: does FBA gene-essentiality FAIL on a SECOND host-dependent parasite (*Toxoplasma gondii*)?

**Registered (Stage 1) BEFORE computing the 2x2 contingency table, odds ratio, Fisher p, precision/recall or AUROC
against the GEM.** Data sources (GEM + CRISPR screen) were fetched and their FORMAT inspected (gene-ID namespaces,
score distribution, and — for threshold justification only — the screen authors' OWN control-gene scores) to design
the mapping and fix the essentiality cutoff. This is method design, not outcome: the ENRICHMENT ANSWER
(OR / p / contingency / precision / recall / AUROC vs the GEM's FBA calls) has NOT been looked at when this file is
written.

## Context / why this experiment
On ONE host-dependent parasite (*P. falciparum*, GENERALIZE5) FBA single-gene-deletion essentiality FAILED the
pre-registered OR>3 gate (OR **2.469**, Fisher p 2.2e-3, precision 0.80, recall 0.20, n=424 mapped), and neither
expression-context (HOSTCTX1 E-Flux, byte-identical no-move) nor host-medium curation (HOSTCTX2, OR stayed ~2.2–2.4)
rescued it. Unified conclusion so far: "metabolic essentiality is the wrong signal for host-embedded biology" — but
that is **n=1**. This experiment HARDENS it: run the SAME validation on a SECOND host-dependent apicomplexan.

## Hypothesis (frozen)
H = FBA single-gene-deletion essentiality computed on a curated *Toxoplasma gondii* genome-scale metabolic model is
tested for enrichment against the parasite's genome-wide CRISPR fitness screen (Sidik et al. 2016 *Cell*). It will
either **FAIL the OR>3 gate again** (hardening "FBA fails on host-embedded biology" to n>1) OR **PASS** (which would
COMPLICATE the parasite conclusion). Reported honestly either way. Same method/gate as GENERALIZE5 and every prior
organism.

## Materials (fixed now)
- **GEM (curated, published):** **iTgo2020** — *T. gondii* genome-scale metabolic model from Krishnan et al. 2020,
  "Functional and Computational Genomics Reveal Unprecedented Flexibility in Stage-Specific *Toxoplasma* Metabolism,"
  *Cell Host & Microbe* 27(2):290-306 (DOI 10.1016/j.chom.2020.01.002). File `iTgo2020_krishnan.mat` obtained from the
  PARADIGM database (Carey et al.; `github.com/maureencarey/paradigm`, `models/published/iTgo2020_krishnan.mat`) — the
  SAME database family that supplied GENERALIZE5's iPfal19. **556 genes, 2067 reactions, 1867 metabolites.** Gene IDs
  are ToxoDB `TGME49_` locus tags. Objective `Biomass_c`; default-medium WT growth = 2.8847 (grows). SHA-256
  `071b5055b427c36b6a5e8bbc4fcdf2828b66f32aba0821177a8117df075c3423`.
  - NOTE on secondary candidates (rejected, documented for honesty): PARADIGM's auto-reconstructed
    `final_TgondiiGT1.xml` / `final_TgondiiME49.xml` FAIL cobrapy SBML validation (cannot load); the
    `tg_tymoshenko2015.xml` published model has **0 gene-reaction rules** (unusable for gene-deletion essentiality).
    iTgo2020 is the only curated, gene-annotated, loadable T. gondii GEM obtained CPU-only/open.
- **Experimental essentiality (ground truth):** **Sidik et al. 2016 *Cell*** 167:1423, "A Genome-wide CRISPR Screen in
  *Toxoplasma* Identifies Essential Apicomplexan Genes" (DOI 10.1016/j.cell.2016.08.019; PMID 27594426). Per-gene
  **mean phenotype score** across 4 biological replicates, from Supplementary `mmc3.xlsx` sheet "Phenotype" (8158
  genes; 8151 with a numeric score). Downloaded from the open Elsevier CDN
  (`ars.els-cdn.com/content/image/1-s2.0-S0092867416310704-mmc3.xlsx`). Gene IDs are ToxoDB `TGGT1_` locus tags.
  Extracted to `sidik2016_phenotype.csv` (SHA-256 `f327bfc6...`); raw xlsx retained (SHA-256 `f3250daf...`). More
  negative phenotype = stronger fitness contribution (= more essential).
- **Gene-ID mapping:** GEM `TGME49_NNNNNN` ↔ screen `TGGT1_NNNNNN`. ToxoDB assigns orthologous genes across the ME49
  and GT1 strains the **same numeric locus suffix**, so the map is: strip the strain prefix, match on the 6-digit
  numeric. Coverage inspected at design time = **550/556 (98.9%)** of GEM genes map to a scored Sidik gene (a clean
  map, so this will be a real effect-size result, not an INCONCLUSIVE namespace artifact). Genes not mapping to a
  scored Sidik entry are excluded from the 2x2 (never forced).

## Essentiality definitions (fixed now)
- **FBA-essential (predicted):** COBRApy `single_gene_deletion`; a gene is essential if KO growth < 1% of WT
  (`< 0.01 * WT`). KO growth rounded to 6 decimals to remove GLPK degenerate-optimum jitter (byte-identical
  reproduction). IDENTICAL to GENERALIZE5 / the bacterial pipeline.
- **Experimentally essential (ground truth), PRIMARY:** Sidik **mean phenotype score < -2.0**. This is the
  field-standard Sidik cutoff for "fitness-conferring." It is a threshold I do NOT tune on the GEM: it is validated
  on the screen authors' OWN control panel (Table S1) — at cutoff -2 it correctly classifies **40/40 dispensable
  controls** (all score ≥ -2; dispensable mean +0.63) and **36/40 essential controls** (score < -2; essential mean
  -3.55), cleanly separating the two control populations. Genes with no Sidik score are excluded from the 2x2.
- **SENSITIVITY (secondary, reported, not the gate):** stricter cutoff **< -3.0** and looser **< -1.5**, to show the
  verdict is not an artifact of the exact cutoff.

## Pre-registered decision gate (fixed now)
2x2 Fisher exact (one-sided, `alternative="greater"`) over the mapped metabolic genes: FBA-essential vs
experimentally-essential. **PASS iff odds ratio > 3 AND Fisher p < 0.01.** Same gate as every prior organism.
Also report precision, recall, AUROC (−KO-growth vs experimental label), full contingency, n mapped.

- **Odds-ratio / p estimator (frozen for comparability):** OR = sample odds ratio `(a*d)/(b*c)`; p = one-sided
  hypergeometric (Fisher "greater") via `math.comb`. This is EXACTLY the estimator GENERALIZE5 used (its metabolic
  env had no scipy). The metabolic env now contains scipy 1.17.1, but scipy's `fisher_exact` returns the *conditional
  MLE* odds ratio, which differs from the sample OR; to keep the head-to-head comparison with Plasmodium's OR 2.469
  apples-to-apples I deliberately use the identical sample-OR + math.comb estimator, not scipy.

- **PASS** ⇒ FBA-essentiality DOES transfer to this second parasite → COMPLICATES the "FBA fails on host-embedded
  biology" story; reported honestly (Plasmodium may be the outlier, not the rule).
- **FAIL** ⇒ hardens the boundary to n>1 (a SECOND host-dependent-parasite FBA failure). A first-class VALUABLE
  negative, recorded, never re-run to a nicer number.
- **INCONCLUSIVE** ⇒ only if the ID map had collapsed (it did not — 98.9%).

## Scope (fixed now)
Essentiality-enrichment only; in-silico FBA vs a published experimental CRISPR screen (not wet-lab we ran); a curated
model is still a model (medium/gap-fill assumptions); *T. gondii* is an obligate intracellular parasite (host-embedded,
salvages host nutrients) — the default-medium GEM may be over-permissive, the same honest deployment risk as
Plasmodium. Not drug-target/selectivity/clinical. Deterministic; reproduced x2 byte-identical (SHA-256 over sorted-key
metrics payload excluding verdict/provenance).
</content>
</invoke>
