# HARDENP1 — FBA essentiality on a 2nd host-dependent parasite (*Toxoplasma gondii*) — SUMMARY

**GATE: PASS — and it CORRECTS an overgeneralization.** The 2nd host-dependent parasite does the *opposite* of
the 1st. Orchestrator-verified (prereg frozen with both outcomes pre-allowed; same estimator as GENERALIZE5;
Sidik cutoff validated on the screen's own controls, not tuned; 550/556 mapped). Reproduced ×2 byte-identical.
**payload sha256:** `d4997e64eb7e8f699a7f047770737bf150cda3b8ab2916c21ee40e58fe1b5c9e`
**Evidence tier:** COMPUTED (in-silico enrichment vs a published CRISPR screen). n=1 additional parasite.

## Result
Curated *T. gondii* GEM **iTgo2020** (Krishnan 2020, Cell Host & Microbe; 556 genes) single-gene FBA deletion
vs **Sidik 2016** genome-wide CRISPR fitness (mean phenotype < −2). Over 550/556 mapped genes:
**OR 14.10, p 7.7e-33, precision 0.843, recall 0.511, AUROC 0.725 → PASS.** Contingency both 118 / FBA-only 22
/ exp-only 113 / neither 297. Robust across cutoffs (−1.5→15.07, −2→14.10, −3→9.56).

## Head-to-head with Plasmodium (GENERALIZE5)
| | *P. falciparum* (iPfal19/Zhang) | *T. gondii* (iTgo2020/Sidik) |
|---|---|---|
| OR | 2.47 — **FAIL** | **14.10 — PASS** |
| recall | **0.20** | **0.51** |
| precision | 0.80 | 0.84 |
| base rate | 0.64 | 0.42 |

## The correction (honest, important)
At n=1 we concluded "metabolic essentiality is the WRONG signal for host-embedded biology." **HARDENP1
falsifies that as a universal rule** — a second host-dependent parasite passes strongly. Disciplined restatement:
**FBA-essentiality transfer is MODEL/ORGANISM-specific, governed by whether the specific GEM's topology encodes
genuine biosynthetic dependence — NOT by host-embeddedness as a category.** The Plasmodium failure is most
plausibly iPfal19's pervasive salvage-bypass topology (the HOSTCTX1/2 root cause: essentials read dispensable →
recall 0.20) + high base rate, not host-dependence per se. iTgo2020 has a *fully open* medium too (so it's not
mere medium permissiveness) but far fewer spurious bypasses → recall 0.51.

## Honest confound
The two GEMs come from different curation teams and the two screens use different technologies (CRISPR vs
piggyBac), so the n=2 disagreement cannot be cleanly attributed to organism biology alone. A rigor win by
*correction of an overgeneralization*, not by another negative. Scope: enrichment only, in-silico vs published
screen, not wet-lab.
