# INTERCEPTA Layer 1 Q6 Synthesis v2 — The Falsifiability Cascade: V0 → V6 Validation Architecture

**CSO:** Claude
**Date:** 2026-05-10
**Phase:** 4 re-do (audit remediation)
**Scope:** Integrating 4 verified primary-source anchor reads (5,131 words across anchors) to ground Decision 6
**Supersedes:** Q6 Synthesis v1 (294 words, pre-audit, archived in `_archive/`)

---

## Executive Summary

Q6 (validation cascade) is **the falsifiability gate for INTERCEPTA's entire vision.** Charter §1.3 explicitly requires that INTERCEPTA's claims be empirically refutable; Charter §3 makes termination criteria binding if validation evidence does not support the architectural commitments. Decisions 5 (OOD detection) and 8 (universality) both reference V0-V6 pass criteria — Q6 is operationally the integration point that determines whether INTERCEPTA's other architectural choices are vindicated or falsified.

The 4 verified Q6 anchors collectively establish:

1. **Within-dataset cross-validation systematically overestimates performance** (Partin 2026 IMPROVE) — V0 alone is insufficient; cross-dataset evaluation is mandatory
2. **Cell line → tumor transfer is achievable at AUROC = 0.77** (Tang 2022 pathway methodology) — V3 empirical floor
3. **Cell line → PDX (TNBC) transfer is achievable at RMSE = 0.11** (Tang 2022) — V4 empirical floor
4. **Patient-level transfer is achievable via disentanglement** (Li-Shen DiSyn 2024) — V5 architecture validation
5. **PDX → patient translation is empirically partial (24.5% biomarker concordance, CCEC 0.204-0.464)** (Kim PDXGEM 2020) — V4-V5 gap quantified
6. **Multi-cancer, multi-drug joint training improves generalization** (Tang 2022) — Decision 4 architectural commitment validated

**The most consequential finding:** Kim 2020 PDXGEM established that only **147 of 600 candidate biomarkers (24.5%) showed concordant expression between PDXs and primary tumors**. This means the cell line → PDX → patient cascade has a substantial signal loss at every step, and Decision 6 must engineer around it rather than claiming clean transfer.

**Decision 6 is a six-level validation cascade with binding pass criteria at every level**, integrated with Decision 5 (OOD detection per level) and Decision 8 (V6 cross-disease as the universality test). The cascade is empirically grounded — each level has a documented anchor providing the empirical floor.

---

## What Each Anchor Establishes

### Anchor 1 — Partin et al. 2026 (IMPROVE benchmark, *Brief Bioinformatics*)

**Established empirically:**
- IMPROVE framework (NCI + DOE consortium backing): 5 publicly available drug screening datasets × 6 standardized DRP models × scalable cross-dataset evaluation workflow
- **Within-dataset CV systematically overestimates performance** vs cross-dataset evaluation — not a single-model artifact; the gap exists across all 6 models tested
- Cross-dataset generalization gap varies by (drug type, dataset pair, model architecture)
- Two-metric framework: **absolute performance** (predictive accuracy) + **relative performance** (drop vs within-dataset baseline)

**What this contributes to Decision 6:** The V0 → V1 transition is empirically mandatory. Within-dataset CV (V0) is necessary but not sufficient — cross-dataset (V1) must be the actual pass criterion.

**What this does NOT establish:** scRNA-seq cross-dataset performance (IMPROVE is bulk-only). Cross-disease generalization (cancer-only). FM-augmented method performance (predates widespread FM benchmark integration).

### Anchor 2 — Tang, Powell & Gottlieb 2022 (UTHealth Houston + Texas A&M, *Scientific Reports*)

**Established empirically:**
- Pathway-feature transfer learning workflow: cell lines → tumors and cell lines → PDX
- **AUROC = 0.77** on TCGA tumor samples (V3 empirical floor)
- **RMSE = 0.11** on PDX from triple-negative breast cancer (V4 empirical floor)
- Pathway-level features improve transfer vs raw gene expression — biological prior helps
- Pan-cancer, pan-drug architecture improves generalization vs per-drug models
- Mechanistically interpretable findings (ER-Golgi + everolimus; class II HDACs + IL-12 + TNBC)

**What this contributes to Decision 6:** The empirical floor for V3 and V4. Tang et al. is also the **Souza & Mehta-style rigor check at Decision 6** — if INTERCEPTA cannot beat this simpler methodology, the FM/multi-paradigm complexity is not earning its cost.

**What this does NOT establish:** Cancer-only validation (no I&I or neurodegeneration). TNBC-only PDX (no other PDX cancer types). Bulk-level (no scRNA-seq). Pre-FM era.

### Anchor 3 — Li, Shen et al. 2024 (Shanghai Institute of Nutrition and Health, *J Pharm Analysis*)

**Established empirically and architecturally:**
- DiSyn: disentangled generative model for sample synthesis enabling cell line → patient transfer
- Equal first-authorship Li K* + Shen B*; senior Hong Li (LiHongCSBLab)
- Multi-dataset validation: TCGA + I-SPY2 + NIBR PDXE (Novartis Institutes for BioMedical Research preclinical PDX panel)
- Achieves cell line → patient transfer via shared latent space architecture
- 5-12% improvement on patient transfer tasks
- CC BY-NC-ND license (academic use OK; commercial use restricted)

**What this contributes to Decision 6:** V5 architecture validation. Disentanglement is empirically validated as a transfer mechanism. Aligns with Decision 4's CPA-style latent space disentanglement commitment.

**What this does NOT establish:** Drug response prediction on truly held-out diseases. License compatibility for commercial INTERCEPTA deployment (CC BY-NC-ND restrictive). Comparison to FM-substrate alternatives.

### Anchor 4 — Kim et al. 2020 (Moffitt Cancer Center + USF, *BMC Bioinformatics*)

**Established empirically and quantitatively:**
- PDXGEM: Patient-Derived Tumor Xenograft-based Gene Expression Model for clinical response prediction
- **600 initial probesets → 147 CCE biomarkers (24.5% concordance)** between PDX and primary tumors
- Concordance Correlation Coefficient (CCEC) range: **0.204-0.464** — moderate at best
- 6 drug-cancer pairs evaluated: paclitaxel + trastuzumab (breast), 5FU + cetuximab (CRC), gemcitabine (pancreatic), erlotinib (NSCLC)
- Publicly available web app: http://pdxgem.moffitt.org
- 4-step methodology: PDX→tumor concordance screen → biomarker selection → model training → clinical validation

**What this contributes to Decision 6:** **Quantitative gap measurement for V4 → V5 (PDX → clinical patient) translation.** The 24.5% concordance is empirical reality, not a methodological pessimism. Decision 6 must operationally distinguish concordant (predictable) from non-concordant (unpredictable) biomarker space.

**What this does NOT establish:** Whether scRNA-seq or FM-derived features improve concordance over bulk-RNA-seq biomarkers. Whether the 24.5% concordance is fundamental or methodologically improvable.

---

## Convergent Patterns Across the 4 Anchors

### Pattern A — Each validation level has measurable signal loss

The cascade has empirically-quantified attrition:

| Transition | Empirical evidence | Approximate signal loss |
|---|---|---|
| V0 (within-dataset CV) | Partin 2026 IMPROVE | Baseline (overestimate) |
| V0 → V1 (cross-cell-line) | Partin 2026 IMPROVE | Significant drop (varies by model) |
| V1 → V3 (cell line → tumor) | Tang 2022 AUROC 0.77 | Achievable but with effort |
| V3 → V4 (cell line → PDX) | Tang 2022 RMSE 0.11 (TNBC); Kim 2020 CCEC 0.204-0.464 | Substantial; ~75% biomarker non-concordance |
| V4 → V5 (PDX → patient) | Kim 2020 PDXGEM 24.5% concordance | Substantial |
| V5 → V6 (cross-disease) | Empirically untested by these anchors | **Unknown — INTERCEPTA novelty** |

**Decision 6 must explicitly quantify the signal loss at each transition**, not hide it behind aggregate metrics.

### Pattern B — Pathway-level features improve transfer vs raw expression

Tang 2022 establishes this empirically for cell line → tumor. Kim 2020 uses gene-level biomarkers and gets 24.5% concordance — suggesting raw-gene-level transfer is harder than pathway-level. **Decision 4's pathway-feature branch is empirically validated as a transfer-enhancement architectural choice**, not just a Charter §8.1 design preference.

### Pattern C — Multi-cancer/multi-drug joint training improves generalization

Tang 2022's pan-cancer, pan-drug design empirically outperforms single-drug models. This **validates Decision 4's commitment to multi-perturbation joint training** (CPA + GEARS architecture) over per-drug models.

### Pattern D — Disentanglement is a viable transfer mechanism

Li-Shen DiSyn 2024 demonstrates disentangled generative architecture enables cell line → patient transfer. This **reinforces Decision 4's CPA-style latent space disentanglement**, providing empirical evidence beyond CPA's own validation.

### Pattern E — Cross-disease (V6) is unsolved by any anchor

All 4 anchors are cancer-only. **V6 is INTERCEPTA's novelty contribution**, not a known-solved problem. Decision 8's V6 AUROC ≥ 0.65 threshold is therefore an empirical hypothesis to test, not a documented achievable target.

### Pattern F — Standardized benchmarks exist for V1 but not V2-V6

IMPROVE provides V1 standardization. **No published benchmark provides standardized V2-V6 evaluation.** INTERCEPTA's contribution includes building V2-V6 standardization (organoid panels, PDX panel, clinical retrospective, cross-disease) — or adopting partial standardization from each anchor (Tang for V3-V4; Kim for V4-V5; Li-Shen for V5).

---

## What the Field Has NOT Resolved (Honest Gaps)

Reading across all 4 anchors, the field's open questions for Q6:

1. **scRNA-seq cross-dataset validation standards.** IMPROVE is bulk-only. INTERCEPTA needs scRNA-seq-equivalent of IMPROVE for V1.

2. **Cell line → organoid (V2) standardization.** HCMI, Sanger organoid panel exist but no published cross-method benchmark establishes empirical V2 floors.

3. **PDX panel beyond TNBC.** Tang 2022 RMSE 0.11 is TNBC-specific; other cancer-type PDX targets are unestablished.

4. **Clinical retrospective (V5) data access.** Even when methodologies exist (PDXGEM), access to retrospective clinical drug response data with paired scRNA-seq is severely limited.

5. **V6 cross-disease threshold validity.** Decision 8's 0.65 AUROC is calibrated to Theunissen 2025's "but not reliably" caveat. Whether 0.65 is achievable, too easy, or too hard is empirically untested.

6. **Statistical power at higher cascade levels.** V0 has thousands of samples (cell line datasets); V5 may have dozens (clinical trial subsets). Decision 6 must specify minimum sample sizes for binding GO/NO-GO decisions to be statistically defensible.

---

## Cross-Decision Architectural Patterns

The Q6 anchors inform decisions beyond Decision 6:

### For Decision 1 v2 (cell representation)

Tang 2022's pathway-feature transfer establishes that **simpler representations transfer well**. This is consistent with Decision 1 v2's deferral of substrate choice to Layer 5 ablations — pathway features may be a candidate alongside (or instead of) FM embeddings. INTERCEPTA's V3-V4 ablations must include pathway-feature baseline.

### For Decision 4 (drug response architecture)

- Pattern C (multi-perturbation joint training validated)
- Pattern D (disentanglement validated)
- Pattern B (pathway-feature branch architecturally justified)

All three reinforce Decision 4's PROPOSED architecture (CPA + GEARS + FM-encoder with pathway-feature parallel input).

### For Decision 5 (OOD detection)

**The Decision 5 v2 pass criteria 1-4 are operationally the V0-V6 OOD-detection sub-criteria:**
- Decision 5 Pass 1 (V0-V1 OOD AUROC ≥ 0.80) ↔ Decision 6 V0-V1 OOD reporting
- Decision 5 Pass 2 (V3-V4 OOD AUROC ≥ 0.70) ↔ Decision 6 V3-V4 OOD reporting
- Decision 5 Pass 3 (V5 ECE ≤ 0.05) ↔ Decision 6 V5 calibration reporting
- Decision 5 Pass 4 (V6 epistemic attribution ≥70%) ↔ Decision 6 V6 OOD reporting

Decision 5 and Decision 6 are **operationally co-bound** — failure of either invalidates the other.

### For Decision 7 (mechanistic interpretability)

Tang 2022's pathway-level interpretability + SHAP-style feature importance provides **empirical validation for Decision 7's mechanistic interpretability commitment**. The pathway → drug associations (ER-Golgi + everolimus; HDACs + TNBC drugs) are mechanistically plausible — interpretability layer works in practice.

### For Decision 8 (universality)

**Decision 6 V6 = Decision 8 Commitment 3 V6 pass criterion.** They are the same threshold. Decision 6 operationalizes it; Decision 8 binds it. The 0.65 AUROC ≥ threshold flows from Theunissen 2025's "but not reliably" caveat (Q5 anchor 1) plus Kim 2020's 24.5% concordance evidence (Q6 anchor 4).

### For Decision 9 (compute)

Decision 6's six-level cascade has variable compute requirements:
- V0-V1: standard CV, large datasets, GPU-feasible
- V2-V4: medium datasets, GPU-affordable
- V5: small datasets, CPU often sufficient
- V6: large evaluation grid (Decision 8 3D grid), GPU-intensive

Decision 9 must allocate compute proportionally per level — most goes to V6 cross-disease grid.

### For Decision 10 (open-source)

- Tang 2022 (CC BY 4.0): commercial-OK — INTERCEPTA can adopt pathway-feature methodology freely
- Partin 2026 IMPROVE (Argonne/NCI open): commercial-OK — IMPROVE framework freely usable
- Kim 2020 PDXGEM (BMC open): commercial-OK — web app + methodology adoptable
- Li-Shen DiSyn 2024 (CC BY-NC-ND): **non-commercial only** — license constraint INTERCEPTA must respect or implement disentanglement independently

**Decision 10 implication:** 3 of 4 Q6 anchors are commercial-OK; DiSyn is the exception. INTERCEPTA's commercial deployment can use the methodologies but should implement disentanglement architecture independently (not adopt DiSyn code).

---

## Decision 6 — REVISED PROPOSED

The revised Decision 6 commitment (to be formalized as a Decision Record file) is the **SEVEN-LEVEL VALIDATION CASCADE V0-V6** with binding GO/NO-GO criteria.

### Level V0 — Within-Dataset Cross-Validation (Development)

**Source:** GDSC, CCLE, or single-dataset training data
**Method:** Standard 5-fold or 10-fold cross-validation
**Pass criterion:** AUROC (binary) or Pearson R (continuous) above zero with statistical significance
**Purpose:** Development sanity check; sufficient for hyperparameter selection
**Failure mode:** F0 — model fundamentally cannot learn the task

### Level V1 — Cross-Cell-Line Dataset Generalization

**Source:** GDSC train → CCLE test (and rotate pairs)
**Method:** Train on one dataset, evaluate on another; rotate across pairs
**Pass criterion:** Match or exceed best IMPROVE baseline + AUROC ≥ 0.65 absolute
**Empirical anchor:** Partin 2026 IMPROVE methodology
**Purpose:** Generalization beyond a single dataset's batch/protocol
**Failure mode:** F1 — dataset-specific overfitting; F2 — cross-platform batch effects

### Level V2 — Cell Line → Organoid Transfer

**Source:** Cell line training → HCMI (Human Cancer Models Initiative) or Sanger organoid panel test
**Method:** Apply cell-line-trained model to organoid scRNA-seq
**Pass criterion:** AUROC ≥ 0.65 on organoid validation
**Empirical anchor:** Field gap — no published standardized benchmark; INTERCEPTA contribution
**Purpose:** Preclinical 3D-context validation before PDX
**Failure mode:** F2 — context loss from 2D → 3D; F3 — organoid-specific selection bias

### Level V3 — Cell Line → Primary Tumor (TCGA)

**Source:** Cell line training → TCGA tumor cohort test
**Method:** Apply cell-line-trained model to TCGA gene expression
**Pass criterion:** **AUROC ≥ 0.77** (Tang 2022 empirical floor)
**Empirical anchor:** Tang, Powell & Gottlieb 2022 (UTHealth + Texas A&M)
**Purpose:** Translation to real tumor heterogeneity and microenvironment
**Failure mode:** F3 — tumor microenvironment factors absent from cell lines; F4 — TCGA cohort selection bias

### Level V4 — Cell Line → PDX

**Source:** Cell line training → NCI PDXNet or other PDX panel test
**Method:** Apply cell-line-trained model to PDX scRNA-seq or bulk RNA-seq
**Pass criterion:** **RMSE ≤ 0.11 on TNBC PDX** (Tang 2022 empirical floor); on broader PDX panel, RMSE ≤ 0.20 with confidence intervals
**Empirical anchor:** Tang 2022 + Kim 2020 PDXGEM
**Critical caveat:** Kim 2020 establishes **only 24.5% biomarker concordance** between PDX and primary tumor. Decision 6 must report concordant vs non-concordant biomarker space separately.
**Purpose:** Preclinical in vivo validation; bridge to patient
**Failure mode:** F4 — PDX selection bias; F5 — biomarker non-concordance (Kim 2020 evidence)

### Level V5 — PDX → Clinical Patient (Retrospective)

**Source:** PDX-trained model → retrospective clinical trial drug response data
**Method:** Apply PDX-trained model to clinical samples with documented drug response outcomes
**Pass criterion:** Calibration error (ECE) ≤ 0.05 + AUROC ≥ 0.65 on independent clinical cohort
**Empirical anchor:** Kim 2020 PDXGEM (web app deployment); Li-Shen DiSyn 2024 (architecture validation)
**Critical caveat:** Retrospective clinical data has small sample sizes (often n < 100 per drug-cancer combination); statistical power must be reported per evaluation
**Purpose:** Validation in the deployment context INTERCEPTA targets
**Failure mode:** F5 — biomarker non-concordance carry-through; F6 — patient population not represented in PDX training

### Level V6 — Cross-Disease Generalization

**Source:** Cancer-trained model → I&I, neurodegeneration, or metabolic disease test
**Method:** Apply cancer-trained model to held-out disease scRNA-seq drug response data
**Pass criterion:** **AUROC ≥ 0.65 on held-out disease, spanning ≥2 therapeutic areas** (Decision 8 Commitment 3, BINDING)
**Empirical anchor:** None — INTERCEPTA novelty contribution
**Critical caveat:** Per Theunissen 2025, subtle shifts are unreliably detected by Q5. V6 must report which fraction of failed predictions are correctly flagged as epistemic (Decision 5 Pass 4: ≥70% epistemic attribution)
**Purpose:** Charter §1.1 universality empirical test
**Failure mode:** F6 — disease class OOD; F7 — patient subpopulation not represented

### Mandatory Cross-Level Reporting

For each (model, paradigm, drug, disease, tissue) evaluation, INTERCEPTA reports:
1. **Performance metric** (AUROC, RMSE, Pearson R as appropriate)
2. **Confidence interval** (bootstrap 95% CI minimum)
3. **Sample size** (cells, samples, patients as appropriate)
4. **Q5 OOD flag distribution** (fraction flagged as epistemic OOD per Decision 5)
5. **Q5 calibration** (ECE per Decision 5)
6. **Failure mode classification** (F0-F7 from Decision 8 taxonomy) for any failed predictions
7. **Comparison to IMPROVE baselines** (where available) and Tang 2022 floors (for V3-V4)

### Termination Criteria (per Charter §3 + §5.3)

**Hard termination — INTERCEPTA must pivot if any of:**
- V1 fails (cross-cell-line generalization broken)
- V3 < AUROC 0.77 (cell line → tumor below 2022 floor — no methodological progress)
- V4 RMSE > 0.20 broadly (cell line → PDX broken)
- V6 < AUROC 0.65 with no paradigm reaching it (Decision 8 Commitment 3 fail)

**Soft termination — INTERCEPTA must revise architecture if:**
- V2 cannot be evaluated (organoid data access blocks)
- V5 power insufficient (clinical retrospective sample sizes too small for statistical significance)
- Q5 attribution accuracy < 70% on V6 (OOD detection broken)

---

## What This Synthesis Does NOT Resolve

Honest gaps that propagate to Layer 5 implementation:

1. **scRNA-seq IMPROVE-equivalent benchmark.** Bulk IMPROVE is V1 standard; scRNA-seq V1 standard does not yet exist. INTERCEPTA may contribute one.

2. **Organoid V2 benchmark.** No standardized cross-method benchmark; HCMI + Sanger panels exist but methodologies have not been head-to-head evaluated.

3. **V5 clinical data access.** Decision 6 specifies V5 architecture but data access (clinical trial retrospective scRNA-seq with documented drug response) is the practical bottleneck. INTERCEPTA's V5 plan needs explicit data acquisition strategy.

4. **Statistical power calculations per level.** Decision 6 specifies pass criteria but minimum sample sizes for binding GO/NO-GO need formal power analysis (Layer 2 task).

These require Layer 5 implementation or Layer 2 statistical design, not more Layer 1 reading.

---

## Drift Catalog This Phase 4 Cycle

- **New drift instances introduced:** 0
- **Anchor depth audit:** Tang 2022 deepened (317→2163w) bringing the only thin Q6 anchor to standard
- **Methodological discipline:** Every quantitative claim primary-source verified before integration; AUROC 0.77 / RMSE 0.11 / 24.5% concordance / CCEC 0.204-0.464 all attributed to specific source documents
- **Cross-question integration:** Decision 5 + Decision 8 explicit operational dependencies documented

---

— Claude (CSO), 2026-05-10 (Phase 4 synthesis)
