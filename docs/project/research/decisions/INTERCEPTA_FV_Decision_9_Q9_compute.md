# INTERCEPTA Decision 9 v2 — Compute Architecture Commitment: Northeastern Explorer Primary + Single-A100 Envelope (PROPOSED — Operational Decision Class)

**Status:** PROPOSED Operational Decision Record (different format from Layer 1 Research Decision Records 1-8; pending CEO taxonomy consent)
**Date:** 2026-05-10
**CSO:** Claude
**Phase:** 7 (audit remediation final phase)
**Supersedes:** Decision 9 v1 (147 words, archived in `_archive/`)

---

## Operational Constraint Foundation

This is **not a Research Decision**. It does not derive from primary-source paper reads or benchmark evidence. It is an **Operational Decision** grounded in INTERCEPTA-specific constraints:

1. **Charter §7.1:** single-institution Northeastern HPC as primary compute target
2. **Charter §1.1 open-science:** no proprietary compute dependencies
3. **Decision 9 v1 commitment:** single-A100 envelope target
4. **Eight-decision architectural commitments** (Decisions 1 v2 through 8) determine total compute demand
5. **Realistic CEO + CSO bandwidth** (single institution, two-person core team + AI assistance)

The empirical state of the field (compute requirements of scFoundation/UCE/CPA/GEARS/etc.) is **inventory data**, not decision grounding. The decision itself is what INTERCEPTA **chooses to operationally commit to**.

---

## The Decision

INTERCEPTA's compute architecture commits to **NORTHEASTERN EXPLORER CLUSTER AS PRIMARY** with single-A100 envelope target, cached embedding architecture, multi-stage training pipelines, SLURM job array patterns for cross-disease grid, and explicit burst capacity policy.

### Operational Architecture Diagram

```
Primary compute: Northeastern Explorer Cluster
                ssh akula.pra@login.explorer.northeastern.edu
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
[GPU Partition]                         [CPU Partition]
A100 (40GB / 80GB VRAM)                Classical compute
        ↓                                       ↓
Decision 1 v2 FM substrate              Decision 1 v2 parameter-free
Decision 2 v2 scANVI/MrVI               Decision 2 v2 Harmony
Decision 3 v2 scAdaDrug                 Decision 3 v2 scRank/Beyondcell
Decision 4 v2 L7 training               Decision 7 v2 Scale 4
Decision 5 v2 N=5 ensembles             Decision 7 v2 Scale 3
Decision 7 v2 Scale 5 IG+SmoothGrad     SHAP DeepSHAP variant
        ↓                                       ↓
        └───────────────────┬───────────────────┘
                            ↓
            /scratch/akula.pra/INTERCEPTA/
            (cached FM embeddings + training checkpoints + V0-V6 results)
                            ↓
            SLURM scheduler — job arrays for V6 grid
                            ↓
[Conditional Burst Capacity — Backup Only]
AWS/GCP if specific Layer 5 experiment empirically demonstrates Northeastern-infeasibility
            (requires CEO approval per occurrence)
```

### Six Operational Commitments

**Commitment 1 — Northeastern Explorer as primary:**
- All Layer 5 implementation work executes on Explorer cluster
- A100 GPU partition + CPU partition + /scratch storage
- SLURM scheduler with standard partitions
- No proprietary compute dependencies in default architecture

**Commitment 2 — Single-A100 envelope target:**
- Each training/inference job designed to fit within single A100 (40GB or 80GB VRAM)
- Multi-A100 parallelism via SLURM job arrays (multiple independent jobs), not via distributed training
- Operational rationale: simplest, most portable, and aligned with academic resource reality
- Multi-A100 distributed training is a Layer 5+ optional optimization, not Layer 1 commitment

**Commitment 3 — Cached embedding architecture:**
- FM embeddings (Decision 1 v2 substrate Branch A) pre-computed in batch jobs
- Stored at `/scratch/akula.pra/INTERCEPTA/embeddings/`
- All downstream training/inference loads embeddings; never recomputes FM forward pass
- Reduces FM inference from the critical path of all downstream experiments

**Commitment 4 — Multi-stage training pipeline (chemCPA architecture surgery):**
- Phase 1: bulk RNA HTS pretraining (GDSC/CCLE/LINCS)
- Phase 2: architecture surgery between bulk + scRNA phases
- Phase 3: single-cell fine-tuning (sci-Plex3)
- Phase 4: cross-disease fine-tuning (held-out diseases for Decision 8 V6)
- Each phase produces checkpoint; pipeline resumable
- Aligns with Decision 4 v2's training protocol

**Commitment 5 — SLURM job array pattern for V6 grid:**
- Decision 6 v2 V0-V6 validation cascade implemented as SLURM job arrays
- Decision 8 V6 cross-disease grid: each (train_disease, test_disease) cell = independent job
- Wall time scales with queue availability, not architecture
- Operational benefit: parallelizes across queue without distributed training complexity

**Commitment 6 — Burst capacity policy (explicit):**
- Northeastern Explorer is primary
- AWS / GCP / Azure **only** if a specific Layer 5 experiment empirically demonstrates Northeastern-infeasibility
- Burst usage requires **CEO approval per occurrence** with explicit operational rationale
- Operational benefit: prevents drift to multi-cloud architecture complexity
- Cost accounting for burst capacity: separate operational budget item; outside Decision 9 v2 scope

---

## Pass Criteria (Binding GO/NO-GO per Operational Decision class)

Decision 9 v2 must satisfy the following empirical/operational criteria before LOCK:

### Pass 1 — Northeastern Explorer Access Operational

**Criterion:** CEO (Prasad) confirms current SSH access to `akula.pra@login.explorer.northeastern.edu` with valid Northeastern Research Computing account, A100 partition queue eligibility, and /scratch quota sufficient for INTERCEPTA storage needs (~100 GB initial estimate).

**Rationale:** Without verified compute access, all Layer 5 commitments are theoretical. **This is the most consequential Decision 9 v2 pass criterion** — single Layer 5 prerequisite gate.

### Pass 2 — Cached Embedding Throughput

**Criterion:** Decision 1 v2 substrate Branch A (FM) embeddings for sci-Plex3 (~650K cells) computable within 24 hours of single-A100 GPU time per FM candidate.

**Rationale:** Cached embedding architecture (Commitment 3) only valuable if cache generation is operationally tractable.

### Pass 3 — Decision 5 v2 N=5 Ensemble Wall Time

**Criterion:** N=5 Deep Ensembles of Decision 4 v2 L7 head trainable sequentially on single A100 within ≤ 10 weeks total wall time (5 × ~2 weeks per ensemble member).

**Rationale:** Decision 5 v2 dominant compute commitment. If sequential ensemble training exceeds 10 weeks, parallel SLURM scheduling or A100 partition queue capacity must absorb the load.

### Pass 4 — V6 Cross-Disease Grid SLURM Operational

**Criterion:** Decision 8 V6 grid (≥ 2 therapeutic areas) implementable as SLURM job array with ≤ 100 total jobs in queue at peak, each job within standard partition wall-time limits.

**Rationale:** Job array pattern viability gate. If V6 grid exceeds queue capacity, prioritization strategy (subset of diseases first) is operationally necessary.

### Pass 5 — Storage Envelope

**Criterion:** Total INTERCEPTA `/scratch/akula.pra/INTERCEPTA/` storage usage projected to fit within Northeastern Research Computing quota over Layer 5 execution.

**Estimated storage budget:**
- Cached FM embeddings: ~5-20 GB per FM × 4 candidates = 20-80 GB
- Training checkpoints: ~1-5 GB per model × N=5 ensemble × 8 decision components = 40-200 GB
- V0-V6 results + intermediate artifacts: ~50 GB
- **Total estimated:** ~110-330 GB
- **Northeastern academic quota typical:** generous (TB-scale)

### Pass 6 — Burst Capacity Triggered ≤ 5% of Layer 5 Compute

**Criterion:** Over the course of Layer 5 implementation, burst capacity (AWS/GCP) is invoked for ≤ 5% of total compute spend.

**Rationale:** Single-institution commitment (Charter §7.1) operational test. If burst capacity dominates, the single-institution architecture is empirically failing. Trigger: revise Decision 9 v2 toward dual-compute architecture.

### Pass 7 — Open-Science Reproducibility (Decision 10 cross-binding)

**Criterion:** All Decision 9 v2 compute commitments use open-source schedulers (SLURM), open-source containers (Singularity/Apptainer or Docker), and reproducible environment specifications (conda/mamba environment files; or container images with locked versions).

**Rationale:** Charter §1.1 open-science commitment. Decision 10 v2 cross-binding: reproducibility requires open compute infrastructure stack.

---

## Trade-offs and Rejected Alternatives

### Why not commit to multi-A100 distributed training?

**Rejected reason:** Multi-A100 distributed training adds complexity (data parallelism + gradient synchronization + checkpoint coordination) without clear benefit for INTERCEPTA's architectural scale. Decision 4 v2 L7 trains within single-A100 envelope. Multi-A100 is Layer 5+ optimization, not Layer 1 commitment.

### Why not commit to cloud-primary (AWS/GCP)?

**Rejected reason:** Charter §7.1 commits to single-institution Northeastern HPC. Cloud-primary breaks the institutional commitment. Burst capacity is the explicit operational exception, not the default.

### Why not commit to 8-A100 parallel ensembles (like original PaSCient)?

**Rejected reason:** PaSCient (Q8.3 anchor) used 8× A100s; INTERCEPTA's single-A100 envelope means 8× wall time. **This is an explicit trade-off** — wall-time cost for compute-envelope simplicity. Acceptable because INTERCEPTA's research timeline (months-years) absorbs sequential training.

### Why not commit to a specific A100 VRAM variant (40GB vs 80GB)?

**Rejected reason:** Depends on Northeastern partition availability at execution time. Operationally pragmatic to use whatever is queue-available. 80GB preferred for memory-heavy experiments (Decision 7 v2 Scale 5 IG+SmoothGrad); 40GB sufficient for most.

### Why include explicit burst capacity policy?

**Rationale:** Without explicit policy, ad-hoc cloud usage drifts INTERCEPTA away from single-institution commitment. **Explicit policy (CEO approval per occurrence; ≤ 5% of total compute target) operationalizes the Charter §7.1 commitment.**

### Why not include CPU-only fallback architecture?

**Rationale:** Decision 1 v2 Branch Y (parameter-free substrate) is CPU-feasible; Decision 9 v2 supports it via CPU partition. **There IS a CPU fallback for substrate**, but full Decision 4 v2 L7 training requires GPU. Pure-CPU INTERCEPTA is operationally infeasible at the architecture's full ambition.

---

## Cross-Decision Implications

Decision 9 v2 affects and is affected by:

- **Decision 1 v2 (cell representation):** Substrate choice has dramatic compute implications. Parameter-free (Branch Y) is the cheapest operationally — if Layer 5 ablations support its competitive position, Decision 9 v2 envelope shrinks dramatically.

- **Decision 2 v2 (cross-cohort):** Multi-method Q2 (scANVI + MrVI + Harmony + Seurat v3) mixes GPU + CPU; Decision 9 v2 supports both partitions.

- **Decision 3 v2 (bulk → single-cell):** scAdaDrug (GPU-heavy) + scRank (CPU-feasible) + Beyondcell (CPU-feasible). Compute spread aligns with Decision 9 v2's GPU+CPU architecture.

- **Decision 4 v2 (drug response architecture):** L7 training is the dominant single line item. chemCPA architecture surgery (Commitment 4) aligns with Decision 9 v2's multi-stage pipeline.

- **Decision 5 v2 (OOD detection):** N=5 Deep Ensembles is the dominant compute consumer. Decision 9 v2 Pass 3 specifies operational tolerance (≤ 10 weeks wall time).

- **Decision 6 v2 (validation cascade):** V0-V6 cascade aligns with SLURM job array pattern (Commitment 5).

- **Decision 7 v2 (mechanistic interpretability):** Scale 5 IG+SmoothGrad is dominant inference-time compute consumer. Decision 9 v2 allocates ~10-20% of Decision 4 v2 inference compute to Q7 stack.

- **Decision 8 (universality):** V6 cross-disease grid aligns with SLURM job array pattern. Paradigm comparison (A/B/C/D) is feasible within envelope.

- **Decision 10 v2 (open-source):** OPERATIONAL CO-BOUND. Decision 9 v2 Pass 7 requires open-source compute infrastructure stack. Decision 10 v2 license commitments must be compatible with Decision 9 v2 reproducibility requirements.

---

## What Decision 9 v2 Does NOT Decide

To be honest about scope:

1. **Specific A100 VRAM variant (40GB vs 80GB).** Depends on Northeastern partition availability; Layer 5 operational detail.

2. **Specific SLURM partition selection per job.** Layer 5 operational scripting.

3. **Burst capacity vendor choice (AWS vs GCP vs Azure).** Conditional on burst-need empirical demonstration.

4. **Cost accounting for burst capacity.** Operational budget item; outside Decision 9 v2 scope.

5. **Storage sub-directory architecture.** /scratch is primary; sub-directory structure is Layer 5 operational scripting.

6. **Compute scheduling and queue management.** Operational practice, not architectural commitment.

7. **Multi-A100 distributed training adoption.** Layer 5+ optimization decision; not Layer 1 commitment.

8. **Distillation timing.** Layer 5+ option after V0-V3 pass criteria met.

These require Layer 5 implementation execution, not more Layer 1 reading.

---

## Discipline Check

- [x] **P3 (research before code):** ✅ Decision grounded in operational analysis of INTERCEPTA-specific constraints (Charter §7.1; Decision 1 v2 through 8 architectural commitments); not paper-anchored because Q9 is an Operational Decision, not Research Decision (taxonomy pending CEO consent)
- [x] **P15 (only correct/honest/real science):** ✅ Single-institution constraint honestly preserved; multi-A100 distributed training honestly rejected as Layer 5+ optimization; burst capacity explicit rather than ambient
- [x] **P16 (preserve past work):** ✅ Decision 9 v1 (147 words) + Q9 synthesis v1 (233 words) archived in `_archive/`; v1 operational reasoning preserved in v2 with formalization, not contradiction
- [x] **P-FV-1 to P-FV-3:** ✅ Decision 9 v2 directly serves Charter §7.1 single-institution commitment
- [x] **Charter §5.3 GO/NO-GO:** ✅ Pass 1-7 criteria explicit and binding (operational tests, not field-evidence tests)
- [x] **Charter §7.1 (single-institution):** ✅ Northeastern Explorer primary; burst capacity explicit exception
- [x] **Cross-decision integration:** ✅ All v2 decisions operationally co-bound; Decision 10 v2 reproducibility binding made explicit
- [x] **Operational Decision class:** ✅ Format distinct from Layer 1 Research Decision Records 1-8; CEO taxonomy consent pending

## Drift Catalog This Phase 7 Decision 9 v2 Write

- **New drift instances:** 0
- **Format reclassification:** Decision 9 reclassified from Research Decision (paper-anchored) to Operational Decision (constraint-anchored) — pending CEO taxonomy consent
- **v1 commitments preserved:** Northeastern Explorer primary + single-A100 envelope + cached embeddings + SLURM job arrays + burst backup — all from v1 reasoning, now formalized as 6 operational commitments
- **v2 additions:** 7 binding pass criteria; explicit cross-decision compute implications; explicit burst capacity policy

---

— Claude (CSO), 2026-05-10 (Phase 7 Decision 9 v2 — Operational Decision Record)
