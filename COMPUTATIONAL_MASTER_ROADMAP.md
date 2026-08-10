# COMPUTATIONAL_MASTER_ROADMAP.md
*The optimal computational path from today's repository to the ultimate vision — "effective drugs for any
disease with minimal experimental data" — under a hard constraint: **no wet lab, and recommend only
computations that materially increase P(vision), never computations whose purpose is publication.**
Grounded in `COMPUTATIONAL_STATE_OF_THE_PROGRAM.md`. Sunk cost ignored.*

## The governing principle (why the usual roadmap is wrong)
The repo proves the binding constraint is **information, not compute**: every frontier wall is the same
inability to predict function beyond conserved-invariant / training manifolds (transfer-condition principle).
Therefore **more GPU-hours on the current paradigms and today's public data cannot reach the vision** — this
is demonstrated, not assumed. The only compute that raises P(vision) does one of three things: (a) exploits
the *softest* wall, where label-free evolutionary information genuinely exists; (b) **instruments** the hard
wall so we detect the moment a new model or public dataset breaks it; (c) **auto-absorbs new public data** so
the achievable subset expands the instant the world produces the missing information. Everything else is in
`COMPUTATIONAL_DEAD_ENDS.md`.

## Ranked directions (by expected increase in P(vision) per GPU-hour)

### R1 — Exploit the softest wall: evolutionary/DMS-scale function & durability prediction ★★★★★
**Attacks:** the extrapolation wall where it is weakest — evolution has *already* "labeled" mutational
tolerance, so residue-level conservation + deep-mutational-scan (DMS) atlases carry real, growing,
label-free signal (unlike novel-target affinity, which has none).
**Do:** finish DYNAMICS5 (within-protein masked-PLM entropy vs documented resistance sites, n≈1,162, CARD);
then generalize to the growing public DMS corpora (ProteinGym-scale) — test whether PLM/evolutionary signal
predicts *functional/durability* effects for **held-out proteins** under strict similarity control.
**Why it moves the vision:** durability/evolvability is a genuinely different, computable axis of "effective"
(resistance-robust) drugging; it is the one place the wall is beatable with public data. **Ceiling (honest):
a proxy, not a fitness measurement.** ~hundreds–low-thousands GPU-h. Expected P(vision) lift: moderate-high.

### R2 — Instrument the hard wall: a leakage-controlled OOD-generalization TESTBED ★★★★★
**Attacks:** the core question the vision reduces to — *can ANY method predict biological function for
genuinely novel targets/chemotypes it has never seen?*
**Do:** build one rigorous, permanent benchmark with **temporal + similarity holdouts and an explicit
training-set-overlap audit** (the AFFINITY1 leakage failure is the cautionary template). Run current
foundation models (ESM/AF/Boltz-class) through it on affinity, mechanism, and function tasks, scored **only on
the leakage-free novel split.** The goal is **not to win** — it is to measure the exact distance to the wall
and to **fire an alarm the day a new model or dataset crosses it.**
**Why it moves the vision:** it converts "is the vision reachable yet?" from opinion into a monitored number.
This is the program's north-star instrument. ~low-thousands GPU-h (mostly one-time). Expected lift: high
(information value), even though most runs will report "still at chance on novel."

### R3 — A public-data ingestion + re-test engine (make the vision data-asymptotic in practice) ★★★★
**Attacks:** the fact that the vision expands with public data, not our compute.
**Do:** an automated pipeline that ingests each new large public functional dataset (DMS, Perturb-seq /
perturbation atlases, structural-genomics, activity DBs) and **automatically re-runs R2 + the
transfer-condition frontier**, logging where the achievable subset grew. Turns "wait for data" into
"systematically capture every new bit of information the moment it is public."
**Why it moves the vision:** it maximizes information capture per unit time toward a data-limited goal. Low GPU, high leverage.

### R4 — Harden + generalization-test the ACHIEVABLE subset ★★★
**Attacks:** nothing new — it *banks* what is already computationally real.
**Do:** package the transfer-condition-gated, abstaining, base-rate-fair target-ID engine; run it **end-to-end
on a pathogen it was never built on** (true generalization, not another in-distribution benchmark). Fold in
DYNAMICS durability once R1 firms it → a durability-aware target *prioritization*.
**Why:** it is the one deliverable that is honestly done; hardening it is cheap and it is the usable core.

### R5 — (CONDITIONAL, gated on R2) heavy compute on the molecule half — ONLY if the wall breaks ★ (else ✗)
**Do nothing here until R2 shows a method beating the extrapolation wall on a leakage-free novel-target split.**
If that alarm ever fires, *then* invest heavily in novel-target affinity + generation. Before that, it is a
proven money-pit (see dead-ends). This is the correct place for "another 10,000 GPU hours" — but **only after
R2 earns it.**

## Is the ultimate vision computationally achievable? (the required answer)
- **As stated ("ANY disease, minimal data, effective drug end-to-end"): NOT achievable by compute on today's
  public data** — proven by the six-fold information wall. **[F]**
- **For the conserved-invariant subset (pathogen target prioritization): achievable now** — validated. **[F]**
- **Eternally impossible? No.** It is **data-asymptotic**: as public functional data accumulates, R3 expands the
  reachable subset, and R2 detects if/when a paradigm finally extrapolates. **[Inference]**
- **Therefore the shortest computational path is NOT to attack the vision head-on** (proven futile) — it is to
  (R1) harvest the softest wall, (R2) instrument the hard wall, (R3) auto-absorb the growing data, (R4) bank the
  achievable core — and let P(vision) rise with the world's data while we hold a monitor on the frontier.
