# MET2 — Does MET1's "FBA-essentiality breaks the conservation ceiling" GENERALIZE across bacteria? (finalized 2026-08-02, PRE-RESULT)

## Why
MET1 found (on E. coli's curated iML1515) that mechanistic FBA gene-essentiality adds target-ID signal BEYOND the
conservation ceiling — the arc's first positive. Its main limitation was SINGLE ORGANISM (only iML1515 had a usable
UniProt gene mapping). MET2 tests generalization the clean way the user directed: **build metabolic models DE NOVO from
each organism's UniProt proteome (CarveMe)** so gene IDs are UniProt accessions by construction — sidestepping the
BiGG/strain/locus-tag mapping wall that blocked S. aureus/K. pneumoniae.

## Feasibility (verified 2026-08-02, before building)
CarveMe 1.6.6 + **SCIP (pyscipopt, free MILP solver)** + **diamond 2.2.4** all install and RUN on arm64 (no GPU). Carve
builds a GEM from a protein FASTA in ~10–25s; genes = the input UniProt accessions (verified: P21420, P06996…). Scope:
CarveMe uses a BACTERIAL universe → generalize across BACTERIA only (E. coli, M. tuberculosis, P. aeruginosa — the 3
with full proteomes + in-proteome ChEMBL targets from TID1).

## Data
De-novo CarveMe GEMs for ecoli/mtb/paeruginosa (from TID1 full proteomes, accession-keyed FASTA). Drug-target positives =
UniProt ChEMBL-xref (TID1). Conservation = mmseqs2 homology of GEM genes to OTHER panel organisms' targets (leave-org-out).

## MEDIUM (feasibility-driven decision, documented PRE-COMMIT)
Pre-planned glucose-aerobic MINIMAL medium (biologically-meaningful essentiality). **But M. tuberculosis and P.
aeruginosa do NOT grow on glucose-minimal** (Mtb is a lipid metaboliser; wt=0) — a consistent minimal medium is
infeasible across these bacteria. Decision: use CarveMe's **DEFAULT (complete) medium** for ALL organisms (consistent;
all grow). Genes essential on complete medium are the CORE indispensable genes (essential regardless of nutrients) —
arguably the MOST drug-relevant, but FEWER (E. coli 31 vs iML1515's 195). Trade-off documented; effect expected weaker
than MET1.

## Design (MET1's gene-level test, per-organism + pooled)
Per GEM gene (UniProt): FBA-essential (default medium, KO growth <1% WT) + is_drug_target + conservation. **H1
(enrichment):** drug-target rate among essential vs non-essential (odds ratio). **H2 (beyond conservation):** 5-fold-CV
nested ΔAUROC (conservation+essentiality vs conservation-only) + pooled partial coefficient. Per-organism + pooled.

## Hypotheses (pre-registered — SAME as MET1, tested for generalization)
- **H1 GENERALIZES:** essentiality enriches for drug targets (odds ratio > 1.5) in the MAJORITY of the 3 bacteria.
- **H2 GENERALIZES (the key claim):** essentiality adds beyond conservation (CV ΔAUROC > 0.02 AND coef_ess > 0.1) in
  ≥2/3 bacteria AND pooled → MET1's ceiling-break is NOT E.coli-specific.
- **H0 (first-class):** the ceiling-break does NOT replicate (≤1/3, pooled ≤0.02) → MET1 was E.coli/GEM-specific; the
  generalization fails honestly.

## Honesty / scope
De-novo CarveMe GEMs (default/complete medium → fewer, CORE essentials; weaker signal than curated iML1515, expected);
metabolic subproteome only; 3 bacteria (P. aeruginosa has only 20 in-GEM targets → underpowered); gene-level n well-
powered but organism n=3; not wet-lab. The generalization CLAIM is direction (does essentiality help beyond conservation
across bacteria), with honest per-organism variance reported.

## Reproducibility
Deterministic (FBA/LP deterministic given model+medium; mmseqs fixed; CV seeds fixed). GEMs + essentiality cached as data
artifacts (regenerable via build_essentiality_cache.py + carve). Reproduce ×2 byte-identical (payload over per-org +
pooled metrics). Output: `experiments/MET2_fba_generalization/results/MET2_metrics.json`. Envs: `metabolic` (carveme/
cobra/diamond/scip), `bioinfo` (mmseqs2), `intercepta-build` (analysis).
