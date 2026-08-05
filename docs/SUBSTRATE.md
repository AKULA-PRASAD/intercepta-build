# INTERCEPTA extensible evidence substrate — architecture & extension guide

The substrate is the vision's **"any disease → a query"** engine (founding charter law **U2**: no disease-specific code in
the core; disease-awareness through configuration). It is not a model — it is the **composition + governance layer** that
lets many independent evidence signals drive a single, safe, honest, *living* decision. Code: `src/intercepta/substrate.py`
(pure-Python core) + `src/intercepta/substrate_providers.py` (adapters). Tests: `tests/test_substrate.py` (data-free).
Demonstrations: `experiments/SUBSTRATE1..3`.

## Why it exists
The zero-data arc validated a set of signals and, just as importantly, a set of *corrections* (rank by conservation is
therapeutically dangerous; selectivity must be a hard filter; mechanism works without homology; self-improvement must be
confidence-gated). The substrate is where those signals + corrections live as reusable, composable, extensible governance —
so every future disease and every future evidence type benefits from them by construction.

## The core (3 ideas)
1. **Evidence, not features.** Every signal is an `EvidenceRecord(entity, signal, value, role, provider, tier, direction)`.
   `entity` is *anything* — a protein accession (front half) or a SMILES (back half). The core is entity-agnostic.
2. **Roles decide how evidence is used** (`SignalRole`):
   - `RANK` — contributes to the ranking (z-scored across candidates, tier- and direction-weighted).
   - `SAFETY_FILTER` — a **hard constraint**: a truthy value EXCLUDES the entity by construction (host-toxic proteins;
     PAINS molecules). This is the FRONT1/E2E2 lesson — safety is a filter, not a soft feature.
   - `ABSTAIN` — a truthy value marks the entity low-confidence / out-of-domain (TID1/TID3 honesty).
   - `FLAG` — advisory annotation (e.g. `needs_experimental_selectivity` — states what the system *cannot yet know*, the
     E2E2/FRONT2 honest boundary).
3. **Provenance tiers are the guardrail** (`ProvenanceTier`, ordered): `QUARANTINED < OWN_HYPOTHESIS < OWN_SINGLE <
   OWN_REPRODUCED < EXTERNAL_VALIDATED`. The engine only lets evidence at/above `min_decision_tier` drive a decision, and the
   `EvidenceStore` auto-**quarantines** self-generated records until they are independently **promoted**. This is what keeps a
   *living, self-absorbing* system from deceiving itself (SIL1/SIL2, enforced structurally; demonstrated in SUBSTRATE3).

## The flow (`TargetEngine.query`)
1. Every registered provider contributes evidence for the query's entities.
2. **Hard safety filters** exclude unsafe entities (they can never enter a shortlist).
3. Remaining `RANK` signals are z-scored across the safe candidates and combined, weighted by provenance tier × direction.
4. Entities with no usable RANK evidence (or an ABSTAIN signal) are flagged low-confidence and sink below the shortlist.
5. Output: `TargetVerdict`s (safe / abstain / rank_score / confidence / full evidence provenance / flags), ranked.

## How to extend it (the whole point)
Add a new evidence type **without touching the core** — subclass `EvidenceProvider`:

```python
from intercepta.substrate import EvidenceProvider, SignalRole, ProvenanceTier

class MyProvider(EvidenceProvider):
    name, signal = "my_signal", "my_signal"
    role = SignalRole.RANK                       # or SAFETY_FILTER / ABSTAIN / FLAG
    tier = ProvenanceTier.OWN_REPRODUCED         # its LEDGER validation status
    direction = 1.0                              # +1: higher = better target; -1: lower = better
    def provide(self, query):
        for e in query.entities:
            yield self._rec(e, my_value_for(e))

engine.register(MyProvider())                    # done — it now composes with everything else
```

Register it, and it immediately participates in safety/abstention/ranking under the same governance. New databases, new
mechanistic signals, new methods, and — via `EvidenceStore.add` + `.promote` — new *experimental results* plug in the same
way. That is the "living net that grows with every query."

## What is demonstrated (reproduced ×2)
- **SUBSTRATE1** — front half on real E. coli + M. tuberculosis: composes conservation + FBA-essentiality + chokepoint,
  excludes host-toxic by construction (0 in every shortlist), flags host-homologous survivors, and **beats the naive
  conservation baseline** on known-target recovery (33/94 E. coli, 17/67 Mtb vs 26/13).
- **SUBSTRATE2** — the same core ranks 2,754 **molecules** (QED + SAscore + PAINS filter), excluding structural-alert
  liabilities by construction. Proves the architecture is entity-agnostic and spans the whole pipeline.
- **SUBSTRATE3** — continuous absorption: self-derived evidence is quarantined and inert (no self-deception); the net grows
  only on independent/external evidence; false self-beliefs never corrupt a decision.

## Use it (CLI — the 10th shipped tool)
The source-agnostic governance engine is shipped as `intercepta substrate`: pipe in an evidence table (from any source) and
get a safe, provenance-tiered, abstaining ranked shortlist.

```
intercepta substrate --evidence evidence.csv --min-tier own_reproduced --out shortlist.csv
# evidence.csv columns: entity,signal,value[,role,tier,direction,provider]
#   role in {rank,safety_filter,abstain,flag}; tier in {quarantined,own_hypothesis,own_single,own_reproduced,external_validated}
```

`SAFETY_FILTER` rows exclude by construction; evidence below `--min-tier` (and self-generated evidence) is quarantined and
cannot drive a decision; every output row carries its confidence tier, contributing signals, and flags. The Python API
(`intercepta.substrate` + `substrate_providers`) is used when you want live bio providers (mmseqs/COBRApy/fpocket) as in the
SUBSTRATE1–4 experiments.

## Honest scope
The substrate is composition + governance — it does **not** itself validate biology. Each provider carries its own
validation tier (traceable to LEDGER.md), and the substrate only lets sufficiently-tiered evidence drive a decision. Outputs
are confidence-tiered candidate **hypotheses with full provenance**, not validated targets or drugs. The binding/potency and
true-selectivity stages remain weak/resource-gated (see the zero-data REPORT); the substrate is built so that the moment real
experimental evidence exists, it enters as high-tier evidence and every decision improves.
