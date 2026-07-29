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
| V8 | Cell-line→PATIENT transfer is REAL but (on mismatched platform) non-specific (B3, L1) | GDSC array map → BeatAML patient ex-vivo AUC, 44 drugs: diagonal ρ=+0.054 permutation p=0.0005 (transfer real); diag−offdiag=+0.022 p=0.12 (not specific on array platform) | B3_metrics.json |
| V9 | On a MATCHED RNA-seq platform, a WEAK but DRUG-SPECIFIC, proliferation-independent cell-line→patient signal exists AND replicates across two independent screens (B3b/L1b + B3c) | DepMap RNA-seq map → BeatAML: prolif-residualized diag−off = +0.040 perm p=0.010 (GDSC2 labels, 44 drugs); replicates with independent GDSC1 labels: +0.051 perm p=0.0015 (59 drugs). Effect is small (diag ρ≈0.07–0.08). **Still single patient cohort (BeatAML, AML) — needs a 2nd patient cohort + other cancers for full external validity.** | B3b_metrics.json, B3c_metrics.json |
| V9+ | V9 is ROBUST to drug- and patient-subsetting (B3d) | Drug jackknife all leave-one-out >0 (min +0.033); bootstrap 95% CI over drugs [+0.008,+0.074] excludes 0; internal patient split-half both halves >0 (+0.053/+0.027). Not driven by any single drug or patient subset. | B3d_metrics.json |
| N1 | The robust transfer signal is NOT explained by AML mechanism (pre-registered NULL, B3e) | H1: drugs in GDSC pathways {RTK signaling, ERK MAPK signaling} (frozen a priori as the AML driver-signaling axis) do NOT transfer better — median resid ρ +0.0519 vs +0.0513, gap +0.0005, one-sided MWU p=0.29, perm p=0.50. H2: transfer ρ does not track within-cell-line CV predictability (Spearman +0.042, p=0.36). B3d's exploratory "AML-relevant drugs transfer best" ranking did NOT survive a rigorous pre-registered test — the visually-striking top drugs were selection, not signal. **Coherence claim withdrawn.** | B3e_metrics.json |
| V10 | The two verified signal types are COMPLEMENTARY — combining mutation marker + expression transfer beats either alone (B4, pre-registered) | On verified drug–marker pairs: combined 5-fold CV Spearman > BOTH single predictors in all 4 testable pairs (trametinib 0.336 vs mk 0.078/tr 0.257; selumetinib 0.380 vs 0.177/0.288; dasatinib 0.213 vs 0.050/0.180; sorafenib 0.469 vs 0.271/0.383). Expression transfer adds beyond the marker (partial p<0.05, correct sign, BHq<5e-8) in 3/4 pairs; complementary (both add) in 3/4. Pre-registered rule (≥3 pairs) MET. **Caveats (honest):** (a) DL random-effects meta is NULL (p=0.21) due to heterogeneity; (b) dasatinib's transfer is INVERTED (β<0, strongly anti-predictive — cell-line dasatinib biology ≠ patient); (c) cabozantinib/NPM1 (V4) NOT testable — no GDSC2 cabozantinib training data; (d) 4 pairs, single cohort (BeatAML), needs an INDEPENDENT cohort. | B4_metrics.json |
| V11 | engine v1 (shipped) faithfully embodies V10, using genome-wide-robust markers | Markers now sourced from B5 (genome-wide screen). Combining marker+transfer beats transfer-alone at predicting BeatAML ex-vivo response in 3/3 genome-wide-robust pairs (sorafenib ρ=−0.47 vs −0.39; selumetinib −0.31 vs −0.25; trametinib −0.30 vs −0.24); reproduced ×2. LOW confidence, one cohort, most correlation is generic proliferation (V8/N1). | engine_v1_metrics.json |
| V12 | Genome-wide mutation→drug marker screen (B5): 177 robust markers | 3051 gene×drug pairs in BeatAML; 177 survive BH-FDR<0.05 + FLT3-ITD/prolif-deconfounding + split-half direction-replication. Dominated by **FLT3-ITD→FLT3 inhibitors** (66; sorafenib BHq=4e-26) and **RAS(KRAS/NRAS)→MEK** — textbook actionable AML biology. 114 sensitizing / 63 resistance (incl. TP53→resistance). ONE cohort — needs external replication. | B5_metrics.json, discovered_markers.json |


## FALSIFIED (removed from the working hypothesis, with the killing test)
- **Therapy-SELECTION coordinate system** — 0/16 subtype-adjusted axis×arm interactions survive BH in I-SPY2
  n=990 (selection_metrics.json). Prognostic, not selective.
- **Therapy-class specificity (axis→matched therapy)** — R_immune predicts pCR broadly; Pembro-specific
  interaction permutation p=0.33 (gse194040_metrics.json).
- **Novel coordinate beyond Ki67+TILs** — composites add over single genes but r(R_immune,CD8A)=0.78,
  r(R_prolif,MKI67)=0.43 → same two known axes (compression_metrics.json).
- **PI3K mechanistic specificity** — flips on GDSC1 external (m5b_external_gdsc1_metrics.json).
- **Scout-2 "de novo generative design"** — corrected to scaffold-hopping (INTERCEPTA VISION_AUDIT).

## REFINED by the genome-wide screen (B5) — earlier pairwise claims tightened
- **V4 NPM1→Cabozantinib** and **V6 DNMT3A→Dasatinib** do NOT independently survive genome-wide BH-FDR when
  co-adjusted for FLT3-ITD. They are real but MODEST pairwise effects; cabozantinib sensitivity is largely the
  co-occurring **FLT3-ITD** (the genome-wide-robust cabo marker). **V5 NRAS→MEK is CONFIRMED genome-wide.**
  The engine's marker table was updated accordingly (cabo→FLT3-ITD; DNMT3A→dasatinib dropped).

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
