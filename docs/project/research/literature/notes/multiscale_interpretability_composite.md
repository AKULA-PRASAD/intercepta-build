# Multi-Scale Interpretability Composite Anchor — SHAP + DeepStrataAge + Cross-Q Integration (Q7 Anchor 4)

## 0. Identification (Composite Anchor)

This is a **composite anchor** integrating multiple sources rather than a single primary paper. Its function is to bridge Q7 to Decisions 1 v2, 3, 4 v2, 5 v2, 6 v2 — providing the integration scaffold for INTERCEPTA's multi-scale interpretability stack.

### Component sources verified

**Source 1 — DeepStrataAge (npj Aging 2026):**
- **Citation:** *npj Aging* 2026, DOI 10.1038/s41514-026-00358-w
- **SHAP-based interpretable deep learning** applied to ~12,000 CpG methylation features
- Reveals age-influential epigenetic "waves" (early-life, midlife, late-life modules)
- Individual-level attribution capability validated

**Source 2 — Cross-Q decision references (already verified in their respective questions):**
- **Kendiukhov 2026 (Q1 anchor):** spectral geometry interpretability of FMs
- **GEARS Roohani 2024 (Q4 anchor 5, Q4 anchor in Decision 4 v2 Slot 4):** graph-based mechanism trace via gene-gene + GO ontology
- **scRank (Q3 anchor 4):** GRN-perturbation propagation for cell-type-specific drug-target mechanism
- **CPA Lotfollahi 2023 (Q4 anchor 4):** disentangled drug embeddings enable drug-similarity / MoA inference

**Source 3 — SHAP foundational framework:**
- **Lundberg & Lee 2017** — "A Unified Approach to Interpreting Model Predictions," NeurIPS 2017
- Shapley value framework with game-theoretic foundation
- Unifies DeepLIFT, IG, LIME under one theoretical umbrella

### Composite scope rationale

Per the original 2026-05-10 note: "Q7 interpretability is **deeply integrated with prior decisions** — GEARS provides graph-based mechanism, scRank provides GRN trace, CPA provides disentangled drug embeddings, Kendiukhov provides spectral geometry. Reading SHAP context completes the picture without re-anchoring on already-covered methods."

This composite-anchor approach **avoids duplicate anchoring** of methods already verified in other questions, while providing the structural integration Decision 7 v2 needs.

## 1. Why this composite matters for Q7

Q7 mechanistic interpretability is **inherently multi-scale**:
- **Geometric scale:** what does the latent representation space look like? (Kendiukhov spectral geometry — Q1)
- **Drug scale:** which drug embedding is similar to which? (CPA disentangled embeddings — Q4)
- **Pathway scale:** which biological pathways drive predictions? (GEARS GO graph + Beyondcell BCS — Q3, Q4)
- **GRN scale:** which transcription-factor-target relationships matter? (scRank — Q3)
- **Gene scale:** which individual genes drive predictions? (IG+SmoothGrad per Reynolds-Pan + EIG significance per Jha — Q7)
- **Spatial scale:** which spatial patterns differ across conditions? (River DSEP — Q7)
- **Patient/sample scale:** which patient features drive individual predictions? (SHAP individual-level attribution — this composite)

**No single anchor covers all scales.** Decision 7 v2 must specify a multi-scale stack that draws from multiple anchors.

## 2. SHAP — the universal attribution baseline

### 2.1 Shapley value foundation (Lundberg & Lee 2017)

**Game-theoretic framework:** for prediction f(x), attribute marginal contributions of each feature i across all possible feature subsets S, weighted by S's size.

φ_i = Σ_{S ⊆ N\{i}} [|S|!(|N|-|S|-1)!/|N|!] × [f(S ∪ {i}) - f(S)]

**Theoretical properties:**
- **Efficiency:** Σ φ_i = f(x) - f(baseline)
- **Symmetry:** equivalent features get equal attribution
- **Linearity:** attribution of linear combinations decomposes linearly
- **Null player:** features with no effect get zero attribution

### 2.2 SHAP variants relevant to INTERCEPTA

**DeepSHAP / Deep Explainer:** combines DeepLIFT with Shapley framework
- Per Reynolds-Pan 2025 (Q7 anchor 1), Gradient SHAP + SmoothGrad achieves precision ~0.68 at top 3% threshold
- **Operationally feasible for INTERCEPTA's L7 head architecture**

**KernelSHAP:** model-agnostic; expensive but architecture-independent
- Useful for cross-paradigm comparison (e.g., comparing FM-substrate attribution vs parameter-free substrate attribution per Decision 1 v2)

**TreeSHAP:** for tree-based models
- Not directly applicable to INTERCEPTA's neural architecture

### 2.3 DeepStrataAge as application example

DeepStrataAge (npj Aging 2026) demonstrates SHAP **at the individual sample level** for epigenetic age prediction:
- ~12,000 CpG methylation features per individual
- SHAP values per CpG per individual
- Cluster individuals by SHAP attribution patterns → reveals **age-influential epigenetic waves** (early-life, midlife, late-life modules)
- **Individual-level attribution enables personalized mechanism interpretation**

**For INTERCEPTA:** SHAP-style individual-level attribution provides **patient-specific drug response mechanism** — which genes drive THIS patient's predicted response to THIS drug. This is the **clinical interpretation layer** Decision 7 v2 requires for clinical adoption.

## 3. The multi-scale Q7 stack for INTERCEPTA Decision 7 v2

### 3.1 Five-scale interpretability architecture

| Scale | Method | Primary Anchor(s) | Decision Family | Substrate-Dependence |
|---|---|---|---|---|
| **Geometric** | Kendiukhov spectral analysis | Q1 (Kendiukhov) | Decision 1 v2 | FM-specific |
| **Drug-class** | CPA disentangled embeddings | Q4 (CPA, chemCPA) | Decision 4 v2 | Substrate-agnostic |
| **Pathway** | GEARS GO graph + Beyondcell BCS | Q3, Q4 (GEARS, Beyondcell) | Decision 4 v2 Slot 4 | Substrate-agnostic |
| **GRN/Cell-type** | scRank perturbation propagation | Q3 (scRank) | Decision 3 | Substrate-agnostic |
| **Gene-level** | IG+SmoothGrad EIG with significance | Q7.1 (Reynolds-Pan) + Q7.3 (Jha) | Decision 7 v2 | Substrate-dependent |
| **Spatial** | River two-branch DSEP | Q7.2 (Cui-Yuan) | Decision 7 v2 | Spatial-modality-specific |
| **Patient** | SHAP individual-level attribution | composite (this anchor) | Decision 7 v2 | Substrate-agnostic |

### 3.2 Substrate dependence — Decision 1 v2 integration

Per Decision 1 v2's substrate flexibility commitment, **the gene-level attribution layer is substrate-dependent**:

**If FM substrate wins Layer 5 ablations (scFoundation/UCE/scGPT/Geneformer):**
- IG+SmoothGrad over FM input layer
- EIG with hidden-space baseline (Jha 2020 methodology) operates on FM embeddings
- Kendiukhov spectral geometry interpretability applies (FM-specific)

**If parameter-free substrate wins (scTOP per Souza-Mehta):**
- Linear projection coefficients **directly expose** gene-level attribution
- No IG path computation needed — interpretability is "built in"
- This is methodologically **easier and more interpretable** than FM substrate
- Souza-Mehta Pattern F (parameter-free baselines mandatory) is reinforced by interpretability ease

**If scVI/scANVI substrate wins:**
- IG+SmoothGrad over VAE decoder for gene reconstruction
- Posterior latent space provides aleatoric+epistemic decomposition (Decision 5 v2 Layer 5.1 integration)
- Standard methodology applies

**Decision 7 v2 must specify all three branches** — gene attribution mechanism varies with substrate choice but the architectural commitment to gene-level interpretability is binding.

### 3.3 Cross-scale consistency checks (mandatory)

Per Charter §1.3 falsifiability, **inter-scale consistency** must be verified:

- **Drug-class similarity (CPA)** should correlate with **gene attribution overlap (EIG)** — drugs with similar mechanism should attribute to similar genes
- **GEARS graph neighbors of drug target** should match **EIG-attributed genes** — biological prior should match empirical attribution
- **scRank top genes for drug-target** should overlap with **EIG-attributed top genes** — GRN-propagation should match gradient-based attribution
- **SHAP individual-level patterns** should cluster meaningfully — patients with similar predicted responses should have similar attribution patterns

**Inconsistency at scale boundaries triggers Q7 layer revision.** INTERCEPTA cannot publish Q7 results with inconsistent multi-scale interpretation — that would be Charter §1.3 falsifiability failure.

## 4. INTERCEPTA implications

### For Decision 7 v2 (mechanistic interpretability)

Composite anchor establishes **the multi-scale stack** Decision 7 v2 commits to:
1. Geometric (Kendiukhov, FM-only)
2. Drug-class (CPA disentangled embeddings)
3. Pathway (GEARS graph + Beyondcell)
4. GRN/cell-type (scRank)
5. Gene-level (Reynolds-Pan SmoothGrad + Jha EIG with significance)
6. Spatial (Cui-Yuan River, spatial modality only)
7. Patient (SHAP individual attribution, DeepStrataAge pattern)

### For Decision 1 v2 (substrate flexibility) interaction

Composite anchor formalizes the **substrate-conditional interpretability branching**:
- FM substrate → spectral + IG+SmoothGrad over FM input
- Parameter-free → linear projection coefficients (intrinsic)
- scVI/scANVI → IG+SmoothGrad over VAE decoder

### For Decision 4 v2 (drug response architecture) integration

Slot 4 (graph-augmented module per GEARS) provides pathway-scale interpretability. Slot 1 (cell encoder per Decision 1 v2) determines gene-scale interpretability mechanism. CPA disentangled latent in the L7 backbone provides drug-class interpretability. **Decision 4 v2 + Decision 7 v2 are operationally co-bound.**

### For Decision 5 v2 (OOD detection) integration

SHAP individual-level attribution provides per-patient mechanism. Combined with Decision 5 v2 aleatoric/epistemic decomposition:
- **High epistemic + clear SHAP attribution:** uncertain prediction with traceable mechanism (hypothesis-generation use case)
- **Low epistemic + clear SHAP attribution:** confident prediction with traceable mechanism (preferred clinical state)
- **Diffuse SHAP attribution:** prediction not driven by clear feature signal — caution flag

### For Charter §1.3 falsifiability

Multi-scale stack provides **multi-scale falsifiability**:
- Pathway-scale claims falsifiable against GO ontology + Beyondcell signatures
- Gene-scale claims falsifiable against Jha significance testing
- Patient-scale claims falsifiable against SHAP individual-level reproducibility across ensemble

## 5. What's strong about this composite approach

- **Avoids duplicate anchoring** of methods already verified in Q1, Q3, Q4
- **Provides structural integration** Decision 7 v2 needs across all v2 decisions
- **Multi-scale design** matches the multi-scale nature of biological mechanism
- **DeepStrataAge as concrete example** of SHAP at individual-attribution level
- **Substrate-conditional branching** explicit per Decision 1 v2 flexibility

## 6. What's limited about this composite approach

- **Not a single primary-source anchor** — composite structure means less rigorous than single-paper Q1-Q3 standards
- **DeepStrataAge applied to aging, not drug response** — methodology transfer is conceptual, not empirically validated for INTERCEPTA's drug response context
- **Cross-scale consistency methodology is INTERCEPTA novelty** — no published framework validates inter-scale interpretability consistency
- **Substrate-conditional branching adds complexity** — three distinct gene-attribution implementations required

## 7. Discipline check

- [x] Composite anchor structure documented and rationalized
- [x] All component sources verified in their respective questions (Q1 Kendiukhov, Q3 scRank, Q4 GEARS + CPA + chemCPA, Q4 Beyondcell)
- [x] DeepStrataAge primary-source verified via npj Aging 2026 DOI 10.1038/s41514-026-00358-w
- [x] SHAP foundational reference (Lundberg & Lee 2017 NeurIPS) verified
- [x] **Substrate-conditional branching** explicit per Decision 1 v2 substrate flexibility
- [x] **Cross-scale consistency framework** introduced as INTERCEPTA novelty
- [x] **Errata note:** Original 2026-05-10 file (304w) had the core composite-anchor structure but lacked: substrate-conditional branching (Decision 1 v2 wasn't yet locked); cross-scale consistency methodology; explicit Decision 5 v2 + Decision 4 v2 integration; SHAP technical foundation; DeepStrataAge methodology depth. This rewrite at ~2,200 words brings the composite anchor to the Q1-Q3 standard while preserving its bridging role.

## Drift catalog this Phase 5 composite anchor enhancement

- **New drift instances introduced:** 0
- **Methodological discipline:** all component anchor claims sourced to respective verified Q-question notes; SHAP foundation primary-source-verified; DeepStrataAge primary-source-verified

— Claude (CSO), 2026-05-10 (Phase 5 composite anchor deepening)
