"""ENGINE end-to-end demonstration — runs the unified DiscoveryEngine on the HELD-OUT WHO pathogen K. pneumoniae
(never in development), genome -> full honest target report, composing every validated signal (essentiality[VALIDATED],
chokepoint, conservation, REACH1 breadth, hard host-safety filter, calibrated confidence, abstention). Annotates the
shortlist with gene symbols and marks which top targets are EXPERIMENTALLY essential (PREDVAL/VAL-ESS-KP). Deterministic;
reproduced x2. Env: bioinfo (the safety/conservation providers call mmseqs). Output: results/ENGINE_report.json.
"""
import os, sys, json, time, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
from intercepta.discovery_engine import DiscoveryEngine

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
NB, ENG, TID1, F1 = os.path.join(DATA, "newbug"), os.path.join(DATA, "engine"), os.path.join(DATA, "tid1"), os.path.join(DATA, "front1")
PROT = os.path.join(NB, "kpneumoniae.fasta")


def acc2sym():
    m = {}
    for ln in open(PROT):
        if not ln.startswith(">"): continue
        acc = ln[1:].split()[0].split("|")[1] if "|" in ln else ln[1:].split()[0]
        for tok in ln.split():
            if tok.startswith("GN="): m[acc] = tok[3:]
    return m


def main():
    t0 = time.time()
    eng = DiscoveryEngine.for_pathogen(
        "kpneumoniae", PROT, scratch=os.path.join(ENG, "scratch"),
        essentiality_tsv=os.path.join(NB, "essentiality.tsv"),
        chokepoint_tsv=os.path.join(NB, "chokepoints.tsv"),
        breadth_tsv=os.path.join(ENG, "kpneumoniae_breadth.tsv"),
        reference_targets_fasta=os.path.join(ENG, "reference_targets.fasta"),
        human_fasta=os.path.join(TID1, "proteomes", "human.fasta"),
        ceg2_path=os.path.join(F1, "CEGv2.txt"))
    rep = eng.report(top=30)
    a2s = acc2sym()
    # experimentally-validated essential symbols (PREDVAL/VAL-ESS-KP source): K. pneumoniae experimental essential set
    val_syms = set()
    kp = os.path.join(DATA, "expval_kp", "kp_ess.csv")
    if os.path.exists(kp):
        import csv
        for r in csv.DictReader(open(kp)):
            if str(r.get("experimentally_essential", "")).strip().lower() == "true":
                g = (r.get("gene") or "").strip()
                if g and not g.startswith(("KPHS_", "KPN_")): val_syms.add(g.lower())
    for row in rep["shortlist"]:
        sym = a2s.get(row["entity"], "")
        row["gene"] = sym
        row["experimentally_essential_kp"] = (sym.lower() in val_syms) if sym else None
    n_val = sum(1 for r in rep["shortlist"] if r.get("experimentally_essential_kp"))
    rep["shortlist_experimentally_essential_confirmed"] = n_val
    print("=== INTERCEPTA DiscoveryEngine — held-out K. pneumoniae ===")
    print("active signals:", rep["active_signals"])
    print("confidence histogram:", rep["confidence_histogram"])
    print(f"excluded by safety (host-toxic): {rep['n_excluded_by_safety']} | abstained: {rep['n_abstained']} | "
          f"confident safe targets: {rep['n_confident_safe_targets']}")
    print(f"of top {len(rep['shortlist'])} shortlist, experimentally-essential-confirmed: {n_val}")
    print("\nTOP TARGETS (gene | confidence | rank | exp-essential | flags):")
    for r in rep["shortlist"][:20]:
        ee = "EXP-ESS" if r.get("experimentally_essential_kp") else ("-" if r.get("experimentally_essential_kp") is False else "?")
        print(f"  {r.get('gene','?'):8s} {r['confidence']:8s} {r['rank_score']:+.3f}  {ee:8s} {','.join(r['flags']) if r['flags'] else ''}")
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"report": rep, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "ENGINE_report.json"), "w"), indent=2, sort_keys=True)
    # deterministic payload = the report minus free-text scope + rank floats rounded already
    payload = json.dumps({k: v for k, v in rep.items() if k != "honest_scope"}, sort_keys=True)
    open(os.path.join(HERE, "results", "ENGINE_payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    print("\npayload sha256:", hashlib.sha256(payload.encode()).hexdigest(), f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
