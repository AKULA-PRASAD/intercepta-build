"""SYNLETH2 — organism-NATIVE resistance-robustness on the HELD-OUT WHO pathogens' own de-novo GEMs.

SYNLETH1 classified E. coli (curated iML1515) and the engine ortholog-transferred those classes. SYNLETH2 removes the
transfer approximation: it runs the same classification directly on the held-out pathogens' OWN CarveMe GEMs
(K. pneumoniae newbug, A. baumannii newbug2), producing native per-accession resistance classes that plug straight into
the DiscoveryEngine (entities are UniProt accessions). Also checks how well the E. coli->pathogen ortholog transfer agreed.

Per GEM: single-gene + single-reaction deletion -> essential genes/reactions; classify each gene monotherapy_robust
(individually essential -> no metabolic bypass) / combination_required (isozyme-buffered essential function) / non_essential;
verify a sample of combination-required sets by double-gene-deletion. Deterministic; reproduced x2. Env: metabolic (cobra).

HONEST SCOPE: these are DE-NOVO CarveMe GEMs on default/complete medium -> FEWER essentials than curated models (rich medium
masks auxotrophy) and AUTO-generated GPRs -> the native classification is LOWER-CONFIDENCE than iML1515 (a real limit, stated).
Models metabolic bypass only (not target-mutation/efflux); hypotheses; not wet-lab.
"""
import os, sys, json, time, hashlib, logging, itertools
import cobra
from cobra.flux_analysis import single_gene_deletion, single_reaction_deletion, double_gene_deletion
logging.getLogger("cobra").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
GEMS = {"kpneumoniae": os.path.join(DATA, "newbug", "kpneumoniae.xml"),
        "abaumannii": os.path.join(DATA, "newbug2", "abaumannii.xml")}
ROOT = os.path.join(HERE, "..", "..")


def gid2acc(gid):
    parts = gid.split("_")
    return parts[1] if len(parts) > 1 else gid


def classify(org, path, t0):
    m = cobra.io.read_sbml_model(path); wt = m.slim_optimize(); thr = 0.01 * wt
    sg = single_gene_deletion(m, m.genes, processes=4); sg["gid"] = sg["ids"].apply(lambda s: list(s)[0])
    ess_genes = set(sg[sg.growth < thr]["gid"])
    sr = single_reaction_deletion(m, m.reactions, processes=4); sr["rid"] = sr["ids"].apply(lambda s: list(s)[0])
    ess_rxns = set(sr[sr.growth < thr]["rid"])
    combo_genes, mono, combo = set(), 0, []
    for rid in ess_rxns:
        r = m.reactions.get_by_id(rid); genes = [g.id for g in r.genes]
        if not genes: continue
        if any(g in ess_genes for g in genes): mono += 1
        else:
            combo.append((rid, genes)); combo_genes.update(genes)
    # verify a deterministic sample of combination-required isozyme sets
    checked = verified = 0
    for rid, genes in sorted(combo)[:15]:
        gg = sorted(genes)
        if len(gg) < 2: continue
        pairs = list(itertools.combinations(gg, 2))[:6]
        dd = double_gene_deletion(m, [p[0] for p in pairs], [p[1] for p in pairs], processes=4)
        checked += 1; verified += int(bool((dd["growth"] < thr).any()))
    # write native per-ACCESSION resistance classes (plugs directly into the engine)
    out = os.path.join(DATA, "synleth", f"{org}_resistance_classes.tsv")
    with open(out, "w") as f:
        f.write("gene\tclass\n")  # 'gene' column holds the UniProt accession (engine matches entities directly)
        seen = set()
        for g in m.genes:
            acc = gid2acc(g.id)
            if acc in seen: continue
            seen.add(acc)
            cls = ("monotherapy_robust" if g.id in ess_genes else
                   "combination_required" if g.id in combo_genes else "non_essential")
            f.write(f"{acc}\t{cls}\n")
    print(f"  [{org}] {len(m.genes)} genes, WT {wt:.2f}: essential {len(ess_genes)}, essential-rxns {len(ess_rxns)}; "
          f"monotherapy fns {mono}, combination-required {len(combo)} (verified {verified}/{checked}) [{time.time()-t0:.0f}s]", flush=True)
    return {"n_genes": len(m.genes), "wt": round(float(wt), 3), "n_essential_genes": len(ess_genes),
            "n_essential_reactions": len(ess_rxns), "n_monotherapy_functions": mono,
            "n_combination_required": len(combo), "verified": {"checked": checked, "confirmed": verified},
            "ess_gene_accs": sorted(gid2acc(g) for g in ess_genes)}


def main():
    t0 = time.time(); res = {}
    for org, path in GEMS.items():
        res[org] = classify(org, path, t0)
    # agreement of E. coli->pathogen ortholog transfer vs native, on our nominated broad-spectrum targets
    agree = {}
    ec = os.path.join(DATA, "synleth", "ecoli_resistance_classes.tsv")
    if os.path.exists(ec):
        ec_sym2cls = {}
        for ln in open(ec).read().splitlines()[1:]:
            p = ln.split("\t")
            if len(p) >= 2: ec_sym2cls[p[0].lower()] = p[1]
        preds = json.load(open(os.path.join(ROOT, "experiments/DRUGGABLE_predictions/results/DRUGGABLE_metrics.json")))["per_gene"]
        nominated = [g["gene"].lower() for g in preds if g["breadth"] >= 3]
        # KP: map symbol->acc via proteome, compare native vs transferred
        acc2sym = {}
        for ln in open(os.path.join(DATA, "newbug", "kpneumoniae.fasta")):
            if ln.startswith(">"):
                acc = ln[1:].split()[0].split("|")[1] if "|" in ln else ln[1:].split()[0]
                for tok in ln.split():
                    if tok.startswith("GN="): acc2sym[acc] = tok[3:].lower()
        native = {}
        for ln in open(os.path.join(DATA, "synleth", "kpneumoniae_resistance_classes.tsv")).read().splitlines()[1:]:
            p = ln.split("\t"); native[p[0]] = p[1]
        sym2accKP = {v: k for k, v in acc2sym.items()}
        rows, n_same = [], 0
        for sym in nominated:
            a = sym2accKP.get(sym); nat = native.get(a) if a else None; tr = ec_sym2cls.get(sym)
            if nat and tr:
                same = (nat == "monotherapy_robust") == (tr == "monotherapy_robust")
                n_same += int(same); rows.append({"gene": sym, "native_kp": nat, "ecoli_transfer": tr, "agree": same})
        agree = {"n_compared": len(rows), "n_agree_on_monotherapy_robust": n_same, "detail": rows}
    summary = {"organisms": res, "ecoli_transfer_agreement_on_nominated": agree}
    kp, ab = res["kpneumoniae"], res["abaumannii"]
    summary["verdict"] = (
        f"ORGANISM-NATIVE resistance classification on the HELD-OUT pathogens' OWN GEMs (removes the E. coli transfer "
        f"approximation). K. pneumoniae: {kp['n_essential_genes']} essential genes, {kp['n_combination_required']} "
        f"combination-required functions (verified {kp['verified']['confirmed']}/{kp['verified']['checked']}). A. baumannii: "
        f"{ab['n_essential_genes']} essential, {ab['n_combination_required']} combination-required "
        f"({ab['verified']['confirmed']}/{ab['verified']['checked']}). Native per-accession classes written -> plug directly "
        f"into the DiscoveryEngine (no ortholog transfer). E. coli->KP transfer agreement on nominated targets: "
        f"{agree.get('n_agree_on_monotherapy_robust')}/{agree.get('n_compared')}. **HONEST BOUNDS: de-novo CarveMe GEMs on "
        f"DEFAULT/complete medium give FAR FEWER essentials than curated iML1515 (rich medium masks auxotrophy) and use "
        f"AUTO-generated GPRs -> this native classification is LOWER-CONFIDENCE than the iML1515 result; it is organism-native "
        f"but model-quality-limited. Models metabolic bypass only; hypotheses; not wet-lab.**")
    print("\nPANEL:", json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "ess_gene_accs"} for k, v in res.items()}, indent=1))
    print("VERDICT:", summary["verdict"])
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump({"summary": summary, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)},
              open(os.path.join(HERE, "results", "SYNLETH2_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({k: v for k, v in summary.items() if k != "verdict"}, sort_keys=True)
    open(os.path.join(HERE, "results", "SYNLETH2_payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    print("payload sha256:", hashlib.sha256(payload.encode()).hexdigest(), f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
