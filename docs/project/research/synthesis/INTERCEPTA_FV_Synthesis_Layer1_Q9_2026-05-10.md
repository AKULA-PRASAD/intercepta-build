# INTERCEPTA Layer 1 Q9 Operational Synthesis v2 — Compute Architecture: Northeastern Explorer as Primary; Burst Capacity as Backup

**CSO:** Claude
**Date:** 2026-05-10
**Phase:** 7 (audit remediation — Operational Decision class)
**Scope:** Operational analysis of compute requirements for Decisions 1 v2 through 8 architectural commitments, grounded in INTERCEPTA-specific constraints (Charter §7.1 single-institution Northeastern HPC; Decision 9 single-A100 envelope target)
**Supersedes:** Q9 synthesis v1 (233 words, archived in `_archive/`)

**Status:** OPERATIONAL DECISION format (different from Research Decision format used for Q1-Q8) — pending CEO taxonomy consent

---

## Executive Summary

Q9 (compute architecture) is **not a research question** — it does not ask what is empirically true about the state of computational biology methods. It asks what INTERCEPTA should operationally commit to given its specific constraints:

1. Charter §7.1: single-institution Northeastern HPC as primary compute target
2. Decision 9 v1 commitment: single-A100 envelope target
3. The eight-decision architectural commitments (Decisions 1 v2 through 8) determine compute demand
4. Realistic CEO + CSO bandwidth constraints

**The operational reality:** Northeastern Explorer cluster provides A100 GPU access via SLURM scheduler with /scratch storage. The eight-decision architecture **fits within this envelope** with explicit trade-offs accepted (multi-stage training pipelines; sequential FM inference; cached embeddings; ensemble training sequentialized over wall time).

**The operational commitment is binary and explicit:**
- **Primary compute:** Northeastern Explorer cluster (A100 GPU partition; CPU partition for parameter-free baselines; /scratch storage)
- **Burst backup:** AWS/GCP only if specific Layer 5 experiments demonstrate Northeastern-infeasibility
- **No proprietary compute dependencies:** ruled out for open-science reproducibility

**Two cross-decision compute integrations now explicit in v2:**

- **Decision 5 v2 N=5 Deep Ensembles + Decision 7 v2 7-scale stack:** dominant compute consumers; require Decision 9 v2 explicit allocation
- **Decision 8 V6 cross-disease grid:** N×(N-1) train-test scenarios across therapeutic areas → SLURM job array operational pattern

---

## Compute Demand Per Architectural Component

### Demand Analysis (Operational Inventory)

| Component | Source | Compute pattern | Northeastern feasible? |
|---|---|---|---|
| **Decision 1 v2 substrate (FM branch)** | scFoundation 100M / UCE 650M / scGPT 51M / Geneformer 10M | Frozen inference (cached embeddings) + optional fine-tuning | ✅ Single A100 |
| **Decision 1 v2 substrate (parameter-free)** | scTOP (Souza-Mehta) | CPU + linear algebra | ✅ Trivial |
| **Decision 1 v2 substrate (scVI/scANVI)** | scvi-tools | Training: single A100, hours-days | ✅ Yes |
| **Decision 2 v2 multi-method Q2** | scANVI/MrVI/Harmony/Seurat v3 | Mix of GPU (VAE) + CPU (Harmony) | ✅ Yes |
| **Decision 3 v2 scAdaDrug** | Adversarial DA training | Single A100, days; adversarial restart sensitivity | ✅ Yes (longer wall time) |
| **Decision 3 v2 scRank** | GRN reconstruction + perturbation | CPU + memory | ✅ Yes |
| **Decision 3 v2 Beyondcell** | Signature scoring | CPU lookups | ✅ Yes |
| **Decision 4 v2 L7 architecture** | CPA + chemCPA + GEARS fusion | Single A100, multi-stage (Phase 1-4) training | ✅ Yes (multi-week training) |
| **Decision 4 v2 chemCPA architecture surgery** | Bulk pretrain → surgery → scRNA fine-tune | Multi-A100 friendly but single-A100 feasible | ✅ Yes (sequential) |
| **Decision 5 v2 N=5 Deep Ensembles** | 5× training cost | 5× wall time on single A100; or 5× A100s parallel | ✅ Yes (longer wall time) |
| **Decision 5 v2 conformal calibration** | Inference + statistics | Fast | ✅ Trivial |
| **Decision 5 v2 energy scoring** | Inference + thresholding | Fast | ✅ Trivial |
| **Decision 6 v2 V0-V6 cascade** | Multiple training runs across validation levels | Aggregate weeks-months on single A100 | ✅ Yes (sequential cascade) |
| **Decision 7 v2 Scale 5 IG+SmoothGrad** | ~50 forward+backward passes per attribution × N=5 ensemble | Memory-heavy but feasible per cell-drug pair | ✅ Yes |
| **Decision 7 v2 Scale 7 SHAP** | KernelSHAP expensive; DeepSHAP cheaper | DeepSHAP feasible per patient | ✅ Yes |
| **Decision 8 V6 cross-disease grid** | N=5 disease classes × N=5 = 25 train-test scenarios | SLURM job array pattern; aggregate weeks | ✅ Yes (parallelizable jobs) |

**Aggregate compute envelope:** Decision 1 v2 through 8 fits within single A100 + CPU partition + /scratch storage on Northeastern Explorer. **No fundamental compute barrier.**

### Bottleneck Identification

**Operational bottlenecks (not blockers):**

1. **Decision 5 v2 N=5 Deep Ensembles** — 5× training cost is the dominant single line item. Mitigation: train ensembles sequentially over wall time rather than parallel A100s.

2. **Decision 8 V6 cross-disease grid** — N×(N-1) train-test scenarios produces O(N²) experiments. Mitigation: SLURM job array pattern; prioritize 2-3 disease classes first; expand iteratively.

3. **Decision 7 v2 Scale 5 IG+SmoothGrad** — memory-heavy per attribution. Mitigation: chunked computation; cached intermediate gradients.

4. **Decision 1 v2 substrate evaluation (FM branch)** — 4 FM candidates × cached embeddings × all downstream evaluations. Mitigation: pre-compute embeddings to /scratch; reuse across ablations.

5. **Storage for cached FM embeddings** — sci-Plex3 ~650K cells × 4 FMs × 512-dim float32 ≈ 5 GB. Manageable.

### Mitigation Strategies (Explicit Operational Commitments)

**Strategy 1 — Cached embedding architecture:**
- Pre-compute FM embeddings (Decision 1 v2 substrate Branch A) for full sci-Plex3 + GDSC + CCLE in batch jobs
- Store in /scratch/akula.pra/INTERCEPTA/embeddings/
- All downstream training/inference loads embeddings; never recomputes FM forward pass
- **Operational benefit:** removes FM inference from the critical path

**Strategy 2 — Multi-stage training pipeline (chemCPA architecture surgery):**
- Phase 1 (bulk pretraining): GDSC/CCLE/LINCS on bulk RNA HTS — single A100, days
- Phase 2 (architecture surgery): layer modification between bulk + scRNA phases
- Phase 3 (single-cell fine-tuning): sci-Plex3 — single A100, days
- Phase 4 (cross-disease fine-tuning): held-out diseases — single A100, days per disease
- **Operational benefit:** breaks training into checkpoint-resumable stages; A100 utilization optimized per stage

**Strategy 3 — SLURM job arrays for V6 grid:**
- Decision 6 v2 V0-V6 validation cascade implemented as SLURM job arrays
- Decision 8 V6 cross-disease grid: each (train_disease, test_disease) cell = one job
- Job arrays scale naturally; A100 partition queue absorbs parallelism
- **Operational benefit:** wall time scales with queue availability not architecture

**Strategy 4 — Distillation as Layer 5+ option:**
- After V0-V3 pass criteria met, optionally distill into smaller models for deployment
- Distilled models reduce inference compute by ~10×
- Not Layer 1 commitment; Layer 5+ operational option

**Strategy 5 — Burst capacity policy:**
- Northeastern Explorer is primary
- AWS/GCP **only** if a specific Layer 5 experiment empirically demonstrates infeasibility on Northeastern (e.g., specific FM 650M-param model requires >40GB VRAM)
- Burst usage requires CEO approval per occurrence
- **Operational benefit:** prevents drift to multi-cloud architecture complexity

---

## Northeastern Explorer Cluster — Operational Specifics

From prior CEO context (`ssh akula.pra@login.explorer.northeastern.edu`):

**Compute partitions:**
- GPU partition: A100 GPUs (40GB or 80GB VRAM variants per partition)
- CPU partition: classical compute for parameter-free baselines + signature scoring + GRN reconstruction
- High-memory partition: for memory-bound experiments (large dataset loads)

**Storage:**
- `/scratch/akula.pra/INTERCEPTA/`: generous quota for academic accounts; primary working directory
- Home directory: code repositories + small artifacts
- Snapshot backup policy: TBD by Northeastern Research Computing

**Scheduler:** SLURM with standard partitions (short / long / GPU / high-memory)

**Software stack:** module-loaded CUDA + Python environment management via conda/mamba

**Network:** institutional fast network; data ingress via scp/rsync from local CEO Mac

**Operational alignment with INTERCEPTA architecture:**
- A100 partition: serves Decision 1 v2 FM substrate + Decisions 2 v2 / 3 v2 / 4 v2 / 5 v2 training
- CPU partition: serves Decision 1 v2 parameter-free substrate + Decision 2 v2 Harmony + Decision 3 v2 scRank/Beyondcell + Decision 7 v2 Scale 4
- High-memory: serves cached embedding generation + Decision 7 v2 Scale 5 IG+SmoothGrad memory peaks

---

## Cross-Decision Compute Implications

### Decision 1 v2 (substrate flexibility)

Substrate choice has dramatic compute implications:
- **FM substrate:** GPU-heavy, multi-day training even for fine-tuning; cached embeddings critical
- **Parameter-free substrate:** trivial compute; Souza-Mehta methodological bar reinforced by compute simplicity
- **scVI/scANVI substrate:** moderate GPU; days of training

**Operational implication:** parameter-free substrate (Decision 1 v2 Branch Y) is **the cheapest operationally** — if Layer 5 ablations support its competitive position, INTERCEPTA's compute envelope shrinks dramatically.

### Decision 4 v2 (L7 architecture)

Six-slot L7 has variable compute per slot:
- Slot 1 (cell encoder): substrate-dependent (see Decision 1 v2 above)
- Slot 2 (drug molecule encoder G): chem-FM evaluation candidates; moderate
- Slot 3 (perturbation network M+S): cheap once trained
- Slot 4 (GEARS graph-augmented module): graph NN training, moderate
- Slot 5 (mode collapse mitigation): training-time overhead; inference-time cheap
- Slot 6 (patient aggregation): cheap (attention pooling at inference)

**Operational commitment:** total Decision 4 v2 training cost ~ PaSCient envelope (Q8.3 anchor, 8× A100s for original PaSCient). INTERCEPTA's single-A100 commitment means 8× wall time vs PaSCient — operationally feasible.

### Decision 5 v2 (4-layer OOD stack)

- Layer 5.1 (substrate posterior): native to Decision 1 v2 VAE substrate; or epistemic decomposition cheap
- **Layer 5.2 (Deep Ensembles N=5):** **dominant compute consumer** — 5× training cost
- Layer 5.3 (conformal): cheap calibration
- Layer 5.4 (energy): cheap inference threshold

**Operational commitment:** Decision 5 v2 N=5 ensembles run sequentially on single A100 over multi-week wall time, OR scheduled as 5 parallel SLURM jobs if A100 partition has capacity.

### Decision 7 v2 (7-scale interpretability)

- Scale 1 (geometric, FM-only): moderate; spectral analysis post-training
- Scale 2 (drug-class CPA): cheap; native to L7 forward pass
- Scale 3 (pathway GEARS + Beyondcell): cheap; native to L7 + signature lookups
- Scale 4 (scRank GRN): moderate; CPU-feasible
- **Scale 5 (gene-level IG+SmoothGrad):** **dominant compute consumer at inference time** — 50 passes per attribution × N=5 ensemble × thousands of cells
- Scale 6 (River DSEP, spatial only): moderate
- Scale 7 (SHAP patient-level): DeepSHAP feasible; KernelSHAP expensive

**Operational commitment:** Decision 7 v2 inference compute ~10-20% of Decision 4 v2 inference compute. Decision 9 v2 allocates this explicitly.

### Decision 8 (universality 4-paradigm comparison)

- Paradigm A (general FM portfolio): compute-heavy (multiple FMs evaluated)
- Paradigm B (disease-area-specific EVA): single FM evaluation
- Paradigm C (patient-level PaSCient-style): training-heavy then cheap inference
- Paradigm D (parameter-free Souza-Mehta): trivial compute

**Operational commitment:** all 4 paradigms must be evaluable within Decision 9 v2 envelope. Paradigm A is the upper bound; Paradigm D is the lower bound.

---

## What Q9 v2 Does NOT Resolve

To be honest about scope:

1. **Specific A100 VRAM variant (40GB vs 80GB).** Depends on Northeastern partition availability at execution time; Layer 5 operational detail.

2. **Specific SLURM partition selection per job.** Layer 5 operational scripting.

3. **Compute scheduling and queue management.** Operational practice, not architectural commitment.

4. **Burst capacity vendor choice (AWS vs GCP vs Azure).** Conditional on burst-need empirical demonstration; Layer 5+ decision.

5. **Cost accounting for burst capacity.** Operational budget item; outside Layer 1 scope.

6. **Specific storage architecture for cached embeddings.** /scratch is primary; sub-directory structure is Layer 5 operational detail.

These require Layer 5 implementation execution, not more Layer 1 reading.

---

## Drift Catalog This Phase 7 Q9 Cycle

- **New drift instances introduced:** 0
- **Format reclassification:** Q9 reclassified from Research Decision (paper-anchored) to Operational Decision (constraint-anchored) per CEO consent taxonomy
- **v1 commitments preserved:** Northeastern Explorer primary + single-A100 envelope + cached embeddings + SLURM job arrays — all from v1 reasoning, now formalized
- **v2 additions:** explicit per-decision compute mapping; explicit bottleneck identification; explicit mitigation strategies; explicit cross-decision compute implications

---

— Claude (CSO), 2026-05-10 (Phase 7 Q9 operational synthesis v2)
