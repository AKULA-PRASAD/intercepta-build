# ROUTERAUTO1 — autonomous biology-class detector for the composite router (completes limitation 12)

**Verdict: PASS (reproduced x2 byte-identical, payload sha256 `29fff6cf…`).** The composite router no longer
needs its biology class hand-specified: an autonomous, zero-fitted-parameter detector classifies a raw input
from objective proteome features + data descriptors, and the UNCHANGED COMPOSITE1/2/3 transfer-gate fires
exactly the validated signal for that class or abstains.

## What was built
- `src/intercepta/class_detector.py` — the pure, data-free detector: `ProteomeFeatures` (objective, each with
  a cited computation method) + a pre-registered ordered rule engine → `DetectionResult`. Zero fitted
  parameters; every threshold is stated in `PREREG.md` before scoring.
- `src/intercepta/composite_router.py` — added `CompositeRouter.decide_auto(organism, features)` (auto-detect
  then apply the unchanged gate), a `detection` audit trace on `RoutingDecision`, and — additively — the
  **ARCHAEON** class in the FBA/conservation full-grade domain (evidence: BLIND6 *M. maripaludis* curated
  iMR539, prospective-blind git-committed-before-reveal, FBA PASS OR 4.23). No prior committed verdict changes.
- Tests: `tests/test_class_detector.py` (21 data-free unit tests, in the default suite).

## Detection rules (pre-registered; first match wins)
R0 declared-class-wins · R1 VIRUS = tiny **AND** acellular **AND** viral hallmark (*tiny-alone is not enough —
the fix for the minimal detector's `size<=60 => virus` bug that would mis-fire on dark proteins*) · R2
HUMAN_CANCER = human proteome **AND** dependency screen (R2b: human, no screen -> abstain) · R3 cellular ->
bacteria/archaea/eukaryota; eukaryote host-dependence undeclared -> abstain (not sequence-derivable) · R4
dark/unsupported -> abstain.

## Leave-one-out routing result (21 committed inputs; LOO == full eval, detector is unfitted)
- **G-CLEAR: 19/19** clear inputs routed to the empirically-correct class + fire/abstain.
  - bacteria 6/6, archaeon 1/1, free-eukaryote 3/3, virus 5/5, human-cancer 1/1, host-dependent parasite 3/3.
  - Host-dependent parasites: Toxoplasma & Plasmodium (curated GEM) -> FBA **capped + uncertainty-flagged**
    (COMPOSITE3; correct even for Plasmodium's a-posteriori fail — the router cannot know a-priori); *T.
    brucei* (only a sparse de-novo carve, **no curated GEM**) -> **ABSTAIN** (the genuine-null reach-limit).
- **G-FAILSAFE (hard): 2/2** — the DARK proteome (DARK1) and the novel zero-screen parasite (TRANSFER1) both
  **abstain with zero signals fired; zero mis-fires.** The dark set is NOT mis-detected as a virus.
- **G-NOREG:** full suite green — `tests/` 71 passed (50 prior + 21 new); committed router suite 17 passed;
  combined **88 passed**. No committed routing verdict changed.

## Honest boundaries (integrity over coverage — reported, not hidden)
The detector ABSTAINS rather than guess on: free-living-vs-host-dependent eukaryote without the declared
`host_dependent` flag; a human proteome without a dependency screen; a cellular input with an unresolved
domain-of-life marker; any input with no positive class marker (dark). Host-dependence and screen availability
are honest inputs, not sequence-derived guesses.

## Scope
Automates class-detection + routing only. It does **not** predict a-priori whether a signal will transfer for a
novel organism — that remains the capped/flagged COMPOSITE3 uncertainty. Outputs are confidence-tiered
candidate hypotheses with provenance, not validated drug targets, not wet-lab, not clinical.

## LEDGER verdict (one line)
`ROUTERAUTO1 (completes limitation 12: autonomous biology-class detector front-ends the router) — PASS,
reproduced x2 byte-identical (sha 29fff6cf): zero-fitted-parameter objective-feature detector routes 19/19
committed clear inputs to the empirically-correct class + fire/abstain and 2/2 fail-safe inputs (DARK proteome,
novel zero-screen parasite) ABSTAIN with zero mis-fires; ARCHAEON added full-grade (BLIND6); no committed
verdict changed; full suite 88 passed.`
