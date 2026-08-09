#!/usr/bin/env python3
"""
DURABLETARGETS1 -- durability-augmented multi-axis antibacterial TARGET-QUALITY scorecard.

INTEGRATION (not new science): assembles ALREADY-COMMITTED, already-reproduced axis
results from BESTINT1 (druggability / breadth / resistance-robustness / condition-robustness
+ its equal-weight composite), PREDVAL (experimental essentiality per organism) and DYNAMICS2
(the resistance-DURABILITY axis: mean ESM-2 masked-marginal entropy over drug-contact residues;
LOWER entropy = MORE durable target) into ONE ranked, transparent target-quality scorecard.

Deterministic. No randomness, no fetch, no recompute of the underlying science. Reproduce x2
byte-identical: payload SHA-256 over sorted-key JSON, EXCLUDING the provenance block.
"""
import json
import math
import os
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

SRC = {
    "BESTINT1": os.path.join(ROOT, "experiments/BESTINT1_multiaxis_score/results/BESTINT1_metrics.json"),
    "PREDVAL":  os.path.join(ROOT, "experiments/PREDVAL_target_scorecard/results/PREDVAL_metrics.json"),
    "DYNAMICS2": os.path.join(ROOT, "experiments/DYNAMICS2_durability_scaleup/results/DYNAMICS2_metrics.json"),
}

LN20 = math.log(20.0)  # max Shannon entropy over 20 amino acids ~= 2.9957 nats

# Antibacterial target set = union of (a) DYNAMICS2 antibacterial-class targets (durability-covered)
# and (b) BESTINT1/flagship antibacterial cores. ispE is a flagship + BESTINT1 core with NO
# drug-bound pocket assigned in DYNAMICS -> durability = NA (kept, to show honest NA coverage).
FLAGSHIP_EXTRA = ["ispE"]


def rnd(x, n=4):
    if x is None:
        return None
    return round(float(x), n)


def zscores(values):
    """Population z-scores (ddof=0). Returns (list_of_z, has_variance)."""
    n = len(values)
    m = sum(values) / n
    var = sum((v - m) ** 2 for v in values) / n
    sd = math.sqrt(var)
    if sd < 1e-12:
        return [0.0 for _ in values], False
    return [(v - m) / sd for v in values], True


def main():
    with open(SRC["BESTINT1"]) as f:
        bestint = json.load(f)
    with open(SRC["PREDVAL"]) as f:
        predval = json.load(f)
    with open(SRC["DYNAMICS2"]) as f:
        dyn = json.load(f)

    # --- index committed axis values by gene symbol ---
    bi = {r["gene"]: r for r in bestint["ranking"]}
    pv = {r["gene"]: r for r in predval["scorecard"]}
    # durability from DYNAMICS2, antibacterial class only (has a drug-binding pocket)
    du = {r["gene"]: r for r in dyn["payload"]["per_target"] if r["cls"] == "abx"}

    # target set: all DYNAMICS abx targets + flagship extras (ispE)
    genes = sorted(set(list(du.keys()) + FLAGSHIP_EXTRA))

    # --- assemble per-target table ---
    scorecard = []
    for g in genes:
        b = bi.get(g)
        p = pv.get(g)
        d = du.get(g)

        # experimental essentiality (PREDVAL) -- number of organisms (0..3), NA if not in PREDVAL
        if p is not None:
            exp_ess = p["n_orgs_exp_essential"]
            exp_ess_norm = round(exp_ess / 3.0, 4)
        else:
            exp_ess = None
            exp_ess_norm = None

        # BESTINT1 axes
        drugg = b["druggability"] if b else None
        breadth = b["breadth_frac"] if b else None
        resist = b["resistance_robust"] if b else None
        cond = b["condition_robust"] if b else None
        bestint_score = b["best_intervention_score"] if b else None

        # durability axis
        if d is not None:
            mean_H = d["mean_entropy"]
            dur_norm = 1.0 - mean_H / LN20  # monotone, higher = more durable, ~[0,1]
            label = d["label"]             # HIGH / LOW resistance liability
        else:
            mean_H = None
            dur_norm = None
            label = None

        scorecard.append({
            "gene": g,
            "exp_essential_orgs": exp_ess,
            "exp_essential_norm": exp_ess_norm,
            "breadth_frac": rnd(breadth),
            "druggability": rnd(drugg),
            "resistance_robust": rnd(resist),
            "condition_robust": rnd(cond),
            "bestint1_composite_noDur": rnd(bestint_score),
            "durability_mean_contact_entropy": rnd(mean_H),
            "durability_norm": rnd(dur_norm),
            "resistance_liability_label": label,
            "durability_pdb": d["pdb"] if d else None,
            "durability_ligand": d["ligand"] if d else None,
        })

    # --- coverage (honest, per axis) ---
    coverage = {
        "n_targets": len(scorecard),
        "with_exp_essentiality": sum(1 for r in scorecard if r["exp_essential_orgs"] is not None),
        "with_bestint1_axes": sum(1 for r in scorecard if r["druggability"] is not None),
        "with_durability": sum(1 for r in scorecard if r["durability_norm"] is not None),
        "with_full_axes_and_durability": sum(
            1 for r in scorecard
            if r["druggability"] is not None and r["durability_norm"] is not None
        ),
    }

    # --- durability-augmented composite on the full-coverage intersection ---
    # (targets having BOTH the 4 BESTINT1 axes AND a durability value)
    full = [r for r in scorecard if r["druggability"] is not None and r["durability_norm"] is not None]
    full_sorted = sorted(full, key=lambda r: r["gene"])

    axis_keys = ["druggability", "breadth_frac", "resistance_robust", "condition_robust"]
    z = {}
    dropped_noDur = []
    for k in axis_keys:
        vals = [r[k] for r in full_sorted]
        zk, has_var = zscores(vals)
        z[k] = zk
        if not has_var:
            dropped_noDur.append(k)  # zero variance within set -> non-informative, drops out
    zdur, dur_has_var = zscores([r["durability_norm"] for r in full_sorted])
    z["durability_norm"] = zdur

    used_noDur = [k for k in axis_keys if k not in dropped_noDur]
    used_withDur = used_noDur + (["durability_norm"] if dur_has_var else [])

    composite = []
    for i, r in enumerate(full_sorted):
        c_no = sum(z[k][i] for k in used_noDur) / len(used_noDur)
        c_with = sum(z[k][i] for k in used_withDur) / len(used_withDur)
        composite.append({
            "gene": r["gene"],
            "resistance_liability_label": r["resistance_liability_label"],
            "durability_norm": r["durability_norm"],
            "bestint1_composite_noDur_raw": r["bestint1_composite_noDur"],
            "z_composite_noDur": round(c_no, 4),
            "z_composite_withDur": round(c_with, 4),
        })

    # ranks (1 = best) for each composite
    order_no = sorted(range(len(composite)), key=lambda i: -composite[i]["z_composite_noDur"])
    order_with = sorted(range(len(composite)), key=lambda i: -composite[i]["z_composite_withDur"])
    rank_no = {order_no[k]: k + 1 for k in range(len(order_no))}
    rank_with = {order_with[k]: k + 1 for k in range(len(order_with))}
    for i, c in enumerate(composite):
        c["rank_noDur"] = rank_no[i]
        c["rank_withDur"] = rank_with[i]
        c["rank_delta"] = rank_no[i] - rank_with[i]  # +ve = ROSE when durability added

    composite_sorted = sorted(composite, key=lambda c: c["rank_withDur"])

    risers = sorted([c["gene"] for c in composite if c["rank_delta"] > 0],
                    key=lambda g: -next(c["rank_delta"] for c in composite if c["gene"] == g))
    fallers = sorted([c["gene"] for c in composite if c["rank_delta"] < 0],
                     key=lambda g: next(c["rank_delta"] for c in composite if c["gene"] == g))

    shortlist = [c["gene"] for c in composite_sorted[:5]]

    # most-durable ranking across ALL durability-covered targets (independent of composite)
    dur_ranked = sorted(
        [r for r in scorecard if r["durability_norm"] is not None],
        key=lambda r: -r["durability_norm"],
    )
    durability_ranking = [
        {"gene": r["gene"], "durability_norm": r["durability_norm"],
         "mean_contact_entropy": r["durability_mean_contact_entropy"],
         "label": r["resistance_liability_label"]}
        for r in dur_ranked
    ]

    payload = {
        "experiment": "DURABLETARGETS1_durability_augmented_scorecard",
        "kind": "INTEGRATION (composition of committed, reproduced-x2 in-silico axes; NOT new science)",
        "axes": {
            "breadth_frac": "BESTINT1: FBA cross-organism breadth / 7",
            "condition_robust": "BESTINT1: CONDROB robust=1 / partial=0.5",
            "druggability": "BESTINT1: fpocket max druggability [0,1]",
            "durability_norm": "DYNAMICS2 (NEW): 1 - mean_contact_entropy/ln(20); higher = more durable (lower ESM-2 masked-marginal entropy at drug-contact residues)",
            "exp_essential_orgs": "PREDVAL: # of {E.coli, K.pneumoniae, M.tb} experimentally essential (0-3)",
            "resistance_robust": "BESTINT1: SYNLETH monotherapy=1 / combination=0.5",
        },
        "durability_transform": "durability_norm = 1 - mean_contact_entropy / ln(20)  [monotone, higher=more durable]",
        "composite_method": (
            "Equal-weight z-score aggregation (population std, ddof=0) computed WITHIN the "
            "full-coverage intersection set, over the informative (non-zero-variance) axes. "
            "z_composite_noDur = mean z over BESTINT1 axes; z_composite_withDur adds durability. "
            "Unfitted equal weights by design (no ground truth of 'best durable target' exists to "
            "fit -> fitting would fabricate confidence, per BESTINT1). Delta isolates durability's "
            "effect because the method is identical except for the added axis."
        ),
        "composite_zero_variance_axes_dropped": sorted(dropped_noDur),
        "composite_axes_used_noDur": sorted(used_noDur),
        "composite_axes_used_withDur": sorted(used_withDur),
        "coverage": coverage,
        "scorecard": scorecard,
        "durability_augmented_composite": composite_sorted,
        "durability_ranking_all_covered": durability_ranking,
        "delta_from_adding_durability": {
            "fallers_when_durability_added": fallers,
            "risers_when_durability_added": risers,
        },
        "shortlist_top5_durability_augmented": shortlist,
        "source_metrics": {
            "BESTINT1_composite": "equal-weight mean(druggability, breadth, resistance, condition); Spearman(score, expEssOrgs)=0.6896",
            "DYNAMICS2_durability_auroc": dyn["payload"]["primary_mean_entropy"]["auroc"],
            "DYNAMICS2_durability_mwu_p": dyn["payload"]["primary_mean_entropy"]["mwu_p"],
            "DYNAMICS2_n": dyn["payload"]["primary_mean_entropy"]["n"],
            "DYNAMICS2_subset_antibacterial_auroc": dyn["payload"]["subset_antibacterial_only"]["auroc"],
            "PREDVAL_focus_broadspectrum_druggable": predval["summary"]["n_focus_broadspectrum_druggable"],
        },
        "scope": (
            "Target-QUALITY triage / decision-support scorecard. INTEGRATION of committed in-silico "
            "axes -- NOT new validation, NOT a drug, NOT clinical. Durability carries DYNAMICS's bounds: "
            "AUROC ~0.83 (n=26, PLM-proxy, STATIC single drug-bound structure, confound-softened strict "
            "significance) and applies ONLY to targets with a (crystal/predicted) drug-binding pocket; "
            "targets without one get durability=NA (honest, not imputed). exp-essentiality is displayed "
            "and used as the independent truth axis; it is NOT folded into the composite (mirrors BESTINT1, "
            "avoids circularity). Cross-organism/ortholog-transferred; hypotheses; not wet-lab."
        ),
        "verdict": (
            "INTEGRATION DELIVERED: a durability-augmented multi-axis antibacterial target-quality "
            "scorecard -- the differentiated deliverable's capstone; composition of committed results, "
            "not new science."
        ),
    }

    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    sha = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

    out = {
        "payload": payload,
        "payload_sha256": sha,
        "provenance": {
            "sources": {
                "BESTINT1": bestint.get("provenance", {}),
                "DYNAMICS2": dyn.get("provenance", {}),
                "PREDVAL": predval.get("provenance", {}),
            },
            "note": "provenance excluded from payload_sha256 (deterministic reproduction).",
        },
    }

    results_dir = os.path.join(HERE, "results")
    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, "DURABLETARGETS1_metrics.json"), "w") as f:
        json.dump(out, f, sort_keys=True, indent=2)
        f.write("\n")
    with open(os.path.join(results_dir, "payload.sha256"), "w") as f:
        f.write(sha + "\n")

    print("payload_sha256:", sha)
    print("coverage:", json.dumps(coverage))
    print("shortlist_top5:", shortlist)
    print("risers:", risers, "| fallers:", fallers)
    print("dropped_zero_variance_axes:", sorted(dropped_noDur))


if __name__ == "__main__":
    main()
