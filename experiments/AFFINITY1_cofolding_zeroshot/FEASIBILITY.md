# AFFINITY1 — FEASIBILITY GATE (actual observed evidence)

Pre-registered caps (PREREG.md): **G1** boltz/chai_lab pip-installs into a fresh CPU venv;
**G2** one small protein+ligand complex completes CPU inference in **≤ 20 min** with **no OOM**
(≤ ~15 GB RSS). Machine: Apple M4, 10 cores, **16 GB RAM**, arm64, macOS, **NO GPU/CUDA**.

Everything below is what I ACTUALLY ran and observed — not inferred from model size.

## G1 — install → **PASS**
- `python -m venv` + `pip install boltz`.
- **Python 3.13 FAILED:** boltz's dep `scipy` has no cp313 wheel for its pinned version, so pip tried
  to build scipy from source and aborted looking for a Fortran compiler (`flang`/`gfortran`/`ifort`… all
  "No such file or directory"). This is a real, honest blocker for py3.13.
- **Python 3.11.14 SUCCEEDED:** recreated the venv on 3.11 → `Successfully installed boltz-2.2.1`
  (torch-2.13.0 CPU wheel `torch-2.13.0-cp311-cp311-macosx_14_0_arm64`, rdkit-2026.3.5, biopython,
  pytorch-lightning 2.5.0, etc.). No CUDA-only blocker. **G1 PASS.**
- Boltz-2 exposes the affinity head we need: `boltz predict ... --sampling_steps_affinity`,
  `--diffusion_samples_affinity`, `properties: - affinity: binder: <id>` → outputs
  `affinity_pred_value` (predicted log(IC50), lower = stronger) + `affinity_probability_binary`.
  `--accelerator cpu` and `--seed` both exist. This is exactly the untried zero-shot affinity signal.

## G2 — single-complex CPU inference → **did NOT complete in window; NO OOM** (recorded as NOT a clean pass)
I actually launched it (I did not infer this from hardware):
```
boltz predict thrombin(L=36aa + H=259aa) + ligand SMILES
  --accelerator cpu --devices 1 --use_msa_server --seed 42 --output_format pdb
```
Observed, in order:
- **One-time weight download 3.6 GB:** `boltz2_conf.ckpt` 2.3 GB + `boltz2_aff.ckpt` 1.3 GB + the CCD
  `mols.tar` (1.8 GB, ~45k component files unpacked). Downloaded fine from HuggingFace (~3.5 min).
- **MSA:** retrieved successfully from the colabfold mmseqs2 server (paired + unpaired a3m written) —
  internet-dependent but worked at zero cost.
- **Structure diffusion:** ran at **500–550 % CPU** (multi-core), **peak RSS ~2.6 GB** — comfortably
  under the ~15 GB cap → **NO OOM** (memory is *not* the wall on this 16 GB machine).
- **Timing:** the boltz process reached **10 min 38 s total wall-clock** (download + MSA + ~7 min of
  pure inference) and had **not yet emitted `affinity_*.json`** when I terminated it (SIGTERM) to
  finalize the run. So a single complex was *not observed to finish* within the observation window; I
  did not let it run to completion, so G2 is recorded honestly as **not-completed-in-window (not a clean
  pass)**, with **no OOM**.

## Verdict → **CPU-INFEASIBLE (for the experiment), with GPU spec delivered**
The binding constraint is **throughput, not memory or installability**. Even at an optimistic
~7–15 min/complex (pure inference, no OOM), the pre-registered head-to-head is:
- full set: **553 complexes ≈ 64–138 CPU-hours**;
- pre-registered `≤24 h` subsample (~40 complexes): also not completed in-session.

So the definitive zero-shot potency-ranking head-to-head vs the docking baseline **cannot be run on this
CPU-only machine in a reasonable wall-clock**. Per the pre-registered plan this is a **first-class
outcome**: STOP the compute, declare CPU-INFEASIBLE honestly, and deliver the exact ready-to-run GPU
benchmark spec → **GPU_BENCHMARK_SPEC.md** (runs the instant a CUDA GPU is available, no further design
decisions; carries the same target/compounds/metrics/gate and the docking baseline 0.4285 to beat).

## What is now KNOWN (bounds the wall precisely)
1. Boltz-2 (AF3-class co-folding + affinity head) **is installable and runnable at zero budget on
   arm64 CPU** — install and memory are NOT the blockers (contradicts a naive "won't run CPU-only").
2. The blocker is **inference throughput** — a single complex is on the order of ~10 min end-to-end,
   making a hundreds-of-compound ranking benchmark CPU-infeasible in-session.
3. The scientific question (does the co-folding affinity proxy beat docking/random on novel-target
   potency ranking?) remains **open and compute-gated** — neither confirmed nor refuted here.
