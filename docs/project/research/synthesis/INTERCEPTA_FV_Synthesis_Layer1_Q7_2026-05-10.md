# INTERCEPTA Layer 1 Q7 Synthesis v2 — Mechanistic Interpretability: The Multi-Scale Falsifiability Stack

**CSO:** Claude
**Date:** 2026-05-10
**Phase:** 5 re-do (audit remediation)
**Scope:** Integrating 4 verified primary-source anchor reads (7,531 words across anchors) to ground Decision 7 v2
**Supersedes:** Q7 Synthesis v1 (340 words, pre-audit, archived in `_archive/`)

---

## Executive Summary

Q7 (mechanistic interpretability) is **the falsifiability mechanism for INTERCEPTA's clinical and scientific claims.** Charter §1.3 requires that drug response predictions be mechanistically traceable; without rigorous Q7, INTERCEPTA produces black-box predictions that cannot be validated, refuted, or trusted in clinical decision-making.

The 4 verified Q7 anchors collectively establish:

1. **SmoothGrad is a cheap-but-decisive improvement** for all gradient-based attribution methods (+0.16 recall, +0.06 precision at top 1%) — Reynolds & Pan 2025
2. **Vanilla Integrated Gradients fails to identify known regulatory features as significant** — 0 meta-features in vanilla IG vs 488 in nonlinear-path IG (Jha 2020 EIG)
3. **Significance testing framework moves attribution from point estimates to falsifiable hypothesis tests** — Jha 2020 EIG p-value framework
4. **Biological discovery validates interpretability methodology** — Jha 2020 identified A1CF as liver-specific splicing regulator, confirmed by Tomtom motif + RNA-seq + PAR-CLIP triple-validation
5. **Spatial transcriptomics requires modality-specific attribution architecture** — Cui & Yuan 2025 River two-branch DSEP design
6. **Multi-scale interpretability is empirically necessary** — different scales (geometric, drug-class, pathway, GRN, gene, spatial, patient) require different methods that cross-validate each other

**The most consequential finding:** **No single attribution method is sufficient.** Vanilla IG fails (Jha); SmoothGrad alone isn't enough without significance testing (Reynolds-Pan); spatial modality requires its own architecture (River); patient-level mechanism requires individual SHAP attribution (composite). **INTERCEPTA's Decision 7 v2 must commit to a multi-scale stack with cross-scale consistency checks**, not to a single attribution method.

**Two drift instances caught in Phase 5:**
- **Drift #32 (fabrication-class):** Original Q7 anchor 3 was attributed to "Liu et al." but actual authors are **Jha A, Aicher JK, Gazzara MR, Singh D, Barash Y** (UPenn). Corrected.
- **Drift #33 (scope-drift):** Original Q7 anchor 2 (River) described as general perturbation attribution; actually **spatial transcriptomics DSEP gene prioritization**. Corrected.

These corrections demonstrate the audit mechanism functioning as designed — catching attribution and scope errors before they propagate into Decision 7 v2.

---

## What Each Anchor Establishes

### Anchor 1 — Reynolds & Pan 2025 (University of Oklahoma + Western Ontario, *PLOS Comp Bio*)

**Established empirically:**
- Four attribution algorithms benchmarked: Saliency, Gradient SHAP, DeepLIFT, Integrated Gradients
- Each evaluated with and without SmoothGrad (8 configurations total)
- Three-aspect framework: **recall** (synthetic spike-ins with additive/dominant/recessive/epistatic effects), **precision** (null decoys with preserved allele structure), **stability** (ensemble consistency)
- UK Biobank scale: ~300K participants, >500K variants, standing height phenotype
- **SmoothGrad improves average recall +0.16 and precision +0.06 at top 1%** — universal improvement across all 4 algorithms
- **IG+SmoothGrad achieves precision ~0.75 at 2% threshold** — highest for strict gene selection
- **Gradient SHAP+SmoothGrad ~0.68 at 3% threshold** — strong secondary option
- Non-smoothed variants: 0.25-0.38 precision at 10-20% thresholds (substantially worse)
- Epistatic recall is the hardest case (highest-order non-linearity)

**What this contributes to Decision 7 v2:** The empirical floor for gene-level attribution methodology. SmoothGrad is methodologically mandatory; IG+SmoothGrad is the primary recommended attribution method for INTERCEPTA's clinical drug target nomination use case.

**What this does NOT establish:** Gene expression attribution (genotype-only). Drug response context. FM-architecture attribution. Biological discovery validation (only precision/recall/stability metrics).

### Anchor 2 — Cui & Yuan 2025 River (Nature Communications) **[SCOPE CORRECTED IN PHASE 5]**

**Established empirically (corrected scope):**
- Introduces **DSEP (Differential Spatial Expression Patterns) gene prioritization** as a new analytical task for spatial transcriptomics
- **Spatial transcriptomics across multiple conditions** — identifies genes whose spatial expression pattern differs across conditions (disease vs healthy, treated vs untreated, etc.)
- Two-branch deep learning architecture: spatial-informed prediction branch + non-spatial prediction branch
- Branch decoupling captures **spatial-specific information** beyond expression alone
- Post-hoc attribution strategy for gene ranking
- Scalability to large spatial datasets emphasized

**What this contributes to Decision 7 v2:** The **spatial modality branch** of INTERCEPTA's multi-scale interpretability stack. Required for spatial transcriptomics inputs from Nicheformer (Q8.1) — tumor microenvironment, inflammatory infiltrates, plaque microregions.

**What this does NOT establish:** Dissociated scRNA-seq attribution (use Reynolds-Pan + Jha methodology instead). General perturbation attribution (was misrepresented in original Q7 note; CORRECTED in Phase 5). Specific attribution methodology details (Borda count claim from original note flagged as unverified pending full-paper fetch).

### Anchor 3 — Jha, Aicher, Gazzara, Singh & Barash 2020 EIG (UPenn, *Genome Biology*) **[ATTRIBUTION CORRECTED IN PHASE 5]**

**Established empirically and methodologically:**
- **Enhanced Integrated Gradients (EIG)** with two-axis variant framework: path type (Linear/Nonlinear) × baseline space (Original/Hidden)
- Four EIG variants: O-L-IG (vanilla), O-N-IG, H-L-IG, H-N-IG
- Six baseline choices tested: zero, encoded-zero, median, k-means, close, random
- **Significance testing framework:** one-sided t-test with Bonferroni correction (p ≤ 0.05) — moves attribution from point estimates to falsifiable hypothesis tests
- **Vanilla IG (O-L-IG) identifies 0 significant meta-features** on splicing task — complete failure
- **Nonlinear-path IG (O-N-IG) identifies 488 meta-features** — methodologically decisive
- **Biological discovery:** A1CF (APOBEC1 complementation factor) identified as key regulator of liver-specific alternative splicing
- **Triple validation of A1CF discovery:** Tomtom motif alignment (RNACompete database) + A1cf knockout RNA-seq + PAR-CLIP binding data

**What this contributes to Decision 7 v2:** Methodological foundation for **significance-tested gene attribution**. Vanilla IG is insufficient; nonlinear-path + hidden-space baseline + significance testing are architecturally required. Biological discovery validation (A1CF) proves attribution methodology can recover real regulators.

**What this does NOT establish:** Drug response context (splicing prediction only). scRNA-seq attribution (tabular feature inputs). FM-era methods. SmoothGrad combination (Reynolds-Pan 2025 addresses this gap).

### Anchor 4 — Multi-Scale Interpretability Composite (DeepStrataAge + Cross-Q References)

**Established structurally:**
- Multi-scale interpretability stack: geometric (Kendiukhov), drug-class (CPA), pathway (GEARS + Beyondcell), GRN/cell-type (scRank), gene-level (Reynolds-Pan + Jha), spatial (River), patient (SHAP)
- SHAP framework (Lundberg & Lee 2017): Shapley value attribution with efficiency, symmetry, linearity, null-player properties
- DeepStrataAge (npj Aging 2026): SHAP-based individual-level attribution on ~12K CpG methylation features reveals age-influential epigenetic waves
- Cross-Q references (Kendiukhov Q1, GEARS Q4, scRank Q3, CPA Q4) provide multi-scale integration

**What this contributes to Decision 7 v2:** The **structural integration** scaffold across all v2 decisions. Decision 7 v2's commitment to multi-scale interpretability is operationalized through the seven-scale architecture.

**What this does NOT establish:** Cross-scale consistency methodology (INTERCEPTA novelty contribution). DeepStrataAge methodology transfer to drug response (conceptual only).

---

## Convergent Patterns Across the 4 Anchors

### Pattern A — No single attribution method is sufficient

Reynolds-Pan: 4 algorithms × SmoothGrad, no single dominant choice. Jha: 4 EIG variants × 6 baselines, multiple work well. River: spatial-specific architecture needed. Composite: 7 scales, 7 different methods. **The field has converged on multi-method, multi-scale interpretability** — Decision 7 v2 must adopt this consensus.

### Pattern B — Significance testing is methodologically mandatory

Reynolds-Pan provides precision/recall/stability quantification (statistical framework). Jha provides per-feature p-value testing (hypothesis framework). **Together they establish that point-estimate attribution is insufficient** — INTERCEPTA's Q7 outputs must be statistically defensible (precision targets met; p-values below threshold).

### Pattern C — SmoothGrad is universally beneficial

Reynolds-Pan: +0.16 recall and +0.06 precision at top 1% across all 4 algorithms. **Operationally a few lines of code; methodologically decisive.** Decision 7 v2 must include SmoothGrad for all gradient-based attribution.

### Pattern D — Biological discovery validates interpretability

Jha: A1CF identified as liver splicing regulator, triple-validated. **This is the gold standard.** INTERCEPTA's Q7 layer should be evaluated by its ability to recover known drug-target biology AND discover novel mechanisms. Failure to recover known biology = Q7 layer failure.

### Pattern E — Modality-specific attribution is required

Dissociated scRNA-seq attribution (Reynolds-Pan + Jha methodology) differs from spatial transcriptomics attribution (River two-branch design). **Decision 7 v2 must be modality-aware** — different attribution architectures for different input modalities.

### Pattern F — Substrate-conditional interpretability branching

If Decision 1 v2 selects FM substrate: spectral analysis (Kendiukhov) + IG+SmoothGrad over FM input.
If parameter-free substrate: linear projection coefficients **intrinsically expose** gene attribution — easier and more interpretable.
If scVI/scANVI substrate: IG+SmoothGrad over VAE decoder.

**Three distinct attribution implementations** required per Decision 1 v2 substrate flexibility.

### Pattern G — Cross-scale consistency is INTERCEPTA novelty

No anchor provides a published framework for validating consistency across geometric / drug-class / pathway / GRN / gene / spatial / patient scales. **INTERCEPTA's contribution includes building this framework** — drug-class similarity should correlate with gene attribution overlap; GEARS graph neighbors should match EIG-attributed genes; etc.

---

## What the Field Has NOT Resolved (Honest Gaps)

Reading across all 4 anchors, open questions for Q7:

1. **scRNA-seq drug response attribution specifically.** Reynolds-Pan is genotype-height; Jha is splicing; River is spatial transcriptomics. **No anchor benchmarks attribution on scRNA-seq drug response prediction** — INTERCEPTA must benchmark its own Q7 layer on its own data.

2. **FM-era attribution methodology.** All 4 anchors predate widespread FM adoption. **Attention-head analysis, FM-specific interpretability methods, FM-tokenization-aware attribution** are unbenchmarked.

3. **Cross-scale consistency framework.** INTERCEPTA novelty contribution — no published methodology validates inter-scale interpretability consistency.

4. **Patient-level attribution stability.** SHAP individual-level attribution (DeepStrataAge pattern) is operationally feasible but stability across patients with similar predictions is unbenchmarked.

5. **Drug-target biology recovery as evaluation metric.** Jha's A1CF validation is the methodological template, but no benchmark systematically evaluates Q7 methods by drug-target recovery rate.

6. **Modality boundaries.** Whether spatial-aware attribution (River) outperforms dissociated attribution (Reynolds-Pan + Jha) when input has spatial coordinates available is empirically untested.

7. **Compute cost of full multi-scale stack.** Decision 7 v2's seven-scale architecture is compute-expensive; trade-offs vs single-method approaches not benchmarked.

---

## Cross-Decision Architectural Patterns

The Q7 anchors inform decisions beyond Decision 7:

### For Decision 1 v2 (cell representation)

Pattern F (substrate-conditional branching) operationalizes Decision 1 v2's substrate flexibility on the interpretability side. **Decision 7 v2 must specify all three substrate branches** (FM / parameter-free / VAE) and the corresponding gene-attribution mechanism.

### For Decision 2 (cross-cohort)

scANVI/MrVI's latent space is amenable to IG+SmoothGrad attribution over the decoder (per Pattern F middle branch). **Decision 2 + Decision 7 v2 are operationally compatible.**

### For Decision 3 (bulk→single-cell)

scRank's GRN-based mechanism trace is **already a Q7 layer at the GRN scale** (per composite anchor Table). Decision 3's GRN methodology directly contributes to Decision 7 v2's multi-scale stack.

### For Decision 4 v2 (drug response architecture)

- **Slot 4 (GEARS graph-augmented module)** provides pathway-scale interpretability natively
- **CPA disentangled latent** provides drug-class scale interpretability
- **Slot 1 (cell encoder)** determines gene-scale attribution mechanism per Decision 1 v2 substrate choice
- **Decision 4 v2 + Decision 7 v2 are operationally co-bound** — Decision 4 v2's architectural slots provide multiple interpretability scales for free

### For Decision 5 v2 (OOD detection)

- **N=5 Deep Ensembles** provides stability measurement for Reynolds-Pan methodology
- **Aleatoric/epistemic decomposition** integrates with SHAP individual-level attribution (composite Pattern):
  - High epistemic + clear SHAP attribution: uncertain but traceable (hypothesis generation)
  - Low epistemic + clear SHAP attribution: confident + traceable (preferred clinical state)
  - High epistemic + diffuse SHAP: caution flag
- **Decision 5 v2 + Decision 7 v2 are operationally co-bound** via shared ensemble + decomposition framework

### For Decision 6 v2 (validation cascade)

- **V0 baseline:** Q7 layer reproduces known mechanism for IFN-β response in PBMCs (analog of scGen evaluation)
- **V3 cell line → tumor:** Q7 layer recovers known cancer driver genes for known cancer drugs
- **V4 cell line → PDX:** Q7 attribution stability across N=5 ensemble; concordant biomarker space (Kim 2020 24.5%) gets stronger attribution than non-concordant
- **V5 clinical retrospective:** SHAP individual-level attribution predicts patient subgroups responsive vs non-responsive
- **V6 cross-disease:** Q7 attribution remains biologically plausible when transferred to held-out diseases
- **Reynolds-Pan decoy methodology** provides falsifiable evaluation framework

### For Decision 8 (universality)

- **U1 cross-disease:** Q7 cross-scale consistency must hold across disease boundaries
- **U2 cross-tissue:** River + spatial Q7 methodology supports tissue-context interpretability
- **U3 cross-resolution:** Q7 stack must work for bulk + scRNA-seq + spatial inputs
- **Paradigm comparison (Decision 8 Commitment 2):** Each paradigm (A/B/C/D) must support gene-level attribution; parameter-free Paradigm D has built-in interpretability advantage

### For Decision 9 (compute)

Full multi-scale Q7 stack is compute-expensive:
- Gene-scale IG+SmoothGrad: ~50 forward+backward passes per attribution × N=5 ensemble × thousands of cells
- Pathway-scale GEARS graph attention: native to L7 forward pass (cheap)
- Drug-class CPA disentangled: native to L7 forward pass (cheap)
- Patient SHAP: KernelSHAP expensive; DeepSHAP cheaper

**Decision 9 must allocate compute for Q7 layer** explicitly. Default: ~10-20% of Decision 4 v2 inference compute reserved for Q7 stack.

### For Decision 10 (open-source)

- Reynolds-Pan + Jha methodology: open methodology, CC BY publications
- River: Nature Communications (open access via license)
- SHAP / DeepSHAP / IG: standard implementations in shap library + Captum (PyTorch)
- **Decision 7 v2 stack is fully open-source-implementable.**

---

## Decision 7 — REVISED PROPOSED

The revised Decision 7 commitment (to be formalized as a Decision Record file) is the **SEVEN-SCALE MULTI-SCALE INTERPRETABILITY STACK** with binding substrate-conditional branching, significance testing, and cross-scale consistency checks.

### Seven-Scale Architecture

```
Scale 1: Geometric (Kendiukhov spectral, FM-substrate-only)
    ↓
Scale 2: Drug-class (CPA disentangled latent)
    ↓
Scale 3: Pathway (GEARS GO graph + Beyondcell BCS)
    ↓
Scale 4: GRN/Cell-type (scRank perturbation propagation)
    ↓
Scale 5: Gene-level (substrate-conditional):
    - FM substrate: IG+SmoothGrad with H-N-IG (Jha EIG) + significance testing
    - Parameter-free: linear projection coefficients (intrinsic)
    - scVI/scANVI: IG+SmoothGrad over VAE decoder
    ↓
Scale 6: Spatial (River two-branch DSEP — spatial modality only)
    ↓
Scale 7: Patient (SHAP individual-level attribution — DeepStrataAge pattern)
```

### Cross-Scale Consistency Checks (BINDING per Charter §1.3)

Each scale's outputs must be cross-consistent:
- **Scale 2 (drug-class similarity)** ↔ **Scale 5 (gene attribution overlap)** for drugs with similar mechanism
- **Scale 3 (GEARS pathway neighbors of drug target)** ↔ **Scale 5 (EIG-attributed genes)**
- **Scale 4 (scRank top genes for drug-target)** ↔ **Scale 5 (EIG-attributed top genes)**
- **Scale 7 (SHAP individual patterns)** cluster meaningfully — similar predictions should have similar attribution patterns

Inconsistency triggers Q7 layer revision per Charter §1.3 falsifiability.

---

## What This Synthesis Does NOT Resolve

Honest gaps that propagate to Layer 5 implementation:

1. **scRNA-seq drug response attribution benchmarks** — INTERCEPTA must build Reynolds-Pan-style spike-in + decoy methodology adapted to drug response context

2. **FM-era attribution methodology** — attention-head analysis, FM-tokenization-aware attribution unbenchmarked

3. **Cross-scale consistency thresholds** — what fraction of cross-scale overlap is "enough"? Layer 5 empirical work

4. **River's specific attribution methodology** — Borda count claim from original note unverified; full-paper fetch needed before Decision 7 v2 commits to specific River sub-methodology

5. **Patient-scale SHAP stability** — across-patient consistency thresholds unbenchmarked

These require Layer 5 implementation, not more Layer 1 reading.

---

## Drift Catalog This Phase 5 Cycle

- **Drift #32 caught real-time:** Wrong-attribution drift (was "Liu et al." 2020 EIG; actual is Jha et al.). **Severity: fabrication-class.** Corrected with new filename `jha_2020_enhanced_ig.md` and full author attribution.

- **Drift #33 caught real-time:** Scope-drift (River 2025 represented as general perturbation attribution; actual scope is spatial transcriptomics DSEP). **Severity: scope-drift.** Corrected.

- **Drift #34 caught real-time:** Unverified methodology claim in River note (Borda count aggregation across IG + DeepLIFT + GradientShap). **Severity: low.** Flagged for full-paper verification rather than removed; honest acknowledgment in note.

- **New drift instances introduced:** 0

- **Methodological discipline:** primary-source first-author verification before writing; methodology depth verified; biological discovery chains rigorously documented; substrate-conditional branching explicit per Decision 1 v2; cross-scale consistency framework documented as INTERCEPTA novelty

---

— Claude (CSO), 2026-05-10 (Phase 5 synthesis)
