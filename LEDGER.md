# INTERCEPTA build ledger — verified / falsified / untestable (tiered, never blurred)

Carried forward from the audits in `~/kaalcura` (HARD_TEST_LEDGER, COMPRESSED_THEORY_AND_LEDGER) and
`~/INTERCEPTA/verification` (INTERCEPTA_VERIFICATION_LEDGER). Only entries reproduced ×2 with a committed
metrics file are marked VERIFIED. Each row states the killing/confirming test.

## VERIFIED (reproduced ×2, controlled, provenance on file)
| # | Finding | Evidence | Source metrics |
|---|---|---|---|
| V1 | Learned expression→response map transfers cross-dataset, beats parameter-free bar | STRICT (disjoint cell lines) mean per-drug ρ=+0.212, 94/100 drugs>0, Wilcoxon p=1.9e-15 vs R_prolif +0.058 | v1b_learned_metrics.json |
| V2 | R_prolif is a real proliferation signal but ≈ GGI (not novel) | r(R_prolif,MKI67)=0.43; r≈0.75 vs GGI; prognostic for chemo pCR | deconfound_metrics.json, compression_metrics.json |
| V3 | Two-axis (prolif+immune) prognostic pCR model | I-SPY2 GSE173839 AUROC 0.795; R_immune adds p=0.019, permutation p=0.0005 | ispy2_harden_metrics.json |
| V4 | NPM1 → Cabozantinib sensitivity (AML) | BeatAML MW p=4.4e-11; ITD-adjusted OLS β=−21.9 p=3.3e-5; split-replicates both halves | beataml_npm1_cabo_metrics.json, ..._split_replication.json |
| V5 | NRAS → MEK-inhibitor sensitivity (AML) | 3 drugs consistent, p~1e-9 to 3e-11 (known biology) | beataml_other_claims_metrics.json |
| V6 | DNMT3A → Dasatinib sensitivity (AML), independent of NPM1/FLT3-ITD | MW p=1.6e-5; OLS β=−23.7 p=1.2e-4 | beataml_other_claims_metrics.json |
| V7 | +0.212 is the public cell-line cross-dataset ceiling (well-powered null, B2) | Adding R_prolif Δρ=+0.0000 p=0.98; adding 50 driver mutations Δρ=+0.0004 p=0.37 BHq=0.74 — neither verified signal beats transcriptome-only | B2_metrics.json |
| V8 | Cell-line→PATIENT transfer is REAL but weak and NON-specific (B3, L1) | GDSC map → BeatAML patient ex-vivo AUC, 44 drugs: diagonal ρ=+0.054 permutation p=0.0005 (transfer real); but diag−offdiag=+0.022 p=0.12 (NOT drug-specific) and does not beat R_prolif-transfer (+0.022, p=0.55) → generic chemosensitivity/proliferation axis, not drug-level patient prediction | B3_metrics.json |

## FALSIFIED (removed from the working hypothesis, with the killing test)
- **Therapy-SELECTION coordinate system** — 0/16 subtype-adjusted axis×arm interactions survive BH in I-SPY2
  n=990 (selection_metrics.json). Prognostic, not selective.
- **Therapy-class specificity (axis→matched therapy)** — R_immune predicts pCR broadly; Pembro-specific
  interaction permutation p=0.33 (gse194040_metrics.json).
- **Novel coordinate beyond Ki67+TILs** — composites add over single genes but r(R_immune,CD8A)=0.78,
  r(R_prolif,MKI67)=0.43 → same two known axes (compression_metrics.json).
- **PI3K mechanistic specificity** — flips on GDSC1 external (m5b_external_gdsc1_metrics.json).
- **Scout-2 "de novo generative design"** — corrected to scaffold-hopping (INTERCEPTA VISION_AUDIT).

## NOT TESTABLE ON CURRENT DATA (Constitution outcome 3 — with the exact missing data)
- **RNA-velocity "time machine" (pre-resistance detection)** — velocity outputs are pseudotime/magnitude only;
  no per-cell drug-response/resistance ground truth in any available scRNA. Needs paired longitudinal scRNA
  (baseline + relapse, same patients) with matched outcome, ideally lineage-traced. Architecturally novel,
  empirically untested — do NOT claim it works. (RNA_VELOCITY_FEASIBILITY.md)
- **Therapy-selective axis in non-ER / metastatic settings** — needs controlled-access RCTs with
  treatment×biomarker design (dbGaP/EGA) — a human gate.

## Probability estimates (subjective, evidence-conditioned)
- P(novel therapy-selection coordinate system correct): **<5%** (falsified at power).
- P(prolif+TILs prognostic, known biology, no selection): **~85–90%**.
- P(a genuinely novel proliferation-independent selective axis exists & findable in better data): **~10–20%**.
