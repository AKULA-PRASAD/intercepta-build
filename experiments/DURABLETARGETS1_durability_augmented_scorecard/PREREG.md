# DURABLETARGETS1 — Pre-registration (frozen plan)

**Type:** INTEGRATION of already-committed, reproduced-×2 in-silico axes into one capstone
decision-support deliverable. **NOT** a new discovery, **NOT** a probe, **NOT** new validation.

## Question
Can we assemble the platform's committed antibacterial target-quality axes into a single ranked
scorecard, and does adding the NEW resistance-**durability** axis (DYNAMICS) change the ranking in
an interpretable way (durable cores rise, resistance-prone targets fall)?

## Inputs (committed only; no fetch, no recompute of the science)
- `BESTINT1_multiaxis_score` → druggability, breadth, resistance-robustness, condition-robustness,
  and the equal-weight `best_intervention_score` composite.
- `PREDVAL_target_scorecard` → experimental essentiality per organism (E. coli / K. pneumoniae / M.tb),
  the independent truth axis (VAL-ESS-anchored).
- `DYNAMICS2_durability_scaleup` → per-target mean ESM-2 masked-marginal Shannon entropy over
  drug-contact residues + HIGH/LOW resistance-liability label. Antibacterial (`cls=="abx"`) subset only.

## Method (frozen before running)
1. Target set = union of DYNAMICS2 antibacterial targets (durability-covered) + flagship BESTINT1
   cores. Map across sources by **gene symbol**. Missing axis → **NA** (never silently imputed).
2. Durability axis = `durability_norm = 1 − mean_contact_entropy / ln(20)` (monotone; higher = more
   durable; lower drug-contact entropy = harder to escape by mutation). NA where no drug-binding pocket.
3. Composite (on the full-coverage intersection = targets with BOTH the 4 BESTINT1 axes AND durability):
   **equal-weight z-score aggregation** (population std) over informative (non-zero-variance) axes.
   - `z_composite_noDur` = mean z over {druggability, breadth, resistance, condition}.
   - `z_composite_withDur` = same axes **+ durability**.
   - Unfitted equal weights **by design** — no ground truth of "best durable target" exists to fit;
     fitting would fabricate confidence (BESTINT1 philosophy). The only difference between the two
     composites is the durability axis, so the rank DELTA isolates durability's effect.
   - Experimental essentiality is **displayed** and used as the independent truth axis; it is **not**
     folded into the composite (mirrors BESTINT1, avoids circularity).
4. Report both composites, the rank DELTA (risers/fallers), the top-5 durable-augmented shortlist,
   and the standalone durability ranking.

## Determinism / reproduction
No randomness, no fetch. Payload SHA-256 over sorted-key JSON, **excluding** provenance. Reproduce ×2
byte-identical.

## Pre-registered scope (binds every row)
Target-QUALITY triage. Durability carries DYNAMICS's bounds: AUROC ~0.83 (n=26, PLM-proxy, static
single drug-bound structure, confound-softened strict significance); applies only to targets with a
(crystal/predicted) drug-binding pocket. Hypotheses, cross-organism/ortholog-transferred, not wet-lab,
not a drug, not clinical.
