# COMPOSITE4 — Expanded-arm router integration + reproducibility drift fix — SUMMARY

**Verdict: PASS** (integration only, no new science). Reproduced x2 byte-identical, payload
sha256 `7911ba05c1e9bb966167ed99f10702e7ec5061324adbfbb1d1444058d3b6312a`. Full pytest suite: **93 passed**
(71 prior + 22 new COMPOSITE4 tests). This is the integration prerequisite for CAPSTONE2.

## What this is
An ADDITIVE wiring of the already-validated expanded arms into the committed composite router
(`src/intercepta/composite_router.py` + `src/intercepta/class_detector.py`), plus a fix for the
router-drift hygiene finding. It adds NO new science — the new classes fire at exactly the confidence
their validation arm earned, and every existing routing VERDICT is unchanged.

## The four additions

### 1. Two new human disease CLASSES (target-ID routing)
- **`HUMAN_MONOGENIC`** — the causal gene is genetically GIVEN (target-ID trivial). Fires
  `Signal.CAUSAL_GENE` (MENDEL1), routes to intervention-**MODE** reasoning (`output_type="mode"`), NOT
  capped. Requires a declared `causal_gene_known` descriptor; abstains without it.
- **`HUMAN_COMPLEX_DISEASE`** — fires `Signal.GENETIC_ASSOCIATION` (GENETICS1) at **CAPPED/uncertain**
  confidence (`confidence_cap=0.5`) with the verbatim note *"popularity-adjusted effect bounded
  [1.67,2.26]; target-relevance only, cross-sectional"*. Reuses the existing COMPOSITE3 capped/uncertain
  machinery. Requires a declared `has_gwas_evidence` descriptor; abstains without it.
- **`HUMAN_CANCER` unchanged** (functional_dependency).

### 2. A cross-class, fail-safe INTERVENTION STAGE (post-target)
`RoutingDecision.intervention = {recommended_modality_class, feasible_set, fail_safe: true, note}`,
driven by a faithful port of **MODALITY1's** validated mechanism x localization x druggability
recommender + frozen feasibility matrix. HARD FAIL-SAFE inherited: the recommended modality is ALWAYS a
member of the computed `feasible_set` (or `ABSTAIN`); an infeasible modality is never emitted (incl. no
ERT-across-the-BBB). ABSTAINS when mechanism/localization features are absent. Orthogonal STAGE — it does
NOT change class->target-ID routing.

### 3. class_detector rules for the new human classes
`R2` now splits a human proteome by DECLARED descriptor: `has_dependency_screen` -> CANCER (unchanged,
now `R2a`), `causal_gene_known` -> MONOGENIC (`R2c`), `has_gwas_evidence` -> COMPLEX (`R2d`); **>1
descriptor -> AMBIGUOUS -> ABSTAIN** (`R2e`, never guess among the three); 0 descriptors -> ABSTAIN
(backward-compatible `requires_descriptor="has_dependency_screen"`).

### 4. The reproducibility drift FIX
`RoutingDecision.verdict_skeleton()` emits ONLY the stable decision essentials — `biology_class`,
sorted `signals_fired`, `abstain` (bool), `capped` (bool), `recommended_modality_class` — with NO
reason-prose and NO evidence strings. The COMPOSITE4 payload (and future capstones) hash the skeleton, so
the decision reproduces byte-identical even as router prose evolves. Demonstrated stable under arbitrary
prose mutation.

## Pre-registered validation results
- **(a) REGRESSION / drift-fix:** all 6 committed CAPSTONE1 cases reproduce their EXACT verdict skeleton
  through the new router (6/6 identical); the committed **CAPSTONE1 artifact still reproduces byte-identical
  (sha 19a72135)** — no existing verdict changed.
- **(b) NEW classes:** complex+GWAS -> `genetic_association` capped (0.5, attenuation note present),
  abstains without GWAS; monogenic+causal-gene -> `mode`, not capped, abstains without the gene.
- **(c) INTERVENTION fail-safe:** 0/11 infeasible recommendations; abstains when features absent.
- **(d) FAIL-SAFE abstentions preserved:** DARK1 proteome + novel zero-screen parasite (TRANSFER1) both
  abstain, 0 mis-fires (incl. no virus mis-call).

## Honest scope (binds every claim)
Integration of already-validated arms; no new science. New classes fire at the confidence their arm
earned: COMPLEX = capped/attenuated **target-RELEVANCE only** (Open Targets cross-sectional, bounded
[1.67,2.26]; not response/molecule/clinical); MONOGENIC = intervention-**MODE** triage (target given, not
a therapy). The intervention stage is **feasibility triage, not a molecule** — the small-molecule branch
still hits the affinity wall (AFFINITY1/HIT2). Pure decision logic; data-free; CPU-only; not wet-lab; not
clinical. If any existing verdict skeleton had changed, the run would FAIL rather than force it.

## LEDGER verdict (one line)
**COMPOSITE4 (PASS): additive router integration of the expanded human arms (HUMAN_MONOGENIC->mode/MENDEL1,
HUMAN_COMPLEX_DISEASE->genetic_association CAPPED/GENETICS1) + a MODALITY1-ported fail-safe intervention
stage (0/11 infeasible) + a `verdict_skeleton()` drift fix — every committed routing verdict UNCHANGED
(CAPSTONE1 still sha 19a72135), 93/93 tests pass, reproduced x2 byte-identical sha 7911ba05; integration
only, target-relevance/feasibility-triage not therapy.**
