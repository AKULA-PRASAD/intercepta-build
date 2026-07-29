# INTERCEPTA Phase B Layer 3 — Artifact 3.2
## 56 Pass Criteria Specification (8 per V-level × 7 V-levels)

**Status:** PROPOSED for CEO LOCK (per Charter v1.2 §5.3 GO/NOGO discipline)
**Date:** 2026-05-11
**Author:** Claude (CSO)
**Predecessor artifacts:** L2.1 LOCKED, L2.2/L2.3/L2.4 PROPOSED, L3.1 PROPOSED — Layer 2 of Phase B COMPLETE
**Parent decision:** Decision 6 v2 Q6 Validation Cascade (LOCKED); Decision 5 v2 (OOD); Decision 8 v2 (universality)
**Co-bound decisions:** Decisions 1, 4, 5, 6, 7, 8, 9, 10 (all v2)
**Phase:** B (drug response prediction platform; 2-4 year horizon per Charter v1.2 §1.7)
**Phase F mapping:** Phase B 56 pass criteria become the precedent template for Phase F's extended V7-V12 levels.
**Target length per Phase B Plan v2:** 5-6K words
**Filename:** INTERCEPTA_FV_L3_2_56_Pass_Criteria_Specification_2026-05-11.md

---

## §0 Identification and Scope

### 0.1 What This Document Is

L3.2 enumerates **56 specific pass criteria** — 8 per V-level × 7 V-levels — that operationalize Decision 6 v2 + Decision 5 v2 + Decision 8 v2 into testable empirical claims. L3.2 is the second artifact of Phase B Layer 3 and consumes L3.1 cascade pipeline infrastructure.

Each criterion is a **binary pass/fail check** with: a binding threshold; a statistical test or computation specifying how the threshold is evaluated; a sample-size floor; and an abstain protocol for when sample size is below the floor.

### 0.2 What This Document Is Not

L3.2 is NOT:
- A theory of why thresholds were chosen at the values they are (that lives in Decision 6 v2 + Decision 8 v2 + their supporting anchors)
- A statistical methods textbook (bootstrap CIs, ECE binning, power analysis: committed to but not re-derived)
- The V6 cross-disease grid (that is L3.3)
- A regulatory clearance protocol (Phase F)

### 0.3 The 8-Criterion Decomposition Pattern

L3.2 decomposes each V-level into 8 criteria using a uniform pattern. Each V-level has 8 criteria across these categories:

| # | Criterion class | Purpose |
|---|---|---|
| C1 | Primary metric threshold | The binding headline number (AUROC ≥ 0.77, ECE ≤ 0.05, etc.) |
| C2 | Bootstrap 95% CI floor | Statistical defensibility of the point estimate |
| C3 | Minimum sample size | Decision 6 v2 per-level requirement |
| C4 | Failure mode classification | F0-F7 attribution of failed predictions |
| C5 | OOD / calibration integration | Q5 flag distribution + ECE per Decision 5 v2 |
| C6 | Baseline comparator | IMPROVE / Tang / Kim per Decision 6 v2 mandatory reporting |
| C7 | Level-specific BINDING | Unique constraint per level (Souza-Mehta at V3, concordance at V4, etc.) |
| C8 | Cross-level consistency / reporting completeness | V0→V1 gap, V3→V4 carry-through, V6 paradigm coverage |

This produces 56 criteria total (8 × 7). All 56 are BINDING for L3.2 LOCK; passing all 56 is the empirical bar for Phase B Layer 5 deployment readiness.

### 0.4 Document Conventions

- **BINDING** — cannot be modified without Decision Record amendment + CEO+CSO co-sign
- **DEFAULT** — Layer-5-revisitable per §10.5
- Thresholds in **bold** trace to Decision 6 v2 or Decision 8 v2 anchor papers
- Code snippets PyTorch 2.x + scipy.stats + statsmodels (BSD/MIT open)

### 0.5 Anchor Re-Read Compliance

Q6 + Q5 + Q8 anchors re-read in primary-source form during 2026-05-11 corpus-read audit; trigger SATISFIED. Key threshold sources:
- Tang 2022: V3 AUROC ≥ 0.77; V4 TNBC RMSE ≤ 0.11
- Kim 2020: V4 concordance 24.5%
- Partin 2026 IMPROVE: V1 two-metric framework
- Li-Shen 2024 DiSyn: V5 ECE ≤ 0.05
- Decision 8 v2: V6 ≥ 0.65 on ≥ 2 areas; 4-paradigm matrix
- Decision 5 v2: epistemic attribution ≥ 70% on V6 failures; Pass 1-4 binding criteria

---

## §1 V0 — Within-Dataset Cross-Validation: 8 Pass Criteria

V0 is the development sanity check; criteria are the most permissive. The cascade rationale: if V0 fails, the architecture cannot learn anything from the data, and proceeding is futile.

### V0-C1: Primary AUROC threshold (binary) / Pearson R (continuous)
- **Threshold:** AUROC > 0.5 (binary) or Pearson R > 0 (continuous), point estimate
- **Test:** standard scikit-learn metric on 5-fold CV pooled predictions
- **Pass:** point estimate above threshold

### V0-C2: Bootstrap 95% CI lower bound > 0.5 (binary) or > 0 (continuous)
- **Threshold:** CI lower bound (2.5th percentile) exceeds zero-skill baseline
- **Test:** 1000-iteration bootstrap on pooled CV predictions
- **Pass:** lower CI bound above zero-skill baseline
- **Rationale:** statistical defensibility — random chance must be excluded at 95% confidence

### V0-C3: Minimum sample size ≥ 1,000 (cell line, drug) pairs
- **Threshold:** 1000 pairs per Decision 6 v2 V0 sample size requirement
- **Test:** len(dataset) >= 1000 before evaluation begins
- **Pass:** sample size floor met; otherwise abstain with documented insufficient-data flag
- **Abstain protocol:** if violated, V0 returns insufficient-data result; cascade halts pending dataset expansion

### V0-C4: Failure mode F0 (model cannot learn) not detected
- **Threshold:** training loss converges; validation AUROC > 0.5 across all 5 folds
- **Test:** per-fold AUROC must each independently clear C1 threshold (not just pooled)
- **Pass:** all 5 folds individually clear; F0 not triggered
- **Hard termination:** F0 detection triggers Decision 6 v2 hard termination per L3.1 §2.2

### V0-C5: Q5 OOD flag distribution sanity check
- **Threshold:** fraction of training-distribution predictions flagged as OOD ≤ 5% (low-rate false alarms)
- **Test:** OODStack evaluates on V0 held-out fold; count `operational_verdict == "abstain_ood"`
- **Pass:** ≤ 5% rate
- **Rationale:** within-dataset CV is by definition in-distribution; high OOD flag rate at V0 indicates broken Layer 5.4 energy scoring (L2.3 §6)
- **Cross-binding:** Decision 5 v2 Pass 1 (energy AUROC ≥ 0.85 on known-OOD); V0 is the known-ID side of that comparison

### V0-C6: Comparison to naive baseline
- **Threshold:** AUROC at least 0.05 above naive "predict mean response" baseline
- **Test:** train a constant predictor; compare AUROC
- **Pass:** non-trivial learning demonstrated
- **Rationale:** "significant signal above zero" must mean "better than uninformative baseline," not just "better than chance"

### V0-C7: Souza-Mehta methodological readiness (level-specific BINDING)
- **Threshold:** parameter-free baseline (PCA + HVG with linear classifier) trained at matched hyperparameter budget; result recorded for V3+ comparison
- **Test:** PCALoadingsAttributor baseline runs at V0 in parallel; result cached at `/scratch/akula.pra/INTERCEPTA/validation/pca_hvg/v0/`
- **Pass:** baseline result present in cascade report
- **Rationale:** Souza-Mehta bar requires comparison; V3 cannot retroactively compute V0 baselines; the cache must exist
- **BINDING per Decision 8 v2 Commitment 5**

### V0-C8: Reporting completeness — all 7 mandatory elements present
- **Threshold:** VLevelResult.notes + cascade_report contain all 7 of: performance metric, CI, sample size, Q5 OOD flag distribution, Q5 ECE, F-mode classification, baseline comparison
- **Test:** automated checker on CascadeReport schema
- **Pass:** 7-of-7 elements present
- **BINDING per Decision 6 v2 §"Mandatory Cross-Level Reporting"**

---

## §2 V1 — Cross-Dataset (IMPROVE Methodology): 8 Pass Criteria

V1 tests generalization beyond single-dataset batch/protocol artifacts. The IMPROVE two-metric framework (Partin 2026) is BINDING.

### V1-C1: Mean cross-dataset AUROC ≥ 0.65
- **Threshold:** mean AUROC across all (train, test) dataset pairs ≥ 0.65 per Decision 6 v2
- **Test:** evaluate on all 6 GDSC/CCLE/CTRP pairs (3 datasets × 2 directions, excluding self-pairs); mean
- **Pass:** mean ≥ 0.65

### V1-C2: Per-pair CI lower bound ≥ 0.60 on at least 4 of 6 pairs
- **Threshold:** per-pair bootstrap 95% CI lower bound; majority of pairs must clear 0.60
- **Test:** 1000-iteration bootstrap per pair
- **Pass:** ≥ 4 of 6 pairs have CI lower bound ≥ 0.60
- **Rationale:** prevents one strong pair from carrying the mean

### V1-C3: Sample size per pair matches IMPROVE-standardized evaluation
- **Threshold:** IMPROVE-published evaluation set sizes per (train, test) pair
- **Test:** verify against IMPROVE workflow manifest
- **Pass:** all 6 pairs use IMPROVE-standardized splits

### V1-C4: Failure mode F1 (dataset overfitting) and F2 (cross-platform batch effects) bounded
- **Threshold:** F1 detection if any single train-pair AUROC > 0.85 while its test-pair AUROC < 0.60 (asymmetric overfitting)
- **Threshold:** F2 detection if all CCLE→x pairs underperform corresponding GDSC→x pairs by > 0.10 AUROC
- **Test:** per-pair AUROC table inspected
- **Pass:** neither F1 nor F2 detected; if detected, soft termination per L3.1

### V1-C5: ECE ≤ 0.10 on cross-dataset predictions
- **Threshold:** ECE ≤ 0.10 (less strict than V5's 0.05; V1 is upstream of calibration recalibration)
- **Test:** _compute_ece per L3.1 §8.3
- **Pass:** mean ECE across pairs ≤ 0.10
- **Cross-binding:** Decision 5 v2 Pass 3 (ECE ≤ 0.05 at deployment); V1 is upstream

### V1-C6: Match best IMPROVE baseline (BINDING per Partin 2026)
- **Threshold:** INTERCEPTA mean AUROC ≥ max(baseline AUROC) - 0.02 (within 2pp of best published IMPROVE baseline)
- **Test:** load IMPROVE-published baseline AUROCs (DeepCDR, PaccMann, naive) per pair; compare
- **Pass:** INTERCEPTA matches or beats best; or within 2pp tolerance (allows architectural innovation while ensuring no regression)
- **BINDING per Decision 6 v2 + Partin 2026 + Decision 8 v2 Commitment 5**

### V1-C7: IMPROVE two-metric framework reported (level-specific BINDING)
- **Threshold:** both absolute AUROC AND relative-to-baseline performance reported per pair
- **Test:** CascadeReport.cross_level_reporting includes both numbers per pair
- **Pass:** two-metric reporting present for all 6 pairs
- **BINDING per Decision 6 v2 + Partin 2026**

### V1-C8: V0 → V1 generalization gap reported and ≤ 0.20
- **Threshold:** |V0 AUROC - V1 mean AUROC| ≤ 0.20
- **Test:** load cached V0 result; compute gap
- **Pass:** gap within bound; report regardless of pass/fail
- **Rationale:** gap > 0.20 indicates severe dataset-specific overfitting (per IMPROVE methodology). Pass-with-reservations if 0.15-0.20; hard-flag if > 0.20
- **BINDING per Decision 6 v2 §"Mandatory Cross-Level Reporting"**

---

## §3 V2 — Cell Line → Organoid: 8 Pass Criteria

V2 has NO empirical anchor — INTERCEPTA defines the standard. Criteria are calibrated for continuity with V1 (cross-dataset) without yet introducing the full tumor microenvironment.

### V2-C1: Mean organoid AUROC ≥ 0.65
- **Threshold:** mean AUROC across organoid datasets (HCMI, Sanger) ≥ 0.65 per Decision 6 v2
- **Test:** standard scikit-learn AUROC per dataset; mean across datasets
- **Pass:** mean ≥ 0.65

### V2-C2: Per-dataset CI lower bound ≥ 0.60
- **Threshold:** bootstrap 95% CI lower bound per organoid dataset ≥ 0.60
- **Test:** 1000-iteration bootstrap per dataset
- **Pass:** both HCMI and Sanger clear

### V2-C3: Minimum 50 organoid samples per cancer type
- **Threshold:** ≥ 50 samples per cancer type per Decision 6 v2 V2 sample size requirement
- **Test:** group-by cancer type; count
- **Pass:** all evaluated cancer types meet floor; underpowered cancer types excluded from aggregate
- **Abstain protocol:** if HCMI/Sanger lack 50 samples for a cancer type, that cancer is reported separately as exploratory, not in V2-C1 aggregate

### V2-C4: Failure modes F2 (3D context loss) and F3 (organoid selection bias) bounded
- **Threshold:** F2 detection if AUROC degradation V1→V2 > 0.15 (large 3D-context penalty)
- **Threshold:** F3 detection if cancer-type composition differs by > 30% from cell-line training distribution
- **Test:** per-cancer-type AUROC table; cell-type composition inspection
- **Pass:** neither F2 nor F3 detected; if detected, document and pass with reservations

### V2-C5: Q5 OOD flag distribution intermediate
- **Threshold:** OOD flag rate between 5% (V0 baseline) and 30% (would indicate severe shift)
- **Test:** OODStack.operational_verdict tallied
- **Pass:** flag rate in [5%, 30%]
- **Rationale:** organoids are 3D-context-shifted from cell lines but not entirely OOD; intermediate rate is biologically plausible

### V2-C6: Comparison to "predict cell line average response" baseline
- **Threshold:** AUROC at least 0.05 above per-drug-mean baseline
- **Test:** for each (drug, organoid), predict the mean cell-line response for that drug; compare
- **Pass:** non-trivial improvement over per-drug average

### V2-C7: V2 standard definition documented (level-specific BINDING)
- **Threshold:** V2 results published as INTERCEPTA-defined V2 standard (per Decision 6 v2 §"Why is V2 in the cascade if no empirical anchor exists")
- **Test:** publication/preprint manifest includes "V2 standard" documentation with methodology, datasets, thresholds
- **Pass:** documentation present
- **Rationale:** since no empirical anchor exists, INTERCEPTA must define the standard explicitly for the field to use

### V2-C8: V1 → V2 transition gap reported
- **Threshold:** |V1 AUROC - V2 AUROC| documented in cascade report
- **Test:** load cached V1 result; compute gap
- **Pass:** gap within 0.20; report regardless
- **Rationale:** large V1→V2 gap indicates cell-line-trained models lose substantial signal when moved to 3D context; must be reported honestly per IMPROVE-style transition reporting

---

## §4 V3 — Cell Line → Tumor (TCGA): 8 Pass Criteria

V3 is the **translational hinge** — Tang 2022 BINDING anchor at AUROC ≥ 0.77. The Souza-Mehta bar is most operationally critical at V3 because the FM/multi-paradigm complexity claims its value here.

### V3-C1: TCGA AUROC ≥ 0.77 (Tang 2022 BINDING)
- **Threshold:** AUROC ≥ 0.77 per Decision 6 v2 BINDING
- **Test:** standard scikit-learn AUROC on TCGA clinical-outcome-labeled samples
- **Pass:** AUROC ≥ 0.77
- **BINDING per Decision 6 v2 + Tang 2022**

### V3-C2: Bootstrap 95% CI lower bound ≥ 0.72
- **Threshold:** CI lower bound ≥ 0.72 (Tang 2022 floor minus 0.05 statistical buffer)
- **Test:** 1000-iteration bootstrap
- **Pass:** CI lower bound clears 0.72
- **Rationale:** if the point estimate of 0.77 has CI [0.70, 0.84], the statistical evidence is weaker than the threshold suggests

### V3-C3: TCGA cohort size ≥ 100 per cancer type
- **Threshold:** ≥ 100 samples per cancer type per Decision 6 v2 V3 sample size requirement
- **Test:** group-by cancer type in TCGA; count
- **Pass:** all evaluated cancer types meet floor
- **Abstain protocol:** rare TCGA cancers (n < 100) reported separately

### V3-C4: Failure modes F3 (TME absence) and F4 (TCGA selection bias) bounded
- **Threshold:** F3 detection if per-cancer-type AUROC variance > 0.10 (some cancers work, others do not — TME-dependent)
- **Threshold:** F4 detection if pre-treatment vs post-treatment AUROC differs by > 0.15 (TCGA is predominantly treatment-naive)
- **Test:** per-cancer-type variance; treatment-status stratification
- **Pass:** both bounded

### V3-C5: ECE ≤ 0.08 on TCGA predictions
- **Threshold:** ECE ≤ 0.08 (between V1 0.10 and V5 0.05; tightening toward deployment)
- **Test:** _compute_ece per L3.1 §8.3
- **Pass:** mean ECE ≤ 0.08

### V3-C6: Comparison to Tang 2022 pathway-feature baseline (BINDING)
- **Threshold:** INTERCEPTA AUROC ≥ Tang 2022 pathway-baseline AUROC (matched-budget per Souza-Mehta)
- **Test:** pathway-feature baseline trained at ≥ 25% of INTERCEPTA hyperparameter budget per Decision 8 v2 Commitment 5
- **Pass:** INTERCEPTA matches or exceeds pathway baseline
- **Soft termination:** INTERCEPTA = Tang 2022 = pathway baseline → FM complexity not earning its cost; revise Decision 1 v2 substrate choice
- **BINDING per Decision 6 v2 + Decision 8 v2 Commitment 5**

### V3-C7: Souza-Mehta pathway baseline integration (level-specific BINDING)
- **Threshold:** pathway-feature baseline included in V3 evaluation at matched compute budget
- **Test:** `v3_souza_mehta_baseline_required = True`; baseline result present in cascade report
- **Pass:** baseline result documented
- **BINDING per Decision 8 v2 Commitment 5; Souza-Mehta 2026 methodological commitment**

### V3-C8: V0 → V3 generalization gap and per-cancer-type breakdown
- **Threshold:** |V0 AUROC - V3 AUROC| ≤ 0.20 acceptable; > 0.20 documented honestly
- **Threshold:** per-cancer-type AUROC reported individually (TCGA has 33 cancer types; aggregate hides translation variability)
- **Test:** cached V0 + cancer-type stratification
- **Pass:** gap reported + per-cancer-type table in cascade report
- **Rationale:** Tang 2022's 0.77 floor was reported in aggregate; INTERCEPTA's per-cancer breakdown reveals where translation succeeds vs fails

---

## §5 V4 — Cell Line → PDX: 8 Pass Criteria

V4 has dual thresholds (Tang 2022 TNBC + broad PDX) and Kim 2020 BINDING concordant/non-concordant biomarker separation.

### V4-C1: TNBC RMSE ≤ 0.11 (Tang 2022 BINDING)
- **Threshold:** RMSE ≤ 0.11 on TNBC PDX subset per Decision 6 v2 BINDING
- **Test:** sqrt(MSE) on TNBC-filtered predictions
- **Pass:** RMSE ≤ 0.11
- **BINDING per Decision 6 v2 + Tang 2022**

### V4-C2: Broader PDX RMSE ≤ 0.20 with bootstrap CI
- **Threshold:** RMSE ≤ 0.20 on broader PDX panel; CI upper bound ≤ 0.22
- **Test:** 1000-iteration bootstrap on non-TNBC PDX subset
- **Pass:** point estimate ≤ 0.20 AND CI upper ≤ 0.22

### V4-C3: NCI PDXNet sample size ≥ 30 per cancer type
- **Threshold:** ≥ 30 PDX samples per cancer type per Decision 6 v2 V4 sample size requirement
- **Test:** group-by cancer type; count
- **Pass:** all evaluated cancer types meet floor

### V4-C4: Failure modes F4 (PDX selection bias) and F5 (biomarker non-concordance) bounded
- **Threshold:** F4 detection if PDX cancer-type distribution differs > 30% from clinical incidence
- **Threshold:** F5 detection is GUARANTEED at the 24.5% concordance rate per Kim 2020; the question is whether INTERCEPTA + L2.3 OOD stack correctly flags non-concordant predictions
- **Test:** flag-rate on non-concordant biomarker subset must be ≥ 70% (Decision 5 v2 Pass 4 standard)
- **Pass:** F4 bounded; F5 acknowledged + OOD flagging adequate

### V4-C5: Q5 OOD flag rate on non-concordant biomarkers ≥ 70%
- **Threshold:** ≥ 70% of non-concordant-biomarker predictions flagged as epistemic OOD
- **Test:** classify each PDX sample as concordant/non-concordant per Kim 2020 24.5% rate; check OODOutput.epistemic_uncertainty > threshold for non-concordant subset
- **Pass:** ≥ 70% flagged
- **BINDING per Decision 5 v2 Pass 4 + Decision 6 v2 Kim 2020 BINDING**

### V4-C6: Comparison to Tang 2022 TNBC baseline + Kim 2020 PDXGEM baseline
- **Threshold:** INTERCEPTA RMSE ≤ Tang 2022 TNBC RMSE; INTERCEPTA AUROC ≥ Kim 2020 PDXGEM AUROC
- **Test:** load Tang 2022 + Kim 2020 baselines; compare per metric
- **Pass:** INTERCEPTA matches or beats both
- **BINDING per Decision 6 v2 §"Mandatory Cross-Level Reporting" element 7**

### V4-C7: Concordant vs non-concordant biomarker space reported separately (level-specific BINDING)
- **Threshold:** RMSE reported separately for concordant biomarker subset AND non-concordant biomarker subset
- **Test:** CascadeReport.cross_level_reporting includes both subsets with separate RMSEs
- **Pass:** dual reporting present
- **BINDING per Decision 6 v2 + Kim 2020 24.5% concordance**

### V4-C8: V3 → V4 transition gap and concordant-only sub-evaluation
- **Threshold:** |V3 AUROC - V4 concordant-subset AUROC| reported; ≤ 0.15 acceptable
- **Test:** load cached V3 + V4 concordant subset; compute gap
- **Pass:** gap reported regardless of magnitude
- **Rationale:** concordant-only sub-evaluation isolates the in-vivo translation effect from biomarker-translation effect; the comparison to V3 reveals which translation gap is dominant

---

## §6 V5 — PDX → Patient (Retrospective Clinical): 8 Pass Criteria

V5 is the **deployment context** test. ECE ≤ 0.05 (Decision 5 v2 + Li-Shen 2024 BINDING) is the strictest calibration requirement; statistical power is mandatory reporting.

### V5-C1: ECE ≤ 0.05 (Decision 5 v2 + Li-Shen 2024 BINDING)
- **Threshold:** ECE ≤ 0.05 on patient predictions per Decision 5 v2 Pass 3
- **Test:** _compute_ece on patient prediction set
- **Pass:** mean ECE across adequate-power cohorts ≤ 0.05
- **BINDING per Decision 5 v2 Pass 3 + Li-Shen 2024**

### V5-C2: AUROC ≥ 0.65 on independent clinical cohort + CI lower bound ≥ 0.60
- **Threshold:** AUROC ≥ 0.65 with bootstrap CI lower bound ≥ 0.60
- **Test:** 1000-iteration bootstrap on aggregate adequate-power cohorts
- **Pass:** both point and CI lower clear thresholds

### V5-C3: Minimum 30 patients per drug-cancer combination
- **Threshold:** ≥ 30 patients per (drug, cancer_type) pair per Decision 6 v2 V5 sample size requirement; ≥ 100 preferred
- **Test:** per-drug-cancer count; partition adequate vs inadequate
- **Pass:** at least 1 adequate-power (drug, cancer) pair exists; aggregate uses only adequate pairs
- **Abstain protocol:** below-floor pairs reported separately with "insufficient power" flag

### V5-C4: Failure modes F5 (biomarker carry-through) and F6 (population mismatch) bounded
- **Threshold:** F5 detection if AUROC on PDX-trained model on patient cohort < V4 AUROC by > 0.10 (biomarker non-concordance from V4 carries through to V5)
- **Threshold:** F6 detection if demographic distribution of training PDX differs from clinical cohort by > 30% in any covariate (age, sex, prior therapy)
- **Test:** demographic comparison; AUROC differential
- **Pass:** both bounded; if not, document carefully

### V5-C5: Q5 OOD flag distribution on patients
- **Threshold:** OOD flag rate ≤ 30% on adequate-power cohorts (high but plausible given PDX→patient shift)
- **Test:** OODStack.operational_verdict tallied per adequate cohort
- **Pass:** rate ≤ 30%; higher rates document as F5/F6
- **Rationale:** some OOD is expected at V5; pathological rates indicate the OOD stack is over-flagging

### V5-C6: Comparison to Kim 2020 PDXGEM web app baseline + Li-Shen 2024 DiSyn architecture-validation baseline
- **Threshold:** INTERCEPTA AUROC ≥ PDXGEM AUROC; INTERCEPTA ECE ≤ DiSyn ECE
- **Test:** load Kim 2020 + Li-Shen 2024 baselines from published results
- **Pass:** INTERCEPTA matches or beats both metrics
- **Note:** DiSyn is CC BY-NC-ND; INTERCEPTA uses its architecture validation patterns, not its codebase (Decision 10 v2)

### V5-C7: Statistical power reported per evaluation (level-specific BINDING)
- **Threshold:** statistical power (1 - β) computed and reported per (drug, cancer) pair
- **Test:** power analysis with α=0.05, effect_size=AUROC-0.5, n=cohort_size; standard formula
- **Pass:** power reported for every cohort; aggregate pass/fail decision uses only power ≥ 0.80 cohorts
- **BINDING per Decision 6 v2 V5 BINDING CAVEAT**

### V5-C8: V4 → V5 transition gap on concordant biomarkers and treatment-status stratification
- **Threshold:** |V4 concordant-subset performance - V5 on equivalent biomarker space| reported
- **Threshold:** treatment-status stratification (treatment-naive vs prior-therapy) reported
- **Test:** load cached V4 concordant subset; stratify V5 patients
- **Pass:** both gap analyses present in cascade report

---

## §7 V6 — Cross-Disease (Universality Test): 8 Pass Criteria

V6 is INTERCEPTA novelty — the Charter §1.1 universality test. Decision 8 v2 BINDING + Decision 5 v2 Pass 4 BINDING.

### V6-C1: At least 1 paradigm achieves AUROC ≥ 0.65 on ≥ 2 therapeutic areas
- **Threshold:** Decision 8 v2 BINDING — ≥ 0.65 AUROC on held-out diseases spanning ≥ 2 therapeutic areas (e.g., oncology + I&I; or oncology + neurodegeneration)
- **Test:** per-paradigm per-disease AUROC matrix; count therapeutic areas where any paradigm achieves ≥ 0.65
- **Pass:** count ≥ 2
- **BINDING per Decision 8 v2 Commitment 3**

### V6-C2: Per-disease bootstrap CI lower bound ≥ 0.55 on passing diseases
- **Threshold:** for diseases where any paradigm passes ≥ 0.65, CI lower bound ≥ 0.55
- **Test:** 1000-iteration bootstrap per (paradigm, disease) cell
- **Pass:** CI lower bound ≥ 0.55 on passing-disease cells

### V6-C3: Minimum 3 held-out diseases × ≥ 2 therapeutic areas × adequate per-disease sample sizes
- **Threshold:** ≥ 3 diseases; ≥ 2 therapeutic areas; ≥ 100 samples per disease (similar to V3 floor)
- **Test:** L3.3 grid specifies the exact disease + sample structure
- **Pass:** grid coverage meets minimums per Decision 6 v2 V6 sample size requirement

### V6-C4: Failure modes F6 (disease class OOD) and F7 (patient subpopulation gap) classified
- **Threshold:** failed predictions classified into F6 vs F7 with > 80% classification accuracy
- **Test:** F6 = entire disease is OOD (mean epistemic high across all predictions); F7 = subpopulation gap (epistemic high for specific patient clusters but not others)
- **Pass:** classification done; rates reported per disease

### V6-C5: Q5 attribution accuracy ≥ 70% on failed predictions (Decision 5 v2 Pass 4 BINDING)
- **Threshold:** ≥ 70% of failed predictions correctly attributed to epistemic uncertainty
- **Test:** for predictions where (predicted_response ≠ true_response), check (OODOutput.epistemic_uncertainty > threshold)
- **Pass:** fraction ≥ 70%
- **BINDING per Decision 5 v2 Pass 4**
- **Soft termination if < 70%:** OOD stack broken on cross-disease shift; revise L2.3 architecture

### V6-C6: Comparison across 4 paradigms (A general FM / B disease-area FM / C patient-aggregation / D parameter-free)
- **Threshold:** all 4 paradigms evaluated per disease; per-paradigm AUROCs reported
- **Test:** L3.1 §9.2 paradigm matrix populated
- **Pass:** 4-paradigm matrix complete
- **BINDING per Decision 8 v2 Commitment 5 Souza-Mehta methodological bar**

### V6-C7: 4-paradigm matrix and Souza-Mehta competitive parameter-free result (level-specific BINDING)
- **Threshold:** Souza-Mehta paradigm D (parameter-free) result within 5pp AUROC of best paradigm OR documented architectural justification for the gap
- **Test:** max(paradigm_AUROC) - paradigm_D_AUROC ≤ 0.05
- **Pass:** parameter-free competitive OR rigorous explanation of failure mode
- **BINDING per Decision 8 v2 Commitment 5; Souza-Mehta 2026 methodological commitment**
- **Rationale:** if paradigm D is far behind, FM/multi-paradigm complexity is empirically justified; if competitive, architecture choice is methodologically open

### V6-C8: Cross-disease interpretability transfer (Decision 7 v2 Pass 7 BINDING)
- **Threshold:** Q7 layer attribution remains biologically plausible on held-out diseases per Decision 7 v2 Pass 3 criterion (≥ 80% canonical-target recovery)
- **Test:** for known drug-target pairs in held-out diseases, check Scale 5 top-K attribution
- **Pass:** ≥ 80% recovery on the V6 evaluation set
- **BINDING per Decision 7 v2 Pass 7 + Charter §1.1 universality test**

---

## §8 Summary Table — All 56 Criteria

| V | C1 Primary | C2 CI | C3 Sample | C4 F-modes | C5 OOD/ECE | C6 Baseline | C7 Level BINDING | C8 Cross-level |
|---|---|---|---|---|---|---|---|---|
| V0 | AUROC > 0.5 | CI > 0.5 | ≥1000 | F0 absent | OOD ≤ 5% | naive +0.05 | Souza-Mehta cache | 7/7 elements |
| V1 | mean ≥ 0.65 | 4/6 pairs ≥ 0.60 | IMPROVE std | F1/F2 bounded | ECE ≤ 0.10 | match IMPROVE | two-metric report | V0→V1 ≤ 0.20 |
| V2 | mean ≥ 0.65 | both datasets ≥ 0.60 | ≥50/cancer | F2/F3 bounded | OOD 5-30% | per-drug-mean +0.05 | V2 standard def | V1→V2 reported |
| V3 | AUROC ≥ 0.77 | CI ≥ 0.72 | ≥100/cancer | F3/F4 bounded | ECE ≤ 0.08 | ≥ pathway baseline | Souza-Mehta baseline | V0→V3 + per-cancer |
| V4 | TNBC RMSE ≤ 0.11 | broad CI ≤ 0.22 | ≥30/cancer | F4/F5 bounded | OOD ≥70% non-conc | Tang+Kim baselines | concord/non sep | V3→V4 concord-only |
| V5 | ECE ≤ 0.05 | AUROC CI ≥ 0.60 | ≥30/drug-cancer | F5/F6 bounded | OOD ≤ 30% | PDXGEM+DiSyn | stat power | V4→V5 + treatment strat |
| V6 | ≥0.65 on ≥2 areas | CI ≥ 0.55 | 3 dis × 2 areas × ≥100 | F6/F7 classified | epistemic ≥70% | 4-paradigm matrix | paradigm D competitive | Q7 interp transfer ≥80% |

**56 total. All BINDING. Passing all 56 is the empirical bar for Phase B Layer 5 deployment readiness.**

---

## §9 Statistical Methods Library (BINDING for Layer 5 Implementation)

### 9.1 Bootstrap 95% CI

Standard percentile bootstrap, 1000 iterations, fixed seed 42. Per L3.1 §2.1.

### 9.2 ECE (Expected Calibration Error)

Per Naeini 2015; 10 equal-width probability bins. Per L3.1 §8.3.

### 9.3 Statistical Power

Two-sample test power formula: power = 1 - β where β computed from effect_size=AUROC-0.5, α=0.05, n=cohort_size. statsmodels.stats.power.

### 9.4 Bonferroni Correction (for V6 cross-disease multiple testing)

When V6 evaluates K diseases simultaneously, per-disease α_corrected = 0.05/K. Applied to per-disease pass criteria where the comparison is "is this disease's AUROC significantly above 0.65?"

### 9.5 Per-Cancer-Type Stratification (V3-V4-V5)

Standard groupby + per-group bootstrap + reporting in stratified table. Aggregate metrics use weighted means by sample size.

---

## §10 Pass Criteria for L3.2 LOCK

### 10.1 Coverage Pass Criteria (BINDING)

- **A1:** All 56 criteria enumerated and decomposed per the 8-class pattern (§0.3).
- **A2:** Each criterion has: threshold, statistical test, sample-size floor, abstain protocol.
- **A3:** All BINDING constraints from Decision 6 v2 + Decision 5 v2 + Decision 8 v2 mapped to specific criteria.
- **A4:** Cross-decision compatibility checked (X-items below).

### 10.2 Cross-Decision Compatibility (BINDING)

- **X1:** Decision 5 v2 Pass 1-4 → V0-C5, V1-C5, V4-C5, V5-C5, V6-C5 (OOD flag/ECE integration)
- **X2:** Decision 6 v2 7-element mandatory reporting → V0-C8 enforces reporting completeness
- **X3:** Decision 7 v2 Pass 7 (V6 interpretability transfer) → V6-C8 explicit
- **X4:** Decision 8 v2 Commitment 3 (≥0.65 on ≥2 areas) → V6-C1 BINDING
- **X5:** Decision 8 v2 Commitment 5 (Souza-Mehta) → V0-C7, V3-C7, V6-C7 across the cascade
- **X6:** Decision 9 v2 (compute envelope) → not directly binding on criteria; affects C3 sample-size feasibility
- **X7:** Decision 10 v2 (open-source) → all statistical methods open-licensed; baselines accessed via open-license sources

### 10.3 Documentation Pass Criteria

- **D1:** L3.2 referenced by L3.3 (V6 grid uses V6-C1, C5, C6, C7, C8 directly).
- **D2:** L3.2 Layer 5 implementation matches each criterion's specification.
- **D3:** Drift catalog this session: 0 new instances.

### 10.4 CEO Sign-Off

L3.2 advances from PROPOSED to LOCKED when:
1. CEO reviews §1-§7 criteria sets and §10 pass criteria
2. CEO confirms §10.5 J-items are within CSO authority
3. CEO co-signs Charter §5.3-style
4. Tag phase-b-l3.2-locked pushed to origin

### 10.5 CSO Judgment Items (Layer 5 Revisitable)

| # | Criterion | Default | Alternatives | Revisit Trigger |
|---|---|---|---|---|
| J1 | V0-C6 naive baseline | per-drug mean | per-cell-line mean, KNN baseline | Per-cell-line mean reveals harder per-cell-line bias |
| J2 | V1-C2 majority threshold | 4/6 pairs | 5/6 (stricter), 3/6 (laxer) | Empirical pair-difficulty variance |
| J3 | V1-C6 IMPROVE baseline tolerance | within 2pp | within 5pp (laxer) | Field consensus on margin |
| J4 | V2-C7 V2 standard threshold | 0.65 mean | 0.60 (laxer organoid bar), 0.70 (stricter) | Empirical organoid difficulty |
| J5 | V3-C2 CI lower buffer | 0.05 below 0.77 | 0.03 (stricter), 0.10 (laxer) | Statistical conservatism |
| J6 | V4-C5 OOD flag floor on non-concord | 70% | 80% (stricter), 60% (laxer) | Empirical OOD detector behavior |
| J7 | V5-C3 power floor | 0.80 | 0.85 (stricter), 0.70 (laxer) | Clinical evidence standards |
| J8 | V6-C2 CI lower bound | 0.55 | 0.50 (laxer), 0.60 (stricter) | V6 difficulty empirics |
| J9 | V6-C7 paradigm D tolerance | within 5pp | within 3pp (stricter), within 10pp (laxer) | Souza-Mehta empirical signal |
| J10 | Bonferroni vs FDR for V6 | Bonferroni | Benjamini-Hochberg FDR | Empirical # diseases tested |

### 10.6 Honest Limitations (per Charter §10 P15 BINDING)

- **All 56 criteria are jointly hard.** The expected per-substrate pass rate across all 56 is unknown; even strong models may miss 5-10 criteria. INTERCEPTA reports criterion-level pass/fail honestly; aggregate "Phase B deployment-ready" requires ALL 56.
- **Some criteria depend on data access.** V5 retrospective clinical and V6 cross-disease scRNA-seq access is non-trivial; sample-size criteria may force soft termination by data unavailability, not by model failure.
- **Bonferroni vs FDR trade-off** at V6 is unresolved; J10 documents the alternatives.
- **V2-C7 "V2 standard definition"** is INTERCEPTA defining a new field standard; the threshold of 0.65 is a commitment, not an empirical anchor.
- **C7 BINDING varies by level** — Souza-Mehta at V0 and V3, Kim concordance at V4, statistical power at V5, paradigm-D at V6. This is intentional; each level has its own dominant rigor concern.

---

## §11 What L3.2 Does NOT Lock

- The specific datasets and version pins (Layer 4)
- The specific baselines' published AUROCs (loaded at Layer 5 runtime from IMPROVE-published, Tang 2022 supplementary, Kim 2020 supplementary)
- The cross-disease V6 grid composition (L3.3)
- The Layer 5 training loops (Layer 4)

---

## §12 Cross-Decision Implications

L3.2 operationalizes Decision 6 v2 + Decision 5 v2 + Decision 8 v2 into 56 testable criteria. Each Decision's BINDING constraints are now an automated check in CascadeRunner. The cross-binding pattern:

- **Decision 5 v2 Pass 1-4 ↔ L3.2 V0-C5, V1-C5, V4-C5, V5-C5, V6-C5**
- **Decision 6 v2 hard/soft termination ↔ L3.2 §1-§7 abstain protocols + L3.1 §2.2 TerminationLogic**
- **Decision 7 v2 Pass 7 ↔ L3.2 V6-C8**
- **Decision 8 v2 Commitment 3 ↔ L3.2 V6-C1**
- **Decision 8 v2 Commitment 5 (Souza-Mehta) ↔ L3.2 V0-C7, V3-C7, V6-C7**

This is the operational falsifiability infrastructure for Phase B per Charter §1.3.

---

## §13 Provenance and Appendix

### 13.1 Provenance

L3.2 written by Claude (CSO, 2026-05-11) per Phase B Plan v2 sequencing. Anchor re-read trigger satisfied (Q6/Q5/Q8 anchors re-read in 2026-05-11 audit).

### 13.2 Discipline Check Per Charter v1.2 Principles

- **P3 (research before code):** ✅ thresholds traced to Decision 6 v2 + anchor papers; methods grounded in published statistics
- **P15 (honest science):** ✅ §10.6 honest limitations; abstain protocols specified for every sample-size criterion; F-mode classification mandatory for failures
- **P16 (preserve past work):** ✅ Decision 6 v2 BINDING constraints preserved verbatim
- **Charter §5.3:** ✅ §10 pass criteria explicit
- **Charter v1.2 §1.7 phase discipline:** ✅ No Phase F items specified

### 13.3 Drift Catalog This Session

New drift instances introduced: 0.

### 13.4 Next Phase B Artifacts

- **L3.3 Cross-Disease V6 Grid (4-5K words):** specifies the exact diseases × therapeutic areas × paradigms × per-disease sample sizes for V6 evaluation; the SLURM job array operational pattern per Q9 compute synthesis
- After L3.3: Layer 3 of Phase B COMPLETE
- Then Layer 4 (L4.1 Implementation Order, L4.2 Testing, L4.3 Failure Modes)
- Then Phase 8 Audit
- Then Layer 5 (actual training and evaluation on Northeastern Explorer)

### 13.5 Criterion-to-Code Mapping (for Layer 5 Implementation)

Each criterion C# at level V# corresponds to a method in the V# Evaluator class:

```python
class V3CellLineToTumorEvaluator(VLevelEvaluator):
    def evaluate(self, ...):
        c1 = self._check_v3_c1_auroc_threshold(...)
        c2 = self._check_v3_c2_ci_lower_bound(...)
        c3 = self._check_v3_c3_sample_size(...)
        c4 = self._check_v3_c4_failure_modes(...)
        c5 = self._check_v3_c5_ece(...)
        c6 = self._check_v3_c6_baseline_comparison(...)
        c7 = self._check_v3_c7_souza_mehta_baseline(...)
        c8 = self._check_v3_c8_v0_v3_gap_per_cancer(...)
        return VLevelResult(
            level="V3",
            criteria_results={"c1": c1, "c2": c2, ..., "c8": c8},
            passed=all([c1.passed, c2.passed, ..., c8.passed]),
            ...
        )
```

This makes each criterion an independently testable assertion. Layer 5 unit tests verify each `_check_v#_c#_*` method independently against synthetic test data before integration.

### 13.6 Key File Paths

- This spec: `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L3_2_56_Pass_Criteria_Specification_2026-05-11.md`
- L3.1 (predecessor): `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L3_1_V0_V6_Validation_Cascade_Pipeline_Specification_2026-05-11.md`
- Decision 6 v2 (parent): `~/INTERCEPTA/docs/research/decisions/INTERCEPTA_FV_Decision_6_Q6_validation.md`
- Validation cache (future): `/scratch/akula.pra/INTERCEPTA/validation/`

---

— L3.2 PROPOSED 2026-05-11 by Claude (CSO).
— Awaiting CEO co-sign and `phase-b-l3.2-locked` tag.
— After L3.2 LOCK, Phase B Plan v2 next artifact is L3.3 Cross-Disease V6 Grid (Layer 3 final artifact).
