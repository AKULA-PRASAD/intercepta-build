# Q9 anchor 1 — Computational requirements for scFM training and inference

## 0. Identification (composite anchor based on Q1-Q8 reading)

Q9 (compute architecture) is informed primarily by the compute claims of the methods already read:

- **scFoundation 100M params** (Hao 2024) — pretrained on 50M+ cells, inference feasible on single A100
- **UCE** (Rosen 2023) — 33-layer, ~650M params on 100+ datasets
- **scGPT 51M params** — fits on consumer GPU (24GB VRAM)
- **Geneformer ~10M params** — lightweight; fits on single GPU
- **TEDDY 70M-400M params** (Q8 anchor) — explicit scaling analysis
- **CPA / scVI / scANVI / MrVI** — VAE models, ~10K-100K params, fast inference
- **DeepCDR / PaccMann** — task-specific, ~1M-10M params
- **GEARS** — graph neural network, ~10M params

## 1. Why this Q9 framing

Charter §7.1 specifies **single-institution Northeastern HPC** as the compute target. Q9 must answer: **Is the Decision 1-8 architecture feasible on Northeastern HPC?**

## 2. Northeastern HPC capabilities (Explorer cluster)

From prior CEO context (`ssh akula.pra@login.explorer.northeastern.edu`, `/scratch/akula.pra/INTERCEPTA/`):
- GPU partition typically has A100s (40GB or 80GB VRAM)
- CPU partition for parameter-free baselines + classical ML
- Storage: /scratch quota typically generous for academic accounts
- SLURM scheduler

## 3. Compute budget per architecture component

| Layer | Component | Compute requirement | Northeastern feasible? |
|---|---|---|---|
| Q1 FM | scFoundation/UCE/scGPT/Geneformer (frozen inference) | Single A100, batch inference | ✅ Yes |
| Q2 cohort | scANVI/MrVI training | Single A100, hours-days | ✅ Yes |
| Q2 fallback | Harmony | CPU only, minutes | ✅ Yes |
| Q3 DA | scAdaDrug adversarial training | Single A100, days | ✅ Yes |
| Q3 GRN | scRank (GRN reconstruction + perturbation) | CPU + memory | ✅ Yes |
| Q4 CPA | Compositional VAE training | Single A100, days | ✅ Yes |
| Q4 GEARS | Graph NN training | Single A100, days | ✅ Yes |
| Q5 ensemble | N=5 Deep Ensembles | 5× training cost | ✅ Yes (longer wall time) |
| Q7 attribution | IG + SmoothGrad post-hoc | Memory-heavy but feasible | ✅ Yes |
| Q8 multi-FM | Multiple frozen FMs inference | Multi-A100 if parallel | ✅ Yes (sequential) |

## 4. Bottlenecks

- **Cross-disease evaluation grid (Charter U3, 5+ disease classes):** N×(N-1) train-test scenarios = significant total compute
- **Multi-FM ensemble inference at scale:** sequential FM inference adds latency
- **N=5 ensembles for Q5:** 5× the training cost
- **sci-Plex benchmark at full scale (~650K cells):** memory pressure during inference

## 5. Mitigations

- Distillation: train smaller models on FM outputs after Layer 5 validation
- Cached embeddings: pre-compute FM embeddings, store in /scratch, reuse
- Disease subset prioritization: start with 2-3 disease classes, expand
- Approximate inference: MC dropout instead of Deep Ensembles where appropriate

## 6. INTERCEPTA implications

**For Q9:** Northeastern HPC is **operationally sufficient** for Layer 5 build. No fundamental compute barrier. **Charter §7.1 single-institution constraint is satisfiable.**

**Decision 9 PROPOSED:**
- Primary: Northeastern Explorer cluster (single-institution)
- Backup: AWS/GCP for burst capacity if specific experiments exceed local
- Architecture: cached embedding storage in /scratch; sequential FM pipeline; SLURM job arrays for cross-disease grid
- No proprietary compute dependencies

— Claude (CSO), 2026-05-10
