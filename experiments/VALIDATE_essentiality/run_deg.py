"""VALIDATE_essentiality (A. baumannii + P. aeruginosa, via DEG) — extends the experimental validation to TWO more ESKAPE
pathogens, including the SECOND held-out NEWBUG pathogen (A. baumannii). Ground truth = DEG (Database of Essential Genes)
bulk download: A. baumannii ATCC 17978 (DEG1043, Wang 2014 INSeq, 458 essential) and P. aeruginosa PAO1 (DEG1036, Turner
2015 Tn-seq, 336 essential). Compared against OUR FBA essentiality (A. baumannii = NEWBUG2 held-out GEM; P. aeruginosa =
MET2 panel GEM). Map via gene symbol (DEG strains differ from our proteomes -> symbol is the robust key). Same 2x2 Fisher +
growth-ratio AUROC + OR>3/p<0.01 gate as E. coli/Mtb/K. pneumoniae. Deterministic; reproduced x2. Env: intercepta-build.
"""
import os, sys, csv, json, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
DEG_ANN = os.path.join(DATA, "expval_deg", "deg_annotation_p.csv")

CONFIG = {
    "abaumannii": {"fba": os.path.join(DATA, "newbug2", "essentiality.tsv"), "org_key": "abaumannii",
                   "proteome": os.path.join(DATA, "newbug2", "abaumannii.fasta"), "deg": "DEG1043", "held_out": True},
    "paeruginosa": {"fba": os.path.join(DATA, "met2", "essentiality.tsv"), "org_key": "paeruginosa",
                    "proteome": os.path.join(DATA, "tid1", "proteomes", "paeruginosa.fasta"), "deg": "DEG1036", "held_out": False},
}


def acc2sym(path):
    m = {}
    for ln in open(path):
        if not ln.startswith(">"): continue
        acc = ln[1:].split()[0].split("|")[1] if "|" in ln else ln[1:].split()[0]
        for tok in ln.split():
            if tok.startswith("GN="): m[acc] = tok[3:].lower()
    return m


def deg_essential_syms(deg_acc):
    syms = set()
    with open(DEG_ANN, encoding="utf-8", errors="ignore") as f:
        for row in csv.reader(f, delimiter=";"):
            if len(row) >= 3 and row[0].strip() == deg_acc:
                g = row[2].strip()
                if g and g != "-": syms.add(g.lower())
    return syms


def analyze(cfg):
    ess, growth = {}, {}
    for ln in open(cfg["fba"]):
        p = ln.rstrip().split("\t")
        if len(p) >= 3 and p[0] == cfg["org_key"]:
            ess[p[1]] = int(p[2])
            try: growth[p[1]] = float(p[3])
            except Exception: growth[p[1]] = 1.0
    a2s = acc2sym(cfg["proteome"])
    deg_syms = deg_essential_syms(cfg["deg"])
    genes = [g for g in ess if g in a2s]                          # adjudicable = has a gene symbol
    exp_ess = set(g for g in genes if a2s[g] in deg_syms)
    a = sum(1 for g in genes if ess[g] == 1 and g in exp_ess)
    b = sum(1 for g in genes if ess[g] == 1 and g not in exp_ess)
    c = sum(1 for g in genes if ess[g] == 0 and g in exp_ess)
    d = sum(1 for g in genes if ess[g] == 0 and g not in exp_ess)
    try:
        from scipy.stats import fisher_exact
        orr, p_fisher = fisher_exact([[a, b], [c, d]], alternative="greater")
    except Exception:
        orr = (a * d) / max(b * c, 1); p_fisher = float("nan")
    try:
        from sklearn.metrics import roc_auc_score
        y = [1 if g in exp_ess else 0 for g in genes]; sc = [-growth[g] for g in genes]
        auroc = float(roc_auc_score(y, sc)) if 0 < sum(y) < len(y) else float("nan")
    except Exception:
        auroc = float("nan")
    prec = a / (a + b) if (a + b) else float("nan")
    rec = a / (a + c) if (a + c) else float("nan")
    return {"deg_source": cfg["deg"], "held_out": cfg["held_out"], "deg_essential_syms": len(deg_syms),
            "n_our_genes": len(ess), "n_adjudicable": len(genes), "n_experimental_essential": len(exp_ess),
            "contingency": {"both": a, "FBA_only": b, "exp_only": c, "neither": d},
            "precision_FBAess": round(prec, 3) if prec == prec else None,
            "recall_FBAess": round(rec, 3) if rec == rec else None,
            "odds_ratio": round(float(orr), 2), "fisher_p": (round(float(p_fisher), 8) if p_fisher == p_fisher else None),
            "auroc": round(auroc, 4) if auroc == auroc else None,
            "H1_OR_gt3_p_lt0.01": bool((orr > 3) and (p_fisher < 0.01 if p_fisher == p_fisher else False))}


def main():
    t0 = time.time()
    res = {o: analyze(cfg) for o, cfg in CONFIG.items()}
    for o, r in res.items():
        print(f"  [{o}] held_out={r['held_out']} DEG={r['deg_source']} | OR {r['odds_ratio']} (p={r['fisher_p']}) "
              f"precision {r['precision_FBAess']} recall {r['recall_FBAess']} AUROC {r['auroc']} | adjudicable {r['n_adjudicable']}")
    allpass = all(r["H1_OR_gt3_p_lt0.01"] for r in res.values())
    summary = {"organisms": res, "all_pass_gate": bool(allpass)}
    ab, pa = res["abaumannii"], res["paeruginosa"]
    if allpass:
        summary["verdict"] = (f"BOTH ESKAPE pathogens VALIDATE — extends the experimental validation to a FOURTH and FIFTH organism, "
                              f"incl. the SECOND held-out NEWBUG pathogen. A. baumannii (HELD-OUT, DEG1043 Wang-2014 INSeq): FBA-essential "
                              f"enriched for experimental essential at OR {ab['odds_ratio']} (p={ab['fisher_p']}), precision {ab['precision_FBAess']}. "
                              f"P. aeruginosa (panel, DEG1036 Turner-2015 Tn-seq): OR {pa['odds_ratio']} (p={pa['fisher_p']}), precision "
                              f"{pa['precision_FBAess']}. So the mechanism signal now validates against experiment in FIVE organisms — E. coli, "
                              f"Mtb, and THREE ESKAPE pathogens (K. pneumoniae + A. baumannii held-out, P. aeruginosa) — with TWO of them "
                              f"genuinely held out of development. HONEST BOUNDS: binary enrichment (precision high, recall {ab['recall_FBAess']}/"
                              f"{pa['recall_FBAess']} — FBA metabolic-scoped); AUROC modest ({ab['auroc']}/{pa['auroc']}); symbol-mapping coverage "
                              f"(adjudicable {ab['n_adjudicable']}/{pa['n_adjudicable']}, skews to named core genes); DEG A. baumannii is a "
                              f"lung-persistence INSeq set (condition-specific); essentiality only, not drug-target/clinical.")
    else:
        summary["verdict"] = (f"MIXED/does-not-fully-validate: A. baumannii OR {ab['odds_ratio']} (p={ab['fisher_p']}), P. aeruginosa OR "
                              f"{pa['odds_ratio']} (p={pa['fisher_p']}). Reported plainly (H1 gate not met for at least one).")
    print("\nPANEL:", json.dumps(summary["organisms"], indent=1))
    print("VERDICT:", summary["verdict"])
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "VALIDATE_essentiality_deg.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps(summary["organisms"], sort_keys=True)
    open(os.path.join(HERE, "results", "VALIDATE_deg_payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    print("payload sha256:", hashlib.sha256(payload.encode()).hexdigest(), f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
