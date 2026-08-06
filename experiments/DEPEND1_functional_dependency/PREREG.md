# DEPEND1 — Functional-dependency target-ID for host-embedded (cancer) biology — PRE-REGISTRATION

*Written and frozen BEFORE any scoring. Wave 3. The host-embedded analog of the bacterial FBA-essentiality
target-ID module. Rigor constitution: falsify-first, negatives first-class, reproduce ×2 byte-identical,
pre-registered numeric gates, mandatory pan-essential confound guard, mandatory leakage guard (split by
cell line).*

Date frozen: 2026-08-05. Seed: 42. K (permutations) = 2000.

---

## 0. Motivation (why this experiment, in one paragraph)
Three verified negatives (GENERALIZE5 + HOSTCTX1 + HOSTCTX2) proved metabolic FBA-essentiality is the WRONG
target-ID signal for host-embedded biology (parasites; by extension intracellular pathogens and human/cancer).
The unified redirection (FAILURE_AUDIT F2↔F3, COMPOSITE_ARCHITECTURE §2): host-embedded target-ID needs a
FUNCTIONAL-DEPENDENCY signal (CRISPR knockout fitness). DEPEND1 builds and validates that signal for cancer
cell-line biology with the same rigor as the bacterial essentiality arc (known-target recovery vs null;
out-of-sample generalization; a label-free arm).

## 1. Data (open, public; not committed)
- DepMap CRISPR gene-effect (Chronos), cell lines × genes; `depmap_crispr_gene_effect.csv`
  sha256 `d1633bfa0bf4719e72e564f15d9bcda7fddbbd3dac2a8a3aebf4898ac9f56f00` — 1095 lines × 17931 genes.
- DepMap sample metadata (lineage/context); `depmap_meta.csv`
  sha256 `382c0c26cf57a2fb82449f797c58cb0dfc2313949908d8f83560ebcf3e5bcbaa`.
- DepMap somatic mutations (MAF, with TCGA/COSMIC hotspot flags); `depmap_mut_try1.csv`
  sha256 `e99e43789c1c4821ccb737a45cd6f4fbbeac709c5a8cca326846d6d9a16cf5c8`.
- CCLE/DepMap expression TPM (label-free arm); `depmap_expression.csv`
  sha256 `6b8d5f3c00ce73a5e025922d52b74929e19359e323786a0314410762b0c08a16` — 1393 lines × ~19k genes.
- Release: DepMap/CCLE public (22Q2-era; ModelID ACH-* / Chronos gene-effect / `SYMBOL (ENTREZ)` columns).
  Provenance recorded by on-disk sha256 above (source: local DepMap public copy).

## 2. Definitions (frozen)
- **Dependent call:** Chronos gene-effect `< -0.5` in a cell line (standard threshold).
- **dependent_fraction(g)** = fraction of screened lines in which gene g is dependent.
- **PAN-ESSENTIAL** (confound to exclude from the target claim): `dependent_fraction > 0.90`.
- **SELECTIVE dependency** (the real, validatable target signal): `0.01 ≤ dependent_fraction ≤ 0.50`
  (dependent in a context-specific subset, not ~all lines).
- **Intermediate** (0.50–0.90) and **rare** (<0.01) reported separately.
- **Context-selectivity score** for gene g in context C:
  `sel(g,C) = mean(effect | lines NOT in C) − mean(effect | lines in C)`. Positive ⇒ g is MORE dependent
  (more negative effect) inside context C ⇒ candidate selective target for C. Genes are ranked DESCENDING by
  `sel`. (No model is trained for G1/G2 — this is a direct differential-dependency statistic.)

**MANDATORY PAN-ESSENTIAL CONFOUND GUARD:** we report n_pan_essential vs n_selective genome-wide, and we
report each pre-registered target's own dependent_fraction. A target that were pan-essential would be a trivial
(non-selective) "hit"; the primary claim is made ONLY about SELECTIVE dependency.

## 3. Pre-registered known-actionable target ⇄ context pairs (the oncology "9/9" analog)
Frozen list (10 pairs). Mutation contexts use activating **hotspot** mutations (isTCGAhotspot OR
isCOSMIChotspot) — the biologically correct definition of oncogene addiction. `n_ctx` = in-context CRISPR lines
(observed pre-scoring, for power only; does not alter gates).

| # | target | context | context definition | n_ctx |
|---|---|---|---|---|
| 1 | BRAF   | BRAF-hotspot   | lines with BRAF activating hotspot        | 94  |
| 2 | KRAS   | KRAS-hotspot   | lines with KRAS activating hotspot        | 170 |
| 3 | NRAS   | NRAS-hotspot   | lines with NRAS activating hotspot        | 54  |
| 4 | PIK3CA | PIK3CA-hotspot | lines with PIK3CA activating hotspot      | 112 |
| 5 | CTNNB1 | CTNNB1-hotspot | lines with CTNNB1 activating hotspot      | 41  |
| 6 | EGFR   | EGFR-hotspot   | lines with EGFR activating hotspot        | 22  |
| 7 | MDM2   | TP53-wildtype  | lines with NO non-silent TP53 mutation    | 391 |
| 8 | SOX10  | skin           | lineage == skin (melanoma master TF)      | 67  |
| 9 | PAX8   | ovary          | lineage == ovary (ovarian lineage dep.)   | 57  |
| 10| FLT3   | blood          | lineage == blood (AML/leukemia)           | 58  |

Excluded a priori with reason: **WRN | MSI** — no MSI-status annotation available in this data release
(cannot define the context without fabricating labels); recorded as an honest exclusion, not a failure.

## 4. Null models
- **Random-pair null (analytic):** a random gene ranked against a real context has P(top-K) = K / n_genes;
  for K=10, n_genes≈17931 ⇒ ~0.00056. Expected recovery@top-10 under null ≈ 0.0006.
- **Permutation null (per pair):** shuffle context labels K=2000× (fixed seed); recompute `sel` for the
  KNOWN target gene; one-sided p = (#{sel_null ≥ sel_obs}+1)/(K+1). Pooled across pairs.

## 5. PRE-REGISTERED GATES (fixed here, before scoring)
- **G1 (recovery vs null):** SELECTIVE-dependency recovers the known actionable targets well above null.
  - **PASS** if recovery@top-10 ≥ 0.60 (≥6/10 targets rank in the top-10 context-selective dependencies of
    their context) AND recovery ≫ the top-10 random null (~0.0006) with pooled permutation p < 0.01.
  - **PARTIAL** if recovery@top-1% (≈ top-179) ≥ 0.60 but recovery@top-10 < 0.60.
  - **NEGATIVE** otherwise.
- **G2 (out-of-sample generalization — leakage guard):** split cell lines 70/30 (seed 42, stratified by
  lineage). Compute `sel` INDEPENDENTLY on the held-out TEST lines only.
  - **PASS** if TEST recovery@top-10 ≥ 0.50 AND pooled TEST permutation p < 0.01 (signal replicates on
    disjoint lines — not an in-sample artifact).
  - **PARTIAL** if TEST recovery@top-1% ≥ 0.50 but @top-10 < 0.50. **NEGATIVE** otherwise.
- **G3 (label-free expr→dependency):** for each actionable target gene, train Ridge on z-scored expression
  (top-2000 most-variable genes) → Chronos gene-effect, 5-fold CV SPLIT BY CELL LINE (KFold shuffle, seed 42);
  report out-of-fold Spearman ρ(pred, true). Baseline = the target gene's OWN expression → its dependency
  (ρ_own). This is the analog of predicting essentiality for a novel pathogen with no CRISPR screen.
  - **PASS** if median CV ρ(model) across the actionable targets ≥ 0.20 AND model beats the own-expression
    baseline (paired sign/permutation p < 0.05).
  - **PARTIAL** if median CV ρ(model) ≥ 0.20 but does not beat the own-expression baseline (still label-free
    predictive, no gain over the trivial feature).
  - **NEGATIVE** if median CV ρ(model) < 0.20.

## 6. Guards (all mandatory)
1. **Pan-essential separation** (§2) — primary claim only about SELECTIVE dependency.
2. **Leakage guard** — G2 splits BY CELL LINE, stratified by lineage; TEST `sel` uses TEST lines only.
3. **Lineage confound** — reported: lineage composition of each mutation context (an oncogene-addiction
   "hit" could be a lineage artifact). Reported as a diagnostic, not a gate.
4. **Scope honesty** — this is cancer cell-line dependency (Chronos), NOT patient/clinical, NOT a
   novel-pathogen wet-lab result. Stated in every claim.

## 7. Reproducibility
All RNG seeded (42). Payload = sorted-key JSON of all numeric results EXCLUDING `verdict`/provenance
(`git_sha`,`timestamp_utc`,`python`,`sklearn`). Script run twice; SHA-256 of payload printed and matched;
`results/payload.sha256` written. NEVER git commit/push. NEVER commit data.
