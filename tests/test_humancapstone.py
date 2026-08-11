"""HUMANCAPSTONE1 — the unified human-disease composite routes each representative disease correctly
(deterministic, pure router logic): right arm/grade where a transfer condition holds; cited abstention where not."""
from intercepta.composite_router import decide, BiologyClass as BC


def _ga_grade(dec):
    ga = [f for f in dec.uncertainty_flags if f["signal"] == "genetic_association"]
    if any(f.get("grade") == "FULL_by_disease_class" for f in ga): return "FULL"
    if any(f.get("confidence_cap") == 0.5 for f in ga): return "CAPPED"
    return None


def test_cancer_fires_dependency():
    d = decide(biology_class=BC.HUMAN_CANCER)
    assert d.output_type == "shortlist" and "functional_dependency" in d.signals_fired


def test_monogenic_with_gene_fires_mode():
    d = decide(biology_class=BC.HUMAN_MONOGENIC, causal_gene_known=True)
    assert d.output_type == "mode" and "causal_gene" in d.signals_fired


def test_monogenic_without_gene_abstains():
    assert decide(biology_class=BC.HUMAN_MONOGENIC).abstention


def test_complex_full_classes_fire_full():
    for cls in ("cardiovascular", "immune_inflammatory", "neuro_psychiatric", "respiratory_fibrotic"):
        d = decide(biology_class=BC.HUMAN_COMPLEX_DISEASE, has_gwas_evidence=True, disease_class=cls)
        assert d.output_type == "shortlist" and _ga_grade(d) == "FULL", cls


def test_complex_metabolic_fires_capped():
    d = decide(biology_class=BC.HUMAN_COMPLEX_DISEASE, has_gwas_evidence=True, disease_class="metabolic")
    assert d.output_type == "shortlist" and _ga_grade(d) == "CAPPED"


def test_complex_musculoskeletal_renal_abstains():
    d = decide(biology_class=BC.HUMAN_COMPLEX_DISEASE, has_gwas_evidence=True, disease_class="musculoskeletal_renal")
    assert d.abstention


def test_complex_no_evidence_abstains():
    assert decide(biology_class=BC.HUMAN_COMPLEX_DISEASE).abstention
