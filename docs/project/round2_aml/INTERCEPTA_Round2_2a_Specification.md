# INTERCEPTA Round 2.2a — Specification (Amendment v2)

**Status:** Pre-code specification. Amended April 22, 2026 to demote Q_F from validation gate to diagnostic metric.

**Amendment rationale:** Pre-committing a threshold on axis range (originally Q_F at 50%) before seeing data is methodologically circular — any chosen threshold would be the number that matches what we expect the mechanism to produce. The principled choice is to gate on the downstream biological claim (does the model predict correctly?) and report the intermediate metric (axis range) as diagnostic information without using it as a pass/fail criterion. If downstream queries pass with compressed axes, that is either a real finding about rank-order preservation under compression, or a confounder that downstream rounds (e.g., Round 2.2b therapeutic index) will expose.

**Date (original):** April 22, 2026 (commit 09da7fd)
**Date (amendment):** April 22, 2026
**Authors:** Prasad Akula & Claude, Co-Founders of INTERCEPTA

---

## 1. Mission Statement

Integrate Van Galen 2019 scRNA-seq cell-type data into the Round 2.1b AML net skeleton as Layer 2 (transcriptome), using pyUCell rank-based gene scoring to produce axis scores that are commensurable between BeatAML bulk and Van Galen pseudobulk data. Train AML-specific drug response models on BeatAML using the new axis mechanism. Apply to Van Galen cell-type pseudobulks for per-cell-type drug sensitivity prediction. Validate via five biologically and methodologically grounded queries, with axis range reported as a diagnostic metric.

This round addresses the Round 2.1d methodology finding that bulk-trained KAALCURA z-score parameters do not transfer to scRNA-seq pseudobulk. By replacing z-score-based axis computation with pyUCell's Mann-Whitney U rank-based scoring, the two modalities enter the same framework without reference-parameter transfer.

---

## 2. Context — What Round 2.1d Established

**Validated (from Round 2.1d v5.2):**
- KAALCURA bulk-trained infrastructure on AML works: median CV-AUROC 0.556, 31/141 drugs ≥ 0.60
- All three KAALCURA axes (prolif, emt, ddr) carry independent drug-prediction signal in AML
- Van Galen AnnData is structurally sound: 44,823 cells, 21 cell types, 48/48 KAALCURA gene coverage, LSC signature biology intact (Round 2.1c validation preserved)

**Methodology gap identified:**
- Z-score-based axis transfer from bulk reference to scRNA-seq pseudobulk produces compressed axes (Van Galen R_prolif range 0.48 vs BeatAML 4.54)
- Root cause: bulk log-TPM and scRNA-seq log-normalized pseudobulk live on different expression scales; z-scoring the second against the first's means/stds uniformly shifts values to extremes
- The three KAALCURA axes themselves are biologically valid — only the bulk-reference z-score mechanism is the transfer barrier

---

## 3. Mechanism — pyUCell Rank-Based Scoring

### 3.1 Why pyUCell

pyUCell (Andreatta & Carmona 2026, *Bioinformatics*) is the Python implementation of UCell, a published rank-based gene signature scoring method. It uses the Mann-Whitney U statistic on gene-expression ranks within a sample, producing scores that depend only on relative gene ordering — independent of expression scale, dataset composition, or technology platform. This makes it the correct tool for cross-modality application where z-score methods fail.

Citation: Andreatta, M., & Carmona, S. J. (2021) *UCell: Robust and scalable single-cell gene signature scoring.* Computational and Structural Biotechnology Journal. Andreatta, M., & Carmona, S. J. (2026) *UCell and pyUCell: single-cell gene signature scoring for R and Python.* Bioinformatics.

### 3.2 Gene sets — unchanged from Round 1

We reuse the three gene sets from `intercepta_kaalcura_v1.py` without modification (Principle 16). The sets are biological definitions, not bulk-RNA-seq-specific artifacts. They transfer cleanly across scoring methods.

| Axis | Gene set (n) | Semantic meaning |
|------|------|------------------|
| prolif | 20 genes: MKI67, TOP2A, PCNA, CDK1, CCNB1, AURKA, BUB1, PLK1, MCM2, MCM6, FOXM1, BIRC5, NUSAP1, TPX2, CDC20, CENPF, KIF11, PRC1, HMGA1, MYBL2 | Active cell division |
| emt | 13 genes: VIM, CDH2, SNAI1, SNAI2, ZEB1, ZEB2, TWIST1, FN1, MMP2, MMP9 (positive); CDH1, CLDN1, TJP1 (inverted — epithelial markers removed) | EMT/mesenchymal state |
| ddr | 15 genes: BRCA1, BRCA2, RAD51, ATM, ATR, CHEK1, CHEK2, PARP1, PARP2, XRCC1, MLH1, MSH2, FANCA, FANCD2, RPA1 | DNA damage repair activity |

Total: 48 genes. BeatAML has 47/48 (missing CLDN1 — an epithelial marker that contributes to EMT as an inverted gene, minor loss). Van Galen has 48/48. Missing genes are handled by pyUCell's `missing_genes='impute'` option (assigned max_rank, treated as not enriched).

**Note on inverted EMT genes (CDH1, CLDN1, TJP1):** pyUCell supports positive/negative signature genes via `+`/`-` suffix. We will format the EMT signature as:
```
emt_signature = ['VIM', 'CDH2', 'SNAI1', 'SNAI2', 'ZEB1', 'ZEB2', 'TWIST1',
                 'FN1', 'MMP2', 'MMP9', 'CDH1-', 'CLDN1-', 'TJP1-']
```
The `-` suffix tells pyUCell those genes contribute negatively. This preserves Round 1's inversion semantic.

### 3.3 The max_rank parameter — empirically determined

Per the pyUCell paper: *"rmax should be set approximately to the median number of detected (non-zero) genes per cell."*

**Empirical measurement (run in Round 2.2 environment, logged in session):**

| Dataset | Min non-zero | Median non-zero | Max non-zero |
|---------|-------------|-----------------|-------------|
| Van Galen pseudobulk (21 cell types) | 13,485 | 17,906 | 20,526 |
| BeatAML bulk (707 samples)           | 16,099 | 17,663 | 19,537 |

The medians are within 1.4% of each other. This is strong evidence that pseudobulk-of-scRNA-seq and bulk-RNA-seq produce comparable gene detection depths in this disease context — exactly the condition that makes pyUCell cross-dataset scoring valid.

**Decision: max_rank = 17,663** (BeatAML median, the lower of the two).

Reasoning: using the lower median ensures both datasets have comparable rank saturation. Genes beyond rank 17,663 are the near-zero / dropout tail that should not contribute to signature scores.

Alternative considered: max_rank = 17,906 (Van Galen median), or 17,785 (midpoint). The difference is ≤1.4% — negligible relative to the 1,500 default that the Round 2.1d attempt implicitly assumed. What matters is that we are in the correct order of magnitude (~18K) not the default 1,500.

### 3.4 Drug response model

Logistic regression on (prolif_UCell, emt_UCell, ddr_UCell) → P(sensitive), binarized at median AUC per drug. 5-fold cross-validation. Same mechanism as Round 1 KAALCURA's `train_drug_models` — we reuse that class's method, just feeding it pyUCell-derived axes instead of z-score-derived axes.

This is the cleanest architectural choice: KAALCURA v1 stays unchanged (Principle 16), we just call its `train_drug_models` with a different axes matrix.

---

## 4. Architecture

### 4.1 Pipeline

```
Van Galen AnnData (44,823 cells × 27,899 genes)
    ↓ pseudobulk per cell type
Pseudobulk AnnData (21 cell types × 27,899 genes)
    ↓ pyUCell with 3 signatures (prolif, emt, ddr)
Van Galen axes (21 × 3)

BeatAML bulk TSV
    ↓ parse display_label/sample_cols
BeatAML DataFrame (707 × 22,842)
    ↓ wrap as AnnData
BeatAML AnnData
    ↓ pyUCell with 3 signatures, SAME max_rank=17663
BeatAML axes (707 × 3)
    ↓ KAALCURA.train_drug_models on BeatAML axes + curve_fits AUC
Drug models (per drug: logistic weights on 3 axes, CV AUROC)
    ↓ KAALCURA.predict_sensitivity_multi_drug with Van Galen axes
Per (cell type, drug) P(sensitive) predictions
    ↓ integrate into Round 2.1b skeleton
Layer 2 net (IF all five validation queries pass)
```

### 4.2 Key design decisions locked

| Decision | Choice | Justification |
|----------|--------|--------------|
| Scoring method | pyUCell rank-based Mann-Whitney U | Scale-invariant, published, cross-modality valid |
| max_rank | 17,663 | Empirical median non-zero gene count (BeatAML, lower of two datasets) |
| Signature format | Round 1 gene sets verbatim, EMT with +/- suffixes | Preserves Round 1 biology, leverages pyUCell negative genes support |
| BeatAML wrapping | pandas DataFrame → AnnData via ad.AnnData(X, obs, var) | pyUCell requires AnnData; wrapping is trivial |
| Drug training | KAALCURA.train_drug_models with pyUCell axes | Reuses validated Round 1 method, swap-in axis source |
| Drug prediction | KAALCURA.predict_sensitivity_multi_drug | Reuses validated Round 1 method |
| missing_genes | 'impute' | Safe default: missing genes treated as not enriched |
| Axis range | Measured and reported as diagnostic only | See section 5.6 — pre-committing a threshold is circular |

### 4.3 Environment

**Python environment: `intercepta-scrna` (conda)**
- Python 3.11.15
- pyucell 0.6.0
- anndata 0.12.11
- pandas 2.3.3, scipy 1.17.1, scikit-learn 1.8.0
- networkx 3.6.1
- openpyxl 3.1.5 (for BeatAML clinical xlsx)
- Frozen package list: `code/environment_round2_2.txt`

**Round 1 KAALCURA import**
- `sys.path.insert(0, CODE_ROOT)` where CODE_ROOT = `~/INTERCEPTA/code`
- Imports: `from intercepta_kaalcura_v1 import KAALCURA` (unmodified Round 1 class)
- We will NOT modify `intercepta_kaalcura_v1.py` (Principle 16)

---

## 5. Validation Queries — Five Pass/Fail Gates + One Diagnostic Metric

All five validation queries (Q_A through Q_E) must pass for the Layer 2 net to be saved. If any fail, diagnostic JSON is written, no graph is saved, and we produce an honest closure memo. Q_F is measured and reported but does not gate the round.

### Q_A — LSC Quiescence (Van Galen biology replicates)
**Criterion:** HSC-like `prolif_UCell` < Mono-like `prolif_UCell`

**Rationale:** Van Galen 2019's core finding is that LSCs are quiescent. Committed monocytes (Mono-like) are proliferative. If pyUCell's rank-based R_prolif does not reproduce this, either the mechanism is wrong for our data or Van Galen's cell type labels have shifted meaning in pseudobulk. This is direct biological ground truth.

### Q_B — Axis Non-Redundancy
**Criterion:** Max pairwise |Pearson r| among (prolif, emt, ddr) UCell scores across 21 cell types < 0.9

**Rationale:** Relaxed threshold honoring Round 2.1d finding — prolif and DDR are biologically coupled in single-tissue AML (|r|=0.76 on BeatAML bulk, likely similar on Van Galen). Threshold 0.9 is a redundancy check (no axis fully derivable from another) not a strict orthogonality check. Documented as a single-tissue limitation, not a methodological failure.

### Q_C — BeatAML Drug Model Quality
**Criterion:** Mean CV-AUROC ≥ 0.55 across trained BeatAML drug models AND all three axes contribute (max|coefficient| > 0 for each axis across drugs with AUROC ≥ 0.60)

**Rationale:** Round 2.1d achieved 0.534 mean / 0.556 median AUROC with z-score axes. pyUCell rank-based axes should match or exceed this. The three-axis contribution check ensures no axis silently drops out. This is the substantive test of axis utility.

### Q_D — Cross-Dataset Biological Prediction
**Criterion:** Spearman correlation between Van Galen Prog-like per-drug P(sensitive) predictions and BeatAML FLT3-ITD+ minus FLT3-ITD- per-drug median AUC differential is negative (ρ < 0) with p < 0.05, across drugs with ≥5 samples in each ITD group.

**Rationale:** If Prog-like is biologically enriched for FLT3-ITD+ biology (per Van Galen 2019 Fig 5), then drugs predicted to be more potent against Prog-like (high P(sensitive)) should also be those that show greater potency (lower AUC) in FLT3-ITD+ patients. Negative Spearman is the expected direction from first principles: high P_sensitive → low AUC → negative correlation. Round 2.1d produced ρ = +0.403 (wrong sign with compressed predictions), indicating the biology was not being learned correctly. Round 2.2a must produce negative rho with significance or fail honestly. A positive significant correlation is a specific, diagnosable failure — the model is learning backwards — not a partial success.

### Q_E — Distinguishability
**Criterion:** Jaccard(HSC-like top 10 drugs, Prog-like top 10 drugs) < 0.6

**Rationale:** Same criterion as Round 2.1d. Different cell types must produce distinguishably different drug rankings. Round 2.1d produced Jaccard = 1.000 (complete collapse). Round 2.2 must produce distinct rankings or fail honestly.

### Q_F (DIAGNOSTIC — not a pass/fail gate)
**Measurement:** For each axis, compute the ratio of (Van Galen 21-cell-type range) / (BeatAML 707-sample range). Report all three ratios in the summary JSON. No threshold is applied.

**Why this is a diagnostic, not a gate:**
Pre-committing a threshold (50%, 70%, or any number) before seeing data is methodologically circular. Any threshold would be designed to match what we expect the mechanism to produce — the test becomes a rubber stamp for expectations rather than a falsifiable claim about the system.

The real test is the downstream biological claim: does the model predict correctly? That is Q_D. If Q_D passes with a narrow axis range, it means rank-order preservation under compression is sufficient for prediction — a real finding worth investigating. If Q_D fails with a wide axis range, the mechanism is broken despite good-looking axes. The proxy metric cannot substitute for the actual prediction test.

**What we do with the reported range ratios:**
1. Record in summary JSON for every round
2. Discuss in closure memo if unusual (very low or very high compared to expectation)
3. Let Round 2.2b (therapeutic index) naturally test whether narrow axes produce noisy selectivity predictions — that is the proper downstream test
4. Build up cross-round evidence: if Round 2.2a and Round 2.2b both pass with consistently compressed axes, that becomes scientifically interesting (possibly publishable as a methodology finding about rank-preservation under pseudobulk compression)

**Principled basis for demotion:** Measuring and documenting a metric is honest science. Gating on a pre-chosen threshold for that metric, when the threshold was picked to feel right rather than derived from theory or prior data, is manipulation dressed as rigor. Round 2.2a gates on biological claims, measures everything else, lets downstream rounds test what upstream diagnostics flag.

---

## 6. Pass/Fail Protocol

### All five pass (Q_A, Q_B, Q_C, Q_D, Q_E) → net saved
- Save `aml_net_round22a_ucell.gpickle` with Layer 2 integrated
- Save `kaalcura_ucell_state_round22a.pkl` (BeatAML drug models + reference)
- Save `beataml_ucell_axes_round22a.csv` (707 samples × 3 axes)
- Save `vangalen_celltype_ucell_axes_round22a.csv` (21 cell types × 3 axes)
- Q_F diagnostic (axis range ratios) included in summary JSON with discussion in closure memo
- Write closure memo `INTERCEPTA_Round2_2a_Closure.md` as successful-integration record with honest discussion of Q_F measurement

### Any of the five fail → no net saved, honest closure
- Graph NOT written to disk
- Diagnostic JSON written with all five query numbers AND Q_F measurement
- Closure memo documents exactly what failed, at what numbers, and why
- Identifies whether the failure is methodological (needs Round 2.2b) or biological (needs deeper net work)

**Principle 15 commitment:** I will not modify thresholds after seeing results. The thresholds in this spec are locked. If Q_D requires ρ < 0 and we get ρ = +0.0001 with p = 0.04, that is a FAIL — we do not invert to ρ < 0.1 to pass. Likewise Q_C at 0.55, Q_E at 0.6 Jaccard, Q_B at 0.9 |r|.

---

## 7. Expected Runtime and File Outputs

**Runtime budget:** 5-15 minutes total.
- BeatAML load + AnnData wrap + pyUCell: ~30 seconds (pyUCell is fast)
- Drug model training (160 drugs × 5-fold CV): ~1 minute
- Van Galen pseudobulk + pyUCell: ~15 seconds
- Drug prediction + validation queries: ~30 seconds
- Net integration and save: ~30 seconds

**Memory:** Peak ~3-5 GB (driven by BeatAML expression matrix + Van Galen AnnData).

**Output artifacts:**

| Path | Size est. | Purpose |
|------|-----------|---------|
| `results/aml_net_round22a_ucell.gpickle` | ~3 MB | Layer 2 integrated net (if all five pass) |
| `results/aml_net_round22a_summary.json` | ~15 KB | Structured verdict + all five query numbers + Q_F diagnostic |
| `results/aml_net_round22a_build.txt` | ~100 KB | Full run log |
| `results/beataml_ucell_axes_round22a.csv` | ~50 KB | 707 × 3 patient axes |
| `results/vangalen_celltype_ucell_axes_round22a.csv` | ~2 KB | 21 × 3 cell-type axes |
| `results/kaalcura_ucell_state_round22a.pkl` | ~2 MB | Trained model object |

---

## 8. Principle Audit — In Advance

| Principle | Applied in Round 2.2a as |
|-----------|-------------------------|
| P3 (research before code) | Done: pyUCell verified with synthetic test, max_rank empirically measured, BeatAML file format verified, clinical xlsx loading tested (openpyxl installed). Spec written before code. |
| P4 (fix structure, don't tune) | This round IS the structural fix for Round 2.1d's failure. Thresholds locked in this spec, not after seeing results. |
| P15 (honest validation) | Five queries with locked thresholds. Q_F demoted to diagnostic to avoid pre-committed threshold circularity. If any of the five fail, no net saved. No post-hoc threshold adjustment. |
| P16 (preserve past work) | `intercepta_kaalcura_v1.py` imported unchanged. Round 1 gene sets reused verbatim. Round 2.1d artifacts preserved as diagnostic baseline. |

**Amendment note on P15:** The Q_F demotion (from gate to diagnostic) is a pre-implementation design decision based on principled argument, not a post-implementation threshold relaxation. The original spec's Q_F=50% was itself a pre-committed threshold that would have constituted a Principle 15 violation if it had been designed to match expected mechanism output. Recognizing this circularity before code is itself the principle in action.

---

## 9. Git Commit Plan

### Commit A (this spec amendment, before code) ← THIS COMMIT
```
Round 2.2a specification amendment: Q_F demoted to diagnostic

Demotes the axis range query (Q_F) from pass/fail gate to reported
diagnostic metric. Pre-committing a threshold on an intermediate metric
would be circular (threshold designed to match expected mechanism
output). Five validation queries (Q_A-Q_E) remain as pass/fail gates
covering the actual biological claims. Q_F range ratios reported in
summary JSON for analysis but do not gate the round.

Principle 15 strengthened: gating on downstream biological claims,
measuring intermediate metrics as diagnostics, documenting honestly,
letting Round 2.2b test what upstream diagnostics flag.
```

### Commit B (after implementation, if all five pass)
```
Round 2.2a — Layer 2 integration validated via pyUCell cross-modality scoring

[stats from actual run, including Q_F diagnostic discussion]
```
Tag: `round2.2a-validated`

### Commit C (after implementation, if any fail)
```
Round 2.2a — honest findings: [specific query failures diagnosed]
```
Tag: `round2.2a-closed-[specific-finding]`

---

## 10. What This Specification Does NOT Cover

The following are explicitly out of scope for Round 2.2a:
- RNA velocity integration (deferred — requires 10X Chromium data, not in Van Galen)
- Therapeutic index computation against non-malignant cell types (deferred to Round 2.2b — this round focuses on proving the mechanism works cross-modality first)
- Novel molecule generation (Round 2.3+)
- Combination drug predictions (Round 2.2c+)
- Selectivity scoring against healthy cell types as a net integration feature (Round 2.2b scope)

**Why scope is tight:** Round 2.1d tried to do too much at once (per-cell-type + selectivity + drug prediction + cross-validation). Round 2.2a reduces scope to: "prove pyUCell scoring produces commensurable axes across modalities and useful drug predictions." If it passes, Round 2.2b extends to selectivity and therapeutic index and will also naturally test the downstream consequence of whatever Q_F diagnostic reveals.

---

## 11. Amendment Change Log

**v1 (commit 09da7fd):** Six validation queries including Q_F at 50% range threshold as pass/fail gate.

**v2 (THIS COMMIT):** Five pass/fail validation queries (Q_A through Q_E). Q_F demoted to diagnostic metric — reported in summary JSON, analyzed in closure memo, but does not gate the round. All other content unchanged.

**Basis for amendment:** Principal co-founder (Prasad) identified that pre-committed thresholds on intermediate metrics (axis range) are methodologically circular — any threshold would be chosen to match expected mechanism output. Gating on the downstream biological claim (Q_D: does the model predict correctly?) is the honest test. Diagnostic metrics are measured and documented but do not determine pass/fail. This amendment is consistent with Principle 15 (honest validation) and Principle 4 (fix structure, not threshold).

---

## 12. Review Checkpoint

This amended specification is the review checkpoint. Prasad reviews this amendment. Concerns, disagreements, further changes go into discussion before implementation begins. Once approved via commit, the spec becomes the contract.

If approved as-is, proceed to implementation. If changes requested, revise this document, recommit, then proceed.

*— Prasad Akula & Claude, Co-Founders of INTERCEPTA*
*April 22, 2026*
