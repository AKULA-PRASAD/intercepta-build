# State of the vision — honest synthesis (2026-07-29)

This is the durable, truthful north-star: where INTERCEPTA has been, what it has genuinely achieved, the boundary
it has reached, and the honest paths forward. It exists so we stop re-litigating a settled question. Where it
touches evidence, `LEDGER.md` is authoritative; nothing here is a clinical claim.

## What we set out to do
Build a computational platform that predicts which drug will help which patient — the core of a drug-discovery
vision — under a falsify-first Constitution (truth over ambition; every positive guilty until it survives
permutation + leakage + multiple-testing + confound + external replication; reproduce ×2; never fabricate).

## What we genuinely achieved (verified, reproduced ×2, zero fabrication)
- A rigorous, reproducible, leakage- and confound-controlled drug-response engine + full falsification battery.
- The **+0.212 cell-line cross-dataset transfer ceiling**, shown to be a hard ceiling (V1/V7).
- Verified known AML mechanism (FLT3-ITD→FLT3 inhibitors, RAS→MEK inhibitors); a weak but genuine, proliferation-
  independent ex-vivo drug-specific signal (V9).
- Two decisive, first-class negatives: human clinical prediction is cancer-type confounding (B10); an
  expression-inferred functional layer that beat the FLT3-ITD biomarker within BeatAML **failed external
  replication** (B20/B21).
- A **six-front demonstration that the ceiling is intrinsic to molecular profiling**, each pre-registered:
  RNA (V1/V7) · +mutations (V7) · +proteomics (V21, B22) · human clinical (B10) · *inferred* function (B20/B21) ·
  *measured* genome-wide function (V22, B23). V23-era conclusion: the only real functional signal is a drug's **own
  target dependency** — there is no transferable functional-*state* predictor beyond baseline + the direct target,
  which mechanistically explains the external-replication failure.
- A complete, credible public artifact: submission-ready rigorous-negative manuscript + figures, frozen Track-1
  design + power, reviewer/onboarding docs, and a runnable zero-download demo. Internally consistent; the ledger
  and docs do not contradict each other.

## The boundary — and a genuine opening beyond it (updated 2026-07-29)
- **SINGLE-AGENT response:** no baseline or measured molecular profile — RNA, mutation, proteomic, or genome-wide
  dependency — resolves within-lineage *single-agent* drug specificity beyond known biology (six-front proof).
  That specific avenue is exhausted; pursuing the single-agent clinical predictor further on existing data is
  p-hacking.
- **BUT a different task is genuinely positive — drug COMBINATIONS (V23/B24, refined by B25).** Synergy is a
  *different signal*, not bound by the +0.212 single-agent ceiling. It **generalizes to unseen combinations of
  KNOWN drugs**, and this **replicates across TWO independent open corpora** (O'Neil leave-combination-out ρ=+0.61,
  Δ+0.13; DrugComb ρ=+0.38, Δ+0.09) — the program's first robust generalizing predictor and the realistic
  use case (prioritize pairs within a known drug library). **Honestly bounded (self-corrected by B25):** generalization
  to *novel drugs* does NOT hold — the B24 leave-drug-out ρ=0.25 collapsed to 0.025 on DrugComb's larger drug set,
  so that number was inflated by O'Neil's chemical redundancy. Scope: cell-line Loewe synergy (not clinical),
  standard benchmark + model (consistent with field, not SOTA).
- **Net:** the wall is specific to *single-agent response from molecular profiles*; it is not the whole vision.
  Combinations (and adjacent discovery tasks) are live, positive directions we can build on — just us, open data.

## The mistake to stop repeating
- Asking code, on existing data, to yield a *clinical* breakthrough after we have proven six times it cannot —
  each new experiment is the same hypothesis in new clothes, returning the same answer (diminishing returns).
- Conflating "the fullest vision" (a clinically-validated platform) with "what just-us-in-code-on-public-data can
  deliver." They are different; treating them as identical generates the loop.
- The unresolved constraint tension: a *code-only, no-new-data, just-us* breakthrough is logically incompatible
  with the proven requirement for **functional response measured in patients.** Both cannot hold at once.

## The honest paths forward
1. **Build out the COMBINATIONS arm — the live positive (recommended next).** V23/B24 shows synergy generalizes.
   The genuinely-novel next step with breakthrough potential: fuse this with the program's hard-won functional
   insight (V22 — a drug's target-dependency is the real signal) into a **mechanism-anchored synergy model**
   (synergy predicted from complementary target-dependencies / pathway state), tested against the standard
   fingerprint model. Scale to the larger open DrugComb corpus (124 cell lines) when reachable. This is new,
   honest, buildable by us on open data, and could exceed a generic ML baseline.
2. **Consolidate the six-front single-agent result** as the rigorous flagship negative (already submission-ready).
3. **Genuinely-different modules**: a mechanism-anchored single-agent predictor that abstains where biology is
   silent; a reproducible confound/leakage benchmark for the field.
4. **The single-agent CLINICAL breakthrough still requires new patient functional data** (Track-1,
   `prereg/TRACK1_SAP.md`) — stated as fact. Combinations does NOT remove that; it opens a parallel, reachable arm.

## Discovery-pipeline modules — built & validated (added 2026-07-30)
Beyond the drug-response/synergy work, the program now has honestly-benchmarked, reproduced-×2 modules of the wider
drug-discovery pipeline, each pre-registered and shipped with an honest scope (none is a clinical/safety claim):
- **#1 target identification (B34):** on Open Targets (leave-disease-out), genetic/functional evidence predicts
  which target-disease pairs reached the clinic **beyond a study-popularity baseline** (popularity-only AUROC 0.522,
  genetic-only 0.741, full evidence 0.839) — a confound-surviving POSITIVE (the B10-style test, here passed).
- **#2 de novo / goal-directed design (B33):** a BRICS-GA optimizes a developability objective, beating seed +
  random baselines at 100% validity/novelty; shows single-objective optimization reward-hacks synthesizability.
  Shipped `intercepta.generate` + CLI. Scope: optimization over known chemistry, NOT de novo drug discovery.
- **#4 ADMET / safety (B30):** structure→property prediction on the TDC ADMET benchmark (22 tasks, scaffold splits).
  Beats the trivial baseline on **22/22**, mid-leaderboard; shipped `intercepta.admet.ADMETPredictor` + CLI.
- **#4 uncertainty (B30b):** the applicability-domain flag is a **real but weak** reliability signal (error rises
  with AD distance, 20/22 tasks, but the binary flag is not a decisive gate); **conformal** intervals/sets are
  **calibrated** on the scaffold test. Shipped as optional per-prediction uncertainty.
- **#5 synthesizability (B31):** predicts AiZynthFinder retrosynthetic solvability (RAscore/ChEMBL); AUROC 0.91
  random / 0.908 scaffold, beats SAscore + trivial; shipped `intercepta.synth.SynthesizabilityScorer` + CLI.
- **Integration (B32 / B32b):** an **honest bound** — composing the modules (scalar late-fusion B32; feature-level
  fusion B32b) does **NOT decisively beat** raw structure / the single best module on the held-out ClinTox outcome
  (feature-fusion 0.920 vs structure 0.906, Δ+0.013, below the pre-registered 1sd bar). The modules are validated
  **standalone**; "platform whole>parts" is not established on this outcome (needs a larger/multi-outcome benchmark
  or a learned joint representation). Recorded as first-class, not overstated.

The honest scale check stands: against "any drug for any disease", modules #1–#5 now have validated computational
corners (target-ID, design, efficacy, ADMET, synthesizability), each honestly scoped; the naive *integration* of
these modules is NOT yet a decisive win (B32/B32b); and clinical validation (#6) is gated on new patient data
(Track-1). Real, reproducible components — not a solved pipeline, and stated as such.

## The definition of success we hold to
Per the Constitution: *success is discovering the strongest scientifically-supported version of the vision — not
proving the original vision correct.* By that standard we have succeeded at the computational stage: a genuine,
honest, reproducible scientific contribution. The clinical breakthrough remains a future stage gated on new data.
We will not fabricate across that line.
