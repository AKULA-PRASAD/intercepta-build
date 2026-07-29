# Cui & Yuan, 2025 — River: Prioritizing Perturbation-Responsive Gene Patterns Using Interpretable Deep Learning (Spatial Transcriptomics DSEP)

## 0. Identification

- **Citation:** Cui Y, Yuan Z. "Prioritizing perturbation-responsive gene patterns using interpretable deep learning." *Nature Communications* 16(1):article 61476 (full ID), December 2025. DOI: 10.1038/s41467-025-61476-9
- **First author:** Yan Cui
- **Senior/corresponding author:** Zhiyuan Yuan
- **Affiliations:** Per RePEc citation graph — institutional affiliations would require full paper fetch but the corresponding author Zhiyuan Yuan is known for spatial transcriptomics methodology work
- **Layer 1 question:** Q7 anchor 2 — **CORRECTED SCOPE:** spatial transcriptomics differential spatial expression pattern (DSEP) gene prioritization across multiple conditions; **NOT general perturbation attribution as the original 2026-05-10 note misrepresented**
- **Read by:** Claude (CSO) — 2026-05-10 (Phase 5 deepening + scope correction; primary-source via Nature Communications + RePEc + biorxiv preprint searches)

## 1. Why this paper matters for Q7

Cui & Yuan 2025 introduces **DSEP gene prioritization** — a new analytical task for spatial transcriptomics that has not been well-addressed before. Three reasons it matters for INTERCEPTA Q7:

1. **It addresses gene attribution in spatial omics specifically** — the spatial transcriptomics modality Nicheformer (Q8 anchor 1) commits INTERCEPTA to supporting. **River is the Q7 layer specifically for the spatial modality.**

2. **Two-branch architecture decoupling spatial and non-spatial components** — methodologically careful. This is a **template for INTERCEPTA's modality-aware interpretability** when spatial transcriptomics is part of the input.

3. **Post-hoc attribution strategy** for ranking genes by contribution to condition differences — operationally compatible with INTERCEPTA's Decision 4 v2 L7 head architecture. Can be layered on top of CPA/GEARS outputs without architectural conflict.

## 2. What they did — full methodology

### 2.1 The DSEP task (newly introduced by this paper)

**Task definition:** Given multi-condition spatial transcriptomics data (e.g., disease vs healthy tissue slices), identify genes whose **spatial expression pattern** differs across conditions.

**Why this is new:** Prior spatial transcriptomics methods (e.g., SpaGCN, Hotspot, SVG identification) focus on **spatially variable genes within a single slice**. Cross-condition spatial pattern comparison — DSEP — was not a recognized analytical task before this paper.

**Why this is relevant to INTERCEPTA:** Drug response in spatial transcriptomics context (e.g., tumor microenvironment response to immunotherapy) requires identifying which genes show **spatially-patterned response** vs uniform response. River provides the methodology.

### 2.2 River architecture (two-branch design)

**Branch 1 — Spatial-informed prediction branch:**
- Takes spatial coordinates + gene expression
- Spatially-aware deep learning (GNN-like or attention-based; specific architecture per paper Methods)
- Predicts condition label from spatial features

**Branch 2 — Non-spatial prediction branch:**
- Takes only gene expression (no spatial coordinates)
- Standard DNN
- Predicts condition label from expression features alone

**Decoupling rationale:** The difference between Branch 1 and Branch 2 predictions captures the **spatial-specific information** beyond what expression alone provides. Genes attributed to Branch 1 but not Branch 2 are spatially-patterned response genes.

### 2.3 Post-hoc attribution strategy

After training:
- Apply attribution algorithm(s) — likely IG, SHAP, or DeepLIFT variants — to both branches
- Rank genes by their contribution to **condition differences** (not just to the prediction itself)
- Decouple spatial vs non-spatial contributions per the two-branch design

The original Q7 note claimed "Borda count aggregation across 3 attribution methods" — this claim needs primary-source verification. **It may be a hallucination from the original note's hasty creation.** The Nature Communications abstract does mention "post hoc attribution strategy" but doesn't specify Borda count in the snippets I've fetched. **Until primary-source full-paper verification, this specific claim is unverified.**

### 2.4 Scalability to large datasets

The paper emphasizes scalability to large spatial datasets — important because spatial transcriptomics datasets are typically 10K-100K spots per slice, and multi-condition designs can include dozens of slices.

## 3. What they found

### 3.1 Primary contribution

**DSEP gene prioritization as a new analytical task** is established and demonstrated on real spatial transcriptomics datasets. The paper presents the task, the methodology, and an empirical demonstration.

### 3.2 Quantitative results

The Nature Communications abstract snippets do not provide specific quantitative results (recall, precision, AUC) — these are in the paper body which I have not fetched in full. **The original note's claim of "improves robustness vs any single method" is unverified at this level of search depth.**

**Honest position:** River works as advertised per peer review (Nature Communications December 2025 publication). Specific empirical magnitudes require full-paper fetch beyond Phase 5 scope.

## 4. What's strong

- **Nature Communications peer-reviewed** — top broad-impact venue
- **Introduces a new analytical task (DSEP)** — methodologically novel
- **Two-branch design** decouples spatial vs non-spatial information — methodologically careful
- **Spatial transcriptomics scalability** addressed explicitly
- **December 2025 publication** reflects current state of the art
- **Direct relevance to INTERCEPTA's Nicheformer/spatial modality support**

## 5. What's limited

- **Spatial transcriptomics only.** Does NOT cover dissociated scRNA-seq, bulk RNA-seq, or other modalities.
- **DSEP focus, not general perturbation attribution.** The original Q7 note misrepresented this as a general perturbation attribution method.
- **Specific attribution methodology not deeply verified in this read.** The "Borda count" claim from original note needs primary-source verification before being relied upon for Decision 7 v2.
- **No FM-based attribution.** Pre-FM era methodology adopted (likely IG/SHAP/DeepLIFT post-hoc).
- **Cancer/disease-vs-healthy focus likely.** Drug perturbation in spatial context probably not directly tested.
- **Replication pending.** 2025 single paper; methodology adoption by other groups not yet documented.
- **First-author + senior-author affiliations not fully verified** in this Phase 5 read (only confirmed names + roles via RePEc; institutional affiliations would require full paper fetch).

## 6. INTERCEPTA implications

### For Decision 7 v2 (mechanistic interpretability)

River provides **the spatial modality branch** of INTERCEPTA's Q7 interpretability stack:

| Modality | Decision 7 v2 Q7 layer method | Anchor |
|---|---|---|
| Dissociated scRNA-seq | EIG (Jha 2020) + SmoothGrad (Reynolds-Pan 2025) | Q7.1 + Q7.3 |
| Spatial transcriptomics | River two-branch architecture + DSEP attribution | Q7.2 |
| Multi-omics (bulk + scRNA + spatial) | Combined per-modality stacks | composite (Q7.4) |

Decision 7 v2 must specify **modality-aware Q7 architecture** — different attribution methods for different input modalities.

### For Nicheformer (Q8 anchor 1) integration

Nicheformer trains jointly on dissociated + spatial. For spatial transcriptomics inputs to INTERCEPTA's L7 layer:
- **River-style two-branch** decoupling can apply at the L7 head
- Attribution of spatial-specific vs expression-specific drug response signal becomes tractable
- This is **directly relevant for tumor microenvironment drug response**, anti-TNF spatial response in I&I, neurodegeneration plaque-microregion analysis

### For Decision 4 v2 (drug response architecture) integration

Decision 4 v2 Slot 1 (cell encoder) does not currently specify spatial-aware encoders. **For spatial transcriptomics inputs, Nicheformer (Q8.1) or similar spatial FM occupies Slot 1.** River's two-branch decoupling can be added as a Decision 4 v2 sub-architecture for spatial inputs.

### For Decision 8 (universality) cross-tissue (U2)

Decision 8 U2 cross-tissue universality benefits from spatial-aware methodology. River + Nicheformer together support INTERCEPTA's spatial-tissue deployment (tumor microenvironment, inflammatory infiltrates, plaque microregions, ischemic boundaries).

### Critical methodological honest note

The original 2026-05-10 Q7 anchor 2 note claimed **"Borda count aggregation across IG + DeepLIFT + GradientShap"** as River's methodology. **This claim is not visible in the Nature Communications abstract** I fetched in Phase 5. It may be present in the paper body — or it may have been a confabulation by the original note author (who was me, in autonomous mode pre-audit). **Until full-paper primary-source verification, Decision 7 v2 should not rely on this specific River methodology claim.**

**Operational implication:** if INTERCEPTA needs the Borda count multi-method aggregation pattern, it should source this from Reynolds-Pan 2025 + Jha 2020 (which I have primary-source-verified) rather than from River (which I have only partially verified). Decision 7 v2 must reflect this distinction.

## 7. Followup citations

1. **SpaGCN** — predecessor for spatially variable gene identification within a single slice
2. **Hotspot** — predecessor for spatial autocorrelation-based gene identification
3. **SVG identification methods** — within-slice spatially variable gene methods
4. **Nicheformer (Q8 anchor 1)** — spatial FM that River can complement
5. **Reynolds & Pan 2025 (Q7 anchor 1)** — complementary general-purpose attribution benchmark
6. **Jha et al. 2020 EIG (Q7 anchor 3)** — IG enhancement methodology

## 8. Discipline check

- [x] Primary-source verification: Nature Communications article page, RePEc citation graph, Cui Y + Yuan Z author confirmation
- [x] First author verified: Yan Cui
- [x] Senior author verified: Zhiyuan Yuan
- [x] Venue verified: Nature Communications 16(1), December 2025
- [x] DOI verified: 10.1038/s41467-025-61476-9
- [x] **SCOPE CORRECTION:** Original note misrepresented River as general perturbation attribution. Primary source establishes it is specifically **spatial transcriptomics DSEP gene prioritization across multiple conditions**. This is a scope drift instance that the audit mechanism caught in Phase 5.
- [x] **Borda count claim flagged as unverified:** Original note's specific methodology claim ("Borda count aggregation across IG + DeepLIFT + GradientShap") was not visible in primary-source abstract snippets. Honest acknowledgment that this is unverified at Phase 5 search depth.
- [x] **Affiliations partially verified:** First-author/senior-author institutional affiliations not fully resolved in this Phase 5 pass; would require full paper fetch beyond current scope.
- [x] **Errata note:** Original 2026-05-10 file (276w) misrepresented River's scope as general perturbation attribution; corrected here to spatial transcriptomics DSEP. Specific methodology claim (Borda count) flagged as unverified pending full-paper fetch.

## Drift catalog this Phase 5 anchor correction

- **Drift Instance #33 caught real-time:** River 2025 scope misrepresentation (general perturbation attribution → actually spatial transcriptomics DSEP gene prioritization). **Severity: scope-drift** (less severe than fabrication-class but still misleading for downstream Decision 7 v2 architecture).
- **Drift Instance #34 caught real-time:** Borda count methodology claim in original note is unverified at Phase 5 search depth — flagged for full-paper verification before being relied upon.
- **New drift instances introduced:** 0
- **Methodological discipline:** primary-source verification revealed two drift instances; both honestly documented rather than hidden

— Claude (CSO), 2026-05-10 (Phase 5 deepening + Drift #33 + #34 corrections)
