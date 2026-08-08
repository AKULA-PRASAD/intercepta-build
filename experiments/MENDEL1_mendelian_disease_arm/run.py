#!/usr/bin/env python
"""MENDEL1 scoring — deterministic, no RNG. Reads the frozen ground_truth.json + cached
fpocket_scores.json, applies the PRE-REGISTERED decision logic, evaluates G1/G2/G3, writes
results/MENDEL1_metrics.json (sorted keys) + payload.sha256. Reproduces byte-identical."""
import json, os, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "/Users/kalki/intercepta_data/mendel1"
RESULTS = os.path.join(HERE, "results")
os.makedirs(RESULTS, exist_ok=True)

# ---- frozen constants (PREREG) ----
DRUG_THRESH = 0.5
DRUGGABLE_CLASSES = {"enzyme", "kinase", "receptor", "ion_channel", "transporter", "nuclear_receptor"}
STABILIZABLE_AGG = {"transport_carrier", "globin"}
MAJORITY_BASELINE = 11.0 / 28.0  # RESTORE_SM = 11 of 28 (stated in PREREG)

gt = json.load(open(os.path.join(HERE, "ground_truth.json")))["genes"]
fp = json.load(open(os.path.join(DATA, "fpocket_scores.json")))


def predict_primary(g):
    c = g["consequence"]; pc = g["protein_class"]; mc = g["mut_class"]
    if c == "TOXIC_AGG":
        return "RESTORE_SM" if pc in STABILIZABLE_AGG else "NOT_SM"
    if c in ("GoF", "DN"):
        return "INHIBIT_SM" if pc in DRUGGABLE_CLASSES else "NOT_SM"
    # LoF
    if pc not in DRUGGABLE_CLASSES:
        return "NOT_SM"
    if mc == "null":
        return "NOT_SM"
    return "RESTORE_SM"


def predict_variantA(g, drug):
    """Variant A: fpocket pocket >= DRUG_THRESH ALSO grants a druggable handle (tests if
    structural druggability adds value / is safe). mut_class==null mechanism rule retained."""
    c = g["consequence"]; pc = g["protein_class"]; mc = g["mut_class"]
    has_pocket = (drug is not None) and (drug >= DRUG_THRESH)
    handle = (pc in DRUGGABLE_CLASSES) or has_pocket
    if c == "TOXIC_AGG":
        return "RESTORE_SM" if (pc in STABILIZABLE_AGG or has_pocket) else "NOT_SM"
    if c in ("GoF", "DN"):
        return "INHIBIT_SM" if handle else "NOT_SM"
    if not handle:
        return "NOT_SM"
    if mc == "null":
        return "NOT_SM"
    return "RESTORE_SM"


def balanced_accuracy(rows, predkey):
    classes = ["INHIBIT_SM", "RESTORE_SM", "NOT_SM"]
    recs = []
    for cl in classes:
        tot = sum(1 for r in rows if r["true_mode"] == cl)
        cor = sum(1 for r in rows if r["true_mode"] == cl and r[predkey] == cl)
        recs.append(cor / tot if tot else 0.0)
    return sum(recs) / len(classes), {c: round(v, 4) for c, v in zip(classes, recs)}


def auroc(pos_scores, neg_scores):
    """Mann-Whitney AUROC with 0.5 tie credit. Deterministic."""
    if not pos_scores or not neg_scores:
        return None
    wins = 0.0
    for p in pos_scores:
        for n in neg_scores:
            if p > n:
                wins += 1.0
            elif p == n:
                wins += 0.5
    return wins / (len(pos_scores) * len(neg_scores))


# ---- score every gene ----
rows = []
for g in gt:
    sym = g["gene"]
    drug = fp.get(sym, {}).get("fpocket_drug_score")
    prim = predict_primary(g)
    va = predict_variantA(g, drug)
    rows.append({
        "gene": sym, "true_mode": g["true_mode"], "sm_feasible": g["sm_feasible"],
        "consequence": g["consequence"], "protein_class": g["protein_class"], "mut_class": g["mut_class"],
        "fpocket_drug_score": drug,
        "pred_primary": prim, "pred_variantA": va,
        "correct_primary": prim == g["true_mode"], "correct_variantA": va == g["true_mode"],
    })
rows.sort(key=lambda r: r["gene"])

n = len(rows)
notsm = [r for r in rows if r["true_mode"] == "NOT_SM"]

# G1 — 3-class accuracy vs majority baseline
acc_primary = sum(r["correct_primary"] for r in rows) / n
bal_primary, rec_primary = balanced_accuracy(rows, "pred_primary")
g1_pass = acc_primary >= 0.60

# naive direction-only baseline (GoF/DN/TOXIC_AGG -> INHIBIT_SM ; LoF -> RESTORE_SM) — for context
def naive(g):
    return "RESTORE_SM" if g["consequence"] == "LoF" else "INHIBIT_SM"
acc_naive = sum(1 for g in gt if naive(g) == g["true_mode"]) / n
naive_unsafe = sum(1 for g in gt if g["true_mode"] == "NOT_SM" and naive(g) in ("INHIBIT_SM", "RESTORE_SM"))

# G2 — FAIL-SAFE: zero unsafe SM calls on true NOT_SM (primary)
unsafe_primary = [r["gene"] for r in notsm if r["pred_primary"] in ("INHIBIT_SM", "RESTORE_SM")]
g2_pass = len(unsafe_primary) == 0

# G3 — does fpocket add value?
pos = [r["fpocket_drug_score"] for r in rows if r["sm_feasible"] and r["fpocket_drug_score"] is not None]
neg = [r["fpocket_drug_score"] for r in rows if (not r["sm_feasible"]) and r["fpocket_drug_score"] is not None]
fpocket_auroc = auroc(pos, neg)
bal_variantA, rec_variantA = balanced_accuracy(rows, "pred_variantA")
unsafe_variantA = [r["gene"] for r in notsm if r["pred_variantA"] in ("INHIBIT_SM", "RESTORE_SM")]
g3_improves = (bal_variantA - bal_primary) >= 0.05
g3_new_violations = len(unsafe_variantA) > len(unsafe_primary)
g3_pass = g3_improves and not g3_new_violations

# misses (all should be safe/conservative = predicted NOT_SM when truth is SM-feasible)
misses = [{"gene": r["gene"], "true": r["true_mode"], "pred": r["pred_primary"]}
          for r in rows if not r["correct_primary"]]
unsafe_misses = [m for m in misses if m["pred"] in ("INHIBIT_SM", "RESTORE_SM") and m["true"] == "NOT_SM"]

overall_pass = g1_pass and g2_pass

# ---- payload (excludes verdict + provenance) for the reproduce-x2 sha ----
payload = {
    "n": n,
    "majority_baseline": round(MAJORITY_BASELINE, 4),
    "naive_direction_baseline_accuracy": round(acc_naive, 4),
    "naive_direction_fail_safe_violations": naive_unsafe,
    "primary": {
        "accuracy": round(acc_primary, 4),
        "balanced_accuracy": round(bal_primary, 4),
        "per_class_recall": rec_primary,
        "fail_safe_unsafe_calls": sorted(unsafe_primary),
        "misses": sorted([(m["gene"], m["true"], m["pred"]) for m in misses]),
    },
    "fpocket_arm": {
        "auroc_sm_feasible_vs_not": None if fpocket_auroc is None else round(fpocket_auroc, 4),
        "n_scored": len(pos) + len(neg),
        "variantA_balanced_accuracy": round(bal_variantA, 4),
        "variantA_per_class_recall": rec_variantA,
        "variantA_fail_safe_unsafe_calls": sorted(unsafe_variantA),
        "delta_balanced_accuracy_vs_primary": round(bal_variantA - bal_primary, 4),
    },
    "gates": {"G1_accuracy": g1_pass, "G2_fail_safe": g2_pass, "G3_fpocket_adds_value": g3_pass},
    "per_gene": [{k: r[k] for k in ("gene", "true_mode", "sm_feasible", "consequence",
                                     "protein_class", "mut_class", "fpocket_drug_score",
                                     "pred_primary", "pred_variantA")} for r in rows],
}
payload_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
sha = hashlib.sha256(payload_str.encode()).hexdigest()

verdict = ("PASS — new validated Mendelian coverage arm (mode triage beats baseline AND fail-safe holds)"
           if overall_pass else
           "NEGATIVE — honest bound (mode not classifiable beyond baseline OR fail-safe violated)")
g3_verdict = ("PASS — structural druggability adds value" if g3_pass
              else "NEGATIVE — fpocket druggability does not add / harms the triage")

metrics = dict(payload)
metrics["_verdict"] = verdict
metrics["_g3_verdict"] = g3_verdict
metrics["_unsafe_misses"] = unsafe_misses
metrics["_payload_sha256"] = sha
metrics["_provenance"] = {
    "experiment": "MENDEL1_mendelian_disease_arm",
    "ground_truth": "experiments/MENDEL1_mendelian_disease_arm/ground_truth.json (n=28, cited)",
    "structures": "AlphaFold DB v6 models; fpocket (bioinfo env) best-pocket Druggability Score",
    "note": "HTT (P42858) absent from AlphaFold DB (>size limit) -> fpocket None; PRIMARY triage unaffected.",
    "determinism": "no RNG; payload sha over sorted-key JSON excluding verdict/provenance",
}

json.dump(metrics, open(os.path.join(RESULTS, "MENDEL1_metrics.json"), "w"),
          indent=2, sort_keys=True)
open(os.path.join(RESULTS, "payload.sha256"), "w").write(sha + "\n")

print("=== MENDEL1 ===")
print(f"n={n}  majority_baseline={MAJORITY_BASELINE:.3f}  naive_direction_acc={acc_naive:.3f} (unsafe={naive_unsafe})")
print(f"PRIMARY accuracy={acc_primary:.3f}  balanced={bal_primary:.3f}  per-class={rec_primary}")
print(f"G1 (acc>=0.60): {g1_pass}")
print(f"G2 FAIL-SAFE unsafe calls on NOT_SM: {unsafe_primary}  -> {g2_pass}")
print(f"misses (all should be safe abstentions): {[(m['gene'],m['true'],'->',m['pred']) for m in misses]}")
print(f"fpocket AUROC (SM vs NOT): {fpocket_auroc}  variantA balacc={bal_variantA:.3f} (d={bal_variantA-bal_primary:+.3f}) variantA_unsafe={unsafe_variantA}")
print(f"G3 (fpocket adds value): {g3_pass}  -> {g3_verdict}")
print(f"OVERALL: {verdict}")
print(f"payload sha256: {sha}")
