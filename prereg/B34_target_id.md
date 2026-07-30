# Pre-registration — B34: target identification — does evidence predict clinical target success BEYOND popularity? (FINALIZED 2026-07-30, PRE-RESULT)

## The question (pipeline module #1; confound-first, like B10)
The head of the discovery pipeline is target identification: which gene, for a given disease, is a good drug
target? The field's landmark finding (Nelson 2015) is that human **genetic** evidence enriches for clinical
success. But target-disease "success" labels are heavily **publication/popularity-biased** — well-studied targets
both get drugs AND accumulate evidence. So the honest question (mirroring B10's cancer-type-confound discipline):
**does genetic / functional evidence predict which target-disease pairs have reached the clinic BEYOND a study-
popularity baseline?**

## Data (OPEN — Open Targets Platform v26.06; fetched by us, cached)
`experiments/B34_target_id/collect_data.py` fetched **12,000 target-disease pairs** across a fixed, diverse
40-disease panel (oncology, immune, metabolic, neuro, cardio, renal, respiratory, musculoskeletal), each with
per-datatype evidence scores. Cached `ot_target_disease.parquet` (sha256 `d14006e8…`, recorded in `data/MANIFEST.md`
+ `ot_meta.json`). Clinical-positive rate 29.3%.

## Label, features, confound
- **Label (reached clinic for this disease):** `clinical` datatype score > 0 (≥1 clinical-stage/approved drug for
  that target-disease). 29.3% positive.
- **Non-clinical evidence features (6):** genetic_association, genetic_literature, somatic_mutation,
  affected_pathway, animal_model, rna_expression. (`clinical` is the label → EXCLUDED from features = leakage control.)
- **Popularity/confound proxy:** `literature` (text-mining co-mention volume) — the study-bias axis to control for.

## Design (leave-disease-out — generalize to unseen diseases)
GroupKFold by `disease_id` (5 folds over the 40 diseases), so the test asks whether evidence predicts clinic-reached
targets in DISEASES the model never saw — not memorizing known target-disease pairs. Models (L2-logistic unless
noted), reported as leave-disease-out mean±sd AUROC/AUPRC:
1. **Trivial** (base rate 0.293).
2. **Popularity baseline** — `literature`-only.
3. **Genetic-only** — `genetic_association`-only.
4. **Full non-clinical** — all 6 non-clinical features.
5. **Full + literature** — 6 features + literature (does popularity dominate?).
Plus a full-data logistic to report signed coefficients (is genetic_association's contribution positive with
literature in the model?).

## Hypotheses (assumed FALSE)
- **H1 (naive usefulness):** full non-clinical AUROC > 0.5 and > trivial.
- **H2 (the decisive confound test):** genetic/functional evidence predicts clinical success **beyond popularity** —
  BOTH (a) genetic_association-only AUROC > 0.5 by >1sd, AND (b) full-non-clinical AUROC > literature-only AUROC by
  >1sd (evidence adds over study-volume), AND genetic_association keeps a positive coefficient with literature in
  the model.
- **H0 (the B10-style null):** once `literature` (popularity) is controlled, non-clinical/genetic evidence does NOT
  beat the popularity baseline → target "success" is largely study-bias-confounded (a decisive first-class negative).

## Decision rule & interpretation (fixed)
- **H2 PASS** → genetic/functional evidence carries real, popularity-independent target-ID signal → report it
  honestly (effect size), and SHIP a transparent `TargetPrioritizer` (ranks candidate targets for a disease by
  evidence, with the honest caveat that it is enrichment, not proof). 
- **H2 FAIL / H0** → target-success prediction here is popularity-confounded (parallel to B10's clinical null) →
  first-class negative; do NOT ship a predictor that just re-ranks by how well-studied a target is.

## Honesty / scope
Open Targets scores are themselves derived from curated evidence (some circularity is unavoidable); `literature`
and `genetic_literature` are text-mining and popularity-tinged; `genetic_association` (GWAS-based) is the cleanest
signal. Association ≠ validated target; leave-disease-out enrichment ≠ prospective success. No clinical claim.

## Reproducibility
Data acquisition (API fetch) is one-time and version-pinned (v26.06, sha recorded); the MODEL runs on the cache and
is deterministic (seed=42; GroupKFold fixed) — reproduce ×2 byte-identical (payload sha256). Output:
`experiments/B34_target_id/results/B34_metrics.json`.
