# Pre-registration — B7: EXTERNAL validation on PDXE (public patient-derived xenografts) (FINALIZED 2026-07-29, pre-run)

## Why this matters
First truly EXTERNAL test of the transfer/engine: a cohort independent of both BeatAML AND cell lines. PDXE
(Gao et al. 2015 Nat Med; public, sha256 in data/MANIFEST.md) = ~399 patient-derived xenografts with RNA-seq +
per-model treatment response (BestAvgResponse). Executes protocol R1/R2/R5 from SECOND_COHORT_VALIDATION.md.

## Data (public, no gate)
Train: DepMap RNA-seq + GDSC2 LN_IC50 (the engine). Test: PDXE RNAseq_fpkm (genes×399 PDX) + PCT curve metrics
(BestAvgResponse per model×treatment). Single-agent drugs mapping GDSC↔PDXE (Novartis codes→generics) with ≥15
PDX models & a GDSC training model: **9 drugs** — ribociclib, buparlisib, alpelisib, paclitaxel, tamoxifen,
trametinib, gemcitabine, dacarbazine, erlotinib.

## Hypotheses (assumed FALSE)
- **H1 (R1 transfer replicates):** mean diagonal per-drug ρ(engine transfer_pred, BestAvgResponse) > 0,
  permutation p<0.05 (higher predicted LN_IC50 = resistant = higher BAR → positive ρ).
- **H2 (drug-specific beyond proliferation):** proliferation-residualized diagonal ρ > off-diagonal ρ AND >0,
  permutation p<0.05 (the V9 drug-specificity claim, tested in a NEW cohort/cancer set).
- H0: no transfer to PDXE, or transfer is entirely generic proliferation.

## Metric + decision rule (fixed)
Per drug (≥15 PDX models): diagonal ρ = Spearman(transfer_pred, BAR); off-diagonal = mean over other drugs'
predictions vs this drug's BAR. Residualize transfer_pred & BAR on R_prolif (PDXE) for H2. Permutation k=2000,
seed=42. **H1 PASS** iff diag mean>0 & p<0.05. **H2 PASS** iff resid(diag−off)>0 & p<0.05.
- H1 PASS → cross-dataset transfer externally validated (patient-proxy). 
- H2 PASS → V9 drug-specificity externally REPLICATES → major upgrade.
- Null(s) → honest bound: transfer does not generalize to PDX (or only generically); recorded first-class.

## Honesty / scope
PDXE = patient-DERIVED XENOGRAFTS (mouse-grown), a proxy — better than cell lines, not human clinical. Response
modality (tumor-volume BAR) and platform (FPKM vs DepMap TPM) differ from training → per-gene z mitigation only.
9 drugs (targeted + chemo). Positive H1 is plausible via proliferation; H2 is the hard, decisive test.

## Reproducibility
Engine deterministic; seed=42, k=2000; reproduce ×2. Aggregate outputs only (no per-model data committed).
Output: `experiments/B7_pdxe_external/results/B7_metrics.json`.
