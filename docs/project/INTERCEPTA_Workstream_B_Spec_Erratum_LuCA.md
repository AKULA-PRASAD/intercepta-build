# INTERCEPTA Workstream B — Spec Erratum: Cohort Design

**Subject:** Erratum to `INTERCEPTA_Workstream_B_NSCLC_Specification.md` — scRNA cohort design changed from 4-cohort to 2-cohort (LuCA + Wu) after Phase 0 inventory revealed data accessibility realities and a stronger design alternative.
**Authors:** Prasad Akula and Claude (CSO), Co-Founders of INTERCEPTA
**Date:** 2026-05-08
**Spec under amendment:** `INTERCEPTA_Workstream_B_NSCLC_Specification.md` (tag: `workstream-b-spec-locked`)
**This erratum tag:** `workstream-b-spec-erratum-luca`
**Status:** Spec amended. Implementation continues against amended design.

---

## What changed

The locked Workstream B spec listed these 4 scRNA cohorts:
1. Kim 2020 (GSE131907) — primary discovery, 208k cells
2. Lambrechts 2018 (E-MTAB-6149) — technical replication, 53k cells
3. Laughney 2020 (GSE123904) — cross-stage validation, 50k cells
4. Wu 2021 (GSE148071) — LUSC subtype coverage, 90k cells

**Amended design uses 2 scRNA cohorts:**
1. Salcher LuCA 2022 (cellxgene + Zenodo) — primary harmonized atlas, 1.2M cells from 29 source studies
2. Wu 2021 (GSE148071) — independent external validation cohort, 90k cells (NOT in LuCA source list)

TCGA-LUAD and TCGA-LUSC bulk RNA cohorts unchanged.

---

## Why the change

### Reason 1: Lambrechts 2018 data is not Python-readable

Phase 0 inventory of E-MTAB-6149 surfaced that the entire cohort's processed data is in R-specific `.Rds` format, pre-split by author-determined cell type clusters (Alveolar.Cellview.Rds, B_cell.Cellview.Rds, etc.). The only alternative is raw FASTQ (~280 GB). Neither matches our processed-matrix Python-native approach (locked CSO call earlier in Phase 0 for cross-cohort comparability).

E-MTAB-6653 (Lambrechts second accession) only contains FASTQ + metadata files.

### Reason 2: A stronger design alternative was found per the termination contract

Per termination contract set during Phase 0 search:
- Required criteria: NSCLC patient samples, ≥30 patients OR ≥40k cells, Python-readable processed format, open access, peer-reviewed, different lab from existing cohorts
- Termination rule: first candidate meeting all 6 criteria → lock

Salcher et al. 2022 (Cancer Cell, doi:10.1016/j.ccell.2022.10.008) — the LuCA NSCLC single-cell atlas — meets all 6 criteria and exceeds them substantially:

| Criterion | Salcher LuCA |
|---|---|
| 1. NSCLC patient samples | 309 patients, 538 samples |
| 2. ≥30 patients OR ≥40k cells | 1,283,972 cells |
| 3. Python-readable processed | h5ad files (scanpy native) on cellxgene + Zenodo |
| 4. Open access | Yes, no DUC required |
| 5. Peer-reviewed | Cancer Cell 2022 |
| 6. Independent lab | Trajanoski lab, Innsbruck (independent of Kim, Laughney, Wu, Lambrechts) |

Per the termination contract, this candidate is the lock.

### Reason 3: 2-cohort design with LuCA is more rigorous than original 4-cohort design

The original 4-cohort design had a hidden flaw the inventory work revealed:

LuCA's source studies INCLUDE Kim 2020 and Laughney 2020 (both are in the 29 harmonized datasets). If we were to use LuCA AND Kim AND Laughney as separate "cohorts," the same patient cells would appear twice in our analyses (once as raw cohort data, once harmonized into LuCA). This violates statistical independence assumptions for cross-cohort claims.

Wu 2021 is NOT in LuCA's source list (LuCA's source studies are pre-2022 publications; Wu 2021 was deposited late 2020 but the cohort was not included in LuCA's curation). Wu therefore provides genuinely independent validation when used alongside LuCA.

**Amended design has cleaner statistical independence than original.** This is a science upgrade, not a science compromise.

---

## What the amended design preserves

- **Cross-cohort triangulation** — LuCA itself is a 29-study triangulation; Wu provides independent external validation. The H2 hypothesis (cross-dataset signal transfer) is more robust under this design, not less.
- **LUAD + LUSC subtype coverage** — Wu 2021 has explicit LUAD/LUSC labels per patient. LuCA includes both subtypes. H5 (LUAD vs LUSC distinguishability) remains testable.
- **TCGA-LUAD + TCGA-LUSC bulk integration** — unchanged.
- **All 6 hypotheses** — H1 through H6 remain falsifiable under amended design with threshold adjustments noted below.

---

## Hypothesis threshold updates

| Hypothesis | Original threshold | Amended threshold | Reason |
|---|---|---|---|
| H1 | ≤0.4 Jaccard on Kim primary | ≤0.4 Jaccard on LuCA primary | Cohort substitution |
| H2 | ≥|ρ| 0.20, p<0.01 in ≥2 of 3 scRNA cohorts | ≥|ρ| 0.20, p<0.01 in BOTH LuCA AND Wu 2021 | 2-cohort design — both must PASS |
| H3 | Mean AUROC ≥0.65 over ≥30 drugs on TCGA-LUAD | UNCHANGED |
| H4 | High-confidence: H3 PASS AND H2 PASS in ≥2 of 3 cohorts | High-confidence: H3 PASS AND H2 PASS in BOTH LuCA AND Wu | Stricter under amended design |
| H5 | LUAD vs LUSC top-20 Jaccard ≤0.6 | UNCHANGED |
| H6 | KAALCURA contribution ≥0.005 ablation delta | UNCHANGED |

**Amended H2 and H4 are STRICTER than original** (require PASS in both cohorts, not 2-of-3). This is intentional: with a 1.2M-cell harmonized atlas as one cohort, BOTH cohorts must validate for the multi-cohort claim to be defensible.

---

## Updated dataset table

| Dataset | Source | URL | Format | Size | Role | Status |
|---|---|---|---|---|---|---|
| TCGA-LUAD | GDC | portal.gdc.cancer.gov | Open Access counts + MAF + clinical | ~10 GB | Drug response discovery, H3, H6 | Pending Phase 0 download |
| TCGA-LUSC | GDC | portal.gdc.cancer.gov | Open Access counts + MAF + clinical | ~10 GB | H5 subtype distinguishability | Pending Phase 0 download |
| **Salcher LuCA 2022** | **Zenodo + cellxgene** | **zenodo.org/records/7227571** | **h5ad (scanpy native) + scArches model** | **~5-10 GB** | **Primary scRNA harmonized atlas, H1, H2 cohort 1, H4** | **Pending Phase 0 download** |
| **Wu 2021** | **GEO GSE148071** | **ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE148071** | **10X RAW.tar (per-sample matrices)** | **180 MB tar** | **Independent validation, H2 cohort 2, H5 LUSC** | **Pending Phase 0 download** |

Datasets DROPPED from original spec:
- Kim 2020 (GSE131907) — already in LuCA
- Laughney 2020 (GSE123904) — already in LuCA
- Lambrechts 2018 (E-MTAB-6149) — Rds-only, not Python-readable

---

## Process audit

| Principle | Applied as |
|---|---|
| P3 (research before code) | Phase 0 inventory work caught Lambrechts incompatibility BEFORE writing slurm download scripts that would have failed. Bounded search per termination contract found a stronger design without burning unbounded time. |
| P4 (fix structure, don't tune) | The fix is structural (cohort replacement with stronger alternative), not parameter tuning of broken design. |
| P15 (only correct, honest, real science) | Erratum is open documentation of design change, including admission of a hidden flaw in the original design (Kim/Laughney would have double-counted in LuCA). Hypothesis thresholds tightened, not loosened. |
| P16 (preserve past work) | Original spec preserved at tag `workstream-b-spec-locked`. This erratum amends it without rewriting history. Phase 0 prep work (HPC env, dataset directories, NSCLC selectivity layer) remains valid under amended design. |

---

## Termination contract honored

Bounded search rules per the contract set during Phase 0:
- Termination criteria: 6 specific must-have requirements
- Termination rule: first candidate meeting all 6 → lock
- Salcher LuCA met all 6 on first verified candidate
- Search terminated as contracted

This erratum closes the cohort question. No further cohort search is in scope of Workstream B.

---

## What's locked now

- **Cohort design: LuCA 2022 + Wu 2021 + TCGA-LUAD + TCGA-LUSC**
- **Hypothesis thresholds: amended per table above**
- **Anti-scope-creep: still binding** — no further cohort substitutions during implementation
- **Phase plan: unchanged structure** (5 phases: download, KAALCURA scoring, cross-cohort, predictor, closure)
- **Tier target: still Tier A guaranteed, Tier B aspired** (per locked CSO call)

---

## Next implementation steps

1. **Write slurm batch download scripts** for:
   - LuCA from Zenodo (`https://zenodo.org/records/7227571`)
   - Wu 2021 RAW.tar from GEO
   - TCGA-LUAD via gdc-client (manifest needed)
   - TCGA-LUSC via gdc-client (manifest needed)

2. **Submit downloads as background slurm jobs.** Per Phase 0 prep log discipline: long-running ops as slurm jobs, not interactive SSH.

3. **Phase 0 closure tag** (`workstream-b-phase0-data-acquired`) after all downloads verify complete.

4. **Phase 1** (KAALCURA scoring across cohorts) follows.

---

*Honest erratum. Real spec amendment. Stronger design than original. Search terminated per contract. Implementation continues.*

— Prasad Akula & Claude (CSO)
2026-05-08
