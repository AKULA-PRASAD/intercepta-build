# INTERCEPTA Round 2.2c — Specification

**Disease:** Acute Myeloid Leukemia (AML)
**Datasets:** BeatAML 2.0 (520 RNA × drug aligned samples, 85 drugs after 10/10 filter), Van Galen 2019 (21 cell types)
**Author:** Prasad Akula & Claude (CSO), Co-Founders of INTERCEPTA
**Date:** 2026-05-06
**Status:** LOCKED before code is written. Per Round 2 discipline (P3 — research before code).
**Direction:** Option γ (per Round 2 closure post-triangulation analysis). KAALCURA is reframed from standalone predictor to one feature among many in a multi-modal model.

---

## 1. Why this round exists

Round 2 closed with Q_C FAIL: KAALCURA 3-axis mean AUROC = 0.526 on within-dataset BeatAML drug sensitivity prediction, three methods, three rounds, same ceiling.

Triangulation experiments (2026-05-06) measured directly on the same data, same task:

| Configuration | Mean AUROC (n drugs) |
|---|---:|
| KAALCURA-3-axis + LogisticRegression (Round 2.2b) | 0.526 (141) |
| KAALCURA-3-axis + LightGBM | 0.532 (85) |
| RNA-1000 + LightGBM (sex confound, 20/20 filter) | 0.670 (56) |
| **RNA-1000 + LightGBM (sex-filtered, 10/10 filter)** | **0.645 (85)** |

The model effect (LightGBM vs LogReg on same 3 features) is +0.006 — essentially zero. The feature gap (KAALCURA 3 axes vs RNA-1000 raw genes, both LightGBM) is +0.113 mean AUROC.

**The gap is in features, not model.** KAALCURA-3-axis encodes ~17% of the within-dataset signal that the top-1000 most variable BeatAML genes carry. The remaining 83% lives outside the curated proliferation/EMT/DDR sets and is recoverable by a tree-based model on raw expression.

**Conclusion:** KAALCURA-as-standalone-predictor is structurally insufficient. KAALCURA-as-feature-among-many is the honest framing.

Round 2.2c builds the multi-modal predictor that KAALCURA should always have been a component of, and tests it against thresholds set from measured baselines.

---

## 2. Hypothesis (locked, falsifiable)

**H1 (primary):** A multi-modal LightGBM predictor that combines [KAALCURA 3 axes + RNA-1000-no-sex + AML mutation status + pathway activity scores + drug-target features] achieves mean CV-AUROC ≥ 0.70 on BeatAML 85-drug panel (10/10 filter, AUC=100 binarization).

**H2 (KAALCURA contribution, secondary but locked):** KAALCURA features measurably contribute to the predictor's performance, defined as either (a) at least one KAALCURA axis appears in top-20 LightGBM feature importance, OR (b) ablating KAALCURA features drops mean AUROC by ≥ 0.005.

**H3 (cross-dataset preservation, locked):** Cross-dataset Prog-FLT3 correlation (Round 2.2b's Q_D PASS at ρ=−0.271, p=0.00125) does not regress under the multi-modal architecture. Specifically, on the multi-modal predictor's KAALCURA-attributable component, cross-dataset Spearman correlation must remain |ρ| ≥ 0.20 with p < 0.01.

**Falsification:**
- If H1 fails (mean AUROC < 0.70): the multi-modal architecture does not surpass RNA-only baseline meaningfully. We accept that and document.
- If H2 fails: KAALCURA contributes nothing measurable on top of RNA features. We accept that and document — the within-dataset role of KAALCURA is then formally retired, with KAALCURA continuing only in cross-dataset and cell-type-specific contexts.
- If H3 fails: the cross-dataset transfer that was Round 2's strongest signal does not survive the multi-modal architecture. We accept that and report.

**No threshold tuning post-hoc.** All thresholds in this section are LOCKED before code.

---

## 3. Five locked validation gates

### Q_C — Within-dataset utility (the originally-failing gate)

**Threshold:** mean CV-AUROC ≥ **0.70** across all evaluated drugs.
**Secondary requirement:** at least 60% of drugs (51/85 if filter holds) achieve AUROC ≥ 0.65.

**Rationale:** RNA-only LightGBM baseline (v2, sex-filtered, 10/10) achieved mean 0.645. The multi-modal predictor must clearly exceed this — 0.70 represents a +0.055 improvement, large enough that it would be detectable above noise (RNA-only std = 0.105 across drugs).

**Why not higher (e.g., 0.75 or 0.80):** The Tercan 2026 PLOS One paper notes that state-of-art classifiers on this exact task "tended to assign all samples to one of the classes in most cases" on external validation. Multi-omics regression methods (MO 2022) achieve R² ~0.12. The honest published ceiling for this task is around 0.70-0.75 mean AUROC. Setting Q_C at 0.70 puts INTERCEPTA at competitive-with-state-of-art — not a fake threshold tuned to pass.

**Why not lower (e.g., 0.65):** A 0.65 threshold would put us at parity with RNA-only baseline. That is not a meaningful contribution. We should beat baseline, not match it.

**FAIL behavior:** Round 2.2c fails Q_C. Predictor still ships if H2 (KAALCURA contribution) and H3 (cross-dataset) pass. Round 2 fully closes with documented within-dataset ceiling. Workstream B proceeds with multi-modal-but-modest-AUROC predictor.

### Q_C2 — Class imbalance robustness

**Threshold:** balanced accuracy (mean of sensitivity and specificity) ≥ **0.65** across drugs.

**Rationale:** Tercan 2026 explicitly noted that AUROC alone can hide class-imbalance failures (state-of-art classifiers collapsing to majority class but still achieving moderate AUROC). Balanced accuracy stresses minority-class performance. This gate guards against the failure mode Tercan documented.

### Q_D — Cross-dataset preservation (KAALCURA's actual strength)

**Threshold:** the multi-modal predictor's KAALCURA-attributable component (computed via SHAP value attribution to KAALCURA features) maintains Spearman ρ ≥ 0.20 with p < 0.01 between predicted Prog-like-cell drug response and observed Van Galen Prog-like R_prolif scores, on the 139-drug alignment set used in Round 2.2b.

**Rationale:** This is the directly-locked successor to Round 2.2b's Q_D PASS (ρ=−0.271, p=0.00125). The threshold is relaxed slightly (|ρ| ≥ 0.20 vs 0.27) because we cannot guarantee that adding RNA features preserves the exact magnitude — but the direction and statistical significance must hold.

**Comparator biology verification (mandatory per Round 2.2a Q_A lesson):** The Prog-like population in Van Galen 2019 has been verified as a cycling LSPC population (Zeng et al. 2022 refines it as "cycling LSPCs"; Van Galen 2019 identifies it as proliferating committed progenitor). FLT3-targeting drugs preferentially affect proliferating leukemic cells. Therefore the expected sign of correlation (negative — high R_prolif coefficient = sensitive to FLT3 inhibitors = low IC50/AUC = predicted positive direction in our binarization) is biologically grounded, not data-fitted.

### Q_E — KAALCURA contribution (the H2 gate, locked)

**Threshold:** at least ONE of the following must be true:
- (a) At least one KAALCURA feature (R_prolif, R_emt, or R_ddr) appears in top-20 LightGBM `gain` feature importance for ≥ 50% of drugs (≥ 43 of 85).
- (b) Leave-KAALCURA-out ablation: training the same LightGBM on [RNA-1000 + mutation + pathway + drug-target] WITHOUT the 3 KAALCURA features drops mean AUROC by ≥ 0.005.

**Rationale:** This is the honest test of whether KAALCURA features add anything on top of RNA-1000 + other features. If neither (a) nor (b) hold, KAALCURA is decorative — and we report that honestly.

**FAIL behavior:** Round 2.2c reports KAALCURA's within-dataset contribution as null. KAALCURA's role in the project narrows to cross-dataset (Q_D) and cell-type (Q_F) only. The vision document Module 1 framing is amended to reflect this finding.

### Q_F — Cell-type distinguishability (the Round 2.2b Q_E successor)

**Threshold:** Top-10 drug ranking (by predicted P(sensitive) for HSC-like vs Prog-like cell-type contexts) achieves Jaccard overlap ≤ **0.4**.

**Rationale:** Round 2.2b achieved Jaccard 0.25 (PASS at threshold 0.6). Threshold tightened to 0.4 because we expect multi-modal features to maintain or improve cell-type-specific drug ranking.

**Methodology:** Multi-modal predictor scored on (HSC-like-mean-axes ⊕ HSC-like-RNA-context-features) vs (Prog-like-mean-axes ⊕ Prog-like-RNA-context-features). Cell-type-context RNA features come from Van Galen 2019 cell-type pseudobulk averages.

**Open question for code:** how to construct cell-type "RNA context" features when RNA features were trained on bulk BeatAML. Implementation must address this; spec mandates a defensible method (e.g., Van Galen pseudobulks projected through the LightGBM feature space, or per-cell-type mean expression mapped to the BeatAML feature names).

### Q_G — No overfitting

**Threshold:** train AUROC vs test AUROC mean gap ≤ **0.10** across drugs (i.e., overfitting bounded).

**Rationale:** With ~1020+ features and ~520 samples, overfitting is a real risk. LightGBM defaults are reasonably robust, but this gate makes the check explicit and locked.

**Methodology:** report `train_auroc - test_auroc` per fold per drug. Mean across folds and drugs must be ≤ 0.10.

---

## 4. Q_F-style diagnostic metrics (NOT pass/fail, per Round 2.2a lesson)

Reported alongside the gates, used for understanding, NOT as gates:

- **Per-feature-class AUROC contribution.** SHAP-based attribution of total AUROC to (KAALCURA, RNA-1000, mutation, pathway, drug-target). Tells us where the signal is.
- **Drug-class subgroup AUROC.** AUROC averaged within drug classes (FLT3 inhibitors, BCL2 inhibitors, kinase inhibitors, chemotherapeutics, etc.). Tells us if certain mechanism classes work better than others.
- **Per-drug feature importance heatmap.** Top 5 features per drug. Tells us interpretability.

These are durable artifacts. None of them is a pass/fail gate. Per Round 2.2a's Q_F lesson: pre-committing thresholds on diagnostics is methodologically circular.

---

## 5. Multi-modal feature stack (locked schema)

For each (sample, drug) pair, the feature vector is:

| Feature group | Dimension | Source | Locked specification |
|---|---:|---|---|
| KAALCURA axes | 3 | `beataml_ucell_residual_axes_round22b.csv` | R_prolif, R_emt, R_ddr (residualized per Round 2.2b) |
| RNA-1000-no-sex | 1000 | `beataml_waves1to4_norm_exp_dbgap.txt` | Top-1000 most variable genes AFTER chrX/chrY filter (per `compute_rna_baseline_v2.py` selection) |
| Mutation status | 15 | `beataml_wes_wv1to4_mutations_dbgap.txt` + clinical FLT3-ITD column | Binary indicators for: FLT3, NPM1, DNMT3A, IDH1, IDH2, RUNX1, CEBPA, TET2, TP53, ASXL1, KIT, KMT2A, RAS family (NRAS+KRAS combined), WT1, FLT3-ITD (separate from FLT3 SNV) |
| Pathway activity | ~10-15 | KEGG `step5_gene_pathway_map.csv` + BeatAML expression | Activity score per pathway = mean expression of pathway member genes. Pathways: AML (hsa05221), Cell cycle (hsa04110), Apoptosis (hsa04210), JAK-STAT (hsa04630), PI3K-Akt (hsa04151), MAPK (hsa04010), Wnt (hsa04310), DNA repair (hsa03430+03450+03440), p53 (hsa04115), Hematopoietic differentiation (hsa04640), and 5 more disease-relevant ones to be selected from KEGG enrichment of BeatAML mutated genes |
| Drug-target features | 4 | ChEMBL annotation (`step1_complete_gene_drug_net.csv`) | (1) Drug's primary target = AML-mutated gene? binary, (2) Drug pchembl on its primary target (continuous), (3) Drug's target in AML pathway? binary, (4) n_targets for the drug |

**Total feature count:** ~1032-1037 features per (sample, drug).
**n samples after alignment:** 520 (BeatAML RNA × drug response intersection).
**n drugs in train/test pool:** 85 (10/10 filter, matches RNA baseline v2).

---

## 6. Implementation requirements (binding)

These are not suggestions. They are spec.

1. **Random state = 42 throughout.** Matches all prior INTERCEPTA work for reproducibility.

2. **5-fold StratifiedKFold per drug, same as Round 2.2b and baselines.** No leakage between folds. No drug-specific tuning.

3. **LightGBM defaults — no hyperparameter tuning.** Baselines used `n_estimators=100, learning_rate=0.1, num_leaves=31`. Round 2.2c keeps these. Tuning would invite per-drug overfitting and is forbidden by spec.

4. **Categorical features handled correctly.** Mutation status binary. Pathway scores continuous (z-scored within BeatAML training set). Drug-target binary/continuous mix.

5. **No data leakage.** Pathway activity scores computed on training fold only; test fold pathway scores use training-fold means and stds. Same for any normalization.

6. **Fail closed.** If any feature class fails to load (e.g., mutation file unavailable), the run aborts with explicit error. No silent feature dropping.

7. **All metrics reported as mean ± std across the 5 folds.** No selective reporting.

8. **Output schema (committed alongside results):**
   - `multimodal_predictor_per_drug.csv` — drug, n_samples, n_sensitive, n_resistant, auroc_mean, auroc_std, balanced_acc, train_test_gap
   - `multimodal_predictor_summary.json` — gate verdicts (Q_C, Q_C2, Q_D, Q_E, Q_F, Q_G), aggregate stats, comparator deltas vs baselines
   - `multimodal_feature_importance.csv` — per-drug top-30 features by gain importance
   - `multimodal_shap_summary.csv` — per-feature-class mean absolute SHAP contribution
   - `kaalcura_ablation_results.json` — leave-KAALCURA-out comparison (for Q_E)

---

## 7. What this round will NOT do

To prevent scope creep, locked exclusions:

- **No drug-class-specific models.** One LightGBM per drug, same hyperparameters, no per-drug tuning.
- **No SMOTE / class-balancing.** Keep imbalance honest. Q_C2 gate measures balanced accuracy, which is the correct way to handle this.
- **No deep learning.** LightGBM is sufficient and fast on Mac CPU. Neural models would be slower, harder to interpret, and not justified by the task scale.
- **No external dataset training.** BeatAML waves 1-4 is the training source. Van Galen used only for cross-dataset validation (Q_D, Q_F).
- **No therapeutic index test.** Selectivity vs healthy comparators stays deferred. Round 2.2d or later.
- **No ODE coupling.** Multi-modal predictor produces P(sensitive) per (sample, drug). ODE integration is Workstream B.
- **No new data acquisition.** All features come from data already on disk.

---

## 8. Comparator biology verification (mandatory per Round 2.2a Q_A lesson)

Every gate that compares biological entities must pre-cite primary-source biology:

**Q_D (Prog-like vs FLT3 inhibitors):** Prog-like = cycling leukemic stem-progenitor cells (Van Galen 2019; refined Zeng 2022). FLT3 inhibitors target proliferating leukemic cells. Negative correlation between predicted FLT3 inhibitor coefficient and Prog-like R_prolif is the biologically expected direction.

**Q_F (HSC-like vs Prog-like distinguishability):** HSC-like = quiescent leukemic stem cell-like population (Van Galen 2019: HSC-like cells show low cycling markers, high stemness signatures; round 2.2b Q_A confirmed: HSC-like R_prolif=0.576 < Prog-like R_prolif=0.823, margin 0.247). Different biology → different drug profiles is the biologically expected direction.

**Q_E (KAALCURA contribution):** This is a methodological gate, not a biological comparator. No biology verification required.

---

## 9. Principle audit (in advance)

| Principle | Applied as |
|---|---|
| P3 (research before code) | Spec written and committed before code. Triangulation experiments (RNA-baseline-v1, RNA-baseline-v2, KAALCURA-LightGBM) ran before this spec to set thresholds against measured numbers, not citations. The MDREAM-citation error of 2026-05-06 morning is documented in the closure erratum. |
| P4 (fix structure, don't tune) | The 0.526 → ~0.70 jump targeted by Round 2.2c is structural (multi-modal architecture), not parameter tuning. LightGBM hyperparameters held at defaults. Q_C threshold = 0.70 set against measured RNA-only baseline 0.645, not chosen to be just above what KAALCURA-multi might achieve. |
| P15 (only correct, honest, real science) | Threshold set from measured baselines this session. KAALCURA contribution gate (Q_E) explicitly tests whether KAALCURA contributes anything — accepts a NULL finding as a valid outcome. Cross-dataset gate (Q_D) preserves Round 2.2b's proven signal direction. No goalpost moving. |
| P16 (preserve past work) | Round 2.2b residualized axes used as feature input. KAALCURA module v1 unchanged. Round 2 closure (committed 2026-05-06) stands as historical record; this spec does not modify it. RNA baseline v2 + KAALCURA-LightGBM scripts remain durable measurement artifacts. |

---

## 10. Why this is the honest path

Round 2.2c could have been written as α (just add features and hope KAALCURA contributes) without the triangulation experiments. The triangulation showed KAALCURA-LightGBM ≈ KAALCURA-LogReg. That data eliminated α as a viable framing.

Round 2.2c could have been written as β (redirect to cross-dataset only, drop within-dataset) without the RNA baseline. The RNA baseline showed within-dataset prediction IS achievable at 0.645. Dropping the within-dataset goal would have papered over a real capability gap.

γ (multi-modal predictor with KAALCURA as feature) is the only path that respects all measured data:
- RNA carries within-dataset signal (we add it)
- KAALCURA carries cross-dataset and cell-type signal (we keep it, and test its contribution honestly)
- Multi-modal combination has not been measured (this round measures it)

This is what "P3 research before code" applied at the SPEC level looks like: the spec itself is built on measurement, not citation, not assumption, not hope.

---

## 11. Round 2.2c entry conditions (must hold before any code)

Before any line of Round 2.2c code is written:

- [x] Round 2 closure committed and tagged (`round2-closed`, 2026-05-06)
- [x] Round 2 closure erratum committed and tagged (`round2-closure-erratum`, 2026-05-06)
- [x] RNA baseline v1 measured: 0.670 over 56 drugs (sex confound flagged)
- [x] RNA baseline v2 measured: 0.645 over 85 drugs (sex-filtered, 10/10)
- [x] KAALCURA-LightGBM baseline measured: 0.532 over 85 drugs
- [x] Triangulation interpretation written into Round 2 closure narrative (this spec section 1)
- [ ] This spec committed and tagged `round2-2c-spec-locked`
- [ ] Round 2.2c implementation begins after spec is locked

Last item is the gate between this spec and the implementation. No code starts until the tag exists.

---

## 12. Round 2.2c exit conditions

Round 2.2c closes when:

1. All 6 gates (Q_C, Q_C2, Q_D, Q_E, Q_F, Q_G) have a recorded PASS or FAIL with all required artifacts saved.
2. Round 2.2c closure document written, modeled on Round 2 closure format, with explicit per-gate verdict.
3. If H1 passes (Q_C ≥ 0.70): tag `round2-2c-passed`. Workstream B begins on the multi-modal predictor as sensitivity input.
4. If H1 fails: tag `round2-2c-failed-honestly`. Workstream B begins anyway, using the multi-modal predictor at whatever AUROC it achieved, with documented limits.
5. If H2 fails (KAALCURA contributes nothing measurable): vision document Module 1 amendment written in subsequent session.
6. If H3 fails: cross-dataset claim retired honestly; Round 2 publishable signal narrows.

There is no "Round 2.2d" planned. Round 2.2c is the last sub-round of Round 2. After 2.2c closes (PASS or FAIL), Round 2 is fully closed and we move to Round 3 (Workstream B with NSCLC ODE generalization).

---

## 13. Effort estimate

- Spec (this document): ~1 session — DONE
- Code implementation: ~3-5 sessions
- Run + verify: ~1-2 sessions
- Closure document: ~1 session

Total: ~6-9 sessions to Round 2.2c closure. Approximately 2-4 weeks elapsed at moderate pace.

CPU only. Mac. No HPC needed for this round.

---

*Spec written before code. Thresholds set against measured baselines. Honest call on KAALCURA's actual role.*

— Prasad Akula & Claude (CSO)
2026-05-06
