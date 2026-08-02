# SIL1 — The conformal-gated SELF-IMPROVING LOOP: do the system's own validated findings improve the task, and does confidence-gating prevent self-deception? (finalized 2026-08-01, PRE-RESULT)

(SIL1 = Self-Improving-Loop chapter 1 — the first rigorous test of VISION principle 6, the "living net", with its anti-self-deception guardrail.)

## Vision alignment (principle 6, directly)
Principle 6: the system is LIVING — its own findings-while-working feed back to improve the current problem — with the
GUARDRAIL that self-generated knowledge is confidence-tiered and quarantined until validated, or the self-improving loop
becomes a self-DECEPTION loop. SIL1 tests that mechanism rigorously and falsifiably: does feeding the system's OWN
high-confidence (conformal-validated) predictions back as knowledge measurably improve the task, and — decisively — is
the confidence-GATING what makes it safe (ungated / shuffled feedback must NOT help, and should hurt: model collapse)?
This is the most vision-central untested capability; it plays to our two proven strengths (calibrated conformal
prediction B30b + proving-ground rigor).

## Phase-0 provenance (3-thread investigation → this design)
Deep research (3 parallel threads) ranked the candidate next capabilities: GNINA docking rescoring = real but MODEST/
incremental; cross-pathogen breadth = feasible but lower-novelty, and cancer→antimicrobial synergy transfer =
data-starved/unjustified; the **self-improving loop = vision-central, genuinely novel (most such claims are
UNFALSIFIABLE demos), rigor-fitting, and valuable either way**. Thread-2 gave the exact rigorous recipe: a with-loop vs
without-loop ABLATION + a SHUFFLED/UNGATED negative control + leakage control, where only conformally-validated outputs
feed back — the guard against MODEL COLLAPSE (Shumailov Nature 2024: training on self-generated data drifts + loses tails).

## The mechanism under test (self-training as the loop's atom)
As the system works a prediction task, it makes predictions on unlabeled chemistry; the CONFORMALLY-CONFIDENT ones
"graduate" to knowledge (GOLD tier) and are fed back as pseudo-labels to retrain — the "net grows with every query" at
the mechanism level. The decisive question is whether the confidence-gating (calibrated conformal, not a raw threshold)
is what makes this help rather than corrupt.

## Data (OPEN; classification tasks with reliable labels; leakage-controlled)
TDC ADMET binary tasks (cached, B30) — a panel of tasks with enough data to carve TRAIN / UNLABELED-pool / TEST. Per
task, SCAFFOLD-disjoint splits (train vs pool vs test all scaffold-disjoint) so pseudo-labels can't leak the test answer;
structural dedup across pool and test. Small labeled TRAIN (to leave room for the loop to help), a large UNLABELED pool,
a held-out TEST. (MoleculeACE potency, binarized, as a robustness panel if TDC is thin.)

## Design (4 arms, ablation + negative controls; per task, ×seeds)
Base model = admet `_TaskModel` (HGB + Mondrian conformal, B30b-calibrated). Per task:
- **A — WITHOUT-loop (baseline):** train on TRAIN only.
- **B — WITH-loop (conformal-gated):** predict the UNLABELED pool; graduate compounds whose CONFORMAL set is a confident
  SINGLETON (`{0}` or `{1}`) as GOLD pseudo-labels; retrain on TRAIN + GOLD.
- **C — NEGATIVE CONTROL (ungated):** retrain on TRAIN + ALL pool pseudo-labels (no confidence gate) — tests whether
  gating matters (ungated should propagate errors / not help = the model-collapse risk).
- **D — NEGATIVE CONTROL (shuffled labels):** take the SAME gated-confident compounds as B but assign SHUFFLED/random
  pseudo-labels — tests whether the gain is from CORRECT knowledge, not just more data (must NOT help; should hurt).
Evaluate all four on the SAME held-out TEST (AUROC). Panel over tasks; 3 seeds.

## Metrics (per task + panel, mean over seeds)
- TEST AUROC for A/B/C/D; deltas ΔB−A (loop effect), ΔB−C (gating value), ΔB−D (correct-knowledge value).
- Diagnostics: # graduated GOLD pseudo-labels, their EMPIRICAL accuracy (are the confident ones actually right?),
  conformal singleton-rate.

## Hypotheses (pre-registered)
- **H1 (loop helps):** panel-median **ΔB−A > 0** (conformal-gated self-training improves TEST above base).
- **H2 (gating is the guardrail — DECISIVE):** **ΔB−C > 0** (gated beats ungated) AND **ΔB−D > 0** (correct beats
  shuffled) → the confidence-gating is what makes the loop help rather than corrupt; ungated/shuffled feedback does NOT
  help (and D should be ≤ A: fake knowledge hurts) — the anti-self-deception guardrail demonstrated.
- **H3 (gated pseudo-labels are trustworthy):** empirical accuracy of GOLD (conformal-singleton) pseudo-labels
  substantially exceeds the ungated pool accuracy → conformal confidence genuinely identifies reliable self-knowledge.
- **H0 (first-class):** ΔB−A ≈ 0 → even conformal-gated self-generated knowledge does NOT improve the task here → the
  "living net helps" hypothesis is falsified in this setting (a valuable, honest boundary most demos hide). Reported plainly.

## Honesty / scope
Retrospective, in-silico; self-training/pseudo-labeling is an ESTABLISHED semi-supervised technique — the contribution is
NOT inventing it but rigorously validating the LIVING-NET MECHANISM + its confidence-gating GUARDRAIL (with the shuffled
+ ungated negative controls + leakage control) in the discovery context, tied to CALIBRATED conformal confidence and
principle 6. Within-task loop (findings-while-working); cross-task accumulation (findings-help-future-problems) is a
harder, likely negative-transfer follow-up (logged). Not wet-lab. A NULL is expected-allowed and first-class.

## Reproducibility
Deterministic (split seeds, model seed=42, conformal seeded, shuffle seeded). Reproduce ×2 byte-identical (payload over
per-task A/B/C/D metrics + deltas). Output: `experiments/SIL1_conformal_self_improving_loop/results/SIL1_metrics.json`.
Env: intercepta-build. Feasibility-gated: verify TDC task panel has enough data for TRAIN/pool/TEST carve; smoke-test the
conformal-singleton graduation on 1 task before the full panel (B63 no-blind-run lesson).
