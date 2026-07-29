# INTERCEPTA Workstream B — NSCLC — Specification (LOCKED)

**Subject:** Generalize INTERCEPTA framework to Non-Small Cell Lung Cancer (NSCLC, LUAD + LUSC subtypes).
**Spec status:** LOCKED. All five direction questions resolved 2026-05-07.
**Authors:** Prasad Akula and Claude (CSO), Co-Founders of INTERCEPTA
**Date:** 2026-05-07
**Predecessor specs:**
  - `INTERCEPTA_Round2_2c_Specification.md` — discipline pattern for locked spec
  - `INTERCEPTA_Selectivity_Redesign_Specification.md` — disease-parameterized infrastructure now available
  - `INTERCEPTA_Vision_Module1_Amendment.md` — KAALCURA role correctly framed
**Status:** PRE-IMPLEMENTATION

---

## 1. Why this Workstream

### 1.1 The vision context

INTERCEPTA's mission is "find the drug for any disease." Round 1 mCRPC, Round 2 AML, and Round 3 GBM (live test, not closure-quality) demonstrated the framework on three diseases. Workstream B adds a fourth — Non-Small Cell Lung Cancer — with a higher rigor bar than prior rounds: **multi-cohort cross-validation by design, both LUAD and LUSC subtypes, binding anti-scope-creep, locked spec before code.**

NSCLC is chosen because:
1. Largest cancer mortality globally — 1.8M deaths/year — high public-health impact
2. Multiple high-quality public scRNA-seq cohorts available (Kim 2020, Lambrechts 2018, Laughney 2020, Wu 2021)
3. TCGA-LUAD and TCGA-LUSC provide the largest publicly-available bulk RNA + drug response cohorts (~1,000 patients combined)
4. Distinct biology from prior diseases — solid tumor like mCRPC, kinase-driven like AML era, with active targeted therapy landscape (EGFR, ALK, ROS1, KRAS-G12C inhibitors)
5. Workstream B is the test of "does INTERCEPTA's framework generalize to a clinically diverse, well-studied disease?"

### 1.2 What this Workstream is NOT

- Not a complete NSCLC clinical decision support tool. Closure tier is "Tier A methodology paper guaranteed; Tier B aspired pending external collaboration."
- Not a single-dataset analysis. Locked design is multi-cohort by spec.
- Not a bench validation effort. All findings computational; no wet lab.
- Not a generalization claim across all lung cancer subtypes. LUAD + LUSC only. SCLC is biologically distinct and out of scope.
- Not Tier C ambition (Cell, Nature). Resource constraints make Tier C unachievable in this Workstream.

### 1.3 Publication tier framing (locked CSO call)

| Tier | Guaranteed by spec | Required external | Achievable? |
|---|---|---|---|
| Tier A: methodology paper (Genome Medicine / Briefings in Bioinformatics) | YES | None | YES — directly produced by spec |
| Tier B: high-impact (Nature Communications / Genome Biology) | NO — aspired | Orthogonal validation cohort | YES post-Tier-A, requires partnership outreach |
| Tier C: top-tier (Nature, Cell, Cancer Cell) | NO | Wet lab + clinical trial | NO with current resources |

**Locked closure expectation:** Tier A publication guaranteed. Tier B as documented future track. Tier C explicitly out of scope.

---

## 2. Falsifiable design hypotheses

### H1 — Disease net + KAALCURA framework generalizes to NSCLC
KAALCURA's three axes (R_prolif, R_emt, R_ddr) computed on NSCLC scRNA-seq produce biologically interpretable cell-type ranking with cross-cell-type Jaccard ≤ 0.4 between major NSCLC populations (epithelial-malignant vs immune-myeloid vs stromal-fibroblast).

**Operational definition:**
- Compute per-cell KAALCURA on Kim 2020 (primary cohort, ~208k cells)
- Aggregate to pseudobulk by cell-type cluster
- Rank top-50 GDSC NSCLC drugs by mean KAALCURA-derived sensitivity score per cell-type
- Compute Jaccard overlap of top-50 between cell-type pairs
- PASS: Jaccard ≤ 0.4 for at least 2 of 3 cell-type pairs (epi-vs-immune, epi-vs-stromal, immune-vs-stromal)
- FAIL: any single Jaccard > 0.4 for all pairs (= cell-types are indistinguishable by drug ranking)

### H2 — Multi-cohort cross-dataset transfer
KAALCURA scores derived from TCGA-LUAD bulk transfer to single-cell cohorts (Kim, Lambrechts, Laughney) with cross-dataset Spearman ρ |ρ| ≥ 0.20 at p < 0.01 in at least 2 of 3 scRNA cohorts.

**Operational definition:**
- Compute TCGA-LUAD bulk-derived KAALCURA per-patient
- Aggregate by KRAS/EGFR/ALK mutation status
- For each scRNA cohort: compute per-cell KAALCURA, aggregate by inferred mutation status (matched via gene expression signatures)
- Compute Spearman ρ between bulk-derived KAALCURA-by-mutation and scRNA-derived KAALCURA-by-mutation
- PASS: |ρ| ≥ 0.20 with p < 0.01 in at least 2 of 3 scRNA cohorts (Kim, Lambrechts, Laughney)
- FAIL: PASS in 0 or 1 cohorts

### H3 — Drug response prediction on TCGA-LUAD
Multi-modal predictor (KAALCURA + RNA-1000 + mutation + pathway features) achieves mean test AUROC ≥ 0.65 on a per-drug basis for at least 30 drugs in TCGA + GDSC alignment, with at least one drug class showing AUROC ≥ 0.85 (analog to Venetoclax 0.91 in AML).

**Operational definition:**
- Align TCGA-LUAD patient-level data with GDSC NSCLC cell line drug response
- Subset to drugs with ≥10 sensitive AND ≥10 resistant cell lines (analog of Round 2.2c 10/10 filter)
- Build feature matrix: KAALCURA-3 axes + RNA-1000-no-sex + 15 NSCLC mutation features + 12 KEGG pathway scores + 4 drug-target indicator features
- Train LightGBM 5-fold StratifiedKFold per-drug
- PASS: mean AUROC ≥ 0.65 across ≥30 drugs AND at least one drug class (kinase inhibitors vs chemotherapy vs targeted) ≥ 0.85
- FAIL: either threshold missed

### H4 — Multi-cohort generalization (the high-confidence prediction set)
Drugs passing H3 (per-drug AUROC ≥ 0.75) AND Q_D analog PASS (H2 cross-cohort) form the "high-confidence cross-cohort prediction" set, which becomes the primary publication artifact.

**Operational definition:**
- Identify drugs passing H3 individual threshold (AUROC ≥ 0.75 per drug)
- Of those, identify drugs whose KAALCURA-derived signal cross-validates in ≥2 of 3 scRNA cohorts (per H2)
- This drug set is the "high-confidence" set
- PASS: ≥10 drugs in this set
- FAIL: <10 drugs (insufficient signal for publication-tier claim)

### H5 — Subtype-specific findings (LUAD vs LUSC)
The framework produces distinguishable findings between LUAD and LUSC cohorts (different top-drugs, different KAALCURA distributions, different mutation correlates).

**Operational definition:**
- Run H3 separately on TCGA-LUAD and TCGA-LUSC
- Compare top-20 drugs by AUROC between subtypes
- Compute Jaccard overlap
- PASS: Jaccard ≤ 0.6 (subtypes ARE distinguishable)
- FAIL: Jaccard > 0.6 (subtypes look the same — suggests confound)

### H6 — KAALCURA contribution analog of Round 2.2c Q_E
KAALCURA contributes measurably to multi-modal predictor performance on TCGA-LUAD beyond raw RNA features.

**Operational definition:**
- Train predictor with full feature stack vs feature stack minus KAALCURA
- Compute mean ablation delta across drugs
- PASS: mean delta ≥ 0.005 (analog to Round 2.2c spec threshold) OR KAALCURA in top-20 features for ≥50% of drugs
- FAIL: both thresholds missed (= replicates Round 2.2c's KAALCURA contribution FAIL on AML)

**Note on H6:** Per Round 2.2c lessons, this hypothesis is expected to FAIL (KAALCURA's value is cross-dataset, not within-dataset). Including H6 is not because we expect PASS — it's because the locked spec discipline requires us to test the hypothesis that the vision document originally claimed (KAALCURA as predictor). H6 FAIL would replicate Round 2.2c finding on a fourth disease, which is a publishable result on its own.

---

## 3. Datasets (locked at spec lock)

### 3.1 TCGA-LUAD (bulk RNA + mutations + drug response + clinical)
- **Source:** GDC portal `https://portal.gdc.cancer.gov/` project TCGA-LUAD
- **Size:** 522 patients, ~20,000 genes RNA-seq, ~507 patients with WES, clinical follow-up median 22 months
- **Drug response:** GDSC pan-cancer with NSCLC cell line subset (~80 cell lines × ~250 drugs)
- **License:** TCGA Data Use Certification — controlled access for raw data, open access for processed RNA-seq counts
- **Storage:** `/scratch/akula.pra/INTERCEPTA/data/tcga_luad/` (HPC, ~10GB)
- **Role:** Primary discovery cohort for H3, H4, H6. Source of bulk-derived KAALCURA for H2.

### 3.2 TCGA-LUSC (bulk RNA + mutations + clinical)
- **Source:** Same GDC portal, project TCGA-LUSC
- **Size:** 504 patients
- **Storage:** `/scratch/akula.pra/INTERCEPTA/data/tcga_lusc/` (HPC, ~10GB)
- **Role:** Subtype validation H5. Distinct from LUAD.

### 3.3 Kim 2020 (scRNA, primary discovery for cell-type analysis)
- **Source:** GEO accession `GSE131907`
- **Citation:** Kim N et al. Nat Commun 2020. "Single-cell RNA sequencing demonstrates the molecular and cellular reprogramming of metastatic lung adenocarcinoma."
- **Size:** ~208,000 cells from 44 LUAD patients (primary tumor + LN metastasis + brain metastasis + adjacent normal)
- **Storage:** `/scratch/akula.pra/INTERCEPTA/data/kim2020/` (HPC, ~5GB processed)
- **Role:** Largest scRNA cohort, primary cell-type characterization, H1 evaluation primary, H2 primary scRNA cohort

### 3.4 Lambrechts 2018 (scRNA, technical replication cohort)
- **Source:** ArrayExpress `E-MTAB-6149` and `E-MTAB-6653`
- **Citation:** Lambrechts D et al. Nat Med 2018. "Phenotype molding of stromal cells in the lung tumor microenvironment."
- **Size:** ~52,698 cells from 5 lung cancer patients (LUAD + LUSC mixed)
- **Storage:** `/scratch/akula.pra/INTERCEPTA/data/lambrechts2018/` (HPC, ~2GB)
- **Role:** H2 technical replication. Different platform (10X Chromium), different lab, different bioinformatic pipeline. Tests technical reproducibility. Includes both LUAD and LUSC samples — supports H5.

### 3.5 Laughney 2020 (scRNA, primary + metastatic stage validation)
- **Source:** GEO accession `GSE123904`
- **Citation:** Laughney AM et al. Nat Med 2020. "Regenerative lineages and immune-mediated pruning in lung cancer metastasis."
- **Size:** ~50,283 cells from 17 NSCLC patients across primary + metastatic sites
- **Storage:** `/scratch/akula.pra/INTERCEPTA/data/laughney2020/` (HPC, ~2GB)
- **Role:** Cross-stage validation. Tests biological generalization beyond Kim's diversity. H2 third cohort.

### 3.6 Wu 2021 (scRNA, LUSC subtype coverage)
- **Source:** GEO accession `GSE148071`
- **Citation:** Wu F et al. Cell 2021. "Single-cell profiling of tumor heterogeneity and the microenvironment in advanced non-small cell lung cancer."
- **Size:** ~89,887 cells from 42 NSCLC patients with explicit LUAD vs LUSC labels
- **Storage:** `/scratch/akula.pra/INTERCEPTA/data/wu2021/` (HPC, ~3GB)
- **Role:** Primary LUSC scRNA cohort. Critical for H5 subtype distinguishability. Added to original 3-cohort design after lock #2 (LUAD+LUSC inclusion) — Lambrechts has small LUSC sample but Wu is the dedicated LUSC reference.

### 3.7 External validation (deferred)
- **FPMTB (Faculty of Precision Medicine Tumor Board) cohort** — flagged in Round 2 closure. Workstream B does NOT require FPMTB for closure. Future Tier B unlock work.
- **POPLAR / OAK clinical trial cohorts** — atezolizumab-treated NSCLC. Tier B aspirational.
- **Independent NSCLC researcher cold-outreach** — Tier B unlock track.

---

## 4. Compute environment (locked)

| Task | Environment | Reason |
|---|---|---|
| TCGA-LUAD + LUSC bulk download (~20 GB total) | HPC `/scratch/akula.pra/INTERCEPTA/data/` | Network bandwidth + storage |
| scRNA cohort downloads (Kim ~5GB, Wu ~3GB, others ~2GB each, ~12GB total) | HPC | Same reason |
| KAALCURA scoring on Kim 208k cells | HPC with `--mem=256G --time=4:00:00` | Memory-heavy cell-by-cell ops |
| KAALCURA scoring on Wu 90k cells | HPC with `--mem=128G --time=2:00:00` | Memory-heavy |
| KAALCURA scoring on Lambrechts/Laughney | Mac Air or HPC | <50k cells, fits on Mac with 16-32GB RAM |
| Multi-modal predictor training (TCGA-LUAD per-drug × ~250 drugs) | HPC array job | Parallelism |
| Q_D cross-dataset gates evaluation | Mac Air | Lightweight statistical computation |
| Spec writing, closure documents, paper drafting | Mac Air | Text |

**HPC verified reachable** at login.explorer.northeastern.edu, `/scratch/akula.pra/` has 729TB free, 2026-05-07.

---

## 5. Phase plan (5 phases, ~40-60 hrs total work, ~6-7 sessions)

### Phase 0 — Data acquisition + environment setup (~8-12 hrs, 1-2 sessions)
- HPC environment setup (`intercepta-nsclc` conda env mirroring `intercepta-scrna`)
- Download TCGA-LUAD via gdc-client with manifest
- Download TCGA-LUSC via gdc-client with manifest
- Download GSE131907 (Kim), E-MTAB-6149+E-MTAB-6653 (Lambrechts), GSE123904 (Laughney), GSE148071 (Wu) via SRA-toolkit / wget
- Build NSCLC gene config `configs/genes_nsclc.json` (bridging existing `disease_net_non-small_cell_lung_carcinoma.json` from Open Targets + KEGG NSCLC pathway hsa05223 + EGFR/KRAS/ALK/ROS1/MET key targets + LUSC-specific genes FGFR1, SOX2, NFE2L2)
- Update `configs/disease_tissue_mapping.json` to add NSCLC entry (move from `future_diseases` to `diseases`)
- Run `audit_gtex_columns.py` on updated config to verify NSCLC tissue ("Lung") matches GTEx exactly
- Run `step6_selectivity_v2.py` for NSCLC to produce `step6_selectivity_nsclc.json`
- Run `step6_selectivity_v2_csv_export.py` to produce disease-aware CSV for NSCLC
- **Phase 0 closure:** all 6 datasets visible on HPC, configs in place, NSCLC selectivity JSON+CSV produced
- **Tag:** `workstream-b-phase0-data-acquired`

### Phase 1 — KAALCURA scoring across cohorts (~8-12 hrs, 1-2 sessions)
- Score TCGA-LUAD bulk → KAALCURA-3 axes per patient
- Score TCGA-LUSC bulk → KAALCURA-3 axes per patient
- Score Kim/Lambrechts/Laughney/Wu scRNA → KAALCURA-3 per cell + per cell-type pseudobulk
- Apply KAALCURA residualization against tissue-of-origin (per Module 1 amendment)
- Evaluate H1 (cross-cell-type Jaccard ≤ 0.4) on Kim primary
- **Phase 1 closure:** six KAALCURA-scored datasets, H1 PASS or FAIL documented
- **Tag:** `workstream-b-phase1-kaalcura-scored`

### Phase 2 — Cross-dataset H2 + H5 evaluation (~6-8 hrs, 1 session)
- Compute Spearman ρ between TCGA-LUAD bulk-derived KAALCURA scores → each scRNA cohort's pseudobulk (Kim, Lambrechts, Laughney, Wu)
- Evaluate H2 across 4 cohorts independently (multi-cohort triangulation)
- Compute LUAD vs LUSC top-20-drug Jaccard for H5 (using TCGA-LUAD vs TCGA-LUSC RNA-only LightGBM at this stage; full multi-modal H3 in Phase 3)
- **Phase 2 closure:** Q_D analog measured 4 ways, multi-cohort triangulation result documented, H5 preliminary PASS/FAIL
- **Tag:** `workstream-b-phase2-cross-cohort-validated`

### Phase 3 — Multi-modal predictor (TCGA-LUAD + TCGA-LUSC) (~12-18 hrs, 2 sessions)
- Build feature stack analogous to Round 2.2c (KAALCURA 3 axes + RNA-1000-no-sex + mutation + pathway + drug-target)
- Train per-drug LightGBM 5-fold CV on TCGA-LUAD aligned with GDSC NSCLC subset
- Train per-drug LightGBM 5-fold CV on TCGA-LUSC similarly
- Evaluate H3 (mean AUROC, drug-class breakdown, KAALCURA contribution analog of Q_E = our H6)
- Evaluate H5 final (LUAD vs LUSC subtype distinguishability with full predictor)
- Evaluate H6 (KAALCURA contribution)
- **Phase 3 closure:** per-drug AUROC distribution measured for both subtypes, top performers identified, KAALCURA contribution measured, expected H6 FAIL documented per Round 2.2c precedent
- **Tag:** `workstream-b-phase3-predictor-shipped`

### Phase 4 — H4 multi-cohort high-confidence drug list + closure (~8-12 hrs, 1-2 sessions)
- Identify drugs passing H3 (≥0.75 AUROC) AND H2 (cross-cohort PASS in ≥2 of 4 scRNA cohorts)
- Document those as the "high-confidence cross-cohort prediction" set
- Run sensitivity analyses: how does the set change with different cohort combinations?
- Generate publication-quality figures for top-N predictions
- Write Workstream B closure document analogous to Round 2 closure
- **Tag:** `workstream-b-shipped`

---

## 6. Implementation requirements (binding)

These are not suggestions. They are spec.

1. **Random state locked:** `np.random.seed(42)` at the top of every script. LightGBM `random_state=42`. CV `random_state=42`.

2. **LightGBM hyperparameters locked (NO TUNING):** Same parameters as Round 2.2c spec — `n_estimators=100`, `learning_rate=0.05`, `max_depth=-1`, `num_leaves=31`, `min_data_in_leaf=20`, `objective='binary'`, `metric='auc'`, `verbose=-1`. NO HYPERPARAMETER TUNING regardless of intermediate results.

3. **Fail-closed on missing inputs:** If any dataset is missing, abort with explicit error. If TCGA Data Use Certification has not been obtained, abort. If `configs/genes_nsclc.json` is missing, abort.

4. **No data leakage:** 5-fold CV must use stratified splits with seed=42. No drug appears in both train and test of the same fold. Per-patient (not per-cell) folds for scRNA.

5. **No hardcoded disease names:** `nsclc`, `luad`, `lusc` are config values. Search final code for the string "prostate" or "mcrpc" — should appear only in cross-references to prior rounds, never in NSCLC logic.

6. **Output schemas disease-agnostic:** All outputs use `primary_tissue_tpm` and disease-aware safety classifications (per selectivity redesign closure). NO `prostate_tpm` field anywhere.

7. **All metrics computed deterministically:** Same input always produces same output. No random sampling beyond seed=42.

8. **Backups before destructive operations:** Same discipline as Phase 4-mCRPC. Any disease net regeneration backs up the existing artifact first.

9. **Explicit sample size minimums:**
   - H1: ≥3 cell-type clusters in Kim 2020
   - H2: ≥3 of 4 scRNA cohorts loaded successfully
   - H3: ≥30 drugs passing 10/10 filter on TCGA-LUAD
   - H5: ≥30 drugs passing 10/10 filter on each of TCGA-LUAD and TCGA-LUSC
   - If any minimum fails, that hypothesis is INDETERMINATE (not FAIL — fail requires sample size to exist)

---

## 7. Falsifiable success criteria for closure

Workstream B closes as `workstream-b-shipped` when these specific criteria are met:

1. All 6 datasets downloaded and validated (Phase 0 complete)
2. KAALCURA-3 axes computed for all 6 datasets (Phase 1 complete)
3. H1 evaluated: PASS or FAIL documented with measured Jaccard
4. H2 evaluated: PASS / FAIL / INDETERMINATE documented per cohort, multi-cohort verdict computed
5. H3 evaluated: mean AUROC measured across ≥30 drugs, top performers identified
6. H4 high-confidence set produced (could be empty list — empty list is valid result if H3 produces few high-AUROC drugs)
7. H5 evaluated: LUAD vs LUSC distinguishability measured
8. H6 evaluated: KAALCURA contribution measured (expected FAIL per Round 2.2c precedent)
9. Closure document written with all 8 above measurements explicitly disclosed
10. Tier A publication target identified (specific journal, specific format)

**If 3+ of criteria 1-8 FAIL or are INDETERMINATE,** Workstream B closes with documented partial success (analog to Round 2.2c FAIL closure) rather than tuning around the failures.

---

## 8. What this Workstream will NOT do

To prevent narrative inflation:

- **Will NOT introduce SCLC.** Single tumor type family (LUAD + LUSC) only.
- **Will NOT introduce wet-lab validation.** Computational only.
- **Will NOT introduce single-cell-resolution drug response prediction.** Bulk drug response only (per Round 2.2c finding that single-cell drug response prediction was structurally weak).
- **Will NOT address Layer 15b-e** (full safety constraint). Out of scope per selectivity redesign closure.
- **Will NOT generalize KAALCURA beyond cross-dataset/cross-cell-type framework** (per `vision-module1-amended`).
- **Will NOT download or process FPMTB cohort.** External validation deferred to post-Tier-A unlock track.
- **Will NOT chase Tier B during this Workstream.** Tier B emerges from successful Tier A as next-step work.
- **Will NOT execute clinical trial outreach during Workstream B.** Documented as future track only.
- **Will NOT use raw GDC controlled-access data without DUC.** Open-access processed counts only unless DUC obtained first.

---

## 9. Anti-scope-creep clauses (BINDING)

If during Phase 0-4 implementation we discover any of the following, the locked response is documented here:

- **A new NSCLC scRNA cohort published more recently than spec lock** → log it for future Workstream B-2; do NOT add mid-implementation
- **A novel KAALCURA gene to add (e.g., immune checkpoint genes for NSCLC)** → log for future Module 1 amendment; do NOT modify R_prolif/R_emt/R_ddr definitions mid-implementation
- **A drug class showing surprising signal (e.g., immune checkpoint inhibitors)** → document but do NOT shift predictor design to optimize for it
- **A method that might improve AUROC (e.g., XGBoost, neural net)** → document and defer; locked LightGBM design IS the test, not a starting point for tuning
- **Mean AUROC comes in below H3 threshold of 0.65** → document FAIL honestly; do NOT shift threshold or restrict to high-performing subset
- **H1 Jaccard comes in above 0.4** → document FAIL honestly; do NOT redefine "cell-type" categories
- **H6 KAALCURA contribution PASSES (unexpected)** → document; do NOT use as "look, KAALCURA works as predictor too" narrative
- **One scRNA cohort fails to load or process** → log as INDETERMINATE for that cohort's Q_D evaluation; do NOT silently exclude

This anti-scope-creep section is BINDING per Round 2.2c discipline. Same as the discipline that produced Round 2.2c's honest FAIL.

---

## 10. Process audit

| Principle | Applied as |
|---|---|
| P3 (research before code) | Spec written before any Phase 0 code. Dataset selection grounded in real GEO/ArrayExpress accessions. HPC verified reachable before committing to HPC-required work. |
| P4 (fix structure, don't tune) | LightGBM hyperparameters locked. NO tuning regardless of mean AUROC. H3 threshold pre-specified at 0.65, not adjusted post-hoc. |
| P15 (only correct, honest, real science) | All 6 hypotheses falsifiable. Anti-scope-creep clauses binding. H6 expected to FAIL per prior data — not hidden. Tier A guarantee with Tier B aspiration honestly disclosed. |
| P16 (preserve past work) | Old `step6_gtex_selectivity.py`, mCRPC unified net, Round 2 outputs all preserved. Workstream B does not modify prior round artifacts. |

---

## 11. Entry conditions for Phase 0

Specific checklist that MUST be true before Phase 0 implementation begins:

- [x] This spec committed and tagged `workstream-b-spec-locked`
- [x] HPC accessible (verified 2026-05-07 at login.explorer.northeastern.edu)
- [ ] TCGA Data Use Certification obtained (open-access counts may not require, but full clinical does — check before downloading)
- [ ] HPC `intercepta-nsclc` conda environment created from `intercepta-scrna` mirror
- [ ] `gdc-client` installed on HPC
- [ ] `sra-toolkit` installed on HPC
- [ ] Storage budget verified: `/scratch/akula.pra/INTERCEPTA/` has at least 50GB free for NSCLC data

Phase 0 implementation begins only after all entry conditions met.

---

## 12. Honest disclosure

This spec is the most ambitious INTERCEPTA round to date in scope (4 scRNA cohorts + 2 bulk cohorts vs Round 2's 1+1) and most rigorous in falsifiable design (6 hypotheses with binding anti-scope-creep vs Round 2.2c's 6 hypotheses with anti-scope-creep on a single cohort).

**Estimated calendar time:** 6-7 work sessions over 3-5 weeks including data acquisition delays.

**Estimated active coding time:** 40-60 hours.

**Closure tier expectation:** Tier A guaranteed (Genome Medicine / Briefings in Bioinformatics tier). Tier B (Nature Communications) aspired post-closure pending external collaboration outreach.

**Key risks to closure:**
1. **TCGA-LUAD drug response data alignment with GDSC may produce <30 drugs after 10/10 filter** → H3 INDETERMINATE, would require Round 2.2c-style honest closure with reduced drug set
2. **Wu 2021 dataset processing may fail on HPC due to format issues** → Phase 1 H2 reduces from 4-cohort to 3-cohort triangulation
3. **HPC quota/runtime issues on Kim 208k-cell scoring** → falls back to subsampling approach with documented limitation
4. **TCGA-LUSC sample size too small for H5** → H5 INDETERMINATE
5. **Fundamental issue with multi-modal architecture replicating Round 2.2c FAIL** → expected per H6 framing, would not block closure

**This is a real spec, not a marketing document.** The "no compromise" commitment from spec lock conversations applies to rigor (binding anti-scope-creep, falsifiable hypotheses, locked hyperparameters), not to resource constraints (single founder, MacBook Air + HPC, no wet lab).

---

## 13. What success and failure look like at closure

### Success (workstream-b-shipped Tier A)
- 5-6 of H1/H2/H3/H4/H5/H6 PASS (some FAILs are expected and acceptable)
- High-confidence drug set has ≥10 drugs
- Multi-cohort triangulation demonstrated
- Closure document drafted to Tier A publication standard
- Outline of Tier A paper produced

### Partial success (workstream-b-shipped with caveats)
- 3-4 of 6 hypotheses PASS
- High-confidence drug set has 5-10 drugs
- Multi-cohort partial validation
- Closure document acknowledges limits explicitly
- Tier A still achievable for honest-null-result paper

### Failure (workstream-b-failed-honestly)
- 0-2 of 6 hypotheses PASS
- High-confidence set <5 drugs OR empty
- No multi-cohort signal detected
- Closure document documents structural failure
- Tier A still publishable as "computational drug response prediction in NSCLC: methodology limits and honest negative results"

**All three outcomes are publishable.** The discipline of locking before code means failure is not catastrophic — it's data.

---

## 14. Tier B unlock track (post-closure work)

After `workstream-b-shipped` ships at Tier A, the following work unlocks Tier B publication possibility:

1. **Cold-email outreach to NSCLC clinician-researchers** with the published Tier A methodology paper attached
2. **Identify ≥1 collaborator with unpublished or partially-published NSCLC cohort**
3. **Apply Workstream B methodology to collaborator's cohort as orthogonal validation**
4. **Co-author manuscript at Tier B journal**

Estimated calendar time: 6-12 months post-Tier-A. Estimated active work: ~20-40 hours including outreach.

This is documented future work, NOT in scope of Workstream B implementation.

---

## 15. Tier C unlock requirements (out of scope)

For completeness: Tier C (Nature, Cell) would require:
1. Tier A publication achieved
2. Tier B collaboration achieved
3. Wet lab partnership established
4. Prospective clinical validation cohort accessed
5. Mechanistic experimental work confirming a specific finding

Estimated investment: $5-50M, 5-10 years, ≥10 person team. Out of scope for current INTERCEPTA configuration.

This is honest forward-disclosure, not aspiration claim.

---

*Locked spec. No code yet. Phase 0 implementation begins after this is committed and tagged `workstream-b-spec-locked`.*

— Prasad Akula & Claude (CSO)
2026-05-07
