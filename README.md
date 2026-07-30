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

> **Reviewing this repo (AI or human)? Start with [`REVIEWERS.md`](REVIEWERS.md)** — a one-page honest map of what
> is verified, what is falsified (two decisive negatives), how to reproduce, and the forward path.
>
> **Want to see it run?** `python examples/demo.py` — a 30-second, zero-download demo of the real engine
> (transfer ranking + verified-marker bonus + OOD confidence gating). Quickstart: [`examples/README.md`](examples/README.md).

## What INTERCEPTA is (the honest one sentence)
> A prognostic + mechanistic drug-response engine on **known cancer biology**, with a verified transferable
> cell-line→patient signal and verified mutation→drug mechanisms — **not** (yet) a novel-molecule or
> therapy-*selection* platform. The original "universal / any-disease / de novo / therapy-selection" vision was
> tested against our own evidence and reconstructed into an evidence-earned milestone ladder ([`VISION.md`](VISION.md)).

## Where we are — the honest ladder (tested to the ceiling)
| Rung | Status |
|---|---|
| **L0** engine + verified core | ✅ DONE — cross-dataset ceiling ρ=+0.212; AML mutation→drug mechanism verified |
| **L1/L1b** drug-specific cell-line→patient transfer (BeatAML ex-vivo) | ✅ real, weak (ρ≈0.07–0.08), replicated across 2 label screens, robust — but mechanism unexplained |
| **engine > parts** (mechanism + transfer) | ✅ combined beats either alone (4/4 pairs, CV); shipped engine embodies it |
| **genome-wide markers · OOD calibration** | ✅ 177 robust AML markers (FLT3-ITD→FLTi, RAS→MEKi); OOD confidence validated |
| **external PDX drug-specificity** | ⚠️ FRAGILE — borderline (p=0.036) then non-sig under a broader screen (p=0.076); **unestablished** |
| **human clinical drug response (TCGA)** | ❌ **NULL** — raw signal is cancer-type confounding; within-cancer AUROC 0.504 (p=0.43) |

## Verified results (reproduced ×2; see [`LEDGER.md`](LEDGER.md), [`MANUSCRIPT`](papers/intercepta_engine/MANUSCRIPT.md))
- **V1** leakage-free cross-dataset transfer, mean per-drug ρ=+0.212 (94/100 drugs, p=1.9e-15); a real *ceiling*
  (adding proliferation/mutations doesn't beat it).
- **V5/V12** genome-wide AML mutation→drug markers — **FLT3-ITD→FLT3 inhibitors**, **RAS→MEK** (177 robust).
  *(Refinement: NPM1→Cabo and DNMT3A→Dasatinib do NOT survive genome-wide correction — B5.)*
- **V9** weak but drug-specific cell-line→patient signal (BeatAML ex-vivo), replicated across GDSC1/GDSC2, robust.
- **V10/V11** mechanism + transfer are complementary; the shipped engine embodies it.
- **V13** out-of-distribution distance is a validated confidence gate.

## What is NOT claimed / was falsified (honest boundaries)
- ❌ **human clinical drug prediction** — TESTED on TCGA, well-powered NULL once cancer type controlled (B10).
- ⚠️ **robust external (PDX) drug-specificity** — fragile/unestablished (B7 p=0.036 → B9 p=0.076).
- ❌ therapy SELECTION (falsified at n=988) ❌ novel coordinate beyond Ki67+TILs (R_prolif ≈ GGI)
- ❌ de novo molecule design (Scout-2 = scaffold-hopping; INTC002 = hypothesis) ❌ quantitative trial prediction
  (ODE directional; 2/6 trials, "5/5" retracted) ❌ RNA-velocity "time machine" (untestable).
- **Net:** a validated cell-line/ex-vivo drug-response + mechanism engine — NOT a clinical predictor.

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
experiments/            B1–B10 + engine validation: pre-registered, permutation-tested, reproduced ×2
prereg/                 pre-registrations (written before each run)
verification/           independent AML verification ledger + prereg + reproduction scripts
papers/                 intercepta_engine/MANUSCRIPT.md (the honest paper) + AML response paper
pyproject.toml tests/   installable `intercepta` package + CLI + 17 unit tests
data/MANIFEST.md        provenance + access class for every external input (nothing committed)
INTEGRITY_SWEEP.md      transparent record of removed/flagged content
reproduce.sh requirements.txt
```

## Install & use as a tool
```bash
pip install -e .            # installs the `intercepta` package + CLI
pytest                      # 17 unit tests (leakage, markers, calibration gate, axes, synergy, admet) — no data needed
intercepta info             # version + HONEST SCOPE
intercepta rank    --expr tumor_expr.csv --drugs trametinib,gemcitabine --out ranking.csv   # needs INTERCEPTA_DATA
intercepta synergy --expr tumor_expr.csv --library drugcomb --out synergy.csv               # combinations arm (V23)
intercepta admet   --molecules "CC(=O)Oc1ccccc1C(=O)O" --tasks bbb_martins,herg --out admet.csv  # ADMET module (B30); needs intercepta[admet]
```
`intercepta rank` outputs, per (sample, drug): transfer_z, marker, combined_score, ood_distance, confidence.
`intercepta admet` predicts ADMET/safety properties from SMILES (structure-only screening filter, B30 — beats
trivial on all 22 TDC tasks, mid-leaderboard; scaffold-split only, NOT a safety guarantee). Each row carries an
applicability-domain flag. `intercepta synergy` ranks synergistic pairs from a known drug library (cell-line Loewe).
**Every prediction is LOW/MODERATE confidence by design** — a research hypothesis, never a clinical decision
(human clinical response was a well-powered null, see `LEDGER.md` / `papers/intercepta_engine/MANUSCRIPT.md`).

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
