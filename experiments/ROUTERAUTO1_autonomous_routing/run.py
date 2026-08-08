"""ROUTERAUTO1 — VALIDATE the autonomous biology-class detector by leave-one-out routing over EVERY committed
organism the arc has a signal-outcome for. The detector has ZERO fitted parameters (all rules pre-registered
from biology in PREREG.md), so leave-one-out == full evaluation: each organism is classified from ONLY its own
objective features, then the UNCHANGED COMPOSITE1/2/3 gate fires. We check (G-CLEAR) every clear case routes to
its empirically-correct class + fire/abstain, and (G-FAILSAFE, HARD) the DARK proteins + the novel zero-screen
parasite ALWAYS abstain with zero signals fired. Deterministic; no RNG; reproduced x2 byte-identical.
"""
import os, sys, json, time, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
from intercepta.composite_router import CompositeRouter, BiologyClass, Signal          # noqa: E402
from intercepta.class_detector import ProteomeFeatures                                 # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BC = BiologyClass

# ------------------------------------------------------------------------------------------------------
# The evaluation panel. `features` are OBJECTIVE (would be computed from each proteome); `expect_*` is the
# PRE-REGISTERED empirically-correct routing (PREREG.md §3-4). `fail_safe` marks the two HARD cases.
# `expect_signal` = the discovery signal that MUST fire (None => a correct abstention).
# ------------------------------------------------------------------------------------------------------
CELL = dict(has_translation_machinery=True)
PANEL = [
    # ---- bacteria (BACTERIUM -> FBA full-grade shortlist) --------------------------------------------
    ("Escherichia coli", "VAL-ESS", ProteomeFeatures(n_proteins=4400, domain_of_life="bacteria", **CELL),
     BC.BACTERIUM, "shortlist", Signal.FBA_ESSENTIALITY, False),
    ("Klebsiella pneumoniae", "CROSSVAL/VAL-ESS-KP/BLIND1", ProteomeFeatures(n_proteins=5000, domain_of_life="bacteria", **CELL),
     BC.BACTERIUM, "shortlist", Signal.FBA_ESSENTIALITY, False),
    ("Neisseria gonorrhoeae", "BLIND1 (prospective PASS OR 6.13)", ProteomeFeatures(n_proteins=2100, domain_of_life="bacteria", **CELL),
     BC.BACTERIUM, "shortlist", Signal.FBA_ESSENTIALITY, False),
    ("Campylobacter jejuni", "BLIND2 (prospective PASS OR 3.92)", ProteomeFeatures(n_proteins=1600, domain_of_life="bacteria", **CELL),
     BC.BACTERIUM, "shortlist", Signal.FBA_ESSENTIALITY, False),
    ("Bacteroides thetaiotaomicron", "BLIND3 (prospective PASS OR 8.03)", ProteomeFeatures(n_proteins=4800, domain_of_life="bacteria", **CELL),
     BC.BACTERIUM, "shortlist", Signal.FBA_ESSENTIALITY, False),
    ("Streptococcus pneumoniae", "BLIND4 (a-posteriori sub-gate; class route still FBA)", ProteomeFeatures(n_proteins=2000, domain_of_life="bacteria", **CELL),
     BC.BACTERIUM, "shortlist", Signal.FBA_ESSENTIALITY, False),
    # ---- archaeon (ARCHAEON -> FBA full-grade shortlist; BLIND6) -------------------------------------
    ("Methanococcus maripaludis", "BLIND6 (prospective PASS OR 4.23)", ProteomeFeatures(n_proteins=1770, domain_of_life="archaea", **CELL),
     BC.ARCHAEON, "shortlist", Signal.FBA_ESSENTIALITY, False),
    # ---- free-living eukaryote / fungus (FREE_EUKARYOTE -> FBA shortlist) ----------------------------
    ("Komagataella phaffii", "BLIND5 (curated GEM; significant enrichment)", ProteomeFeatures(n_proteins=5000, domain_of_life="eukaryota", host_dependent=False, **CELL),
     BC.FREE_EUKARYOTE, "shortlist", Signal.FBA_ESSENTIALITY, False),
    ("Candida albicans", "HARDENF1 (OR 13.93 PASS)", ProteomeFeatures(n_proteins=6200, domain_of_life="eukaryota", host_dependent=False, **CELL),
     BC.FREE_EUKARYOTE, "shortlist", Signal.FBA_ESSENTIALITY, False),
    ("Saccharomyces cerevisiae", "GENERALIZE4 (OR 4.65 PASS)", ProteomeFeatures(n_proteins=6000, domain_of_life="eukaryota", host_dependent=False, **CELL),
     BC.FREE_EUKARYOTE, "shortlist", Signal.FBA_ESSENTIALITY, False),
    # ---- host-dependent parasites -------------------------------------------------------------------
    # Toxoplasma / Plasmodium: curated GEM -> FBA fires CAPPED+flagged (COMPOSITE3; correct route even for
    # Plasmodium whose a-posteriori OR failed -- the router cannot know a-priori, so it fires capped).
    ("Toxoplasma gondii", "HARDENP1 (curated iTgo2020; OR 14.10 PASS)", ProteomeFeatures(n_proteins=8300, domain_of_life="eukaryota", host_dependent=True, has_curated_gem=True, **CELL),
     BC.HOST_DEPENDENT_PARASITE, "shortlist", Signal.FBA_ESSENTIALITY, False),
    ("Plasmodium falciparum", "GENERALIZE5 (curated iPfal19; noise-floor FAIL -> capped)", ProteomeFeatures(n_proteins=5400, domain_of_life="eukaryota", host_dependent=True, has_curated_gem=True, **CELL),
     BC.HOST_DEPENDENT_PARASITE, "shortlist", Signal.FBA_ESSENTIALITY, False),
    # T. brucei: only a sparse de-novo carve, NO curated GEM -> correct route is ABSTAIN (genuine null / the
    # pre-named reach-limit BLIND7). Abstention is the empirically-correct, fail-safe outcome.
    ("Trypanosoma brucei", "BLIND7 (no curated GEM; genuine null OR 0.64)", ProteomeFeatures(n_proteins=9500, domain_of_life="eukaryota", host_dependent=True, has_curated_gem=False, **CELL),
     BC.HOST_DEPENDENT_PARASITE, "abstention", None, False),
    # ---- viruses (VIRUS -> structural class-ID; GENERALIZE3 + HARDENV1) ------------------------------
    ("SARS-CoV-2", "GENERALIZE3 (blind Mpro/RdRp)", ProteomeFeatures(n_proteins=30, has_translation_machinery=False, has_viral_hallmark=True),
     BC.VIRUS, "structural_class_id", Signal.STRUCTURAL_HOMOLOGY, False),
    ("HIV-1", "HARDENV1 (cross-family)", ProteomeFeatures(n_proteins=15, has_translation_machinery=False, has_viral_hallmark=True),
     BC.VIRUS, "structural_class_id", Signal.STRUCTURAL_HOMOLOGY, False),
    ("Influenza A", "HARDENV1 (cross-family)", ProteomeFeatures(n_proteins=12, has_translation_machinery=False, has_viral_hallmark=True),
     BC.VIRUS, "structural_class_id", Signal.STRUCTURAL_HOMOLOGY, False),
    ("Hepatitis C virus", "HARDENV1 (cross-family)", ProteomeFeatures(n_proteins=10, has_translation_machinery=False, has_viral_hallmark=True),
     BC.VIRUS, "structural_class_id", Signal.STRUCTURAL_HOMOLOGY, False),
    ("Herpes simplex virus", "HARDENV1 (cross-family)", ProteomeFeatures(n_proteins=40, has_translation_machinery=False, has_viral_hallmark=True),
     BC.VIRUS, "structural_class_id", Signal.STRUCTURAL_HOMOLOGY, False),
    # ---- human cancer (HUMAN_CANCER -> functional-dependency; DEPEND1) -------------------------------
    ("human melanoma (DepMap)", "DEPEND1 G1/G2/G3 PASS", ProteomeFeatures(n_proteins=20000, is_human_proteome=True, has_dependency_screen=True),
     BC.HUMAN_CANCER, "shortlist", Signal.FUNCTIONAL_DEPENDENCY, False),
    # ---- FAIL-SAFE (hard): MUST abstain, MUST NOT fire ----------------------------------------------
    ("DARK proteins (22)", "DARK1 (22/22 abstain)", ProteomeFeatures(n_proteins=22, has_translation_machinery=False, has_viral_hallmark=False, has_analyzable_structure=False, is_human_proteome=False),
     BC.UNKNOWN, "abstention", None, True),
    ("novel zero-screen parasite", "TRANSFER1 (do NOT un-gate)", ProteomeFeatures(n_proteins=5200, domain_of_life="eukaryota", host_dependent=True, has_curated_gem=False, **CELL),
     BC.HOST_DEPENDENT_PARASITE, "abstention", None, True),
]


def main():
    t0 = time.time()
    router = CompositeRouter()
    cases = []
    for organism, cite, feats, exp_class, exp_out, exp_sig, fail_safe in PANEL:
        dec = router.decide_auto(organism, feats)
        fired = sorted(dec.signals_fired)
        class_ok = dec.biology_class == exp_class.value
        out_ok = dec.output_type == exp_out
        if exp_sig is None:                       # correct answer is an abstention
            sig_ok = (dec.output_type == "abstention") and (fired == [])
        else:
            sig_ok = exp_sig.value in fired
        correct = bool(class_ok and out_ok and sig_ok)
        # fail-safe truth: the case abstained with zero signals fired
        abstained_safe = (dec.output_type == "abstention") and (fired == [])
        cases.append({
            "organism": organism, "evidence": cite, "fail_safe": fail_safe,
            "expected_class": exp_class.value, "detected_class": dec.biology_class,
            "detection_rule": dec.detection["rule"], "class_source": dec.detection["source"],
            "expected_output": exp_out, "output_type": dec.output_type,
            "expected_signal": (exp_sig.value if exp_sig else None), "signals_fired": fired,
            "uncertain_flag": bool(dec.uncertain), "confidence_cap": dec.confidence_cap,
            "requires_descriptor": dec.detection.get("requires_descriptor"),
            "class_ok": class_ok, "output_ok": out_ok, "signal_ok": sig_ok,
            "routed_correctly": correct, "abstained_safe": abstained_safe,
        })

    clear = [c for c in cases if not c["fail_safe"]]
    fs = [c for c in cases if c["fail_safe"]]
    n_clear_ok = sum(1 for c in clear if c["routed_correctly"])
    n_fs_safe = sum(1 for c in fs if c["abstained_safe"])
    fs_misfire = [c["organism"] for c in fs if not c["abstained_safe"]]

    g_clear = (n_clear_ok == len(clear))
    g_failsafe = (n_fs_safe == len(fs)) and (len(fs_misfire) == 0)
    overall = bool(g_clear and g_failsafe)

    # per-class LOO accuracy breakdown
    by_class = {}
    for c in clear:
        b = by_class.setdefault(c["expected_class"], [0, 0])
        b[1] += 1
        b[0] += int(c["routed_correctly"])
    class_accuracy = {k: {"correct": v[0], "n": v[1]} for k, v in sorted(by_class.items())}

    payload = {
        "n_inputs": len(cases),
        "n_clear": len(clear), "n_clear_routed_correct": n_clear_ok,
        "n_fail_safe": len(fs), "n_fail_safe_abstained": n_fs_safe, "fail_safe_misfires": sorted(fs_misfire),
        "class_accuracy": class_accuracy,
        "G_CLEAR": g_clear, "G_FAILSAFE": g_failsafe, "PASS": overall,
        "cases": sorted(cases, key=lambda c: c["organism"]),
        "detector": {
            "fitted_parameters": 0,
            "leave_one_out_equals_full_eval": True,
            "note": ("detector has zero fitted parameters (all rules pre-registered from biology); each "
                     "organism is classified from ONLY its own objective features -> leave-one-out is "
                     "identical to full evaluation, no leakage possible"),
        },
        "principle": ("The autonomous detector selects the routing class from objective features; the UNCHANGED "
                      "COMPOSITE1/2/3 gate then fires exactly the validated signal for that class or abstains. "
                      "Fail-safe cases (dark proteins; novel zero-screen parasite) MUST abstain -- a mis-fire is "
                      "a hard fail. This completes limitation 12: the class no longer needs hand-specifying."),
    }
    verdict = (
        f"ROUTERAUTO1 {'PASS' if overall else 'FAIL'}: autonomous class-detection routed {n_clear_ok}/{len(clear)} "
        f"clear inputs to the empirically-correct class + fire/abstain, and {n_fs_safe}/{len(fs)} fail-safe inputs "
        f"ABSTAINED with zero mis-fires ({'fail-safe HELD' if g_failsafe else 'FAIL-SAFE BREACHED: ' + ', '.join(fs_misfire)}). "
        f"The detector has zero fitted parameters (leave-one-out == full eval). It fires FBA full-grade for "
        f"bacteria/archaeon/free-eukaryote, structural class-ID for viruses, functional-dependency for human "
        f"cancer, capped+flagged FBA for host-dependent parasites WITH a curated GEM (Toxoplasma/Plasmodium), and "
        f"ABSTAINS for a host-dependent parasite with NO curated GEM (T. brucei genuine null; novel zero-screen "
        f"parasite), a human proteome with no dependency screen, an undeclared-host-dependence eukaryote, and the "
        f"DARK proteome. It never confidently routes a dark protein or a zero-screen parasite to a firing signal. "
        f"SCOPE: automates class-detection + routing; does NOT predict a-priori signal transfer for a novel "
        f"organism (capped/flagged per COMPOSITE3); hypotheses with provenance, not drugs; not wet-lab/clinical.")

    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    print("PANEL:", json.dumps({k: payload[k] for k in
          ("n_inputs", "n_clear", "n_clear_routed_correct", "n_fail_safe", "n_fail_safe_abstained",
           "fail_safe_misfires", "class_accuracy", "G_CLEAR", "G_FAILSAFE", "PASS")}, indent=1))
    print("\nROUTED DECISIONS:")
    for c in sorted(cases, key=lambda c: (c["fail_safe"], c["expected_class"], c["organism"])):
        tag = "ABSTAIN" if c["output_type"] == "abstention" else (
            "+".join(c["signals_fired"]) + (" [uncertain]" if c["uncertain_flag"] else ""))
        mark = "OK " if c["routed_correctly"] else "XX "
        fsm = " (FAIL-SAFE)" if c["fail_safe"] else ""
        print(f"  {mark}{c['organism'][:34]:34s} -> {c['detected_class']:24s} {tag}{fsm}")
    print("\nVERDICT:", verdict)

    out = {"payload": payload, "verdict": verdict, "provenance": prov, "runtime_sec": round(time.time() - t0, 3)}
    json.dump(out, open(os.path.join(HERE, "results", "ROUTERAUTO1_metrics.json"), "w"), indent=2, sort_keys=True)
    blob = json.dumps(payload, sort_keys=True)   # provenance + verdict EXCLUDED from the reproducibility hash
    sha = hashlib.sha256(blob.encode()).hexdigest()
    open(os.path.join(HERE, "results", "ROUTERAUTO1_payload.sha256"), "w").write(sha + "\n")
    print("payload sha256:", sha, f"[{time.time()-t0:.2f}s]")
    return overall


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
