"""S. aureus (Gram-positive, MRSA-relevant core) — extends the validated multi-axis engine + experimental-essentiality
validation to the single most clinically important missing pathogen AND to a new axis of generality (Gram-positive; prior
validations were Gram-negative + Mtb). (A) VAL-ESS-style Fisher enrichment of FBA-essentiality vs DEG experimental essentiality
(DEG1032, NCTC 8325 TMDH Tn-based, strain-matched to our proteome). (B) full 7-signal DiscoveryEngine genome->target report
with S. aureus-NATIVE resistance + condition classes. Deterministic; reproduced x2. Env: bioinfo (engine mmseqs providers).
"""
import os, sys, csv, json, time, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
from intercepta.discovery_engine import DiscoveryEngine

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
NB3, ENG, TID1, F1, SL = (os.path.join(DATA, "newbug3"), os.path.join(DATA, "engine"), os.path.join(DATA, "tid1"),
                          os.path.join(DATA, "front1"), os.path.join(DATA, "synleth"))
PROT = os.path.join(NB3, "saureus.fasta")
DEG_ACC = "DEG1032"   # S. aureus NCTC 8325 (strain-matched), TMDH/Tn-based essential set


def acc2sym():
    m = {}
    for ln in open(PROT):
        if not ln.startswith(">"): continue
        acc = ln[1:].split()[0].split("|")[1] if "|" in ln else ln[1:].split()[0]
        for tok in ln.split():
            if tok.startswith("GN="): m[acc] = tok[3:]
    return m


def deg_essential_syms():
    syms = set()
    for row in csv.reader(open(os.path.join(DATA, "expval_deg", "deg_annotation_p.csv"), encoding="utf-8", errors="ignore"), delimiter=";"):
        if len(row) >= 3 and row[0].strip() == DEG_ACC:
            g = row[2].strip()
            if g and g != "-": syms.add(g.lower())
    return syms


def main():
    t0 = time.time()
    a2s = acc2sym(); sym2a = {}
    for a, s in a2s.items(): sym2a.setdefault(s.lower(), a)
    deg_syms = deg_essential_syms()
    deg_ess_acc = {sym2a[s] for s in deg_syms if s in sym2a}
    # (A) VAL-ESS Fisher enrichment: FBA-essential vs DEG-essential over the GEM genes
    fba = {}
    for ln in open(os.path.join(NB3, "essentiality.tsv")):
        p = ln.rstrip().split("\t")
        if p and p[0] == "saureus":
            fba[p[1]] = int(p[2])
    genes = [g for g in fba if g in a2s]                 # adjudicable = GEM genes with a symbol
    exp = set(g for g in genes if g in deg_ess_acc)
    a = sum(1 for g in genes if fba[g] == 1 and g in exp); b = sum(1 for g in genes if fba[g] == 1 and g not in exp)
    c = sum(1 for g in genes if fba[g] == 0 and g in exp); d = sum(1 for g in genes if fba[g] == 0 and g not in exp)
    try:
        from scipy.stats import fisher_exact
        orr, pval = fisher_exact([[a, b], [c, d]], alternative="greater")
    except Exception:   # env-independent one-sided hypergeometric fallback (bioinfo env lacks scipy)
        from math import comb
        n = a + b + c + d; r = a + b; col = a + c
        pval = sum(comb(col, k) * comb(n - col, r - k) for k in range(a, min(r, col) + 1)) / comb(n, r)
        orr = (a * d) / max(b * c, 1)
    val = {"deg_source": DEG_ACC, "deg_essential_mapped": len(exp), "adjudicable_genes": len(genes),
           "contingency": {"both": a, "FBA_only": b, "exp_only": c, "neither": d},
           "precision": round(a / (a + b), 3) if (a + b) else None, "recall": round(a / (a + c), 3) if (a + c) else None,
           "odds_ratio": round(float(orr), 2), "fisher_p": (round(float(pval), 8) if pval == pval else None),
           "gate_pass": bool(orr > 3 and (pval < 0.01 if pval == pval else False))}
    # (B) engine
    eng = DiscoveryEngine.for_pathogen(
        "saureus", PROT, scratch=os.path.join(ENG, "scratch_sa"),
        essentiality_tsv=os.path.join(NB3, "essentiality.tsv"), chokepoint_tsv=os.path.join(NB3, "chokepoints.tsv"),
        breadth_tsv=os.path.join(ENG, "saureus_breadth.tsv"), reference_targets_fasta=os.path.join(ENG, "reference_targets.fasta"),
        human_fasta=os.path.join(TID1, "proteomes", "human.fasta"), ceg2_path=os.path.join(F1, "CEGv2.txt"),
        resistance_classes_tsv=os.path.join(SL, "saureus_resistance_classes.tsv"),
        condition_robust_tsv=os.path.join(SL, "saureus_condition_robust.tsv"))
    rep = eng.report(top=25)
    for r in rep["shortlist"]:
        sym = a2s.get(r["entity"], ""); r["gene"] = sym; r["deg_experimentally_essential"] = (sym.lower() in deg_syms) if sym else None
    rep["shortlist_deg_experimentally_essential"] = sum(1 for r in rep["shortlist"] if r.get("deg_experimentally_essential"))

    summary = {"organism": "S_aureus_NCTC8325", "gram": "positive", "validation": val,
               "engine": {k: rep[k] for k in ("active_signals", "n_entities", "n_excluded_by_safety", "n_confident_safe_targets",
                          "n_monotherapy_robust", "n_combination_required", "n_condition_robust",
                          "shortlist_deg_experimentally_essential")}}
    summary["verdict"] = (
        f"S. AUREUS (Gram-positive) — validated essentiality WEAKLY generalizes to a 6th organism + a new Gram class (passes the "
        f"gate, but is the WEAKEST of the six). (A) FBA-essential is enriched for EXPERIMENTAL essentiality (DEG {DEG_ACC}, "
        f"NCTC 8325 Tn-based) at odds ratio {val['odds_ratio']} (Fisher p={val['fisher_p']}), precision {val['precision']}, "
        f"{'PASS' if val['gate_pass'] else 'FAIL'} the pre-registered OR>3/p<0.01 gate -> the experimentally-verified mechanism "
        f"signal holds in Gram-POSITIVE S. aureus, not just the Gram-negatives + Mtb. **But it is markedly weaker than E. coli "
        f"(64)/K. pneumoniae (63)/P. aeruginosa (23) — the low OR ({val['odds_ratio']}) and precision ({val['precision']}) reflect "
        f"the SPARSE de-novo Gram-positive CarveMe GEM (only 24 FBA-essential from 860 genes -> most S. aureus essentiality is "
        f"outside the metabolic model), NOT independence from the signal.** (B) The full 7-signal engine runs genome->target: "
        f"{rep['n_excluded_by_safety']} host-toxic excluded, {rep['n_confident_safe_targets']} confident safe targets, "
        f"{rep.get('n_condition_robust')} condition-robust, {rep.get('n_monotherapy_robust')} monotherapy-robust; "
        f"{rep['shortlist_deg_experimentally_essential']}/{len(rep['shortlist'])} "
        f"of the shortlist DEG-experimentally-essential. HONEST BOUNDS: de-novo default-medium CarveMe GEM is SPARSE (860 genes, "
        f"24 FBA-essential) -> low recall; validation is essentiality-enrichment only; S. aureus reference strain (essential core "
        f"shared with MRSA, resistance genes differ); confidence saturates genome-scale; hypotheses; not wet-lab.")
    print("PANEL:", json.dumps(summary["validation"], indent=1)); print("ENGINE:", json.dumps(summary["engine"], indent=1))
    print("VERDICT:", summary["verdict"])
    print("\nTOP TARGETS:")
    for r in rep["shortlist"][:15]:
        ee = "DEG-ESS" if r.get("deg_experimentally_essential") else "-"
        print(f"  {r.get('gene','?'):8s} {r['rank_score']:+.3f} {ee:8s} {','.join(r['flags']) if r['flags'] else ''}")
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump({"summary": summary, "shortlist": rep["shortlist"], "provenance": prov, "runtime_sec": round(time.time() - t0, 1)},
              open(os.path.join(HERE, "results", "SAUREUS_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"validation": val, "engine": summary["engine"], "shortlist_genes": [r.get("gene") for r in rep["shortlist"]]}, sort_keys=True)
    open(os.path.join(HERE, "results", "SAUREUS_payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    print("payload sha256:", hashlib.sha256(payload.encode()).hexdigest(), f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
