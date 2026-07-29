# Pre-registration — B20: INDEPENDENT external replication of V19 + V20 in the FIMM/Malani AML cohort (FINALIZED 2026-07-29, PRE-RESULT)

## The question (the one evidence standard V19/V20 have not met)
Every functional-inference result (V15–V20) is from a single patient cohort: BeatAML. External replication in an
INDEPENDENT cohort is the decisive missing test. We replicate in the FIMM/Malani AML cohort (Zenodo 7370747,
CC-BY 4.0; Malani et al., Cancer Discovery 2022) — a different institution (Helsinki), different assay (DSRT drug
sensitivity score, DSS) than BeatAML (OHSU probit AUC). If V19/V20 replicate here, they are not a BeatAML artifact.

## Data (public, downloaded, MD5-verified 3db5280e20f315d56d6bf07dd6a9e241)
- Expression: File_7 RNA-seq Log2CPM, 163 AML patients (Ensembl → HGNC symbol via local GENCODE map ensg2symbol.tsv).
- Drug response: File_3.2 DSS per (Sample_ID, drug). **DSS: higher = MORE sensitive** (opposite sign to BeatAML AUC).
- FLT3 inhibitors present in DSS: sorafenib, quizartinib, crenolanib, midostaurin, sunitinib, tandutinib, dovitinib
  (7; gilteritinib absent). BCL2 inhibitor: venetoclax.
- Mutations: File_6 binary, incl. FLT3 (FLT3-mutation; predominantly ITD in AML — used as the mutation covariate;
  NOT ITD-specific, stated honestly) and NPM1. Linked by Sample_ID (AML_xxx_xx) across all files.
- Inferred dependency: engine `fit_dependency(["FLT3","BCL2"])` on DepMap CRISPR (unchanged from V19/V20), applied
  to FIMM expression. R_prolif from FIMM expression.

## Sign convention
dep_score = −(inferred gene-effect) (higher = more dependent). DSS higher = more sensitive. **Sensitizing =
POSITIVE** Spearman(dep_score, DSS) / positive OLS coefficient. (Direction fixed a priori.)

## Hypotheses (assumed FALSE)
- **R1 (V19 core replicates):** inferred-FLT3-dependency predicts FLT3-inhibitor sensitivity (DSS), proliferation-
  adjusted, pooled across the 7 FLT3 inhibitors — pooled ρ>0, p<0.05.
- **R2 (V20 specificity replicates):** proliferation-adjusted double dissociation — matched (FLT3-dep→FLT3i,
  BCL2-dep→venetoclax) diagonal ρ > mismatched off-diagonal ρ, target↔drug-shuffle permutation p<0.05; and
  venetoclax predicted by BCL2-dep (ρ>0, p<0.05) not FLT3-dep.
- **R3 (V19 beyond-mutation replicates, bonus):** OLS `DSS ~ dep_score + FLT3_mut + R_prolif`, dep_score coefficient
  >0 (p<0.05) pooled across FLT3 inhibitors (adds beyond the mutation); and within FLT3-mutation-NEGATIVE patients,
  dep_score predicts FLT3i sensitivity (pooled ρ>0, p<0.05).
- H0 for each: null / wrong sign — the BeatAML finding does not generalize.

## Decision rule & interpretation (fixed)
Per drug ≥25 samples with DSS + dep + prolif. Pooled = sample-size-weighted Fisher-z (one-sided sensitizing).
- **R1 PASS** iff pooled prolif-adj ρ>0 & p<0.05. **R2 PASS** iff diagonal>off (perm p<0.05) & venetoclax
  BCL2-specific. **R3 PASS** iff meta dep coef>0 (p<0.05) & FLT3-mut-negative pooled ρ>0 (p<0.05).
- R1 pass → V19 core externally replicated (independent cohort/assay) — a materially stronger claim. R2 pass →
  target-specificity replicated. R3 pass → beyond-mutation value replicated. Any FAIL → honest bound on external
  validity (report which parts generalize and which are BeatAML-specific). All outcomes first-class.

## Honesty / scope
Ex-vivo (DSS), AML, dependency model pan-cancer-trained — same scope caveats as V19; B17 already bounds the clinical
endpoint. FIMM FLT3 mutation is not ITD-specific (a limitation vs BeatAML's ITD field). A null is fully expected
and first-class. No claim of clinical validity.

## Reproducibility
Deterministic (fixed permutation seed); reproduce ×2. Data sha256 in results. Output:
experiments/B20_fimm_external_replication/results/B20_metrics.json.
