# COMPOSITE4 — Pre-registration (frozen BEFORE coding/scoring)

**Type:** INTEGRATION (no new science). Additively wire the already-validated expanded arms
(GENETICS1, MENDEL1, MODALITY1) into the committed composite router, and FIX the reproducibility
drift the LEDGER hygiene note flagged (2026-08-07). This is the integration prerequisite for CAPSTONE2.

**Non-negotiables (constitution):** additive only; MUST NOT change any committed routing VERDICT
(fire/abstain decision) for existing classes; full existing pytest suite (71) must still pass; zero
budget / CPU-only; no git commit; no data commit. If any existing verdict skeleton would change, STOP.

---

## What is being added (the four items)

### 1. New disease CLASSES + signals (target-ID routing)
- `BiologyClass.HUMAN_MONOGENIC` — causal gene is GIVEN (target-ID trivial) -> route to intervention-MODE
  reasoning (MENDEL1). Fires a new `Signal.CAUSAL_GENE`. Requires a declared `causal_gene_known`
  descriptor. Output type `"mode"`. NOT capped (MENDEL1 PASS: 3-class mode accuracy 0.857, hard fail-safe
  0/10). Honest bound: target-ID is trivial/given; the deliverable is intervention-MODE triage, NOT therapy.
- `BiologyClass.HUMAN_COMPLEX_DISEASE` — fires a new `Signal.GENETIC_ASSOCIATION` (GENETICS1:
  popularity-controlled GWAS->target). Requires a declared `has_gwas_evidence` descriptor. Fires
  **CAPPED / uncertainty-flagged** (confidence_cap 0.5) with the verbatim note:
  "popularity-adjusted effect bounded [1.67,2.26]; target-relevance only, cross-sectional". Uses the
  EXISTING COMPOSITE3 capped/uncertain machinery (uncertain_domain + uncertain_requires + confidence_cap).
- `HUMAN_CANCER` stays UNCHANGED (functional_dependency).

### 2. New INTERVENTION STAGE (post-target, cross-class), driven by MODALITY1
- Add `RoutingDecision.intervention` = {recommended_modality_class, feasible_set, fail_safe: true, note}.
- A pure `recommend_intervention(...)` function ports MODALITY1's VALIDATED mechanism x localization x
  druggability recommender + frozen feasibility matrix (MODALITY1 run.py, sha 57b85479).
- HARD FAIL-SAFE inherited: the recommended modality is ALWAYS a member of the computed feasible_set
  (or ABSTAIN); an infeasible modality is NEVER recommended.
- When objective features (mechanism/localization/protein_class) are absent -> ABSTAIN.
- Honest bound: feasibility TRIAGE, not a molecule; the SM branch still hits the affinity wall.
- Orthogonal STAGE: it does NOT gate class->target-ID routing and does not change any fired signal.

### 3. class_detector rules for the two new human classes (objective + declared descriptors only)
- human proteome + `has_gwas_evidence` -> COMPLEX
- human proteome + `causal_gene_known` -> MONOGENIC
- human proteome + `has_dependency_screen` -> CANCER (unchanged)
- human proteome with >1 of those descriptors -> AMBIGUOUS -> ABSTAIN (never guess among the three)
- human proteome with 0 of those descriptors -> ABSTAIN (require a descriptor; backward-compat: the
  existing committed test expects requires_descriptor == "has_dependency_screen", preserved literally;
  reasons enumerate all three human descriptors)

### 4. FIX the reproducibility drift
- Add `RoutingDecision.verdict_skeleton()` emitting ONLY stable decision essentials:
  `{biology_class, signals_fired(sorted), abstain(bool), capped(bool), recommended_modality_class}`.
  NO reason-prose, NO evidence strings, NO gated-signal reasons.
- The COMPOSITE4 payload hashes ONLY verdict skeletons -> byte-identical even as prose/evidence evolve.
- Demonstrate: skeleton is stable while `abstention`/gated `reason` prose is mutated.

---

## Pre-registered validation (frozen expectations)

Regression is anchored to the committed CAPSTONE1 artifact (sha 19a72135). Committed per-case verdicts:

| case | class | fired signals | abstain | uncertain(capped) |
|---|---|---|---|---|
| bacterium (K. pneumoniae, GEM) | bacterium | conservation_breadth, fba_essentiality, structural_homology | no | no |
| fungus (C. albicans, GEM) | free_eukaryote | conservation_breadth, fba_essentiality | no | no |
| virus (SARS-CoV-2) | virus | structural_homology | no | no |
| human cancer (skin) | human_cancer | functional_dependency | no | no |
| host-dep parasite w/ GEM (Toxo) | host_dependent_parasite | fba_essentiality | no | YES (0.5) |
| novel zero-screen parasite, no GEM | host_dependent_parasite | (none) | YES | no |

**(a) REGRESSION / drift-fix:** re-run every committed case (the 6 above) through the NEW router;
assert each verdict_skeleton is byte-identical to a frozen expected skeleton AND that fired-signal /
abstain / capped match the committed CAPSTONE1 metrics. Expected: 6/6 identical.
Also assert `recommended_modality_class == "ABSTAIN"` for all six (no intervention features supplied) —
stable, so the skeleton is reproducible.

**(b) NEW classes route correctly:**
- HUMAN_COMPLEX_DISEASE + has_gwas_evidence -> fires `genetic_association`, `uncertain=True`,
  `confidence_cap==0.5`, note contains "popularity-adjusted effect bounded [1.67,2.26]" and
  "target-relevance only". Without has_gwas_evidence -> ABSTAIN.
- HUMAN_MONOGENIC + causal_gene_known -> fires `causal_gene`, output_type `"mode"`, NOT capped.
  Without causal_gene_known -> ABSTAIN.

**(c) INTERVENTION stage fail-safe:** over a pre-registered feature test set (MODALITY1-style tuples),
0 infeasible recommendations (recommended always in feasible_set or ABSTAIN); ABSTAIN when features absent.

**(d) FAIL-SAFE abstentions PRESERVED:** DARK proteome (DARK1) and novel zero-screen parasite (TRANSFER1)
still ABSTAIN with 0 signals fired, never mis-fire (incl. never a virus mis-call).

**Reproduce x2:** COMPOSITE4 payload (verdict skeletons + fail-safe counts + new-class skeletons, sorted
keys, excluding provenance/timestamps) sha256 must be byte-identical across two independent runs.

**Unit tests:** added to tests/test_composite4_integration.py covering (a)-(d) + verdict_skeleton
stability-under-prose-mutation. FULL pytest suite must pass (>= 71 + new).

## Honest scope (binds every claim)
Integration of already-validated arms. New classes fire at the confidence their arm earned:
COMPLEX = capped/attenuated (target-relevance only, cross-sectional; bounded [1.67,2.26]);
MONOGENIC = mode-triage (target given). Neither is therapy. The intervention stage is feasibility
triage, not a molecule (SM branch still hits the affinity wall). No new science.
