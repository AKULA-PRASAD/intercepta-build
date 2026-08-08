"""ROUTERAUTO1 — DATA-FREE unit tests for the AUTONOMOUS biology-class detector + its wiring into the router.

Like the existing router tests (experiments/COMPOSITE1_explicit_router/test_router.py) these exercise ONLY the
pure feature->class rules and the decide_auto() front-end: no files, no network, no heavy deps. They assert (a)
each supported class is detected from objective features and routed to the empirically-correct signal, and (b)
the FAIL-SAFE cases (dark protein set; novel zero-screen parasite) ALWAYS abstain and NEVER mis-fire.
"""
from intercepta.class_detector import ProteomeFeatures, detect_biology_class, DetectionResult
from intercepta.composite_router import CompositeRouter, BiologyClass, Signal


# ============================ pure detector: one supported class per rule ============================
def test_detect_bacterium():
    r = detect_biology_class(ProteomeFeatures(n_proteins=4000, has_translation_machinery=True,
                                              domain_of_life="bacteria"))
    assert r.biology_class == BiologyClass.BACTERIUM.value and r.source == "autodetected"


def test_detect_archaeon():
    r = detect_biology_class(ProteomeFeatures(n_proteins=1800, has_translation_machinery=True,
                                              domain_of_life="archaea"))
    assert r.biology_class == BiologyClass.ARCHAEON.value


def test_detect_free_eukaryote_requires_not_host_dependent():
    r = detect_biology_class(ProteomeFeatures(n_proteins=6000, has_translation_machinery=True,
                                              domain_of_life="eukaryota", host_dependent=False))
    assert r.biology_class == BiologyClass.FREE_EUKARYOTE.value


def test_detect_virus_needs_hallmark_not_just_tiny():
    r = detect_biology_class(ProteomeFeatures(n_proteins=30, has_translation_machinery=False,
                                              has_viral_hallmark=True))
    assert r.biology_class == BiologyClass.VIRUS.value


def test_detect_human_cancer_needs_screen():
    r = detect_biology_class(ProteomeFeatures(n_proteins=20000, is_human_proteome=True,
                                              has_dependency_screen=True))
    assert r.biology_class == BiologyClass.HUMAN_CANCER.value


def test_detect_host_dependent_parasite():
    r = detect_biology_class(ProteomeFeatures(n_proteins=5000, has_translation_machinery=True,
                                              domain_of_life="eukaryota", host_dependent=True))
    assert r.biology_class == BiologyClass.HOST_DEPENDENT_PARASITE.value


# ============================ honest boundaries: ABSTAIN rather than guess ============================
def test_tiny_acellular_without_hallmark_is_NOT_virus():
    # the minimal detector's bug fix: tiny + acellular but no viral hallmark must NOT be called a virus
    r = detect_biology_class(ProteomeFeatures(n_proteins=22, has_translation_machinery=False,
                                              has_viral_hallmark=False, has_analyzable_structure=False))
    assert r.biology_class == BiologyClass.UNKNOWN.value
    assert "R4" in r.rule


def test_human_without_screen_abstains_pending_descriptor():
    r = detect_biology_class(ProteomeFeatures(n_proteins=20000, is_human_proteome=True,
                                              has_dependency_screen=False))
    assert r.biology_class == BiologyClass.UNKNOWN.value
    assert r.requires_descriptor == "has_dependency_screen"


def test_eukaryote_undeclared_host_dependence_abstains_pending_descriptor():
    r = detect_biology_class(ProteomeFeatures(n_proteins=6000, has_translation_machinery=True,
                                              domain_of_life="eukaryota", host_dependent=None))
    assert r.biology_class == BiologyClass.UNKNOWN.value
    assert r.requires_descriptor == "host_dependent"


def test_cellular_unresolved_domain_abstains():
    r = detect_biology_class(ProteomeFeatures(n_proteins=3000, has_translation_machinery=True,
                                              domain_of_life=None))
    assert r.biology_class == BiologyClass.UNKNOWN.value
    assert r.requires_descriptor == "domain_of_life"


def test_empty_features_abstain():
    r = detect_biology_class(ProteomeFeatures())
    assert r.biology_class == BiologyClass.UNKNOWN.value


def test_declared_class_wins():
    r = detect_biology_class(ProteomeFeatures(n_proteins=30, has_translation_machinery=False,
                                              has_viral_hallmark=True),
                             declared_class=BiologyClass.BACTERIUM)
    assert r.biology_class == BiologyClass.BACTERIUM.value and r.source == "declared"


# ============================ decide_auto: end-to-end routing (still data-free) ============================
def test_auto_bacterium_fires_fba_shortlist():
    d = CompositeRouter().decide_auto("ecoli", ProteomeFeatures(n_proteins=4000,
                                      has_translation_machinery=True, domain_of_life="bacteria"))
    assert d.output_type == "shortlist"
    assert Signal.FBA_ESSENTIALITY.value in d.signals_fired
    assert d.detection["source"] == "autodetected"


def test_auto_archaeon_fires_fba_shortlist():
    d = CompositeRouter().decide_auto("mmaripaludis", ProteomeFeatures(n_proteins=1800,
                                      has_translation_machinery=True, domain_of_life="archaea"))
    assert d.output_type == "shortlist"
    assert Signal.FBA_ESSENTIALITY.value in d.signals_fired
    assert Signal.CONSERVATION_BREADTH.value in d.signals_fired
    assert d.biology_class == BiologyClass.ARCHAEON.value


def test_auto_virus_structure_only():
    d = CompositeRouter().decide_auto("sars2", ProteomeFeatures(n_proteins=30,
                                      has_translation_machinery=False, has_viral_hallmark=True))
    assert d.output_type == "structural_class_id"
    assert d.signals_fired == [Signal.STRUCTURAL_HOMOLOGY.value]
    assert Signal.FBA_ESSENTIALITY.value not in d.signals_fired


def test_auto_human_cancer_fires_functional_dependency():
    d = CompositeRouter().decide_auto("melanoma", ProteomeFeatures(n_proteins=20000,
                                      is_human_proteome=True, has_dependency_screen=True))
    assert d.output_type == "shortlist"
    assert Signal.FUNCTIONAL_DEPENDENCY.value in d.signals_fired


def test_auto_parasite_with_gem_fires_capped_flagged():
    d = CompositeRouter().decide_auto("toxoplasma", ProteomeFeatures(n_proteins=8000,
                                      has_translation_machinery=True, domain_of_life="eukaryota",
                                      host_dependent=True, has_curated_gem=True))
    assert d.output_type == "shortlist"
    assert Signal.FBA_ESSENTIALITY.value in d.signals_fired
    assert d.uncertain is True and d.confidence_cap == 0.5


# ============================ FAIL-SAFE (hard): dark + novel zero-screen parasite MUST abstain ============
def test_failsafe_dark_proteins_abstain_never_fire():
    d = CompositeRouter().decide_auto("dark22", ProteomeFeatures(n_proteins=22,
                                      has_translation_machinery=False, has_viral_hallmark=False,
                                      has_analyzable_structure=False, is_human_proteome=False))
    assert d.output_type == "abstention"
    assert d.signals_fired == []
    assert d.biology_class == BiologyClass.UNKNOWN.value
    # must NOT have been mis-detected as a virus (the minimal-detector failure mode)
    assert d.detection["biology_class"] != BiologyClass.VIRUS.value


def test_failsafe_novel_zero_screen_parasite_abstains():
    # declared host-dependent, NO curated GEM -> the unchanged COMPOSITE3 no-signal abstention
    d = CompositeRouter().decide_auto("novel_apicomplexan", ProteomeFeatures(n_proteins=5000,
                                      has_translation_machinery=True, domain_of_life="eukaryota",
                                      host_dependent=True, has_curated_gem=False))
    assert d.output_type == "abstention"
    assert d.signals_fired == []
    assert Signal.FBA_ESSENTIALITY.value not in d.signals_fired


def test_failsafe_novel_parasite_undeclared_also_abstains():
    # even if host-dependence is undeclared, a bare eukaryote abstains (require descriptor) -> never mis-fires
    d = CompositeRouter().decide_auto("novel_euk", ProteomeFeatures(n_proteins=6000,
                                      has_translation_machinery=True, domain_of_life="eukaryota",
                                      host_dependent=None))
    assert d.output_type == "abstention"
    assert d.signals_fired == []


def test_detection_result_serializable():
    r = detect_biology_class(ProteomeFeatures(n_proteins=4000, has_translation_machinery=True,
                                              domain_of_life="bacteria"))
    dd = r.to_dict()
    assert set(dd) >= {"biology_class", "source", "rule", "reasons", "requires_descriptor"}
