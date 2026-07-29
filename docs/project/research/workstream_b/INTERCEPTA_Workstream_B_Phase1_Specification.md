# INTERCEPTA Workstream B — Phase 1 Specification (LOCKED)

**Subject:** KAALCURA scoring across 4 NSCLC cohorts (LuCA + Wu + TCGA-LUAD + TCGA-LUSC) for Workstream B hypothesis testing.
**Spec status:** LOCKED before code, per Round 2.2c discipline (P3 — research before code).
**Authors:** Prasad Akula (CEO) and Claude (CSO), Co-Founders of INTERCEPTA
**Date:** 2026-05-10
**Predecessor specs:**
  - `INTERCEPTA_Workstream_B_NSCLC_Specification.md` (parent spec, May 7, tag `workstream-b-spec-locked`)
  - `INTERCEPTA_Workstream_B_Spec_Erratum_LuCA.md` (cohort design amendment, May 8, tag `workstream-b-spec-erratum-luca`)
  - `INTERCEPTA_Workstream_B_Phase0_Prep_Log.md` (HPC environment setup, May 8)
  - `WORKSTREAM_B_PHASE0_LAUNCH.md` (data acquisition, May 10)
- **Phase 0 closure:** tag `workstream-b-phase0-prior-work-preserved-2026-05-10` (May 10)
- **Verified data on HPC:** 76 GB LuCA + 5.3 GB TCGA + 344 MB Wu + Travaglini-Krasnow already at LuCA `data/12_input_adatas/`
**Status:** PRE-IMPLEMENTATION
**Tag (when committed):** `workstream-b-phase1-spec-locked`

---

## 0. Why this Phase

Workstream B parent spec defines 6 hypotheses (H1-H6) for NSCLC. Phase 1 produces the foundational artifact those hypotheses test against: **KAALCURA scores per cell or per sample across all 4 cohorts**. Every downstream phase (Phase 2 H2 cross-cohort, Phase 3 H3/H5/H6 multi-modal predictor, Phase 4 H4 high-confidence drug list) consumes Phase 1 outputs.

**No Phase 1 outputs → no Workstream B closure.**

This spec is bounded: take the 4 verified datasets and produce one clean KAALCURA scoring per dataset, in a format the downstream phases can directly consume. **Not** building the predictor. **Not** doing cross-cohort transfer. **Not** doing pseudobulk aggregation for cell-type analysis. Those are Phase 2-4.

---

## 1. Phase 1 deliverables (locked)

### 1.1 Per-dataset KAALCURA score files

| Cohort | Cell-/Sample-level | Output file | Rows | Columns |
|---|---|---|---|---|
| **LuCA Salcher 2022** | Per-cell | `data/nsclc/luca_salcher2022/derived/kaalcura_per_cell.parquet` | ~1.28M cells | cell_id, sample_id, study, cell_type (LuCA author label), R_prolif, R_emt, R_ddr, R_prolif_residual, R_emt_residual, R_ddr_residual |
| **Wu 2021** | Per-cell | `data/nsclc/wu2021/derived/kaalcura_per_cell.parquet` | ~89,887 cells (target) | cell_id, sample_id (P1-P42), patient_subtype (LUAD/LUSC), R_prolif, R_emt, R_ddr, R_prolif_residual, R_emt_residual, R_ddr_residual |
| **TCGA-LUAD** | Per-sample (bulk) | `data/nsclc/tcga_luad/derived/kaalcura_per_sample.parquet` | ~601 samples | sample_id, mutations_summary (KRAS, EGFR, TP53, etc), R_prolif, R_emt, R_ddr |
| **TCGA-LUSC** | Per-sample (bulk) | `data/nsclc/tcga_lusc/derived/kaalcura_per_sample.parquet` | ~562 samples | sample_id, mutations_summary, R_prolif, R_emt, R_ddr |

### 1.2 Per-dataset reports (JSON)

| File | Purpose |
|---|---|
| `data/nsclc/luca_salcher2022/derived/luca_kaalcura_report.json` | n_cells_scored, n_studies, gene_coverage % vs KAALCURA-3 axes, score distribution stats per cell type |
| `data/nsclc/wu2021/derived/wu_kaalcura_report.json` | Same; per patient |
| `data/nsclc/tcga_luad/derived/tcga_luad_kaalcura_report.json` | n_samples, gene_coverage, score distribution stats by mutation status |
| `data/nsclc/tcga_lusc/derived/tcga_lusc_kaalcura_report.json` | Same |
| `data/nsclc/derived/phase1_summary.json` | Cross-cohort summary: gene coverage comparisons, sample size accounting, any cohort-specific caveats |

### 1.3 Per-dataset code

| File | Purpose |
|---|---|
| `code/workstream_b/score_kaalcura_luca.py` | Loads LuCA full-atlas h5ad, computes KAALCURA per cell, writes parquet |
| `code/workstream_b/score_kaalcura_wu.py` | Loads Wu per-sample `.txt.gz` matrices, computes KAALCURA per cell (note format constraint per Phase 0 verification) |
| `code/workstream_b/score_kaalcura_tcga.py` | Loads TCGA bulk RNA-seq (601+562 STAR counts), computes KAALCURA per sample |
| `code/workstream_b/aggregate_phase1.py` | Combines per-dataset reports into `phase1_summary.json` |

### 1.4 Slurm scripts

| File | Compute estimate |
|---|---|
| `code/slurm/score_kaalcura_luca.slurm` | GPU node, ~3-6 hrs (1.28M cells) |
| `code/slurm/score_kaalcura_wu.slurm` | CPU node, ~30-60 min (89,887 cells) |
| `code/slurm/score_kaalcura_tcga.slurm` | CPU node, ~10-20 min (1,163 bulk samples combined) |

### 1.5 Closure document

`docs/INTERCEPTA_Workstream_B_Phase1_Closure.md` — closure-format document with:
- Per-cohort outputs verified
- Gene coverage numbers per cohort (KAALCURA-3 gene set vs cohort HVGs)
- Honest documentation of any cohort-specific caveats
- Tag commit: `workstream-b-phase1-shipped` (or `-shipped-with-caveats` per parent spec §13)

---

## 2. Falsifiable design hypotheses (Phase-1-specific)

These are **not** the Workstream B headline hypotheses (those are H1-H6 in parent spec). These are **Phase 1 internal gates** that must pass before Phase 2 consumes Phase 1 outputs.

### Phase 1 Gate G1.1 — Gene coverage minimum
**Question:** Does each cohort's expression data contain enough KAALCURA-3 genes (R_prolif, R_emt, R_ddr signature genes) to compute meaningful axis scores?

**Operational definition:**
- KAALCURA-3 canonical gene set: per `code/intercepta_kaalcura_v1.py` — R_prolif (50 genes), R_emt (200 genes), R_ddr (100 genes) per Hallmark MSigDB signatures
- Per-cohort: count how many of each axis's genes are present in the cohort's expression matrix
- Coverage = % of canonical genes present per axis

**PASS criteria:**
- LuCA: ≥60% coverage on each of R_prolif, R_emt, R_ddr (LuCA HVGs may be limited per Architectural Debt Erratum §)
- Wu: ≥70% coverage on each axis (full-transcriptome per-sample matrices, expected high)
- TCGA-LUAD: ≥85% coverage on each axis (bulk RNA-seq, full transcriptome)
- TCGA-LUSC: ≥85% coverage on each axis

**FAIL criteria:** Any cohort below threshold on any axis. **Failure mode:** investigate, document gene-coverage limitation in Phase 1 closure, optionally augment KAALCURA-3 with proxy genes from the same Hallmark pathway.

**Why this gate:** Per Architectural Debt Erratum, LuCA HVGs cover only ~36% of canonical KAALCURA gene set. We must measure coverage explicitly per cohort. If coverage is too low, KAALCURA scores are unreliable and Phase 2 conclusions would be biased.

### Phase 1 Gate G1.2 — Score distribution sanity
**Question:** Do KAALCURA scores produce reasonable distributions (not all zeros, not pathological NaN cascades, not single-mode collapse)?

**Operational definition:**
- For each cohort, for each axis (R_prolif, R_emt, R_ddr), report:
  - n_NaN, n_zero, n_finite
  - mean, median, std
  - 5th, 25th, 50th, 75th, 95th percentiles

**PASS criteria:**
- n_NaN < 1% of cells/samples per axis
- n_zero (exact zero) < 5% per axis (some legitimate zeros expected; mass-zero indicates pipeline failure)
- std ≥ 0.1 per axis (some variance must exist)
- 95th percentile > 0 AND 5th percentile < 0 (residualized scores should span both signs)

**FAIL criteria:** Any cohort × axis combination violates above.

### Phase 1 Gate G1.3 — Cell-type face validity (LuCA + Wu only)
**Question:** Do KAALCURA scores produce biologically plausible patterns by cell type?

**Operational definition:**
- For LuCA: aggregate per-cell KAALCURA by `cell_type` author label; verify malignant epithelial cells show higher R_prolif than fibroblasts and immune cells (basic sanity)
- For Wu: same, using inferred cell-type labels from canonical NSCLC marker genes (Wu didn't provide cell type labels in the per-sample matrices — see Phase 1 caveat §5.2)

**PASS criteria:**
- LuCA: malignant epithelial cells have median R_prolif > median R_prolif of fibroblasts (positive direction)
- LuCA: malignant epithelial cells have median R_prolif > median R_prolif of T cells (positive direction)
- Wu: same, using marker-based cell typing

**FAIL criteria:** Both checks fail OR any direction inverted.

**Why this gate:** Round 2.2a Q_A discipline lesson — comparator biology must verify. If R_prolif doesn't separate proliferating cancer from quiescent stroma, the axis is computed wrong somehow.

### Phase 1 Gate G1.4 — Cross-cohort sample-size accounting
**Question:** Do final cell/sample counts match cohort expectations?

**PASS criteria:**
- LuCA: ≥1,000,000 cells scored (atlas total ~1.28M; allow some QC dropouts)
- Wu: ≥80,000 cells scored (atlas total ~89,887)
- TCGA-LUAD: ≥550 samples scored (cohort total ~601)
- TCGA-LUSC: ≥510 samples scored (cohort total ~562)

**FAIL criteria:** Any cohort >10% below expected count.

---

## 3. KAALCURA implementation specification (locked from canonical)

### 3.1 Use canonical KAALCURA module

`code/intercepta_kaalcura_v1.py` is the canonical implementation (1,046 lines, validated on GDSC at AUROC=0.6715 across 286 drugs per `kaalcura_real_validation_RERUN.csv`). **Phase 1 uses this module verbatim — does not re-implement.**

### 3.2 Three axes, residualization, tissue PCA

Per canonical module:
- R_prolif from MSigDB Hallmark `MITOTIC_SPINDLE` ∪ `G2M_CHECKPOINT` ∪ `E2F_TARGETS` gene set intersection
- R_emt from `EPITHELIAL_MESENCHYMAL_TRANSITION` Hallmark
- R_ddr from `DNA_REPAIR` Hallmark + ATM/ATR/CHK pathway extensions

**Residualization:** R_prolif_residual = R_prolif − coef_emt × R_emt − coef_ddr × R_ddr (regression-based decoupling). Same for R_emt_residual and R_ddr_residual. This is per Round 2.2b methodology.

**Tissue PCA:** TCGA cohorts get tissue-level PCA decomposition added per canonical pipeline. scRNA cohorts (LuCA, Wu) use per-cell scoring without tissue PCA (cell is the unit, tissue PCA doesn't apply at single-cell level).

### 3.3 Score normalization

Per cohort: z-score each axis within the cohort BEFORE residualization. This matches Round 2.2b protocol and ensures cross-cohort comparison in Phase 2 is well-defined.

### 3.4 Wu 2021 format handling (LOCKED per Phase 0 verification)

Wu 2021 cohort uses per-sample `.txt.gz` expression matrices (NOT 10X mtx triplets). Phase 1 code must:
- Use `scanpy.read_csv()` per sample
- Concatenate into single AnnData object (~89,887 cells, 42 patients labeled P1-P42)
- Annotate `obs['patient']` from the GSM filename
- Annotate `obs['subtype']` (LUAD vs LUSC) from Wu 2021 Supplementary Table 1 (TBD: locate during implementation; if not findable, derive from EGFR/KRAS/TP53 mutation signatures)

---

## 4. Implementation requirements (binding)

These are not suggestions. They are spec.

1. **Random state = 42 throughout.** Matches all prior INTERCEPTA work.

2. **Use canonical `intercepta_kaalcura_v1.py` — do not re-implement.** If the canonical module needs an extension (e.g., new gene-list config for NSCLC), the extension is added as a config file, not by modifying the canonical module.

3. **Output format = parquet.** parquet is fast, compressed, columnar; faster than CSV for ~1.28M cell tables. Use `pyarrow` (already in HPC env per Phase 0 Prep Log).

4. **Disk paths = HPC scratch.** All Phase 1 code reads from and writes to `/scratch/akula.pra/INTERCEPTA/` paths. No `~` paths. No `/home/akula.pra/` paths.

5. **Per-cohort independent execution.** Each `score_kaalcura_*.py` runs as its own slurm job. No cross-job dependencies. (Phase 1 itself is "score 4 cohorts independently.")

6. **Memory limits.** LuCA full atlas at 16 GB h5ad needs ≥32 GB RAM compute node; spec requires `#SBATCH --mem=64G` for safety margin.

7. **Fail closed.** If any axis gene set has <50% coverage in a cohort, the run aborts with explicit error message. No silent imputation. No silent zeros for missing genes.

8. **All metrics reported, not selectively.** Per-cohort report JSON has full distributional stats (n_NaN, n_zero, percentiles, std), not just mean.

9. **Output schema committed alongside results:**
   - parquet schemas locked in spec §1.1
   - JSON schemas locked in spec §1.2

10. **Logging.** Each slurm job writes to `/scratch/akula.pra/INTERCEPTA/logs/phase1_<cohort>_<jobid>.{out,err}`. No quiet failures.

---

## 5. Anti-scope-creep clauses (BINDING)

To prevent scope creep:

- **Will NOT do cross-cohort transfer in Phase 1.** That is Phase 2 (H2 evaluation).
- **Will NOT do drug response prediction in Phase 1.** That is Phase 3 (H3 multi-modal predictor).
- **Will NOT do cell-type pseudobulk aggregation in Phase 1.** That is Phase 2 (H1 cell-type ranking).
- **Will NOT touch Lambrechts cohort.** Spec Erratum dropped it (R-only data not Python-readable). Out of scope.
- **Will NOT add new disease parameterizations.** Selectivity Redesign already shipped NSCLC config (per `INTERCEPTA_Selectivity_Redesign_Closure.md`).
- **Will NOT introduce new KAALCURA axis definitions.** R_prolif, R_emt, R_ddr are locked per canonical module.
- **Will NOT modify canonical KAALCURA module.** Per P16, canonical at tag `architectural-debt-erratum-2026-05-09` is preserved.
- **Will NOT skip gene-coverage check.** G1.1 is binding — if coverage is below threshold, we document it, not work around it.
- **Will NOT generate the closure document until G1.1-G1.4 PASS or are explicitly noted as caveats.**

These clauses are binding. Same discipline as Round 2.2c spec §7 and Workstream B parent spec §9.

---

## 6. Comparator biology verification (per Round 2.2a Q_A lesson)

For each Phase 1 gate involving biological comparison:

**G1.3 LuCA cell-type face validity:**
- Malignant epithelial cells = LuCA cell_type label "Tumor cells" or equivalent (verify in atlas before code; don't assume)
- Fibroblasts = "Fibroblasts" label per Salcher 2022
- T cells = "T cells" or "T cells CD4" + "T cells CD8" labels per Salcher 2022
- **Direction:** R_prolif (cancer) > R_prolif (stroma) is biologically expected per Hallmark gene set definition (proliferation markers high in dividing cancer cells).

**G1.3 Wu cell-type face validity:**
- Wu doesn't provide cell type labels in per-sample matrices (per Phase 0 log)
- Implementation must use marker-based cell typing: EPCAM+/KRT19+ = epithelial, COL1A1+/COL3A1+ = fibroblast, CD3D+/CD3E+ = T cells
- **Direction:** same as LuCA — epithelial R_prolif > stromal R_prolif

No biology verification required for G1.1, G1.2, G1.4 (these are computational sanity gates, not biological comparator gates).

---

## 7. Process audit (in advance)

| Principle | Applied as |
|---|---|
| **P3 (research before code)** | This spec written and committed before code. Hypotheses + thresholds locked. |
| **P4 (fix structure, don't tune)** | Gate thresholds set against measured baselines (LuCA 36% coverage per Architectural Debt Erratum motivates 60% threshold for LuCA, not chosen to make LuCA pass) |
| **P15 (only correct, honest, real science)** | G1.1 explicitly tests gene coverage and accepts FAIL. G1.3 has direction-of-correlation pre-specified. Wu cell-typing limitation honestly disclosed. |
| **P16 (preserve past work)** | Canonical KAALCURA module unchanged. Round 2.2b residualization protocol reused unchanged. Phase 0 outputs preserved. |
| **P-FV-1 (no jumping rounds)** | Phase 1 stays in Phase 1. Phase 2 questions deferred. Phase 3 modeling deferred. |
| **P-FV-2 (architectural commitments require trade-off documentation)** | If G1.1 fails for LuCA, the trade-off (use limited gene set vs augment vs drop axis) is documented before resolution |
| **P-FV-3 (verification before declaration)** | Phase 1 closure requires G1.1-G1.4 PASS evidence; not "Phase 1 done, trust me" |
| **P-FV-Discipline** | Anti-scope-creep clauses binding |

---

## 8. Effort estimate

- Spec (this document): ~1 session — DONE on commit
- Implementation:
  - score_kaalcura_luca.py: ~1 session of CSO work + 1 LuCA test run
  - score_kaalcura_wu.py: ~0.5 session (Wu format already understood from Phase 0)
  - score_kaalcura_tcga.py: ~0.5 session (bulk RNA-seq is straightforward)
  - aggregate_phase1.py: ~0.25 session
- Slurm execution + verification: ~1 session of monitoring + result reads
- Phase 1 closure document: ~0.5 session

**Total: ~4-5 sessions of focused CSO work + ~6-12 hours of HPC compute time. Approximately 1-2 weeks elapsed at moderate pace.**

GPU only required for LuCA (1.28M cells). Other cohorts CPU.

---

## 9. Entry conditions for implementation

Before any Phase 1 implementation code is written:

- [x] This spec committed and tagged `workstream-b-phase1-spec-locked`
- [x] Phase 0 closure verified (tag `workstream-b-phase0-prior-work-preserved-2026-05-10` exists)
- [x] All 4 datasets verified on HPC scratch (76 GB LuCA + 5.3 GB TCGA + 344 MB Wu)
- [x] Canonical KAALCURA module verified on HPC (`code/intercepta_kaalcura_v1.py`, 46,605 bytes)
- [x] T1 Full-Lite verification passed (5/5 sub-tests, May 10) — confirms canonical KAALCURA is producing correct results
- [ ] CEO sign-off on Phase 1 spec (this document)

---

## 10. Phase 1 exit conditions

Phase 1 closes when ALL of:

1. All 4 cohort outputs (parquet + JSON) generated and verified per §1.1-1.2
2. Phase 1 gates G1.1-G1.4 evaluated; PASS or explicit caveats documented
3. Phase 1 closure document (`INTERCEPTA_Workstream_B_Phase1_Closure.md`) drafted
4. If all PASS: tag `workstream-b-phase1-shipped`. Phase 2 begins.
5. If partial PASS with caveats: tag `workstream-b-phase1-shipped-with-caveats`. Phase 2 begins with documented caveats threading downstream.
6. If structural failure (e.g., G1.1 fails on multiple cohorts beyond rescue): tag `workstream-b-phase1-failed-honestly`; trigger Phase 1 spec re-write before retry.

---

## 11. Risk register (per Workstream B parent §12)

Known risks for Phase 1 specifically:

| Risk | Likelihood | Mitigation |
|---|---|---|
| LuCA gene coverage <60% | MEDIUM (current LuCA HVG analysis showed 36% coverage; full atlas may be better) | If <60%, document and use proxy-gene augmentation |
| Wu cell-type labels not findable | MEDIUM (per-sample matrices lack cell type) | Marker-based cell typing pre-specified |
| LuCA full-atlas h5ad I/O slow on HPC | LOW (16 GB h5ad on scratch should be fast) | Use 64 GB RAM node; chunked reads if needed |
| TCGA RNA-seq mismatch with KAALCURA gene IDs | LOW (TCGA STAR counts use Ensembl IDs; canonical KAALCURA uses HGNC symbols) | Mapping done via existing `~/INTERCEPTA/data/manifests/gene_id_map.csv` per Phase 0 prep |
| OOM on LuCA (1.28M cells × ~30K genes = ~38B floats) | MEDIUM | Chunked scoring per study (29 source studies in atlas) |
| Wu format edge cases (sample-level QC failures) | LOW-MEDIUM | Per-sample try/except; report failures don't crash batch |

Known risks for Workstream B overall (per parent §12) carry into Phase 1 contextually but their mitigations are at parent-spec level.

---

## 12. Honest disclosure

Phase 1 is mechanical execution. The science questions (does cross-cohort transfer work? does multi-modal predictor work? what are the high-confidence drugs?) are Phases 2-4. Phase 1 produces clean inputs.

**This is the foundation. If we don't get Phase 1 right, Phases 2-4 conclusions are unreliable.** Hence the 4 explicit gates, the binding gene coverage threshold, the honest cell-typing limitations.

The discipline that produced Round 2.2b's residualized axes (n=520 BeatAML samples, 6 weeks of careful work) produces this Phase 1 spec. Different scale (4 cohorts, ~1.4M total cells) but same discipline.

---

## 13. What success looks like at Phase 1 closure

### Best case
- All 4 cohorts scored
- All 4 gates PASS
- Closure document publishable as Phase 1 methods section of Workstream B paper
- Phase 2 (H2 cross-cohort transfer) begins with verified inputs

### Acceptable case
- All 4 cohorts scored
- 3 of 4 gates PASS; one cohort has coverage caveat documented
- Closure document publishable with caveat noted
- Phase 2 begins with caveat threading downstream

### Failure case
- Cannot score one or more cohorts (e.g., LuCA OOM unsolvable, Wu format unparseable)
- G1.1 or G1.3 fails systemically across cohorts
- Tag `workstream-b-phase1-failed-honestly`
- Investigate root cause; spec amendment; retry from clean state
- Workstream B timeline shifts; Tier A publication still achievable per parent §13 honest-failure-publication path

---

## 14. Closure honesty statement

Phase 1 spec is the same discipline as Round 2.2c spec applied to a different scope. Locked thresholds, falsifiable gates, anti-scope-creep clauses, honest disclosure of cohort-specific limitations.

If the spec is wrong about something (e.g., gene coverage threshold was set too lenient, or LuCA atlas has a structure we didn't anticipate), the spec is amended (not silently violated) and the amendment tagged.

Phase 1 produces 4 parquet files + 5 JSON reports + 1 closure document. That's it. **Bounded. Verifiable. Auditable.**

---

*Locked spec. No code yet. Implementation begins after this is committed and tagged.*

— Prasad Akula (CEO) & Claude (CSO)
2026-05-10
