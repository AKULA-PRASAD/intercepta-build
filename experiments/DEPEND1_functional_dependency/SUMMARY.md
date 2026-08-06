# DEPEND1 — Functional-dependency target-ID for host-embedded (cancer) biology — SUMMARY

**Verdict: G1 PASS · G2 PASS · G3 PASS.** The host-embedded analog of the bacterial FBA-essentiality
target-ID module is VALIDATED for cancer cell-line biology: SELECTIVE CRISPR dependency recovers known
clinically-actionable targets far above null, the signal GENERALIZES to disjoint held-out cell lines (no
leakage), and a LABEL-FREE expression->dependency model predicts dependency out-of-sample and beats the
own-expression baseline. Reproduced x2 byte-identical.

- DepMap release: DepMap/CCLE public (22Q2-era; Chronos CRISPRGeneEffect, ModelID ACH-*).
- Payload SHA-256 (reproduced x2): a7b57531de5e99dcff796cda8eabb1fe06cd84db9c187d7b334118c3d95de5dc
- Env: scikit-learn 1.8.0, CPU-only. Seed 42, K=2000. Aggregate outputs only; no data committed.

## Data (open; sha256 in PREREG section 1)
CRISPR gene-effect 1095 cell lines x 17931 genes; sample metadata (lineage); somatic MAF (TCGA/COSMIC
hotspot flags); CCLE expression (label-free arm, 988 lines shared with CRISPR).

## Mandatory pan-essential confound guard (the first false claim guarded)
Genome-wide separation of dependent-fraction:
| class | definition | n genes |
|---|---|---|
| PAN-ESSENTIAL | dependent in >90% of lines | 1020 |
| SELECTIVE | dependent in 1-50% of lines | 3664 |
| intermediate | 50-90% | 562 |
| rare | <1% | 12685 |

All 10 pre-registered actionable targets are SELECTIVE, none pan-essential (dependent fraction
0.008-0.416). The primary claim is made only about selective dependency; pan-essential genes (ribosome/
proteasome/etc.) are explicitly separated and never counted as target-discovery successes.

## G1 — known-actionable recovery vs null (all lines): PASS
recovery@top-10 = 0.80 (8/10), recovery@top-1% = 0.90 (9/10), pooled permutation p = 5.6e-21,
vs random-pair null recovery@top-10 ~ 0.0006. Rank of each target among ~17931 genes' context-selectivity:
BRAF 1, KRAS 1, NRAS 1, PIK3CA 1, CTNNB1 1, MDM2 (in TP53-WT) 1, SOX10 (skin) 1, PAX8 (ovary) 1;
EGFR 38 (top-1%, not top-10; only 22 hotspot lines); FLT3 (blood) 557 — MISS.
- Honest miss FLT3: dependent in only 0.8% of lines; FLT3 dependency is specific to FLT3-ITD/mutant AML,
  not the whole blood lineage, so a lineage-level context does not recover it. Correctly counted as a miss.
- Honest partial EGFR: recovered in top-1% but not top-10; small hotspot context (n=22) + EGFR
  dependency concentrates in the EGFR-amplified/mutant NSCLC subset.

## G2 — out-of-sample generalization (leakage guard; the second false claim guarded): PASS
Cell lines split 70/30 (769 train / 326 test), stratified by lineage; context-selectivity recomputed on the
held-out TEST lines only (disjoint cell lines — no line in both). TEST recovery@top-10 = 0.80 (8/10),
@top-1% = 0.90, pooled TEST permutation p = 9.0e-21. Concordant with train (0.80/0.90). The same 8 targets
are top-selective on completely disjoint lines => the signal is NOT an in-sample artifact.

## G3 — label-free expr->dependency (the North-Star-relevant arm): PASS
Ridge on z-scored expression (top-2000 variable genes) -> Chronos gene-effect, 5-fold CV split by cell line.
Median out-of-fold Spearman rho(pred, true) = 0.358. Per target rho: MDM2 0.58, EGFR 0.56, PIK3CA 0.44,
CTNNB1 0.43, KRAS 0.38, BRAF 0.33, SOX10 0.33, PAX8 0.32, FLT3 0.14, NRAS 0.13.
Fair baseline = the target gene's OWN expression (predictive strength |rho|, since higher expression predicts
dependency => negative signed rho): median |rho|(model) 0.358 vs median |rho|(own-expr) 0.201, paired
permutation p = 0.003. The full transcriptome adds predictive power beyond the single self-expression feature
and predicts dependency for held-out lines from expression alone — the analog of predicting essentiality for a
novel host-embedded organism with no CRISPR screen.

## What this closes and its honest scope
- Resolves the F2<->F3 redirection: where metabolic FBA fails for host-embedded biology (three verified
  negatives), a functional-dependency signal succeeds with the same rigor (known-target recovery vs null +
  out-of-sample generalization + a label-free arm) as the bacterial essentiality module.
- Populates the COMPOSITE_ARCHITECTURE "human/cancer -> functional dependency" cell from HYPOTHESIS toward a
  validated, out-of-sample, label-free-capable module.
- Scope boundaries (stated, not hidden): cancer cell-line Chronos dependency — NOT patient/clinical, NOT a
  novel-pathogen wet-lab result. Lineage-level contexts miss mutation-subset dependencies (FLT3). Selectivity
  is a differential-dependency statistic on public screens; the label-free arm is validated on held-out DepMap
  lines, not yet on an organism with no screen at all.

## Reproducibility
run.py -> results/DEPEND1_metrics.json (sorted keys) + results/payload.sha256. Payload SHA-256 over
sorted-key JSON of all numeric results (excludes verdict/provenance); run twice, identical. Seeds fixed (42).
No git commit/push; no data committed.
