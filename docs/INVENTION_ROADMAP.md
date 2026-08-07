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

## Frontier 1 — Eukaryote-robust essentiality transfer  ·  **INVENTABLE-NOW**
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
