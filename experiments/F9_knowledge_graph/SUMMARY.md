# F9 — composite knowledge graph (validated arms + FIRST-CLASS negatives, with provenance)

*The machine-readable form of the program's "composite architecture" (many validated models + their
transfer-conditions + where they fail). Built deterministically from the authoritative records; every claim
carries provenance; **negatives/dead-ends are first-class nodes**. Integration/provenance — makes NO new
scientific claim. `build_kg.py` (sha-stable) → `kg.json`; `src/intercepta/knowledge_graph.py` (load/query/
integrity); `tests/test_knowledge_graph.py` (8 tests, in the passing suite); CLI `intercepta kg`.*

## What it is
A queryable graph unifying **11 validated arms**, **20 first-class negatives/dead-ends**, **7 disease classes**,
and the **9 removed fabrications** — sourced from `LEDGER.md` (V1–V23), `COMPUTATIONAL_DEAD_ENDS.md` (D1–D9),
`src/intercepta/composite_router` (transfer conditions), `MR1`, and `INTEGRITY_SWEEP.md`. Edge grades:
**9 FULL, 9 CAPPED, 1 ABSTAIN** (abstention is rare by construction — most classes have *some* applicable arm).

## Two hard integrity invariants (enforced by `integrity_check()` + tests)
1. **Every validated-arm claim edge carries an evidence path AND an explicit `reproduced` flag.** No claim
   without provenance.
2. **Every ABSTAIN decision cites a specific dead-end node** (with that dead-end's falsifiable reopen-trigger).
   No silent/unexplained abstention. And every dead-end is falsifiably reopenable.

## What it does (the query)
`kg.query(disease_class)` → the applicable validated arms (grade + metric + evidence + reproduced), plus the
capabilities it must **ABSTAIN** on and *why* (cited dead-end + reopen condition), plus the dead-ends that
**bound** the applicable arms. Examples (`intercepta kg --class …`):
- **virus** → host-safety FULL + structural target-class CAPPED; **ABSTAINS on metabolic target-ID, citing D1**
  (no metabolism; reopen iff mechanism labels/new modality).
- **complex_human_disease** → both genetic arms FULL (`genetic_support` OR 2.26, `cis_MR` OR 3.16), repurposing
  CAPPED — with `cis_MR` bounded by MR1-H2 (redundant-with-OT).
- **bacteria_self_metabolism** → FBA OR 5–64 FULL + conservation 0.908 FULL + host-safety FULL, all bounded by D1.
- **cancer** → synergy FULL (known-library) bounded by the novel-drug failure (B25) + B26; dependency CAPPED
  (target-tautological, B23); expression-transfer CAPPED (weak, D3).

## The first-class negatives (`intercepta kg --negatives`) — the honest failure map
Encoded by category, each with metric + reopen-trigger + evidence path:
- **dead-end-closed:** D1 (non-metabolic mechanism ceiling 0.9078), D2 (novel-target affinity), D3 (baseline
  drug-response wall), D4 (breadth), D5 (generation), D7 (ipTM), D8 (audits).
- **falsified-own-claim:** D9/DYNAMICS5 (durability entropy p=0.99997 wrong-direction), N1 (mechanistic-coherence
  withdrawn), B25 (novel-drug synergy 0.25→0.025), B20 (V19/V20 external-replication fail), PARARESOLVE1.
- **honest-negative-result:** MR1-H2, B26 (mechanism-synergy), AMR1 (resistance-liability 0.556), B23
  (functional advantage is target-tautological).
- **leakage/artifact-caught:** AFFINITY1 (Boltz training-leak), STRUCTREPURPOSE1/D6 (promiscuity 25/32 null),
  B10 (cancer-type confound), MR1 parquet collider (positive control inverted → rebuilt universe).
- **removed fabrications:** the 9 FAKE claims (hand-written MoA/safety/synthesis/trial text + hand-typed Pareto
  scores presented as pipeline output) + deleted artifact chains (`INTEGRITY_SWEEP.md`, `VISION_AUDIT.txt`).

## Honest scope (what F9 is NOT)
It creates **no new biological signal** and does not raise the program's contribution — it is provenance/
integration engineering. Its value: it makes the honest composite *queryable*, operationalizes **abstention as
integrity** (cited, reopenable), and keeps negatives first-class so the map of *where the vision fails* is as
accessible as where it works. The graph is only as current as its source records; re-run `build_kg.py` after
new experiments.

## Reproduce
`python build_kg.py` (deterministic; kg.json sha-stable) · `python test_and_demo.py` · `pytest tests/test_knowledge_graph.py`
· `intercepta kg --class <c>` / `intercepta kg --negatives`.
