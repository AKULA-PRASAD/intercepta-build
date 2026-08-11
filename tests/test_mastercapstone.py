"""MASTERCAPSTONE1 — one composite router across the WHOLE disease universe (pathogen + human) routes each
representative input correctly, with first-class cited abstention. Deterministic (pure router logic)."""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "..", "experiments", "MASTERCAPSTONE1_any_disease_composite", "run.py")


def _metrics():
    subprocess.run([sys.executable, RUN], check=True, capture_output=True,
                   cwd=os.path.dirname(RUN))
    return json.load(open(os.path.join(os.path.dirname(RUN), "results", "MASTERCAPSTONE1_metrics.json")))


def test_spans_both_halves_and_all_arms():
    m = _metrics()
    assert m["n_inputs"] == 16
    assert m["n_signal_backed"] == 12 and m["n_abstain"] == 4
    # all six validated arms (three pathogen, three human) are exercised
    assert set(m["arms_exercised"]) == {
        "conservation_breadth", "fba_essentiality", "structural_homology",
        "functional_dependency", "causal_gene", "genetic_association"}


def test_abstentions_are_first_class():
    m = _metrics()
    abst = {r["input"] for r in m["coverage"] if r["abstains"]}
    # both abstention TYPES, both halves: no-GEM parasite, monogenic w/o gene, class-level genetic, dark proteome
    assert any("parasite -GEM" in a for a in abst)
    assert any("monogenic -gene" in a for a in abst)
    assert any("musculoskeletal_renal" in a for a in abst)
    assert any("unknown" in a or "dark" in a for a in abst)


def test_key_routes():
    m = _metrics()
    by = {r["input"]: r for r in m["coverage"]}
    assert by["virus (SARS-CoV-2)"]["output_type"] == "structural_class_id"
    assert by["cancer (melanoma)"]["fired"] == ["functional_dependency"]
    assert by["complex/cardiovascular (CAD)"]["genetic_grade"] == "FULL"
    assert by["complex/metabolic (T2D)"]["genetic_grade"] == "CAPPED"
