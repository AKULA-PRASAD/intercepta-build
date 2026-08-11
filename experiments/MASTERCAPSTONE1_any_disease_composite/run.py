#!/usr/bin/env python
"""MASTERCAPSTONE1 — the MASTER composite: ONE router, the WHOLE reachable disease universe (pathogen + human),
end-to-end. Unifies the pathogen-side CAPSTONE2 (bacterium/archaeon/eukaryote/virus/host-dependent-parasite ->
FBA/conservation/structure) and the human-side HUMANCAPSTONE1 (cancer/monogenic/complex-class-aware ->
dependency/causal-gene/genetic) into a single demonstration of the North Star 'any disease' delivered as HONEST
DECISION-COVERAGE with cited abstention. No new science -- composition of committed, reproduced-x2, validated
arms. Pure router logic (data-free); deterministic; reproduces byte-identical."""
import os, sys, json, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
from intercepta.composite_router import decide, BiologyClass as BC

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)

# Frozen master panel: representative input across EVERY reachable class + both abstention types, both halves.
PANEL = [
    # ---- PATHOGEN / non-human half (CAPSTONE2 arms) ----
    ("bacterium (E. coli)",              "pathogen", dict(biology_class=BC.BACTERIUM, organism="E. coli")),
    ("archaeon (M. maripaludis)",        "pathogen", dict(biology_class=BC.ARCHAEON, organism="M. maripaludis")),
    ("free eukaryote (S. cerevisiae)",   "pathogen", dict(biology_class=BC.FREE_EUKARYOTE, organism="S. cerevisiae")),
    ("virus (SARS-CoV-2)",               "pathogen", dict(biology_class=BC.VIRUS, organism="SARS-CoV-2")),
    ("parasite +GEM (Toxoplasma)",       "pathogen", dict(biology_class=BC.HOST_DEPENDENT_PARASITE, has_curated_gem=True)),
    ("parasite -GEM (Plasmodium)",       "pathogen", dict(biology_class=BC.HOST_DEPENDENT_PARASITE)),  # ABSTAIN
    # ---- HUMAN half (HUMANCAPSTONE1 arms) ----
    ("cancer (melanoma)",                "human", dict(biology_class=BC.HUMAN_CANCER)),
    ("monogenic +gene (cystic fibrosis)","human", dict(biology_class=BC.HUMAN_MONOGENIC, causal_gene_known=True)),
    ("monogenic -gene (Duchenne)",       "human", dict(biology_class=BC.HUMAN_MONOGENIC)),  # ABSTAIN
    ("complex/cardiovascular (CAD)",     "human", dict(biology_class=BC.HUMAN_COMPLEX_DISEASE, has_gwas_evidence=True, disease_class="cardiovascular")),
    ("complex/immune (RA)",              "human", dict(biology_class=BC.HUMAN_COMPLEX_DISEASE, has_gwas_evidence=True, disease_class="immune_inflammatory")),
    ("complex/neuro (Parkinson)",        "human", dict(biology_class=BC.HUMAN_COMPLEX_DISEASE, has_gwas_evidence=True, disease_class="neuro_psychiatric")),
    ("complex/respiratory (IPF)",        "human", dict(biology_class=BC.HUMAN_COMPLEX_DISEASE, has_gwas_evidence=True, disease_class="respiratory_fibrotic")),
    ("complex/metabolic (T2D)",          "human", dict(biology_class=BC.HUMAN_COMPLEX_DISEASE, has_gwas_evidence=True, disease_class="metabolic")),
    ("complex/musculoskeletal_renal (OA)","human", dict(biology_class=BC.HUMAN_COMPLEX_DISEASE, has_gwas_evidence=True, disease_class="musculoskeletal_renal")),  # class ABSTAIN
    # ---- the north-star 'never-seen' case, either half ----
    ("unknown / dark proteome",          "either", dict(biology_class=BC.UNKNOWN)),  # ABSTAIN
]

def row_of(label, half, dec):
    ga = [f for f in dec.uncertainty_flags if f["signal"] == "genetic_association"]
    grade = ("FULL" if any(f.get("grade") == "FULL_by_disease_class" for f in ga)
             else "CAPPED" if any(f.get("confidence_cap") == 0.5 for f in ga) else None)
    interv = dec.intervention or {}
    return {"input": label, "half": half, "output_type": dec.output_type,
            "fired": list(dec.signals_fired), "genetic_grade": grade,
            # COMPOSITE6: the class-appropriate intervention-modality space (target-ID -> intervention loop)
            "intervention_modality_applicability": interv.get("class_modality_applicability", []),
            "abstains": bool(dec.abstention), "abstention_reason": dec.abstention or None}

def main():
    rows = [row_of(l, h, decide(**kw)) for l, h, kw in PANEL]
    n_abs = sum(r["abstains"] for r in rows)
    out = {
        "about": "MASTER composite: one COMPOSITE router across the WHOLE reachable disease universe (pathogen + "
                 "human). North-star 'any disease' as honest DECISION-COVERAGE -- a signal-backed result where a "
                 "committed transfer condition holds, a CITED abstention where none does. NOT a universal model.",
        "n_inputs": len(rows), "n_signal_backed": len(rows) - n_abs, "n_abstain": n_abs,
        "n_classes_pathogen": len({r["input"] for r in rows if r["half"] == "pathogen"}),
        "n_classes_human": len({r["input"] for r in rows if r["half"] == "human"}),
        "arms_exercised": sorted({s for r in rows for s in r["fired"]}),
        "coverage": rows,
        "scope": "Composition of committed, reproduced-x2, validated arms (FBA/conservation/structure for "
                 "pathogens; DEPEND1 dependency / MENDEL1 mode / GENETICS1+GENETICCLASS1 class-graded genetic for "
                 "humans). Deliverables are target-relevance / mode / class-ID hypotheses -- NOT drugs, NOT "
                 "clinical. Abstention is first-class (dark proteome, no-GEM parasite, class-level genetic "
                 "ABSTAIN, descriptor-absent). Pure router logic, no per-run data.",
    }
    payload = json.dumps(out, indent=2, sort_keys=True)
    open(os.path.join(RES, "MASTERCAPSTONE1_metrics.json"), "w").write(payload + "\n")
    open(os.path.join(RES, "payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    for r in rows:
        tag = (f"genetic:{r['genetic_grade']}" if r["genetic_grade"]
               else (r["fired"][0] if r["fired"] else "ABSTAIN"))
        mod = ",".join(m.replace("SMALL_MOLECULE_", "SM_").replace("MONOCLONAL_ANTIBODY", "mAb")
                       for m in r["intervention_modality_applicability"]) or "-"
        print(f"  [{r['half']:8s}] {r['input']:36s} -> {r['output_type']:18s} [{tag}]  modality:{{{mod}}}")
    print(f"\nany-disease decision-coverage: signal-backed {out['n_signal_backed']}/{len(rows)} | "
          f"abstain {n_abs}/{len(rows)} | arms: {out['arms_exercised']}")
    print("sha256:", hashlib.sha256(payload.encode()).hexdigest())

if __name__ == "__main__":
    main()
