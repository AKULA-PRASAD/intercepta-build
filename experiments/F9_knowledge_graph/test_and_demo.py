#!/usr/bin/env python
"""F9 — integrity tests + demo queries for the composite knowledge graph.
Asserts the two hard invariants (every claim edge has provenance+reproduced; every ABSTAIN cites a dead-end),
then demonstrates per-disease-class queries. Run: python test_and_demo.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
from intercepta.knowledge_graph import KnowledgeGraph, GRADES

KG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kg.json")

def main():
    kg = KnowledgeGraph.load(KG)

    # ---- invariant 1+2 via integrity_check ----
    errs = kg.integrity_check()
    assert not errs, "INTEGRITY FAILURES:\n  " + "\n  ".join(errs)
    print("integrity_check: PASS (no violations)")

    # ---- invariant: every ABSTAIN edge cites a KNOWN dead-end ----
    n_abstain = 0
    for a in kg.arms.values():
        for app in a.get("applies_to", []):
            assert app["grade"] in GRADES
            if app["grade"] == "ABSTAIN":
                assert app.get("deadend") in kg.deadends, f"{a['id']} abstains without a known dead-end"
                n_abstain += 1
    print(f"abstention edges all cite a dead-end: PASS ({n_abstain} abstain edges)")

    # ---- invariant: every dead-end is falsifiably reopenable ----
    for d in kg.deadends.values():
        assert d["reopen_trigger"], f"dead-end {d['id']} not reopenable"
    print(f"all {len(kg.deadends)} dead-ends carry a reopen trigger: PASS")

    print("\nstats:", kg.stats())

    # ---- demo queries ----
    for dc in ["bacteria_self_metabolism", "virus", "complex_human_disease", "cancer"]:
        print("\n" + "=" * 90)
        print(kg.query(dc).summary())

    # ---- the honest negatives ledger (first-class) ----
    print("\n" + "=" * 90)
    print("FIRST-CLASS NEGATIVES (by category):")
    from collections import defaultdict
    bycat = defaultdict(list)
    for d in kg.negatives_ledger():
        bycat[d["category"]].append(d["id"])
    for cat in sorted(bycat):
        print(f"  {cat}: {', '.join(bycat[cat])}")
    fr = kg.fabrications_removed
    print(f"  removed-fabrications: {len(fr['nine_fake_claims'])} fake claims + "
          f"{len(fr['deleted_result_files'])} deleted artifact groups (INTEGRITY_SWEEP.md)")

    print("\nALL F9 TESTS PASS")

if __name__ == "__main__":
    main()
