# DURABLETARGETS1 — Durability-augmented multi-axis antibacterial target-quality scorecard

The programme's **capstone deliverable**: one ranked, transparent target-quality scorecard for the
flagship antibacterial targets, produced by **composing already-committed, reproduced-×2 in-silico
axes** and adding the NEW resistance-**durability** axis from DYNAMICS. This is an INTEGRATION —
composition of committed results, **not new science**.

## Run
```
~/miniconda3/envs/intercepta-build/bin/python run.py
```
Reads only committed source metrics (BESTINT1, PREDVAL, DYNAMICS2). Deterministic; reproduces ×2
byte-identical. Writes `results/DURABLETARGETS1_metrics.json` (sorted keys) + `results/payload.sha256`.

## Axes (columns)
| Axis | Source | Meaning |
|---|---|---|
| exp_essential_orgs | PREDVAL | # of {E.coli, K.pneumoniae, M.tb} experimentally essential (0–3); independent truth axis |
| breadth_frac | BESTINT1 | FBA cross-organism breadth / 7 |
| druggability | BESTINT1 | fpocket max druggability [0,1] |
| resistance_robust | BESTINT1 | SYNLETH monotherapy=1 / combination=0.5 |
| condition_robust | BESTINT1 | CONDROB robust=1 / partial=0.5 |
| **durability_norm** | **DYNAMICS2 (NEW)** | `1 − mean_contact_entropy/ln(20)`; higher = more durable (lower ESM-2 masked-marginal entropy at drug-contact residues) + HIGH/LOW resistance-liability label |

## Composite
Two composites on the full-coverage intersection (targets with BOTH the BESTINT1 axes AND durability),
equal-weight z-score aggregation over informative axes: `z_composite_noDur` (BESTINT1 axes only) and
`z_composite_withDur` (+ durability). The delta isolates durability. Unfitted equal weights by design.
Within this elite set `resistance_robust` and `condition_robust` are invariant (all 1.0) and drop out
as non-informative — so the ranking is driven by druggability + breadth (+ durability), which are also
BESTINT1's genuinely-independent axes.

## Scope
Decision-support target-QUALITY triage. Durability carries DYNAMICS's bounds (AUROC ~0.83, n=26,
PLM-proxy, static structure, confound-softened significance) and applies only to targets with a
drug-binding pocket; others get durability = NA (honest). Hypotheses; not a drug; not clinical.
See `PREREG.md` for the frozen plan and `SUMMARY.md` for results.
