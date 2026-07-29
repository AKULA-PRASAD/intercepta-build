# INTERCEPTA Operational — Environment Drift Log

Per L4.3 §3.1 I1: this log records every environment drift event between Mac (CEO local dev) and Northeastern Explorer (production).

---

## Event 1 — 2026-05-11 — Mambaforge retirement (Stage 1 Step 3a)

**Detection:** Stage 1 Execution Runbook §4.1 specified `Mambaforge-MacOSX-arm64.sh` install URL. The URL returns 9-byte "Not Found" response. Conda-forge has retired Mambaforge in favor of `Miniforge3` (which now bundles mamba 2.x natively).

**Recovery:** Switched download to `https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh` (54 MB; Miniforge3 26.3.2-0). Installed cleanly to `/Users/kalki/miniforge3/`. Verified `mamba 2.6.0` and `conda 26.3.2` both available; single init block in ~/.zshrc (no duplicate conflict).

**Time to resolution:** ~10 minutes including web search verification.

**Lesson learned:** Future spec writing should reference `Miniforge3` not `Mambaforge`. Stage 1 Execution Runbook §4.1 to be updated in a follow-up commit. URLs in specs need periodic refresh; this is an artifact-staleness category of I1 distinct from genuine env drift.

**Severity:** LOW — straightforward URL substitution; same functional outcome (mamba available).

**Drift instance:** 1 of 3 before escalation threshold.

---

## Event 2 — 2026-05-11 — arm64 CUDA omission (Stage 1 Step 3b)

**Detection:** Mac is Apple Silicon (arm64); environment.yml references `pytorch-cuda=12.1` and `cudatoolkit=12.1` which are Linux/x86_64-only. Apple Silicon uses MPS (Metal Performance Shaders), not CUDA.

**Recovery:** Commented out the two CUDA lines in `environment.yml` on Mac with prefix `# arm64 (I1 per L4.3): `. Original preserved as `environment.yml.linux_explorer_original`. Explorer install (Step 5) will use the original unpatched version (or restore from backup before creating env).

**Time to resolution:** < 5 minutes.

**Lesson learned:** Cross-platform conda env divergence is expected. If this pattern recurs at scale, consider splitting `environment.yml` into `environment-mac.yml` (with MPS hint instead of CUDA) and `environment-explorer.yml` (with CUDA) — a Stage 2 operational decision.

**Severity:** LOW — expected platform-specific divergence, mitigation straightforward.

**Drift instance:** 2 of 3 before escalation threshold (per L4.3 §3.1).
