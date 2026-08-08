# INTERCEPTA — Invention Roadmap (North Star), first-principles, honest (2026-08-07)

*Replaces the cancer-era `BREAKTHROUGH_ROADMAP.md`. Rule (per the founder's directive + Constitution): every step must be a
**genuine invention / new capability**, planned by deep research — NOT trial-and-error, NOT a rehash, NOT a faked solution. For
each frontier: what it is, why it matters, the **specific invention** required, and an honest **feasibility tier** —
INVENTABLE-NOW (real new capability we can build + validate CPU-only) · OPEN-PROBLEM (genuine unsolved science; attempt honestly,
never claim solved) · DATA/EXPERIMENT-GATED (no computation substitutes). No frontier is advanced by pretending.*

## What is already a genuine invention (built + validated — the assets we stand on)
- **The transfer-condition law + biology-class-aware composite router** (COMPOSITE1–3): a *new kind* of discovery system that
  fires only the signal whose biological invariant is conserved for the input, at calibrated/capped confidence, and **abstains**
  where none is — proven to fail *safe* at the dark-proteome edge (DARK1). This is a real, publishable novelty. Status: shipped.
- **Prospective-blind FBA-essentiality target-ID across all three domains of life** (BLIND1–7, 4 pass / 3 fail): the rare,
  gold-standard evidence that the mechanism *predicts, not postdicts* — with a mechanistically-explained transfer boundary.

## Frontier 1 — Eukaryote-robust essentiality transfer  ·  ✅ **BUILT + VALIDATED (2026-08-07)**
*Delivered: META1 diagnosed the OR>3 gate as base-rate-confounded (a fixed model flips PASS↔FAIL purely on screen base rate;
driver of transfer strength is GEM quality, ρ=+0.55). FAIRGATE1 then invented + validated the fix — a base-rate-fair gate on the
**risk ratio** (RR=precision/base_rate), proven base-rate-invariant (the flipping pair now gives a consistent verdict; simulation:
OR swings 15× across base rate, RR CV≈0). Shipped as `intercepta.metrics.fair_gate()` with a data-free invariance unit test.
Recommended gate for future prospective essentiality-transfer tests; supersedes raw OR>3. Honestly, the eukaryote signal is real
(K. phaffii fair-PASS, p 4×10⁻⁵) — the earlier "eukaryotes fail" reading was partly a gate artifact, now corrected.*

### (original problem statement, retained)
- *Problem (our own result):* strict-blind eukaryotes came sub-gate (fungus OR 2.4 but p≈4×10⁻⁵ real; kinetoplastid null) while
  prokaryotes + retrospective eukaryotes pass — an unexplained boundary.
- *Deep-analysis step (in progress):* **META1** quantifies whether the OR>3 gate is base-rate-confounded / driven by GEM coverage
  vs a true eukaryote weakness.
- *The invention (contingent on META1):* if base-rate confounding is confirmed → a **base-rate-robust transfer metric** (a fairer
  gate than raw OR, e.g. a base-rate-adjusted effect size or precision-at-fixed-recall) that correctly credits real-but-compressed
  signal; if GEM-compartmentalization is the driver → a **compartment-aware eukaryotic essentiality** step. Either is a real
  methodological invention, CPU-only, validated against the committed suite. *Execute after META1 lands — planned, not guessed.*

## Frontier 2 — Novel-target binding-affinity ranking (the molecule wall)  ·  **OPEN-PROBLEM (do NOT fake)**
- *Problem:* to go target→drug for the ~93% undrugged validated targets you must rank binding affinity for a target with zero
  activity data. We have *proven* the standard tools fail: docking ≈ random for potency (HIT2), proteochemometric transfer adds
  ~nothing (B49), active-learning on novel chemotypes is a null (B65), structural repurposing is promiscuity (STRUCTREPURPOSE1).
- *The invention required:* a genuine zero-shot affinity signal. Honest state of the art: co-folding models (AlphaFold3/Boltz-class)
  and ML interatomic potentials are the only credible candidates, but (a) most are not installable/runnable at zero budget CPU-only,
  and (b) none is prospectively validated for *ranking* novel-target affinity. **This is a real open problem in the field, not a
  bug we can patch.** Honest plan: (i) precisely specify the minimal experiment that WOULD test a candidate method if a runnable
  one becomes available; (ii) attempt only what can be rigorously validated CPU-only; (iii) **never present a pose-plausible
  hypothesis as a potency-ranked lead.** We advance this frontier by characterizing it exactly, not by claiming a solution.

## Frontier 3 — Function/druggability of a truly novel fold (dark proteome)  ·  **PARTIALLY INVENTABLE / OPEN**
- *Problem:* the vision's deepest case — a protein with no sequence/structure homolog. DARK1 proved the composite correctly
  *abstains* there (fails safe). The invention would be to say something *useful* rather than only abstain.
- *What is inventable now:* homology-free steps — ESMFold structure + fpocket pocket detection + a pLDDT-gated druggability read —
  can produce a *cautious* structural hypothesis without any analog. *What stays open:* inferring actual function/target-validity
  from a novel fold with no reference is genuinely unsolved. Honest plan: extend the composite with a homology-free structural
  module that emits a clearly-labeled low-confidence hypothesis, and keep abstaining on function — no overclaim.

## Frontier 4 — Real therapeutic validation (target→drug→cure)  ·  **DATA/EXPERIMENT-GATED**
- *Problem:* every ultimate claim is in-silico. Confirmation needs wet-lab (a CRISPRi knockdown of a nominated target) and,
  eventually, clinical data. No computation substitutes (proven: B10/B17/B20 clinical nulls; F0/F4).
- *Plan (the external channels):* the collaboration ask (`docs/EXPERIMENTAL_VALIDATION.md`) + the preprint are prepared; the
  invention here is *institutional* (a partner), not computational. State it as the strategic dependency it is; never fake across
  the line.

## The operating discipline (so no step is trial-and-error)
1. **Diagnose before inventing** (META1 before the eukaryote-metric invention). 2. **Pre-register the invention's success/failure
gate before running.** 3. **Reproduce ×2, control nulls/leakage, report negatives first-class.** 4. **Label each frontier's tier
honestly** — build where INVENTABLE-NOW, characterize where OPEN-PROBLEM, name the dependency where GATED. 5. **No false claim,
ever** — a hypothesis is labeled a hypothesis; an open problem is not dressed as solved. This is how "100% ready" and "always real
and scientific" hold together: ready to invent where invention is genuinely possible, honest where it requires new technology or
new data we do not yet have.

## REMAINING COMPUTATIONAL BUILD — execution backlog (2026-08-07; per the "compute-complete before external channels" directive)
*The full remaining computational surface toward the North Star, ordered by leverage × buildability, honestly tiered. External
channels (publication/collaboration) are deferred until this is built out. Each BUILDABLE item is a genuine invention with a
pre-registered validation; a rigorous NEGATIVE is a first-class result, not a failure.*

**Wave A — in flight (launched 2026-08-07):**
- **NONMET1 · BUILDABLE-NOW · the single biggest gap on the validated spine.** FBA covers only ~half of drug targets; the
  **non-metabolic essential half** (proteases, polymerases, ribosomal/structural — exactly what a novel pandemic presents) has
  **no honest mechanistic signal** since MET4 (PPI-centrality) died of study bias and the coexpression control collapsed the lift.
  New, study-bias-*resistant* hypothesis to test: **essentiality is encoded in conserved genomic context** (synteny / conserved
  gene-neighborhoods with known essentials) — homology-adjacent but neighborhood-based, so immune to literature study-bias.
  Pre-registered gate: does it add beyond the conservation null on the *non-metabolic* subproteome vs experimental essentiality?
  PASS → a genuine ceiling-break for the FBA-blind half; FAIL → a first-class negative closing another door (as MET4 did).
- **ROUTERAUTO1 · BUILDABLE-NOW · completes limitation (12).** The router's class detector is currently minimal/hand-specified.
  Build + validate an **autonomous biology-class detector** (raw proteome + data descriptors → class → the empirically-correct
  signal), leave-one-out over all committed organisms, with fail-safe abstention preserved (must NOT confidently route the
  dark-proteome / novel-zero-screen cases). Honest scope: automates the routing + abstention that is currently hand-set; it does
  **not** claim to solve a-priori transfer prediction (COMPOSITE3 showed that is not a-priori decidable at n=2 — inherited as the
  capped/flagged uncertainty). Makes "any disease in → routed answer out" actually autonomous.

**Wave A+ — also in flight (launched 2026-08-07, alongside NONMET1/ROUTERAUTO1):**
- **MENDEL1 · BUILDABLE-NOW · new disease paradigm.** Human **monogenic/Mendelian** disease: the causal gene is genetically
  established, so the task is intervention-MODE reasoning (LoF→restore/potentiate vs GoF→inhibit/silence) + druggability triage +
  honest abstention where the answer is "not a small-molecule target." A *different* zero-data shape than cancer's
  popularity-confounded dependency.
- **AFFINITY1 · OPEN-PROBLEM, honest attempt · the intervention half.** Feasibility-first co-folding (Boltz/Chai) test of
  zero-shot novel-target affinity ranking, head-to-head vs the docking baseline. Three honest outcomes: crack / bound-negative /
  CPU-infeasible-with-GPU-spec. Not faking — attempting the wall, reporting evidence.

**Wave B — next (BUILDABLE, queued behind the current wave's quality gate):**
- **GENETICS1 · the missing human-disease arm (found by the 2026-08-07 first-principles re-derivation).** The three human
  disease paradigms are somatic **cancer** (DEPEND1, built), germline **monogenic** (MENDEL1, in flight) — and the largest,
  **common/complex/polygenic** disease, which we do NOT cover. Human **genetics** (GWAS→gene via L2G/colocalization, Open
  Targets Genetics) is a real target-ID signal that **sidesteps the popularity-confound** that sank generic human target-ID
  (DEPEND1/F3CLIN1), because genetic causality is not research-attention-inferred. Pre-registered validation: are
  genetically-supported targets enriched for approved-drug targets (the Nelson-2015 ~2× effect), and does it beat a
  study-bias/popularity null? PASS = the third human arm; NEGATIVE = an honest bound. Completes human-disease coverage
  (cancer + Mendelian + complex).
- **Other new-class COVERAGE:** **helminths**, **antimicrobial-resistance genes as targets** — each a new validated router arm
  vs known drugged targets in that class.
- **GEM-quality lift for eukaryotes** — META1's driver #1 is model quality; a curated-GEM ingestion path could move the blind
  eukaryote fails (K. phaffii) above a fair gate. BUILDABLE (data-integration), incremental.

**Deeper frontiers surfaced by the re-derivation (honestly tiered — do not fake):**
- **Disease-mechanism inference from PHENOTYPE alone** (no causal gene given — the deepest "any disease" case): largely
  OPEN/SEMI-OPEN. Tractable sub-piece = phenotype/HPO → candidate-gene via known gene-phenotype maps (a lookup+ranking, honest);
  true de-novo mechanism inference from a phenotype with no prior is OPEN — characterize, don't fake.
- **Modality selection** (small molecule vs biologic vs ASO vs gene therapy vs enzyme replacement): MENDEL1 builds the
  intervention-mode seed; generalizing it into a validated modality-recommender is a real BUILDABLE Wave-C capability
  (validatable against approved-drug modalities per target class).

**OPEN-PROBLEM (attempt only what is rigorously validatable CPU-only; never fake):** Frontier 2 novel-target affinity ranking
(HIT2/B49/B65 nulls stand); Frontier 3 dark-fold *function* (apo-pocket druggability already ≈ random per FRONT2 — so a dark
structural module would largely re-derive that negative; deprioritized); binding-site-level true selectivity (FRONT2: resource-gated).

**GATED (not computational — deferred, already staged):** wet-lab validation (CRISPRIDESIGN1 turnkey), clinical.

## DEFINITION OF DONE — "total computational build of the fullest vision" (the finish line)
*Per the compute-complete-before-external-channels directive, this makes the goal MEASURABLE — we move to publication/collaboration
when the computational build meets these criteria, not before, and not endlessly. A criterion is met when it is BUILT+validated,
or its wall is HONESTLY CHARACTERIZED (an open frontier precisely bounded, never silently missing). GATED/OPEN-by-nature items
(novel-molecule affinity, wet-lab, clinical) are explicitly NOT part of "compute complete" — they require GPU/lab/patients.*

**A. Disease-class coverage (target-ID validated, or honest abstention):**
- [x] Bacteria (multi-phyla) · [x] Archaea (BLIND6) · [x] Fungi/free eukaryotes (bounded) · [x] Viruses (structural class-ID)
- [~] Host-dependent parasites (GEM/base-rate-bounded, characterized) · [x] Human somatic cancer (dependency)
- [x] Human germline monogenic (MENDEL1) · [⧗] Human complex/polygenic (GENETICS1 — in flight)
- [ ] Helminths (low-priority coverage) · [○] Non-genetic / phenotype-only disease (OPEN — only the lookup sub-piece is honest)

**B. Intervention half (target → therapy):**
- [x] Repurposing target→existing drug (INTERVENE1/2, honest narrow ceiling) · [x] ADMET + synthesizability (B30/B31)
- [x] Combinations/synergy, calibrated (B24–29) · [~] Intervention-mode (MENDEL1) + [⧗] modality recommender (MODALITY1 — in flight)
- [○] Novel-molecule affinity for a novel target — OPEN/GPU-gated (AFFINITY1 characterized + GPU spec) — NOT required for compute-complete

**C. Integration & governance:**
- [x] Composite router + transfer-condition gating + abstention · [x] Autonomous class detection (ROUTERAUTO1)
- [ ] End-to-end integration of the EXPANDED arm set on a held-out novel case (CAPSTONE2 — gated on GENETICS1+MODALITY1)

**D. Honest bounds characterized (not faked):**
- [x] Conservation ceiling (TID1–4) · [x] Non-metabolic mechanism door closed (MET4, NONMET1) · [x] Affinity wall (HIT2/B49/B65/AFFINITY1)
- [x] Selectivity resource-gated (FRONT2) · [x] Clinical/response tested-negative (B10/B20) · [x] Dependency non-transfer (TRANSFER1)

**COMPUTE-COMPLETE when:** A (all reachable classes covered-or-abstaining; OPEN ones characterized), B (built-or-bounded; affinity
GPU-specced), C (router autonomous + CAPSTONE2 done), D (every wall characterized). **Remaining to finish line:** GENETICS1 +
MODALITY1 (in flight) → CAPSTONE2 integration → optional helminth/AMR/GEM-lift coverage → then, and only then, external channels.
Honest estimate: the finish line is CLOSE (the two in-flight arms + one integration capstone are the critical path); the OPEN/GATED
items (affinity, phenotype-only, wet-lab, clinical) are correctly OUT of scope for "computational build complete."
