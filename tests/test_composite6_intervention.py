"""COMPOSITE6 — the intervention stage is now CLASS-AWARE: it reports which modality CLASSES are biologically
applicable to the routed biology class, and flags a class-inapplicable recommendation (e.g. siRNA for a
bacterium). Additive: never changes recommended_modality_class / feasible_set; backward-compatible."""
from intercepta.composite_router import decide, recommend_intervention, BiologyClass as BC


def test_pathogen_only_small_molecule_applicable():
    d = decide(BC.BACTERIUM, organism="E. coli")
    assert d.intervention["class_modality_applicability"] == ["SMALL_MOLECULE_INHIBITOR"]


def test_monogenic_spans_host_modalities():
    d = decide(BC.HUMAN_MONOGENIC, causal_gene_known=True)
    appl = set(d.intervention["class_modality_applicability"])
    assert {"GENE_THERAPY", "ASO_siRNA", "ENZYME_PROTEIN_REPLACEMENT"} <= appl


def test_class_consistent_flag_catches_inapplicable_modality():
    # a bacterial target whose features would drive siRNA -> siRNA is NOT applicable to a pathogen -> flagged
    d = decide(BC.BACTERIUM, organism="x",
               intervention_features={"mechanism": "GoF", "localization": "intracellular",
                                      "protein_class": "transcription_factor"})
    assert d.intervention["recommended_modality_class"] == "ASO_siRNA"
    assert d.intervention["class_consistent"] is False


def test_consistent_when_recommendation_in_class():
    d = decide(BC.HUMAN_MONOGENIC, causal_gene_known=True,
               intervention_features={"mechanism": "LoF", "localization": "intracellular"})
    assert d.intervention["recommended_modality_class"] == "GENE_THERAPY"
    assert d.intervention["class_consistent"] is True


def test_backward_compatible_without_biology_class():
    # direct call without a class -> the class fields are absent (pre-COMPOSITE6 behaviour)
    r = recommend_intervention(mechanism="GoF", localization="cell_surface")
    assert "class_modality_applicability" not in r and "class_consistent" not in r
