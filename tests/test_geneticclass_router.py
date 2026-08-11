"""COMPOSITE5 / GENETICCLASS1 — the genetic-association arm is now disease-class-aware in the router.
Verifies: FULL classes fire full-grade; the ABSTAIN class gates out; CAPPED + undeclared preserve the
original blanket-CAPPED behaviour (backward compatible)."""
from intercepta.composite_router import decide, BiologyClass, Signal

GA = Signal.GENETIC_ASSOCIATION.value
HCD = BiologyClass.HUMAN_COMPLEX_DISEASE


def _fired(dec):
    return set(dec.signals_fired)


def _gated_signals(dec):
    return {g.signal if hasattr(g, "signal") else g.get("signal") for g in dec.signals_gated_out}


def test_full_class_fires_full_grade():
    dec = decide(HCD, has_gwas_evidence=True, disease_class="cardiovascular")
    assert GA in _fired(dec)
    flags = [f for f in dec.uncertainty_flags if f["signal"] == GA]
    assert flags and flags[0].get("grade") == "FULL_by_disease_class"


def test_abstain_class_gates_genetic_arm():
    dec = decide(HCD, has_gwas_evidence=True, disease_class="musculoskeletal_renal")
    assert GA not in _fired(dec)
    assert GA in _gated_signals(dec)


def test_capped_class_fires_capped():
    dec = decide(HCD, has_gwas_evidence=True, disease_class="metabolic")
    assert GA in _fired(dec)
    flags = [f for f in dec.uncertainty_flags if f["signal"] == GA]
    assert flags and flags[0].get("confidence_cap") == 0.5   # capped default, NOT the FULL upgrade


def test_undeclared_class_is_backward_compatible():
    # no disease_class -> original blanket-CAPPED firing (the pre-COMPOSITE5 behaviour)
    dec = decide(HCD, has_gwas_evidence=True)
    assert GA in _fired(dec)
    flags = [f for f in dec.uncertainty_flags if f["signal"] == GA]
    assert flags and flags[0].get("confidence_cap") == 0.5 and flags[0].get("grade") is None


def test_no_gwas_evidence_still_gates_regardless_of_class():
    dec = decide(HCD, has_gwas_evidence=False, disease_class="cardiovascular")
    assert GA not in _fired(dec)
    assert GA in _gated_signals(dec)
