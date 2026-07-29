# Pre-registration — B10: TCGA human clinical drug-response validation (FINALIZED 2026-07-29, pre-run)

## Why (and the honesty up front)
First test against REAL HUMAN PATIENTS on PUBLIC data (no gate): does the cell-line-trained transfer predict
actual TCGA clinical drug response? **This is the most CONFOUNDED test in the program** — observational, response
is to the whole REGIMEN (attributed per drug), cancer-type and stage differ across drug-treated groups, and
"response" (RECIST) is coarse. A well-powered NULL is fully expected and is a first-class result; any positive is
heavily caveated. We pre-commit the confound adjustments below.

## Data (public, no gate)
- Response: lifeome curated TCGA drug-response (drug_response.txt; responder = Complete/Partial Response,
  non-responder = Stable/Clinical Progressive Disease). 2572 pairs, 1197 patients, 28 cancers.
- Expression: UCSC Xena pancanatlas `EB++AdjustPANCAN_IlluminaHiSeq_RNASeqV2.geneExp` (gene symbols × TCGA
  samples, batch-corrected log2), matched to response patients by TCGA barcode (tumor -01 → patient).
- Transfer: engine trained on DepMap RNA-seq + PRISM AUC (broad drug coverage) and/or GDSC.
- Drugs: those with ≥20 labeled patients, ≥8 in EACH class, trainable (GDSC/PRISM), expression available.

## Hypotheses (assumed FALSE)
- **H1 (transfer→response):** across drugs, per-drug AUROC(transfer_pred → NON-response) has mean > 0.5,
  permutation p<0.05 (predicted-resistant patients respond worse).
- **H2 (adjusted):** in logistic `responder ~ transfer_pred + cancer_type + R_prolif`, transfer_pred coefficient
  is negative (higher predicted resistance → lower response) — pooled/meta across drugs, p<0.05.
- **H3 (drug-specific):** matched-drug prediction beats mismatched (diagonal>off-diagonal AUROC), perm p<0.05.
- H0: no association, or it vanishes after cancer-type/proliferation adjustment (→ confounded/uninformative).

## Decision rule (fixed)
Per drug: AUROC(transfer_pred, non-response); logistic adjusted coefficient. Pooled: mean AUROC + permutation
(k=2000, seed=42); DerSimonian–Laird meta of adjusted coefficients; BH-FDR across drugs. 
- H1 PASS iff mean AUROC>0.5 & perm p<0.05. H2 PASS iff meta coef<0 & p<0.05. H3 PASS iff diag>off & perm p<0.05.
- Report ALL. If H1 holds but H2 (adjusted) fails → association is confounded by cancer-type/proliferation
  (reported as such, NOT as validation).

## Honesty / scope
Regimen-vs-single-drug attribution, observational confounding, coarse RECIST → this cannot establish causal
drug-level prediction. Best case = "transfer prediction carries some real, cancer-type/proliferation-adjusted
signal for human response"; likely case = confounded/null. Either way recorded first-class.

## Reproducibility
Deterministic; seed=42, k=2000; reproduce ×2. Expression sha256 in data/MANIFEST.md. Aggregate outputs only
(no patient-level data committed). Output: `experiments/B10_tcga_outcome/results/B10_metrics.json`.
