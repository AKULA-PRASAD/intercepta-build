#!/usr/bin/env python
"""HUMANCAPSTONE1 — the unified HUMAN-DISEASE composite, end-to-end. The human analog of the pathogen-side
CAPSTONE1/2: drive the (now disease-class-aware) COMPOSITE router over a frozen panel of representative human
diseases spanning every reachable human-disease class + validated arm, and show honest decision-coverage —
a signal-backed result where an arm's transfer condition holds, an explicit CITED abstention where none does.
Ties together GENETICCLASS1 (class envelope) + COMPOSITE5 (class-aware genetic arm) + MENDEL1 (monogenic) +
DEPEND1 (cancer dependency). Pure router logic (data-free); deterministic; reproduces byte-identical."""
import os, sys, json, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
from intercepta.composite_router import decide, BiologyClass as BC

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)

# Frozen panel: (label, kwargs to decide) — real diseases spanning all human classes, arms, and both
# abstention types (class-level ABSTAIN; and no-descriptor ABSTAIN). Expected routing is asserted in tests.
PANEL = [
    ("melanoma (cancer)",                    dict(biology_class=BC.HUMAN_CANCER)),
    ("cystic fibrosis (monogenic, CFTR)",    dict(biology_class=BC.HUMAN_MONOGENIC, causal_gene_known=True)),
    ("Duchenne (monogenic, gene unknown)",   dict(biology_class=BC.HUMAN_MONOGENIC)),  # -> abstain (no gene)
    ("coronary artery disease (complex)",    dict(biology_class=BC.HUMAN_COMPLEX_DISEASE, has_gwas_evidence=True, disease_class="cardiovascular")),
    ("rheumatoid arthritis (complex)",       dict(biology_class=BC.HUMAN_COMPLEX_DISEASE, has_gwas_evidence=True, disease_class="immune_inflammatory")),
    ("Parkinson disease (complex)",          dict(biology_class=BC.HUMAN_COMPLEX_DISEASE, has_gwas_evidence=True, disease_class="neuro_psychiatric")),
    ("idiopathic pulmonary fibrosis",        dict(biology_class=BC.HUMAN_COMPLEX_DISEASE, has_gwas_evidence=True, disease_class="respiratory_fibrotic")),
    ("type 2 diabetes (complex)",            dict(biology_class=BC.HUMAN_COMPLEX_DISEASE, has_gwas_evidence=True, disease_class="metabolic")),
    ("osteoarthritis (complex)",             dict(biology_class=BC.HUMAN_COMPLEX_DISEASE, has_gwas_evidence=True, disease_class="musculoskeletal_renal")),  # -> class ABSTAIN
    ("undiagnosed/idiopathic (no data)",     dict(biology_class=BC.HUMAN_COMPLEX_DISEASE)),  # -> abstain (no descriptor)
]

def summarize(dec):
    ga = [f for f in dec.uncertainty_flags if f["signal"] == "genetic_association"]
    grade = "FULL" if any(f.get("grade") == "FULL_by_disease_class" for f in ga) else \
            ("CAPPED" if any(f.get("confidence_cap") == 0.5 for f in ga) else None)
    reasons = [g.reason if hasattr(g, "reason") else "" for g in dec.signals_gated_out]
    return {"output_type": dec.output_type, "fired": list(dec.signals_fired),
            "genetic_grade": grade, "abstains": bool(dec.abstention),
            "abstention_reason": dec.abstention if dec.abstention else None,
            "n_gated": len(dec.signals_gated_out)}

def main():
    rows = []
    for label, kw in PANEL:
        dec = decide(**kw)
        rows.append({"disease": label, **summarize(dec)})
    n_shortlist = sum(1 for r in rows if r["output_type"] == "shortlist")
    n_mode = sum(1 for r in rows if r["output_type"] == "mode")
    n_abstain = sum(1 for r in rows if r["abstains"])
    n_full = sum(1 for r in rows if r["genetic_grade"] == "FULL")
    n_capped = sum(1 for r in rows if r["genetic_grade"] == "CAPPED")
    out = {
        "about": "Unified human-disease composite: honest decision-coverage across human-disease classes via the "
                 "disease-class-aware COMPOSITE router (GENETICCLASS1+COMPOSITE5 genetic arm, MENDEL1 monogenic, "
                 "DEPEND1 cancer-dependency). Signal-backed where a validated transfer condition holds; cited "
                 "abstention where none does. 'Any human disease' = decision-coverage, NOT a universal model.",
        "n_inputs": len(rows), "n_signal_backed": n_shortlist + n_mode, "n_abstain": n_abstain,
        "genetic_FULL": n_full, "genetic_CAPPED": n_capped,
        "arms_exercised": sorted({s for r in rows for s in r["fired"]}),
        "coverage": rows,
        "scope": "Each fired arm is traceable to a committed, reproduced validation (DEPEND1 / MENDEL1 / "
                 "GENETICS1+GENETICCLASS1). Retrospective, target-RELEVANCE/mode (not a drug, not clinical). "
                 "The two abstention TYPES (class-level ABSTAIN for musculoskeletal_renal; descriptor-absent "
                 "ABSTAIN) are both first-class. Pure router logic — no per-run data.",
    }
    payload = json.dumps(out, indent=2, sort_keys=True)
    open(os.path.join(RES, "HUMANCAPSTONE1_metrics.json"), "w").write(payload + "\n")
    open(os.path.join(RES, "payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    for r in rows:
        tag = (f"genetic:{r['genetic_grade']}" if r["genetic_grade"] else
               (r["fired"][0] if r["fired"] else "ABSTAIN"))
        print(f"  {r['disease']:38s} -> {r['output_type']:11s} [{tag}]")
    print(f"\nsignal-backed {out['n_signal_backed']}/{len(rows)} | abstain {n_abstain}/{len(rows)} "
          f"(genetic FULL {n_full}, CAPPED {n_capped}) | arms: {out['arms_exercised']}")
    print("sha256:", hashlib.sha256(payload.encode()).hexdigest())

if __name__ == "__main__":
    main()
