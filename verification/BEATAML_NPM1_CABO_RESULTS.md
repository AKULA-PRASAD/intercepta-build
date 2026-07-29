# BeatAML NPM1 + Cabozantinib — VERIFIED & DECONFOUNDED (reproduced ×2)
Date 2026-07-29. Falsify-first verification of INTERCEPTA's strongest claim. Real BeatAML patient data
(probit AUC + curated clinical FLT3-ITD/NPM1). Deterministic; reproduced ×2 identical.

## Result
- REPRODUCED: NPM1-mut more sensitive to Cabozantinib (lower AUC). n_mut=157, n_wt=425, median 144.5 vs 185.3
  (diff 40.8), Mann-Whitney p=4.4e-11. [Delta vs claim: claim reported n=131/399, p=2.9e-12 using WES-NPM1;
  I used curated-clinical NPM1 + per-subject median AUC → 157/425, p=4.4e-11. Same direction/magnitude; robust.]
- FLT3-ITD is the DOMINANT (known) driver: ITD+ vs ITD− p=5.1e-21 (median 123.2 vs 188.0). Cabozantinib
  inhibits FLT3 — established biology.
- NPM1 is INDEPENDENT of FLT3-ITD (survives deconfound):
  - Within ITD-negative: NPM1-mut vs wt p=3.1e-3, same direction (median 169.4 vs 189.0).
  - OLS auc ~ NPM1 + FLT3-ITD (n=582): NPM1 β=−21.9, p=3.3e-5; ITD β=−49.8, p=8.3e-19.
  - Co-occurrence: NPM1-mut 73/157 ITD+ vs NPM1-wt 68/425 ITD+ (enriched, as expected).

## Honest verdict
GENUINE, reproduced, FDR-context (65/1072), deconfounded association: NPM1 mutation independently predicts
Cabozantinib sensitivity in AML beyond FLT3-ITD. Caveats (Constitution — keep attacking): the FLT3-ITD effect
is ~2× larger; the NPM1-independent component (~20 AUC units) is modest and its mechanism is unresolved —
could still be residual FLT3-TKD (D835), DNMT3A/co-mutation, or a genuine NPM1 vulnerability. Remaining
confound tests before any strong claim: adjust for FLT3-TKD point mutations and DNMT3A; replicate in an
independent AML cohort (e.g., TCGA-LAML / a second inhibitor screen). Status: strongest INTERCEPTA result,
now independently verified & ITD-deconfounded; NOT yet mechanism-resolved or externally replicated.

## Extended deconfound (2026-07-29) — survives ALL major co-mutations
Full OLS auc ~ NPM1 + FLT3-ITD + FLT3-point + DNMT3A (n=582):
- NPM1 β=−16.7, p=2.6e-3 (independent); FLT3-ITD β=−49.2, p=3.2e-18 (dominant); FLT3-point β=−17.7, p=0.013; DNMT3A β=−12.2, p=0.038.
- Strictest subset (ITD-neg & FLT3-point-neg): NPM1-mut vs wt p=1.6e-2 (median 174.5 vs 192.3, n=64/326).
**NPM1 → Cabozantinib sensitivity is independent of FLT3-ITD, FLT3-point, and DNMT3A.** Effect shrinks as
confounders are added (β −21.9 → −16.7) but survives. Dominant driver remains FLT3-ITD (known FLT3-inhibitor
biology). Only remaining test before a strong claim: external replication in an independent AML cohort.
