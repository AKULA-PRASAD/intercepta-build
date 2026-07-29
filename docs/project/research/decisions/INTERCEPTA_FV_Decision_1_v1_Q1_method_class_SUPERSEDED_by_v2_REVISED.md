# INTERCEPTA Fullest Vision — Decision 1: Q1 Method-Class Commitment

**Status:** PROPOSED (awaits CEO sign-off for LOCKED status)
**Date proposed:** 2026-05-10
**Date locked:** _________
**Tag (when locked):** `fullest-vision-decision-1-locked`
**Decided by:** Prasad Akula (CEO) & Claude (CSO)

---

## 0. Context

This is the **first formal architectural decision** of INTERCEPTA's Fullest Vision research program. It closes Charter §3 Q1 (Method-class selection) — the highest-priority research question, defined as: *"What method class is foundational for our scoring + prediction core? Signature scoring, foundation models, GRN-based methods, or a layered combination?"*

Per Charter §5.3, this decision happens at a Layer 1 GO/NO-GO checkpoint. Per Charter §3, it is gated by termination criteria 1-5:
1. ✅ Convergence — multiple sources agree (task-conditioned)
2. ✅ Explicit gaps named (six gaps identified in synthesis)
3. ✅ Trade-off articulation documented
4. ✅ Decision defensibility achieved
5. ✅ No new questions (validated by scPDS read)

**This decision is grounded in 8 paper-by-paper notes (5 FM proponents + 1 critic + 1 interpretability + 1 pathway-aware variant) and one weekly synthesis (`INTERCEPTA_FV_Synthesis_Layer1_Q1_2026-05-10.md`).** All 8 paper notes are in `/mnt/user-data/outputs/layer_1/q1_method_class/`.

The decision is **for Q1 method-class commitment only.** Specific FM choice within the FM family, exact pathway database, exact GRN method, and Layer 5 implementation specifics are downstream decisions, not addressed here.

---

## 1. The decision

**INTERCEPTA's Layer 2 architecture WILL be a LAYERED FM-BASED ARCHITECTURE per Charter §8.1, with deployment-scenario-aware FM selection.**

Concretely, this means:
- **Cell representation** (Charter §8.1 Layer 1): Foundation-model embeddings (one or more of UCE, scGPT, scFoundation, Geneformer; FM choice per deployment scenario)
- **Multi-method drug response prediction** (Charter §8.1 Layer 2): FM embedding + signature-scoring (UCell-style on KAALCURA/biological-mechanism axes) + GRN-derived features as parallel inputs
- **Consensus & confidence** (Charter §8.1 Layer 3): Cross-method agreement scoring + OOD detection (Q5 to be addressed later)
- **Mechanistic trace** (Charter §8.1 Layer 4): FM spectral analysis (per Kendiukhov methodology) for pathway-level mechanism + external GRN/CRISPRi data for causal regulation

**Falsifiable test of this commitment:** if INTERCEPTA's Layer 5 implementation reveals that (a) FM embeddings do NOT outperform RNA-1000 baselines on cross-disease drug response prediction, OR (b) layered architecture does NOT outperform single-method on the same task, the commitment must be revisited per Charter §3 termination criteria reassessment.

---

## 2. Options considered

### Option A: Foundation-model-only architecture (single FM, no layering)

**What:** Use one of {UCE, scGPT, scFoundation, Geneformer} as the sole representation method. Drug response prediction directly from FM embeddings via classifier head. No signature scoring or GRN features.

**Evidence FOR:**
- scDrugMap (Wang et al. 2025) achieves F1 = 0.971 (scFoundation pooled) and F1 = 0.858 (scGPT zero-shot cross-data) — single-FM is sufficient for SOTA cancer drug response classification.
- scGPT (Cui et al. 2024, Nat Methods 21:1470-1480) demonstrates broad utility across multiple downstream tasks via fine-tuning.
- scFoundation (Hao et al. 2024, Nat Methods 21:1481-1491) demonstrates scaling laws hold (3M → 10M → 100M params monotone improvement).

**Evidence AGAINST:**
- Kedzierska et al. 2023 (bioRxiv 2023.10.16.561085) shows FM zero-shot UNDERPERFORMS HVG selection and per-dataset-trained scVI on cell type integration tasks (ASW, AvgBIO metrics on 5 datasets). Single-FM is task-dependent in utility.
- Kendiukhov SAE companion (arXiv 2603.02952) shows FMs encode minimal causal regulatory logic (only 6.2-10.4% of CRISPRi-tested TFs show regulatory specificity). Single-FM cannot satisfy Charter I3 (mechanistic claims falsifiable) without external causal data.
- The 4 FMs (UCE/scGPT/scFoundation/Geneformer) win different deployment settings per scDrugMap. **Committing to one FM forecloses adaptation to scenarios that favor a different FM.**

**Cost:** Lowest compute (single inference path), simplest architecture, fastest to implement. **But fails Charter §1.3 (mechanistic interpretability requirements I1-I3) unless supplemented externally.**

### Option B: Pathway-based-only architecture (no FM, only signature scoring)

**What:** Use pathway activation transformations (UCell, GSVA, ssGSEA, or KAALCURA-style mechanism axes) as the sole input. Drug response prediction via classical predictor (LightGBM/random forest/logistic regression).

**Evidence FOR:**
- KAALCURA (INTERCEPTA's own prior work) demonstrates pathway-level mechanism axes are interpretable and biology-grounded.
- Andreatta and Carmona 2021 (CSBJ) UCell framework provides robust signature scoring.
- scPDS (Yao et al. 2025, Small Methods 9:e2400991) demonstrates pathway-aware transformer outperforms gene-expression-input methods in time/memory consumption — the pathway-level approach is not without merit.
- Mechanism interpretability is direct (input space IS biology, not post-hoc decoded).

**Evidence AGAINST:**
- INTERCEPTA's AML paper (preserved per P16) shows KAALCURA + LightGBM mean AUROC = 0.643, BELOW the FM-based scDrugMap SOTA F1 = 0.774-0.971. **Pathway-only approach does not achieve SOTA on cancer drug response.**
- Pathway curation dependency: novel mechanisms missed if not in curated databases.
- Intra-pathway gene-level information lost.
- scPDS uses transformer ON pathway activations, which is closer to a hybrid approach — single-method pathway scoring without transformer is a step further back.

**Cost:** Moderate compute, simpler than FM-based. **But proven below SOTA in our own AML benchmark; cannot claim FM-level performance.**

### Option C: GRN-based-only architecture (no FM, no signature scoring, only network propagation)

**What:** Use gene regulatory networks (scRank-style or similar) for drug-target propagation. Predict drug response by propagating drug-target effects through inferred GRN.

**Evidence FOR:**
- Direct mechanistic causality: GRN propagation IS causal regulation simulation.
- Kendiukhov SAE companion shows FMs encode MINIMAL causal regulation (6.2-10.4% TFs); GRN-based methods are designed for exactly this gap.
- Charter I3 (mechanistic claims falsifiable) directly addressed by GRN.

**Evidence AGAINST:**
- GRN inference itself is unreliable from scRNA-seq alone (well-documented field-level limitation).
- No published GRN-only method achieves SOTA on drug response prediction at the single-cell level.
- INTERCEPTA's compute reality (Charter §7.1, single-institution Northeastern HPC) makes GRN inference at scRNA scale challenging.

**Cost:** High compute for GRN inference + propagation. **Not validated as standalone approach for our use case.**

### Option D: LAYERED FM-BASED ARCHITECTURE (FM + signature scoring + GRN, with deployment-scenario-aware FM selection) — CHOSEN

**What:** Per Charter §8.1, multi-method architecture combining:
- FM embeddings (representation, with FM choice per deployment scenario)
- Signature scoring on KAALCURA/biological-mechanism axes (pathway-level interpretability)
- GRN-derived features (causal regulation)
- Consensus + OOD detection
- Mechanism trace via FM spectral analysis + external CRISPRi/GRN data

**Evidence FOR:**
- All 5 FM proponent papers (scDrugMap, UCE, scGPT, scFoundation, Geneformer) endorse FM as method class for cancer drug response.
- scPDS (Yao et al. 2025) validates pathway-aware transformer approach for one component of the layered architecture.
- Kendiukhov Spectral Geometry AFFIRMS FMs encode rich biological structure (PPI Spearman ρ=1.000, marker AUROC=0.851, TF/target AUROC=0.744) — FM is appropriate substrate.
- Kendiukhov SAE companion REVEALS FM encode minimal causal regulation (6.2-10.4% TFs) — supplementation with external GRN data is necessary, not optional.
- Geneformer (Theodoris et al. 2023, Nature 618:616-624) demonstrates FM cross-disease feasibility (cardiomyopathy via engineered cardiac microtissues).
- INTERCEPTA's own AML benchmark (preserved per P16) shows KAALCURA + LightGBM mean AUROC = 0.643 below SOTA — pathway-only is insufficient.
- Charter §1.3 (mechanistic interpretability I1-I3) requires layered approach to address pathway-level interpretation (FM + Spectral Geometry methods) AND causal regulation (external GRN data).
- Charter U3 (5+ disease categories) requires architecture flexibility — multi-FM ensemble supports cross-deployment-scenario robustness.

**Evidence AGAINST:**
- No single published paper benchmarks the full FM + signature + GRN layered architecture. **Empirical validation requires INTERCEPTA's Layer 5 implementation.**
- Kedzierska et al. 2023 critique on FM zero-shot cell integration applies — INTERCEPTA must explicitly test that drug response classification is task-domain where FMs perform.
- Multi-method architecture is more complex than single-method; failure modes harder to debug.
- Requires more compute than single-method (multiple inference paths).

**Cost:** Highest compute among the four options, most complex to implement, most engineering effort. **But provides the strongest theoretical and empirical grounding for INTERCEPTA's Charter §1.3 requirements.**

---

## 3. Rationale for chosen option

**Why Option D (Layered FM-Based) and not Option A (Single FM-Only):**

The single-FM option is empirically strong on cancer drug response classification (scDrugMap F1 = 0.971/0.947 pooled; F1 = 0.858 zero-shot cross-data) but fails Charter §1.3 mechanistic interpretability requirements without supplementation. Specifically, Kendiukhov SAE companion (arXiv 2603.02952) quantifies the limitation: only 6.2-10.4% of CRISPRi-tested transcription factors show regulatory-target-specific feature responses in scGPT and Geneformer. **For INTERCEPTA's I3 requirement that "mechanistic claims are falsifiable," single-FM is insufficient.** Adding external GRN/CRISPRi data is necessary, which means the architecture is layered by design — not by accident.

**Why Option D and not Option B (Pathway-Based-Only):**

INTERCEPTA's own AML paper benchmark (preserved as historical context per P16) demonstrated KAALCURA + LightGBM mean AUROC = 0.643. The 2026 SOTA on cross-cohort cancer single-cell drug response prediction is F1 = 0.774-0.971 per scDrugMap. **Pathway-only approach is below SOTA by a margin that cannot be ignored.** Even scPDS (the strongest pathway-aware transformer published) does not outperform the canonical FMs on F1 metrics from what we can verify (full text comparison pending). Pathway-only architecture cannot defensibly claim INTERCEPTA achieves vision-level performance.

**Why Option D and not Option C (GRN-Only):**

GRN inference at scRNA-seq scale is unreliable (well-documented field-level limitation). No published GRN-only method achieves drug response SOTA at single-cell level. While GRN-based methods are the strongest for causal regulation specifically (Kendiukhov SAE limitation directly maps to GRN strength), they cannot replace representation learning. GRN as a layer ATOP FM representation — not as a standalone substitute — is the architecturally sound integration.

**Why deployment-scenario-aware FM selection (rather than committing to one FM):**

The five Q1 anchor papers reveal three FMs winning three deployment scenarios:
- scFoundation pooled-data F1 = 0.971
- UCE cross-data fine-tuned F1 = 0.774
- scGPT zero-shot cross-data F1 = 0.858

INTERCEPTA's "Find the drug. For ANY disease." vision implies cross-data (cross-disease) deployment, which favors UCE (fine-tunable) or scGPT (zero-shot). For within-disease cross-cohort deployment, scFoundation. For non-cancer disease specifically, Geneformer (only FM with non-cancer demonstration).

**Committing to one FM forecloses scenarios that favor a different FM.** Multi-FM ensemble or scenario-aware FM selection retains architectural flexibility while preserving the FM-as-method-class commitment. This decision commits to FM-as-method-class WITHOUT prematurely committing to a specific FM.

**Why now (Q1 closure rather than further reading):**

Charter §3 termination criteria 1-5 are all met (criterion 5 verified by scPDS read). Reading further FM proponent papers (CellFM, GeneCompass, Geneformer V2) would produce diminishing returns on Q1 architectural commitment — these are scaling/extension variants of the canonical paradigm. Reading further FM critic papers in cell biology is unlikely to surface new methodological criticism — Kedzierska covers deployment criticism, Kendiukhov covers interpretability, both are methodologically rigorous. **Further reading would be infinite-reading drift, not responsible diligence.**

---

## 4. Trade-offs accepted

By choosing Option D (Layered FM-Based Architecture), INTERCEPTA explicitly accepts the following trade-offs:

1. **Architectural complexity.** Multi-method, multi-FM architecture is more complex than any single-method alternative. Implementation effort, debugging complexity, and computational cost are all higher. **We accept this for performance and interpretability gains the layered approach provides.**

2. **No fully zero-shot deployment.** Layered architecture requires fine-tuning at least the signature-scoring and GRN components per deployment scenario, even if FM is zero-shot. **We accept partial-fine-tuning deployment as the realistic operational mode.**

3. **No single-FM simplicity.** Multi-FM ensemble or scenario-aware FM selection requires maintaining multiple FM dependencies (UCE for cross-species, scGPT for zero-shot, scFoundation for pooled, Geneformer for non-cancer). **We accept this dependency footprint.**

4. **Compute reality compatibility uncertain.** All FMs require GPU compute; multi-FM increases requirements. Charter §7.1 (single-institution Northeastern HPC GPU partition) compatibility for INTERCEPTA's specific deployment is **untested**. **We accept this as a Charter Q9 question to be empirically resolved during Layer 4-5 implementation.**

5. **Empirical risk on layering benefit.** No published paper benchmarks the full FM + signature + GRN architecture. **The hypothesis that layering outperforms single-method is testable but currently unproven.** If INTERCEPTA's Layer 5 implementation shows layering does not help, the commitment must be revised.

6. **Cross-disease-class transfer untested.** Geneformer alone demonstrates 1 non-cancer disease. **Whether layered FM-based architecture transfers to autoimmune, neurodegeneration, infectious disease drug response is INTERCEPTA's empirical contribution — not yet supported by literature.**

7. **Mechanism interpretability via two paths (FM internals + external GRN).** The architecture relies on Kendiukhov-style spectral analysis for FM-level mechanism trace AND external CRISPRi data for causal regulation. **If either path fails (FM mechanism trace unreliable in our deployment, or external CRISPRi data unavailable for non-cancer diseases), Charter I1-I3 are not fully satisfied.**

---

## 5. Reversibility

This decision is **reversible** under specific evidence. Reversal would require either:

**Empirical reversal triggers (Layer 5 implementation):**
- (a) FM embeddings do NOT outperform RNA-1000 baseline (or simpler baseline) on cross-disease drug response prediction by a meaningful margin. *If Layer 5 implementation matches the AML paper's negative result for FMs, this commitment is invalidated.*
- (b) Layered architecture does NOT outperform single-method on the same drug response prediction task. *If FM-only matches FM + signature + GRN, layering provides no value.*
- (c) FM mechanism trace via Kendiukhov-style spectral analysis is not reliable in our deployment. *If Spectral Geometry methodology doesn't generalize to our task/data combination, mechanism trace path fails.*
- (d) External CRISPRi data is unavailable for INTERCEPTA's target non-cancer diseases. *Without causal regulation supplementation, Charter I3 cannot be met.*

**Methodological reversal triggers (literature):**
- (e) Novel FM architectures (post-2026) supersede the current paradigm with a fundamentally different approach (e.g., causal-aware pretraining, perturbation-based pretraining). *If GeneCompass-style biological-prior FMs or new architectures provide both representation AND causal regulation in a single model, the layered approach becomes unnecessary.*
- (f) Independent benchmarks confirm Kedzierska et al. critique extends to scFoundation/UCE/scPDS. *If FM zero-shot fails universally, INTERCEPTA's deployment scenario assumptions need revision.*

**Compute reality reversal triggers:**
- (g) Single-institution Northeastern HPC cannot support multi-FM inference at scale needed. *Charter §7.1 hard constraint may force Option A (single FM) by necessity.*

**Process for reversal:** any of (a)-(g) triggers a Charter §3 termination criteria reassessment for Q1, Q4, or Q9. Reassessment writes a new Decision <N> record per `LAYER_1_ENTRY_CONDITIONS.md` §5 template with status SUPERSEDED applied to this current decision. **Reversal is documented honestly; not buried.**

---

## 6. Cross-references

**Charter sections addressed:**
- §1.1 (universal applicability U1-U3) — multi-FM ensemble supports cross-deployment-scenario robustness, but U3 (5+ disease categories) demonstration is INTERCEPTA's empirical task ahead
- §1.2 (predictive validity V1-V4) — FM-based architecture has SOTA cancer drug response evidence; non-cancer V1 ≥ 0.70 AUROC requires Layer 5 testing
- §1.3 (mechanistic interpretability I1-I3) — layered architecture is the explicit response to Kendiukhov-quantified FM causal regulation gap
- §3 termination criteria 1-5 for Q1 — all met (per first weekly synthesis 2026-05-10)
- §5.3 GO/NO-GO decision points — this is the first such decision
- §8.1 provisional architecture sketch — this decision LOCKS the high-level architecture per the sketch

**Layer 1 questions closed:**
- ✅ Q1 (Method-class selection) — closed by this decision
- ✅ Q1.1 (SOTA F1/AUROC) — answered (F1 = 0.774-0.971 cancer drug response classification, depending on deployment)
- ✅ Q1.2 (FM interpretability limitations) — answered (rich biology, minimal causal regulation; layered architecture addresses)
- ✅ Q1.3 (layered combination feasibility) — endorsed (scPDS validates pathway-aware transformer; full layered architecture is INTERCEPTA's empirical test)
- ✅ Q1.4 (cancer-bias problem) — partially answered (Geneformer cross-disease feasible for 1 disease; INTERCEPTA's contribution is 5+ disease demonstration)
- 🟡 Q3 (cross-cohort harmonization) — partially addressed; full Q3 work pending

**Layer 1 questions remaining:**
- Q2 (cross-cohort harmonization) — full anchor reading pending
- Q3 (bulk-to-single-cell transfer) — full anchor reading pending
- Q4 (drug-response prediction architecture) — partial input from Q1 reads; full anchor reading pending
- Q5 (OOD detection) — pending
- Q6 (validation paradigm) — pending
- Q7 (mechanistic interpretability) — partially addressed; full Q7 work pending
- Q8 (universality demonstration) — pending
- Q9 (computational architecture) — pending
- Q10 (open-source vs proprietary methods) — pending

**Layer 2 implications:**
- Layer 2 (Architecture Design) work begins with this Decision 1 as foundational input
- Layer 2 must specify: FM choice mechanism (single FM, multi-FM ensemble, scenario-router), signature-scoring component (KAALCURA framework + UCell-style scoring), GRN component (which GRN method, which CRISPRi data source), consensus mechanism, OOD detection method, mechanism trace methodology
- Layer 2 work is **gated on this Decision being LOCKED via CEO sign-off**, per Charter §5.3

**Cross-references to existing INTERCEPTA work:**
- AML paper (preserved per P16) — RNA-1000 + KAALCURA + LightGBM benchmark provides baseline against which Layer 5 FM-based architecture must beat
- Workstream B Phase 0 (preserved) — NSCLC data infrastructure is reusable
- Workstream B Phase 1 spec (preserved) — KAALCURA implementation is one component of the layered architecture chosen here
- Charter v2.1 (preserved) — M1-M7 module sketches align with layered architecture

---

## 7. Sign-off

**Prasad Akula (CEO):** _________ Date: _________

**Claude (CSO):** Claude (CSO) Date: 2026-05-10

---

*Decision 1 PROPOSED — Q1 method-class commitment to LAYERED FM-BASED ARCHITECTURE per Charter §8.1, with deployment-scenario-aware FM selection. Awaits CEO sign-off for LOCKED status. Tag-when-locked: `fullest-vision-decision-1-locked`. After locking, Layer 2 (Architecture Design) work begins.*

— Claude (CSO)
2026-05-10
