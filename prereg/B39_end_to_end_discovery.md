# Pre-registration — B39: end-to-end in-silico candidate discovery (assemble the validated modules into a working pipeline) (FINALIZED 2026-07-30, PRE-RESULT)

## Why (build the vision, positively)
The validated modules (design B33, synthesizability B31, ADMET/safety B30) have only been benchmarked in isolation.
The drug-discovery vision is about *producing candidate molecules*. B39 assembles the modules into an end-to-end
pipeline — generate → multi-objective optimize for developability AND predicted safety AND synthesizability → rank —
and asks the honest positive question: **does the assembled pipeline produce valid, novel, synthesizable,
predicted-safe candidate molecules, improving over the starting chemical population?** This is NOT the (already-
falsified) "whole>parts predictor" claim; it is the modules used for their *intended* purpose — as a generator +
filters.

## Method (deterministic, on open data)
- **Generator:** BRICS fragment recombination + goal-directed genetic algorithm (`intercepta.generate`,
  validated B33), seeded from ChEMBL, deterministic (seed=42).
- **Multi-objective developability+safety score F ∈ [0,1]** (all higher = better), the GA fitness:
  `F = QED · synth · safety`, where `synth = (10 − SAscore)/9` (B31 domain), and
  `safety = 1 − mean(P_tox)` over the B30 ADMET toxicity modules {herg, ames, dili} (predicted probability of the
  adverse class), each module fit on its own TDC data.
- **Output:** top-N candidates with full profiles (QED, SAscore, per-module tox probabilities, ADMET
  applicability-domain flag) — every candidate an explicit computational hypothesis.

## Baselines & metrics
- **Baselines:** the ChEMBL **seed population** F; a **single-objective (QED-only) GA** (to show the multi-objective
  matters and does not simply reward-hack).
- **Metrics:** validity (BRICS ⇒ 1.0 by construction), uniqueness, **novelty** (fraction of top candidates not in the
  ChEMBL seed set), and the composite F (best + mean) of the GA population vs baselines; plus the mean per-component
  (QED, synth, safety) of the top candidates.

## Hypotheses (assumed FALSE)
- **H1 (the pipeline works):** the multi-objective GA's final-population mean F and best F exceed the ChEMBL seed
  population, at validity 1.0 and high uniqueness/novelty — i.e. the assembled pipeline yields improved, novel,
  synthesizable, predicted-safe candidates.
- **H2 (multi-objective matters):** the multi-objective GA's candidates are more synthesizable AND lower predicted-tox
  than a QED-only GA's (the safety/synth objectives change the output, not just QED).
- **H0:** the GA does not beat the seed population on F → the assembled pipeline adds nothing.

## Honesty / scope (mandatory caveats)
- **Optimizing against predictors invites gaming.** The GA can find molecules the ADMET/synth models *call* good;
  the reported applicability-domain flags mark candidates where those calls are unreliable (out-of-domain). This is a
  computational prioritization demonstration, **not** validated safe/synthesizable molecules.
- Every candidate is a hypothesis over KNOWN chemistry (fragment recombination), NOT a validated or novel *drug*, and
  NOT a clinical/safety determination. No wet-lab, no claim of real efficacy.

## Ship
If H1 passes, ship `intercepta discover` — the assembled generate→screen→rank pipeline (CLI) — with the honest scope
banner above. This is the platform running end-to-end, honestly bounded.

## Reproducibility
Deterministic (seed=42; module fits seeded; GA seeded). Reproduce ×2 byte-identical (payload sha256). Output:
`experiments/B39_end_to_end_discovery/results/B39_metrics.json`.
