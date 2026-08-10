#!/usr/bin/env python
"""F9 — build the composite knowledge graph (kg.json) from the program's AUTHORITATIVE records
(LEDGER.md V1–V23, COMPUTATIONAL_DEAD_ENDS.md D1–D9, src/intercepta/composite_router transfer-conditions,
MR1, INTEGRITY_SWEEP.md). Deterministic: pure data assembly, no RNG. Negatives are FIRST-CLASS nodes.

Every arm 'applies_to' edge carries an evidence path + a reproduced flag; every ABSTAIN edge cites a
dead-end; every dead-end carries a falsifiable reopen_trigger. Enforced by knowledge_graph.integrity_check()
and the F9 tests. This encodes provenance — it makes NO new scientific claim (see SUMMARY.md, honest scope).
"""
import json, os, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))

DISEASE_CLASSES = [
    "bacteria_self_metabolism", "host_dependent_parasite", "virus", "fungus",
    "cancer", "complex_human_disease", "monogenic_disease",
]

# ---- DEAD-ENDS / NEGATIVES (first-class). Each: id, name, tried, negative_outcome, category, reopen_trigger, evidence ----
DEADENDS = [
    ("D1", "Label-free non-metabolic mechanism signal", "6 signal classes vs conservation-breadth null",
     "conservation AUROC 0.9078 unbeaten (NONMET1 +0.021, PLMESS1 +0.008/study-ctrl -0.0006, REGNET1 -0.006, "
     "PLMSTRUCT1 +0.0076, MULTISIG1 +0.019, MET4 +0.128->-0.004 after study-bias control)", "dead-end-closed",
     "curated mechanism LABELS or a fundamentally new data modality appears", "COMPUTATIONAL_DEAD_ENDS.md#D1"),
    ("D2", "Novel-target/novel-chemotype affinity", "docking / QSAR / PCM / co-folding on public benchmarks",
     "docking AUROC 0.428 (HIT2); QSAR 0.90->0.67 novel-chemotype (HIT1); PCM adds nothing (B49); Boltz-2 "
     "training-leaked, novel-split n=5 ~0.52 (AFFINITY1)", "dead-end-closed",
     "the R2 OOD testbed shows a method beating the wall on a leakage-controlled novel-target split",
     "COMPUTATIONAL_DEAD_ENDS.md#D2"),
    ("D3", "Single-agent human drug-response from baseline profiles", "cross-dataset + within-cancer clinical",
     "cross-dataset ceiling rho +0.212; within-cancer clinical AUROC 0.504 (p=0.43); inferred functional layer "
     "fails external replication (B20/B21)", "dead-end-closed",
     "MEASURED functional/perturbation response data becomes available (experimental, outside compute scope)",
     "COMPUTATIONAL_DEAD_ENDS.md#D3"),
    ("D4", "More disease-class breadth / router coverage arms", "adding arms / re-benchmarking the core",
     "CPU-arm expansion ~= 0 marginal real-world value (independent audit)", "dead-end-closed",
     "a genuinely new signal type (not the same hypothesis in new clothes)", "COMPUTATIONAL_DEAD_ENDS.md#D4"),
    ("D5", "De-novo molecule generation without a validated novel-target scorer", "GuacaMol generator",
     "generator below SOTA (B52); no validated novel-target scoring function to optimize (D2); prior 'de novo' "
     "were relabeled scaffold-hops (INTEGRITY_SWEEP)", "dead-end-closed", "D2's gate opens",
     "COMPUTATIONAL_DEAD_ENDS.md#D5"),
    ("D6", "Structural repurposing for novel-pathogen coverage expansion", "structure-based target-drug matching",
     "promiscuity/fold-census artifact: 18/32 vs random null 25/32; honest novel-target coverage stays 1/32 "
     "(STRUCTREPURPOSE1)", "leakage-artifact-caught", "a null-guarded method exceeds the random-fold census",
     "COMPUTATIONAL_DEAD_ENDS.md#D6"),
    ("D7", "ipTM / interface-confidence as an affinity proxy", "Boltz/AF interface confidence",
     "ipTM saturates ~0.95 for actives AND inactives (AFFINITY_IPTM1)", "dead-end-closed",
     "a confidence signal separates actives from inactives on a leakage-free split", "COMPUTATIONAL_DEAD_ENDS.md#D7"),
    ("D8", "Re-running program-level audits", "repeated due-diligence audits",
     "verdict stable across audits; the missing input is DATA, not compute", "dead-end-closed",
     "new experimental data changes the evidence base", "COMPUTATIONAL_DEAD_ENDS.md#D8"),
    ("D9", "Durability via masked-PLM entropy at resistance sites", "DYNAMICS5 powered re-test (n=198, 1143 sites)",
     "FALSIFIED at scale: Wilcoxon p=0.99997 (opposite direction), mean dH=-0.22, position AUROC 0.446 (below "
     "chance); overturns DYNAMICS1's n=15 AUROC 0.84 small-n artifact", "falsified-own-claim",
     "a different powered observable (FEP/MD ddG or measured DMS fitness)",
     "experiments/DYNAMICS5_resistance_site_entropy/results/DYNAMICS5_metrics.json"),
    ("N1", "Mechanistic-coherence of cell-line->patient transfer (B3e)", "do AML-relevant drugs transfer best",
     "WITHDRAWN pre-registered null: MWU p=0.29, perm p=0.50; transfer strength doesn't track predictability",
     "falsified-own-claim", "a powered multi-cohort test", "DECISIONS.md#2026-07-29-D8"),
    ("MR1_H2", "cis-MR adds predictive value beyond Open Targets aggregate", "MR1 H2 grouped-CV vs OT",
     "honest-negative: small significant coef (0.022) but dAUPRC +0.0001 (CI [-0.0018,0.0010]); redundant with OT",
     "honest-negative-result", "a colocalization-aware MR or a target class OT under-covers",
     "experiments/MR1_causal_target_id/SUMMARY.md"),
    ("B25_novel_drug", "Drug-synergy generalization to NOVEL drugs", "leave-drug-out on DrugComb 124-drug set",
     "collapses: B24 leave-drug-out rho 0.25 -> 0.025 (CI [0.012,0.038]); the 0.25 was O'Neil chemical redundancy",
     "falsified-own-claim", "a synergy model generalizes out-of-chemistry on a diverse corpus",
     "LEDGER.md#V23"),
    ("B26_mech_synergy", "Mechanism-anchored (target-dependency) synergy for novel drugs", "CRISPR-dep features",
     "does NOT beat fingerprints for novel drugs (MECH 0.076 vs FP 0.162)", "honest-negative-result",
     "a mechanism encoding beats chemistry on novel drugs", "LEDGER.md#B26"),
    ("B20_ext_replication", "External replication of inferred-FLT3-dependency layer (V19/V20)", "FIMM/Malani cohort",
     "fails: pooled rho +0.05 (p=0.08), adds beta -0.02 (p=0.92), sorafenib flips sign; V19/V20 DOWNGRADED",
     "falsified-own-claim", "replication in a 2nd independent patient cohort", "LEDGER.md#V19"),
    ("STRUCTREPURPOSE1", "Structural repurposing coverage jump 1/32->18/32", "structure matching",
     "promiscuity artifact; random-protein null 25/32 > drug targets; honest 1/32", "leakage-artifact-caught",
     "see D6", "LEDGER.md#L63"),
    ("PARARESOLVE1", "Salvage-bypass topology explains Plasmodium FBA failure", "GEM salvage-FN analysis",
     "mechanism FALSIFIED: salvage-FN iPfal19 0.907 ~= Toxo 0.867; GEM swap doesn't close the gap",
     "falsified-own-claim", "a mechanistic account that predicts which parasites FBA transfers to",
     "FAILURE_AUDIT.md#F2"),
    ("AMR1", "Zero-data whole-protein resistance-liability", "4 static features, n=17",
     "NEGATIVE: composite AUROC 0.556, MWU p=0.74 (gate>=0.70); drugged-only 0.472 (below chance)",
     "honest-negative-result", "a dynamic/measured resistance observable",
     "experiments/AMR1_resistance_liability/results/AMR1_metrics.json"),
    ("B10_clinical", "Human CLINICAL drug-response (TCGA)", "baseline expression -> clinical outcome",
     "within-cancer AUROC 0.504 (p=0.43); raw 0.539 was a cancer-type confound", "leakage-artifact-caught",
     "measured functional response data", "docs/ENG#2.7"),
    ("B23_functional_tautology", "Measured CRISPR-dependency beats baseline transcriptomics generally", "498 lines",
     "NO: dep 0.459 <= RNA 0.487; own-target-excluded 0.504 vs 0.514 (p=0.06) -> functional advantage is "
     "target-tautological, not a transferable functional-state signal", "honest-negative-result",
     "a functional-state predictor that generalizes beyond a drug's own target", "LEDGER.md#V22"),
    ("AFFINITY1_leak", "Boltz-2 co-folding 'zero-shot' affinity", "CHEMBL204 thrombin benchmark",
     "'zero-shot' indefensible (affinity head trained on ChEMBL/BindingDB; thrombin in-cutoff); novel-split n=5 ~0.52",
     "leakage-artifact-caught", "a leakage-controlled novel-target evaluation (R2)",
     "experiments/AFFINITY1_cofolding_zeroshot/LEAKAGE_AUDIT.md"),
]

# ---- VALIDATED ARMS. applies_to grade in {FULL, CAPPED, ABSTAIN}; ABSTAIN edges cite a deadend ----
ARMS = [
    dict(id="FBA_target_id", capability="target_identification",
         name="FBA metabolic gene-essentiality target-ID", reproduced=True,
         evidence="experiments/VALIDATE_essentiality/ (+CROSSVAL, BLIND1-7)",
         headline_metric="OR 5-64 vs experimental essentiality (K.pneumoniae OR 63/prec 92%)",
         transfer_condition="requires a self-contained metabolic network (GEM); enrichment not a target list (recall ~0.22)",
         applies_to=[
             dict(cls="bacteria_self_metabolism", grade="FULL", metric="OR 5-64 (blind 4/7 pass)"),
             dict(cls="host_dependent_parasite", grade="CAPPED", metric="GEM-topology-contingent; Plasmodium OR 2.47 (COMPOSITE3)"),
             dict(cls="fungus", grade="CAPPED", metric="K.phaffii OR 2.4 (BLIND5, sub-gate)"),
             dict(cls="virus", grade="ABSTAIN", deadend="D1", metric="no metabolism -> route to structural arm"),
         ], bounded_by=["D1"]),
    dict(id="conservation_breadth", capability="target_identification",
         name="Conservation-breadth workhorse", reproduced=True,
         evidence="LEDGER.md (conservation null); COMPUTATIONAL_DEAD_ENDS.md#D1",
         headline_metric="AUROC 0.9078 (the label-free ceiling)",
         transfer_condition="the only transferable label-free signal is conservation; no residual for a new CPU signal",
         applies_to=[dict(cls="bacteria_self_metabolism", grade="FULL", metric="AUROC 0.908")],
         bounded_by=["D1"]),
    dict(id="host_nonhomology_safety", capability="host_safety_filter",
         name="Host-non-homology safety hard-filter", reproduced=True,
         evidence="experiments/FRONT1_*, E2E2",
         headline_metric="excludes 35-52% of known targets (safety/recall tension)",
         transfer_condition="applies to any organism with a sequenced proteome vs the human proteome",
         applies_to=[dict(cls=c, grade="FULL", metric="host-homology exclusion") for c in
                     ["bacteria_self_metabolism", "host_dependent_parasite", "fungus", "virus"]],
         bounded_by=[]),
    dict(id="structural_target_class_id", capability="target_identification",
         name="Structural target-class ID (viruses)", reproduced=True,
         evidence="composite_router (virus route)",
         headline_metric="target-CLASS identification (not affinity)",
         transfer_condition="identifies druggable target class from structure; NOT novel-target affinity (D2)",
         applies_to=[dict(cls="virus", grade="CAPPED", metric="target-class only")], bounded_by=["D2"]),
    dict(id="cancer_dependency_target_id", capability="target_identification",
         name="Cancer dependency target-ID", reproduced=True,
         evidence="LEDGER.md#V15,#V22 (B12/B23)",
         headline_metric="target's own dependency rho +0.187 (MDM2 +0.47); NO transferable functional-state beyond target",
         transfer_condition="signal is a drug's OWN target dependency (target-specific), not a general functional predictor",
         applies_to=[dict(cls="cancer", grade="CAPPED", metric="target-anchored dependency only")],
         bounded_by=["D3", "B23_functional_tautology"]),
    dict(id="genetic_support_target_id", capability="target_identification",
         name="Genetic-support (Open Targets) target-ID", reproduced=True,
         evidence="experiments/GENETICS1_complex_disease_genetics/",
         headline_metric="genassoc>0 -> clinical precedence OR 2.26 (dose-response to 5.18)",
         transfer_condition="requires GWAS/genetic evidence for the disease; confounded by gene 'fame' (adjust)",
         applies_to=[dict(cls="complex_human_disease", grade="FULL", metric="OR 2.26 (fame-confounded)")],
         bounded_by=["D4"]),
    dict(id="cis_MR_causal_target_id", capability="target_identification",
         name="Transparent cis-MR causal target-ID", reproduced=True,
         evidence="experiments/MR1_causal_target_id/",
         headline_metric="MR-sig genes -> clinical precedence OR 3.16 (CI [2.03,5.19]); direction-aware",
         transfer_condition="requires a cis-eQTL instrument + disease GWAS; predictively REDUNDANT with OT aggregate (H2)",
         applies_to=[dict(cls="complex_human_disease", grade="FULL", metric="OR 3.16 (transparent/direction-aware)")],
         bounded_by=["MR1_H2"]),
    dict(id="monogenic_arm", capability="target_identification",
         name="Monogenic-disease mechanism arm (MENDEL1)", reproduced=True,
         evidence="experiments/MENDEL1_mendelian_disease_arm/",
         headline_metric="druggability-class routing for monogenic modes",
         transfer_condition="requires a known causal gene + mode-of-action",
         applies_to=[dict(cls="monogenic_disease", grade="CAPPED", metric="mode-of-action routing")],
         bounded_by=[]),
    dict(id="synergy_ranker", capability="combination_intervention",
         name="SynergyRanker (drug-combination synergy)", reproduced=True,
         evidence="experiments/{B24,B25,B28,B29}/; src/intercepta/synergy.py",
         headline_metric="leave-combination-out rho +0.385-0.606 (known library); conformal-calibrated",
         transfer_condition="new pairings of a KNOWN drug library only; NOVEL-drug synergy does NOT generalize",
         applies_to=[dict(cls="cancer", grade="FULL", metric="known-library rho +0.39-0.61 (cell-line Loewe)")],
         bounded_by=["B25_novel_drug", "B26_mech_synergy"]),
    dict(id="repurposing_map", capability="intervention_mapping",
         name="Target->drug repurposing (INTERVENE1)", reproduced=True,
         evidence="INTERVENE1 layer",
         headline_metric="validated 9/9 known target->drug; novel-target coverage 1/32",
         transfer_condition="maps KNOWN targets to KNOWN drugs; does NOT expand novel-pathogen coverage (D6)",
         applies_to=[dict(cls=c, grade="CAPPED", metric="known target->drug only") for c in
                     ["bacteria_self_metabolism", "cancer", "complex_human_disease"]],
         bounded_by=["D6", "STRUCTREPURPOSE1"]),
    dict(id="expression_response_transfer", capability="drug_response_prediction",
         name="Expression->response cross-dataset transfer (V1/V9)", reproduced=True,
         evidence="LEDGER.md#V1,#V9 (B1/B3b/B3c)",
         headline_metric="drug-specific diag-off +0.040-0.051 (weak; single cohort BeatAML)",
         transfer_condition="weak, drug-specific, single-cohort; bounded by the +0.212 baseline ceiling",
         applies_to=[dict(cls="cancer", grade="CAPPED", metric="weak drug-specific transfer")],
         bounded_by=["D3", "B10_clinical"]),
]

FABRICATIONS_REMOVED = {
    "source_of_truth": "docs/audits/VISION_AUDIT.txt (92 requirements: 23 MET / 36 PARTIAL / 24 NOT / 9 FAKE)",
    "removal_record": "INTEGRITY_SWEEP.md",
    "nine_fake_claims": [
        "AI generative de-novo molecules (was R-group/scaffold hopping)",
        "Stage-5 Pareto scores presented as computed (dimension scores typed by hand)",
        "Mechanism-of-action explanations (hand-written text)",
        "Full safety profile (hand-written)",
        "Synthesis route (hand-written; no retrosynthesis engine)",
        "Comparison vs standard-of-care (hand-written)",
        "Clinical-trial design (hand-written)",
        "'Generates novel molecules' differentiator (no AI model)",
        "Pareto-ranking technology 'working' (inputs human-assigned)",
    ],
    "deleted_result_files": [
        "results/pharma_deliverable_*.json", "results/INTERCEPTA_{pharma,FINAL}_package.json",
        "results/INTERCEPTA_explanations.json", "results/pareto_ranking_mcrpc.json",
        "results/INTERCEPTA_*_candidates.csv (fabricated ranking chain)",
        "results/round3_gbm/pharma_deliverable_gbm_v0.{json,md}",
        "8 build-logs with BeatAML sample IDs (PHI safety net)", "unverifiable KAALI PDFs",
    ],
    "mislabeled_but_real_retained": [
        "*denovo*molecules*.csv = scaffold-hopped analogues (NOT de novo)",
        "phase1_5trial_VALIDATED.* = '5/5' retracted; real 2/6 (Cox PH)",
        "lead_candidate_INTC002.json = computational hypothesis (novelty 0.266), not a validated drug",
    ],
    "also_retracted": ["6/6 scouts", "79% complete", "universal", "p38 MAPK finding"],
}

def main():
    kg = {
        "_about": "F9 composite knowledge graph: validated arms + FIRST-CLASS negatives/dead-ends + transfer "
                  "conditions + abstention boundaries, with per-edge provenance. Integration/provenance only — "
                  "makes NO new scientific claim. Built from LEDGER.md, COMPUTATIONAL_DEAD_ENDS.md, composite_router, "
                  "MR1, INTEGRITY_SWEEP.md by build_kg.py (deterministic).",
        "disease_classes": DISEASE_CLASSES,
        "arms": ARMS,
        "deadends": [dict(id=i, name=n, tried=t, negative_outcome=o, category=c, reopen_trigger=r, evidence=e)
                     for (i, n, t, o, c, r, e) in DEADENDS],
        "fabrications_removed": FABRICATIONS_REMOVED,
    }
    out = os.path.join(HERE, "kg.json")
    payload = json.dumps(kg, indent=2, sort_keys=True)
    with open(out, "w") as f:
        f.write(payload + "\n")
    print(f"arms={len(ARMS)} deadends={len(DEADENDS)} disease_classes={len(DISEASE_CLASSES)} "
          f"fake_claims={len(FABRICATIONS_REMOVED['nine_fake_claims'])}")
    print("kg.json sha256:", hashlib.sha256(payload.encode()).hexdigest())
    print("written ->", out)

if __name__ == "__main__":
    main()
