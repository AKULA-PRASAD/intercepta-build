"""COMPOSITE4 — DATA-FREE unit tests for the additive expanded-arm integration.

Covers (a) verdict_skeleton drift-fix + regression (committed skeletons UNCHANGED, stable under prose
mutation), (b) the two NEW human classes (complex->genetic_association CAPPED; monogenic->mode), (c) the
fail-safe INTERVENTION stage (0 infeasible recs; abstains when features absent), (d) fail-safe abstentions
preserved (dark + novel zero-screen parasite). No files, no network, no heavy deps — pure decision logic.
"""
from intercepta.composite_router import (
    CompositeRouter, BiologyClass, Signal, decide, recommend_intervention,
    TRANSFER_GATE, RoutingDecision, GatedSignal,
)
from intercepta.class_detector import ProteomeFeatures, detect_biology_class


# ====================================================================================================
# (d/regression base) frozen committed verdicts — the CAPSTONE1 (sha 19a72135) per-case decisions.
# ====================================================================================================
COMMITTED_CASES = [
    dict(organism="Klebsiella pneumoniae", declared_class=BiologyClass.BACTERIUM, has_curated_gem=True),
    dict(organism="Candida albicans", declared_class=BiologyClass.FREE_EUKARYOTE, has_curated_gem=True),
    dict(organism="SARS-CoV-2", proteome_size=30, has_curated_gem=False),
    dict(organism="human melanoma", declared_class=BiologyClass.HUMAN_CANCER, has_curated_gem=False),
    dict(organism="Toxoplasma gondii", declared_class=BiologyClass.HOST_DEPENDENT_PARASITE, has_curated_gem=True),
    dict(organism="novel apicomplexan", declared_class=BiologyClass.HOST_DEPENDENT_PARASITE, has_curated_gem=False),
]
EXPECTED_SKELETONS = [
    {"biology_class": "bacterium",
     "signals_fired": ["conservation_breadth", "fba_essentiality", "structural_homology"],
     "abstain": False, "capped": False, "recommended_modality_class": "ABSTAIN"},
    {"biology_class": "free_eukaryote", "signals_fired": ["conservation_breadth", "fba_essentiality"],
     "abstain": False, "capped": False, "recommended_modality_class": "ABSTAIN"},
    {"biology_class": "virus", "signals_fired": ["structural_homology"],
     "abstain": False, "capped": False, "recommended_modality_class": "ABSTAIN"},
    {"biology_class": "human_cancer", "signals_fired": ["functional_dependency"],
     "abstain": False, "capped": False, "recommended_modality_class": "ABSTAIN"},
    {"biology_class": "host_dependent_parasite", "signals_fired": ["fba_essentiality"],
     "abstain": False, "capped": True, "recommended_modality_class": "ABSTAIN"},
    {"biology_class": "host_dependent_parasite", "signals_fired": [],
     "abstain": True, "capped": False, "recommended_modality_class": "ABSTAIN"},
]


def test_regression_committed_skeletons_unchanged():
    """Every committed routing decision reproduces its EXACT verdict skeleton through the new router."""
    r = CompositeRouter()
    for case, expected in zip(COMMITTED_CASES, EXPECTED_SKELETONS):
        d = r.decide(**case)
        assert d.verdict_skeleton() == expected, (case, d.verdict_skeleton())


# ====================================================================================================
# (4) verdict_skeleton drift FIX — stable while volatile prose changes.
# ====================================================================================================
def test_verdict_skeleton_keys_are_only_stable_essentials():
    d = decide(BiologyClass.BACTERIUM, organism="ecoli")
    sk = d.verdict_skeleton()
    assert set(sk) == {"biology_class", "signals_fired", "abstain", "capped", "recommended_modality_class"}
    # no prose/evidence leaks in
    for v in sk.values():
        assert "evidence" not in str(v).lower() and "HARDENP1" not in str(v)


def test_skeleton_stable_under_prose_mutation():
    """Mutating reason/abstention/gated prose must NOT change the verdict skeleton (the drift fix)."""
    d = decide(BiologyClass.HOST_DEPENDENT_PARASITE, organism="pf", has_curated_gem=False)
    before = d.verdict_skeleton()
    d.abstention = "TOTALLY DIFFERENT PROSE " + (d.abstention or "")
    d.signals_gated_out = [GatedSignal("fba_essentiality", "some other rewritten reason string")]
    for f in d.uncertainty_flags:
        f["note"] = "rewritten note"
    assert d.verdict_skeleton() == before  # skeleton unchanged despite prose churn


# ====================================================================================================
# (b) NEW human classes route correctly.
# ====================================================================================================
def test_complex_disease_fires_genetic_association_capped():
    d = decide(BiologyClass.HUMAN_COMPLEX_DISEASE, organism="T2D", has_gwas_evidence=True)
    assert d.output_type != "abstention"
    assert d.signals_fired == [Signal.GENETIC_ASSOCIATION.value]
    assert d.uncertain is True and d.confidence_cap == 0.5
    note = d.uncertainty_flags[0]["note"]
    assert "popularity-adjusted effect bounded [1.67,2.26]" in note
    assert "target-relevance only" in note and "cross-sectional" in note


def test_complex_disease_without_gwas_abstains():
    d = decide(BiologyClass.HUMAN_COMPLEX_DISEASE, organism="T2D", has_gwas_evidence=False)
    assert d.output_type == "abstention"
    assert d.signals_fired == []
    assert "has_gwas_evidence" in d.abstention


def test_monogenic_fires_causal_gene_mode_not_capped():
    d = decide(BiologyClass.HUMAN_MONOGENIC, organism="cystic fibrosis", causal_gene_known=True)
    assert d.output_type == "mode"
    assert d.signals_fired == [Signal.CAUSAL_GENE.value]
    assert d.uncertain is False and d.confidence_cap is None  # NOT capped (target given, MENDEL1 PASS)


def test_monogenic_without_causal_gene_abstains():
    d = decide(BiologyClass.HUMAN_MONOGENIC, organism="x", causal_gene_known=False)
    assert d.output_type == "abstention"
    assert d.signals_fired == []
    assert "causal_gene_known" in d.abstention


def test_gate_table_new_signals_domains():
    ga = TRANSFER_GATE[Signal.GENETIC_ASSOCIATION]
    assert ga.built and ga.discovery_grade
    assert ga.domain == frozenset()  # never full-grade
    assert BiologyClass.HUMAN_COMPLEX_DISEASE in ga.uncertain_domain
    assert ga.uncertain_requires == "gwas_evidence" and ga.confidence_cap == 0.5
    assert "GENETICS1" in ga.evidence
    cg = TRANSFER_GATE[Signal.CAUSAL_GENE]
    assert cg.built and cg.discovery_grade
    assert cg.domain == frozenset({BiologyClass.HUMAN_MONOGENIC})
    assert cg.requires_descriptor == "causal_gene_known" and cg.output_mode == "mode"
    assert "MENDEL1" in cg.evidence


def test_new_signals_do_not_fire_for_wrong_classes():
    for cls in BiologyClass:
        d = decide(cls, has_gwas_evidence=True, causal_gene_known=True)
        if cls != BiologyClass.HUMAN_COMPLEX_DISEASE:
            assert Signal.GENETIC_ASSOCIATION.value not in d.signals_fired
        if cls != BiologyClass.HUMAN_MONOGENIC:
            assert Signal.CAUSAL_GENE.value not in d.signals_fired


# ---- class_detector: the three human routes + ambiguity abstention -------------------------------
def test_detect_human_complex_via_gwas():
    r = detect_biology_class(ProteomeFeatures(n_proteins=20000, is_human_proteome=True, has_gwas_evidence=True))
    assert r.biology_class == BiologyClass.HUMAN_COMPLEX_DISEASE.value


def test_detect_human_monogenic_via_causal_gene():
    r = detect_biology_class(ProteomeFeatures(n_proteins=20000, is_human_proteome=True, causal_gene_known=True))
    assert r.biology_class == BiologyClass.HUMAN_MONOGENIC.value


def test_detect_human_cancer_still_via_screen():
    r = detect_biology_class(ProteomeFeatures(n_proteins=20000, is_human_proteome=True, has_dependency_screen=True))
    assert r.biology_class == BiologyClass.HUMAN_CANCER.value


def test_detect_human_ambiguous_abstains():
    r = detect_biology_class(ProteomeFeatures(n_proteins=20000, is_human_proteome=True,
                                              has_dependency_screen=True, causal_gene_known=True))
    assert r.biology_class == BiologyClass.UNKNOWN.value
    assert "AMBIGUOUS" in r.rule


def test_detect_human_no_descriptor_backward_compat():
    # committed behavior preserved: requires_descriptor stays 'has_dependency_screen'
    r = detect_biology_class(ProteomeFeatures(n_proteins=20000, is_human_proteome=True))
    assert r.biology_class == BiologyClass.UNKNOWN.value
    assert r.requires_descriptor == "has_dependency_screen"


def test_decide_auto_routes_new_human_classes():
    rr = CompositeRouter()
    dc = rr.decide_auto("T2D", ProteomeFeatures(n_proteins=20000, is_human_proteome=True, has_gwas_evidence=True))
    assert dc.signals_fired == [Signal.GENETIC_ASSOCIATION.value] and dc.uncertain is True
    dm = rr.decide_auto("CF", ProteomeFeatures(n_proteins=20000, is_human_proteome=True, causal_gene_known=True))
    assert dm.output_type == "mode" and dm.signals_fired == [Signal.CAUSAL_GENE.value]


# ====================================================================================================
# (c) INTERVENTION stage — MODALITY1 fail-safe port.
# ====================================================================================================
# Representative MODALITY1-style feature tuples spanning mechanisms/localizations/classes.
INTERV_TEST_SET = [
    ("GoF", "intracellular", "kinase", False, False),
    ("GoF", "membrane", "kinase", False, False),
    ("overactivity", "secreted", "enzyme", False, False),
    ("dominant_negative", "intracellular", "transcription_factor", False, False),
    ("toxic_aggregation", "secreted", "globin", False, False),
    ("LoF_misfold", "lysosomal", "enzyme", False, False),
    ("LoF_null", "secreted", "enzyme", False, False),
    ("LoF_null", "lysosomal", "enzyme", True, False),      # BBB -> ERT infeasible -> must not be recommended
    ("LoF_null", "intracellular", "enzyme", False, False),
    ("LoF", "membrane", "transporter", False, False),
    ("GoF", "unknown_loc", "unclassified", False, False),  # no confident call -> ABSTAIN
]


def test_intervention_fail_safe_zero_infeasible():
    """HARD fail-safe: the recommendation is ALWAYS in feasible_set (or ABSTAIN). 0 infeasible over the set."""
    n_infeasible = 0
    for mech, loc, pc, bbb, splice in INTERV_TEST_SET:
        rec = recommend_intervention(mech, loc, pc, bbb, splice)
        assert rec["fail_safe"] is True
        r = rec["recommended_modality_class"]
        if r != "ABSTAIN" and r not in rec["feasible_set"]:
            n_infeasible += 1
    assert n_infeasible == 0


def test_intervention_bbb_ert_never_recommended():
    rec = recommend_intervention("LoF_null", "lysosomal", "enzyme", bbb_cns=True)
    assert rec["recommended_modality_class"] != "ENZYME_PROTEIN_REPLACEMENT"  # ERT cannot cross the BBB


def test_intervention_abstains_when_features_absent():
    for rec in (recommend_intervention(), recommend_intervention(mechanism="GoF"),
                recommend_intervention(localization="intracellular")):
        assert rec["recommended_modality_class"] == "ABSTAIN"
        assert rec["feasible_set"] == [] and rec["fail_safe"] is True


def test_intervention_wired_onto_decision():
    d = decide(BiologyClass.HUMAN_MONOGENIC, organism="CF", causal_gene_known=True,
               intervention_features={"mechanism": "LoF_null", "localization": "secreted",
                                      "protein_class": "enzyme"})
    assert d.intervention is not None
    assert d.intervention["recommended_modality_class"] == "ENZYME_PROTEIN_REPLACEMENT"
    assert d.verdict_skeleton()["recommended_modality_class"] == "ENZYME_PROTEIN_REPLACEMENT"


def test_intervention_default_abstain_on_decision():
    d = decide(BiologyClass.BACTERIUM, organism="ecoli")
    assert d.intervention["recommended_modality_class"] == "ABSTAIN"  # no features supplied


# ====================================================================================================
# (d) FAIL-SAFE abstentions PRESERVED — dark + novel zero-screen parasite never mis-fire.
# ====================================================================================================
def test_failsafe_dark_still_abstains():
    d = CompositeRouter().decide_auto("dark22", ProteomeFeatures(n_proteins=22, has_translation_machinery=False,
                                      has_viral_hallmark=False, has_analyzable_structure=False,
                                      is_human_proteome=False))
    assert d.output_type == "abstention" and d.signals_fired == []
    assert d.detection["biology_class"] != BiologyClass.VIRUS.value
    assert d.verdict_skeleton()["abstain"] is True


def test_failsafe_novel_parasite_still_abstains():
    d = CompositeRouter().decide_auto("novel_apicomplexan", ProteomeFeatures(n_proteins=5000,
                                      has_translation_machinery=True, domain_of_life="eukaryota",
                                      host_dependent=True, has_curated_gem=False))
    assert d.output_type == "abstention" and d.signals_fired == []
    assert Signal.FBA_ESSENTIALITY.value not in d.signals_fired
