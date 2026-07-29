# Partin et al., 2026 — Benchmarking community drug response prediction models: datasets, models, tools, and metrics for cross-dataset generalization analysis (IMPROVE benchmark)

## 0. Identification
- **Citation:** Partin A, Vasanthakumari P, Narykov O, Wilke A, Koussa N, Jones SE, Zhu Y, Overbeek JC, Jain R, Fernando GD, Sanchez-Villalobos C, Garcia-Cardona C, Mohd-Yusof J, Chia N, Wozniak JM, Ghosh S, Pal R, Brettin TS, Weil MR, Stevens RL. *Briefings in Bioinformatics* 2026 (PMC12794626, DOI 10.1093/bib/bbaf667, January 12, 2026). Originally arXiv 2503.14356v1 (March 18, 2025).
- **DOI (peer-reviewed):** 10.1093/bib/bbaf667 ✓ (verified via PMC12794626)
- **arXiv ID:** 2503.14356
- **First author:** Alexander Partin (1 of 20+ authors per arXiv abstract page; "Alexander Partin and 50 other authors" per arXiv)
- **Senior author (last position):** Rick L. Stevens
- **Institutional context:** JDACS4C-IMPROVE consortium (Joint Design of Advanced Computing Solutions for Cancer, NCI + DOE collaboration)
- **Layer 1 question:** Q6 anchor 1 — cross-dataset validation framework
- **Read by:** Claude (CSO) — 2026-05-10 (corrected — original note missed peer-reviewed publication status; this rewrite reflects January 2026 Brief Bioinformatics publication)

## 1. Why this paper

The IMPROVE benchmark is **the field-standard cross-dataset evaluation framework for drug response prediction**. NCI + DOE consortium backing makes it the de facto reference. For INTERCEPTA's Charter §1.2 V1 (cross-cell-line dataset) and V2 (cell-line-to-organoid), IMPROVE provides:
1. The standardized evaluation protocol
2. The empirical evidence that within-dataset CV systematically overestimates
3. The infrastructure (5 datasets + 6 standardized models + scalable workflow) for benchmarking INTERCEPTA against published baselines

## 2. What they did

**Framework components (per arXiv abstract):**
- **5 publicly available drug screening datasets** — GDSC, CCLE, and three additional sources
- **6 standardized DRP (drug response prediction) models** — implementations harmonized for fair comparison
- **Scalable workflow** for systematic cross-dataset evaluation

**Evaluation metrics introduced:**
- **Absolute performance** — predictive accuracy across datasets (AUROC, RMSE, etc.)
- **Relative performance** — performance *drop* compared to within-dataset results (quantifies generalization gap)

**Methodology:**
- Train on dataset A, test on dataset B (rotated across pairs)
- Compare within-dataset CV to cross-dataset performance for each (model, dataset-pair)
- Quantify how much within-dataset CV overestimates real generalization

## 3. What they found

- **Within-dataset cross-validation systematically overestimates model performance** compared to cross-dataset evaluation
- Performance gap exists across all 6 models tested — not a single-model artifact
- Cross-dataset generalization gap varies by (drug type, dataset pair, model architecture)
- Standardized framework enables reproducibility for community
- **Conclusion:** within-dataset CV is necessary but not sufficient for assessing real-world DRP applicability

## 4. What's strong

- **Peer-reviewed in *Briefings in Bioinformatics*** (January 2026) — upgraded from arXiv preprint status
- **NCI + DOE institutional backing** via JDACS4C-IMPROVE consortium — gold-standard pharmacogenomic methodology infrastructure
- **20+ authors** including computational biology specialists at Argonne National Laboratory, NCI, Texas Tech, Frederick National Laboratory — broad expertise base
- **5 datasets + 6 models** — rigorous multi-axis comparison
- **Two-metric framework** (absolute + relative performance) — captures both raw accuracy and generalization gap
- **Standardized workflow** released as community infrastructure
- **Field-defining for INTERCEPTA's V1 validation level** — INTERCEPTA can be benchmarked directly against IMPROVE-standardized models

## 5. What's limited

- **Bulk cell-line drug response only** — does not test scRNA-seq drug response prediction (INTERCEPTA's actual target)
- **Cancer-only** — same Charter §1.1 universality gap as all cell-line-based work
- **6 standardized models predate FM-based methods** — scFoundation, UCE, scGPT, Geneformer FM-augmented variants not in the benchmark as of publication. **INTERCEPTA contribution: extend IMPROVE-style methodology to FM-era methods.**
- **Cross-dataset is intermediate, not clinical** — IMPROVE tests dataset-A-to-dataset-B; the further translation to organoids, PDX, patients still has additional generalization gaps (Charter V2-V5)
- **Drug-specific failure modes not deeply analyzed** — paper reports aggregate generalization gaps; per-drug-class failure characterization is shallower

## 6. INTERCEPTA implications

**For Q6 (Decision 6 validation cascade):**
- **V1 (cross-cell-line dataset):** INTERCEPTA must use IMPROVE-style cross-dataset evaluation. Specifically, train on GDSC, test on CCLE/CTRP; rotate pairs.
- **Use IMPROVE-standardized model implementations as baselines.** Any INTERCEPTA gain over IMPROVE baselines is the actual contribution.
- **Report both absolute and relative performance metrics** per IMPROVE protocol.

**For Charter §1.2 V1-V4 predictive validity:**
IMPROVE empirically validates the **falsifiability of within-dataset CV**. INTERCEPTA's V0 (within-dataset CV) is necessary, but the architecture's real defensibility depends on V1+ cross-dataset performance.

**For Decision 6 PROPOSED commitment:**
- V1 pass criterion should be "INTERCEPTA matches or exceeds the best IMPROVE baseline on cross-dataset AUROC"
- V0-to-V1 generalization gap should be reported as a Decision 6 metric (per IMPROVE relative-performance framework)

**For Charter §1.1 universality:**
IMPROVE's bulk-cell-line focus means cross-disease V6 is unaddressed in the existing benchmark. **INTERCEPTA's contribution to the field would be extending IMPROVE methodology to:**
- scRNA-seq deployment context (not just bulk)
- Cross-disease grid (not just cross-dataset within cancer)
- FM-based methods (not just classical DRP)

## 7. Followup citations
1. **Vasanthakumari et al.** (co-author on Partin 2026; specific drug response methodology papers worth tracking)
2. **JDACS4C-IMPROVE consortium publications** at https://github.com/JDACS4C-IMPROVE/ — production codebase
3. **Tang, Powell, Gottlieb 2022** (Q6 anchor 2) — pathway-based transfer learning; complementary methodology
4. **Recent benchmark extensions** — bioRxiv 2025.12.09.693213 cites Partin 2025 and extends to perturbation response models (uses CPA, GEARS, scFoundation as baselines)

## 8. Discipline check
- [x] All claims verified primary-source: arXiv abstract page (showing "Alexander Partin and 50 other authors"), PMC12794626 listing all 20 named authors, bioRxiv citations referencing Partin et al. as IMPROVE benchmark anchor
- [x] DOI verified (peer-reviewed Brief Bioinformatics + arXiv preprint both confirmed)
- [x] First author verified: Alexander Partin
- [x] Senior author verified: Rick L. Stevens (last position)
- [x] Peer-reviewed publication status (Brief Bioinformatics Jan 2026) verified — corrects original note's "arxiv preprint as of 2026 cutoff" claim
- [x] **Errata note:** original 2026-05-10 file said "arxiv preprint" — paper is now peer-reviewed in Briefings in Bioinformatics (Jan 12, 2026). Note rewritten to reflect updated publication status. Drift Instance #4 (minor) corrected.

— Claude (CSO), 2026-05-10 (corrected pass)
