"""INTERCEPTA extensible evidence substrate — the "any disease -> a query" core.

This is the vision's enduring differentiator, built to the founding charter's law **U2** ("no disease-specific code paths
in the core engine; all disease-awareness through configuration") and the **continuous-absorption guardrail** ("all
absorbed knowledge is provenance- and confidence-tiered; self-generated / low-tier records are QUARANTINED and down-weighted
until they survive validation, never treated as ground truth"). It composes independent EVIDENCE PROVIDERS (each a pluggable
adapter for one signal) into a provenance-tiered, confidence-tiered, SAFE, abstaining target ranking — and it bakes in every
hard-won correction from the zero-data arc:

- **Mechanism over homology** (MET1-3): mechanistic signals (e.g. FBA essentiality) are first-class RANK evidence.
- **Safety is a hard filter, not a soft feature** (FRONT1/E2E2): SAFETY_FILTER providers (e.g. host non-homology) EXCLUDE
  unsafe entities by construction; the "rank by conservation" workhorse is therapeutically dangerous on its own.
- **Honest abstention** (TID1/TID3/TID4): entities with no usable signal are FLAGGED low-confidence, never silently ranked.
- **Selectivity beyond sequence is unresolved** (E2E2/FRONT2): entities that pass a safety filter but are host-homologous
  carry an explicit `needs_experimental_selectivity` flag — the substrate states what it CANNOT yet know.
- **Provenance tiering** (the guardrail): self-generated findings enter QUARANTINED and cannot influence a decision until
  reproduced/promoted — the anti-self-deception mechanism that keeps a living, self-absorbing system honest.

HONEST SCOPE: this is the *composition + governance* layer. It does not itself validate biology; each provider carries its
own validation status (LEDGER) and provenance tier, and the substrate only lets sufficiently-tiered evidence drive a
decision. Outputs are confidence-tiered candidate hypotheses with full provenance, NOT validated targets or drugs.

The core (this module) is pure-Python and data-free unit-testable. Real bio providers (mmseqs/COBRApy/fpocket adapters)
live in `substrate_providers.py` and lazy-import their heavy deps, so importing the core never requires them.
"""
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Callable, Iterable


class ProvenanceTier(IntEnum):
    """Ordered trust levels. Higher = more trustworthy. QUARANTINED evidence NEVER drives a decision."""
    QUARANTINED = 0          # self-generated, unvalidated -> excluded from decisions (the guardrail)
    OWN_HYPOTHESIS = 1       # our own prediction, not reproduced
    OWN_SINGLE = 2           # our own result, single run
    OWN_REPRODUCED = 3       # our own result, reproduced x2 + committed (LEDGER-grade)
    EXTERNAL_VALIDATED = 4   # externally validated fact (curated DB / peer-reviewed)


# tier -> trust weight multiplier (QUARANTINED contributes nothing)
TIER_WEIGHT = {
    ProvenanceTier.QUARANTINED: 0.0,
    ProvenanceTier.OWN_HYPOTHESIS: 0.25,
    ProvenanceTier.OWN_SINGLE: 0.5,
    ProvenanceTier.OWN_REPRODUCED: 1.0,
    ProvenanceTier.EXTERNAL_VALIDATED: 1.25,
}


class SignalRole(Enum):
    RANK = "rank"                    # contributes to the target ranking (see `direction`)
    SAFETY_FILTER = "safety_filter"  # HARD constraint: value truthy => entity is UNSAFE => excluded
    ABSTAIN = "abstain"              # value truthy => entity is low-confidence / out-of-domain
    FLAG = "flag"                    # advisory annotation only (e.g. needs_experimental_selectivity)


@dataclass(frozen=True)
class EvidenceRecord:
    """One piece of evidence about one entity (e.g. a protein) from one provider."""
    entity: str
    signal: str
    value: float
    role: SignalRole
    provider: str
    tier: ProvenanceTier
    direction: float = 1.0           # RANK only: +1 => higher value is a BETTER target, -1 => lower is better
    meta: dict = field(default_factory=dict)

    @property
    def usable(self) -> bool:
        return self.tier > ProvenanceTier.QUARANTINED


@dataclass
class TargetVerdict:
    entity: str
    safe: bool
    abstain: bool
    rank_score: float
    confidence: str                  # "high" | "moderate" | "low" | "excluded"
    evidence: list = field(default_factory=list)   # list[EvidenceRecord]
    flags: list = field(default_factory=list)      # list[str]


class EvidenceProvider(ABC):
    """A pluggable adapter for one evidence signal. Disease-agnostic: it receives a query and returns records.

    Subclasses declare their `name`, `signal`, `role`, and default `tier` (its LEDGER validation status).
    """
    name: str = "provider"
    signal: str = "signal"
    role: SignalRole = SignalRole.RANK
    tier: ProvenanceTier = ProvenanceTier.OWN_REPRODUCED
    direction: float = 1.0

    @abstractmethod
    def provide(self, query: "Query") -> Iterable[EvidenceRecord]:
        ...

    def _rec(self, entity: str, value: float, **meta) -> EvidenceRecord:
        return EvidenceRecord(entity=entity, signal=self.signal, value=float(value), role=self.role,
                              provider=self.name, tier=self.tier, direction=self.direction, meta=meta)


@dataclass
class Query:
    """A disease/pathogen expressed purely as configuration (U2) — no disease-specific code in the core."""
    pathogen: str
    entities: list                    # candidate entity ids (e.g. proteome accessions)
    config: dict = field(default_factory=dict)


class EvidenceStore:
    """Append-only, provenance-tiered store — the LIVING substrate. Self-generated findings enter QUARANTINED and cannot
    drive a decision until `promote`d (after independent reproduction). `active()` never returns quarantined records."""

    def __init__(self):
        self._records: list[EvidenceRecord] = []

    def add(self, records: Iterable[EvidenceRecord], quarantine_self_generated: bool = True) -> int:
        n = 0
        for r in records:
            if quarantine_self_generated and r.tier in (ProvenanceTier.OWN_HYPOTHESIS, ProvenanceTier.OWN_SINGLE):
                # a freshly self-generated record is provisional; downgrade to QUARANTINED until promoted
                r = EvidenceRecord(r.entity, r.signal, r.value, r.role, r.provider,
                                   ProvenanceTier.QUARANTINED, r.direction, {**r.meta, "was_tier": int(r.tier)})
            self._records.append(r); n += 1
        return n

    def promote(self, provider: str, to_tier: ProvenanceTier = ProvenanceTier.OWN_REPRODUCED) -> int:
        """Promote quarantined records from a provider after they survive validation (reproduced x2)."""
        out, n = [], 0
        for r in self._records:
            if r.provider == provider and r.tier == ProvenanceTier.QUARANTINED:
                out.append(EvidenceRecord(r.entity, r.signal, r.value, r.role, r.provider, to_tier, r.direction, r.meta)); n += 1
            else:
                out.append(r)
        self._records = out
        return n

    def active(self) -> list[EvidenceRecord]:
        return [r for r in self._records if r.usable]

    def __len__(self):
        return len(self._records)


def _zscore(vals: list[float]) -> list[float]:
    if not vals:
        return []
    m = sum(vals) / len(vals)
    var = sum((v - m) ** 2 for v in vals) / len(vals)
    sd = math.sqrt(var)
    return [0.0 for _ in vals] if sd < 1e-9 else [(v - m) / sd for v in vals]


class TargetEngine:
    """The core "any disease -> a query" engine. Register providers; call `query()`; get a SAFE, provenance-tiered,
    abstaining, ranked shortlist. Disease-agnostic (U2) — the pathogen is a query parameter, not code."""

    def __init__(self, min_decision_tier: ProvenanceTier = ProvenanceTier.OWN_REPRODUCED):
        self.providers: list[EvidenceProvider] = []
        self.min_decision_tier = min_decision_tier

    def register(self, provider: EvidenceProvider) -> "TargetEngine":
        self.providers.append(provider)
        return self

    def query(self, query: Query, store: EvidenceStore | None = None) -> list[TargetVerdict]:
        store = store or EvidenceStore()
        for p in self.providers:
            store.add(list(p.provide(query)), quarantine_self_generated=False)  # providers declare their own real tier
        records = [r for r in store.active() if r.tier >= self.min_decision_tier]
        by_entity: dict[str, list[EvidenceRecord]] = {e: [] for e in query.entities}
        for r in records:
            by_entity.setdefault(r.entity, []).append(r)

        # 1) HARD safety filters — any truthy SAFETY_FILTER excludes the entity by construction (FRONT1/E2E2)
        unsafe = {e: [r for r in recs if r.role == SignalRole.SAFETY_FILTER and r.value] for e, recs in by_entity.items()}
        # 2) RANK signals -> per-signal z-score across the SAFE, non-abstaining candidates, tier+direction weighted
        safe_entities = [e for e in query.entities if not unsafe.get(e)]
        rank_sig: dict[str, dict[str, float]] = {}   # signal -> {entity: value*direction}
        rank_weight: dict[str, float] = {}
        for e in safe_entities:
            for r in by_entity.get(e, []):
                if r.role == SignalRole.RANK:
                    rank_sig.setdefault(r.signal, {})[e] = r.value * r.direction
                    rank_weight[r.signal] = TIER_WEIGHT[r.tier]
        # z-score each signal across the safe candidates that have it, then weighted-sum
        z_by_entity: dict[str, float] = {e: 0.0 for e in safe_entities}
        wsum = 0.0
        for sig, vals in rank_sig.items():
            ents = list(vals)
            zs = _zscore([vals[e] for e in ents])
            w = rank_weight.get(sig, 1.0); wsum += w
            for e, z in zip(ents, zs):
                z_by_entity[e] += w * z
        if wsum > 0:
            z_by_entity = {e: s / wsum for e, s in z_by_entity.items()}

        verdicts: list[TargetVerdict] = []
        for e in query.entities:
            recs = by_entity.get(e, [])
            safe = not unsafe.get(e)
            # abstain if any ABSTAIN signal truthy OR no RANK evidence at all (TID1/TID3 honesty)
            abstained = any(r.role == SignalRole.ABSTAIN and r.value for r in recs) or \
                        (safe and not any(r.role == SignalRole.RANK for r in recs))
            flags = sorted({r.signal for r in recs if r.role == SignalRole.FLAG and r.value})
            n_rank = sum(1 for r in recs if r.role == SignalRole.RANK)
            if not safe:
                conf = "excluded"
            elif abstained:
                conf = "low"
            elif n_rank >= 2:
                conf = "high"
            else:
                conf = "moderate"
            verdicts.append(TargetVerdict(entity=e, safe=safe, abstain=abstained,
                                          rank_score=round(z_by_entity.get(e, 0.0), 4) if safe else float("-inf"),
                                          confidence=conf, evidence=recs, flags=flags))
        # ranked: safe & non-abstaining first, by rank_score desc; excluded/abstained sink
        verdicts.sort(key=lambda v: (v.safe and not v.abstain, v.rank_score if v.safe else float("-inf")), reverse=True)
        return verdicts

    def shortlist(self, query: Query, k: int = 20, store: EvidenceStore | None = None) -> list[TargetVerdict]:
        vs = self.query(query, store=store)
        return [v for v in vs if v.safe and not v.abstain][:k]
