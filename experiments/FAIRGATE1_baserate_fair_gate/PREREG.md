# FAIRGATE1 — A base-rate-FAIR gate for zero-data FBA-essentiality transfer

**Status: PRE-REGISTERED. Metric, gate threshold, and decisive validation frozen BEFORE scoring.**
**Date frozen:** 2026-08-07. **Author:** INTERCEPTA autonomous module (rigor constitution).

---

## 0. Motivation (diagnosis, not trial-and-error)

META1 established the *transfer law* and, in `base_rate_confound`, showed a within-organism
FLIP: the **identical** iPfal19 GEM for *P. falciparum* PASSED the frozen `OR>3` gate against
the Bushell barseq screen (base rate 0.463, OR 3.67) but FAILED against the Zhang piggyBac screen
(base rate 0.644, OR 2.47). Same organism, same model — only the screen's **base rate** differs,
yet the verdict flips. The `OR>3` gate is therefore **base-rate-confounded**: it is not a clean
test of whether FBA-essentiality transfers to true essentiality.

This module is the *planned* fix: replace the confounded odds-ratio gate with a base-rate-FAIR
effect-size metric, and subject that fix to a falsifiable decisive test.

## 1. The metric and its deep-research justification (principle, stated before scoring)

The odds ratio approximates the risk ratio **only for rare outcomes**. For a 2×2 table with
exposed-event probability `p1 = P(E|F)` and baseline `p0`:

> `OR = RR · (1 − p0) / (1 − p1)`.

When the outcome E (experimental essentiality) is **rare**, `(1−p0)/(1−p1) ≈ 1` and `OR ≈ RR`.
When E is **common** — and our experimental-essential base rates run **0.03 → 0.64** — the factor
`(1−p0)/(1−p1)` diverges from 1 and **OR systematically inflates/deflates relative to the true
effect size**. That inflation is a function of the base rate, which is *exactly* why the same
iPfal19 model flipped PASS↔FAIL on nothing but the screen's base rate.

The principled, base-rate-normalized effect size is the **risk ratio / fold-enrichment over chance**:

> **RR = precision / base_rate = P(exp-essential | FBA-essential) / P(exp-essential)**

RR asks: *among genes the GEM calls essential, how many-fold more often are they truly essential
than a gene picked at random from the same screen?* RR = 1 means no transfer; RR > 1 means genuine
enrichment. RR is dimensionless in base rate: it divides precision by the very base rate that
distorts OR, so it is invariant to the screen's prevalence by construction. (This RR is identical
to META1's committed `lift` column; we recompute it from the committed contingency tables.)

**Reported for every organism:** RR point estimate, a **95% CI** (primary: nonparametric bootstrap,
20 000 multinomial resamples of the N adjudicable genes over the 4 contingency cells, fixed
per-organism seed, 2.5/97.5 percentiles; secondary cross-check: log-normal CI from the bootstrap
log-RR SD), and the **one-sided Fisher exact p** (alternative='greater', recomputed from the
committed contingency counts). A large RR on tiny counts is not enough — significance is still required.

## 2. The FROZEN fair gate (pre-registered; T justified from first principles, NOT tuned)

> **FAIRGATE PASS ⇔ (RR_lower_95%CI > 1) AND (RR_point ≥ T) AND (Fisher one-sided p < 0.01)**,
> with **T = 1.0**.

**Justification of T = 1.0 (from first principles, before seeing any CI):**
The disease we are curing is that a *fixed threshold on a base-rate-sensitive statistic* (OR > 3)
maps to different real enrichments at different base rates. The only effect-size floor that is
itself **free of arbitrary convention and free of base-rate sensitivity** is the null of
no-enrichment, **RR = 1**. Any RR significantly above 1 means FBA-essentiality is *genuinely*
enriched for true essentiality — that *is* real transfer signal. Protection against trivially small
but "significant" enrichments on large N is supplied by requiring the **lower 95% CI to exceed 1**
and **Fisher p < 0.01** (two independent significance guards), *not* by an arbitrary large fold-floor.
Imposing a larger fixed floor (e.g. T = 1.5) would (a) re-introduce exactly the kind of arbitrary
line whose base-rate-dependent crossing we are trying to eliminate, and (b) mechanically penalize
*high*-base-rate screens, whose RR is compressed toward 1 even when the signal is real and highly
significant — re-importing base-rate sensitivity through the back door. This gate is therefore a
**validity** gate ("is the transfer real?"); the RR magnitude + CI separately report **strength**
("is it strong enough to act on?"). **T-sensitivity over T ∈ {1.0, 1.25, 1.5, 2.0} is reported in
full for transparency** so a reader who prefers a stricter floor sees exactly what changes.

This gate is **FROZEN** now and will not be edited after scoring.

## 3. THE DECISIVE VALIDATION (falsifiable; pre-registered)

**(3a) Empirical base-rate invariance — the within-Pf pair.** Score the identical iPfal19 GEM
against BOTH screens (committed contingencies):
- iPfal19 vs **Zhang** piggyBac: base 0.644, OR 2.469 → **OR-gate FAIL**.
- iPfal19 vs **Bushell** barseq: base 0.463, OR 3.667 → **OR-gate PASS**.

> **The invention SUCCEEDS iff FAIRGATE gives the SAME verdict for the same GEM across the two
> base rates (verdict consistency), whereas the OR gate flipped (FAIL vs PASS).**
> If FAIRGATE *also* flips across the pair, the invention FAILS on this test.

**(3b) Simulation — OR vs RR under pure base-rate variation.** Fix a true fold-enrichment L and a
fixed FBA-essential fraction f and sample size N; sweep the base rate p from 0.10 → 0.65
(constraining precision = L·p ≤ 1). At each p derive the implied 2×2, and compute OR and RR.

> **Prediction: RR stays exactly at L (CV = 0) while OR swings widely with p.**
> If RR swings as much as OR, the invention FAILS. We quantify the swing (min, max, ratio, CV) for
> both metrics for L ∈ {1.5, 2.0}.

**Overall verdict rule:** deliver the invention (call RR a validated base-rate-fair gate) **only if
BOTH 3a (verdict consistency across the pair) AND 3b (RR invariant, OR swings) pass.** Otherwise
report honestly that RR is not the fix and propose nothing.

## 4. Application & honest framing

Apply FAIRGATE to all 19 committed organisms; emit the re-scored table (organism, OR, RR, RR-CI,
Fisher p, OR-gate verdict, FAIRGATE verdict). **This is a PROPOSED FAIRER / SECONDARY LENS for
FUTURE prospective tests.** It does **NOT** retroactively flip any committed, pre-registered OR>3
verdict — those stand as recorded under their frozen gate. We report which committed OR-"fails" are
**real-signal-under-OR-compression** under RR (expectation from META1: K. phaffii, Fisher p ≈ 4e-5)
versus **genuine nulls** (expectation: T. brucei, RR < 1, p ≈ 0.87).

## 5. Reproducibility & honest scope

Payload SHA-256 over sorted-key JSON (excluding `verdict`/`provenance`); `run.py` run twice, SHAs
must match byte-identically; all randomness seeded. **Scope:** this is a *statistical-metric*
invention validated by base-rate-invariance + simulation on **committed in-silico results**. It is
**not** new wet-lab evidence; it changes **no organism's biology**, only the fairness of the transfer
verdict.

## Inputs (committed contingency tables — read, not fabricated)
- `META1_transfer_law/results/META1_metrics.json` (assembled 19 organisms).
- Per-experiment reveal/metrics JSONs carrying `[both, FBA_only, exp_only, neither]`:
  CROSSVAL_curated, VALIDATE_essentiality(_deg), BLIND1–7, GENERALIZE4/5, HARDENF1/HARDENP1,
  PARARESOLVE1 (Zhang swap) and PARARESOLVE2 (Bushell screen-tech probe).
