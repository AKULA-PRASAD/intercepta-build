# INTERCEPTA Layer 1 Q5 Synthesis v2 — Out-of-Distribution Detection: The Safety Boundary for Cross-Disease Universality

**CSO:** Claude
**Date:** 2026-05-10
**Phase:** 3 re-do (audit remediation)
**Scope:** Integrating 6 verified primary-source anchor reads (8,486 words across anchors) to ground Decision 5
**Supersedes:** Q5 Synthesis v1 (352 words, pre-audit, archived in `_archive/`)

---

## Executive Summary

Q5 (OOD detection) is **the safety boundary for Charter §1.1 universality.** Decision 8's V6 cross-disease pass criterion (AUROC ≥ 0.65 on held-out disease) is only meaningful if INTERCEPTA knows when its predictions are unreliable. Without rigorous Q5, the system overconfidently predicts drug response for biological states it has never seen — a deployment failure mode that would invalidate Charter §1.3 falsifiability and pose direct harm in clinical translation contexts.

The 6 verified Q5 anchors collectively establish:

1. **No single OOD method dominates** (Theunissen 2025 empirical finding on scRNA-seq; Engelmann 2022 corroborates on HLCA) → INTERCEPTA must stack methods, not commit to one
2. **The aleatoric vs epistemic decomposition must be operational** (Engelmann 2022 + Theunissen 2025) → Q5 outputs report both separately
3. **Statistical guarantees are only available via conformal prediction** (López-De-Castro 2025) → only method with distribution-free coverage guarantees
4. **Compute-efficient single-forward-pass methods exist** (Engelmann 2022 DKL/MIMO; Liu 2020 energy score) → Decision 9 compute envelope is feasible
5. **Standard scArches WKNN uncertainty is insufficient** (Engelmann 2022 ECE finding) → cannot rely on scvi-tools native output as the Q5 layer
6. **Integration does not destroy the OOD signal** (Theunissen 2025) → Decision 2 cross-cohort harmonization and Decision 5 OOD detection are architecturally compatible

**The most consequential finding:** Theunissen et al. state plainly that OOD methods "can identify severe data shifts, but not reliably." This is the empirical caveat INTERCEPTA must engineer around, not against. **The honest scientific position is that drug response prediction OOD is partially solvable; the 0.65 V6 threshold is calibrated to this reality.**

**Decision 5 is a stacked OOD architecture** with four layers, each contributing what the others cannot: native VAE uncertainty (Decision 2/4) → epistemic refinement (Deep Ensembles or MIMO/DKL) → energy-based post-hoc flag (fast pre-filter) → conformal prediction (statistical guarantees). This stack is empirically motivated by the absence of a universal winner.

---

## What Each Anchor Establishes

### Anchor 1 — Theunissen et al. 2025 (Ghent University + VIB, *Brief Bioinformatics*)

**Established empirically:**
- Six OOD methods (LogitNorm, MC Dropout, Deep Ensembles, Energy, Deep NN, Posterior Networks) benchmarked on scRNA-seq cell annotation with synthetic and real-life biological OOD scenarios
- **Severe shifts (novel cell types) are detectable; subtle shifts (within-cell-type biological state changes) are unreliably detected**
- No single method dominates across all settings — performance is method-and-task dependent
- **Dataset integration does NOT hinder novel cell type detection** — operational compatibility of harmonization and OOD detection confirmed
- Aleatoric vs epistemic decomposition is methodologically essential; methods that conflate them underperform

**What this contributes to Decision 5:** The empirical foundation for the stacked architecture. No single-method commitment is defensible given Theunissen's findings.

**What this does NOT establish:** Drug response prediction OOD (the actual INTERCEPTA setting). FM-based OOD detection. Cross-disease OOD specifically.

### Anchor 2 — López-De-Castro et al. 2025 (University of Navarra, *Bioinformatics*)

**Established theoretically and empirically:**
- Conformal prediction provides **distribution-free statistical guarantees** on prediction set coverage — the only Q5 method offering formal statistical properties
- Three annotation taxonomies tested (standard, classwise, cluster-aware) × three non-conformity measures across 10 batched experiments on multiple tissues
- Anomaly detector effectively identifies previously unseen cell types
- Well-calibrated prediction sets — empirical coverage matches theoretical 1-α guarantees
- **Model-agnostic** — wraps around any base classifier (scANVI, MrVI, scGPT, INTERCEPTA's own L7 layer)

**What this contributes to Decision 5:** The statistical-guarantee layer. The only Q5 method that delivers what Charter §1.3 falsifiability requires for clinical drug response prediction.

**What this does NOT establish:** Drug response prediction (cell annotation only). Cross-disease conformal calibration (calibration set requirements are non-trivial when held-out diseases have no labeled samples).

### Anchor 3 — Lakshminarayanan, Pritzel & Blundell 2017 (DeepMind, NeurIPS)

**Established methodologically:**
- Deep Ensembles = N independent neural networks trained with different random init; predictions averaged; disagreement = epistemic uncertainty
- Non-Bayesian, embarrassingly parallel, scalable
- Empirically beats MC Dropout on calibration in image classification
- **Method-class foundational** — every subsequent OOD benchmark cites this as the epistemic uncertainty baseline

**What this contributes to Decision 5:** The default epistemic uncertainty layer. N=5 is the standard ensemble size.

**What this does NOT establish:** Calibration in scRNA-seq specifically (Theunissen 2025 partially addresses this). Cost-effectiveness — N=5 multiplies INTERCEPTA training compute by 5×.

### Anchor 4 — Gal & Ghahramani 2016 (Cambridge, ICML)

**Established theoretically:**
- MC Dropout (dropout active at inference, T forward passes) = approximate Bayesian inference on Deep Gaussian Process
- Bridges practical (dropout regularization) and principled (Bayesian neural networks)
- **Compute-efficient alternative** to Deep Ensembles (single model, T forward passes ≪ N training runs)

**What this contributes to Decision 5:** The compute-budget fallback for epistemic uncertainty when Deep Ensembles are unaffordable.

**What this does NOT establish:** Whether the Bayesian approximation is tight enough for high-stakes OOD scenarios (subsequent theoretical work has questioned this for far OOD inputs). Theunissen 2025 finds MC Dropout is outperformed by Deep Ensembles on most scRNA-seq tasks.

### Anchor 5 — Liu, Wang, Owens & Li 2020 (UCSD/UC Davis/UW-Madison, NeurIPS)

**Established theoretically and empirically:**
- Energy score E(x) = -T log Σ exp(z_i/T) is theoretically aligned with input probability density (unlike softmax, which is shift-invariant and overconfident)
- **15-fold FPR@95 TPR reduction** (51.04% → 3.32%) on CIFAR-10 with energy-bound fine-tuning vs softmax confidence
- AUROC improvement 90.90% → 98.92%
- Works post-hoc on any pretrained classifier (Mode A — zero retraining)
- Theunissen 2025 includes Energy as one of the 6 methods benchmarked

**What this contributes to Decision 5:** The fast pre-filter layer. Cheapest OOD method computationally; can be applied as a first-pass filter before more expensive conformal prediction.

**What this does NOT establish:** Statistical guarantees (Liu energy has none; only conformal prediction does). scRNA-seq-specific performance magnitudes (Theunissen 2025 provides this).

### Anchor 6 — Engelmann, Hetzel, Palla et al. 2022 (Helmholtz Munich, ICML Workshop)

**Established empirically on HLCA:**
- **WKNN (scArches default) has poor Expected Calibration Error** — standard scRNA-seq label transfer uncertainty is inadequate
- Single-forward-pass methods (DKL, MIMO with 3/8 subnetworks) are both well-calibrated AND OOD-detective on the Human Lung Cell Atlas (580K cells, 58 cell types, 107 individuals)
- **Compute-efficient alternative** to Deep Ensembles validated at scale
- Aleatoric/epistemic decomposition operationalized: model uncertainty (epistemic) is the OOD-relevant signal; predictive uncertainty alone is insufficient

**What this contributes to Decision 5:** The architecturally specific evidence that scvi-tools/scArches native output cannot be the final Q5 layer. Validates DKL/MIMO as compute-efficient alternatives to N=5 Deep Ensembles.

**What this does NOT establish:** Generalization beyond single-tissue (HLCA is lung-only). Drug response prediction OOD. FM-based OOD detection.

---

## Convergent Patterns Across the 6 Anchors

### Pattern A — No universal winner; stack architecture is empirically required

Theunissen 2025 (6 methods, no dominance), Engelmann 2022 (4 model classes, DKL/MIMO win on calibration + OOD but trade off elsewhere), and the broader literature (López-De-Castro covers what Theunissen does not; Liu energy covers what Lakshminarayanan does not) collectively establish that **method-task dependence is the rule**. INTERCEPTA's stacked architecture is not over-engineering; it is the empirically defensible response.

### Pattern B — Aleatoric/epistemic decomposition is non-negotiable

Engelmann 2022 (formula and operationalization), Theunissen 2025 (independent confirmation), and Gal 2016 (theoretical Bayesian foundation) all establish that uncertainty must be decomposed:
- **Epistemic** = OOD-relevant signal (drug response novel disease)
- **Aleatoric** = label noise / ambiguous biological state (drug response in transitioning cells)

INTERCEPTA's Q5 output must report both separately. **Collapsing them into a single "uncertainty" score is methodologically wrong per the field consensus.**

### Pattern C — Statistical guarantees are unique to conformal prediction

López-De-Castro 2025 stands alone in providing distribution-free coverage guarantees. Deep Ensembles, MC Dropout, Energy, DKL, MIMO — all heuristics. For Charter §1.3 falsifiability of drug response predictions in clinical contexts, **conformal prediction is operationally mandatory** as the top-of-stack layer.

### Pattern D — Compute-efficient alternatives exist for academic deployment

For Decision 9 single-A100 budget:
- **Cheapest:** Energy-based scoring (zero overhead beyond logits) — Liu 2020
- **Cheap:** MC Dropout (1× training, T× inference) — Gal 2016
- **Single-forward-pass:** DKL or MIMO (slightly more parameters than standard classifier) — Engelmann 2022
- **More expensive:** Deep Ensembles N=5 (5× training, 5× memory) — Lakshminarayanan 2017
- **Calibration overhead:** Conformal prediction (held-out calibration set + per-class score storage) — López-De-Castro 2025

INTERCEPTA can choose compute-quality trade-offs explicitly per deployment context.

### Pattern E — Integration ≠ OOD signal loss

Theunissen 2025's finding that integration does not hinder novel cell type detection is operationally critical. It means Decisions 2 (cross-cohort harmonization via scANVI/MrVI/Harmony) and 5 (OOD detection) are not in tension. INTERCEPTA's pipeline can integrate first, then detect OOD on integrated latents — the architecturally clean approach.

### Pattern F — The drug response OOD gap is unsolved by anyone

**None of the 6 anchors tests OOD detection on drug response prediction directly.** All test cell type annotation or disease state classification. This is the gap INTERCEPTA's Layer 5 must close empirically. **The honest scientific position:** INTERCEPTA inherits the Q5 methods from the cell annotation literature but cannot inherit their performance guarantees — must benchmark independently.

---

## What the Field Has NOT Resolved (Honest Gaps)

Reading across all 6 anchors, the field's open questions for Q5 that INTERCEPTA must address in Layer 5:

1. **Drug response OOD vs cell type OOD.** Every Q5 anchor tests cell annotation; INTERCEPTA needs drug response. Whether the same methods transfer is empirically untested.

2. **Cross-disease OOD calibration.** Conformal prediction requires a calibration set with the same distribution as the test set. For held-out diseases, no calibration set exists. Open question: can cross-disease conformal recalibration work with small fine-tuning samples from each new disease?

3. **FM-based OOD detection.** All 6 anchors predate widespread FM adoption or do not test FM-based methods. FM embedding distance to training distribution is a plausible OOD signal but unbenchmarked.

4. **Subtle-shift detection reliability.** Theunissen 2025's "but not reliably" caveat applies specifically to subtle shifts. For INTERCEPTA, subtle shifts (familiar disease, novel patient subpopulation) are exactly the deployment scenarios where false-confidence errors are clinically dangerous.

5. **Aleatoric/epistemic ratio interpretability.** The field operationalizes the decomposition mathematically but provides limited guidance on how to communicate the dual uncertainty to clinical end-users. INTERCEPTA's Charter §1.3 falsifiability requires solving this.

6. **OOD detection across resolutions.** scRNA-seq Q5 anchors do not cover bulk RNA-seq or spatial transcriptomics. Decision 8 universality (U3 cross-resolution) needs OOD detection that works across data modalities, not just within scRNA-seq.

---

## Cross-Decision Architectural Patterns

The Q5 anchors inform decisions beyond Decision 5:

### For Decision 1 v2 (cell representation)

Engelmann 2022's finding that **scANVI's native classifier uncertainty (WKNN) is inadequate** has implications for Decision 1 v2's substrate choice. Whichever substrate wins Layer 5 ablations (scFoundation, scTOP, scVI, or other), the substrate's own uncertainty estimate is not the operational Q5 output. A separate Q5 layer must wrap any substrate. This **decouples Decision 5 from Decision 1 v2's deferral** — Q5 layer works regardless of substrate choice.

### For Decision 2 (cross-cohort)

Theunissen 2025's integration-OOD compatibility means **scANVI/MrVI integration is the architecturally clean substrate** for Q5 detection. INTERCEPTA's pipeline can integrate datasets first, then detect OOD on integrated representations without architectural conflict.

### For Decision 4 (drug response architecture)

The Q5 stack must wrap the L7 drug response prediction head. **Conformal prediction wraps prediction sets/intervals** for response category or AUC bin predictions. Deep Ensembles N=5 of the L7 layer (CPA + GEARS + FM-encoder) is the default epistemic uncertainty path. **Decision 4's architecture must be compatible with N=5 ensembling** — implies modular design where the L7 head is the ensembled unit, not the entire pipeline.

### For Decision 6 (validation)

V0-V6 validation cascade must report OOD detection performance per level. Specifically:
- **V0-V1 (within-cohort, cross-cell-line dataset):** OOD detection of held-out cell lines
- **V3-V4 (organoid, PDX):** OOD detection of preclinical-to-clinical translation shifts
- **V5 (clinical retrospective):** OOD detection of patient subpopulations
- **V6 (cross-disease):** OOD detection of held-out diseases — the hardest setting, where Theunissen's "but not reliably" caveat is most consequential

### For Decision 7 (mechanistic interpretability)

The aleatoric/epistemic decomposition (Pattern B) is **mechanistically interpretable**:
- High aleatoric → "the cell is in a transitioning state where the label is genuinely ambiguous"
- High epistemic → "the model has never seen anything like this cell + drug combination"

Decision 7's interpretability layer should explicitly distinguish these two failure modes, not just report a single uncertainty score.

### For Decision 8 (universality)

Decision 8 V6 (cross-disease AUROC ≥ 0.65) is **only meaningful if Q5 reliably flags held-out-disease predictions.** Theunissen 2025's subtle-shift unreliability finding is the empirical caveat. The 0.65 threshold is calibrated to account for partial Q5 reliability. **If Q5 fails entirely, Decision 8 V6 fails by transitivity.**

### For Decision 9 (compute)

Q5 compute budget is dominated by Deep Ensembles (5× training) and Conformal calibration. Engelmann 2022's single-forward-pass alternatives (DKL, MIMO) provide a viable fallback for compute-constrained deployments. **Decision 9 should specify both a "full Q5 stack" budget and a "compute-constrained Q5" budget** so INTERCEPTA can deploy at different scales.

### For Decision 10 (open-source)

All Q5 anchors have open implementations:
- conformal prediction → GitHub digital-medicine-research-group-UNAV/conformalized_single_cell_annotator + Zenodo
- Deep Ensembles → standard PyTorch
- MC Dropout → standard PyTorch
- Energy-based → GitHub wetliu/energy_ood
- DKL/MIMO → reference implementations available

INTERCEPTA's Q5 stack is fully open-source-implementable.

---

## Decision 5 — REVISED PROPOSED

The revised Decision 5 commitment (to be formalized as a Decision Record file) is the **STACKED OOD ARCHITECTURE** with the following layers:

### Layer 5.1 — Native Substrate Uncertainty

- Source: scANVI/MrVI/CPA posterior from Decision 2 / Decision 4 substrate
- Output: per-cell aleatoric + epistemic decomposition (per Smith & Gal 2018 framework)
- Cost: zero marginal — built into substrate

### Layer 5.2 — Epistemic Refinement (compute-budget-dependent)

**Default (high compute):** Deep Ensembles N=5 over L7 drug response prediction head
- Provides better calibration than MC Dropout (per Lakshminarayanan 2017 + Theunissen 2025 evidence)
- Cost: 5× training compute, 5× memory

**Fallback (compute-constrained):** MIMO8 (8 subnetworks, single forward pass) per Engelmann 2022
- Single model, similar quality to Deep Ensembles per Engelmann's HLCA evaluation
- Cost: ~1.5× parameters of standard classifier; single forward pass

**Further fallback:** MC Dropout with T=50 forward passes
- Cost: 1× training, 50× inference latency

### Layer 5.3 — Statistical-Guarantee Layer

- Source: Conformal prediction (López-De-Castro 2025 methodology) on L7 predictions
- Output: prediction sets/intervals with distribution-free 1-α coverage guarantee (default α=0.05)
- Requirement: held-out calibration set from same distribution as test set
- **For cross-disease V6:** cross-disease conformal recalibration with small fine-tuning samples from each new disease

### Layer 5.4 — Post-Hoc Energy Flag

- Source: Energy score (Liu 2020) computed on L7 logits
- Output: fast pre-filter — high-energy inputs flagged before conformal layer invoked
- Cost: zero overhead beyond logits

### Pass Criteria for Decision 5 (binding GO/NO-GO per Charter §5.3)

1. **V0-V1 (within-cohort):** OOD detection AUROC ≥ 0.80 on held-out cell lines
2. **V3-V4 (preclinical translation):** OOD detection AUROC ≥ 0.70 on PDX/organoid shifts
3. **V5 (clinical retrospective):** Calibration error (ECE) ≤ 0.05 on patient predictions
4. **V6 (cross-disease):** Aleatoric/epistemic decomposition correctly attributes ≥70% of failed predictions to epistemic uncertainty (rather than aleatoric)

If any of V0-V6 pass criteria fail, **Decision 5 architecture must be revised before INTERCEPTA Layer 5 publication.**

### What Decision 5 Does NOT Commit To

To be honest about scope:
1. **Specific conformal non-conformity measure.** López-De-Castro tested 3 variants; the optimal for INTERCEPTA's drug response context will be a Layer 5 ablation.
2. **Specific energy temperature T.** Liu 2020 default T=1 may not be optimal; will be tuned in Layer 5.
3. **Exact ensemble size N.** Default N=5 may be revised based on Layer 5 compute-quality trade-off.
4. **OOD threshold for clinical deployment.** Setting the abstain-vs-predict threshold is a regulatory and clinical-context decision, not a Layer 1 architectural decision.

---

## What This Synthesis Does NOT Resolve

Honest gaps that propagate to Layer 5 implementation:

1. **The drug response OOD benchmarking gap (Pattern F).** No literature exists; INTERCEPTA must benchmark its own Q5 stack on its own drug response data.

2. **Cross-disease conformal calibration without held-out labels.** Open methodological question; possible Layer 5 contribution.

3. **FM-based OOD detection.** Unbenchmarked; possible INTERCEPTA novelty if FMs win Decision 1 v2 ablations.

4. **Clinical UX of dual aleatoric/epistemic uncertainty.** Beyond Layer 1 scope; requires user research with clinicians.

These are knowable but require Layer 5 implementation, not more Layer 1 reading.

---

## Drift Catalog This Phase 3 Cycle

- **New drift instances introduced:** 0
- **Cross-reference contamination fixed:** Theunissen note's prior reference to fabricated "Khoshchehreh" replaced with verified López-De-Castro citation (drift instance #31 caught real-time during Phase 3, corrected before propagating)
- **Anchor depth audit:** Engelmann (279→1983w), Liu (206→1871w), Theunissen (417→2028w) all brought to Q1-Q3 standard
- **Methodological discipline:** every claim primary-source verified before integration into synthesis

---

— Claude (CSO), 2026-05-10 (Phase 3 synthesis)
