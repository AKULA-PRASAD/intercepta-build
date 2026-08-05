"""VALIDATE_essentiality (K. pneumoniae, HELD-OUT) — the strongest generalization test: does the experimental validation
of FBA-essentiality hold on a pathogen the method NEVER SAW during development? K. pneumoniae is a WHO critical-priority
pathogen used in the NEWBUG held-out demonstration (never in the 7-organism development panel). Here we test its NEWBUG
FBA-essentiality predictions against INDEPENDENT EXPERIMENTAL essentiality (published K. pneumoniae CRISPRi / Tn-seq,
aggregated in ersilia-os/gradi-target-prioritization: kp_essentiality.csv `experimentally_essential`).

CRITICAL (no circularity): the source table ALSO contains its OWN fba columns — we IGNORE those entirely and use ONLY its
EXPERIMENTAL label, compared against OUR NEWBUG FBA essentiality (newbug/essentiality.tsv). We also VERIFY the experimental
label is experiment-only (not contaminated by ortholog-transfer / predictors) before trusting it. Map via gene symbol
(different strain proteome versions -> zero direct-accession overlap). Same analysis + gate as E. coli/Mtb. Reproduced x2.
Env: intercepta-build.
"""
import os, sys, csv, json, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
NEWBUG = os.path.join(DATA, "newbug")
KP = os.path.join(DATA, "expval_kp")


def is_locus_tag(g):
    g = (g or "").strip()
    return (not g) or g.startswith(("KPHS_", "KPN_", "KPNIH", "A6T", "gene-")) or g.isupper() and "_" in g


def main():
    t0 = time.time()
    # OUR NEWBUG FBA essentiality (held-out K. pneumoniae)
    ess, growth = {}, {}
    for ln in open(os.path.join(NEWBUG, "essentiality.tsv")):
        p = ln.rstrip().split("\t")
        if p and p[0] == "kpneumoniae":
            ess[p[1]] = int(p[2])
            try: growth[p[1]] = float(p[3])
            except Exception: growth[p[1]] = 1.0
    # acc -> gene symbol from OUR NEWBUG proteome
    acc2sym = {}
    for ln in open(os.path.join(NEWBUG, "kpneumoniae.fasta")):
        if not ln.startswith(">"): continue
        acc = ln[1:].split()[0].split("|")[1] if "|" in ln else ln[1:].split()[0]
        for tok in ln.split():
            if tok.startswith("GN="): acc2sym[acc] = tok[3:].lower()
    # EXPERIMENTAL essentiality (symbol -> essential), experiment-only, from the ersilia aggregation
    sym_exp_ess, sym_seen = set(), set()
    contamination = 0
    with open(os.path.join(KP, "kp_ess.csv")) as f:
        for r in csv.DictReader(f):
            g = (r.get("gene") or "").strip().lower()
            if is_locus_tag(r.get("gene")): continue
            sym_seen.add(g)
            exp = str(r.get("experimentally_essential", "")).strip().lower() == "true"
            # verify experiment-only: experimentally_essential should be backed by an experimental evidence field
            exp_backed = any(str(r.get(c, "")).strip() not in ("", "0", "0.0", "False", "false", "None")
                             for c in ("evidence_experimental", "kp_ess_in_vitro_call", "kp_ess_urine_call",
                                       "kp_ess_serum_call", "crispri_ce_library", "kpnih1_essential", "kp_ess_sources"))
            if exp and not exp_backed: contamination += 1
            if exp and exp_backed: sym_exp_ess.add(g)
    # map OUR genes -> experimental via symbol
    genes = [g for g in ess if g in acc2sym and acc2sym[g] in sym_seen]  # only genes we can adjudicate
    exp_ess = set(g for g in genes if acc2sym[g] in sym_exp_ess)
    matched = len(exp_ess)
    print(f"=== VALIDATE_essentiality (K. pneumoniae, HELD-OUT) : NEWBUG FBA vs experimental (ersilia CRISPRi/Tn-seq) ===")
    print(f"  our NEWBUG KP genes {len(ess)}; adjudicable (symbol in experimental table) {len(genes)}; experimental-essential among them {matched}")
    print(f"  contamination check (experimentally_essential=True but NO experimental evidence field): {contamination} -> excluded")
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
        y = [1 if g in exp_ess else 0 for g in genes]; score = [-growth[g] for g in genes]
        auroc = float(roc_auc_score(y, score)) if 0 < sum(y) < len(y) else float("nan")
    except Exception:
        auroc = float("nan")
    prec = a / (a + b) if (a + b) else float("nan")
    rec = a / (a + c) if (a + c) else float("nan")
    H1 = (orr > 3) and (p_fisher < 0.01 if p_fisher == p_fisher else False)
    summary = {"organism": "K_pneumoniae_HELD_OUT", "experimental_source": "ersilia_gradi_CRISPRi_Tnseq_experimentally_essential",
               "n_our_genes": len(ess), "n_adjudicable": len(genes), "n_experimental_essential": matched,
               "contingency_FBAess_vs_expess": {"both": a, "FBA_only": b, "exp_only": c, "neither": d},
               "precision_FBAess": round(prec, 3) if prec == prec else None,
               "recall_FBAess": round(rec, 3) if rec == rec else None,
               "odds_ratio": round(float(orr), 2), "fisher_p": (round(float(p_fisher), 8) if p_fisher == p_fisher else None),
               "auroc_growthratio_vs_experimental": round(auroc, 4) if auroc == auroc else None,
               "label_contamination_excluded": contamination, "H1_enrichment_OR_gt3_p_lt0.01": bool(H1)}
    if H1:
        summary["verdict"] = (f"HELD-OUT VALIDATION HOLDS — on K. pneumoniae (a WHO pathogen the method NEVER saw in development), "
                              f"the NEWBUG FBA-essentiality predictions are enriched for INDEPENDENT EXPERIMENTAL (CRISPRi/Tn-seq) "
                              f"essentiality at odds ratio {orr:.1f} (Fisher p={p_fisher:.1e}), precision {prec:.0%}. So the "
                              f"experimentally-validated mechanism signal is NOT confined to development organisms — it holds on a "
                              f"genuinely held-out pathogen (the north-star claim), now against experimental truth. THREE-ORGANISM "
                              f"picture: E. coli OR 64, Mtb OR 7.9, K. pneumoniae (held-out) OR {orr:.1f}. HONEST BOUNDS: binary "
                              f"enrichment validated; recall {rec:.0%} (FBA metabolic-scoped); continuous AUROC {auroc:.2f}; experimental "
                              f"label is an aggregation of published K. pneumoniae essentiality studies (verified experiment-backed, "
                              f"{contamination} non-experimental rows excluded); essentiality only, not drug-target/clinical. "
                              f"COVERAGE CAVEAT: only {len(genes)}/{len(ess)} of our genes were adjudicable (gene-symbol-mappable into "
                              f"the experimental table; strain-proteome versions differ so direct-accession overlap is 0) — that "
                              f"subset skews toward well-annotated core genes, so the association is valid WITHIN it but not a "
                              f"whole-proteome estimate.")
    else:
        summary["verdict"] = (f"HELD-OUT: does NOT clearly validate — OR {orr:.1f} (p={p_fisher}), precision {prec}, AUROC "
                              f"{auroc if auroc==auroc else 'NA'}, adjudicable {len(genes)}, exp-essential {matched}. Reported plainly; "
                              f"if weak, the held-out experimental validation is not established (check symbol-mapping coverage).")
    print("\nPANEL:", json.dumps({k: v for k, v in summary.items() if k != "verdict"}, indent=1))
    print("VERDICT:", summary["verdict"])
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "VALIDATE_essentiality_kp.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({k: v for k, v in summary.items() if k != "verdict"}, sort_keys=True)
    open(os.path.join(HERE, "results", "VALIDATE_kp_payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
