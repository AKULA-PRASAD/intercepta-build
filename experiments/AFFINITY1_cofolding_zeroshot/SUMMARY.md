# AFFINITY1 — SUMMARY

**Frontier 2 (OPEN-PROBLEM): zero-shot binding-affinity ranking for a target with zero activity data.**
Verdict: **CPU-INFEASIBLE (compute-gated), with a ready-to-run GPU spec** — a first-class outcome.

The one credible untried zero-shot candidate for the novel-target affinity wall is a deep co-folding
model. We attempted it honestly. **Boltz-2 (v2.2.1) — an AlphaFold3-class co-folding model with a direct
affinity head — installs and runs at zero budget on this Apple-Silicon arm64 CPU** (G1 PASS on Python
3.11; py3.13 forced a from-source scipy build and failed; memory is NOT a wall — a single thrombin+ligand
complex peaked at only ~2.6 GB RSS with no OOM). But the binding constraint is **inference throughput**:
one complex runs on the order of ~10 minutes end-to-end on CPU and did not finish in our observation
window before we terminated it to finalize, so the pre-registered 553-compound head-to-head vs the
docking baseline — and even the <=24 h subsample — is CPU-infeasible in a reasonable wall-clock
(~64-138 CPU-hours for the full set). We therefore did **not** score a ranking; the definitive test is
committed as GPU_BENCHMARK_SPEC.md (same thrombin/1OYT target, same MoleculeACE compounds HIT2 docked,
same metrics, same pre-registered gate — PASS = overall AUROC >= 0.60 AND > docking's 0.4285 AND
novel-vs-inactive AUROC >= 0.60), runnable the instant a GPU is available. **Crucially, this is NOT another
refutation:** unlike the docking (HIT2 AUROC 0.43), ligand-transfer (HIT1), proteochemometric (B49), and
active-learning (B65) negatives — which genuinely tried and failed to rank novel-target affinity — the
co-folding invention here is **neither confirmed nor refuted**; it is compute-gated. The wall stands
**untested-on-CPU**, and we have bounded exactly why (throughput, not installability or memory) and
specified precisely what would test it.

## Reproducibility (honest disclosure)
Neural co-folding inference is non-deterministic and, moreover, **no ranking inference was completed**, so
there are no model-output numbers to reproduce here. The deliverable that IS reproduced is the
**downstream bookkeeping** (`run.py finalize_infeasible`): pure-deterministic, no RNG, no dependence on any
boltz output. Ran x2 -> **payload_sha256 = 556ba69d4403a75ad90342e21ea8aded2a7b22d9f97906ef42d9b2c72daa7089
(byte-identical)**. The sha is over the sorted-key payload excluding the provenance block. When the GPU
run happens, `run.py score` caches the raw affinity_*.json and reproduces the scoring x2 byte-identical,
disclosing any inference nondeterminism per PREREG.md.

## Scope
in-silico; one target (thrombin — docking's most favourable case); CPU-only arm64, NO GPU/CUDA; a
confidence/affinity PROXY, not measured affinity; not wet-lab; no SOTA claim; the co-folding method is
UNtested here, not refuted.

## Files
PREREG.md · FEASIBILITY.md (actual G1/G2 evidence) · GPU_BENCHMARK_SPEC.md · run.py ·
results/AFFINITY1_metrics.json + payload.sha256 · data/models in $INTERCEPTA_DATA/affinity1/
(venv, 3.6 GB boltz weights, test_novelty.csv). NOT git-committed.

## One-line LEDGER verdict
**AFFINITY1 (co-folding zero-shot affinity — Frontier 2 open wall): CPU-INFEASIBLE-with-GPU-spec —
Boltz-2 installs + runs at zero budget on arm64 CPU (memory fine, ~2.6 GB, no OOM) but ~10 min/complex
makes the 553-compound head-to-head infeasible on CPU (~64-138 CPU-hrs); the co-folding invention is
COMPUTE-GATED, neither confirmed nor refuted (distinct from the HIT2/HIT1/B49/B65 refutations); definitive
test delivered as a ready-to-run GPU spec carrying the docking baseline 0.4285 + pre-registered gate;
downstream reproduced x2 byte-identical (payload sha256 556ba69d...).**
