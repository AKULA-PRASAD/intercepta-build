# INTERCEPTA Workstream B — NSCLC — Specification

**Subject:** Generalize INTERCEPTA framework to fourth disease (Non-Small Cell Lung Cancer / LUAD).
**Spec status:** SCAFFOLDING — sections marked [TO FILL] pending direction confirmation. Full spec lock after confirmation.
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

INTERCEPTA's mission is "find the drug for any disease." Round 1 mCRPC, Round 2 AML, and Round 3 GBM (live test, not closure-quality) demonstrate the framework on three diseases. Workstream B adds a fourth — Non-Small Cell Lung Cancer (NSCLC, specifically the LUAD subtype) — with a higher rigor bar than prior rounds: **multi-cohort cross-validation by design, not as an afterthought.**

NSCLC is chosen because:
1. Largest cancer mortality globally — 1.8M deaths/year — high public-health impact
2. Multiple high-quality public scRNA-seq cohorts available (Kim 2020, Lambrechts 2018, Laughney 2020)
3. TCGA-LUAD provides the largest publicly-available bulk RNA + drug response cohort
4. Distinct biology from prior diseases (NSCLC is solid tumor like mCRPC, but with drugability landscape closer to AML's kinase-targeted therapy era — EGFR, ALK, KRAS-G12C inhibitors)
5. Workstream B is the test of "does INTERCEPTA's framework generalize to a clinically diverse, well-studied disease?"

### 1.2 What this Workstream is NOT

- Not a complete NSCLC clinical decision support tool. Closure tier is "publishable methodology paper + Round-2-equivalent disease pipeline."
- Not a single-dataset analysis. The locked design is multi-cohort by spec.
- Not a bench validation effort. All findings are computational; no wet lab.
- Not a generalization claim across all NSCLC subtypes. LUAD only. LUSC and SCLC are deliberately out of scope.

---

## 2. Falsifiable design hypotheses

### H1 — Disease net + KAALCURA framework generalizes to NSCLC
KAALCURA's three axes (R_prolif, R_emt, R_ddr) computed on NSCLC scRNA-seq produce biologically interpretable cell-type ranking with cross-cell-type Jaccard ≤ 0.4 between major NSCLC populations.

### H2 — Multi-cohort cross-dataset transfer (Q_D analog)
KAALCURA scores derived from TCGA-LUAD bulk transfer to single-cell cohorts (Kim, Lambrechts, Laughney) with cross-dataset Spearman ρ |ρ| ≥ 0.20 at p < 0.01 in at least 2 of 3 scRNA cohorts.

### H3 — Drug response prediction on TCGA-LUAD
Multi-modal predictor (KAALCURA + RNA-1000 + mutation + pathway features) achieves mean test AUROC ≥ 0.65 on a per-drug basis for at least 30 drugs in TCGA + GDSC alignment, with at least one drug class showing AUROC ≥ 0.85 (analog to Venetoclax in AML).

### H4 — Multi-cohort generalization
For drugs where Q_D PASSES on at least 2 of 3 scRNA cohorts AND H3's per-drug AUROC ≥ 0.75 — those drugs are flagged as "high-confidence cross-cohort predictions" and become the primary publication artifact.

**[TO FILL — Section 2 needs concrete operational definitions for each gate's measurement procedure, exactly like Round 2.2c spec Section 3 had]**

---

## 3. Datasets (locked at spec lock)

### 3.1 TCGA-LUAD (bulk RNA + mutations + drug response + clinical)
- **Source:** GDC portal (https://portal.gdc.cancer.gov/) project TCGA-LUAD
- **Size:** 522 patients, ~20,000 genes RNA-seq, ~12,000 patients with WES, clinical follow-up
- **Drug response:** GDSC pan-cancer with NSCLC cell line subset (~80 cell lines × ~250 drugs)
- **Role:** Primary discovery cohort for H3 (drug response) and the source of the KAALCURA bulk axis used in H2

### 3.2 Kim 2020 (scRNA, primary discovery for cell-type analysis)
- **Source:** GEO accession GSE131907
- **Citation:** Kim N et al. Nat Commun 2020. "Single-cell RNA sequencing demonstrates the molecular and cellular reprogramming of metastatic lung adenocarcinoma."
- **Size:** ~208,000 cells from 44 LUAD patients (primary tumor + LN metastasis + brain metastasis + adjacent normal)
- **Role:** Largest scRNA cohort, primary cell-type characterization, H1 evaluation primary, H2 primary scRNA cohort

### 3.3 Lambrechts 2018 (scRNA, technical replication cohort)
- **Source:** ArrayExpress E-MTAB-6149 / E-MTAB-6653
- **Citation:** Lambrechts D et al. Nat Med 2018. "Phenotype molding of stromal cells in the lung tumor microenvironment."
- **Size:** ~52,698 cells from 5 lung cancer patients (mostly LUAD, with smaller LUSC component)
- **Role:** H2 technical replication — independent cohort with different sequencing platform, sample handling, and bioinformatic pipeline. Tests technical reproducibility.

### 3.4 Laughney 2020 (scRNA, primary + metastatic stage validation)
- **Source:** GEO accession GSE123904
- **Citation:** Laughney AM et al. Nat Med 2020. "Regenerative lineages and immune-mediated pruning in lung cancer metastasis."
- **Size:** ~50,283 cells from 17 patients across primary tumor + LN/brain metastases
- **Role:** Cross-stage validation — does KAALCURA differentiate primary from metastatic populations? Tests biological generalization beyond Kim's diversity.

### 3.5 External validation (deferred)
- **FPMTB (Faculty of Precision Medicine Tumor Board) cohort** — TBD external. Round 2 closure flagged this as future external validation. Workstream B does NOT require FPMTB for closure; FPMTB is post-closure work.

**[TO FILL — Section 3 needs file size estimates, download instructions per dataset, license/data-use agreement notes]**

---

## 4. Compute environment (locked)

| Task | Environment | Reason |
|---|---|---|
| TCGA-LUAD bulk download (~10 GB) | Northeastern Explorer HPC `/scratch/akula.pra/INTERCEPTA/data/tcga_luad/` | Network bandwidth + storage |
| scRNA cohort downloads (Kim ~5GB, others ~2GB each) | HPC | Same reason |
| KAALCURA scoring on Kim 208k cells | HPC with `--mem=256G` | Memory-heavy cell-by-cell ops |
| KAALCURA scoring on Lambrechts/Laughney | Either Mac Air or HPC | <50k cells, fits on Mac with 16-32GB RAM |
| Multi-modal predictor training (TCGA-LUAD per-drug) | HPC for parallelism | LightGBM per-drug × ~250 drugs |
| Q_D cross-dataset gates evaluation | Mac Air | Lightweight statistical computation |
| Spec writing, closure documents, paper drafting | Mac Air | Text |

**HPC verified reachable** (login.explorer.northeastern.edu, `/scratch/akula.pra/`, 729TB free).

---

## 5. Phase plan (5 phases, ~35-55 hrs total work, ~6 sessions)

### Phase 0 — Data acquisition + environment setup (~6-10 hrs, 1-2 sessions)
- HPC environment setup (`intercepta-nsclc` conda env mirroring `intercepta-scrna`)
- Download TCGA-LUAD via gdc-client
- Download GSE131907 (Kim), E-MTAB-6149 (Lambrechts), GSE123904 (Laughney) via SRA-toolkit / wget
- Build NSCLC gene config `configs/genes_nsclc.json` (bridging existing `disease_net_non-small_cell_lung_carcinoma.json` from Open Targets + KEGG NSCLC pathway hsa05223 + EGFR/KRAS/ALK key targets)
- Update `configs/disease_tissue_mapping.json` to add NSCLC entry (currently in `future_diseases` section)
- **Phase 0 closure:** all 4 datasets visible on HPC, configs in place
- **Tag:** `workstream-b-phase0-data-acquired`

### Phase 1 — KAALCURA scoring across cohorts (~6-8 hrs, 1 session)
- Score TCGA-LUAD bulk → KAALCURA-3 axes per patient
- Score Kim/Lambrechts/Laughney scRNA → KAALCURA-3 per cell + per cell-type pseudobulk
- Evaluate H1 (cross-cell-type Jaccard ≤ 0.4) on Kim primary
- **Phase 1 closure:** four KAALCURA-scored datasets, H1 PASS or FAIL documented
- **Tag:** `workstream-b-phase1-kaalcura-scored`

### Phase 2 — Cross-dataset H2 evaluation (~4-6 hrs, 1 session)
- Compute Spearman ρ between TCGA-LUAD bulk-derived KAALCURA scores → each scRNA cohort's pseudobulk
- Evaluate H2 across 3 cohorts independently
- **Phase 2 closure:** Q_D analog measured 3 ways, multi-cohort triangulation result documented
- **Tag:** `workstream-b-phase2-cross-cohort-validated`

### Phase 3 — Multi-modal predictor (TCGA-LUAD) (~10-15 hrs, 2 sessions)
- Build feature stack analogous to Round 2.2c (KAALCURA 3 axes + RNA-1000-no-sex + mutation + pathway + drug-target)
- Train per-drug LightGBM 5-fold CV on TCGA-LUAD aligned with GDSC NSCLC subset
- Evaluate H3 (mean AUROC, drug-class breakdown, KAALCURA contribution analog of Q_E)
- **Phase 3 closure:** per-drug AUROC distribution measured, top performers identified, KAALCURA contribution measured
- **Tag:** `workstream-b-phase3-predictor-shipped`

### Phase 4 — H4 multi-cohort high-confidence drug list + closure (~6-10 hrs, 1 session)
- Identify drugs passing H3 (≥0.75 AUROC) AND Q_D PASS in ≥2 scRNA cohorts
- Document those as the "high-confidence cross-cohort prediction" set
- Write Workstream B closure document analogous to Round 2 closure
- **Tag:** `workstream-b-shipped`

**[TO FILL — each phase needs detailed step-by-step procedures, falsifiable success criteria, fail-closed conditions, data shape contracts. Round 2.2c spec Section 4 had the level of detail required.]**

---

## 6. Implementation requirements (binding) — [TO FILL]

Same structure as Round 2.2c Section 6 + selectivity redesign Section 6:
- Random state locked
- LightGBM hyperparameters locked (no tuning)
- Fail-closed on missing inputs
- No hardcoded disease names
- Fail-closed on missing data_use_agreements (TCGA has DUA requirement)
- ...

---

## 7. Falsifiable success criteria for closure — [TO FILL]

Section will list ~7-10 specific measurable criteria, each must PASS for `workstream-b-shipped` to be appropriate. If 3+ FAIL, Workstream B closes with documented partial success (analog to Round 2.2c FAIL closure).

---

## 8. What this Workstream will NOT do

- Not introduce LUSC or SCLC. Single subtype (LUAD) only.
- Not introduce wet-lab validation. Computational only.
- Not introduce single-cell-resolution drug response prediction. Bulk drug response only (per Round 2.2c finding that single-cell drug response prediction was structurally weak).
- Not address Layer 15b-e (full safety constraint). Out of scope per selectivity redesign closure.
- Not generalize KAALCURA beyond cross-dataset/cross-cell-type framework (per `vision-module1-amended`).
- Not download or process FPMTB cohort. External validation deferred.

---

## 9. Process audit — [TO FILL after spec is locked]

Mirror structure of Round 2.2c and selectivity redesign Process Audit sections.

---

## 10. Entry conditions for Phase 0 — [TO FILL]

Specific checklist that must be true before Phase 0 implementation begins:
- [ ] This spec committed and tagged `workstream-b-spec-locked`
- [ ] HPC accessible (verified 2026-05-07)
- [ ] TCGA Data Use Agreement reviewed
- [ ] ...

---

## 11. Anti-scope-creep (locked)

If during Phase 0-4 implementation we discover:

- **A new NSCLC scRNA cohort published more recently** — log it for future Workstream B-2, do NOT add mid-implementation
- **A novel KAALCURA gene to add** — log for future Module 1 amendment, do NOT modify R_prolif/R_emt/R_ddr definitions mid-implementation
- **A drug class showing surprising signal** — document it but do NOT shift the predictor design to optimize for it (this is the goalpost-moving discipline from Round 2.2c)
- **A method that might improve AUROC** — document and defer; the locked LightGBM design is the test, not a starting point for tuning

This anti-scope-creep section is binding. Same as Round 2.2c.

---

## 12. Honest disclosure

This spec is more ambitious than the original 24-week plan suggested. Round 1 took 5 weeks, Round 2 took 3 weeks; Workstream B is estimated 35-55 hrs spread across 6 sessions, possibly 3-4 weeks of calendar time including data acquisition delays.

**This is the right scope for Workstream B given the resource budget** (one founder, one MacBook Air, HPC access for heavy compute, no wet lab). It is significantly more rigorous than a single-dataset analysis would be. It is significantly less than a "publishable to Cell with prospective validation" claim would require.

**Closure tier expectation:** publishable to Genome Medicine or Briefings in Bioinformatics (not Cell or Nature without external validation). Acceptable for a graduate-student-led methodology paper.

If during implementation we discover a fundamental issue (e.g., TCGA-LUAD drug response data is too sparse for H3 evaluation), Workstream B closes with documented null result rather than tuning around the issue. **Same discipline as Round 2.2c.**

---

## OUTLINE COMPLETE — DIRECTION CONFIRMATION REQUEST

**Before I fill in [TO FILL] sections, please confirm or push back on:**

1. **Multi-cohort design with 4 datasets** (TCGA-LUAD + Kim + Lambrechts + Laughney) — confirm or reduce
2. **LUAD subtype only** (not LUSC, not SCLC) — confirm or expand
3. **Closure tier: methodology paper, no external prospective validation** — confirm or set higher
4. **Phase plan and ~6-session estimate** — confirm or rescope
5. **Anti-scope-creep section** binding — confirm

If you confirm: I write the full ~600-line spec. ~45-60 min more work. Tag `workstream-b-spec-locked`.

If you push back on anything: tell me which item, I revise.

If you want different scope entirely: tell me what.
