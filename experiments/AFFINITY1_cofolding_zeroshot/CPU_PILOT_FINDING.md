# AFFINITY co-folding CPU pilot — honest empirical finding (2026-08-09)

**Self-correction of a claim I made and then tested.** Two turns after AFFINITY1's original
CPU-infeasible verdict, deep re-analysis argued the *realistic* use case is ranking a SMALL
candidate set (~20 mols) for one target, which I claimed was CPU-feasible (~3 h) — and I
softened the plan's "GPU-gated" status accordingly. I then RAN it (AFFINITY1's own
pre-registered stratified subsample, 20 compounds, thrombin/1OYT, boltz-2 CPU, full affinity
module).

**Result: the claim was WRONG. CPU co-folding AFFINITY is impractical even at small-n.**
- ~85 min CPU / ~48 min wall → **0 of 20 predictions emitted**; progress bar never left
  "Predicting 0/20"; no new output in the final 12 min.
- Root cause of my error: my ~10 min/complex figure was AFFINITY1's *structure-only* timing
  (it had terminated *before* the diffusion step). The **affinity head adds many extra
  diffusion samples** (sampling_steps_affinity 200 × diffusion_samples_affinity 5), so the
  affinity-inclusive per-complex CPU time is far larger (tens of minutes to >1 h), making even
  ~20 complexes effectively non-finishing in a session (~10–20 h+).

**Honest corrected status: co-folding affinity is GPU-gated even at the small-candidate scale.**
My "CPU-feasible for small-candidate ranking" reframe is RETRACTED. The definitive test remains
the GPU benchmark (GPU_BENCHMARK_SPEC.md). No scored result was produced (no overclaim possible).
