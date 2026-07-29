# INTERCEPTA

The clean, reproducible, Constitution-governed build of the INTERCEPTA program — a **mechanism-anchored cancer
drug-response engine**. This repository is the consolidated home for all of INTERCEPTA: **code + rigorously-
cleaned docs only. No data, ever** (all inputs referenced by [`data/MANIFEST.md`](data/MANIFEST.md); controlled
dbGaP/patient data is excluded by policy). Seeded fresh — the old exploration tree's git history is never
imported, because it contained controlled data.

Everything here is governed by [`CONSTITUTION.md`](CONSTITUTION.md): truth over vision, falsify-first, every
positive guilty until it survives permutation + leakage + multiple-testing + confound + external replication,
reproduce ×2, never fabricate. Where legacy code docstrings overclaim, the module `README.md` and
[`LEDGER.md`](LEDGER.md) are authoritative.

## What INTERCEPTA is (the honest one sentence)
> A prognostic + mechanistic drug-response engine on **known cancer biology**, with a verified transferable
> cell-line→patient signal and verified mutation→drug mechanisms — **not** (yet) a novel-molecule or
> therapy-*selection* platform. The original "universal / any-disease / de novo / therapy-selection" vision was
> tested against our own evidence and reconstructed into an evidence-earned milestone ladder ([`VISION.md`](VISION.md)).

## Where we are on the ladder
| Rung | Status |
|---|---|
| **L0** engine + verified core | ✅ DONE — cross-dataset ceiling ρ=+0.212; AML mutation→drug mechanism verified |
| **L1** cell-line → patient transfer | ✅ real (perm p=5e-4), non-specific on mismatched platform |
| **L1b** drug-specific, proliferation-independent transfer | ✅ PASS · replicated across 2 label screens · robust; weak (ρ≈0.07–0.08), mechanism unexplained |
| **L3** engine > parts (preview) | ✅ first evidence — mutation marker + expression transfer complementary (combined CV beats both in 4/4 pairs) |
| **L2** controlled clinical trials | ⛔ needs dbGaP/EGA (human gate) |
| **L4** beyond first cancer | conditional |

## Verified results (reproduced ×2; see [`LEDGER.md`](LEDGER.md))
- **V1** leakage-free cross-dataset drug-response transfer, mean per-drug ρ=+0.212 (94/100 drugs), beats the
  parameter-free bar (Wilcoxon p=1.9e-15).
- **V4–V6** mutation→drug in AML: **NPM1→Cabozantinib** (p=4.4e-11, deconfounded, split-replicated),
  NRAS→MEK, DNMT3A→Dasatinib.
- **V9** weak but drug-specific cell-line→patient signal (BeatAML), replicated across GDSC2/GDSC1 labels, robust.
- **V10** the two verified signals are **complementary** — combining them beats either alone (4/4 pairs, CV).

## What is NOT claimed (honest boundaries)
- ❌ therapy SELECTION (falsified at n=988) ❌ a novel coordinate beyond Ki67+TILs (R_prolif ≈ GGI)
- ❌ de novo molecule design (Scout-2 = scaffold-hopping; INTC002 = hypothesis, novelty 0.266)
- ❌ quantitative trial prediction (ODE = directional ranking; 2/6 trials, "5/5" retracted)
- ❌ RNA-velocity pre-resistance "time machine" (untestable on current data)
- ❌ validated patient drug predictor (V9/V10 are weak, single cohort, need a 2nd patient cohort)

## Repository layout
```
CONSTITUTION.md VISION.md LEDGER.md DECISIONS.md CONSOLIDATION_PLAN.md
docs/
  vision/               reconstructed north-star + research charter
  architecture/         (module specs, honestly annotated)
  audits/               VISION_AUDIT, EXHAUSTIVE_AUDIT, ODE limitations (self-corrections)
  aspirational_original/ QUARANTINED maximalist originals (banner-tagged; not results)
src/intercepta/         library: sha256-gated data loaders, splits, metrics, frozen axes
engine/                 ode/ net/ scouts/ kaalcura/ velocity/ cell_fm/ aml/ synergy_pk/ pipeline/ audit/
                        (142 code files; each module README states its honest status)
experiments/            B1–B4: pre-registered, permutation-tested, reproduced ×2
prereg/                 pre-registrations (written before each run)
verification/           independent AML verification ledger + prereg + reproduction scripts
papers/                 honest AML response paper ("where ML works, where it doesn't, and why")
data/MANIFEST.md        provenance + access class for every external input (nothing committed)
reproduce.sh requirements.txt
```

## Reproduce
```bash
pip install -r requirements.txt
export INTERCEPTA_DATA=/path/to/public/data        # matching data/MANIFEST.md sha256
export INTERCEPTA_BEATAML=/path/to/your/dbgap/beataml   # controlled — your own access only
bash reproduce.sh                                   # runs B1–B4, writes metrics JSON, reproduce ×2
```
Public-data results (B1/B2) reproduce for anyone; controlled-data results (B3–B4) require your own dbGaP access.

## Integrity
Every experiment emits a provenance-stamped metrics JSON (git sha, versions, input sha256, seed) and must
reproduce ×2. Failed/false claims are recorded as first-class negatives and, where they were once asserted,
explicitly withdrawn (see `LEDGER.md` N1, `DECISIONS.md` D8). This project's audit trail is its core asset.
