"""ENGINE multi-axis demonstration on the SECOND held-out WHO pathogen A. baumannii (WHO #1 critical; never in development).
Runs the unified DiscoveryEngine genome->target report composing all validated signals, with A. baumannii-NATIVE resistance
(SYNLETH2) and condition-robustness (condrob_ab) — no E. coli transfer (AB is not Enterobacteriaceae). Annotates the shortlist
with DEG experimental essentiality (DEG1043). Deterministic; reproduced x2. Env: bioinfo (mmseqs providers).
"""
import os, sys, csv, json, time, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
from intercepta.discovery_engine import DiscoveryEngine

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
NB2, ENG, TID1, F1, SL = (os.path.join(DATA, "newbug2"), os.path.join(DATA, "engine"), os.path.join(DATA, "tid1"),
                          os.path.join(DATA, "front1"), os.path.join(DATA, "synleth"))
PROT = os.path.join(NB2, "abaumannii.fasta")


def acc2sym():
    m = {}
    for ln in open(PROT):
        if not ln.startswith(">"): continue
        acc = ln[1:].split()[0].split("|")[1] if "|" in ln else ln[1:].split()[0]
        for tok in ln.split():
            if tok.startswith("GN="): m[acc] = tok[3:]
    return m


def deg_ab_essential_syms():
    syms = set()
    p = os.path.join(DATA, "expval_deg", "deg_annotation_p.csv")
    if os.path.exists(p):
        for row in csv.reader(open(p, encoding="utf-8", errors="ignore"), delimiter=";"):
            if len(row) >= 3 and row[0].strip() == "DEG1043":
                g = row[2].strip()
                if g and g != "-": syms.add(g.lower())
    return syms


def main():
    t0 = time.time()
    eng = DiscoveryEngine.for_pathogen(
        "abaumannii", PROT, scratch=os.path.join(ENG, "scratch_ab"),
        essentiality_tsv=os.path.join(NB2, "essentiality.tsv"),
        chokepoint_tsv=os.path.join(NB2, "chokepoints.tsv"),
        breadth_tsv=os.path.join(ENG, "abaumannii_breadth.tsv"),
        reference_targets_fasta=os.path.join(ENG, "reference_targets.fasta"),
        human_fasta=os.path.join(TID1, "proteomes", "human.fasta"),
        ceg2_path=os.path.join(F1, "CEGv2.txt"),
        resistance_classes_tsv=os.path.join(SL, "abaumannii_resistance_classes.tsv"),   # AB-native (SYNLETH2)
        condition_robust_tsv=os.path.join(SL, "abaumannii_condition_robust.tsv"))        # AB-native (condrob_ab)
    rep = eng.report(top=30)
    a2s = acc2sym(); val = deg_ab_essential_syms()
    for row in rep["shortlist"]:
        sym = a2s.get(row["entity"], ""); row["gene"] = sym
        row["deg_experimentally_essential"] = (sym.lower() in val) if sym else None
    n_val = sum(1 for r in rep["shortlist"] if r.get("deg_experimentally_essential"))
    rep["shortlist_deg_experimentally_essential"] = n_val
    print("=== INTERCEPTA DiscoveryEngine — held-out A. baumannii (WHO #1 critical) ===")
    print("active signals:", rep["active_signals"])
    print("confidence histogram:", rep["confidence_histogram"])
    print(f"excluded by safety (host-toxic): {rep['n_excluded_by_safety']} | abstained: {rep['n_abstained']} | "
          f"confident safe targets: {rep['n_confident_safe_targets']}")
    print(f"resistance (AB-native): monotherapy-robust {rep.get('n_monotherapy_robust')} | combination-required {rep.get('n_combination_required')}")
    print(f"condition-robust (AB-native): {rep.get('n_condition_robust')}")
    print(f"of top {len(rep['shortlist'])} shortlist, DEG-experimentally-essential: {n_val}")
    print("\nTOP TARGETS (gene | conf | rank | DEG-ess | flags):")
    for r in rep["shortlist"][:20]:
        ee = "DEG-ESS" if r.get("deg_experimentally_essential") else ("-" if r.get("deg_experimentally_essential") is False else "?")
        print(f"  {r.get('gene','?'):8s} {r['confidence']:8s} {r['rank_score']:+.3f}  {ee:8s} {','.join(r['flags']) if r['flags'] else ''}")
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump({"report": rep, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)},
              open(os.path.join(HERE, "results", "ENGINE_ab_report.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({k: v for k, v in rep.items() if k != "honest_scope"}, sort_keys=True)
    open(os.path.join(HERE, "results", "ENGINE_ab_payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    print("\npayload sha256:", hashlib.sha256(payload.encode()).hexdigest(), f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
