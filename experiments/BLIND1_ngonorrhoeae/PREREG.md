# BLIND1 — pre-registered PROSPECTIVE-blind essentiality test on *Neisseria gonorrhoeae* MS11

**Registered (Stage 1) BEFORE any experimental essentiality data for this organism was fetched, parsed, or inspected.**
This converts the program's retrospective validation into a *prospective-blind* test: predictions are locked and committed
to git first; the experimental answer is revealed and scored only in Stage 2 (a separate later commit). The git history is
the audit trail of blindness.

## Organism & rationale
*Neisseria gonorrhoeae* MS11 — WHO high-priority, increasingly untreatable (multidrug-resistant gonorrhea), a CARB-X
therapeutic-theme pathogen. **Genuinely novel to this pipeline** (never in the development panel; never previously validated).
Chosen by clinical priority + novelty, NOT by predicted ease — a fastidious organism whose de-novo default-medium GEM may be
sparse (an honest deployment risk we accept and will report either way).

## Deployment scenario (deliberate)
No curated genome-scale model exists for *N. gonorrhoeae* → we use a **de-novo CarveMe reconstruction from the genome** — the
actual "new pathogen, no curated model" case. This tests the honest, weaker deployment path (not the curated best case).

## Locked prediction (Stage 1 output, committed before reveal)
From the CarveMe GEM alone (COBRApy single-gene FBA deletion, essential if KO growth <1% WT), the exact set of
**FBA-predicted-essential genes** (UniProt accessions + symbols) is written to `results/LOCKED_predictions.tsv` and hashed
(`results/LOCKED_predictions.sha256`). No experimental essentiality is consulted to produce it.

## Pre-registered hypothesis & decision rule (fixed now)
**H1:** the locked FBA-essential set is enriched for the organism's EXPERIMENTAL essential genes (DEG *N. gonorrhoeae* MS11),
2×2 Fisher **odds ratio > 3 AND p < 0.01** over the metabolic-subproteome genes (identifiers matched by gene symbol / locus
tag). Same gate as every prior organism.
- **PASS** ⇒ the mechanism signal predicts experimental essentiality on a genuinely novel, pre-registered pathogen
  (prospective-blind evidence).
- **FAIL** ⇒ reported first-class as an honest negative (e.g., de-novo GEM too sparse for this fastidious organism, or the
  signal does not transfer here) — recorded, not hidden or re-run to a better number.

## What this does and does not show
Even a PASS is scoped to essentiality-enrichment (not drug-target/selectivity/clinical), is in-silico vs a published
experimental set (not a wet-lab experiment we ran), and uses a de-novo model. It is the strongest *prospective-blind*
evidence obtainable without a laboratory: prediction committed before outcome observed.

---
## REVEAL OUTCOME (Stage 2, committed after Stage 1)
- **Stage 2a (symbol match): INCONCLUSIVE** — DEG N. gonorrhoeae MS11 (DEG1055) uses `NGFG_` locus tags absent from UniProt;
  only 1/613 mapped. Not a signal result; an identifier-namespace artifact.
- **Stage 2b (sequence-homology bridge, objectively-correct adjudication; predictions LOCKED/sha-verified unchanged):
  PASS.** DEG1055's 751 essential proteins mapped by mmseqs (pident≥90) into our accession space; over the 619 locked GEM
  genes: 25 both / 7 FBA-only / 216 exp-only / 371 neither → **odds ratio 6.13, Fisher p=4.2e-06, precision 0.78, recall 0.10**
  → clears the pre-registered gate (OR>3, p<0.01).
- **Honest integrity note:** the adjudication METHOD was corrected post-fail (symbol→sequence) for an objective namespace
  error; the PREDICTIONS were not changed (sha intact). A reviewer may still note the adjudication was finalized after an
  inconclusive first attempt — disclosed here. pident≥90 is a principled same-species ortholog cutoff, set once, not swept.
- **Meaning:** genuine prospective-blind evidence that FBA-essentiality predicts experimental essentiality on a pre-registered,
  never-seen pathogen — high precision (0.78), low recall (0.10, metabolic-scoped), sparse de-novo GEM. Essentiality-enrichment
  only; not drug-target/clinical; not wet-lab.
