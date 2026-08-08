# CONFORMAL1 — pre-registration (frozen before results)

**Domain:** uncertainty / abstention (INTERCEPTA's core property + the audit's strongest domain). **No external fetch** —
reuses cached E. coli (PEC) and M. tuberculosis (DeJesus 2017) pools from NONMET1. CPU-trivial, deterministic.

## The question (stress-tests the vision's defining claim)
The whole program rests on **honest abstention — "the system knows what it cannot know."** That has only ever been shown
as *in-distribution* calibration (CALIB1). But the vision's real case is a **never-seen organism**. So: **does a
distribution-free coverage guarantee, calibrated on one organism, still hold on a novel organism?** (split-conformal
essentiality prediction, calibrated on E. coli, coverage measured on held-out E. coli vs on out-of-distribution M. tb).

## Method
- Features: conservation-breadth + genomic-context (both cached, comparable across organisms). Classifier: logistic,
  trained on an E. coli TRAIN split.
- Split-conformal (target coverage 1−α, α=0.10): nonconformity sᵢ = 1 − p̂[true label] on an E. coli CALIBRATION split;
  q = the ⌈(n+1)(1−α)⌉/n quantile of s; prediction set(x) = { y : p̂[y] ≥ 1−q }. Empirical coverage = fraction of test
  points whose TRUE label ∈ prediction set. Also report mean set size (1 = confident; 2 = {both} = abstain; 0 = confident-wrong).
- Deterministic split (fixed seed); reproduce ×2.

## Pre-registered gates
- **G1 (sanity — conformal implemented correctly):** in-distribution held-out E. coli coverage ≥ 0.85 (target 0.90).
  PASS required for the OOD result to be interpretable.
- **G2 (the real question — characterization, not pass/fail):** report OOD **M. tuberculosis coverage**. Hypothesis:
  conformal guarantees marginal coverage only under exchangeability, so OOD coverage may **degrade**. If OOD coverage
  holds (≥0.85) → the abstention guarantee *transfers* to a novel organism (good for the vision). If it degrades
  (<0.85) → honest bound: **the guarantee is in-distribution only; abstention on a truly novel organism must be more
  conservative than the nominal rate.** Either is a first-class result.

## Reproduction / scope
Deterministic; payload = SHA-256 over sorted-key metrics (in-dist coverage, OOD coverage, set sizes, α). Run twice,
byte-identical. Scope: n=2 organisms (a demonstration/bound, not a population estimate); conservation features;
essentiality prediction only; in-silico. It characterizes the *abstention guarantee*, not a target.
