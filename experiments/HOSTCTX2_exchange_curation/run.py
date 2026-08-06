"""HOSTCTX2 — does HOST-EXCHANGE / MEDIUM CURATION rescue the malaria FBA-essentiality signal?

Controlled A/B: copies GENERALIZE5's method EXACTLY (same GEM, truth, alias map, gene-ID mapping, 2x2 one-sided Fisher
gate, essential-if-KO-growth<1%WT, 6-dp GLPK-jitter rounding). The ONLY manipulated variable is the set of exchange
reactions permitted to carry UPTAKE flux (host-RBC-available nutrient set, frozen in PREREG.md).

Media frozen in PREREG.md BEFORE any curated scoring. Baseline = default open medium (must reproduce GENERALIZE5).
Env: metabolic (cobra 0.31; NO scipy -> math.comb hypergeometric Fisher fallback). Deterministic; reproduced x2.
"""
import os, csv, json, time, hashlib, logging
import cobra
from cobra.flux_analysis import single_gene_deletion
logging.getLogger("cobra").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
D = os.path.join(DATA, "generalize5")               # REUSE GENERALIZE5 assets read-only
MODEL = os.path.join(D, "iPfal19.xml")
ZHANG = os.path.join(D, "zhang2018_essentiality.csv")
ALIAS = os.path.join(D, "Pfalciparum3D7_GeneAliases.csv")

MIS_ESSENTIAL_THRESHOLD = 0.2  # (kept for parity; primary gate uses phenotype)

# ---- FROZEN host-available nutrient sets (PREREG.md). Values are model EX reaction IDs. ----
def _ex(names):
    return set((("EX_lipid_c") if n == "lipid_c" else f"EX_{n}_e") for n in names)

RPMI_AA = ["arg__L", "asn__L", "asp__L", "cysi__L", "glu__L", "gln__L", "gly", "his__L", "ile__L", "leu__L",
           "lys__L", "met__L", "phe__L", "pro__L", "ser__L", "thr__L", "trp__L", "tyr__L", "val__L"]
RPMI_VIT = ["pnto__R", "pnto_R", "fol", "ncam", "4abz", "pydxn", "ribflv", "thm", "inost", "chol"]
RPMI_SALT = ["pi", "so4", "hco3", "no3"]
GAS = ["o2", "co2", "h2o", "h"]
CORE = ["glc__D", "gthrd", "hxan", "hb", "fe2", "lipid_c"]

PRIMARY = _ex(RPMI_AA + RPMI_VIT + RPMI_SALT + GAS + CORE)
STRICT = _ex(["glc__D", "hxan", "pnto__R", "pnto_R", "ile__L", "hb", "fe2", "so4", "o2", "ribflv", "pi", "hco3",
              "h2o", "h", "co2", "fol", "ncam", "pydxn", "thm", "inost", "chol", "lipid_c"])
RBC_PURINE = ["adn", "ins", "ade", "gua", "xan", "gsn", "dad_2", "dgsn", "din"]
PERMISSIVE = PRIMARY | _ex(RBC_PURINE) | _ex(["glyc", "etha"])

MEDIA = {"baseline_default_open": None, "curated_primary": PRIMARY,
         "curated_strict": STRICT, "curated_permissive": PERMISSIVE}


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fisher_greater(a, b, c, d):
    try:
        from scipy.stats import fisher_exact
        orr, p = fisher_exact([[a, b], [c, d]], alternative="greater")
        return float(orr), float(p)
    except Exception:
        from math import comb
        n = a + b + c + d; r = a + b; col = a + c
        p = sum(comb(col, k) * comb(n - col, r - k) for k in range(a, min(r, col) + 1)) / comb(n, r)
        orr = (a * d) / max(b * c, 1)
        return float(orr), float(p)


def load_aliases():
    amap = {}
    with open(ALIAS, encoding="utf-8", errors="ignore") as f:
        for row in csv.reader(f):
            if not row or not row[0].strip() or row[0].strip() == "name1":
                continue
            canon = row[0].strip()
            for cell in row:
                c = cell.strip()
                if c and c.upper() != "NA":
                    amap[c.lower()] = canon
    return amap


def load_zhang():
    z = {}
    for row in csv.DictReader(open(ZHANG, encoding="utf-8", errors="ignore")):
        gid = row["Gene ID"].strip().upper()
        if not gid:
            continue
        try:
            mis = float(row["Zhang MIS"]) if row["Zhang MIS"] not in ("", "NA") else None
        except ValueError:
            mis = None
        z[gid] = {"mis": mis, "phenotype": row["Zhang Phenotype"].strip()}
    return z


def apply_medium(model, allow):
    """The ONLY manipulation: restrict UPTAKE to host-available exchanges. allow=None -> default open (baseline).
    For host-available EX: lower_bound=-1000 (uptake allowed). Else: lower_bound=0 (block import, KEEP export)."""
    if allow is None:
        return
    for r in model.exchanges:
        if r.id in allow:
            if r.lower_bound > -1000.0:
                r.lower_bound = -1000.0
        else:
            r.lower_bound = 0.0
    # EX_lipid_c is a two-sided pseudo-exchange; ensure it is fully closed when not host-available
    if "EX_lipid_c" not in allow:
        model.reactions.EX_lipid_c.lower_bound = 0.0
        model.reactions.EX_lipid_c.upper_bound = 0.0


def build_mapping(genes):
    aliases = load_aliases(); zhang = load_zhang()

    def canon(gid):
        u = gid.strip().upper()
        if u in zhang:
            return u
        a = aliases.get(gid.strip().lower())
        if a and a.upper() in zhang:
            return a.upper()
        return None

    mapped = {}; unmapped = []
    for g in genes:
        c = canon(g.id)
        (mapped.__setitem__(g.id, c) if c else unmapped.append(g.id))
    return mapped, unmapped, zhang


def essentiality(model):
    """single_gene_deletion FBA; essential if KO growth < 1% WT. Returns (wt, growth_dict, fba_ess_set)."""
    wt = round(float(model.slim_optimize()), 6)
    thr = 0.01 * wt
    genes = list(model.genes)
    sg = single_gene_deletion(model, genes, processes=1)
    sg["gid"] = sg["ids"].apply(lambda s: list(s)[0])
    gr = {r.gid: round(float(r.growth), 6) for r in sg.itertuples()}
    fba_ess = set(g.id for g in genes if gr.get(g.id, wt) < thr)
    return wt, gr, fba_ess


def score(mapped, gr, fba_ess, wt, exp_ess_ids, label):
    a = b = c = d = 0
    for gid, cid in mapped.items():
        pe = gid in fba_ess; ee = cid in exp_ess_ids
        if pe and ee: a += 1
        elif pe and not ee: b += 1
        elif not pe and ee: c += 1
        else: d += 1
    orr, p = fisher_greater(a, b, c, d)
    prec = a / (a + b) if (a + b) else None
    rec = a / (a + c) if (a + c) else None
    y = [1 if cid in exp_ess_ids else 0 for gid, cid in mapped.items()]
    sc = [-gr.get(gid, wt) for gid in mapped]
    auroc = None
    npos = sum(y); nneg = len(y) - npos
    if 0 < npos < len(y):
        order = sorted(range(len(sc)), key=lambda i: sc[i])
        ranks = [0.0] * len(sc); i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and sc[order[j + 1]] == sc[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[order[k]] = avg
            i = j + 1
        sum_pos = sum(ranks[i] for i in range(len(y)) if y[i] == 1)
        auroc = (sum_pos - npos * (npos + 1) / 2.0) / (npos * nneg)
    return {"definition": label,
            "n_exp_essential_mapped": sum(1 for cid in mapped.values() if cid in exp_ess_ids),
            "n_fba_essential_mapped": a + b,
            "contingency": {"both": a, "FBA_only": b, "exp_only": c, "neither": d},
            "odds_ratio": round(orr, 3),
            "fisher_p_greater": float(f"{p:.3e}"),
            "precision": round(prec, 3) if prec is not None else None,
            "recall": round(rec, 3) if rec is not None else None,
            "auroc": round(auroc, 4) if auroc is not None else None,
            "gate_pass": bool(orr > 3 and p < 0.01)}


def run():
    base = cobra.io.read_sbml_model(MODEL)
    genes = list(base.genes)
    mapped, unmapped, zhang = build_mapping(genes)

    results = {}
    for name, allow in MEDIA.items():
        m = base.copy()
        apply_medium(m, allow)
        wt, gr, fba_ess = essentiality(m)
        exp_primary = set(cid for cid in mapped.values() if zhang[cid]["phenotype"] == "Non - Mutable in CDS")
        exp_mis = set(cid for cid in mapped.values()
                      if zhang[cid]["mis"] is not None and zhang[cid]["mis"] <= MIS_ESSENTIAL_THRESHOLD)
        pr = score(mapped, gr, fba_ess, wt, exp_primary, "phenotype:Non-Mutable-in-CDS")
        se = score(mapped, gr, fba_ess, wt, exp_mis, f"MIS<={MIS_ESSENTIAL_THRESHOLD}")
        results[name] = {"wt_growth": round(float(wt), 4),
                         "n_open_uptake_exchanges": sum(1 for r in m.exchanges if r.lower_bound < 0),
                         "n_host_available_set": (len(allow) if allow else None),
                         "feasible": bool(wt > 1e-6),
                         "n_fba_essential_total": len(fba_ess),
                         "primary": pr, "sensitivity_MIS": se}

    # precision-collapse guard + gate logic (baseline vs each curated), primary definition
    base_p = results["baseline_default_open"]["primary"]
    base_reproduced = bool(base_p["contingency"] == {"both": 55, "FBA_only": 14, "exp_only": 218, "neither": 137}
                           and base_p["odds_ratio"] == 2.469)
    verdicts = {}
    for name in ["curated_primary", "curated_strict", "curated_permissive"]:
        cp = results[name]["primary"]
        or_up = cp["odds_ratio"] > base_p["odds_ratio"]
        prec_ok = (cp["precision"] is not None and cp["precision"] >= 0.5)
        # balloon check: essential-set > 2x baseline mapped-essential AND precision fell below baseline
        n_ess = cp["n_fba_essential_mapped"]; base_ess = base_p["n_fba_essential_mapped"]
        balloon = (n_ess > 2 * base_ess) and (cp["precision"] is not None and cp["precision"] < base_p["precision"])
        if cp["odds_ratio"] > 3 and cp["fisher_p_greater"] < 0.01 and or_up and prec_ok and not balloon:
            v = "RESCUE"
        elif cp["odds_ratio"] > 3 and cp["fisher_p_greater"] < 0.01 and (not prec_ok or balloon):
            v = "NEGATIVE-with-artifact(precision-collapse/balloon)"
        elif or_up and cp["fisher_p_greater"] < 0.01 and prec_ok and not balloon:
            v = "PARTIAL"
        else:
            v = "NEGATIVE"
        verdicts[name] = {"verdict": v, "or_improves_over_baseline": bool(or_up), "precision_ok(>=0.5)": bool(prec_ok),
                          "essential_set_balloon_artifact": bool(balloon),
                          "n_fba_essential_mapped": n_ess, "baseline_n_fba_essential_mapped": base_ess}

    payload = {
        "organism": "Plasmodium falciparum 3D7 (malaria)", "model": "iPfal19",
        "manipulated_variable": "exchange/import (uptake) bounds only — host-RBC-available nutrient set",
        "baseline_reproduced_vs_GENERALIZE5": base_reproduced,
        "n_model_genes": len(genes), "n_genes_mapped_to_zhang": len(mapped), "n_genes_unmapped": len(unmapped),
        "host_available_sets": {"curated_primary": sorted(PRIMARY), "curated_strict": sorted(STRICT),
                                "curated_permissive": sorted(PERMISSIVE)},
        "results_by_medium": results,
        "gate_verdicts_primary_definition": verdicts,
    }
    prov = {"model_sha256": sha256_file(MODEL), "zhang_sha256": sha256_file(ZHANG), "alias_sha256": sha256_file(ALIAS)}
    return payload, prov


def main():
    t0 = time.time()
    payload, filehashes = run()
    lines = ["baseline_reproduced_vs_GENERALIZE5 = %s" % payload["baseline_reproduced_vs_GENERALIZE5"]]
    for name, r in payload["results_by_medium"].items():
        p = r["primary"]
        lines.append(f"{name:22s} feasible={r['feasible']} WT={r['wt_growth']:>8} "
                     f"n_open={r['n_open_uptake_exchanges']:>3} OR={p['odds_ratio']:>6} p={p['fisher_p_greater']:.2e} "
                     f"prec={p['precision']} rec={p['recall']} auroc={p['auroc']} "
                     f"cont={p['contingency']} n_ess_map={p['n_fba_essential_mapped']} gate={p['gate_pass']}")
    for name, v in payload["gate_verdicts_primary_definition"].items():
        lines.append(f"VERDICT {name:20s} -> {v['verdict']} (OR_up={v['or_improves_over_baseline']} "
                     f"prec_ok={v['precision_ok(>=0.5)']} balloon={v['essential_set_balloon_artifact']})")
    verdict = "\n".join(lines)
    out = {"payload": payload, "verdict": verdict,
           "provenance": {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                          "git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
                          "cobra_version": cobra.__version__, "file_hashes": filehashes,
                          "runtime_sec": round(time.time() - t0, 1)}}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "HOSTCTX2_metrics.json"), "w"), indent=2, sort_keys=True)
    payload_json = json.dumps(payload, sort_keys=True)
    sha = hashlib.sha256(payload_json.encode()).hexdigest()
    open(os.path.join(HERE, "results", "HOSTCTX2_payload.sha256"), "w").write(sha + "\n")
    print(verdict)
    print("\npayload sha256:", sha, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
