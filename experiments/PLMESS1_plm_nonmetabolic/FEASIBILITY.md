# PLMESS1 — Feasibility Gate (CPU-only, zero budget)

## Verdict: FEASIBLE (executed within the pre-registered cap)

## Environment (pre-existing, no GPU)
- `/Users/kalki/miniforge3/envs/intercepta/bin/python` — torch **2.10.0** (CPU) + transformers **4.41.0**,
  sklearn 1.8.0, scipy 1.13.1, numpy 1.26.4. All free/open-source; arm64 CPU wheels.
- ESM-2 `facebook/esm2_t30_150M_UR50D` already cached in `$INTERCEPTA_DATA/hf_cache`.
- 10 CPU threads (`os.cpu_count()`), single machine, no GPU.

## Pre-registered model + params (see PREREG.md)
- Model: `esm2_t30_150M_UR50D` (150M params, hidden dim **640**) — small, CPU-feasible (NOT 650M+). Capacity caveat noted.
- Embedding: mean-pooled last-layer hidden state, attention-masked, deterministic eval, `torch.manual_seed(0)`.
- Truncation: **1022 residues** (`max_length=1024`). The pooler head is UNUSED (its random init never enters the embedding).

## Timing measurement (one-protein → pool estimate)
- Model load: **2.5 s** (one-time).
- Per-protein embed: measured **~0.2–0.7 s** (median-length ~276 aa proteins ~0.5 s; a 820-aa protein 1.6 s).
- Non-metabolic pool size: **n = 2547** proteins with a PEC call.
- Length distribution: median 276 aa, mean 312, max 2339; only **1.2%** exceed 1022 aa (truncated).

## HARD CPU-time cap (LOCKED): total embedding ≤ 60 min
- Estimate: 2547 × ~0.6 s ≈ **~25 min** → within cap.
- Actual (measured, summed across two resume invocations due to a 10-min shell wrapper limit — the
  embedding itself is a single continuous cached job): ~0.65 s/protein, total **~24 min** wall-clock
  for the full 2547-protein pool. **Under the 60-min cap.** Embeddings cached to
  `$INTERCEPTA_DATA/plmess1/emb_<locustag>.npy` (2547 files) → downstream scoring is deterministic and
  reproduced x2 byte-identical.

## Not triggered
Install did NOT fail and timing did NOT blow the cap, so the CPU-INFEASIBLE branch (deliver a GPU spec)
was not needed. The experiment ran end-to-end on CPU.
