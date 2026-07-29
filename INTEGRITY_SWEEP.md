# Integrity sweep — record of what was removed, flagged, and retained (2026-07-29)

A repo-wide sweep for false/overstated/fabricated content, done under `CONSTITUTION.md`. This file is the
transparent record: nothing is hidden — removals are listed here.

## Principle used (why not "delete every occurrence")
Terms like "de novo", "for ANY disease", "5/5 trials", "therapy selection" appear in 800+ places. **Most are
legitimate** and were RETAINED: literature notes describing *other papers'* methods, the LEDGER/READMEs
*refuting* the claims, quarantined founding docs (already banner-flagged), and the honest AML paper's
discussion. Deleting those would destroy real science and hide the audit trail. The sweep is therefore
**surgical**: remove genuinely fabricated artifacts, flag historical docs, preserve legitimate mentions.

## REMOVED — fabricated artifacts (hand-written/human-assigned content presented as computed pipeline output)
Ground truth: `docs/audits/VISION_AUDIT.txt` (its "9 FAKE CLAIMS"). These result files contained MoA / safety
profile / synthesis route / trial-design text that a human *wrote*, and Pareto dimension scores a human
*typed*, presented as pipeline output. Deleted (code that produced them is kept, and is flagged honestly in
`engine/scouts/README.md`):
- `results/pharma_deliverable_complete.json`, `results/pharma_deliverable_enza_alis.json`
- `results/INTERCEPTA_pharma_package.json`, `results/INTERCEPTA_FINAL_package.json`
- `results/INTERCEPTA_explanations.json` (hand-written MoA explanations)
- `results/pareto_ranking_mcrpc.json` (dimension scores typed by hand)
- `results/INTERCEPTA_FINAL_candidates.csv`, `_AUDIT_FIXED_candidates.csv`, `_STABILIZED_candidates.csv`,
  `_ranked_candidates.csv`, `_unified_candidates.csv` (outputs of the fabricated ranking chain)
- `results/round3_gbm/pharma_deliverable_gbm_v0.json` + `.md`, `docs/project/round3_gbm/results/pharma_deliverable_gbm_v0.md`
Previously (docs-import safety net) also auto-removed **8 build-log files** that contained BeatAML patient
sample IDs, and the unverifiable **KAALI conversation PDFs**.

## MISLABELED BUT REAL — kept, with honest name-caveats (see `results/README.md`)
Real computations whose *filenames* overclaim; renamed-in-spirit via README flags, not deleted:
- `*denovo*molecules*.csv` = **scaffold-hopped** analogues, NOT de novo generation.
- `phase1_5trial_VALIDATED.*` = the "5/5" claim is **retracted**; real result 2/6 (Cox PH).
- `lead_candidate_INTC002.json` = a **computational hypothesis** (ChEMBL novelty 0.266), not a validated drug.

## FLAGGED IN PLACE — historical/working docs (retained as record; LEDGER is authoritative)
`docs/status/` and `docs/project/` contain historical working docs that assert now-retracted claims
(5/5 trials, 6/6 scouts, 79% complete, de novo, universal, p38 MAPK). They are kept as the project's real
history but carry `_INTEGRITY_NOTICE.md` banners; where any conflicts with `LEDGER.md`, the ledger wins.
Founding maximalist docs are in `docs/aspirational_original/` (banner-tagged).

## RETAINED — legitimately (NOT false claims)
- `docs/project/research/literature/notes/*` — notes summarizing *cited* external papers.
- `LEDGER.md`, `VISION.md`, `README.md`, `engine/*/README.md`, `results/README.md`, `docs/audits/*` — these
  MENTION the claims specifically to refute/flag them. Correct and authoritative.

## The validated core that SURVIVES (the real science)
Everything above is the cleanup. What is actually validated (pre-registered, permutation-tested, replicated,
reproduced ×2) is in `LEDGER.md` (V1–V10), `experiments/` (B1–B4), and `verification/`:
V1 cross-dataset transfer ρ=+0.212; V4–V6 AML mutation→drug (NPM1→Cabo etc.); V9 drug-specific patient
transfer (replicated, robust); V10 mechanism+expression complementarity. Falsified/untested items are logged
as first-class negatives (N1, and the FALSIFIED/NOT-TESTABLE sections).
