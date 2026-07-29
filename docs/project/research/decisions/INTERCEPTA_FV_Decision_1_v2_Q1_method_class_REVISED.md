# INTERCEPTA Decision 1 v2 — Q1 Method-Class Commitment (REVISED)

**Status:** REVISION PROPOSED (Layer 1 Decision Record, Charter §5.3 class)
**Supersedes:** Decision 1 v1 (`INTERCEPTA_FV_Decision_1_Q1_method_class.md`, 2,709 words, PROPOSED 2026-05-10)
**Triggered by:** Souza & Mehta 2026 evidence from Q8 anchor read (Phase 6 audit remediation)
**CSO:** Claude
**Date:** 2026-05-10 (Phase 6)
**Per P16:** v1 file preserved in archive; v2 is the operational record going forward

---

## Why a Revision Is Required

The original Decision 1 (v1) committed to a **LAYERED FM-BASED ARCHITECTURE** with FM embeddings as the cell representation substrate. The v1 grounding was 8 paper-by-paper notes for Q1 (FM proponents, critics, pathway-aware variants). At v1 closure, the dominant evidence supported FM-based architecture conditional on per-scenario FM selection.

**Q8 Phase 6 re-do introduced new evidence that v1 did not adequately weigh:**

Souza & Mehta 2026 (arXiv 2602.16696, Boston University Physics / Mehta lab; NIH NIGMS R35GM119461 + CZI funded) demonstrate:
1. **scTOP (parameter-free, zero free parameters) matches TranscriptFormer on Tabula Sapiens 2.0** at mean macro F1 of 0.899 vs TranscriptFormer's 0.910/0.907 — essentially tied at the largest cell-type classification benchmark.
2. **scTOP beats FMs on cross-species annotation across all 8 mammalian species** including platypus.
3. **scTOP matches FMs on disease-state classification** (SARS-CoV-2 infected vs uninfected, 4 donors).
4. **Compute differential is staggering:** TranscriptFormer training requires ~100M+ cells on 1000 H100 GPUs; scTOP runs on a CPU with zero training.
5. **Manifold geometry analysis** suggests near-linear transcriptional geometry for biological directions — providing a theoretical explanation for why parameter-free methods work.

**Combined with the v1 "falsifiable test of this commitment" clause** (which explicitly anticipated revision if FM advantage failed to materialize), the v1 commitment to FM-based architecture is no longer **architecturally safe to lock pre-empirically.** The Charter §1.1 universality vision, the Charter §5.3 GO/NO-GO discipline, and the P15 "only honest science" principle all require that this revision be made openly rather than retained as an unrevisited commitment.

---

## What v2 Decides

**INTERCEPTA's cell representation layer (Charter §8.1 Layer 1) commits to a FRAMEWORK for substrate selection, not a fixed substrate.**

### Commitment 1 — Default Development Substrate

For initial INTERCEPTA development (Layer 5 first implementation cycle), the default substrate is:

- **scFoundation** (BiomapAI, 100M parameters, scRNA-seq-trained, scvi-tools-compatible, permissive license)

Rationale for the default choice: scFoundation is the largest open FM with the most permissive license and the most direct scvi-tools integration (Decision 2 compatibility). Choosing it as default does NOT commit to FM-based architecture; it commits to using a concrete FM substrate as one of the four paradigms under test (per Decision 8 Commitment 2).

### Commitment 2 — Co-Equal Baselines (BINDING)

Three baselines must be implemented **co-equally** with the default substrate, not as fallbacks:

**Baseline A — PCA + HVG + log-normalization (classical)**
- Top 2,000 highly variable genes (HVG)
- log1p normalization
- PCA to 50-100 components
- Single forward path; CPU-runnable

**Baseline B — scTOP-style parameter-free (Souza & Mehta methodology)**
- z-score normalization per cell
- Pseudo-bulk reference basis from labeled cell types
- Non-orthogonal linear projection for classification tasks
- ANOVA + PCA + logistic regression where needed (e.g., Tabula Sapiens 2.0 settings)
- Zero free parameters; CPU-runnable

**Baseline C — scVI / scANVI / MrVI (Yosef lab probabilistic VAE)**
- 30-50 dimensional latent space
- Batch covariate conditioning (per Decision 2 Q2 commitment)
- scvi-tools BSD-3 licensed; production-ready

These three baselines are NOT optional. Per Decision 8 Commitment 5 (Souza & Mehta methodological bar), INTERCEPTA cannot publish architectural claims of FM benefit without rigorous comparison to at least Baseline B with the same hyperparameter search budget at 25% scale.

### Commitment 3 — Decision Logic Based on Layer 5 Ablation Results

The architectural choice between scFoundation (default substrate) and Baselines A/B/C is **deferred to Layer 5 empirical evidence.** Specific decision rules:

- **If scFoundation wins by ≥5 percentage points AUROC** on the V0-V6 drug response prediction grid (Decision 6 cascade): keep FM as the primary substrate; Baselines remain as required ablation comparators in publications.
- **If parameter-free Baseline B wins or ties within 2 percentage points** on the same grid: **DEMOTE FMs from the primary substrate position**; Baseline B becomes primary; FMs become optional comparators.
- **If scVI Baseline C wins**: probabilistic VAE becomes primary; FMs become optional.
- **If results are scenario-dependent** (e.g., FM wins on cancer, parameter-free wins on I&I): INTERCEPTA commits to **explicit per-scenario substrate selection logic**, with the selection logic itself becoming a Layer 2 architectural component that requires its own Decision Record.

### Commitment 4 — Interface Stability

Regardless of which substrate ultimately wins, INTERCEPTA's Layer 3 module interface (Charter §8.1) remains stable:

- **Input:** anndata-style scRNA-seq object (cells × genes)
- **Output:** fixed-dimensional cell embedding (default: 512-dim; substrate can adapt internally)
- **Downstream:** L4-L8 (drug response prediction, OOD detection, patient aggregation, mechanistic interpretability) consume the embedding without knowing the substrate

This interface stability means that swapping substrates based on Layer 5 evidence is an O(1) architectural change, not a rebuild. **This is the most important architectural commitment of v2:** the swap-ability is what makes the deferred decision safe.

### Commitment 5 — Honest Stated Uncertainty (BINDING per P15)

As of May 2026, the published literature does NOT support a confident commitment to FM-based architecture for **drug response prediction specifically.** Every Q8 anchor tests classification, annotation, or disease-state tasks. **No Q8-relevant paper tests drug response prediction with FM-vs-parameter-free head-to-head.** This is the gap INTERCEPTA's Layer 5 must close.

**INTERCEPTA's publications and internal documentation must state this uncertainty openly** rather than asserting FM superiority on drug response. The honest scientific position is: "We don't know whether FMs help drug response prediction beyond properly-tuned parameter-free baselines; INTERCEPTA's Layer 5 results will tell us."

---

## What v2 Does NOT Change from v1

To be precise about scope:

1. **Layered architecture commitment** (Charter §8.1 multi-layer design) — UNCHANGED. The substrate is one layer; consensus, OOD, mechanism trace are other layers; v1's commitment to layered architecture is preserved.
2. **Signature-scoring + GRN-derived features as parallel inputs** to L7 drug response — UNCHANGED. These are complementary to substrate choice, not substitutes.
3. **Mechanistic interpretability via FM spectral analysis** (Kendiukhov methodology) — CONDITIONALLY UNCHANGED. If FMs win, spectral analysis applies. If parameter-free wins, mechanistic interpretability comes from gene-level attribution on the linear projections (which is actually easier and more interpretable).
4. **8 Q1 anchor reads** — UNCHANGED. The v1 grounding remains the literature foundation for the FM family. Souza & Mehta is a Q8 anchor (universality), not a Q1 anchor (method class); v2 incorporates Q8 evidence per cross-question integration.

---

## What v2 Does NOT Decide

To be honest about residual uncertainty:

1. **Which specific FM within Paradigm A is best.** Even if FMs win Layer 5, the choice among scFoundation / UCE / scGPT / Geneformer is a subsequent decision.
2. **Whether all four FMs in the v1 portfolio should be ensembled.** v1 anticipated multi-FM ensemble; v2 leaves this open pending Layer 5 ablations.
3. **Disease-area-specialized FM integration.** EVA-60M (Q8 anchor 4) is open-source and may be a better substrate for I&I deployments than general FMs. This is a Paradigm B question per Decision 8, not a Decision 1 v2 commitment.
4. **Patient-level aggregation strategy.** PaSCient-style attention (Q8 anchor 3) is the leading candidate but specific architecture (Decision 4 family) is decided separately.

---

## Termination Criteria for v2 Lock

Per Charter §5.3 GO/NO-GO discipline, v2 is LOCKED when:

1. **Layer 5 ablation infrastructure is in place** to run scFoundation vs Baselines A/B/C head-to-head on at least one V0 / V1 grid cell (within-dataset CV + cross-dataset)
2. **Baseline B (scTOP-style) is implemented and verified** to reproduce Souza & Mehta's reported numbers on Tabula Sapiens 2.0 within 2 percentage points (sanity check)
3. **Hyperparameter budget allocation is documented** showing Baseline B receives ≥25% of FM hyperparameter search compute (Decision 8 Commitment 5 binding requirement)
4. **CEO sign-off** on the v2 record per Charter §5.3

Until those four conditions are met, v2 remains in REVISION PROPOSED status.

---

## Why This Revision Is Not "Backing Down"

The CSO function is to make the most defensible architectural decisions for the Fullest Vision. v1 was defensible at the time of writing based on Q1 evidence. v2 is more defensible now that Q8 evidence is on the table.

**The vision is unchanged.** "Find the drug, for ANY disease" still holds. **The path is updated** because Souza & Mehta showed the path of "scale FMs" may not be the path of universality.

If anything, v2 makes the Fullest Vision MORE achievable, not less:
- Parameter-free baselines run at **CPU scale**, not 1000-H100 scale → universality is achievable at single-institution compute
- Open-source parameter-free methods are not subject to license restrictions → Charter §7 open-science commitment is easier
- Mechanistic interpretability of parameter-free linear projections is **easier than FM spectral analysis** → Charter §1.3 falsifiability is easier

**The conservative move (keep v1 locked) would have been the wrong move for the vision.** The audit-discipline move (open the v1 commitment to revision when new evidence requires) is the right move for the vision.

---

## Cross-Decision Implications

- **Decision 2 (Q2 cross-cohort):** UNCHANGED. scIB + Harmony + scANVI + MrVI commitments stand independently of substrate choice.
- **Decision 3 (Q3 bulk→single):** UNCHANGED. SCAD + scDEAL + scAdaDrug + scRank + Beyondcell stack stands independently.
- **Decision 4 (Q4 drug response):** REINFORCED. CPA + GEARS + FM-derived-encoders architecture becomes "encoder family that accepts any substrate" — if FM wins, FM-derived encoders; if scVI wins, scVI-derived encoders; if scTOP wins, projection-derived encoders.
- **Decision 5 (Q5 OOD):** REINFORCED. Conformal prediction + Deep Ensembles + MC Dropout layer on top of any substrate.
- **Decision 6 (Q6 validation):** REINFORCED. V0-V6 cascade includes all four paradigms per Decision 8.
- **Decision 7 (Q7 interpretability):** CONDITIONALLY REINFORCED. Spectral analysis if FM; gene attribution if parameter-free. Both are first-class.
- **Decision 8 (Q8 universality):** PARENT DECISION. Decision 1 v2 is the implementation of Decision 8 Commitment 2 (the multi-paradigm comparison).
- **Decision 9 (Q9 compute):** EASED. Default substrate compute requirement no longer dictates an FM-scale envelope; can target PaSCient (8 A100s) or smaller.
- **Decision 10 (Q10 open-source):** REINFORCED. All four substrates have open implementations.

---

## Discipline Check

- [x] **P3 (research before code):** ✅ Revision grounded in 5 verified primary-source Q8 anchor reads (Phase 6 work) + the original 8 Q1 anchors (v1 work)
- [x] **P15 (only correct/honest/real science):** ✅ Commitment 5 binds INTERCEPTA to honest statement of uncertainty; revision openly acknowledged
- [x] **P16 (preserve past work):** ✅ v1 file preserved in archive; v2 is the new operational record; v1 grounding remains valid for the FM family literature
- [x] **P-FV-1 to P-FV-3:** ✅ Revision serves the Fullest Vision (universality is more achievable with substrate flexibility than with substrate commitment)
- [x] **Charter §5.3 GO/NO-GO:** ✅ v2 termination criteria explicit; v2 lock conditions specified
- [x] **Souza & Mehta methodological bar (Decision 8 Commitment 5):** ✅ Binding on v2 publications

## Drift catalog this Phase 6 Decision 1 v2 write

- **New drift instances:** 0
- **Audit-derived improvement:** Pre-audit Decision 1 (2,709 words, PROPOSED) was strong but had inadequately weighed Souza & Mehta evidence. v2 corrects this without invalidating v1's literature grounding for FMs themselves.
- **Methodological commitment:** v2's "honest stated uncertainty" makes future Decision 1 drift on substrate choice structurally prevented (must compare to Baseline B before claiming FM benefit on drug response).

---

— Claude (CSO), 2026-05-10 (Phase 6 Decision 1 v2)
