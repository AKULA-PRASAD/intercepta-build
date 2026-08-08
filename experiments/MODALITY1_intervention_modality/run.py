#!/usr/bin/env python
"""MODALITY1 scoring — deterministic, no RNG. Reads frozen ground_truth.json, applies the
PRE-REGISTERED mechanism+localization-first modality recommender + frozen feasibility matrix,
evaluates G1/G2/G3, writes results/MODALITY1_metrics.json (sorted keys) + payload.sha256.
Reproduces byte-identical. The supplementary fpocket cross-check reuses MENDEL1's cached scores."""
import json, os, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "/Users/kalki/intercepta_data/modality1"
RESULTS = os.path.join(HERE, "results")
os.makedirs(RESULTS, exist_ok=True)

# ---- frozen constants (PREREG) ----
DRUGGABLE_CLASSES = {"enzyme", "kinase", "receptor", "ion_channel", "transporter",
                     "nuclear_receptor", "transport_carrier", "globin"}
STABILIZABLE = {"transport_carrier", "globin"}
MAJORITY_BASELINE = 8.0 / 43.0  # SM_INHIBITOR = 8 of 43 (stated in PREREG)
SM_MODALITIES = {"SMALL_MOLECULE_INHIBITOR", "SMALL_MOLECULE_ACTIVATOR"}

rows_gt = json.load(open(os.path.join(HERE, "ground_truth.json")))["rows"]


def druggable(pc):
    return pc in DRUGGABLE_CLASSES


# ---- PRIMARY recommender (mechanism + localization + druggability) ----
def recommend(mech, loc, pc):
    d = druggable(pc)
    if mech in ("GoF", "overactivity"):
        if loc in ("secreted", "cell_surface"):
            return "MONOCLONAL_ANTIBODY"
        if loc in ("membrane", "intracellular"):
            return "SMALL_MOLECULE_INHIBITOR" if d else "ASO_siRNA"
        return "ABSTAIN"
    if mech in ("dominant_negative", "toxic_aggregation"):
        if pc in STABILIZABLE:
            return "SMALL_MOLECULE_ACTIVATOR"
        if loc == "intracellular":
            return "ASO_siRNA"
        return "ABSTAIN"
    if mech == "LoF_misfold":
        if d and loc in ("membrane", "intracellular", "lysosomal"):
            return "SMALL_MOLECULE_ACTIVATOR"
        return "ABSTAIN"
    if mech in ("LoF_null", "LoF"):
        if pc == "enzyme" and loc == "lysosomal":
            return "ENZYME_PROTEIN_REPLACEMENT"  # bbb handled below via feasibility-aware wrapper
        if loc == "secreted":
            return "ENZYME_PROTEIN_REPLACEMENT"
        if loc in ("intracellular", "membrane"):
            return "GENE_THERAPY"
        return "ABSTAIN"
    return "ABSTAIN"


def recommend_primary(r):
    """PRIMARY = recommend() + the bbb_cns gate on lysosomal enzyme replacement (localization-aware)."""
    rec = recommend(r["mechanism"], r["localization"], r["protein_class"])
    if rec == "ENZYME_PROTEIN_REPLACEMENT" and r["localization"] == "lysosomal" and r["bbb_cns"]:
        return "ABSTAIN"  # ERT cannot cross the BBB -> abstain (HEXA/ARSA)
    return rec


# ---- mechanism-only ablation (localization-blind) for G3 ----
def recommend_mechonly(mech, pc):
    d = druggable(pc)
    if mech in ("GoF", "overactivity"):
        return "SMALL_MOLECULE_INHIBITOR" if d else "ASO_siRNA"
    if mech in ("dominant_negative", "toxic_aggregation"):
        return "ASO_siRNA"  # cannot know 'stabilizable native fold' without localization/class handle
    if mech == "LoF_misfold":
        return "SMALL_MOLECULE_ACTIVATOR" if d else "ABSTAIN"
    if mech in ("LoF_null", "LoF"):
        return "ENZYME_PROTEIN_REPLACEMENT" if d else "GENE_THERAPY"
    return "ABSTAIN"


# ---- frozen feasibility matrix ----
def is_feasible(modality, r):
    mech, loc, pc = r["mechanism"], r["localization"], r["protein_class"]
    d = druggable(pc)
    if modality == "ABSTAIN":
        return True  # abstention is never a violation
    if modality == "MONOCLONAL_ANTIBODY":
        return loc not in ("intracellular", "lysosomal")
    if modality == "SMALL_MOLECULE_INHIBITOR":
        return mech in ("GoF", "overactivity") and d
    if modality == "SMALL_MOLECULE_ACTIVATOR":
        return d and (mech == "LoF_misfold" or (mech == "toxic_aggregation" and pc in STABILIZABLE))
    if modality == "ENZYME_PROTEIN_REPLACEMENT":
        return mech in ("LoF_null", "LoF") and (loc == "secreted" or (loc == "lysosomal" and not r["bbb_cns"]))
    if modality == "GENE_THERAPY":
        return mech not in ("GoF", "overactivity", "dominant_negative", "toxic_aggregation")
    if modality == "ASO_siRNA":
        if mech in ("LoF_null", "LoF", "LoF_misfold"):
            return bool(r.get("splice_addressable"))
        return True
    return True


def feasible_set(r):
    all_mod = ["SMALL_MOLECULE_INHIBITOR", "SMALL_MOLECULE_ACTIVATOR", "MONOCLONAL_ANTIBODY",
               "ASO_siRNA", "ENZYME_PROTEIN_REPLACEMENT", "GENE_THERAPY"]
    return [m for m in all_mod if is_feasible(m, r)]


# ---- COHERENCE ASSERTION: no approved true_modality is flagged infeasible ----
coherence_violations = []
for r in rows_gt:
    if r["true_modality"] != "ABSTAIN" and not is_feasible(r["true_modality"], r):
        coherence_violations.append(r["id"])
assert not coherence_violations, f"feasibility matrix contradicts ground truth for {coherence_violations}"


def auroc(pos, neg):
    if not pos or not neg:
        return None
    wins = 0.0
    for p in pos:
        for n in neg:
            wins += 1.0 if p > n else (0.5 if p == n else 0.0)
    return wins / (len(pos) * len(neg))


# ---- score every row ----
rows = []
for r in rows_gt:
    prim = recommend_primary(r)
    mo = recommend_mechonly(r["mechanism"], r["protein_class"])
    rows.append({
        "id": r["id"], "gene": r["gene"], "disease_class": r["disease_class"],
        "mechanism": r["mechanism"], "localization": r["localization"], "protein_class": r["protein_class"],
        "true_modality": r["true_modality"], "also_feasible": r["also_feasible"],
        "pred_primary": prim, "pred_mechonly": mo,
        "correct_primary": prim == r["true_modality"],
        "primary_feasible": is_feasible(prim, r),
        "mechonly_feasible": is_feasible(mo, r),
        "feasible_set": feasible_set(r),
    })
rows.sort(key=lambda x: x["id"])
n = len(rows)

# G1 — top-modality accuracy
n_correct = sum(x["correct_primary"] for x in rows)
acc_primary = n_correct / n
g1_pass = acc_primary >= (MAJORITY_BASELINE + 0.20)

# per-class recall + macro balanced accuracy
classes = sorted(set(x["true_modality"] for x in rows))
per_class = {}
for cl in classes:
    tot = sum(1 for x in rows if x["true_modality"] == cl)
    cor = sum(1 for x in rows if x["true_modality"] == cl and x["pred_primary"] == cl)
    per_class[cl] = {"n": tot, "recall": round(cor / tot, 4)}
bal_acc = round(sum(v["recall"] for v in per_class.values()) / len(per_class), 4)

# G2 — FAIL-SAFE: 0 infeasible primary recommendations
unsafe_primary = sorted([x["id"] for x in rows if not x["primary_feasible"]])
g2_pass = len(unsafe_primary) == 0

# G3 — localization load-bearing: mech-only violations vs primary (0)
unsafe_mechonly = sorted([x["id"] for x in rows if not x["mechonly_feasible"]])
acc_mechonly = sum(1 for x in rows if x["pred_mechonly"] == x["true_modality"]) / n
g3_pass = (len(unsafe_mechonly) >= 1) and (len(unsafe_primary) == 0)

# misses (all should be SAFE: either an alternative FEASIBLE modality or ABSTAIN)
misses = [{"id": x["id"], "true": x["true_modality"], "pred": x["pred_primary"],
           "pred_feasible": x["primary_feasible"],
           "pred_in_also_feasible": x["pred_primary"] in x["also_feasible"] or x["pred_primary"] == "ABSTAIN"}
          for x in rows if not x["correct_primary"]]
unsafe_misses = [m for m in misses if not m["pred_feasible"]]

# supplementary fpocket structural cross-check (reuse MENDEL1 cache; NOT a gate)
fp_path = os.path.join(DATA, "fpocket_scores_reused.json")
fp = json.load(open(fp_path)) if os.path.exists(fp_path) else {}
sm_scores, notsm_scores = [], []
for r in rows_gt:
    e = fp.get(r["gene"])
    if not e or e.get("fpocket_drug_score") is None:
        continue
    s = e["fpocket_drug_score"]
    (sm_scores if r["true_modality"] in SM_MODALITIES else notsm_scores).append(s)
fp_auroc = auroc(sm_scores, notsm_scores)

overall_pass = g1_pass and g2_pass

# ---- payload (excludes verdict + provenance) for reproduce-x2 sha ----
payload = {
    "n": n,
    "majority_baseline": round(MAJORITY_BASELINE, 4),
    "class_counts": {cl: per_class[cl]["n"] for cl in classes},
    "primary": {
        "accuracy": round(acc_primary, 4),
        "n_correct": n_correct,
        "balanced_accuracy": bal_acc,
        "per_class_recall": {cl: per_class[cl]["recall"] for cl in classes},
        "fail_safe_infeasible_recs": unsafe_primary,
        "misses": sorted([(m["id"], m["true"], m["pred"], m["pred_feasible"]) for m in misses]),
        "n_unsafe_misses": len(unsafe_misses),
    },
    "mechonly_ablation": {
        "accuracy": round(acc_mechonly, 4),
        "fail_safe_infeasible_recs": unsafe_mechonly,
        "n_infeasible": len(unsafe_mechonly),
    },
    "fpocket_supplementary": {
        "auroc_sm_vs_not": None if fp_auroc is None else round(fp_auroc, 4),
        "n_sm": len(sm_scores), "n_not": len(notsm_scores),
        "note": "reused MENDEL1 cache; expected WEAK per MENDEL1 G3 (mechanism+localization determine modality, not pocket score)",
    },
    "gates": {"G1_accuracy": g1_pass, "G2_fail_safe": g2_pass, "G3_localization_load_bearing": g3_pass},
    "per_row": [{k: x[k] for k in ("id", "gene", "disease_class", "mechanism", "localization",
                                    "protein_class", "true_modality", "pred_primary", "pred_mechonly",
                                    "primary_feasible", "feasible_set")} for x in rows],
}
payload_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
sha = hashlib.sha256(payload_str.encode()).hexdigest()

verdict = ("PASS - validated cross-class intervention-modality recommender (beats baseline AND fail-safe holds)"
           if overall_pass else
           "NEGATIVE - honest bound (modality not recoverable beyond baseline OR fail-safe violated)")
g3_verdict = ("PASS - localization is load-bearing: it eliminates the fail-safe violations the mechanism-only ablation commits"
              if g3_pass else "NEGATIVE - localization does not change the fail-safe outcome")

metrics = dict(payload)
metrics["_verdict"] = verdict
metrics["_g3_verdict"] = g3_verdict
metrics["_unsafe_misses"] = unsafe_misses
metrics["_coherence_check"] = "PASS - no approved true_modality flagged infeasible by the matrix"
metrics["_payload_sha256"] = sha
metrics["_provenance"] = {
    "experiment": "MODALITY1_intervention_modality",
    "ground_truth": "experiments/MODALITY1_intervention_modality/ground_truth.json (n=43, cited)",
    "features": "UniProt localization + mechanism (OMIM/ClinVar/lit) + protein-class druggability; causal_node uniform",
    "fpocket_reuse": "MENDEL1 AlphaFold-v6 fpocket cache for 21 overlapping targets (supplementary, non-gate)",
    "determinism": "no RNG; payload sha over sorted-key JSON excluding verdict/provenance",
}

json.dump(metrics, open(os.path.join(RESULTS, "MODALITY1_metrics.json"), "w"), indent=2, sort_keys=True)
open(os.path.join(RESULTS, "payload.sha256"), "w").write(sha + "\n")

print("=== MODALITY1 ===")
print(f"n={n}  majority_baseline={MAJORITY_BASELINE:.3f}")
print(f"PRIMARY accuracy={acc_primary:.3f} ({n_correct}/{n})  balanced={bal_acc:.3f}")
for cl in classes:
    print(f"   {cl}: recall {per_class[cl]['recall']:.3f} (n={per_class[cl]['n']})")
print(f"G1 (acc>={MAJORITY_BASELINE+0.20:.3f}): {g1_pass}")
print(f"G2 FAIL-SAFE infeasible recs: {unsafe_primary} -> {g2_pass}")
print(f"   misses (all should be safe): {[(m['id'],m['true'],'->',m['pred'],'feasible' if m['pred_feasible'] else 'INFEASIBLE') for m in misses]}")
print(f"   unsafe misses: {unsafe_misses}")
print(f"G3 mech-only ablation acc={acc_mechonly:.3f}  infeasible_recs={unsafe_mechonly} (n={len(unsafe_mechonly)}) -> {g3_pass}")
print(f"fpocket supplementary AUROC(SM vs not)={fp_auroc}  (n_sm={len(sm_scores)}, n_not={len(notsm_scores)})")
print(f"OVERALL: {verdict}")
print(f"payload sha256: {sha}")
