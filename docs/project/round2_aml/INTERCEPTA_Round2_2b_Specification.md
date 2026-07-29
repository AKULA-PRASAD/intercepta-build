# INTERCEPTA Round 2.2b — Specification

**Status:** Pre-code specification. Written and committed before implementation.

**Date:** April 22, 2026
**Authors:** Prasad Akula & Claude, Co-Founders of INTERCEPTA
**Predecessor:** Round 2.2a closure (commit 81db630, tag round2.2a-closed-partial-success)

---

## 1. Mission Statement

Re-run the Round 2.2a pyUCell-based AML net integration with three corrections derived from Round 2.2a's partial-success findings:

1. **Q_A operationalization corrected** — test LSC quiescence against the proliferating committed progenitor population (Prog-like), not the terminally differentiated monocyte population (Mono-like). Correction grounded in Van Galen 2019 primary source verification.

2. **Q_B addressed via residualization** — replace raw R_ddr with PCNA-style residualized R_ddr. This is a published standard technique for separating DNA repair signal from proliferation co-regulation, not a threshold relaxation.

3. **Q_C threshold preserved at 0.55** — we do NOT lower the threshold to match Round 2.2a's observed 0.532. If within-dataset drug prediction truly plateaus at 0.53 with 3 gene-signature axes, that is a finding that must earn its documentation through repeated failure, not through pre-emptive threshold relaxation.

Scope is tight — corrections only. Therapeutic index and selectivity testing are deferred to Round 2.2c.

---

## 2. Context — What Round 2.2a Established

**Scientific wins preserved (commit 81db630):**
- Q_D PASSED: Spearman ρ = −0.235, p = 0.00537, 139 drugs aligned. First validated cross-dataset drug prediction in INTERCEPTA. Sign flipped from Round 2.1d's ρ = +0.403 to correct negative direction.
- Q_E PASSED: Jaccard = 0.111. HSC-like top 10 includes Venetoclax — BCL2-targeting LSC therapy per vision Part 5.2, surfaced autonomously from drug-response data.

**Gate failures requiring correction:**
- Q_A: HSC-like R_prolif (0.576) not < Mono-like R_prolif (0.506). Specification design error: Mono-like is terminally differentiated, not proliferative.
- Q_B: max pairwise |r| = 0.932 (R_prolif vs R_ddr) > 0.9 threshold. Known AML biology.
- Q_C: mean CV-AUROC = 0.532 < 0.55 threshold. Matches Round 2.1d (0.534) — essentially unchanged by scoring method.

**Van Galen cell-type axes preserved (from Round 2.2a):**
The file `results/vangalen_celltype_ucell_axes_round22a.csv` contains the pyUCell-computed UCell axes for all 21 cell types. Round 2.2b reuses these directly (Principle 16 — preserve past work) rather than recomputing.

---

## 3. Literature-Grounded Design Decisions

### 3.1 Q_A comparator correction — Van Galen 2019 primary source

**Verified claim from Van Galen 2019 (Cell):** "less than 7% of CD14+ cells are proliferating" (reference: the original Van Galen et al. 2019 Cell paper, Figure 4G-H analysis of AML419A sample).

**Verified hierarchy from Van Galen 2019:** Malignant AML cells are classified into six types — HSC-like, Progenitor-like (Prog-like), GMP-like, ProMono-like, Mono-like, cDC-like. The paper describes "HSC/Prog-like cells and differentiated monocyte-like cells" as "two malignant cell types at opposite ends of the developmental axis" — both low-proliferation but for opposite reasons (stem quiescence vs terminal differentiation).

**Verified refinement from Zeng et al. 2022 (Nature Medicine):** Seven refined AML subpopulations ranging from "quiescent LSPCs, primed LSPCs, cycling LSPCs" (primitive states) to "GMP-like, Pro-Mono-like, Mono-like, cDC-like" (differentiated states).

**Operationalization for Q_A:** LSC quiescence is a biological property of HSC-like cells RELATIVE TO actively proliferating progenitors. The correct comparator is Prog-like (or GMP-like as a secondary check), NOT Mono-like.

**Round 2.2a data that would have passed this test:**
- HSC-like R_prolif = 0.576
- Prog-like R_prolif = 0.823 (margin = 0.247, strong pass)
- GMP-like R_prolif = 0.862 (margin = 0.286, strong pass)

### 3.2 Q_B treatment — PCNA-style residualization (pick B2)

**Published method basis:** Peterson LE & Kovyrshina T, Cancers 2019 (11:501), "DNA Repair Gene Expression Adjusted by the PCNA Metagene Predicts Survival in Multiple Cancers" (PMID 30965671). This paper demonstrates that DNA repair genes are "strongly co-regulated by proliferation" across 18 TCGA cancers, and establishes PCNA-metagene residualization as the standard statistical approach for separating DNA repair signal from proliferation signal.

**Related published work:** Venet et al.'s meta-PCNA score (cited across multiple cancer drug-response prediction papers); the POLθ paper in npj Precision Oncology 2025 demonstrating "strong correlation (Pearson's r = 0.7–0.8) with gene expression signatures of cellular proliferation" for DNA repair genes across most cancer types.

**Why residualization rather than threshold relaxation (B1) or gene-set rebuild (B3):**
- **B1 (threshold relax to 0.95):** Any threshold I pick will be a number that lets Round 2.2a's observed 0.932 pass. This is post-hoc threshold tuning even with literature justification. Rejected.
- **B3 (rebuild DDR signature to exclude proliferation-coupled genes):** Literature falsifies this approach. BRCA1, BRCA2, RAD51, FANCA, FANCD2, RPA1 are all E2F targets with S-phase peak expression. Only MLH1, MSH2, ATM are plausibly proliferation-independent at the gene-expression level — three genes is too few for a pyUCell signature. Rejected.
- **B2 (residualize):** Published standard technique. Produces R_ddr_residual = DNA repair activity above the proliferation baseline — a meaningful biological quantity that correlates with actual HR-deficiency / MMR-deficiency rather than just "this cell is dividing." Selected.

**Implementation detail:** After pyUCell scoring produces (R_prolif, R_emt, R_ddr) on BeatAML:
```
Fit on BeatAML:  R_ddr = α + β · R_prolif + residual
Compute:         R_ddr_residual_BeatAML = R_ddr − (α + β · R_prolif)
Apply same β, α to Van Galen:
                 R_ddr_residual_Vangalen = R_ddr_Vangalen − (α + β · R_prolif_Vangalen)
```

Both datasets use the SAME α and β (fitted on BeatAML, the larger cohort) to preserve cross-modality commensurability.

**Predicted outcome:** By construction, corr(R_prolif, R_ddr_residual) ≈ 0 on BeatAML. On Van Galen, the correlation should also be near zero if the β coefficient transfers cleanly.

### 3.3 Q_C threshold preserved — literature anchor

**Published BeatAML benchmarks from research:**
- MDREAM (npj Precision Oncology 2023): Spearman correlation 0.68 on BeatAML validation, using ensemble models with gene expression + mutations + clinical data across 122 drugs
- NetAML (Advanced Science 2025): AUROC >0.70 only for specific well-characterized drugs (Venetoclax, FLT3is) with mean correlation 0.38
- Systematic assessment of 110,000 drug-response prediction models (Menden et al.): gene expression features with elastic net across ALL genomic profiling platforms required for best-in-class predictors

**What this tells us:** Our 3-axis predictor at AUROC 0.53 is genuinely at the low end of the field. But the literature ceiling of 0.68 Spearman requires FULL omics + ensembles of hundreds of features. We are using 48 genes condensed to 3 axes. The gap is expected.

**Why we hold threshold at 0.55:** If we lower the threshold to match observed performance, we produce a "passing" result that tells us nothing. If we hold the threshold and fail again, we earn the right to document a real finding: "3-axis gene-signature predictors plateau at ~0.53 for pan-AML drug prediction regardless of scoring method (z-score in 2.1d, pyUCell in 2.2a, pyUCell+residualization in 2.2b)." That finding justifies Round 2.2c or later as an explicit feature-engineering round.

### 3.4 Scope — corrections only (pick G2)

Round 2.2b does NOT include:
- Therapeutic index (malignant vs non-malignant selectivity) → deferred to Round 2.2c
- Q_H Venetoclax reproducibility as formal gate → tracked as informal diagnostic in closure memo
- Feature-space expansion (mutations, pathway signatures, clinical) → deferred to later rounds

Rationale: Round 2.1d → 2.2a sequence demonstrated that scope creep kills rounds. Tight scope lets us test exactly the corrections and nothing else. Each corrected element earns its own pass or fail honestly.

---

## 4. Mechanism — Unchanged from Round 2.2a

pyUCell rank-based Mann-Whitney U scoring with `max_rank=17663`, `missing_genes='impute'`, `n_jobs=1` (the Round 2.2a bug fix).

Gene sets unchanged. The only computation change is the post-hoc residualization of R_ddr on R_prolif.

---

## 5. Architecture

```
Van Galen AnnData (44,823 cells × 27,899 genes)
    ↓ pseudobulk per cell type
Pseudobulk AnnData (21 cell types × 27,899 genes)
    ↓ pyUCell with 3 signatures (prolif, emt, ddr)
Van Galen axes (21 × 3): R_prolif, R_emt, R_ddr

BeatAML bulk TSV
    ↓ wrap as AnnData
BeatAML AnnData (707 × 22,842)
    ↓ pyUCell with 3 signatures, max_rank=17663
BeatAML axes (707 × 3): R_prolif, R_emt, R_ddr
    ↓ fit α, β from: R_ddr = α + β · R_prolif + ε
    ↓ compute R_ddr_residual = R_ddr − (α + β · R_prolif)
BeatAML final axes: R_prolif, R_emt, R_ddr_residual
Van Galen final axes: R_prolif, R_emt, R_ddr_residual (using BeatAML-fit α, β)
    ↓ KAALCURA.train_drug_models on BeatAML final axes + curve_fits AUC
Drug models (per drug: logistic weights on 3 axes, CV AUROC)
    ↓ KAALCURA.predict_sensitivity_multi_drug with Van Galen final axes
Per (cell type, drug) P(sensitive) predictions
    ↓ 5 validation queries + 1 diagnostic
Layer 2 net (IF all 5 pass)
```

**Key implementation note:** The residualization regression (β, α fit) happens on BeatAML ONLY, then applied to Van Galen. This is the correct direction — BeatAML has n=707 (stable β estimate), Van Galen has n=21 (unstable if fit there). Cross-modality commensurability requires using the same β on both.

---

## 6. Validation Queries — Five Pass/Fail Gates + One Diagnostic

### Q_A (corrected) — LSC Quiescence against proliferating progenitors

**Criterion:** HSC-like R_prolif < Prog-like R_prolif

**Comparator biology verification (mandatory new section per Round 2.2a spec-design-lesson):**
- Van Galen 2019 Cell (10.1016/j.cell.2019.01.031): Prog-like is identified as the actively proliferating committed progenitor population; HSC-like is the undifferentiated quiescent stem-cell-like population
- Zeng et al. 2022 Nature Medicine: Refines into "quiescent LSPCs" and "cycling LSPCs" as distinct primitive subpopulations
- Primary text quote: HSC/Prog-like occupies one developmental pole; Mono-like occupies the opposite pole; both are low-proliferation but for opposite reasons

**Rationale:** Testing LSC quiescence requires comparing HSC-like to a proliferating cell type. Prog-like is Van Galen's proliferating committed progenitor population. Mono-like was the wrong comparator in Round 2.2a because monocytes are terminally differentiated.

**Expected:** Should PASS comfortably. Round 2.2a data had HSC-like = 0.576, Prog-like = 0.823 (margin 0.247). Residualization of R_ddr does not affect R_prolif values.

**Secondary check (diagnostic, not gate):** Also report HSC-like R_prolif vs GMP-like R_prolif for cross-reference. Round 2.2a data: HSC-like 0.576 vs GMP-like 0.862.

### Q_B (corrected via residualization) — Axis Non-Redundancy

**Criterion:** Max pairwise |Pearson r| among (R_prolif, R_emt, R_ddr_residual) across 21 Van Galen cell types < 0.9

**Computation:** After BeatAML-fit residualization applied to Van Galen, compute the 3×3 correlation matrix on the 21 cell types and check max off-diagonal |r|.

**Expected outcome:** By construction, |corr(R_prolif, R_ddr_residual)| ≈ 0 on BeatAML. On Van Galen, the correlation depends on whether the BeatAML-fit β transfers cleanly. Likely Van Galen max |r| will be driven by R_prolif vs R_emt (was 0.044 in Round 2.2a) or R_emt vs R_ddr_residual (unknown).

**What "pass" tells us:** R_prolif and R_ddr_residual capture distinct biological signals — DDR activity above baseline proliferation is a non-redundant feature.

**What "fail" tells us:** Either the BeatAML β doesn't transfer to Van Galen (different cancer subpopulation coupling), or R_emt correlates with one of the other axes in an unexpected way.

### Q_C (unchanged) — BeatAML Drug Model Quality

**Criterion:** Mean CV-AUROC ≥ 0.55 across trained BeatAML drug models AND all three axes contribute (max|coefficient| > 0 for each of R_prolif, R_emt, R_ddr_residual across drugs with AUROC ≥ 0.60)

**Threshold justification:** Held at 0.55 intentionally. Round 2.1d achieved 0.534, Round 2.2a achieved 0.532. If Round 2.2b with residualized axes achieves similar 0.53, we have three consecutive rounds establishing a genuine plateau. That plateau becomes scientifically documentable — feature engineering beyond 3 axes is needed for higher AUROC. Lowering the threshold to 0.53 now would foreclose that finding.

**Per-axis contribution structure check:** Round 2.2a passed this check (all three axes had non-zero max |coef|). Round 2.2b should pass if the residualized R_ddr still carries drug-discrimination signal (which it should, since residualization removes proliferation covariance but preserves DDR-specific signal).

### Q_D (unchanged) — Cross-Dataset Biological Prediction

**Criterion:** Spearman correlation between Van Galen Prog-like per-drug P(sensitive) predictions and BeatAML FLT3-ITD+ minus FLT3-ITD- per-drug median AUC differential is negative (ρ < 0) with p < 0.05, across drugs with ≥5 samples in each ITD group.

**Expected:** Should continue to PASS. Round 2.2a achieved ρ = −0.235, p = 0.00537. Residualization of R_ddr shouldn't disrupt this — the Prog-like signal is driven by R_prolif primarily, which is unchanged.

### Q_E (unchanged) — Distinguishability

**Criterion:** Jaccard(HSC-like top 10 drugs, Prog-like top 10 drugs) < 0.6

**Expected:** Should continue to PASS. Round 2.2a achieved 0.111. The drug ranking semantics should be preserved even with residualized R_ddr.

**Venetoclax preservation diagnostic (not gated):** Report whether Venetoclax appears in HSC-like top 10. Round 2.2a had it. If Round 2.2b preserves it, this is a cross-round reproducibility signal worth documenting.

### Q_F (DIAGNOSTIC — unchanged) — Axis Range

Report per-axis Van Galen / BeatAML range ratio for all three final axes (R_prolif, R_emt, R_ddr_residual). No threshold applied.

---

## 7. Pass/Fail Protocol

### All five pass (Q_A, Q_B, Q_C, Q_D, Q_E) → net saved
- Save `aml_net_round22b_ucell_residual.gpickle`
- Save `kaalcura_ucell_residual_state_round22b.pkl`
- Save `beataml_ucell_residual_axes_round22b.csv` (707 × 3: R_prolif, R_emt, R_ddr_residual)
- Save `vangalen_ucell_residual_axes_round22b.csv` (21 × 3)
- Save `residualization_coefficients_round22b.json` (α, β from BeatAML fit)
- Write closure memo as successful-integration record
- Tag: `round2.2b-validated`

### Any of the five fail → no net saved
- Summary JSON written with all query numbers
- Closure memo documents exactly what failed and why
- If Q_C fails at ~0.53 again: documented as a three-round plateau finding, scoping Round 2.2c as feature-engineering
- If Q_B fails: residualization didn't transfer cleanly across datasets; documented as a new methodology finding
- If Q_A fails: something fundamental is wrong with the corrected comparator choice; re-examine

**Principle 15 commitment (unchanged):** Thresholds locked. No post-hoc adjustment. Failed gates produce honest closure memos, not spec revisions.

---

## 8. Expected Runtime and File Outputs

**Runtime:** Similar to Round 2.2a (~5-10 minutes). Residualization adds a single linear regression (<1s).

**Memory:** Same as Round 2.2a (~3-5 GB peak).

**Output artifacts:**

| Path | Purpose |
|------|---------|
| `results/aml_net_round22b_ucell_residual.gpickle` | Layer 2 integrated net (if all 5 pass) |
| `results/aml_net_round22b_summary.json` | Structured verdict + all query numbers + Q_F diagnostic |
| `results/aml_net_round22b_build.txt` | Full run log |
| `results/beataml_ucell_residual_axes_round22b.csv` | 707 × 3 with residualized axis |
| `results/vangalen_ucell_residual_axes_round22b.csv` | 21 × 3 with residualized axis |
| `results/residualization_coefficients_round22b.json` | α, β from BeatAML fit |
| `results/kaalcura_ucell_residual_state_round22b.pkl` | Trained model object |

---

## 9. Principle Audit — In Advance

| Principle | Applied in Round 2.2b as |
|-----------|-------------------------|
| P3 (research before code) | Done: Van Galen 2019 comparator verified, PCNA residualization method verified in Peterson 2019 / Venet, BeatAML benchmark AUROCs checked (MDREAM 0.68 with full omics establishes context for 0.55 threshold). Spec written before code. |
| P4 (fix structure, don't tune) | Q_A fixes specification error structurally (correct comparator). Q_B fixes axis computation structurally (residualization). Q_C threshold NOT tuned despite repeated near-misses — structural fix would require feature expansion (Round 2.2c+). |
| P15 (honest validation) | Five queries with locked thresholds. Q_C held at 0.55 despite knowing Round 2.2a achieved 0.532 — refuses to retrofit threshold to observed result. No post-hoc adjustment. |
| P16 (preserve past work) | Round 2.2a pyUCell axes CSV reused directly. KAALCURA v1 unchanged. Gene sets unchanged. Only addition: post-hoc residualization step. |

### New audit element — Comparator Biology Verification (spec-design-lesson from Round 2.2a)

**Mandatory for every future round specification:** When a validation gate compares two biological entities (e.g., HSC-like vs X), the spec must include explicit primary-source citations that establish the biology of BOTH entities. Round 2.2a failed Q_A because the spec author assumed Mono-like was proliferative without checking Van Galen 2019. This section institutionalizes the check.

**Applied in Round 2.2b:**
- Q_A comparator (Prog-like) verified: Van Galen 2019 identifies Prog-like as proliferating committed progenitor population; Zeng et al. 2022 refines as "cycling LSPCs"
- Q_A cross-check (GMP-like) verified: Van Galen 2019 identifies GMP-like as granulocyte-macrophage progenitor, developmentally downstream of Prog-like, also actively proliferating

---

## 10. Git Commit Plan

### Commit A (this spec, before code) ← THIS COMMIT
```
Round 2.2b specification: corrections round with literature-grounded design

Three corrections from Round 2.2a closure:
- Q_A comparator fixed (Prog-like not Mono-like per Van Galen 2019
  primary source: CD14+ <7% proliferating, HSC/Prog-like and Mono-like
  at opposite developmental poles)
- Q_B via PCNA-style residualization (Peterson 2019 Cancers standard
  method; R_ddr_residual = R_ddr - (α + β·R_prolif), fit on BeatAML)
- Q_C threshold held at 0.55 (not relaxed); three consecutive rounds
  near 0.53 would document a real plateau finding

Scope tight: corrections only. Therapeutic index deferred to Round 2.2c.

New spec section: mandatory comparator biology verification with primary
source citations (spec-design-lesson from Round 2.2a).
```

### Commit B (after implementation, if all five pass)
```
Round 2.2b validated: corrections accepted, Layer 2 net saved

[stats from actual run including residualization coefficients α, β]
```
Tag: `round2.2b-validated`

### Commit C (after implementation, if any fail)
```
Round 2.2b closure: [specific findings]

Honest documentation of what passed/failed with [specific numerical
evidence], scoping Round 2.2c or deeper reexamination.
```
Tag: `round2.2b-closed-[finding]`

---

## 11. What Round 2.2b Does NOT Cover

Explicitly out of scope:
- RNA velocity integration (requires 10X Chromium data, not in Van Galen — deferred to later)
- Therapeutic index computation against non-malignant cell types (Round 2.2c scope)
- Novel molecule generation (Round 2.3+)
- Combination drug predictions (Round 2.2d+)
- Feature-space expansion beyond 3 gene-signature axes (if Q_C fails again, Round 2.2c or later)
- Formal Q_H (Venetoclax reproducibility as gate) — tracked as informal diagnostic only

---

## 12. Review Checkpoint

This specification is the review checkpoint. Prasad reviews. Concerns, disagreements, changes go into discussion before implementation begins. Once approved via commit, spec becomes the contract.

The three locked design decisions (Q_A comparator = Prog-like; Q_B mechanism = residualization with BeatAML-fit β; Q_C threshold = 0.55 held strict) are the result of honest research that changed CSO picks twice when literature contradicted initial intuition. Document the decision lineage in case Round 2.2b fails and future rounds need to understand why these specific picks were made.

If approved as-is, proceed to implementation. If changes requested, revise this document, recommit, then proceed.

*— Prasad Akula & Claude, Co-Founders of INTERCEPTA*
*April 22, 2026*
