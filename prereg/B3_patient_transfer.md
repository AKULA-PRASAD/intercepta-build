# Pre-registration — B3 (L1): cell-line → PATIENT drug-response transfer (FINALIZED 2026-07-29, pre-run)

## Question
Does a per-drug expression→response map trained on **cell lines (GDSC)** rank **real patient** ex-vivo drug
response (BeatAML primary AML samples), for drugs shared by both — and does it do so with genuine
**drug-specificity**, beyond a generic proliferation/chemosensitivity axis?

## Hypothesis (assumed FALSE until it survives)
- H1_transfer: across the shared drugs, matched (diagonal) per-drug Spearman ρ(GDSC-map prediction, BeatAML
  ex-vivo AUC) has mean > 0, one-sided permutation p<0.05.
- H1_specific: matched (diagonal) ρ > mismatched (off-diagonal, GDSC map for drug X vs BeatAML AUC for drug
  Y≠X) mean ρ, paired/permutation p<0.05 — i.e., the transfer is drug-specific, not one shared axis.
- H0: no transfer to patients (mean diagonal ρ ≈ 0), OR transfer is entirely non-specific (diagonal ≈
  off-diagonal) → it is only a generic chemosensitivity/proliferation signal, not drug-level patient prediction.

## Data (public/dbGaP-derived, already held; sha256 in data/MANIFEST.md)
- Train: GDSC2 expression + LN_IC50 (as B1).
- Test: BeatAML `beataml_waves1to4_norm_exp_dbgap.txt` (patient tumor RNA, genes×707 samples, gene symbol in
  `display_label`) + ex-vivo AUC from `beataml_probit_curve_fits_v4_dbgap.txt`. Join expression columns to AUC
  via `dbgap_rnaseq_sample` (520 patients with both). Drug name lowercased, parenthetical code stripped;
  44 drugs overlap GDSC↔BeatAML.

## Design (locked)
Per-drug RidgeCV (alphas {10,100,1000}) on GDSC z-expression (top-2000-variance shared genes; genes shared
across GDSC ∩ BeatAML symbols) → LN_IC50. Predict on BeatAML patient z-expression (per-gene z within each
dataset — the same crude batch mitigation as B1, stated as a limitation: array vs RNA-seq platforms differ).
Score per-drug Spearman(prediction, BeatAML ex-vivo AUC) over patients with ≥15 samples for that drug and ≥30
GDSC training cells. Direction: higher GDSC LN_IC50 and higher BeatAML AUC both = more resistant → expect
ρ>0.

## Baselines / the bar (mandatory)
- **Frozen R_prolif transfer** (proliferation-only predictor) per drug — the transfer must add over this to be
  more than a proliferation axis.
- **Off-diagonal (drug-mismatched) ρ** — the specificity control.

## Primary metric + decision rule (fixed in advance)
1. TRANSFER PASS iff mean diagonal per-drug ρ > 0 AND permutation p<0.05 (patient-label permutation, k=2000).
2. SPECIFICITY PASS iff mean diagonal ρ > mean off-diagonal ρ AND permutation p<0.05.
3. Report diagonal ρ vs R_prolif-transfer ρ (paired Wilcoxon) — a transfer that does not beat R_prolif is
   logged as "proliferation-driven, not drug-specific patient prediction."
Full claim ("cell-line→patient drug-specific transfer is real") requires BOTH 1 and 2, AND beating R_prolif.

## Falsification battery
Permutation nulls (above); leakage is structurally absent (GDSC cell lines ≠ BeatAML patients — different
organisms of data); BH not needed for the two primary tests but per-drug ρ signs reported; confound = the
proliferation bar + the off-diagonal specificity control are the confound tests.

## Honest prior
The +0.212 cell-line ceiling and known platform/batch gaps make a strong drug-specific patient transfer
uncertain (~30–50% for *some* significant diagonal ρ; lower for passing specificity too). A null or a
"transfers but only via proliferation" result is a first-class, vision-re-sizing outcome — it bounds L1 and
tells us exactly what better data (matched-platform, larger per-drug n) would be needed.

## Reproducibility
Ridge closed-form; top-gene selection deterministic; permutation seed=42, k=2000. Reproduce ×2 = identical
metrics JSON (timestamp aside). Output: `experiments/B3_patient_transfer/results/B3_metrics.json`.
