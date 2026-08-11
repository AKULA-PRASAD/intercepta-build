# NUCLEIC1 — status: ENGINE BUILT, empirical validation BLOCKED by validation-data access (honest, not faked)

**Status 2026-08-11: engine implemented + real; empirical efficacy validation NOT completed — and NOT faked.**

## What is real and done
- `sirna_engine.py`: a deterministic siRNA design engine implementing **cited, independently-validated** rules
  — Reynolds 2004 (8-criterion), Ui-Tei 2004 (4-rule), thermodynamic end-asymmetry (Khvorova/Schwarz via a
  nearest-neighbor ΔG table), immunostimulatory/homopolymer/GC filters. Enumerates + ranks 19-mer candidates
  over a target mRNA. No training data, no ViennaRNA. This module claims **no new efficacy algorithm** — its
  intended contribution is systemic (the first modality in the composite that reaches UNDRUGGABLE targets,
  behind MODALITY1's ASO/siRNA triage; sidesteps the affinity wall AFFINITY2/D2).

## Why it is NOT declared validated (the honest blocker)
Pre-registered validation V2 requires **real siRNA data** — either measured-efficacy siRNAs (to test potent-vs-
random ranking) or genuine literature-validated potent sequences. In this environment I could not source a
clean, citable open siRNA-efficacy benchmark despite five reliable-method attempts (Zenodo API, figshare API
[only a figure], NCBI GEO, multiple GitHub raws). **I refused to fabricate positive-control sequences** (a
self-test placeholder was caught and is NOT used as evidence). Therefore I cannot honestly claim the composite
scorer predicts real-world potency. What IS verifiable without external data — that each rule matches its
published specification (V1) — is a fidelity check, not proof the composite ranks efficacy.

## The honest pattern (and the distinction from over-gating)
This is the SECOND consecutive genuinely-buildable module (after DMS1 durability) whose **validation** is blocked
by real-world data that is not cleanly fetchable in this sandbox — while the engine/code itself is buildable.
This is NOT the earlier error of gating-by-classification-without-trying: here the engine WAS built and the data
WAS genuinely pursued. The binding constraint on completing these specific modules is **validation-data ACCESS**
(a channel/resource question), not computation and not a fundamental dead-end. The data exists in the literature
(e.g., Huesken 2005, siRecords); it was not retrievable here without spiraling.

## Honest options to complete it (no fake, no shortcut)
1. **Supply the data:** an open siRNA-efficacy table (sequence + measured knockdown; e.g., Huesken 2005 SI) →
   NUCLEIC1's V2 (held-out efficacy correlation) + the systemic coverage result run cleanly and it ships validated.
2. **Or pivot** to an over-gated component whose validation uses data ALREADY cached (Open Targets, DepMap, CARD,
   GEMs) — e.g., signaling/network-target ID validated against cached OT drug targets — avoiding the external-data wall.

*No `results/` metrics written (no validated score to report). Engine + pre-registration are committed as real
work-in-progress; nothing is claimed as validated.*
