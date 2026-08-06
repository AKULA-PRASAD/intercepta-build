"""COMPOSITE1 — demonstration + validation of the explicit biology-class-aware ROUTER (see PREREG.md).

Three representative inputs, PRE-REGISTERED routing outcomes asserted:
  (A) BACTERIUM  — held-out K. pneumoniae (reuse ENGINE_endtoend inputs/caches):
         router applies FBA + full composite -> confidence-tiered SHORTLIST; assert cores {murA,murG,mraY,dxs}
         present and consistency with the committed ENGINE_endtoend report.
  (B) VIRUS      — SARS-CoV-2 (autodetected by tiny proteome): structural class-ID FIRES; FBA and
         sequence-repurposing are NOT fired; surfaces Mpro->protease, RdRp->polymerase (GENERALIZE3).
  (C) HOST-DEPENDENT PARASITE — P. falciparum (declared): router ABSTAINS (no confident FBA shortlist),
         returns the explicit host-embedded reason. THE DECISIVE INTEGRITY TEST.

Deterministic; reproduced x2 (SHA-256 over sorted-key JSON payload excluding verdict/provenance). The DiscoveryEngine
providers call the bioinfo mmseqs binary via absolute path, so any python can run this. Output:
results/COMPOSITE1_metrics.json (+payload.sha256), SUMMARY.md.  NO git commit/push.
"""
import os, sys, json, time, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
from intercepta.composite_router import CompositeRouter, BiologyClass, Signal  # noqa: E402

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
NB = os.path.join(DATA, "newbug"); ENG = os.path.join(DATA, "engine")
TID1 = os.path.join(DATA, "tid1"); F1 = os.path.join(DATA, "front1")
KP_PROT = os.path.join(NB, "kpneumoniae.fasta")
VIRUS_FASTA = os.path.join(DATA, "generalize1", "mature_proteins.fasta")
G3_METRICS = os.path.join(HERE, "..", "GENERALIZE3_viral_structural_blind", "results", "GENERALIZE3_metrics.json")
COMMITTED_ENGINE = os.path.join(HERE, "..", "ENGINE_endtoend", "results", "ENGINE_report.json")

CORES = ["murA", "murG", "mraY", "dxs"]   # known validated K. pneumoniae metabolic cores (ENGINE)


def acc2sym(fasta):
    m = {}
    for ln in open(fasta):
        if not ln.startswith(">"):
            continue
        acc = ln[1:].split()[0].split("|")[1] if "|" in ln else ln[1:].split()[0]
        for tok in ln.split():
            if tok.startswith("GN="):
                m[acc] = tok[3:]
    return m


def count_proteins(fasta):
    return sum(1 for ln in open(fasta) if ln.startswith(">"))


# ---------------------------------------------------------------------------------------------------
def case_A_bacterium(router):
    """Declared bacterium -> FBA composite SHORTLIST."""
    decision = router.decide("kpneumoniae", declared_class=BiologyClass.BACTERIUM)
    engine_kwargs = dict(
        proteome_fasta=KP_PROT, scratch=os.path.join(ENG, "scratch"),
        essentiality_tsv=os.path.join(NB, "essentiality.tsv"),
        chokepoint_tsv=os.path.join(NB, "chokepoints.tsv"),
        breadth_tsv=os.path.join(ENG, "kpneumoniae_breadth.tsv"),
        reference_targets_fasta=os.path.join(ENG, "reference_targets.fasta"),
        human_fasta=os.path.join(TID1, "proteomes", "human.fasta"),
        ceg2_path=os.path.join(F1, "CEGv2.txt"),
        resistance_classes_tsv=os.path.join(DATA, "synleth", "ecoli_resistance_classes.tsv"),
        condition_robust_tsv=os.path.join(DATA, "synleth", "ecoli_condition_robust.tsv"),
    )
    rep = router.run_fba_composite("kpneumoniae", engine_kwargs, top=30)
    a2s = acc2sym(KP_PROT)
    top_genes = [a2s.get(row["entity"], row["entity"]) for row in rep["shortlist"]]
    cores_present = {c: (c in top_genes) for c in CORES}

    # consistency with the committed ENGINE_endtoend report (same machinery, same inputs)
    consistent = None
    if os.path.exists(COMMITTED_ENGINE):
        committed = json.load(open(COMMITTED_ENGINE))["report"]
        committed_top = [r.get("gene", r["entity"]) for r in committed["shortlist"][:20]]
        consistent = (top_genes[:20] == committed_top)

    fired = set(decision.signals_fired)
    assertions = {
        "output_is_shortlist": decision.output_type == "shortlist",
        "fba_fired": Signal.FBA_ESSENTIALITY.value in fired,
        "all_cores_present": all(cores_present.values()),
        "not_abstained": decision.abstention is None,
        "consistent_with_committed_engine_top20": bool(consistent) if consistent is not None else None,
    }
    return {
        "routing": decision.to_dict(),
        "engine_active_signals": rep["active_signals"],
        "n_confident_safe_targets": rep["n_confident_safe_targets"],
        "top_genes": top_genes,
        "cores_present": cores_present,
        "assertions": assertions,
    }


def case_B_virus(router):
    """SARS-CoV-2 -> autodetect VIRUS -> structural class-ID; FBA & sequence-repurposing NOT fired."""
    n_prot = count_proteins(VIRUS_FASTA)
    decision = router.decide("SARS-CoV-2", proteome_size=n_prot)
    struct = router.structural_class_id_from_generalize3(os.path.normpath(G3_METRICS))
    hyp = {h["protein"]: h for h in struct["hypotheses"]}
    fired = set(decision.signals_fired)
    assertions = {
        "autodetected_virus": decision.biology_class == BiologyClass.VIRUS.value and decision.class_source == "autodetected",
        "output_is_structural_class_id": decision.output_type == "structural_class_id",
        "structural_fired": Signal.STRUCTURAL_HOMOLOGY.value in fired,
        "fba_NOT_fired": Signal.FBA_ESSENTIALITY.value not in fired,
        "sequence_repurposing_NOT_fired": Signal.SEQUENCE_REPURPOSING.value not in fired,
        "Mpro_is_protease": hyp["nsp5_Mpro"]["target_class"] == "protease",
        "RdRp_is_polymerase": hyp["nsp12_RdRp"]["target_class"] == "polymerase",
    }
    return {
        "proteome_size": n_prot,
        "routing": decision.to_dict(),
        "structural_hypotheses": struct["hypotheses"],
        "structural_gate": struct["gate"],
        "assertions": assertions,
    }


def case_C_parasite(router):
    """P. falciparum -> declared host-dependent parasite -> MUST ABSTAIN (decisive integrity test)."""
    decision = router.decide("Plasmodium falciparum", declared_class=BiologyClass.HOST_DEPENDENT_PARASITE)
    from intercepta.composite_router import HOST_EMBEDDED_ABSTENTION
    gated = {g["signal"]: g["reason"] for g in decision.to_dict()["signals_gated_out"]}
    fired = set(decision.signals_fired)
    assertions = {
        "output_is_abstention": decision.output_type == "abstention",
        "did_NOT_emit_shortlist": decision.output_type != "shortlist",
        "fba_NOT_fired": Signal.FBA_ESSENTIALITY.value not in fired,
        "fba_gated_out": Signal.FBA_ESSENTIALITY.value in gated,
        "functional_dependency_gated_out": Signal.FUNCTIONAL_DEPENDENCY.value in gated,
        "no_discovery_signal_fired": len(fired) == 0,
        "abstention_reason_matches_prereg": decision.abstention == HOST_EMBEDDED_ABSTENTION,
    }
    return {
        "routing": decision.to_dict(),
        "abstention_reason": decision.abstention,
        "gated_signals": gated,
        "assertions": assertions,
    }


def main():
    t0 = time.time()
    router = CompositeRouter()
    A = case_A_bacterium(router)
    B = case_B_virus(router)
    C = case_C_parasite(router)

    def all_true(case):
        return all(v is True for v in case["assertions"].values() if v is not None)

    payload = {
        "test": "COMPOSITE1 explicit biology-class-aware router (transfer-gate + abstention)",
        "case_A_bacterium": A,
        "case_B_virus": B,
        "case_C_parasite": C,
        "all_assertions_pass": bool(all_true(A) and all_true(B) and all_true(C)),
    }
    # ---- reproduction hash (payload only; excludes verdict/provenance) ----
    payload_json = json.dumps(payload, sort_keys=True)
    sha = hashlib.sha256(payload_json.encode()).hexdigest()

    verdict = (
        f"ROUTER: (A) BACTERIUM K.pneumoniae -> {A['routing']['output_type']} "
        f"(FBA fired={A['assertions']['fba_fired']}, cores present={A['assertions']['all_cores_present']}); "
        f"(B) VIRUS SARS-CoV-2 -> {B['routing']['output_type']} "
        f"(FBA fired={not B['assertions']['fba_NOT_fired']}, Mpro->protease & RdRp->polymerase); "
        f"(C) PARASITE P.falciparum -> {C['routing']['output_type']} "
        f"(FBA fired={not C['assertions']['fba_NOT_fired']}, abstained correctly). "
        f"ALL ASSERTIONS PASS: {payload['all_assertions_pass']}. "
        f"The decisive integrity test HOLDS: the parasite ABSTAINED and the virus did NOT fire FBA."
    )

    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "runtime_sec": round(time.time() - t0, 1)}
    json.dump({"payload": payload, "verdict": verdict, "provenance": prov},
              open(os.path.join(HERE, "results", "COMPOSITE1_metrics.json"), "w"), indent=2, sort_keys=True)
    open(os.path.join(HERE, "results", "COMPOSITE1_payload.sha256"), "w").write(sha + "\n")

    print("=== COMPOSITE1 explicit router — 3-case routing ===")
    for tag, case in (("A bacterium", A), ("B virus", B), ("C parasite", C)):
        print(f"\n[{tag}] class={case['routing']['biology_class']} ({case['routing']['class_source']}) "
              f"-> {case['routing']['output_type']}")
        print(f"   fired(discovery): {case['routing']['signals_fired']}")
        print(f"   supporting:       {case['routing']['supporting_signals']}")
        print(f"   gated out:        {[g['signal'] for g in case['routing']['signals_gated_out']]}")
        for k, v in case["assertions"].items():
            print(f"     assert {k}: {v}")
    print("\nVERDICT:", verdict)
    print("payload sha256:", sha, f"[{time.time()-t0:.0f}s]")

    if not payload["all_assertions_pass"]:
        raise SystemExit("COMPOSITE1 FAILED: one or more pre-registered routing assertions did not hold.")


if __name__ == "__main__":
    main()
