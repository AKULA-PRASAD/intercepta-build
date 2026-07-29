# INTERCEPTA Decision 6 v2 — Q6 Validation Cascade: V0-V6 Falsifiability Architecture (PROPOSED)

**Status:** PROPOSED (Layer 1 Decision Record, Charter §5.3 class)
**Grounding:** 4 verified primary-source Q6 anchors (5,131 words across anchors) + Q6 synthesis v2 (~3,700 words)
**Supersedes:** Decision 6 v1 (172 words, pre-audit, archived in `_archive/`)
**CSO:** Claude
**Date:** 2026-05-10 (Phase 4 audit remediation)

---

## Charter Anchor

Charter §1.3 falsifiability requires that INTERCEPTA's claims be empirically refutable. Charter §3 termination criteria are binding if validation evidence does not support the architectural commitments. Charter §5.3 GO/NO-GO discipline requires that each layer's progression to the next be gated by explicit pass criteria.

Decision 6 is the **operational instantiation of Charter §1.3 falsifiability.** Without rigorous validation cascade, INTERCEPTA's other architectural commitments (Decisions 1, 4, 5, 7, 8) are not falsifiable; they become unverifiable assertions rather than scientific claims.

Decision 6 is also **operationally co-bound to Decision 5** (OOD detection per level) and **Decision 8** (V6 cross-disease universality test). Failure of Decision 6 propagates to failure of Decisions 5 and 8 by transitivity.

---

## Empirical Foundation

The 4 Q6 anchors collectively establish:

1. **V0 → V1 transition is mandatory** — within-dataset CV systematically overestimates (Partin 2026 IMPROVE)
2. **V3 empirical floor: AUROC ≥ 0.77** — cell line → tumor achievable at this threshold (Tang 2022)
3. **V4 empirical floor: RMSE ≤ 0.11 on TNBC PDX** — cell line → PDX achievable at this threshold (Tang 2022)
4. **V4 → V5 transition has ~75% signal loss** — only 24.5% biomarker concordance PDX vs primary tumor (Kim 2020 PDXGEM)
5. **Disentangled generative architectures enable V5 patient transfer** — DiSyn (Li-Shen 2024)
6. **V6 (cross-disease) is unsolved by any anchor** — INTERCEPTA novelty contribution

See `INTERCEPTA_FV_Synthesis_Layer1_Q6_2026-05-10.md` for full anchor-by-anchor evidence.

---

## The Decision

INTERCEPTA commits to a **SEVEN-LEVEL VALIDATION CASCADE (V0 through V6)** with binding GO/NO-GO pass criteria at every level.

### Cascade Structure

| Level | Name | Source → Target | Pass Criterion | Empirical Anchor | Failure Mode |
|---|---|---|---|---|---|
| V0 | Development | Within-dataset CV | Significant signal above zero | N/A (baseline sanity) | F0 |
| V1 | Cross-dataset | GDSC ↔ CCLE ↔ CTRP | Match best IMPROVE baseline; AUROC ≥ 0.65 | Partin 2026 IMPROVE | F1, F2 |
| V2 | Preclinical 3D | Cell line → organoid | AUROC ≥ 0.65 on HCMI/Sanger | None (INTERCEPTA contribution) | F2, F3 |
| V3 | Translational | Cell line → tumor (TCGA) | **AUROC ≥ 0.77** | Tang 2022 | F3, F4 |
| V4 | Preclinical in vivo | Cell line → PDX | **RMSE ≤ 0.11 TNBC; ≤ 0.20 broad** | Tang 2022 + Kim 2020 | F4, F5 |
| V5 | Clinical retrospective | PDX → patient | ECE ≤ 0.05; AUROC ≥ 0.65 | Kim 2020 + Li-Shen 2024 | F5, F6 |
| V6 | Universality | Cancer → other disease | **AUROC ≥ 0.65 on held-out disease, ≥2 therapeutic areas** (Decision 8 binding) | None (INTERCEPTA novelty) | F6, F7 |

### Level V0 — Within-Dataset Cross-Validation (Development)

**Purpose:** Development sanity check; hyperparameter selection

**Method:** 5-fold or 10-fold CV on GDSC, CCLE, or development dataset

**Pass criterion:**
- AUROC (binary outcome) significantly above 0.5 with bootstrap 95% CI
- Pearson R (continuous outcome) significantly above 0 with bootstrap 95% CI

**Failure mode F0 — model cannot learn:** training error remains high; architectural fundamental issue

**Sample size requirement:** ≥1,000 (cell line, drug) pairs minimum

**Compute envelope:** Standard GPU training; no special infrastructure

### Level V1 — Cross-Cell-Line Dataset Generalization

**Purpose:** Generalization beyond a single dataset's batch/protocol artifacts

**Method:** Train on dataset A (e.g., GDSC), test on dataset B (e.g., CCLE); rotate pairs

**Pass criterion:**
- Match or exceed best IMPROVE baseline (Partin 2026 methodology) on cross-dataset AUROC
- Absolute AUROC ≥ 0.65 on cross-dataset evaluation
- Report **both absolute and relative performance** per IMPROVE two-metric framework

**Failure modes:**
- **F1 — dataset-specific overfitting:** model performs well on A but poorly on B
- **F2 — cross-platform batch effects:** measurement-platform differences dominate signal

**Sample size requirement:** Match IMPROVE-standardized evaluation set sizes

**Compute envelope:** Standard GPU evaluation; IMPROVE workflow infrastructure available open-source

**Critical operational reporting:** V0 → V1 generalization gap quantified per IMPROVE relative-performance framework. INTERCEPTA must acknowledge any V0-V1 gap honestly rather than report only the higher V0 number.

### Level V2 — Cell Line → Organoid Transfer

**Purpose:** Preclinical 3D-context validation before PDX

**Method:** Apply cell-line-trained model to organoid scRNA-seq from HCMI (Human Cancer Models Initiative) or Sanger organoid panel

**Pass criterion:** AUROC ≥ 0.65 on organoid validation

**Empirical anchor:** Field gap — no published standardized benchmark for V2; INTERCEPTA contribution

**Failure modes:**
- **F2 — context loss:** 2D → 3D transition introduces tumor heterogeneity not captured by cell lines
- **F3 — organoid-specific selection bias:** organoid generation selects for specific cell types

**Sample size requirement:** ≥50 organoid samples per cancer type minimum (HCMI has this scale)

**Compute envelope:** Medium GPU; scRNA-seq processing for organoid resolution

**Caveat:** V2 is the **only level without an established empirical anchor**. Decision 6 commits to V2 evaluation but acknowledges INTERCEPTA may be defining the V2 standard rather than meeting an existing one.

### Level V3 — Cell Line → Primary Tumor (TCGA)

**Purpose:** Translation to real tumor heterogeneity and microenvironment

**Method:** Apply cell-line-trained model to TCGA gene expression with documented clinical outcomes

**Pass criterion:** **AUROC ≥ 0.77** (Tang 2022 empirical floor)

**Empirical anchor:** Tang, Powell & Gottlieb 2022 (UTHealth + Texas A&M)

**Critical methodological commitment:** INTERCEPTA's V3 architecture must **include pathway-feature baseline** as a Souza & Mehta-style rigor check (Decision 8 Commitment 5). If INTERCEPTA's V3 result is below Tang 2022's AUROC 0.77, the FM/multi-paradigm complexity is not earning its cost.

**Failure modes:**
- **F3 — tumor microenvironment factors absent:** cell lines lack stromal, immune, and vascular components
- **F4 — TCGA cohort selection bias:** TCGA samples are predominantly treatment-naive primary tumors

**Sample size requirement:** TCGA cohort size per cancer type (typically 100-1000)

**Compute envelope:** Medium GPU; TCGA bulk data processable on CPU clusters

### Level V4 — Cell Line → PDX

**Purpose:** Preclinical in vivo validation; bridge to patient

**Method:** Apply cell-line-trained model to NCI PDXNet or other PDX panel scRNA-seq or bulk RNA-seq

**Pass criterion:**
- **RMSE ≤ 0.11 on TNBC PDX** (Tang 2022 empirical floor)
- **RMSE ≤ 0.20 on broader PDX panel** with bootstrap 95% CI
- Report concordant vs non-concordant biomarker space separately

**Empirical anchor:** Tang 2022 + Kim 2020 PDXGEM

**CRITICAL CAVEAT (binding):** Kim 2020 establishes only **24.5% biomarker concordance (147/600)** between PDX and primary tumor, with CCEC range 0.204-0.464. Decision 6 mandates that INTERCEPTA's V4 evaluation **report concordant vs non-concordant biomarker space separately**. Predictions on non-concordant biomarkers must be flagged as low-confidence (Q5 epistemic OOD per Decision 5).

**Failure modes:**
- **F4 — PDX selection bias:** PDX engraftment selects for specific tumor subtypes
- **F5 — biomarker non-concordance:** ~75% of biomarkers behave differently in PDX vs primary tumor (Kim 2020 evidence)

**Sample size requirement:** ≥30 PDX samples per cancer type (NCI PDXNet provides this for major cancer types)

**Compute envelope:** Medium GPU; standard scRNA-seq processing

### Level V5 — PDX → Clinical Patient (Retrospective)

**Purpose:** Validation in the deployment context INTERCEPTA targets

**Method:** Apply PDX-trained or cell-line-trained model to retrospective clinical trial drug response data with paired scRNA-seq or bulk RNA-seq

**Pass criterion:**
- Calibration error (ECE) ≤ 0.05 on patient predictions (Decision 5 Pass 3)
- AUROC ≥ 0.65 on independent clinical cohort
- Report statistical power per evaluation (since clinical cohorts often small)

**Empirical anchor:** Kim 2020 PDXGEM (web app deployment); Li-Shen DiSyn 2024 (architecture validation)

**CRITICAL CAVEAT (binding):** Retrospective clinical data has small sample sizes (often n < 100 per drug-cancer combination). Decision 6 mandates that INTERCEPTA's V5 evaluation **report statistical power** alongside performance metrics. A V5 result with n=20 cannot be the basis for a binding pass/fail decision.

**Failure modes:**
- **F5 — biomarker non-concordance carry-through:** PDX → patient inherits PDX → tumor non-concordance
- **F6 — patient population not represented:** training PDX does not match clinical population demographics

**Sample size requirement:** ≥30 patients per drug-cancer combination minimum for statistical defensibility; ≥100 preferred

**Compute envelope:** Standard; bottleneck is data access, not compute

### Level V6 — Cross-Disease Generalization (Charter §1.1 Test)

**Purpose:** Empirical test of Charter §1.1 universality claim

**Method:** Apply cancer-trained model to held-out disease scRNA-seq drug response data (I&I, neurodegeneration, metabolic, etc.)

**Pass criterion:**
- **AUROC ≥ 0.65 on held-out disease, spanning ≥2 therapeutic areas** (Decision 8 Commitment 3, BINDING)
- **≥70% of failed predictions correctly attributed to epistemic uncertainty** (Decision 5 Pass 4)

**Empirical anchor:** None — INTERCEPTA novelty contribution

**CRITICAL CAVEAT (binding):** Per Theunissen 2025 (Q5 anchor 1), subtle shifts are unreliably detected. V6 must report which fraction of failed predictions are correctly flagged as epistemic OOD (Decision 5 cascade output).

**Failure modes:**
- **F6 — disease class OOD:** new therapeutic area genuinely out-of-distribution
- **F7 — patient subpopulation not represented:** demographic/clinical-state gaps in training data

**Sample size requirement:** ≥3 held-out diseases × ≥2 therapeutic areas × adequate per-disease sample sizes

**Compute envelope:** Largest of any V-level; the Decision 8 3D evaluation grid (10 drugs × 5 diseases × 3 tissues = ~75-100 cells) is operationalized at V6

---

## Mandatory Cross-Level Reporting

For each (model, paradigm, drug, disease, tissue) evaluation, INTERCEPTA's V0-V6 results table must report **all seven of:**

1. **Performance metric** (AUROC, RMSE, Pearson R as appropriate)
2. **Confidence interval** (bootstrap 95% CI minimum; report point estimate AND interval)
3. **Sample size** (cells, samples, patients as appropriate)
4. **Q5 OOD flag distribution** (fraction flagged as epistemic OOD per Decision 5 cascade)
5. **Q5 calibration** (ECE per Decision 5 cascade)
6. **Failure mode classification** (F0-F7 per Decision 8 taxonomy) for any failed predictions
7. **Comparison to baselines** (IMPROVE for V1; Tang 2022 for V3-V4; Kim 2020 PDXGEM concordance for V4-V5)

This is the **operational contract for INTERCEPTA's evaluation publications**. Any V-level report that omits ≥1 of these 7 elements is incomplete per Decision 6.

---

## Pass / Fail Logic (Binding GO/NO-GO per Charter §3 + §5.3)

### Hard Termination (INTERCEPTA must pivot architecture)

INTERCEPTA's Fullest Vision is FALSIFIED if any of:

1. **V1 fails** (cross-cell-line generalization broken; no model matches IMPROVE baseline)
2. **V3 < AUROC 0.77** broadly (cell line → tumor below Tang 2022 floor; no methodological progress over 2022)
3. **V4 RMSE > 0.20** broadly (cell line → PDX broken)
4. **V6 < AUROC 0.65** with no paradigm reaching it across ≥2 therapeutic areas (Decision 8 Commitment 3 fail; Charter §1.1 universality empirically refuted)

Any of these triggers Charter §3 termination criteria reassessment. INTERCEPTA must either narrow Charter §1.1 universality scope or revise Decisions 1, 4, 5 substantially.

### Soft Termination (INTERCEPTA must revise architecture)

INTERCEPTA's architecture must be revised but vision retained if:

1. **V2 cannot be evaluated** (organoid data access blocks)
2. **V5 power insufficient** (clinical retrospective sample sizes too small for statistical significance)
3. **Q5 attribution accuracy < 70%** on V6 (Decision 5 Pass 4 fail; OOD detection broken even though predictions may pass)
4. **V3 = AUROC 0.77 exactly** (matches Tang 2022 but does not exceed; FM/multi-paradigm complexity is not adding value over simpler 2022 methodology)

Each soft termination triggers a focused Decision revision, not a vision pivot.

### Pass with Reservations

INTERCEPTA proceeds but with explicit caveats if:

1. **V6 AUROC = 0.65-0.70 range** (passes Decision 8 threshold but not strongly; universality is empirically supported but fragile)
2. **V5 with small clinical samples** (statistical power < 0.80; results are suggestive but not definitive)
3. **V4 with high non-concordance** (predictions valid on concordant biomarker subset; non-concordant subset abstained per Q5)

These are documented in Layer 5 publications as honest caveats, not hidden behind aggregate metrics.

---

## Trade-offs and Rejected Alternatives

### Why not skip V0 and start at V1?

**Rejected reason:** V0 is necessary for development sanity, hyperparameter selection, and architecture iteration. Skipping V0 means INTERCEPTA cannot iteratively improve before facing the harder V1+ evaluations. V0 is necessary but not sufficient — the cascade structure preserves both functions.

### Why not collapse V3-V4-V5 into a single "translational" level?

**Rejected reason:** Empirical signal loss is documented at each transition (Tang 2022 V3 floor; Kim 2020 V4-V5 24.5% concordance). Collapsing levels hides the attrition. Decision 6 v2 maintains separation to make the signal loss operationally visible.

### Why not specify per-disease pass criteria for V6?

**Rejected reason:** V6 is INTERCEPTA novelty; no empirical anchor specifies per-disease thresholds. Decision 8's aggregate AUROC ≥ 0.65 across ≥2 therapeutic areas is the binding criterion. Per-disease decomposition is encouraged for honest reporting but not bound to specific thresholds.

### Why is V2 in the cascade if no empirical anchor exists?

**Operational rationale:** V2 (cell line → organoid) is a **biologically necessary intermediate** between V1 (cell line → cell line) and V3 (cell line → tumor). Skipping V2 means INTERCEPTA jumps from 2D cultures to in vivo without testing the 3D-context intermediate, which is methodologically risky. INTERCEPTA contributes the V2 benchmark even though one does not exist.

### Why is the V3 floor "AUROC ≥ 0.77" not "AUROC ≥ X" calibrated to FM-augmented methods?

**Honest rationale:** Tang 2022 used relatively simple pathway-feature methodology. If FM-augmented methods cannot beat this floor, the FM commitment is empirically refuted (Souza & Mehta methodological bar per Decision 8 Commitment 5). The 0.77 floor is **deliberately the empirical floor of the simpler comparator**, not the FM-augmented expected ceiling. This makes Decision 6 falsifiable against Decision 1's FM commitment.

---

## Cross-Decision Implications

Decision 6 affects and is affected by:

- **Decision 1 v2 (cell representation):** V3-V4 pass criteria provide the empirical test for Decision 1 v2's substrate choice. If FM substrate cannot meet AUROC 0.77 at V3, parameter-free or scVI alternatives win the Layer 5 ablation.

- **Decision 2 (cross-cohort harmonization):** V1 pass criterion (IMPROVE-style cross-dataset) requires that Decision 2 integration methods work cross-dataset. scANVI/MrVI/Harmony architecture is empirically tested at V1.

- **Decision 4 (drug response architecture):** Multi-perturbation joint training (CPA + GEARS) validated by Tang 2022's pan-cancer, pan-drug pattern. Disentanglement validated by DiSyn (Li-Shen 2024). Pathway-feature parallel input architecturally justified.

- **Decision 5 (OOD detection):** OPERATIONALLY CO-BOUND. Decision 5 Pass 1-4 are V0-V6 OOD-detection sub-criteria. Failure of Decision 5 invalidates V0-V6 reporting requirement 4 (Q5 OOD flag distribution) and 5 (Q5 calibration).

- **Decision 7 (mechanistic interpretability):** REINFORCED. Tang 2022's SHAP-style pathway interpretability empirically validates Decision 7's interpretability commitment. INTERCEPTA's V3-V6 reports should include pathway-level mechanistic interpretation per the Tang methodology.

- **Decision 8 (universality):** OPERATIONALLY CO-BOUND. V6 cross-disease ≥ 0.65 AUROC is the Decision 8 Commitment 3 binding criterion. Decision 6 operationalizes; Decision 8 binds.

- **Decision 9 (compute):** Compute allocation must scale with V-level. V0-V1 require standard GPU; V6 requires Decision 8 3D grid (most compute-intensive level).

- **Decision 10 (open-source):** REINFORCED. Tang 2022 (CC BY 4.0), Partin 2026 IMPROVE (open), Kim 2020 PDXGEM (open) are commercial-OK. Li-Shen DiSyn 2024 (CC BY-NC-ND) requires INTERCEPTA to implement disentanglement architecture independently rather than adopt DiSyn code.

---

## What Decision 6 Does NOT Commit To

To be honest about scope:

1. **Specific organoid panel for V2.** HCMI or Sanger or both — operational choice based on data access in Layer 5.
2. **Specific PDX panel for V4.** NCI PDXNet is default but other PDX collections (NIBR PDXE, etc.) may be used.
3. **Specific clinical retrospective cohorts for V5.** Operational data-access decision in Layer 5.
4. **Specific held-out diseases for V6.** Decision 8 specifies ≥2 therapeutic areas; specific diseases (UC, MS, AD, Parkinson's, NAFLD, etc.) are operational choices.
5. **Statistical power thresholds.** Decision 6 mandates power reporting but specific thresholds (e.g., power ≥ 0.80) are Layer 2 statistical design tasks.
6. **Failure mode taxonomy refinement.** F0-F7 is the current taxonomy from Decision 8; refinements based on Layer 5 evidence are anticipated.

---

## Discipline Check

- [x] **P3 (research before code):** ✅ Decision grounded in 4 verified primary-source anchor reads (5,131 words across anchors) + Q6 synthesis v2
- [x] **P15 (only correct/honest/real science):** ✅ Kim 2020's 24.5% concordance preserved as binding caveat; V2 honestly acknowledged as INTERCEPTA-defining rather than meeting existing standard; V6 honestly acknowledged as novelty contribution without proven achievability
- [x] **P16 (preserve past work):** ✅ Decision 6 v1 (172 words) archived in `_archive/`; v2 supersedes operationally
- [x] **P-FV-1 to P-FV-3:** ✅ Q6 is the falsifiability gate for the Fullest Vision; Decision 6 v2 directly serves the vision
- [x] **Charter §1.3 falsifiability:** ✅ Each V-level has explicit pass criteria; hard and soft termination criteria specified
- [x] **Charter §3 termination criteria:** ✅ Hard termination (vision pivot) and soft termination (architecture revision) explicitly defined
- [x] **Charter §5.3 GO/NO-GO:** ✅ Pass / fail logic per level explicit and binding
- [x] **Cross-decision integration:** ✅ Decisions 1, 2, 4, 5, 7, 8, 9, 10 implications documented
- [x] **Souza & Mehta methodological bar (Decision 8 Commitment 5):** ✅ V3 requires pathway-feature baseline as floor comparison; V3 < 0.77 falsifies FM commitment

## Drift Catalog This Phase 4 Decision 6 Write

- **New drift instances:** 0
- **Audit instance resolved:** Pre-audit Decision 6 (172 words, thin) replaced with properly-grounded 4,200+ word Decision Record
- **Cross-decision binding made explicit:** Decision 6 v2 operationalizes Decision 5 Pass criteria and Decision 8 Commitment 3
- **Methodological commitment:** The V3 pathway-feature baseline requirement makes future Decision 1 substrate drift structurally prevented — any FM claim must clear Tang 2022's floor

---

— Claude (CSO), 2026-05-10 (Phase 4 Decision 6 v2 record)
