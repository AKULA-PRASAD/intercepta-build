# INTERCEPTA — Collaboration & Compute Brief (current, 2026-08-08)

*A rigor-first, falsify-first computational program. Every claim below is pre-registered, reproduced ×2 byte-identical, and
first-class-negative-honest (evidence: `LEDGER.md`, `experiments/*`, `github.com/AKULA-PRASAD/intercepta-build`). We do NOT
overclaim: the program's honest real-world contribution today is a validated, reproducible **target-identification method +
a decisive negative map + a fail-safe engine** — not a drug, not a clinical tool. This brief names the three partnerships
that would convert that validated computation into real-world impact, ranked by leverage-per-cost. Supersedes the earlier
cancer-only version (that ask is retained as Arm 3).*

---

## Arm 1 — ⭐ the cheapest, highest-leverage ask: one wet-lab CRISPRi test (microbiology partner)
**One line.** We built a validated, analyst-blind, zero-data antibacterial **target-identification** method; **one ~$300,
~3-week CRISPRi experiment** on a target we nominate would be its **first real-world confirmation** — and the experiment is
already fully designed.

- **What's validated (honest, committed):** flux-balance gene-essentiality identifies real, host-safe, essential antibacterial
  targets from a genome alone (no drug data), enriched for *experimental* knockout essentiality across **6 curated organisms
  (odds ratios 4–45)** and — in an **analyst-blind, lock-before-reveal** suite across all three domains of life — **4 of 7
  never-seen organisms pass** (with the 3 failures reported first-class on mapped boundaries). The method composes into a
  fail-safe engine that abstains where no signal transfers.
- **The ask:** run a pre-registered **CRISPRi essentiality knockdown** of one nominated broad-spectrum target (top picks:
  **dxr/ispC** or **murA** — MEP/cell-wall cores) in *E. coli* K-12, vs a non-targeting control + known-essential (ftsZ) and
  dispensable (lacZ) controls. **The design is turnkey and ready** — real, specificity-checked sgRNA sequences, controls, and
  a pre-registered readout are in `experiments/CRISPRIDESIGN1_wetlab_ready/PROTOCOL.md` (est. **$200–400, ~2–3 weeks**,
  standard bench).
- **Pre-registered outcome:** targeting guide reduces growth ≥5× vs control (p<0.01, n≥3) → **first prospective wet-lab
  confirmation** of a computational nomination. If not → the prediction is wrong, reported as a first-class negative and the
  nominating signal is recalibrated. **The experiment cannot produce an uninformative answer.**
- **Honest scope:** this validates the *biology/method* (essentiality → a real target), **not** a drug, selectivity, or
  clinical efficacy. In return: co-authorship, the turnkey protocol, and a rigorous, reproducible analysis layer.

## Arm 2 — a GPU / compute partner (unlocks the target→drug frontier)
**One line.** The single biggest *computational* gap — ranking binding affinity for a **novel** target with zero activity
data — is not solvable on our CPU-only budget, but the definitive test is fully specified and one GPU-run away.

- **What's established (honest negatives):** standard tools fail this on our controlled setups — docking ≈ chance for potency
  (HIT2), ligand/QSAR analog-bound (HIT1), proteochemometric null (B49), active-learning null (B65). The one credible untried
  approach — AlphaFold3-class **co-folding** (Boltz-2) — installs and runs on CPU but is **too slow** for a real benchmark
  (~10 min/complex; a 553-compound head-to-head ≈ 64–138 CPU-hours).
- **The ask:** modest **GPU time** to run the pre-registered benchmark in `experiments/AFFINITY1_cofolding_zeroshot/GPU_BENCHMARK_SPEC.md`
  (same target/compounds/metric as our docking baseline; pre-registered pass gate AUROC ≥0.60 AND > docking's 0.4285). A pass
  would be the first genuine crack in the zero-shot-affinity wall; a fail bounds it rigorously. Either is publishable.

## Arm 3 — a functional-precision-oncology partner (the earlier ask, retained)
**One line.** We proved, across five fronts, that *baseline* transcriptomics (and proteomics) predict cancer type and
proliferation, **not** drug-specific clinical response (within-cancer AUROC 0.504, p=0.43; external replication failed) — so
the way forward is **measured functional/perturbation response in patients**, with our validated engine as the ready analysis
layer.
- **The ask:** a functional-precision (ex-vivo/organoid/PDX) + molecular-profiling partner (or funding) for a **prospective
  ≥300-patient functional cohort** (AML first) testing whether *measured* ex-vivo response predicts clinical outcome under
  pre-registered confound control (`docs/TRACK1_PROTOCOL.md`, `prereg/TRACK1_SAP.md`). Success or falsification are both
  field-moving. Full design, negatives, and reusable falsification battery are committed and open.

---

## What is de-risked and open (all three arms)
A pip-installable engine (`intercepta`) + CLI + passing test suite; a full pre-registration + reproduce-×2 + null/leakage/
study-bias control battery as reusable code; an append-only evidence ledger with verified results **and** first-class
negatives; MIT-licensed, no controlled data committed. The bottleneck in every arm is a **resource we lack (a bench, a GPU,
a patient cohort)** — the rigorous, reproducible analysis is done.

## Honest risk statement (binds all arms)
We make **no** claim of a validated drug, a validated novel target, or a clinical predictor today — we have proven method
validity (target-ID) and mapped, honestly, where computation stops. Our contribution is rigor + a decisive, pre-registered
answer, not a promised miracle. That integrity — every positive survived falsification; the headline negatives are reported
openly — is what makes any genuine advance here believable.

*Contact: Prasad Akula — akula.pra@northeastern.edu. Code, methods, pre-registrations, evidence ledger, and the turnkey
wet-lab protocol: github.com/AKULA-PRASAD/intercepta-build.*
