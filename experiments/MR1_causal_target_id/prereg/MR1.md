# MR1 — transparent cis-MR causal target identification (PRE-REGISTRATION)

*Locked 2026-08-10, BEFORE inspecting any outcome (disease GWAS) data or computing any MR estimate.
Extends the program's one validated capability — target identification — into the human complex-disease
universe via a **self-computed, transparent, direction-aware causal instrument** (cis Mendelian
randomization), rather than reusing Open Targets' black-box aggregated `genetic_association`
(the GENETICS1 baseline). Falsify-first: the build is designed so that the most likely outcome
(OT-association subsumes MR) is a reportable HONEST NEGATIVE, not a hidden failure.*

## Motivation / prior state
- GENETICS1 established that OT's **aggregated** `genetic_association` enriches for clinical drug-target
  precedence (genetic support → higher clinical success). It is a black box (L2G/coloc/burden fused,
  no direction, no provenance).
- The field's gold-standard genetic target evidence is **cis-MR + colocalization** (transparent,
  mechanistic, direction-aware). MR-supported targets have ~2× clinical success (Nelson 2015; King 2019).
- MR1 asks whether a **transparent, self-computed** cis-MR signal (a) reproduces the genetic-support
  result and (b) **adds** predictive value beyond the public aggregate.

## Falsifiable hypotheses + decision gates (locked)
- **H1 (replication).** Genes with significant cis-MR causal evidence for a disease are enriched for
  clinical precedence vs the genome-wide base rate.
  - **Gate H1-PASS:** pooled-panel Fisher odds ratio (MR-significant vs not, for clinical=1) has
    **95% CI lower bound > 1.0**.
- **H2 (added value — the real test).** cis-MR carries clinical-precedence signal **beyond** OT
  `genetic_association`.
  - **Gate H2-PASS (BOTH required):**
    1. In logistic `clinical ~ OT_genetic_association + MR_score` (pooled), the **MR_score coefficient
       is positive with p < 0.05**; AND
    2. Adding MR_score improves **grouped 5-fold CV AUPRC** (folds = whole diseases, so a disease's pairs
       never split across folds) over the OT-only model by **ΔAUPRC ≥ 0.01 with a bootstrap 95% CI
       excluding 0** (2000 resamples, seed 42).
  - **H2-FAIL → HONEST NEGATIVE:** "transparent cis-MR reproduces the genetic-support signal (if H1
    passed) but does not add predictive value beyond the public aggregate." Still-valuable byproduct
    (transparent, direction-aware provenance) is reported as such; **no** predictive-upgrade claim.

## Method (transparent cis-MR; locked)
- **Instruments:** eQTLGen 2019 cis-eQTLs, FDR < 0.05 (blood, N≈31,684). Per gene, the **single strongest
  cis-eQTL SNP** (max |Z|) → **Wald-ratio MR** (needs no external LD panel; the primary, most robust cis
  design). eQTLGen Z→beta: `beta = Z / sqrt(2·MAF·(1−MAF)·(N + Z²))`, `se = 1 / sqrt(2·MAF·(1−MAF)·(N + Z²))`.
- **Outcome:** disease GWAS harmonized summary stats (GWAS Catalog **open** harmonized sumstats; no token).
  Extract the instrument SNP's `beta_gwas, se_gwas`, harmonize to the exposure **assessed allele**
  (flip sign on allele mismatch); **drop ambiguous palindromic SNPs** (A/T, C/G) with MAF in [0.40,0.60].
- **Estimate:** Wald ratio `theta = beta_gwas / beta_eqtl`; delta-method `se = se_gwas / |beta_eqtl|`;
  two-sided p from `theta/se`. **MR_score = −log10(p_MR)**; **MR-significant = p_MR < 0.05/n_tested**
  (Bonferroni within disease). Causal **direction = sign(theta)** is recorded (provenance byproduct).
- **Universe / labels:** restrict to (gene, disease) pairs present in the GENETICS1 dataset so
  `OT_genetic_association` and `clinical` (ChEMBL clinical-precedence, the ground truth) are defined;
  genes lacking a cis instrument get MR_score = 0 (tested = no).

## Panel (locked by open-sumstats availability, finalized in DATA.md before scoring)
Target 5 GENETICS1 diseases with open GWAS Catalog harmonized full sumstats. Priority candidates:
Alzheimer disease, coronary artery disorder, asthma, schizophrenia, IPF / (fallback: any GENETICS1
disease with harmonized sumstats). Final list + accessions recorded in `DATA.md` (which is written
before any H1/H2 statistic is computed).

## CORRECTION 2026-08-10 (forced by a positive-control failure; made before reading any MR H1/H2 result)
The locked universe ("(gene,disease) pairs present in the GENETICS1 dataset") is **selection-biased**: the
cached `genetics1_dataset.parquet` is an OT *evidence subset* (~6.4k genes/disease, 94% with some evidence),
not the genome-wide universe. On it, GENETICS1's **own validated positive control** — `genassoc>0` vs
`clinical>0` — **inverts** to OR **0.599** (p=1.7e-36) vs GENETICS1's reported **2.26**, because conditioning
on "has evidence" makes genetic and clinical evidence anti-correlated (a collider). A universe on which the
KNOWN positive is undetectable cannot test anything. **Correction:** rebuild the exact GENETICS1 genome-wide
universe — all **20,596 NCBI protein-coding symbols × the 5 diseases**, OT `gen`/`clinical` where present else
0 — and **require the OT positive control to reproduce (Fisher OR>1, CI-lower>1)** before any MR verdict is
read. This is not outcome-shopping: it is fixing a broken instrument so the known signal is detectable; the MR
result is reported whatever it is. Also add the **fame confounder** (NCBI gene2pubmed `logpub`, GENETICS1's
primary confounder) to H2 as context, since GWAS/eQTL power is fame-correlated.

## Rigor / integrity constraints
- **Reproduce ×2 byte-identical** (deterministic; fixed seeds; CV seed 42). `results/MR1_metrics.json`
  (sorted keys) + `payload.sha256`.
- **Aggregate outputs only** in the repo; **all raw GWAS/eQTL data stays in `$INTERCEPTA_DATA/mr1`**,
  never committed.
- Base-rate-fair reporting (OR / risk-ratio vs the genome-wide clinical base rate).
- No gate is changed after seeing outcomes; any deviation is appended as a dated CORRECTION with rationale.
- Negatives are first-class: an H2-FAIL is committed and reported as prominently as a pass.
