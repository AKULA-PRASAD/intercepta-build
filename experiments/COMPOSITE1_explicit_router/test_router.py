"""COMPOSITE1 — DATA-FREE unit tests for the router's transfer-gate + abstention logic.

No files, no network, no heavy deps: exercises the PURE `decide()` / `detect_class()` gating logic only.
Run: `python -m pytest test_router.py -q`  OR  `python test_router.py` (self-runs without pytest).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
from intercepta.composite_router import (  # noqa: E402
    CompositeRouter, BiologyClass, Signal, decide, detect_class,
    HOST_EMBEDDED_ABSTENTION, TRANSFER_GATE, VIRUS_MAX_PROTEOME,
)


# ---- bacterium: FBA fires -> shortlist ------------------------------------------------------------
def test_bacterium_fires_fba_shortlist():
    d = decide(BiologyClass.BACTERIUM, organism="ecoli")
    assert d.output_type == "shortlist"
    assert Signal.FBA_ESSENTIALITY.value in d.signals_fired
    assert Signal.CONSERVATION_BREADTH.value in d.signals_fired
    assert d.abstention is None


# ---- free eukaryote: FBA (weaker) still fires -> shortlist ----------------------------------------
def test_free_eukaryote_fires_fba():
    d = decide(BiologyClass.FREE_EUKARYOTE, organism="scerevisiae")
    assert d.output_type == "shortlist"
    assert Signal.FBA_ESSENTIALITY.value in d.signals_fired


# ---- virus: structure ONLY; FBA and sequence-repurposing must NOT fire ----------------------------
def test_virus_structure_only_no_fba():
    d = decide(BiologyClass.VIRUS, organism="sars2")
    assert d.output_type == "structural_class_id"
    assert d.signals_fired == [Signal.STRUCTURAL_HOMOLOGY.value]
    assert Signal.FBA_ESSENTIALITY.value not in d.signals_fired
    assert Signal.SEQUENCE_REPURPOSING.value not in d.signals_fired  # validation-grade only
    gated = {g.signal for g in d.signals_gated_out}
    assert Signal.FBA_ESSENTIALITY.value in gated


# ---- host-dependent parasite: FBA gated out -> ABSTAIN with the exact reason ----------------------
def test_parasite_abstains_fba_gated():
    d = decide(BiologyClass.HOST_DEPENDENT_PARASITE, organism="pfalciparum")
    assert d.output_type == "abstention"
    assert d.signals_fired == []                      # NO discovery signal transfers
    assert d.abstention == HOST_EMBEDDED_ABSTENTION
    for cite in ("GENERALIZE5", "HOSTCTX1/2", "metabolic essentiality falsified", "functional-dependency"):
        assert cite in d.abstention
    gated = {g.signal for g in d.signals_gated_out}
    assert Signal.FBA_ESSENTIALITY.value in gated
    assert Signal.FUNCTIONAL_DEPENDENCY.value in gated


# ---- human/cancer: functional-dependency not built -> ABSTAIN -------------------------------------
def test_human_cancer_abstains():
    d = decide(BiologyClass.HUMAN_CANCER, organism="aml")
    assert d.output_type == "abstention"
    assert d.signals_fired == []
    assert d.abstention == HOST_EMBEDDED_ABSTENTION


# ---- functional-dependency is never fired anywhere (module not built) -----------------------------
def test_functional_dependency_never_fires():
    for cls in BiologyClass:
        d = decide(cls)
        assert Signal.FUNCTIONAL_DEPENDENCY.value not in d.signals_fired


# ---- sequence-repurposing is never a discovery signal (validation-grade only) ---------------------
def test_sequence_repurposing_never_discovery():
    for cls in BiologyClass:
        d = decide(cls)
        assert Signal.SEQUENCE_REPURPOSING.value not in d.signals_fired
    assert TRANSFER_GATE[Signal.SEQUENCE_REPURPOSING].discovery_grade is False


# ---- the gate table itself encodes the falsified host-dependent FBA boundary ----------------------
def test_gate_table_fba_domain():
    dom = TRANSFER_GATE[Signal.FBA_ESSENTIALITY].domain
    assert BiologyClass.BACTERIUM in dom
    assert BiologyClass.FREE_EUKARYOTE in dom
    assert BiologyClass.HOST_DEPENDENT_PARASITE not in dom   # GENERALIZE5/HOSTCTX1/2
    assert BiologyClass.HUMAN_CANCER not in dom
    assert BiologyClass.VIRUS not in dom                     # no metabolism


# ---- class detector: tiny proteome -> virus; declared wins; host-dependence declared --------------
def test_detector_virus_by_size():
    cls, src = detect_class(proteome_size=30)
    assert cls == BiologyClass.VIRUS and src == "autodetected"


def test_detector_large_proteome_unknown():
    cls, src = detect_class(proteome_size=5000)
    assert cls == BiologyClass.UNKNOWN


def test_detector_declared_wins_over_size():
    # a declared class overrides size (host-dependence is not sequence-derivable)
    cls, src = detect_class(proteome_size=5000, declared_class=BiologyClass.HOST_DEPENDENT_PARASITE)
    assert cls == BiologyClass.HOST_DEPENDENT_PARASITE and src == "declared"


def test_detector_host_dependent_flag():
    cls, src = detect_class(host_dependent=True)
    assert cls == BiologyClass.HOST_DEPENDENT_PARASITE and src == "declared"


def test_boundary_threshold():
    assert detect_class(proteome_size=VIRUS_MAX_PROTEOME)[0] == BiologyClass.VIRUS
    assert detect_class(proteome_size=VIRUS_MAX_PROTEOME + 1)[0] == BiologyClass.UNKNOWN


# ---- router.decide end-to-end wiring (still data-free) --------------------------------------------
def test_router_decide_wiring():
    r = CompositeRouter()
    assert r.decide("kp", declared_class=BiologyClass.BACTERIUM).output_type == "shortlist"
    assert r.decide("sars2", proteome_size=30).output_type == "structural_class_id"
    assert r.decide("pf", host_dependent=True).output_type == "abstention"


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print(f"OK — {len(fns)} data-free unit tests passed.")


if __name__ == "__main__":
    _run_all()
