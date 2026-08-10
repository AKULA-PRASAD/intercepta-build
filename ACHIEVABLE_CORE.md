# ACHIEVABLE_CORE.md — the banked computational contribution (roadmap R4)

*The one thing the program has that is computationally achievable TODAY on public data, hardened and
reproducible. Everything beyond it is data-/wet-lab-gated (`COMPUTATIONAL_STATE_OF_THE_PROGRAM.md`,
`COMPUTATIONAL_DEAD_ENDS.md`). Last verified 2026-08-10: package imports, **94/94 tests pass**, `CAPSTONE2`
end-to-end reproduces (G1–G3 PASS + correct abstention).*

## What it is
A **transfer-condition-gated, abstaining, base-rate-fair, host-safe zero-data TARGET-IDENTIFICATION engine**
(`src/intercepta/`: `composite_router`, `class_detector`, `engine`, `axes`, `metrics`; console script
`intercepta`, also `python -m intercepta`). It identifies candidate antimicrobial targets from genome/GEM +
transferable knowledge alone, and **abstains** where no validated signal applies.

## What it does (the pipeline)
`genome / GEM` → **FBA metabolic gene-essentiality** (the one signal that beats the conservation null) +
**conservation-breadth** (workhorse) + **host-non-homology safety filter** → **base-rate-fair (risk-ratio)
gate** (`FAIRGATE1`) decides whether the transfer-condition holds → **ranked, host-safe target shortlist +
calibrated confidence**, OR **ABSTAIN** where the invariant doesn't transfer (dark proteome, zero-screen
parasite, sparse GEM). Viruses (no metabolism) route to structural target-class ID.

## Validated evidence (cited; reproduced ×2)
- FBA-essentiality enriches for **experimental** knockout essentiality: OR **5–64** across 6 curated GEMs
  (`VALIDATE_essentiality`, `CROSSVAL`), incl. **held-out WHO priority pathogens** (K. pneumoniae OR 63 /
  prec 92%, A. baumannii OR 13, P. aeruginosa OR 23; `LEDGER:12,15`).
- **Analyst-blind (lock-before-reveal) 4/7** never-seen organisms across three domains of life pass, failures
  on mapped boundaries (`BLIND1–7`).
- Conservation-breadth ceiling **0.908**; base-rate-fair gate (`FAIRGATE1/META1`); host-safety (`FRONT1/E2E2`);
  end-to-end composition + abstention (`CAPSTONE2`); **94/94** unit tests.

## Honest limits (must ship with any use)
- **Enrichment, not a target list:** precision ~0.77 but **recall ~0.22**, continuous ranking AUROC **~0.63**
  (finds *some* real targets, misses most; `VALIDATE_essentiality`).
- **Metabolic-scoped:** the non-metabolic mechanism is CLOSED (conservation ceiling; `COMPUTATIONAL_DEAD_ENDS.md` D1).
- **Wet-lab-UNCONFIRMED:** zero targets validated in a living cell. The turnkey test is `CRISPRIDESIGN1` +
  `docs/OUTREACH_ANTIMICROBIAL.md` — the single highest-value external step.
- **Not** a drug, selectivity, durability (falsified, `COMPUTATIONAL_DEAD_ENDS.md` D9), or clinical claim.
- **"Any disease" = decision COVERAGE** (validated signal where the invariant holds; abstain elsewhere) —
  **not** a universal model.

## How to run / reproduce
`python -m intercepta …` (or the `intercepta` console script); `pytest tests/` (94 pass);
`python experiments/CAPSTONE2_expanded_integration/run.py` (end-to-end proof + abstention).

## Status
This is the **hardened, reproducible, honestly-scoped floor** of the program — the computationally-achievable
subset. Its forward growth is **data-asymptotic** (roadmap R3 expands coverage as public data lands) and its
real-world value is **wet-lab-gated** (one CRISPRi confirmation). No further compute is warranted on the
directions in `COMPUTATIONAL_DEAD_ENDS.md`.
