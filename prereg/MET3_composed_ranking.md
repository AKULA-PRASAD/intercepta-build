# MET3 — Practical capstone: does adding FBA-essentiality to the target-ID RANKING improve top-k recovery? (finalized 2026-08-03, PRE-RESULT)

## Why (the practical payoff of the MET line)
MET1/MET2 showed (via logistic ΔAUROC) that FBA-essentiality adds target-ID signal beyond conservation, reliably in
E. coli + M. tuberculosis. MET3 converts that into the form the vision pipeline actually uses: a RANKED target shortlist.
Does a conservation+essentiality composite recover more KNOWN drug targets at the TOP (precision@k, enrichment) than
conservation alone — i.e. is the improved front-half real at the ranking level, not just as a coefficient? This is the
capstone; it re-uses MET2's per-gene conservation + essentiality (no new data), adding held-out ranking metrics.

## Data / design
E. coli + M. tuberculosis (the 2 bacteria with enough drug targets for a reliable estimate; MET2). Per GEM gene:
conservation (mmseqs2 to other orgs' targets), FBA-essentiality (MET2 cache), is_drug_target (ChEMBL-xref). Composite
score = **5-fold-CV out-of-fold** logistic P(target | conservation, essentiality) — HELD-OUT, so no overfitting.
Baseline = conservation score alone. Metrics: precision@k (k = #targets), enrichment@k, AUROC — composite vs conservation.
Report the top-ranked recovered targets (interpretable).

## Hypotheses (pre-registered)
- **H1:** composite (cons+essentiality) precision@k > conservation-alone precision@k in BOTH organisms (practical
  top-k improvement).
- **H0 (first-class):** no top-k improvement (composite ≈ conservation at the ranking level) → the ΔAUROC gain doesn't
  translate to better top-k recovery (honest — global AUROC gain need not help the top). Reported plainly.

## Honesty / scope
Metabolic subproteome only; 2 bacteria (E. coli, Mtb); OOF composite avoids overfitting; capstone/demonstration re-using
MET2 signals (not a new discovery — the practical form of the MET1/MET2 finding); FBA essentiality medium-dependent; not
wet-lab.

## Reproducibility
Deterministic (mmseqs fixed; FBA cached; CV seeds fixed). Reproduce ×2 byte-identical (payload over per-organism ranking
metrics + top targets). Output: `experiments/MET3_composed_ranking/results/MET3_metrics.json`. Envs: bioinfo (mmseqs) +
intercepta-build.
