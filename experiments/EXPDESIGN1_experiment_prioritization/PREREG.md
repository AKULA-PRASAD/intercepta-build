# EXPDESIGN1 — pre-registration (frozen before results)

**Domain:** experiment design / active learning (Phase-1 audit: ~8% built — a genuine gap). **No external fetch** —
reuses the cached E. coli pool from NONMET1 (`$INTERCEPTA_DATA/nonmet1` orthology/conservation + `expval/PECData.dat`
PEC essentiality + `met2` GEM membership). CPU-trivial, deterministic (no RNG except a fixed seed for the random baseline).

## The question (the program's real lever: scarce wet-lab experiments)
Given the zero-data engine's target nominations and a *tiny* experiment budget (CRISPRIDESIGN1 reality: ~$300/target),
**which targets should a lab test first to validate the most real essential targets per experiment — and does an
uncertainty/VOI-aware policy beat naive selection?** This turns the validated target-ID score into an *experiment
prioritization* — the computational bridge to Phase-2 that optimizes the scarce resource, without doing any wet-lab.

## Setup
- **Pool:** all E. coli genes with a PEC experimental-essentiality label; zero-data priority score = **conservation
  breadth** (`own`, the manuscript's validated workhorse, AUROC≈0.73 for essentiality), plus features {conservation,
  genomic-context, is-metabolic} for the learning arm. Outcome y = PEC essential (0/1).
- **Policies (select B genes, "reveal" y):** (1) RANDOM (fixed seed), (2) GREEDY on the zero-data score (exploit),
  (3) UNCERTAINTY-sampling (logistic prob nearest 0.5; explore), (4) VOI-HYBRID (exploit early for validation, then
  uncertainty for learning — a budget-split policy).

## Pre-registered gates (fixed before scoring)
- **G1 (headline — validation efficiency):** GREEDY (zero-data score) finds true essentials in the first B=30 experiments
  at **≥2× the rate of RANDOM**, hypergeometric **p<0.01**. Report the concrete **"experiments saved"** (how many random
  experiments to validate the same number of true targets greedy validates). PASS ⇒ the engine's zero-data ranking is a
  *validated* experiment prioritizer with a quantified wet-lab efficiency gain.
- **G2 (honest characterization — the validate-vs-learn tradeoff):** does UNCERTAINTY-sampling improve held-out predictive
  AUROC faster than GREEDY (expected), while GREEDY wins for *validation recovery* (expected)? Report both curves; this is
  characterization, not pass/fail. VOI-HYBRID is scored on a combined objective (essentials-found + final AUROC).
- **NEGATIVE (first-class):** if GREEDY does NOT beat RANDOM (G1 fails), that contradicts the conservation-AUROC result
  and is reported honestly as a null.

## Reproduction
Deterministic; payload = SHA-256 over sorted-key metrics (essentials@B, enrichment, hypergeom p, experiments-saved,
per-strategy learning AUROC curve, VOI-hybrid combined score); run twice, assert byte-identical.

## Scope
Retrospective simulation on ONE organism's cached pool (E. coli/PEC); "experiment outcome" = the existing PEC label, not a
new wet-lab result. It validates the *prioritization policy*, not a target. In-silico; a decision-support layer over the
validated engine, not a discovery. Frozen before running.
