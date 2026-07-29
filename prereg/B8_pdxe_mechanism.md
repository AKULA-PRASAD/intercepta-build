# Pre-registration — B8: engine mechanism layer + V10 integration on PDXE (solid tumors) (FINALIZED 2026-07-29, pre-run)

## Question
Does the engine's mechanism-anchored integration (marker + transfer, V10) hold in the PDXE solid-tumor cohort
using ESTABLISHED solid-tumor marker→drug biology — and do the markers themselves validate (sensitizing) there?

## Frozen marker→drug pairs (a priori established biology; declared before running)
1. **PIK3CA (functional mut) → alpelisib** (PI3Kα inhibitor; FDA-approved for PIK3CA-mut breast) — sensitizing.
2. **PIK3CA (functional mut) → buparlisib** (pan-PI3K) — sensitizing.
3. **RAS (KRAS or NRAS functional mut) → trametinib** (MEK inhibitor) — sensitizing.
(BRAF→encorafenib added only if ≥8 mutant models with single-agent encorafenib.)
"Functional mut" = PDXE Category ∈ {MutKnownFunctional, MutLikelyFunctional} (excludes MutNovel VUS + CN Amp/Del).

## Data (public PDXE; no gate)
Transfer from the engine (DepMap RNA-seq + GDSC). Test = PDXE BestAvgResponse (higher=resistant), PDXE
functional mutations, R_prolif from PDXE RNA. Per model.

## Model + hypotheses (assumed FALSE)
Per pair, OLS `BAR ~ marker + transfer_pred + R_prolif` (models with drug BAR + expression + mut status; ≥8 mut):
- **H_marker:** marker partial p<0.05, β<0 (sensitizing) — the mutation predicts sensitivity in PDXE.
- **H_engine (V10):** 5-fold CV Spearman of combined (marker+transfer) predicting BAR > BOTH transfer-only and
  marker-only.

## Decision rule (fixed)
- Markers: BH-FDR across pairs on marker p; a pair's marker VALIDATES iff BH-q<0.05 & β<0.
- Engine>parts: count pairs where combined CV beats both singles. Overall PASS iff ≥ half of pairs.
- These are ESTABLISHED associations → they double as positive controls: PIK3CA→alpelisib especially SHOULD
  validate, or the PDXE mechanism pipeline is flawed.

## Honesty / scope
PDXE = patient-proxy (xenograft), solid tumors. Small n per pair (trametinib ~37 models). Established biology
→ confirmatory, not novel. A null on PIK3CA→alpelisib would indicate a pipeline/power problem, reported as such.

## Reproducibility
OLS deterministic; CV seed=42; reproduce ×2. Output: `experiments/B8_pdxe_mechanism/results/B8_metrics.json`.
