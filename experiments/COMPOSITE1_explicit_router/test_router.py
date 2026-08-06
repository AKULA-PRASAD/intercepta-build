"""COMPOSITE1 — DATA-FREE unit tests for the router's transfer-gate + abstention logic.

No files, no network, no heavy deps: exercises the PURE `decide()` / `detect_class()` gating logic only.
Run: `python -m pytest test_router.py -q`  OR  `python test_router.py` (self-runs without pytest).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
from intercepta.composite_router import (  # noqa: E402
    CompositeRouter, BiologyClass, Signal, decide, detect_class,
    HOST_EMBEDDED_ABSTENTION, HOST_DEPENDENT_PARASITE_NO_GEM_ABSTENTION,
    TRANSFER_GATE, VIRUS_MAX_PROTEOME,
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


# ---- COMPOSITE3: host-dependent parasite with NO GEM -> ABSTAIN (no signal available) --------------
# v3 correction: this is now the ONLY parasite abstention case. WITH a GEM, FBA fires capped-and-flagged
# (see the next test) rather than blanket-abstaining -- the old "metabolic essentiality falsified" premise
# was falsified by HARDENP1 (Toxoplasma PASS OR 14.10).
def test_parasite_no_gem_abstains():
    d = decide(BiologyClass.HOST_DEPENDENT_PARASITE, organism="pfalciparum", has_curated_gem=False)
    assert d.output_type == "abstention"
    assert d.signals_fired == []                      # NO discovery signal transfers (no GEM -> no capped FBA)
    assert d.uncertain is False
    assert d.abstention == HOST_EMBEDDED_ABSTENTION == HOST_DEPENDENT_PARASITE_NO_GEM_ABSTENTION
    # v3 reason: no-GEM / GEM-topology-contingent, NOT "metabolic essentiality falsified"
    assert "NO curated GEM" in d.abstention
    assert "metabolic essentiality falsified" not in d.abstention   # the corrected overgeneralization is gone
    for cite in ("HARDENP1", "GENERALIZE5", "capped-and-flagged", "functional-dependency"):
        assert cite in d.abstention
    gated = {g.signal for g in d.signals_gated_out}
    assert Signal.FBA_ESSENTIALITY.value in gated             # gated ONLY because no GEM (would fire if present)
    assert Signal.FUNCTIONAL_DEPENDENCY.value in gated        # TRANSFER1: still does not transfer to a parasite


# ---- COMPOSITE3: host-dependent parasite WITH a curated GEM -> FBA FIRES, capped + uncertainty-flagged ---
def test_parasite_with_gem_fires_capped_flagged():
    d = decide(BiologyClass.HOST_DEPENDENT_PARASITE, organism="toxoplasma", has_curated_gem=True)
    assert d.output_type == "shortlist"                       # NOT an abstention
    assert d.abstention is None
    assert Signal.FBA_ESSENTIALITY.value in d.signals_fired   # FBA fires (the correction)
    assert d.uncertain is True                                # ... but flagged
    assert d.confidence_cap == 0.5                            # ... and capped (< bacterial full-grade)
    flags = {f["signal"]: f for f in d.uncertainty_flags}
    assert Signal.FBA_ESSENTIALITY.value in flags
    note = flags[Signal.FBA_ESSENTIALITY.value]["note"]
    for cite in ("GEM-topology-dependent", "n=2", "Toxoplasma", "Plasmodium", "lower-confidence"):
        assert cite in note
    # FUNCTIONAL_DEPENDENCY still does NOT fire for the parasite even with a GEM (unchanged; TRANSFER1)
    assert Signal.FUNCTIONAL_DEPENDENCY.value not in d.signals_fired
    gated = {g.signal for g in d.signals_gated_out}
    assert Signal.FUNCTIONAL_DEPENDENCY.value in gated


# ---- human/cancer: COMPOSITE2 — functional-dependency NOW FIRES -> shortlist (the NEW capability) --
def test_human_cancer_fires_functional_dependency():
    d = decide(BiologyClass.HUMAN_CANCER, organism="melanoma")
    assert d.output_type == "shortlist"                       # was "abstention" in COMPOSITE1
    assert Signal.FUNCTIONAL_DEPENDENCY.value in d.signals_fired
    assert d.abstention is None
    # FBA must STILL be gated out for human/cancer (host-embedded metabolism; not un-gated by COMPOSITE2)
    gated = {g.signal for g in d.signals_gated_out}
    assert Signal.FBA_ESSENTIALITY.value in gated


# ---- COMPOSITE2 — functional-dependency fires ONLY for HUMAN_CANCER (data-dependent transfer) ------
def test_functional_dependency_fires_only_for_human_cancer():
    for cls in BiologyClass:
        d = decide(cls)
        if cls == BiologyClass.HUMAN_CANCER:
            assert Signal.FUNCTIONAL_DEPENDENCY.value in d.signals_fired
        else:
            assert Signal.FUNCTIONAL_DEPENDENCY.value not in d.signals_fired


# ---- COMPOSITE2 — the DECISIVE integrity test: parasite does NOT fire functional-dependency --------
def test_parasite_functional_dependency_gated_not_transferred():
    d = decide(BiologyClass.HOST_DEPENDENT_PARASITE, organism="pfalciparum")
    assert d.output_type == "abstention"
    assert Signal.FUNCTIONAL_DEPENDENCY.value not in d.signals_fired   # does NOT transfer to a parasite
    gated = {g.signal: g.reason for g in d.signals_gated_out}
    assert Signal.FUNCTIONAL_DEPENDENCY.value in gated
    # the gate reason must cite the DATA-DEPENDENT non-transfer (no parasite screen / label-free not moved)
    fd_reason = gated[Signal.FUNCTIONAL_DEPENDENCY.value]
    assert "HUMAN_CANCER" in fd_reason
    assert "not organism-transfer" in fd_reason.lower() or "organism-transfer" in fd_reason.lower()
    # and the class-level abstention reason cites the scope bound explicitly
    for cite in ("no dependency data", "label-free", "organism-transferred"):
        assert cite in d.abstention


# ---- sequence-repurposing is never a discovery signal (validation-grade only) ---------------------
def test_sequence_repurposing_never_discovery():
    for cls in BiologyClass:
        d = decide(cls)
        assert Signal.SEQUENCE_REPURPOSING.value not in d.signals_fired
    assert TRANSFER_GATE[Signal.SEQUENCE_REPURPOSING].discovery_grade is False


# ---- the gate table itself encodes the falsified host-dependent FBA boundary ----------------------
def test_gate_table_fba_domain():
    spec = TRANSFER_GATE[Signal.FBA_ESSENTIALITY]
    dom = spec.domain
    assert BiologyClass.BACTERIUM in dom
    assert BiologyClass.FREE_EUKARYOTE in dom
    assert BiologyClass.HOST_DEPENDENT_PARASITE not in dom   # NOT full-grade ...
    assert BiologyClass.HUMAN_CANCER not in dom
    assert BiologyClass.VIRUS not in dom                     # no metabolism
    # COMPOSITE3: host-dependent parasite is in the CAPPED/UNCERTAIN (GEM-contingent) domain, not full domain
    assert BiologyClass.HOST_DEPENDENT_PARASITE in spec.uncertain_domain
    assert spec.uncertain_requires == "curated_gem"
    assert spec.confidence_cap is not None and spec.confidence_cap < 1.0
    for cite in ("GEM-topology-dependent", "n=2", "Toxoplasma", "Plasmodium"):
        assert cite in spec.uncertainty_note


# ---- COMPOSITE2 — the gate table encodes functional-dependency's HUMAN_CANCER-ONLY validated domain ---
def test_gate_table_functional_dependency_domain():
    spec = TRANSFER_GATE[Signal.FUNCTIONAL_DEPENDENCY]
    assert spec.built is True                                          # NOW built (DEPEND1)
    assert spec.discovery_grade is True
    dom = spec.domain
    assert BiologyClass.HUMAN_CANCER in dom                            # VALIDATED (DEPEND1 on DepMap)
    assert BiologyClass.HOST_DEPENDENT_PARASITE not in dom             # NOT organism-transferred -> excluded
    assert BiologyClass.BACTERIUM not in dom
    assert BiologyClass.VIRUS not in dom
    assert "DEPEND1" in spec.evidence


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
