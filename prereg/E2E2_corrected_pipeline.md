# E2E2 — the CORRECTED zero-data front-half pipeline: what does therapeutic safety cost in recall? (finalized 2026-08-04, PRE-RESULT)

## Why
E2E1 composed a first zero-data pipeline but ranked targets by a conservation-dominated composite. FRONT1 then showed that
is THERAPEUTICALLY DANGEROUS — conservation promotes host-toxic targets (human core-essential homologs are the most
conserved) — and that soft selectivity doesn't fix it; the fix is a HARD host-non-homology FILTER. E2E2 builds the corrected
pipeline (mechanistic essentiality + hard host-non-homology filter + calibrated abstention) and answers the non-obvious,
decision-relevant question: **making the shortlist SAFE removes host-toxic targets by construction — but at what cost to
recovery of the real known targets?**

## Pipeline (zero-data, from genome; reuses MET2 GEMs + FRONT1 signals)
Per pathogen metabolic-subproteome gene: conservation C (mmseqs to other-org targets), essentiality E (MET2), chokepoint K
(FRONT1 cache), host non-homology S (mmseqs vs human proteome). Host-toxic = human homolog is a Hart-CEG2 core-essential gene.
- **NAIVE baseline (E2E1-style):** rank all genes by conservation C.
- **CORRECTED pipeline:** (1) HARD-FILTER out host-homologous genes (S=0); (2) rank the remaining host-non-homologous genes
  by an UNSUPERVISED mechanistic composite z(C)+z(E)+z(K) (no labels — truly zero-data); (3) ABSTAIN on genes with no
  conservation homolog (C=0) as low-confidence.
Shortlist = top-k (k = number of known targets in the organism). On M. tuberculosis (E2E1's pathogen) + E. coli.

## Hypotheses (pre-registered)
- **H1 (safety, expected by construction — quantify the naive risk):** corrected top-k contains ZERO host-toxic targets;
  the NAIVE conservation top-k contains N>0 host-toxic targets → quantify how many unsafe targets the naive recipe would
  shortlist.
- **H2 (recall cost — the real question):** what fraction of known targets is LOST to the hard filter (i.e. known targets
  that are host-homologous)? Compare known-target recall@k and precision@k: corrected (filtered+mechanistic) vs naive
  conservation. Report the safety/recall tradeoff explicitly.
- **H0/verdict is quantitative, not pass/fail:** the deliverable is the honest tradeoff — "the corrected pipeline removes all
  host-toxic targets and retains X% of known-target recovery, losing Y% of known targets that are host-homologous."

## Honesty / scope
Metabolic subproteome (FBA-blind non-metabolic half unaddressed); 2 bacteria; unsupervised composite (no fitting →
zero-data, may underperform a fitted ranker but is the honest zero-label pipeline); ChEMBL target ground-truth is
selection-biased toward host-nonhomologous druggable essentials (→ the recall cost of the filter may be UNDER-estimated vs
a truly novel pathogen whose real targets we don't know); CEG2 cell-line-derived; molecule-half (docking) stage is honestly
weak (C1/HIT2) → output is pose-plausible hypotheses, not potency-ranked leads; not wet-lab.

## Reproducibility
Deterministic (GEM/essentiality/chokepoint cached; mmseqs fixed; unsupervised composite = fixed z-score sum). Reproduce ×2
byte-identical (payload over per-organism safety + recall/precision metrics). Output:
`experiments/E2E2_corrected_pipeline/results/E2E2_metrics.json`. Envs: bioinfo (mmseqs) + intercepta-build.
