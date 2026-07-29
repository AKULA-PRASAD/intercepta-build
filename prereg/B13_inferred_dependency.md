# Pre-registration — B13: can EXPRESSION-inferred dependency recover the functional signal? (FINALIZED 2026-07-29, PRE-RESULT)

## Rationale (follows directly from B12/V15)
B12 proved functional gene-dependency predicts drug response and beats baseline target expression (median |ρ|
0.134 vs 0.071). But dependency is unmeasurable in patients. **If dependency is predictable from expression**
(measurable in patients), a two-step **expression → inferred-dependency → drug** layer could carry the functional
signal into any expression-only cohort. B13 tests this directly on DepMap (expression + CRISPR + drug, same cells).

## Data (public, in hand)
DepMap expression + CRISPR gene-effect + PRISM/GDSC response. Target genes from B12 with significant
dependency→drug: MDM2, EGFR, PIK3CA, MAP2K1, CDK6, BRAF, FLT3 (as available).

## Method (leakage-controlled)
Per target gene g: 5-fold CV Ridge (DepMap expression, top-2000 genes → CRISPR effect[g]); out-of-fold
**predicted dependency dep̂[g]** (drug response NEVER used here). Then per (drug, g):
- inferred-functional predictor: Spearman(dep̂[g], drug response)
- baseline comparator: Spearman(target expression[g], drug response)  [B12's rho_expr]
- upper bound: Spearman(true dependency[g], drug response)            [B12's rho_dep]

## Hypotheses (assumed FALSE)
- **H0a (dependency is learnable):** CV ρ(dep̂[g], true dep[g]) > 0 for target genes.
- **H1 (inference adds):** across (drug,g), |ρ(dep̂, drug)| > |ρ(target-expression, drug)| — routing through
  inferred dependency beats direct target expression — paired permutation p<0.05.
- **H2 (signal recovered):** ρ(dep̂, drug) recovers a meaningful fraction of the true-dependency upper bound.

## Decision rule (fixed)
Report CV expr→dep ρ per gene. Pooled paired test |ρ_inferred| vs |ρ_expr| across pairs, permutation k=2000
seed=42, BH per pair. **H1 PASS** iff median(|ρ_inferred|−|ρ_expr|)>0 and perm p<0.05. Recovery fraction =
mean(ρ_inferred / ρ_true) over pairs where ρ_true>0.1.

## Interpretation (fixed)
- H0a+H1 pass → an expression→dependency functional layer is real and improves over baseline expression → a
  genuine, novel, patient-translatable architecture (needs only expression at inference). The most promising
  advance in the program — to then be tested in the Track-1 cohort.
- H1 fail → inference does not beat direct expression (dependency not learnable enough); honest bound.

## Honesty / scope
Still cell-line for training/validation; patient translation is a hypothesis for Track-1, not proven here.
Effect sizes reported honestly; a null is first-class.

## Reproducibility
Deterministic (CV seed=42; perm seed=42, k=2000); reproduce ×2. Output: experiments/B13_inferred_dependency/results/B13_metrics.json.
