# BEATAML_NPM1_CABOZANTINIB — verification + deconfound pre-registration
Date 2026-07-29. Falsify-first verification (Constitution) of INTERCEPTA's strongest claim:
"NPM1-mut AML more sensitive to Cabozantinib, n=131 vs 399, p=2.9e-12 (BH-FDR sig of 1072 tests)."
Data: BeatAML probit AUC (beataml_probit_curve_fits_v4) + clinical (FLT3-ITD, NPM1). Deterministic; reproduce x2.

## Reproduce
NPM1-mut vs wt Cabozantinib AUC (lower AUC = more sensitive), Mann-Whitney; expect p<1e-6, NPM1 lower AUC, n~131/399.

## Decisive confound test (FLT3-ITD)
NPM1-mut AML is enriched for FLT3-ITD; Cabozantinib inhibits FLT3. So the apparent NPM1 effect may be
FLT3-ITD (known FLT3-inhibitor biology). Tests:
1. FLT3-ITD pos vs neg Cabozantinib AUC (is ITD itself a strong driver?).
2. WITHIN FLT3-ITD-negative patients: NPM1-mut vs wt Cabozantinib (does NPM1 survive without ITD?).
3. OLS auc ~ NPM1 + FLT3_ITD: is NPM1 coefficient independent (p<0.05)?

## PRE-REGISTERED verdict (frozen)
- REPRODUCED iff NPM1 vs wt p<1e-6, correct direction, n~131/399.
- NPM1 is an INDEPENDENT predictor iff within-ITD-negative NPM1 p<0.05 (same direction) AND OLS NPM1 coef p<0.05.
- Else: signal is (partly) FLT3-ITD-confounded = known FLT3-inhibitor biology (understanding, not novel).
Report exact values whichever way. No tuning.
