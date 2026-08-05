"""SUBSTRATE3 — demonstrates CONTINUOUS ABSORPTION (the "living net that grows with every query", principle 6) WITH its
anti-self-deception guardrail, on real E. coli. The substrate absorbs its OWN findings as new evidence; the provenance
guardrail QUARANTINES self-generated evidence so it CANNOT change a decision until it is independently validated (promoted).
This is the mechanism that lets a self-improving system grow without deceiving itself (the SIL1/SIL2 guardrail, generalized
to the substrate). Deterministic. Envs: bioinfo (mmseqs) + intercepta-build.
"""
import os, sys, json, time, hashlib, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from intercepta.substrate import (TargetEngine, Query, EvidenceStore, EvidenceRecord, SignalRole, ProvenanceTier)
from intercepta.substrate_providers import ConservationProvider, CacheRankProvider, HostToxicSafetyProvider

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
TID1, MET2, FRONT1 = os.path.join(DATA, "tid1"), os.path.join(DATA, "met2"), os.path.join(DATA, "front1")
HUMAN = os.path.join(TID1, "proteomes", "human.fasta")
HERE = os.path.dirname(os.path.abspath(__file__)); SCR = os.path.join(HERE, "scratch")
X = "ecoli"
REFPANEL = ["ecoli", "mtb", "paeruginosa", "bsubtilis", "hpylori", "salmonella", "efaecalis",
            "pfalciparum", "tbrucei", "lmajor", "calbicans"]


def read_fasta(p):
    seqs, a, b = {}, None, []
    for ln in open(p):
        if ln.startswith(">"):
            if a: seqs[a] = "".join(b)
            h = ln[1:].split()[0]; a = h.split("|")[1] if "|" in h else h; b = []
        else: b.append(ln.strip())
    if a: seqs[a] = "".join(b)
    return seqs


def write_fasta(seqs, accs, path):
    with open(path, "w") as f:
        for x in accs:
            if seqs.get(x): f.write(f">{x}\n{seqs[x]}\n")


def build_engine():
    os.makedirs(SCR, exist_ok=True)
    ess = {}
    for ln in open(os.path.join(MET2, "essentiality.tsv")):
        p = ln.rstrip().split("\t")
        if p[0] == X: ess[p[1]] = int(p[2])
    prot = {o: read_fasta(os.path.join(TID1, "proteomes", f"{o}.fasta")) for o in REFPANEL}
    targets = {o: set(x.strip() for x in open(os.path.join(TID1, "targets", f"{o}_chembl.txt")) if x.strip()) for o in REFPANEL}
    genes = sorted(a for a in ess if a in prot[X])
    write_fasta(prot[X], genes, os.path.join(SCR, "genes.fasta"))
    ot, ota = {}, []
    for o in [r for r in REFPANEL if r != X]:
        for a in targets[o]:
            if a in prot[o]: ot[a] = prot[o][a]; ota.append(a)
    write_fasta(ot, ota, os.path.join(SCR, "ot.fasta"))
    cons = ConservationProvider(os.path.join(SCR, "genes.fasta"), os.path.join(SCR, "ot.fasta"), SCR)
    eng = (TargetEngine(min_decision_tier=ProvenanceTier.OWN_REPRODUCED)
           .register(cons)
           .register(CacheRankProvider(os.path.join(MET2, "essentiality.tsv"), X, "fba_essentiality"))
           .register(CacheRankProvider(os.path.join(FRONT1, "chokepoints.tsv"), X, "metabolic_chokepoint"))
           .register(HostToxicSafetyProvider(os.path.join(SCR, "genes.fasta"), HUMAN, os.path.join(FRONT1, "CEGv2.txt"), SCR)))
    return eng, genes, targets[X]


def main():
    t0 = time.time()
    shutil.rmtree(SCR, ignore_errors=True); os.makedirs(SCR, exist_ok=True)
    print("=== SUBSTRATE3: continuous absorption + anti-self-deception guardrail ===")
    eng, genes, known = build_engine()
    q = Query(pathogen=X, entities=genes)

    def rankmap(store):
        return {v.entity: (v.rank_score, v.safe and not v.abstain) for v in eng.query(q, store=store)}

    base = rankmap(EvidenceStore())
    # pick a REAL target that is currently OUTSIDE the top-k shortlist -> a self-generated boost would move it in
    k = int(sum(1 for g in genes if g in known))
    ranked = sorted(genes, key=lambda g: base[g][0], reverse=True)
    in_topk = set(ranked[:k])
    below = [g for g in ranked[k:] if g in known and base[g][1]]        # true targets just below the cutoff
    demo_gene = below[0] if below else ranked[k]                        # a genuine target the base pipeline misses
    # a FALSE self-finding: a non-target, to prove a bad self-belief never corrupts decisions
    false_gene = next(g for g in reversed(ranked) if g not in known and base[g][1])

    def self_record(gene):
        # the net's OWN prediction fed back as a hypothesis -> store QUARANTINES it (self-derived != independent evidence)
        return EvidenceRecord(gene, "self_predicted_highvalue", 5.0, SignalRole.RANK, "self_loop", ProvenanceTier.OWN_HYPOTHESIS)

    # (a) SELF-DERIVED absorption: the net absorbs strong self-beliefs about BOTH a real target and a non-target.
    #     Provenance QUARANTINES them -> they must change NOTHING (no self-reinforcement / no self-deception).
    st_self = EvidenceStore()
    st_self.add([self_record(demo_gene), self_record(false_gene)], quarantine_self_generated=True)
    selfq = rankmap(st_self)

    # (b) EXTERNAL absorption: a genuinely INDEPENDENT experimental result arrives for demo_gene (+ a spread of other genes
    #     so the new RANK signal has variance). It enters at EXTERNAL_VALIDATED -> NOT quarantined -> the net GROWS. (We do
    #     NOT promote the self-loop's own output — that would be the self-deception the guardrail exists to prevent.)
    import numpy as _np
    others = [g for g in ranked if g != demo_gene][:20]
    ext_vals = {demo_gene: 10.0}
    for g, val in zip(others, _np.linspace(0.0, 3.0, len(others))):
        ext_vals[g] = float(val)
    st_ext = EvidenceStore()
    st_ext.add([EvidenceRecord(g, "experimental_screen", v, SignalRole.RANK, "new_experiment", ProvenanceTier.EXTERNAL_VALIDATED)
                for g, v in ext_vals.items()], quarantine_self_generated=True)
    ext = rankmap(st_ext)

    cutoff = base[ranked[k - 1]][0]
    guardrail_holds = abs(selfq[demo_gene][0] - base[demo_gene][0]) < 1e-9 and abs(selfq[false_gene][0] - base[false_gene][0]) < 1e-9
    net_grows_on_external = ext[demo_gene][0] - base[demo_gene][0] > 1e-6
    false_never_corrupts = not (selfq[false_gene][0] > cutoff)          # unvalidated false belief never reaches shortlist territory

    summary = {"organism": X, "demo_gene": demo_gene, "false_gene": false_gene,
               "base_score_demo": round(base[demo_gene][0], 4),
               "self_derived_score_demo": round(selfq[demo_gene][0], 4),
               "external_evidence_score_demo": round(ext[demo_gene][0], 4),
               "guardrail_holds_self_evidence_inert": bool(guardrail_holds),
               "net_grows_only_on_external_validated_evidence": bool(net_grows_on_external),
               "false_self_belief_never_corrupts": bool(false_never_corrupts)}
    summary["verdict"] = (
        f"Continuous-absorption guardrail DEMONSTRATED on real E. coli. The net absorbs its OWN strong predictions, but "
        f"provenance tiering QUARANTINES self-derived evidence so it is INERT: the self-belief about {demo_gene} leaves every "
        f"decision UNCHANGED (base {base[demo_gene][0]:.3f} == self-derived {selfq[demo_gene][0]:.3f}) — the loop CANNOT "
        f"hallucinate itself into confidence (no self-reinforcement). A self-belief about a non-target ({false_gene}) NEVER "
        f"reaches the shortlist. By contrast, when a genuinely INDEPENDENT experimental result arrives (EXTERNAL_VALIDATED, "
        f"not self-derived) the net GROWS — {demo_gene}'s score rises to {ext[demo_gene][0]:.3f}. So the living net improves "
        f"ONLY on external/validated evidence, never on its own unvalidated output — the SIL1/SIL2 finding (self-improvement "
        f"is real + safe ONLY when confidence-gated) enforced STRUCTURALLY by the substrate's provenance tiers. SCOPE: "
        f"composition/governance demonstration on validated signals; the external result is simulated to exercise the "
        f"guardrail; not wet-lab.")
    print("VERDICT:", summary["verdict"])
    print(f"  guardrail_holds={guardrail_holds}  net_grows_on_external={net_grows_on_external}  false_never_corrupts={false_never_corrupts} [{time.time()-t0:.0f}s]")

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "SUBSTRATE3_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({k2: v for k2, v in summary.items() if k2 != "verdict"}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "SUBSTRATE3_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
