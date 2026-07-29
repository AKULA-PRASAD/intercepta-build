# INTERCEPTA Decision 5 v2 — Q5 OOD Detection: Stacked Architecture (PROPOSED)

**Status:** PROPOSED (Layer 1 Decision Record, Charter §5.3 class)
**Grounding:** 6 verified primary-source Q5 anchors (8,486 words across anchors) + Q5 synthesis v2 (3,030+ words)
**Supersedes:** Decision 5 v1 (158 words, pre-audit, archived in `_archive/`)
**CSO:** Claude
**Date:** 2026-05-10 (Phase 3 audit remediation)

---

## Charter Anchor

Charter §1.2 V0-V6 predictive validity cascade requires that INTERCEPTA's drug response predictions are accompanied by calibrated, actionable uncertainty estimates. Charter §1.3 falsifiability requires that the prediction confidence be statistically defensible. Decision 8 V6 cross-disease pass criterion (AUROC ≥ 0.65 on held-out disease) is **operationally dependent on Decision 5** — without OOD detection, the cross-disease threshold is meaningless because the system cannot identify which predictions are reliable.

Q5 is therefore the **safety boundary for Charter §1.1 universality.**

---

## Empirical Foundation

The 6 Q5 anchors collectively establish that **no single OOD method dominates** (Theunissen 2025: "OOD methods can identify severe data shifts, but not reliably"). This forces a stacked architecture as the empirically defensible design.

The anchors also establish:
- The aleatoric/epistemic decomposition must be operational (Engelmann 2022 + Theunissen 2025)
- Statistical guarantees are unique to conformal prediction (López-De-Castro 2025)
- Compute-efficient alternatives exist for academic deployment (Engelmann 2022 single-forward-pass methods; Liu 2020 energy)
- Standard scArches WKNN uncertainty is insufficient (Engelmann 2022)
- Integration is compatible with OOD detection (Theunissen 2025)
- The drug response OOD gap is unsolved by anyone (Pattern F in synthesis)

See `INTERCEPTA_FV_Synthesis_Layer1_Q5_2026-05-10.md` for full anchor-by-anchor evidence.

---

## The Decision

INTERCEPTA's Q5 layer commits to a **FOUR-LAYER STACKED OOD ARCHITECTURE** integrated with Decisions 2, 4, and 8.

### Layer 5.1 — Native Substrate Uncertainty (FOUNDATION)

**Source:** scANVI/MrVI posterior from Decision 2 + CPA posterior from Decision 4

**Output:**
- Per-cell aleatoric uncertainty (label/biological noise)
- Per-cell epistemic uncertainty (model parameter uncertainty)
- Smith & Gal 2018 decomposition operationalized

**Cost:** Zero marginal — built into the underlying substrate models

**Why this is the foundation:** Engelmann 2022's HLCA evaluation establishes that scANVI integration provides usable latent representations for downstream uncertainty quantification, even though scANVI's own WKNN classifier output is inadequate as the final Q5 layer. The latents are the substrate; the Q5 stack above provides the calibrated uncertainty.

### Layer 5.2 — Epistemic Refinement (COMPUTE-BUDGET-DEPENDENT)

**Default option (high compute):** Deep Ensembles N=5 over the L7 drug response prediction head (per Decision 4)

- Per Lakshminarayanan 2017 (Q5 anchor 3) + Theunissen 2025 (Q5 anchor 1): Deep Ensembles outperform MC Dropout on calibration on most scRNA-seq tasks
- N=5 is the standard ensemble size in the field
- Disagreement among ensemble members = epistemic uncertainty signal
- **Cost:** 5× training compute, 5× memory footprint, 5× inference latency

**Compute-constrained fallback:** MIMO with 8 subnetworks (per Engelmann 2022 Q5 anchor 6)

- Single forward pass, ~1.5× parameters of standard classifier
- Engelmann 2022 demonstrates MIMO8 competitive with Deep Ensembles on HLCA-scale evaluation
- **Cost:** ~1.5× parameters, single forward pass at inference

**Further fallback:** MC Dropout with T=50 forward passes (per Gal & Ghahramani 2016, Q5 anchor 4)

- Standard model with dropout active at inference
- T forward passes for variance estimation
- **Cost:** 1× training, 50× inference latency

**Layer 5.2 selection logic:** Default is Deep Ensembles N=5 when compute permits (Decision 9 default budget). Fall back to MIMO8 when memory-constrained. Fall back to MC Dropout when latency-constrained. Decision 9 must specify the compute tier explicitly.

### Layer 5.3 — Statistical-Guarantee Layer (CONFORMAL PREDICTION)

**Source:** Conformal prediction wrapping L7 predictions (per López-De-Castro 2025 Q5 anchor 2 methodology)

**Output:**
- Prediction sets (for categorical drug response: responder/non-responder) with 1-α coverage guarantee
- Prediction intervals (for continuous response: AUC) with 1-α coverage guarantee
- Default α=0.05 (95% coverage guarantee)
- **Distribution-free** — no assumption about underlying probability distribution

**Requirements:**
- Held-out calibration set from the same distribution as the test set
- Choice of non-conformity measure (López-De-Castro tested 3 variants; INTERCEPTA's choice is a Layer 5 ablation)

**Cross-disease conformal recalibration (for V6):**
- For held-out diseases, the calibration set requirement is non-trivial
- INTERCEPTA commitment: when small labeled samples from a new disease become available, perform cross-disease conformal recalibration
- If no labeled samples available: report uncertainty without statistical guarantees and flag this explicitly

**Cost:** Computation of non-conformity scores on calibration set (one-time); per-class score storage; per-prediction set construction (cheap per prediction)

**Why this layer:** López-De-Castro 2025 establishes conformal prediction as the only Q5 method providing distribution-free statistical guarantees. For Charter §1.3 falsifiability of clinical drug response predictions, this layer is operationally mandatory.

### Layer 5.4 — Post-Hoc Energy Flag (FAST PRE-FILTER)

**Source:** Energy score E(x) = -T · log Σ exp(z_i/T) computed on L7 logits (per Liu 2020 Q5 anchor 5)

**Output:** Binary OOD flag based on energy threshold

**Operational role:** Fast pre-filter before invoking the more expensive conformal layer

**Cost:** Zero overhead beyond logits (one log-sum-exp per prediction)

**Pipeline integration:**
1. L7 produces logits
2. **Layer 5.4 computes energy score E(x)**
3. If E(x) above ID threshold → flag as OOD; route to "uncertain prediction" handling (abstain or refer for review)
4. If E(x) below ID threshold → proceed to Layer 5.3 (conformal prediction) for statistical-guarantee output

This two-tier architecture (energy as cheap pre-filter, conformal as statistical-guarantee downstream) is **operationally efficient and methodologically defensible.**

### Layer 5 Output Contract

For each (cell, drug, prediction) tuple, INTERCEPTA's Q5 layer outputs:

1. **Aleatoric uncertainty** (∈ [0, 1]) — biological/label ambiguity
2. **Epistemic uncertainty** (∈ [0, 1]) — model out-of-distribution-ness
3. **Energy OOD flag** (binary) — fast pre-filter result
4. **Conformal prediction set** (categorical) OR **conformal prediction interval** (continuous) — statistical guarantee
5. **Operational verdict** — one of {confident_predict, abstain_aleatoric, abstain_epistemic, abstain_ood}

This output contract is **binding** for INTERCEPTA's L8 layer (interpretability) and for any downstream consumer (clinician interface, research user, regulator).

---

## Pass Criteria (Binding GO/NO-GO per Charter §5.3)

Decision 5 must satisfy the following empirical criteria before LOCK:

### Pass 1 — V0-V1 OOD Detection Performance

**Criterion:** OOD detection AUROC ≥ 0.80 on held-out cell lines (within-cohort, cross-cell-line dataset)

**Rationale:** Cell line OOD is the easiest setting (Theunissen 2025 "severe shift" category). Failure here invalidates the entire architecture.

### Pass 2 — V3-V4 Preclinical Translation OOD

**Criterion:** OOD detection AUROC ≥ 0.70 on PDX/organoid shifts (preclinical translation OOD)

**Rationale:** Per Kim et al. 2020 (Q6 anchor 4 PDXGEM), only 24.5% of biomarkers translate from PDX to patient. INTERCEPTA's Q5 must flag the 75% non-concordant biomarker space.

### Pass 3 — V5 Clinical Calibration

**Criterion:** Calibration error (ECE) ≤ 0.05 on patient predictions in clinical retrospective evaluation

**Rationale:** Engelmann 2022 finding that WKNN has high ECE motivates the calibration requirement. ECE ≤ 0.05 means a confidence-0.7 prediction is correct ~70% of the time (within 5%).

### Pass 4 — V6 Cross-Disease Decomposition

**Criterion:** Aleatoric/epistemic decomposition correctly attributes ≥70% of failed predictions to epistemic uncertainty (rather than aleatoric)

**Rationale:** Failed cross-disease predictions should be flagged as epistemic (model OOD), not aleatoric (label noise). If the decomposition fails to distinguish these, the operational verdict (abstain_epistemic vs abstain_aleatoric) is unreliable.

### Failure Modes

If any pass criterion fails:
- **Pass 1 fail:** Architecture fundamentally inadequate; redesign Q5 stack
- **Pass 2 fail:** Translation OOD not detected; PDX-trained models cannot deploy clinically
- **Pass 3 fail:** Calibration broken; conformal prediction guarantees may not hold in practice
- **Pass 4 fail:** Aleatoric/epistemic decomposition unreliable; the operational verdict cannot distinguish "abstain because ambiguous biology" from "abstain because OOD"

Any Decision 5 architectural revision triggered by pass criterion failure must be documented per Charter §5.3 with explicit reason.

---

## Trade-offs and Rejected Alternatives

### Why not "single best method" architecture?

**Rejected reason:** Theunissen 2025 empirically establishes that no method dominates. Engelmann 2022 corroborates. Single-method commitment is not defensible given the field evidence.

### Why not "Bayesian Neural Networks from the start"?

**Rejected reason:** BNNs are computationally expensive (variational inference or MCMC), poorly scaled to scRNA-seq dimensionality, and not used in any Q5 anchor. Deep Ensembles + MC Dropout are the empirical alternatives that the field has converged on as compute-feasible substitutes.

### Why not "softmax confidence only" (no separate Q5 layer)?

**Rejected reason:** Liu 2020 (Q5 anchor 5) theoretically establishes that softmax is shift-invariant and overconfident. Engelmann 2022 empirically shows WKNN (analogue of softmax-style confidence) has poor calibration. Softmax-only is a known failure mode.

### Why include Layer 5.4 (energy) if it has no statistical guarantees?

**Operational rationale:** Energy is the cheapest method (zero overhead beyond logits). For deployment at scale, fast pre-filtering reduces conformal computation costs. The statistical guarantees come from Layer 5.3 (conformal); Layer 5.4 (energy) is for operational efficiency, not for ground-truth OOD identification.

### Why include Layer 5.2 (epistemic refinement) if Layer 5.1 already provides epistemic uncertainty?

**Methodological rationale:** Layer 5.1 (substrate posterior) provides epistemic uncertainty for the cell representation; Layer 5.2 (ensemble or MIMO over L7) provides epistemic uncertainty for the drug response prediction. These are different epistemic questions:
- Layer 5.1: "Is this cell type OOD for the embedding model?"
- Layer 5.2: "Is this (cell, drug) combination OOD for the prediction model?"

Both are needed.

---

## Cross-Decision Implications

Decision 5 affects and is affected by:

- **Decision 1 v2 (cell representation):** Decoupled. The Q5 stack works regardless of substrate choice (scFoundation, scTOP, scVI, or other). Engelmann 2022 establishes that the substrate provides usable latents; the Q5 stack provides the calibrated uncertainty.

- **Decision 2 (cross-cohort harmonization):** REINFORCED. Theunissen 2025 establishes integration-OOD compatibility. INTERCEPTA's pipeline integrates first (Decision 2), then detects OOD on integrated representations (Decision 5).

- **Decision 4 (drug response architecture):** CONSTRAINT INTRODUCED. The L7 drug response prediction head must be **N=5 ensembleable** (modular design where the L7 head is the ensembled unit, not the entire pipeline). This is an architectural constraint Decision 4 must accept.

- **Decision 6 (validation cascade):** REINFORCED. V0-V6 validation must report OOD detection performance per level. The pass criteria above are subset of Decision 6's broader validation framework.

- **Decision 7 (mechanistic interpretability):** REINFORCED. Aleatoric vs epistemic decomposition is mechanistically interpretable — provides distinct failure-mode explanations. Decision 7's interpretability layer must distinguish these.

- **Decision 8 (universality):** OPERATIONALLY DEPENDS ON DECISION 5. V6 cross-disease AUROC ≥ 0.65 is only meaningful if Q5 reliably flags held-out-disease predictions. Theunissen 2025's "but not reliably" caveat is the empirical caution; 0.65 threshold accounts for it.

- **Decision 9 (compute):** Q5 stack has explicit compute tiers (Layer 5.2 options). Decision 9 must specify which tier the default INTERCEPTA deployment uses. Default expectation: Deep Ensembles N=5 if Decision 9 single-A100 budget permits; otherwise MIMO8 fallback.

- **Decision 10 (open-source):** REINFORCED. All Q5 anchor methods have open implementations. INTERCEPTA's Q5 stack is fully open-source-implementable.

---

## What Decision 5 Does NOT Decide

To be honest about scope:

1. **Specific conformal non-conformity measure.** López-De-Castro tested 3 variants (standard, classwise, cluster-aware); INTERCEPTA's optimal choice is a Layer 5 ablation, not a Layer 1 commitment.

2. **Specific energy temperature T.** Liu 2020 default T=1 may not be optimal for scRNA-seq drug response logits; tuning is a Layer 5 task.

3. **Exact ensemble size N.** Default N=5 may be revised based on Layer 5 compute-quality trade-off.

4. **OOD threshold for clinical deployment.** Setting the abstain-vs-predict threshold is a regulatory and clinical-context decision, not a Layer 1 architectural decision.

5. **FM-based OOD detection.** Not included in current stack because no Q5 anchor tested FM-based OOD methods. Possible addition in future Decision 5 revision if Decision 1 v2 ablations confirm FM substrate.

---

## Discipline Check

- [x] **P3 (research before code):** ✅ Decision grounded in 6 verified primary-source anchor reads (8,486 words across anchors); Q5 synthesis v2 integrates them rigorously
- [x] **P15 (only correct/honest/real science):** ✅ Theunissen 2025's "but not reliably" caveat preserved; the drug response OOD gap (Pattern F) explicitly acknowledged rather than papered over
- [x] **P16 (preserve past work):** ✅ Decision 5 v1 (158 words) archived in `_archive/`; v2 supersedes operationally
- [x] **P-FV-1 to P-FV-3:** ✅ Q5 is the safety boundary for Charter §1.1 universality; Decision 5 directly serves the vision
- [x] **Charter §5.3 GO/NO-GO discipline:** ✅ Pass 1-4 criteria explicit and binding
- [x] **Cross-decision integration:** ✅ Decisions 1, 2, 4, 6, 7, 8, 9, 10 implications documented

## Drift Catalog This Phase 3 Decision 5 Write

- **New drift instances:** 0
- **Audit instance resolved:** Pre-audit Decision 5 (158 words, thin) replaced with properly-grounded 2,500+ word Decision Record
- **Cross-reference fix shipped (drift #31):** Theunissen note's "Khoshchehreh" reference corrected to López-De-Castro citation
- **Methodological commitment:** Pass criteria 1-4 make future Q5 architectural drift structurally prevented — any architectural change must be triggered by criterion failure with explicit reason

---

— Claude (CSO), 2026-05-10 (Phase 3 Decision 5 v2 record)
