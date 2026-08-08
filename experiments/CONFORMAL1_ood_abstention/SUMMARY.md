# CONFORMAL1 — SUMMARY (does the abstention guarantee transfer to a novel organism?)

**Reproduced ×2 byte-identical, payload sha256 `c5c8a256089dba0a34bc1a57cac8c4dce315636d62b670b82051a7317ed5c8ae`.
No external fetch** (cached E. coli/PEC + M. tuberculosis/DeJesus). This directly stress-tests the vision's defining
claim — *"the system knows what it can't know"* — under its real case: a never-seen organism.

## The three-part honest finding
E. coli n=4195 (287 essential); M. tb n=3885 (460 essential); split-conformal target coverage 90%.

1. **Marginal conformal is VACUOUS for the targets (the caution).** Marginal coverage looks fine — 0.901 in-dist,
   0.869 OOD — but that is **entirely the ~93% non-essential majority** (non-essential coverage 0.975 / 0.985). The
   **essential class — the actual drug targets — is covered 0.0 in-dist AND 0.0 OOD.** A marginal coverage guarantee
   does NOT make abstention trustworthy for the minority target class; it is achieved by confidently predicting
   "non-essential" for everything.
2. **Mondrian (class-conditional) conformal fixes it in-distribution (the fix).** Calibrating a separate threshold per
   class restores essential-class coverage to **0.9375** in-distribution (by construction), at a modest mean set size 1.24.
3. **But the class-conditional guarantee does NOT transfer to a novel organism (the honest bound).** On out-of-distribution
   M. tuberculosis, Mondrian essential-class coverage **drops from 0.94 to 0.55** (gap +0.39). So even done correctly, the
   target-class coverage guarantee weakens badly on a never-seen organism.

## Why this matters (genuine contribution — mostly cautionary)
The whole program's trust rests on honest abstention. CONFORMAL1 shows, rigorously, that:
- a naive (marginal) coverage guarantee would be **worthless** for the target class (0% essential coverage), and
- even the correct (class-conditional) guarantee **does not hold at the nominal rate on a novel organism** (94%→55%).

**Honest implication for deployment:** on a truly novel organism the engine's abstention/confidence cannot be trusted at
its nominal coverage; it must be made **substantially more conservative**, or its confidence reported as *not guaranteed
out-of-distribution*. This is a first-class, mostly-negative result that strengthens the program's honesty rather than its
capability — it tells us exactly where the "knows what it can't know" claim breaks.

## Scope
n=2 organisms (a demonstration/bound, not a population estimate); conservation-only features (a weak base classifier —
part of why marginal coverage collapses onto the majority); essentiality prediction; in-silico. It characterizes the
**abstention guarantee under organism shift**, not a target. The clean extensions (stronger base predictor; more organisms;
a conservative OOD coverage inflation) are named, not done.
