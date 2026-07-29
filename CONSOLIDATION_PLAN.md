# INTERCEPTA consolidation plan — full vision → this repo (Constitution-governed)

**Goal:** bring ALL of `~/INTERCEPTA` (22 GB, 3,274 files) into this clean repo as a real, honest,
reproducible project — **code + rigorously-cleaned docs only; NO data ever** (referenced by sha256 manifest).
Seeded fresh (this repo), because `~/INTERCEPTA/.git` contains controlled dbGaP data in history and must never
be migrated. Based on the 2026-07-29 read-only inventory.

## Hard rules (non-negotiable, override "no compromise")
1. **No controlled/individual-level patient data** in the repo, ever: all `data/beataml/*dbgap*`,
   `beataml_*clinical*`, `data/su2c/*`, per-patient mutation/clinical/expression tables. Referenced by manifest.
2. **No bulk data or third-party models**: `data/` (9.4 G), `models/Geneformer` (5.5 G third-party, own .git) —
   externalized, download-scripted, never vendored.
3. **Every claim carried forward must trace to a reproduced result** or be tagged [aspiration]/[untested].
   Overstated/false claims are rewritten or quarantined, not copied.

## Disposition of each component (verified / rewrite / exclude)
| Component | Source | Disposition |
|---|---|---|
| Honest north-star | `INTERCEPTA_TRUE_VISION_AND_PLAN.md` | CARRY → `docs/vision/` (already reconciled with reality) |
| Verification ledger + prereg + scripts | `verification/` | CARRY → `verification/` (the strongest asset) |
| ODE limitations (honest) | `docs/INTERCEPTA_Validation_Limitations_v1.md` | CARRY → `docs/audits/` |
| Audit scorecards | `VISION_AUDIT.txt`, `EXHAUSTIVE_AUDIT.txt`, `PRE_REBUILD_AUDIT.txt` | CARRY → `docs/audits/` |
| AML response paper (draft2, honest) | `papers/aml_response_paper/sections_draft2_clean/` | CARRY → `papers/` |
| Constitution / charter | `docs/research/…Charter_v1_2…` | CARRY → `docs/` (Phase B vs Phase F) |
| Phase-B package (packaged, tested) | `code/phase_b/` | MERGE into `src/intercepta/` |
| Engine: ODE / phenotype models | `code/intercepta_*ode*.py`, `aml_ode*.py` | CARRY → `engine/ode/` + honest header ("directional ranking, NOT quantitative predictor; 2/6 trials, 0/3 g-rate") |
| Net / knowledge-graph builders | `code/step1..14_*`, `build_*_net.py` | CARRY → `engine/net/` (code only; outputs via manifest) |
| Scouts / discovery | `code/scout*.py`, docking | CARRY → `engine/scouts/` + honest header ("Scout-2 = scaffold-hopping, NOT de novo; INTC002 novelty=0.266, hypothesis only") |
| KAALCURA axes | `code/intercepta_kaalcura*.py`, `r_validation/` | CARRY → `engine/kaalcura/` ("R_prolif ≈ GGI, validated proliferation prognostic, NOT novel axis") |
| RNA velocity | `code/step3_run_scvelo.py` etc | CARRY → `engine/velocity/` ("time-machine claim NOT TESTABLE on current data") |
| Cell FM processing (Geneformer) | `code/cell_processing/` | CARRY → `engine/cell_fm/` (model downloaded externally) |
| BeatAML analysis | `code/beataml_analysis.py`, `round2_aml/code/*` | CARRY → `engine/aml/` (code only) |
| **README.md** (stale/overstated) | root | **REWRITE** — do NOT carry ("universal/any disease", "5/5 trials" are false) |
| `docs/…COMPLETE_VISION…docx`, `…Phase_F…`, `Net_Spec/Architecture` (maximalist) | `docs/` | QUARANTINE → `docs/aspirational_original/` with a header banner: "ORIGINAL VISION — contains claims later falsified; see LEDGER" |
| `phase1_5trial_VALIDATED.csv`, `pharma_deliverable_*`, `pareto_ranking_*`, `*denovo*` outputs | `results/` | EXCLUDE (data/results) + RELABEL in any doc that cites them |
| All `data/`, `models/`, bulk `results/`, `round3` live-test logs | — | EXCLUDE → `data/MANIFEST.md` (sha256 + provenance) |

## Target structure (Harvard-level)
```
README.md              honest overview + the milestone ladder + how to reproduce
CONSTITUTION.md VISION.md LEDGER.md DECISIONS.md CONSOLIDATION_PLAN.md
docs/
  vision/              INTERCEPTA_TRUE_VISION_AND_PLAN + charter
  architecture/        net / scouts / ODE / kaalcura / velocity specs (honestly annotated)
  audits/              VISION_AUDIT, EXHAUSTIVE_AUDIT, Validation_Limitations
  aspirational_original/  quarantined maximalist docs (banner-tagged)
src/intercepta/        library (data w/ sha256 gate, splits, metrics, axes) + phase_b merge
engine/                ode/ net/ scouts/ kaalcura/ velocity/ cell_fm/ aml/  (code, honest headers)
experiments/           B1–B4 (+ future) — pre-registered, reproduced x2
prereg/                pre-registrations
verification/          AML verification ledger + prereg + reproduction scripts
papers/                honest AML response paper
data/MANIFEST.md       sha256 + provenance of every external input (public + controlled-flagged)
reproduce.sh requirements.txt .gitignore
```

## Order of execution
1. [emergency, user] Fix the exposed `kaalcura` repo (delete or purge+force-push) + dbGaP DUA check.
2. [now, local, reversible] Carry forward honest docs + verification + paper (this commit).
3. Import engine code module-by-module with honest headers (largest step, iterative).
4. Extend `data/MANIFEST.md` with every external input; write download scripts for public data.
5. Rewrite README honestly; quarantine the maximalist originals with banners.
6. Pre-push scan (no data, no secrets, no controlled files) → THEN push to `intercepta-build` (private).
