# FRONT1 — Selective mechanistic target discovery (the front-half chapter): does mechanism + selectivity beat conservation AND avoid host-toxic targets? (finalized 2026-08-04, PRE-RESULT; run HELD until HIT2 completes)

## Why (the biggest capability gap, built on the one signal that worked)
The capability map marks the FRONT HALF — mechanism inference + selectivity — as ✗ absent. The MET line taught the lesson:
MECHANISM computed from a pathogen's own biology (FBA essentiality), not homology, is the ONE signal that broke the
conservation ceiling. FRONT1 deepens it into the established antimicrobial-target framework (subtractive genomics:
essentiality + metabolic CHOKEPOINT + HOST NON-HOMOLOGY), done FULLY ZERO-DATA (CarveMe GEM from genome + human-homology),
and — the step the field's case-study papers skip — BENCHMARKED against the conservation baseline with nulls and, crucially,
tested for THERAPEUTIC VALIDITY (does it avoid host-toxic targets?), not just target recovery.

## Data (feasibility-verified 2026-08-04; inputs on hand)
7 bacteria with MET2 CarveMe GEMs + cached FBA essentiality (E.coli, M.tuberculosis, P.aeruginosa, B.subtilis, H.pylori,
Salmonella, E.faecalis). Human proteome local (tid1/proteomes/human.fasta) for host non-homology. Drug-target positives =
UniProt ChEMBL-xref (TID1). Human essential-gene list (for H2 host-toxicity) = a public set (DepMap common-essential or
OGEE human), mapped to UniProt — the one input to source at build.

## Signals per pathogen metabolic-subproteome gene (UniProt-keyed)
- **C = conservation** (mmseqs best-bits to OTHER panel organisms' targets; the MET baseline).
- **E = FBA essentiality** (MET2 cache; the mechanism signal that broke the ceiling).
- **K = metabolic CHOKEPOINT** (binary): the gene catalyzes a reaction that is the UNIQUE producer OR unique consumer of
  some metabolite in the GEM. Currency metabolites (h, h2o, atp/adp, nad(p)(h), pi, ppi, co2, o2, coa, etc.) and
  exchange/transport reactions EXCLUDED (else trivial). Standard Yeh-2004/Rahman-2008 definition.
- **S = host NON-homology** (selectivity): no significant mmseqs hit of the pathogen protein to the human proteome
  (e-value threshold pre-set); S=1 means safe-to-hit (absent from host).

## Hypotheses (pre-registered)
- **H1 (recovery — does mechanism+selectivity ADD beyond conservation+essentiality):** 5-fold-CV nested ΔAUROC, on the 2
  reliably-testable bacteria (E.coli, Mtb; MET2). Test [C+E+K+S] vs [C] (>0.02) AND vs [C+E] (does K+S add beyond
  conservation+essentiality, ΔAUROC>0.01) + partial coefficients. **CIRCULARITY CAVEAT (foregrounded):** known drug
  targets are ALREADY selected to be druggable host-nonhomologous essentials, so S/E predicting y is partly ground-truth
  SELECTION bias, not "better biology" — H1 measures predictive value honestly but its interpretation is confounded by the
  ground truth. This is why H2 is the cleaner test of the CAPABILITY.
- **H2 (THERAPEUTIC VALIDITY — the differentiator the field skips):** define HOST-TOXIC pathogen genes = those WITH a human
  homolog whose human ortholog is ESSENTIAL (human essential-gene list). Does the selective composite rank host-toxic genes
  LOWER than the conservation baseline does? Metric: AUROC / mean-rank of host-toxic-vs-rest under [C+E+K+S] vs under [C];
  the selective composite should DOWN-rank host-toxic genes (lower host-toxic AUROC-as-target). This tests we find
  SELECTIVE (safe) targets, not merely recoverable ones — the front-half therapeutic-reasoning capability, and it is NOT
  circular with the ChEMBL ground truth.
- **H0 (first-class):** K+S add nothing beyond C+E (H1) and/or the composite does not down-rank host-toxic genes (H2) →
  chokepoint+selectivity are not a usable zero-data front-half improvement here; reported plainly.

## Controls / robustness
Permutation null; currency-metabolite exclusion sensitivity for K; host non-homology e-value sensitivity; the nested
ΔAUROC (K+S beyond C+E) controls for conservation/essentiality already carrying the signal; per-organism + the 2-reliable
pooled. Report all 7 organisms' H1 descriptively (only E.coli+Mtb powered, per MET2).

## Honesty / scope
Metabolic subproteome only (FBA-blind to non-metabolic targets — the MET4 boundary still applies); 7 bacteria (2 reliably
testable); ChEMBL target ground-truth is selection-biased (→ H1 partly circular, H2 designed to avoid it); chokepoint is a
topological heuristic (not flux-validated); host non-homology = sequence threshold (not structural); human essential list
is cell-line-derived (imperfect host-toxicity proxy); retrospective, in-silico, open data; not wet-lab. The CLAIM is the
capability direction (does zero-data mechanism+selectivity improve recovery AND therapeutic validity), with honest
per-organism variance + the circularity caveat foregrounded.

## Reproducibility
Deterministic (GEM/FBA cached; mmseqs fixed; chokepoint = deterministic stoichiometry pass; CV seed 42). Reproduce ×2
byte-identical (payload over per-organism H1 + H2 metrics). Output:
`experiments/FRONT1_selective_mechanistic_targets/results/FRONT1_metrics.json`. Envs: metabolic (cobra), bioinfo (mmseqs),
intercepta-build (analysis). Data: MET2 GEMs + human proteome + human essential list (MANIFEST). **RUN HELD until HIT2
docking completes (avoid two build threads / CPU contention).**
