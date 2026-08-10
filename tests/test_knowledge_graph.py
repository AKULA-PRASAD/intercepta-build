"""F9 — pytest coverage for the composite knowledge graph (provenance + abstention integrity)."""
import os
import pytest
from intercepta.knowledge_graph import KnowledgeGraph, GRADES

KG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "experiments", "F9_knowledge_graph", "kg.json")


@pytest.fixture(scope="module")
def kg():
    return KnowledgeGraph.load(KG_PATH)


def test_loads_and_has_content(kg):
    s = kg.stats()
    assert s["arms"] >= 10 and s["deadends"] >= 15 and s["disease_classes"] >= 5


def test_integrity_no_violations(kg):
    assert kg.integrity_check() == []


def test_every_claim_edge_has_provenance_and_reproduced(kg):
    for a in kg.arms.values():
        for app in a["applies_to"]:
            assert app["grade"] in GRADES
            if app["grade"] in ("FULL", "CAPPED"):
                assert a.get("evidence"), f"{a['id']} claim without evidence"
                assert "reproduced" in a, f"{a['id']} claim without reproduced flag"


def test_every_abstain_cites_known_deadend(kg):
    n = 0
    for a in kg.arms.values():
        for app in a["applies_to"]:
            if app["grade"] == "ABSTAIN":
                assert app.get("deadend") in kg.deadends
                n += 1
    assert n >= 1


def test_every_deadend_is_falsifiably_reopenable(kg):
    for d in kg.deadends.values():
        assert d["reopen_trigger"] and d["evidence"]


def test_virus_abstains_on_metabolic_target_id(kg):
    dec = kg.query("virus")
    assert any("D1" in ab["because_deadend"] for ab in dec.abstains)


def test_complex_disease_has_both_genetic_arms(kg):
    caps = {a["arm"] for a in kg.query("complex_human_disease").applicable}
    assert {"genetic_support_target_id", "cis_MR_causal_target_id"} <= caps


def test_negatives_ledger_spans_categories(kg):
    cats = {d["category"] for d in kg.negatives_ledger()}
    assert {"dead-end-closed", "falsified-own-claim", "honest-negative-result",
            "leakage-artifact-caught"} <= cats
