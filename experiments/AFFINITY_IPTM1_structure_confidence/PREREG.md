# AFFINITY_IPTM1 — Structure-only co-folding INTERFACE CONFIDENCE as a zero-data binder proxy

**Pre-registered BEFORE running boltz / before any scoring.** Date: 2026-08-09.
Author: INTERCEPTA AFFINITY_IPTM1 module (CPU-only, zero budget).

## 1. The idea being tested (the un-bypassed variant)
AFFINITY1 tested the FULL Boltz-2 **affinity module** on CPU (sampling_steps_affinity 200 ×
diffusion_samples_affinity 5 = the slow diffusion). Verdict: 0/20 emitted in ~48 min wall,
GPU-gated. This experiment tests the **lighter, untested variant**: run boltz **STRUCTURE-ONLY**
(NO `properties: affinity` block, so NO affinity diffusion) and use the co-folding **interface
confidence** — primarily **ipTM**, secondarily complex pLDDT / PAE — as a cheap, label-free
binder-vs-non-binder proxy. Hypothesis: a co-folding confidence signal ranks binders where
docking failed (HIT2 thrombin AUROC = 0.43, ~ chance).

## 2. This is an underpowered FEASIBILITY + SIGNAL PROBE, not a benchmark
- n = 8 is tiny. AUROC/Spearman on n=8 have huge CIs. Treat directional only.
- ipTM measures **pose/interface confidence**, NOT affinity. It is a WEAK binding proxy by
  construction. Even a positive result is a hint to scale, not proof.
- Zero tuning. The gate and metrics below are fixed now.

## 3. Pre-registered compound set (idx from compounds_manifest.csv), FIXED
Target: thrombin (1OYT), protein chains A+B identical across all complexes; ligand = SMILES.
Balanced 4 active / 4 inactive, novelty mix (5 analog, 3 novel), pKi span 4.09–8.74.

| idx | pact (pKi) | active | novelty | vina |
|-----|-----------|--------|---------|------|
| 21  | 8.7447 | 1 | analog | (none) |
| 67  | 4.4318 | 0 | analog | -8.172 |
| 167 | 5.1701 | 0 | novel  | -8.472 |
| 217 | 6.5229 | 1 | novel  | -5.001 |
| 340 | 8.4559 | 1 | analog | -9.779 |
| 384 | 6.2218 | 0 | analog | -8.301 |
| 529 | 6.7212 | 1 | novel  | -9.612 |
| 535 | 4.0851 | 0 | analog | -9.693 |

idx list (sorted): [21, 67, 167, 217, 340, 384, 529, 535]
Actives: {21, 217, 340, 529}. Inactives: {67, 167, 384, 535}.

## 4. Run command (STRUCTURE ONLY — no affinity module)
```
boltz predict <yamls_structonly> --out_dir out_iptm --cache <boltz_cache> \
  --accelerator cpu --devices 1 --use_msa_server --seed 42
```
Defaults: recycling_steps 3, sampling_steps 200, diffusion_samples 1. NO --affinity*,
NO `properties: affinity` in any YAML. Confidence JSON (ipTM, complex_pLDDT, PAE) is emitted
per prediction under out_iptm/.../predictions/cmpd_XXXX/confidence_*.json.

## 5. Metrics (computed only AFTER JSONs exist)
- Primary: **AUROC** of ipTM vs binary active label (n=8, 4 vs 4).
- Secondary: **Spearman** rho of ipTM vs continuous pKi (pact); also complex_pLDDT AUROC.
- Baselines: docking AUROC = **0.4285** (HIT2 thrombin), random = **0.5**.

## 6. Pre-registered decision gate (fixed BEFORE seeing results)
- **PROMISING (PASS):** ipTM AUROC > 0.60 AND ipTM AUROC > 0.4285 (beats docking).
  → cheap structure-only ipTM ranks binders; a CPU affinity proxy worth scaling on GPU.
- **NEGATIVE:** ipTM AUROC <= 0.60 or <= docking (i.e. ~ chance).
  → co-folding affinity signal is gated even in the cheap structure-only form (tested).
- **INFEASIBLE (also a valid, honest finding):** if structure-only boltz cannot finish the
  8-complex set on CPU in a practical window → co-folding affinity is CPU-gated in EVERY form.

## 7. Reproducibility
Scoring reads cached confidence JSONs and writes results/AFFINITY_IPTM1_metrics.json (sorted
keys). SHA-256 of the sorted-key payload -> results/payload.sha256. Scoring is run twice; the
two SHAs must be byte-identical. No fabrication: if boltz does not finish, metrics are marked
null and the finding is INFEASIBLE.
