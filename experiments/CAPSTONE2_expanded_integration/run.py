"""CAPSTONE2 — end-to-end integration proof of the FULLY-EXPANDED INTERCEPTA composite.

Drives the AUTONOMOUS router (ROUTERAUTO1 decide_auto + COMPOSITE4 classes/intervention stage) across one
representative input per covered class, from OBJECTIVE ProteomeFeatures, and checks the pre-registered gate
(PREREG.md, frozen before COMPOSITE4/AMR1 landed). Payload hashes ONLY verdict_skeleton() (the drift-proof
decision essentials) so it reproduces byte-identical as prose evolves. No new science; composition of
committed, reproduced-x2, validated arms. Deterministic; no RNG; data-free.
"""
import json, hashlib, os
from intercepta.composite_router import CompositeRouter
from intercepta.class_detector import ProteomeFeatures

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
os.makedirs(RES, exist_ok=True)
router = CompositeRouter()

# (id, organism, features, intervention_features, expected_class, expected_abstain, expect_capped)
# intervention stage exercised on the HUMAN cases (MODALITY1's validated mechanism-vocab domain); pathogen
# cases pass no intervention_features -> modality ABSTAINS (honest: MODALITY1 was validated on human disease).
CASES = [
    ("bacterium", "Klebsiella pneumoniae (held-out)",
     ProteomeFeatures(n_proteins=5000, has_translation_machinery=True, domain_of_life="bacteria",
                      has_curated_gem=True), None, "bacterium", False, False),
    ("archaeon", "Methanococcus maripaludis (BLIND6)",
     ProteomeFeatures(n_proteins=1800, has_translation_machinery=True, domain_of_life="archaea",
                      has_curated_gem=True), None, "archaeon", False, False),
    ("free_eukaryote", "Komagataella phaffii (fungus)",
     ProteomeFeatures(n_proteins=5300, has_translation_machinery=True, domain_of_life="eukaryota",
                      host_dependent=False, has_curated_gem=True), None, "free_eukaryote", False, None),
    ("virus", "SARS-CoV-2 (emerging)",
     ProteomeFeatures(n_proteins=29, has_translation_machinery=False, has_viral_hallmark=True,
                      has_analyzable_structure=True), None, "virus", False, None),
    ("host_dep_parasite_gem", "Toxoplasma gondii (curated GEM)",
     ProteomeFeatures(n_proteins=8300, has_translation_machinery=True, domain_of_life="eukaryota",
                      host_dependent=True, has_curated_gem=True), None,
     "host_dependent_parasite", False, True),
    ("human_cancer", "melanoma (DepMap dependency)",
     ProteomeFeatures(n_proteins=20000, has_translation_machinery=True, domain_of_life="eukaryota",
                      is_human_proteome=True, has_dependency_screen=True),
     {"mechanism": "overactivity", "localization": "intracellular", "protein_class": "kinase"},
     "human_cancer", False, None),
    ("human_monogenic", "Pompe disease / GAA (germline)",
     ProteomeFeatures(n_proteins=20000, has_translation_machinery=True, domain_of_life="eukaryota",
                      is_human_proteome=True, causal_gene_known=True),
     {"mechanism": "LoF_null", "localization": "lysosomal", "protein_class": "enzyme", "bbb_cns": False},
     "human_monogenic", False, None),
    ("human_complex", "type-2 diabetes (GWAS/L2G)",
     ProteomeFeatures(n_proteins=20000, has_translation_machinery=True, domain_of_life="eukaryota",
                      is_human_proteome=True, has_gwas_evidence=True),
     {"mechanism": "overactivity", "localization": "intracellular", "protein_class": "enzyme"},
     "human_complex_disease", False, True),
    ("failsafe_dark", "dark proteome (DARK1)",
     ProteomeFeatures(n_proteins=22, has_translation_machinery=False, has_viral_hallmark=False,
                      has_analyzable_structure=False, is_human_proteome=False), None, "unknown", True, None),
    ("failsafe_novel_parasite", "novel zero-screen parasite, no GEM (TRANSFER1)",
     ProteomeFeatures(n_proteins=6000, has_translation_machinery=True, domain_of_life="eukaryota",
                      host_dependent=True, has_curated_gem=False), None,
     "host_dependent_parasite", True, None),
]

rows = []
for cid, org, feats, interv, exp_cls, exp_abstain, exp_capped in CASES:
    dec = router.decide_auto(org, features=feats, intervention_features=interv)
    sk = dec.verdict_skeleton()
    iv = dec.intervention or {}
    rec = iv.get("recommended_modality_class")
    feasible = iv.get("feasible_set", [])
    infeasible_violation = bool(rec) and rec != "ABSTAIN" and rec not in feasible
    rows.append({
        "case": cid, "organism": org,
        "detected_class": sk["biology_class"], "expected_class": exp_cls,
        "class_ok": sk["biology_class"] == exp_cls,
        "abstain": sk["abstain"], "expected_abstain": exp_abstain,
        "abstain_ok": sk["abstain"] == exp_abstain,
        "signals_fired": sk["signals_fired"],
        "capped": sk["capped"], "expected_capped": exp_capped,
        "capped_ok": (exp_capped is None) or (sk["capped"] == exp_capped),
        "recommended_modality_class": rec, "modality_feasible_set": feasible,
        "intervention_failsafe_violation": infeasible_violation,
        "verdict_skeleton": sk,
    })

# ---- pre-registered gates -------------------------------------------------------------------------------
clear = [r for r in rows if not r["case"].startswith("failsafe")]
fs = [r for r in rows if r["case"].startswith("failsafe")]
G1 = all(r["class_ok"] and r["abstain_ok"] and (not r["abstain"]) and len(r["signals_fired"]) >= 1 for r in clear)
G2 = all(r["class_ok"] and r["abstain"] and r["signals_fired"] == [] for r in fs)
G3 = sum(r["intervention_failsafe_violation"] for r in rows) == 0
capped_cases = {"host_dep_parasite_gem", "human_complex"}
G5 = all(r["capped"] for r in rows if r["case"] in capped_cases) and all(r["capped_ok"] for r in rows)

# ---- G4 verdict-stable payload (hash ONLY the skeletons; deterministic) ---------------------------------
skeletons = sorted((r["verdict_skeleton"] for r in rows), key=lambda s: s["biology_class"] + str(s["signals_fired"]))
payload = json.dumps(skeletons, sort_keys=True, separators=(",", ":"))
sha = hashlib.sha256(payload.encode()).hexdigest()

overall = G1 and G2 and G3 and G5
metrics = {
    "experiment": "CAPSTONE2_expanded_integration",
    "n_cases": len(rows),
    "gates": {"G1_routing_correct": G1, "G2_failsafe_abstain": G2,
              "G3_intervention_failsafe_zero_infeasible": G3, "G5_honesty_capped_flags": G5},
    "overall_PASS": overall,
    "intervention_infeasible_count": sum(r["intervention_failsafe_violation"] for r in rows),
    "cases": rows,
    "payload_sha256": sha,
    "scope": ("integration proof: composition of committed reproduced-x2 validated arms; target-PRIORITIZATION "
              "+ feasibility-triage HYPOTHESES with provenance, NOT drugs/clinical/wet-lab. 'Any disease' = honest "
              "DECISION coverage (answer where a signal transfers, abstain where none), NOT a universal model. "
              "Human-COMPLEX + host-dep-parasite fire CAPPED (attenuated/GEM-contingent). Novel-target affinity "
              "(AFFINITY1 GPU-gated), wet-lab (CRISPRIDESIGN1), clinical remain OUT of scope."),
}
with open(os.path.join(RES, "CAPSTONE2_metrics.json"), "w") as fh:
    json.dump(metrics, fh, indent=2, sort_keys=True)
with open(os.path.join(RES, "payload.sha256"), "w") as fh:
    fh.write(sha + "\n")

print(f"CAPSTONE2: {len(rows)} cases | G1={G1} G2={G2} G3={G3} G5={G5} | overall_PASS={overall}")
print(f"payload_sha256={sha}")
for r in rows:
    print(f"  {r['case']:24s} -> {r['detected_class']:22s} fired={r['signals_fired']} "
          f"abstain={r['abstain']} capped={r['capped']} modality={r['recommended_modality_class']}"
          + ("" if r['class_ok'] and r['abstain_ok'] and r['capped_ok'] else "  <<CHECK"))
