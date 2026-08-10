"""F9 — the provenance-tracked composite KNOWLEDGE GRAPH.

Unifies the program's evidence into one queryable structure whose INTEGRITY is that negatives, dead-ends,
and abstention-boundaries are FIRST-CLASS nodes alongside the validated arms. This is the machine-readable
form of the "composite architecture" (many validated models + their transfer-conditions + where they fail)
and the backend the COMPOSITE router's abstention logic can cite.

Two hard invariants, enforced by `integrity_check()` (and the F9 tests):
  1. Every VALIDATED-arm claim edge must carry `evidence` (a repo path) AND an explicit `reproduced` flag.
  2. Every ABSTAIN decision must cite a specific dead-end node (no silent / unexplained abstention).

This module is pure-stdlib and self-contained (loads `kg.json`); it makes NO new scientific claim — it is
integration/provenance, not a new signal (see experiments/F9_knowledge_graph/SUMMARY.md, honest scope).
"""
from __future__ import annotations
import json, os
from dataclasses import dataclass, field
from typing import Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_KG = os.path.join(_HERE, "..", "..", "experiments", "F9_knowledge_graph", "kg.json")

GRADES = {"FULL", "CAPPED", "ABSTAIN"}  # transfer grades an arm can have for a disease class


@dataclass
class Decision:
    disease_class: str
    applicable: list = field(default_factory=list)   # [{arm, capability, grade, metric, evidence, reproduced}]
    abstains: list = field(default_factory=list)      # [{capability, because_deadend, reopen_trigger}]
    bounding_deadends: list = field(default_factory=list)

    def summary(self) -> str:
        lines = [f"disease_class = {self.disease_class}"]
        if self.applicable:
            lines.append("  APPLICABLE validated arms:")
            for a in self.applicable:
                rep = "reproduced×2" if a["reproduced"] else "NOT-reproduced"
                lines.append(f"    - [{a['grade']}] {a['capability']} via {a['arm']} — {a['metric']} ({rep}; {a['evidence']})")
        if self.abstains:
            lines.append("  ABSTAIN (with cited reason):")
            for ab in self.abstains:
                lines.append(f"    - {ab['capability']}: {ab['because_deadend']} — reopen iff: {ab['reopen_trigger']}")
        return "\n".join(lines)


class KnowledgeGraph:
    def __init__(self, data: dict):
        self.data = data
        self.arms = {a["id"]: a for a in data.get("arms", [])}
        self.deadends = {d["id"]: d for d in data.get("deadends", [])}
        self.disease_classes = data.get("disease_classes", [])
        self.fabrications_removed = data.get("fabrications_removed", [])

    @classmethod
    def load(cls, path: Optional[str] = None) -> "KnowledgeGraph":
        with open(path or _DEFAULT_KG) as f:
            return cls(json.load(f))

    # ---- integrity: the graph is only trustworthy if these hold ----
    def integrity_check(self) -> list:
        errors = []
        for aid, a in self.arms.items():
            for app in a.get("applies_to", []):
                if app["grade"] not in GRADES:
                    errors.append(f"arm {aid}: bad grade {app['grade']!r}")
                if app["grade"] in ("FULL", "CAPPED"):
                    if not a.get("evidence"):
                        errors.append(f"arm {aid}: FULL/CAPPED claim without evidence path")
                    if "reproduced" not in a:
                        errors.append(f"arm {aid}: claim without explicit reproduced flag")
            for did in a.get("bounded_by", []):
                if did not in self.deadends:
                    errors.append(f"arm {aid}: bounded_by unknown dead-end {did!r}")
        for did, d in self.deadends.items():
            if not d.get("evidence"):
                errors.append(f"deadend {did}: missing evidence path")
            if not d.get("reopen_trigger"):
                errors.append(f"deadend {did}: missing reopen_trigger (dead-ends must be falsifiable-reopenable)")
        return errors

    # ---- the core query: what applies to a disease class, and where must we abstain (and why) ----
    def query(self, disease_class: str) -> Decision:
        dc = disease_class.lower()
        dec = Decision(disease_class=disease_class)
        seen_caps = {}
        for a in self.arms.values():
            for app in a.get("applies_to", []):
                if app["cls"].lower() != dc:
                    continue
                if app["grade"] == "ABSTAIN":
                    did = app.get("deadend")
                    d = self.deadends.get(did, {})
                    dec.abstains.append({"capability": a["capability"],
                                         "because_deadend": f"{did}: {d.get('name', '?')}",
                                         "reopen_trigger": d.get("reopen_trigger", "?")})
                else:
                    dec.applicable.append({"arm": a["id"], "capability": a["capability"], "grade": app["grade"],
                                           "metric": app.get("metric", a.get("headline_metric", "")),
                                           "evidence": a.get("evidence", ""), "reproduced": bool(a.get("reproduced"))})
                    seen_caps[a["capability"]] = a
        for a in seen_caps.values():
            for did in a.get("bounded_by", []):
                if did in self.deadends and did not in [b["id"] for b in dec.bounding_deadends]:
                    dec.bounding_deadends.append({"id": did, "name": self.deadends[did]["name"]})
        return dec

    def negatives_ledger(self) -> list:
        """All first-class negatives (dead-ends + removed fabrications), for the honest accounting."""
        return sorted(self.deadends.values(), key=lambda d: (d.get("category", ""), d["id"]))

    def stats(self) -> dict:
        grades = [app["grade"] for a in self.arms.values() for app in a.get("applies_to", [])]
        return {"arms": len(self.arms), "deadends": len(self.deadends),
                "fabrications_removed": len(self.fabrications_removed),
                "disease_classes": len(self.disease_classes),
                "edges_FULL": grades.count("FULL"), "edges_CAPPED": grades.count("CAPPED"),
                "edges_ABSTAIN": grades.count("ABSTAIN")}
