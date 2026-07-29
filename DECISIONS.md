# Decision log — INTERCEPTA build (append-only)

## 2026-07-29 — D1: Seed a clean, separate Phase-B build repo
Decision: create `~/INTERCEPTA_BUILD` distinct from the 22 GB exploration tree (`~/INTERCEPTA`) and the audit
repo (`~/kaalcura`). Rationale: the build must contain only verified, reproduced, provenance-tracked work; the
exploration repos carry falsified/abandoned branches that would blur the ledger. Reversible.

## 2026-07-29 — D2: Phase B scope = transcriptomic drug-response prediction, not therapy selection
Decision: build against the near-term, achievable, evidence-supported goal (Phase B), not the falsified
therapy-selection claim. Rationale: LEDGER V1 (a real transferable signal exists) supports Phase B; the
selection coordinate is falsified at power (<5%). Novel ideas (velocity time machine) stay in the ledger as
untestable until the specified data exists — not in the build path.

## 2026-07-29 — D3: The bar is +0.212, established in-repo by B1 before any new modeling
Decision: no new model is accepted until B1 reproduces the leakage-free ceiling inside this repo, and every
future model is measured against it with the full falsification battery + external replication. Rationale:
Constitution rules 3 & 8 — bar before boast, positives guilty until proven innocent.

## 2026-07-29 — D4: Data referenced by sha256 manifest, never committed
Decision: inputs stay out of git; `INTERCEPTA_DATA` env var + `data/MANIFEST.md` sha256 verification at load.
Rationale: reproducibility without shipping 1.5 GB of public data or risking a silent data swap.
