# AFFINITY_IPTM1 — CPU structure-only ipTM: honest NEGATIVE (CPU-impractical), + a new lever found

## What was tested (solve-don't-bypass on the affinity wall)
The lighter, untested affinity variant: boltz-2 **structure-only** co-folding (no affinity module) on a
small balanced set (8 thrombin compounds), using interface confidence (ipTM) as a CPU-feasible binder
proxy. This was the un-bypassed variant (the prior pilot tested the heavy affinity module).

## Result: CPU-IMPRACTICAL (tested, not assumed)
- Preprocessing (MSA/featurization) for all 8 inputs finished fast (~seconds each).
- The **structure diffusion** then completed **0 of 8** complexes in **~57 min** of pegged CPU
  (`Predicting DataLoader 0: 0/8`), dropping to 1 core. At this rate the small set is 6+ hours.
- This mirrors the earlier affinity pilot (0/20 in ~48 min). CONCLUSION: co-folding affinity is
  CPU-impractical **even in the lighter structure-only ipTM form** — a TESTED closure of the CPU path,
  not an assumption. Job orchestrator-terminated on this evidence to reclaim CPU for higher-value work.

## The new lever (why the affinity wall is NOT fully closed)
The boltz log shows: `GPU available: True (mps), used: False`. This Mac has an **Apple-Silicon GPU
(Metal / MPS backend)** that the run ignored (`--accelerator cpu`). The affinity wall was previously
declared "GPU-gated (assuming no GPU)" — but there IS a GPU here. Whether boltz-2's ops run on MPS
(PyTorch MPS has known op-coverage gaps → may error or silently fall back to CPU) is UNTESTED and worth a
bounded test (AFFINITY_MPS): 1 complex with `--accelerator mps` (+ PYTORCH_ENABLE_MPS_FALLBACK=1),
timed. If MPS runs the diffusion materially faster, the affinity wall may be crackable on EXISTING
hardware. MPS uses the GPU, not the CPU, so it can run in parallel with CPU work (e.g. #2) without contention.

---

## UPDATE 2026-08-09 — the wall CRACKS on existing hardware (MPS + MSA subsampling), TESTED
The affinity wall was NOT truly "GPU-gated"; it was **memory-gated on 16 GB with a deep MSA**, and the
Apple-Silicon GPU (MPS) was simply never used.
- `--accelerator gpu` on Apple Silicon → PyTorch-Lightning uses **MPS** (confirmed: "pin_memory not
  supported on MPS", one `aten::linalg_svd` falls back to CPU — minor).
- Full-MSA on MPS → OOM (16 GB unified). FIX: `--subsample_msa --num_subsampled_msa 512
  --diffusion_samples 1` → **completed 1 complex, 0 failures, ~4:54 min**, wrote a full confidence JSON
  (cmpd_0340: ipTM 0.967, ligand_ipTM 0.989, complex_pLDDT 0.941) + structure CIF.
- CONSEQUENCE: co-folding structure prediction is **feasible on THIS Mac** at ~5 min/complex → the
  8-compound AFFINITY_IPTM1 ranking (~40 min) is now runnable → the pre-registered ipTM-vs-docking gate
  is finally ANSWERABLE without a cloud GPU. (Caveat: reduced-fidelity settings — subsampled MSA + 1
  diffusion sample — a binder-RANKING proxy, not a high-fidelity structure; ipTM discrimination across
  the 8 is the actual test, running now.)
This is the "solve-don't-bypass / use-every-channel" payoff: from "affinity is GPU-cloud-gated, give up
on CPU" → found the machine's own GPU + the real (memory) constraint + a working fix, each step tested.
