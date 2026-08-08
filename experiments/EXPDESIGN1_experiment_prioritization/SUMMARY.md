# EXPDESIGN1 — SUMMARY (value-of-information experiment prioritization)

**PASS on the pre-registered headline (G1). Reproduced ×2 byte-identical, payload sha256
`41b8a5e39741b14f41ad059b71971ffee6275d3e0ef4a2ade134a93c4ba2cfba`. No external fetch — reused the cached E. coli
pool (NONMET1 conservation + PEC essentiality + MET2 GEM).** Domain: experiment design (Phase-1 audit gap, ~8%).

## G1 — validation efficiency (the clean, useful result): PASS
Pool = **4195** E. coli genes with a PEC label, **287** experimentally essential (base rate **6.8%**). Priority score =
conservation breadth (the zero-data workhorse). Testing the top-30 conservation-ranked genes first "validates" **16** true
essential targets vs **~2.1** expected by random selection — **7.8× enrichment, hypergeometric p = 9.3×10⁻¹²**, an
**~8.1× reduction in wet-lab experiments** to validate the same number of real targets.

**What this genuinely contributes (honestly bounded):** it translates the *already-validated* zero-data essentiality
signal into a **quantified experiment-prioritization** — the decision-support layer the program's real bottleneck (scarce
wet-lab budget; CRISPRIDESIGN1 ~$300/target) actually needs: "test these first, in this order, to validate the most real
targets per experiment." The underlying signal (conservation predicts essentiality) is **not new**; the contribution is
the experiment-design framing + the concrete efficiency number (~8× fewer experiments). Modest, real, useful.

## G2 — validate-vs-learn tradeoff: CONFOUNDED, reported honestly (not a clean finding)
The active-learning arm evaluated each acquisition strategy's model on its **own shrinking unlabeled remainder**, so the
final-AUROC numbers (random 0.905 > uncertainty 0.889 > greedy 0.877) are **confounded by a strategy-dependent test set**:
greedy removes the easy positives first, leaving a harder remainder → artificially lower AUROC; random leaves a
representative remainder → higher AUROC. This is a **test-set-shift confound**, so the G2 numbers do **NOT** support a
clean "which strategy learns fastest" claim. G2 was pre-registered as *characterization only* (not pass/fail), so it does
not affect the PASS verdict — but the honest statement is: **G2 is inconclusive as implemented.** The clean fix (a fixed
held-out test set) is noted for any future version; I am not over-reading the current numbers.

## Verdict
A **modest, genuine, honestly-bounded** experiment-design capability: the validated zero-data ranking is an ~8×-efficient
prioritizer of which targets to validate first (G1, clean); the acquisition-strategy learning comparison (G2) is confounded
and inconclusive. In-silico, one organism (E. coli/PEC), retrospective ("experiment outcome" = existing PEC label); it
validates the *policy*, not a target — a decision-support layer over the engine, not a discovery.
