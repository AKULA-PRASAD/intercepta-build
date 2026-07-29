# The Constitution of Scientific Discovery — INTERCEPTA build

This repository is governed by these rules. They override ambition, deadlines, and the founders' hopes.
Any result that violates them is not a result.

1. **Truth over vision.** Loyalty is to what the data shows, never to what we want it to show. If evidence
   contradicts the vision, the vision changes.
2. **Falsify first.** Every hypothesis is assumed FALSE until it survives an honest attempt to kill it. We
   design the test that would break the claim, then run it.
3. **Every positive is guilty until proven innocent.** A positive result is provisional until it survives:
   permutation null, leakage audit, multiple-testing correction (BH-FDR), confound adjustment, and
   external/independent replication. Numbers reported before those checks are labeled provisional.
4. **Compress.** Prefer the explanation with the fewest new assumptions and no unnecessary novel entities. If a
   simpler known-biology model explains the evidence, that is the answer — even if it is less exciting.
5. **Negatives are first-class.** A well-powered null, a falsified hypothesis, and a "not testable on current
   data" verdict are real scientific results and are recorded with equal weight.
6. **Never fabricate.** No invented numbers, no simulated-as-real data, no cherry-picked seeds, no rounding a
   claim into significance. Every number traces to a committed script + committed metrics file, reproduced ×2.
7. **Reproduce ×2.** A result counts only if two independent runs produce identical metrics (timestamp aside).
   Determinism is required; seeds are fixed and recorded.
8. **Bar before boast.** Every model is compared against honest baselines (predict-the-mean, single-gene
   surrogate, parameter-free axis). "Better than nothing" is not a result; "better than the honest bar" is.
9. **State scope.** Cell lines are not patients. An association is not a validated predictor. Say exactly what
   was and was not shown.
10. **Ready for novelty, but only real novelty.** Pursue genuinely new ideas; subject them to rules 1–9 without
    mercy. An untested novel idea is logged as untested, never as working.

Provenance requirement: every experiment writes a metrics JSON containing `git_sha`, `python`, library
versions, input sha256, seed, and timestamp. Data inputs are verified against `data/MANIFEST.md` at load time.
