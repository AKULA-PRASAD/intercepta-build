# MET4 — Mechanism BEYOND metabolism: does PPI-network centrality break the conservation ceiling for NON-metabolic targets? (finalized 2026-08-03, PRE-RESULT)

## Why (the honest gap MET1–MET3 leave open)
MET1–MET3 proved FBA gene-essentiality is a mechanistic, non-homology signal that breaks the conservation ceiling — but
ONLY for METABOLIC targets (FBA is blind to the ~half of drug targets that are non-metabolic: proteases, polymerases,
ribosomal/structural — exactly the kind a novel pandemic often presents, e.g. Mpro). MET4 asks: is there a mechanistic,
non-homology signal for NON-metabolic targets? Candidate = **PPI-network topology essentiality** (Jeong 2001
lethality-centrality; Yu 2007 bottlenecks): network hubs/bottlenecks are enriched for essential/important genes,
independent of sequence homology — IF the network is measured, not homology-inferred.

## THE circularity trap (and its control — the crux)
STRING's `combined_score` fuses homology-transferred channels → naive centrality could be CIRCULAR with conservation
(centrality proxying homology). Control: STRING's per-channel `full` file exposes a DIRECT `experiments` channel (neither
homology-derived nor cross-species-transferred). We build TWO networks and require the signal to survive on the clean one:
- **FULL** network: `combined_score >= 700` (high-confidence but homology-laden) — the naive test.
- **EXPERIMENTAL** network: direct `experiments >= 400` (11,650 E. coli edges; non-homology, non-transferred) — the HONEST test.
A beyond-conservation lift counts as a genuine non-homology mechanistic signal ONLY if it survives on the EXPERIMENTAL network.

## Data (fetched, feasibility-verified 2026-08-03)
E. coli K-12 STRING v12 (taxid 511145): 984,760 edges, 4,093 proteins mapped to UniProt_AC (mapping WORKS — no MET2
locus-tag wall). Drug-target positives = UniProt ChEMBL-xref (TID1). Conservation = mmseqs2 best-bits of each protein to
OTHER panel organisms' targets (leave-E.coli-out; identical to MET1/MET3). NON-metabolic subproteome = E. coli proteins
NOT in the MET2 CarveMe GEM gene set (the FBA-blind half) — the population MET4 is specifically about.

## Design (mirrors MET1/MET3, on the NON-metabolic subproteome)
Per node (non-metabolic E. coli protein, mapped + in STRING): conservation C; degree + betweenness centrality on the FULL
network and on the EXPERIMENTAL network (4 centrality features). y = is_drug_target.
- **H1 (enrichment):** top-quartile-centrality drug-target rate vs rest (odds ratio), each network.
- **H2 (beyond conservation — the claim):** 5-fold-CV nested ΔAUROC (C + centrality vs C-only) + centrality partial
  coefficient, computed SEPARATELY for FULL and EXPERIMENTAL networks.
- **Circularity control (decisive):** compare ΔAUROC_experimental vs ΔAUROC_full. Genuine iff experimental survives.
Also report the full-proteome (metabolic+non-metabolic) numbers for context, but the pre-registered CLAIM is on the
non-metabolic subproteome + experimental network.

## Hypotheses (pre-registered)
- **H1:** centrality enriches for non-metabolic drug targets (OR > 1.5) on the EXPERIMENTAL network.
- **H2 (the claim):** centrality adds beyond conservation (CV ΔAUROC > 0.02 AND |coef_centrality| > 0.1) on the
  EXPERIMENTAL network → a genuine non-homology mechanistic signal for NON-metabolic targets → mechanism extends beyond
  metabolism.
- **H0 (first-class):** no beyond-conservation lift on the experimental network (lift only on the homology-laden full
  network, or none) → network centrality is NOT a clean non-homology signal for non-metabolic targets; mechanism (as
  tested) stays metabolism-bound. Reported plainly as the honest boundary.

## Honesty / scope (foregrounded)
- **Novel-pathogen caveat (critical):** even a POSITIVE requires a MEASURED experimental PPI network, which a truly-novel
  pathogen LACKS → this would be an in-domain / well-studied-pathogen capability, NOT a zero-data-novel-pathogen one.
  Stated prominently in any positive verdict.
- Single organism (E. coli — in-domain existence test, like MET1; generalization deferred); non-metabolic subproteome;
  gene-level n well-powered but organism n=1; STRING experimental channel is sparse (avg degree low → betweenness noisy);
  not wet-lab.

## AMENDMENT (2026-08-03, PRE-COMMIT — before recording any verdict): STUDY-BIAS control added
The original design controlled only HOMOLOGY circularity (experimental vs full network). Re-examination surfaced a
second, more severe confound the homology control does NOT remove: **STUDY/ANNOTATION BIAS**. Drug targets are the
most-studied proteins → they accumulate more EXPERIMENTAL PPI edges simply from research attention (reverse causation:
drug-target → studied → more assays → higher degree), independent of any biological centrality. The experimental channel
is exactly where study bias lives. Two controls added PRE-COMMIT (making the test strictly harder before looking at
whether it passes):
1. **Study-intensity covariate** = textmining-channel degree (literature-prominence proxy). Primary H2 test becomes: does
   centrality add beyond **[conservation + study-intensity]** (not just beyond conservation)?
2. **Coexpression network** (direct `coexpression` col8, measured genome-wide, non-homology, NOT inflated by per-protein
   study effort) as a study-bias-ROBUST arbiter. A genuine mechanistic signal should survive here.
Revised claim: H2 counts as a genuine non-homology, non-study-bias mechanistic signal ONLY if the beyond-conservation
lift survives (a) conditioning on study-intensity AND (b) appears on the unbiased coexpression network. If it collapses
under these, MET4 is a first-class NEGATIVE — PPI-network target-ID for non-metabolic targets is largely a study-bias
artifact (unlike the genuinely mechanistic FBA signal), an important honest distinction.

## Reproducibility
Deterministic (STRING files pinned as data artifacts; mmseqs fixed params; networkx degree/betweenness deterministic; CV
seed 42). Reproduce ×2 byte-identical (payload over per-network H1/H2 metrics on the non-metabolic subproteome). Output:
`experiments/MET4_mechanism_beyond_metabolism/results/MET4_metrics.json`. Envs: bioinfo (mmseqs), intercepta-build
(networkx/sklearn). Data: STRING v12 511145 links.full + aliases (MANIFEST).
