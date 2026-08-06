"""COMPOSITE3 — demonstration + validation of the HONEST host-dependent-parasite FBA refinement (router v3).

The correction (see PREREG.md): router v2 blanket-ABSTAINS on host-dependent parasites for FBA. HARDENP1
falsified that premise (Toxoplasma PASSES OR 14.10; Plasmodium FAILS OR 2.47 — both host-dependent). v3 fires
FBA on a host-dependent organism THAT HAS A CURATED GEM, but at capped/reduced confidence with an explicit
uncertainty flag — NEITHER a blanket abstention (which would wrongly refuse Toxoplasma) NOR bacterial-grade
confidence (which would overclaim on Plasmodium). With NO GEM there is no signal → it still ABSTAINS.

Pre-registered routing outcomes asserted (reusing ONLY committed, reproduced-x2 results):
  (A) Toxoplasma (host-dep, GOOD GEM iTgo2020)   -> shortlist; FBA FIRES capped+flagged; HARDENP1 OR 14.10 PASS
      surfaced a-posteriori. NOT an abstention.
  (B) Plasmodium (host-dep, salvage GEM iPfal19) -> shortlist; FBA FIRES capped+flagged (SAME flag); GENERALIZE5
      OR 2.47 FAIL surfaced a-posteriori — exactly why confidence is capped; unknowable a-priori.
  (C) host-dependent organism, NO GEM            -> ABSTENTION (no signal); reason cites no-GEM (NOT "metabolic
      essentiality falsified").
  (D) REGRESSION: bacterium -> FBA full-grade shortlist; virus -> structural; human_cancer -> functional-dep.

Also emits the OPTIONAL ADVISORY (HEURISTIC / NOT VALIDATED) GEM-topology descriptor for both parasites and
demonstrates it does NOT separate the PASS from the FAIL a-priori.

Deterministic (pure logic + reuse of committed results). Reproduced x2 (SHA-256 over sorted-key JSON payload
excluding verdict/provenance). Output: results/COMPOSITE3_metrics.json (+payload.sha256), SUMMARY.md.
NO git commit/push. NO data committed.
"""
import os, sys, json, time, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
from intercepta.composite_router import (  # noqa: E402
    CompositeRouter, BiologyClass, Signal, TRANSFER_GATE,
    HOST_DEPENDENT_PARASITE_NO_GEM_ABSTENTION,
)

EXP = os.path.normpath(os.path.join(HERE, ".."))
HARDENP1 = os.path.join(EXP, "HARDENP1_parasite_multi", "results", "HARDENP1_metrics.json")
GENERALIZE5 = os.path.join(EXP, "GENERALIZE5_parasite_fba", "results", "GENERALIZE5_metrics.json")
ENGINE_REPORT = os.path.join(EXP, "ENGINE_endtoend", "results", "ENGINE_report.json")
G3_METRICS = os.path.join(EXP, "GENERALIZE3_viral_structural_blind", "results", "GENERALIZE3_metrics.json")
DEPEND1 = os.path.join(EXP, "DEPEND1_functional_dependency", "results", "DEPEND1_metrics.json")

CORES = ["murA", "murG", "mraY", "dxs"]
FBA_NOTE = TRANSFER_GATE[Signal.FBA_ESSENTIALITY].uncertainty_note   # the frozen verbatim uncertainty sentence


def _committed_counts(path):
    p = json.load(open(path))["payload"]
    return p["n_fba_essential"], p["n_model_genes"]


# ---------------------------------------------------------------------------------------------------
def case_A_toxoplasma(router):
    """host-dependent + GOOD GEM -> FBA FIRES capped+flagged (NOT abstain). HARDENP1 OR 14.10 PASS a-posteriori."""
    d = router.decide("Toxoplasma gondii", declared_class=BiologyClass.HOST_DEPENDENT_PARASITE,
                      has_curated_gem=True)
    fired = set(d.signals_fired)
    flags = {f["signal"]: f for f in d.uncertainty_flags}
    sl = router.fba_capped_shortlist_from_committed(HARDENP1, "Toxoplasma gondii")
    apost = sl["a_posteriori_validation"]
    assertions = {
        "output_is_shortlist_not_abstention": d.output_type == "shortlist" and d.abstention is None,
        "fba_FIRES": Signal.FBA_ESSENTIALITY.value in fired,
        "uncertain_flag_set": d.uncertain is True,
        "confidence_capped_below_full": d.confidence_cap == 0.5,
        "fba_flag_present_with_verbatim_note": (Signal.FBA_ESSENTIALITY.value in flags
                                                and flags[Signal.FBA_ESSENTIALITY.value]["note"] == FBA_NOTE),
        "functional_dependency_did_NOT_fire": Signal.FUNCTIONAL_DEPENDENCY.value not in fired,
        "aposteriori_OR_is_14_10": round(apost["odds_ratio"], 2) == 14.10,
        "aposteriori_bacterial_gate_PASS": apost["bacterial_gate_pass"] is True,
    }
    return {"routing": d.to_dict(), "fba_capped_shortlist": sl, "assertions": assertions}


def case_B_plasmodium(router):
    """host-dependent + salvage GEM -> FBA FIRES capped+flagged (SAME flag). GENERALIZE5 OR 2.47 FAIL a-posteriori."""
    d = router.decide("Plasmodium falciparum", declared_class=BiologyClass.HOST_DEPENDENT_PARASITE,
                      has_curated_gem=True)
    fired = set(d.signals_fired)
    flags = {f["signal"]: f for f in d.uncertainty_flags}
    sl = router.fba_capped_shortlist_from_committed(GENERALIZE5, "Plasmodium falciparum")
    apost = sl["a_posteriori_validation"]
    assertions = {
        "output_is_shortlist_not_abstention": d.output_type == "shortlist" and d.abstention is None,
        "fba_FIRES": Signal.FBA_ESSENTIALITY.value in fired,
        "uncertain_flag_set": d.uncertain is True,
        "confidence_capped_below_full": d.confidence_cap == 0.5,
        "SAME_flag_note_as_toxoplasma": (Signal.FBA_ESSENTIALITY.value in flags
                                         and flags[Signal.FBA_ESSENTIALITY.value]["note"] == FBA_NOTE),
        "functional_dependency_did_NOT_fire": Signal.FUNCTIONAL_DEPENDENCY.value not in fired,
        "aposteriori_OR_is_2_47": round(apost["odds_ratio"], 2) == 2.47,
        "aposteriori_bacterial_gate_FAIL": apost["bacterial_gate_pass"] is False,  # WHY the cap exists
    }
    return {"routing": d.to_dict(), "fba_capped_shortlist": sl, "assertions": assertions}


def case_C_no_gem(router):
    """host-dependent organism with NO GEM -> ABSTENTION (no signal). NOT the old 'metabolic falsified' reason."""
    d = router.decide("novel host-dependent organism (no curated GEM)",
                      declared_class=BiologyClass.HOST_DEPENDENT_PARASITE, has_curated_gem=False)
    gated = {g["signal"]: g["reason"] for g in d.to_dict()["signals_gated_out"]}
    fired = set(d.signals_fired)
    assertions = {
        "output_is_abstention": d.output_type == "abstention",
        "no_signal_fired": len(fired) == 0,
        "not_uncertain": d.uncertain is False,
        "abstention_matches_no_gem_constant": d.abstention == HOST_DEPENDENT_PARASITE_NO_GEM_ABSTENTION,
        "reason_cites_no_gem": "NO curated GEM" in (d.abstention or ""),
        "reason_NOT_metabolic_falsified": "metabolic essentiality falsified" not in (d.abstention or ""),
        "reason_cites_hardenp1_and_generalize5": ("HARDENP1" in (d.abstention or "")
                                                  and "GENERALIZE5" in (d.abstention or "")),
        "fba_gated_because_no_gem": (Signal.FBA_ESSENTIALITY.value in gated
                                     and "curated GEM" in gated.get(Signal.FBA_ESSENTIALITY.value, "").lower()
                                     or "unavailable" in gated.get(Signal.FBA_ESSENTIALITY.value, "")),
        "functional_dependency_still_gated": Signal.FUNCTIONAL_DEPENDENCY.value in gated,
    }
    return {"routing": d.to_dict(), "abstention_reason": d.abstention, "assertions": assertions}


def case_D_regression(router):
    """REGRESSION: bacterium (FBA full-grade) / virus (structural) / human_cancer (functional-dep). All unchanged."""
    # D1 bacterium
    b = router.decide("Klebsiella pneumoniae", declared_class=BiologyClass.BACTERIUM)
    committed = json.load(open(ENGINE_REPORT))["report"]
    committed_genes = [r.get("gene", r["entity"]) for r in committed["shortlist"]]
    cores_present = {c: (c in committed_genes) for c in CORES}
    # D2 virus
    v = router.decide("SARS-CoV-2", proteome_size=30)
    struct = router.structural_class_id_from_generalize3(G3_METRICS)
    hyp = {h["protein"]: h for h in struct["hypotheses"]}
    # D3 human_cancer
    h = router.decide("human cancer (DepMap)", declared_class=BiologyClass.HUMAN_CANCER)
    assertions = {
        "D1_bacterium_shortlist": b.output_type == "shortlist",
        "D1_fba_fired_FULL_grade": (Signal.FBA_ESSENTIALITY.value in b.signals_fired
                                    and b.uncertain is False and b.confidence_cap is None),
        "D1_cores_present": all(cores_present.values()),
        "D2_virus_structural": v.output_type == "structural_class_id" and v.class_source == "autodetected",
        "D2_fba_not_fired": Signal.FBA_ESSENTIALITY.value not in v.signals_fired,
        "D2_Mpro_protease": hyp["nsp5_Mpro"]["target_class"] == "protease",
        "D2_RdRp_polymerase": hyp["nsp12_RdRp"]["target_class"] == "polymerase",
        "D3_human_cancer_shortlist": h.output_type == "shortlist",
        "D3_functional_dependency_fired": Signal.FUNCTIONAL_DEPENDENCY.value in h.signals_fired,
        "D3_not_uncertain": h.uncertain is False,
        "D3_fba_not_fired": Signal.FBA_ESSENTIALITY.value not in h.signals_fired,
    }
    return {"bacterium": b.to_dict(), "cores_present": cores_present, "virus": v.to_dict(),
            "structural_hypotheses": struct["hypotheses"], "human_cancer": h.to_dict(),
            "assertions": assertions}


def advisory_diagnostic(router):
    """OPTIONAL, HEURISTIC, **NOT VALIDATED** advisory: the screen-free GEM-topology descriptor for both
    parasites, demonstrating it does NOT separate the PASS from the FAIL a-priori. NEVER gates the router."""
    tox_ess, tox_n = _committed_counts(HARDENP1)
    pf_ess, pf_n = _committed_counts(GENERALIZE5)
    tox = router.gem_topology_advisory(tox_ess, tox_n, "Toxoplasma gondii (PASS OR 14.10)")
    pf = router.gem_topology_advisory(pf_ess, pf_n, "Plasmodium falciparum (FAIL OR 2.47)")
    # honest demonstration: the FAIL organism has the LOWER FBA-essential fraction -> naive heuristic would MISRANK
    non_discriminating = pf["frac_fba_essential"] < tox["frac_fba_essential"]  # FAIL < PASS: no usable direction
    assertions = {
        "advisory_labeled_not_validated": ("NOT VALIDATED" in tox["status"]
                                           and tox["does_not_predict_fba_reliability"] is True),
        "does_not_separate_pass_from_fail_apriori": non_discriminating,   # the honest point (n=2, no threshold)
    }
    return {"toxoplasma": tox, "plasmodium": pf,
            "interpretation": ("FAIL (Plasmodium) frac %.4f < PASS (Toxoplasma) frac %.4f: the descriptor does "
                               "NOT give a usable a-priori direction/threshold; the true discriminators (recall "
                               "0.51 vs 0.20, base rate 0.42 vs 0.64) need a screen a novel organism lacks. "
                               "ADVISORY ONLY, never gates." % (pf["frac_fba_essential"], tox["frac_fba_essential"])),
            "assertions": assertions}


def main():
    t0 = time.time()
    router = CompositeRouter()
    A = case_A_toxoplasma(router)
    B = case_B_plasmodium(router)
    C = case_C_no_gem(router)
    D = case_D_regression(router)
    ADV = advisory_diagnostic(router)

    def all_true(case):
        return all(v is True for v in case["assertions"].values() if v is not None)

    payload = {
        "test": "COMPOSITE3 host-dependent FBA refinement (router v3): fire-capped-and-flagged, not blanket-abstain",
        "case_A_toxoplasma": A,
        "case_B_plasmodium": B,
        "case_C_no_gem": C,
        "case_D_regression": D,
        "advisory_diagnostic_NOT_VALIDATED": ADV,
        "all_assertions_pass": bool(all_true(A) and all_true(B) and all_true(C) and all_true(D) and all_true(ADV)),
    }
    payload_json = json.dumps(payload, sort_keys=True)
    sha = hashlib.sha256(payload_json.encode()).hexdigest()

    verdict = (
        f"ROUTER v3 host-dependent FBA refinement: "
        f"(A) Toxoplasma (GOOD GEM) -> {A['routing']['output_type']} -- FBA FIRES capped(0.5)+flagged, NO LONGER "
        f"abstains (HARDENP1 OR 14.10 PASS a-posteriori); "
        f"(B) Plasmodium (salvage GEM) -> {B['routing']['output_type']} -- FBA FIRES with the SAME cap+flag "
        f"(GENERALIZE5 OR 2.47 FAIL a-posteriori = exactly why confidence is capped; unknowable a-priori); "
        f"(C) no-GEM host-dependent -> {C['routing']['output_type']} (no signal; NOT 'metabolic falsified'); "
        f"(D) REGRESSION bacterium=full-grade shortlist / virus=structural / human_cancer=functional-dep, all "
        f"unchanged. ALL ASSERTIONS PASS: {payload['all_assertions_pass']}. HONEST ADMISSION: the router CANNOT "
        f"predict a-priori whether a novel host-dependent organism's GEM is Toxoplasma-like (pass) or "
        f"Plasmodium-like (fail); it fires FBA with flagged, capped uncertainty rather than pretending to know. "
        f"The advisory GEM-topology descriptor is HEURISTIC/NOT VALIDATED and does NOT separate pass from fail."
    )

    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "runtime_sec": round(time.time() - t0, 2)}
    json.dump({"payload": payload, "verdict": verdict, "provenance": prov},
              open(os.path.join(HERE, "results", "COMPOSITE3_metrics.json"), "w"), indent=2, sort_keys=True)
    open(os.path.join(HERE, "results", "COMPOSITE3_payload.sha256"), "w").write(sha + "\n")

    print("=== COMPOSITE3 host-dependent FBA refinement (router v3) — routing validation ===")
    for tag, case, key in (("A toxoplasma", A, "routing"), ("B plasmodium", B, "routing"),
                           ("C no-GEM", C, "routing")):
        r = case[key]
        print(f"\n[{tag}] class={r['biology_class']} -> {r['output_type']} | "
              f"uncertain={r['uncertain']} cap={r['confidence_cap']}")
        print(f"   fired: {r['signals_fired']}  flags: {[f['signal'] for f in r['uncertainty_flags']]}")
        for k, v in case["assertions"].items():
            print(f"     assert {k}: {v}")
    print("\n[D regression]")
    for k, v in D["assertions"].items():
        print(f"     assert {k}: {v}")
    print("\n[ADVISORY — HEURISTIC / NOT VALIDATED, never gates]")
    print("   ", ADV["interpretation"])
    for k, v in ADV["assertions"].items():
        print(f"     assert {k}: {v}")
    print("\nVERDICT:", verdict)
    print("payload sha256:", sha, f"[{time.time()-t0:.1f}s]")

    if not payload["all_assertions_pass"]:
        raise SystemExit("COMPOSITE3 FAILED: one or more pre-registered routing assertions did not hold.")


if __name__ == "__main__":
    main()
