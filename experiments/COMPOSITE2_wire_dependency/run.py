"""COMPOSITE2 — demonstration + validation of wiring the VALIDATED DEPEND1 functional-dependency layer into
the explicit router, transfer-condition-precise (see PREREG.md).

Four inputs, PRE-REGISTERED routing outcomes asserted:
  (A) HUMAN_CANCER (declared) — functional-dependency NOW FIRES -> shortlist. Reuses DEPEND1's committed
      results; asserts a KNOWN selective target appears for the context (skin -> SOX10; KRAS-hotspot -> KRAS).
      THE NEW CAPABILITY.
  (B) HOST_DEPENDENT_PARASITE — P. falciparum (declared): STILL ABSTAINS; functional-dependency did NOT fire;
      gate + abstention reason cite the DATA-DEPENDENT non-transfer (no dependency data / label-free not
      organism-transferred). THE DECISIVE INTEGRITY TEST.
  (C) BACTERIUM — K. pneumoniae (declared): FBA path unchanged (regression); cores present (reuse committed
      ENGINE_endtoend report — no recompute).
  (D) VIRUS — SARS-CoV-2 (autodetected): structural class-ID unchanged (regression); FBA + functional-
      dependency NOT fired (reuse committed GENERALIZE3).

Deterministic (pure logic + reuse of committed results). Reproduced x2 (SHA-256 over sorted-key JSON payload
excluding verdict/provenance). Output: results/COMPOSITE2_metrics.json (+payload.sha256), SUMMARY.md.
NO git commit/push. NO data committed.
"""
import os, sys, json, time, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
from intercepta.composite_router import (  # noqa: E402
    CompositeRouter, BiologyClass, Signal, HOST_DEPENDENT_PARASITE_ABSTENTION,
)

DEPEND1_METRICS = os.path.normpath(os.path.join(
    HERE, "..", "DEPEND1_functional_dependency", "results", "DEPEND1_metrics.json"))
ENGINE_REPORT = os.path.normpath(os.path.join(
    HERE, "..", "ENGINE_endtoend", "results", "ENGINE_report.json"))
G3_METRICS = os.path.normpath(os.path.join(
    HERE, "..", "GENERALIZE3_viral_structural_blind", "results", "GENERALIZE3_metrics.json"))

CORES = ["murA", "murG", "mraY", "dxs"]   # validated K. pneumoniae metabolic cores (ENGINE)
# pre-registered HUMAN_CANCER (context -> expected known selective target) pairs
HUMAN_CANCER_CONTEXTS = [("skin", "SOX10"), ("KRAS-hotspot", "KRAS")]


# ---------------------------------------------------------------------------------------------------
def case_A_human_cancer(router):
    """Declared human_cancer -> functional-dependency FIRES -> shortlist (NEW capability)."""
    decision = router.decide("human cancer (DepMap context)", declared_class=BiologyClass.HUMAN_CANCER)
    fired = set(decision.signals_fired)
    gated = {g["signal"] for g in decision.to_dict()["signals_gated_out"]}

    contexts = {}
    known_target_recovered = {}
    depend1_all_pass = None
    for ctx, expected_tgt in HUMAN_CANCER_CONTEXTS:
        sl = router.functional_dependency_shortlist_from_depend1(DEPEND1_METRICS, ctx)
        targets = {row["target"]: row for row in sl["shortlist"]}
        hit = expected_tgt in targets
        rank_ok = hit and targets[expected_tgt]["selectivity_rank_genomewide"] == 1 \
            and targets[expected_tgt]["in_top10"] is True
        contexts[ctx] = {"shortlist": sl["shortlist"], "scope": sl["scope"]}
        known_target_recovered[ctx] = {"expected_target": expected_tgt, "present": hit,
                                        "rank1_and_in_top10": bool(rank_ok)}
        depend1_all_pass = all(v == "PASS" for v in sl["depend1_gates"].values())

    assertions = {
        "output_is_shortlist": decision.output_type == "shortlist",
        "functional_dependency_FIRED": Signal.FUNCTIONAL_DEPENDENCY.value in fired,
        "not_abstained": decision.abstention is None,
        "fba_still_gated_out": Signal.FBA_ESSENTIALITY.value in gated,   # host-embedded; NOT un-gated
        "skin_recovers_SOX10_rank1": known_target_recovered["skin"]["rank1_and_in_top10"],
        "kras_hotspot_recovers_KRAS_rank1": known_target_recovered["KRAS-hotspot"]["rank1_and_in_top10"],
        "depend1_gates_all_pass": bool(depend1_all_pass),
    }
    return {"routing": decision.to_dict(), "contexts": contexts,
            "known_target_recovered": known_target_recovered, "assertions": assertions}


def case_B_parasite(router):
    """P. falciparum -> STILL ABSTAINS; functional-dependency did NOT fire (decisive integrity test)."""
    decision = router.decide("Plasmodium falciparum", declared_class=BiologyClass.HOST_DEPENDENT_PARASITE)
    gated = {g["signal"]: g["reason"] for g in decision.to_dict()["signals_gated_out"]}
    fired = set(decision.signals_fired)
    fd_reason = gated.get(Signal.FUNCTIONAL_DEPENDENCY.value, "")
    assertions = {
        "output_is_abstention": decision.output_type == "abstention",
        "did_NOT_emit_shortlist": decision.output_type != "shortlist",
        "functional_dependency_did_NOT_fire": Signal.FUNCTIONAL_DEPENDENCY.value not in fired,
        "functional_dependency_gated_out": Signal.FUNCTIONAL_DEPENDENCY.value in gated,
        "fd_gate_reason_cites_human_cancer_scope": "HUMAN_CANCER" in fd_reason,
        "fd_gate_reason_cites_no_organism_transfer": "organism-transfer" in fd_reason.lower(),
        "fba_NOT_fired": Signal.FBA_ESSENTIALITY.value not in fired,
        "fba_gated_out": Signal.FBA_ESSENTIALITY.value in gated,
        "no_discovery_signal_fired": len(fired) == 0,
        "abstention_matches_prereg_constant": decision.abstention == HOST_DEPENDENT_PARASITE_ABSTENTION,
        "abstention_cites_no_dependency_data": "no dependency data" in (decision.abstention or ""),
        "abstention_cites_label_free": "label-free" in (decision.abstention or ""),
        "abstention_cites_organism_transfer": "organism-transferred" in (decision.abstention or ""),
    }
    return {"routing": decision.to_dict(), "abstention_reason": decision.abstention,
            "functional_dependency_gate_reason": fd_reason, "assertions": assertions}


def case_C_bacterium(router):
    """K. pneumoniae -> FBA path unchanged (regression). Cores present via committed ENGINE report."""
    decision = router.decide("kpneumoniae", declared_class=BiologyClass.BACTERIUM)
    fired = set(decision.signals_fired)
    committed = json.load(open(ENGINE_REPORT))["report"]
    committed_genes = [r.get("gene", r["entity"]) for r in committed["shortlist"]]
    cores_present = {c: (c in committed_genes) for c in CORES}
    assertions = {
        "output_is_shortlist": decision.output_type == "shortlist",
        "fba_fired": Signal.FBA_ESSENTIALITY.value in fired,
        "conservation_breadth_fired": Signal.CONSERVATION_BREADTH.value in fired,
        "functional_dependency_NOT_fired": Signal.FUNCTIONAL_DEPENDENCY.value not in fired,  # out of domain
        "all_cores_present_in_committed_engine": all(cores_present.values()),
        "not_abstained": decision.abstention is None,
    }
    return {"routing": decision.to_dict(), "cores_present": cores_present, "assertions": assertions}


def case_D_virus(router):
    """SARS-CoV-2 -> autodetect VIRUS -> structural class-ID (regression). FBA & FD NOT fired."""
    decision = router.decide("SARS-CoV-2", proteome_size=30)
    struct = router.structural_class_id_from_generalize3(G3_METRICS)
    hyp = {h["protein"]: h for h in struct["hypotheses"]}
    fired = set(decision.signals_fired)
    assertions = {
        "autodetected_virus": decision.biology_class == BiologyClass.VIRUS.value
                              and decision.class_source == "autodetected",
        "output_is_structural_class_id": decision.output_type == "structural_class_id",
        "structural_fired": Signal.STRUCTURAL_HOMOLOGY.value in fired,
        "fba_NOT_fired": Signal.FBA_ESSENTIALITY.value not in fired,
        "functional_dependency_NOT_fired": Signal.FUNCTIONAL_DEPENDENCY.value not in fired,
        "Mpro_is_protease": hyp["nsp5_Mpro"]["target_class"] == "protease",
        "RdRp_is_polymerase": hyp["nsp12_RdRp"]["target_class"] == "polymerase",
    }
    return {"routing": decision.to_dict(), "structural_hypotheses": struct["hypotheses"],
            "assertions": assertions}


def main():
    t0 = time.time()
    router = CompositeRouter()
    A = case_A_human_cancer(router)
    B = case_B_parasite(router)
    C = case_C_bacterium(router)
    D = case_D_virus(router)

    def all_true(case):
        return all(v is True for v in case["assertions"].values() if v is not None)

    payload = {
        "test": "COMPOSITE2 wire DEPEND1 functional-dependency into the router (transfer-condition-precise)",
        "case_A_human_cancer": A,
        "case_B_parasite": B,
        "case_C_bacterium": C,
        "case_D_virus": D,
        "all_assertions_pass": bool(all_true(A) and all_true(B) and all_true(C) and all_true(D)),
    }
    payload_json = json.dumps(payload, sort_keys=True)
    sha = hashlib.sha256(payload_json.encode()).hexdigest()

    verdict = (
        f"ROUTER v2: (A) HUMAN_CANCER -> {A['routing']['output_type']} "
        f"(functional_dependency FIRED={A['assertions']['functional_dependency_FIRED']}; "
        f"skin->SOX10 & KRAS-hotspot->KRAS recovered at rank 1); "
        f"(B) PARASITE P.falciparum -> {B['routing']['output_type']} "
        f"(functional_dependency did NOT fire={B['assertions']['functional_dependency_did_NOT_fire']}; "
        f"STILL ABSTAINS -- no dependency data / label-free not organism-transferred); "
        f"(C) BACTERIUM K.pneumoniae -> {C['routing']['output_type']} (FBA unchanged, cores present); "
        f"(D) VIRUS SARS-CoV-2 -> {D['routing']['output_type']} (structural unchanged, FBA not fired). "
        f"ALL ASSERTIONS PASS: {payload['all_assertions_pass']}. "
        f"INTEGRITY HOLDS: functional-dependency un-gated ONLY for human/cancer (data exists); the novel "
        f"parasite STILL ABSTAINS by design. Scope: cancer CELL-LINE dependency, NOT patient/clinical."
    )

    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "runtime_sec": round(time.time() - t0, 2)}
    json.dump({"payload": payload, "verdict": verdict, "provenance": prov},
              open(os.path.join(HERE, "results", "COMPOSITE2_metrics.json"), "w"), indent=2, sort_keys=True)
    open(os.path.join(HERE, "results", "COMPOSITE2_payload.sha256"), "w").write(sha + "\n")

    print("=== COMPOSITE2 wire functional-dependency — 4-case routing ===")
    for tag, case in (("A human_cancer", A), ("B parasite", B), ("C bacterium", C), ("D virus", D)):
        print(f"\n[{tag}] class={case['routing']['biology_class']} ({case['routing']['class_source']}) "
              f"-> {case['routing']['output_type']}")
        print(f"   fired(discovery): {case['routing']['signals_fired']}")
        print(f"   supporting:       {case['routing']['supporting_signals']}")
        print(f"   gated out:        {[g['signal'] for g in case['routing']['signals_gated_out']]}")
        for k, v in case["assertions"].items():
            print(f"     assert {k}: {v}")
    print("\nVERDICT:", verdict)
    print("payload sha256:", sha, f"[{time.time()-t0:.1f}s]")

    if not payload["all_assertions_pass"]:
        raise SystemExit("COMPOSITE2 FAILED: one or more pre-registered routing assertions did not hold.")


if __name__ == "__main__":
    main()
