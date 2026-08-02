# SIL2 — Does the conformal-gated self-improving loop survive DISTRIBUTION SHIFT (novel chemistry)? (finalized 2026-08-01, PRE-RESULT)

(SIL2 = Self-Improving-Loop chapter 2 — maps WHERE the SIL1 living-net loop works vs breaks; connects principle 6 to the B60–B62 information ceiling.)

## Why (the honest open question SIL1 raised)
SIL1 showed the conformal-gated loop helps IN-DOMAIN (median ΔB−A +0.011, 6/6 tasks) with its anti-self-deception
guardrail. But the vision's stress regime is NOVEL chemistry (a new pathogen's compounds are unlike training). Two of
our OWN results are in tension there: B30b (conformal intervals stay CALIBRATED under scaffold shift) vs B61 (AD-distance
is NULL for novel-chemistry error) + B62 (novel-chemistry potency is an information ceiling / signal-loss). So: does the
self-improving loop's benefit SURVIVE distribution shift, or does it collapse (and possibly HARM) where the base model
is weak and its confident predictions may be untrustworthy? Falsifiable either way; both outcomes map principle 6's scope.

## Phase-0 provenance
Autonomous choice after GNINA (the one back-half docking lever, Thread-1) proved INFEASIBLE on this Apple-Silicon Mac
(Linux+CUDA only) and cross-task accumulation proved ill-posed (activity labels are not transferable across targets).
SIL2 is the clean, feasible, vision-relevant continuation: SIL1's 4-arm design, re-run with an explicit IN-DOMAIN vs
NOVEL-CHEMISTRY test contrast.

## Data (OPEN; MoleculeACE — SAME data/regime as B60–B62, for continuity)
Per target (continuous potency → binarised at the per-target median), scaffold-disjoint carve: TRAIN (≤250) / UNLABELED
POOL / and TWO held-out tests — **IN-DOMAIN test** (random hold-out from the pool's scaffold space) and **NOVEL test**
(scaffold-disjoint AND NN-Tanimoto < 0.40 to TRAIN). Targets with < 30 novel-test compounds skipped (the B55 lesson).

## Design (SIL1's 4 arms, evaluated on BOTH test sets)
Base model = admet `_TaskModel` (HGB + Mondrian conformal). Arms: **A** train-only · **B** train + conformal-singleton
GOLD pseudo-labels from the POOL · **C** ungated (all-pool pseudo-labels) · **D** shuffled labels on B's compounds.
Evaluate A/B/C/D AUROC on the IN-DOMAIN test AND the NOVEL test. 3 seeds; panel over targets.

## Metrics (per target + panel; on EACH test set)
ΔB−A (loop effect), ΔB−C (gating value), ΔB−D (correct-vs-shuffled) on in-domain AND novel tests; GOLD pseudo-label
accuracy; and the conformal singleton-rate + calibration on in-domain vs novel pool compounds (diagnostic).

## Hypotheses (pre-registered)
- **H1 (in-domain replication):** panel-median ΔB−A(in-domain) > 0 → SIL1 reproduces on this data/regime.
- **H2 (KEY — does the loop survive shift?):** compare ΔB−A(novel) vs ΔB−A(in-domain). **H2a (survives):** ΔB−A(novel)
  > 0 and ≈ in-domain → the loop helps even under shift. **H2b (collapses, expected):** ΔB−A(novel) ≈ 0 or < in-domain
  → the loop's benefit is a near-domain phenomenon; self-accumulated in-domain knowledge does NOT cross the
  novel-chemistry ceiling (consistent with B62). Either is first-class and decisive.
- **H3 (guardrail holds under shift):** ΔB−D(novel) ≥ 0 (shuffled still doesn't help/ hurts) AND the loop does not HARM
  the novel test (B ≥ A − noise) → gating prevents self-deception even under shift, OR — first-class — the loop HARMS
  novel-chem (B < A), revealing that in-domain conformal confidence is untrustworthy for feeding novel-regime knowledge.
- **H4 (why):** GOLD pseudo-label accuracy on POOL vs the loop's novel-test benefit — does trustworthy self-knowledge
  fail to transfer because the knowledge is in-domain while the test is novel?

## Honesty / scope
Retrospective, in-silico, MoleculeACE (ChEMBL medchem), binarised potency; within-task loop; the POOL is largely
in-domain (so GOLD knowledge is in-domain by construction — the point is whether in-domain self-knowledge helps a NOVEL
test); n ≈ 15–24 targets; modest effects expected; not wet-lab. A NULL/HARM on novel chemistry is expected-allowed and
first-class (it bounds principle 6's loop to the near-domain regime, consistent with B62).

## Reproducibility
Deterministic (split seeds, model seed=42, conformal + shuffle seeded). Reproduce ×2 byte-identical (payload over
per-target A/B/C/D metrics on both test sets). Output: `experiments/SIL2_loop_under_shift/results/SIL2_metrics.json`.
Env: intercepta-build. Feasibility-gated: verify enough MoleculeACE targets have ≥30 novel-test compounds; smoke-test
1 target before the full panel (B63 no-blind-run lesson).
