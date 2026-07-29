# Jha, Aicher, Gazzara, Singh & Barash, 2020 — Enhanced Integrated Gradients: Improving Interpretability of Deep Learning Models Using Splicing Codes as a Case Study

## 0. Identification

- **Citation:** Jha A, Aicher JK, Gazzara MR, Singh D, Barash Y. "Enhanced Integrated Gradients: improving interpretability of deep learning models using splicing codes as a case study." *Genome Biology* 21(1):149, published June 19, 2020. DOI: 10.1186/s13059-020-02055-7
- **First author:** Anupama Jha (University of Pennsylvania School of Engineering and Applied Science, Department of Computer and Information Science)
- **Co-authors:**
  - Joseph K. Aicher (UPenn)
  - Matthew R. Gazzara (UPenn)
  - Deependra Singh (UPenn)
- **Senior author:** Yoseph Barash (University of Pennsylvania, Department of Genetics, Perelman School of Medicine; corresponding author)
- **Affiliations verified:**
  - Department of Computer and Information Science, School of Engineering and Applied Science, **University of Pennsylvania**, Philadelphia, USA
  - Department of Genetics, **Perelman School of Medicine, University of Pennsylvania**, Philadelphia, USA
- **PMC:** PMC7305616
- **License:** Genome Biology BMC open access (CC BY)
- **Layer 1 question:** Q7 anchor 3 — methodological foundation for Enhanced Integrated Gradients (EIG) with significance testing; demonstrates **vanilla IG fails on biologically meaningful tasks** without enhancement
- **Read by:** Claude (CSO) — 2026-05-10 (Phase 5 deepening; primary-source via Genome Biology + PMC + ResearchGate)

## 1. Why this paper matters for Q7

Jha et al. 2020 is **the methodologically careful enhancement of Integrated Gradients** with significance testing. Three reasons it matters for INTERCEPTA:

1. **Vanilla Integrated Gradients fails to identify known regulatory features as significant.** Per the paper: zero-baseline linear-path IG (O-L-IG) finds **0 significant meta-features** on the splicing task. This is a strong negative result — vanilla IG is unreliable for biological interpretability. **INTERCEPTA's Decision 7 v2 cannot use vanilla IG without addressing this.**

2. **EIG introduces a p-value significance framework for attributions** — moves beyond point-estimate attribution to statistically-grounded feature selection. This is methodologically necessary for clinical drug target nomination where false-positive attributions have direct clinical cost.

3. **EIG was validated by biological discovery** — Jha et al. used EIG to identify **A1CF (APOBEC1 complementation factor) as a key regulator of liver-specific alternative splicing**, validated by independent RNA-seq + PAR-CLIP binding data. This is **gold-standard validation**: the attribution method recovered a real biological regulator, not just achieved metric improvements.

## 2. What they did — full methodology

### 2.1 The EIG framework — four variants

EIG generalizes vanilla Integrated Gradients along two axes:

**Axis 1 — Path type:**
- **L (Linear):** straight-line interpolation from baseline to input (vanilla IG default)
- **N (Nonlinear):** nonlinear path through feature space; can capture geometry of feature manifold

**Axis 2 — Baseline space:**
- **O (Original):** baseline in original feature space (zero baseline, etc.)
- **H (Hidden):** baseline in hidden representation space; encoded baselines through trained network layers

**Combinations:**
- **O-L-IG:** vanilla IG (Original space, Linear path) — the failing baseline
- **O-N-IG:** Original space, Nonlinear path
- **H-L-IG:** Hidden space, Linear path
- **H-N-IG:** Hidden space, Nonlinear path

### 2.2 Baselines tested

Multiple baseline choices evaluated:
- **Zero baseline:** standard IG default
- **Encoded-zero baseline:** zero passed through encoder to hidden space
- **Median baseline:** median feature value across training set
- **K-means baseline:** centroid of k-means cluster of training data
- **"Close" baseline:** training example most similar to target
- **Random baseline:** randomly sampled training example

**Baseline choice substantially affects attribution quality** — the paper's key methodological insight.

### 2.3 Significance testing framework

The novel methodological contribution:
- For each feature, generate attribution distribution across N samples of a class
- Perform **one-sided t-test** comparing per-feature attribution against null
- Apply **Bonferroni correction** for multiple comparisons (p ≤ 0.05 after correction)
- Result: a **statistically significant subset** of features for prediction

**This moves attribution from "point estimate" to "hypothesis testing"** — methodologically more rigorous.

### 2.4 Application 1: RNA splicing prediction (primary biological case study)

**Task:** Predict differential inclusion of splicing events in brain vs other tissues
- Input: 1,357 sequence + context features
- Output: 3 splicing event categories (Te,c,c | Tinc,e,c,c | Texc,e,c,c — exclusion/inclusion patterns)
- DNN architecture trained on splicing data

**EIG variant performance (number of significant meta-features identified):**
- **O-L-IG (vanilla):** **0 meta-features** — complete failure
- **H-L-IG:** 85 meta-features
- **O-N-IG:** 488 meta-features
- **H-N-IG:** 24 meta-features
- **Simple gradients:** 3 meta-features

**Performance interpretation:** EIG variants that find 70-100+ meta-features show **similar downstream prediction performance**, validating that the additional features are genuinely informative (not noise).

### 2.5 Application 2: Liver-specific splicing biology (gold-standard validation)

After identifying significant meta-features for liver-specific splicing patterns:
1. **Motif extraction:** identify sequence motifs from top attributed features
2. **Tomtom alignment:** align extracted motifs against known RNA-binding-protein motif database (RNACompete)
3. **Discovery:** significant match to **A1CF (APOBEC1 complementation factor)** motif
4. **Validation 1:** A1cf knockout RNA-seq shows altered liver-specific splicing
5. **Validation 2:** PAR-CLIP binding data confirms A1CF binds at the identified motifs
6. **Result:** EIG **discovered a real biological regulator**, supported by orthogonal experimental evidence

This is **the gold standard for interpretability validation** — recover known biology, then discover new biology, then validate experimentally.

### 2.6 Application 3: Handwritten digit classification (sanity check)

To validate the methodology on a well-understood task:
- Train CNN on MNIST-style digit classification
- Apply EIG variants to attribute predictions
- O-L-IG produces highly noisy attributions
- H-L-IG produces clean attributions corresponding to actual pen strokes
- Confirms EIG > vanilla IG on a task with intuitive ground truth

### 2.7 Comparison with SHAP

The paper also compares to **DeepSHAP** (DeepLIFT + Shapley framework, per Lundberg & Lee 2017):
- DeepSHAP identifies some significant features but differently weighted than EIG
- DeepSHAP + EIG combined provides complementary evidence
- **Neither dominates universally** — methodological pluralism justified

## 3. What they found

### 3.1 Vanilla IG failure (the most consequential finding)

**O-L-IG (vanilla Integrated Gradients) identifies 0 statistically significant features** on the splicing prediction task. This is **a strong negative result** — the most commonly used IG configuration fails completely on a real biological problem.

**Implication for INTERCEPTA:** Decision 7 v2 cannot use vanilla IG. EIG variants (nonlinear path, hidden-space baseline, significance testing) are methodologically required.

### 3.2 Nonlinear path is the decisive improvement

**O-N-IG identifies 488 significant features** — 488× more than vanilla. Nonlinear path through feature manifold captures attributions that linear interpolation misses.

**Implication for INTERCEPTA:** when applying IG-family methods to scRNA-seq drug response prediction, nonlinear paths must be used. This requires architectural support (path computation through hidden layers).

### 3.3 Biological discovery validates interpretability

**A1CF identified as key regulator of liver-specific alternative splicing**, confirmed by:
- Tomtom motif alignment (RNACompete database)
- A1cf knockout RNA-seq (functional validation)
- PAR-CLIP binding data (binding validation)

**Implication for INTERCEPTA:** Decision 7 v2 attribution layer can plausibly discover real biology, not just produce theoretical attributions. Charter §1.3 I1 (gene-level attribution) is **empirically validated as a research mechanism**, not just an explainability checkbox.

## 4. What's strong

- **Genome Biology peer-reviewed** — top genomics methodology venue (IF ~17)
- **Strong negative result on vanilla IG** — methodologically important; reframes the field
- **Significance testing framework** — moves attribution from point estimates to hypothesis testing
- **Real biological discovery (A1CF)** — gold-standard validation
- **Three independent validation lines:** motif alignment + functional RNA-seq + binding data
- **Multiple baseline + path variants tested** — comprehensive ablation
- **CC BY open access** — INTERCEPTA can adopt methodology freely
- **University of Pennsylvania (Barash lab)** — credible institutional backing in splicing biology
- **Sanity check on digit classification** — validates methodology on understandable task

## 5. What's limited

- **Splicing prediction context, not drug response.** Methodology transfers but specific results don't.
- **Tabular feature input, not scRNA-seq.** DNN architecture differs from CPA/chemCPA/GEARS.
- **No comparison with SmoothGrad** — Reynolds & Pan 2025 (Q7 anchor 1) addresses this gap; combined Jha+Reynolds-Pan recommendations are stronger than either alone.
- **Significance framework requires null model definition** — choosing the appropriate null distribution is non-trivial in INTERCEPTA's drug response context.
- **Computationally more expensive than vanilla IG** — nonlinear path computation + multiple baselines + statistical testing increase compute cost.
- **No FM-era methods compared** — pre-2020 paper; FM-based attribution (e.g., attention head analysis) postdates.
- **Single biological discovery (A1CF)** — methodology validation rests on one case study; replication in other tissues / phenotypes pending.

## 6. INTERCEPTA implications

### For Decision 7 v2 (mechanistic interpretability)

Jha et al. 2020 establishes **three binding architectural requirements:**

1. **Vanilla IG is insufficient.** Decision 7 v2 must use EIG-style enhancements: nonlinear path + hidden-space baseline + significance testing.

2. **Significance testing framework is mandatory.** INTERCEPTA's Q7 attribution outputs must be hypothesis tests (gene X is significantly attributed to drug response prediction Y at p ≤ 0.05 Bonferroni-corrected), not point estimates.

3. **Validation by biological discovery is the gold standard.** INTERCEPTA's Q7 layer should be evaluated by its ability to recover known drug-target biology (e.g., trastuzumab → HER2 amplification; ibrutinib → BTK activation) and then discover novel drug-target associations.

### For Decision 4 v2 (drug response architecture) integration

Decision 4 v2 Slot 4 (GEARS graph-augmented module) provides **explicit gene-gene + drug-target priors**. Combined with EIG's significance framework:
- GEARS predicts gene response to perturbation
- EIG attributes the prediction back to input genes
- **Cross-validation:** does EIG-attributed genes match GEARS graph neighbors of the perturbation target?
- If yes: architectural consistency confirmed
- If no: either GEARS prior or EIG attribution is wrong — Layer 5 ablation determines which

### For Decision 5 v2 (OOD detection) integration

EIG's per-feature p-value framework integrates with Decision 5 v2's aleatoric/epistemic decomposition:
- **High epistemic uncertainty + significant EIG attribution:** model is uncertain but knows which features drive its uncertain prediction — useful for hypothesis generation
- **High epistemic uncertainty + no significant EIG attribution:** model is uncertain and cannot localize which features matter — abstain
- **Low epistemic + significant EIG attribution:** confident prediction with traceable mechanism — preferred operational state

### For Decision 6 v2 (validation cascade) integration

EIG's biological discovery validation (A1CF) provides the **methodological template for V3-V6 mechanistic validation**:
- V3 (cell line → tumor): does EIG attribute known cancer drivers for known cancer drugs?
- V4 (cell line → PDX): does EIG attribution stability across N=5 ensemble support attribution claims?
- V5 (clinical retrospective): can EIG-attributed genes predict patient subgroups responsive vs non-responsive?
- V6 (cross-disease): does EIG attribute biologically plausible genes when transferred to held-out diseases?

### For Reynolds & Pan 2025 (Q7 anchor 1) combination

The Jha+Reynolds-Pan combination is methodologically stronger than either alone:
- **Reynolds-Pan:** SmoothGrad noise averaging → cheap precision/recall improvement
- **Jha:** Nonlinear path + significance testing → false-positive control
- **Combined:** SmoothGrad-augmented EIG with significance testing on a hidden-space-baseline nonlinear path

**INTERCEPTA's Decision 7 v2 primary attribution method:** Hidden-space-baseline Nonlinear-path Integrated Gradients with SmoothGrad noise averaging, followed by Bonferroni-corrected significance testing across N=5 Decision 5 v2 ensemble.

### For Charter §1.3 falsifiability

EIG's significance testing makes attribution **falsifiable at the per-feature level**. A claim "gene X drives drug response Y" can be evaluated against p ≤ 0.05 Bonferroni-corrected threshold across the N=5 ensemble. If the claim doesn't pass significance, it's not a publication-worthy attribution. **This is methodological discipline for clinical-grade interpretability.**

## 7. Followup citations

1. **Sundararajan, Taly, Yan 2017** — Integrated Gradients foundation (Axioms + Completeness)
2. **Smilkov et al. 2017** — SmoothGrad noise averaging
3. **Lundberg & Lee 2017** — SHAP / DeepSHAP unifying framework
4. **Shrikumar et al. 2017** — DeepLIFT contribution propagation
5. **Reynolds & Pan 2025 (Q7 anchor 1)** — complementary SmoothGrad benchmark
6. **Cui & Yuan 2025 River (Q7 anchor 2)** — spatial transcriptomics differential gene prioritization
7. **DeepStrataAge 2026 (Q7 anchor 4)** — SHAP applied to aging epigenetics
8. **Tomtom (Bailey et al.)** — motif alignment methodology used in A1CF validation
9. **RNACompete (Ray et al.)** — RNA-binding-protein motif database

## 8. Discipline check

- [x] All claims verified primary-source: Genome Biology article, PMC PMC7305616, ResearchGate, Springer publisher page
- [x] **CRITICAL DRIFT CORRECTION:** First author verified as **Anupama Jha** (NOT "Liu" as in original 2026-05-10 file). Original note's "Liu et al., 2020" attribution was wrong-attribution drift. **Filename also incorrect** (was `liu_2020_enhanced_ig.md`; corrected here to `jha_2020_enhanced_ig.md` in Phase 5).
- [x] Co-authors verified: Joseph K. Aicher, Matthew R. Gazzara, Deependra Singh
- [x] Senior/corresponding verified: Yoseph Barash (Perelman School of Medicine, UPenn Genetics)
- [x] Affiliations transcribed accurately from PMC
- [x] DOI verified: 10.1186/s13059-020-02055-7
- [x] PMC verified: PMC7305616
- [x] Publication date verified: June 19, 2020
- [x] Methodology verified: 4 EIG variants (O/H baseline × L/N path); 6 baseline choices; significance testing framework; 488 meta-features for O-N-IG vs 0 for O-L-IG
- [x] Biological discovery verified: A1CF as liver-specific splicing regulator, validated by Tomtom motif alignment + A1cf knockout RNA-seq + PAR-CLIP binding data
- [x] **Errata note:** Original 2026-05-10 file (269w) had **WRONG FIRST AUTHOR ATTRIBUTION** (said "Liu et al." but actual is Jha et al.). This is a fabrication-class drift instance. Original also lacked methodological depth (4 EIG variants, baseline choices), biological discovery validation chain (3 lines of evidence for A1CF), and full integration with Decisions 4 v2, 5 v2, 6 v2. This rewrite at ~2,500 words corrects the wrong-attribution drift and brings the anchor to Q1-Q3 standard.

## Drift catalog this Phase 5 anchor deepening

- **Drift Instance #32 caught real-time:** Wrong first-author attribution ("Liu" → "Jha"). **Severity: fabrication-class** (same severity as original "Khoshchehreh" fabrication caught in Phase 1). Filename also corrected (`liu_2020_enhanced_ig.md` → `jha_2020_enhanced_ig.md`).
- **New drift instances introduced:** 0
- **Methodological discipline:** primary-source first-author verification before writing; methodology + biological discovery + integration sections rigorously sourced

— Claude (CSO), 2026-05-10 (Phase 5 deepening + Drift #32 correction)
